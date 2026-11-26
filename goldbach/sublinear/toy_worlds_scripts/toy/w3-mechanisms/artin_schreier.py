# Mechanism "Artin-Schreier / composition":  L = x^p - x over F_q (q = p^e).
# Varshamov: for g in F_q[y] monic of degree m,  g(L(x)) is irreducible  iff  g is irreducible and
#            Tr_{F_q/F_p}(coefficient of y^(m-1) of g) != 0.
# Forcing: N = A(L), A = y^m + a y^(m-1) + ..., Tr(a) = 0.  Then N - Q is reducible for EVERY row of the form Q = C(L),
#          deg C <= m - 2  (these are exactly the rows fixed by x -> x + 1).
#   python3 artin_schreier.py p e cmax m nA seed
import itertools, random, sys
from flint import fq_default_ctx, fq_default_poly_ctx
p, e, cmax, m, nA, seed = (int(v) for v in sys.argv[1:7]); random.seed(seed); q = p ** e
F = fq_default_ctx(p, e); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(p), repeat=e)]
def tr(v):
    s = F(0); w = v
    for _ in range(e): s += w; w = w ** p
    return s
L = x ** p - x
rows = []; tot_irr = {}
for c in range(1, cmax + 1):
    cnt = 0
    for co in itertools.product(els, repeat=c):
        C = R(list(co) + [F(1)])
        if not C.is_irreducible(): continue
        Q = C(L); irr = Q.is_irreducible()
        assert irr == (tr(co[-1]) != 0)                 # Varshamov on the rows themselves
        if irr: rows.append((C, Q)); cnt += 1
    tot_irr[c] = cnt
print(f"F_{q}: rows of the form C(x^{p} - x): " + ", ".join(f"degree {p*c}: {v}" for c, v in tot_irr.items()))
for trace_zero in (True, False):
    red = irr = 0; viol = 0; pat = set()
    for _ in range(nA):
        while True:
            a = random.choice(els)
            if (tr(a) == 0) == trace_zero: break
        A = R([random.choice(els) for _ in range(m - 1)] + [a, F(1)])
        N = A(L)
        for C, Q in rows:
            f = N - Q; g = A - C
            if f.is_irreducible():
                irr += 1
                if trace_zero or not g.is_irreducible(): viol += 1
            else:
                red += 1
                if (not trace_zero) and g.is_irreducible(): viol += 1
    print(f"  A of degree {m} (deg N = {p*m}), Tr(second coefficient) {'= 0' if trace_zero else '!= 0'}: {nA} random A x {len(rows)} rows: "
          f"N - Q reducible {red}, irreducible {irr}, violations of the rule {viol}")
