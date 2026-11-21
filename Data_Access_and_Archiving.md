# Data access and archiving

The versioned public release contains the numerical inputs, statistical replay code, and figure materials for the 600-run C/M/K experiment. It also includes numerical results and summaries for the separately timed EAX comparison and the 30-second fixed-start continuation diagnostic. Historical material remains in its original release. [Current versioned release](https://github.com/wang-d-c/TSP-CMK-Corresponding-Author-Final-Review-20261121/releases/tag/cmk-author-review-v3-20261121) · [Historical release](https://github.com/wang-d-c/TSP-SCI-Reproducibility-And-Evidence-20261118/releases/tag/v1.6)

| Task | Access and evidence |
| --- | --- |
| Reproduce the numerical statistics | Use the numerical tables and replay script in the public package. Statistical replay uses saved results and runs no solver. |
| Independently check saved routes | Local integrity and exact EUC_2D checks passed for the 596 saved tours from the main experiment, using the matching maps. Complete city sequences and map inputs require lawful access. External reviewer access to the route archive remains pending permission and a journal-approved channel. |
| Run the full frozen solver workflow | A complete rerun requires the frozen native implementations, their permitted source or build artifacts, matching inputs, and the recorded execution environment and timing controls. Potential reviewers should obtain third-party inputs and upstream sources from their lawful origins. External end-to-end reproductions are not verified by the public release. |

The EAX supplement includes 200 recorded runs, of which 199 produced valid outcomes. The conditional diagnostic includes 120 runs and 60 paired seed effects for three selected parent pools. These public numerical records and summaries do not transfer the underlying EAX or continuation tour archives. The 596-tour archive described above covers the main experiment only.

The GitHub release provides a versioned public snapshot. No Zenodo deposit or DOI has been verified for this version.
