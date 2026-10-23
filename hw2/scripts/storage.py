#!/usr/bin/env python3
"""CS 423 HW2 — storage (in bits) of a direction predictor or an L1D
prefetcher, with the counting rules of the handout (Bonus Task 5).

Usage (inside or outside the container; plain Python 3, no gem5 needed):
    python3 scripts/storage.py BiModeBP globalPredictorSize=4096
    python3 scripts/storage.py TAGE logTagTableSizes=11,9,9,9,9,9,9,9
    python3 scripts/storage.py LTAGE logSizeLoopPred=4
    python3 scripts/storage.py StridePrefetcher table_entries=32
    python3 scripts/storage.py DCPTPrefetcher table_entries=16 deltas_per_entry=16

Parameters you do not give take gem5 v25.1.0.1's defaults (the same
names as in BranchPredictor.py / Prefetcher.py). For LTAGE, parameters of
its TAGE part and of its loop predictor go on the same command line.

Counting rules (the handout's, Bonus Task 5):
  * Count every table: entries x all fields of an entry. A field whose width
    a parameter declares counts that width (counters, tags such as TAGE's
    tagTableTagWidths or BOP's tag_bits, TAGE's useful bits, confidence,
    delta_bits, ...).
  * Count every history register: the global history at the longest length
    the design uses (TAGE: maxHist), the path history (pathHistBits); local
    histories are a table (entries x history bits).
  * Prefetcher fields without a declared width: a stored address, PC or
    tag counts 48 bits; a stride, delta or offset counts 16 bits; per-block
    state counts its declared bits per block.
  * Do NOT count: valid bits, replacement state (LRU), the prefetch queue
    (keep queue_size at its default), the cache's per-block prefetched bit,
    statistics/epoch counters, and exactly these single counters: TAGE's
    useAltOnNa counter(s) and useful-bit reset counter, the loop
    predictor's WITHLOOP counter.
  * Classes this script does not support: apply the same rules table by
    table, from the class's parameters and the entry struct in its .hh
    file, and show that table in your report.

TournamentBP is not supported on purpose: its storage is Task 1 Q1.3, and
it is the budget of Bonus Task 5.1 (the script checks the budget for you).

Supported: LocalBP, BiModeBP, TAGE, LTAGE, TaggedPrefetcher,
StridePrefetcher, DCPTPrefetcher, AMPMPrefetcher, SmsPrefetcher. For any other class (or your own), compute the storage
yourself with the same rules and show the arithmetic in your report.
"""
import math
import sys

ADDR = 48          # bits per stored address / PC / tag (prefetchers)
DELTA = 16         # bits per stored stride / delta (prefetchers)


def clog2(n):
    return int(math.ceil(math.log2(n)))


DEFAULTS = {
    "LocalBP": dict(localPredictorSize=2048, localCtrBits=2),
    "TournamentBP": dict(localPredictorSize=2048, localCtrBits=2,
                         localHistoryTableSize=2048, globalPredictorSize=8192,
                         globalCtrBits=2, choicePredictorSize=8192,
                         choiceCtrBits=2),
    "BiModeBP": dict(globalPredictorSize=8192, globalCtrBits=2,
                     choicePredictorSize=8192, choiceCtrBits=2),
    "TAGE": dict(nHistoryTables=7, maxHist=130,
                 tagTableTagWidths=[0, 9, 9, 10, 10, 11, 11, 12],
                 logTagTableSizes=[13, 9, 9, 9, 9, 9, 9, 9],
                 logRatioBiModalHystEntries=2, tagTableCounterBits=3,
                 tagTableUBits=2, pathHistBits=16),
    # LTAGE = TAGE with LTAGE_TAGE's sizes + a loop predictor. If your
    # config gives LTAGE a tage=TAGEBase(...) object, pass that object's
    # sizes (nHistoryTables, maxHist, tagTableTagWidths, logTagTableSizes).
    "LTAGE": dict(nHistoryTables=12, maxHist=640,
                  tagTableTagWidths=[0, 7, 7, 8, 8, 9, 10, 11, 12, 12, 13,
                                     14, 15],
                  logTagTableSizes=[14, 10, 10, 11, 11, 11, 11, 10, 10, 10,
                                    10, 9, 9],
                  logRatioBiModalHystEntries=2, tagTableCounterBits=3,
                  tagTableUBits=2, pathHistBits=16,
                  logSizeLoopPred=8, loopTableAgeBits=8,
                  loopTableConfidenceBits=2, loopTableTagBits=14,
                  loopTableIterBits=14, useDirectionBit=0, useSpeculation=0),
    "TaggedPrefetcher": dict(degree=2),
    "StridePrefetcher": dict(table_entries=64, confidence_counter_bits=3),
    # parameters of the inner dcpt= / ampm= objects go on the same line
    "DCPTPrefetcher": dict(table_entries=128, deltas_per_entry=20,
                           delta_bits=12),
    "AMPMPrefetcher": dict(access_map_table_entries=256, hot_zone_size=2048),
    "SmsPrefetcher": dict(ft_size=64, pht_size=16384, region_size=4096),
}


def local_bp(p):
    ctrs = p["localPredictorSize"] // p["localCtrBits"]
    return [("counters", ctrs, p["localCtrBits"])]


def tournament_bp(p):
    lhist = clog2(p["localPredictorSize"])
    ghist = max(clog2(p["globalPredictorSize"]),
                clog2(p["choicePredictorSize"]))
    return [
        ("local counters", p["localPredictorSize"], p["localCtrBits"]),
        (f"local history table ({lhist}-bit histories)",
         p["localHistoryTableSize"], lhist),
        ("global counters", p["globalPredictorSize"], p["globalCtrBits"]),
        ("choice counters", p["choicePredictorSize"], p["choiceCtrBits"]),
        ("global history register", 1, ghist),
    ]


def bimode_bp(p):
    ghist = clog2(p["globalPredictorSize"])
    return [
        ("taken direction table", p["globalPredictorSize"],
         p["globalCtrBits"]),
        ("not-taken direction table", p["globalPredictorSize"],
         p["globalCtrBits"]),
        ("choice counters", p["choicePredictorSize"], p["choiceCtrBits"]),
        ("global history register", 1, ghist),
    ]


# TAGEBase parameters that do not change the storage (accepted, ignored)
TAGE_OTHER = ["minHist", "histBufferSize", "logUResetPeriod", "numUseAltOnNa",
              "initialTCounterValue", "useAltOnNaBits", "maxNumAlloc",
              "speculativeHistUpdate", "takenOnlyHistory", "instShiftAmt",
              "noSkip"]
LOOP_OTHER = ["withLoopBits", "logLoopTableAssoc", "useHashing",
              "restrictAllocation", "initialLoopIter", "initialLoopAge",
              "optionalAgeReset"]
for k in TAGE_OTHER:
    DEFAULTS["TAGE"].setdefault(k, None)
    DEFAULTS["LTAGE"].setdefault(k, None)
for k in LOOP_OTHER:
    DEFAULTS["LTAGE"].setdefault(k, None)


def tage(p):
    n = p["nHistoryTables"]
    logs = p["logTagTableSizes"]
    tags = p["tagTableTagWidths"]
    if len(logs) != n + 1 or len(tags) != n + 1:
        sys.exit("logTagTableSizes and tagTableTagWidths need "
                 "nHistoryTables + 1 entries")
    rows = [("bimodal prediction bits", 2 ** logs[0], 1),
            ("bimodal hysteresis bits",
             2 ** (logs[0] - p["logRatioBiModalHystEntries"]), 1)]
    enabled = p.get("noSkip") or [1] * (n + 1)
    if isinstance(enabled, int):
        enabled = [enabled]
    for i in range(1, n + 1):
        if i < len(enabled) and not enabled[i]:
            continue                       # table disabled by noSkip
        w = tags[i] + p["tagTableCounterBits"] + p["tagTableUBits"]
        rows.append((f"tagged table {i} (tag {tags[i]} + ctr "
                     f"{p['tagTableCounterBits']} + u {p['tagTableUBits']})",
                     2 ** logs[i], w))
    rows.append(("global history register (maxHist)", 1, p["maxHist"]))
    rows.append(("path history register", 1, p["pathHistBits"]))
    return rows


def ltage(p):
    rows = tage(p)
    iters = 3 if p["useSpeculation"] else 2
    w = (iters * p["loopTableIterBits"] + p["loopTableConfidenceBits"]
         + p["loopTableTagBits"] + p["loopTableAgeBits"]
         + (1 if p["useDirectionBit"] else 0))
    rows.append((f"loop predictor ({iters} x iter + conf + tag + age"
                 f"{' + dir' if p['useDirectionBit'] else ''})",
                 2 ** p["logSizeLoopPred"], w))
    return rows


def tagged_pf(p):
    return [("(no table: uses the cache's per-block prefetched bit)", 0, 0)]


def stride_pf(p):
    w = ADDR + ADDR + DELTA + p["confidence_counter_bits"]
    return [(f"PC table (PC tag {ADDR} + last address {ADDR} + stride "
             f"{DELTA} + confidence {p['confidence_counter_bits']})",
             p["table_entries"], w)]


def dcpt_pf(p):
    w = ADDR + ADDR + p["deltas_per_entry"] * p["delta_bits"]
    return [(f"table (PC tag {ADDR} + last address {ADDR} + "
             f"{p['deltas_per_entry']} deltas x {p['delta_bits']})",
             p["table_entries"], w)]


def ampm_pf(p):
    blocks = p["hot_zone_size"] // 64
    return [(f"access maps (zone tag {ADDR} + {blocks} blocks x 2-bit state)",
             p["access_map_table_entries"], ADDR + 2 * blocks)]


def sms_pf(p):
    blocks = p["region_size"] // 64
    off = clog2(blocks)
    return [
        (f"filter table (region tag {ADDR} + PC {ADDR} + offset {off})",
         p["ft_size"], 2 * ADDR + off),
        (f"active generation table (... + {blocks}-bit pattern)",
         p["ft_size"], 2 * ADDR + off + blocks),
        (f"pattern history table (PC {ADDR} + offset {off} + {blocks}-bit "
         f"pattern)", p["pht_size"], ADDR + off + blocks),
    ]


FUNCS = {"LocalBP": local_bp, "TournamentBP": tournament_bp,
         "BiModeBP": bimode_bp, "TAGE": tage, "LTAGE": ltage,
         "TaggedPrefetcher": tagged_pf, "StridePrefetcher": stride_pf,
         "DCPTPrefetcher": dcpt_pf, "AMPMPrefetcher": ampm_pf,
         "SmsPrefetcher": sms_pf}

BUDGET_PF = 8192   # bits (1 KiB), Bonus Task 5.2


def total(rows):
    return sum(n * w for _, n, w in rows)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "TournamentBP":
        sys.exit("TournamentBP: compute it yourself (Task 1 Q1.3)")
    if len(sys.argv) < 2 or sys.argv[1] not in FUNCS:
        print(__doc__)
        sys.exit(1)
    cls = sys.argv[1]
    p = dict(DEFAULTS[cls])
    for arg in sys.argv[2:]:
        k, _, v = arg.partition("=")
        if k not in p:
            sys.exit(f"{cls}: unknown or unsupported parameter '{k}'")
        conv = lambda x: {"true": 1, "false": 0}.get(x.lower(), x)
        if "," in v:
            p[k] = [int(conv(x)) for x in v.split(",")]
        else:
            v = conv(v)
            try:
                p[k] = int(v)
            except ValueError:
                p[k] = v                   # e.g. a memory size string
    rows = FUNCS[cls](p)
    print(f"{cls} {' '.join(sys.argv[2:])}".rstrip())
    for name, n, w in rows:
        if n:
            print(f"  {name:<58} {n:>7} x {w:>3} = {n * w:>8,} bits")
    t = total(rows)
    print(f"  {'total':<58} {'':>17} {t:>8,} bits ({t / 8192:.2f} KiB)")
    if cls.endswith("BP") or cls in ("TAGE", "LTAGE"):
        budget = total(tournament_bp(DEFAULTS["TournamentBP"]))
        print(f"  budget 5.1 (the default TournamentBP's storage, Q1.3): "
              f"{'within' if t <= budget else 'OVER'} budget")
    else:
        print(f"  prefetcher budget: {BUDGET_PF:,} bits -> "
              f"{'within' if t <= BUDGET_PF else 'OVER'} budget "
              f"(a MultiPrefetcher's storage is the sum of its parts)")


if __name__ == "__main__":
    main()
