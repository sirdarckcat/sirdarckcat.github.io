#!/usr/bin/env python3
"""Saturation with three DISTINCT list classes: every class of Z/s is c1 + c2 - c3 with c1, c2, c3 distinct in G
(so the integer vector e_c1 + e_c2 - e_c3, of squared norm 3 and coordinate sum 1, represents it)."""
import math, numpy as np, itertools
from base import *
from lists_scan import LATER
for label, size in (("16 classes", 16), ("20 classes", 20), ("24 classes", 24), ("rho = 5%", 0.05), ("rho = 10%", 0.10), ("rho = 20%", 0.20)):
    full = 0; frac = []
    for s in LATER[:12]:
        f, g = tables(s); n = size if isinstance(size, int) else int(math.ceil(size * s)); G = [int(c) for c in np.argsort(-g, kind="stable")[:n]]
        seen = np.zeros(s, dtype=bool)
        for a, b in itertools.combinations(G, 2):
            for c in G:
                if c != a and c != b: seen[(a + b - c) % s] = True
        full += seen.all(); frac.append(seen.mean())
    print(f"{label}: classes of Z/s represented by three distinct list classes: mean {np.mean(frac):.4f}; all of Z/s at {full} of 12 primes")
