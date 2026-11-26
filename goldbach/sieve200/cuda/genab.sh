#!/bin/bash
# bench_split.py's generate-kernel lines (ms a 2^24 window: gen = pass A + pass B) for the unroll depth, the CTA size and the staging buffer of gbig_gen_st, on top of the options already in production
# (packed bins, hoisted loops, flat flush, grid order, tile unroll 4 + prefetch).  Campaign to be paused by the caller.
#   bash genab.sh /content/m89_8.json [extra bench_split.py args]
# Why: at 2 CTAs an SM (smem 37.9 KB each) a warp runs ~14-28 visit iterations a pass, each waiting for its prime-table load (~300-600 cycles) before ~25 instructions of work; flat flush
# (-50% instructions) took only -4.9 ms, so the kernel is bound by latency, not issue.  GEN_UNROLL = 4 | 8 keeps 4 | 8 table loads in flight a warp (clamped loads: ~23-24 instructions a
# visit at every depth, as unroll 1); a smaller staging buffer / CTA means more CTAs an SM (4096 words, 256 threads: 4 CTAs of 20.9 KB).
SPEC=${1:?usage: genab.sh spec.json}
shift
cd "$(dirname "$0")"
BASE="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256"
run() {   # label, bench_split args, extra env...
    local label=$1 args=$2; shift 2
    local out gen genA genB
    out=$(env $BASE "$@" python3 bench_split.py "$SPEC" --rg 32 --tile-threads 512 $args 2>&1)
    gen=$(echo "$out" | awk '/^  gen \(staged/ {print $NF}')
    genA=$(echo "$out" | awk '/pass A/ {print $NF}')
    genB=$(echo "$out" | awk '/pass B/ {print $NF}')
    printf "%-46s gen %7s (A %6s B %6s)\n" "$label" "$gen" "$genA" "$genB"
    echo "$out" | grep -q SPLIT-DONE || { echo "  (failed:)"; echo "$out" | tail -3; }
}
EXTRA="$*"
run "unroll 1 (gen 512, rcta 8, stage 8192)"   "--rcta 8 --gen-threads 512 --stage-cap 8192 $EXTRA"
run "unroll 2"                                 "--rcta 8 --gen-threads 512 --stage-cap 8192 $EXTRA" DEEP_GEN_UNROLL=2
run "unroll 4"                                 "--rcta 8 --gen-threads 512 --stage-cap 8192 $EXTRA" DEEP_GEN_UNROLL=4
run "unroll 8"                                 "--rcta 8 --gen-threads 512 --stage-cap 8192 $EXTRA" DEEP_GEN_UNROLL=8
run "gen 256, stage 8192 (2 CTAs, 8 warps), unroll 4" "--rcta 8 --gen-threads 256 --stage-cap 8192 $EXTRA" DEEP_GEN_UNROLL=4
run "gen 256, stage 6144 (3 CTAs an SM), unroll 4"    "--rcta 8 --gen-threads 256 --stage-cap 6144 $EXTRA" DEEP_GEN_UNROLL=4
run "gen 256, stage 4096 (4 CTAs an SM), unroll 4"    "--rcta 8 --gen-threads 256 --stage-cap 4096 $EXTRA" DEEP_GEN_UNROLL=4
run "gen 256, stage 4096, unroll 1"                   "--rcta 8 --gen-threads 256 --stage-cap 4096 $EXTRA"
run "gen 512, rcta 16, stage 8192, unroll 4"          "--rcta 16 --gen-threads 512 --stage-cap 8192 $EXTRA" DEEP_GEN_UNROLL=4
