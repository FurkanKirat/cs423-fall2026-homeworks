#!/usr/bin/env bash
# CS 423 HW2 — reproducibility entry point (Deliverable).
#
# THIS SCRIPT MUST REGENERATE EVERY NUMBER AND PLOT IN YOUR REPORT
# when run inside the pinned course container from the hw2/ directory of a
# fresh unzip of your submission:
#   docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/hw -w /hw \
#       s4lbot/cs423-gem5:v25.1.0.1 bash reproduce.sh
#
# The skeleton below covers the standard runs and plots. EXTEND it with
# anything else your report uses (extra runs, your own plots or analysis
# scripts). A reproduce.sh that fails to run caps your total score; see the
# handout. JOBS=<n> runs n simulations in parallel (about 1 GB of RAM each).
set -euo pipefail
cd "$(dirname "$0")"

# OPTIONAL Bonus Task 5: add task5 (or task5bp / task5pf, one part) here.
TASKS="task1 task2 task2ras task3 task4"

# Bonus Task 5, route B only (your own C++): uncomment these two lines to
# rebuild gem5 from gem5-patches/student.patch (long; see README.md) and
# run every simulation on your binary.
# rm -rf gem5 && bash scripts/get_gem5_source.sh && bash scripts/build_gem5.sh
# export GEM5=gem5/build/RISCV/gem5.opt

JOBS="${JOBS:-1}" bash scripts/run_all.sh $TASKS
python3 scripts/plot_results.py results/summary.csv -o plots
# Bonus Task 5: uncomment to print the score table.
# python3 scripts/task5_score.py results/summary.csv

# TODO(student): add any additional runs, plots and analysis commands your
# report relies on.
