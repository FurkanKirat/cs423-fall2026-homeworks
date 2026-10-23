#!/usr/bin/env python3
"""CS 423 HW2 — turn results/summary.csv into the report's core plots.

Usage (inside the container, after scripts/run_all.sh):
    python3 scripts/plot_results.py results/summary.csv -o plots

Produces (each only if its runs exist in the CSV):
    plots/task2_cycles.png   Task 2.1: cycles of each predictor relative to
                             MinorCPU's default predictor, per workload
    plots/task2_sweep.png    Task 2.2: mispredictions vs. table size on brmany
    plots/task2_ras.png      Task 2.3: mispredicted returns vs. return
                             address stack entries on recurse
    plots/task3_degree.png   Task 3.4: stride-prefetcher speedup over no
                             prefetching vs. degree, one line per MSHR count

Task 4 plots (if you want any) are yours to make: copy and adapt.
"""
import argparse
import csv
import os
import re
from pathlib import Path

# The container runs as the student's host uid, which has no home directory;
# without this, matplotlib warns about an unwritable config dir on every run.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# fixed categorical order (colorblind-validated): blue, orange, aqua
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
INK, INK2, GRID = "#1a1a19", "#5f5e56", "#d9d8d0"
PREDICTORS = ["local", "tournament", "bimode"]
WORKLOADS = ["brbias", "brloop"]


def style(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK2)
    ax.tick_params(colors=INK2, labelcolor=INK)


def plot_task2_cycles(rows, outdir):
    data = {(r["bp"], r["workload"]): r for r in rows if r["pf"] == "none"}
    if not any(("default", w) in data for w in WORKLOADS):
        return None
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=150)
    style(ax)
    width = 0.26
    for k, bp in enumerate(PREDICTORS):
        pos, vals = [], []
        for i, w in enumerate(WORKLOADS):
            if (bp, w) in data and ("default", w) in data:
                v = (float(data[(bp, w)]["numCycles"])
                     / float(data[("default", w)]["numCycles"]))
                pos.append(i + (k - 1) * (width + 0.02))
                vals.append(v)
        ax.bar(pos, vals, width, color=SERIES[k], label=bp, zorder=3)
        for p, v in zip(pos, vals):
            ax.text(p, v, f"{v:.3f}", ha="center", va="bottom", fontsize=7,
                    color=INK2)
    ax.axhline(1.0, color=INK2, linewidth=0.8, linestyle="--")
    ax.set_xticks(range(len(WORKLOADS)), WORKLOADS)
    ax.set_ylabel("cycles / cycles with default predictor\n(lower is better)",
                  color=INK)
    ax.set_title("Task 2.1 — direction predictors, relative cycles",
                 color=INK, fontsize=11)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="lower center",
              bbox_to_anchor=(0.5, -0.32))
    fig.tight_layout()
    path = outdir / "task2_cycles.png"
    fig.savefig(path)
    return path


def plot_task2_sweep(rows, outdir):
    series = {}
    for r in rows:
        m = re.fullmatch(r"brmany-c(\d+)", r["workload"])
        if m and r["pf"] == "none" and r["bp"] in ("local", "bimode"):
            series.setdefault(r["bp"], []).append(
                (int(m.group(1)), int(r["condMispred"] or 0)))
    if not series:
        return None
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=150)
    style(ax)
    for bp in ("local", "bimode"):
        if bp not in series:
            continue
        pts = sorted(series[bp])
        ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o",
                markersize=5, linewidth=2, color=SERIES[PREDICTORS.index(bp)],
                label=bp, zorder=3)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("2-bit counters per direction table", color=INK)
    ax.set_ylabel("mispredicted conditional branches\n(mispredicted_0::DirectCond)",
                  color=INK)
    ax.set_title("Task 2.2 — table size sweep on brmany", color=INK,
                 fontsize=11)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    path = outdir / "task2_sweep.png"
    fig.savefig(path)
    return path


def plot_task2_ras(rows, outdir):
    pts = []
    for r in rows:
        m = re.fullmatch(r"recurse-r(\d+)", r["workload"])
        if m and r["bp"] == "default" and r["pf"] == "none":
            pts.append((int(m.group(1)), int(r["returnMispred"] or 0)))
    if not pts:
        return None
    pts.sort()
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=150)
    style(ax)
    xs = list(range(len(pts)))
    ys = [max(p[1], 1) for p in pts]          # log axis: plot 0 as 1
    ax.bar(xs, ys, 0.6, color=SERIES[0], zorder=3)
    for x, p, y in zip(xs, pts, ys):
        ax.text(x, y * 1.25, f"{p[1]:,}", ha="center", va="bottom",
                fontsize=7, color=INK)
    ax.set_xticks(xs, [str(p[0]) for p in pts])
    ax.set_yscale("log")
    ax.set_ylim(1, max(ys) * 8)
    ax.set_xlabel("return address stack entries (0 = no stack)", color=INK)
    ax.set_ylabel("mispredicted returns\n(mispredicted_0::Return, log scale)",
                  color=INK)
    ax.set_title("Task 2.3 — return address stack size on recurse",
                 color=INK, fontsize=11)
    fig.tight_layout()
    path = outdir / "task2_ras.png"
    fig.savefig(path)
    return path


def plot_task3_degree(rows, outdir):
    none = {}
    lines = {}
    for r in rows:
        if r["bp"] != "default":
            continue
        m = re.fullmatch(r"pfstreams-m(\d+)", r["workload"])
        if m and r["pf"] == "none":
            none[int(m.group(1))] = float(r["numCycles"])
        m = re.fullmatch(r"pfstreams-d(\d+)-m(\d+)", r["workload"])
        if m and r["pf"] == "stride":
            lines.setdefault(int(m.group(2)), []).append(
                (int(m.group(1)), float(r["numCycles"])))
    lines = {k: v for k, v in lines.items() if k in none}
    if not lines:
        return None
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=150)
    style(ax)
    for k, mshrs in enumerate(sorted(lines)):
        pts = sorted(lines[mshrs])
        ax.plot([p[0] for p in pts], [none[mshrs] / p[1] for p in pts],
                marker="o", markersize=5, linewidth=2,
                color=SERIES[k % len(SERIES)], label=f"{mshrs} MSHRs",
                zorder=3)
    ax.set_xscale("log", base=2)
    ax.set_xticks([1, 2, 4, 8], ["1", "2", "4", "8"])
    ax.set_xlabel("prefetch degree", color=INK)
    ax.set_ylabel("speedup over no prefetching\n(same MSHR count)",
                  color=INK)
    ax.set_title("Task 3.4 — stride prefetcher on pfstreams", color=INK,
                 fontsize=11)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    path = outdir / "task3_degree.png"
    fig.savefig(path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("-o", "--outdir", type=Path, default=Path("plots"))
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    with args.csv.open() as fh:
        rows = list(csv.DictReader(fh))
    made = [p for p in (plot_task2_cycles(rows, args.outdir),
                        plot_task2_sweep(rows, args.outdir),
                        plot_task2_ras(rows, args.outdir),
                        plot_task3_degree(rows, args.outdir)) if p]
    if made:
        print("wrote " + ", ".join(str(p) for p in made))
    else:
        print("no plottable runs yet (run scripts/run_all.sh first)")


if __name__ == "__main__":
    main()
