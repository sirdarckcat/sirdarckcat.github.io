#!/bin/bash
# plt9.sh (uarch session, 23 Nov 2026): the persistent Fermat kernel again, with the fix for the slowdown plt8 measured (p1 2.68 s, pn 2.81 s a batch against base 1.84 s: ~1 s SLOWER).
# The diagnosis (fermat28_persist_kernel.cuh, "WARP CONVERGENCE"): the kernel's step loop is the production loop (same SASS), but the ~7% of lanes whose member just ended fetch a new one (a global atomic and
# four dependent loads) while the other lanes branch past the fetch, and on Volta and later nothing made the two groups meet before the 660-step test: ptxas put its only convergence barrier at the END of
# the loop body.  The lanes that did not fetch start the next test alone, the fetching lanes arrive later at the same code, and the warp then issues every instruction of the step loop twice (once a group).
# The fix is __syncwarp() before each test (WARPSYNC in the SASS, FM28_PSYNC=1, the default; FERMAT_PERSIST_SYNC=0 compiles the first version).  This script tests it, in two steps:
#   1. bench_persist.py (kernel time only, ~2 min): the production kernel's tests/s on random sieved 661-bit rows, then the persistent kernel on a synthetic pool of 400,000 members, once without and once
#      with __syncwarp: ms, tests/s, the ratio to the production kernel, and a check of every result against the production kernel's flags.  Expect sync 0 ~0.5 x and sync 1 ~1.0 x if the diagnosis is right.
#   2. the driver (6 batches a run, the harness of plt3-8): base (reference for the slice lines), a2 (the deployed setting, control), pn1 (persist + tail, no pipeline, __syncwarp, with FERMAT_PERSIST_TRACE),
#      pn0 (the same without __syncwarp, traced: it must reproduce plt8's pn ~2.8 s), ps1 (persist + tail + the pipeline of a2, __syncwarp), a2b (control again).  The trace prints, per flush, the kernel's
#      own milliseconds, the tests it did, the members left in flight, and the wall of the round-based path that finishes them.
# Needs: /content/ua_v3 (as plt8); /content/f28p = /content/f28w + the uarch branch's goldbach/fermat661/cuda/gpu_fermat28.py, fermat28_persist_kernel.cuh and bench_persist.py (at the commit named in the message);
# /content/c3g/search_gpu5_xb5.py as for plt8 (the driver patch has not changed).  Output: /content/plt9/result.txt.
W=/content/plt9; mkdir -p $W; cd $W; rm -rf base a2 pn1 pn0 ps1 a2b result.txt bench.txt
T=/content/ua_v3; [ -d $T ] || { echo NO-TREE > result.txt; exit 1; }
[ -f /content/f28p/bench_persist.py ] || { echo NO-F28P > result.txt; exit 1; }
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt9/my_specs.json", "w"))
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
# 1. the kernel alone
( cd /content/f28p && timeout 600 python3 bench_persist.py --sync 0 1 ) > $W/bench.txt 2>&1
echo "$(date -u +%FT%TZ) bench_persist done (rc=$?)" >> status.txt
run() {   # name driver tree extra-env extra-args
  D=$W/$1; mkdir -p $D; cp $W/my_specs.json $D/
  timeout 400 env $E DEEP_STAGED=1 $4 python3 /content/c3g/$2 --campaign $D --goldbach /content/c3g --batch 2 --pool 2097152 --skip-frac 0.97 --p-est 0.055 \
    --kmax 1073741824 --klo 1006632960 --desc --no-stop --kernel 28 --sieve200 $3/goldbach/sieve200 --sieve-threads 256 --k28-step fermat28_step_s1r.cuh --k28-asm 1 \
    --near-miss 157837 --deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 $5 > $D/driver.log 2>&1 &
  PID=$!
  last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
X=search_gpu5_xb5.py
PF="FERMAT28_DIR=/content/f28p"
A2="GBATCH_GROUP_DELAY_US=500"
PL3="--pipeline 1 --pipeline-depth 2 --trace-pipeline 1"
TT="--deep-tile-threads 512"
TL="--tail-target 65536 --dtail 256"
run base $X $T "" "--pool-threads 2"
run a2   $X $T "$A2" "$PL3 --pool-threads 2 $TT"
run pn1  $X $T "$PF FERMAT_PERSIST_TRACE=1" "--pool-threads 2 --persist 1 $TL"
run pn0  $X $T "$PF FERMAT_PERSIST_TRACE=1 FERMAT_PERSIST_SYNC=0" "--pool-threads 2 --persist 1 $TL"
run ps1  $X $T "$A2 $PF" "$PL3 --pool-threads 2 $TT --persist 1 $TL"
run a2b  $X $T "$A2" "$PL3 --pool-threads 2 $TT"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/plt9"
print(open(f"{W}/status.txt").read())
print("--- bench_persist.py ---")
print(open(f"{W}/bench.txt").read())
print("--- driver runs ---")
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stamps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    return [t for n, t in v if n >= 1]
ref = lines("base")
for d in ("base", "a2", "pn1", "pn0", "ps1", "a2b"):
    t = stamps(d)
    g = [round(y - x, 3) for x, y in zip(t, t[1:])]
    beside = sum(g[:-1]) / len(g[:-1]) if len(g) > 1 else float("nan")
    v = lines(d)
    L = open(f"{W}/{d}/driver.log").read().splitlines() if os.path.exists(f"{W}/{d}/driver.log") else []
    err = [l.strip()[:160] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:3]
    print(f"{d:5s}: gaps {g} | mean of all but the last batch {beside:.3f} s | slice lines vs base: {'IDENTICAL' if v and v == ref else 'DIFFERENT'} ({len(v)}) | {err}")
    pl = [l for l in L if l.startswith("[persist]")]
    for l in pl[:6]:
        print("        " + l[:330])
    if len(pl) > 6:
        print(f"        ... {len(pl)} [persist] lines")
print("PLT9-DONE")
PY
