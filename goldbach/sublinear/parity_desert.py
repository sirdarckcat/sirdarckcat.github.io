# Toy setting: polynomials over F_q.  "Rows" = monic irreducible Q of small degree; we want N - Q reducible for all rows.
# Mechanism tested here (no small factor is exhibited): take N = lam * V^p * x^(p a) with V vanishing at every critical
# point of every row (V = product of all monic irreducibles of degree <= J, J = max row degree - 1).  Then N' = 0, so
# (N - Q)' = -Q', and by Stickelberger/Swan (number r of irreducible factors of a squarefree f of degree n over F_q,
# q odd:  chi(disc f) = (-1)^(n - r)) the parity of r should be the same for all rows Q of a given degree.
#
#   python3 parity_desert.py p e "2,3" a lam_is_square [max_rows_per_degree]
import itertools, random, sys
from flint import fq_default_ctx, fq_default_poly_ctx

p, e = int(sys.argv[1]), int(sys.argv[2]); degs = [int(t) for t in sys.argv[3].split(",")]
a = int(sys.argv[4]); lam_sq = int(sys.argv[5]); cap = int(sys.argv[6]) if len(sys.argv) > 6 else 10 ** 9
q = p ** e
F = fq_default_ctx(p, e); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(p), repeat=e)]
lam = next(v for v in els if v != 0 and bool(v.is_square()) == bool(lam_sq) and (lam_sq == 0 or v == 1))
J = max(degs) - 1
V = R(1)
for j in range(1, J + 1):
    g = pow(x, q ** j, None) - x if q ** j < 5000 else None
    assert g is not None
    V = V * (g // V.gcd(g))
N = lam * V ** p * x ** (p * a)
n = N.degree()
assert N.derivative() == 0
print(f"F_{q} (p = {p}), N = lam * V^{p} * x^{p*a}, deg V = {V.degree()}, deg N = {n}, lam {'square' if lam_sq else 'non-square'}")
random.seed(1)
for d in degs:
    rows = []
    for c in itertools.product(els, repeat=d):
        Q = R(list(c) + [F(1)])
        if Q.is_irreducible(): rows.append(Q)
    total = len(rows)
    if total > cap: rows = random.sample(rows, cap)
    par = {0: 0, 1: 0}; irr = 0; nonsqf = 0; rmin = 10 ** 9
    for Q in rows:
        f = N - Q
        lc, fac = f.factor()
        r = sum(m for _, m in fac)
        if any(m > 1 for _, m in fac): nonsqf += 1
        par[r % 2] += 1; irr += (r == 1); rmin = min(rmin, r)
    print(f"  rows of degree {d}: {total} monic irreducibles, {len(rows)} tested: r even {par[0]}, r odd {par[1]}, "
          f"N - Q irreducible for {irr}, fewest factors {rmin}, not squarefree {nonsqf}" + ("   [p divides d]" if d % p == 0 else ""))
