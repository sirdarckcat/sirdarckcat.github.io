#!/usr/bin/env python3
"""blockperm.py: permutation calibration of blockmin.py (the law F there is the window's own histogram, so the chi-square is not
calibrated): mean and sd of the block minima after shuffling the members, 40 shuffles."""
import numpy as np
S = np.fromfile("S8.100000000.u16", dtype=np.uint16); K = len(S); rng = np.random.default_rng(7)
parts = {"contiguous 4096": lambda A: A[:(K // 4096) * 4096].reshape(4096, K // 4096).min(axis=1),
         "k mod 467": lambda A: A[:(K // 467) * 467].reshape(K // 467, 467).min(axis=0),
         "k mod 467*479": lambda A: A[:(K // 223693) * 223693].reshape(K // 223693, 223693).min(axis=0)}
real = {n: (f(S).mean(), f(S).std()) for n, f in parts.items()}
sh = {n: [] for n in parts}
for i in range(40):
    A = rng.permutation(S)
    for n, f in parts.items(): m = f(A); sh[n].append((m.mean(), m.std()))
for n in parts:
    a = np.array(sh[n]); print(f"{n}: real mean of minima {real[n][0]:.4f}, shuffled {a[:,0].mean():.4f} +- {a[:,0].std():.4f} (z = {(real[n][0]-a[:,0].mean())/a[:,0].std():+.2f}); real sd {real[n][1]:.4f}, shuffled {a[:,1].mean():.4f} +- {a[:,1].std():.4f} (z = {(real[n][1]-a[:,1].mean())/a[:,1].std():+.2f})")
