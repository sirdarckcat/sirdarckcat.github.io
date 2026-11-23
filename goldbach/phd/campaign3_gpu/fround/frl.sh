#!/bin/bash
# Fused Fermat rounds (uarch 4639f17, --fused-rounds 1: run_pool's bookkeeping as 5 device kernels) on this L4 / T4, 88 moduli, the card's own production configuration
# (next_campaign_env, deep_env; no pipeline), under the lead's standing rule for engine changes. The campaign is STOPPED for the checks (this card's memory
# holds one campaign's sieve matrix only) and restarted at the end: with the fused rounds if every check passes, else as it was.
#   base, base_b: the production driver /content/c3g/search_gpu5.py, the card's FERMAT28_DIR and K28_STEP;  frw: search_gpu5_fr.py --fused-rounds 1, /content/f29fr (the card's
#   FERMAT28_DIR with fround.py and fround_kernels.cuh), the same step
#   identity: 4 of the card's Q = 170,000 vectors x 2 production windows just below 2^30 (no campaign scans k < 2^30): slice lines identical, no range errors
#   known case (frw): 146,191's member (r200_q140k_c_v77, k = 3,101,585,871) under its Q = 150,000 residual (1,120 rows; 146,191 the 1,072nd), the 2^20 window
#   from 3,100,639,232, every member tested (f = 0), near-misses >= 140,000: the member reported, CPU-verified, with g = 146,191 by (a) the normal sieve
#   (B = 10^6) and (c) the deep sieve (B = 10^8).  Deployed only if, besides, frw's batch is at least 1% faster than production's.  Result in /content/frl/result.txt (FRL-GATE PASSED/FAILED), deploy.txt, status.txt.
W=/content/frl; mkdir -p $W; cd $W; rm -rf base frw base_b kca kcc result.txt deploy.txt status.txt
E=$(cat /content/next_campaign_env); DE=$(cat /content/deep_env); C=$(cat /content/next_campaign_dir | awk '{print $1}')
val() { echo "$E" | tr ' ' '\n' | sed -n "s/^$1=//p" | tail -n 1; }
FD0=$(val FERMAT28_DIR); ST0=$(val K28_STEP)
S=$(python3 -c "import sys; a = sys.argv[1].split(); print(a[a.index('--slice') + 1])" "$DE")
KLO_T=$(( (1 << 30) - 2 * S ))
[ -f /content/f29fr/fround.py ] || { [ -d /content/f29fr ] || cp -a $FD0 /content/f29fr; tar -xzf /content/fr_overlay.tgz -C /content/f29fr; }
python3 - "$C" <<'PY'
import json, sys
s = json.load(open(sys.argv[1] + "/my_specs.json"))[:4]
for v in s:
    v.pop("kstart", None); v.pop("kmax", None)
json.dump(s, open("/content/frl/ids.json", "w"))
PY
STARTED=0
start_campaign() {
  [ $STARTED = 1 ] && return; STARTED=1
  setsid nohup bash -c 'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" bash /content/run_v5_campQ.sh '"$C" > /dev/null 2>&1 < /dev/null &
  echo "$(date -u +%FT%TZ) campaign restarted in $C with $(cat /content/next_campaign_env | tr ' ' '\n' | grep -E '^(FERMAT28_DIR|K28_STEP)=' | tr '\n' ' ')" >> $W/status.txt
}
trap start_campaign EXIT
echo "$(date -u +%FT%TZ) stopping the campaign in $C (slice $S, test windows k in [$KLO_T, 2^30))" > status.txt
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f "search_gpu[345][.]py --campaign $C "
for i in $(seq 1 90); do pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null || break; sleep 1; done
pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null && { pkill -9 -f "search_gpu[345][.]py --campaign $C "; sleep 10; }
echo "$(date -u +%FT%TZ) stopped" >> status.txt
run() {   # name driver fermat-dir step specs klo kmax batch extra-args...
  local n=$1 drv=$2 fd=$3 st=$4 sp=$5 lo=$6 hi=$7 b=$8; shift 8
  local D=$W/$n; mkdir -p $D; cp $sp $D/my_specs.json
  ( export $E; export FERMAT28_DIR=$fd
    timeout 900 python3 /content/c3g/$drv --campaign $D --goldbach /content/c3g --batch $b --pool ${POOL:-1048576} --p-est 0.055 --kmax $hi --klo $lo --desc --no-stop \
      --kernel ${KERNEL:-28} --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $st --k28-asm ${K28_ASM:-1} "$@" > $D/driver.log 2>&1 ) &
  local PID=$! last=0 m
  while kill -0 $PID 2>/dev/null; do
    m=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$m" != "$last" ]; then echo "$m $(date +%s.%N)" >> $D/stamps.txt; last=$m; fi
    sleep 0.05
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
B=$(val BATCH); F=$(val SKIPF); NM=$(val NEAR_MISS)
run base search_gpu5.py $FD0 $ST0 $W/ids.json $KLO_T 1073741824 ${B:-2} --skip-frac ${F:-0.97} --near-miss ${NM:-0} $DE
run frw search_gpu5_fr.py /content/f29fr $ST0 $W/ids.json $KLO_T 1073741824 ${B:-2} --skip-frac ${F:-0.97} --near-miss ${NM:-0} $DE --fused-rounds 1
run base_b search_gpu5.py $FD0 $ST0 $W/ids.json $KLO_T 1073741824 ${B:-2} --skip-frac ${F:-0.97} --near-miss ${NM:-0} $DE
run kca search_gpu5_fr.py /content/f29fr $ST0 /content/nm150_v77.json 3100639232 3101687808 1 --skip-frac 0 --near-miss 140000 --sieve-b 1000000 --slice 1048576 --fused-rounds 1
run kcc search_gpu5_fr.py /content/f29fr $ST0 /content/nm150_v77.json 3100639232 3101687808 1 --skip-frac 0 --near-miss 140000 \
    --deep 1 --klog 20 --slice 1048576 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --fused-rounds 1
echo "$(date -u +%FT%TZ) checks done" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/frl"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stamps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    return [t for n, t in v if n >= 1]
def errs(d):
    f = f"{W}/{d}/driver.log"
    L = open(f).read().splitlines() if os.path.exists(f) else []
    return [l.strip()[:200] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l or "outside" in l][:4]
def found(d):
    f = f"{W}/{d}/found.jsonl"
    return [json.loads(l[l.index("{"):]) for l in open(f) if l.strip()] if os.path.exists(f) else []
ref = lines("base"); ok_id = len(ref) == 8; mean = {}
for d in ("base", "frw", "base_b"):
    t = stamps(d); g = [round(y - x, 3) for x, y in zip(t, t[1:])]
    m = sum(g) / len(g) if g else float("nan"); mean[d] = m
    v = lines(d); same = bool(v) and v == ref
    e = errs(d)
    ok_id = ok_id and same and not any("outside" in x or "Traceback" in x or "rror" in x for x in e)
    print(f"{d:6s}: gaps {g} | mean after the first batch {m:.3f} s | slice lines vs base: {'IDENTICAL' if same else 'DIFFERENT'} ({len(v)}) | {e}")
ok = {}
for d, what in (("kca", "normal sieve"), ("kcc", "deep sieve")):
    r = found(d)
    ok[d] = any(int(x["k"]) == 3101585871 and int(x["g"]) == 146191 and x.get("near_miss") for x in r)
    print(f"{d}: known case ({what}): reported {[(x['k'], x['g'], x.get('near_miss')) for x in r]} | slices {len(lines(d))} | {errs(d)} | 146,191's member: {ok[d]}")
b0 = (mean["base"] + mean["base_b"]) / 2; fast = mean["frw"] <= 0.99 * b0
print(f"batch: frw {mean['frw']:.3f} s against {b0:.3f} s for production (x{mean['frw'] / b0:.4f}); deploy needs <= x0.99: {fast}")
print("FRL-GATE", "PASSED" if ok_id and ok["kca"] and ok["kcc"] and fast else "FAILED")
PY
if grep -q "FRL-GATE PASSED" result.txt; then
  [ -f /content/c3g/search_gpu5_prev_fr.py ] || cp -p /content/c3g/search_gpu5.py /content/c3g/search_gpu5_prev_fr.py
  cp -p /content/c3g/search_gpu5_fr.py /content/c3g/search_gpu5.py
  python3 - <<'PY'
e = [x for x in open("/content/next_campaign_env").read().split() if not x.startswith("FERMAT28_DIR=")]
open("/content/next_campaign_env", "w").write(" ".join(e + ["FERMAT28_DIR=/content/f29fr"]))
d = open("/content/deep_env").read().strip()
if "--fused-rounds" not in d:
    open("/content/deep_env", "w").write(d + " --fused-rounds 1")
PY
  echo "deployed: driver search_gpu5_fr.py as search_gpu5.py (the old one kept as search_gpu5_prev_fr.py), FERMAT28_DIR=/content/f29fr, --fused-rounds 1 in deep_env" > deploy.txt
else
  echo "not deployed: the gate failed; the campaign restarts unchanged" > deploy.txt
fi
start_campaign; trap - EXIT
sleep 20; echo "$(date -u +%FT%TZ) procs $(pgrep -fc "search_gpu5[.]py --campaign $C ")" >> status.txt
echo FRL-DONE >> result.txt
