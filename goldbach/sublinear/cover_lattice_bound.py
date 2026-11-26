#!/usr/bin/env python3
"""Does the one structure of the lists (they are all images of the same rows) let a lattice find aligned members?

    python3 cover_lattice_bound.py [rows = 1502] [ln of the window = 16.9] [largest modulus = 463]

The one structural fact: "N mod s lies in the image of the rows" for many primes s at once means the single integer F(N) = prod over rows (N - q)
has a large smooth part.  Root-finding modulo an unknown divisor (Coppersmith, Howgrave-Graham, May; Boneh's CRT decoding for smooth integers in
short intervals): for a polynomial of degree n and a modulus P, all k < K with gcd(F(N0 + kM), P) >= d are found in polynomial time when
ln K <= (ln d)^2 / (n ln P).  Here: how large the smooth part of F(N) is for a typical member, for the best member of a window, and what is needed.
The kills by a prime s are taken Poisson with mean n/s (random member); the modulus is P = prod s^e over the primes in (x, z].
"""
import math, sys
import numpy as np
n = int(sys.argv[1]) if len(sys.argv) > 1 else 1502; lnK = float(sys.argv[2]) if len(sys.argv) > 2 else 16.9; x = int(sys.argv[3]) if len(sys.argv) > 3 else 463
ZMAX = 300000
sv = np.ones(ZMAX, dtype=bool); sv[:2] = False
for i in range(2, int(ZMAX ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
ps = np.nonzero(sv)[0]; ps = ps[ps > x].astype(float)
print(f"rows n = {n}, window ln K = {lnK}, moduli up to {x}")
print("primes (x, z] | exponent cap e | ln P | smooth part of F(N): typical member, sd | needed sqrt(n ln K ln P) | typical / needed | best of the window (+5.4 sd) / needed | window the method could handle for a typical member, ln K")
best = None
for z in (600, 1000, 1500, 2300, 4000, 10000, 50000, 200000):
    s = ps[ps <= z]; lam = n / s                         # kills by s: Poisson(n/s) for a random member
    for e in (1, 2, 3, 8):
        # E min(Poisson(lam), e) and its variance
        ks = np.arange(0, 60)[:, None]; pm = np.exp(-lam + ks * np.log(lam) - np.array([math.lgamma(k + 1) for k in range(60)])[:, None])
        m1 = (np.minimum(ks, e) * pm).sum(0); m2 = (np.minimum(ks, e) ** 2 * pm).sum(0)
        lnP = e * np.log(s).sum(); mean = (m1 * np.log(s)).sum(); sd = math.sqrt(((m2 - m1 ** 2) * np.log(s) ** 2).sum())
        need = math.sqrt(n * lnK * lnP); r = mean / need
        if best is None or r > best[0]: best = (r, z, e)
        if e in (1, 3): print(f"({x}, {z}] | {e} | {lnP:.0f} | {mean:.0f}, {sd:.0f} | {need:.0f} | {r:.3f} | {(mean + 5.4 * sd) / need:.3f} | {mean ** 2 / (n * lnP):.2f}")
print(f"largest typical/needed over the grid: {best[0]:.3f} at z = {best[1]}, cap {best[2]}")
