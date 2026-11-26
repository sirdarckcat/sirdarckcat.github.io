# Does the parity desert (odd characteristic, Result 1) force more than parity?
# F_9, J = 2, V = x^81 - x, lam a non-square.  Desert:  N = lam * (V*B)^3 (N' = 0), B monic of degree 2.
# Control:  Nc = N + V*C, C random of degree < deg N - 81 - 1 (same degree, same leading coefficient, Nc = 0 mod V too,
# so N - Q and Nc - Q are both free of factors of degree <= 2; but Nc' != 0).
# Rows: every monic irreducible Q of degree 4 whose derivative is 2-smooth.
# Output: histogram of r = number of irreducible factors, and of the least factor degree, for both;
# chi-square for homogeneity between (desert) and (control restricted to r even).
#   python3 parity_only.py nB seed
import itertools, random, sys
from collections import Counter
from flint import fq_default_ctx, fq_default_poly_ctx
nB = int(sys.argv[1]); random.seed(int(sys.argv[2]))
F = fq_default_ctx(3, 2); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(3), repeat=2)]
lam = next(v for v in els if v != 0 and not v.is_square())
V = pow(x, 81, None) - x
rows = []
for d in (4,):          # degree 4 only: p = 3 does not divide 4, so the parity is forced even (rows of degree 3 follow the sign rule for p | d and are mixed)
    for c in itertools.product(els, repeat=d):
        Q = R(list(c) + [F(1)])
        if not Q.is_irreducible(): continue
        D = Q.derivative()
        if D.degree() >= 1 and any(g.degree() > 2 for g, _ in D.factor()[1]): continue
        rows.append(Q)
print(f"F_9, J = 2: {len(rows)} rows (monic irreducible of degree 4 with 2-smooth derivative)")
hd, hc = Counter(), Counter(); md, mc = Counter(), Counter(); sizes = (0, 0)
def bucket(m): return m if m <= 5 else (6 if m <= 8 else (9 if m <= 16 else 17))
for b in range(nB):
    B = R([random.choice(els), random.choice(els), F(1)])
    N = lam * (V * B) ** 3; n = N.degree()
    C = R([random.choice(els) for _ in range(n - 81 - 1)])
    Nc = N + V * C
    assert N.derivative() == 0 and Nc.derivative() != 0 and Nc.degree() == n
    for Q in rows:
        fa = (N - Q).factor()[1]; r = sum(m for _, m in fa); hd[r] += 1; md[bucket(min(g.degree() for g, _ in fa))] += 1
        fa = (Nc - Q).factor()[1]; r = sum(m for _, m in fa); hc[r] += 1
        if r % 2 == 0: mc[bucket(min(g.degree() for g, _ in fa))] += 1
    print(f"  B = {B}: n = {n} done", flush=True)
tot_d = sum(hd.values()); tot_c = sum(hc.values())
print("r : desert count | control count")
for r in sorted(set(hd) | set(hc)): print(f"  {r:2d}: {hd[r]:6d} | {hc[r]:6d}")
print(f"desert: {tot_d} values, r odd {sum(v for r, v in hd.items() if r % 2)}, r = 1 (irreducible) {hd[1]}")
print(f"control: {tot_c} values, r odd {sum(v for r, v in hc.items() if r % 2)} ({sum(v for r, v in hc.items() if r % 2)/tot_c:.4f}), r = 1 {hc[1]}")
def chi2(ca, cb, keys):
    # homogeneity chi-square between two samples over the given cells (cells with small totals merged into the last)
    A = [ca[k] for k in keys]; Bv = [cb[k] for k in keys]
    cells = []
    acc = [0, 0]
    for a_, b_ in zip(A, Bv):
        acc[0] += a_; acc[1] += b_
        if acc[0] + acc[1] >= 40: cells.append(tuple(acc)); acc = [0, 0]
    if acc != [0, 0]:
        if cells: cells[-1] = (cells[-1][0] + acc[0], cells[-1][1] + acc[1])
        else: cells.append(tuple(acc))
    sa = sum(c[0] for c in cells); sb = sum(c[1] for c in cells); X = 0.0
    for a_, b_ in cells:
        ea = (a_ + b_) * sa / (sa + sb); eb = (a_ + b_) * sb / (sa + sb)
        X += (a_ - ea) ** 2 / ea + (b_ - eb) ** 2 / eb
    return X, len(cells) - 1
ev = [r for r in sorted(set(hd) | set(hc)) if r % 2 == 0]
X, df = chi2(hd, hc, ev)
print(f"number of factors, desert vs control|r even: chi2 = {X:.2f} on {df} degrees of freedom")
ks = sorted(set(md) | set(mc)); X2, df2 = chi2(md, mc, ks)
print("least factor degree (buckets 3,4,5,6-8,9-16,17+): desert", [md[k] for k in ks], "control|even", [mc[k] for k in ks])
print(f"least factor degree, desert vs control|r even: chi2 = {X2:.2f} on {df2} degrees of freedom")
try:
    from scipy.stats import chi2 as c2
    print(f"p-values: {c2.sf(X, df):.3f}, {c2.sf(X2, df2):.3f}")
except Exception as e: print("scipy not available:", e)
md_mean = sum(r * v for r, v in hd.items()) / tot_d
ce = {r: v for r, v in hc.items() if r % 2 == 0}; mc_mean = sum(r * v for r, v in ce.items()) / sum(ce.values())
print(f"mean r: desert {md_mean:.4f}, control|even {mc_mean:.4f}")
