"""Ceiling for any scheme that mixes the cover with class lists on the primes beyond the line, at equal work.
Every member gets the score  rows left at depth 23 - lambda x (incidences with 29..199 - 75)  for free (this is what
weighted lists, product lists and bucketing select on, and it costs as much as the scoring itself); the W best by that
score are then scored at depth 200 and examined in that order.  lambda = 0 is the cover-first prefix (the reference).
Also the direct order: the same score used to examine members without any scoring at depth 200."""
import math
import numpy as np
import pp
from refcurve import gains, cells

k1 = np.asarray(pp.K1).astype(np.float32); k2 = np.asarray(pp.K2); su = np.asarray(pp.SUCC)
inc = np.load("data/inc_deep.npy").astype(np.float32)
rng = np.random.default_rng(5); noise = rng.random(len(k1), dtype=np.float32) * 1e-3
WS = (10000, 100000, 1000000, 10000000)
print("work W | lambda | largest rows left at depth 23 among the W | successes among the W | N examined for 1 | 3 | 10 | 30 | gain in nats over cover first at 1 | 3 | 10 | 30")
for lam in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0):
    key = k1 - np.float32(lam) * (inc - np.float32(75.0)) + noise
    part = np.argpartition(key, WS[-1])[:WS[-1]]
    part = part[np.argsort(key[part], kind="stable")]
    for W in WS:
        idx = np.sort(part[:W]); ex = pp.examined(k2[idx], su[idx]); d = {"examined": ex, "gain": gains(ex)}
        print(f"{W:>10,d} | {lam:.2f} | {int(k1[idx].max())} | {int(su[idx].sum())} | {cells(d)} | {cells(d, 'gain', '{:+.2f}')}", flush=True)
