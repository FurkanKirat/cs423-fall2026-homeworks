/* CS 423 HW2 (provided; Bonus Task 5 suite) — the same irregular footprint
 * in every region, regions in random order.
 *
 * The 8 MiB array is divided into 4096 regions of 2 KiB (32 blocks each).
 * The kernel visits the regions in a fixed pseudo-random order (built once
 * by the setup code) and, in each region, reads one byte from the same 8
 * blocks, always in the same order: blocks 0, 5, 9, 12, 19, 22, 27, 30 of
 * the region. PASSES passes over all regions. A setup pass first writes
 * every block once.
 */
#include <stdint.h>
#include <stdio.h>

#define BYTES    (8UL * 1024 * 1024)
#define BLOCK    64UL
#define REGION   (2UL * 1024)
#define REGIONS  (BYTES / REGION)                 /* 4096 */
#define PASSES   6

static uint8_t buf[BYTES] __attribute__((aligned(4096)));
static uint16_t order[REGIONS];
static const uint8_t footprint[8] = {0, 5, 9, 12, 19, 22, 27, 30};

int main(void) {
    for (uint64_t k = 0; k < BYTES; k += BLOCK)
        buf[k] = (uint8_t)(k >> 6);
    uint64_t x = 0xD1B54A32D192ED03UL;           /* random region order */
    for (uint64_t r = 0; r < REGIONS; r++) order[r] = (uint16_t)r;
    for (uint64_t r = REGIONS - 1; r > 0; r--) {
        x ^= x << 13; x ^= x >> 7; x ^= x << 17;
        uint64_t j = x % (r + 1);
        uint16_t t = order[r]; order[r] = order[j]; order[j] = t;
    }

    const volatile uint8_t *p = buf;
    uint64_t s = 0;
    for (int pass = 0; pass < PASSES; pass++)
        for (uint64_t r = 0; r < REGIONS; r++) {
            const uint64_t base = (uint64_t)order[r] * REGION;
            for (int f = 0; f < 8; f++)
                s += p[base + footprint[f] * BLOCK];
        }
    printf("pfregions: s=%lu\n", (unsigned long)s);
    return 0;
}
