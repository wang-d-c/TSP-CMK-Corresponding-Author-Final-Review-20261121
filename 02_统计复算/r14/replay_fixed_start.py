"""Reconstruct the frozen fixed-start diagnostic and optionally render Figure 5."""

import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
import sys


FROZEN_REPORT = {
    "outcomes_120.csv": "8fe87628d2ae008ec037456ce4d39b701922ffa0c826d51e162aa8b7eb3004d8",
    "pairs_60.csv": "db8874f42a9c60aec80372601750feb4ab821036bdf02293ac6c61420bb33283",
    "diagnostics_summary.json": "ecb6b137b60227e3eb4f9194757c63f43c68ac0bee4033e2ae53b04439251bc6",
}
PLAN_SHA256 = "a29877a03404afb94ed556591ef1967d468a95f3222083a243ff4fe58a27916d"
POOLS = ("C10k.0/981", "genC15k.seed100004/2521", "genC15k.seed100004/1861")
ORDERS = ("M_first", "K_first")
ARMS = ("M_parent", "K_selected")
RESAMPLES = 10_000


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def verify_plan(outcomes, plan_path):
    require(sha256(plan_path) == PLAN_SHA256, "Frozen diagnostic plan hash mismatch")
    plan = read_csv(plan_path)
    keys = ("slot", "run_id", "map", "pool_seed", "start", "continuation_seed", "within_pair")
    require(len(plan) == len(outcomes), "Frozen plan and outcome counts differ")
    for registered, observed in zip(plan, outcomes, strict=True):
        require(all(registered[key] == observed[key] for key in keys),
                f"Outcome does not match the frozen plan at slot {registered['slot']}")


def rebuild_pairs(outcomes):
    require(len(outcomes) == 120, "Expected 120 diagnostic outcomes")
    require([int(row["slot"]) for row in outcomes] == list(range(1, 121)),
            "Outcome slots are not 1–120 in frozen order")
    require(len({row["run_id"] for row in outcomes}) == 120, "Duplicate run ID")
    grouped = defaultdict(dict)
    start_evidence = defaultdict(set)
    for row in outcomes:
        pool = f"{row['map']}/{row['pool_seed']}"
        arm = row["start"]
        seed = int(row["continuation_seed"])
        require(pool in POOLS and arm in ARMS and row["status"] == "valid",
                f"Unexpected pool, arm or status at slot {row['slot']}")
        require(arm not in grouped[pool, seed], f"Duplicate outcome for {pool}/{seed}/{arm}")
        for prefix in ("start", "end"):
            require(int(row[f"{prefix}_length"]) > 0 and
                    re.fullmatch("[0-9a-f]{64}", row[f"{prefix}_sha256"]),
                    f"Invalid route metadata at slot {row['slot']}")
        start_evidence[pool, arm].add((row["start_length"], row["start_sha256"]))
        grouped[pool, seed][arm] = row
    require(all(len(evidence) == 1 for evidence in start_evidence.values()),
            "Start identity changed within a pool and arm")

    pairs = []
    audit = []
    for (pool, seed), arms in grouped.items():
        require(set(arms) == set(ARMS), f"Missing arm in {pool}/{seed}")
        m, k = (arms[arm] for arm in ARMS)
        m_slot, k_slot = int(m["slot"]), int(k["slot"])
        require(abs(m_slot - k_slot) == 1 and
                (m["within_pair"], k["within_pair"]) ==
                (("1", "2") if m_slot < k_slot else ("2", "1")),
                f"Inconsistent pair order in {pool}/{seed}")
        m_end, k_end = int(m["end_length"]), int(k["end_length"])
        pairs.append({
            "pool": pool, "continuation_seed": seed,
            "order": "M_first" if m_slot < k_slot else "K_first",
            "M_status": m["status"], "K_status": k["status"], "M_end": m_end, "K_end": k_end,
            "K_over_M_ppm": float(Fraction(1_000_000 * (m_end - k_end), m_end)),
        })
        audit.append({"M_slot": m_slot, "K_slot": k_slot, "M_run_id": m["run_id"], "K_run_id": k["run_id"]})
    require(len(pairs) == 60, "Expected 60 complete diagnostic pairs")
    seeds = [{row["continuation_seed"] for row in pairs if row["pool"] == pool} for pool in POOLS]
    require(len(seeds[0]) == 20 and seeds.count(seeds[0]) == len(POOLS),
            "Each pool must have the same 20 continuation seeds")
    require(Counter((row["pool"], row["order"]) for row in pairs) ==
            Counter({(pool, order): 10 for pool in POOLS for order in ORDERS}),
            "Expected 10 pairs per pool and execution order")
    return pairs, audit


def summarize(values, seed):
    # Preserve the frozen statistic, sample order, generator and interpolation rule.
    generator = random.Random(seed)
    means = sorted(statistics.mean(generator.choices(values, k=len(values))) for _ in range(RESAMPLES))
    interval = []
    for quantile in (0.025, 0.975):
        location = (len(means) - 1) * quantile
        index = int(location)
        interval.append(means[index] + (location - index) * (means[index + 1] - means[index]))
    return {
        "pairs": len(values),
        "short_tied_long": [sum(v > 0 for v in values), sum(v == 0 for v in values), sum(v < 0 for v in values)],
        "mean_ppm": statistics.mean(values),
        "median_ppm": statistics.median(values),
        "range_ppm": [min(values), max(values)],
        "seed_bootstrap_95_percentile_interval": interval,
    }


def reconstruct_statistics(pairs, expected):
    groups = []
    for pool_index, pool in enumerate(POOLS):
        pool_rows = [row for row in pairs if row["pool"] == pool]
        reference = expected["pool_summaries"][pool]
        for label, subset, seed, frozen in [
            ("all_orders", pool_rows, 20261121 + pool_index, reference["paired"]),
            *((order, [row for row in pool_rows if row["order"] == order],
               20261125 + 2 * pool_index + order_index, reference["by_order"][order])
              for order_index, order in enumerate(ORDERS)),
        ]:
            result = summarize([row["K_over_M_ppm"] for row in subset], seed)
            require(result == frozen, f"Recorded statistic mismatch for {pool}/{label}")
            short, tied, long = result["short_tied_long"]
            lower, upper = result["seed_bootstrap_95_percentile_interval"]
            minimum, maximum = result["range_ppm"]
            groups.append({
                "pool": pool, "subset": label, "pairs": result["pairs"],
                "K_shorter": short, "tied": tied, "K_longer": long,
                "mean_ppm": result["mean_ppm"], "median_ppm": result["median_ppm"],
                "min_ppm": minimum, "max_ppm": maximum, "ci95_low_ppm": lower,
                "ci95_high_ppm": upper, "bootstrap_seed": seed, "bootstrap_draws": RESAMPLES,
            })
    return groups


def plotting_data(pairs, audit):
    ranks = Counter()
    plot_rows = []
    for row, pair_audit in zip(pairs, audit, strict=True):
        pool, order = row["pool"], row["order"]
        index = ranks[pool, order]
        ranks[pool, order] += 1
        offset = (-0.24 if order == "M_first" else -0.10) + 0.009 * (index - 4.5)
        plot_y = 2 - POOLS.index(pool) + offset
        plot_rows.append({**row, **pair_audit, "plot_y": plot_y})
    return plot_rows


def plot(points, groups, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    matplotlib.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "font.size": 9})
    figure, axis = plt.subplots(figsize=(7.35, 3.35))
    figure.subplots_adjust(left=0.265, right=0.97, bottom=0.19, top=0.86)
    styles = {"M_first": ("M first", "o", "#28627B"), "K_first": ("K first", "^", "#926132")}
    axis.axvline(0, color="#565656", linewidth=0.85, linestyle=(0, (4, 3)), zorder=1)
    for order, (label, marker, color) in styles.items():
        rows = [row for row in points if row["order"] == order]
        axis.scatter([row["K_over_M_ppm"] for row in rows], [row["plot_y"] for row in rows],
                     s=20, marker=marker, label=label, facecolors="white", edgecolors=color,
                     linewidths=0.8, zorder=3)
    for group in groups:
        if group["subset"] != "all_orders":
            continue
        y = 2 - POOLS.index(group["pool"]) + 0.18
        low, center, high = (group[key] for key in ("ci95_low_ppm", "mean_ppm", "ci95_high_ppm"))
        axis.errorbar(center, y, xerr=[[center - low], [high - center]], fmt="D", markersize=3.9,
                      linewidth=1.1, capsize=3, color="#202020", zorder=4)
    axis.set_yticks([2, 1, 0], POOLS)
    axis.set_ylim(-0.42, 2.34)
    axis.set_xlabel("Final route improvement of K over M (ppm)")
    axis.set_axisbelow(True)
    axis.grid(axis="x", color="#e4e4e4", linewidth=0.55)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0)
    handles, labels = axis.get_legend_handles_labels()
    handles.append(Line2D([0], [0], color="#202020", marker="D", markersize=4, linewidth=1.1))
    labels.append("Pool mean and 95% interval")
    axis.legend(handles, labels, ncol=3, loc="lower center", bbox_to_anchor=(0.50, 1.035),
                frameon=False, borderaxespad=0, handletextpad=0.5, columnspacing=1.2)
    metadata = {"Title": "Fixed-start diagnostic: all 60 paired outcomes",
                "Subject": "Paired seed effects and per-pool bootstrap intervals", "CreationDate": None}
    figure.savefig(output / "figure5_fixed_start.pdf", metadata=metadata)
    figure.savefig(output / "figure5_fixed_start.png", dpi=400)
    plt.close(figure)
    return matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Directory containing the three frozen diagnostic report files")
    parser.add_argument("output", type=Path, help="A new output directory")
    parser.add_argument("--plan", type=Path, help="Optional frozen diagnostic_plan_120.csv for slot-level validation")
    parser.add_argument("--plot", action="store_true", help="Also render vector PDF and 400-dpi PNG with Matplotlib")
    args = parser.parse_args()

    hashes = {name: sha256(args.source / name) for name in FROZEN_REPORT}
    require(hashes == FROZEN_REPORT, "At least one input differs from the frozen report bytes")
    outcomes = read_csv(args.source / "outcomes_120.csv")
    if args.plan:
        verify_plan(outcomes, args.plan)
    pairs, audit = rebuild_pairs(outcomes)
    saved_pairs = read_csv(args.source / "pairs_60.csv")
    require([{key: str(value) for key, value in row.items()} for row in pairs] == saved_pairs,
            "At least one reconstructed pair differs from the corresponding frozen row")
    expected = json.loads((args.source / "diagnostics_summary.json").read_text(encoding="utf-8-sig"))
    require(expected["planned_runs"] == len(outcomes) and expected["statuses"] == {"valid": len(outcomes)} and
            expected["planned_seed_pairs"] == len(pairs) and expected["plan_sha256"] == PLAN_SHA256,
            "Recorded coverage or plan digest differs from source data")
    groups = reconstruct_statistics(pairs, expected)
    points = plotting_data(pairs, audit)

    args.output.mkdir()
    write_csv(args.output / "r14_rebuilt_pairs.csv", pairs)
    write_csv(args.output / "r14_statistics.csv", groups)
    write_csv(args.output / "r14_plot_data.csv", points)
    matplotlib_version = plot(points, groups, args.output) if args.plot else None
    outputs = {path.name: sha256(path) for path in sorted(args.output.iterdir()) if path.is_file()}
    write_json(args.output / "r14_replay_receipt.json", {
        "protocol": "30-second conditional fixed-start diagnostic; fixed pools in two maps",
        "inputs_sha256": hashes,
        "run_plan_sha256": PLAN_SHA256,
        "run_plan_identity_verified": bool(args.plan),
        "outcomes_validated": len(outcomes),
        "complete_pairs_matching_frozen_reference": len(pairs),
        "statistics_groups_matching_frozen_reference": len(groups),
        "bootstrap_intervals_matching_exactly": len(groups),
        "bootstrap_draws_per_group": RESAMPLES,
        "python": sys.version.split()[0],
        "matplotlib": matplotlib_version,
        "outputs": outputs,
        "scope": "CSV and frozen-statistic replay; does not rerun native search or revalidate route geometry",
    })
    print(f"Verified {len(outcomes)} outcomes, {len(pairs)} pairs, {len(groups)} exact bootstrap intervals.")


if __name__ == "__main__":
    main()
