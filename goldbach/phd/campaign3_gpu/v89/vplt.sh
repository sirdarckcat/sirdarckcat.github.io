#!/bin/bash
# Vector-mode tuning (GPU session, 23 Nov ~11:20Z): in the 89-moduli vector campaign the sieve thread is the bottleneck (busy the whole batch, the consumer waits
# 0.03-0.08 s a batch), so the a2 bubble (GBATCH_GROUP_DELAY_US=500 after each checked row group, tuned for the 88-moduli mode where the sieve had slack) and the
# row-group size (wcost2: rg 32 / 64 take 6.5-7 ms off a 2^24 window alone) are re-tried in vector mode. 24 test vectors (q170000_m89_t1_v8..v31, in no campaign),
# one 2^24 window each from k_lo, batches of 4 (6 batches a run), production vector flags otherwise. Slice lines must be identical to v0.
#   v0 / v0b: production (500 us, rg 16)   d0: 0 us   d250: 250 us   r32: 0 us rg 32   r64: 0 us rg 64   r64d500: 500 us rg 64   r64d1000: 1000 us rg 64
# Campaign paused (SIGSTOP) and resumed at the end, whatever happens. Output /content/vplt/result.txt.
W=/content/vplt; mkdir -p $W; cd $W; rm -rf v0 d0 d250 r32 r64 r64d500 r64d1000 v0b result.txt
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
DA="--deep 1 --klog 24 --slice 16777216 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 4 --trace-pipeline 1 --deep-tile-threads 512 --log-near-exp 1"
run() {   # name delay_us extra-args
  D=$W/$1; mkdir -p $D
  timeout 400 env $E GBATCH_GROUP_DELAY_US=$2 python3 /content/c3g/search_gpu5.py --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 \
    --skip-frac 0.97 --p-est 0.055 --no-stop --kernel 28 --sieve200 /content/ua_v3/goldbach/sieve200 --sieve-threads 256 --k28-step fermat28_step_s1r.cuh --k28-asm 1 \
    --near-miss 157837 $DA $3 > $D/driver.log 2>&1 &
  PID=$!
  last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
run v0 500 ""
run d0 0 ""
run d250 250 ""
run r32 0 "--deep-rg 32"
run r64 0 "--deep-rg 64"
run r64d500 500 "--deep-rg 64"
run r64d1000 1000 "--deep-rg 64"
run v0b 500 ""
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/vplt"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stamps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    return [t for n, t in v if n >= 1]
ref = lines("v0")
for d in ("v0", "d0", "d250", "r32", "r64", "r64d500", "r64d1000", "v0b"):
    t = stamps(d)
    g = [round(y - x, 3) for x, y in zip(t, t[1:])]
    beside = sum(g[:-1]) / len(g[:-1]) if len(g) > 1 else float("nan")
    v = lines(d)
    L = open(f"{W}/{d}/driver.log").read().splitlines() if os.path.exists(f"{W}/{d}/driver.log") else []
    err = [l.strip()[:160] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:3]
    pw = [re.search(r"waited ([\d.]+) s for the sieve; the sieve thread made (\d+) windows in ([\d.]+) s and waited ([\d.]+) s", l) for l in L if l.startswith("[pipeline]")]
    pw = [m for m in pw if m and m.group(2) == "4"]
    cw = sum(float(m.group(1)) for m in pw) / max(len(pw), 1); sb = sum(float(m.group(3)) for m in pw) / max(len(pw), 1); si = sum(float(m.group(4)) for m in pw) / max(len(pw), 1)
    print(f"{d:8s}: gaps {g} | mean of batches 2..5 {beside:.3f} s | consumer waited {cw:.3f} s, sieve busy {sb:.3f} s, idle {si:.3f} s a batch | slice lines vs v0: {'IDENTICAL' if v and v == ref else 'DIFFERENT'} ({len(v)}) | {err}")
print("VPLT-DONE")
PY
