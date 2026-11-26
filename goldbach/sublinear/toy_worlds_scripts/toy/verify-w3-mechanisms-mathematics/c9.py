import itertools, random, sys, math
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
def setup(p, k):
    F = fq_default_ctx(p, k); R = fq_default_poly_ctx(F); x = R.gen()
    els = [F(list(c)) for c in itertools.product(range(p), repeat=k)]
    return F, R, x, els
def Vj(R, x, q, j):
    v = R(1)
    for i in range(1, j+1):
        g = pow(x, q**i, None) - x; v = v * (g // v.gcd(g))
    return v
def LJ(R, x, q, J):
    L = R(1)
    for m in range(1, J+1): L = L * Vj(R, x, q, J//m)
    return L
# S | L_J counts
for k, J, ds in ((1, 4, (11, 13)), (2, 2, (7,))):
    q = 2**k; F, R, x, els = setup(2, k); one = F(1)
    L = LJ(R, x, q, J)
    for d in ds:
        tot = ok = 0
        for c in itertools.product(els, repeat=d):
            Q = R(list(c)+[one])
            if not Q.is_irreducible(): continue
            co = Q.coeffs(); S = R([co[i]**(q//2) for i in range(1, d+1, 2)])
            tot += 1; ok += (L % S == 0)
        print("F_%d J=%d deg L=%d: rows of degree %d: %d, with S | L_J: %d" % (q, J, L.degree(), d, tot, ok))
# chi2
from scipy.stats import chi2_contingency, chi2
import numpy as np
a = np.array([[586,1640,1072,228,38],[295,785,544,114,15]])
c2, p, dof, _ = chi2_contingency(a, correction=False); print("r dist chi2 %.2f dof %d p %.3f" % (c2, dof, p))
b = np.array([[992, 538, 410, 550, 515, 559],[493, 286, 178, 299, 261, 236]])
c2, p, dof, _ = chi2_contingency(b, correction=False); print("least-degree chi2 %.2f dof %d p %.3f" % (c2, dof, p))
print("p for 1.39/4, 9.08/5:", chi2.sf(1.39, 4), chi2.sf(9.08, 5))
# aligned classes for larger q: rows of degree <= J+1 left for R monic of degree J+1
for p_, k, J in ((3, 2, 1), (5, 1, 2), (7, 1, 1), (2, 4, 1)):
    q = p_**k; F, R, x, els = setup(p_, k); one = F(1)
    irr = {d: [Q for Q in (R(list(c)+[one]) for c in itertools.product(els, repeat=d)) if Q.is_irreducible()] for d in range(1, J+2)}
    res = []
    for c in itertools.product(els, repeat=J+1):
        Rp = R(list(c)+[one]); left = [0]*(J+2)
        for d in range(1, J+2):
            for Q in irr[d]:
                D = Rp - Q
                if D == 0: continue
                # struck iff D has an irreducible factor of degree <= J
                if not any(h.degree() <= J for h, m in D.factor()[1]): left[d] += 1
        res.append((sum(left), left[1:]))
        if len(res) >= 400: break
    res.sort()
    print("F_%d J=%d: rows by degree %s; aligned R of degree J+1 (%d tried): best total left %s, mean %.1f, max over R of rows of degree J+1 left %d" % (
        q, J, [len(irr[d]) for d in range(1, J+2)], len(res), res[0], sum(r[0] for r in res)/len(res), max(r[1][-1] for r in res)))
