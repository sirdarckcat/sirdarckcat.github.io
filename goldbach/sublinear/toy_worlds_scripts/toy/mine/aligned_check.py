# Aligned classes in F_p[x]: N = R modulo every irreducible of degree <= J strikes the row Q iff R - Q has an
# irreducible factor of degree <= J.  For each monic R of degree J + 1: rows of degree <= J + 1 left.
import itertools, sys
from flint import nmod_poly
def monic(p, d):
    for c in itertools.product(range(p), repeat=d):
        yield nmod_poly(list(c) + [1], p)
def irreducible(f):
    fac = f.factor()[1]
    return len(fac) == 1 and fac[0][1] == 1
def min_factor_degree(f):
    return min(g.degree() for g, e in f.factor()[1])
for p, J in ((3, 3), (3, 2), (5, 2), (7, 1), (5, 1)):
    rows = [Q for d in range(1, J + 2) for Q in monic(p, d) if irreducible(Q)]
    VJdeg = sum(Q.degree() for Q in rows if Q.degree() <= J)
    best = None
    for R in monic(p, J + 1):
        left = 0
        for Q in rows:
            D = R - Q
            if D.degree() < 0: continue                      # Q = R: N - Q divisible by everything
            if D.degree() == 0 or min_factor_degree(D) > J: left += 1
        if best is None or left < best[0]: best = (left, R)
    print(f"F_{p}, J = {J}: {len(rows)} rows of degree <= {J+1}; room deg V_J = {VJdeg}; best aligned R leaves {best[0]} rows (R coefficients low to high: {[int(best[1][i]) for i in range(J+2)]}); the parity desert's room is {p * VJdeg}")
