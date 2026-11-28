#!/usr/bin/env python3
"""blockmin.py: is the minimum of the exact sieve count over a block of members the minimum of independent draws?
The window is cut into B blocks; the law of the block minimum predicted from the single-member histogram, (1-F(s-1))^n - (1-F(s))^n,
is compared with the B observed minima (chi-square on pooled cells), for contiguous blocks and for residue classes k mod B."""
import numpy as np, math
S = np.fromfile("S8.100000000.u16", dtype=np.uint16).astype(np.int64); K = len(S)
h = np.bincount(S).astype(np.float64); F = np.cumsum(h) / K
def test(name, mins, n):
    B = len(mins); G = (1 - F) ** n; pm = np.empty(len(F)); pm[0] = 1 - G[0]; pm[1:] = G[:-1] - G[1:]      # P(min = s)
    obs = np.bincount(mins, minlength=len(F)).astype(float); exp = B * pm
    # pool cells to expected >= 8
    cells = []; o = e = 0.0
    for s in range(len(F)):
        o += obs[s]; e += exp[s]
        if e >= 8: cells.append((o, e)); o = e = 0.0
    if e > 0: cells[-1] = (cells[-1][0] + o, cells[-1][1] + e)
    chi = sum((o - e) ** 2 / e for o, e in cells); df = len(cells) - 1
    em = float((pm * np.arange(len(F))).sum()); ev = float((pm * (np.arange(len(F)) - em) ** 2).sum())
    print(f"{name}: B={B}, n={n}: mean of minima {mins.mean():.3f} (independent draws: {em:.3f} +- {math.sqrt(ev/B):.3f}), sd {mins.std():.3f} ({math.sqrt(ev):.3f}); chi2 {chi:.1f} on {df} df")
for B in (256, 4096):
    n = K // B; test("contiguous blocks", S[:n * B].reshape(B, n).min(axis=1), n)
    test("classes k mod B", S[:n * B].reshape(n, B).min(axis=0), n)
n = K // 467; test("classes k mod 467 (a later prime: one shared residue)", S[:n * 467].reshape(n, 467).min(axis=0), n)
n = K // (467 * 479); test("classes k mod 467*479 (two shared residues)", S[:n * 467 * 479].reshape(n, 467 * 479).min(axis=0), n)
# spacing of the extreme members
idx = np.nonzero(S <= 440)[0]; gaps = np.diff(idx) / (K / len(idx)); gaps.sort()
ks = np.max(np.abs((np.arange(1, len(gaps) + 1) / len(gaps)) - (1 - np.exp(-gaps))))
print(f"the {len(idx)} members with S <= 440: spacings against the exponential law: KS distance {ks:.4f} (5% critical value {1.36/math.sqrt(len(gaps)):.4f}); mean gap^2/2 = {np.mean(gaps**2)/2:.3f} (1 for Poisson)")
