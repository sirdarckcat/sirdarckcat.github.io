#!/bin/bash
# uarch's generate-kernel latencies and reductions (a606d5b: DEEP_GEN_SCAN2 / RESV_LATE / MINRED, "LEAN") and the pipelined tile kernel (b4e60df: DEEP_TILE_PIPE=1 AT=64, which replaces
# the prefetch) on top of production, in the driver on this RTX PRO 6000, under the standing rule: tree /content/ua_v9 (ua_v3 with f58ff97's whole sieve200/cuda; defaults unchanged):
#   base (production: ua_v7 and this card's DEEP_* options) | v9 (ua_v9, the same options) | phu: + LEAN | phup: + LEAN + TILE_PIPE AT=64, PF off, then base_b / phu_b / phup_b;
#   slice lines identical to base's; then the vector known case with phu's settings. deploy_lean.py deploys the faster of phu / phup if all of it holds and it is >= 1% faster
#   than base. Campaign paused (SIGSTOP), resumed whatever happens.
W=/content/leanab; mkdir -p $W; cd $W; rm -rf base* v5* phu* kc result.txt status.txt
[ -d /content/ua_v9 ] || cp -a /content/ua_v3 /content/ua_v9
tar -xzf /content/ua9_cuda.tgz -C /content/ua_v9/goldbach/sieve200/cuda
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89); SKIPF=$(echo "$E" | tr ' ' '\n' | sed -n 's/^SKIPF=//p')
SIEVE200_PROD=$(echo "$E" | tr ' ' '\n' | sed -n 's/^SIEVE200=//p')
PHU="DEEP_GEN_SCAN2=1 DEEP_GEN_RESV_LATE=1 DEEP_GEN_MINRED=1"; PHUP="DEEP_GEN_SCAN2=1 DEEP_GEN_RESV_LATE=1 DEEP_GEN_MINRED=1 DEEP_TILE_PIPE=1 DEEP_TILE_PIPE_AT=64 DEEP_TILE_PREFETCH=0"
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
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
T3=$SIEVE200_PROD; T5=/content/ua_v9/goldbach/sieve200
run base $T3 ""; run v5 $T5 ""; run phu $T5 "$PHU"; run phup $T5 "$PHUP"; run base_b $T3 ""; run phu_b $T5 "$PHU"; run phup_b $T5 "$PHUP"
D=$W/kc; mkdir -p $D/camp $D/vec
python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$D/vec/vec_000000.json', 'w'))"
( export $E $PHU
  timeout 900 python3 /content/c3g/search_gpu5.py --campaign $D/camp --vector-dir $D/vec --vector-wait 3 --goldbach /content/c3g --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
    --no-stop --kernel 28 --sieve200 $T5 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 46171 --log-near-exp 1 \
    --deep 1 --klog 19 --slice 524288 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 1 --deep-tile-threads 512 \
    --deep-gen-threads 512 --fused-rounds 1 --target 524288 > $D/camp/driver.log 2>&1 )
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/leanab"
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
    return [l.strip()[:140] for l in (open(f).read().splitlines() if os.path.exists(f) else []) if "rror" in l or "Traceback" in l or "outside" in l][:2]
ref = sl("base"); ok = len(ref) == 24; m = {}
for d in ("base", "v5", "phu", "phup", "base_b", "phu_b", "phup_b"):
    g = gaps(d); st = g[:-1]; m[d] = sum(st) / len(st) if st else float("nan")
    same = bool(sl(d)) and sl(d) == ref and not errs(d); ok = ok and same
    print(f"{d:6s}: gaps {[round(x, 3) for x in g]} | mean of batches 2-5 {m[d]:.3f} s | slice lines vs base: {'IDENTICAL' if same else 'DIFFERENT'} ({len(sl(d))}) | {errs(d)}")
b = (m["base"] + m["base_b"]) / 2; u = (m["phu"] + m["phu_b"]) / 2; p = (m["phup"] + m["phup_b"]) / 2
print(f"phu (LEAN) {u:.3f} s (x{u / b:.4f}) | phup (LEAN + TILE_PIPE AT=64) {p:.3f} s (x{p / b:.4f}) | base {b:.3f} s | v9 with production's options {m['v5']:.3f} s")
nm = sorted((int(x["k"]), int(x["g"])) for x in (json.loads(l[l.index("{"):]) for l in (open(f"{W}/kc/camp/found.jsonl") if os.path.exists(f"{W}/kc/camp/found.jsonl") else []) if l.strip()))
print(f"known case with phu's settings (production + LEAN): {len(nm)} near-misses, identical to the CPU brute force's 23: {nm == REF}")
best = "phup" if p <= u else "phu"
print("LEAN-CHOICE", best, f"x{min(u, p) / b:.4f}")
print("LEAN-GATE", "PASSED" if ok and nm == REF and min(u, p) / b <= 0.99 else "FAILED")
print("LEANAB-DONE")
PY
