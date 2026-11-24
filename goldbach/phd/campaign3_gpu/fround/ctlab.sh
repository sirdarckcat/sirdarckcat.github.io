#!/bin/bash
# uarch's control stream for the fused rounds (27db8d0: the rounds' small launches on a stream above the sieve, only the Fermat kernel on the pool's own stream) on this RTX PRO 6000,
# production vector config, the 24 test windows, every run under its own timeout (CUDA event ordering is not CPU-verifiable: a mistake would hang or change lines):
#   pA / pB / pC with --profile-pool 1: production | + FERMAT_CTL_PRIORITY=-100 OVERLAP_SIEVE_PRIORITY=-4 | + OVERLAP_SIEVE_PRIORITY=-4 alone (the gap a half-pool: the falsifier);
#   then A / B / A_b / B_b without profiling (batch times). Slice lines of every run identical to pA's. A separate Fermat dir /content/f29fr2 (f29fr + 27db8d0's fround.py);
#   driver search_gpu5_ctl.py (production's + search_gpu5_ctlprio.patch). A measurement: production is not changed. Campaign paused (SIGSTOP), resumed whatever happens.
W=/content/ctlab; mkdir -p $W; cd $W; rm -rf p* A* B* result.txt status.txt
[ -d /content/f29fr2 ] || cp -a /content/f29fr /content/f29fr2
tar -xzf /content/fr2_overlay.tgz -C /content/f29fr2
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89); SKIPF=$(echo "$E" | tr ' ' '\n' | sed -n 's/^SKIPF=//p')
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
run() {   # name driver fermat-dir extra-env extra-args
  D=$W/$1; mkdir -p $D
  ( export $E $4; export FERMAT28_DIR=$3
    timeout 300 python3 /content/c3g/$2 --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 --skip-frac $SKIPF \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 158209 $DA $5 > $D/driver.log 2>&1 ) &
  PID=$!; last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
CTL="FERMAT_CTL_PRIORITY=-100 OVERLAP_SIEVE_PRIORITY=-4"
run pA search_gpu5.py /content/f29fr "" "--profile-pool 1"
run pB search_gpu5_ctl.py /content/f29fr2 "$CTL" "--profile-pool 1"
run pC search_gpu5_ctl.py /content/f29fr2 "OVERLAP_SIEVE_PRIORITY=-4" "--profile-pool 1"
run A search_gpu5.py /content/f29fr "" ""
run B search_gpu5_ctl.py /content/f29fr2 "$CTL" ""
run A_b search_gpu5.py /content/f29fr "" ""
run B_b search_gpu5_ctl.py /content/f29fr2 "$CTL" ""
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/ctlab"
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def sl(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
def gaps(d):
    f = f"{W}/{d}/stamps.txt"
    v = [tuple(map(float, l.split())) for l in open(f)] if os.path.exists(f) else []
    t = [x for n, x in v if n >= 1]
    return [y - x for x, y in zip(t, t[1:])]
def drv(d):
    f = f"{W}/{d}/driver.log"
    return open(f).read().splitlines() if os.path.exists(f) else []
ref = sl("pA")
for d in ("pA", "pB", "pC", "A", "B", "A_b", "B_b"):
    L = drv(d); g = gaps(d); st = g[:-1]; m = sum(st) / len(st) if st else float("nan")
    pg = [float(re.search(r"gap ([\d.]+) s", l).group(1)) for l in L if "[profile-pool]" in l and "gap" in l and "members" in l]
    rc = [l for l in L if l.startswith("rc=")]
    err = [l.strip()[:120] for l in L if "rror" in l or "Traceback" in l][:2]
    same = bool(sl(d)) and sl(d) == ref
    print(f"{d:4s}: batch {m:.3f} s | profile gap a half-pool: mean {sum(pg) / len(pg) if pg else float('nan'):.3f} s over {len(pg)} | slice lines vs pA: {'IDENTICAL' if same else 'DIFFERENT'} ({len(sl(d))}) | {rc} {err}")
PY
echo CTLAB-DONE >> result.txt
