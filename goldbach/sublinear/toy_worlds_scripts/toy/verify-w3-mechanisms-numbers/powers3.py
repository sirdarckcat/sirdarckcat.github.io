import numpy as np, itertools
from f3int import *
D = 7; J = 3
irr = irreducibles(D)
primes = [f for d in range(1, J + 1) for f in irr[d]]
rows = [f for d in range(1, D + 1) for f in irr[d]]
print("rows", len(rows), "primes", len(primes))
rowres = [[toint(pmod(Q, pi)) for pi in primes] for Q in rows]
def left(resN):
    return sum(1 for rr in rowres if all(a != b for a, b in zip(rr, resN)))
# (1) identity: x^(3^D - 1) - 1 = product of monic irreducibles of degree | D other than x
for Dd in (1, 2, 3):
    P = [1]
    for d in range(1, Dd + 1):
        if Dd % d == 0:
            for f in irr[d]:
                if f != [0, 1]: P = pmul(P, f)
    T = [2] + [0] * (3 ** Dd - 2) + [1]
    print("D =", Dd, "identity holds:", P == T)
vals = []
for m in range(60, 260):
    resN = [toint(pmod([0] * m + [1], pi)) for pi in primes]
    vals.append(left(resN))
vals = np.array(vals)
print(f"x^m, m = 60..259: mean {vals.mean():.1f}, sd {vals.std(ddof=1):.1f}, min {vals.min()}")
rng = np.random.default_rng(3)
sizes = [3 ** (len(pi) - 1) for pi in primes]
ix = primes.index([0, 1])
v1 = []; v2 = []
for t in range(2000):
    r = [int(rng.integers(1, s)) for s in sizes]
    v1.append(left(r))
    r2 = r[:]; r2[ix] = 0
    v2.append(left(r2))
print(f"random classes, nonzero everywhere (2000): mean {np.mean(v1):.1f}, sd {np.std(v1, ddof=1):.1f}, min {min(v1)}")
print(f"random classes, zero at x and nonzero elsewhere (2000): mean {np.mean(v2):.1f}, sd {np.std(v2, ddof=1):.1f}, min {min(v2)}")
# Carlitz module over F_3: C_x(a) = x a + a^3 ; C_M(1) for M monic of degree 4 with C_M(1) prime to all 14 primes
def padd(a, b):
    n = max(len(a), len(b)); a = a + [0] * (n - len(a)); b = b + [0] * (n - len(b))
    r = [(u + v) % 3 for u, v in zip(a, b)]
    while r and r[-1] == 0: r.pop()
    return r
def cube(a):
    r = [0] * (3 * (len(a) - 1) + 1) if a else []
    for i, c in enumerate(a): r[3 * i] = c
    return r
def Cx(a): return padd([0] + a if a else [], cube(a))
def CM(M, a):
    # C_M(a) = sum m_i C_x^i(a)
    out = []; cur = a
    for mi in M:
        out = padd(out, [(mi * c) % 3 for c in cur]); cur = Cx(cur)
    return out
vc = []; degs = set()
for t in itertools.product(range(3), repeat=4):
    M = list(t) + [1]
    v = CM(M, [1])
    degs.add(len(v) - 1)
    resN = [toint(pmod(v, pi)) for pi in primes]
    if all(r != 0 for r in resN): vc.append(left(resN))
print(f"C_M(1), M monic of degree 4, prime to all 14 primes: {len(vc)} values, mean {np.mean(vc):.1f}, sd {np.std(vc, ddof=1):.1f}, min {min(vc)}; degrees of C_M(1) seen: {sorted(degs)} (3^4 = 81)")
# degree claim deg C_Lam(a) = q^deg(Lam) * deg a
for a in ([1], [0, 1], [1, 1, 1], [2, 0, 0, 1]):
    for Lam in ([0, 1], [1, 0, 1], [2, 1, 0, 1]):
        v = CM(Lam, a)
        print("   a degree", len(a) - 1, "Lam degree", len(Lam) - 1, "deg C_Lam(a) =", len(v) - 1, "claimed", 3 ** (len(Lam) - 1) * (len(a) - 1))
