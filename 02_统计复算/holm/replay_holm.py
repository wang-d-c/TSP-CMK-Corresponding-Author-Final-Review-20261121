"""Recompute R16 from the frozen core and EAX numerical ledgers without solvers."""

import argparse
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from csv import DictReader, DictWriter
from fractions import Fraction
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
from statistics import mean


COMPARISONS = {
    'K/M': ('K_new', 'M_new'),
    'K/C': ('K_new', 'C_ref'),
    'M/C': ('M_new', 'C_ref'),
    'K/EAX': ('K_new', 'EAX_ref'),
    'M/EAX': ('M_new', 'EAX_ref'),
}
CORE = Path('03_数据与复算/data')
EAX = Path('08_独立补验与执行证据/EAX200/正式结果')
FILES = {
    'core': (CORE / 'core_600_runs.csv', 'f589f6382e02165ea575100b880b511b389a9691ce739feb638369d1d57bbbc7'),
    'eax': (EAX / 'supplemental_eax_200.csv', 'e2b93def1296ce87d28e4619dc55d64b48b5292ea27dc31b741641a491b45f97'),
    'core_reference': (CORE / 'frozen_reference.json', None),
    'eax_reference': (EAX / 'supplemental_eax_summary.json', '54d68906b50ae09ef9c48b1734970135fb7fd9174779452a54a6e70d3fb4d05c'),
}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(DictReader(stream))


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def scores(core, later):
    require(len(core) == 600 and len(later) == 200, 'Unexpected ledger size')
    grid = defaultdict(dict)
    map_bindings = {}
    ids = set()
    counts = Counter()
    for cohort, rows, length_key, hash_key in (
        ('core', core, 'checked_length', 'instance_sha256'),
        ('eax', later, 'quality_if_valid', 'input_sha256'),
    ):
        for row in rows:
            identity = row['map'], row['seed']
            method = row['method'] if cohort == 'core' else 'EAX_ref'
            require(method in {'C_ref', 'M_new', 'K_new', 'EAX_ref'}, f'Unknown method {method}')
            require(row['run_id'] not in ids and method not in grid[identity], 'Repeated run identity')
            ids.add(row['run_id'])
            map_binding = row['stratum'], row[hash_key]
            require(map_bindings.setdefault(row['map'], map_binding) == map_binding, f'Inconsistent map {identity}')
            if row['status'] == 'valid':
                require(int(row[length_key]) > 0, f'Invalid valid length {identity}')
                require(len(row['route_sha256']) == 64, f'Missing route digest {identity}')
                if cohort == 'eax':
                    require(row['verified_independently'] == 'True', f'Missing route receipt {identity}')
                grid[identity][method] = int(row[length_key])
                counts[method] += 1
            else:
                require(not row[length_key], f'Invalid result has a score {identity}')
                grid[identity][method] = None
    require(len(grid) == 200 and len(map_bindings) == 20, 'Incorrect pairing grid')
    require(all(len(arms) == 4 for arms in grid.values()), 'At least one pair slot is absent')
    require(counts == {'C_ref': 198, 'M_new': 199, 'K_new': 199, 'EAX_ref': 199}, 'Run validity counts changed')
    return grid, counts


def exact_signflip(map_values):
    denominator = lcm(*(value.denominator for value in map_values))
    terms = [int(value * denominator) for value in map_values]
    cutoff = abs(sum(terms))
    trials = 1 << len(terms)
    if not cutoff:
        return Fraction(1), trials, trials

    def signed_sums(values):
        sums = [0]
        for value in values:
            sums = [x + value for x in sums] + [x - value for x in sums]
        return sums

    half = len(terms) // 2
    right = sorted(signed_sums(terms[half:]))
    hits = sum(
        bisect_right(right, -cutoff - lhs) + len(right) - bisect_left(right, cutoff - lhs)
        for lhs in signed_sums(terms[:half])
    )
    return Fraction(hits, trials), hits, trials


def contrast(grid, treatments):
    arm, reference = treatments
    paired = defaultdict(list)
    for (map_id, _), values in grid.items():
        score, reference_score = values[arm], values[reference]
        if score is not None and reference_score is not None:
            paired[map_id].append(Fraction(1_000_000 * (reference_score - score), reference_score))
    map_values = [mean(paired[map_id]) for map_id in sorted(paired)]
    p, hits, trials = exact_signflip(map_values)
    return p, hits, trials, len(map_values), sum(map(len, paired.values()))


def holm(raw):
    highest = Fraction(0)
    corrected = {}
    for rank, name in enumerate(sorted(raw, key=raw.__getitem__)):
        highest = max(highest, min(Fraction(1), (len(raw) - rank) * raw[name]))
        corrected[name] = highest
    return corrected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='new output directory outside the bundle')
    args = parser.parse_args()
    bundle, output = args.bundle.resolve(strict=True), args.output.resolve()
    require(not output.is_relative_to(bundle), 'Output must be outside the input bundle')
    paths = {name: bundle / spec[0] for name, spec in FILES.items()}
    file_hashes = {name: sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    for name, (_, expected) in FILES.items():
        require(expected is None or file_hashes[name] == expected, f'Frozen input changed: {name}')
    core_reference = read_json(paths['core_reference'])
    eax_reference = read_json(paths['eax_reference'])
    require(file_hashes['core'] == core_reference['portable_csv_sha256'] == eax_reference['frozen_core_ledger_sha256'],
            'References do not recognize the same core ledger')
    grid, counts = scores(read_csv(paths['core']), read_csv(paths['eax']))
    observed = {name: contrast(grid, arms) for name, arms in COMPARISONS.items()}
    raw = {name: values[0] for name, values in observed.items()}
    a = holm({'K/C': raw['K/C'], 'M/C': raw['M/C'], 'K/EAX': Fraction(1), 'M/EAX': Fraction(1)})
    b = holm({name: raw[name] for name in ('K/EAX', 'M/EAX')})
    c = holm({name: value for name, value in raw.items() if name != 'K/M'})
    for name, (arm, ref) in COMPARISONS.items():
        if ref == 'EAX_ref':
            reference = eax_reference['profiles'][arm]
            require(float(b[name]) == reference['supplementary_holm_two_contrasts'], f'Follow-up Holm mismatch: {name}')
            r = reference['two_sided_exact_signflip_p'], reference['maps'], reference['n_valid_pairs']
        else:
            reference = core_reference['effects'][f'{arm}/{ref}']
            if name in a:
                require(float(a[name]) == reference['holm_p'], f'Core Holm mismatch: {name}')
            r = reference['sign_flip_p'], reference['maps'], reference['pairs']
        _, _, _, maps, pairs = observed[name]
        require((float(raw[name]), maps, pairs) == r, f'Frozen comparison mismatch: {name}')

    def decimal(table, name):
        return float(table[name]) if name in table else None

    records = []
    for name, (value, hits, trials, maps, pairs) in observed.items():
        records.append({
            'contrast': name, 'maps': maps, 'valid_pairs': pairs,
            'extreme_sign_assignments': hits, 'all_sign_assignments': trials,
            'raw_p_exact': str(value), 'raw_p': float(value),
            'core_holm_a_input': (float(raw[name]) if name in ('K/C', 'M/C') else 1.0 if name in b else None),
            'core_holm_a_p': decimal(a, name), 'later_holm_b_p': decimal(b, name),
            'four_observed_holm_c_p': decimal(c, name),
        })
    alpha = Fraction(1, 20)
    unchanged = all((p <= alpha) == ((a | b)[name] <= alpha) for name, p in c.items())
    output.mkdir(parents=True, exist_ok=False)
    with (output / 'holm_comparison.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = DictWriter(stream, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    receipt = {
        'verified_input_sha256': {FILES[name][0].name: digest for name, digest in file_hashes.items()},
        'valid_by_arm': counts, 'all_frozen_raw_p_and_pair_counts_matched': True,
        'original_holm_a_and_b_match_frozen': True,
        'comparison_c_is_cross_period_sensitivity': True,
        'four_observed_secondary_decisions_unchanged_at_0_05': unchanged,
        'new_solver_runs': 0, 'records': records,
    }
    (output / 'holm_replay_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
