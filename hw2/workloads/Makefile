# CS 423 HW2 — cross-compiles all workloads to static RISC-V binaries.
# Run INSIDE the course container:  make -C workloads
#
# All workloads are built for rv64g (no compressed instructions), so every
# instruction is 4 bytes long and 4-byte aligned, as the branch predictors'
# PC indexing assumes.
CC      := riscv64-linux-gnu-gcc
CFLAGS  := -O2 -static -march=rv64g -mabi=lp64d -Wall -Wextra
# -O1 for the branch workloads: keeps every if() an actual conditional branch
# (and the recursion of recurse.c a recursion). interp.c needs -O2: it gives
# every handler of the threaded interpreter its own indirect jump.
CFLAGS_BR := -O1 -static -march=rv64g -mabi=lp64d -Wall -Wextra

# Tasks 1-4: hello brbias brloop brmany recurse interp pfstreams (+ task4/)
# Bonus Task 5 suites also use: brhist brperiod pfdelta pfregions
BINS := bin/hello bin/brbias bin/brloop bin/brmany bin/recurse bin/interp \
        bin/pfstreams bin/brhist bin/brperiod bin/pfdelta bin/pfregions \
        bin/bpatterns bin/apatterns

all: $(BINS)

bin:
	mkdir -p bin

bin/%: %.c | bin
	$(CC) $(CFLAGS) -o $@ $<

bin/brmany: brmany.c | bin
	$(CC) $(CFLAGS_BR) -o $@ $<

bin/brbias: brbias.c | bin
	$(CC) $(CFLAGS_BR) -o $@ $<

bin/brloop: brloop.c | bin
	$(CC) $(CFLAGS_BR) -o $@ $<

bin/brhist: brhist.c | bin
	$(CC) $(CFLAGS_BR) -o $@ $<

bin/brperiod: brperiod.c | bin
	$(CC) $(CFLAGS_BR) -o $@ $<

bin/recurse: recurse.c | bin
	$(CC) $(CFLAGS_BR) -o $@ $<

bin/bpatterns: task4/bpatterns.c | bin
	$(CC) $(CFLAGS_BR) -o $@ $<

bin/apatterns: task4/apatterns.c | bin
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -rf bin

.PHONY: all clean
