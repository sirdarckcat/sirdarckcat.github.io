#!/usr/bin/env python3
"""Completion of champ_digits.py (that run was cut short while printing the '3,5,7' block): which residues carry the bias of the
decimal digit-sum parity?  Controls N + 2Pj, j = +-1..+-4, sharing the residues of N modulo the primes of P; level g >= 500."""
import numpy as np, math
d = np.fromfile("big/hits_2e10.bin", dtype=np.dtype([("N", "<u8"), ("g", "<u4")]))
N = d["N"].astype(np.int64); X = 2 * 10 ** 10; del d
def popc(a):
    a = a.copy(); s = np.zeros(len(a), dtype=np.int8)
    while a.any(): s ^= (a & 1).astype(np.int8); a >>= 1
    return s
def dpar(a):
    a = a.copy(); s = np.zeros(len(a), dtype=np.int8)
    while a.any(): s ^= ((a % 10) & 1).astype(np.int8); a //= 10
    return s
feats = {"binary digit sum odd (Thue-Morse)": popc, "decimal digit sum odd": dpar}
for Pname, P in (("none (neighbours N + 2j)", 1), ("3", 3), ("11", 11), ("3 and 11", 33), ("3, 5, 7", 105), ("3, 5, 7, 11", 1155)):
    for name, f in feats.items():
        a = f(N).mean(); tot = 0; cnt = 0
        for j in (-4, -3, -2, -1, 1, 2, 3, 4):
            c = N + 2 * P * j; c = c[(c > 0) & (c <= X)]; v = f(c); tot += int(v.sum()); cnt += len(v)
        b = tot / cnt; se = math.sqrt(a * (1 - a) / len(N) + b * (1 - b) / cnt)
        print(f"controls share N mod {Pname:26s} {name:34s} hits {a:.5f}  controls {b:.5f}  difference {a - b:+.5f} +- {se:.5f}  (z = {(a - b) / se:+.1f})", flush=True)
