#!/usr/bin/env python3
"""Specs for many covers of the same moduli (search.py's spec format), each capped below 10^ceiling, split across workers.

    python3 cover_specs.py dump.txt Q ncovers ceiling nworkers out_prefix [--kmax-rows K] [--exclude other_dump.txt ...]

dump.txt: COVER lines ("COVER k r:a r:a ...", ptcover's PT_DUMP) and/or BEST lines.  The covers are taken in order of rows
(k), distinct by their (r, a) vector, at most ncovers of them, rows <= --kmax-rows if given; any cover also present in an
--exclude file is dropped.  Each spec scans k in [0, kmax) with kmax = the largest multiple of 32,768 (search.py's block)
with N0 + (kmax - 1) M < 10^ceiling, so no member has more than `ceiling` digits.  out_prefix_w<i>.json gets every
nworkers-th spec (one search_c.py --procs 1 per worker: no idle tail between covers)."""
import json, sys
from sympy import primerange
args = sys.argv[1:]
excl = []
kmax_rows = None
while "--exclude" in args:
    i = args.index("--exclude"); excl.append(args[i + 1]); del args[i:i + 2]
if "--kmax-rows" in args:
    i = args.index("--kmax-rows"); kmax_rows = int(args[i + 1]); del args[i:i + 2]
src, Q, ncov, ceil, nw, prefix = args[0], int(args[1]), int(args[2]), int(args[3]), int(args[4]), args[5]


def covers(path):
    out = []
    for l in open(path):
        t = l.split()
        if not t or t[0] not in ("COVER", "BEST"):
            continue
        pairs = t[2:] if t[0] == "COVER" else t[1:]
        cov = tuple(tuple(map(int, p.split(":"))) for p in pairs)
        out.append((int(t[1]) if t[0] == "COVER" else None, cov))
    return out


seen = set(c for p in excl for _, c in covers(p))
nex = len(seen)
cand = []
for k, c in covers(src):
    if c in seen:
        continue
    seen.add(c)
    cand.append((k, c))
primes = list(primerange(3, Q))
specs = []
for k, cov in sorted(cand, key=lambda x: (x[0] if x[0] is not None else 10 ** 9)):
    rows = [q for q in primes if all(q % r != a for r, a in cov)]
    if kmax_rows is not None and len(rows) > kmax_rows:
        continue
    M, N0 = 2, 0
    for r, a in cov:
        t = ((a - N0) * pow(M, -1, r)) % r
        N0 += M * t; M *= r
    assert N0 % 2 == 0 and all(N0 % r == a for r, a in cov)
    kcap = (10 ** ceil - 1 - N0) // M + 1          # members k < kcap are below 10^ceil
    kmax = kcap // 32768 * 32768
    specs.append({"name": f"c{len(specs):04d}_r{len(rows)}", "N0": str(N0), "M": str(M), "Q": Q, "residual": rows,
                  "cover": [[r, a] for r, a in cov], "kstart": 0, "kmax": kmax, "ceiling_digits": ceil})
    if len(specs) >= ncov:
        break
for w in range(nw):
    json.dump(specs[w::nw], open(f"{prefix}_w{w}.json", "w"))
rows = [len(s["residual"]) for s in specs]
print(f"{len(cand)} distinct covers ({nex} excluded), {len(specs)} specs: rows {min(rows)}..{max(rows)}, "
      f"{specs[0]['kmax']} members each below 10^{ceil}, {nw} worker files {prefix}_w*.json")
