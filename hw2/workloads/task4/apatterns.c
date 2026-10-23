/* CS 423 HW2 — Task 4.2 template: access patterns that separate prefetchers.
 *
 * YOUR JOB (see handout Task 4.2): write the bodies of two kernels that use
 * the same 8 MiB array buf[]:
 *
 *   kernel_strides — ONE loop with TWO interleaved loads per iteration: one
 *                    from the first half of buf (A) and one from the second
 *                    half (B), each with its own CONSTANT stride. Choose two
 *                    DIFFERENT strides, both larger than one 64-byte block
 *                    (set S1 and S2 below).
 *   kernel_scatter — ACCESSES loads that defeat both prefetchers, for
 *                    example independent loads from the pseudo-random
 *                    blocks that scatter_block(k) (provided) returns for
 *                    k = 0, 1, 2, ...
 *
 *   Predict the accuracy, coverage and timeliness of each prefetcher on each
 *   kernel BEFORE running, then measure:
 *     ./apatterns strides     and     ./apatterns scatter
 *
 * The file compiles and runs as shipped: the placeholder kernels walk buf
 * with a single 64-byte stride. That is NOT a valid answer.
 *
 * Keep ITERS, ACCESSES and the array size as they are, so that every run does a
 * comparable amount of work. Use `volatile` (as below) or the result value so
 * that the compiler cannot delete or merge your loads; check the loads in
 * the disassembly: riscv64-linux-gnu-objdump -d workloads/bin/apatterns
 */
#include <stdint.h>
#include <stdio.h>

#define BLOCK      64UL                       /* cache block size, bytes  */
#define BUF_BYTES  (8UL * 1024 * 1024)        /* 8 MiB, used by both kernels */
#define HALF       (BUF_BYTES / 2)            /* A = first half, B = second */
#define BLOCKS     (BUF_BYTES / BLOCK)        /* 131072 blocks              */
#define ITERS      (1UL << 19)                /* kernel_strides iterations  */
#define ACCESSES   (4 * BLOCKS)               /* kernel_scatter accesses    */

/* TODO(student): your two strides in bytes (different, both > BLOCK). */
#define S1 64UL                               /* placeholder */
#define S2 64UL                               /* placeholder */

static uint8_t buf[BUF_BYTES] __attribute__((aligned(4096)));

/* ---- provided scaffold: pseudo-random block numbers ---------------------- */
/* Returns a block number in [0, BLOCKS) for access number k. It is a fixed
 * hash of k (the splitmix64 finalizer): the same k always gives the same
 * block, and the blocks of consecutive k are unrelated to each other. */
static inline uint64_t scatter_block(uint64_t k) {
    uint64_t h = k + 0x9E3779B97F4A7C15UL;
    h = (h ^ (h >> 30)) * 0xBF58476D1CE4E5B9UL;
    h = (h ^ (h >> 27)) * 0x94D049BB133111EBUL;
    h ^= h >> 31;
    return h & (BLOCKS - 1);
}
/* ---- end of the provided scaffold ---------------------------------------- */

/* TODO(student): two interleaved loads per iteration, strides S1 and S2.
 * Keep both offsets inside their half, e.g. (i * S1) & (HALF - 1). */
static uint64_t kernel_strides(void) {
    const volatile uint8_t *A = buf, *B = buf + HALF;
    (void)B;                        /* placeholder does not use B yet */
    uint64_t s = 0;
    for (uint64_t i = 0; i < ITERS; i++) {
        s += A[(i * S1) & (HALF - 1)];          /* placeholder: one load */
    }
    return s;
}

/* TODO(student): ACCESSES loads that defeat both prefetchers. */
static uint64_t kernel_scatter(void) {
    const volatile uint8_t *p = buf;
    uint64_t s = 0;
    for (uint64_t k = 0; k < ACCESSES; k++) {
        s += p[(k * BLOCK) & (BUF_BYTES - 1)];  /* placeholder: sequential */
    }
    return s;
}

int main(int argc, char **argv) {
    /* select on the command line so each run measures ONE kernel:
     *   ./apatterns strides    or    ./apatterns scatter                  */
    int scatter = (argc > 1 && argv[1][0] == 's' && argv[1][1] == 'c');
    uint64_t r = scatter ? kernel_scatter() : kernel_strides();
    printf("apatterns: %s result=%016lx\n", scatter ? "scatter" : "strides",
           (unsigned long)r);
    return 0;
}
