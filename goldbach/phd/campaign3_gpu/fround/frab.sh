#!/bin/bash
# Fused Fermat rounds (uarch 4639f17, --fused-rounds 1) on this RTX PRO 6000 at the production keep fraction f = 0.985 (vector mode, 29-bit kernel, r32, pipeline depth 4,
# batches of 4): the same 24 test windows, alternating fr0 (production driver) / fr1 (search_gpu5_fr.py --fused-rounds 1) / fr0b / fr1b; slice lines of every run
# must be identical to fr0's. Then p0 / p1: the fr driver with --profile-pool 1 and --fused-rounds 0 / 1 (the [profile-pool] lines: the gap a round).
# A separate Fermat dir /content/f29fr (a copy of /content/f29 with fround.py and fround_kernels.cuh). Campaign paused (SIGSTOP), resumed whatever happens.
W=/content/frab; mkdir -p $W; cd $W; rm -rf fr0* fr1* p0 p1 result.txt status.txt
[ -d /content/f29fr ] || cp -a /content/f29 /content/f29fr
tar -xzf /content/fr_overlay.tgz -C /content/f29fr
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89 | sed -e 's/ --deep-head-b [0-9]*//' -e 's/ --deep-head-rows [0-9]*//')
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
run() {   # name driver fermat-dir extra-args
  D=$W/$1; mkdir -p $D
  ( export $E; export FERMAT28_DIR=$3
    timeout 400 python3 /content/c3g/$2 --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 --skip-frac 0.985 \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 /content/ua_v3/goldbach/sieve200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step fermat29_step_s1.cuh --k28-asm 1 \
      --near-miss 157837 $DA $4 > $D/driver.log 2>&1 ) &
  PID=$!; last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
run fr0 search_gpu5.py /content/f29 ""
run fr1 search_gpu5_fr.py /content/f29fr "--fused-rounds 1"
run fr0b search_gpu5.py /content/f29 ""
run fr1b search_gpu5_fr.py /content/f29fr "--fused-rounds 1"
run p0 search_gpu5_fr.py /content/f29fr "--fused-rounds 0 --profile-pool 1"
run p1 search_gpu5_fr.py /content/f29fr "--fused-rounds 1 --profile-pool 1"
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/frab"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def sl(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def gaps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    t = [x for n, x in v if n >= 1]
    return [y - x for x, y in zip(t, t[1:])]
def lines(d, key):
    f = f"{W}/{d}/driver.log"
    return [l.strip()[:300] for l in (open(f).read().splitlines() if os.path.exists(f) else []) if key in l]
ref = sl("fr0"); m = {}
for d in ("fr0", "fr1", "fr0b", "fr1b", "p0", "p1"):
    g = gaps(d); st = g[:-1]; m[d] = sum(st) / len(st) if st else float("nan")
    err = [l for l in lines(d, "rror") + lines(d, "Traceback") + lines(d, "outside")][:2]
    print(f"{d:4s}: gaps {[round(x, 3) for x in g]} | mean of batches 2-5 {m[d]:.3f} s | slice lines vs fr0: {'IDENTICAL' if sl(d) and sl(d) == ref else 'DIFFERENT'} ({len(sl(d))}) | {err}")
b = (m["fr0"] + m["fr0b"]) / 2; f = (m["fr1"] + m["fr1b"]) / 2
print(f"fused rounds against production at f = 0.985: {f:.3f} s against {b:.3f} s a batch (x{f / b:.4f})")
for d in ("p0", "p1"):
    L = lines(d, "profile-pool")
    print(f"{d} profile lines: {len(L)}; last 3:"); [print("   ", l) for l in L[-3:]]
print("FRAB-DONE")
PY
