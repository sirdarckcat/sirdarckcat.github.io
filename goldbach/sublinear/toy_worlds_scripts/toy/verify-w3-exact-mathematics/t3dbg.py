import random, sympy
from sympy import Poly, symbols, discriminant, resultant
from flint import nmod_poly
X = symbols('x'); random.seed(1)
p = 5; shown = 0
for trial in range(400):
    n = random.randint(2, 8)
    c = [random.randrange(p) for _ in range(n)] + [1]
    f = nmod_poly(c, p); d = f.derivative()
    if d.degree() < 0: continue
    e = d.degree(); l = int(d[e]); linv = pow(l, -1, p)
    g = [(int(d[k]) * linv) % p for k in range(e + 1)]
    fZ = Poly(sum(ci * X ** i for i, ci in enumerate(c)), X); gZ = Poly(sum(ci * X ** i for i, ci in enumerate(g)), X)
    disc = int(discriminant(fZ, X)) % p
    R = int(resultant(gZ, fZ, X)) % p if e > 0 else 1
    rhs = ((-1) ** (n * (n - 1) // 2 + n * e) * pow(l, n, p) * R) % p
    fac = f.factor()[1]; sqf = all(mm == 1 for _, mm in fac); r = sum(mm for _, mm in fac)
    chi = lambda a: 0 if a % p == 0 else (1 if pow(a % p, (p - 1) // 2, p) == 1 else -1)
    if disc != rhs or (sqf and chi(disc) != (-1) ** (n - r)):
        shown += 1
        if shown <= 6: print(c, "n", n, "e", e, "l", l, "disc", disc, "rhs", rhs, "sqf", sqf, "r", r, "chi", chi(disc), "gdeg", gZ.degree(), "fZdeg", fZ.degree())
print("fails", shown)
