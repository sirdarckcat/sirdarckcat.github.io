import random, math, re
from fam import world
# (A) F2 forcing: q=3 n=12 (4 | n) all members; q=7 n=28 sample; q=3 n=6 (not forced: parity odd)
random.seed(3)
for q, n, full in ((3, 12, True), (7, 28, False), (3, 6, True), (7, 14, False), (5, 10, False)):
    p, F, R, x, el = world(q); m = n // p; tot = forced = 0; odd_all = True; even_all = True
    import itertools
    it = itertools.product(el, repeat=m + 1) if full else [tuple(random.choice(el) for _ in range(m + 1)) for _ in range(25)]
    for cs in it:
        A = R(list(cs[:m]) + [F(1)]); N = A.compose(x ** p) + x * x + cs[m] * x; tot += 1; ok = True
        for u in el:
            for w in el:
                f = N - (x * x + u * x + w); fac = f.factor()[1]; r = sum(mm for _, mm in fac)
                ok &= r > 1
                if u != cs[m]: odd_all &= (r % 2 == 1); even_all &= (r % 2 == 0)
        forced += ok
    print(f"F2 q={q} n={n}: members tested {tot}, all q^2 quadratics reducible for {forced}; for u != c: r always even: {even_all}, always odd: {odd_all}")
# (B) tail levels and naive first-moment ratios from my own histograms
for q, n in ((3, 16), (5, 11), (7, 9), (9, 8), (3, 18)):
    H = sorted((int(a), int(b)) for a, b in (l.split() for l in open(f"gh_{q}_{n}.txt")))
    tot = q ** n; In = None
    for fn in ("enum_mid.txt", "enum_big.txt"):
        L = open(fn).read().split("\n")
        for i, s in enumerate(L):
            if s.startswith(f"q {q} n {n} "): In = int(L[i + 1].split()[-1])
    rho = In / tot
    def surv(g): return sum(c for gg, c in H if gg >= g)
    lev = []
    for k in range(1, 7):
        g = 0
        while surv(g) >= 10 ** -k * tot: g += 1
        lev.append(g)
    Gmax = H[-1][0]
    print(f"({q},{n}) levels {lev}; naive max {math.log(tot) / -math.log(1 - rho):.1f} vs Gmax {Gmax}; hits/naive at levels k=2..6: " + ", ".join(f"{surv(g) / (tot * (1 - rho) ** g):.3g}" for g in lev[1:]))
