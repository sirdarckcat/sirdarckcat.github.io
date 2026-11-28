#!/usr/bin/env python3
import math, random, numpy as np, sympy, flint, itertools
COVER = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
Q = 200000
line = [x for x in open(COVER) if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
rows = np.array([q for q in sympy.primerange(3, Q) if all(q % r != a for r, a in cov)]); n = len(rows)
K = 21378978
# 1. h(t)/t minimum  (sharper floor: certified work factor C needs ln E >= n ln(c0 n / ln C))
h = lambda t: math.log((1 + 2 * t) / (1 - t))
c0 = min(h(i / 1e5) / (i / 1e5) for i in range(1, 100000)); print("min h(t)/t on (0,1):", c0, " => certified factor <= e needs ln E/n >= ln n +", math.log(c0))
# 2. certificate in the REAL window with density-1/2 progressions: which m has prod(1+2tau)/prod(1-tau) <= e ?
def reduced(sl, el, ell):
    nn = len(sl) + 1; SC = max(ell) << 40; w = [SC // l for l in ell]
    G = [[0] * nn for _ in range(nn)]; G[0][0] = 1
    for i, (s, e) in enumerate(zip(sl, el)): G[0][i + 1] = e; G[i + 1][i + 1] = s
    A = flint.fmpz_mat([[G[i][j] * w[j] for j in range(nn)] for i in range(nn)]).lll(delta=0.99, eta=0.51)
    return [[int(A[i, j]) // w[j] for j in range(nn)] for i in range(nn)]
LP = list(sympy.primerange(467, 5000)); random.seed(99)
print("real window, random progressions; fraction of 40 draws with certified factor <= e, median factor, median ln E/n:")
for dens in (2, 4, 8):
  for m in (1, 2, 3, 4, 5, 6):
    sl = LP[:m]; fac = []; ce = []
    for rep in range(40):
        lists = [(random.randrange(s), random.randrange(1, s), s // dens) for s in sl]
        el = [pow(d, -1, s) for s, (a, d, L) in zip(sl, lists)]; ell = [K] + [L for a, d, L in lists]
        B = reduced(sl, el, ell); nn = m + 1
        tau = [sum(abs(B[i][j]) for i in range(nn)) / ell[j] for j in range(nn)]
        E = K * math.prod(L / s for s, (a, d, L) in zip(sl, lists))
        assert math.prod(tau) * E >= 1 - 1e-9
        fac.append(math.prod(1 + 2 * t for t in tau) / math.prod(1 - t for t in tau) if max(tau) < 1 else float("inf")); ce.append(math.log(E) / nn)
    print(f"   density 1/{dens}  m={m} (n={m+1}): certified<=e in {sum(f <= math.e for f in fac)}/40; median factor {np.median(fac):.3g}; ln E/n = {np.median(ce):.2f}; floor ln n + {math.log(c0):.2f} = {math.log(nn)+math.log(c0):.2f}")
# 3. Parseval: mean nontrivial multiplicative character power == function of the table variance
print("Parseval identity: mean |sum chi(q)|^2/m over nontrivial chi  vs  [(s-1) sum a_c^2 - m^2]/((s-2) m)  and var/mean of the table")
for s in (467, 1009, 4999):
    c = rows % s; nz = c[c != 0]; m = len(nz); a = np.bincount(nz, minlength=s)[1:].astype(float)
    g = sympy.primitive_root(s); dl = np.zeros(s, dtype=np.int64); x = 1
    for j in range(s - 1): dl[x] = j; x = x * g % s
    P = np.abs(np.fft.fft(np.bincount(dl[nz], minlength=s - 1).astype(float))) ** 2 / m
    t = np.bincount(c, minlength=s)
    print(f"   s={s}: direct {P[1:].mean():.6f}  identity {((s-1)*(a*a).sum()-m*m)/((s-2)*m):.6f}  table var/mean {t.var()/t.mean():.6f}")
# 4. Prop E quantitative: decomposition of the common-integer covariance
print("Prop E: Cov_c<s(f_s, f_s') = Var(1_R) + Cov(1_R,g') + Cov(g,1_R) + Cov(g,g'), g = other rows of the class; means over pairs")
for lo, hi, cnt in ((467, 1000, 78), (2000, 5000, 120), (20000, 60000, 120)):
    pr = list(sympy.primerange(lo, hi)); step = max(1, len(pr) // cnt); pr = pr[::step]
    ind = np.zeros(Q, dtype=float); ind[rows] = 1
    tabs = {s: np.bincount(rows % s, minlength=s).astype(float) for s in pr}
    acc = np.zeros(5); corr = []; pred = []; pred2 = []
    for i, s in enumerate(pr):
        one = ind[:s]; g = tabs[s] - one
        for s2 in pr[i + 1:]:
            f2 = tabs[s2][:s]; g2 = f2 - one
            cv = lambda x, y: np.mean(x * y) - x.mean() * y.mean()
            parts = np.array([cv(one, one), cv(one, g2), cv(g, one), cv(g, g2), cv(tabs[s], f2)]); acc += parts
            den = math.sqrt(tabs[s].var() * f2.var()); corr.append(parts[4] / den); pred.append((one.sum() / s) / den); pred2.append(parts[0] / den)
    acc /= len(corr)
    print(f"   [{lo},{hi}): pairs {len(corr)}; mean corr {np.mean(corr):+.5f}; page's prediction {np.mean(pred):+.5f}; Var(1_R) only {np.mean(pred2):+.5f};"
          f" parts: Var(1_R) {acc[0]:.3e}, Cov(1_R,g') {acc[1]:.3e}, Cov(g,1_R) {acc[2]:.3e}, Cov(g,g') {acc[3]:.3e}, total {acc[4]:.3e}")
# 5. progression lists above Q: rate of a pin on a row, and of short APs made of rows, at s just above Q
s = sympy.nextprime(Q); R = set(int(x) for x in rows)
print(f"s = {s}: pin on a row: {(1 - n / s) / math.log(s):.4f} rows/nat; full progression 1 mod 6: {(6 * n / Q - n / s) / math.log(6 * s / Q):.4f}")
best = {}
for L in (2, 3, 4, 5, 6):
    found = None
    for d in range(6, 3000, 6):
        for q in rows:
            if all(int(q) + i * d in R for i in range(L)): found = (int(q), d); break
        if found: break
    if found: print(f"   AP of {L} rows: start {found[0]} diff {found[1]}: rate {(1 - n / s) / math.log(s / L):.4f} rows/nat")
for D in (6, 30, 210, 2310, 30030):
    cnt = np.bincount(rows % D, minlength=D); b = int(np.argmax(cnt)); L = (Q - 1 - b) // D + 1
    print(f"   best class mod {D}: {cnt.max()} rows in {L} classes: rate {(cnt.max() / L - n / s) / math.log(s / L):.4f} rows/nat")
