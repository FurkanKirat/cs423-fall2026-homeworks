/* CS 423 HW2 — Task 4.1 template: branch patterns that separate predictors.
 *
 * YOUR JOB (see handout Task 4.1):
 *   1. Write the body of run_kernel(): a loop over i whose body contains
 *      conditional branches on the precomputed arrays a[i] and b[i], with
 *      cheap work on each path. The SAME kernel runs for both patterns, so
 *      both measurements execute the same static code.
 *   2. Fill a[] and b[] in the two pattern functions:
 *        make_perbranch_pattern()  — outcomes that a predictor which keeps
 *                                    a per-branch (local) history can learn;
 *        make_correlated_pattern() — outcomes where one branch is determined
 *                                    by an earlier, DIFFERENT branch, so that
 *                                    only a predictor with global history can
 *                                    learn it.
 *   3. Predict the misprediction count of each direction predictor on each
 *      pattern BEFORE running, then measure:
 *        ./bpatterns perbranch     and     ./bpatterns correlated
 *
 * The file compiles and runs as shipped: the placeholders below fill both
 * arrays with zeros and the kernel does not branch on them at all, so every
 * predictor behaves the same. That is NOT a valid answer.
 *
 * rand_bit() returns pseudo-random bits (xorshift64): no predictor can learn
 * them. Compile with the provided Makefile (it uses -O1 for this file, to
 * keep gcc from turning your if()s into branch-free code), and check the
 * branches in the disassembly:
 *   riscv64-linux-gnu-objdump -d workloads/bin/bpatterns | less
 */
#include <stdint.h>
#include <stdio.h>

#define N 1000000UL                 /* kernel iterations                  */

static uint8_t a[N], b[N];          /* branch conditions, one per iteration */

static uint64_t xs = 88172645463325252UL;   /* xorshift64 state */
static inline uint8_t rand_bit(void) {
    xs ^= xs << 13; xs ^= xs >> 7; xs ^= xs << 17;
    return (uint8_t)(xs & 1);
}

/* TODO(student): a pattern that a per-branch-history predictor can learn. */
static void make_perbranch_pattern(void) {
    for (uint64_t i = 0; i < N; i++) {
        a[i] = 0;                   /* placeholder */
        b[i] = 0;                   /* placeholder */
    }
}

/* TODO(student): a pattern that only a global-history predictor can learn. */
static void make_correlated_pattern(void) {
    for (uint64_t i = 0; i < N; i++) {
        a[i] = 0;                   /* placeholder */
        b[i] = 0;                   /* placeholder */
    }
}

/* TODO(student): the shared kernel — branch on a[i] and on b[i]. */
static uint64_t run_kernel(void) {
    uint64_t s = 0;
    for (uint64_t i = 0; i < N; i++) {
        s += a[i] + b[i];           /* placeholder — no branch on a or b! */
    }
    return s;
}

int main(int argc, char **argv) {
    /* select on the command line so each run measures ONE pattern:
     *   ./bpatterns perbranch    or    ./bpatterns correlated            */
    int correlated = (argc > 1 && argv[1][0] == 'c');
    if (correlated)
        make_correlated_pattern();
    else
        make_perbranch_pattern();
    printf("bpatterns: %s result=%016lx\n",
           correlated ? "correlated" : "perbranch",
           (unsigned long)run_kernel());
    return 0;
}
