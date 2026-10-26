# CS 423 — HW2 starter: Predicting the Future (Branch Prediction and Prefetching)

Everything here runs inside the **pinned course container**: gem5 v25.1.0.1
(RISC-V, `gem5.opt`) plus the `riscv64-linux-gnu` cross toolchain, the same
image as HW1. Read the handout PDF (`handout.pdf`) for the tasks; this README
covers only the environment and the commands.

Questions? Use the HW2 discussion forum:
https://github.com/SAL-Research/comparch-fall-2026/discussions/categories/hw2
(no solutions, code, configurations, or measurements there).

## 0. Get the latest starter first

HW2 does not use any of your HW1 files. Update your copy of the homework
repository before you start, and again whenever the forum announces a fix:

```sh
cd cs423-fall2026-homeworks
git pull
```

The smoke test prints the starter version (`STARTER VERSION: ...`); quote it
in your report.

## 1. Get the environment (once; skip if you still have it from HW1)

```sh
docker pull s4lbot/cs423-gem5:v25.1.0.1
```

Fallback, if you cannot pull: build the same image yourself (30–60 min, at
least ~16 GB of free disk during the build). In the homework repository the
recipe sits at the repo top level, one directory above `hw2/`:

```sh
(cd ../docker && ./build.sh)   # from hw2/ in cs423-fall2026-homeworks
```

The prebuilt image is published for linux/amd64 and linux/arm64. **Do not use
any other gem5 version: results differ and will not be regraded.**

## 2. Smoke test (Task 1 starts here)

From this directory (`hw2/`):

```sh
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/hw -w /hw \
    s4lbot/cs423-gem5:v25.1.0.1 bash scripts/smoke_test.sh
```

Expected: the versions block, the workloads cross-compile, gem5 runs `hello`
on the provided MinorCPU system, the headline stats are printed, and the
script ends with `STARTER VERSION: ...` and `SMOKE TEST PASSED`.

For interactive work, open a shell in the container once and stay in it:

```sh
docker run --rm -it -u "$(id -u):$(id -g)" -v "$PWD":/hw -w /hw \
    s4lbot/cs423-gem5:v25.1.0.1
```

All commands below are written for that in-container shell.

## 3. Layout

| Path | What it is |
|---|---|
| `../docker/` | course-image recipe (top level of the homework repository, shared by all homeworks) |
| `configs/hw2.py` | **complete** scalar MinorCPU system; you fill the `TODO(student)` slots (Task 2: `--bp`, Task 3: `--pf`, optional Bonus Task 5: `--bp custom` / `--pf custom`) |
| `workloads/` | provided workloads (`brbias`, `brloop`, `brmany`, `recurse`, `interp`, `pfstreams`, `hello`; Bonus Task 5 only: `brhist`, `pfdelta`, `pfregions`) + `Makefile` |
| `workloads/task4/` | templates for YOUR Task 4 patterns (`bpatterns.c`, `apatterns.c`) |
| `scripts/smoke_test.sh` | environment check + starter version (Task 1) |
| `scripts/run_all.sh` | runs the standard experiments, per task, into `results/` |
| `scripts/extract_stats.py` | `results/*/stats.txt` → `results/summary.csv` |
| `scripts/plot_results.py` | `summary.csv` → `plots/task2_cycles.png`, `plots/task2_sweep.png`, `plots/task2_ras.png`, `plots/task3_degree.png` |
| `scripts/task5_score.py` | Bonus Task 5: your design vs. the best baseline per suite workload, and the score |
| `scripts/storage.py` | Bonus Task 5: storage in bits of a predictor/prefetcher configuration, and the budget check |
| `scripts/get_gem5_source.sh`, `scripts/build_gem5.sh`, `scripts/save_gem5_patch.sh`, `gem5-patches/` | Bonus Task 5 route B only: your own gem5 build (section 6) |
| `reproduce.sh` | your one-shot reproducibility script (deliverable) |
| `report.pdf` | YOUR report goes here, at the top of `hw2/` (the template is in `report/`) |
| `report/report-template.md` | required report structure (the report is a grading gate) |
| `AI_USAGE.md` | your GenAI usage log (write `None.` if you used none); required |

## 4. Everyday commands

```sh
# build workloads (again after editing workloads/task4/*.c)
make -C workloads

# one run by hand: results/<tag>/stats.txt appears
gem5.opt --outdir=results/default-none-brbias configs/hw2.py \
    --cmd workloads/bin/brbias

# options of configs/hw2.py (see its header):
#   --bp default|local|tournament|bimode    (needs TODO slot 1 except default)
#   --pf none|nextline|stride --pf-degree D (needs TODO slot 2 except none)
#   --bp custom / --pf custom               (optional Bonus Task 5, slot 3)
#   --pred-param NAME=VALUE  --pf-param NAME=VALUE  --mshrs N
#   --ras-entries N  --indirect simple|none (Tasks 2.3 and 2.4)
#   --args "<workload arguments>", e.g. --args threaded for interp

# the standard runs of one or more tasks, then the summary CSV
bash scripts/run_all.sh task1
bash scripts/run_all.sh task2          # JOBS=4 ... runs 4 at a time
bash scripts/run_all.sh task2ras       # Task 2.3: write your prediction first

# plots for the report
python3 scripts/plot_results.py results/summary.csv -o plots

# optional Bonus Task 5: suites x {baselines, your design}, then the score
bash scripts/run_all.sh task5          # or task5bp / task5pf
python3 scripts/task5_score.py results/summary.csv
python3 scripts/storage.py TAGE logTagTableSizes=11,9,9,9,9,9,9,9
# several designs: see the header of scripts/task5_score.py (--suffix)
```

`run_all.sh` writes each run's gem5 output to `results/<tag>/run.log`
instead of the terminal; look there when a run fails. The handout lists how
long each run takes.

## 5. Result-naming convention (graders rely on it)

`results/<bp>-<pf>-<workload>[-<variant>]/stats.txt`, for example
`results/bimode-none-brloop/` or `results/default-stride-pfstreams-d4-m8/`:
exactly what `scripts/run_all.sh` produces. Keep the `results/` directory of
every run you report, and make sure `reproduce.sh` regenerates all of them.

## 6. Optional: Bonus Task 5, route B (your own C++ in gem5)

Route A (configuring gem5's built-in classes in slot 3) needs nothing
below. Route B builds your own gem5 binary from source, inside the same
container, in your mounted `hw2/` directory. Read the handout's cost
statement first: the first build compiles all of gem5 (measured on the
instructor's 8-core laptop: about 20 min with 8 parallel jobs, about 36 min
in 6 GB of memory, mostly with 2 jobs), needs about 7 GB of disk, and Docker needs at least **6 GB of
memory** (Docker Desktop: Settings → Resources → Memory). `build_gem5.sh`
uses 2 parallel jobs by default, which fits in 6 GB; 8 parallel jobs peaked
near 9 GB. With 4 GB the final link step is killed. A killed build resumes
when you rerun it.

```sh
# 1. copy the pinned source to hw2/gem5/ and apply the course skeleton
#    (classes HW2CustomBP and HW2CustomPrefetcher)
bash scripts/get_gem5_source.sh

# 2. first build (long): hw2/gem5/build/RISCV/gem5.opt
bash scripts/build_gem5.sh                # 2 jobs; JOBS=8 only with >= 10 GB

# 3. edit your mechanism, then rebuild (about 1.5 min: one file + link)
#      gem5/src/cpu/pred/hw2_custom_bp.{hh,cc}, HW2Custom.py
#      gem5/src/mem/cache/prefetch/hw2_custom.{hh,cc}, HW2CustomPrefetcher.py
#    quick compile check of one file, without linking (seconds; works
#    after the first full build):
#      (cd gem5 && scons build/RISCV/cpu/pred/hw2_custom_bp.o --ignore-style)
bash scripts/build_gem5.sh

# 4. in configs/hw2.py, slot 3: e.g.
#      from m5.objects import HW2CustomBP
#      return HW2CustomBP(tableSize=4096, historyBits=12)
#    then run the suite on YOUR binary
GEM5=gem5/build/RISCV/gem5.opt bash scripts/run_all.sh task5
python3 scripts/task5_score.py results/summary.csv

# 5. save ALL your changes (edited and new files) as a patch: this is what
#    you submit, not gem5/ (a plain `git diff` would miss new files)
bash scripts/save_gem5_patch.sh
```

Adding files: editing the skeleton's `.cc`/`.hh`/`.py` files needs nothing
else. A NEW `.cc` file must be listed in its directory's `SConscript`, and a
new SimObject Python file too, exactly as the skeleton patch does in
`gem5/src/cpu/pred/SConscript`:

```python
SimObject('HW2Custom.py', sim_objects=['HW2CustomBP'])
Source('hw2_custom_bp.cc')
```

(A new header `.hh` needs no entry.) There is no cheap check before the
first full build; after it, compiling a single object (step 3) takes
seconds.

`reproduce.sh` rebuilds gem5 from `gem5-patches/student.patch` when you
uncomment its two route-B lines; `get_gem5_source.sh` applies the skeleton
and then your patch. Never put `hw2/gem5/` in your submission archive (see
the handout). The skeleton's direction predictor is a working gshare
(PC XOR global history, 2-bit counters) and its prefetcher a working
next-line prefetcher with a small PC-indexed table: start from them.
