#!/usr/bin/env python3
"""A record directory for a hit of a g >= Q scan: N, its digits, g(N), the cover, and two checks.

    python3 make_record.py found.jsonl spec.json outdir [index]

found.jsonl: search.py's output (one JSON line per hit: k, N, digits, g); spec.json: the scan's spec (N0, M, Q, cover,
residual).  Writes outdir/N.txt (the decimal N), record.json (name, N, digits, g, k, N0, M, Q, cover, residual), then runs
../verify_record.py (record.json -> evidence.json: a compositeness reason for N - q for every prime q < g, g prime, N - g
BPSW) and ../fscan/check.py on N alone (check.log: g(N) recomputed from N by testing N - q for every prime q < g), and
writes MANIFEST.sha256."""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GB = os.path.dirname(HERE)
found, specf, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
idx = int(sys.argv[4]) if len(sys.argv) > 4 else 0
hit = [json.loads(l) for l in open(found) if l.strip()][idx]
spec = json.load(open(specf))
if isinstance(spec, list):
    spec = next(s for s in spec if s.get("kstart", 0) <= hit["k"] < s.get("kmax", 1 << 62))
N0, M, k = int(spec["N0"]), int(spec["M"]), int(hit["k"])
N = N0 + k * M
assert str(N) == hit["N"] and len(str(N)) == hit["digits"] and N % 2 == 0
assert all(N % r == a for r, a in spec["cover"])
os.makedirs(outdir, exist_ok=True)
open(os.path.join(outdir, "N.txt"), "w").write(str(N) + "\n")
rec = {"name": spec["name"], "N": str(N), "digits": len(str(N)), "g": hit["g"], "k": k, "N0": str(N0), "M": str(M),
       "Q": spec["Q"], "cover": spec["cover"], "residual": spec["residual"]}
json.dump(rec, open(os.path.join(outdir, "record.json"), "w"))
r1 = subprocess.run([sys.executable, os.path.join(GB, "verify_record.py"), os.path.join(outdir, "record.json"),
                     os.path.join(outdir, "evidence.json")], capture_output=True, text=True)
open(os.path.join(outdir, "verify_record.log"), "w").write(r1.stdout + r1.stderr)
r2 = subprocess.run([sys.executable, os.path.join(GB, "fscan", "check.py"), str(N)], capture_output=True, text=True)
open(os.path.join(outdir, "check.log"), "w").write(r2.stdout + r2.stderr)
with open(os.path.join(outdir, "MANIFEST.sha256"), "w") as mf:
    for fn in sorted(os.listdir(outdir)):
        if fn != "MANIFEST.sha256":
            mf.write(hashlib.sha256(open(os.path.join(outdir, fn), "rb").read()).hexdigest() + "  " + fn + "\n")
print(f"{outdir}: N has {len(str(N))} digits, g = {hit['g']}; verify_record exit {r1.returncode}, check.py exit {r2.returncode}")
print((r1.stdout + r1.stderr).strip()[-600:])
print((r2.stdout + r2.stderr).strip()[-400:])
