# Verifier: independent flint checks of family statements (does not import the page's code).
import itertools, sys, math
from flint import fq_default_ctx, fq_default_poly_ctx
def world(q):
    p = 3 if q == 9 else q
    F = fq_default_ctx(p, 2 if q == 9 else 1); R = fq_default_poly_ctx(F); x = R.gen()
    if q == 9:
        g = F.gen(); els0 = [F(a) + F(b) * g for a in range(3) for b in range(3)]
        i = next(v for v in els0 if v * v == F(-1))
        # choose i: two square roots of -1; the page takes "next" in its own order. record both
        el = [F(a) + F(b) * i for b in range(3) for a in range(3)]
    else:
        el = [F(a) for a in range(q)]
    return p, F, R, x, el
def poly(R, F, el, q, v, m):
    cs = []
    for _ in range(m): cs.append(el[v % q]); v //= q
    return R(cs + [F(1)])
def rows_upto(R, F, el, q, maxdeg):
    out = []
    for d in range(1, maxdeg + 1):
        for v in range(q ** d):
            Q = poly(R, F, el, q, v, d)
            if Q.is_irreducible(): out.append(Q)
    return out
def GD(N, rows, n):
    for i, Q in enumerate(rows):
        if (N - Q).is_irreducible(): return i, Q.degree()
    return len(rows), n
if __name__ == "__main__":
    q, n, maxdeg = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    p, F, R, x, el = world(q)
    rows = rows_upto(R, F, el, q, min(maxdeg, n - 1))
    cnt = {}
    for Q in rows: cnt[Q.degree()] = cnt.get(Q.degree(), 0) + 1
    print("q", q, "n", n, "rows by degree", cnt)
    m = n // p
    # (1) N' = 0 : N = A(x^p)
    best = None
    for cs in itertools.product(el, repeat=m):
        A = R(list(cs) + [F(1)]); N = A.compose(x ** p)
        g, d = GD(N, rows, n)
        if best is None or g > best[0]: best = (g, d, N)
    print("  N'=0 family size", q ** m, "best G", best[0], "D", best[1], "(valid only if best D <= maxdeg)")
    # (2) translation-invariant: N = A(x^p - x) (q prime: full group; q=9: subgroup F_3)
    y = x ** p - x; res = []
    for cs in itertools.product(el, repeat=m):
        A = R(list(cs) + [F(1)]); N = A.compose(y); res.append((GD(N, rows, n), N))
    for d in range(2, maxdeg + 2):
        print("  transl family D>=%d: %d of %d" % (d, sum(1 for (g, dd), N in res if dd >= d), len(res)))
    b = max(res, key=lambda t: t[0][0]); print("  transl family best G", b[0], b[1])
    # T2(ii) cap for q prime
    if q == p:
        I = cnt; viol = 0; tight = 0
        for (g, d), N in res:
            if d < n and d % p != 0 and d in I:
                cap = sum(I[j] for j in range(1, d)) + I[d] // p - 1
                viol += g > cap; tight += g == cap
        print("  T2(ii) cap violations", viol, "tight cases", tight)
