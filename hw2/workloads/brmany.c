/* CS 423 HW2 (provided) — many biased branches.
 *
 * One loop whose body holds K = 64 different conditional branches. Branch j
 * always goes the same way (taken or not taken, fixed per branch by the
 * bits of DIRS), so every branch is perfectly predictable on its own.
 * Built at -O1 by the Makefile so that every if() stays a conditional branch.
 */
#include <stdint.h>
#include <stdio.h>

#define ITERS 50000UL
#define DIRS  0x9E3779B97F4A7C15UL   /* direction of branch j = bit j */

static uint8_t dir[64];

#define B(j) if (dir[j]) s += (j) + 1; else s ^= (j) + 1;   /* +1: branch 0 must not be a no-op */
#define B8(j) B(j) B(j+1) B(j+2) B(j+3) B(j+4) B(j+5) B(j+6) B(j+7)

int main(void) {
    for (int j = 0; j < 64; j++)
        dir[j] = (DIRS >> j) & 1;

    uint64_t s = 0;
    for (uint64_t i = 0; i < ITERS; i++) {
        B8(0) B8(8) B8(16) B8(24) B8(32) B8(40) B8(48) B8(56)
        __asm__ volatile("" : "+r"(s));   /* keep the loop body as written */
    }
    printf("brmany: s=%016lx\n", (unsigned long)s);
    return 0;
}
