# Audit of the EAX and R14 follow-up studies

## EAX comparisons across execution blocks

All 200 EAX attempts reached a terminal state. Exact integer EUC_2D recounts and Hamiltonian checks were repeated on the 199 valid saved tours. The unscored first-attempt evidence failure, `e0316`, remains in the original ledger. The original audit classified 78 of 79 attempts as valid; the corrected post-run audit accepted all 121 subsequently dispatched attempts. The native executable, wrapper, charged work and time limits stayed fixed. The follow-up ran separately on November 21, 2026, 13:47:30–19:21:31 Beijing time (UTC+08:00).

For each map and seed, shortening equals 10⁶ times the EAX length minus M or K length, divided by the EAX length. Map means receive equal weight. The percentile intervals come from 100,000 map bootstrap resamples, and the exact two-sided sign-flip tests depend on independent sign exchangeability across maps under the null. The table retains the auxiliary two-contrast Holm calculation from the original EAX follow-up. This two-contrast family was not separately preregistered. The final four-contrast Holm adjustment gives 0.000206 for K/C, K/EAX and M/EAX and 0.000561 for M/C. [Final Holm replay](../../../02_统计复算/holm/README.md) Each contrast loses one pair to `e0316` and one to a monitoring failure in its corresponding original arm.

| Contrast | Valid pairs | LKH arm shorter / tied / EAX shorter | Mean ppm | 95% map bootstrap interval ppm | Auxiliary follow-up Holm p |
| --- | ---: | ---: | ---: | ---: | ---: |
| M versus EAX | 198 | 159 / 2 / 37 | +24030.25 | [+6763.64, +50836.32] | 0.000102997 |
| K versus EAX | 198 | 164 / 3 / 31 | +24008.70 | [+6742.41, +50802.43] | 0.000102997 |

The results differ across the fixed benchmark. In a descriptive split at 12,000 cities, the 12 smaller maps ranged from 8,246 to 10,639 cities and had means of +4250.42 ppm (M) and +4222.60 ppm (K). The eight larger maps ranged from 12,000 to 16,928 cities, with means of +53699.99 ppm (M) and +53687.85 ppm (K). Both larger-map contrasts favored the LKH arm in all 79 valid pairs. EAX won all ten M pairs and nine of ten K pairs on xmc10150. On gr9882 EAX won six of ten M pairs even though the map mean was +5.97 ppm. The K comparison there was 4/2/4 with a +20.26 ppm mean. On genC15k.seed100004 the paired mean lengths were 54,315,775.6 for EAX and 41,454,179.8 for M, at +236720.81 ppm with the EAX denominator. Size and source vary together in the fixed panel.

| Source stratum | Maps | M mean ppm (shorter / tied / longer) | K mean ppm (shorter / tied / longer) |
| --- | ---: | ---: | ---: |
| VLSI | 5 | +5980.16 (31 / 1 / 18) | +5959.93 (33 / 1 / 16) |
| DIMACS clustered | 5 | +71670.28 (49 / 0 / 0) | +71582.84 (50 / 0 / 0) |
| DIMACS uniform | 5 | +13646.22 (49 / 0 / 0) | +13652.82 (49 / 0 / 0) |
| Geographic | 5 | +4824.33 (30 / 1 / 19) | +4839.21 (32 / 2 / 15) |

[All map effects and valid-pair counts](eax_map_effects_40.csv) · [Source and size summaries](eax_source_and_size_effects.csv) · [Full view and near-zero detail](EAX_map_effects_and_near_zero_detail.png)

## EAX implementation and charged observation

The recorded arguments were `1 DATA 100 30`, specifying one trial per process, output prefix DATA, population size 100 and offspring parameter 30. A replacement process after natural completion used the registered seed plus 100,000 times its process index. The native implementation initializes random tours by 2-opt. Its instrumented publisher writes strict incumbent improvements, including during population initialization. All 220 process invocations across the 200 attempts were audited. Among valid attempts 20 children completed naturally and were followed by another trial. The active final child in each attempt was stopped by the time policy.

The Python wrapper and solver shared logical CPU0; the resource sampler ran on CPU1. Python parsed decimal coordinates once before applying exact scaled-integer EUC_2D arithmetic. It checked and hashed each unique complete route. Two extra Python writes and snapshot read-back applied to improving deliveries. The raw ledgers reconcile 217,679 produced and consumed files across the 199 valid attempts, with 210,099 improvement commits and 7,580 non-improving validations. The observed count range of **529–1,573** (median 1,066) differs from the preliminary estimate of 579–1,555. The reported range comes from the full frozen ledger. One completed immutable file had no appended native event but was recorded by the consumer; its event time was left unknown.

| Valid attempts | Minimum | Median | Maximum |
| --- | ---: | ---: | ---: |
| Wrapper process CPU seconds inside the charged window | 9.406 | 13.234 | 17.484 |
| Native direct child CPU seconds, summed within attempt | 64.438 | 68.781 | 73.375 |
| Charged wall seconds through owned-process cleanup | 85.119 | 85.207 | 85.639 |
| Total outer-controller wall seconds | 97.252 | 97.332 | 97.819 |
| Resource sampler CPU seconds on CPU1 | 0.266 | 0.359 | 0.484 |

The 85 s request target allows stop proof before 86 s, certification before 88 s and cleanup before 90 s. Outer-controller wall time also includes about 12 s of admission/administrative work. Wrapper CPU is the actual process cost on the same logical CPU as the solver, including polling, validation and file work. It cannot be converted to an equal reduction in native search wall time. The wrapper changed the engineering poll interval to 5 ms, but there is no timed, otherwise-identical uninstrumented control. The observed counts, stages and elapsed intervals characterize this configuration and its cross-block comparison only.

The first published genetic improvement occurred a median 9.99 s after native observation initialized in the smaller group and 19.25 s in the larger group. These timings include earlier preparatory activity up to a genetic incumbent and do not isolate initialization time. The median last incumbent-improvement generation was 1258.5 versus 888; the logged generation is a checkpoint and stdout may have been buffered. Charged-time commits at or after 80 s occurred in 176 of 199 valid attempts, including all 79 valid attempts on larger maps. These observations establish progress close to the cutoff in this implementation. They do not establish a causal explanation for the route gap, a convergence classification, or performance without observation overhead.

[Per-map wrapper and candidate counts](eax_observer_cost_by_map.csv) · [Public native-process tables](../../../02_统计复算/EAX重启审计/README.md)

Per-attempt resources, raw progress evidence and the original machine receipt remain author-controlled. [Access conditions](../../../Data_Access_and_Archiving.md)

## Fixed-start conditional diagnostic

An independent EUC_2D recount verified the 120 delivered tours. The 60 paired results and the existing figure use the same frozen, hashed data. Each of the three selected pools used the same 20 new continuation seeds, with ten pairs per order. Two pools belong to one of the two maps. The 30 s continuation window leaves saved starts and parent-pool costs outside the charge.

| Fixed parent pool | K shorter / tied / longer | Mean ppm | Within-pool 95% interval ppm | M first ppm | K first ppm |
| --- | ---: | ---: | ---: | ---: | ---: |
| C10k.0/981 | 14 / 0 / 6 | +716.29 | [+251.78, +1200.80] | +537.91 | +894.68 |
| genC15k.seed100004/2521 | 12 / 0 / 8 | −109.03 | [−371.59, +139.14] | −216.44 | −1.61 |
| genC15k.seed100004/1861 | 8 / 0 / 12 | −219.79 | [−664.72, +273.42] | −79.71 | −359.86 |

The positive C10k.0/981 mean under the fixed-start diagnostic qualifies interpretation of its extreme single negative end-to-end observation. The two trials estimate different conditions. The selected pools neither establish a causal mechanism nor support inference across independent maps. The separate 800-slot mechanism-diagnostic plan remains deferred. Neither follow-up alters the 600-attempt study.

[Pool and run-order results](r14_pool_order_results.csv)
