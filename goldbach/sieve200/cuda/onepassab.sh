#!/bin/bash
# The one-pass generate kernel (DEEP_GEN_ONEPASS=1, gbig_kernels.cuh "one-pass kernel") against production, bench_split.py's lines (ms a 2^24 window).  Campaign to be paused by the caller.
#   bash onepassab.sh /content/m89_8.json [extra bench_split.py args]
# Why: gbig_gen_st visits every (prime, row) pair twice (pass A counts the marks of each bin, pass B visits again to place them); here each bin owns SLOT_C shared-memory words and the counting
# atomic's rank places the mark, so the pairs are visited once and there is no scan.  Production's pass B (17.96 of 28.74 ms at unroll 4) is the second visit + the staging + the flush; the
# flush stays.  With one pass, "pass A" below (cap = 0: the CTA visits, counts, reserves, finds the room too small, returns) is the whole visit work and "pass B" is the flush alone.
# Rows: production (LEAN + unroll 4 + the other options in production), one-pass at 40 slots a bin (44.0 KB a CTA, 2 CTAs an SM), the same at unroll 8, 30 slots with 6144-word chunks (~18
# marks a bin), 25 slots with 4096-word chunks (~12 a bin: 3 CTAs of 512 threads an SM).  Every row prints the generate kernel; the sieve phase is in the full output (SPLIT lines) if wanted.
SPEC=${1:?usage: onepassab.sh spec.json}
shift
cd "$(dirname "$0")"
BASE="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_GEN_SCAN2=1 DEEP_GEN_RESV_LATE=1 DEEP_GEN_MINRED=1 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256"
run() {   # label, bench_split args, extra env...
    local label=$1 args=$2; shift 2
    local out gen genA genB
    out=$(env $BASE "$@" python3 bench_split.py "$SPEC" --rg 32 --tile-threads 512 $args 2>&1)
    gen=$(echo "$out" | awk '/^  gen \(staged/ {print $NF}')
    genA=$(echo "$out" | awk '/pass A/ {print $NF}')
    genB=$(echo "$out" | awk '/pass B/ {print $NF}')
    printf "%-52s gen %7s (A %6s B %6s)\n" "$label" "$gen" "$genA" "$genB"
    echo "$out" | grep -q SPLIT-DONE || { echo "  (failed:)"; echo "$out" | tail -3; }
}
EXTRA="$*"
run "production (rcta 8, gen 512, stage 8192)"         "--rcta 8 --gen-threads 512 --stage-cap 8192 $EXTRA"
run "ONEPASS, 40 slots"                                "--rcta 8 --gen-threads 512 --stage-cap 8192 $EXTRA" DEEP_GEN_ONEPASS=1
run "ONEPASS, 40 slots, 40 registers (bounds 512,3)"   "--rcta 8 --gen-threads 512 --stage-cap 8192 $EXTRA" DEEP_GEN_ONEPASS=1 DEEP_GEN_LB=512,3
run "ONEPASS, 40 slots, unroll 8"                      "--rcta 8 --gen-threads 512 --stage-cap 8192 $EXTRA" DEEP_GEN_ONEPASS=1 DEEP_GEN_UNROLL=8
run "ONEPASS, 30 slots, stage 6144"                    "--rcta 8 --gen-threads 512 --stage-cap 6144 $EXTRA" DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=30
run "ONEPASS, 25 slots, stage 4096 (3 CTAs an SM)"     "--rcta 8 --gen-threads 512 --stage-cap 4096 $EXTRA" DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=25 DEEP_GEN_LB=512,3
run "production again"                                 "--rcta 8 --gen-threads 512 --stage-cap 8192 $EXTRA"
