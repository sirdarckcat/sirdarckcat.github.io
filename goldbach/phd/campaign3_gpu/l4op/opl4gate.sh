#!/bin/bash
# The RTX cards' sieve options (+ uarch's one-pass kernel) on this L4/T4 in the driver, under the standing rule (same tested members and first-PRP rows by construction; identity on
# the same windows + the known case; >= 1% of a batch). NEW_ENV / NEW_ARGS below are set by the launcher (sed) from opl4b.sh's best row. Tree /content/ua_v10 (this card's uaB +
# f1b904a's sieve200/cuda + fc12768's gbig.py). base = production (uaB, deep_env), new = ua_v10 + NEW_ENV + deep_env + NEW_ARGS; base / new / base_b / new_b on 4 of this card's
# vectors x 2 windows of 2^25 just below 2^30 (campaign mode, production's f and batch); slice lines identical; then pm_base / pm_new: the m88f known-case vector (kc_m88f.json) on
# ONE production-size window, k in [2^32 - 2^25, 2^32), f = 0 (every member tested), near-misses >= 45,061: the per-member (k, first-PRP row) lists identical between base and new
# (the one-pass FAST path: 64 tiles x rcta 2 = 128 bins, ~48 marks a bin < 75 slots), and inside [2^32 - 2^19, 2^32) exactly cpu_brute_k0.py's 40 (the known case at the production
# window; a 2^19 window has one tile, where one-pass would only run its fallback, and fc12768's host check refuses it). Campaign STOPPED (one campaign's memory), restarted at the end.
NEW_ENV="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256 DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=75"
NEW_ARGS="--deep-rg 32 --deep-gen-threads 512 --deep-tile-threads 512"
W=/content/opl4g; mkdir -p $W; cd $W; rm -rf base new base_b new_b pm_base pm_new result.txt status.txt
[ -d /content/ua_v10 ] || cp -a /content/uaB /content/ua_v10
tar -xzf /content/ua10_cuda.tgz -C /content/ua_v10/goldbach/sieve200/cuda
E=$(cat /content/next_campaign_env); DE=$(cat /content/deep_env); C=$(cat /content/next_campaign_dir | awk '{print $1}')
val() { echo "$E" | tr ' ' '\n' | sed -n "s/^$1=//p" | tail -n 1; }
T3=$(val SIEVE200); T10=/content/ua_v10/goldbach/sieve200
S=$(python3 -c "import sys; a = sys.argv[1].split(); print(a[a.index('--slice') + 1])" "$DE"); KLO_T=$(( (1 << 30) - 2 * S ))
python3 -c "import json; s=json.load(open('$C/my_specs.json'))[:4]; [v.pop(k, None) for v in s for k in ('kstart', 'kmax')]; json.dump(s, open('$W/four.json', 'w'))"
STARTED=0
start_campaign() {
  [ $STARTED = 1 ] && return; STARTED=1
  setsid nohup bash -c 'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" bash /content/run_v5_campQ.sh '"$C" > /dev/null 2>&1 < /dev/null &
  echo "$(date -u +%FT%TZ) campaign restarted in $C (unchanged)" >> $W/status.txt
}
trap start_campaign EXIT
echo "$(date -u +%FT%TZ) stopping the campaign in $C | base tree $T3 | new: $NEW_ENV $NEW_ARGS" > status.txt
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f "search_gpu[345][.]py --campaign $C "
for i in $(seq 1 90); do pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null || break; sleep 1; done
pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null && { pkill -9 -f "search_gpu[345][.]py --campaign $C "; sleep 10; }
echo "$(date -u +%FT%TZ) stopped" >> status.txt
run() {   # name specs klo kmax batch tree extra-env extra-args...
  local n=$1 sp=$2 lo=$3 hi=$4 b=$5 tree=$6 xe=$7; shift 7
  local D=$W/$n; mkdir -p $D; cp $sp $D/my_specs.json
  ( export $E $xe
    timeout 900 python3 /content/c3g/search_gpu5.py --campaign $D --goldbach /content/c3g --batch $b --pool ${POOL:-2097152} --p-est 0.055 --kmax $hi --klo $lo --desc --no-stop \
      --kernel ${KERNEL:-28} --sieve200 $tree --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm ${K28_ASM:-0} "$@" > $D/driver.log 2>&1 ) &
  local PID=$! last=0 m
  while kill -0 $PID 2>/dev/null; do
    m=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$m" != "$last" ]; then echo "$m $(date +%s.%N)" >> $D/stamps.txt; last=$m; fi
    sleep 0.05
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
B=$(val BATCH); F=$(val SKIPF)
run base   $W/four.json $KLO_T 1073741824 ${B:-2} $T3  ""         --skip-frac ${F:-0.97} --near-miss 158209 $DE
run new    $W/four.json $KLO_T 1073741824 ${B:-2} $T10 "$NEW_ENV" --skip-frac ${F:-0.97} --near-miss 158209 $DE $NEW_ARGS
run base_b $W/four.json $KLO_T 1073741824 ${B:-2} $T3  ""         --skip-frac ${F:-0.97} --near-miss 158209 $DE
run new_b  $W/four.json $KLO_T 1073741824 ${B:-2} $T10 "$NEW_ENV" --skip-frac ${F:-0.97} --near-miss 158209 $DE $NEW_ARGS
run pm_base /content/kc_m88f.json $(( (1 << 32) - (1 << 25) )) $(( 1 << 32 )) 1 $T3  ""         --skip-frac 0 --near-miss 45061 $DE
run pm_new  /content/kc_m88f.json $(( (1 << 32) - (1 << 25) )) $(( 1 << 32 )) 1 $T10 "$NEW_ENV" --skip-frac 0 --near-miss 45061 $DE $NEW_ARGS
start_campaign; trap - EXIT
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/opl4g"
REF = [(4294454767, 53857), (4294464281, 53617), (4294473436, 48817), (4294480898, 48049), (4294491537, 51607), (4294541430, 47041), (4294542945, 46861), (4294559947, 53617),
       (4294567075, 48757), (4294577715, 51691), (4294583129, 51061), (4294594077, 45979), (4294601316, 49171), (4294646766, 52999), (4294649190, 47797), (4294660934, 51517),
       (4294661226, 55051), (4294675479, 46861), (4294678224, 55057), (4294684842, 46171), (4294689431, 49477), (4294700014, 58687), (4294704723, 48871), (4294723595, 51349),
       (4294843739, 47041), (4294864526, 46171), (4294867414, 46861), (4294867716, 48817), (4294870650, 48649), (4294874592, 49669), (4294875689, 46867), (4294904695, 48259),
       (4294905461, 51439), (4294927539, 52189), (4294933892, 75037), (4294934565, 46687), (4294954675, 48757), (4294955845, 45979), (4294957980, 51061), (4294960722, 46441)]
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def rd(f):
    return open(f).read().splitlines() if os.path.exists(f) else []
def sl(d):
    return {m.group(1): m.group(4) for m in map(pat.match, rd(f"{W}/{d}/search.log")) if m}
def errs(d):
    return [l.strip()[:150] for l in rd(f"{W}/{d}/driver.log") if "rror" in l or "Traceback" in l or "static_assert" in l or "refuse" in l][:2]
def gaps(d):
    v = [tuple(map(float, l.split())) for l in rd(f"{W}/{d}/stamps.txt")]
    t = [x for n, x in v if n >= 1]
    return [y - x for x, y in zip(t, t[1:])]
print(open(f"{W}/status.txt").read().strip())
ref = sl("base"); ok = len(ref) == 8; m = {}
for d in ("base", "new", "base_b", "new_b"):
    g = gaps(d); m[d] = sum(g) / len(g) if g else float("nan")
    same = bool(sl(d)) and sl(d) == ref and not errs(d); ok = ok and same
    print(f"{d:6s}: gaps {[round(x, 3) for x in g]} | mean {m[d]:.3f} s | slice lines vs base: {'IDENTICAL' if same else 'DIFFERENT'} ({len(sl(d))}) | {errs(d)}")
b = (m["base"] + m["base_b"]) / 2; n = (m["new"] + m["new_b"]) / 2
def nms(d):
    return sorted((int(x["k"]), int(x["g"])) for x in (json.loads(t[t.index("{"):]) for t in rd(f"{W}/{d}/found.jsonl") if t.strip()))
pb, pn = nms("pm_base"), nms("pm_new")
kc = [x for x in pn if x[0] >= (1 << 32) - (1 << 19)]
print(f"new {n:.3f} s a batch against base {b:.3f} s: x{n / b:.4f}")
print(f"one 2^25 window at f = 0, near-misses >= 45,061: base {len(pb)}, new {len(pn)}, per-member identical {pb == pn} | slices base {sl('pm_base')} new {sl('pm_new')} | {errs('pm_base')} {errs('pm_new')}")
print(f"known case inside it (k >= 2^32 - 2^19): {len(kc)} near-misses, identical to the CPU brute force's 40: {kc == REF}")
ok_pm = bool(pb) and pb == pn and sl("pm_base") == sl("pm_new") and kc == REF
print("L4-GATE", "PASSED" if ok and ok_pm and n / b <= 0.99 else "FAILED", f"x{n / b:.4f}")
print("OPL4G-DONE")
PY
