# Data access and archiving

The [current review package](https://github.com/wang-d-c/TSP-CMK-Corresponding-Author-Final-Review-20261121/releases/tag/cmk-final-science-20261122) contains portable numerical replays for three separate cohorts. The [v3 package](https://github.com/wang-d-c/TSP-CMK-Corresponding-Author-Final-Review-20261121/releases/tag/cmk-author-review-v3-20261121) and previous reference artifacts remain versioned. The 600-run main batch, the 200-slot later EAX run block, and the 120-run fixed-start diagnostic have separate time blocks and statistical scopes.

| Capability | What the review package provides |
| --- | --- |
| Numerical replay | Inputs and standard-library commands reproduce the main comparisons, the two later EAX comparisons, and the fixed-pool diagnostic, including its original bootstrap intervals. See the [replay guide](02_统计复算/README.md). |
| Figure regeneration | Figures 1–4 use bundled numerical and exploratory exports, Figure 5 uses all 60 pairs rebuilt from the diagnostic outcomes, and Figure S2 uses the later EAX map effects recomputed from paired runs. Figures 3 and 4 use precomputed exploratory input tables. |
| Route geometry validation | Existing local checks cover 596 main routes, 199 later EAX routes and 120 continuation routes against the matching map files. City orders and restricted map files stay in controlled archives. An external reviewer needs authorized access to both inputs. A reviewer channel has yet to be established and verified. |
| End-to-end solve from coordinates | Requires the matching maps, authorized frozen implementation or build artifacts, the recorded operating environment and the timing and verification controls. The public numerical package does not establish that an external party can rerun the frozen solver workflow. |

The authors still need to confirm which routes, maps and frozen implementations may be shared and test the approved channel with the intended access scope. The study's recorded software hashes identify the frozen implementations. Distribution rights remain to be confirmed separately. [LKH upstream](https://keldhelsgaun.github.io/) · [GA-EAX upstream](https://github.com/nagata-yuichi/GA-EAX)

The public package has no independently verified Zenodo deposit or DOI. Use the stated release or the corresponding commit to cite this review snapshot.

[上一轮独立公开包](https://github.com/wang-d-c/TSP-CMK-Corresponding-Author-Final-Review-20261121/releases/tag/cmk-reviewer-fixes-20261122) · [二轮统计与配置核查](02_统计复算/README_第二轮.md)
