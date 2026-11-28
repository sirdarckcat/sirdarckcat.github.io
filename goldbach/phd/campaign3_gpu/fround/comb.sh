#!/bin/bash
# Fused Fermat rounds (uarch 4639f17, --fused-rounds 1) together with DEEP_RCTA=8 and --deep-gen-threads 512 on this RTX PRO 6000 at the production vector config (f = 0.985,
# 29-bit kernel, r32, pipeline depth 4, batches of 4), under the lead's standing rule for engine changes: the same 24 test windows, base (production) / comb / base_b /
# comb_b, slice lines identical; then the vector known case with comb's settings (q170000_m89_t1_v0, one 2^19 window from k_lo, f = 0, near-misses >= 46,171): the
# same 23 (k, q) as the CPU brute force. Campaign paused (SIGSTOP), resumed whatever happens; deploy_comb.py deploys only if all of it holds and comb is faster.
W=/content/comb; mkdir -p $W; cd $W; rm -rf base* comb* kc result.txt status.txt
[ -f /content/f29fr/fround.py ] || { [ -d /content/f29fr ] || cp -a /content/f29 /content/f29fr; tar -xzf /content/fr_overlay.tgz -C /content/f29fr; }
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
run() {   # name driver fermat-dir extra-env extra-args
  D=$W/$1; mkdir -p $D
  ( export $E $4; export FERMAT28_DIR=$3
    timeout 400 python3 /content/c3g/$2 --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 --skip-frac 0.985 \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 157837 $DA $5 > $D/driver.log 2>&1 ) &
  PID=$!; last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
run base search_gpu5.py /content/f29 "" ""
run comb search_gpu5_fr.py /content/f29fr DEEP_RCTA=8 "--fused-rounds 1 --deep-gen-threads 512"
run base_b search_gpu5.py /content/f29 "" ""
run comb_b search_gpu5_fr.py /content/f29fr DEEP_RCTA=8 "--fused-rounds 1 --deep-gen-threads 512"
D=$W/kc; mkdir -p $D/camp $D/vec
python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$D/vec/vec_000000.json', 'w'))"
( export $E DEEP_RCTA=8; export FERMAT28_DIR=/content/f29fr
  timeout 900 python3 /content/c3g/search_gpu5_fr.py --campaign $D/camp --vector-dir $D/vec --vector-wait 3 --goldbach /content/c3g --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
    --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 46171 --log-near-exp 1 \
    --deep 1 --klog 19 --slice 524288 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 1 --deep-tile-threads 512 \
    --deep-gen-threads 512 --fused-rounds 1 > $D/camp/driver.log 2>&1 )
echo "rc=$?" >> $D/camp/driver.log
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/comb"
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
    return [l.strip()[:160] for l in (open(f).read().splitlines() if os.path.exists(f) else []) if "rror" in l or "Traceback" in l or "outside" in l][:2]
ref = sl("base"); m = {}; ident = 0
for d in ("base", "comb", "base_b", "comb_b"):
    g = gaps(d); st = g[:-1]; m[d] = sum(st) / len(st) if st else float("nan")
    same = bool(sl(d)) and sl(d) == ref and len(ref) == 24 and not errs(d); ident += same
    print(f"{d:6s}: gaps {[round(x, 3) for x in g]} | mean of batches 2-5 {m[d]:.3f} s | slice lines vs base: {'IDENTICAL' if same else 'DIFFERENT'} ({len(sl(d))}) | {errs(d)}")
b = (m["base"] + m["base_b"]) / 2; c = (m["comb"] + m["comb_b"]) / 2
print(f"comb against base at f = 0.985: {c:.3f} s against {b:.3f} s a batch (x{c / b:.4f})")
K = f"{W}/kc/camp"
nm = sorted((int(x["k"]), int(x["g"])) for x in (json.loads(l[l.index("{"):]) for l in (open(f"{K}/found.jsonl") if os.path.exists(f"{K}/found.jsonl") else []) if l.strip()))
print(f"known case (fused rounds, DEEP_RCTA=8, gen 512): {len(nm)} near-misses >= 46171, identical to the CPU brute force's 23: {nm == REF} | {errs('kc/camp')}")
print("COMB-GATE", "PASSED" if ident == 4 and nm == REF and c / b <= 0.99 else "FAILED")
print("COMB-DONE")
PY
