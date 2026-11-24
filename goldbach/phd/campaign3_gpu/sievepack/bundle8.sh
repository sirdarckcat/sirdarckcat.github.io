#!/bin/bash
# The bundle of small sieve items (uarch 88fe93c..b4e60df) on this RTX PRO 6000, on top of production's stack (PACK HOIST FLUSH2 ORDER GEN_UNROLL=4 TILE_UNROLL=4 PF=256), every row a
# bench_split.py run under its own 120 s timeout (the pipelined tile kernel uses a named barrier: a hang must not stall the campaign). Tree /content/ua_v8 (ua_v3 + b4e60df's sieve200/cuda);
# the first row in production's /content/ua_v7 (the tile kernel's clamped loads are the difference). Campaign paused, resumed whatever happens. ms a 2^24 window.
OUT=/content/bundle8.txt; : > $OUT
[ -d /content/ua_v8 ] || cp -a /content/ua_v3 /content/ua_v8
tar -xzf /content/ua8_cuda.tgz -C /content/ua_v8/goldbach/sieve200/cuda
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
COMMON="--rg 32 --rcta 8 --gen-threads 512 --tile-threads 512"
STACK="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4"
run() {   # label tree extra-args env...
  local label=$1 tree=$2 args=$3; shift 3
  local out
  out=$(cd /content/$tree/goldbach/sieve200/cuda && env $STACK "$@" timeout 120 python3 bench_split.py /content/m89_8.json $COMMON $args 2>&1); local rc=$?
  local gen=$(echo "$out" | awk '/^  gen \(staged/ {print $NF}') genA=$(echo "$out" | awk '/pass A/ {print $NF}') genB=$(echo "$out" | awk '/pass B/ {print $NF}')
  local tile=$(echo "$out" | awk '/^  tile kernel/ {print $NF}') small=$(echo "$out" | awk '/small-prime marks/ {print $3}') apply=$(echo "$out" | awk '/bin apply/ {print $3}')
  local sieve=$(echo "$out" | awk '/^whole window/ {for (i=1;i<=NF;i++) if ($i=="sieve") print $(i+1)}')
  printf "%-40s gen %7s (A %6s B %6s)  tile %7s (small %6s apply %6s)  sieve %6s  rc %s\n" "$label" "$gen" "$genA" "$genB" "$tile" "$small" "$apply" "$sieve" "$rc" >> $OUT
  echo "$out" | grep -q SPLIT-DONE || { echo "  (failed:)" >> $OUT; echo "$out" | tail -3 >> $OUT; }
}
run "ua_v7 (production tree) PF=256"   ua_v7 ""             DEEP_TILE_PREFETCH=256
run "ua_v8 PF=256 (reference)"         ua_v8 ""             DEEP_TILE_PREFETCH=256
run "ua_v8 PF=384"                     ua_v8 ""             DEEP_TILE_PREFETCH=384
run "ua_v8 PF=512"                     ua_v8 ""             DEEP_TILE_PREFETCH=512
run "ua_v8 PF=256 split 524288"        ua_v8 "--split 524288"  DEEP_TILE_PREFETCH=256
run "ua_v8 PF=256 split 700000"        ua_v8 "--split 700000"  DEEP_TILE_PREFETCH=256
run "ua_v8 PF=256 split 1500000"       ua_v8 "--split 1500000" DEEP_TILE_PREFETCH=256
run "ua_v8 tile 18 PF=128"             ua_v8 "--tile 18"    DEEP_TILE_PREFETCH=128
run "ua_v8 tile 18 no PF"              ua_v8 "--tile 18"
run "ua_v8 TILE_PIPE AT=128 CH=4092"   ua_v8 ""             DEEP_TILE_PIPE=1
run "ua_v8 TILE_PIPE AT=64"            ua_v8 ""             DEEP_TILE_PIPE=1 DEEP_TILE_PIPE_AT=64
run "ua_v8 TILE_PIPE AT=192"           ua_v8 ""             DEEP_TILE_PIPE=1 DEEP_TILE_PIPE_AT=192
run "ua_v8 TILE_PIPE AT=128 CH=2040"   ua_v8 ""             DEEP_TILE_PIPE=1 DEEP_TILE_PIPE_CH=2040
run "ua_v8 PF=256 (reference again)"   ua_v8 ""             DEEP_TILE_PREFETCH=256
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo BUNDLE8-DONE >> $OUT
