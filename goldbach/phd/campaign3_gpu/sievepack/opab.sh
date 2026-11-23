#!/bin/bash
# uarch's one-pass generate kernel (f1b904a: DEEP_GEN_ONEPASS=1, opt-in; the preprocessed kernel is byte-identical with it unset) on this RTX PRO 6000, bench_split.py rows (ms a
# 2^24 window of /content/m89_8.json), each under its own 120 s timeout. Tree /content/ua_v10 = ua_v3 + f1b904a's sieve200/cuda. First and last rows: this card's production tree and
# options (ua_v7 / SIEVE200 from next_campaign_env, its DEEP_* options). Campaign paused (SIGSTOP), resumed whatever happens.
OUT=/content/opab.txt; : > $OUT
[ -d /content/ua_v10 ] || cp -a /content/ua_v3 /content/ua_v10
tar -xzf /content/ua10_cuda.tgz -C /content/ua_v10/goldbach/sieve200/cuda
E=$(cat /content/next_campaign_env)
PT=$(echo "$E" | tr ' ' '\n' | sed -n 's#^SIEVE200=/content/\([^/]*\)/.*#\1#p')
PO=$(echo "$E" | tr ' ' '\n' | grep '^DEEP_' | grep -v '^DEEP_RCTA=\|^DEEP_STAGED=' | tr '\n' ' ')
LEAN="DEEP_GEN_SCAN2=1 DEEP_GEN_RESV_LATE=1 DEEP_GEN_MINRED=1"
echo "production tree $PT | options $PO" >> $OUT
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> $OUT
COMMON="--rg 32 --rcta 8 --gen-threads 512 --tile-threads 512"
run() {   # label tree extra-args env...
  local label=$1 tree=$2 args=$3; shift 3
  local out
  out=$(cd /content/$tree/goldbach/sieve200/cuda && env -u DEEP_GEN_ONEPASS $PO "$@" timeout 120 python3 bench_split.py /content/m89_8.json $COMMON $args 2>&1); local rc=$?
  local gen=$(echo "$out" | awk '/^  gen \(staged/ {print $NF}') genA=$(echo "$out" | awk '/pass A/ {print $NF}') genB=$(echo "$out" | awk '/pass B/ {print $NF}')
  local tile=$(echo "$out" | awk '/^  tile kernel/ {print $NF}')
  local sieve=$(echo "$out" | awk '/^whole window/ {for (i=1;i<=NF;i++) if ($i=="sieve") print $(i+1)}')
  printf "%-50s gen %7s (A %6s B %6s)  tile %7s  sieve %6s  rc %s\n" "$label" "$gen" "$genA" "$genB" "$tile" "$sieve" "$rc" >> $OUT
  echo "$out" | grep -q SPLIT-DONE || { echo "  (failed:)" >> $OUT; echo "$out" | tail -3 >> $OUT; }
}
run "production ($PT, its options)"                $PT    ""
run "ua_v10, the same options (flag unset)"        ua_v10 ""
run "ONEPASS 40 slots"                             ua_v10 ""                  DEEP_GEN_ONEPASS=1
run "ONEPASS 40 slots, bounds 512,3"               ua_v10 ""                  DEEP_GEN_ONEPASS=1 DEEP_GEN_LB=512,3
run "ONEPASS 40 slots, unroll 8"                   ua_v10 ""                  DEEP_GEN_ONEPASS=1 DEEP_GEN_UNROLL=8
run "ONEPASS 30 slots, stage 6144"                 ua_v10 "--stage-cap 6144"  DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=30
run "ONEPASS 25 slots, stage 4096, bounds 512,3"   ua_v10 "--stage-cap 4096"  DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=25 DEEP_GEN_LB=512,3
run "ONEPASS 40 slots + LEAN"                      ua_v10 ""                  DEEP_GEN_ONEPASS=1 $LEAN
run "LEAN alone (ua_v10)"                          ua_v10 ""                  $LEAN
run "production again"                             $PT    ""
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> $OUT
echo OPAB-DONE >> $OUT
