#!/usr/bin/env python3
"""Independent recheck of search specs (campaign3 JSON format).  It does not use the residue list to decide which
rows are covered: a row q is covered exactly when gcd(N0 - q, M) > 1, computed from the integers N0 and M.

    python3 check_specs.py specs.json [cap_digits=200]
"""
import json, sys, math
from math import gcd
specs = json.load(open(sys.argv[1])); cap = 10 ** (int(sys.argv[2]) if len(sys.argv) > 2 else 200)
def odd_primes_below(n):
    s = bytearray([1]) * n; s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(3, n) if s[i]]
rows_cache = {}
seen = set(); ks = []
for sp in specs:
    Q = sp["Q"]; N0 = int(sp["N0"]); M = int(sp["M"]); cover = sp["cover"]
    rows = rows_cache.setdefault(Q, odd_primes_below(Q))
    prod = 2
    for r, a in cover:
        assert 0 < a < r, (sp["name"], r, a)
        assert N0 % r == a, (sp["name"], "N0 residue", r)
        prod *= r
    assert prod == M and N0 % 2 == 0 and 0 <= N0 < M, sp["name"]
    assert all(M % r == 0 for r, _ in cover) and len({r for r, _ in cover}) == len(cover)
    uncovered = [q for q in rows if gcd(N0 - q, M) == 1]
    assert uncovered == sp["residual"], (sp["name"], len(uncovered), len(sp["residual"]))
    assert N0 + (sp["kmax"] - 1) * M < cap, (sp["name"], "exceeds the cap")
    assert N0 not in seen, (sp["name"], "duplicate vector"); seen.add(N0)
    boost = 2.0
    for r, _ in cover: boost *= r / (r - 1)
    assert abs(boost - sp["boost"]) < 1e-9 * boost
    ks.append(len(uncovered))
print(f"{sys.argv[1]}: {len(specs)} specs OK; Q = {sorted({s['Q'] for s in specs})}; residual sizes {min(ks)}..{max(ks)} "
      f"(mean {sum(ks)/len(ks):.1f}); moduli {len(specs[0]['cover'])}; M has {len(specs[0]['M'])} digits; "
      f"largest N has {max(len(str(int(s['N0']) + (s['kmax'] - 1) * int(s['M']))) for s in specs)} digits; all N0 distinct")
