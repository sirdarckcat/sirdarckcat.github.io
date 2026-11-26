#!/usr/bin/env python3
"""coincid.py: first-order prediction of corr(S(k), S(k+D)) from the tables alone:
   C1(D) = sum over later primes p <= depth of w_p^2 [A_p(D M mod p)/p - n^2/p^2],  A_p(d) = #{(q,q') rows: q' - q = d mod p}
(d = 0 includes the n diagonal pairs: that is the 'common residue' term; d != 0 is pure coincidence of row differences)."""
import sys, math, numpy as np
depth = 1000000
nr, npr, K, N0, M = open("base6.meta").read().split(); N0 = int(N0); M = int(M); K = int(K)
raw = np.fromfile("base6.bin", dtype=np.uint32, offset=24); n = int(nr); npr = int(npr)
rows = raw[:n].astype(np.int64); P = raw[n:n + npr].astype(np.int64)
S = np.fromfile("S.1000000.u16", dtype=np.uint16).astype(np.float64); var = S.var(); w = S.mean() / n
Mp = np.array([M % int(p) for p in P], dtype=np.int64)
rho = np.load("rho.S.1000000.npy")
def C1(D):
    tot = 0.0; diag = 0.0
    for p, mp in zip(P.tolist(), Mp.tolist()):
        d = (D % p) * mp % p
        r = np.sort(rows % p)
        t = (r + d) % p
        lo = np.searchsorted(r, t, side="left"); hi = np.searchsorted(r, t, side="right")
        A = int((hi - lo).sum()); wp = w / (1 - 1 / p)
        term = wp * wp * (A / p - n * n / p / p); tot += term
        if d == 0: diag += wp * wp * n / p * (1 - 1 / p)
    return tot / var, diag / var
print("D | first-order prediction C1(D)/Var | of which common residues (p | D) | measured rho(D) (pair noise 0.00022)")
for D in (1, 2, 210, 463, 467, 479, 934, 1009, 10007, 100003, 467 * 479, 5037904, 4700906, 9448565, 10534137, 1234567):
    c, dg = C1(D); print(f"{D} | {c:+.5f} | {dg:.5f} | {rho[D-1]:+.5f}", flush=True)
