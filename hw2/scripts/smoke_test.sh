#!/usr/bin/env bash
# CS 423 HW2 — end-to-end smoke test. Run INSIDE the course container from
# the hw2/ directory:
#   bash scripts/smoke_test.sh
# Expected: the starter version and tool versions are printed, the workloads
# build, gem5 runs hello on the provided MinorCPU system, and the script
# prints the headline stats. Takes well under a minute.
set -euo pipefail
cd "$(dirname "$0")/.."

STARTER_VERSION="$(sed -n 's/^STARTER_VERSION = "\(.*\)"$/\1/p' configs/hw2.py)"

echo "== [0/3] versions (quote this block in your report's setup statement) =="
echo "starter:   ${STARTER_VERSION:-unknown}"
echo "gem5:      $(cat /opt/gem5/GEM5_VERSION 2>/dev/null || echo unknown)"
echo "cross-gcc: $(riscv64-linux-gnu-gcc -dumpfullversion 2>/dev/null || echo unknown)"
echo "python3:   $(python3 --version 2>&1 | cut -d' ' -f2)"

echo "== [1/3] cross-compiling workloads =="
make -C workloads

echo "== [2/3] running hello on the provided system (scalar MinorCPU) =="
gem5.opt --outdir=results/smoke configs/hw2.py --cmd workloads/bin/hello

echo "== [3/3] headline stats from results/smoke/stats.txt =="
grep -E "^(simInsts|simSeconds|hostSeconds)\s" results/smoke/stats.txt
grep -E "^system\.cpu\.(numCycles|branchPred\.(committed|mispredicted)_0::DirectCond)\s" \
    results/smoke/stats.txt

echo "STARTER VERSION: ${STARTER_VERSION:-unknown}"
echo "SMOKE TEST PASSED"
