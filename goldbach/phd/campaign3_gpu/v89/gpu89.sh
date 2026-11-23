#!/bin/bash
# 89-moduli validation on this RTX PRO 6000 (campaign paused by SIGSTOP and resumed at the end, whatever happens):
#  (1) check89.py: the deep sieve against sieve200's CPU feeder at k_lo (the first 200-digit k), the kernel-28 flags against gmpy2 at the new k range;
#  (2) the new driver (search_gpu5_v89.py) on the 88-moduli test (6 Q = 170,000 vectors x 2 windows of 2^25, campaign mode, production flags + --log-near-exp 1):
#      slice lines against the production driver (search_gpu5.py), same flags;
#  (3) the known case: the new driver in vector mode on one 89-moduli vector (q170000_m89_t1_v0), one window of 2^19 from k_lo, --skip-frac 0 (every member
#      tested), --near-miss 46171: every member whose first PRP row is >= 46171 goes to found.jsonl (CPU-verified), for the comparison with the CPU brute force.
W=/content/g89; mkdir -p $W; cd $W; rm -rf base new kc result.txt check89.txt
T=46171
E=$(cat /content/next_campaign_env)
P=$(pgrep -f "search_gpu[345][.]py --campaign /content/c" | head -n 1)
resume() { [ -n "$P" ] && kill -CONT $P 2>/dev/null; }
trap resume EXIT
[ -n "$P" ] && kill -STOP $P
echo "$(date -u +%FT%TZ) paused pid ${P:-none}" > status.txt
( cd /content/ua_v3/goldbach/sieve200/cuda && FERMAT28_DIR=/content/f28w timeout 900 python3 /content/check89.py /content/m89_8.json ) > check89.txt 2>&1
echo "$(date -u +%FT%TZ) check89 done" >> status.txt
python3 - <<'PY'
import json
s = json.load(open("/content/probe/s25.json"))
out = []
for v in s:
    v = dict(v); v["name"] = v["name"].split("@")[0]; v.pop("kstart", None); v.pop("kmax", None); out.append(v)
json.dump(out, open("/content/g89/my_specs.json", "w"))
PY
DA="--deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 2 --trace-pipeline 1 --deep-tile-threads 512"
run88() {  # name driver extra
  D=$W/$1; mkdir -p $D; cp $W/my_specs.json $D/
  timeout 400 env $E python3 /content/c3g/$2 --campaign $D --goldbach /content/c3g --batch 2 --pool 2097152 --skip-frac 0.97 --p-est 0.055 \
    --kmax 1073741824 --klo 1006632960 --desc --no-stop --kernel 28 --sieve200 /content/ua_v3/goldbach/sieve200 --sieve-threads 256 --k28-step fermat28_step_s1r.cuh --k28-asm 1 \
    --near-miss 157837 $DA $3 > $D/driver.log 2>&1; echo "rc=$?" >> $D/driver.log
}
run88 base search_gpu5.py ""
run88 new search_gpu5_v89.py "--log-near-exp 1"
echo "$(date -u +%FT%TZ) 88-moduli runs done" >> status.txt
D=$W/kc; mkdir -p $D/camp $D/vec
python3 -c "import json; s=json.load(open('/content/m89_8.json')); json.dump(s[:1], open('$D/vec/vec_000000.json', 'w'))"
timeout 900 env $E python3 /content/c3g/search_gpu5_v89.py --campaign $D/camp --vector-dir $D/vec --vector-wait 5 --goldbach /content/c3g --batch 1 --pool 2097152 --skip-frac 0 --p-est 0.055 \
    --no-stop --kernel 28 --sieve200 /content/ua_v3/goldbach/sieve200 --sieve-threads 256 --k28-step fermat28_step_s1r.cuh --k28-asm 1 --near-miss $T --log-near-exp 1 \
    --deep 1 --klog 19 --slice 524288 --sieve-b 100000000 --p-est 0.0715 --deep-max-rows 1300 --pool-threads 2 --pipeline 1 --pipeline-depth 1 --deep-tile-threads 512 > $D/camp/driver.log 2>&1
echo "rc=$?" >> $D/camp/driver.log
echo "$(date -u +%FT%TZ) known case done" >> status.txt
resume; trap - EXIT
echo "$(date -u +%FT%TZ) resumed pid ${P:-none}" >> status.txt
python3 - <<'PY' > result.txt 2>&1
import json, os, re
W = "/content/g89"
print(open(f"{W}/check89.txt").read().strip())
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
def lines(d):
    f = f"{W}/{d}/search.log"
    return {m.group(1): m.group(4) for m in map(pat.match, open(f).read().splitlines() if os.path.exists(f) else []) if m}
a, b = lines("base"), lines("new")
print(f"(2) 88-moduli: slice lines of the new driver {'IDENTICAL' if a and a == b else 'DIFFERENT'} to the production driver ({len(a)} / {len(b)} slices)")
for d in ("base", "new"):
    st = open(f"{W}/{d}/gpu3_stats.log").read().splitlines() if os.path.exists(f"{W}/{d}/gpu3_stats.log") else []
    print(f"    {d}: {st[-1][-260:] if st else '(no stats)'}")
    L = open(f"{W}/{d}/driver.log").read().splitlines()
    print("     ", [l.strip()[:150] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=")][:3])
K = f"{W}/kc/camp"
L = open(f"{K}/driver.log").read().splitlines() if os.path.exists(f"{K}/driver.log") else []
print("(3) known case driver:", [l.strip()[:200] for l in L if "rror" in l or "Traceback" in l or l.startswith("rc=") or "C3GPU" in l][:4])
print("    slice:", open(f"{K}/search.log").read().strip().splitlines()[-1][:300] if os.path.exists(f"{K}/search.log") else "(none)")
print("    stats:", open(f"{K}/gpu3_stats.log").read().strip()[-300:] if os.path.exists(f"{K}/gpu3_stats.log") else "(none)")
nm = []
for l in (open(f"{K}/found.jsonl") if os.path.exists(f"{K}/found.jsonl") else []):
    l = l.strip()
    if l:
        r = json.loads(l[l.index("{"):])
        nm.append((int(r["k"]), int(r["g"]), bool(r.get("near_miss"))))
print(f"    GPU near-misses (first PRP row >= T): {len(nm)}")
for k, g, f in sorted(nm):
    print(f"GPU k={k} q={g} near_miss={f}")
print("G89-DONE")
PY
