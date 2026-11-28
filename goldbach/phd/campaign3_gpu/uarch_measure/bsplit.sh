#!/bin/bash
# uarch bench_split.py (2c49ba1): where a vector window's sieve time goes, kernel by kernel (gen pass A / B, the tile kernel's small-prime marks, bin apply, init + write),
# on this RTX PRO 6000 in /content/ua_v4 (ua_v3 + 0e45ea8's sieve200/cuda; bench_split.py added), four configurations; campaign paused, resumed whatever happens.
OUT=/content/bsplit.txt; : > $OUT
cp /content/bench_split_2c49ba1.py /content/ua_v4/goldbach/sieve200/cuda/bench_split.py
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
cd /content/ua_v4/goldbach/sieve200/cuda
for a in "--rg 32 --rcta 2 --gen-threads 256 --tile-threads 512" "--rg 32 --rcta 8 --gen-threads 512 --tile-threads 512" "--rg 8 --rcta 2 --gen-threads 256 --tile-threads 512" "--rg 4 --rcta 2 --gen-threads 256 --tile-threads 512"; do
  echo "--- $a" >> $OUT
  timeout 600 python3 bench_split.py /content/m89_8.json $a >> $OUT 2>&1 || echo "FAILED rc=$? ($a)" >> $OUT
done
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo BSPLIT-DONE >> $OUT
