#!/bin/bash
# plt6.sh (uarch session, 23 Nov 2026 ~09:30Z): a CPU share that does not delay the GPU driver's threads.  plt4's `top` (GPU session): the host has 48 cores, load 40, 91% of the CPU niced (4 drivers x 11 search_c.py
# processes at nice 5), and the GPU driver (main thread, two Fermat threads, the sieve thread: all at nice 0) wakes from a CUDA sync ~300 times a batch (3 syncs a Fermat round, a check after each of ~80 row groups
# a window): on a host whose cores are all busy a waking thread can wait for a core (CFS wake-up preemption of a nice-5 task is not immediate), which lengthens exactly the host gaps between the Fermat rounds
# and the sieve's bubbles.  plt5 (GPU session) measures the effect with the CPU share paused (SIGSTOP).  This script tries the DEPLOYABLE versions, so that the CPU share keeps running:
#   i : every thread of the CPU share (search_c.py workers and their launcher, which passes the policy on to the workers it starts) in SCHED_IDLE (chrt -i): runs only when no normal thread wants the core, and
#       is preempted at once by a waking GPU thread (a nice-5 task is only de-prioritised, not preempted at once);
#   t : the CPU share pinned away from 4 physical cores (8 hardware threads, both siblings of each; taskset), the GPU driver pinned to those: its threads never meet a busy core or a busy SMT sibling.
# Runs (6 batches each, the harness of plt3-5): j0 / a2 with the CPU share as it is (control), j0i / a2i (SCHED_IDLE), j0t / a2t (pinned), basei (the production driver without the pipeline, SCHED_IDLE).
# a2 = GBATCH_GROUP_DELAY_US=500 + --deep-tile-threads 512 (plt4's best).  The policy / affinity of the CPU share is restored at the end, whatever happens, and the campaign resumed.
W=/content/plt6; mkdir -p $W; cd $W; rm -rf j0 a2 j0i a2i j0t a2t basei result.txt
T=/content/ua_v3; [ -d $T ] || { echo NO-TREE > result.txt; exit 1; }
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt6/my_specs.json", "w"))
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
share() { pgrep -f 'search_c[.]py|run_campaign3_hi[.]py'; }
# the cores kept for the GPU driver: 4 PHYSICAL cores with both hardware threads (the 48 "cores" of an AMD EPYC 9B45 host are probably 24 cores x 2 SMT threads: a driver thread whose SMT sibling runs a
# CPU-share worker (AVX-512 IFMA) loses much of its core however the scheduler ranks the two); REST = all the others, for the CPU share
read RES REST <<< "$(python3 - <<'PY'
seen, res = [], []
n = 0
while True:
    try:
        s = open(f"/sys/devices/system/cpu/cpu{n}/topology/thread_siblings_list").read().strip()
    except Exception:
        break
    n += 1
    if s not in seen and len(seen) < 4:
        seen.append(s)
def expand(t):
    out = set()
    for part in t.split(","):
        a, _, b = part.partition("-")
        out.update(range(int(a), int(b or a) + 1))
    return out
r = set()
for s in seen:
    r |= expand(s)
f = lambda S: ",".join(str(x) for x in sorted(S))
print(f(r), f(set(range(n)) - r))
PY
)"
idle() {     # idle on|off: SCHED_IDLE for every thread of the CPU share (off: back to SCHED_OTHER)
  for p in $(share); do
    for t in /proc/$p/task/*; do
      if [ "$1" = on ]; then chrt -i -p 0 ${t##*/} 2>/dev/null; else chrt -o -p 0 ${t##*/} 2>/dev/null; fi
    done
  done
}
pin() {      # pin on|off: the CPU share on REST (everything but the 4 cores kept for the driver); off: all cores again
  for p in $(share); do if [ "$1" = on ]; then taskset -a -cp $REST $p >/dev/null 2>&1; else taskset -a -cp $(cat /sys/devices/system/cpu/online) $p >/dev/null 2>&1; fi; done
}
restore() { idle off; pin off; [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap restore EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}; driver cores [$RES], CPU share cores [$REST]; threads per core: $(lscpu | grep -i 'thread(s) per core'); CPU share: $(share | wc -l) processes; policies before: $(for p in $(share | head -3); do chrt -p $p | head -1; done | tr '\n' ' ')" > status.txt
run() {   # name driver extra-env extra-args prefix
  D=$W/$1; mkdir -p $D; cp $W/my_specs.json $D/
  timeout 400 env $E DEEP_STAGED=1 $3 $5 python3 /content/c3g/$2 --campaign $D --goldbach /content/c3g --batch 2 --pool 2097152 --skip-frac 0.97 --p-est 0.055 \
    --kmax 1073741824 --klo 1006632960 --desc --no-stop --kernel 28 --sieve200 $T/goldbach/sieve200 --sieve-threads 256 --k28-step fermat28_step_s1r.cuh --k28-asm 1 \
    --near-miss 157837 --deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 $4 > $D/driver.log 2>&1 &
  PID=$!
  (sleep 9; top -H -b -n 1 -w 200 2>/dev/null | head -16 > $D/top.txt) &
  last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
PL="--pipeline 1 --pipeline-depth 2 --trace-pipeline 1 --pool-threads 2"
X=search_gpu5_xb3.py
A2="GBATCH_GROUP_DELAY_US=500"
run j0 $X "" "$PL" ""
run a2 $X "$A2" "$PL --deep-tile-threads 512" ""
idle on;  echo "$(date -u +%FT%TZ) CPU share SCHED_IDLE: $(for p in $(share | head -3); do chrt -p $p | head -1; done | tr '\n' ' ')" >> status.txt
run j0i $X "" "$PL" ""
run a2i $X "$A2" "$PL --deep-tile-threads 512" ""
run basei search_gpu5.py "" "--pool-threads 2" ""
idle off; pin on; echo "$(date -u +%FT%TZ) CPU share pinned away from [$RES] (driver) onto [$REST]: $(for p in $(share | head -3); do taskset -p $p; done | tr '\n' ' ')" >> status.txt
run j0t $X "" "$PL" "taskset -c $RES"
run a2t $X "$A2" "$PL --deep-tile-threads 512" "taskset -c $RES"
pin off
restore; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/plt6"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stamps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    return [t for n, t in v if n >= 1]
ref = lines("j0")
print(open(f"{W}/status.txt").read())
for d in ("j0", "a2", "j0i", "a2i", "basei", "j0t", "a2t"):
    t = stamps(d)
    g = [round(y - x, 3) for x, y in zip(t, t[1:])]
    beside = sum(g[:-1]) / len(g[:-1]) if len(g) > 1 else float("nan")
    v = lines(d)
    L = open(f"{W}/{d}/driver.log").read().splitlines() if os.path.exists(f"{W}/{d}/driver.log") else []
    err = [l.strip()[:160] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:3]
    print(f"{d:6s}: gaps {g} | mean of the batches with a sieve beside them {beside:.3f} s | slice lines vs j0: {'IDENTICAL' if v and v == ref else 'DIFFERENT'} ({len(v)}) | {err}")
    for l in [l for l in L if l.startswith("[pipeline]")][1:-1]:
        m = re.search(r"waited ([\d.]+) s for the sieve; the sieve thread made (\d+) windows in ([\d.]+) s and waited ([\d.]+) s", l)
        if m:
            print(f"         [pipeline] waited {m.group(1)} s; sieve {m.group(2)} windows busy {m.group(3)} s, idle {m.group(4)} s")
    tp = f"{W}/{d}/top.txt"
    if os.path.exists(tp):
        T = open(tp).read().splitlines()
        print("          top:", " | ".join(x.strip()[:110] for x in T[:3]))
print("PLT6-DONE")
PY
