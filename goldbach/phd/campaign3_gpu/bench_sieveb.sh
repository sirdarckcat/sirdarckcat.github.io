#!/bin/bash
# search_gpu5.py at several sieve bounds B on the same 64 production-range slices (4 variants x 16 k-rows just below 2^30, under
# every campaign's KLO), production configuration otherwise (/content/next_campaign_env). Each batch line logs the batch time,
# tests and the model's expected hits (sum over tested members of (1 - p^)^count, p^ measured at that B), so expected hits per
# second compare directly across B on the same members. The campaign is paused meanwhile.
W=/content/sieveb; mkdir -p $W; cd $W; rm -f o_*.txt f_*.jsonl result.txt
python3 - <<'PY'
import json
s = json.load(open("/content/c150/my_specs.json"))[-4:]
json.dump([dict(v, name=f"{v['name']}@{k0}", kstart=k0, kmax=k0 + (1 << 20)) for k0 in [(1 << 30) - ((4 + j) << 20) for j in range(16)] for v in s], open("s64.json", "w"))
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign" | head -n 1)
[ -n "$P" ] && kill -STOP $P
for B in ${BLIST:-1000000 2000000 4000000 10000000 20000000}; do
  for rep in 1 2; do
    env $E bash -c "python3 /content/c3g/search_gpu5.py s64.json --goldbach /content/c3g --out f_$B.jsonl --skip-frac 0.97 --batch 64 --pool 2097152 --sieve-b $B"' --kernel ${KERNEL:-3} --sieve200 ${SIEVE200:-/content/gs/goldbach/sieve200} --sieve-threads ${SIEVE_THREADS:-256} --k28-step ${K28_STEP:-fermat28_step_s1.cuh} --k28-asm ${K28_ASM:-1}' > o_${B}_$rep.txt 2>&1
  done
done
[ -n "$P" ] && kill -CONT $P
python3 - <<'PY' > result.txt 2>&1
import glob, re
base = None
for B in sorted({int(f.split("_")[1]) for f in glob.glob("o_*_2.txt")}):
    L = open(f"o_{B}_2.txt").read()
    m = re.search(r"\(64 slices\) ([\d.]+)s: tests (\d+) counted, (\d+) computed.*?expected hits ([\d.e+-]+)", L)
    sl = re.findall(r"alive/k=(\S+) E\^=(\S+) hit%=(\S+)", L)
    if not m:
        print(B, "NO BATCH LINE", [l[:200] for l in L.splitlines() if "rror" in l or "Trace" in l][:3]); continue
    t, tc, tp, e = float(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4))
    t1 = re.search(r"\(64 slices\) ([\d.]+)s", open(f"o_{B}_1.txt").read())
    if base is None: base = (t, e)
    print(f"B={B:.0e}: batch {t:.2f}s (first run {t1.group(1) if t1 else '?'}s), tests {tc/1e6:.2f}M counted {tp/1e6:.2f}M computed, expected hits {e:.4e}, "
          f"alive/k {sum(float(a) for a, _, _ in sl)/len(sl):.1f}, E^ {sum(float(b) for _, b, _ in sl)/len(sl):.2f} | "
          f"expected x{e/base[1]:.3f}, time x{t/base[0]:.3f}, expected/s x{(e/t)/(base[1]/base[0]):.3f}")
print("SIEVEB-DONE")
PY
