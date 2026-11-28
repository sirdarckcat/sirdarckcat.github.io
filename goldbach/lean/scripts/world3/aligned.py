#!/usr/bin/env python3
"""Aligned classes against every choice of classes (prime q).

usage: aligned.py q J
Moduli: every irreducible of degree at most J. Target: the rows (monic irreducibles) of degree at most J + 1.
A cell is a class for each modulus; a row Q is struck in the cell when Q is in the class of some modulus.
Aligned cell of R (monic of degree J + 1): the class of every modulus is that of R, so Q is struck iff R - Q has a
factor of degree at most J. Prints the fewest rows left over ALL cells (by enumeration) and over the aligned ones.
"""
import sys, itertools
from flint import nmod_poly
q, J = int(sys.argv[1]), int(sys.argv[2])
def poly(idx, d):
    c = []
    for _ in range(d):
        c.append(idx % q); idx //= q
    return nmod_poly(c + [1], q)
def irreducible(f):
    _, fac = f.factor(); return len(fac) == 1 and fac[0][1] == 1
irr = {d: [poly(i, d) for i in range(q ** d) if irreducible(poly(i, d))] for d in range(1, J + 2)}
moduli = [P for d in range(1, J + 1) for P in irr[d]]
rows = [Q for d in range(1, J + 2) for Q in irr[d]]
nrow = len(rows)
def key(f, P):
    return tuple(int(c) for c in (f % P).coeffs())
# for each modulus: class -> bitmask of the rows in it
struck = []
for P in moduli:
    d = {}
    for j, Q in enumerate(rows):
        k = key(Q, P); d[k] = d.get(k, 0) | (1 << j)
    struck.append(d)
ncells = 1
for P in moduli: ncells *= q ** P.degree()
# the best over all cells: only the classes that strike something matter, plus "nothing"
best = nrow; nbest = 0
opts = [sorted(set(d.values()) | {0}) for d in struck]
mult = []
for P, d in zip(moduli, struck):
    cnt = {}
    for v in d.values(): cnt[v] = cnt.get(v, 0) + 1
    cnt[0] = cnt.get(0, 0) + (q ** P.degree() - len(d))
    mult.append(cnt)
if ncells <= 5 * 10 ** 7:
    for combo in itertools.product(*[list(m.items()) for m in mult]):
        mk = 0; w = 1
        for v, c in combo:
            mk |= v; w *= c
        left = nrow - bin(mk).count('1')
        if left < best: best, nbest = left, w
        elif left == best: nbest += w
    allres = f"fewest rows left over all {ncells} cells: {best} ({nbest} cells)"
else:
    allres = f"{ncells:.3g} cells: not enumerated"
al = []
for i in range(q ** (J + 1)):
    R = poly(i, J + 1)
    mk = 0
    for P, d in zip(moduli, struck):
        mk |= d.get(key(R, P), 0)
    al.append((nrow - bin(mk).count('1'), i))
al.sort()
nb = sum(1 for l, _ in al if l == al[0][0])
print(f"q={q} J={J}: {len(moduli)} moduli (total degree {sum(P.degree() for P in moduli)}), {nrow} rows of degree <= {J+1}; {allres}; "
      f"aligned cells (R monic of degree {J+1}, {len(al)} of them): fewest rows left {al[0][0]} ({nb} cells), e.g. R = {poly(al[0][1], J + 1)}; "
      f"median over aligned cells {al[len(al)//2][0]}")
