#!/bin/bash
# uarch splitab.sh (8558276: + DEEP_GEN_FLUSH2, DEEP_GEN_ORDER): bench_split.py under every opt-in sieve variant (DEEP_BIN_PACK, DEEP_GEN_HOIST, DEEP_TILE_UNROLL, DEEP_TILE_PREFETCH) at the production geometry,
# in /content/ua_v6 (a copy of /content/ua_v3 with 8558276's whole sieve200/cuda over it); production's tree untouched. Campaign paused, resumed whatever happens.
OUT=/content/splitab6.txt; : > $OUT
[ -d /content/ua_v6 ] || cp -a /content/ua_v3 /content/ua_v6
tar -xzf /content/ua6_cuda.tgz -C /content/ua_v6/goldbach/sieve200/cuda
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
timeout 1200 bash /content/ua_v6/goldbach/sieve200/cuda/splitab.sh /content/m89_8.json >> $OUT 2>&1 || echo "FAILED rc=$?" >> $OUT
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo SPLITAB6-DONE >> $OUT
