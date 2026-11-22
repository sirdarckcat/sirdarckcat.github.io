#!/bin/bash
# search_gpu4.py (CPU feeder + GPU tests) against search_gpu3.py on the slices of check_k28.sh: identical slice lines.
cd /content && tar -xzf /content/sieve200.tgz
cd /content/c3g
P=$(pgrep -f "search_gpu3[.]py --campaign" | head -n 1)
[ -n "$P" ] && kill -STOP $P
python3 search_gpu4.py k28_slices.json --goldbach /content/c3g --out k4_found.jsonl --skip-frac 0.97 --batch 8 --kernel 28 --threads 46 > k4_out.txt 2>&1
python3 search_gpu4.py k28_slices_f0.json --goldbach /content/c3g --out k4_found0.jsonl --skip-frac 0 --batch 4 --kernel 28 --threads 46 > k4_out0.txt 2>&1
[ -n "$P" ] && kill -CONT $P
python3 - <<'PY' > k4_check.txt 2>&1
import re
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=.*)$")
ok = True
for a_f, b_f in (("k28_out_28.txt", "k4_out.txt"), ("k28_out0_28.txt", "k4_out0.txt")):
    a = {m.group(1): m.group(4) for m in map(pat.match, open(a_f)) if m}
    b = {m.group(1): m.group(4) for m in map(pat.match, open(b_f)) if m}
    same = bool(a) and a == b; ok &= same
    print(a_f, "(v3) vs", b_f, "(v4):", len(a), len(b), "slices,", "IDENTICAL" if same else "DIFFERENT")
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k): print("   DIFF", k, "| v3:", a.get(k), "| v4:", b.get(k))
for f in ("k4_out.txt", "k4_out0.txt"):
    print(f, [l.strip()[:220] for l in open(f) if l.startswith("#") or "Error" in l or "Traceback" in l or "error" in l][:5])
print("V4 CHECK PASSED" if ok else "V4 CHECK FAILED")
PY
echo CHECKV4-DONE >> k4_check.txt
