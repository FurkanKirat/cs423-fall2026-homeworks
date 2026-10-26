#!/usr/bin/env bash
# CS 423 HW2 — OPTIONAL, Bonus Task 5 route B only. Builds hw2/gem5/ (made by
# scripts/get_gem5_source.sh) into hw2/gem5/build/RISCV/gem5.opt.
# Run INSIDE the course container from the hw2/ directory:
#   bash scripts/build_gem5.sh            # 2 parallel compile jobs (default)
#   JOBS=8 bash scripts/build_gem5.sh     # more jobs: only with >= 10 GB
# Memory (measured, see the handout): Docker needs at least 6 GB, and with
# 6 GB use JOBS=2 (4 jobs were killed for lack of memory); one job per core
# on 8 cores peaked near 9 GB. The final link step alone needs more than
# 4 GB even with --limit-ld-memory-usage (below).
# The first build compiles all of gem5 and takes long (the handout gives
# measured times); later builds recompile only what you changed.
set -euo pipefail
cd "$(dirname "$0")/.."

[ -f gem5/SConstruct ] || { echo "!! gem5/ not found: run scripts/get_gem5_source.sh first" >&2; exit 1; }
JOBS="${JOBS:-2}"     # default 2: fits in 6 GB of Docker memory
echo "== building with JOBS=$JOBS (if the build is killed, retry with JOBS=2; it resumes) =="
export HOME="${HOME:-/tmp}"
[ -w "$HOME" ] || export HOME=/tmp

start=$(date +%s)
(cd gem5 && scons build/RISCV/gem5.opt -j"$JOBS" --ignore-style \
    --limit-ld-memory-usage)
end=$(date +%s)
echo "== built gem5/build/RISCV/gem5.opt in $((end - start)) s (JOBS=$JOBS) =="
echo "run with: GEM5=gem5/build/RISCV/gem5.opt bash scripts/run_all.sh task5"
