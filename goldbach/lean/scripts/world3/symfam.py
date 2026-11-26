#!/usr/bin/env python3
"""Translation-invariant members beyond the reach of exhaustive enumeration (prime q).

usage: symfam.py q n dmax [line quadratics]

The family: N = g(t^q - t), g monic of degree n/q (q^(n/q) members of the q^n monic polynomials of degree n).
For N in the family the rows Q(t), Q(t+1), ..., Q(t+q-1) succeed together, so one irreducibility test serves an
orbit. Prints the histogram of L over the family and its best members, and the level the cell model gives to the
best of ALL q^n members: cells = classes modulo the linear polynomials (and the first `line quadratics`
irreducible quadratics), rows left independent with the exact average chance.
"""
import sys, math, time
from flint import nmod_poly

q, n, dmax = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
nquad = int(sys.argv[4]) if len(sys.argv) > 4 else 0
assert n % q == 0
m = n // q


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


t0 = time.time()
rows = []           # (degree, index, polynomial), in order
for d in range(1, dmax + 1):
    for idx in range(q ** d):
        f = poly(idx, d)
        if irreducible(f):
            rows.append((d, idx, f))
pos = {(d, idx): j for j, (d, idx, _) in enumerate(rows)}
# orbits under t -> t + 1, each at the position of its first row
shift = nmod_poly([1, 1], q)
orbit_first = []    # positions j that are the least of their orbit
seen = set()
for j, (d, idx, f) in enumerate(rows):
    if j in seen:
        continue
    orbit_first.append(j)
    g = f
    for _ in range(q):
        seen.add(pos[(d, index(g))])
        g = g(shift)
print(f"q={q} n={n}: {len(rows)} rows of degree <= {dmax}, {len(orbit_first)} orbits; family of {q**m} members", flush=True)

u = nmod_poly([0, q - 1] + [0] * (q - 2) + [1], q)      # t^q - t
hist = {}
best = []
tests = 0
for x in range(q ** m):
    g = poly(x, m)
    N = g(u)
    L = len(rows)
    for j in orbit_first:
        tests += 1
        if irreducible(N - rows[j][2]):
            L = j
            break
    hist[L] = hist.get(L, 0) + 1
    best.append((L, x))
best.sort(reverse=True)
print(f"family: tests {tests}, mean L {sum(k * v for k, v in hist.items()) / q**m:.1f}, time {time.time() - t0:.0f} s")
print("family best:", ", ".join(f"L={L} (D={rows[L][0] if L < len(rows) else '>' + str(dmax)}, g index {x})" for L, x in best[:8]))

# ---- the cell model for all members of degree n ----
def mobius(k):
    r = 1; p = 2
    while p * p <= k:
        if k % p == 0:
            k //= p
            if k % p == 0: return 0
            r = -r
        p += 1
    return -r if k > 1 else r

pi_n = sum(mobius(d) * q ** (n // d) for d in range(1, n + 1) if n % d == 0) // n
moduli = [f for d, idx, f in rows if d == 1] + [f for d, idx, f in rows if d == 2][:nquad]
dens = 1.0
for P in moduli:
    dens *= 1 - q ** (-P.degree())
p_line = pi_n / q ** n / dens
# struck[i][a] = bitmask of the rows congruent to the class a modulo the i-th modulus
struck = []
for P in moduli:
    d = {}
    for j, (_, _, f) in enumerate(rows):
        key = tuple(int(c) for c in (f % P).coeffs())
        d[key] = d.get(key, 0) | (1 << j)
    classes = []
    for a in range(q ** P.degree()):
        c = []; y = a
        for _ in range(P.degree()):
            c.append(y % q); y //= q
        while c and c[-1] == 0: c.pop()
        classes.append(d.get(tuple(c), 0))
    struck.append(classes)
# all cells: the rows struck, as bit-packed arrays (one row of 64-bit words per cell)
import numpy as np
nw = (len(rows) + 63) // 64
def to_words(mk):
    return [(mk >> (64 * i)) & 0xFFFFFFFFFFFFFFFF for i in range(nw)]
cellmask = np.zeros((1, nw), dtype=np.uint64)
for classes in struck:
    a = np.array([to_words(c) for c in classes], dtype=np.uint64)
    cellmask = (cellmask[:, None, :] | a[None, :, :]).reshape(-1, nw)
ncell = cellmask.shape[0]
lq = math.log1p(-p_line)

def predicted(R):
    fw = np.array(to_words((1 << R) - 1), dtype=np.uint64)
    struck_count = np.bitwise_count(cellmask & fw).sum(axis=1, dtype=np.int64)
    return float(q ** n) * float(np.exp(lq * (R - struck_count)).mean())

def level(target):
    lo, hi = 1, len(rows)
    if predicted(hi) > target:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if predicted(mid) > target: lo = mid + 1
        else: hi = mid
    return lo

print(f"cell model for all {q}^{n} members: line of {len(moduli)} moduli ({ncell} cells), chance of a row left {p_line:.4f}; "
      f"rows R with 10, 1, 0.1 members expected: {level(10)}, {level(1)}, {level(0.1)}")
# degree by degree: members with every row of degree <= d failing, in the family and (cell model) among all
upto = {}
for j, (d, _, _) in enumerate(rows):
    upto[d] = j + 1
print("BYDEGREE (d: rows of degree <= d | family members with all of them failing | expected among all members, cell model | its q-th root)")
for d in sorted(upto):
    Fd = sum(v for k, v in hist.items() if k >= upto[d])
    Gd = predicted(upto[d])
    print(f"  d={d}: rows {upto[d]} | family {Fd} of {q**m} | all {Gd:.3g} | root {Gd ** (1.0 / q):.3g}")
Lb = best[0][0]
if Lb < len(rows):
    print(f"expected number of members of all {q}^{n} at the family's best level L >= {Lb}: {predicted(Lb):.3g}")
