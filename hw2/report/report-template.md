# CS 423 HW2 report template

The report is REQUIRED and is how every task is graded: an answer, number, or
plot that is not in the report earns no points, and a submission without a
report is not graded. Convert it to PDF, saved as `hw2/report.pdf` (top of
`hw2/`, not in `report/`), with any tool on your
host machine (LaTeX, Word/Google Docs export, pandoc, ...) and keep the
section structure below. Page guide: about 6–9 pages including plots. This
is a guideline, not a limit.

Every question in the handout states the form of the answer it expects
([number], [table], [plot], [1–3 sentences], [paragraph], [quoted lines]).
For every [number], show the arithmetic and the stats you used.

## Gate checklist (fill in; missing items can block grading)

- [ ] GenAI disclosure at the end of this report, consistent with `AI_USAGE.md`
      (`AI_USAGE.md` contains `None.` or one row per use).
- [ ] Reproducibility statement (Section 5) and a `reproduce.sh` that ran
      from a fresh unzip of my submission (see the handout's self-check).
- [ ] Starter version printed by `scripts/smoke_test.sh`: `hw2-starter-....`

---

## 0. Setup statement (Task 1)

- Docker image and tag; host OS and architecture; the versions block printed
  by `scripts/smoke_test.sh` (starter, gem5, cross-gcc, Python).

## 1. Task 1: bring-up and the branch unit

- Answers to Q1.1–Q1.4 (Q1.3: show the storage arithmetic).

## 2. Task 2: branch predictors on the provided workloads

- 2.1 Table (misprediction rate, CPI, cycles relative to the default
  predictor) and your answer; `plots/task2_cycles.png`.
- 2.2 `plots/task2_sweep.png` and your explanation.
- 2.3 Return address stack: your prediction (written BEFORE you run
  `run_all.sh task2ras`; stated before the measured
  numbers, with your model), the measured table, `plots/task2_ras.png`, and
  your explanation.
- 2.4 Indirect jumps: the table (per program run) and your explanation.

## 3. Task 3: prefetchers on pfstreams

- 3.1 Table.
- 3.2 (a) Accuracy, coverage and timeliness of both prefetchers, with the
  arithmetic; (b) the perfect-prefetcher estimate C_ideal, the fraction of
  the possible gain each prefetcher achieves, and the split of the gap.
- 3.3 Your answer.
- 3.4 `plots/task3_degree.png` and your explanation.

## 4. Task 4: patterns that separate predictors

For each of 4.1 (branches) and 4.2 (memory accesses):
- What your kernels do and why (the patterns, not the code).
- Your predictions, stated BEFORE the measured numbers.
- Measured results (table or plot).
- Your explanation at the level of mechanisms, with the stats that show it.

## 5. Reproducibility statement

- "Run `bash reproduce.sh` in the pinned container" (or the exact commands),
  and anything nonstandard about your environment (Bonus Task 5 route B:
  say that `reproduce.sh` rebuilds gem5 from `gem5-patches/student.patch`).

## 6. Bonus Task 5 (optional; omit if you did not do it)

For each part you did (5.1 direction predictor, 5.2 prefetcher):
- (a) Your mechanism and the rationale, tied to what you observed in
  Tasks 2–4. Route A or B.
- (b) Its storage with the arithmetic, and the budget check.
- (c) The per-workload table and score printed by `scripts/task5_score.py`.
- (d) Where it wins, where it loses or ties, and why (with statistics).

## GenAI disclosure

Per the course policy: state what (if any) GenAI assistance you used and for
which parts. Keep this consistent with your `AI_USAGE.md` log.
