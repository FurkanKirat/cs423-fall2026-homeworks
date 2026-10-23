/* CS 423 HW2 (provided) — a biased, data-dependent branch.
 *
 * Counts the elements of a pseudo-random array that are below a threshold.
 * The threshold is chosen so that the if() is taken for about 90% of the
 * elements, in an order no history can predict (xorshift64 data).
 * Built at -O1 by the Makefile so that the if() stays a conditional branch.
 */
#include <stdint.h>
#include <stdio.h>

#define N 1000000UL

static uint16_t v[N];

int main(void) {
    uint64_t x = 0x2545F4914F6CDD1DUL;
    for (uint64_t i = 0; i < N; i++) {
        x ^= x << 13; x ^= x >> 7; x ^= x << 17;
        v[i] = (uint16_t)(x % 1000);          /* 0 .. 999 */
    }

    uint64_t below = 0, sum = 0;
    for (uint64_t i = 0; i < N; i++) {
        if (v[i] < 900)                        /* taken for ~90% of i */
            below++;
        else
            sum += v[i];
        __asm__ volatile("" : "+r"(below), "+r"(sum));
    }
    printf("brbias: below=%lu sum=%lu\n", (unsigned long)below,
           (unsigned long)sum);
    return 0;
}
