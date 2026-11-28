import itertools, random, sys, math
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
random.seed(8)
def setup(p, k):
    F = fq_default_ctx(p, k); R = fq_default_poly_ctx(F); x = R.gen()
    els = [F(list(c)) for c in itertools.product(range(p), repeat=k)]
    return F, R, x, els
def nfac(f): return sum(m for _, m in f.factor()[1])
def irreds(R, els, d, one):
    return [Q for Q in (R(list(c) + [one]) for c in itertools.product(els, repeat=d)) if Q.is_irreducible()]
# direct: d=4, q3=0 => r(N-Q) = k*a mod 2
tot = bad = 0
for k in (1,2,3,4):
    F, R, x, els = setup(2, k); zero, one = F(0), F(1)
    for t in range(1000):
        Q = R([random.choice(els), random.choice(els[1:]), random.choice(els), zero, one])
        a = random.randint(2, 7); A = R([random.choice(els) for _ in range(a)] + [one]); lam = random.choice(els[1:])
        f = lam*A**4 - Q
        r = nfac(f); tot += 1; bad += (r - k*a) % 2
print("d=4,q3=0: r(N-Q)=k*a mod 2:", tot, "cases,", bad, "bad")
# Carlitz degree with a = 1 over F_3
F, R, x, els = setup(3, 1); one = F(1)
def carlitz(M, a):
    co = M.coeffs(); res = R(0); cur = a   # cur = C_{T^i}(a)
    for c in co:
        res += c*cur; cur = x*cur + cur**3
    return res
for Lam in (x, x*x+1, x**3+2*x+1, x**4+x+2):
    print("deg C_Lam(1) for deg Lam =", Lam.degree(), ":", carlitz(Lam, R(1)).degree(), " deg C_Lam(x):", carlitz(Lam, x).degree())
# Prop 4: F_3, J=3, R quartic strikes every row of degree<=4 ?
irr = {d: irreds(R, els, d, one) for d in (1,2,3,4)}
small = irr[1]+irr[2]+irr[3]
best = []
for c in itertools.product(els, repeat=4):
    Rp = R(list(c)+[one]); left = 0
    for d in (1,2,3,4):
        for Q in irr[d]:
            D = Rp - Q
            if D == 0: continue
            if not any(D % pi == 0 for pi in small): left += 1
    best.append((left, str(Rp)))
best.sort(); print("Prop 4, F_3 J=3: rows of degree<=4 left, best quartic R:", best[:3], "count with 0 left:", sum(1 for b in best if b[0]==0), "of 81; max left", best[-1])
# Theorem 3 counts
def tr_p(v, p, e):
    s = v*0; w = v
    for _ in range(e): s += w; w = w**p
    return s
for p, e, degs in ((3,1,(1,2,3)), (3,2,(1,2)), (2,2,(1,2,3)), (5,1,(1,2))):
    F, R, x, els = setup(p, e); one = F(1); zero = F(0)
    out = []
    for m in degs:
        Cs = irreds(R, els, m, one)
        rows = [C for C in Cs if (C(x**p - x)).is_irreducible()]
        out.append((p*m, len(rows)))
        # check criterion: irreducible iff Tr(second coeff) != 0
        for C in Cs:
            assert (C(x**p-x)).is_irreducible() == (tr_p(C.coeffs()[m-1], p, e) != zero)
    print("F_%d rows C(x^p-x): (degree, count)" % (p**e), out)
# Theorem 3 small exhaustive check over F_3: A of degree 4, trace 0 (a=0), all C of degree<=2 rows
F, R, x, els = setup(3, 1); one = F(1); zero = F(0)
cnt = Counter()
rowsC = [C for m in (1,2) for C in irreds(R, els, m, one) if C.coeffs()[m-1] != zero]
for c in itertools.product(els, repeat=3):
    for a in els:
        A = R(list(c) + [a, one])
        for C in rowsC:
            g = A - C; f = g(x**3 - x)
            fac = f.factor()[1]
            if a == zero:
                if g.is_irreducible(): cnt['tr0: g irr -> 3 factors of deg m', len(fac) == 3 and all(h.degree()==4 and mm==1 for h, mm in fac)] += 1
                else: cnt['tr0: g red', f.is_irreducible()] += 1
            else:
                cnt['tr!=0: irr(f)==irr(g)', f.is_irreducible() == g.is_irreducible()] += 1
print(dict(cnt))
