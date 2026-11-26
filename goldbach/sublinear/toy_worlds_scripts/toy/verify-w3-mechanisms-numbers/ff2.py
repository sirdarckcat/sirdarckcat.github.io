# independent helpers for characteristic 2 (verifier's own code)
import itertools, random
from flint import fq_default_ctx, fq_default_poly_ctx

class W:
    def __init__(self, k):
        self.k = k; self.q = 2**k
        self.F = fq_default_ctx(2, k, var='z')
        self.R = fq_default_poly_ctx(self.F)
        self.x = self.R.gen()
        z = self.F.gen() if k > 1 else self.F(1)
        self.els = []
        for i in range(self.q):
            e = self.F(0)
            for b in range(k):
                if (i >> b) & 1:
                    e = e + z**b
            self.els.append(e)
        assert len(set(str(e) for e in self.els)) == self.q
    def tr(self, c):
        t = self.F(0); y = c
        for i in range(self.k):
            t = t + y; y = y*y
        assert t == self.F(0) or t == self.F(1)
        return 0 if t == self.F(0) else 1
    def sqrt(self, c):
        y = c
        for i in range(self.k-1):
            y = y*y
        assert y*y == c
        return y
    def poly(self, coeffs):
        return self.R(list(coeffs))
    def monics(self, d):
        for t in itertools.product(self.els, repeat=d):
            yield self.R(list(t) + [self.F(1)])
    def irreducibles(self, d):
        return [f for f in self.monics(d) if f.is_irreducible()]
    def rand_monic(self, d, rng):
        return self.R([rng.choice(self.els) for _ in range(d)] + [self.F(1)])
    def V(self, j):
        # product of monic irreducibles of degree <= j = lcm_{i<=j} (x^(q^i) - x)
        P = self.R([1])
        for i in range(1, j+1):
            g = self.x**(self.q**i) + self.x
            P = P * g.exact_division(P.gcd(g)) if hasattr(g, 'exact_division') else P*(g // P.gcd(g))
        return P
    def L(self, J):
        P = self.R([1])
        for m in range(1, J+1):
            P = P * self.V(J // m)
        return P
    def S_of(self, Q):
        # Q' = S^2
        c = Q.derivative().coeffs()
        assert all(c[i] == self.F(0) for i in range(1, len(c), 2))
        return self.R([self.sqrt(c[i]) for i in range(0, len(c), 2)]) if c else self.R([0])
    def nfac(self, f):
        lead, fs = f.factor()
        return sum(e for _, e in fs), all(e == 1 for _, e in fs)

def predicted(w, lam, A, Q, rQ):
    """Theorem 1 prediction of r(N-Q) mod 2, or None if hypotheses fail."""
    k = w.k; a = A.degree(); n = 4*a; d = Q.degree()
    if d >= n: return None
    S = w.S_of(Q)
    if S.is_zero(): return None
    if not (A % S).is_zero(): return None
    c = Q.coeffs()
    if d % 2 == 1:
        return (rQ + 1 + k*(a + (d*d-1)//8)) % 2
    if c[d-1] == w.F(0): return None
    if n - d < 4: return None
    if d % 4 == 0:
        return (rQ + k*(a + d//4)) % 2
    return (rQ + k*(a + (d-2)//4) + w.tr(c[d-2]/(c[d-1]*c[d-1]))) % 2
