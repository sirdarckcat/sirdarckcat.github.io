#!/usr/bin/env python3
"""FRESH DATA (seed 4242, other members): replication of the largest pair scores of ml_screen.py on two halves of the members (even and odd member index)."""
import numpy as np, math
d = np.load("ml_data_fresh.npz"); mem, y, ctrl, hi, res, sp, lo = (d[x] for x in ("mem", "y", "ctrl", "hi", "res", "sp", "lo"))
keep = ~ctrl; yy = y[keep].astype(float); m = mem[keep]
def bit(a, i): return ((a[keep] >> np.uint64(i)) & np.uint64(1)).astype(float)
i23 = list(sp).index(23)
f1 = bit(hi, 32); f2 = np.cos(2 * np.pi * res[keep][:, i23] / 23.0)
def z(a, w):
    a = a - a.mean(); w = w - w.mean(); return (a * w).sum() / math.sqrt((a * a).sum() * w.var())
for name, sel in (("all", np.ones(len(yy), bool)), ("even members", m % 2 == 0), ("odd members", m % 2 == 1)):
    a = (f1[sel] - f1[sel].mean()) / f1[sel].std(); b = (f2[sel] - f2[sel].mean()) / f2[sel].std()
    print(f"high bit 32 x cos(n mod 23): {name}: z = {z(a * b, yy[sel]):+.2f}")
