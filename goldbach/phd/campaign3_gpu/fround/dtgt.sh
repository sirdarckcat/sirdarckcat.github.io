#!/bin/bash
# --target 524288 (most tests in one Fermat launch, half the default) on this RTX card for a production A/B against the other two (tune2.sh: x0.986 a batch, 3.1% waste
# against 5.7%, slice lines identical in both passes). First the vector known case with it (campaign paused ~40 s): the same 23 (k, q) as the CPU brute force; only then
# --target 524288 goes into /content/deep_env_v89 and the campaign restarts in place.
W=/content/dtgt; mkdir -p $W/camp $W/vec; cd $W; rm -rf camp/* result.txt
E=$(cat /content/next_campaign_env)
python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$W/vec/vec_000000.json', 'w'))"
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
[ -n "$P" ] && kill -STOP $P
( export $E
  timeout 900 python3 /content/c3g/search_gpu5.py --campaign $W/camp --vector-dir $W/vec --vector-wait 3 --goldbach /content/c3g --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
    --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 46171 --log-near-exp 1 \
    --deep 1 --klog 19 --slice 524288 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 1 --deep-tile-threads 512 \
    --deep-gen-threads 512 --fused-rounds 1 --target 524288 > $W/camp/driver.log 2>&1 )
[ -n "$P" ] && kill -CONT $P
python3 - <<'PY' > result.txt 2>&1
import json
REF = [(2138520, 46327), (2179102, 53551), (2179987, 49741), (2189571, 46687), (2193647, 55381), (2222542, 56311), (2223210, 48259), (2249515, 47317),
       (2283416, 61441), (2288959, 57529), (2343716, 46441), (2431570, 51241), (2432966, 51607), (2438432, 48157), (2469450, 48799), (2470026, 59509),
       (2472121, 52009), (2516834, 51241), (2517629, 49171), (2518859, 48157), (2587266, 52579), (2599668, 48757), (2636003, 48817)]
nm = sorted((int(x["k"]), int(x["g"])) for x in (json.loads(l[l.index("{"):]) for l in open("/content/dtgt/camp/found.jsonl") if l.strip()))
print(f"known case with --target 524288: {len(nm)} near-misses, identical to the CPU brute force's 23: {nm == REF}")
print("DTGT-KC", "PASSED" if nm == REF else "FAILED")
PY
if grep -q "DTGT-KC PASSED" result.txt; then
  a=$(cat /content/deep_env_v89); case "$a" in *--target*) ;; *) echo "$a --target 524288" > /content/deep_env_v89;; esac
  pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f "search_gpu[345][.]py --campaign /content/c170v "
  for i in $(seq 1 60); do pgrep -f "search_gpu[345][.]py --campaign /content/c170v " > /dev/null || break; sleep 1; done
  setsid nohup bash -c 'env $(cat /content/next_campaign_env) BATCH=4 DEEP_ARGS="$(cat /content/deep_env_v89)" bash /content/run_v5_vec.sh /content/c170v /content/vec89' > /dev/null 2>&1 < /dev/null &
  sleep 8; echo "$(date -u +%FT%TZ) deployed --target 524288 | procs $(pgrep -fc 'search_gpu5[.]py --campaign /content/c170v ') | $(cat /content/deep_env_v89)" >> result.txt
else
  echo "not deployed" >> result.txt
fi
echo DTGT-DONE >> result.txt
