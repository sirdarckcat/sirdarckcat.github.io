#!/bin/bash
# plt7.sh (uarch session, 23 Nov 2026 ~09:35Z): more Fermat threads beside the sieve.  plt5 (GPU session) --profile-pool: beside the sieve a half-pool's Fermat KERNELS take 0.70-0.76 s on the GPU instead of
# 0.65-0.69 (x1.08, the probe's x1.10) but its run_pool WALL grows 1.33 -> 1.54 s: the rest of the 0.23 s a batch the Fermat side loses is GAPS, GPU time between the Fermat kernels of the two halves while the
# ~40 small kernels of a round (gathers, cumsum, searchsorted, scatter_min ...) queue behind sieve CTAs (the sieve stream has the higher priority).  The CPU share is not the cause (plt5).  With 3 or 4 parts
# (search_gpu5_poolsplitn.patch: --pool-threads 3 / 4) more Fermat kernels are in flight at any moment.  a2 = the deployed setting (GBATCH_GROUP_DELAY_US=500, --deep-tile-threads 512, pipeline depth 2,
# --pool-threads 2).  Runs: base (production without the pipeline, reference for the slice lines), a2 (control), a2p3 / a2p4 (3 / 4 parts), a2e (Fermat streams at the sieve's priority: FERMAT_STREAM_PRIORITY=high,
# which search_gpu5_prio.patch already provides; the small kernels no longer queue BEHIND the sieve's, but the sieve then has to share the SMs with the big Fermat kernels on equal terms), a2e3 (equal priority and
# 3 parts), a2' (control again).  Needs: /content/ua_v3 (4f8edff, as now) and /content/c3g/search_gpu5_xb4.py = the deployed driver (/content/c3g/search_gpu5.py, d5e5f14 + prio patch) with
# goldbach/sieve200/cuda/search_gpu5_poolsplitn.patch applied (patch -p1; dry-run verified).  Output: /content/plt7/result.txt.
W=/content/plt7; mkdir -p $W; cd $W; rm -rf base a2 a2p3 a2p4 a2e a2e3 a2b result.txt
T=/content/ua_v3; [ -d $T ] || { echo NO-TREE > result.txt; exit 1; }
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt7/my_specs.json", "w"))
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
run() {   # name driver tree extra-env extra-args
  D=$W/$1; mkdir -p $D; cp $W/my_specs.json $D/
  timeout 400 env $E DEEP_STAGED=1 $4 python3 /content/c3g/$2 --campaign $D --goldbach /content/c3g --batch 2 --pool 2097152 --skip-frac 0.97 --p-est 0.055 \
    --kmax 1073741824 --klo 1006632960 --desc --no-stop --kernel 28 --sieve200 $3/goldbach/sieve200 --sieve-threads 256 --k28-step fermat28_step_s1r.cuh --k28-asm 1 \
    --near-miss 157837 --deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 $5 > $D/driver.log 2>&1 &
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
PL="--pipeline 1 --pipeline-depth 2 --trace-pipeline 1 --pool-threads 2"
X=search_gpu5_xb4.py
FIT="--deep-tile-threads 128 --deep-gen-threads 128"
A2="GBATCH_GROUP_DELAY_US=500"
TT="--deep-tile-threads 512"
PL3="--pipeline 1 --pipeline-depth 2 --trace-pipeline 1"
run base  search_gpu5.py $T "" "--pool-threads 2"                    # production without the pipeline (reference for the slice lines)
run a2    $X $T "$A2" "$PL3 --pool-threads 2 $TT"
run a2p3  $X $T "$A2" "$PL3 --pool-threads 3 $TT"
run a2p4  $X $T "$A2" "$PL3 --pool-threads 4 $TT"
run a2e   $X $T "$A2 FERMAT_STREAM_PRIORITY=high" "$PL3 --pool-threads 2 $TT"
run a2e3  $X $T "$A2 FERMAT_STREAM_PRIORITY=high" "$PL3 --pool-threads 3 $TT"
run a2b   $X $T "$A2" "$PL3 --pool-threads 2 $TT"                   # the control again (noise)
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/plt7"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stamps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    return [t for n, t in v if n >= 1]
def mem(d):
    f = f"{W}/{d}/mem.txt"
    v = [int(x) for x in open(f).read().split() if x.isdigit()] if os.path.exists(f) else []
    return max(v) if v else None
ref = lines("base")
for d in ("base", "a2", "a2p3", "a2p4", "a2e", "a2e3", "a2b"):
    t = stamps(d)
    g = [round(y - x, 3) for x, y in zip(t, t[1:])]
    beside = sum(g[:-1]) / len(g[:-1]) if len(g) > 1 else float("nan")
    v = lines(d)
    L = open(f"{W}/{d}/driver.log").read().splitlines() if os.path.exists(f"{W}/{d}/driver.log") else []
    err = [l.strip()[:160] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:3]
    print(f"{d:6s}: gaps {g} | batches with a sieve beside them: mean {beside:.3f} s | slice lines vs base: {'IDENTICAL' if v and v == ref else 'DIFFERENT'} ({len(v)}) | peak GPU memory {mem(d)} MiB | {err}")
    for l in L:
        m = re.search(r"\[pipeline\] batch \S+: the consumer waited ([\d.]+) s for the sieve; the sieve thread made (\d+) windows in ([\d.]+) s and waited ([\d.]+) s", l)
        if m and m.group(2) != "0" and float(m.group(1)) < 1.0:
            print(f"         [pipeline] waited {m.group(1)} s; sieve {m.group(2)} windows busy {m.group(3)} s, idle {m.group(4)} s")
print("PLT7-DONE")
PY
