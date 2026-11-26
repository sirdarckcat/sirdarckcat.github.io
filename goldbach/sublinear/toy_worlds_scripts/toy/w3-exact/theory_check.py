# Numerical checks of the proved statements (python-flint; the resultant is computed here by Euclid's algorithm).
#  (P)  parity through the derivative: for monic f of degree n with f' != 0, e = deg f', l = lc f':
#           Res(f, f') = (-1)^(n e) l^n Res(f'/l, f),  disc f = (-1)^(n(n-1)/2) Res(f, f'),  chi(disc f) = (-1)^(n - r) for squarefree f
#  (F1) N = A(x^p) + c x:  N - (x - a) is a p-th power (c = 1) or has (-1)^(n-r) = chi(-1)^(n(n-1)/2) chi(c-1)^n (c != 1), for every a
#  (F2) N = A(x^p) + x^2 + c x:  N - (x^2 + u x + w) is a p-th power (u = c) or has (-1)^(n-r) = chi(-1)^(n(n-1)/2) chi(c-u)^n
#  (O)  orbit lemma: if N(x+b) = N(x) then N - Q and N - Q(x+b) have the same factorisation type
import random, itertools, sys
from gfcommon import World, ftype
random.seed(7)
def res(W, f, g):
    # resultant of f and g (actual degrees), by Euclid:  Res(f, g) = (-1)^(deg f deg g) lc(g)^(deg f - deg r) Res(g, r)
    F = W.F; out = F(1)
    while True:
        m, k = f.degree(), g.degree()
        if g.is_zero(): return F(0)
        if k == 0: return out * g.leading_coefficient() ** m
        r = f.divmod(g)[1]
        if r.is_zero(): return F(0)
        out = out * F(-1) ** (m * k) * g.leading_coefficient() ** (m - r.degree())
        f, g = g, r
for q in (3, 5, 7, 9):
    W = World(q); p = W.p; x = W.x; F = W.F; chi = W.chi
    rnd = lambda m: W.poly(random.randrange(q ** m), m)
    # (P)
    bad = 0; tested = 0
    for trial in range(3000):
        n = random.randint(2, 14); f = rnd(n)
        if random.random() < 0.5 and n >= p:        # make the derivative small: f = A(x^p) + low degree part
            m = n // p; f = rnd(m).compose(x ** p) * x ** (n - m * p) if False else rnd(m).compose(x ** p) + (rnd(random.randint(1, min(n - 1, 4))) if n > 1 else 0)
            n = f.degree()
            if not f.is_monic(): continue
        d = f.derivative()
        if d.is_zero(): continue
        e = d.degree(); l = d.leading_coefficient()
        R1 = res(W, f, d); R2 = F(-1) ** (n * e) * l ** n * res(W, d * (1 / l), f)
        disc = F(-1) ** (n * (n - 1) // 2) * R1
        typ, sqf = ftype(f); r = len(typ)
        ok = (R1 == R2) and ((disc == 0) == (not sqf)) and (not sqf or chi(disc) == (-1) ** (n - r))
        ok = ok and (not sqf or chi(disc) == chi(F(-1)) ** (n * (n - 1) // 2 + n * e) * chi(l) ** n * chi(res(W, d * (1 / l), f)))
        bad += not ok; tested += 1
    print(f"F_{q}: (P) {tested} random monic f (half of them A(x^p) + low degree): failures {bad}")
    # (F1), (F2)
    for m in (1, 2, 3):
        n = p * m; b1 = b2 = t1 = t2 = 0; forced1 = forced2 = 0; fam1 = fam2 = 0
        for trial in range(60):
            A = rnd(m).compose(x ** p)
            for c in W.el:
                N = A + c * x; fam1 += 1; allred = True
                for a in W.el:
                    f = N - (x - a); typ, sqf = ftype(f); r = len(typ); t1 += 1
                    if c == F(1): ok = f.derivative().is_zero() and all(mm % p == 0 for g, mm in f.factor()[1])
                    else: ok = sqf and (-1) ** (n - r) == chi(F(-1)) ** (n * (n - 1) // 2) * chi(c - 1) ** n
                    b1 += not ok; allred &= (r > 1)
                forced1 += allred
                if p > 2 and n > 2:
                    N = A + x * x + c * x; fam2 += 1; allred = True
                    for u in W.el:
                        for w in W.el:
                            f = N - (x * x + u * x + w); typ, sqf = ftype(f); r = len(typ); t2 += 1
                            if u == c: ok = f.derivative().is_zero() and r >= p
                            else: ok = sqf and (-1) ** (n - r) == chi(F(-1)) ** (n * (n - 1) // 2) * chi(c - u) ** n
                            b2 += not ok; allred &= (r > 1)
                    forced2 += allred
        print(f"F_{q}: n={n}: (F1) {t1} pairs, failures {b1}; members with all q linear rows reducible: {forced1}/{fam1}"
              f" | (F2) {t2} pairs, failures {b2}; members with all q^2 monic quadratics reducible: {forced2}/{fam2}")
    # (O)
    bad = 0; tested = 0
    rows = W.rows(3)
    for trial in range(40):
        m = random.randint(1, 3); y = x ** p - x; N = rnd(m).compose(y)
        for Q in rows:
            for b in range(1, p):
                tested += 1; bad += ftype(N - Q) != ftype(N - Q.compose(x + F(b)))
    print(f"F_{q}: (O) {tested} (N, Q, b) with N in F_q[x^p - x]: type mismatches {bad}")
