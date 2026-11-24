#!/usr/bin/env python3
"""Summary of hgen2.txt: how well the heuristic at each depth names the real terms.

    python3 -I hgen2_summary.py hgen2.txt > hgen2_summary.txt
"""
import math
import sys

thetas, rows = None, []
for line in open(sys.argv[1]):
    if line.startswith('#'):
        if 'theta=' in line:
            thetas = [tok.split('=')[1] for tok in line.split() if tok.startswith('theta=')]
        continue
    parts = [p.strip() for p in line.rstrip().rstrip('|').split('|')]
    if len(parts) < 2: continue
    Nk, Gk, m, n = map(int, parts[0].split())
    cells = []
    for p in parts[1:]:
        t = p.replace('~', ' ').split()
        cells.append((int(t[0]), int(t[1]), int(t[2])))
    if thetas and len(cells) == len(thetas): rows.append((Nk, Gk, m, n, cells))

print(f"{len(rows)} stretches between consecutive real terms, from {rows[0][0]} to the term after {rows[-1][0]}")
print("depth z = N^theta; open = strikers the heuristic cannot settle for the real next term; place = position of the")
print("real next term when the numbers of its stretch are taken in the heuristic's order of preference")
print()
print(" theta   median z   median open   named first   place: median   geometric mean   walk / place (nats saved)   nats still missing")
for i, th in enumerate(thetas):
    z = sorted(r[4][i][0] for r in rows)[len(rows) // 2]
    op = sorted(r[4][i][1] for r in rows)[len(rows) // 2]
    places = [r[4][i][2] for r in rows]
    named = sum(1 for p in places if p == 1)
    med = sorted(places)[len(places) // 2]
    gm = math.exp(sum(math.log(p) for p in places) / len(places))
    saved = sum(math.log(max(r[3], 1) / r[4][i][2]) for r in rows) / len(rows)
    missing = sum(math.log(p) for p in places) / len(places)
    print(f" {th:>5} {z:10d} {op:13d} {named:9d}/{len(rows):<3d} {med:14d} {gm:16.1f} {saved:22.1f} {missing:22.1f}")
walk = sum(math.log(max(r[3], 1)) for r in rows) / len(rows)
print(f"\nwalking every even number of a stretch costs e^{walk:.1f} numbers on average (geometric mean of the stretch lengths)")
