#!/bin/bash
# Deep head (uarch 0e45ea8: the primes in (1e8, 1e9] on the first 64 rows, after the selection) on this RTX PRO 6000: steps 1-2 of DEEPSIEVE.md's GPU list,
# under the lead's gate (first-PRP rows, successes and near-misses identical to production on the same windows; logged expected values within ~1%).
# Campaign paused (SIGSTOP) and resumed at the end, whatever happens. Production's tree (/content/ua_v3) and driver are not touched.
#   tree /content/ua_v4 = a copy of /content/ua_v3 with 0e45ea8's sieve200/cuda over it; driver /content/c3g/search_gpu5_head.py = the deployed search_gpu5.py (k29)
#   + search_gpu5_head.patch.
#   1. headcheck.py /content/m89_8.json --rg 32 --rcta 8: HEADCHECK-OK and the head's ms a window (break-even ~26 ms).
#   2. The 24 test vectors (one 2^24 window each from k_lo), the production vector config (29-bit kernel, r32, pipeline depth 4, batches of 4), three runs:
#      prod: production driver and tree; base: head driver, ua_v4, no head, --dump-members; head: the same with --deep-head-b 1e9 --deep-head-rows 64.
#      prod and base must have identical slice lines (the new code is inert without the head); compare_dumps base head: DUMPS-IDENTICAL (sid / k / first-PRP row /
#      success of every member) with ~8.4% fewer tests; the expected hits and near-misses >= 157,837 logged per batch: head within ~1% of base.
W=/content/headv; mkdir -p $W; cd $W; rm -rf prod base head hc.txt cmp.txt result.txt status.txt
[ -d /content/ua_v4 ] || cp -a /content/ua_v3 /content/ua_v4
tar -xzf /content/head_overlay.tgz -C /content/ua_v4/goldbach/sieve200/cuda
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
( cd /content/ua_v4/goldbach/sieve200/cuda && export $E && timeout 900 python3 headcheck.py /content/m89_8.json --rg 32 --rcta 8 ) > hc.txt 2>&1
echo "$(date -u +%FT%TZ) headcheck done" >> status.txt
run() {   # name driver tree extra-args
  D=$W/$1; mkdir -p $D
  ( export $E
    timeout 900 python3 /content/c3g/$2 --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 --skip-frac 0.97 \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 $3 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 157837 $DA $4 > $D/driver.log 2>&1 ) &
  PID=$!; last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
run prod search_gpu5.py /content/ua_v3/goldbach/sieve200 ""
run base search_gpu5_head.py /content/ua_v4/goldbach/sieve200 "--dump-members $W/base/dump"
run head search_gpu5_head.py /content/ua_v4/goldbach/sieve200 "--dump-members $W/head/dump --deep-head-b 1000000000 --deep-head-rows 64"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 /content/ua_v4/goldbach/sieve200/cuda/compare_dumps.py $W/base/dump $W/head/dump > cmp.txt 2>&1; echo "compare_dumps rc=$?" >> cmp.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/headv"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def sl(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stats(d):
    f = f"{W}/{d}/gpu3_stats.log"
    S = open(f).read().splitlines() if os.path.exists(f) else []
    near = sum(float(re.search(r"expected near>=\d+ ([\d.e+-]+)", l).group(1)) for l in S if "expected near>=" in l)
    hits = sum(float(re.search(r"expected hits ([\d.e+-]+)", l).group(1)) for l in S if "expected hits" in l)
    tests = sum(int(re.search(r"tests (\d+) counted", l).group(1)) for l in S if "counted" in l)
    return len(S), near, hits, tests
def gaps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    t = [x for n, x in v if n >= 1]
    return [round(y - x, 3) for x, y in zip(t, t[1:])]
def errs(d):
    f = f"{W}/{d}/driver.log"
    L = open(f).read().splitlines() if os.path.exists(f) else []
    return [l.strip()[:200] for l in L if "rror" in l or "Traceback" in l or "outside" in l or l.startswith("rc=") or "C3GPU" in l or "head" in l.lower()][:6]
for d in ("prod", "base", "head"):
    n, near, hits, tests = stats(d); g = gaps(d)
    print(f"{d:4s}: batches {n} | expected near>=157837 {near:.4e} | expected hits {hits:.4e} | tests {tests:,} | gaps {g} | {errs(d)}")
a, b = sl("prod"), sl("base")
print("prod / base slice lines:", "IDENTICAL" if a and a == b else "DIFFERENT", f"({len(a)} / {len(b)})")
nb, near_b, hits_b, tests_b = stats("base"); nh, near_h, hits_h, tests_h = stats("head")
if near_b and hits_b and tests_b:
    print(f"head / base: expected near x{near_h / near_b:.4f}, expected hits x{hits_h / hits_b:.4f}, tests x{tests_h / tests_b:.4f}")
print(open(f"{W}/cmp.txt").read().strip())
print(open(f"{W}/hc.txt").read().strip()[-3000:])
print("HEADV-DONE")
PY
