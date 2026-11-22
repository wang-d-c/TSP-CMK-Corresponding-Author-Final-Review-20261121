# R03 and R04 · Fixed-start diagnostic replay

The analysis starts from 120 frozen outcomes and reconstructs 60 complete seed pairs. It checks each pair against the original export and recovers the original percentile intervals. The three starting-tour pairs come from two maps and were selected because their original main-study runs had large negative reversals. Each starting-tour pair is reported separately. Between-pool pooling and inference to new maps are outside the diagnostic's design.

## R03 · Rebuild Table 5B and Figure 5

Use Python 3.10 or later. The statistics command uses the Python standard library. Matplotlib is needed for the figure, and the recorded render used Matplotlib 3.10.6.

```text
python replay_fixed_start.py FROZEN_REPORT NEW_OUTPUT --plan DIAGNOSTIC_PLAN.csv
python replay_fixed_start.py FROZEN_REPORT ANOTHER_NEW_OUTPUT --plan DIAGNOSTIC_PLAN.csv --plot
```

`FROZEN_REPORT` is the folder containing `outcomes_120.csv`, `pairs_60.csv`, and `diagnostics_summary.json`. `DIAGNOSTIC_PLAN.csv` is the separately archived `diagnostic_plan_120.csv`. The optional plan argument additionally checks the registered slot, instance, historical pool seed, role, continuation seed and order against every outcome. Use new output folders for each invocation.

The replay pairs by instance, historical pool seed, and continuation seed. It verifies adjacent M/K arm slots, status, order, and integer end length. It computes the signed paired effect as `1,000,000 × (M_end − K_end) / M_end`, with positive values indicating a shorter K tour. `r14_rebuilt_pairs.csv` has the same SHA256 as the frozen pair file. `r14_plot_data.csv` identifies each plotted point by pool, continuation seed and the two original run IDs and slots. The only display offsets are on the vertical axis. `r14_statistics.csv` links Table 5B and the Figure 5 intervals to each pool's `all_orders` row and includes the six execution-order strata.

The saved analysis code `report_diag.py` (SHA256 `b3662c5f149ee31027415b1b531eddd97c2ba603d3740daa91f82f069076cb2a`) initializes `random.Random(20261121 + i)` for whole-pool intervals and `random.Random(20261125 + 2*i + j)` for execution-order strata. The zero-based pool order is the order shown below. Order strata use M first at `j=0` and K first at `j=1`. Every group draws 10,000 same-size replacement samples with `random.choices`, computes the arithmetic mean, then linearly interpolates empirical quantiles at `(N−1) p` for `p=0.025` and `0.975`. The replay reproduces all nine point estimates and interval endpoints exactly, with the rows in frozen slot order. These are descriptive intervals over continuation seeds within each fixed pool.

| Historical pool | Paired seeds | K shorter / tied / longer | Mean effect, ppm | 95% interval, ppm | M-first / K-first means, ppm |
|---|---:|---:|---:|---:|---:|
| C10k.0 / 981 | 20 | 14 / 0 / 6 | +716.29 | [+251.78, +1200.80] | +537.91 / +894.68 |
| genC15k.seed100004 / 2521 | 20 | 12 / 0 / 8 | −109.03 | [−371.59, +139.14] | −216.44 / −1.61 |
| genC15k.seed100004 / 1861 | 20 | 8 / 0 / 12 | −219.79 | [−664.72, +273.42] | −79.71 / −359.86 |

The standard-library-only run used Python 3.13.9 with `-I -S` and the plot run used that version with Matplotlib 3.10.6. An independent read-only rerun of the original data exporter checked the 120 raw dispatches, terminals, completion hashes and delivered route hashes. The new outcome CSV, pair CSV and original-form summary all matched their frozen exports byte for byte. The new Figure 5 was opened for visual inspection. Its single-page PDF has no image objects and its PNG is 2,940 × 1,340 pixels at 400 dpi. The frozen plot files were retained.

## R04 · What this timed run measures

All 120 diagnostic terminal records identify the same frozen native continuation executable as the six selected source arms in the main batch. This was the Windows LKH 3.0.14 research build `LKH-review-common.exe` (SHA256 `d239bf79873b085ae2d246812b0237af74f6d6b97c413490ea9ac9f8b295d665`), built with w64devkit GCC 16.2.0. The recorded compiler options include `-O3 -std=gnu99 -fcommon -DTWO_LEVEL_TREE -march=native -ffp-contract=off`. The native build receipt and all compared bindings are digested in the runtime audit receipt.

The realized search parameters match the corresponding main continuation arms apart from the seed. The main continuation uses the historical pool seed plus 3000. The diagnostic uses the 20 registered new seeds, shared across all three pools and paired within the pool. Diagnostic options include POPMUSIC candidates with at most five candidates, move type 5, subsequent move type 5, `PATCHING_A=1`, `PATCHING_C=0`, `POPULATION_SIZE=0`, `RECOMBINATION=GPX2`, one run and at most 100,000 trials under the wall-clock stop. The detailed settings are in the runtime audit receipt.

Seed generation takes SHA256 of the fixed namespace `TSP_CMK_review_20261121/R14/fixed-before-outcomes` followed by `/seed/` and the draw index. It adds 10,000,000 to the digest integer modulo 1,990,000,000 and excludes collisions and earlier registered continuation seeds. Another SHA256 rank independently balances each pool to ten M-first and ten K-first pairs. Each pair runs in adjacent slots and the two arms use the same continuation seed. Start bytes and length are checked before installation as `start.tour` with `INITIAL_TOUR_FRACTION=1`. The native first-tour witness has a recorded hash and agrees with that tour after canonicalization for rotation and reversal.

The monotonic clock starts on entry to the diagnostic routine, before map and historical-start preparation and native launch. Input checks and staging, LKH launch and initialization, candidate checks, in-window route validation, certification and cleanup all use that clock. The first native launch ranged from 1.36143 to 1.47071 s. The raw clock evidence gives:

| Event | Registered boundary, s | Across 120 runs, s |
|---|---:|---:|
| Stop request | 27.6 target | 27.60008–27.61579 |
| Native stop proof | Before 28 | 27.61285–27.63904 |
| Native Job cleanup | Before 30 | 27.61377–27.64116 |
| Certified route delivery | Before 29 | 27.64792–27.69090 |
| Sampler cleanup observed | Before 30 | 27.67539–27.95445 |
| Charged completion observed | Before 30 | 27.73331–28.03610 |

`charged_seconds` is the recorded monotonic time from routine entry through durable result payload validation and the completion observation. The signed completion record and its readback follow that observation. The 30 seconds are a ceiling for the accepted completion and cleanup, so ending near 28 seconds follows the registered stop and completion protocol. The native solver used logical CPU 0 (mask 1), the independent sampler used logical CPU 1, and all terminal Job records reported zero active processes. The 120 arms ran from 12:46:03 to 13:42:10 Beijing time on November 21, 2026. The two qualification runs are outside this analysis.

Historically producing the parent pool and the two selected starts, including the additional external GPX2 work, is outside the diagnostic window. The main-batch continuation has a different charged origin that includes the historical shared-parent charge and, for K, the extra GPX2 actions in its own live clock. The equal-window diagnostic measures conditional continuation with fixed existing starts. It cannot estimate the end-to-end benefit or identify a causal explanation for the original reversals.

## Evidence index

- [Replay source](replay_fixed_start.py), [replay acceptance](replayed/r14_replay_receipt.json), [paired effects](replayed/r14_rebuilt_pairs.csv), [pool and order effects](replayed/r14_statistics.csv), [Figure 5 point data](replayed/r14_plot_data.csv), [vector PDF](replayed/figure5_fixed_start.pdf) and [400-dpi PNG](replayed/figure5_fixed_start.png).
- [Public numerical replay](replay_fixed_start.py) and [path-free runtime audit receipt](r14_runtime_audit_receipt.json). The runtime audit requires controlled original terminal files, staged route bytes, and main-result bindings. The statistics replay can run from the numerical export.
- R03 completed on the frozen numerical export and plan. R04 completed on the existing native binding, six main arms, and 120 original diagnostic runtime receipts. Neither check launched a solver.
