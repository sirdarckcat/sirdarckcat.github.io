#!/bin/bash
# --vector-place top (the lead's decision of 23 Nov 16:36Z; /content/c3g/search_gpu5_vtop.py = production + search_gpu5_vtop.patch) on this RTX PRO 6000, with production's
# settings (next_campaign_env, deep_env_v89). The campaign is paused (SIGSTOP) for the GPU runs and resumed whatever happens:
#   kc_bot: the vector known case (q170000_m89_t1_v0, 2^19 from k_lo, f = 0, near-misses >= 46,171), patched driver, default placement: the same 23 (k, q) as the CPU brute force;
#   kc_top: the same vector with --vector-place top: k in [kend - 2^19, kend), kend = 21,378,978 (one past its last 200-digit k): the list for cpu_brute_k0.py's;
#   n97 / n90: the normal path (B = 10^6, block 32768, p-est 0.055) with --vector-place top --klog 20 on a production vector (the first of the newest chunk), f = 0.97 / 0.9:
#              slice lines for search_c.py's (c97 / c90, after the resume) on the same k range;
#   base / bot / top, then base_b / bot_b / top_b: production's driver, the patched one (bottom) and the patched one (--vector-place top) on the 24 test vectors:
#              bot's slice lines == base's; batch times; expected near-misses >= 158,209 (--log-near-exp 1) at the top against the bottom.
# vtop_loader.py (conditions 1 and 4) runs on a snapshot of /content/vec89 with c170v's done set, in the background meanwhile.
W=/content/vtop; mkdir -p $W; cd $W; rm -rf kc_bot kc_top n97 n90 c97 c90 base bot top base_b bot_b top_b vsnap vn vplt loader.txt result.txt status.txt
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89); SKIPF=$(echo "$E" | tr ' ' '\n' | sed -n 's/^SKIPF=//p')
DK=$(echo "$DA" | sed -e 's/--klog [0-9]*//' -e 's/--slice [0-9]*//' -e 's/--pipeline-depth [0-9]*//' -e 's/--log-near-exp [0-9]*//')
G=/content/c3g; PROD=$G/search_gpu5.py; NEW=$G/search_gpu5_vtop.py
mkdir -p vsnap; for f in /content/vec89/vec_*.json; do ln -s $f vsnap/; done; cp /content/c170v/search.log vsnap_search.log
( nice -n 5 python3 /content/vtop_loader.py $PROD $NEW $W/vsnap $W/vsnap_search.log > $W/loader.txt 2>&1; echo LOADER-EXIT >> $W/loader.txt ) &
mkdir -p vplt vn; cp /content/vplt_vec_000000.json vplt/vec_000000.json
python3 - <<'PY'
import json, glob
f = sorted(glob.glob("/content/vec89/vec_*.json"))[-1]
s = json.load(open(f))[0]
json.dump([s], open("/content/vtop/vn/vec_000000.json", "w"))
from gmpy2 import mpz
N0, M = mpz(s["N0"]), mpz(s["M"]); kend = min(int(s["kmax"]), int((mpz(10) ** 200 - N0 + M - 1) // M)); ks = kend - (1 << 20)
json.dump([dict(s, name=f"{s['name']}@{ks}", kstart=ks, kmax=kend)], open("/content/vtop/slice_top.json", "w"))
print(f"normal-path vector {s['name']} (from {f}): top 2^20 = [{ks}, {kend})")
PY
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
kc() {   # name extra
  D=$W/$1; mkdir -p $D/camp $D/vec
  python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$D/vec/vec_000000.json', 'w'))"
  ( export $E
    timeout 900 python3 $NEW --campaign $D/camp --vector-dir $D/vec --vector-wait 3 --goldbach $G --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
      --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 46171 $DK \
      --klog 19 --slice 524288 --pipeline-depth 1 --log-near-exp 1 $2 > $D/camp/driver.log 2>&1 ); echo "rc=$?" >> $D/camp/driver.log
}
kc kc_bot ""
kc kc_top "--vector-place top"
echo "$(date -u +%FT%TZ) known cases done" >> status.txt
for f in 0.97 0.9; do
  D=$W/n${f#0.}; mkdir -p $D
  ( export $E
    timeout 600 python3 $NEW --campaign $D --vector-dir $W/vn --vector-wait 3 --vector-place top --klog 20 --goldbach $G --batch 1 --pool 2097152 --skip-frac $f --p-est 0.055 \
      --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --sieve-b 1000000 --block 32768 --fused-rounds 1 \
      > $D/driver.log 2>&1 ); echo "rc=$?" >> $D/driver.log
done
echo "$(date -u +%FT%TZ) normal path done" >> status.txt
run() {   # name driver extra
  D=$W/$1; mkdir -p $D
  ( export $E
    timeout 400 python3 $2 --campaign $D --vector-dir $W/vplt --vector-wait 3 --goldbach $G --batch 4 --pool 2097152 --skip-frac $SKIPF \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 158209 $DA $3 > $D/driver.log 2>&1 ) &
  PID=$!; last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
run base $PROD ""; run bot $NEW ""; run top $NEW "--vector-place top"; run base_b $PROD ""; run bot_b $NEW ""; run top_b $NEW "--vector-place top"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
CG=/content/c150cpu/goldbach
for f in 0.97 0.9; do
  D=$W/c${f#0.}; mkdir -p $D
  timeout 3000 nice -n 5 python3 $CG/sieve200/search_c.py $W/slice_top.json --procs 8 --block 32768 --sieve-b 1000000 --skip-frac $f --p-est 0.055 --out $D/found.jsonl > $D/out.txt 2>&1
  echo "rc=$?" >> $D/out.txt
done
echo "$(date -u +%FT%TZ) CPU slices done" >> status.txt
for i in $(seq 1 600); do grep -q LOADER-EXIT $W/loader.txt 2>/dev/null && break; sleep 2; done
python3 /content/vtop_result.py > result.txt 2>&1
