# general finite-field helper (verifier's own code)
import itertools, random
from flint import fq_default_ctx, fq_default_poly_ctx
class FF:
    def __init__(self, p, e=1):
        self.p = p; self.e = e; self.q = p**e
        self.F = fq_default_ctx(p, e, var='z')
        self.R = fq_default_poly_ctx(self.F)
        self.x = self.R.gen()
        z = self.F.gen() if e > 1 else self.F(1)
        self.els = []
        for t in itertools.product(range(p), repeat=e):
            el = self.F(0)
            for i, c in enumerate(t):
                el = el + self.F(c) * z**i
            self.els.append(el)
        assert len(set(str(t) for t in self.els)) == self.q
        self.zero = self.F(0); self.one = self.F(1)
    def tr(self, c):
        t = self.zero; y = c
        for i in range(self.e):
            t = t + y; y = y**self.p
        return t
    def monics(self, d):
        for t in itertools.product(self.els, repeat=d):
            yield self.R(list(t) + [self.one])
    def irreducibles(self, d):
        return [f for f in self.monics(d) if f.is_irreducible()]
    def rand_monic(self, d, rng):
        return self.R([rng.choice(self.els) for _ in range(d)] + [self.one])
    def rand_poly(self, dmax, rng):
        return self.R([rng.choice(self.els) for _ in range(dmax+1)])
    def nfac(self, f):
        lead, fs = f.factor()
        return sum(m for _, m in fs)
