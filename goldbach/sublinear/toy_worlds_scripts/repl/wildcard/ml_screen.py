#!/usr/bin/env python3
"""First- and second-order screening of the same 222 features on the same real rows (ml_data.npz, rows with no factor
<= 10^6): the z-score of every feature and of every product of two features against 'the row is prime', with the exact
permutation variance.  No information: mean z^2 = 1 and the largest |z| that of as many normal draws."""
import numpy as np, math
d = np.load("ml_data.npz")
mem, k, q, y, ctrl, lo, hi, res, jac, S, rank, sp = (d[x] for x in ("mem", "k", "q", "y", "ctrl", "lo", "hi", "res", "jac", "S", "rank", "sp"))
def bits(a): return ((a[:, None] >> np.arange(64, dtype=np.uint64)[None, :]) & np.uint64(1)).astype(np.float32)
F = [bits(lo)[:, 1:], bits(hi)]; names = [f"low bit {i}" for i in range(1, 64)] + [f"high bit {i}" for i in range(64)]
ang = 2 * np.pi * res.astype(np.float32) / sp[None, :].astype(np.float32); F += [np.cos(ang), np.sin(ang)]; names += [f"cos n mod {p}" for p in sp] + [f"sin n mod {p}" for p in sp]
for i, p in enumerate(sp[:5]): F.append((res[:, i][:, None] == np.arange(1, p)[None, :]).astype(np.float32)); names += [f"n = {a} mod {p}" for a in range(1, p)]
F.append(jac.astype(np.float32)); names += ["(-1|n)", "(2|n)", "(3|n)", "(5|n)", "(7|n)", "(q|n)"]
gap_prev = np.r_[0, np.diff(q)].astype(np.float64); gap_prev[rank == 0] = q[rank == 0]
gap_next = np.r_[np.diff(q), 0].astype(np.float64); last = np.r_[rank[1:] == 0, True]; gap_next[last] = 200000 - q[last]
pop = bits(lo).sum(1) + bits(hi).sum(1)
F.append(np.c_[q / 2e5, k / 2.14e7, S, rank / S, np.log(gap_prev + 1), np.log(gap_next + 1), pop].astype(np.float32)); names += ["q", "k", "survivors in the member", "rank of the row", "gap to the previous survivor", "gap to the next", "popcount"]
X = np.concatenate(F, axis=1)[~ctrl].astype(np.float64); yy = y[~ctrl].astype(np.float64); n = len(yy)
sd = X.std(0); ok = sd > 1e-9; X = (X[:, ok] - X[:, ok].mean(0)) / sd[ok]; names = [nm for nm, o in zip(names, ok) if o]
w = yy - yy.mean(); vw = w.var() * n / (n - 1)
z1 = (X.T @ w) / np.sqrt(n * vw)
print(f"rows {n}, primes {int(yy.sum())}, features in use {X.shape[1]} (constant ones dropped)")
print(f"single features: mean z^2 = {np.mean(z1 ** 2):.3f}, largest |z| = {np.abs(z1).max():.2f} ({names[int(np.abs(z1).argmax())]}); expected largest of {len(z1)} normal draws about {math.sqrt(2 * math.log(len(z1))):.2f}")
T = X.T @ (X * w[:, None]); S2 = (X ** 2).T @ (X ** 2); S1 = X.T @ X
z2 = T / np.sqrt((S2 - S1 ** 2 / n) * vw)
iu = np.triu_indices(X.shape[1], 1); zz = z2[iu]
i = int(np.abs(zz).argmax())
print(f"products of two features: {len(zz)} pairs, mean z^2 = {np.mean(zz ** 2):.3f}, largest |z| = {np.abs(zz).max():.2f} ({names[iu[0][i]]} x {names[iu[1][i]]}); expected largest about {math.sqrt(2 * math.log(len(zz))):.2f}")
print(f"   pairs with |z| > 4: {int((np.abs(zz) > 4).sum())} (expected {len(zz) * 6.33e-5:.1f}); > 4.5: {int((np.abs(zz) > 4.5).sum())} (expected {len(zz) * 6.8e-6:.2f})")
# sensitivity: the z a 'parity' coin would have (a feature that doubles the prime rate on half the rows)
pi = yy.mean(); print(f"for scale: a fair coin that doubles the prime rate of its half would have z = {pi * math.sqrt(n) / math.sqrt(pi * (1 - pi)):.0f}; a feature moving the rate by 1% of itself, z = {0.01 * pi * math.sqrt(n) / math.sqrt(pi * (1 - pi)):.2f}")
