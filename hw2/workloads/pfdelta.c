/* CS 423 HW2 (provided; Bonus Task 5 suite) — one load, two alternating
 * strides.
 *
 * One load walks an 8 MiB array whose consecutive addresses differ by
 * 1 block, then 6 blocks, then 1 block, then 6 blocks, ... (64 B and 384 B,
 * 7 blocks every two accesses), for PASSES passes. One byte is read per
 * visited block. A setup pass first writes every block once.
 */
#include <stdint.h>
#include <stdio.h>

#define BYTES   (8UL * 1024 * 1024)
#define BLOCK   64UL
#define PASSES  6

static uint8_t buf[BYTES] __attribute__((aligned(4096)));

int main(void) {
    for (uint64_t k = 0; k < BYTES; k += BLOCK)
        buf[k] = (uint8_t)(k >> 6);

    const volatile uint8_t *p = buf;
    uint64_t s = 0;
    for (int pass = 0; pass < PASSES; pass++) {
        uint64_t off = 0;
        while (off + 7 * BLOCK <= BYTES) {
            s += p[off];                        /* the one load ...        */
            off += (off / BLOCK) % 7 == 0 ? 1 * BLOCK : 6 * BLOCK;
        }
    }
    printf("pfdelta: s=%lu\n", (unsigned long)s);
    return 0;
}
