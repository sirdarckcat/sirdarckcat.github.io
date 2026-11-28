#!/usr/bin/env python3
"""The law mean lambda on z-rough = rho'(u)/omega(u), against the LOCAL measurements of mini_parity.py (intervals of 4e7 at X, z-rough)."""
import math, numpy as np
h = 1e-3; U = 12; ng = int(round(U / h)) + 1; ug = np.arange(ng) * h; i1 = int(round(1 / h)); i2 = 2 * i1
rho = np.ones(ng)
for i in range(i1 + 1, ng): rho[i] = h * (rho[i - i1] / 2 + rho[i - i1 + 1:i].sum()) / (ug[i] - h / 2)
om = np.zeros(ng); om[i1:i2 + 1] = 1 / ug[i1:i2 + 1]; W = ug * om
for i in range(i2 + 1, ng): W[i] = W[i - 1] + h * 0.5 * (om[i - 1 - i1] + om[i - i1]); om[i] = W[i] / ug[i]
R = lambda u: float(np.interp(u, ug, rho)); O = lambda u: float(np.interp(u, ug, om))
meas = [(5e11, 1000, -0.028779, 0.000556, 0.45848, 0.89131), (1e12, 1000, -0.022738, 0.000556, 0.44686, 0.87386), (3e12, 1000, -0.016312, 0.000556, 0.43004, 0.84628),
        (7e12, 1000, -0.010878, 0.000556, 0.41704, 0.82511), (1e12, 100, -0.000298, 0.000456, 0.30067, 0.60115)]
print("X | z | u | mean lambda on rough, measured | law rho'(u)/omega(u) | primes among rough, measured | 1/(u omega(u)) | primes among odd-Omega rough, measured | 2/(u omega(u) + rho(u-1))")
for X, z, ml, se, pr, po in meas:
    u = math.log(X) / math.log(z)
    print(f"{X:g} | {z} | {u:.3f} | {ml:+.6f} +- {se:.6f} | {-R(u - 1) / (u * O(u)):+.6f} | {pr:.5f} | {1 / (u * O(u)):.5f} | {po:.5f} | {2 / (u * O(u) + R(u - 1)):.5f}")
