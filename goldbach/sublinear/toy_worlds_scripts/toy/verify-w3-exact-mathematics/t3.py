# independent check of T3 for prime q.
#  disc f: sympy discriminant of the integer lift, reduced mod p (universal polynomial in the coefficients)
#  prod_{f'(beta)=0} f(beta): norm of f in F_p[x]/(f'/l) = determinant of multiplication by f (no resultant routine, no sign convention)
#  r: flint factorisation
import random
from sympy import Poly, symbols, discriminant
from flint import nmod_poly, nmod_mat
X = symbols('x'); random.seed(2026)
def chi(a, p):
    a %= p
    return 0 if a == 0 else (1 if pow(a, (p - 1) // 2, p) == 1 else -1)
def norm(f, g, p):          # g monic of degree e >= 1
    e = g.degree(); rows = []
    xk = nmod_poly([1], p)
    for k in range(e):
        h = (f * xk) % g; rows.append([int(h[j]) for j in range(e)]); xk = xk * nmod_poly([0, 1], p)
    return int(nmod_mat(e, e, [v for r in rows for v in r], p).det())
for p in (3, 5, 7, 11):
    bad = tested = sqf_n = lowdeg = 0
    for trial in range(1500):
        n = random.randint(2, 13)
        if random.random() < 0.6 and n >= p:
            m = n // p; n = m * p
            c = [0] * (n + 1); c[n] = 1
            for k in range(m): c[k * p] = random.randrange(p)
            for k in range(random.randint(1, min(n - 1, 4)) + 1):
                if k < n: c[k] = random.randrange(p)
        else:
            c = [random.randrange(p) for _ in range(n)] + [1]
        f = nmod_poly(c, p); d = f.derivative()
        if d.degree() < 0: continue
        e = d.degree(); l = int(d[e]); linv = pow(l, -1, p)
        lowdeg += e < n - 1
        fZ = Poly(sum(ci * X ** i for i, ci in enumerate(c)), X)
        disc = int(discriminant(fZ, X)) % p
        R = norm(f, d * linv, p) if e > 0 else 1
        rhs = ((-1) ** (n * (n - 1) // 2 + n * e) * pow(l, n, p) * R) % p
        fac = f.factor()[1]; sqf = all(mm == 1 for _, mm in fac); r = sum(mm for _, mm in fac)
        ok = (disc == rhs) and ((disc == 0) == (not sqf))
        if sqf:
            sqf_n += 1
            ok = ok and chi(disc, p) == (-1) ** (n - r) and chi(-1, p) ** (n * (n - 1) // 2 + n * e) * chi(l, p) ** n * chi(R, p) == (-1) ** (n - r)
        bad += not ok; tested += 1
    print("p", p, "tested", tested, "of which deg f' < n-1:", lowdeg, "squarefree", sqf_n, "failures", bad)
