#!/bin/bash
# uarch's one-pass generate kernel (f1b904a, DEEP_GEN_ONEPASS=1) in the driver on this RTX PRO 6000, under the standing rule (same tested members and first-PRP rows by construction;
# identity on the same windows + the known case; >= 1% of a batch). Tree /content/ua_v10 (ua_v3 + f1b904a's sieve200/cuda). This card's production tree and DEEP_* options from
# next_campaign_env; base = production; op = ua_v10 + the same options + ONEPASS; opl = op + DEEP_GEN_LB=512,3; then base_b / op_b / opl_b, on the 24 test vectors with production's
# deep_env_v89 (vector mode, f, --target, top placement); slice lines identical to base's; then the vector known case (bottom, 2^19 from k_lo, f = 0, >= 46,171) with the faster
# variant's settings: 23 (k, q) = the CPU brute force's. Campaign paused (SIGSTOP), resumed whatever happens.
W=/content/opgate; mkdir -p $W; cd $W; rm -rf base* op* kc result.txt status.txt
[ -d /content/ua_v10 ] || cp -a /content/ua_v3 /content/ua_v10
tar -xzf /content/ua10_cuda.tgz -C /content/ua_v10/goldbach/sieve200/cuda
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89); SKIPF=$(echo "$E" | tr ' ' '\n' | sed -n 's/^SKIPF=//p')
T3=$(echo "$E" | tr ' ' '\n' | sed -n 's/^SIEVE200=//p'); T10=/content/ua_v10/goldbach/sieve200
OP="DEEP_GEN_ONEPASS=1"; OPL="DEEP_GEN_ONEPASS=1 DEEP_GEN_LB=512,3"
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none} | base tree $T3" > status.txt
run() {   # name tree extra-env
  D=$W/$1; mkdir -p $D
  ( export $E $3
    timeout 400 python3 /content/c3g/search_gpu5.py --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 --skip-frac $SKIPF \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 $2 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 158209 $DA > $D/driver.log 2>&1 ) &
  PID=$!; last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
run base $T3 ""; run op $T10 "$OP"; run opl $T10 "$OPL"; run base_b $T3 ""; run op_b $T10 "$OP"; run opl_b $T10 "$OPL"
python3 - <<'PY' > $W/choice.txt
import os
W = "/content/opgate"
def gaps(d):
    v = [tuple(map(float, l.split())) for l in open(f"{W}/{d}/stamps.txt")] if os.path.exists(f"{W}/{d}/stamps.txt") else []
    t = [x for n, x in v if n >= 1]; g = [y - x for x, y in zip(t, t[1:])][:-1]
    return sum(g) / len(g) if g else 9e9
a = (gaps("op") + gaps("op_b")) / 2; b = (gaps("opl") + gaps("opl_b")) / 2
print("opl" if b < a else "op")
PY
CH=$(cat $W/choice.txt); [ "$CH" = opl ] && KX="$OPL" || KX="$OP"
D=$W/kc; mkdir -p $D/camp $D/vec
python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$D/vec/vec_000000.json', 'w'))"
DK=$(echo "$DA" | sed -e 's/--klog [0-9]*//' -e 's/--slice [0-9]*//' -e 's/--pipeline-depth [0-9]*//' -e 's/--log-near-exp [0-9]*//' -e 's/--vector-place [a-z]*//')
( export $E $KX
  timeout 900 python3 /content/c3g/search_gpu5.py --campaign $D/camp --vector-dir $D/vec --vector-wait 3 --goldbach /content/c3g --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
    --no-stop --kernel 28 --sieve200 $T10 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 46171 $DK \
    --klog 19 --slice 524288 --pipeline-depth 1 --log-near-exp 1 > $D/camp/driver.log 2>&1 )
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none} | kc with $CH" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/opgate"
REF = [(2138520, 46327), (2179102, 53551), (2179987, 49741), (2189571, 46687), (2193647, 55381), (2222542, 56311), (2223210, 48259), (2249515, 47317),
       (2283416, 61441), (2288959, 57529), (2343716, 46441), (2431570, 51241), (2432966, 51607), (2438432, 48157), (2469450, 48799), (2470026, 59509),
       (2472121, 52009), (2516834, 51241), (2517629, 49171), (2518859, 48157), (2587266, 52579), (2599668, 48757), (2636003, 48817)]
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def sl(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def gaps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    t = [x for n, x in v if n >= 1]
    return [y - x for x, y in zip(t, t[1:])]
def errs(d):
    f = f"{W}/{d}/driver.log"
    return [l.strip()[:140] for l in (open(f).read().splitlines() if os.path.exists(f) else []) if "rror" in l or "Traceback" in l or "outside" in l or "static_assert" in l][:2]
print(open(f"{W}/status.txt").read().strip())
ref = sl("base"); ok = len(ref) == 24; m = {}
for d in ("base", "op", "opl", "base_b", "op_b", "opl_b"):
    g = gaps(d); st = g[:-1]; m[d] = sum(st) / len(st) if st else float("nan")
    same = bool(sl(d)) and sl(d) == ref and not errs(d); ok = ok and same
    print(f"{d:6s}: gaps {[round(x, 3) for x in g]} | mean of batches 2-5 {m[d]:.3f} s | slice lines vs base: {'IDENTICAL' if same else 'DIFFERENT'} ({len(sl(d))}) | {errs(d)}")
b = (m["base"] + m["base_b"]) / 2; o = (m["op"] + m["op_b"]) / 2; l = (m["opl"] + m["opl_b"]) / 2
print(f"op (ONEPASS) {o:.3f} s (x{o / b:.4f}) | opl (ONEPASS + LB 512,3) {l:.3f} s (x{l / b:.4f}) | base {b:.3f} s")
nm = sorted((int(x["k"]), int(x["g"])) for x in (json.loads(t[t.index("{"):]) for t in (open(f"{W}/kc/camp/found.jsonl") if os.path.exists(f"{W}/kc/camp/found.jsonl") else []) if t.strip()))
ch = open(f"{W}/choice.txt").read().strip()
print(f"known case with {ch}'s settings: {len(nm)} near-misses, identical to the CPU brute force's 23: {nm == REF}")
print("OP-CHOICE", ch, f"x{min(o, l) / b:.4f}")
print("OP-GATE", "PASSED" if ok and nm == REF and min(o, l) / b <= 0.99 else "FAILED")
print("OPGATE-DONE")
PY
