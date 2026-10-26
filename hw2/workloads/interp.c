/* CS 423 HW2 (provided) — a tiny bytecode interpreter, two dispatch styles.
 *
 * The interpreter runs the same 12-instruction bytecode program REPS times.
 *   ./interp switch    — one loop with a switch(): gcc compiles it to a
 *                        jump table and ONE indirect jump (jr) that every
 *                        bytecode instruction goes through;
 *   ./interp threaded  — "threaded" dispatch with gcc's computed goto: every
 *                        handler ends with its OWN indirect jump to the next
 *                        handler.
 * Both styles execute the same handlers in the same order; only the number
 * of indirect-jump sites differs. Built at -O1 by the Makefile.
 */
#include <stdint.h>
#include <stdio.h>

#define REPS 150000UL

enum { ADD, SUB, XOR, SHL, MUL, ROT, END };

/* the program: 12 instructions, then END (MUL is not used) */
static const uint8_t prog[] = {
    ADD, SUB, XOR, ADD, SHL, ROT, ADD, SUB, XOR, ADD, SHL, ROT, END
};

static uint64_t run_switch(uint64_t acc) {
    const uint8_t *pc = prog;
    for (;;) {
        switch (*pc++) {
        case ADD: acc += 0x9E37; break;
        case SUB: acc -= 0x79B9; break;
        case XOR: acc ^= acc >> 7; break;
        case SHL: acc ^= acc << 3; break;
        case MUL: acc *= 5; break;
        case ROT: acc = (acc >> 11) | (acc << 53); break;
        default:  return acc;                   /* END */
        }
    }
}

static uint64_t run_threaded(uint64_t acc) {
    static void *const table[] = {
        &&L_ADD, &&L_SUB, &&L_XOR, &&L_SHL, &&L_MUL, &&L_ROT, &&L_END
    };
    const uint8_t *pc = prog;
#define NEXT goto *table[*pc++]
    NEXT;
L_ADD: acc += 0x9E37; NEXT;
L_SUB: acc -= 0x79B9; NEXT;
L_XOR: acc ^= acc >> 7; NEXT;
L_SHL: acc ^= acc << 3; NEXT;
L_MUL: acc *= 5; NEXT;
L_ROT: acc = (acc >> 11) | (acc << 53); NEXT;
L_END: return acc;
#undef NEXT
}

int main(int argc, char **argv) {
    int threaded = (argc > 1 && argv[1][0] == 't');
    uint64_t acc = 1;
    for (uint64_t r = 0; r < REPS; r++)
        acc = threaded ? run_threaded(acc) : run_switch(acc);
    printf("interp: %s acc=%016lx\n", threaded ? "threaded" : "switch",
           (unsigned long)acc);
    return 0;
}
