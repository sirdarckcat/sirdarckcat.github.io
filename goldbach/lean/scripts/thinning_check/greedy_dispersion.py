#!/usr/bin/env python3
"""How the rows that are left spread over the classes of the next covering prime.

Rows: the odd primes below Q = 213,070.  A greedy cover on the 89 odd primes 3..463 (each
prime takes the nonzero class holding the most rows still left) is run on the real rows and
on two models in which the rows left fall into the classes at random (independent Poisson
counts; a multinomial).  The real class counts are less dispersed than Poisson (variance /
mean well below 1 for the small primes), so a model with Poisson class counts overstates what
a cover can do: 1,450 rows against 1,680 for the same greedy rule (the best cover known has
1,609).
"""
import numpy as np
Q = 213070
def primes_upto(n):
    sv = np.ones(n + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]: sv[i * i::i] = False
    return np.nonzero(sv)[0]
P = primes_upto(Q); rows = P[(P > 2) & (P < Q)]
cov = [int(p) for p in P if 3 <= p <= 463]
R = len(rows)
alive = np.ones(R, dtype=bool); k = R; fano = []
print("real rows, greedy from the small primes up: prime, rows left before it, mean per class, largest class, variance/mean")
for s in cov:
    cnt = np.bincount(rows[alive] % s, minlength=s)[1:]
    lam = cnt.mean(); a = 1 + int(cnt.argmax())
    fano.append(cnt.var() / lam)
    if s in (3, 5, 7, 11, 31, 101, 211, 307, 401, 463):
        print(f"  {s:4d} {k:6d} {lam:9.2f} {cnt.max():6d} {cnt.var() / lam:7.3f}")
    alive &= (rows % s != a); k = int(alive.sum())
print(f"rows left by the greedy cover on the real rows: {k};  for a typical N: {R * np.prod([1 - 1 / (s - 1) for s in cov]):.1f}")
rng = np.random.default_rng(1)
for name, draw in (("Poisson", lambda k, s: rng.poisson(k / (s - 1), size=s - 1)),
                   ("multinomial", lambda k, s: rng.multinomial(k, [1 / (s - 1)] * (s - 1)))):
    res = []
    for t in range(20):
        k = R
        for s in cov: k -= int(draw(k, s).max())
        res.append(k)
    print(f"same greedy rule, {name} class counts: {np.mean(res):.1f} rows left (sd {np.std(res):.1f} over 20 runs)")
print(f"mean variance/mean of the class counts on the real greedy path: primes below 50: {np.mean(fano[:14]):.3f}; "
      f"50 to 200: {np.mean(fano[14:45]):.3f}; above 200: {np.mean(fano[45:]):.3f}")
