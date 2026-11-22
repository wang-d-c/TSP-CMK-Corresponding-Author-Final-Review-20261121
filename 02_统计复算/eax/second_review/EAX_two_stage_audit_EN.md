# EAX stop evidence replay and comparison by original M/K order

## The two post-run evidence gates

EAX ran in a later block on 21 November 2026. The M and K scores come from the original 600-run block. The schedule pairs scores by map and seed. Within the later EAX block, the first 79 terminals used R13a01 and the remaining 121 used R13a02.

| Applied phase | UTC, 21 November 2026 | Terminals | Official valid | Pass when replaying a01 | Pass when replaying a02 before preserving the first failure |
| --- | --- | ---: | ---: | ---: | ---: |
| R13a01 | 05:47:30.525–07:56:51.360 | 79 | 78 | 78 | 79 |
| R13a02 | 08:03:17.945–11:21:31.258 | 121 | 121 | 121 | 121 |

- R13a01’s `inspect_outputs` required the saved `stop.requested_s` in `[85, 86)` seconds, exactly one stopped child, intact owned Job proof, observed zero active processes before 86 s, and complete candidate and certification evidence.
- R13a02 installed `audit_action_clock` on the same controller’s inspection callback, after the timed runner returned. The lower bound applies to the captured native kernel operation, and the proof must show `85 ≤ termination_call_s ≤ job_zero_observed_s < 86`. A `terminate_owned_job` record must bind the child PID, with preparation no later than the actual call. A `no_running_child` observation must have a null child PID and fall after the recorded zero-activity time and before 86 s. Any relaxation of a lower-bound rejection is limited to early preparation on the same owned Job, with complete candidate accounting, clean outer evidence, valid independent recounts and the original certification and cleanup deadlines.
- All 200 runs bind the same native executable and decimal observer. Each final owned Job receipt records affinity mask 1 and the observer and its native child in the same Job. The observer’s initial affinity was CPU0 and its charged CPU is logged in `wrapper_cpu_seconds_charged`. The two gates add no separate core. The operational 85-second request, stop-proof deadline before 86 s, certification before 88 s, cleanup before 90 s, candidate consumption, timed wrapper and charging were unchanged. This is a comparison of workflows under the specified budget and recorded resource allocation. Subgroup estimates apply to these inputs; the post hoc 12,000-city split also reflects the mix of instance sources.

The audit ran both actual frozen inspection functions on all 200 archived terminals and checked four material-file hashes per terminal, including the raw wrapper result, outer result, independent certificate and Job record. The originally assigned rule reproduced all 200 terminal states and scores. The first 79 terminal hashes match the immutable continuation receipt. The actual model and implementation identities are in the [machine-readable replay receipt](eax_two_stage_replay_receipt.json). The underlying code and logs stay in the author-controlled archive.

## Effect on accepted comparisons

Slot `e0316` is the only disagreement. It logged preparation at 84.999985801 s, the kernel call at 85.000083901 s and observed Job-zero proof at 85.104539801 s. The recorded failure and its null score are preserved. All 121 accepted a02 slots also passed the a01 gate. Applying either rule to the archive with the first failure preserved gives 199 valid EAX records and 198 pairs per contrast, with unchanged missing counts, point estimates, confidence intervals and p values. One invalid original core result in each arm accounts for the remaining excluded pair beyond `e0316`.

The last two rows show a read-only counterfactual that applies a02 to `e0316` as well. Its already archived route passed the a02 audit with dual archived recounts, and an additional local EUC_2D geometry recount of that single archived route confirmed the length and hashes. The counterfactual is audit-only. The published sample and the archived terminal keep their original eligibility and score.

| Scoring scope | Contrast | Valid pairs | Map-equal mean ppm | 95% map-bootstrap interval ppm | Raw map sign-flip p | Auxiliary follow-up Holm p |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| Official and both failure-preserving replays | M/EAX | 198 | 24030.25 | [6763.64, 50836.32] | 0.0000591278076171875 | 0.000102996826171875 |
| Official and both failure-preserving replays | K/EAX | 198 | 24008.70 | [6742.41, 50802.43] | 0.0000514984130859375 | 0.000102996826171875 |
| Raw a02 counterfactual, never scored in the official sample | M/EAX | 199 | 24017.41 | [6750.64, 50815.90] | 0.0000591278076171875 | 0.000102996826171875 |
| Raw a02 counterfactual, never scored in the official sample | K/EAX | 199 | 23995.73 | [6730.79, 50791.18] | 0.0000514984130859375 | 0.000102996826171875 |

The replays use the original 100,000 map bootstrap draws, seed `20261120`, exact two-sided map sign flips and the two-contrast adjustment reported in the EAX follow-up. This table retains that auxiliary calculation to assess the effect of the stop rule. The final prespecified four-contrast adjustment uses the official scores and is documented in the [Holm replay](../../holm/README.md). The original 600-run core-stage snapshot remains separate.

## Descriptive sensitivity by original M/K order

Each row groups the original M/K slots by the earlier of their two registered positions. It then matches each accepted original arm to the later EAX result on the same map and seed. The map-equal means weight each map equally after averaging eligible seed pairs within that group. Every row represents all 20 maps. Positive effects mean shorter M or K tours relative to EAX. There are zero subgroup hypothesis tests.

| Original M/K order | Contrast | Pairs | Shorter / tied / longer | Map-equal mean ppm |
| --- | --- | ---: | --- | ---: |
| M first | M/EAX | 99 | 80 / 1 / 18 | 24459.20 |
| M first | K/EAX | 98 | 81 / 2 / 15 | 24428.10 |
| K first | M/EAX | 99 | 79 / 1 / 19 | 23608.68 |
| K first | K/EAX | 100 | 83 / 1 / 16 | 23590.15 |

The descriptive effect stays positive in the two original M/K orders. Since EAX was timed afterward, these groups neither assign a running order to EAX nor identify a causal order effect. [Aggregate CSV](order/eax_descriptive_core_order.csv) · [Map CSV](order/eax_descriptive_core_order_maps.csv) · [Replay script](descriptive_order.py) · [Input receipt](order/eax_order_replay_receipt.json).
