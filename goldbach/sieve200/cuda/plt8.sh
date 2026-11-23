#!/bin/bash
# plt8.sh (uarch session, 23 Nov 2026): the PERSISTENT Fermat kernel (goldbach/fermat661/cuda/fermat28_persist_kernel.cuh, gpu_fermat28.persist_pool, search_gpu5_persist.patch).
# Why: the round-based run_pool tests a pool in ~45 rounds of ~100 small cupy kernels and ~6 host syncs each, computes ~3% tests past a member's first PRP, and idles the GPU in the gaps (plt5: the flush
# is 1.34 s without a sieve beside it while the Fermat kernels take 1.27 s; beside the sieve the flush is 1.58 s: kernels x1.08 slower and ~0.14 s of gaps).  The persistent kernel is ONE launch a
# pool: every thread takes a member from a queue (one atomicAdd), tests its rows in order until the first PRP, takes the next; no waste, no gaps, no host work; the ~120k members in flight when the queue
# runs empty (~6% of the tests) are finished by the round-based code.  It also looks to the sieve like the probe's single big Fermat launch (the probe: Fermat x1.10, sieve x2.89, work rate x1.25, against
# x1.165 in the driver).  Per-member results are identical (tests counted, PRP, success, first-PRP row: test_fermat28_persist.py compares them with sequential Python pow on the CPU for 1-24 lanes).
# Runs (6 batches each, the harness of plt3-7; a2 = GBATCH_GROUP_DELAY_US=500, --deep-tile-threads 512, pipeline depth 2, --pool-threads 2 = the deployed setting):
#   base  production without the pipeline and without persist (reference for the slice lines)      a2   the deployed setting (control)
#   p1    a2 + --persist 1 (CTAs an SM from the kernel's registers: 5)       p1c4  a2 + --persist 1 --persist-cta-sm 4 (a CTA's room beside the Fermat CTAs for the sieve)
#   p1t1  a2 + --persist 1 --pool-threads 1 (the leftovers finished by one thread)
#   pn    --persist 1 WITHOUT the pipeline (the persistent kernel alone against base)             a2b  the control again
# Needs: /content/ua_v3 (4f8edff, as now); /content/f28p = a copy of /content/f28w (production's Fermat dir) with goldbach/fermat661/cuda/gpu_fermat28.py and fermat28_persist_kernel.cuh from the uarch
# branch over it (fermat28_kernel.cuh and the step files are unchanged); /content/c3g/search_gpu5_xb5.py = the deployed driver (/content/c3g/search_gpu5.py) + goldbach/fermat661/cuda/search_gpu5_persist.patch
# (patch -p1 from the repo root; dry-run verified).  Output: /content/plt8/result.txt.
W=/content/plt8; mkdir -p $W; cd $W; rm -rf base a2 p1 p1c4 p1t1 pn a2b result.txt
T=/content/ua_v3; [ -d $T ] || { echo NO-TREE > result.txt; exit 1; }
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt8/my_specs.json", "w"))
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
X=search_gpu5_xb5.py
FIT="--deep-tile-threads 128 --deep-gen-threads 128"
A2="GBATCH_GROUP_DELAY_US=500"
TT="--deep-tile-threads 512"
PL3="--pipeline 1 --pipeline-depth 2 --trace-pipeline 1"
PF="FERMAT28_DIR=/content/f28p"
run base  $X $T "" "--pool-threads 2"                                      # production without the pipeline and without persist (the reference for the slice lines)
run a2    $X $T "$A2" "$PL3 --pool-threads 2 $TT"
run p1    $X $T "$A2 $PF" "$PL3 --pool-threads 2 $TT --persist 1"
run p1c4  $X $T "$A2 $PF" "$PL3 --pool-threads 2 $TT --persist 1 --persist-cta-sm 4"
run p1t1  $X $T "$A2 $PF" "$PL3 --pool-threads 1 $TT --persist 1"
run pn    $X $T "$PF" "--pool-threads 2 --persist 1"                       # persist alone, no pipeline, no sieve shaping
run a2b   $X $T "$A2" "$PL3 --pool-threads 2 $TT"                          # the control again (noise)
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/plt8"
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
for d in ("base", "a2", "p1", "p1c4", "p1t1", "pn", "a2b"):
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
print("PLT8-DONE")
PY
