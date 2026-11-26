#!/usr/bin/env python3
"""The digit-sum parities of the deep N are NOT fair (champ_analyze.txt: Thue-Morse chi2 475).  Is that structure beyond
residues, or the finite-length correlation between digit sums and residues (Newman 1969: multiples of 3 below x have
an excess of even binary digit sums of order x^(log 3/log 4))?  Matched controls: for every hit N the numbers
N + 2Pj, j = +-1..+-8, with P = 3*5*...*23 (the same residue modulo every odd prime <= 23, about the same size).
If the bias is a residue effect the controls show it too; structure beyond residues would leave a difference."""
import numpy as np, math
d = np.fromfile("big/hits_2e10.bin", dtype=np.dtype([("N", "<u8"), ("g", "<u4")]))
N = d["N"].astype(np.int64); g = d["g"]; X = 2 * 10 ** 10
def popc(a):
    a = a.copy(); s = np.zeros(len(a), dtype=np.int64)
    while a.any(): s += a & 1; a >>= 1
    return s
def dsum(a, b):
    a = a.copy(); s = np.zeros(len(a), dtype=np.int64)
    while a.any(): s += a % b; a //= b
    return s
feats = {"binary digit sum odd (Thue-Morse)": lambda a: popc(a) % 2 == 1, "decimal digit sum odd": lambda a: dsum(a, 10) % 2 == 1,
         "binary digit sum = 0 mod 3": lambda a: popc(a) % 3 == 0, "base-4 digit sum odd": lambda a: dsum(a, 4) % 2 == 1,
         "bit 20 of N": lambda a: (a >> 20) & 1 == 1}
for Pname, P in (("3..23", 111546435), ("3 only", 3), ("3,5,7", 105), ("none (shift by 2j)", 1)):
    print(f"\ncontrols share the residues of N modulo the primes: {Pname}  (shift 2*{P}*j)")
    for L in (500, 700, 1000):
        Nh = N[g >= L]
        ctl = np.concatenate([Nh + 2 * P * j for j in (-8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8)]); ctl = ctl[(ctl > 0) & (ctl <= X)]
        for name, f in feats.items():
            a = f(Nh).mean(); b = f(ctl).mean(); se = math.sqrt(a * (1 - a) / len(Nh) + b * (1 - b) / len(ctl))
            print(f"  g >= {L:4d}  {name:34s} hits {a:.5f}  controls {b:.5f}  difference {a - b:+.5f} +- {se:.5f}  (z = {(a - b) / se:+.1f})")
