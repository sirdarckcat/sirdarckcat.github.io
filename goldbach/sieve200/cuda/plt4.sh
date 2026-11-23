#!/bin/bash
# plt4.sh: the combinations of plt3's two best settings (uarch session, 23 Nov 2026 ~09:20Z).  plt3 result (RTX PRO 6000, 6 batches, slice lines identical, mean of the batches with a sieve beside them):
# j0 1.571 s, j1 1.568; d1 (GBATCH_GROUP_DELAY_US=1000) 1.548 (the sieve busy 1.35-1.48 s of the batch, idle 0.05-0.16: nearly sieve-bound), d2 (2500) 1.629 (the sieve falls behind); tt512 (--deep-tile-threads 512)
# 1.553 (busy 0.83-1.10); s2 1.575, s4 1.580, r4 1.646, r8 1.565, tt128 1.639, dm6 1.581; the sieve in the registers the Fermat CTAs leave (fA 1.969, fB 1.736, fC 1.784) is sieve-bound: 128-thread CTAs are too slow.
# Here: a delay AND 512-thread tile CTAs (the faster sieve can afford a longer bubble), a delay with 1024 threads, with 8-row groups, and the baseline twice; same harness as plt3.sh (same prerequisites:
# /content/ua_v3 and /content/c3g/search_gpu5_xb3.py; nothing new to build).  Output /content/plt4/result.txt.
# DIAGNOSTIC (pb, pj): the Fermat rounds lose ~0.25 s a batch beside the sieve however gently the sieve runs (j0 0.26 s for 0.434 s of sieve work; d1 0.24 s although the sieve then takes 1.4 s: the loss follows the
# sieve's WORK, not its intensity), twice what the probe's single big Fermat launch lost (0.12 s).  Two candidates: the Fermat KERNELS run slower beside sieve CTAs (GPU sharing: the sum of their event times
# grows), or the host side of the Fermat rounds gets slower (GIL / CPU contention with the sieve thread: the kernels stay at 1.27 s and the GAP between them grows).  pb / pj = base / j0 with --profile-pool
# (per flush: Fermat kernels X s on the GPU, run_pool wall Y s, gap Z s); pj also keeps a `top -H` snapshot 9 s into the run (a thread a line: a Python thread at 100% = CPU-bound), and nproc is saved.
W=/content/plt4; mkdir -p $W; cd $W; rm -rf base j0 a1 a2 a3 a4 a5 a6 pb pj j1 result.txt
T=/content/ua_v3; [ -d $T ] || { echo NO-TREE > result.txt; exit 1; }
nproc > nproc.txt; grep -m1 "model name" /proc/cpuinfo >> nproc.txt; free -g | head -2 >> nproc.txt
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt4/my_specs.json", "w"))
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
  case $1 in pj) (sleep 9; top -H -b -n 1 -w 200 2>/dev/null | head -30 > $D/top.txt) & ;; esac
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
X=search_gpu5_xb3.py
FIT="--deep-tile-threads 128 --deep-gen-threads 128"
run base  search_gpu5.py $T "" "--pool-threads 2"                    # production without the pipeline (reference for the slice lines)
run j0    $X $T "" "$PL"
run a1    $X $T "GBATCH_GROUP_DELAY_US=1000" "$PL --deep-tile-threads 512"
run a2    $X $T "GBATCH_GROUP_DELAY_US=500" "$PL --deep-tile-threads 512"
run a3    $X $T "GBATCH_GROUP_DELAY_US=1500" "$PL --deep-tile-threads 512"
run a4    $X $T "GBATCH_GROUP_DELAY_US=1000" "$PL --deep-tile-threads 1024"
run a5    $X $T "GBATCH_GROUP_DELAY_US=1000" "$PL --deep-tile-threads 512 --deep-rg 8"
run a6    $X $T "" "$PL --deep-tile-threads 512"                   # tt512 again (noise)
run pb    search_gpu5.py $T "" "--pool-threads 2 --profile-pool"   # production without the pipeline, with the pool profile (kernel time / gap per flush)
run pj    $X $T "" "$PL --profile-pool"                            # the pipeline, with the pool profile and a top -H snapshot
run j1    $X $T "" "$PL"                                           # the baseline again (noise)
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/plt4"
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
for d in ("base", "j0", "a1", "a2", "a3", "a4", "a5", "a6", "pb", "pj", "j1"):
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
for d in ("pb", "pj"):
    f = f"{W}/{d}/driver.log"
    L = [l for l in open(f).read().splitlines() if l.startswith("[profile-pool]")] if os.path.exists(f) else []
    print(f"--- {d}: the last {min(len(L), 12)} of {len(L)} [profile-pool] lines")
    for l in L[-12:]:
        print("   ", l[:260])
t = f"{W}/pj/top.txt"
print("--- top -H of pj (9 s in):")
print(open(t).read() if os.path.exists(t) else "(none)")
print("--- nproc / cpu / memory:")
print(open(f"{W}/nproc.txt").read() if os.path.exists(f"{W}/nproc.txt") else "(none)")
print("PLT4-DONE")
PY
