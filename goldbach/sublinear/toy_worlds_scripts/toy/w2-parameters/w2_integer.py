#!/usr/bin/env python3
"""The integer side of the World 2 accounting, on the real 200,000 cover (1,502 rows).

Theorem 2 of the page, transported to Z (the dictionary deg <-> ln; the integer form of Theorem 1 is proved on the page
with Minkowski's theorem): if a weighted interpolation (Johnson-type) decoder guarantees a set S of members of a window
of K members, and pi_p is the distribution of N mod p over S (any probability measure on S), then

        sum_p ln p * ||pi_p||_2^2  >  ln K * (1 - o(1)),      ||pi_p||^2 = (1 + chi2_p) / p,

the sum over the places the decoder uses.  For the uniform distribution chi2 = 0 and the sum is the Mertens sum.
Model of the aligned members (the README's measured description: one price at every later prime): the class of N
modulo a later prime p is drawn with probability proportional to exp(theta f_p(c)), f_p(c) = rows in class c.
kappa(theta) = sum_p KL(pi_p || uniform) is the depth; X(theta) = sum_p (ln p / p) chi2_p is all that alignment adds.
"""
import sys, os, math
import numpy as np
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr

rows, p_hit = cr.load(cr.S + "q200000_m89.txt")
rows = rows[rows < 200000]                                   # the rows of the design level (cr.load returns them to 260,000)
R = len(rows)
assert R == 1502
line = [x for x in open(cr.S + "q200000_m89.txt") if x.startswith(("COVER", "BEST"))][0].split()
cover_primes = [int(t.split(":")[0]) for t in line if ":" in t]
lnK = 24.35 * math.log(2)
print(f"rows R = {R}; cover primes: {len(cover_primes)} up to {max(cover_primes)}; window ln K = 24.35 ln 2 = {lnK:.3f}")

P1 = 2_000_000; Y = 10 ** 8
sv = np.ones(P1 + 1, dtype=bool); sv[:2] = False
for i in range(2, int(P1 ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
primes = np.nonzero(sv)[0]
later = primes[primes > max(cover_primes)]
KMAX = 24
H = np.zeros((len(later), KMAX + 1), dtype=np.int64)       # H[i, k] = number of classes of later[i] holding k rows
for i, p in enumerate(later):
    mult = np.unique(rows % p, return_counts=True)[1]       # rows per occupied class
    cnt = np.bincount(mult)                                 # cnt[k] = classes with k rows (k >= 1)
    assert len(cnt) <= KMAX + 1
    H[i, :len(cnt)] = cnt
    H[i, 0] = p - H[i, 1:].sum()
assert (H @ np.arange(KMAX + 1) == R).all()
lp = np.log(later.astype(float)); pf = later.astype(float)
mert = float((lp / pf).sum())
print(f"later primes {later[0]}..{later[-1]}: {len(later)}; sum ln p / p over them = {mert:.4f} (ln({P1}/463) = {math.log(P1 / 463):.4f})")
ks = np.arange(KMAX + 1, dtype=float)
# tails beyond P1 (classes hold 0 or 1 row up to collisions of relative size R/p):  sum 1/p and sum ln p / p^2
tail_inv = math.log(math.log(Y) / math.log(P1))            # sum_{P1 < p <= Y} 1/p  (Mertens)
tail_lp2 = 1 / P1 - 1 / Y                                   # sum_{P1 < p <= Y} ln p / p^2  ~ int dt / t^2


def stats(theta):
    w = np.exp(theta * ks)[None, :]
    Z = (H * w).sum(axis=1)
    pk = w / Z[:, None]                                     # probability of one class holding k rows
    KL = (H * pk * np.log(pk * pf[:, None])).sum(axis=1)
    S2 = pf * (H * pk * pk).sum(axis=1)                     # 1 + chi2
    kills = (H * pk * ks).sum(axis=1)
    kappa = KL.sum() + R * (theta * math.exp(theta) - math.exp(theta) + 1) * tail_inv
    X = ((lp / pf) * (S2 - 1)).sum() + R * (math.exp(theta) - 1) ** 2 * tail_lp2
    Xmax = (lp / pf).max() * 2 * kappa
    exk = kills.sum() + R * math.exp(theta) * tail_inv
    return kappa, X, S2[0] - 1, exk, KL[0]


def solve(kappa):
    lo, hi = 0.0, 3.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if stats(mid)[0] < kappa: lo = mid
        else: hi = mid
    return (lo + hi) / 2


typ = stats(0.0)[3]
print(f"typical member: expected strikes at the later primes to 1e8, with repeats: {typ:.1f}")
print()
print("depth kappa | tilt theta | strikes (x typical) | X = sum (ln p/p) chi2_p | chi2 at 467 | KL at 467 | Mertens mass needed "
      "ln K - X | places to y = 463 e^(ln K - X) | pi(y) ~ y/ln y | README bound (sqrt(ln K) - sqrt(2 kappa ln467/467))^2 -> y")
for kappa in (1.0, 4.2, 8.0, 12.0, 16.6, 30.0):
    th = solve(kappa)
    k, X, chi467, exk, kl467 = stats(th)
    need = lnK - X
    y = 463 * math.exp(need)
    rb = (math.sqrt(lnK) - math.sqrt(2 * kappa * math.log(467) / 467)) ** 2
    print(f"{kappa:5.1f} | {th:.4f} | {exk:.1f} ({exk / typ:.3f}) | {X:.4f} | {chi467:.4f} | {kl467:.4f} | {need:.3f} | {y:.3e} | "
          f"{y / math.log(y):.3e} | {rb:.3f} -> {463 * math.exp(rb):.3e}")
print()
print("the same for sub-windows (pins spend the rest of the window): K_s members, alignment at depth min(16.6, ln K_s):")
for Ks in (2, 16, 1024, 2 ** 20, 2 ** 24.35):
    kappa = min(16.6, math.log(Ks))
    th = solve(kappa); X = stats(th)[1]
    need = math.log(Ks) - X
    y = 463 * math.exp(max(need, 0))
    npl = y / math.log(y) - 463 / math.log(463)
    print(f"K_s = {Ks:.4g}: X = {X:.4f}; Mertens mass needed {need:.3f}; places 463 < p <= {y:.4g}: about {npl:.4g} primes "
          f"= {npl / Ks:.1f} per member; dense tables sum p ~ y^2/(2 ln y) = {y * y / (2 * math.log(y)):.3g} = {y * y / (2 * math.log(y)) / Ks:.3g} per member")
print()
print("support form of Theorem 2: sum over the (p, c) that carry a weight of ln p * pi_p(c)^2 must exceed ln K_s; the least number")
print("of weighted classes that can reach it (greedy, exact histograms for the primes to 2e6):")
def min_weights(target, theta):
    w = np.exp(theta * ks)[None, :]
    Z = (H * w).sum(axis=1)
    val = lp[:, None] * (w / Z[:, None]) ** 2            # value of one class of prime i holding k rows
    v = val.reshape(-1); mlt = H.reshape(-1).astype(float)
    order = np.argsort(-v)
    cum = np.cumsum(v[order] * mlt[order]); cnt = np.cumsum(mlt[order])
    if cum[-1] < target:
        return None, cum[-1]
    j = int(np.searchsorted(cum, target))
    prev_c = cnt[j - 1] if j else 0.0; prev_s = cum[j - 1] if j else 0.0
    return prev_c + math.ceil((target - prev_s) / v[order][j]), cum[-1]
for Ks in (2, 16, 256, 1024, 4096):
    kappa = min(16.6, math.log(Ks)); th = solve(kappa)
    nw, tot = min_weights(math.log(Ks), th)
    sparse = float((lp[:, None] * ((np.exp(th * ks)[None, :] / (H * np.exp(th * ks)[None, :]).sum(axis=1)[:, None]) ** 2) * H)[:, 1:].sum())
    print(f"K_s = {Ks}: at least {nw:.0f} weighted classes = {nw / Ks:.3g} per member (all classes of all primes to 2e6 give {tot:.3f});"
          f" weights only on the classes that hold a row give at most {sparse:.3f} in all")
th = solve(16.6)
sparse = float((lp[:, None] * ((np.exp(th * ks)[None, :] / (H * np.exp(th * ks)[None, :]).sum(axis=1)[:, None]) ** 2) * H)[:, 1:].sum())
print(f"full window, theta = {th:.4f}: weights only on the classes that hold a row: sum over primes to 2e6 = {sparse:.3f}, "
      f"tail to infinity < R e^(2 theta) / 2e6 = {R * math.exp(2 * th) / 2e6:.4f}; against ln K = {lnK:.3f}")
print()
print("prime powers as places: the mass of p^e is e ln p / p^e instead of ln p / p")
allp = primes.astype(float)
for lo in (2, 463):
    sel = allp[allp > lo] if lo > 2 else allp
    m2 = sum(float((e * np.log(sel) / sel ** e).sum()) for e in range(2, 40))
    print(f"   sum over p {'>' if lo > 2 else '>='} {lo} (to {P1}) and e >= 2 of e ln p / p^e = {m2:.5f}")
print("   cylinder lists (a list of classes mod p lifted to p^e): d/l term e ln p / (l p^(e-1)) against ln p / l: ratio e / p^(e-1):",
      ", ".join(f"p={p},e={e}: {e / p ** (e - 1):.4f}" for p, e in ((2, 2), (2, 3), (3, 2), (5, 2), (467, 2))))
