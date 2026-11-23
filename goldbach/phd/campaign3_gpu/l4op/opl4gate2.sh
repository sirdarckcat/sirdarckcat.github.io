#!/bin/bash
# The L4 gate's per-member part again (opl4gate.sh's f = 0 window ran out of memory on the L4: 28 GB of survivor rows for 2^25 members):
#   pm2_base / pm2_new: the m88f known-case vector (kc_m88f.json), one production window k in [2^32 - 2^25, 2^32), production's f, near-misses >= 45,061: the per-member
#     (k, first-PRP row) lists of the tested members identical between base (uaB, production) and new (ua_v10 + the options + one-pass: the FAST path, 128 bins, ~48 marks a bin, 75 slots),
#     and every one of them inside [2^32 - 2^19, 2^32) equal to cpu_brute_k0.py's entry for that k;
#   kc2_new: the known case itself (2^19 window, f = 0, >= 45,061) with new's options and parameters but one-pass off (fc12768's host check refuses one-pass on a one-tile window):
#     the same 40 (k, q) as the CPU brute force.
# The campaign is STOPPED (one campaign's memory) and restarted unchanged at the end.
NEW_ENV="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256 DEEP_GEN_ONEPASS=1 DEEP_GEN_SLOT_C=75"
NEW_ENV_KC="DEEP_BIN_PACK=1 DEEP_GEN_HOIST=1 DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1 DEEP_GEN_UNROLL=4 DEEP_TILE_UNROLL=4 DEEP_TILE_PREFETCH=256"
NEW_ARGS="--deep-rg 32 --deep-gen-threads 512 --deep-tile-threads 512"
W=/content/opl4g2; mkdir -p $W; cd $W; rm -rf pm2_base pm2_new kc2_new result.txt status.txt
E=$(cat /content/next_campaign_env); DE=$(cat /content/deep_env); C=$(cat /content/next_campaign_dir | awk '{print $1}')
val() { echo "$E" | tr ' ' '\n' | sed -n "s/^$1=//p" | tail -n 1; }
T3=$(val SIEVE200); T10=/content/ua_v10/goldbach/sieve200; F=$(val SKIPF)
STARTED=0
start_campaign() {
  [ $STARTED = 1 ] && return; STARTED=1
  setsid nohup bash -c 'env $(cat /content/next_campaign_env) DEEP_ARGS="$(cat /content/deep_env)" bash /content/run_v5_campQ.sh '"$C" > /dev/null 2>&1 < /dev/null &
  echo "$(date -u +%FT%TZ) campaign restarted in $C (unchanged)" >> $W/status.txt
}
trap start_campaign EXIT
echo "$(date -u +%FT%TZ) stopping the campaign in $C | base tree $T3" > status.txt
pkill -f 'run_v[345]_[a-zA-Z0-9_]*[.]sh'; sleep 1; pkill -f "search_gpu[345][.]py --campaign $C "
for i in $(seq 1 90); do pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null || break; sleep 1; done
pgrep -f "search_gpu[345][.]py --campaign $C " > /dev/null && { pkill -9 -f "search_gpu[345][.]py --campaign $C "; sleep 10; }
echo "$(date -u +%FT%TZ) stopped" >> status.txt
run() {   # name specs klo kmax batch tree extra-env extra-args...
  local n=$1 sp=$2 lo=$3 hi=$4 b=$5 tree=$6 xe=$7; shift 7
  local D=$W/$n; mkdir -p $D; cp $sp $D/my_specs.json
  ( export $E $xe
    timeout 900 python3 /content/c3g/search_gpu5.py --campaign $D --goldbach /content/c3g --batch $b --pool ${POOL:-2097152} --p-est 0.055 --kmax $hi --klo $lo --desc --no-stop \
      --kernel ${KERNEL:-28} --sieve200 $tree --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm ${K28_ASM:-0} "$@" > $D/driver.log 2>&1 ); echo "rc=$?" >> $D/driver.log
}
run pm2_base /content/kc_m88f.json $(( (1 << 32) - (1 << 25) )) $(( 1 << 32 )) 1 $T3  ""            --skip-frac ${F:-0.97} --near-miss 45061 $DE
run pm2_new  /content/kc_m88f.json $(( (1 << 32) - (1 << 25) )) $(( 1 << 32 )) 1 $T10 "$NEW_ENV"     --skip-frac ${F:-0.97} --near-miss 45061 $DE $NEW_ARGS
run kc2_new  /content/kc_m88f.json $(( (1 << 32) - (1 << 19) )) $(( 1 << 32 )) 1 $T10 "$NEW_ENV_KC"  --skip-frac 0 --near-miss 45061 $DE --klog 19 --slice 524288 $NEW_ARGS
start_campaign; trap - EXIT
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/opl4g2"
REF = [(4294454767, 53857), (4294464281, 53617), (4294473436, 48817), (4294480898, 48049), (4294491537, 51607), (4294541430, 47041), (4294542945, 46861), (4294559947, 53617),
       (4294567075, 48757), (4294577715, 51691), (4294583129, 51061), (4294594077, 45979), (4294601316, 49171), (4294646766, 52999), (4294649190, 47797), (4294660934, 51517),
       (4294661226, 55051), (4294675479, 46861), (4294678224, 55057), (4294684842, 46171), (4294689431, 49477), (4294700014, 58687), (4294704723, 48871), (4294723595, 51349),
       (4294843739, 47041), (4294864526, 46171), (4294867414, 46861), (4294867716, 48817), (4294870650, 48649), (4294874592, 49669), (4294875689, 46867), (4294904695, 48259),
       (4294905461, 51439), (4294927539, 52189), (4294933892, 75037), (4294934565, 46687), (4294954675, 48757), (4294955845, 45979), (4294957980, 51061), (4294960722, 46441)]
R = dict(REF)
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def rd(f):
    return open(f).read().splitlines() if os.path.exists(f) else []
def sl(d):
    return {m.group(1): m.group(4) for m in map(pat.match, rd(f"{W}/{d}/search.log")) if m}
def nms(d):
    return sorted((int(x["k"]), int(x["g"])) for x in (json.loads(t[t.index("{"):]) for t in rd(f"{W}/{d}/found.jsonl") if t.strip()))
def errs(d):
    return [l.strip()[:150] for l in rd(f"{W}/{d}/driver.log") if "rror" in l or "Traceback" in l or "refuse" in l][:2]
print(open(f"{W}/status.txt").read().strip())
pb, pn = nms("pm2_base"), nms("pm2_new")
inkc = [x for x in pn if x[0] >= (1 << 32) - (1 << 19)]
cons = all(R.get(k) == q for k, q in inkc)
print(f"one 2^25 window at production f, near-misses >= 45,061 among the tested: base {len(pb)}, new {len(pn)}, per-member identical {pb == pn} | slices identical {sl('pm2_base') == sl('pm2_new')} {sl('pm2_new')} | {errs('pm2_base')} {errs('pm2_new')}")
print(f"  of them inside [2^32 - 2^19, 2^32): {len(inkc)}, each equal to the CPU brute force's entry: {cons} ({inkc[:6]})")
kc = nms("kc2_new")
print(f"known case (2^19, f = 0) with new's options and parameters, one-pass off: {len(kc)} near-misses, identical to the CPU brute force's 40: {kc == REF} | {errs('kc2_new')}")
print("L4-GATE2", "PASSED" if pb and pb == pn and sl("pm2_base") == sl("pm2_new") and cons and kc == REF else "FAILED")
print("OPL4G2-DONE")
PY
