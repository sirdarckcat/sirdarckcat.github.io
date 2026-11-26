#!/usr/bin/env python3
"""covmove_prep.py: the move 'change the class of the cover prime 463 and keep the residues modulo 467*479*487':
N' - N = (M/463) t with 467*479*487 | t.  For each new class a' find the offset Delta = k' - k (if one lies in the window)."""
import math, numpy as np
from sympy.ntheory.modular import crt
f = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
l = [x for x in open(f) if x.startswith("COVER")][0].split(); cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in l if ":" in t]
Q = 200000
s = np.ones(Q, dtype=bool); s[:2] = False
for i in range(2, int(Q ** .5) + 1):
    if s[i]: s[i * i::i] = False
PR = np.nonzero(s)[0]; PR = PR[PR > 2]
mods = [2] + [r for r, _ in cov]; M = math.prod(mods); R = 463; Mq = M // R
N0 = int(crt(mods, [0] + [a for _, a in cov])[0]); K = (10 ** 200 - 1 - N0) // M + 1
a_old = dict(cov)[R]; L3 = 467 * 479 * 487
alive0 = np.ones(len(PR), dtype=bool)
for r, a in cov:
    if r != R: alive0 &= (PR % r) != a
out = []
for a2 in range(1, R):
    if a2 == a_old: continue
    N02 = int(crt(mods, [0] + [(a2 if r == R else a) for r, a in cov])[0]); t0 = (N02 - N0) // Mq; assert (N02 - N0) % Mq == 0
    # t = t0 + R (k'-k) = j L3  ->  j = t0 / L3 mod R
    j0 = t0 * pow(L3, -1, R) % R; Delta = (j0 * L3 - t0) // R; assert (j0 * L3 - t0) % R == 0
    for Dl in (Delta, Delta - L3):
        if abs(Dl) < K // 2:
            nrows = int((alive0 & ((PR % R) != a2)).sum()); out.append((nrows, a2, Dl))
out.sort(); print("classes a' of 463 whose 3-prime-preserving offset lies within K/2: (rows of the new cover, a', Delta)"); print(out[:12], len(out))
