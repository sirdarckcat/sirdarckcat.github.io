#!/bin/bash
# The RTX cards' sieve options and uarch's one-pass generate kernel (f1b904a, with fc12768's host-side slot check in gbig.py) on this L4: bench_split.py rows, ms a 2^25 window (--ks 25) of the first m88f vector of
# /content/m88f_top2.json, each under its own 300 s timeout. Tree /content/ua_v10 = this card's uaB + f1b904a's sieve200/cuda (bench_split is not in uaB; the first row is the L4's
# production parameters without options: --rg 16, gen 256, tile 256, rcta 2). One-pass slots sized as uarch advised: ~3/4 of stage 8192 marks over rcta x 64 tiles bins a CTA
# (rcta 8: ~12 a bin, 20 slots; rcta 4: ~24, 40 slots; rcta 2: ~48, 75 slots). The campaign is STOPPED (one campaign's memory on this card) and restarted unchanged at the end.
W=/content/opl4; mkdir -p $W; OUT=$W/bench.txt; : > $OUT
[ -d /content/ua_v10 ] || cp -a /content/uaB /content/ua_v10
tar -xzf /content/ua10_cuda.tgz -C /content/ua_v10/goldbach/sieve200/cuda
C=$(cat /content/next_campaign_dir | awk '{print $1}')
python3 -c "import json; s=json.load(open('/content/m88f_top2.json')); json.dump(s[:1], open('$W/spec1.json', 'w')); print(s[0]['name'])" >> $OUT
STARTED=0
start_campaign() {
  [ $STARTED = 1 ] && return; STARTED=1
  setsid nohup bash -c 'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" bash /content/run_v5_campQ.sh '"$C" > /dev/null 2>&1 < /dev/null &
  echo "$(date -u +%FT%TZ) campaign restarted in $C (unchanged)" >> $OUT
}
trap start_campaign EXIT
echo "$(date -u +%FT%TZ) stopping the campaign in $C" >> $OUT
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f "search_gpu[345][.]py --campaign $C "
for i in $(seq 1 90); do pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null || break; sleep 1; done
pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null && { pkill -9 -f "search_gpu[345][.]py --campaign $C "; sleep 10; }
echo "$(date -u +%FT%TZ) stopped" >> $OUT
STACK="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256"
LEAN="DEEP_GEN_SCAN2=1 DEEP_GEN_RESV_LATE=1 DEEP_GEN_MINRED=1"
L4P="--ks 25 --rg 16 --gen-threads 256 --tile-threads 256 --rcta 2"
run() {   # label args env...
  local label=$1 args=$2; shift 2
  local out
  out=$(cd /content/ua_v10/goldbach/sieve200/cuda && env "$@" timeout 300 python3 bench_split.py $W/spec1.json $args 2>&1); local rc=$?
  local gen=$(echo "$out" | awk '/^  gen \(staged/ {print $NF}') genA=$(echo "$out" | awk '/pass A/ {print $NF}') genB=$(echo "$out" | awk '/pass B/ {print $NF}')
  local tile=$(echo "$out" | awk '/^  tile kernel/ {print $NF}')
  local sieve=$(echo "$out" | awk '/^whole window/ {for (i=1;i<=NF;i++) if ($i=="sieve") print $(i+1)}')
  printf "%-58s gen %7s (A %7s B %7s)  tile %7s  sieve %7s  rc %s\n" "$label" "$gen" "$genA" "$genB" "$tile" "$sieve" "$rc" >> $OUT
  echo "$out" | grep -q SPLIT-DONE || { echo "  (failed:)" >> $OUT; echo "$out" | tail -4 >> $OUT; }
}
run "L4 production params (rg 16, 256/256, rcta 2), no options" "$L4P"                                                   DEEP_STAGED=1
run "+ RTX option stack"                                         "$L4P"                                                   DEEP_STAGED=1 $STACK
run "+ stack, rg 32, gen 512, tile 512, rcta 8"                  "--ks 25 --rg 32 --gen-threads 512 --tile-threads 512 --rcta 8" DEEP_STAGED=1 $STACK
run "+ stack, rg 16, gen 512, tile 512, rcta 8"                  "--ks 25 --rg 16 --gen-threads 512 --tile-threads 512 --rcta 8" DEEP_STAGED=1 $STACK
run "+ stack + LEAN, rg 32, 512/512, rcta 8"                     "--ks 25 --rg 32 --gen-threads 512 --tile-threads 512 --rcta 8" DEEP_STAGED=1 $STACK $LEAN
run "+ stack + ONEPASS 20 slots, rg 32, 512/512, rcta 8"         "--ks 25 --rg 32 --gen-threads 512 --tile-threads 512 --rcta 8" DEEP_STAGED=1 $STACK DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=20
run "+ stack + ONEPASS 40 slots, rg 32, 512/512, rcta 4"         "--ks 25 --rg 32 --gen-threads 512 --tile-threads 512 --rcta 4" DEEP_STAGED=1 $STACK DEEP_GEN_ONEPASS=1
run "+ stack + ONEPASS 40 slots, rg 16, 512/512, rcta 4"         "--ks 25 --rg 16 --gen-threads 512 --tile-threads 512 --rcta 4" DEEP_STAGED=1 $STACK DEEP_GEN_ONEPASS=1
run "+ stack + ONEPASS 75 slots, rg 32, 512/512, rcta 2"         "--ks 25 --rg 32 --gen-threads 512 --tile-threads 512 --rcta 2" DEEP_STAGED=1 $STACK DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=75
run "+ stack + ONEPASS 75 slots, L4 params (rg 16, 256/256, rcta 2)" "$L4P"                                                 DEEP_STAGED=1 $STACK DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=75
run "L4 production params again"                                 "$L4P"                                                   DEEP_STAGED=1
start_campaign; trap - EXIT
echo OPL4B-DONE >> $OUT
