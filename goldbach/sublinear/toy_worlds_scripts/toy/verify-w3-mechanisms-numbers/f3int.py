# F_3[x] with polynomials coded as base-3 integers (verifier's own pure-python/numpy code, no flint)
import numpy as np, itertools
def tolist(n):
    L = []
    while n: L.append(n % 3); n //= 3
    return L
def toint(L):
    v = 0
    for c in reversed(L): v = v*3 + c % 3
    return v
def deg(L):
    L = L[:]
    while L and L[-1] % 3 == 0: L.pop()
    return len(L) - 1
def pmod(a, m):
    a = [c % 3 for c in a]; dm = len(m) - 1; inv = 1 if m[-1] == 1 else 2
    for i in range(len(a) - 1, dm - 1, -1):
        c = a[i] * inv % 3
        if c:
            for j in range(dm + 1):
                a[i - dm + j] = (a[i - dm + j] - c * m[j]) % 3
    return a[:dm] + [0] * max(0, dm - len(a))
def pmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b): r[i + j] = (r[i + j] + x * y) % 3
    return r
def irreducibles(D):
    """monic irreducibles of degree 1..D over F_3 by sieving (lists, low degree first)"""
    out = {d: [] for d in range(1, D + 1)}
    comp = set()
    for d in range(1, D + 1):
        for t in itertools.product(range(3), repeat=d):
            f = list(t) + [1]
            if toint(f) not in comp: out[d].append(f)
        # mark multiples of products
        for d1 in range(1, d + 1):
            pass
        # composites of degree d+1.. are marked lazily below
        if d < D:
            # all monic products g*h with deg g = e <= deg h, total degree d+1
            tgt = d + 1
            for e in range(1, tgt // 2 + 1):
                for g in itertools.product(range(3), repeat=e):
                    G = list(g) + [1]
                    for h in itertools.product(range(3), repeat=tgt - e):
                        comp.add(toint(pmul(G, list(h) + [1])))
    return out
