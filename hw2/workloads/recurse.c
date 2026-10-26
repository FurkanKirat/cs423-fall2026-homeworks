/* CS 423 HW2 (provided) — calls and returns at varying depth.
 *
 * Walk w (w = 0, 1, 2, ...) calls down(d) with d = 1 + (w % 20): down()
 * calls itself until d reaches 0, so one walk makes d + 1 nested calls and
 * then d + 1 returns. Every call is a direct call (its target is fixed);
 * every return goes back to a different place depending on the depth.
 * The asm barrier and noinline keep gcc from turning the recursion into a
 * loop. Built at -O1 by the Makefile.
 */
#include <stdint.h>
#include <stdio.h>

#define WALKS 100000UL
#define MAXD  20

__attribute__((noinline)) static uint64_t down(uint64_t d) {
    if (d == 0)
        return 1;
    uint64_t r = down(d - 1);
    __asm__ volatile("" : "+r"(r));
    return r * 3 + d;
}

int main(void) {
    uint64_t s = 0;
    for (uint64_t w = 0; w < WALKS; w++)
        s += down(1 + (w % MAXD));
    printf("recurse: s=%016lx\n", (unsigned long)s);
    return 0;
}
