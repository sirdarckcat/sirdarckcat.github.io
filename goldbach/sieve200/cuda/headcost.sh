#!/bin/bash
# headcost.sh (uarch session, 23 Nov 2026): what a DEEP HEAD would cost.  Idea (HEADROOM.md 2, "a deeper sieve for the first rows only"): the rows are tested in ascending q until the first PRP, so the
# first alive row of a member carries most of the tests (a row of index i among the 1,248 is tested with probability ~ exp(-0.022 i): 90% of all tests are on the first ~100 rows), and
# the alive rows (no factor below 1e8) of those rows have a prime factor in (1e8, 1e9] with probability 11.1% (ln(ln 1e9 / ln 1e8) = 0.118): sieving ONLY the first ~64-100 rows by the primes in (1e8, 1e9] removes
# those composites from the tested rows: 8-10% of all Fermat tests (25-30 ms of the ~0.30 s of Fermat of a 2^24 window) for 45M primes x 64-100 rows = 3-4.5e9 pair visits and ~1.3e8 marks.
# Whether it pays depends on the stage's real cost for that shape, which the model cannot say (the current stage's ~30 ms FIXED part is 7.2e9 pair visits and ~80 groups).  This script times it alone with
# bench_bigprimes.py (the large-prime stage in isolation, random roots, as it is built for the deep bound): primes in (2^27, 2^30] (1.3e8 .. 1.07e9; 49M of them), a 2^24 window, 64 / 128 rows.
# Break-even: the stage's wall time a window (ms) x ~0.55 (the sieve's tax on the Fermat kernel when hidden) against ~25 ms saved: below ~35 ms it pays (net +4-6% of a batch), above ~50 ms it does not.
# Needs /content/ua_v3 (bench_bigprimes.py, gbig.py); each run builds the prime list with numpy (~2 min) and a 780 MB table.  Campaign paused (SIGSTOP), resumed whatever happens.  Output /content/headcost/out.txt.
OUT=/content/headcost/out.txt; mkdir -p /content/headcost; : > $OUT
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
cd /content/ua_v3/goldbach/sieve200/cuda
run() {   # label args
  echo "--- $1" >> $OUT
  timeout 900 python3 bench_bigprimes.py --plo 27 --b 30 --ks 24 --staged 1 $2 >> $OUT 2>&1 || echo "FAILED $1" >> $OUT
}
run "64 rows, rg 16, rcta 2 (as the stage is today)"        "--rows 64 --rg 16 --rcta 2"
run "64 rows, rg 16, rcta 8, 512 threads"                   "--rows 64 --rg 16 --rcta 8 --threads 512"
run "128 rows, rg 32, rcta 8, 512 threads"                  "--rows 128 --rg 32 --rcta 8 --threads 512"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo HEADCOST-DONE >> $OUT
