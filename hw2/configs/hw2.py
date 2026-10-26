# CS 423 HW2 — complete system: scalar in-order MinorCPU (SE mode) with a
# swappable branch direction predictor and an optional L1D prefetcher.
#
# Everything is provided and FROZEN except the TODO(student) slots:
#   slot 1 (Task 2): make_direction_predictor()  -> --bp
#   slot 2 (Task 3): make_prefetcher()           -> --pf / --pf-degree
#   slot 3 (optional Bonus Task 5): make_custom_direction_predictor()
#                                   -> --bp custom
#                                   make_custom_prefetcher() -> --pf custom
#           Slot 3 may contain any Python that builds gem5 SimObjects,
#           e.g. helper functions, imports from m5.objects, or reading an
#           environment variable to switch between several designs:
#             import os; design = os.environ.get("MY_DESIGN", "a")
#           (then:  MY_DESIGN=b gem5.opt ... --bp custom).
# With the defaults (--bp default --pf none) the config runs as shipped, so
# Task 1 needs no code:
#   gem5.opt --outdir=results/default-none-brbias configs/hw2.py \
#       --cmd workloads/bin/brbias
#
# Sweep plumbing (provided; repeatable options):
#   --pred-param NAME=VALUE   set a parameter of the direction predictor,
#                             e.g. --pred-param globalPredictorSize=1024
#   --pf-param NAME=VALUE     set a parameter of the prefetcher
#   --mshrs N                 number of L1 data-cache MSHRs (default 4)
#   --ras-entries N           return address stack entries (default 16;
#                             0 = no return address stack)       (Task 2.3)
#   --indirect simple|none    indirect-target predictor: gem5's
#                             SimpleIndirectPredictor (default), or none,
#                             so that the BTB alone predicts the targets of
#                             indirect jumps                     (Task 2.4)
# Parameter lists with defaults, inside the container:
#   /opt/gem5/src/cpu/pred/BranchPredictor.py
#   /opt/gem5/src/mem/cache/prefetch/Prefetcher.py
#
# gem5 v25.1.0.1, RISC-V. Do not change anything outside the three slots.

import argparse

import m5
from m5.params import NULL
from m5.objects import (
    AddrRange,
    BiModeBP,
    BranchPredictor,
    Cache,
    DDR3_1600_8x8,
    LocalBP,
    MemCtrl,
    Process,
    RiscvMinorCPU,
    Root,
    SEWorkload,
    SrcClockDomain,
    StridePrefetcher,
    System,
    SystemXBar,
    TaggedPrefetcher,
    TournamentBP,
    VoltageDomain,
)

STARTER_VERSION = "hw2-starter-2026-10-22"

# ---------------------------------------------------------------------------
# command line
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--cmd", required=True, help="RISC-V static binary to run")
parser.add_argument(
    "--args", default="", help="whitespace-separated argv for the workload"
)
parser.add_argument("--clock", default="1GHz", help="CPU clock (default 1GHz)")
parser.add_argument(
    "--bp",
    default="default",
    choices=["default", "local", "tournament", "bimode", "custom"],
    help="branch direction predictor (Task 2; default: MinorCPU's own; "
    "custom: Bonus Task 5)",
)
parser.add_argument(
    "--pred-param",
    action="append",
    default=[],
    metavar="NAME=VALUE",
    help="override one direction-predictor parameter (repeatable)",
)
parser.add_argument(
    "--pf",
    default="none",
    choices=["none", "nextline", "stride", "custom"],
    help="L1 data-cache prefetcher (Task 3; default: none; "
    "custom: Bonus Task 5)",
)
parser.add_argument(
    "--pf-degree",
    type=int,
    default=1,
    help="prefetch degree: blocks requested per trigger (default 1)",
)
parser.add_argument(
    "--pf-param",
    action="append",
    default=[],
    metavar="NAME=VALUE",
    help="override one prefetcher parameter (repeatable)",
)
parser.add_argument(
    "--mshrs", type=int, default=4, help="L1 data-cache MSHRs (default 4)"
)
parser.add_argument(
    "--ras-entries",
    type=int,
    default=16,
    help="return address stack entries (Task 2.3; default 16, 0 = none)",
)
parser.add_argument(
    "--indirect",
    default="simple",
    choices=["simple", "none"],
    help="indirect-target predictor (Task 2.4; default: simple)",
)
args = parser.parse_args()


# ===========================================================================
# ==== TODO(student) slot 1 — Task 2: the branch direction predictor ========
# ===========================================================================
def make_direction_predictor(name):
    """Return a gem5 BranchPredictor for --bp NAME, or None to keep
    MinorCPU's built-in default (which you identify in Task 1).

    gem5's branch unit is a BranchPredictor container whose
    `conditionalBranchPred` part predicts directions; leave its other
    parts (BTB, return address stack, indirect predictor) at their
    defaults. The three direction predictors of this homework are the
    classes LocalBP, TournamentBP and BiModeBP (already imported above;
    see /opt/gem5/src/cpu/pred/BranchPredictor.py). Use each class's
    default parameters here: --pred-param overrides are applied later.
    """
    if name == "default":
        return None
    # TODO(student): map "local", "tournament", "bimode" to a
    # BranchPredictor whose conditionalBranchPred is the matching class.
    # Delete the `raise` when you are done.
    raise NotImplementedError(f"Task 2: --bp {name} is not implemented yet")


# ===========================================================================
# ==== TODO(student) slot 2 — Task 3: the L1 data-cache prefetcher ==========
# ===========================================================================
def make_prefetcher(name, degree):
    """Return a gem5 prefetcher object for --pf NAME with the given
    degree, or None for no prefetcher.

    next-line -> class TaggedPrefetcher; stride -> class StridePrefetcher
    (both already imported above; see
    /opt/gem5/src/mem/cache/prefetch/Prefetcher.py). Both classes take a
    `degree` parameter. Leave every other parameter at its default:
    --pf-param overrides are applied later.
    """
    if name == "none":
        return None
    # TODO(student): map "nextline" and "stride" to the matching
    # prefetcher class, constructed with degree=degree.
    # Delete the `raise` when you are done.
    raise NotImplementedError(f"Task 3: --pf {name} is not implemented yet")


# ===========================================================================
# ==== TODO(student) slot 3 — OPTIONAL Bonus Task 5: your own designs =======
# ===========================================================================
def make_custom_direction_predictor():
    """Return the DIRECTION predictor (a ConditionalPredictor object, not a
    BranchPredictor) of your Bonus Task 5.1 design, used by --bp custom.
    The provided code puts it into the branch unit for you.

    Route A: any direction predictor of gem5 v25.1.0.1 with parameters of
    your choice, e.g. a TAGE family member (see BranchPredictor.py); import
    the class here, e.g.  from m5.objects import TAGE
    Any Python is fine here (helpers, environment variables to switch
    designs, combining objects). Route B: your own class, built into your
    own gem5 binary from
    hw2/gem5/ (see README.md), e.g.  from m5.objects import HW2CustomBP
    State its storage in bits in your report (budget: see the handout).
    """
    raise NotImplementedError("Bonus Task 5.1: --bp custom is not implemented")


def make_custom_prefetcher():
    """Return the L1 data-cache prefetcher of your Bonus Task 5.2 design,
    used by --pf custom (--pf-degree is ignored; set the degree, if your
    design has one, here). Route A: any prefetcher class of gem5
    v25.1.0.1 (see Prefetcher.py), with parameters of your choice. Route B:
    your own class, e.g.  from m5.objects import HW2CustomPrefetcher
    """
    raise NotImplementedError("Bonus Task 5.2: --pf custom is not implemented")


# ===========================================================================
# ==== end of the TODO(student) slots — everything below is FROZEN ==========
# ===========================================================================


def apply_overrides(obj, overrides, what):
    """Apply NAME=VALUE overrides (integers) to a SimObject."""
    for override in overrides:
        pname, _, value = override.partition("=")
        if pname not in obj._params:
            raise AttributeError(f"{what} has no parameter '{pname}'")
        setattr(obj, pname, int(value))
        print(f"** {what} override: {pname} = {value}")


# ---------------------------------------------------------------------------
# L1 caches (same as HW1). Latency model: a hit takes 1 cycle
# (max(tag_latency, data_latency), because sequential_access is False);
# a miss allocates an MSHR, goes over the memory bus to DRAM, and the
# returning block is delivered after response_latency (1 cycle).
# ---------------------------------------------------------------------------
class L1ICache(Cache):
    size = "16KiB"
    assoc = 2
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 4
    tgts_per_mshr = 8


class L1DCache(Cache):
    size = "16KiB"
    assoc = 2
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 4
    tgts_per_mshr = 8


# ---------------------------------------------------------------------------
# system
# ---------------------------------------------------------------------------
system = System()
system.clk_domain = SrcClockDomain(
    clock=args.clock, voltage_domain=VoltageDomain()
)
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]
system.membus = SystemXBar()

# CPU: MinorCPU configured as a SCALAR in-order pipeline (one instruction
# per stage per cycle), exactly as in HW1's pipeline.py.
system.cpu = RiscvMinorCPU()
for pname in ("decodeInputWidth", "executeInputWidth",
              "executeIssueLimit", "executeCommitLimit"):
    setattr(system.cpu, pname, 1)

if args.bp == "custom":
    bp = BranchPredictor(
        conditionalBranchPred=make_custom_direction_predictor())
else:
    bp = make_direction_predictor(args.bp)
if bp is not None:
    system.cpu.branchPred = bp
# RISC-V instructions are 4 bytes, so the two lowest PC bits are always 0.
# Index every PC-indexed table with PC >> 2 (gem5's default shift of 0
# would leave three of every four entries of such a table unused).
system.cpu.branchPred.instShiftAmt = 2
apply_overrides(system.cpu.branchPred.conditionalBranchPred,
                args.pred_param, "direction predictor")
# Target prediction (Tasks 2.3 and 2.4): return address stack and
# indirect-target predictor of the branch unit.
if args.ras_entries > 0:
    system.cpu.branchPred.ras.numEntries = args.ras_entries
else:
    system.cpu.branchPred.ras = NULL
if args.indirect == "none":
    system.cpu.branchPred.indirectBranchPred = NULL

system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()
system.cpu.dcache.mshrs = args.mshrs
if args.pf == "custom":
    pf = make_custom_prefetcher()
else:
    pf = make_prefetcher(args.pf, args.pf_degree)
if pf is not None:
    system.cpu.dcache.prefetcher = pf
    apply_overrides(system.cpu.dcache.prefetcher, args.pf_param,
                    "prefetcher")
elif args.pf_param:
    raise ValueError("--pf-param needs a prefetcher (--pf nextline|stride|custom)")

system.cpu.icache_port = system.cpu.icache.cpu_side
system.cpu.dcache_port = system.cpu.dcache.cpu_side
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports
system.cpu.createInterruptController()

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

# ---------------------------------------------------------------------------
# SE-mode workload
# ---------------------------------------------------------------------------
system.workload = SEWorkload.init_compatible(args.cmd)
process = Process()
process.cmd = [args.cmd] + args.args.split()
system.cpu.workload = process
system.cpu.createThreads()

# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
root = Root(full_system=False, system=system)
m5.instantiate()

print(f"** {STARTER_VERSION}: MinorCPU (scalar) @ {args.clock}, "
      f"bp={args.bp}, pf={args.pf}"
      + (f" (degree {args.pf_degree})" if args.pf in ("nextline", "stride")
         else "")
      + f", L1D mshrs={args.mshrs}, ras={args.ras_entries}"
      + f", indirect={args.indirect}: {process.cmd}")
exit_event = m5.simulate()
print(f"** exited @ tick {m5.curTick()}: {exit_event.getCause()}")
