#!/bin/bash
# The lead's gate (2) and (3) for research's top32 shift on this L4, production's settings (the deployed next_campaign_env / deep_env: the RTX options, one-pass, rg 32 / 512 / 512):
#   kc: the shifted known-case vector (kc_s32.json, q170000_m88f_top4s_v0), k in [2^32 - 2^19, 2^32), f = 0, near-misses >= T (row 400), one-pass off (a one-tile window):
#       its list for cpu_brute_k0.py's;
#   u / s / u_b / s_b: 8 covers unshifted (eight_u.json, top4) and the same 8 shifted (eight_s.json, top4s), the top two levels k in [2^32 - 2^26, 2^32), production's f and
#       batch: expected design hits (and batch time) shifted against unshifted. The campaign is STOPPED (one campaign's memory) and restarted unchanged at the end.
T=${1:?T}
W=/content/s32g; mkdir -p $W; cd $W; rm -rf kc u s u_b s_b result.txt status.txt
E=$(cat /content/next_campaign_env); DE=$(cat /content/deep_env); C=$(cat /content/next_campaign_dir | awk '{print $1}')
EKC=$(echo "$E" | tr ' ' '\n' | grep -v '^DEEP_GEN_ONEPASS=\|^DEEP_GEN_SLOT_C=\|^KLO=' | tr '\n' ' ')
val() { echo "$E" | tr ' ' '\n' | sed -n "s/^$1=//p" | tail -n 1; }
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
echo "$(date -u +%FT%TZ) stopped" >> status.txt
run() {   # name specs klo kmax batch env extra-args...
  local n=$1 sp=$2 lo=$3 hi=$4 b=$5 xe=$6; shift 6
  local D=$W/$n; mkdir -p $D; cp $sp $D/my_specs.json
  ( export $xe
    timeout 900 python3 /content/c3g/search_gpu5.py --campaign $D --goldbach /content/c3g --batch $b --pool ${POOL:-2097152} --p-est 0.055 --kmax $hi --klo $lo --desc --no-stop \
      --kernel ${KERNEL:-28} --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm ${K28_ASM:-0} "$@" > $D/driver.log 2>&1 ) &
  local PID=$! last=0 m
  while kill -0 $PID 2>/dev/null; do
    m=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$m" != "$last" ]; then echo "$m $(date +%s.%N)" >> $D/stamps.txt; last=$m; fi
    sleep 0.05
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
B=$(val BATCH); F=$(val SKIPF)
run kc /content/kc_s32.json $(( (1 << 32) - (1 << 19) )) $(( 1 << 32 )) 1 "$EKC" --skip-frac 0 --near-miss $T $DE --klog 19 --slice 524288
TOP2=$(( (1 << 32) - (1 << 26) ))
run u   /content/eight_u.json $TOP2 $(( 1 << 32 )) ${B:-2} "$E" --skip-frac ${F:-0.97} --near-miss 158209 $DE
run s   /content/eight_s.json $TOP2 $(( 1 << 32 )) ${B:-2} "$E" --skip-frac ${F:-0.97} --near-miss 158209 $DE
run u_b /content/eight_u.json $TOP2 $(( 1 << 32 )) ${B:-2} "$E" --skip-frac ${F:-0.97} --near-miss 158209 $DE
run s_b /content/eight_s.json $TOP2 $(( 1 << 32 )) ${B:-2} "$E" --skip-frac ${F:-0.97} --near-miss 158209 $DE
start_campaign; trap - EXIT
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/s32g"
def rd(f):
    return open(f).read().splitlines() if os.path.exists(f) else []
def errs(d):
    return [l.strip()[:150] for l in rd(f"{W}/{d}/driver.log") if "rror" in l or "Traceback" in l or "refuse" in l][:2]
def ex(d):
    L = rd(f"{W}/{d}/gpu3_stats.log")
    return sum(float(m.group(1)) for m in (re.search(r"expected hits ([\d.e+-]+)", l) for l in L) if m), len(L)
def gaps(d):
    v = [tuple(map(float, l.split())) for l in rd(f"{W}/{d}/stamps.txt")]
    t = [x for n, x in v if n >= 1]
    g = [y - x for x, y in zip(t, t[1:])]
    return sum(g) / len(g) if g else float("nan")
print(open(f"{W}/status.txt").read().strip())
kc = sorted((int(x["k"]), int(x["g"])) for x in (json.loads(t[t.index("{"):]) for t in rd(f"{W}/kc/found.jsonl") if t.strip()))
print(f"kc (shifted vector, f = 0): {len(kc)} near-misses | {errs('kc')}")
for k, q in kc:
    print(f"GPU k={k} q={q}")
for d in ("u", "s", "u_b", "s_b"):
    h, n = ex(d); sl = len([l for l in rd(f"{W}/{d}/search.log") if l.startswith("[")])
    print(f"{d:4s}: {n} batches, {sl} slices, expected design hits {h:.4e}, batch {gaps(d):.3f} s | {errs(d)}")
hu = ex("u")[0] + ex("u_b")[0]; hs = ex("s")[0] + ex("s_b")[0]
bu = (gaps("u") + gaps("u_b")) / 2; bs = (gaps("s") + gaps("s_b")) / 2
print(f"shifted / unshifted, same 8 covers, top two levels: expected design hits a batch x{hs / hu:.4f}, batch time x{bs / bu:.4f}, a second x{hs / hu * bu / bs:.4f}")
print("S32-RATE", "PASSED" if hs / hu >= 1.03 else "FAILED", f"x{hs / hu:.4f} (>= 1.03; research's prediction x1.056)")
print("S32G-DONE")
PY
