#!/usr/bin/env python3
"""How many covers lie within a few rows of a best one?

    python3 cover_nearopt.py covers.txt Q [which cover of the file, by rank = 0]

Single-class changes from the cover: for a modulus r and another class c, the rows added are (rows covered by r alone)
minus (uncovered rows in class c).  Their counts by cost, and a crude count of independent pairs and triples.  On the
1,245-row cover of the 491 set at 170,000 this gives about 1,800 covers within two rows and 20,000 to 30,000 within
three, which is what the capped walks found (1,800 and 26,000) and what the fleet's ledgers hold (28,000 at 1,248 or
fewer): the walks have essentially all of them.
"""
import sys, collections, numpy as np
f = sys.argv[1]; Q = int(sys.argv[2]); pick = int(sys.argv[3]) if len(sys.argv) > 3 else 0
lines = [l.split() for l in open(f) if l.startswith("COVER")]; lines.sort(key=lambda t: int(t[1])); t = lines[pick]
cl = {int(x.split(":")[0]): int(x.split(":")[1]) for x in t[2:] if ":" in x}; mods = sorted(cl)
sv = np.ones(Q, dtype=bool); sv[:2] = False
for i in range(2, int(Q ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
sv[2] = False; q = np.nonzero(sv)[0]
cnt = np.zeros(len(q), dtype=int)
for r in mods: cnt += (q % r) == cl[r]
unc = cnt == 0; print("rows", int(unc.sum()), "(file says", t[1] + ")")
hist = collections.Counter(); per = {}
for r in mods:
    e = int((((q % r) == cl[r]) & (cnt == 1)).sum()); u = np.bincount(q[unc] % r, minlength=r)
    d = e - u; d[cl[r]] = 99; d[0] = 99
    for x in d: 
        if x <= 4: hist[int(x)] += 1
    per[r] = (e, int((d <= 0).sum()), int((d <= 1).sum()), int((d <= 2).sum()), int((d <= 3).sum()))
print("single changes by delta (rows added):", sorted(hist.items()))
print("modulus: rows it covers alone, classes with delta <= 0, 1, 2, 3   (the top 14 moduli)")
for r in mods[-14:]: print(f"  {r}: {per[r]}")
n = [hist[d] for d in (-2, -1, 0, 1, 2, 3)]; neg = hist[-1] + hist[-2] + hist[-3]
n0 = sum(v for d, v in hist.items() if d <= 0); n1, n2, n3 = hist[1], hist[2], hist[3]
print("with improvements counted as 0:", n0, n1, n2, n3)
for cap in (1, 2, 3):
    s1 = n0 + sum([n1, n2, n3][:cap])
    pairs = n0 * n0 / 2 + (n0 * n1 if cap >= 1 else 0) + (n0 * n2 + n1 * n1 / 2 if cap >= 2 else 0) + (n0 * n3 + n1 * n2 if cap >= 3 else 0)
    trip = n0 ** 3 / 6 + (n0 * n0 * n1 / 2 if cap >= 1 else 0) + (n0 * n0 * n2 / 2 + n0 * n1 * n1 / 2 if cap >= 2 else 0) + (n0 * n0 * n3 / 2 + n0 * n1 * n2 + n1 ** 3 / 6 if cap >= 3 else 0)
    print(f"within +{cap} rows: singles {s1}, independent pairs about {pairs:.3g}, triples about {trip:.3g}")
