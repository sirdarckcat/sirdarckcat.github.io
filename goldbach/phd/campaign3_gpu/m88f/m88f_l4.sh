#!/bin/bash
# research's m88f covers (the first 88 odd primes, b3d6688) through this L4's production engine, before the switch (the lead's conditions 2-4). The campaign is STOPPED (this card's memory
# holds one campaign only) and restarted UNCHANGED at the end.
#   n97 / n90: the normal path (B = 10^6, block 32768, p-est 0.055) on a 2^20 slice of q170000_m88f_t1_v1, f = 0.97 / 0.9: slice lines to compare with search_c.py's on the same slice;
#   kc: the deep path (this card's deep_env) at f = 0 on q170000_m88f_t1_v0, k in [2^32 - 2^19, 2^32), near-misses >= 45,061 (row 400): to compare with cpu_brute_k0.py's list;
#   cur / new / cur_b / new_b: the production configuration on 4 campaign vectors / 4 m88f vectors, 2 windows of 2^25 just below 2^30 each (members a second).
W=/content/m88f; mkdir -p $W; cd $W; rm -rf n97 n90 kc cur new cur_b new_b result.txt status.txt
E=$(cat /content/next_campaign_env); DE=$(cat /content/deep_env); C=$(cat /content/next_campaign_dir | awk '{print $1}')
val() { echo "$E" | tr ' ' '\n' | sed -n "s/^$1=//p" | tail -n 1; }
S=$(python3 -c "import sys; a = sys.argv[1].split(); print(a[a.index('--slice') + 1])" "$DE"); KLO_T=$(( (1 << 30) - 2 * S ))
python3 - "$C" <<'PY'
import json, sys
s = json.load(open(sys.argv[1] + "/my_specs.json"))[:4]
for v in s:
    v.pop("kstart", None); v.pop("kmax", None)
json.dump(s, open("/content/m88f/cur4.json", "w"))
PY
STARTED=0
start_campaign() {
  [ $STARTED = 1 ] && return; STARTED=1
  setsid nohup bash -c 'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" bash /content/run_v5_campQ.sh '"$C" > /dev/null 2>&1 < /dev/null &
  echo "$(date -u +%FT%TZ) campaign restarted in $C (unchanged)" >> $W/status.txt
}
trap start_campaign EXIT
echo "$(date -u +%FT%TZ) stopping the campaign in $C" > status.txt
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f "search_gpu[345][.]py --campaign $C "
for i in $(seq 1 90); do pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null || break; sleep 1; done
pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null && { pkill -9 -f "search_gpu[345][.]py --campaign $C "; sleep 10; }
echo "$(date -u +%FT%TZ) stopped" >> status.txt
( export $E
  for f in 0.97 0.9; do
    n=n${f#0.}; mkdir -p $W/$n
    timeout 900 python3 /content/c3g/search_gpu5.py /content/slice_m88f.json --goldbach /content/c3g --out $W/$n/found.jsonl --batch 1 --pool ${POOL:-2097152} --skip-frac $f --p-est 0.055 \
      --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm ${K28_ASM:-0} --sieve-b 1000000 --block 32768 --fused-rounds 1 > $W/$n/out.txt 2>&1
    echo "rc=$?" >> $W/$n/out.txt
  done )
run() {   # name specs klo kmax batch extra-args...
  local n=$1 sp=$2 lo=$3 hi=$4 b=$5; shift 5
  local D=$W/$n; mkdir -p $D; cp $sp $D/my_specs.json
  ( export $E
    timeout 900 python3 /content/c3g/search_gpu5.py --campaign $D --goldbach /content/c3g --batch $b --pool ${POOL:-1048576} --p-est 0.055 --kmax $hi --klo $lo --desc --no-stop \
      --kernel ${KERNEL:-28} --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm ${K28_ASM:-1} "$@" > $D/driver.log 2>&1 ) &
  local PID=$! last=0 m
  while kill -0 $PID 2>/dev/null; do
    m=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$m" != "$last" ]; then echo "$m $(date +%s.%N)" >> $D/stamps.txt; last=$m; fi
    sleep 0.05
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
B=$(val BATCH); F=$(val SKIPF)
run kc /content/kc_m88f.json $(( (1 << 32) - (1 << 19) )) $(( 1 << 32 )) 1 --skip-frac 0 --near-miss 45061 $DE --klog 19 --slice 524288
run cur $W/cur4.json $KLO_T 1073741824 ${B:-2} --skip-frac ${F:-0.97} --near-miss 158209 $DE
run new /content/four_m88f.json $KLO_T 1073741824 ${B:-2} --skip-frac ${F:-0.97} --near-miss 158209 $DE
run cur_b $W/cur4.json $KLO_T 1073741824 ${B:-2} --skip-frac ${F:-0.97} --near-miss 158209 $DE
run new_b /content/four_m88f.json $KLO_T 1073741824 ${B:-2} --skip-frac ${F:-0.97} --near-miss 158209 $DE
start_campaign; trap - EXIT
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/m88f"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) (\S+) \((\S+) k/s\) (tests=.*)$")
def lines(f):
    return [m.groups() for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m]
for n in ("n97", "n90"):
    L = lines(f"{W}/{n}/out.txt")
    err = [l.strip()[:160] for l in (open(f"{W}/{n}/out.txt").read().splitlines() if os.path.exists(f"{W}/{n}/out.txt") else []) if "rror" in l or "Traceback" in l or "deep sieve" in l or "M with" in l][:3]
    print(f"{n}: slice lines {[(x[0], x[5]) for x in L]} | {err}")
f = f"{W}/kc/found.jsonl"
nm = sorted((int(x["k"]), int(x["g"])) for x in (json.loads(l[l.index("{"):]) for l in (open(f) if os.path.exists(f) else []) if l.strip()))
print(f"kc: {len(nm)} near-misses >= 45061: {nm}")
print("kc deep-sieve line:", [l.strip()[:220] for l in open(f"{W}/kc/driver.log").read().splitlines() if "deep sieve" in l][:1] if os.path.exists(f"{W}/kc/driver.log") else None)
def gaps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    t = [x for n, x in v if n >= 1]
    g = [y - x for x, y in zip(t, t[1:])]
    return sum(g) / len(g) if g else float("nan")
m = {d: gaps(d) for d in ("cur", "new", "cur_b", "new_b")}
c = (m["cur"] + m["cur_b"]) / 2; n = (m["new"] + m["new_b"]) / 2
print(f"batch: campaign vectors {m['cur']:.3f} / {m['cur_b']:.3f} s, m88f vectors {m['new']:.3f} / {m['new_b']:.3f} s: members a second x{c / n:.4f} (m88f against the campaign's)")
for d in ("cur", "new"):
    L = lines(f"{W}/{d}/search.log"); print(d, "slice lines:", [(x[0], x[5][:90]) for x in L][:2])
print("M88F-DONE")
PY
