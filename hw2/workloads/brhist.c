/* CS 423 HW2 (provided; Bonus Task 5 suite) — correlation at a distance.
 *
 * Each outer iteration:
 *   1. branch R on a pseudo-random bit r (unpredictable);
 *   2. an inner loop of INNER = 12 iterations (its loop branch goes one way 11 times
 *      and the other way once), with one more if() inside that always goes the
 *      same way;
 *   3. branch E, which repeats the outcome of R from 25 branches
 *      earlier.
 * Built at -O1 by the Makefile; the volatile trip count keeps gcc from
 * unrolling the inner loop.
 */
#include <stdint.h>
#include <stdio.h>

#define OUTER 200000UL

static volatile int inner_count = 12;
static uint8_t rbits[OUTER];

int main(void) {
    uint64_t x = 0x9E3779B97F4A7C15UL;
    for (uint64_t i = 0; i < OUTER; i++) {
        x ^= x << 13; x ^= x >> 7; x ^= x << 17;
        rbits[i] = (uint8_t)(x & 1);
    }

    const int inner = inner_count;
    uint64_t s = 0, t = 0;
    for (uint64_t i = 0; i < OUTER; i++) {
        const int r = rbits[i];
        if (r)                                  /* R: random */
            s += i;
        else
            s ^= i;
        __asm__ volatile("" : "+r"(s));
        for (int j = 0; j < inner; j++) {       /* inner loop: 12 iterations */
            if (rbits[i] <= 1)                  /* always true (bits are 0/1) */
                t += j;
            else
                t ^= j;
            __asm__ volatile("" : "+r"(t));
        }
        if (r)                                  /* E: same outcome as R */
            t ^= s;
        else
            t += 7;
        __asm__ volatile("" : "+r"(t));
    }
    printf("brhist: s=%lu t=%lu\n", (unsigned long)s, (unsigned long)t);
    return 0;
}
