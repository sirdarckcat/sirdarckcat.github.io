#!/usr/bin/env python3
"""No tie between any two rows, on real 200-digit members (ml_data.npz: 1,500 members, rows sieved to 10^6 and
by the 25 control primes after the fact, every survivor Fermat-tested).  For every pair of rows: the number of members
in which both survive and both are prime, against independence.  A tie (the two rows succeed or fail together)
would give about 15 joint primes for a pair; independence gives 0.8."""
import numpy as np, math
d = np.load("ml_data.npz"); mem, q, y, ctrl = d["mem"], d["q"], d["y"], d["ctrl"]
keep = ~ctrl; mem, q, y = mem[keep], q[keep], y[keep]
uq, qi = np.unique(q, return_inverse=True); nm = mem.max() + 1
A = np.zeros((nm, len(uq)), dtype=np.float32); P = np.zeros_like(A); A[mem, qi] = 1; P[mem, qi] = y
pi = y.mean(); C = P.T @ P; Nn = A.T @ A
iu = np.triu_indices(len(uq), 1); c = C[iu]; nn = Nn[iu]; E = nn * pi * pi
print(f"members {nm}, rows {len(uq)}, pairs {len(c)}, prime rate of a surviving row {pi:.5f}")
print(f"joint primes over all pairs: found {c.sum():.0f}, independence expects {E.sum():.0f}, ratio {c.sum() / E.sum():.4f}")
print(f"a pair survives together in {nn.mean():.0f} members on average; independence expects {E.mean():.3f} joint primes a pair, a tie {nn.mean() * pi:.1f}")
h = np.bincount(c.astype(int)); lam = E.mean()
print("joint primes a pair:   " + " ".join(f"{i}:{h[i]}" for i in range(len(h))))
# Poisson mixture expectation with each pair's own mean
ex = [float((np.exp(-E) * E ** i / math.factorial(i)).sum()) for i in range(len(h) + 2)]
print("independent (Poisson): " + " ".join(f"{i}:{ex[i]:.1f}" for i in range(len(h) + 2)))
print(f"largest joint count {int(c.max())}; variance of the count over pairs / mean: {c.var() / c.mean():.4f} (1 for independent rows up to the spread of the means: {(E.var() + E.mean()) / E.mean():.4f})")
# rows in a member: primes per member dispersion
tot = P.sum(1); al = A.sum(1); print(f"primes per member: variance / binomial variance = {((tot - al * pi) ** 2).mean() / (al * pi * (1 - pi)).mean():.4f} +- {math.sqrt(2 / nm):.4f}")
