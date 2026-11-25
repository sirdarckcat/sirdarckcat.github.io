"""Q3: operations a member to sieve a window of W members of one cover (R rows below Q) to depth B, when each prime s takes the cheaper
of per-row start positions (R visits) and lattice enumeration of the residues below Q (W Q / s + log2 s steps): primes above W only."""
import math
from sympy import primerange
R, Q = 1502, 200000
import numpy as np
for B in (10 ** 7, 10 ** 8):
    ps = np.array(list(primerange(467, B)), dtype=np.float64)
    for lw in (15, 17, 19, 21, 24):
        W = 2.0 ** lw
        big = ps[ps > W]
        per_row = R * np.ones_like(big)
        lattice = W * Q / big + np.log2(big)
        ops = np.minimum(per_row, lattice).sum() / W
        visits_only = R * big.size / W
        sstar = W * Q / R
        print(f"B={B:.0e} W=2^{lw}: {ops:9.0f} operations a member for the primes above W (crossover s* = {sstar:.2e}); per-row visits alone {visits_only:9.0f}")
