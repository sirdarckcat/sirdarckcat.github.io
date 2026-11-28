#!/bin/bash
# The second bundle of small sieve items (uarch a606d5b..f58ff97: GEN_SCAN2 / GEN_RESV_LATE / GEN_MINRED, TILE_PROBE) on this RTX PRO 6000, on top of production's stack (PACK HOIST FLUSH2 ORDER GEN_UNROLL=4 TILE_UNROLL=4 PF=256), every row a
# bench_split.py run under its own 120 s timeout (the pipelined tile kernel uses a named barrier: a hang must not stall the campaign). Tree /content/ua_v9 (ua_v3 + f58ff97's sieve200/cuda);
# the first row in production's /content/ua_v7. TILE_PROBE is timing only (its bits are wrong). Campaign paused, resumed whatever happens. ms a 2^24 window.
OUT=/content/bundle9.txt; : > $OUT
[ -d /content/ua_v9 ] || cp -a /content/ua_v3 /content/ua_v9
tar -xzf /content/ua9_cuda.tgz -C /content/ua_v9/goldbach/sieve200/cuda
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
run "ua_v7 (production tree) PF=256"   ua_v7 ""  DEEP_TILE_PREFETCH=256
run "ua_v9 PF=256 (reference)"         ua_v9 ""  DEEP_TILE_PREFETCH=256
run "ua_v9 + SCAN2"                    ua_v9 ""  DEEP_TILE_PREFETCH=256 DEEP_GEN_SCAN2=1
run "ua_v9 + RESV_LATE"                ua_v9 ""  DEEP_TILE_PREFETCH=256 DEEP_GEN_RESV_LATE=1
run "ua_v9 + MINRED"                   ua_v9 ""  DEEP_TILE_PREFETCH=256 DEEP_GEN_MINRED=1
run "ua_v9 + LEAN (all three)"         ua_v9 ""  DEEP_TILE_PREFETCH=256 DEEP_GEN_SCAN2=1 DEEP_GEN_RESV_LATE=1 DEEP_GEN_MINRED=1
run "ua_v9 + LEAN + TILE_PIPE AT=64"   ua_v9 ""  DEEP_TILE_PIPE=1 DEEP_TILE_PIPE_AT=64 DEEP_GEN_SCAN2=1 DEEP_GEN_RESV_LATE=1 DEEP_GEN_MINRED=1
run "ua_v9 TILE_PIPE AT=64 alone"      ua_v9 ""  DEEP_TILE_PIPE=1 DEEP_TILE_PIPE_AT=64
run "PROBE: tile table from L1"        ua_v9 ""  DEEP_TILE_PREFETCH=256 DEEP_TILE_PROBE=1
run "ua_v9 PF=256 (reference again)"   ua_v9 ""  DEEP_TILE_PREFETCH=256
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo BUNDLE9-DONE >> $OUT
