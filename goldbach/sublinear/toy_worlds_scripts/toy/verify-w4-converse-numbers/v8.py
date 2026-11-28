import math, numpy as np
from vlib import *
cov, rows = get(); n = len(rows); rng = np.random.default_rng(8); P = lp(467, 5000)
def fall(a, d): return math.prod(a - i for i in range(d))
def exp_energy(a, s):
    p = [fall(a, d) / fall(s, d) for d in range(5)]
    return s * p[1] + 2 * s * (s - 1) * (p[2] + p[3]) + (s ** 3 - 4 * s * s + 3 * s) * p[4]
def energy(A):
    s = len(A); a = A.astype(np.int64); full = np.convolve(a, a)          # exact integer convolution, then fold mod s
    r = full[:s].copy(); r[:s - 1] += full[s:]; return int((r * r).sum())
# sanity of exp_energy against permutations
A = rng.random(467) < 0.4; print("check analytic expectation: analytic %.1f, mean of 400 perms %.1f" % (exp_energy(int(A.sum()), 467), np.mean([energy(rng.permutation(A)) for _ in range(400)])))
rec = []
for s in P:
    t = tab(rows, s); thr = np.sort(t)[::-1][max(1, s // 4) - 1]; A = t >= max(thr, 1); a = int(A.sum())
    E = energy(A); Er = exp_energy(a, s)
    # interval of the same size: exact energy
    I = np.zeros(s, bool); I[:a] = True
    F = np.abs(np.fft.fft(t.astype(float))) ** 2; share = 2 * F[1:].max() / F[1:].sum()
    Fu = np.abs(np.fft.fft(rng.permutation(t).astype(float))) ** 2; shu = 2 * Fu[1:].max() / Fu[1:].sum()
    rec.append((s, a / s, E / Er - 1, energy(I) / Er - 1, share, shu))
rec = np.array(rec)
for lo, hi in ((467, 1000), (1000, 2000), (2000, 3500), (3500, 5000)):
    r = rec[(rec[:, 0] >= lo) & (rec[:, 0] < hi)]
    print("[%d,%d) density %.2f energy/random-1 %+.5f +- %.5f (interval %+.2f) share real %.4f shuf %.4f" % (lo, hi, r[:, 1].mean(), r[:, 2].mean(), r[:, 2].std() / math.sqrt(len(r)), r[:, 3].mean(), r[:, 4].mean(), r[:, 5].mean()))
# Proposition E: measured correlation, the page's prediction, and the exact decomposition
AP = lp(467, 60000)
for lo, hi, cnt in ((467, 1000, 78), (2000, 5000, 120), (20000, 60000, 120)):
    pr = [s for s in AP if lo <= s < hi]; pr = pr[::max(1, len(pr) // cnt)]
    tabs = {s: tab(rows, s).astype(float) for s in pr}; inR = np.zeros(60000); inR[rows[rows < 60000]] = 1
    out = []
    for i, s in enumerate(pr):
        for s2 in pr[i + 1:]:
            a = tabs[s]; b = tabs[s2][:s]; u = inR[:s]; g = a - u; g2 = b - u; nrm = math.sqrt(a.var() * b.var())
            cv = lambda x, y: (x * y).mean() - x.mean() * y.mean()
            out.append((np.corrcoef(a, b)[0, 1], (rows < s).sum() / s / nrm, cv(u, u) / nrm, (cv(u, g2) + cv(g, u)) / nrm, cv(g, g2) / nrm, cv(a, b) / nrm))
    o = np.array(out)
    print("[%d,%d) %d primes %d pairs: corr %.5f +- %.5f | page prediction %.5f | shared-row term rho(1-rho) %.5f, cross terms Cov(1_R,g')+Cov(g,1_R) %+.5f, Cov(g,g') %+.5f, sum %.5f" % (lo, hi, len(pr), len(o), o[:, 0].mean(), o[:, 0].std() / math.sqrt(len(o)), o[:, 1].mean(), o[:, 2].mean(), o[:, 3].mean(), o[:, 4].mean(), o[:, 5].mean()))
