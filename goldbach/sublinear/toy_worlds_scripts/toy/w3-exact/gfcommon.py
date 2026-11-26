# Common helpers: the same objects as gfgold.c, built independently with python-flint.
# Field labels 0..q-1 (q prime: integers mod q; q = 9: a + 3b <-> a + b*i with i^2 = -1).
# Monic polynomial of degree m <-> index v = sum c_k q^k over its non-leading coefficients.
import itertools
from flint import fq_default_ctx, fq_default_poly_ctx

class World:
    def __init__(self, q):
        self.q = q
        self.p = 3 if q == 9 else q
        e = 2 if q == 9 else 1
        self.F = fq_default_ctx(self.p, e); self.R = fq_default_poly_ctx(self.F); self.x = self.R.gen()
        if q == 9:
            g = self.F.gen()
            els = [self.F(a) + self.F(b) * g for a in range(3) for b in range(3)]
            i = next(v for v in els if v * v == self.F(-1))
            self.el = [self.F(a) + self.F(b) * i for b in range(3) for a in range(3)]   # label a + 3b
        else:
            self.el = [self.F(a) for a in range(q)]
        self.lab = {str(v): k for k, v in enumerate(self.el)}
    def poly(self, v, m):
        cs = []
        for _ in range(m): cs.append(self.el[v % self.q]); v //= self.q
        return self.R(cs + [self.F(1)])
    def index(self, f):
        cs = f.coeffs(); m = len(cs) - 1
        return sum(self.lab[str(cs[k])] * self.q ** k for k in range(m)), m
    def rows(self, maxdeg, limit=None):
        out = []
        for d in range(1, maxdeg + 1):
            for v in range(self.q ** d):
                Q = self.poly(v, d)
                if Q.is_irreducible():
                    out.append(Q)
                    if limit and len(out) >= limit: return out
        return out
    def chi(self, a):          # quadratic character of F_q
        if a == 0: return 0
        return 1 if a.is_square() else -1
    def show(self, f):
        return str(f)
def ftype(f):
    lc, fac = f.factor()
    return tuple(sorted(d for g, m in fac for d in [g.degree()] * m)), all(m == 1 for g, m in fac)
