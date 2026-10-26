/* CS 423 HW2 (provided) — a short inner loop inside an outer loop.
 *
 * The inner loop runs TRIP = 4 iterations every time, so its loop branch
 * repeats the same short sequence of outcomes over and over.
 * TRIP is read from a volatile variable so that gcc cannot unroll the inner
 * loop away. Built at -O1 by the Makefile.
 */
#include <stdint.h>
#include <stdio.h>

#define OUTER 400000UL

static volatile int trip_count = 4;
static uint32_t data[64];

int main(void) {
    for (int k = 0; k < 64; k++)
        data[k] = (uint32_t)(k * 2654435761u);

    const int trip = trip_count;
    uint64_t s = 0;
    for (uint64_t i = 0; i < OUTER; i++) {
        for (int j = 0; j < trip; j++)         /* inner loop: TRIP = 4 */
            s += data[(i + j) & 63];
        s ^= i;
        __asm__ volatile("" : "+r"(s));
    }
    printf("brloop: s=%016lx\n", (unsigned long)s);
    return 0;
}
