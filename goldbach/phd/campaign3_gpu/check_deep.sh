#!/bin/bash
# On this GPU, with the campaign paused, on 2 variants x 2^25 members just below 2^30 (no campaign scans k < 2^30):
#  p6: production driver and sieve tree (/content/c3g/search_gpu5.py, $SIEVE200 of the campaign env), 64 slices of 2^20
#  n6: the patched driver with the new sieve tree (/content/ua57: Shoup sieve, 1024 sieve threads), same 64 slices   -> slice lines identical to p6
#  d6: the patched driver, --deep 1 at B = 10^6, the same members as 2 slices of 2^25                               -> tests and PRPs identical to n6
#  d8: --deep 1 at B = 10^8, the same 2 slices                                                                       -> tests ~x0.75, expected hits ~x1.4
W=/content/deepcheck; mkdir -p $W; cd $W; rm -f o_*.txt f_*.jsonl result.txt
cp /content/search_gpu5_deep.py /content/c3g/search_gpu5_deep.py
python3 - <<'PY'
import json
s = json.load(open("/content/c150/my_specs.json"))[:2]
k0 = (1 << 30) - (1 << 25)
json.dump([dict(v, name=f"{v['name']}@{k}", kstart=k, kmax=k + (1 << 20)) for k in range(k0, k0 + (1 << 25), 1 << 20) for v in s], open("s20.json", "w"))
json.dump([dict(v, name=f"{v['name']}@{k0}", kstart=k0, kmax=k0 + (1 << 25)) for v in s], open("s25.json", "w"))
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign" | head -n 1); [ -n "$P" ] && kill -STOP $P
K='--kernel ${KERNEL:-3} --k28-step ${K28_STEP:-fermat28_step_s1.cuh} --k28-asm ${K28_ASM:-1}'
env $E bash -c "python3 /content/c3g/search_gpu5.py s20.json --goldbach /content/c3g --out f_p6.jsonl --skip-frac 0.97 --p-est 0.055 --batch 64 --pool 2097152 --sieve-b 1000000"' --sieve200 ${SIEVE200:-/content/gs/goldbach/sieve200} --sieve-threads ${SIEVE_THREADS:-256} '"$K" > o_p6.txt 2>&1
env $E bash -c "python3 /content/c3g/search_gpu5_deep.py s20.json --goldbach /content/c3g --out f_n6.jsonl --skip-frac 0.97 --p-est 0.055 --batch 64 --pool 2097152 --sieve-b 1000000 --sieve200 /content/ua57/goldbach/sieve200 --sieve-threads 1024 $K" > o_n6.txt 2>&1
env $E bash -c "python3 /content/c3g/search_gpu5_deep.py s25.json --goldbach /content/c3g --out f_d6.jsonl --skip-frac 0.97 --p-est 0.055 --deep 1 --klog 25 --slice 33554432 --batch 2 --pool 2097152 --sieve-b 1000000 --sieve200 /content/ua57/goldbach/sieve200 $K" > o_d6.txt 2>&1
env $E bash -c "python3 /content/c3g/search_gpu5_deep.py s25.json --goldbach /content/c3g --out f_d8.jsonl --skip-frac 0.97 --p-est 0.0715 --deep 1 --klog 25 --slice 33554432 --batch 2 --pool 2097152 --sieve-b 100000000 --sieve200 /content/ua57/goldbach/sieve200 $K" > o_d8.txt 2>&1
[ -n "$P" ] && kill -CONT $P
python3 - <<'PY' > result.txt 2>&1
import re, collections
pat = re.compile(r"^\[(\S+)@(\d+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=(\d+) prp=(\d+) p\^=(\S+) alive/k=(\S+) E\^=(\S+) hit%=(\S+) found=(\d+))")
bat = re.compile(r"batch .*\((\d+) slices\) ([\d.]+)s: tests (\d+) counted, (\d+) computed.*?expected hits ([\d.e+-]+)")
def load(f):
    L = open(f).read().splitlines()
    sl = {}; agg = collections.defaultdict(lambda: [0, 0, 0.0, 0]); bt = []
    for l in L:
        m = pat.match(l)
        if m:
            nm, k0, a, b = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
            sl[f"{nm}@{k0}"] = m.group(5)
            g = agg[nm]; g[0] += int(m.group(6)); g[1] += int(m.group(7)); g[2] += float(m.group(9)) * (b - a); g[3] += b - a
        m = bat.search(l)
        if m: bt.append((int(m.group(1)), float(m.group(2)), int(m.group(3)), int(m.group(4)), float(m.group(5))))
    errs = [l[:200] for l in L if "Traceback" in l or "Error" in l]
    return sl, dict(agg), bt, errs
R = {k: load(f"o_{k}.txt") for k in ("p6", "n6", "d6", "d8")}
for k, (sl, agg, bt, errs) in R.items():
    print(f"{k}: {len(sl)} slices, batches {[(n, t, e) for n, t, _, _, e in bt]}, errors {errs[:3]}")
    for nm, g in agg.items(): print(f"   {nm}: tests {g[0]:,} prps {g[1]:,} alive/k {g[2]/max(g[3],1):.2f} members {g[3]:,}")
ok1 = R["p6"][0] and R["p6"][0] == R["n6"][0]
print("1) sieve v2 vs production sieve, slice lines:", "IDENTICAL" if ok1 else "DIFFERENT")
ok2 = R["n6"][1] and all(R["n6"][1][nm][:2] == R["d6"][1].get(nm, [None, None])[:2] for nm in R["n6"][1])
print("2) --deep at B = 1e6 vs normal, tests and PRPs per variant:", "IDENTICAL" if ok2 else "DIFFERENT")
if R["d8"][2] and R["n6"][2]:
    e8 = sum(b[4] for b in R["d8"][2]); e6 = sum(b[4] for b in R["n6"][2]); t8 = sum(b[2] for b in R["d8"][2]); t6 = sum(b[2] for b in R["n6"][2])
    s8 = sum(b[1] for b in R["d8"][2]); s6 = sum(b[1] for b in R["n6"][2]); sd6 = sum(b[1] for b in R["d6"][2])
    print(f"3) B = 1e8 deep vs B = 1e6: expected hits x{e8/e6:.3f}, tests x{t8/t6:.3f}, batch time {s8:.2f}s vs {s6:.2f}s (deep at 1e6: {sd6:.2f}s)")
print("DEEPCHECK", "PASSED" if ok1 and ok2 else "FAILED")
PY
echo DEEPCHECK-DONE >> result.txt
