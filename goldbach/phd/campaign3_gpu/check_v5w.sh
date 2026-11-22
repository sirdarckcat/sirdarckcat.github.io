#!/bin/bash
# search_gpu5.py with kernel 28 on another step file: the production configuration (/content/next_campaign_env) against the
# same with /content/k28w_env on top (KERNEL, K28_STEP, K28_ASM, FERMAT28_DIR), on 12 production-range slices (k just below
# 2^30, scanned by no campaign) at f = 0.97 and f = 0: the slice lines (tests, prp, p^, alive/k, E^, hit%, found) must be
# identical. The campaign is paused meanwhile. Result in /content/k28w_check/check.txt.
[ -f /content/f28w/gpu_fermat28.py ] || { mkdir -p /content/f28w && cd /content/f28w && tar -xzf /content/cuda28w.tgz; }
W=/content/k28w_check; mkdir -p $W; cd $W; rm -f f*.jsonl o*.txt check.txt
BASE=$(cat /content/next_campaign_env); NEW="$BASE $(cat /content/k28w_env)"
python3 - <<'PY'
import json
s = json.load(open("/content/c150/my_specs.json"))[:4]
mk = lambda k0s: [dict(v, name=f"{v['name']}@{k0}", kstart=k0, kmax=k0 + (1 << 20)) for k0 in k0s for v in s]
json.dump(mk(((1 << 30) - (1 << 20), (1 << 30) - (2 << 20))), open("s97.json", "w"))
json.dump(mk(((1 << 30) - (3 << 20),)), open("s0.json", "w"))
PY
P=$(pgrep -f "search_gpu[345][.]py --campaign" | head -n 1)
[ -n "$P" ] && kill -STOP $P
for T in base new; do
  E=$BASE; [ $T = new ] && E=$NEW
  for F in 97 0; do
    SF=0.97; B=8; [ $F = 0 ] && { SF=0; B=4; }
    env $E bash -c "python3 /content/c3g/search_gpu5.py s$F.json --goldbach /content/c3g --out f${F}_$T.jsonl --skip-frac $SF --batch $B"' --kernel ${KERNEL:-3} --sieve200 ${SIEVE200:-/content/gs/goldbach/sieve200} --sieve-threads ${SIEVE_THREADS:-256} --k28-step ${K28_STEP:-fermat28_step_s1.cuh} --k28-asm ${K28_ASM:-1}' > o${F}_$T.txt 2>&1
  done
done
[ -n "$P" ] && kill -CONT $P
python3 - "$BASE" "$NEW" <<'PY' > check.txt 2>&1
import re, sys
print("base:", sys.argv[1]); print("new: ", sys.argv[2])
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
ok = True
for F in ("97", "0"):
    a = {m.group(1): m.group(4) for m in map(pat.match, open(f"o{F}_base.txt")) if m}
    b = {m.group(1): m.group(4) for m in map(pat.match, open(f"o{F}_new.txt")) if m}
    same = len(a) == (8 if F == "97" else 4) and a == b; ok &= same
    print(f"f={'0.97' if F == '97' else '0'}: {len(a)} / {len(b)} slices,", "IDENTICAL" if same else "DIFFERENT")
    for k in sorted(set(a) | set(b)):
        print("   " if a.get(k) == b.get(k) else "   DIFF", k, "| base:", (a.get(k) or "")[:120], "" if a.get(k) == b.get(k) else f"| new: {b.get(k)}")
    for T in ("base", "new"):
        print("  ", T, [l.strip()[:200] for l in open(f"o{F}_{T}.txt") if l.startswith("#") or "rror" in l or "Traceback" in l][:6])
print("CHECKW PASSED" if ok else "CHECKW FAILED")
PY
echo CHECKW-DONE >> check.txt
