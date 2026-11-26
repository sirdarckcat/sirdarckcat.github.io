#!/usr/bin/env python3
"""Independent check of w3 for a prime q and a small n, with FLINT factorisations instead of the sieve.

usage: check_w3.py q n mu OUT.txt     (OUT.txt written by: w3 q n mu b OUT.txt ...)
Recomputes from scratch: the histogram of L over every member, and for every target of the file the histograms of
the rows left after the linear factors, of the odd-squarefree rows, and the successes by level.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flint import nmod_poly
from analyse import parse

q, n, mu = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
r = parse(sys.argv[4])
b = r['b']

def poly(idx, d):
    c = []
    for _ in range(d):
        c.append(idx % q); idx //= q
    return nmod_poly(c + [1], q)

def info(f):
    """(irreducible, squarefree and odd number of factors, least degree of a factor)"""
    _, fac = f.factor()
    om = sum(e for _, e in fac); sqf = all(e == 1 for _, e in fac)
    return (len(fac) == 1 and fac[0][1] == 1, sqf and om % 2 == 1, min(g.degree() for g, _ in fac))

rows = []
for d in range(1, b):
    for idx in range(q ** d):
        f = poly(idx, d)
        if info(f)[0]:
            rows.append(f)
assert len(rows) == r['nrow'], (len(rows), r['nrow'])
targets = [t for t, _ in r['targets']]
Rmax = max(targets)
histL = {}
HK0 = {t: {} for t in targets}; HO = {t: {} for t in targets}
for idx in range(q ** n):
    M = poly(idx, n)
    L = None; k0 = 0; o = 0; won = False
    for j, Q in enumerate(rows):
        if j >= Rmax and L is not None:
            break
        irr, odd, least = info(M - mu * Q)
        if irr and L is None:
            L = j
        if j < Rmax:
            if irr: won = True
            if least > 1: k0 += 1
            if odd: o += 1
            if j + 1 in HK0:
                s = 0 if won else 1
                a = HK0[j + 1].setdefault(k0, [0, 0]); a[0] += 1; a[1] += s
                a = HO[j + 1].setdefault(o, [0, 0]); a[0] += 1; a[1] += s
    if L is None: L = len(rows)
    histL[L] = histL.get(L, 0) + 1
ok = histL == r['histL']
print('histogram of L:', 'agrees' if ok else 'DIFFERS', '(%d levels, record %d)' % (len(histL), max(histL)))
for t in targets:
    a = sorted((k, v[0], v[1]) for k, v in HK0[t].items()); bb = sorted((k, v[0], v[1]) for k, v in HO[t].items())
    print('target', t, 'rows left after the linear factors:', 'agrees' if a == r['HK'][(t, 0)] else 'DIFFERS',
          '| odd-squarefree rows:', 'agrees' if bb == r['HO'][(t, -1)] else 'DIFFERS')
