# verifier: variance by depth, D(z) to 1e8, pins, free lists / progressions / intervals / arcs, Fourier
import math, time, numpy as np
from base import *
t0 = time.time()
lnX = 200 * math.log(10)
# ---- primes to 1e8 (odd-only sieve)
LIM = 10**8
n = LIM // 2
sv = np.ones(n, dtype=bool); sv[0] = False            # index i <-> 2i+1
for i in range(1, int(LIM**0.5) // 2 + 1):
    if sv[i]:
        p = 2 * i + 1; sv[(p * p) // 2::p] = False
pr = 2 * np.nonzero(sv)[0].astype(np.int64) + 1; del sv
print("pi(1e8) =", len(pr) + 1, f"[{time.time() - t0:.1f}s]")
lg = np.log(pr.astype(np.float64)); cth = np.cumsum(lg) + math.log(2)
def theta(z): return cth[np.searchsorted(pr, z, side="right") - 1]
for z in (463, 10**6, 10**7, 10**8):
    print(f"theta({z}) = {theta(z):.3f}  D = {theta(z) - lnX:.3f}")
# ---- variance of hit_s over classes
lp = pr[pr > 463]
var = np.empty(len(lp))
small = lp < 200000
R = ROWS
for i in np.nonzero(small)[0]:
    s = int(lp[i]); cnt = np.bincount(R % s, minlength=s).astype(np.float64); var[i] = (cnt**2).sum() / s - (n0 / s)**2
big = lp[~small].astype(np.float64); var[~small] = n0 / big - (n0 / big)**2
cum = np.cumsum(var); tot = cum[-1]
i2 = np.searchsorted(lp, 2 * 10**6, side="right") - 1
print(f"sum of variances to 2e6: {cum[i2]:.1f}; exact tail 2e6..1e8: {tot - cum[i2]:.1f} (their estimate n0*(lnln1e8-lnln2e6) = {n0 * (math.log(math.log(1e8)) - math.log(math.log(2e6))):.1f}); total {tot:.1f}  [{time.time() - t0:.1f}s]")
for z in (487, 491, 499, 503, 509, 523, 541, 1000, 2000, 10**4, 10**5, 2 * 10**5, 2 * 10**6):
    i = np.searchsorted(lp, z, side="right") - 1
    print(f"   z={z}: later primes {i + 1}, D={theta(z) - lnX:.1f}, variance {cum[i]:.1f}, share {100 * cum[i] / tot:.1f}%")
# ---- pins, lists
L30 = LATER[:30]; hit = {s: hit_table(s) for s in L30}
g = [int(hit[s].max()) - n0 / s for s in L30]; nat = [math.log(s) for s in L30]
print(f"pin: {np.mean(g):.2f} rows for {np.mean(nat):.2f} nats = {sum(g) / sum(nat):.2f} rows/nat; first 8: {sum(g[:8]) / sum(nat[:8]):.2f}; mean n0/s = {np.mean([n0 / s for s in L30]):.2f}; 30th later prime {L30[-1]}")
P30 = M * prod(L30)
def four(h, s, l, dch):
    free = np.sort(h)[::-1][:l].sum()
    best = 0; res = {}
    for d in range(1, s):
        seq = h[(np.arange(s + l) * d) % s]
        cs = np.concatenate([[0], np.cumsum(seq)])
        w = (cs[l:l + s] - cs[:s]).max()
        best = max(best, w)
        if d == 1: res["int"] = w
        if d == dch: res["arc"] = w
    return np.array([free, best, res["int"], res["arc"]], dtype=float)
rng = np.random.default_rng(12345)
for name, lf in (("s/e", lambda s: round(s / math.e)), ("s/20", lambda s: round(s / 20))):
    acc = np.zeros(4); accr = np.zeros(4); natsum = 0
    for s in L30:
        l = lf(s); dch = (P30 // s) % s
        acc += four(hit[s], s, l, dch) / l - n0 / s; natsum += math.log(s / l)
        for _ in range(4):
            hr = np.bincount(rng.integers(0, s, n0), minlength=s)
            accr += (four(hr, s, l, dch) / l - n0 / s) / 4
    print(f"lists of {name} classes: real per prime free/AP/interval/arc = {np.round(acc / 30, 2)}; per nat = {np.round(acc / natsum, 2)}; random per prime = {np.round(accr / 30, 2)}  [{time.time() - t0:.1f}s]")
mx = [np.abs(np.fft.fft(hit[s]))[1:].max() / math.sqrt(n0) for s in L30]
mr = [np.abs(np.fft.fft(np.bincount(rng.integers(0, s, n0), minlength=s)))[1:].max() / math.sqrt(n0) for s in L30 for _ in range(10)]
print(f"largest Fourier coefficient / sqrt(n0): real mean {np.mean(mx):.2f} max {np.max(mx):.2f}; random (10 draws each) mean {np.mean(mr):.2f} max {np.max(mr):.2f}")
