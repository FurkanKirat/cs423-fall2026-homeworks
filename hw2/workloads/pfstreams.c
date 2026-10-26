/* CS 423 HW2 (provided) — four concurrent read streams.
 *
 * Four 2 MiB arrays A, B, C, D (8 MiB in total, far larger than the L1 data
 * cache). One pass writes every 64-byte block of each array; then PASSES
 * passes read one byte per block of all four arrays in lockstep:
 *     s += A[k] + B[k] + C[k] + D[k],   k = 0, 64, 128, ...
 * The arrays start at different offsets within an 8 KiB window so that the
 * four streams use different sets of the 2-way L1 data cache.
 */
#include <stdint.h>
#include <stdio.h>

#define ARR     (2UL * 1024 * 1024)   /* bytes per array */
#define BLOCK   64UL
#define SKEW    (2UL * 1024)          /* set offset between the arrays */
#define PASSES  4

static uint8_t pool[4 * ARR + 4 * SKEW] __attribute__((aligned(4096)));

int main(void) {
    uint8_t *A = pool;
    uint8_t *B = pool + 1 * (ARR + SKEW);
    uint8_t *C = pool + 2 * (ARR + SKEW);
    uint8_t *D = pool + 3 * (ARR + SKEW);

    for (uint64_t k = 0; k < ARR; k += BLOCK) {
        A[k] = (uint8_t)k; B[k] = (uint8_t)(k >> 6);
        C[k] = (uint8_t)(k >> 7); D[k] = (uint8_t)(k >> 8);
    }

    const volatile uint8_t *a = A, *b = B, *c = C, *d = D;
    uint64_t s = 0;
    for (int p = 0; p < PASSES; p++)
        for (uint64_t k = 0; k < ARR; k += BLOCK)
            s += a[k] + b[k] + c[k] + d[k];

    printf("pfstreams: s=%lu\n", (unsigned long)s);
    return 0;
}
