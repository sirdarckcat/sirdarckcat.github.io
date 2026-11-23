#!/bin/bash
# bench_split.py under every opt-in sieve variant of this tree, one line each: the kernel-by-kernel attribution of a 2^24 vector window (ms), campaign to be paused by the caller.
#   bash splitab.sh /content/m89_8.json [extra bench_split.py args]
# Production is DEEP_STAGED=1 rcta 8, 512 generate threads, 512 tile threads, rg 32 (what the base row runs).
SPEC=${1:?usage: splitab.sh spec.json}
shift
cd "$(dirname "$0")"
COMMON="--rg 32 --rcta 8 --gen-threads 512 --tile-threads 512 $*"
run() {   # label, env assignments... (BS_ARGS="--tile 18" adds arguments to bench_split.py instead of an environment variable)
    local label=$1; shift
    local out extra="" envs=() a
    for a in "$@"; do case "$a" in BS_ARGS=*) extra="${a#BS_ARGS=}";; *) envs+=("$a");; esac; done
    out=$(env "${envs[@]}" python3 bench_split.py "$SPEC" $COMMON $extra 2>&1)
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
# the tile kernel's unroll depth beyond 4 (50 / 96 registers, 1 CTA of 512 threads an SM: registers are not the limit; ~28 instructions a prime at every depth)
run "TILE_UNROLL=8 (+ PACK HOIST FLUSH2 ORDER PF)"  DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_TILE_UNROLL=8 DEEP_TILE_PREFETCH=256
run "TILE_UNROLL=16 (+ PACK HOIST FLUSH2 ORDER PF)" DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_TILE_UNROLL=16 DEEP_TILE_PREFETCH=256
# the L2 prefetch of the whole bin (packed bins are ~360 KB a (row, tile): 256 KB covers 70%); with 1 tile CTA an SM the bin reads of a wave all hit the DRAM together, ~45 us for the 68 MB of 188 bins
run "PF=384 (whole bin) on all"        DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=384
run "PF=512 on all"                    DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=512
run "PF=256 on all (reference)"        DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256
# tiles of 2^18 bits (32 KB of shared memory): 3 tile CTAs an SM instead of 1, so the apply's DRAM waits of one CTA overlap the small-prime marks of another; the price is twice the tiles, i.e. twice
# the small-prime table through the L2 (100 GB a window).  Never timed so far.
STACK="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4"
run "stack, tile 19 (reference), PF=256"          $STACK DEEP_TILE_PREFETCH=256
run "stack, tile 18, PF=128"                      $STACK DEEP_TILE_PREFETCH=128 BS_ARGS="--tile 18"
run "stack, tile 18, no PF"                       $STACK BS_ARGS="--tile 18"
run "stack, tile 18, tile unroll 2"               DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=2 BS_ARGS="--tile 18"
# the pipelined tile kernel (DEEP_TILE_PIPE=1): the bin streams through shared memory (cp.async, 2 x TILE_PIPE_CH words) while the other warps make the small primes' marks; 96 KB of shared memory.
# AT = threads that apply (default 128 = 4 of 16 warps), CH = words a chunk (default 4092 = 16 KB).  No PF: the copies replace it.
PIPE_STACK="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PIPE=1"
run "TILE_PIPE AT=128 CH=4092"       $PIPE_STACK
run "TILE_PIPE AT=64 CH=4092"        $PIPE_STACK DEEP_TILE_PIPE_AT=64
run "TILE_PIPE AT=192 CH=4092"       $PIPE_STACK DEEP_TILE_PIPE_AT=192
run "TILE_PIPE AT=128 CH=2040"       $PIPE_STACK DEEP_TILE_PIPE_CH=2040
# TIMING PROBE (the bits are wrong, read only the tile line): every small-prime table entry from a 256-entry sample of the table (L1-resident): does the table's trip through the L2 bound the tile kernel's small-prime phase?
run "PROBE: tile table from L1 (unroll 4, PF 256)" DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256 DEEP_TILE_PROBE=1
# the generate kernel's fixed per-CTA latencies and the visit's reductions (GEN_SCAN2 shuffle scan: 3 barriers instead of 16; GEN_RESV_LATE: the reservation's atomic round trip hides behind pass B; GEN_MINRED: 2 instructions fewer a visit)
LEAN="DEEP_GEN_SCAN2=1 DEEP_GEN_RESV_LATE=1 DEEP_GEN_MINRED=1"
GSTACK="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256"
run "stack + SCAN2"                 $GSTACK DEEP_GEN_SCAN2=1
run "stack + RESV_LATE"             $GSTACK DEEP_GEN_RESV_LATE=1
run "stack + MINRED"                $GSTACK DEEP_GEN_MINRED=1
run "stack + all three (LEAN)"      $GSTACK $LEAN
run "stack + LEAN + pipelined tile AT=64" DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PIPE=1 DEEP_TILE_PIPE_AT=64 $LEAN
