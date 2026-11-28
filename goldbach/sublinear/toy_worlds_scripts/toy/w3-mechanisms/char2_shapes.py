# Exploration: N = (A^2 * C)^2 over F_q (q = 2^k), A = L_J, C a small polynomial (so N' = 0 but N is not a 4th power
# unless C is a square).  Tabulates the parity of r(N - Q) over all monic irreducible rows by (d mod 8, deg Q', invariant).
#   python3 char2_shapes.py k J Cindex dmin dmax
import itertools, sys
from collections import defaultdict
from flint import fq_default_ctx, fq_default_poly_ctx
k, J, ci, dmin, dmax = (int(v) for v in sys.argv[1:6]); q = 2 ** k
F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]; one, zero = F(1), F(0)
def tr(v):
    s = zero; w = v
    for _ in range(k): s += w; w = w * w
    return 1 if s == one else 0
def V(j):
    v = R(1)
    for i in range(1, j + 1):
        g = pow(x, q ** i, None) - x; v = v * (g // v.gcd(g))
    return v
A = R(1)
for m in range(1, J + 1): A = A * V(J // m)
z = els[1] if k == 1 else F([0, 1] + [0] * (k - 2))
Cs = [R(1), x, x + 1, x ** 2 + x + 1, x ** 3 + x + 1, x ** 3, x * (x + 1), x + z, x ** 3 + z * x ** 2 + 1]
C = Cs[ci]
N = (A * A * C) ** 2; n = N.degree()
print(f"F_{q}: N = (L_{J}^2 * C)^2, C = {C}, n = {n} (n mod 8 = {n % 8})")
for d in range(dmin, dmax + 1):
    tab = defaultdict(lambda: [0, 0])
    for c in itertools.product(els, repeat=d):
        Q = R(list(c) + [one])
        if not Q.is_irreducible(): continue
        e = Q.derivative().degree()
        qc = Q.coeffs()
        inv = tr(qc[d - 2] / qc[d - 1] ** 2) if (d % 2 == 0 and qc[d - 1] != zero) else "-"
        fac = (N - Q).factor()[1]
        r = sum(m for _, m in fac)
        tab[(e, inv)][r % 2] += 1
    print(f"  d = {d}: " + "; ".join(f"e={e},inv={inv}: even {v[0]} odd {v[1]}" for (e, inv), v in sorted(tab.items(), key=str)))
