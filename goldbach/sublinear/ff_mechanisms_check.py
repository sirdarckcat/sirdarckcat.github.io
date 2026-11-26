#!/usr/bin/env python3
"""Independent check of two statements of the forcing-mechanism catalogue (function fields), with python-flint.
C2 (characteristic 2, over F_2, k = 1): N = A^4, Q monic squarefree of odd degree d < 4 deg A, Q' = S^2, S | A
    =>  r(N - Q) = r(Q) + 1 + deg A + (d^2 - 1)/8  (mod 2),  r = number of irreducible factors with multiplicity.
C4 (Artin-Schreier, over F_p): A monic of degree m with second coefficient 0, C of degree <= m - 2
    =>  (A - C)(x^p - x) is reducible.
"""
import random, sys
from flint import nmod_poly
random.seed(12345)

def rnd(p, deg, monic=True):
    c = [random.randrange(p) for _ in range(deg)] + [1 if monic else random.randrange(1, p)]
    return nmod_poly(c, p)

def nfac(f):
    return sum(e for _, e in f.factor()[1])

def squarefree(f):
    return f.gcd(f.derivative()).degree() == 0

# ---- C2 over F_2
bad = tot = 0
for trial in range(4000):
    d = random.choice([1, 3, 5, 7, 9, 11])
    Q = rnd(2, d)
    if not squarefree(Q): continue
    qc = [int(Q[i]) for i in range(d + 1)]
    S = nmod_poly([qc[i] for i in range(1, d + 1, 2)], 2)          # Q' = S^2
    assert (S * S) == Q.derivative()
    if S.degree() < 0: continue
    B = rnd(2, random.randrange(1, 5))
    A = S * B
    if 4 * A.degree() <= d: continue
    N = A ** 4
    lhs = nfac(N - Q) % 2
    rhs = (nfac(Q) + 1 + A.degree() + (d * d - 1) // 8) % 2
    tot += 1; bad += lhs != rhs
print(f"C2 over F_2: {tot} instances, {bad} disagreements")
# control: drop the hypothesis S | A
bad = tot = 0
for trial in range(3000):
    d = random.choice([5, 7, 9, 11])
    Q = rnd(2, d)
    if not squarefree(Q): continue
    qc = [int(Q[i]) for i in range(d + 1)]
    S = nmod_poly([qc[i] for i in range(1, d + 1, 2)], 2)
    A = rnd(2, random.randrange(3, 7))
    if S.degree() < 1 or (A % S).degree() < 0: continue
    N = A ** 4
    tot += 1; bad += (nfac(N - Q) % 2) != ((nfac(Q) + 1 + A.degree() + (d * d - 1) // 8) % 2)
print(f"C2 control (S not dividing A): {tot} instances, {bad} disagreements (about half expected if the hypothesis matters)")

# ---- C4 over F_p
for p in (3, 5, 7):
    x = nmod_poly([0, 1], p); y = x ** p - x
    red = tot = 0
    for trial in range(600):
        m = random.randrange(2, 6)
        c = [random.randrange(p) for _ in range(m - 1)] + [0, 1]      # second coefficient 0
        g = nmod_poly(c, p)                                            # g = A - C: same top two coefficients as A
        f = g(y)
        fac = f.factor()[1]
        tot += 1; red += not (len(fac) == 1 and fac[0][1] == 1)
    # control: second coefficient non-zero: irreducible exactly when g is
    agree = tot2 = 0
    for trial in range(600):
        m = random.randrange(2, 6)
        c = [random.randrange(p) for _ in range(m - 1)] + [random.randrange(1, p), 1]
        g = nmod_poly(c, p)
        fg = g.factor()[1]; gi = len(fg) == 1 and fg[0][1] == 1
        ff = g(y).factor()[1]; fi = len(ff) == 1 and ff[0][1] == 1
        tot2 += 1; agree += gi == fi
    print(f"C4 over F_{p}: trace 0: {red} of {tot} reducible; trace non-zero: irreducible exactly when g is in {agree} of {tot2}")
