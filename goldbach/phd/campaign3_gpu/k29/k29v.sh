#!/bin/bash
# 29-bit kernel identity check in vector mode on this RTX PRO 6000 (lead's standing rule: identical tested members / first-PRP rows, identity against production
# on the same windows, the known case). 24 test vectors, one 2^24 window each, the production vector config (r32: no bubble, rg 32):
#   v0 / v0b: production driver, /content/f28w, fermat28_step_s1r.cuh     k29: the patched driver (search_gpu5_k29.py), /content/f29, fermat29_step_s1.cuh
#   kc29: the known case with the 29-bit kernel (q170000_m89_t1_v0, one 2^19 window from k_lo, --skip-frac 0, --near-miss 46171): must find the same 23 members
# Campaign paused (SIGSTOP) and resumed at the end, whatever happens.
W=/content/k29v; mkdir -p $W; cd $W; rm -rf v0 k29 v0b kc29 result.txt
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
DA="--deep 1 --klog 24 --slice 16777216 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 4 --trace-pipeline 1 --deep-tile-threads 512 --log-near-exp 1 --deep-rg 32"
run() {   # name driver fermat-dir step asm extra-args
  D=$W/$1; mkdir -p $D
  timeout 400 env $E GBATCH_GROUP_DELAY_US=0 FERMAT28_DIR=$3 python3 /content/c3g/$2 --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 \
    --skip-frac 0.97 --p-est 0.055 --no-stop --kernel 28 --sieve200 /content/ua_v3/goldbach/sieve200 --sieve-threads 256 --k28-step $4 --k28-asm $5 \
    --near-miss 157837 $DA $6 > $D/driver.log 2>&1 &
  PID=$!
  last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
run v0 search_gpu5.py /content/f28w fermat28_step_s1r.cuh 1 ""
run k29 search_gpu5_k29.py /content/f29 fermat29_step_s1.cuh 1 ""
run v0b search_gpu5.py /content/f28w fermat28_step_s1r.cuh 1 ""
D=$W/kc29; mkdir -p $D/camp $D/vec
python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$D/vec/vec_000000.json', 'w'))"
timeout 900 env $E FERMAT28_DIR=/content/f29 python3 /content/c3g/search_gpu5_k29.py --campaign $D/camp --vector-dir $D/vec --vector-wait 3 --goldbach /content/c3g --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
    --no-stop --kernel 28 --sieve200 /content/ua_v3/goldbach/sieve200 --sieve-threads 256 --k28-step fermat29_step_s1.cuh --k28-asm 1 --near-miss 46171 --log-near-exp 1 \
    --deep 1 --klog 19 --slice 524288 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 1 --deep-tile-threads 512 > $D/camp/driver.log 2>&1
echo "rc=$?" >> $D/camp/driver.log
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/k29v"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stamps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    return [t for n, t in v if n >= 1]
ref = lines("v0")
for d in ("v0", "k29", "v0b"):
    t = stamps(d); g = [round(y - x, 3) for x, y in zip(t, t[1:])]
    beside = sum(g[:-1]) / len(g[:-1]) if len(g) > 1 else float("nan")
    v = lines(d)
    L = open(f"{W}/{d}/driver.log").read().splitlines() if os.path.exists(f"{W}/{d}/driver.log") else []
    err = [l.strip()[:160] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l or "outside" in l][:3]
    print(f"{d:4s}: gaps {g} | mean of batches 2..5 {beside:.3f} s | slice lines vs v0: {'IDENTICAL' if v and v == ref else 'DIFFERENT'} ({len(v)}) | {err}")
K = f"{W}/kc29/camp"
L = open(f"{K}/driver.log").read().splitlines() if os.path.exists(f"{K}/driver.log") else []
print("kc29 driver:", [l.strip()[:200] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:4])
nm = []
for l in (open(f"{K}/found.jsonl") if os.path.exists(f"{K}/found.jsonl") else []):
    l = l.strip()
    if l:
        r = json.loads(l[l.index("{"):]); nm.append((int(r["k"]), int(r["g"])))
print(f"kc29 near-misses (first PRP row >= 46171): {len(nm)}")
for k, g in sorted(nm):
    print(f"K29 k={k} q={g}")
print("K29V-DONE")
PY
