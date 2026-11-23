#!/bin/bash
# Re-tune after the fused rounds (uarch's list, 23 Nov 12:43Z): on this RTX PRO 6000, the production vector config (f = 0.985, 29-bit kernel, fused rounds, rcta 8 / gen 512,
# r32, no bubble, pipeline depth 4, batches of 4; all from next_campaign_env and deep_env_v89) on the same 24 test windows, each variant twice (two interleaved passes):
#   base | sync2 / sync4 / sync0: GBATCH_SYNC_EVERY=2 / 4 / 0 (the bin-overflow check after every 2nd / 4th group / only at the window's end) | dmax4 / dmax6: --dmax 4 / 6 |
#   tgt512k: --target 524288 | depth2 / depth3: --pipeline-depth 2 / 3.
# Slice lines of every run must be identical to the first base run's. A measurement: production is not changed. Campaign paused (SIGSTOP), resumed whatever happens.
W=/content/tune2; mkdir -p $W; cd $W; rm -rf r_* result.txt status.txt
VEC=/content/vplt_vec; mkdir -p $VEC; cp /content/vplt_vec_000000.json $VEC/vec_000000.json
E=$(cat /content/next_campaign_env); DA=$(cat /content/deep_env_v89); SKIPF=$(echo "$E" | tr ' ' '\n' | sed -n 's/^SKIPF=//p')
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
run() {   # name extra-env extra-args
  D=$W/$1; mkdir -p $D
  ( export $E $2
    timeout 400 python3 /content/c3g/search_gpu5.py --campaign $D --vector-dir $VEC --vector-wait 3 --goldbach /content/c3g --batch 4 --pool 2097152 --skip-frac $SKIPF \
      --p-est 0.055 --no-stop --kernel 28 --sieve200 $SIEVE200 --sieve-threads ${SIEVE_THREADS:-256} --k28-step $K28_STEP --k28-asm $K28_ASM --near-miss 157837 $DA $3 > $D/driver.log 2>&1 ) &
  PID=$!; last=0
  while kill -0 $PID 2>/dev/null; do
    n=$(cat $D/gpu3_stats.log 2>/dev/null | wc -l)
    if [ "$n" != "$last" ]; then echo "$n $(date +%s.%N)" >> $D/stamps.txt; last=$n; fi
    sleep 0.02
  done
  wait $PID; echo "rc=$?" >> $D/driver.log
}
for p in 1 2; do
  run r_base_$p "" ""
  run r_sync2_$p GBATCH_SYNC_EVERY=2 ""
  run r_sync4_$p GBATCH_SYNC_EVERY=4 ""
  run r_sync0_$p GBATCH_SYNC_EVERY=0 ""
  run r_dmax4_$p "" "--dmax 4"
  run r_dmax6_$p "" "--dmax 6"
  run r_tgt512k_$p "" "--target 524288"
  run r_depth2_$p "" "--pipeline-depth 2"
  run r_depth3_$p "" "--pipeline-depth 3"
done
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import os, re
W = "/content/tune2"
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
def waste(d):
    f = f"{W}/{d}/gpu3_stats.log"
    S = open(f).read().splitlines() if os.path.exists(f) else []
    w = [float(re.search(r"waste ([\d.]+)%", l).group(1)) for l in S if "waste" in l]
    return sum(w) / len(w) if w else float("nan")
ref = sl("r_base_1"); res = {}
for v in ("base", "sync2", "sync4", "sync0", "dmax4", "dmax6", "tgt512k", "depth2", "depth3"):
    ms = []; same = True; e = []
    for p in (1, 2):
        d = f"r_{v}_{p}"; g = gaps(d); st = g[:-1]
        ms.append(sum(st) / len(st) if st else float("nan")); same = same and bool(sl(d)) and sl(d) == ref; e += errs(d)
    res[v] = sum(ms) / 2
    print(f"{v:8s}: batch {ms[0]:.3f} / {ms[1]:.3f} s, mean {res[v]:.3f} | waste {waste(f'r_{v}_1'):.1f}% | slice lines vs base: {'IDENTICAL' if same else 'DIFFERENT'} | {e}")
b = res["base"]
print("against base:", ", ".join(f"{v} x{res[v] / b:.4f}" for v in res if v != "base"))
print("TUNE2-DONE")
PY
