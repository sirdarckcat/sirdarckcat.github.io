#!/bin/bash
# uarch bench_rows.py (df715e1): the window's rows kernel and its variants (rows2, rows without stores / without loads, order + rows_ord / rows_ord2, rowmask / rowlist) on a synthetic
# window (no sieve), on this RTX PRO 6000, in /content/ua_v11 (ua_v3 + df715e1's sieve200/cuda). Campaign paused, resumed whatever happens.
OUT=/content/brows.txt; : > $OUT
[ -d /content/ua_v11 ] || cp -a /content/ua_v3 /content/ua_v11
tar -xzf /content/ua11_cuda.tgz -C /content/ua_v11/goldbach/sieve200/cuda
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
cd /content/ua_v11/goldbach/sieve200/cuda && timeout 300 python3 bench_rows.py >> $OUT 2>&1 || echo "FAILED rc=$?" >> $OUT
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo BROWS-DONE >> $OUT
