import random, itertools, numpy as np, os
from vlib import W
from compare1 import mine
random.seed(4242)
def chi(w, c):
    assert c != w.els[0]; return 1 if c ** ((w.q - 1) // 2) == w.els[1] else -1
def res(w, A, B):
    # resultant by Euclid
    a, b = A.degree(), B.degree()
    if b == 0: return B.coeffs()[0] ** a
    R = A % B
    if R == 0: return w.els[0]
    r = R.degree(); sgn = -1 if (a * b) % 2 else 1
    lcB = B.coeffs()[-1]
    return res(w, B, R) * lcB ** (a - r) * (w.els[1] if sgn == 1 else -w.els[1])
def nfac(f):
    c, fl = f.factor(); return sum(e for g, e in fl), all(e == 1 for g, e in fl), fl
fails = {"T3": 0, "F1": 0, "F2": 0, "T2": 0}; tests = {"T3": 0, "F1": 0, "F2": 0, "T2": 0}
for q in (3, 5, 7, 9):
    w = W(q); p = w.p; x = w.x; one = w.els[1]
    # T3
    for _ in range(1500):
        n = random.randint(2, 14); f = w.poly(random.randrange(q ** n), n); fp = f.derivative()
        if fp == 0: continue
        r, sqf, fl = nfac(f)
        if not sqf: continue
        e = fp.degree(); l = fp.coeffs()[-1]; g = fp * (one / l)
        R = res(w, g, f) if e > 0 else one
        pred = (chi(w, -one) ** ((n * (n - 1) // 2 + n * e) % 2)) * (chi(w, l) ** (n % 2)) * chi(w, R)
        tests["T3"] += 1
        if pred != (-1) ** (n - r): fails["T3"] += 1
    # F1, F2
    for _ in range(60):
        m = random.randint(1, 4); n = p * m; A = w.poly(random.randrange(q ** m), m)(x ** p)
        for c in w.els:
            N = A + c * x
            for a in w.els:
                f = N - (x - a); r, sqf, fl = nfac(f); tests["F1"] += 1
                if c == one: ok = all(e % p == 0 for g, e in fl)
                else: ok = sqf and (-1) ** (n - r) == chi(w, -one) ** ((n * (n - 1) // 2) % 2) * chi(w, c - one) ** (n % 2)
                if not ok: fails["F1"] += 1
            N2 = A + x * x + c * x
            if n > 2:
                for u in w.els:
                    wv = random.choice(w.els); f = N2 - (x * x + u * x + wv); r, sqf, fl = nfac(f); tests["F2"] += 1
                    if u == c: ok = all(e % p == 0 for g, e in fl)
                    else: ok = sqf and (-1) ** (n - r) == chi(w, -one) ** ((n * (n - 1) // 2) % 2) * chi(w, c - u) ** (n % 2)
                    if not ok: fails["F2"] += 1
    # T2 orbit lemma, translations and general affine maps
    for _ in range(200):
        m = random.randint(1, 3); n = p * m; c = random.choice(w.els[1:]); y = x ** p - c ** (p - 1) * x
        N = w.poly(random.randrange(q ** m), m)(y); b = c * random.randrange(1, p)
        assert N(x + b) == N
        d = random.randint(1, n - 1); Q = w.poly(random.randrange(q ** d), d); Qh = Q(x + b)
        t1 = sorted((g.degree(), e) for g, e in (N - Q).factor()[1]); t2 = sorted((g.degree(), e) for g, e in (N - Qh).factor()[1])
        tests["T2"] += 1
        if t1 != t2 or Q.is_irreducible() != Qh.is_irreducible(): fails["T2"] += 1
print("checks (tests, failures):", tests, fails)
# F2 forced for all q^2 quadratics when n even and (q=1 mod 4 or 4|n); not forced otherwise
for q, n in [(9, 6), (5, 10), (3, 12), (3, 6), (7, 14), (9, 12), (7, 28)]:
    w = W(q); p = w.p; x = w.x; m = n // p; bad = 0; tot = 0
    for _ in range(40):
        N = w.poly(random.randrange(q ** m), m)(x ** p) + x * x + random.choice(w.els) * x
        for v in range(q * q):
            Q = w.poly(v, 2); tot += 1
            if (N - Q).is_irreducible(): bad += 1
    print(f"F2 q={q} n={n}: N-Q irreducible in {bad} of {tot} (member, monic quadratic) pairs; forced by statement: {(q % 4 == 1) or n % 4 == 0}")
# F2 at (9,6) against the enumeration
w = W(9); x = w.x; g = np.fromfile("out/v_9_6.g16", dtype=np.uint16)
fam = [w.poly(v, 2)(x ** 3) + x * x + c * x for v in range(81) for c in w.els]
idx = [w.index(N) for N in fam]; Gs = [int(g[i]) for i in idx]
print("F2 (9,6): members", len(set(idx)), "with G>=45 (i.e. D>=3):", sum(1 for G in Gs if G >= 45), "min G over family:", min(Gs), "with G>=9:", sum(1 for G in Gs if G >= 9),
      "; all N with D>=3:", int((g >= 45).sum()), "; top-3 of all N in F2:", [int(i) in set(idx) for i in np.argsort(-g.astype(int), kind='stable')[:3]])
irrq = [P for v, P in w.irreducibles(2)]
cube = par = irr = 0
for N in fam[:729]:
    for Q in irrq:
        f = N - Q; c_, fl = f.factor()
        if all(e % 3 == 0 for gg, e in fl): cube += 1
        elif len(fl) == 1 and fl[0][1] == 1: irr += 1
        else: par += 1
print("F2 (9,6): per member quadratic rows: cubes", cube / 729, "reducible squarefree", par / 729, "irreducible", irr / 729)
# translation-invariant families overlap with F2 at (9,6)?
# reflection family
def rowsbelow(q, n):
    for line in open(f"out/v_{q}_{n}.txt"):
        if line.startswith("rows_below"): return [int(t) for t in line.split()[1:]]
for q, n in [(3, 14), (9, 8), (7, 8), (5, 9), (5, 8), (3, 10)]:
    w = W(q); x = w.x; g = np.fromfile(f"out/v_{q}_{n}.g16", dtype=np.uint16).astype(np.int64); rb = rowsbelow(q, n); m = n // 2
    fam = set()
    for x0 in w.els:
        u = (x - x0) ** 2
        for v in range(q ** m):
            N = w.poly(v, m)(u)
            if n % 2: N = N * (x - x0)
            fam.add(w.index(N))
    fi = np.array(sorted(fam)); gf = g[fi]; hdr, gh, gh0, dh, dh0, top, lst = mine(q, n); Dmax = max(dh)
    out = []
    for d in range(2, Dmax + 1):
        thr = rb[d - 1]; F = int((gf >= thr).sum()); K = int((g >= thr).sum()); out.append(f"d={d}: {F}/{K} enr {F / len(fi) / (K / q ** n):.2f}")
    print(f"reflection q={q} n={n}: {len(fi)} members; " + "; ".join(out))
# optimum of (3,18) as a polynomial, G recomputed directly
w = W(3); N = w.poly(40060310, 18); print("(3,18) optimum:", N)
rows = [(d, P) for d in range(1, 9) for v, P in w.irreducibles(d)]
print("   direct flint G:", next(i for i, (d, Q) in enumerate(rows) if (N - Q).is_irreducible()), "rows of degree<=8:", len(rows))
