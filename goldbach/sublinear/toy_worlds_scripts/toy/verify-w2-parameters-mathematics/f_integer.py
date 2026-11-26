# Independent recomputation of the integer numbers of the page on the real cover.
import sys, math, numpy as np
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
rows, _ = cr.load(cr.S + "q200000_m89.txt")
rows = np.array(rows); rows = rows[rows < 200000]; R = len(rows)
lnK = 24.35 * math.log(2)
print("rows", R, "lnK", round(lnK, 4))
# primes to 1e8 by segmented numpy sieve; S(x) = sum_{467 <= p <= x} ln p / p
LIM = 10 ** 8
base = np.ones(10 ** 4 + 1, bool); base[:2] = False
for i in range(2, 101):
    if base[i]: base[i * i::i] = False
bp = np.nonzero(base)[0]
S = 0.0; cnt = 0; marks = {}; seg = 2 * 10 ** 6; small = None; sum_small = 0.0
checkpoints = [2 * 10 ** 6, 10 ** 7, 10 ** 8]
for lo in range(0, LIM, seg):
    hi = lo + seg
    sv = np.ones(seg, bool)
    if lo == 0: sv[:2] = False
    for p in bp:
        st = max(p * p, ((lo + p - 1) // p) * p)
        sv[st - lo::p] = False
    pr = np.nonzero(sv)[0] + lo
    if lo == 0:
        small = pr.copy()
        sum_small = float((np.log(pr[pr < 467]) / pr[pr < 467]).sum())
    prf = pr[pr >= 467].astype(float)
    S += float((np.log(prf) / prf).sum()); cnt += len(prf)
    if hi in checkpoints: marks[hi] = (S, cnt)
for x, (s, c) in marks.items():
    print(f"sum_(467<=p<={x:.0e}) ln p/p = {s:.5f}  (ln(x/463) = {math.log(x/463):.5f}, ln(x/467) = {math.log(x/467):.5f}); primes: {c}")
S8 = marks[10 ** 8][0]
for need in (16.820, lnK, 16.878 - 0.437, math.log(2), math.log(16)):
    y = 1e8 * math.exp(need - S8) if need > S8 else None
    print(f"mass {need:.3f} from 467: y = {y if y is None else f'{y:.4g}'}; page formula 463 e^need = {463 * math.exp(need):.4g}")
def li(x): return x / math.log(x) * (1 + 1 / math.log(x) + 2 / math.log(x) ** 2 + 6 / math.log(x) ** 3)
for y in (9.339e9, 1.0e10):
    print(f"pi({y:.3e}) ~ {li(y):.4g} (y/ln y = {y/math.log(y):.4g}); sum of primes ~ {y*y/(2*math.log(y))*(1+1/(2*math.log(y))):.3g}")
# tilt statistics on primes 467..2e6, exact class counts
later = small[(small >= 467)]
ths = [0.0723, 0.1409, 0.1868]
acc = {th: dict(kl=0.0, X=0.0, sparse=0.0, kills=0.0) for th in ths}
chi467 = {}
MW_rows = 0.0
for p in later:
    f = np.bincount(rows % p, minlength=p).astype(float)
    for th in ths:
        w = np.exp(th * f); Z = w.sum(); pi = w / Z
        a = acc[th]
        a["kl"] += float((pi * np.log(pi * p)).sum())
        chi = p * float((pi * pi).sum()) - 1
        a["X"] += math.log(p) / p * chi
        a["sparse"] += math.log(p) * float((pi[f > 0] ** 2).sum())
        a["kills"] += float((pi * f).sum())
        if p == 467: chi467[th] = (chi, float((pi * np.log(pi * p)).sum()))
    MW_rows += math.log(p) * (f > 0).sum() / p ** 2
tail_inv = math.log(math.log(1e8) / math.log(2e6)); tail_lp2 = 1 / 2e6 - 1 / 1e8
for th in ths:
    a = acc[th]
    kappa = a["kl"] + R * (th * math.exp(th) - math.exp(th) + 1) * tail_inv
    X = a["X"] + R * (math.exp(th) - 1) ** 2 * tail_lp2
    print(f"theta={th}: kappa(to 1e8)={kappa:.3f}  X={X:.4f}  chi2@467={chi467[th][0]:.4f} KL@467={chi467[th][1]:.4f}  sparse mass (classes holding a row, p<=2e6)={a['sparse']:.3f}  Poisson chi2@467={math.exp(R/467*(math.exp(th)-1)**2)-1:.4f}")
print("uniform mass of the classes that hold a row, sum ln p * #occupied / p^2 (p <= 2e6):", round(MW_rows, 4), " tail <", R / 2e6)
# K_s = 2 : least number of classes (uniform value ln p / p^2 each, smallest primes first) with total mass ln 2, ln 16
for tgt in (math.log(2), math.log(16)):
    cum = 0.0; ncl = 0
    for p in later:
        v = math.log(p) / p
        if cum + v >= tgt:
            ncl += math.ceil((tgt - cum) / (math.log(p) / p ** 2)); break
        cum += v; ncl += int(p)
    print(f"mass {tgt:.3f}: least number of weighted classes at theta=0: {ncl}")
# prime powers
allp = small.astype(float)
tot = float((np.log(allp) * (2 * allp - 1) / (allp * (allp - 1) ** 2)).sum())
big = allp[allp > 463]
print("sum_{p<=2e6} sum_{e>=2} e ln p/p^e =", round(tot, 5), "; p>463:", round(float((np.log(big) * (2 * big - 1) / (big * (big - 1) ** 2)).sum()), 5), "+ tail", round(2 / 2e6, 6))
