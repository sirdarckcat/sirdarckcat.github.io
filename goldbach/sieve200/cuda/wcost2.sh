#!/bin/bash
# wcost2.sh (uarch session, 23 Nov 2026): where the ~30 ms of FIXED sieve cost a window goes (wcost 09:38Z, 89-moduli vector, B = 1e8, staged, 512-thread tile CTAs: 2^25 members 163.6 ms, 2^24 members 96.8 ms
# of sieve (gen + tiles), i.e. 30 ms + 67 ms a 2^24 members; with one 2^24 window a vector the fixed part is 28% of the window and 7% of a batch).  The pair visits (5.76M large primes x 1,248 rows = 7.2e9)
# should cost ~0.5-3 ms at 4 instructions a pair, so the rest is probably per row group: ~80 groups (rg = 16) x (a gen launch, the tile launch, a blocking read of the bin-overflow flag ~100-200 us) = 10-20 ms,
# plus per-window set-up.  Test: the sieve alone at 2^24 with larger row groups (fewer launches and syncs), more primes a thread, and a 2^23 window to separate the per-member part.
# If the wall of a 2^24 window falls by 10 ms or more with rg 32 / 64, the vector mode gains ~2-3% of a batch for free (the a2 bubble, GBATCH_GROUP_DELAY_US, is per group too: fewer groups, fewer bubbles).
# Campaign paused (SIGSTOP) and resumed whatever happens.  Output /content/wcost2/out.txt.
OUT=/content/wcost2/out.txt; mkdir -p /content/wcost2; : > $OUT
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
cd /content/ua_v3/goldbach/sieve200/cuda
SPEC=/content/m89_8.json
run() {   # label args
  echo "--- $1" >> $OUT
  timeout 600 python3 bench_batch.py $SPEC --B 100000000 --f 0.97 --staged 1 --reps 3 --tile-threads 512 $2 >> $OUT 2>&1 || echo "FAILED $1" >> $OUT
}
run "rg 16 ks 24 (control)"        "--ks 24 --rg 16"
run "rg 32 ks 24"                  "--ks 24 --rg 32"
run "rg 64 ks 24"                  "--ks 24 --rg 64"
run "rg 128 ks 24"                 "--ks 24 --rg 128"
run "rg 32 ppt 8 ks 24"            "--ks 24 --rg 32 --ppt 8"
run "rg 16 ks 23 (per-member part)" "--ks 23 --rg 16"
run "rg 64 ks 23"                  "--ks 23 --rg 64"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo WCOST2-DONE >> $OUT
