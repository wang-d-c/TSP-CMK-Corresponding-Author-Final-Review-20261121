"""Replay the three numerical cohorts into a new directory without running a solver."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
STATS = Path('02_统计复算')
CORE = Path('03_数据与复算')
EVIDENCE = Path('08_独立补验与执行证据')
EAX = EVIDENCE / 'EAX200/正式结果'
EAX_FIGURES = EVIDENCE / 'EAX200/本轮公平性审计'
DIAG = EVIDENCE / '条件续搜120/report_final'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--figures', action='store_true', help='Also regenerate Figures 1–5 and S2 (Matplotlib required)')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.is_relative_to(ROOT):
        parser.error('Choose an unused output directory outside the input package')
    out.mkdir(parents=True, exist_ok=False)
    output_arg = lambda name: os.path.relpath(out / name, ROOT)
    log = []

    def call(label, argv, pure=True):
        flags = ['-I', '-S', '-B', '-X', 'utf8'] if pure else ['-B', '-X', 'utf8']
        command = [sys.executable, *flags, *map(str, argv)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        (out / f'{label}.stdout.txt').write_text(result.stdout, encoding='utf-8')
        (out / f'{label}.stderr.txt').write_text(result.stderr, encoding='utf-8')
        log.append({'stage': label, 'arguments_after_python': [*flags, *map(str, argv)], 'exit': result.returncode})
        (out / 'commands.json').write_text(json.dumps(log, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        result.check_returncode()

    call('core', [CORE / 'reproduce.py', '--no-plot', '--output', output_arg('core')])
    call('eax', [STATS / 'eax/reproduce_eax.py', '--core', CORE / 'data/core_600_runs.csv',
                 '--eax', EAX / 'supplemental_eax_200.csv', '--reference-dir', EAX,
                 '--figure-reference', EAX_FIGURES / 'eax_map_effects_40.csv', '--output', output_arg('eax')])
    call('r14', [STATS / 'r14/replay_fixed_start.py', DIAG, output_arg('r14'), '--plan', STATS / 'r14/diagnostic_plan_120.csv'])

    core_csv = sorted((ROOT / CORE / '复算产物').glob('*.csv'))
    rows = [('core', p.name, sha(p), sha(out / 'core' / p.name)) for p in core_csv]
    for name, reference in (
        ('supplemental_eax_valid_pairs.csv', EAX), ('supplemental_eax_map_effects.csv', EAX),
        ('eax_map_effects_40.csv', EAX_FIGURES),
    ):
        rows.append(('eax', name, sha(ROOT / reference / name), sha(out / 'eax' / name)))
    rows.append(('r14', 'pairs_60.csv', sha(ROOT / DIAG / 'pairs_60.csv'), sha(out / 'r14/r14_rebuilt_pairs.csv')))
    report = [{'cohort': cohort, 'reference': name, 'expected_sha256': before, 'actual_sha256': after,
               'byte_equal': before == after} for cohort, name, before, after in rows]
    (out / 'byte_comparisons.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if len(core_csv) != 8 or not all(row['byte_equal'] for row in report):
        raise RuntimeError('Numerical output bytes differed from the frozen reference')

    if args.figures:
        call('figures_1_to_4', ['assets/figures/redraw_main.py', '.', output_arg('figures')], pure=False)
        call('figure_s2', [EAX_FIGURES / 'render_eax_effects.py', output_arg('eax/eax_map_effects_40.csv'),
                           output_arg('figure_s2')], pure=False)
        call('figure_5', [STATS / 'r14/replay_fixed_start.py', DIAG, output_arg('figure_5'), '--plan',
                          STATS / 'r14/diagnostic_plan_120.csv', '--plot'], pure=False)

    print('All three numerical replays passed. Frozen CSV equality: core 8/8, EAX 3/3, fixed-start 1/1.')


if __name__ == '__main__':
    main()
