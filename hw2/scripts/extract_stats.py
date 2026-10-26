#!/usr/bin/env python3
"""CS 423 HW2 — collect headline stats from gem5 results into one CSV.

Usage (inside or outside the container):
    python3 scripts/extract_stats.py results -o results/summary.csv

Expects the run_all.sh naming convention:
    results/<bp>-<pf>-<workload>[-<variant>]/stats.txt
where <bp> is default|local|tournament|bimode|custom and <pf> is
none|nextline|stride|custom. Directories that do not follow it (smoke/, trace/)
are skipped. Reports raw counts only; the derived metrics of the handout
(misprediction rate aside) are yours to compute.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

BPS = {"default", "local", "tournament", "bimode", "custom"}
PFS = {"none", "nextline", "stride", "custom"}

# stat name in stats.txt -> CSV column
WANTED = {
    "simInsts": "simInsts",
    "simSeconds": "simSeconds",
    "hostSeconds": "hostSeconds",
    "system.cpu.numCycles": "numCycles",
    # branch unit (direction predictor + BTB + RAS + indirect predictor)
    # conditional branches, counted when they COMMIT (no wrong-path ones):
    # use these for misprediction rates of conditional branches
    "system.cpu.branchPred.committed_0::DirectCond": "condCommitted",
    "system.cpu.branchPred.mispredicted_0::DirectCond": "condMispred",
    # gem5's condPredicted counts conditional-branch LOOKUPS (incl. the
    # wrong path); condIncorrect counts committed mispredictions of ALL
    # branch types (returns, indirect jumps, ...). Kept for reference only.
    "system.cpu.branchPred.condPredicted": "condPredicted",
    "system.cpu.branchPred.condIncorrect": "condIncorrect",
    "system.cpu.branchPred.mispredictDueToPredictor_0::DirectCond":
        "mispredDueToPredictor",
    "system.cpu.branchPred.mispredictDueToBTBMiss_0::DirectCond":
        "mispredDueToBTBMiss",
    # target prediction: returns (RAS) and indirect jumps, committed and
    # mispredicted (Tasks 2.3 and 2.4)
    "system.cpu.branchPred.committed_0::Return": "returns",
    "system.cpu.branchPred.mispredicted_0::Return": "returnMispred",
    "system.cpu.branchPred.committed_0::IndirectUncond": "indirectJumps",
    "system.cpu.branchPred.mispredicted_0::IndirectUncond":
        "indirectMispred",
    # L1 data cache, demand (load + store) accesses
    "system.cpu.dcache.demandHits::total": "dHits",
    "system.cpu.dcache.demandMisses::total": "dMisses",
    "system.cpu.dcache.demandMshrHits::total": "dMshrHits",
    "system.cpu.dcache.demandMshrMisses::total": "dMshrMisses",
    # time the loads waited for misses, in ticks (Task 3.2(b))
    "system.cpu.dcache.ReadReq.missLatency::total": "readMissLatency",
    "system.cpu.dcache.ReadReq.mshrMissLatency::total": "readMshrMissLatency",
    "system.cpu.dcache.ReadReq.mshrHits::total": "readMshrHits",
    # L1 data-cache prefetcher (absent when --pf none)
    "system.cpu.dcache.prefetcher.pfIssued": "pfIssued",
    "system.cpu.dcache.HardPFReq.mshrMisses::total": "pfSent",
    "system.cpu.dcache.prefetcher.pfUnused": "pfUnused",
    "system.cpu.dcache.prefetcher.pfUseful": "pfUseful",
    "system.cpu.dcache.prefetcher.accuracy": "gem5Accuracy",
}

LINE_RE = re.compile(r"^(\S+)\s+([-\d.e+na]+)")


def parse_stats(path: Path) -> dict:
    out = {}
    with path.open() as fh:
        for line in fh:
            if line.startswith("---------- End Simulation Statistics"):
                break      # only the first (whole-run) dump
            m = LINE_RE.match(line)
            if m and m.group(1) in WANTED:
                out[WANTED[m.group(1)]] = m.group(2)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="CSV path (default: stdout)")
    args = ap.parse_args()

    rows = []
    for stats in sorted(args.results_dir.glob("*/stats.txt")):
        tag = stats.parent.name
        parts = tag.split("-", 2)
        if len(parts) < 3 or parts[0] not in BPS or parts[1] not in PFS:
            continue           # not a <bp>-<pf>-<workload> run
        vals = parse_stats(stats)
        if "simInsts" not in vals:
            print(f"warning: {stats} has no simInsts (run failed?), skipping",
                  file=sys.stderr)
            continue
        insts = float(vals["simInsts"])
        cycles = float(vals.get("numCycles", "nan"))
        pred = float(vals.get("condCommitted", "nan"))
        wrong = float(vals.get("condMispred", "nan"))
        row = {
            "run": tag,
            "bp": parts[0],
            "pf": parts[1],
            "workload": parts[2],
            "simInsts": int(insts),
            "numCycles": int(cycles),
            "cpi": f"{cycles / insts:.4f}",
            "mispredRate": (f"{wrong / pred:.6f}" if pred == pred and pred
                            else ""),
        }
        for col in WANTED.values():
            if col not in row and col not in ("simInsts", "numCycles"):
                row[col] = vals.get(col, "")
        rows.append(row)

    if not rows:
        print("no stats.txt found — did you run scripts/run_all.sh?",
              file=sys.stderr)
        return 1

    fieldnames = list(rows[0].keys())
    out = args.output.open("w", newline="") if args.output else sys.stdout
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    if args.output:
        out.close()
        print(f"wrote {args.output} ({len(rows)} runs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
