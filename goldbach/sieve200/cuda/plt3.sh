#!/bin/bash
# Tuning of the sieve beside the Fermat rounds on an RTX PRO 6000 (uarch session, 23 Nov 2026 ~09:15Z): an adaptation of the GPU session's plt2.sh (same harness: campaign mode, 6 Q = 170,000 vectors x
# 2 windows of 2^25 = 6 batches of 2 windows, batch ends stamped every 20 ms, GPU memory sampled, the campaign paused and resumed, slice lines compared with run `base`).
#
# What the 08:37Z runs showed (pipeline depth 2, --pool-threads 2): the sieve with a blocking host check after EVERY row group (GBATCH_SYNC_EVERY=1, the old behaviour) trickles at x2.2 beside the
# Fermat rounds and is hidden: batches of 1.55-1.60 s against 1.744 s; with no check inside the window (GBATCH_SYNC_EVERY=0, a flat-out sieve on the highest-priority stream) the sieve takes the SMs
# at full speed, the Fermat rounds wait, and the batch is 1.73-1.76 s.  So the SIZE OF THE SIEVE'S BURSTS is what matters.  Probes of 08:04Z (one big Fermat launch): the sieve slows the Fermat kernel
# by x1.10 and gets x2.89 (work rate x1.25); in the driver it is x1.36 / x2.2 (x1.17): the Fermat rounds lose more.  This script tries, in the pipeline configuration of production:
#   j0    baseline (GBATCH_SYNC_EVERY unset = 1: a check after every group)
#   d1 d2 a bubble after every checked group: GBATCH_GROUP_DELAY_US = 1000 / 2500 (the sieve stream idles that long: a gentler sieve; it has ~0.5 s a batch to spare)
#   s2 s4 a host check only after every 2nd / 4th group (longer bursts)
#   r4 r8 row groups of 4 / 8 rows (--deep-rg: 316 / 158 checks a window: shorter bursts)
#   tt128 tt512  tile-kernel CTAs of 128 / 512 threads (--deep-tile-threads: NO EFFECT before a752ea3+1: BatchFeeder ignored tile_threads; 256 is all that was ever run)
#   fA fB fC     the sieve in the registers the Fermat CTAs leave free: DEEP_TILE_MAXREG=32 + 128-thread tile and gen CTAs (4,096 registers each = what 5 resident Fermat CTAs of 92 registers x 128 threads
#                leave on a 65,536-register SM), so a sieve CTA never displaces a Fermat CTA.  fA: sieve stream at the default priority, Fermat streams at the highest (FERMAT_STREAM_PRIORITY=high needs
#                --pool-threads 2), no checks (flat out: the sieve cannot take slots from the Fermat CTAs); fB: the same shape, sieve stream high priority as production, check after every group;
#                fC: as fA with a check after every group
#   dm6   --dmax 6 (rows a member per round: waste 3.1% at 8)
# Needs: /content/ua_v3.tgz = the sieve200/cuda + fermat661/cuda sources of the uarch branch at the commit named in the message, over a copy of /content/ua_v2 (as for a752ea3);
#        /content/c3g/search_gpu5_xb3.py = the deployed driver (d5e5f14 / e15ecc3) with goldbach/sieve200/cuda/search_gpu5_prio.patch applied (patch -p1 from the repo root).
# Output: /content/plt3/result.txt (one line a run: gaps, the mean of the batches that have a sieve beside them = all but the last, slice lines vs base, peak memory, the [pipeline] counters).
W=/content/plt3; mkdir -p $W; cd $W; rm -rf base j0 d1 d2 s2 s4 r4 r8 tt128 tt512 fA fB fC dm6 j1 result.txt
T=/content/ua_v3; [ -d $T ] || cp -a /content/ua_v2 $T; tar -xzf /content/ua_v3.tgz -C $T || { echo TAR-FAILED > result.txt; exit 1; }
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/plt3/my_specs.json", "w"))
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
run() {   # name driver tree extra-env extra-args
  D=$W/$1; mkdir -p $D; cp $W/my_specs.json $D/
  timeout 400 env $E DEEP_STAGED=1 $4 python3 /content/c3g/$2 --campaign $D --goldbach /content/c3g --batch 2 --pool 2097152 --skip-frac 0.97 --p-est 0.055 \
    --kmax 1073741824 --klo 1006632960 --desc --no-stop --kernel 28 --sieve200 $3/goldbach/sieve200 --sieve-threads 256 --k28-step fermat28_step_s1r.cuh --k28-asm 1 \
    --near-miss 157837 --deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 $5 > $D/driver.log 2>&1 &
  PID=$!
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 500 > $D/mem.txt 2>/dev/null &
  MP=$!
  last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
  kill $MP 2>/dev/null
}
PL="--pipeline 1 --pipeline-depth 2 --trace-pipeline 1 --pool-threads 2"
X=search_gpu5_xb3.py
FIT="--deep-tile-threads 128 --deep-gen-threads 128"
run base  search_gpu5.py $T "" "--pool-threads 2"                    # production without the pipeline (reference for the slice lines)
run j0    $X $T "" "$PL"
run d1    $X $T "GBATCH_GROUP_DELAY_US=1000" "$PL"
run d2    $X $T "GBATCH_GROUP_DELAY_US=2500" "$PL"
run s2    $X $T "GBATCH_SYNC_EVERY=2" "$PL"
run s4    $X $T "GBATCH_SYNC_EVERY=4" "$PL"
run r4    $X $T "" "$PL --deep-rg 4"
run r8    $X $T "" "$PL --deep-rg 8"
run tt128 $X $T "" "$PL --deep-tile-threads 128"
run tt512 $X $T "" "$PL --deep-tile-threads 512"
run fA    $X $T "DEEP_TILE_MAXREG=32 OVERLAP_SIEVE_PRIORITY=0 FERMAT_STREAM_PRIORITY=high GBATCH_SYNC_EVERY=0" "$PL $FIT"
run fB    $X $T "DEEP_TILE_MAXREG=32" "$PL $FIT"
run fC    $X $T "DEEP_TILE_MAXREG=32 OVERLAP_SIEVE_PRIORITY=0 FERMAT_STREAM_PRIORITY=high" "$PL $FIT"
run dm6   $X $T "" "$PL --dmax 6"
run j1    $X $T "" "$PL"                                           # the baseline again (noise)
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/plt3"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def stamps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    return [t for n, t in v if n >= 1]
def mem(d):
    f = f"{W}/{d}/mem.txt"
    v = [int(x) for x in open(f).read().split() if x.isdigit()] if os.path.exists(f) else []
    return max(v) if v else None
ref = lines("base")
for d in ("base", "j0", "d1", "d2", "s2", "s4", "r4", "r8", "tt128", "tt512", "fA", "fB", "fC", "dm6", "j1"):
    t = stamps(d)
    g = [round(y - x, 3) for x, y in zip(t, t[1:])]
    beside = sum(g[:-1]) / len(g[:-1]) if len(g) > 1 else float("nan")
    v = lines(d)
    L = open(f"{W}/{d}/driver.log").read().splitlines() if os.path.exists(f"{W}/{d}/driver.log") else []
    err = [l.strip()[:160] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:3]
    print(f"{d:6s}: gaps {g} | batches with a sieve beside them: mean {beside:.3f} s | slice lines vs base: {'IDENTICAL' if v and v == ref else 'DIFFERENT'} ({len(v)}) | peak GPU memory {mem(d)} MiB | {err}")
    for l in L:
        m = re.search(r"\[pipeline\] batch \S+: the consumer waited ([\d.]+) s for the sieve; the sieve thread made (\d+) windows in ([\d.]+) s and waited ([\d.]+) s", l)
        if m and m.group(2) != "0" and float(m.group(1)) < 1.0:
            print(f"         [pipeline] waited {m.group(1)} s; sieve {m.group(2)} windows busy {m.group(3)} s, idle {m.group(4)} s")
print("PLT3-DONE")
PY
