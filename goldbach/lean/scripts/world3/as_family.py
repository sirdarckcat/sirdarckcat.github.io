#!/usr/bin/env python3
"""The q(q-1) polynomials lam*(t^q - t + c) over F_q (q prime): the family invariant under every translation.

usage: as_family.py q [dmax]
Rows: monic irreducibles by degree then index; a row succeeds when N - Q is irreducible; the q translates of a row
succeed together, so one factorisation serves an orbit. Prints L and D for the best members and the level
ln(q^q) / -ln(1 - 1/q) at which one member of all q^q polynomials of degree q with a given leading coefficient is
expected if every row had the chance 1/q.
"""
import sys, math, time
from flint import nmod_poly

q = int(sys.argv[1]); dmax = int(sys.argv[2]) if len(sys.argv) > 2 else 3
t0 = time.time()

def poly(idx, d):
    c = []
    for _ in range(d):
        c.append(idx % q); idx //= q
    return nmod_poly(c + [1], q)

def index(f):
    c = [int(x) for x in f.coeffs()]
    return sum(c[i] * q ** i for i in range(len(c) - 1))

def irreducible(f):
    _, fac = f.factor()
    return len(fac) == 1 and fac[0][1] == 1

shift = nmod_poly([1, 1], q)
rows = []; orbit_first = []; seen = set(); pos = 0
for d in range(1, dmax + 1):
    base = pos; idxs = []
    for idx in range(q ** d):
        if irreducible(poly(idx, d)):
            idxs.append(idx)
    where = {idx: base + j for j, idx in enumerate(idxs)}
    for idx in idxs:
        j = where[idx]
        rows.append((d, idx))
        if j in seen:
            continue
        orbit_first.append((j, d, idx))
        g = poly(idx, d)
        for _ in range(q):
            seen.add(where[index(g)]); g = g(shift)
    pos += len(idxs)
u = nmod_poly([0, q - 1] + [0] * (q - 2) + [1], q)
res = []
for lam in range(1, q):
    for c in range(q):
        N = lam * (u + c)
        L = len(rows); D = dmax + 1
        for j, d, idx in orbit_first:
            if irreducible(N - poly(idx, d)):
                L = j; D = d
                break
        res.append((L, D, lam, c))
res.sort(reverse=True)
naive = q * math.log(q) / -math.log(1 - 1 / q)
bylam = {}
for L, D, lam, c in res:
    bylam.setdefault(lam, []).append(L)
monic = sorted(bylam[1], reverse=True)
print(f"q={q}: rows of degree <= {dmax}: {len(rows)} in {len(orbit_first)} orbits; family {len(res)} members; "
      f"naive level for q^q members: {naive:.0f}; best: " + ', '.join(f"L={L} D={'>' + str(dmax) if D > dmax else D} (lam={lam}, c={c})" for L, D, lam, c in res[:4])
      + f"; best monic: {monic[0]}; median over the family: {sorted(L for L, _, _, _ in res)[len(res) // 2]}; "
      f"members at or above the naive level: {sum(1 for L, _, _, _ in res if L >= naive)}; time {time.time() - t0:.0f} s", flush=True)
