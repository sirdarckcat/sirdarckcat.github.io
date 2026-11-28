#!/bin/bash
# The vector known case on this RTX card with production's own current settings (next_campaign_env and deep_env_v89: tree, DEEP_* options, kernel, fused rounds, --target):
# q170000_m89_t1_v0, one 2^19 window from k_lo, f = 0, near-misses >= 46,171: must give the same 23 (k, q) as the CPU brute force. Campaign paused ~40 s.
W=/content/kc_prod; rm -rf $W; mkdir -p $W/camp $W/vec; cd $W
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89 | sed -e 's/--klog [0-9]*//' -e 's/--slice [0-9]*//' -e 's/--pipeline-depth [0-9]*//' -e 's/--log-near-exp [0-9]*//')
python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$W/vec/vec_000000.json', 'w'))"
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
[ -n "$P" ] && kill -STOP $P
( export $E
  timeout 900 python3 /content/c3g/search_gpu5.py --campaign $W/camp --vector-dir $W/vec --vector-wait 3 --goldbach /content/c3g --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
    --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 46171 $DA \
    --klog 19 --slice 524288 --pipeline-depth 1 --log-near-exp 1 > $W/camp/driver.log 2>&1 )
[ -n "$P" ] && kill -CONT $P
python3 - <<'PY' > $W/result.txt 2>&1
import json, os
REF = [(2138520, 46327), (2179102, 53551), (2179987, 49741), (2189571, 46687), (2193647, 55381), (2222542, 56311), (2223210, 48259), (2249515, 47317),
       (2283416, 61441), (2288959, 57529), (2343716, 46441), (2431570, 51241), (2432966, 51607), (2438432, 48157), (2469450, 48799), (2470026, 59509),
       (2472121, 52009), (2516834, 51241), (2517629, 49171), (2518859, 48157), (2587266, 52579), (2599668, 48757), (2636003, 48817)]
f = "/content/kc_prod/camp/found.jsonl"
nm = sorted((int(x["k"]), int(x["g"])) for x in (json.loads(l[l.index("{"):]) for l in (open(f) if os.path.exists(f) else []) if l.strip()))
env = [e for e in open("/content/next_campaign_env").read().split() if e.startswith(("SIEVE200=", "DEEP_", "FERMAT28_DIR=", "K28_STEP="))]
print(f"known case with production's settings {env}: {len(nm)} near-misses, identical to the CPU brute force's 23: {nm == REF}")
print("KCPROD", "PASSED" if nm == REF else "FAILED")
PY
echo KCPROD-DONE >> $W/result.txt
