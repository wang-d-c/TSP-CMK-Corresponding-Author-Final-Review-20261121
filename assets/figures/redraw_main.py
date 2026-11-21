"""Restyle Figures 1–4 using frozen numeric exports; preserve Figure 5 bytes."""

import csv
from hashlib import sha256
import json
from math import isclose
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


HERE = Path(__file__).resolve().parent
STATS = "03_数据与复算/复算产物"
EXPLORE = "02_方法与统计补充/当前批次探索分析/results"
R14 = "08_独立补验与执行证据/条件续搜120/report_final"
ART = "assets/figures"
FIGURES = {
    "fig1_primary": ("overall_effects_95ci.png", STATS),
    "fig2_maps": ("map_effects.png", STATS),
    "fig3_start_finish": ("cmk_start_vs_finish.png", EXPLORE),
    "fig4_order": ("cmk_order_sensitivity.png", EXPLORE),
    "fig5_r14": ("R14_paired_distribution.png", R14),
}
COLORS = dict(zip(("01", "02", "03", "04"), ("#226A95", "#B54B30", "#258273", "#7B619C")))
STRATA = dict(zip(("01", "02", "03", "04"), ("VLSI", "Clustered", "Uniform", "Geographic")))
CONTRASTS = {"K_new/M_new": "K/M", "K_new/C_ref": "K/C", "M_new/C_ref": "M/C"}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def save(fig, output, name):
    fig.savefig(output / f"{name}.png", dpi=340)
    fig.savefig(output / f"{name}.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def zero(ax, vertical=True):
    method = ax.axvline if vertical else ax.axhline
    method(0, color="#667079", ls=(0, (3, 2)), lw=0.85, zorder=1)


def draw(source, output):
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.5, "axes.labelsize": 10.5,
        "axes.spines.right": False, "axes.spines.top": False, "pdf.fonttype": 42,
        "axes.edgecolor": "#6E7680", "grid.color": "#C2CAD0", "grid.alpha": 0.48,
        "figure.facecolor": "white", "axes.unicode_minus": True, "legend.fontsize": 9,
    })
    line = "#226A95"

    stats_path = source / STATS / "statistical_reproduction.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8-sig"))["effects"]
    fig, ax = plt.subplots(figsize=(8.2, 2.3), layout="constrained")
    for i, (key, name) in enumerate(CONTRASTS.items()):
        obj = stats[key]
        avg = obj["mean_ppm"]
        lo, hi = obj["ci95_pct_map_bootstrap_ppm"]
        ax.errorbar(avg, i, xerr=[[avg - lo], [hi - avg]], fmt="o" if i == 0 else "s",
                    color=line if i == 0 else "#313C48", capsize=4, lw=1.5)
    ax.set(yticks=list(range(3)), yticklabels=list(CONTRASTS.values()), ylim=(2.5, -.5),
           xlabel="Map-equal route-length reduction (ppm)")
    zero(ax)
    ax.grid(axis="x", lw=.55)
    save(fig, output, "fig1_primary")

    map_path = source / STATS / "map_effects.csv"
    data = rows(map_path)
    ordered = sorted({(r["stratum"][:2], r["map"]) for r in data})
    assert len(data) == 60 and len(ordered) == 20
    fig, axes = plt.subplots(1, 3, sharex=True, sharey=True, figsize=(10, 5.15), layout="constrained")
    for ax, (key, name) in zip(axes, CONTRASTS.items()):
        values = {r["map"]: float(r["mean_reduction_ppm"]) for r in data if r["comparison"] == key}
        ax.scatter([values[m] for _, m in ordered], range(20), c=[COLORS[s] for s, _ in ordered], s=23, zorder=4)
        ax.set(title=name, xlabel="Reduction (ppm)")
        zero(ax)
        ax.grid(axis="x", lw=.55)
    axes[0].set_yticks(range(20), [m for _, m in ordered], fontsize=9.5)
    axes[0].set_ylim(19.75, -.75)
    save(fig, output, "fig2_maps")

    pair_path = source / EXPLORE / "start_end_pairs.csv"
    data = rows(pair_path)
    shorter = [r for r in data if r["start_relation"] == "shorter"]
    same = [r for r in data if r["start_relation"] == "same_sha256"]
    assert (len(data), len(shorter), len(same)) == (198, 181, 17)
    assert sum(r["final_relation"] == "tied" for r in same) == 15
    assert sum(r["final_relation"] == "longer" for r in shorter) == 71
    xkey, ykey = "start_advantage_ppm", "final_advantage_ppm"
    xs = [float(r[xkey]) for r in data]
    ys = [float(r[ykey]) for r in data]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout="constrained")
    for ax, caption in zip(axes, ("(a) All 198 valid pairs", "(b) Central view, same pairs")):
        for stratum, setting in STRATA.items():
            group = [r for r in shorter if r["stratum"].startswith(stratum)]
            ax.scatter([float(r[xkey]) for r in group], [float(r[ykey]) for r in group], c=COLORS[stratum],
                       s=20, edgecolors="white", lw=.25, alpha=.8, label=setting, zorder=3)
        ax.scatter([float(r[xkey]) for r in same], [float(r[ykey]) for r in same], s=33, edgecolors="#263746",
                   facecolors="white", lw=.9, label="Same starting bytes", zorder=4)
        ax.plot([-40, max(xs) * 1.06], [-40, max(xs) * 1.06], color="#34495E", ls=(0, (5, 2)),
                lw=1.1, label=r"$y=x$", zorder=2)
        zero(ax)
        zero(ax, False)
        ax.set(xlabel="K start reduction (ppm)", title=caption)
        ax.grid(lw=.55)
    axes[0].set(ylabel="K final reduction (ppm)", xlim=(-40, max(xs) * 1.06), ylim=(min(ys) - 140, max(ys) + 140))
    axes[1].set(xlim=(-25, 265), ylim=(-350, 350))
    for record in sorted(data, key=lambda r: float(r[ykey]))[:3]:
        tag = f"{record['map'].split('.seed')[0]}/{record['seed']}"
        axes[0].annotate(tag, (float(record[xkey]), float(record[ykey])), textcoords="offset points",
                         xytext=(6, 1), fontsize=8.5)
    axes[1].annotate("15 coincident ties", xy=(0, 0), xytext=(64, -130),
                     arrowprops={"arrowstyle": "-", "lw": .7}, fontsize=8.5)
    losses = [float(r[ykey]) for r in same if r["final_relation"] == "longer"]
    assert len(losses) == 2
    axes[1].annotate("Two near-coincident one-unit losses", xy=(0, sum(losses) / 2), xytext=(28, 270),
                     arrowprops={"arrowstyle": "-", "lw": .7}, fontsize=8.5)
    handles, labels = axes[1].get_legend_handles_labels()
    axes[0].legend(handles, labels, ncol=2, loc="lower right", facecolor="white", framealpha=.94)
    save(fig, output, "fig3_start_finish")

    order_path = source / EXPLORE / "order_by_map.csv"
    order_rows = sorted(rows(order_path), key=lambda r: (r["stratum"], r["map"]))
    assert len(order_rows) == 20
    fig, (left, right) = plt.subplots(1, 2, sharey=True, figsize=(10, 4.55), layout="constrained")
    diffs = []
    for i, r in enumerate(order_rows):
        lo, hi = (float(r[k]) for k in ("M_first_ppm", "K_first_ppm"))
        delta = float(r["K_first_minus_M_first_ppm"])
        assert isclose(delta, hi - lo, abs_tol=1e-9)
        diffs.append(delta)
        color = COLORS[r["stratum"][:2]]
        left.plot([lo, hi], [i, i], color=color, lw=.85, alpha=.5)
        left.scatter(lo, i, facecolors="white", edgecolor=color, s=32, zorder=3)
        left.scatter(hi, i, c=color, marker="D", s=24, zorder=3)
        right.scatter(delta, i, c=color, s=25, zorder=3)
    left.set(title="(a) Within-map effects", xlabel="Final reduction (ppm)")
    right.set(title="(b) Within-map order differences", xlabel="K first minus M first (ppm)")
    left.set_yticks(range(20), [r["map"] for r in order_rows], fontsize=9.5)
    left.set_ylim(19.75, -.75)
    for ax in (left, right):
        zero(ax)
        ax.grid(axis="x", lw=.55)
        for y in (4.5, 9.5, 14.5):
            ax.axhline(y, color="#CCD4D9", lw=.5)
    left.legend(handles=[
        Line2D([], [], marker="o", fillstyle="none", color="#263746", ls="", label="M first"),
        Line2D([], [], marker="D", color="#263746", ls="", label="K first"),
    ], loc="lower left", framealpha=.94)
    average = sum(diffs) / len(diffs)
    right.axvline(average, color=line, ls=(0, (4, 2)), lw=1.35, label=f"Map mean {average:+.2f} ppm")
    right.legend(loc="lower right", framealpha=.94)
    save(fig, output, "fig4_order")

    r14_path = source / R14 / "pairs_60.csv"
    summary_path = source / R14 / "diagnostics_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
    assert len(rows(r14_path)) == 60 and summary["planned_seed_pairs"] == 60
    for ext in ("png", "pdf"):
        original = source / R14 / f"R14_paired_distribution.{ext}"
        copied = output / f"fig5_r14.{ext}"
        shutil.copyfile(original, copied)
        assert digest(original) == digest(copied)
    receipt = {
        "inputs": {str(p.relative_to(source)).replace("\\", "/"): digest(p) for p in (
            stats_path, map_path, pair_path, order_path, r14_path, summary_path,
            source / R14 / "R14_paired_distribution.png", source / R14 / "R14_paired_distribution.pdf",
        )},
        "outputs": {p.name: digest(p) for p in sorted(output.iterdir()) if p.suffix in (".png", ".pdf")},
        "figure3": {"plotted_pairs": len(data), "byte_identical_starts": len(same), "shorter_starts": len(shorter),
                    "all_negative_tail_points_retained": True, "y_equals_x_in_both_panels": True},
        "figure4_map_count": len(order_rows),
        "figure5": {"valid_seed_pairs": len(rows(r14_path)), "original_image_bytes": True, "pools": 3},
    }
    (output / "plot_provenance.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse

    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("package", type=Path)
    cli.add_argument("output", type=Path)
    args = cli.parse_args()
    draw(args.package, args.output)
