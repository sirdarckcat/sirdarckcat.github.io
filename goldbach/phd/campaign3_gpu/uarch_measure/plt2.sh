#!/bin/bash
# Cross-batch sieve pipeline v2 (uarch a752ea3: search_gpu5_xbatch2.patch, overlap.Pipeline depth + counters, sync-free sieve windows) against production,
# campaign mode: 6 Q = 170,000 vectors x k in [2^30 - 2 x 2^25, 2^30) = 12 slices = 6 batches of 2 windows.
#   p:  production driver, production tree /content/uaB                p2: production driver, new tree (sync-free sieve, no pipeline)
#   h:  patched driver, new tree, --pipeline 1 --pipeline-depth 2 --trace-pipeline 1 --pool-threads 2 (pool 2097152, one flush a batch)
#   i:  h with --pool-threads 1                                         j:  h with GBATCH_DEFER_CHECK=0 (the per-group check)
#   p2_nm / h_nm: p2 / h with a near-miss threshold at the 536th residual row of the first vector (a few dozen near-misses to compare)
# New tree /content/ua_v2: /content/uaB (untouched) with the a752ea3 sources over it. Fermat from /content/f28w (production). Batch ends stamped every
# 20 ms; GPU memory sampled every 0.5 s. Campaign paused (SIGSTOP) and resumed at the end, whatever happens.
W=/content/plt2; mkdir -p $W; cd $W; rm -rf p p2 h i j p2_nm h_nm result.txt
T=/content/ua_v2; [ -d $T ] || cp -a /content/uaB $T; tar -xzf /content/ua_v2.tgz -C $T || { echo TAR-FAILED > result.txt; exit 1; }
NMT=$(python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt2/my_specs.json", "w"))
r = out[0]["residual"]; r = json.loads(r) if isinstance(r, str) else r
print(int(sorted(r)[535]))
PY
)
echo "near-miss threshold for the _nm runs: $NMT" > status.txt
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" >> status.txt
run() {   # name driver tree near-miss extra-env extra-args
  D=$W/$1; mkdir -p $D; cp $W/my_specs.json $D/
  timeout 400 env $E DEEP_STAGED=1 $5 python3 /content/c3g/$2 --campaign $D --goldbach /content/c3g --batch 2 --pool 2097152 --skip-frac 0.97 --p-est 0.055 \
    --kmax 1073741824 --klo 1006632960 --desc --no-stop --kernel 28 --sieve200 $3/goldbach/sieve200 --sieve-threads 256 --k28-step fermat28_step_s1r.cuh --k28-asm 1 \
    --near-miss $4 --deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 $6 > $D/driver.log 2>&1 &
  PID=$!
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 500 > $D/mem.txt 2>/dev/null &
  MP=$!
  last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
  kill $MP 2>/dev/null
}
PL="--pipeline 1 --pipeline-depth 2 --trace-pipeline 1"
run p search_gpu5.py /content/uaB 157837 "" "--pool-threads 2"
run p2 search_gpu5.py $T 157837 "" "--pool-threads 2"
run h search_gpu5_xb2.py $T 157837 "" "$PL --pool-threads 2"
run i search_gpu5_xb2.py $T 157837 "" "$PL --pool-threads 1"
run j search_gpu5_xb2.py $T 157837 "GBATCH_DEFER_CHECK=0" "$PL --pool-threads 2"
run p2_nm search_gpu5.py $T $NMT "" "--pool-threads 2"
run h_nm search_gpu5_xb2.py $T $NMT "" "$PL --pool-threads 2"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re, json
W = "/content/plt2"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stamps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    return [t for n, t in v if n >= 1]
def found(d):
    f = f"{W}/{d}/found.jsonl"
    out = []
    for l in (open(f) if os.path.exists(f) else []):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l[l.index("{"):])
        except Exception:
            r = {"raw": l[:100]}
        out.append((l.split()[0] if not l.startswith("{") else "", r.get("name"), r.get("k"), r.get("g")))
    return sorted(out, key=str)
def mem(d):
    f = f"{W}/{d}/mem.txt"
    v = [int(x) for x in open(f).read().split() if x.isdigit()] if os.path.exists(f) else []
    return max(v) if v else None
ref = lines("p")
for d in ("p", "p2", "h", "i", "j", "p2_nm", "h_nm"):
    t = stamps(d)
    b = [round(y - x, 3) for x, y in zip(t, t[1:])]
    steady = (t[-1] - t[1]) / (len(t) - 2) if len(t) > 2 else float("nan")
    v = lines(d)
    L = open(f"{W}/{d}/driver.log").read().splitlines() if os.path.exists(f"{W}/{d}/driver.log") else []
    err = [l.strip()[:200] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:4]
    tr = [l for l in L if l.startswith("[pipeline]")]
    print(f"{d:6s}: {len(t)} batch ends, gaps {b}, steady (batches 3..{len(t)}) {steady:.3f} s | slice lines vs p: {'IDENTICAL' if v and v == ref else 'DIFFERENT'} ({len(v)}) | peak GPU memory {mem(d)} MiB | {err}")
    for l in tr:
        m = re.search(r"waited ([\d.]+) s for the sieve; the sieve thread made (\d+) windows in ([\d.]+) s and waited ([\d.]+) s", l)
        if m:
            print(f"         [pipeline] consumer waited {m.group(1)} s; sieve thread {m.group(2)} windows in {m.group(3)} s busy, {m.group(4)} s idle")
a, b = found("p2_nm"), found("h_nm")
print(f"near-misses: p2_nm {len(a)}, h_nm {len(b)}, identical: {a == b}")
for x in a[:12]:
    print("  ", x)
print("PLT2-DONE")
PY
