#!/usr/bin/env bash
# CS 423 HW2 — OPTIONAL, Bonus Task 5 route B only. Saves ALL your changes to
# the gem5 source (edited files AND new files you created under gem5/src/)
# as gem5-patches/student.patch, relative to the "HW2 skeleton" commit made
# by scripts/get_gem5_source.sh. Run INSIDE the course container from hw2/:
#   bash scripts/save_gem5_patch.sh
# (A plain `git diff` would miss new, untracked files.)
set -euo pipefail
cd "$(dirname "$0")/.."

[ -d gem5/.git ] || { echo "!! gem5/ not found: run scripts/get_gem5_source.sh first" >&2; exit 1; }
export HOME="${HOME:-/tmp}"
[ -w "$HOME" ] || export HOME=/tmp

git -C gem5 add -A -- src            # stage edits + new files (build/ is ignored)
git -C gem5 diff --cached HEAD > gem5-patches/student.patch
echo "== files in gem5-patches/student.patch =="
git -C gem5 diff --cached --stat HEAD
echo "== saved $(wc -l < gem5-patches/student.patch) lines =="
