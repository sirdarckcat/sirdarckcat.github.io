import flint
class W:
    def __init__(s, q):
        s.q = q
        if q == 9:
            s.F = flint.fq_default_ctx(3, 2, var="i", modulus=flint.fmpz_mod_poly_ctx(3)([1,0,1]))
            s.els = [s.F([a, b]) for b in range(3) for a in range(3)]
        else:
            s.F = flint.fq_default_ctx(q, 1); s.els = [s.F(a) for a in range(q)]
        s.R = flint.fq_default_poly_ctx(s.F)
        s.lab = {e: k for k, e in enumerate(s.els)}
        s.x = s.R([s.els[0], s.els[1]])
        s.p = 3 if q == 9 else q
    def poly(s, v, d):
        c = []
        for _ in range(d): c.append(s.els[v % s.q]); v //= s.q
        c.append(s.els[1]); return s.R(c)
    def index(s, P):
        cs = P.coeffs(); d = len(cs) - 1; assert cs[-1] == s.els[1]
        return sum(s.lab[cs[k]] * s.q ** k for k in range(d))
    def monics(s, d):
        for v in range(s.q ** d): yield s.poly(v, d)
    def irreducibles(s, d):
        for v in range(s.q ** d):
            P = s.poly(v, d)
            if P.is_irreducible(): yield v, P
    def family(s, n, sq):   # N = F(x^p - sq*x), F monic of degree n/p; sq = c^(p-1) (a label)
        y = s.x ** s.p - s.els[sq] * s.x; m = n // s.p; out = []
        for v in range(s.q ** m):
            F = s.poly(v, m); out.append(F(y))
        return out
    def GD(s, N, rows, maxdeg=None):
        # rows: list of (d, Q) in order. returns (G, D)
        n = N.degree()
        for i, (d, Q) in enumerate(rows):
            if (N - Q).is_irreducible(): return i, d
        return len(rows), None
