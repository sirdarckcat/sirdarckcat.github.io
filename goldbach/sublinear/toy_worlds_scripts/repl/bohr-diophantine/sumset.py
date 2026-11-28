#!/usr/bin/env python3
"""Sumset saturation of the real lists: |G + G - G| / s for the best l classes (or best rho) of the first 12 later primes,
and the LLL planted test for l = 3..10 (does the lattice still see the list?)."""
import math, numpy as np
from base import *
from lists_scan import LATER
from lists_lll import run
def ggg(G, s):
    a = np.zeros(s, dtype=bool); a[G] = True
    two = np.zeros(s, dtype=bool)
    for c in G: two |= np.roll(a, c)            # G + G
    three = np.zeros(s, dtype=bool)
    for c in G: three |= np.roll(two, -c)       # G + G - G
    return int(two.sum()), int(three.sum())
print("l | mean |G+G|/s | mean |G+G-G|/s | primes (of 12) with G+G-G = Z/s      (G = the l classes of the real table that strike most rows)")
for l in (3, 4, 5, 6, 7, 8, 10, 12, 16, 24, 48, 96):
    r2 = []; r3 = []; full = 0
    for s in LATER[:12]:
        f, g = tables(s); G = np.argsort(-g, kind="stable")[:l]
        t2, t3 = ggg(G, s); r2.append(t2 / s); r3.append(t3 / s); full += (t3 == s)
    print(f"{l} | {np.mean(r2):.3f} | {np.mean(r3):.3f} | {full}")
rng = np.random.default_rng(7)
print("\nplanted member, J = 12, lists of l (LLL, Kannan embedding), 6 trials each")
for l in (3, 4, 5, 6, 7, 8, 10):
    ok = 0
    for trial in range(6):
        kstar = int(rng.integers(0, K)); Ls = []
        for s in LATER[:12]:
            f, g = tables(s); order = [int(c) for c in np.argsort(-g, kind="stable") if c != kstar % s][:l - 1]
            Ls.append((s, np.array(sorted(order + [kstar % s]))))
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): ok += run(Ls, "", {kstar})
    print(f"l = {l}: l^3/s = {l ** 3 / 500:.2f}; knapsack density {12 * math.log(l) / 57.93:.2f}; recovered {ok} of 6")
