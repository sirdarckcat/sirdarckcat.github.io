#!/usr/bin/env python3
"""pins_split.py: what a translation move can transfer (the parent's classes at the primes dividing D) against the pin
(the best classes at the same primes), on the exact sieve counts at depth 10^8; and the Gaussian splitting bound."""
import numpy as np, math
S = np.fromfile("S8.100000000.u16", dtype=np.uint16).astype(np.float64); K = len(S); mu = S.mean(); sd = S.std()
lamp = 0.073908; tau = lamp * sd; k = np.arange(K)
h = np.exp(-lamp * (S - mu)); hbar = h.mean()
def cls(p):
    c = k % p; cnt = np.bincount(c, minlength=p); return c, np.bincount(c, weights=S, minlength=p) / cnt, np.bincount(c, weights=h, minlength=p) / cnt
c1, m1, h1 = cls(467); c2, m2, h2 = cls(479)
print(f"single primes: 467: class means of S range {m1.min()-mu:+.2f}..{m1.max()-mu:+.2f} rows, sd {m1.std():.3f}; best class hit-chance factor e^{math.log(h1.max()/hbar):.3f}")
print(f"               479: {m2.min()-mu:+.2f}..{m2.max()-mu:+.2f}, sd {m2.std():.3f}; e^{math.log(h2.max()/hbar):.3f}")
cell = c1 * 479 + c2; cnt = np.bincount(cell, minlength=467 * 479); hm = np.bincount(cell, weights=h, minlength=467 * 479) / np.maximum(cnt, 1); sm = np.bincount(cell, weights=S, minlength=467 * 479) / np.maximum(cnt, 1)
b = int(np.argmax(h1)) * 479 + int(np.argmax(h2))
print(f"PIN (best class of each, chosen from the single-prime tables): cell of {cnt[b]} members, mean S {sm[b]-mu:+.2f} rows, hit-chance factor e^{math.log(hm[b]/hbar):.3f}")
print(f"best cell of all {467*479} by its own mean hit chance (an oracle; includes luck of {int(cnt.mean())} members): e^{math.log(hm.max()/hbar):.3f}")
# splitting: parent = a kept member (S <= 467) or one of the 251 best (S <= 430); children = its 467*479-translates
for name, t in (("kept at 1.67% (S<=467)", 467), ("S<=450 (1e-3)", 450), ("S<=430 (1.2e-5)", 430)):
    par = S <= t
    # mean hit chance of the other members of the parents' cells (leave-one-out)
    cs = np.bincount(cell, weights=h, minlength=467 * 479); tot = (cs[cell[par]] - h[par]) / (cnt[cell[par]] - 1)
    z = (S[par].mean() - mu) / sd
    print(f"SPLIT from parents {name}: {par.sum()} parents, mean z {z:.2f}; children's hit-chance factor e^{math.log(tot.mean()/hbar):+.4f} (+- {tot.std()/tot.mean()/math.sqrt(par.sum()):.4f}); Gaussian bound tau*rho*|z| with rho=0.0017: {tau*0.0017*abs(z):.4f}")
print(f"Gaussian splitting bound with the largest translate correlation in the window (0.0028) and the deepest parent (z=-5.2): {tau*0.0028*5.2:.4f} nats")
