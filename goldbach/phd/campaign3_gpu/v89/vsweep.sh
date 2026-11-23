#!/bin/bash
# Keep fraction in vector mode (89 moduli) on this RTX PRO 6000, the production vector config (29-bit kernel, r32, batches of 4, pipeline depth 4): the same
# 24 test vectors (one 2^24 window each from k_lo) at f = 0.96 ... 0.99, and f = 0.97 again last (drift control). Per f: the batch time (batches 2-5; batch 1
# is not timed, batch 6 is the tail), and from gpu3_stats.log the expected near-misses >= 157,837 and the expected design hits of the tested members, per batch.
# Ranked by expected near >= record per second. Last, r8: f = 0.97 with DEEP_RCTA=8 and --deep-gen-threads 512 (uarch wcost3: -5.3 ms a 2^24 window of
# sieve alone), whose slice lines must be identical to f_0.97's. A measurement only: production is not changed. Campaign paused (SIGSTOP), resumed whatever happens.
W=/content/vsweep; mkdir -p $W; cd $W; rm -rf f_* result.txt
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
DA=$(cat /content/deep_env_v89)
run() {   # name f [extra env] [extra args]
  D=$W/$1; mkdir -p $D
  ( export $E $3
    timeout 400 python3 /content/c3g/search_gpu5.py --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 --skip-frac $2 \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 157837 $DA $4 > $D/driver.log 2>&1 ) &
  PID=$!; last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
for f in 0.96 0.965 0.97 0.975 0.98 0.985 0.99; do run f_$f $f; done
run f_0.97b 0.97
run r8_0.97 0.97 DEEP_RCTA=8 "--deep-gen-threads 512"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/vsweep"
rows = []
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def sl(n):
    f = f"{W}/{n}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
for name in ("f_0.96", "f_0.965", "f_0.97", "f_0.975", "f_0.98", "f_0.985", "f_0.99", "f_0.97b", "r8_0.97"):
    D = f"{W}/{name}"
    v = [tuple(map(float, l.split())) for l in open(f"{D}/stamps.txt")] if os.path.exists(f"{D}/stamps.txt") else []
    t = [x for n, x in v if n >= 1]; g = [y - x for x, y in zip(t, t[1:])]
    steady = g[:-1]; bt = sum(steady) / len(steady) if steady else float("nan")
    S = open(f"{D}/gpu3_stats.log").read().splitlines() if os.path.exists(f"{D}/gpu3_stats.log") else []
    near = [float(re.search(r"expected near>=\d+ ([\d.e+-]+)", l).group(1)) for l in S if "expected near>=" in l]
    hits = [float(re.search(r"expected hits ([\d.e+-]+)", l).group(1)) for l in S if "expected hits" in l]
    tests = [int(re.search(r"tests (\d+) counted", l).group(1)) for l in S if "counted" in l]
    L = open(f"{D}/driver.log").read().splitlines() if os.path.exists(f"{D}/driver.log") else []
    err = [l.strip()[:120] for l in L if "rror" in l or "Traceback" in l or "outside" in l][:2]
    nb = len(near)
    nps = (sum(near) / nb) / bt if nb and bt == bt else float("nan")
    hps = (sum(hits) / nb) / bt if nb and bt == bt else float("nan")
    rows.append((name, bt, nb, sum(near) / max(nb, 1), sum(hits) / max(nb, 1), sum(tests) / max(nb, 1), nps, hps, [round(x, 3) for x in g], err))
base = [r for r in rows if r[0] == "f_0.97"][0]
print(f"{'f':8s} {'batch s':>8s} {'batches':>7s} {'near/batch':>11s} {'hits/batch':>11s} {'tests/batch':>12s} {'near/s':>11s} {'x f0.97':>8s} {'hits/s':>11s} {'x f0.97':>8s}  gaps | errors")
for r in rows:
    print(f"{r[0]:8s} {r[1]:8.3f} {r[2]:7d} {r[3]:11.4e} {r[4]:11.4e} {r[5]:12.0f} {r[6]:11.4e} {r[6] / base[6]:8.4f} {r[7]:11.4e} {r[7] / base[7]:8.4f}  {r[8]} | {r[9]}")
print("r8 (DEEP_RCTA=8, --deep-gen-threads 512, f = 0.97): slice lines vs f_0.97:", "IDENTICAL" if sl("r8_0.97") and sl("r8_0.97") == sl("f_0.97") else "DIFFERENT",
      "| f_0.97b vs f_0.97:", "IDENTICAL" if sl("f_0.97b") and sl("f_0.97b") == sl("f_0.97") else "DIFFERENT")
print("VSWEEP-DONE")
PY
