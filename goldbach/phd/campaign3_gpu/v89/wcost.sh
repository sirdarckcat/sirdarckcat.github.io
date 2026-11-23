#!/bin/bash
# Deep-sieve cost per window at 2^24 and 2^25 members, 88-moduli (Q = 170,000, 1,262 rows) and 89-moduli (1,248 rows) vectors, B = 1e8, staged, 512-thread
# tile CTAs (production), no bubble (the sieve alone). Campaign paused (SIGSTOP), resumed at the end, whatever happens.
OUT=/content/wcost/out.txt; mkdir -p /content/wcost; : > $OUT
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
cd /content/ua_v3/goldbach/sieve200/cuda
for spec in /content/probe/s25.json /content/m89_8.json; do
  for ks in 25 24; do
    echo "--- $spec ks $ks" >> $OUT
    timeout 600 python3 bench_batch.py $spec --B 100000000 --ks $ks --f 0.97 --staged 1 --reps 3 --tile-threads 512 >> $OUT 2>&1 || echo "FAILED $spec $ks" >> $OUT
  done
done
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo WCOST-DONE >> $OUT
