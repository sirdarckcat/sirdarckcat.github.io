#!/bin/bash
# bench_split.py under every opt-in sieve variant of this tree, one line each: the kernel-by-kernel attribution of a 2^24 vector window (ms), campaign to be paused by the caller.
#   bash splitab.sh /content/m89_8.json [extra bench_split.py args]
# Production is DEEP_STAGED=1 rcta 8, 512 generate threads, 512 tile threads, rg 32 (what the base row runs).
SPEC=${1:?usage: splitab.sh spec.json}
shift
cd "$(dirname "$0")"
COMMON="--rg 32 --rcta 8 --gen-threads 512 --tile-threads 512 $*"
run() {   # label, env assignments...
    local label=$1; shift
    local out
    out=$(env "$@" python3 bench_split.py "$SPEC" $COMMON 2>&1)
    local gen tile genA genB small apply sieve
    gen=$(echo "$out" | awk '/^  gen \(staged/ {print $NF}')
    genA=$(echo "$out" | awk '/pass A/ {print $NF}')
    genB=$(echo "$out" | awk '/pass B/ {print $NF}')
    tile=$(echo "$out" | awk '/^  tile kernel/ {print $NF}')
    small=$(echo "$out" | awk '/small-prime marks/ {print $3}')
    apply=$(echo "$out" | awk '/bin apply/ {print $3}')
    sieve=$(echo "$out" | awk '/^whole window/ {for (i=1;i<=NF;i++) if ($i=="sieve") print $(i+1)}')
    printf "%-34s gen %7s (A %6s B %6s)  tile %7s (small %6s apply %6s)  bench_batch sieve %6s\n" "$label" "$gen" "$genA" "$genB" "$tile" "$small" "$apply" "$sieve"
    echo "$out" | grep -q SPLIT-DONE || { echo "  (failed:)"; echo "$out" | tail -3; }
}
run "base (rcta 8, 512)"          DEEP_BIN_PACK=0
run "DEEP_BIN_PACK=1"             DEEP_BIN_PACK=1
run "DEEP_GEN_HOIST=1"            DEEP_GEN_HOIST=1
run "PACK + HOIST"                DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1
run "DEEP_TILE_UNROLL=2"          DEEP_TILE_UNROLL=2
run "DEEP_TILE_UNROLL=4"          DEEP_TILE_UNROLL=4
run "DEEP_TILE_PREFETCH=256"      DEEP_TILE_PREFETCH=256
run "PACK + HOIST + UNROLL=4"     DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_TILE_UNROLL=4
run "PACK + HOIST + UNROLL=4 + PF" DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256
# the flat flush of the staging buffer (a thread a word instead of a warp a bin: ~half of the kernel's instructions) and the grid order (the slices of a chunk together: the prime table from DRAM once a group)
run "DEEP_GEN_FLUSH2=1"           DEEP_GEN_FLUSH2=1
run "DEEP_GEN_ORDER=1"            DEEP_GEN_ORDER=1
run "HOIST + FLUSH2"              DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1
run "PACK + HOIST + FLUSH2"       DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1
run "PACK + HOIST + FLUSH2 + ORDER" DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1
run "ALL (+ UNROLL=4 + PF)"       DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256
