"""Replay the later EAX numerical comparisons from two exported run ledgers."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
from hashlib import sha256
import json
from math import isclose, lcm
from pathlib import Path
import platform
import random
from statistics import mean


METHODS = ('M_new', 'K_new')
CORE_ARMS = ('C_ref', *METHODS)
BOOTSTRAP_SEED = 20261120
BOOTSTRAP_REPEATS = 100_000
FLOAT_ATOL_PPM = 1e-9
MILLION = 1_000_000
FIRST_FAILURE = ('genE12k.seed100006', '2521')
FIRST_FAILURE_SHA256 = '3cd77510f4bbb63aae45541be02fb2a0876b4ab01a3b30f803b8eb753ca153db'
STRATA = {
    '01_VLSI_engineering': 'VLSI engineering',
    '02_DIMACS_clustered': 'DIMACS clustered',
    '03_DIMACS_uniform': 'DIMACS uniform',
    '04_Waterloo_geographic': 'Geographic',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    with path.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def unique_rows(rows, columns):
    index = {tuple(row[k] for k in columns): row for row in rows}
    require(len(index) == len(rows), f'Duplicate keys for {", ".join(columns)}')
    return index


def validated_grid(core_rows, eax_rows):
    core = unique_rows(core_rows, ('map', 'seed', 'method'))
    eax = unique_rows(eax_rows, ('map', 'seed'))
    require(len(core) == 600 and len(eax) == 200, 'Expected 600 core rows and 200 later EAX rows')
    require(len({r['run_id'] for r in core_rows}) == 600, 'Duplicate core run identifier')
    require(len({r['run_id'] for r in eax_rows}) == 200, 'Duplicate EAX run identifier')
    require(set(core) == {(map_id, seed, arm) for (map_id, seed) in eax for arm in CORE_ARMS},
            'Core and EAX map-seed slots do not align')
    seed_counts = Counter(map_id for map_id, _ in eax)
    require(len(seed_counts) == 20 and set(seed_counts.values()) == {10}, 'Unexpected map-seed grid')
    metadata = {}
    for (map_id, seed, method), row in core.items():
        item = row['stratum'], int(row['dimension']), row['instance_sha256']
        require(item[0] in STRATA and item[1] > 0 and len(item[2]) == 64, f'Invalid map metadata {map_id}')
        require(metadata.setdefault(map_id, item) == item, f'Map metadata changed across runs: {map_id}')
        if row['status'] == 'valid':
            require(int(row['checked_length']) > 0 and len(row['route_sha256']) == 64,
                    f'Invalid scored core run {(map_id, seed, method)}')
        else:
            require(row['checked_length'] == '', f'Invalid core row contained a score {(map_id, seed, method)}')
    require(Counter(item[0] for item in metadata.values()) == Counter({k: 5 for k in STRATA}),
            'The four source strata must contain five maps each')
    delivery = Counter(row['status'] for row in eax_rows)
    require(delivery == {'valid': 199, 'isolated_eax_evidence_failure': 1}, 'Frozen EAX delivery counts differ')
    invalid = eax[FIRST_FAILURE]
    require(invalid['status'] == 'isolated_eax_evidence_failure'
            and invalid['formal_terminal_sha256'] == FIRST_FAILURE_SHA256,
            'e0316 did not retain its frozen terminal identity')
    for (map_id, seed), row in eax.items():
        stratum, _, input_digest = metadata[map_id]
        require((row['stratum'], row['input_sha256']) == (stratum, input_digest),
                f'Input mismatch for {(map_id,seed)}')
        valid = row['status'] == 'valid'
        require(row['verified_independently'] == str(valid), f'Inconsistent frozen verification flag {(map_id,seed)}')
        if valid:
            require(int(row['quality_if_valid']) > 0 and len(row['route_sha256']) == 64,
                    f'Invalid scored EAX run {(map_id,seed)}')
        else:
            require(not row['quality_if_valid'] and not row['route_sha256'], f'Unscored EAX row has quality {(map_id,seed)}')
    return core, eax, metadata, delivery


def outcome_counts(ppm_values):
    return [sum(v > 0 for v in ppm_values), sum(v == 0 for v in ppm_values), sum(v < 0 for v in ppm_values)]


def signflip_probability(exact_map_means):
    """Count all assignments with the original exact-integer Gray traversal."""
    denominator = lcm(*(v.denominator for v in exact_map_means))
    terms = [v.numerator * (denominator // v.denominator) for v in exact_map_means]
    cutoff = abs(sum(terms))
    signed_sum = -sum(terms)
    extreme = int(abs(signed_sum) >= cutoff)
    previous_gray = 0
    patterns = 1 << len(terms)
    for index in range(1, patterns):
        gray = index ^ (index >> 1)
        changed = gray ^ previous_gray
        term = terms[changed.bit_length() - 1]
        signed_sum += 2 * term if gray & changed else -2 * term
        extreme += abs(signed_sum) >= cutoff
        previous_gray = gray
    return Fraction(extreme, patterns), extreme, patterns


def bootstrap_interval(map_means):
    """Replay the original map bootstrap with a fresh RNG for each contrast."""
    n = len(map_means)
    rng = random.Random(BOOTSTRAP_SEED)
    draws = sorted(sum(rng.choices(map_means, k=n)) / n for _ in range(BOOTSTRAP_REPEATS))
    bounds = []
    for quantile in (0.025, 0.975):
        at = (len(draws) - 1) * quantile
        low = int(at)
        bounds.append(draws[low] + (draws[low+1] - draws[low]) * (at-low))
    return bounds


def make_pairs(core, eax):
    groups = {arm: defaultdict(list) for arm in METHODS}
    paired_rows = []
    missing_rows = []
    for (map_id, seed), observed in eax.items():
        for arm in METHODS:
            original = core[map_id, seed, arm]
            if original['status'] != 'valid' or observed['status'] != 'valid':
                missing_rows.append({
                    'method': arm, 'map': map_id, 'seed': seed, 'core_status': original['status'],
                    'supplement_status': observed['status'], 'supplement_run_id': observed['run_id'],
                    'e0316': (map_id, seed) == FIRST_FAILURE,
                })
                continue
            l_arm = int(original['checked_length'])
            l_eax = int(observed['quality_if_valid'])
            ppm = Fraction(MILLION * (l_eax - l_arm), l_eax)
            groups[arm][map_id].append((ppm,l_arm,l_eax))
            paired_rows.append({
                'method': arm, 'map': map_id, 'seed': seed, 'stratum': observed['stratum'],
                'paired_core_length': l_arm, 'later_eax_length': l_eax, 'ppm': float(ppm),
                'exact_ppm': str(ppm),
            })
    require(sum(row['e0316'] for row in missing_rows) == len(METHODS), 'e0316 missing-pair propagation failed')
    return groups, paired_rows, missing_rows


def build_comparisons(groups, missing_rows, metadata, eax):
    profiles, maps, figure_rows = {}, [], []
    for arm, by_map in groups.items():
        map_keys = sorted(by_map)
        exact = {name: mean(p[0] for p in by_map[name]) for name in map_keys}
        floats = list(map(float, exact.values()))
        ppms = [v for name in map_keys for v,_,_ in by_map[name]]
        p_value, extreme, patterns = signflip_probability(list(exact.values()))
        strata = {}
        for tag in STRATA:
            subset = [name for name in map_keys if metadata[name][0] == tag]
            count = sum(len(by_map[name]) for name in subset)
            strata[tag] = {
                'available_maps': len(subset), 'available_pairs': count,
                'map_equal_mean_ppm': float(mean(exact[name] for name in subset)),
                'short_tied_long': outcome_counts([p[0] for name in subset for p in by_map[name]]),
            }
        profiles[arm] = {
            'maps': len(exact), 'n_valid_pairs': len(ppms), 'short_tied_long': outcome_counts(ppms),
            'mean_ppm': mean(floats), 'interval_95_ppm': bootstrap_interval(floats),
            'two_sided_exact_signflip_p': float(p_value),
            'exact_sign_patterns': patterns, 'extreme_patterns_including_equality': extreme,
            'missing_pair_categories': dict(Counter(
                f"core:{r['core_status']}|supplement:{r['supplement_status']}"
                for r in missing_rows if r['method'] == arm)),
            'map_exact_means_ppm': {name:str(value) for name,value in exact.items()},
            'descriptive_strata': strata,
        }
        require(len(exact) == 20 and len(ppms) == 198, f'Unexpected qualifying pairs for {arm}')
        relevant = Counter(m for (m,_), row in eax.items() if row['status'] == 'valid')
        for name in map_keys:
            triples = by_map[name]
            shorter,tied,longer = outcome_counts([p[0] for p in triples])
            maps.append({
                'method':arm, 'map':name, 'valid_pairs':len(triples), 'shorter':shorter, 'tied':tied,
                'longer':longer, 'mean_ppm':float(exact[name]), 'exact_mean_ppm':str(exact[name]),
            })
            figure_rows.append({
                'method':arm, 'map':name, 'stratum':metadata[name][0], 'cities':metadata[name][1],
                'valid_pairs':len(triples), 'core_shorter':shorter, 'tied':tied, 'eax_shorter':longer,
                'mean_ppm':float(exact[name]), 'exact_mean_ppm':str(exact[name]),
                'mean_eax_length':float(mean(p[2] for p in triples)),
                'mean_core_length':float(mean(p[1] for p in triples)), 'eax_valid_runs':relevant[name],
            })
    running = 0.0
    sorted_values = sorted((record['two_sided_exact_signflip_p'], arm) for arm,record in profiles.items())
    for rank,(raw,arm) in enumerate(sorted_values):
        running = max(running, min(1.0,(len(METHODS) - rank) * raw))
        profiles[arm]['supplementary_holm_two_contrasts'] = running
    figure_rows.sort(key=lambda r: (r['method'],r['map']))
    return profiles, maps, figure_rows


class Reconciliation:
    """Record check coverage, maximum ppm differences and any failure details."""

    def __init__(self):
        self.groups = {}
        self.failures = []

    def compare(self, group, label, actual, frozen, float_ppm=False):
        record = self.groups.setdefault(group, {'group': group, 'checks': 0, 'differences': 0,
                                                  'max_abs_numeric_difference_ppm': 0.0})
        record['checks'] += 1
        if float_ppm:
            discrepancy = abs(float(actual) - float(frozen))
            record['max_abs_numeric_difference_ppm'] = max(record['max_abs_numeric_difference_ppm'], discrepancy)
            passed = isclose(float(actual), float(frozen), rel_tol=0, abs_tol=FLOAT_ATOL_PPM)
        else:
            passed = actual == frozen
        if not passed:
            record['differences'] += 1
            self.failures.append({'group':group, 'field':label, 'replayed':actual, 'frozen':frozen})

    def check_csv(self, group, rows, actual, keys):
        frozen = unique_rows(rows, keys)
        actual_index = unique_rows(actual, keys)
        self.compare(group, 'keys', sorted(tuple(map(str,k)) for k in actual_index), sorted(frozen))
        for key, record in actual_index.items():
            saved = frozen.get(tuple(map(str,key)))
            if saved is None:
                continue
            self.compare(group, f'{key} fields', set(record) == set(saved), True)
            for field in record:
                if field not in saved:
                    continue
                val = saved[field]
                label = f'{key}/{field}'
                if field in {'ppm', 'mean_ppm'}:
                    self.compare(group, label, record[field], val, float_ppm=True)
                elif field in {'exact_ppm','exact_mean_ppm'}:
                    self.compare(group, label, Fraction(record[field]), Fraction(val))
                elif field in {'mean_eax_length','mean_core_length'}:
                    self.compare(group, label, float(record[field]), float(val))
                else:
                    self.compare(group, label, str(record[field]), val)


def reconcile(profiles, pairs, maps, figure_rows, summary, frozen_pairs, frozen_maps, frozen_figure,
              core_sha, delivery, invalid):
    checks = Reconciliation()
    for key,expected in {
        'bootstraps_per_qualifying_comparison': BOOTSTRAP_REPEATS, 'bootstrap_seed': BOOTSTRAP_SEED,
        'planned': 200, 'terminals': sum(delivery.values()), 'delivery': dict(delivery),
        'independent_recounts': delivery['valid'], 'frozen_core_ledger_sha256': core_sha,
        'preserved_first_failure': {'label': 'e0316', 'status': invalid['status'], 'score':None},
    }.items():
        checks.compare('batch', key, expected, summary[key])
    checks.check_csv('paired_run_rows', frozen_pairs, pairs, ('method','map','seed'))
    checks.check_csv('within_map_rows', frozen_maps, maps, ('method','map'))
    checks.check_csv('figure_S2_rows', frozen_figure, figure_rows, ('method','map'))
    for arm,record in profiles.items():
        saved = summary['profiles'][arm]
        for key in ('maps','n_valid_pairs','short_tied_long','two_sided_exact_signflip_p',
                    'supplementary_holm_two_contrasts','missing_pair_categories','map_exact_means_ppm'):
            checks.compare('overall_inference', f'{arm}/{key}', record[key], saved[key])
        checks.compare('overall_inference', f'{arm}/mean_ppm', record['mean_ppm'], saved['mean_ppm'], float_ppm=True)
        for index,(value,expected) in enumerate(zip(record['interval_95_ppm'],saved['interval_95_ppm'],strict=True)):
            checks.compare('overall_inference', f'{arm}/interval_95_ppm/{index}', value, expected, float_ppm=True)
        for stratum, sub in record['descriptive_strata'].items():
            frozen = saved['descriptive_strata'][stratum]
            for key in ('available_maps','available_pairs','map_equal_mean_ppm'):
                checks.compare('table_5A', f'{arm}/{stratum}/{key}', sub[key], frozen[key],
                               float_ppm=key=='map_equal_mean_ppm')
            fixed = [r for r in frozen_figure if r['method'] == arm and r['stratum'] == stratum]
            S_T_L = [sum(int(r[k]) for r in fixed) for k in ('core_shorter','tied','eax_shorter')]
            checks.compare('table_5A', f'{arm}/{stratum}/short_tied_long', sub['short_tied_long'], S_T_L)
    return checks


def table_5a(profiles):
    rows = []
    for code,label in STRATA.items():
        raw_m,raw_k = (profiles[arm]['descriptive_strata'][code] for arm in METHODS)
        rows.append({
            'source_stratum':label, 'maps':raw_m['available_maps'],
            'M_vs_EAX_ppm':raw_m['map_equal_mean_ppm'], 'M_vs_EAX_short_tied_long':'/'.join(map(str,raw_m['short_tied_long'])),
            'K_vs_EAX_ppm':raw_k['map_equal_mean_ppm'], 'K_vs_EAX_short_tied_long':'/'.join(map(str,raw_k['short_tied_long'])),
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', required=True, type=Path, help='Frozen core_600_runs.csv')
    parser.add_argument('--eax', required=True, type=Path, help='Frozen supplemental_eax_200.csv')
    parser.add_argument('--reference-dir', required=True, type=Path, help='Frozen EAX summary, pair and map outputs')
    parser.add_argument('--figure-reference', required=True, type=Path, help='Frozen eax_map_effects_40.csv')
    parser.add_argument('--output', required=True, type=Path, help='New output directory')
    args = parser.parse_args()

    require(not args.output.exists(), 'Use a new output directory')
    refs = {name:args.reference_dir/name for name in ('supplemental_eax_summary.json',
                                                        'supplemental_eax_valid_pairs.csv',
                                                        'supplemental_eax_map_effects.csv')}
    core, eax, metadata, delivery = validated_grid(read_csv(args.core),read_csv(args.eax))
    groups,pairs,missing_rows = make_pairs(core,eax)
    profiles, maps, figure_rows = build_comparisons(groups,missing_rows,metadata,eax)
    # The three frozen analysis exports are comparison targets only. They
    # never enter the pair construction, bootstrap or sign-flip calculations.
    checks = reconcile(
        profiles, pairs, maps, figure_rows, load_json(refs['supplemental_eax_summary.json']),
        read_csv(refs['supplemental_eax_valid_pairs.csv']),
        read_csv(refs['supplemental_eax_map_effects.csv']), read_csv(args.figure_reference),
        digest(args.core), delivery, eax[FIRST_FAILURE],
    )
    used = (args.core,args.eax,args.figure_reference,*refs.values())
    report = {
        'scope': 'Portable numerical replay of saved later EAX results. No new solving or route validation.',
        'implementation': platform.python_implementation(), 'python_version': platform.python_version(),
        'sources': {p.name:digest(p) for p in used},
        'counts': {'core_rows': len(core), 'eax_terminal_rows':len(eax),'eax_delivery':dict(delivery)},
        'preserved_first_failure': {'label':'e0316','map':FIRST_FAILURE[0],'seed':FIRST_FAILURE[1],
                                    'terminal_sha256': FIRST_FAILURE_SHA256, 'score': None},
        'statistical_settings': {
            'match': 'map, registered seed, core arm; scored only if both rows valid',
            'reduction_ppm': '1000000 * (EAX length - arm length) / EAX length',
            'mean': 'mean within map, then equal map weight',
            'bootstrap': {'generator': 'Python random.Random (MT19937)', 'seed': BOOTSTRAP_SEED,
                          'repeats': BOOTSTRAP_REPEATS, 'reset_per_contrast': True,
                          'sampling': 'uniform map mean with replacement from ascending map ID; 20 maps per draw',
                          'quantiles': [0.025,0.975], 'interpolation': 'linear at zero-based (B-1)*q'},
            'test': 'all map sign assignments; absolute signed sum at least absolute observed sum, inclusive equality, exact rational units',
            'holm_family': list(METHODS),
            'primary_family_unchanged': True,
        },
        'comparison_tolerance': {'absolute_ppm': FLOAT_ATOL_PPM, 'exact_join_counts_rational_values_and_p': True},
        'profiles': profiles,
        'check_groups': list(checks.groups.values()),
        'differences': [{key: str(value) if isinstance(value,(Fraction,set)) else value for key,value in row.items()}
                        for row in checks.failures],
        'outputs': ['supplemental_eax_valid_pairs.csv','supplemental_eax_map_effects.csv','eax_map_effects_40.csv',
                    'missing_pairs.csv','Table_5A.csv','reconciliation.csv','eax_replay.json'],
    }
    args.output.mkdir(parents=True)
    for name,rows in (('supplemental_eax_valid_pairs.csv',pairs),('supplemental_eax_map_effects.csv',maps),
                      ('eax_map_effects_40.csv',figure_rows),('missing_pairs.csv',missing_rows),
                      ('Table_5A.csv',table_5a(profiles)),('reconciliation.csv',report['check_groups'])):
        write_csv(args.output/name, rows)
    write_json(args.output/'eax_replay.json', report)
    if checks.failures:
        parser.exit(1, f'EAX replay found {len(checks.failures)} differences. See eax_replay.json.\n')
    print(f"EAX numerical replay passed: {delivery['valid']} scored terminals, {len(pairs)} paired rows, "
          f"{len(maps)} within-map rows, {sum(row['checks'] for row in checks.groups.values())} frozen-reference checks.")


if __name__ == '__main__':
    main()
