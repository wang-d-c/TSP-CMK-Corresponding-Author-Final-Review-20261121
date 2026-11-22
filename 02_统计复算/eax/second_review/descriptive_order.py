"""Report the later EAX contrasts by the original main-block M/K slot order."""

import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with path.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--core', required=True, type=Path)
    cli.add_argument('--eax', required=True, type=Path)
    cli.add_argument('--output', required=True, type=Path)
    args = cli.parse_args()
    core = {(r['map'], r['seed'], r['method']): r for r in read_csv(args.core)}
    eax = {(r['map'], r['seed']): r for r in read_csv(args.eax)}
    assert len(core) == 600 and len(eax) == 200
    assert sum(r['status'] == 'valid' for r in eax.values()) == 199
    groups = defaultdict(lambda: defaultdict(list))
    missing = defaultdict(Counter)
    for (map_id, seed), e in eax.items():
        m, k = (core[map_id, seed, arm] for arm in ('M_new', 'K_new'))
        assert e['input_sha256'] == m['instance_sha256'] == k['instance_sha256']
        order = 'M_first' if int(m['slot']) < int(k['slot']) else 'K_first'
        for arm in (m, k):
            group = order, arm['method']
            if arm['status'] == e['status'] == 'valid':
                e_length = int(e['quality_if_valid'])
                groups[group][map_id].append(Fraction(10**6 * (e_length - int(arm['checked_length'])), e_length))
            else:
                missing[group][f"core:{arm['status']}|supplement:{e['status']}"] += 1
    assert len(groups) == 4 and all(len(by_map) == 20 for by_map in groups.values())
    summaries, details = [], []
    for (order, arm), by_map in sorted(groups.items()):
        effects = mean(mean(v) for v in by_map.values())
        vals = [v for part in by_map.values() for v in part]
        counts = [sum(v > 0 for v in vals), vals.count(0), sum(v < 0 for v in vals)]
        summaries.append({'main_block_mk_order': order, 'comparison': arm + '/EAX', 'maps': len(by_map),
                          'valid_pairs': len(vals), 'shorter': counts[0], 'tied': counts[1], 'longer': counts[2],
                          'map_equal_mean_ppm': float(effects), 'exact_mean_ppm': str(effects),
                          'missing_reason_counts': json.dumps(dict(missing[order, arm]), sort_keys=True)})
        for map_id, group in sorted(by_map.items()):
            effect = mean(group)
            details.append({'main_block_mk_order': order, 'comparison': arm + '/EAX', 'map': map_id,
                            'valid_pairs': len(group), 'mean_ppm': float(effect), 'exact_mean_ppm': str(effect)})
    assert sum(r['valid_pairs'] for r in summaries) == 396
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    write_csv(output / 'eax_descriptive_core_order.csv', summaries)
    write_csv(output / 'eax_descriptive_core_order_maps.csv', details)
    receipt = {'input_sha256': {'core_600_runs.csv': sha256(args.core.read_bytes()).hexdigest(),
                                'supplemental_eax_200.csv': sha256(args.eax.read_bytes()).hexdigest()},
               'n_groups': len(summaries), 'n_map_groups': len(details), 'n_all_paired_rows': 396,
               'hypothesis_tests': 0, 'new_solves': 0,
               'meaning': 'Order comes from the original M/K slots. Later EAX was separately timed.'}
    (output / 'eax_order_replay_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
