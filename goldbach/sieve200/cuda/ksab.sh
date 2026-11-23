#!/bin/bash
# bench_split.py on windows of 2^24 / 2^25 / 2^26 members (--ks), with the six options in production: what does a LONGER window of ONE vector cost a member?
#   bash ksab.sh /content/m89_8.json [extra bench_split.py args]
# Why: a (prime, row) pair is visited once a window and marks 2^ks / s times: the visits (pass A + pass B: 54% of the generate kernel's instructions, and the loads the kernel waits for) are
# paid a window, the marks a member.  A window of 2^26 has 1/4 of the visits a member (with 2 rows a CTA: a CTA's visit work is ~1/4 and its mark work the same, so the CTA is ~half the instructions
# and a quarter of the load waits).  The tile kernel is the same per member (a CTA is a (row, tile) either way).  Needs NB = rcta x 2^(ks - 19) <= gen threads, so rcta 2 / 256 threads at 2^26.
# The line to read: ms a 2^24 members = the printed times / (2^(ks - 24)).  Memory: the bit matrix is 1,248 x 2^ks / 8 bytes (2.6 / 5.2 / 10.4 GB).
SPEC=${1:?usage: ksab.sh spec.json}
shift
cd "$(dirname "$0")"
BASE="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256"
run() {   # label, ks, bench_split args, extra env...
    local label=$1 ks=$2 args=$3; shift 3
    local out gen genA genB tile small apply sieve div=$(( 1 << (ks - 24) ))
    out=$(env $BASE "$@" python3 bench_split.py "$SPEC" --ks $ks --rg 32 --tile-threads 512 $args 2>&1)
    gen=$(echo "$out" | awk '/^  gen \(staged/ {print $NF}'); genA=$(echo "$out" | awk '/pass A/ {print $NF}'); genB=$(echo "$out" | awk '/pass B/ {print $NF}')
    tile=$(echo "$out" | awk '/^  tile kernel/ {print $NF}'); small=$(echo "$out" | awk '/small-prime marks/ {print $3}'); apply=$(echo "$out" | awk '/bin apply/ {print $3}')
    sieve=$(echo "$out" | awk '/^whole window/ {for (i=1;i<=NF;i++) if ($i=="sieve") print $(i+1)}')
    awk -v l="$label" -v d=$div -v g="$gen" -v a="$genA" -v b="$genB" -v t="$tile" -v s="$small" -v p="$apply" -v w="$sieve" \
        'BEGIN {printf "%-40s a 2^24 members: gen %6.1f (A %5.1f B %5.1f)  tile %6.1f (small %5.1f apply %5.1f)  sieve phase %6.1f\n", l, g/d, a/d, b/d, t/d, s/d, p/d, w/d}'
    echo "$out" | grep -q SPLIT-DONE || { echo "  (failed:)"; echo "$out" | tail -3; }
}
EXTRA="$*"
run "2^24, rcta 8, gen 512 (production)"          24 "--rcta 8 --gen-threads 512 $EXTRA"
run "2^25, rcta 4, gen 512"                       25 "--rcta 4 --gen-threads 512 $EXTRA"
run "2^25, rcta 2, gen 256"                       25 "--rcta 2 --gen-threads 256 $EXTRA"
run "2^26, rcta 2, gen 256"                       26 "--rcta 2 --gen-threads 256 $EXTRA"
run "2^26, rcta 1, gen 256"                       26 "--rcta 1 --gen-threads 256 $EXTRA"
run "2^26, rcta 2, gen 256, unroll 4"             26 "--rcta 2 --gen-threads 256 $EXTRA" DEEP_GEN_UNROLL=4
run "2^26, rcta 4, gen 512"                       26 "--rcta 4 --gen-threads 512 $EXTRA"
