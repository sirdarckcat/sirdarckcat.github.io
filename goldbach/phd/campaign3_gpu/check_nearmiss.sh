#!/bin/bash
# Near-miss reporting, known case: the 146,191 record's member (r200_q140k_c_v77, k = 3,101,585,871) under its vector's
# Q = 150,000 residual list must be reported as a near-miss at g = 146,191; reporting on or off must give identical slice lines.
W=/content/nmcheck; mkdir -p $W; cd $W; rm -f o_*.txt f_*.jsonl result.txt
cp /content/nm_s20.json s20.json; cp /content/nm_s25.json s25.json
python3 - <<'PY'
import json
s = json.load(open("/content/c150/my_specs.json"))[:2]
k0 = (1 << 30) - (1 << 25)
json.dump([dict(v, name=f"{v['name']}@{k0}", kstart=k0, kmax=k0 + (1 << 25)) for v in s], open("p25.json", "w"))
PY
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign" | head -n 1); [ -n "$P" ] && kill -STOP $P
K='--kernel ${KERNEL:-28} --k28-step ${K28_STEP:-fermat28_step_s1r.cuh} --k28-asm ${K28_ASM:-1}'
D="--deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1200 --sieve200 /content/ua57/goldbach/sieve200"
run() { env $E bash -c "python3 /content/c3g/search_gpu5_nm.py $1 --goldbach /content/c3g --out f_$2.jsonl --batch 2 --pool 2097152 $3 $K" > o_$2.txt 2>&1; }
run s20.json a "--skip-frac 0 --p-est 0.055 --sieve-b 1000000 --sieve200 /content/ua57/goldbach/sieve200 --sieve-threads 1024 --near-miss 140000"
run s20.json b "--skip-frac 0 --p-est 0.055 --sieve-b 1000000 --sieve200 /content/ua57/goldbach/sieve200 --sieve-threads 1024"
run s25.json c "--skip-frac 0.97 $D --near-miss 140000"
grep -q "SUCCESS-NEARMISS" o_c.txt || run s25.json c9 "--skip-frac 0.9 $D --near-miss 140000"
run p25.json d1 "--skip-frac 0.97 $D --near-miss 100000"
run p25.json d0 "--skip-frac 0.97 $D"
[ -n "$P" ] && kill -CONT $P
python3 - <<'PY' > result.txt 2>&1
import re, json, os
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
sl = lambda f: {m.group(1): m.group(4) for m in map(pat.match, open(f)) if m}
for f in ("o_a.txt", "o_b.txt", "o_c.txt", "o_c9.txt", "o_d1.txt", "o_d0.txt"):
    if os.path.exists(f):
        L = open(f).read().splitlines()
        print(f, "|", " || ".join(l.strip()[:200] for l in L if "NEARMISS" in l or "SUCCESS" in l or "Traceback" in l or "Error" in l or l.startswith("[")) [:900])
for f in ("f_a.jsonl", "f_c.jsonl", "f_c9.jsonl", "f_d1.jsonl"):
    if os.path.exists(f):
        print(f, [ (r["name"], r["k"], r["g"], r.get("near_miss"), r.get("Q")) for r in map(json.loads, filter(str.strip, open(f))) ])
ok_a = any(r["k"] == 3101585871 and r["g"] == 146191 and r.get("near_miss") for r in map(json.loads, filter(str.strip, open("f_a.jsonl")))) if os.path.exists("f_a.jsonl") else False
ok_ab = sl("o_a.txt") == sl("o_b.txt") and bool(sl("o_a.txt"))
cf = "f_c9.jsonl" if os.path.exists("f_c9.jsonl") else "f_c.jsonl"
ok_c = any(r["k"] == 3101585871 and r["g"] == 146191 for r in map(json.loads, filter(str.strip, open(cf)))) if os.path.exists(cf) else False
ok_d = sl("o_d1.txt") == sl("o_d0.txt") and bool(sl("o_d1.txt"))
print("a) normal path, all members, near-miss >= 140,000: 146,191's member reported:", ok_a)
print("b) normal path, slice lines with and without near-miss reporting identical:", ok_ab)
print("c) deep path: 146,191's member reported (" + cf + "):", ok_c)
print("d) deep production slices, slice lines with and without near-miss reporting identical:", ok_d)
print("NMCHECK", "PASSED" if ok_a and ok_ab and ok_c and ok_d else "FAILED")
PY
echo NMCHECK-DONE >> result.txt
