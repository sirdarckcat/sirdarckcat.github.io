#!/bin/bash
# Cross-batch sieve pipeline (uarch search_gpu5_xbatch.patch, overlap.Pipeline at d1c6797) against production, in CAMPAIGN mode (the pipeline
# exists only there): 6 Q = 170,000 vectors x k in [2^30 - 2 x 2^25, 2^30) = 12 slices = 6 batches of 2 windows.
#   p: production driver (--pool 2097152 --pool-threads 2)          f: patched driver, --pipeline 1 --flush-each-window 1 --pool-threads 1
#   g: patched driver, --pipeline 1 --flush-each-window 1 --pool-threads 2
#   p_nm / g_nm: p and g with --near-miss 100000 (a dozen near-misses to compare)
# Tree /content/ua_xb: the production uarch tree (/content/uaB, untouched) with the d1c6797 sources over it (same kernels). Fermat from /content/f28w
# (production). Batch ends are stamped every 20 ms from the stats file; GPU memory sampled every 0.5 s. Campaign paused (SIGSTOP), resumed at the end.
W=/content/plt; mkdir -p $W; cd $W; rm -rf p f g p_nm g_nm result.txt
T=/content/ua_xb; [ -d $T ] || cp -a /content/uaB $T; tar -xzf /content/ua_xb.tgz -C $T || { echo TAR-FAILED > result.txt; exit 1; }
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt/my_specs.json", "w"))
print(len(out), [v["name"] for v in out])
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
run() {   # name driver near-miss extra
  D=$W/$1; mkdir -p $D; cp $W/my_specs.json $D/
  timeout 400 env $E DEEP_STAGED=1 python3 /content/c3g/$2 --campaign $D --goldbach /content/c3g --batch 2 --pool 2097152 --skip-frac 0.97 --p-est 0.055 \
    --kmax 1073741824 --klo 1006632960 --desc --no-stop --kernel 28 --sieve200 $T/goldbach/sieve200 --sieve-threads 256 --k28-step fermat28_step_s1r.cuh --k28-asm 1 \
    --near-miss $3 --deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 $4 > $D/driver.log 2>&1 &
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
run p search_gpu5.py 157837 "--pool-threads 2"
run f search_gpu5_xb.py 157837 "--pipeline 1 --flush-each-window 1 --pool-threads 1"
run g search_gpu5_xb.py 157837 "--pipeline 1 --flush-each-window 1 --pool-threads 2"
run p_nm search_gpu5.py 100000 "--pool-threads 2"
run g_nm search_gpu5_xb.py 100000 "--pipeline 1 --flush-each-window 1 --pool-threads 2"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re, json
W = "/content/plt"
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
    L = [l.strip() for l in open(f) if l.strip()] if os.path.exists(f) else []
    out = []
    for l in L:
        try:
            r = json.loads(l[l.index("{"):]) if "{" in l else {}
        except Exception:
            r = {"raw": l[:120]}
        out.append((l.split()[0] if not l.startswith("{") else "", r.get("k"), r.get("g"), r.get("name")))
    return sorted(out, key=str)
def mem(d):
    f = f"{W}/{d}/mem.txt"
    v = [int(x) for x in open(f).read().split() if x.isdigit()] if os.path.exists(f) else []
    return max(v) if v else None
ref = lines("p")
for d in ("p", "f", "g", "p_nm", "g_nm"):
    t = stamps(d)
    b = [round(y - x, 3) for x, y in zip(t, t[1:])]
    steady = (t[-1] - t[1]) / (len(t) - 2) if len(t) > 2 else float("nan")
    st = [l.split(" batch ")[1].split(":")[0][-6:] for l in open(f"{W}/{d}/gpu3_stats.log")] if os.path.exists(f"{W}/{d}/gpu3_stats.log") else []
    v = lines(d)
    err = [l.strip()[:200] for l in open(f"{W}/{d}/driver.log") if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:4]
    print(f"{d:5s}: {len(t)} batch ends, gaps {b}, steady (batches 3..{len(t)}) {steady:.3f} s | driver figures {st} | slice lines vs p: {'IDENTICAL' if v and v == ref else 'DIFFERENT'} ({len(v)}) | peak GPU memory {mem(d)} MiB | {err}")
a, b = found("p_nm"), found("g_nm")
print(f"near-misses at 100,000: p_nm {len(a)}, g_nm {len(b)}, identical: {a == b}")
for x in a[:20]:
    print("  ", x)
print("PLT-DONE")
PY
