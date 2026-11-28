#!/usr/bin/env python3
"""The cover as a sieve of dimension 2 on [1, Q): what the upper- and lower-bound sieves allow at s = ln Q/ln 463 = 1.99,
   against the worst and the best covers that greedy rules find."""
import math, numpy as np
Q = 200000
s = np.ones(Q, dtype=bool); s[:2] = False
for i in range(2, int(Q ** .5) + 1):
    if s[i]: s[i * i::i] = False
PR = np.nonzero(s)[0]; PR = PR[PR > 2]; mods = [int(r) for r in PR[PR <= 463]]
V = 0.5
for r in mods: V *= (1 - 2 / r)
EG = math.exp(0.5772156649015329); sv = math.log(Q) / math.log(463)
sigma2 = sv ** 2 / (math.exp(2 * 0.5772156649015329) * 2)          # sigma_kappa(s) = s^kappa/(e^(gamma kappa) Gamma(kappa+1)) for s <= 2
print(f"dimension-2 sieve on [1,Q): X V(z) = Q * (1/2) prod_(3<=r<=463) (1 - 2/r) = {Q * V:.1f}; s = {sv:.3f}")
print(f"Selberg upper bound, leading term: X V / sigma_2(s) = {Q * V / sigma2:.0f} (sigma_2 = {sigma2:.4f}); lower-bound sieves of dimension 2: zero for s below the sifting limit beta_2 = 4.27 (from memory), here s = {sv:.2f}")
def run(rule):
    alive = np.ones(len(PR), dtype=bool)
    for r in mods:
        q = PR[alive]; b = np.bincount(q % r, minlength=r).astype(float); b[0] = np.nan
        a = int(np.nanargmax(b)) if rule == "max" else int(np.nanargmin(b)); alive[alive] = (q % r) != a
    return int(alive.sum())
print(f"greedy (heaviest non-zero class at each prime, ascending): {run('max')} rows; anti-greedy (lightest non-zero class): {run('min')} rows; real cover 1502; product of local densities 2150.4")
