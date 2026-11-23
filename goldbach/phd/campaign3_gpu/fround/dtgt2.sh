#!/bin/bash
# --target 524288 on this RTX card, under the standing rule (the production A/B on gold-g4, 12:51:30-13:10Z: 0.8473 s a batch against 0.8585 s on the other two, x0.987):
# this card's own check first, campaign paused: the 24 test windows base / tgt / base_b / tgt_b (slice lines identical) and the vector known case with --target 524288
# (the same 23 (k, q) as the CPU brute force). Only then --target 524288 goes into /content/deep_env_v89 and the campaign restarts in place (which also picks up NEAR_MISS).
W=/content/dtgt2; mkdir -p $W; cd $W; rm -rf b* t* kc result.txt
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89 | sed 's/ --target [0-9]*//'); SKIPF=$(echo "$E" | tr ' ' '\n' | sed -n 's/^SKIPF=//p')
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
run() {   # name extra-args
  D=$W/$1; mkdir -p $D
  ( export $E
    timeout 400 python3 /content/c3g/search_gpu5.py --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 --skip-frac $SKIPF \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 158209 $DA $2 > $D/driver.log 2>&1 )
  echo "rc=$?" >> $D/driver.log
}
run base ""; run tgt "--target 524288"; run base_b ""; run tgt_b "--target 524288"
D=$W/kc; mkdir -p $D/camp $D/vec
python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$D/vec/vec_000000.json', 'w'))"
( export $E
  timeout 900 python3 /content/c3g/search_gpu5.py --campaign $D/camp --vector-dir $D/vec --vector-wait 3 --goldbach /content/c3g --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
    --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 46171 --log-near-exp 1 \
    --deep 1 --klog 19 --slice 524288 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 1 --deep-tile-threads 512 \
    --deep-gen-threads 512 --fused-rounds 1 --target 524288 > $D/camp/driver.log 2>&1 )
resume; trap - EXIT
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/dtgt2"
REF = [(2138520, 46327), (2179102, 53551), (2179987, 49741), (2189571, 46687), (2193647, 55381), (2222542, 56311), (2223210, 48259), (2249515, 47317),
       (2283416, 61441), (2288959, 57529), (2343716, 46441), (2431570, 51241), (2432966, 51607), (2438432, 48157), (2469450, 48799), (2470026, 59509),
       (2472121, 52009), (2516834, 51241), (2517629, 49171), (2518859, 48157), (2587266, 52579), (2599668, 48757), (2636003, 48817)]
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def sl(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
ref = sl("base"); ok = len(ref) == 24
for d in ("base", "tgt", "base_b", "tgt_b"):
    same = bool(sl(d)) and sl(d) == ref; ok = ok and same
    print(f"{d:6s}: slice lines vs base: {'IDENTICAL' if same else 'DIFFERENT'} ({len(sl(d))})")
nm = sorted((int(x["k"]), int(x["g"])) for x in (json.loads(l[l.index("{"):]) for l in (open(f"{W}/kc/camp/found.jsonl") if os.path.exists(f"{W}/kc/camp/found.jsonl") else []) if l.strip()))
print(f"known case with --target 524288: {len(nm)} near-misses, identical to the CPU brute force's 23: {nm == REF}")
print("DTGT2-GATE", "PASSED" if ok and nm == REF else "FAILED")
PY
if grep -q "DTGT2-GATE PASSED" result.txt; then
  a=$(cat /content/deep_env_v89); case "$a" in *--target*) ;; *) echo "$a --target 524288" > /content/deep_env_v89;; esac
  echo "deployed --target 524288" >> result.txt
else
  echo "not deployed (gate failed); restarting unchanged for NEAR_MISS" >> result.txt
fi
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f "search_gpu[345][.]py --campaign /content/c170v "
for i in $(seq 1 60); do pgrep -f "search_gpu[345][.]py --campaign /content/c170v " > /dev/null || break; sleep 1; done
setsid nohup bash -c 'env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" bash /content/run_v5_vec.sh /content/c170v /content/vec89' > /dev/null 2>&1 < /dev/null &
sleep 8; echo "$(date -u +%FT%TZ) restarted | procs $(pgrep -fc 'search_gpu5[.]py --campaign /content/c170v ') | $(grep -o 'NEAR_MISS=[0-9]*' /content/next_campaign_env) | $(cat /content/deep_env_v89)" >> result.txt
echo DTGT2-DONE >> result.txt
