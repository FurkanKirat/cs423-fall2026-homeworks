#!/usr/bin/env python3
"""CS 423 HW2 — Bonus Task 5 score: your design vs. the best baseline on
each workload of the fixed evaluation suites.

Usage (after `bash scripts/run_all.sh task5`, which ends with
extract_stats.py):
    python3 scripts/task5_score.py results/summary.csv

For each suite workload w:
    best baseline   = the baseline run of w with the FEWEST cycles (chosen
                      per workload: it can differ between workloads)
    speedup(w)      = cycles(best baseline) / cycles(your design)
and the score of the design is the geometric mean of speedup(w) over the
suite. A score of at least 1.005 beats the baselines (handout).

Suites and baselines (handout, Bonus Task 5):
    5.1  brbias brloop brmany brhist brperiod; baselines: LocalBP, TournamentBP,
         BiModeBP (default sizes); yours: custom-none-<w>
    5.2  pfstreams pfdelta pfregions (4 MSHRs); baselines: next-line and
         stride, degree 1, 2 and 4; yours: default-custom-<w>-m4

Comparing several designs: run each design, then rename (or copy) its
custom result directories with a suffix, re-extract, and score each suffix:
    bash scripts/run_all.sh task5bp            # design A in slot 3
    for w in brbias brloop brmany brhist brperiod; do
        mv results/custom-none-$w results/custom-none-$w-A; done
    ... switch slot 3 to design B, run task5bp again, rename with -B ...
    python3 scripts/extract_stats.py results -o results/summary.csv
    python3 scripts/task5_score.py results/summary.csv --suffix=-A
    python3 scripts/task5_score.py results/summary.csv --suffix=-B
(prefetchers: the directories are results/default-custom-*-m4). Write
--suffix=-A with "=": a value that starts with "-" needs it. Without
--suffix, the runs without a suffix (the last design you ran) are scored.
The score is printed with 4 decimals: "beats" means >= 1.0050.
"""
import argparse
import csv
import math
import sys
from pathlib import Path

BP_SUITE = ["brbias", "brloop", "brmany", "brhist", "brperiod"]
BP_BASE = ["local", "tournament", "bimode"]
PF_SUITE = ["pfstreams", "pfdelta", "pfregions"]
BEAT = 1.005       # handout: below half a percent is not a mechanism
PF_BASE = [f"{pf}-d{d}" for pf in ("nextline", "stride") for d in (1, 2, 4)]


def geomean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


def score(title, suite, base_tags, custom_tag, none_tag, runs, extra):
    print(f"== {title} ==")
    hdr = f"{'workload':<10} {'best baseline':<22} {'cycles':>12} " \
          f"{'yours':>12} {'speedup':>8}"
    if extra:
        hdr += f"  {extra[0]:>16} {extra[0] + ' (yours)':>16}"
    print(hdr)
    speedups = []
    for w in suite:
        base = {name: runs.get(tag(w)) for name, tag in base_tags.items()}
        missing = [n for n, r in base.items() if r is None]
        mine = runs.get(custom_tag(w))
        if missing or mine is None:
            print(f"{w:<10} missing runs: "
                  f"{', '.join(missing + ([] if mine else ['yours']))}")
            continue
        best = min(base, key=lambda n: int(base[n]["numCycles"]))
        c_best = int(base[best]["numCycles"])
        c_mine = int(mine["numCycles"])
        sp = c_best / c_mine
        speedups.append(sp)
        line = f"{w:<10} {best:<22} {c_best:>12,} {c_mine:>12,} {sp:>8.4f}"
        if extra:
            col = extra[1]
            line += f"  {base[best].get(col, ''):>16} {mine.get(col, ''):>16}"
        if none_tag and none_tag(w) in runs:
            c_none = int(runs[none_tag(w)]["numCycles"])
            line += f"   (vs. no prefetching: best baseline " \
                    f"{c_none / c_best:.3f}x, yours {c_none / c_mine:.3f}x)"
        print(line)
    if len(speedups) == len(suite):
        g = geomean(speedups)
        print(f"{'geomean':<10} {'':<22} {'':>12} {'':>12} {g:>8.4f}   -> "
              f"{'BEATS the baselines' if g >= BEAT else 'does not beat the baselines'}"
              f" (beats means >= {BEAT})")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("--suffix", default="")
    args = ap.parse_args()
    with args.csv.open() as fh:
        runs = {r["run"]: r for r in csv.DictReader(fh)}
    sfx = args.suffix
    score("Bonus 5.1: direction predictor", BP_SUITE,
          {bp: (lambda w, bp=bp: f"{bp}-none-{w}") for bp in BP_BASE},
          lambda w: f"custom-none-{w}{sfx}", None, runs,
          ("condMispred", "condMispred"))
    score("Bonus 5.2: L1D prefetcher (4 MSHRs)", PF_SUITE,
          {b: (lambda w, b=b: "default-{}-{}-{}-m4".format(
              b.split("-")[0], w, b.split("-")[1])) for b in PF_BASE},
          lambda w: f"default-custom-{w}-m4{sfx}",
          lambda w: f"default-none-{w}-m4", runs, None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
