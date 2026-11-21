"""Render every audited map contrast and a labeled near-zero detail panel."""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("table", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    with args.table.open(encoding="utf-8-sig", newline="") as source:
        rows = {(r["method"], r["map"]): r for r in csv.DictReader(source)}
    names = sorted({name for _, name in rows}, key=lambda n: (int(rows["M_new", n]["cities"]), n))
    assert len(rows) == len(names) * 2 == 40
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8.5, "axes.labelsize": 8.5,
        "axes.titlesize": 9.5, "pdf.fonttype": 42,
    })
    figure, (full, detail) = plt.subplots(1, 2, figsize=(10.9, 5.7),
                                          gridspec_kw={"width_ratios": [1.3, 1.0]}, layout="constrained")
    style = (("M_new", "o", "#286c94"), ("K_new", "^", "#b35632"))
    near = [name for name in names if max(abs(float(rows[m, name]["mean_ppm"])) for m, _, _ in style) < 400]
    for panel, selected, title in (
        (full, names, "A. All 20 maps"),
        (detail, near, "B. Near-zero detail, 5 maps"),
    ):
        panel.axvline(0, linestyle="--", linewidth=.85, color="#545454")
        for index, (method, marker, color) in enumerate(style):
            values = [float(rows[method, name]["mean_ppm"]) for name in selected]
            dy = -0.12 if index == 0 else 0.12
            panel.scatter(values, [y + dy for y in range(len(values))], s=22,
                          marker=marker, color=color, label=f"{method[0]} versus EAX", zorder=3)
        panel.set_yticks(range(len(selected)),
                         labels=[f"{name}    ({int(rows['M_new', name]['cities']):,})" for name in selected])
        panel.invert_yaxis()
        panel.set_xlabel("Within-map mean shortening (ppm)")
        panel.set_title(title, loc="left")
        panel.grid(axis="x", linewidth=.5, alpha=.3)
        panel.spines[["top", "right", "left"]].set_visible(False)
        panel.tick_params(axis="y", length=0)
        panel.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    full.set_xlim(-8_000, 255_000)
    full.set_xticks([0, 50_000, 100_000, 150_000, 200_000, 250_000])
    detail.set_xlim(-380, 110)
    detail.set_xticks([-350, -250, -150, -50, 50])
    detail.legend(loc="upper left", frameon=False)
    args.output.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        figure.savefig(args.output / f"EAX_map_effects_and_near_zero_detail.{ext}", dpi=300)
    plt.close(figure)


if __name__ == "__main__":
    main()
