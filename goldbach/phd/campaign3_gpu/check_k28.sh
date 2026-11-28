#!/bin/bash
# search_gpu3.py with kernel 3 and with kernel 28 on the same production-range slices (k just below 2^30, scanned by no
# campaign): the slice lines (tests, prp, p^, alive/k, E^, hit%, found) must be identical, at f = 0.97 and at f = 0.
cd /content/c3g
P=$(pgrep -f "search_gpu3[.]py --campaign" | head -n 1)
[ -n "$P" ] && kill -STOP $P
python3 - <<'PY'
import json
s = json.load(open("/content/c150/my_specs.json"))[:4]
mk = lambda k0s: [dict(v, name=f"{v['name']}@{k0}", kstart=k0, kmax=k0 + (1 << 20)) for k0 in k0s for v in s]
json.dump(mk(((1 << 30) - (1 << 20), (1 << 30) - (2 << 20))), open("k28_slices.json", "w"))
json.dump(mk(((1 << 30) - (3 << 20),)), open("k28_slices_f0.json", "w"))
PY
for K in 3 28; do
  python3 search_gpu3.py k28_slices.json --goldbach /content/c3g --out k28_found_$K.jsonl --skip-frac 0.97 --batch 8 --kernel $K > k28_out_$K.txt 2>&1
  python3 search_gpu3.py k28_slices_f0.json --goldbach /content/c3g --out k28_found0_$K.jsonl --skip-frac 0 --batch 4 --kernel $K > k28_out0_$K.txt 2>&1
done
[ -n "$P" ] && kill -CONT $P
python3 - <<'PY' > k28_check.txt 2>&1
import re
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
ok = True
for a_f, b_f in (("k28_out_3.txt", "k28_out_28.txt"), ("k28_out0_3.txt", "k28_out0_28.txt")):
    a = {m.group(1): m.group(4) for m in map(pat.match, open(a_f)) if m}
    b = {m.group(1): m.group(4) for m in map(pat.match, open(b_f)) if m}
    same = bool(a) and a == b; ok &= same
    print(a_f, "vs", b_f, ":", len(a), "slices,", "IDENTICAL" if same else "DIFFERENT")
    for k in sorted(a): print("  ", k, a[k][:110])
for f in ("k28_out_3.txt", "k28_out_28.txt", "k28_out0_3.txt", "k28_out0_28.txt"):
    print(f, [l.strip()[:200] for l in open(f) if l.startswith("#") or "Error" in l or "Traceback" in l])
print("K28 CHECK PASSED" if ok else "K28 CHECK FAILED")
PY
echo CHECKK28-DONE >> k28_check.txt
