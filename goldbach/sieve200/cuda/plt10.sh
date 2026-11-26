#!/bin/bash
# plt10.sh (uarch session, 23 Nov 2026): the persistent Fermat kernel BESIDE the sieve.  plt9 (GPU session, 10:46Z): the kernel is right and as fast as production (23.4M tests/s = 0.98 x, sync 0 or 1; plt8's
# 2.8 s was the first version's control flow: `continue` / `break` inside the fetch block left the compiler no reconvergence point before the test, the restructured kernel has a BSSY / BSYNC around the
# fetch: SASS of FM28_PSYNC=0 checked); without the pipeline it beats base (pn1 1.782 s against 1.844 s, -3.4%); but with the a2 pipeline (ps1) it is 1.667 s against a2's 1.537 s, +8.5%.
# Why (reading, not measured): 940 persistent CTAs (5 an SM x 128 threads x 96 registers = 61,440 of 65,536 registers) never retire, so a sieve CTA (512 threads x 40 registers = 20,480, 64 KB of shared memory)
# has no room beside them until the kernel ends: the sieve cannot overlap at all (the round-based kernels free a slot every ~5 ms, which is what the a2 / pipeline setting lives on).  Also the persistent kernel was
# launched without FERMAT_CARVEOUT (production's kernel() applies it; persist_kernel() now does too), so even with free registers the SM's shared-memory configuration may have refused the sieve's 64 KB CTAs.
# This script gives the sieve room: the persistent kernel with 4 / 3 / 2 CTAs an SM (the step loop's throughput is flat from 2 warps a scheduler, i.e. 2 CTAs an SM: bench_persist.py --cta-sm checks it first),
# with the carve-out hints, in the a2 setting and with the sieve flat out (no per-group check, no bubble: GBATCH_SYNC_EVERY=0 GBATCH_GROUP_DELAY_US=0, which starved the round-based Fermat kernels but cannot starve
# a persistent kernel that holds its slots).  The probe (one big Fermat launch beside the sieve) measured a work rate of x1.25 against the driver's x1.20 (a2 here: 1.844 / 1.537), so ~+4% is the room.
#   1. bench_persist.py --sync 1 --cta-sm 5 / 3 / 2: kernel tests/s alone at each residency (needs: a flat line).
#   2. driver runs (6 batches each): base (slice-line reference), a2 (control), ps3 (persistent, 3 CTAs an SM + tail rule + a2 sieve + carve-outs), ps3f (ps3 with the sieve flat out), ps2 (2 CTAs an SM),
#      ps4t (4 CTAs an SM with 256-thread tile CTAs: 10,240 registers fit in the 16,384 left), ps5c (5 CTAs an SM + carve-outs: does the carve-out alone change plt9's ps1?), a2b (control again).
# Needs: as plt9.sh, with /content/f28p updated to the commit named in the message (gpu_fermat28.py: persist_kernel applies FERMAT_CARVEOUT).  Output: /content/plt10/result.txt.
W=/content/plt10; mkdir -p $W; cd $W; rm -rf base a2 ps3 ps3f ps2 ps4t ps5c a2b result.txt bench.txt
T=/content/ua_v3; [ -d $T ] || { echo NO-TREE > result.txt; exit 1; }
[ -f /content/f28p/bench_persist.py ] || { echo NO-F28P > result.txt; exit 1; }
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt10/my_specs.json", "w"))
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
# 1. the kernel alone
( cd /content/f28p && for c in 5 3 2; do echo "--- --cta-sm $c"; timeout 600 python3 bench_persist.py --sync 1 --cta-sm $c --reps 3; done ) > $W/bench.txt 2>&1
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
X=search_gpu5_xb6.py
PF="FERMAT28_DIR=/content/f28p"
A2="GBATCH_GROUP_DELAY_US=500"
PL3="--pipeline 1 --pipeline-depth 2 --trace-pipeline 1"
TT="--deep-tile-threads 512"
TL="--tail-target 65536 --dtail 256"
CV="FERMAT_CARVEOUT=100 DEEP_CARVEOUT=100"
PS="--pool-threads 2 --persist 1 $TL"
run base $X $T "" "--pool-threads 2"
run a2   $X $T "$A2" "$PL3 --pool-threads 2 $TT"
run ps3  $X $T "$A2 $PF $CV" "$PL3 $PS --persist-cta-sm 3 $TT"
run ps3f $X $T "GBATCH_SYNC_EVERY=0 GBATCH_GROUP_DELAY_US=0 $PF $CV" "$PL3 $PS --persist-cta-sm 3 $TT"
run ps2  $X $T "$A2 $PF $CV" "$PL3 $PS --persist-cta-sm 2 $TT"
run ps4t $X $T "$A2 $PF $CV" "$PL3 $PS --persist-cta-sm 4 --deep-tile-threads 256"
run ps5c $X $T "$A2 $PF $CV" "$PL3 $PS $TT"
run a2b  $X $T "$A2" "$PL3 --pool-threads 2 $TT"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/plt10"
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
for d in ("base", "a2", "ps3", "ps3f", "ps2", "ps4t", "ps5c", "a2b"):
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
print("PLT10-DONE")
PY
