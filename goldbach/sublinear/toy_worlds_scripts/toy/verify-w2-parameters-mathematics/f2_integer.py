# tilt statistics on primes 467..2e6 (independent implementation via sorted residues)
import sys, math, numpy as np
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
rows, _ = cr.load(cr.S + "q200000_m89.txt")
rows = np.array(rows, dtype=np.int64); rows = rows[rows < 200000]; R = len(rows)
P1 = 2 * 10 ** 6
sv = np.ones(P1 + 1, bool); sv[:2] = False
for i in range(2, 1415):
    if sv[i]: sv[i * i::i] = False
small = np.nonzero(sv)[0]
later = small[small >= 467]
ths = [0.0723, 0.1409, 0.1868]
acc = {th: dict(kl=0.0, X=0.0, sparse=0.0) for th in ths}
chi467 = {}; MW_rows = 0.0; cum = 0.0; ncl = {}; targets = {"ln2": math.log(2), "ln16": math.log(16)}; done = set()
for p in later:
    r = np.sort(rows % p)
    brk = np.flatnonzero(np.diff(r)) + 1
    f = np.diff(np.concatenate(([0], brk, [R]))).astype(float)     # rows per occupied class
    empty = int(p) - len(f)
    lp = math.log(p)
    for th in ths:
        w = np.exp(th * f); Z = w.sum() + empty
        pi = w / Z; pe = 1.0 / Z
        kl = float((pi * np.log(pi * p)).sum()) + empty * pe * math.log(pe * p)
        s2 = float((pi * pi).sum()) + empty * pe * pe
        a = acc[th]; a["kl"] += kl; a["X"] += lp / p * (p * s2 - 1); a["sparse"] += lp * float((pi * pi).sum())
        if p == 467: chi467[th] = (p * s2 - 1, kl, float(f.var() / f.mean()) if empty == 0 else None, len(f))
    MW_rows += lp * len(f) / p ** 2
    for name, tgt in targets.items():
        if name in done: continue
        v = lp / p
        if cum + v >= tgt:
            ncl[name] = ncl.get(name, 0) + math.ceil((tgt - cum) / (lp / p ** 2)); done.add(name)
        else:
            ncl[name] = ncl.get(name, 0) + int(p)
    cum += lp / p
tail_inv = math.log(math.log(1e8) / math.log(2e6)); tail_lp2 = 1 / 2e6 - 1 / 1e8
for th in ths:
    a = acc[th]
    kappa = a["kl"] + R * (th * math.exp(th) - math.exp(th) + 1) * tail_inv
    X = a["X"] + R * (math.exp(th) - 1) ** 2 * tail_lp2
    print(f"theta={th}: kappa(to 1e8)={kappa:.3f} X={X:.4f} chi2@467={chi467[th][0]:.4f} KL@467={chi467[th][1]:.4f} sparse mass={a['sparse']:.3f}; Poisson chi2@467 would be {math.exp(R/467*(math.exp(th)-1)**2)-1:.4f}")
print("occupied classes at 467:", chi467[ths[0]][3], "of 467")
c = np.bincount(rows % 467, minlength=467); print("rows per class mod 467: mean", c.mean(), "var", c.var(), "classes with 0 rows:", (c == 0).sum(), "max", c.max())
print("uniform mass of the classes holding a row, sum ln p #occ/p^2 (p<=2e6):", round(MW_rows, 4), "tail <", R / 2e6, " exp =", round(math.exp(MW_rows), 2))
print("least number of weighted classes at theta = 0 for mass ln 2, ln 16:", ncl)
allp = small.astype(float)
print("sum e>=2 e ln p/p^e, p<=2e6:", round(float((np.log(allp) * (2 * allp - 1) / (allp * (allp - 1) ** 2)).sum()), 5), "; p>463:", round(float((np.log(allp[allp > 463]) * (2 * allp[allp > 463] - 1) / (allp[allp > 463] * (allp[allp > 463] - 1) ** 2)).sum()), 5))
