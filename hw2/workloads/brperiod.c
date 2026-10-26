/* CS 423 HW2 (provided; Bonus Task 5 suite) — a periodic loop exit hidden in
 * global noise.
 *
 * Each outer iteration runs an inner loop of TRIP = 12 iterations; inside it,
 * one if() goes on a pseudo-random bit (unpredictable). So the inner loop's
 * exit branch repeats the same 13-outcome sequence on its own, while the
 * global history around it is full of random outcomes.
 * Built at -O1 by the Makefile; the volatile trip count keeps gcc from
 * unrolling the inner loop.
 */
#include <stdint.h>
#include <stdio.h>

#define OUTER 100000UL
#define NBITS (1UL << 16)

static volatile int trip_count = 12;
static uint8_t rbits[NBITS];

int main(void) {
    uint64_t x = 0x9E3779B97F4A7C15UL;
    for (uint64_t i = 0; i < NBITS; i++) {
        x ^= x << 13; x ^= x >> 7; x ^= x << 17;
        rbits[i] = (uint8_t)(x & 1);
    }

    const int trip = trip_count;
    uint64_t s = 0, k = 0;
    for (uint64_t i = 0; i < OUTER; i++) {
        for (int j = 0; j < trip; j++) {        /* inner loop: 12 iterations */
            if (rbits[k++ & (NBITS - 1)])       /* random */
                s += j;
            else
                s ^= j;
            __asm__ volatile("" : "+r"(s));
        }
    }
    printf("brperiod: s=%lu\n", (unsigned long)s);
    return 0;
}
