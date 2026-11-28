#!/bin/bash
# wcost3.sh (uarch session, 23 Nov 2026): the sieve of a 2^24 vector window against the row-group size AND the rows a generate CTA (rcta) / its threads.  wcost2 (11:07Z): rg 32 / 64 take 6.5-7 ms off a window (95.2 -> 88.7 / 88.1 ms),
# deployed as rg 32 without bubble.  headcost (11:09Z) showed that rcta matters far more for the pair visits than I had assumed: the same stage (46.8M primes x 64 rows) costs 39.0 ms of generate at rcta 2 and 15.0 ms at
# rcta 8 with 512 threads (a CTA reads its chunk of the prime table once for rcta rows, so the table is re-read 4x less).  Production still runs rcta 2 (DEEP_RCTA, set when a 2^25 window gained only 6.6 ms from rcta 8,
# DEEPSIEVE.md section H); with the fixed part now the larger share of a 2^24 window (40-55 ms) the gain may be bigger.  Sieve alone, 89-moduli vector, B = 1e8, 512-thread tiles; campaign paused, resumed whatever happens.
# Output /content/wcost3/out.txt.  Read the "sieve (gen + tiles)" column; the control is rg 32 rcta 2 (production).
OUT=/content/wcost3/out.txt; mkdir -p /content/wcost3; : > $OUT
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
cd /content/ua_v3/goldbach/sieve200/cuda
SPEC=/content/m89_8.json
run() {   # label args
  echo "--- $1" >> $OUT
  timeout 600 python3 bench_batch.py $SPEC --B 100000000 --f 0.97 --staged 1 --reps 3 --tile-threads 512 --ks 24 $2 >> $OUT 2>&1 || echo "FAILED $1" >> $OUT
}
run "rg 32 rcta 2 gen 256 (production)"   "--rg 32 --rcta 2"
run "rg 32 rcta 4 gen 256"                "--rg 32 --rcta 4"
run "rg 32 rcta 8 gen 256"                "--rg 32 --rcta 8"
run "rg 32 rcta 8 gen 512"                "--rg 32 --rcta 8 --gen-threads 512"
run "rg 64 rcta 8 gen 512"                "--rg 64 --rcta 8 --gen-threads 512"
run "rg 32 rcta 16 gen 1024 stage 6144"   "--rg 32 --rcta 16 --gen-threads 1024 --stage-cap 6144"
run "rg 64 rcta 16 gen 1024 stage 6144"   "--rg 64 --rcta 16 --gen-threads 1024 --stage-cap 6144"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo WCOST3-DONE >> $OUT
