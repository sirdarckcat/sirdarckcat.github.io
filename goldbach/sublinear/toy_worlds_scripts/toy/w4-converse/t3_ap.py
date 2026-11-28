#!/usr/bin/env python3
"""t3: lists that are arithmetic progressions of classes, every common difference (so every labelling c -> d c, including the
window's own labelling k and the Bohr sets of every additive character).
For a table t on Z/s, a difference d (1 <= d <= (s-1)/2), a start a and a length L:
     heavy list  A = {a + d i : i < L}:            gain = mean of t on A - mean of t,              cost = ln(s/L)
     thin list   A = complement of the emptiest progression of length L:
                                                   gain = L (mean t - mean on the excluded)/(s-L),  cost = -ln(1 - L/s)
The best gain and the best rate (gain/cost, rows per nat) over all (d, a) for each length, on the real table and on the same
table with its classes permuted at random (2 permutations)."""
import math, sys, numpy as np
from common import *
cov, rows = load(); rng = np.random.default_rng(11)
FR = (2, 3, 4, 6, 8, 12, 16, 32, 64)
def best(t):
    s = len(t); d = np.arange(1, (s - 1) // 2 + 1); Ls = [max(2, s // f) for f in FR]; Lm = Ls[0]
    idx = (d[:, None] * np.arange(s + Lm)[None, :]) % s
    cs = np.zeros((len(d), s + Lm + 1), dtype=np.int32); np.cumsum(t[idx], axis=1, out=cs[:, 1:])
    m = t.mean(); res = []
    for L in Ls:
        W = cs[:, L:L + s] - cs[:, :s]; hi = W.max(); lo = W.min()
        gh = hi / L - m; ch = math.log(s / L); gt = L * (m - lo / L) / (s - L); ct = -math.log(1 - L / s)
        res.append((gh, gh / ch, gt, gt / ct))
    return np.array(res)
LP = later_primes(464, 5000); sel = [s for s in LP if s < 1000] + [s for s in LP if s >= 1000][::4]
R = []; U = []
for s in sel:
    t = table(rows, s).astype(np.int32); R.append(best(t)); U.append(np.mean([best(rng.permutation(t)) for _ in range(2)], axis=0))
R = np.array(R); U = np.array(U); S = np.array(sel)
print(f"primes used: {len(sel)} (all below 1000, every 4th from 1000 to 5000)")
for lo, hi in ((467, 1000), (1000, 2000), (2000, 5000), (467, 5000)):
    k = (S >= lo) & (S < hi); print(f"s in [{lo},{hi}): {k.sum()} primes")
    print("    density  | heavy list: gain real / shuffled (rows)   rate real / shuffled (rows per nat) | thin list (complement): gain real / shuffled   rate real / shuffled")
    for i, f in enumerate(FR):
        r = R[k, i].mean(axis=0); u = U[k, i].mean(axis=0)
        print(f"    1/{f:<3d}    |   {r[0]:.4f} / {u[0]:.4f}      {r[1]:.4f} / {u[1]:.4f}                          |   {r[2]:.4f} / {u[2]:.4f}     {r[3]:.4f} / {u[3]:.4f}")
    br = R[k][:, :, 1].max(axis=1); bu = U[k][:, :, 1].max(axis=1); tr = R[k][:, :, 3].max(axis=1); tu = U[k][:, :, 3].max(axis=1)
    print(f"    best heavy rate over lengths: real {br.mean():.4f}, shuffled {bu.mean():.4f}, difference {np.mean(br-bu):+.4f} +- {np.std(br-bu)/math.sqrt(k.sum()):.4f}")
    print(f"    best thin  rate over lengths: real {tr.mean():.4f}, shuffled {tu.mean():.4f}, difference {np.mean(tr-tu):+.4f} +- {np.std(tr-tu)/math.sqrt(k.sum()):.4f}")
np.save("t3.npy", np.array([R, U]))
