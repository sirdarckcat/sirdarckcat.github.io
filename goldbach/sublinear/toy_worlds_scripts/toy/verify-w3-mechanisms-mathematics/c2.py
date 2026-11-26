import itertools, random, sys
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
def setup(p, k):
    F = fq_default_ctx(p, k); R = fq_default_poly_ctx(F); x = R.gen()
    els = [F(list(c)) for c in itertools.product(range(p), repeat=k)]
    return F, R, x, els
def nfac(f): return sum(m for _, m in f.factor()[1])
def irreds(R, els, d):
    one = els[0]*0+1
    out = []
    for c in itertools.product(els, repeat=d):
        Q = R(list(c) + [one])
        if Q.is_irreducible(): out.append(Q)
    return out
# (a) corollary instances
for k in (2, 4):
    F, R, x, els = setup(2, k); q = 2**k
    N = x**(4*q) + x**4
    cnt = Counter()
    for d in (1, 2, 3):
        for Q in irreds(R, els, d):
            r = nfac(N + Q); cnt[(d, r % 2, r == 1)] += 1
    print("F_%d: x^(4q)+x^4+Q, (deg, r mod 2, irreducible): " % q, dict(cnt))
# (b) counts over F_4
F, R, x, els = setup(2, 2); q = 4; zero = F(0); one = F(1)
def tr(v, k=2):
    s = zero; w = v
    for _ in range(k): s += w; w = w*w
    return 0 if s == zero else 1
sext = irreds(R, els, 6)
c = Counter()
for Q in sext:
    co = Q.coeffs()
    c['q5=0' if co[5] == zero else 'tr=%d' % tr(co[4]/co[5]**2)] += 1
print("F_4 sextics:", len(sext), dict(c))
quart = irreds(R, els, 4)
print("F_4 quartics:", len(quart), "with q3=0:", sum(1 for Q in quart if Q.coeffs()[3] == zero))
# forced-fraction of rows up to degree 2J+2 for q=4 (theorem only)
from sympy import mobius, divisors
def Nd(q, d): return sum(mobius(e) * q ** (d // e) for e in divisors(d)) // d
