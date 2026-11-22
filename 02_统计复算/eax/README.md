# Recompute the later EAX comparison

This command derives the two paired quality comparisons from the original 600-row C/M/K export and the later 200-row EAX export. No solver, coordinate files, route files or third-party Python packages are required. Use an unused output directory. The original inputs and reference outputs are opened read-only.

The six inputs from the review bundle are collected below. Their names may be used directly if you put the executable, ledgers and reference subdirectory together in a scratch directory.

| Input | File | Role |
|---|---|---|
| `--core` | `core_600_runs.csv` | Primary per-run ledger with validity and checked integer lengths |
| `--eax` | `supplemental_eax_200.csv` | Later EAX per-run ledger with validity and checked integer lengths |
| `--reference-dir` | `supplemental_eax_summary.json`, `supplemental_eax_valid_pairs.csv`, `supplemental_eax_map_effects.csv` | Frozen inference and supporting numerical exports checked after the calculation |
| `--figure-reference` | `eax_map_effects_40.csv` | Previous Figure S2 plot coordinates, checked after the calculation |

From the review package root, PowerShell can use the bundled paths directly.

```powershell
$core = '03_数据与复算/data/core_600_runs.csv'
$refs = '08_独立补验与执行证据/EAX200/正式结果'
$figure = '08_独立补验与执行证据/EAX200/本轮公平性审计/eax_map_effects_40.csv'
python -I -S -B -X utf8 '02_统计复算/eax/reproduce_eax.py' --core $core --eax "$refs/supplemental_eax_200.csv" --reference-dir $refs --figure-reference $figure --output eax_recomputed
```

In an isolated directory laid out as described above, the same entry point is

```text
python -I -S -B -X utf8 reproduce_eax.py --core core_600_runs.csv --eax supplemental_eax_200.csv --reference-dir reference --figure-reference reference/eax_map_effects_40.csv --output eax_recomputed
```

In that example `reference` contains all four reference files. Each flag accepts an explicit relative or absolute path for layouts where the files are stored separately. The run raises an error if the ledgers disagree on keys or instance identities, if the output directory already exists, or if a reference value fails reconciliation. Numerical differences found in reconciliation are recorded before the script exits with status 1. The JSON records hashes and software version and omits machine paths.

## Outputs

| Output | What it contains |
|---|---|
| `supplemental_eax_valid_pairs.csv` | 396 scored pair rows, with the integer lengths and exact rational ppm |
| `supplemental_eax_map_effects.csv` | 40 map-method rows, with counts, exact means and numerical means |
| `eax_map_effects_40.csv` | Figure S2 data with dimensions and per-map delivery and quality summaries |
| `Table_5A.csv` | Four source strata, with map-equal means and short/tied/long counts for each comparison |
| `missing_pairs.csv` | The failed EAX row and the arm-specific missing core rows that prevent four comparisons |
| `eax_replay.json`, `reconciliation.csv` | Exact design settings, inference, input hashes and per-group reference comparisons |

The ppm denominator is the EAX route length. Each map receives equal weight after averaging its valid pairs. The original implementation used 100,000 draws of 20 map means with replacement. It sorted by map ID and restarted Python `random.Random(20261120)` for each comparison. The percentile bounds linearly interpolate at zero-based index `(B - 1)q`. The exact sign-flip test uses all 1,048,576 assignments and compares the absolute signed map-effect sum, counting equality in exact rational arithmetic. This replay matches the historical EAX follow-up output, including its two-contrast Holm values of 0.000103 for both contrasts. Those adjusted values are supplementary. The final four-contrast Holm adjustment gives 0.000206 for K/C, K/EAX and M/EAX and 0.000561 for M/C. The frozen core-stage snapshot retains its two unavailable EAX placeholders. For the final family and its prespecification evidence, use the [four-contrast Holm replay](../holm/README.md).

`render_eax_effects.py` in the Figure S2 evidence directory can consume the regenerated `eax_map_effects_40.csv` as its first argument and an output directory as its second argument. That optional plotting step requires Matplotlib. A fresh PDF can have different metadata, including creation time.

## Run receipt

- CPython 3.12.14 in isolated standard-library mode exited with status 0. A separate directory containing only the script, ledgers and reference exports produced seven identical output files. The two runs passed 4,547 frozen-reference comparisons apiece. Counts, exact proportions and p values were checked for equality. Decimal ppm fields used an absolute tolerance of `1e-9 ppm`. All observed reference differences were zero.
- Both pair and map exports and the Figure S2 data CSV were byte-identical to the historical reference. Re-rendering Figure S2 with CPython 3.13.9 and Matplotlib 3.10.6 produced the same PNG bytes and identical 144 dpi rasterizations of the two PDFs. The regenerated PDF recorded a fresh creation time.
- The EAX ledger contains 199 valid results and one `isolated_eax_evidence_failure`. The original e0316 terminal digest matches `3cd77510f4bbb63aae45541be02fb2a0876b4ab01a3b30f803b8eb753ca153db`. That run has no scored length and is absent from both comparisons. A distinct invalid core run prevents one further pair in each comparison.
- The algorithmic reference is the archived project statistics module `analyze_review_eax.py` with SHA256 `0d6d30afc8f08a4829c2f42e92cc81acc89a21aaaa3ac4ccc37ed221616932bd`. This portable script adapts the numerical logic to read the release exports. It checks existing independent-verification flags and route hashes in the ledger. Revalidating route geometry and running solvers remain separate tasks.
- `REPLAY_OUTPUT_SHA256.txt` lists the seven generated numerical files from this execution. The JSON records the Python version, so its bytes can vary across versions even when the numerical output matches.
