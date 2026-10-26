#!/usr/bin/env bash
# CS 423 HW2 — runs the standard experiments of the handout. Run INSIDE the
# course container from the hw2/ directory:
#   bash scripts/run_all.sh                 # every task
#   bash scripts/run_all.sh task1 task2     # only the tasks you name
#   bash scripts/run_all.sh task2ras        # Task 2.3 only (predict first!)
#   bash scripts/run_all.sh task5           # optional Bonus Task 5 (also:
#                                           # task5bp, task5pf: one part)
#   JOBS=4 bash scripts/run_all.sh task2    # 4 simulations in parallel
#                                           # (each needs about 1 GB of RAM)
#
# Results land in results/<bp>-<pf>-<workload>[-<variant>]/stats.txt; this
# naming convention is what scripts/extract_stats.py and the graders expect:
#   <bp>  default | local | tournament | bimode | custom    (--bp)
#   <pf>  none | nextline | stride | custom                 (--pf)
#   variants: -c<N> N two-bit counters per table (Task 2.2),
#             -r<N> N return-address-stack entries (Task 2.3),
#             -<style>-<simple|none> dispatch style and indirect-target
#             predictor (Task 2.4),
#             -d<D> prefetch degree, -m<M> L1D MSHRs (Tasks 3 and 5).
#
# Runs FAIL until you fill the matching TODO(student) slot in configs/hw2.py:
# --bp local|tournament|bimode needs slot 1 (Task 2), --pf nextline|stride
# needs slot 2 (Task 3), --bp custom / --pf custom need slot 3 (Bonus 5). The task4 runs work as shipped but measure the
# placeholder kernels until you write yours. That is expected; rerun the
# task as you progress.
set -uo pipefail
cd "$(dirname "$0")/.."

JOBS="${JOBS:-1}"
# The gem5 binary: the image's by default; Bonus Task 5 route B sets
# GEM5=gem5/build/RISCV/gem5.opt (your own build, see README.md).
GEM5="${GEM5:-gem5.opt}"
command -v "$GEM5" > /dev/null || [ -x "$GEM5" ] || { echo "!! gem5 binary '$GEM5' not found" >&2; exit 1; }
TASKS="${*:-task1 task2 task2ras task3 task4}"   # task5* only when named
want() { [[ " $TASKS " == *" $1 "* ]]; }

make -C workloads || exit 1

# One simulation; its gem5 output goes to results/<tag>/run.log.
run_one() { # run_one <tag> <binary> <workload-args> [config options...]
    local tag="$1" bin="$2" wargs="$3"
    shift 3
    mkdir -p "results/$tag"   # the log is opened before gem5 creates the dir
    if "$GEM5" --outdir="results/$tag" configs/hw2.py \
            --cmd "workloads/bin/$bin" ${wargs:+--args "$wargs"} "$@" \
            > "results/$tag/run.log" 2>&1; then
        echo "   done $tag"
    else
        # gem5's stderr is unbuffered but its redirected stdout is not, so the
        # error sits near the TOP of the log: grep first, tail as a fallback.
        # (Collected first and printed at once, so parallel runs don't mix.)
        local err
        err="$(grep -m4 -E "Error|error:|Traceback|Exception" "results/$tag/run.log" \
               || tail -n 6 "results/$tag/run.log")"
        printf '!! %s FAILED (gem5 output: results/%s/run.log). The error:\n%s\n' \
            "$tag" "$tag" "$(sed 's/^/   | /' <<< "$err")"
    fi
}

run() { # same arguments as run_one; runs up to $JOBS simulations at once
    if [ "$JOBS" -le 1 ]; then
        run_one "$@"
    else
        while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n; done
        run_one "$@" &
    fi
}

if want task1; then
    echo "== Task 1: default predictor, no prefetcher =="
    run default-none-brbias brbias ""
fi

if want task2; then
    echo "== Task 2.1: direction predictors x brbias, brloop =="
    for bp in default local tournament bimode; do
        # default-none-brbias is the Task 1 run; rerun it only if needed
        if [ "$bp" != default ] || ! want task1; then
            run "$bp-none-brbias" brbias "" --bp "$bp"
        fi
        run "$bp-none-brloop" brloop "" --bp "$bp"
    done

    echo "== Task 2.2: table size sweep on brmany =="
    # LocalBP's localPredictorSize counts BITS (2 per counter);
    # BiModeBP's globalPredictorSize counts COUNTERS (per direction table).
    for c in 16 32 64 128 256 512 1024; do
        run "local-none-brmany-c$c" brmany "" --bp local \
            --pred-param localPredictorSize=$((2 * c))
        run "bimode-none-brmany-c$c" brmany "" --bp bimode \
            --pred-param globalPredictorSize=$c
    done

    echo "== Task 2.4: indirect jumps on interp =="
    for style in switch threaded; do
        for ind in simple none; do
            run "default-none-interp-$style-$ind" interp "$style" \
                --indirect "$ind"
        done
    done
fi

if want task2ras; then
    # Task 2.3 has its own target: write your prediction (2.3(a)) first.
    echo "== Task 2.3: return address stack size on recurse =="
    for r in 0 1 2 4 8 16 32; do
        run "default-none-recurse-r$r" recurse "" --ras-entries "$r"
    done
fi

if want task3; then
    echo "== Task 3.1: prefetchers on pfstreams (degree 1, 4 MSHRs) =="
    run default-none-pfstreams-m4 pfstreams ""
    run default-nextline-pfstreams-d1-m4 pfstreams "" --pf nextline --pf-degree 1
    run default-stride-pfstreams-d1-m4 pfstreams "" --pf stride --pf-degree 1

    echo "== Task 3.4: stride prefetcher, degree x MSHRs =="
    for m in 4 8 16; do
        [ "$m" = 4 ] || run "default-none-pfstreams-m$m" pfstreams "" --mshrs "$m"
        for d in 1 2 4 8; do
            [ "$m-$d" = 4-1 ] && continue          # already run for Task 3.1
            run "default-stride-pfstreams-d$d-m$m" pfstreams "" \
                --pf stride --pf-degree "$d" --mshrs "$m"
        done
    done
fi

if want task4; then
    echo "== Task 4.1: your branch patterns x direction predictors =="
    for bp in local tournament bimode; do
        run "$bp-none-bpatterns-perbranch" bpatterns perbranch --bp "$bp"
        run "$bp-none-bpatterns-correlated" bpatterns correlated --bp "$bp"
    done

    echo "== Task 4.2: your access patterns x prefetchers (degree 1) =="
    for pf in none nextline stride; do
        run "default-$pf-apatterns-strides" apatterns strides --pf "$pf"
        run "default-$pf-apatterns-scatter" apatterns scatter --pf "$pf"
    done
fi

# Bonus Task 5: the fixed evaluation suites, baselines and your design.
# task5bp = 5.1 (direction predictor), task5pf = 5.2 (prefetcher),
# task5 = both. Baseline runs that Task 2 or 3 already make in the same
# invocation are not repeated.
if want task5 || want task5bp; then
    echo "== Bonus 5.1: direction-predictor suite x {baselines, custom} =="
    for wl in brbias brloop brmany brhist brperiod; do
        for bp in local tournament bimode; do
            case "$wl" in brbias|brloop) want task2 && continue ;; esac
            run "$bp-none-$wl" "$wl" "" --bp "$bp"
        done
        run "custom-none-$wl" "$wl" "" --bp custom
    done
fi
if want task5 || want task5pf; then
    echo "== Bonus 5.2: prefetcher suite x {baselines, custom} (4 MSHRs) =="
    for wl in pfstreams pfdelta pfregions; do
        shared=no
        [ "$wl" = pfstreams ] && want task3 && shared=yes
        [ "$shared" = yes ] || run "default-none-$wl-m4" "$wl" ""
        for pf in nextline stride; do
            for d in 1 2 4; do
                if [ "$shared" = yes ] && { [ "$pf" = stride ] || [ "$d" = 1 ]; }; then
                    continue                    # made by Task 3
                fi
                run "default-$pf-$wl-d$d-m4" "$wl" "" --pf "$pf" --pf-degree "$d"
            done
        done
        run "default-custom-$wl-m4" "$wl" "" --pf custom
    done
fi

wait
echo "== extracting stats =="
python3 scripts/extract_stats.py results -o results/summary.csv
