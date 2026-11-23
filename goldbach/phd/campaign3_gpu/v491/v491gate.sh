#!/bin/bash
# research's 491-family 89-moduli vectors (bbc8cd8: the first 88 odd primes and 491; 463 becomes a sieve prime) on this RTX PRO 6000, with production's settings (next_campaign_env,
# deep_env_v89: one-pass, top placement, f = 0.985). Campaign paused (SIGSTOP) for the GPU runs, resumed whatever happens:
#   n97 / n90: the normal path (B = 10^6, block 32768) on the top 2^19 of the known-case vector (q170000_m89r491_t491a_v0), f = 0.97 / 0.9: slice lines for search_c.py's (c97 / c90);
#   kc: the known case, production's deep path, --vector-place top --klog 19, f = 0, near-misses >= 48,661 (row 400): its list for cpu_brute_k0.py's (run on the session's container);
#   pm_old / pm_new: the top 2^24 window of the same vector at f = 0, near-misses >= 48,661, before one-pass (next_campaign_env_pre_onepass) and now: per-member identity (fast path);
#   ck_base / ck_prod: check491.py (check89.py at the top of a 491 vector): the deep sieve against sieve200's CPU feeder (base kernels, then production's DEEP_* options) and the
#     production Fermat kernel's flags against gmpy2;
#   r463p / r491w / r463p_b / r491w_b: what production would consume, 24 vectors from this card's newest 463 chunk against 24 walk-level 491 vectors (1,248 rows), production
#     settings: batch time, expected near-misses >= 158,209 and design hits a batch (the lead's test: hits/s >= +3%, near-misses not below -3%);
#   r463v / r491s (reference, once): the fixed 24 test vectors (research's best 463 covers, 1,248 rows) and 24 start-level 491 vectors (1,247 rows).
W=/content/v491; rm -rf $W; mkdir -p $W/vkc $W/v491s $W/v491w $W/v463v $W/v463p; cd $W
cp /content/kc491_spec.json $W/vkc/vec_000000.json; cp /content/v491_24.json $W/v491s/vec_000000.json; cp /content/v491_24w.json $W/v491w/vec_000000.json
cp /content/vplt_vec_000000.json $W/v463v/vec_000000.json
python3 -c "import json, glob; f = sorted(glob.glob('/content/vec89/vec_*.json'))[-1]; s = json.load(open(f))[:24]; json.dump(s, open('$W/v463p/vec_000000.json', 'w')); print('production 463 arm from', f, s[0]['name'])"
python3 - <<'PY'
import json
from gmpy2 import mpz
s = json.load(open("/content/kc491_spec.json"))[0]
N0, M = mpz(s["N0"]), mpz(s["M"]); kend = min(int(s["kmax"]), int((mpz(10) ** 200 - N0 + M - 1) // M)); ks = kend - (1 << 19)
json.dump([dict(s, name=f"{s['name']}@{ks}", kstart=ks, kmax=kend)], open("/content/v491/slice19.json", "w"))
print(f"known-case vector {s['name']}: top 2^19 = [{ks}, {kend})")
PY
E=$(cat /content/next_campaign_env); EO=$(cat /content/next_campaign_env_pre_onepass); DA=$(cat /content/deep_env_v89); SKIPF=$(echo "$E" | tr ' ' '\n' | sed -n 's/^SKIPF=//p')
DK=$(echo "$DA" | sed -e 's/--klog [0-9]*//' -e 's/--slice [0-9]*//' -e 's/--pipeline-depth [0-9]*//' -e 's/--log-near-exp [0-9]*//')
G=/content/c3g
( cd /content/ua_v10/goldbach/sieve200/cuda && export FERMAT28_DIR=$(echo "$E" | tr " " "\n" | sed -n "s/^FERMAT28_DIR=//p") K28_STEP=$(echo "$E" | tr " " "\n" | sed -n "s/^K28_STEP=//p") K28_ASM=$(echo "$E" | tr " " "\n" | sed -n "s/^K28_ASM=//p") && timeout 900 python3 /content/check491.py /content/kc491_spec.json ) > $W/ck_base.txt 2>&1
( cd /content/ua_v10/goldbach/sieve200/cuda && export $E && timeout 900 python3 /content/check491.py /content/kc491_spec.json ) > $W/ck_prod.txt 2>&1
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
for f in 97 90; do
  D=$W/n$f; mkdir -p $D
  ( export $E
    timeout 600 python3 $G/search_gpu5.py --campaign $D --vector-dir $W/vkc --vector-wait 3 --vector-place top --klog 19 --goldbach $G --batch 1 --pool 2097152 --skip-frac 0.$f --p-est 0.055 \
      --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --sieve-b 1000000 --block 32768 --fused-rounds 1 > $D/driver.log 2>&1 ); echo "rc=$?" >> $D/driver.log
done
D=$W/kc; mkdir -p $D
( export $E
  timeout 900 python3 $G/search_gpu5.py --campaign $D --vector-dir $W/vkc --vector-wait 3 --goldbach $G --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
    --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 48661 $DK \
    --klog 19 --slice 524288 --pipeline-depth 1 --log-near-exp 1 > $D/driver.log 2>&1 ); echo "rc=$?" >> $D/driver.log
pm() {   # name env
  D=$W/$1; mkdir -p $D
  ( export $2
    timeout 900 python3 $G/search_gpu5.py --campaign $D --vector-dir $W/vkc --vector-wait 3 --goldbach $G --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
      --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 48661 $(echo "$DA" | sed -e 's/--pipeline-depth [0-9]*//') --pipeline-depth 1 > $D/driver.log 2>&1 ); echo "rc=$?" >> $D/driver.log
}
pm pm_old "$EO"; pm pm_new "$E"
run() {   # name vecdir
  D=$W/$1; mkdir -p $D
  ( export $E
    timeout 400 python3 $G/search_gpu5.py --campaign $D --vector-dir $2 --vector-wait 3 --goldbach $G --batch 4 --pool 2097152 --skip-frac $SKIPF \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 158209 $DA > $D/driver.log 2>&1 ) &
  PID=$!; last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
run r463p $W/v463p; run r491w $W/v491w; run r463p_b $W/v463p; run r491w_b $W/v491w; run r463v $W/v463v; run r491s $W/v491s
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
CG=/content/c150cpu/goldbach
for f in 97 90; do
  D=$W/c$f; mkdir -p $D
  timeout 3000 nice -n 5 python3 $CG/sieve200/search_c.py $W/slice19.json --procs 8 --block 32768 --sieve-b 1000000 --skip-frac 0.$f --p-est 0.055 --out $D/found.jsonl > $D/out.txt 2>&1
  echo "rc=$?" >> $D/out.txt
done
echo "$(date -u +%FT%TZ) CPU slices done" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/v491"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def rd(f):
    return open(f).read().splitlines() if os.path.exists(f) else []
def sl(f):
    return {m.group(1): (m.group(2), m.group(3), m.group(4)) for m in map(pat.match, rd(f)) if m}
def nms(d):
    return sorted((int(x["k"]), int(x["g"])) for x in (json.loads(t[t.index("{"):]) for t in rd(f"{W}/{d}/found.jsonl") if t.strip()))
def errs(f):
    return [l.strip()[:150] for l in rd(f) if "rror" in l or "Traceback" in l or "ssert" in l][:2]
print(open(f"{W}/status.txt").read().strip())
ok = True
for f in ("97", "90"):
    g, c = sl(f"{W}/n{f}/search.log"), sl(f"{W}/c{f}/out.txt"); same = bool(g) and g == c and not errs(f"{W}/n{f}/driver.log"); ok = ok and same
    print(f"normal path, top 2^19, f = 0.{f}: GPU {g} | CPU {c} | {'IDENTICAL' if same else 'DIFFERENT'} | {errs(W + '/n' + f + '/driver.log')}")
kc = nms("kc"); print(f"known case (production deep path, f = 0, >= 48,661): {len(kc)} near-misses | {sl(W + '/kc/search.log')} | {errs(W + '/kc/driver.log')}")
for k, q in kc:
    print(f"GPU k={k} q={q}")
a, b = nms("pm_old"), nms("pm_new"); same = bool(a) and a == b and sl(f"{W}/pm_old/search.log") == sl(f"{W}/pm_new/search.log"); ok = ok and same
print(f"top 2^24 window, f = 0, >= 48,661: before one-pass {len(a)}, now {len(b)}, per-member identical {same} | {sl(W + '/pm_new/search.log')} | {errs(W + '/pm_old/driver.log')} {errs(W + '/pm_new/driver.log')}")
print("PM-KC-INSIDE", sorted(x for x in b if x[0] >= int(json.load(open(f"{W}/slice19.json"))[0]["kstart"])))
def gaps(d):
    v = [tuple(map(float, l.split())) for l in rd(f"{W}/{d}/stamps.txt")]
    t = [x for n, x in v if n >= 1]
    return [y - x for x, y in zip(t, t[1:])]
def ex(d):
    L = rd(f"{W}/{d}/gpu3_stats.log")
    near = sum(float(m.group(1)) for m in (re.search(r"expected near>=\d+ ([\d.e+-]+)", l) for l in L) if m)
    hits = sum(float(m.group(1)) for m in (re.search(r"expected hits ([\d.e+-]+)", l) for l in L) if m)
    return near, hits, len(L)
for f in ("ck_base", "ck_prod"):
    print(f, "|", " || ".join(l.strip()[:170] for l in rd(f"{W}/{f}.txt") if l.strip().startswith(("(1)", "(2)", "CHECK491", "q170000", "Traceback")) or "rror" in l)[:900])
ok = ok and all("CHECK491 OK" in open(f"{W}/{f}.txt").read() for f in ("ck_base", "ck_prod"))
m = {}
for d in ("r463p", "r491w", "r463p_b", "r491w_b", "r463v", "r491s"):
    g = gaps(d); st = g[:-1]; m[d] = sum(st) / len(st) if st else float("nan"); n, h, nb = ex(d)
    print(f"{d:6s}: batch {m[d]:.3f} s | expected near>=158209 {n:.4e}, hits {h:.4e} over {nb} batches | {len(sl(W + '/' + d + '/search.log'))} slices | {errs(W + '/' + d + '/driver.log')}")
n4, h4 = [sum(ex(d)[i] for d in ("r463p", "r463p_b")) for i in (0, 1)]; n9, h9 = [sum(ex(d)[i] for d in ("r491w", "r491w_b")) for i in (0, 1)]
b4 = (m["r463p"] + m["r463p_b"]) / 2; b9 = (m["r491w"] + m["r491w_b"]) / 2
hs, ns = h9 / h4 * b4 / b9, n9 / n4 * b4 / b9
print(f"491 walk-level / 463 production supply (24 vectors each): batch x{b9 / b4:.4f} | a second: design hits x{hs:.4f}, near-misses x{ns:.4f}")
nv, hv = ex("r463v")[:2]; n5, h5 = ex("r491s")[:2]
print(f"reference: 491 start-level / 463 fixed test set: design hits a vector x{h5 / hv:.4f}, near-misses x{n5 / nv:.4f}; 463 fixed set / 463 production supply: hits x{hv / (h4 / 2):.4f}, near x{nv / (n4 / 2):.4f}")
print("RATE-TEST", "PASSED" if hs >= 1.03 and ns >= 0.97 else "FAILED", f"(hits/s x{hs:.4f} >= 1.03, near-misses x{ns:.4f} >= 0.97)")
print("V491-GPU", "PASSED" if ok else "FAILED", "(normal path + fast path; the known case is compared with the CPU brute force separately)")
print("V491-DONE")
PY
