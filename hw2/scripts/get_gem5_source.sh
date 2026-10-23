#!/usr/bin/env bash
# CS 423 HW2 — OPTIONAL, Bonus Task 5 route B only (your own C++ mechanism).
# Run INSIDE the course container from the hw2/ directory:
#   bash scripts/get_gem5_source.sh
#
# 1. copies the pinned gem5 source (/opt/gem5, without its prebuilt binary)
#    to hw2/gem5/, in your mounted working directory, so it survives the
#    container;
# 2. makes it a git repository with one commit "pristine v25.1.0.1";
# 3. applies gem5-patches/hw2-skeleton.patch (two skeleton classes you can
#    edit: HW2CustomBP, a direction predictor, and HW2CustomPrefetcher, an
#    L1D prefetcher) and commits it as "HW2 skeleton";
# 4. applies gem5-patches/student.patch if it exists (your own changes),
#    WITHOUT committing it.
# Then build with `bash scripts/build_gem5.sh` (the first build takes long;
# see the handout) and run with GEM5=gem5/build/RISCV/gem5.opt.
#
# Save your changes (edited AND new files) with
#   bash scripts/save_gem5_patch.sh
# and never put hw2/gem5/ into your submission archive (several GB): the
# patch is enough, reproduce.sh rebuilds from it.
set -euo pipefail
cd "$(dirname "$0")/.."

SRC=/opt/gem5
DST=gem5

if [ -e "$DST" ]; then
    echo "!! $DST/ already exists; remove it first if you want a fresh copy" >&2
    echo "   (save your changes first: bash scripts/save_gem5_patch.sh)" >&2
    exit 1
fi
[ -f "$SRC/SConstruct" ] || { echo "!! $SRC not found: run this inside the course container" >&2; exit 1; }

echo "== copying $SRC (without build/) to $DST/ =="
mkdir -p "$DST"
tar -C "$SRC" --exclude=./build -cf - . | tar -C "$DST" -xf -

export GIT_AUTHOR_NAME=cs423 GIT_AUTHOR_EMAIL=cs423@localhost
export GIT_COMMITTER_NAME=cs423 GIT_COMMITTER_EMAIL=cs423@localhost
export HOME="${HOME:-/tmp}"
[ -w "$HOME" ] || export HOME=/tmp

git -C "$DST" init -q
git -C "$DST" config core.fileMode false
git -C "$DST" add -A
git -C "$DST" commit -q -m "pristine $(cat "$SRC/GEM5_VERSION" 2>/dev/null || echo gem5)"

echo "== applying gem5-patches/hw2-skeleton.patch =="
git -C "$DST" apply --whitespace=nowarn "../gem5-patches/hw2-skeleton.patch"
git -C "$DST" add -A
git -C "$DST" commit -q -m "HW2 skeleton"

if [ -f gem5-patches/student.patch ]; then
    echo "== applying gem5-patches/student.patch (your changes, uncommitted) =="
    git -C "$DST" apply --whitespace=nowarn "../gem5-patches/student.patch"
fi

echo "== done: $DST/ ($(git -C "$DST" log --oneline | wc -l) commits) =="
echo "next: bash scripts/build_gem5.sh"
