#!/bin/bash
# plt5.sh (GPU session, 23 Nov 09:20Z): does the CPU share on this host (4 drivers x 11 search_c.py processes at nice 5 on 48 cores: load 40, 91% of the CPU
# niced in plt4's top snapshot) slow the GPU driver's host threads? Same harness as the uarch's plt4.sh (/content/ua_v3, search_gpu5_xb3.py, 6 batches), plus
# the --profile-pool diagnostic that plt4 lost (the flag needs a value).  With the CPU share running: j0 (production pipeline), a2 (500 us bubble + 512-thread
# tiles), pj (j0 + --profile-pool 1), pb (no pipeline + --profile-pool 1); then with the CPU share paused (SIGSTOP): j0c, a2c, pjc, basec.  The campaign and the
# CPU share are resumed at the end, whatever happens.
W=/content/plt5; mkdir -p $W; cd $W; rm -rf j0 a2 pj pb j0c a2c pjc basec result.txt
T=/content/ua_v3; [ -d $T ] || { echo NO-TREE > result.txt; exit 1; }
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt5/my_specs.json", "w"))
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
cpu() { pkill -$1 -f 'run_campaign3_hi[.]py'; pkill -$1 -f 'search_c[.]py'; }
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; cpu CONT; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}; CPU share: $(pgrep -fc 'search_c[.]py') search_c.py processes" > status.txt
run() {   # name driver extra-env extra-args
  D=$W/$1; mkdir -p $D; cp $W/my_specs.json $D/
  timeout 400 env $E DEEP_STAGED=1 $3 python3 /content/c3g/$2 --campaign $D --goldbach /content/c3g --batch 2 --pool 2097152 --skip-frac 0.97 --p-est 0.055 \
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
run j0 $X "" "$PL"
run a2 $X "$A2" "$PL --deep-tile-threads 512"
run pj $X "" "$PL --profile-pool 1"
run pb search_gpu5.py "" "--pool-threads 2 --profile-pool 1"
cpu STOP; echo "$(date -u +%FT%TZ) CPU share paused" >> status.txt
run j0c $X "" "$PL"
run a2c $X "$A2" "$PL --deep-tile-threads 512"
run pjc $X "" "$PL --profile-pool 1"
run basec search_gpu5.py "" "--pool-threads 2"
cpu CONT; echo "$(date -u +%FT%TZ) CPU share resumed" >> status.txt
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/plt5"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stamps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    return [t for n, t in v if n >= 1]
ref = lines("j0")
for d in ("j0", "a2", "pj", "pb", "j0c", "a2c", "pjc", "basec"):
    t = stamps(d)
    g = [round(y - x, 3) for x, y in zip(t, t[1:])]
    beside = sum(g[:-1]) / len(g[:-1]) if len(g) > 1 else float("nan")
    allb = sum(g) / len(g) if g else float("nan")
    v = lines(d)
    L = open(f"{W}/{d}/driver.log").read().splitlines() if os.path.exists(f"{W}/{d}/driver.log") else []
    err = [l.strip()[:160] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:3]
    print(f"{d:6s}: gaps {g} | mean of batches 2..5 {beside:.3f} s (2..6 {allb:.3f}) | slice lines vs j0: {'IDENTICAL' if v and v == ref else 'DIFFERENT'} ({len(v)}) | {err}")
    pl = [l for l in L if l.startswith("[pipeline]")]
    for l in pl[1:-1]:
        m = re.search(r"waited ([\d.]+) s for the sieve; the sieve thread made (\d+) windows in ([\d.]+) s and waited ([\d.]+) s", l)
        if m:
            print(f"         [pipeline] waited {m.group(1)} s; sieve {m.group(2)} windows busy {m.group(3)} s, idle {m.group(4)} s")
    pp = [l for l in L if l.startswith("[profile-pool]")]
    for l in pp[-6:]:
        print("         ", l[:240])
    tp = f"{W}/{d}/top.txt"
    if os.path.exists(tp):
        T = open(tp).read().splitlines()
        print("          top:", " | ".join(x.strip()[:110] for x in T[:3]))
print("PLT5-DONE")
PY
