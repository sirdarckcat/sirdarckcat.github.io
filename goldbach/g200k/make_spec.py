#!/usr/bin/env python3
"""A search.py spec from a cover: N = a_r mod r for every modulus, N = 0 mod 2; rows = the odd primes below Q in no class.
    python3 make_spec.py cover.txt Q name out.json     (cover.txt: a BEST or COVER line, or a JSON list of [r, a])"""
import sys, json
from sympy import primerange
src, Q, name, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
txt = open(src).read()
if txt.lstrip().startswith('['):
    cover = [tuple(x) for x in json.loads(txt)]
else:
    line = next(l for l in txt.splitlines() if l.split() and l.split()[0] in ("BEST", "COVER")).split()
    cover = [tuple(map(int, t.split(":"))) for t in line[(1 if line[0] == "BEST" else 2):]]
M, N0 = 2, 0
for r, a in cover:
    t = ((a - N0) * pow(M, -1, r)) % r
    N0 += M * t; M *= r
assert N0 % 2 == 0 and all(N0 % r == a for r, a in cover)
rows = [q for q in primerange(3, Q) if all(q % r != a for r, a in cover)]
spec = {"name": name, "N0": str(N0), "M": str(M), "Q": Q, "residual": rows, "cover": [[r, a] for r, a in cover]}
json.dump(spec, open(out, "w"))
print(f"{name}: {len(cover)} moduli up to {max(r for r, _ in cover)}, M has {len(str(M))} digits, N0 {len(str(N0))} digits, {len(rows)} rows left below {Q}")
