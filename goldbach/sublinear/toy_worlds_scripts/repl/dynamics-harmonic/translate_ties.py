#!/usr/bin/env python3
"""Ties between rows of DIFFERENT targets: N - q = (N + t) - (q + t).  For the real 200,000 cover and every even shift
t < Q: the rows of N' = N + t (N' inherits the shifted classes a_r + t), how many of them test an integer that is also a row
of N (q' - t prime), and how many are left free.  All t at once by correlation (FFT)."""
import math, numpy as np
from common import setup, cover
import cover_record as cr
cov, rows, N0, M, K = setup(); Q = 200000
L = 1 << 19; off = Q
m = np.arange(-Q, Q); U = np.ones(2 * Q, bool)
for r, a in cov: U &= (m % r) != a
isp = np.zeros(2 * Q, bool); PR = cr.PR[cr.PR < Q]; isp[PR + off] = True          # odd primes below Q, index m + Q
P = np.zeros(L); P[:2 * Q] = isp
A1 = np.zeros(L); A1[:2 * Q] = U                         # rows'(t)  = sum_x P[x] U[x - t]
A2 = np.zeros(L); A2[:2 * Q] = U & isp                   # tied(t)   = sum_x P[x] (U & prime)[x - t]
FP = np.fft.rfft(P)
c1 = np.fft.irfft(FP * np.conj(np.fft.rfft(A1)), L); c2 = np.fft.irfft(FP * np.conj(np.fft.rfft(A2)), L)
t = np.arange(0, Q, 2); rows_t = np.rint(c1[t]).astype(int); tied_t = np.rint(c2[t]).astype(int); free_t = rows_t - tied_t
print(f"t=0: rows {rows_t[0]} tied {tied_t[0]} (must be {len(rows)}, {len(rows)})")
s = slice(1, None)
print(f"even t in [2,{Q}): rows of N+t: mean {rows_t[s].mean():.1f} sd {rows_t[s].std():.1f} min {rows_t[s].min()} ; tied to a row of N: mean {tied_t[s].mean():.1f} max {tied_t[s].max()} ; free rows: mean {free_t[s].mean():.1f} sd {free_t[s].std():.1f} min {free_t[s].min()} at t={int(t[s][free_t[s].argmin()])}")
for tt in (2, 6, 30, 210, 2310, 30030, 60060, 90090, 510510 % Q):
    i = tt // 2; print(f"  t={tt}: rows {rows_t[i]}, tied {tied_t[i]}, free {free_t[i]}")
lam = 36.5 / 1502
print(f"given a hit N at level Q, expected number of further hits among N+t: sum_t exp(-lam*free(t)) = {np.exp(-lam*free_t[s]).sum():.3e}  (a fresh member of the cover: exp(-36.5) = {math.exp(-36.5):.3e}); best single t: exp(-{lam*free_t[s].min():.1f})")
# small t: the first rows q' < t are never tied; shifts below 2000
i = np.arange(1, 1000); j = free_t[i].argmin(); print(f"  best t below 2000: t={int(t[i][j])}: rows {rows_t[i][j]}, tied {tied_t[i][j]}, free {free_t[i][j]}")
