import itertools
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
F = fq_default_ctx(2, 1); R = fq_default_poly_ctx(F); x = R.gen(); els=[F(0),F(1)]; one=F(1)
V3 = x*(x+1)*(x**2+x+1)*(x**3+x+1)*(x**3+x**2+1); N = V3**4
c = Counter()
for co in itertools.product(els, repeat=9):
    Q = R(list(co)+[one])
    if not Q.is_irreducible(): continue
    cc = Q.coeffs(); S = R([cc[i] for i in range(1, 10, 2)])
    rad = R(1)
    for h, m in S.factor()[1]: rad *= h
    f = N - Q; r = sum(m for _, m in f.factor()[1])
    c[('S|A' if V3 % S == 0 else ('rad|A' if V3 % rad == 0 else 'neither'), r % 2)] += 1
print(sorted(c.items()))
# V_J vs x^(q^J)-x for J=3 over F_2
print("deg V_3 =", V3.degree(), " deg x^(q^3)-x =", 8, " equal:", V3 == x**8 + x)
