#!/bin/bash
# uarch genab.sh and splitab.sh (0d42e4d: generate unroll with clamped loads, smaller generate CTAs, rcta 16; tile unroll 8 / 16) on this RTX PRO 6000, in /content/ua_v7 (a copy of
# /content/ua_v3 with 0d42e4d's whole sieve200/cuda over it); production's tree untouched. Campaign paused, resumed whatever happens.
OUT=/content/genab.txt; : > $OUT
[ -d /content/ua_v7 ] || cp -a /content/ua_v3 /content/ua_v7
tar -xzf /content/ua7_cuda.tgz -C /content/ua_v7/goldbach/sieve200/cuda
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
echo "--- genab.sh" >> $OUT
timeout 1200 bash /content/ua_v7/goldbach/sieve200/cuda/genab.sh /content/m89_8.json >> $OUT 2>&1 || echo "FAILED genab rc=$?" >> $OUT
echo "--- splitab.sh" >> $OUT
timeout 1200 bash /content/ua_v7/goldbach/sieve200/cuda/splitab.sh /content/m89_8.json >> $OUT 2>&1 || echo "FAILED splitab rc=$?" >> $OUT
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo GENAB-DONE >> $OUT
