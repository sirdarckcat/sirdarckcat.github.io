#!/usr/bin/env python3
"""Second-order term of a cover's success probability: do the rows it leaves cluster modulo the sieve primes?

For a random member of a cover, P(no row prime) = (1-p)^k * exp(p^2 * T + ...), with
T = sum over sieve primes s of [pairs of left rows congruent mod s] * ln((s-1)/(s-2)) + C(k,2) * sum_s ln((1-2/s)/(1-1/s)^2).
Prints T for each cover and its spread, in nats of success probability.
"""
import math, sys
import numpy as np

def primes_upto(n):
    sv = np.ones(n + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]: sv[i * i::i] = False
    return np.nonzero(sv)[0]

Q, path, ncov, B = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rows_all = primes_upto(Q - 1); rows_all = rows_all[rows_all > 2]
sieve_all = primes_upto(B)
lnN, out = 200 * math.log(10), []
lines = [l.split() for l in open(path) if l.startswith("COVER")]
step = max(1, len(lines) // ncov)
for parts in lines[::step][:ncov]:
    k_file = int(parts[1]); vec = [tuple(map(int, x.split(":"))) for x in parts[2:]]
    alive = np.ones(len(rows_all), dtype=bool)
    for r, a in vec: alive &= (rows_all % r) != a
    R = rows_all[alive]; k = len(R)
    mods = {r for r, _ in vec}
    boost = 2.0
    for r in mods: boost *= r / (r - 1)
    p = boost / lnN
    T = 0.0; base = 0.0
    for s in sieve_all:
        s = int(s)
        if s < 3 or s in mods: continue
        cnt = np.bincount(R % s, minlength=s)
        pairs = int((cnt * (cnt - 1) // 2).sum())
        T += pairs * math.log((s - 1) / (s - 2))
        base += math.log((1 - 2 / s) / (1 - 1 / s) ** 2)
    T += k * (k - 1) / 2 * base
    out.append((k_file, k, p, T))
ks = np.array([o[1] for o in out]); Ts = np.array([o[3] for o in out]); p = out[0][2]
print(f"{path.split('/')[-1]}: {len(out)} covers, rows left as recomputed {ks.min()}..{ks.max()} (file says {min(o[0] for o in out)}..{max(o[0] for o in out)}), p = {p:.5f}")
print(f"  T: mean {Ts.mean():+.3f}, sd {Ts.std():.3f}, min {Ts.min():+.3f}, max {Ts.max():+.3f}   (sieve primes up to {B})")
print(f"  in nats of success probability (p^2 T): mean {p*p*Ts.mean():+.6f}, sd {p*p*Ts.std():.6f}, best minus worst {p*p*(Ts.max()-Ts.min()):.6f}")
print(f"  for comparison one row is worth {-math.log(1-p):.4f} nats")
