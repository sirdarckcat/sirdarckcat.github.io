#!/usr/bin/env python3
import numpy as np, math
S = np.fromfile("S.1000000.u16", dtype=np.uint16).astype(np.float64); T = np.fromfile("SA.1000000.u16", dtype=np.uint16).astype(np.float64)
print("cover: mean", S.mean(), "sd", S.std(), "| cover with 463:235 (1504 rows): K", len(T), "mean", T.mean(), "sd", T.std(), "min", T.min())
Zs = (S - S.mean()) / S.std(); Zt = (T - T.mean()) / T.std()
def c(D):       # corr(S(k), T(k + D))
    if D >= 0: a, b = Zs[:len(Zs) - D], Zt[D:D + len(Zs) - D]
    else: a, b = Zs[-D:], Zt[:len(Zs) + D]
    m = min(len(a), len(b)); return float((a[:m] * b[:m]).mean()), 1 / math.sqrt(m)
Dl = -7764515
print("move: class of 463 changed -> 235 with residues mod 467*479*487 kept (k' = k + Delta, Delta = %d): corr %.5f +- %.5f" % ((Dl,) + c(Dl)))
for off in (1, -1, 2, 467, 1000, 467 * 479):
    print("   control, k' = k + Delta + %d: corr %.5f +- %.5f" % ((off,) + c(Dl + off)))
