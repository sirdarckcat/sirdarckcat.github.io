#!/usr/bin/env python3
"""Checks an fscan built with fscan_wide.patch against an independent replay in Python, on a class whose rows need the wide masks.

    gcc -O3 -march=native -fopenmp -DMAXROWS=512 -o fscan512 fscan.c -lm
    python3 check_wide.py ./fscan512 [Q] [L] [Xmin] [count]       (default 14138 383 1e29 1528729: 30 digits, rows 258)

1. dump=1 lists the residue vectors; the first one with the fewest rows is taken (above 256 at the default Q).
2. The exact stage: fscan's histogram of the alive rows (hist=1, sample=6: every 64th member) against the rows that no score
   prime in (43, L] kills, recomputed here for the same members.
3. Score, selection and Fermat: fscan's selected / kept / tests / prps with relaxed thresholds (theta = R - 118, Ta = 175) against
   the same pipeline here (byte score saturating at 255, exact rows, base-2 Fermat in row order until the first probable prime).
The member range is Xmin < N <= Xmax with Xmax chosen so that the vector has about `count` members."""
import subprocess
import sys

import numpy as np
from sympy import primerange

exe = sys.argv[1]
Q = int(sys.argv[2]) if len(sys.argv) > 2 else 14138
L = int(sys.argv[3]) if len(sys.argv) > 3 else 383
Xmin = int(float(sys.argv[4])) if len(sys.argv) > 4 else 10 ** 29
count = int(sys.argv[5]) if len(sys.argv) > 5 else 1528729
RS = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43)
M = 2
for p in RS:
    M *= p
SP = list(primerange(44, L + 1))


def run(*args):
    return subprocess.run([exe, *map(str, args)], capture_output=True, text=True, check=True).stdout


Xmax = Xmin + count * M
vec = None
for rhi in range(150, 513, 4):
    out = run(Q, L, 100, rhi, Xmin, Xmax, 0, 0, "dump=1", "threads=1")
    vs = [l.split() for l in out.splitlines() if l.startswith("V ")]
    if vs:
        vec = min(vs, key=lambda v: (int(v[2]), int(v[1])))
        break
N0, R = int(vec[1]), int(vec[2])
rows = [int(x) for x in vec[3:]]
assert len(rows) == R
print(f"Q={Q} L={L}: vector N0={N0} with {R} rows (the fewest), members in ({Xmin:.3g}, {Xmax:.3g}]")
kmin = (Xmin - N0) // M + 1 if Xmin > N0 else 0
kmax = (Xmax - N0) // M


def alive(N):
    return [q for q in rows if all((N - q) % s for s in SP)]


# 2. the exact stage on the sampled members
out = run(Q, L, R, R, Xmin, Xmax, R - 95, R * 6 // 10, f"rref={R}", f"one={N0}", "sample=6", "hist=1", "threads=1")
ha = next(l for l in out.splitlines() if l.startswith("HA")).split()[1:]
fs = {int(a): int(c) for a, c in (t.split(":") for t in ha)}
py = {}
for k in range(kmin, kmax + 1):
    if k % 64 == 0:
        a = len(alive(N0 + k * M))
        py[a] = py.get(a, 0) + 1
print(f"exact stage, {sum(py.values())} sampled members: fscan and the replay {'AGREE' if fs == py else 'DIFFER'}")
ok = fs == py

# 3. score, selection, Fermat
th, Ta = R - 118, 175
out = run(Q, L, R, R, Xmin, Xmax, th, Ta, f"rref={R}", f"one={N0}", "threads=1")
st = next(l for l in out.splitlines() if l.startswith("STATS")).split("|")[1].split()
st = dict(t.split("=") for t in st)
ks = np.arange(kmax - kmin + 1, dtype=np.int64)
score = np.zeros(len(ks), dtype=np.int64)
for s in SP:
    cnt = np.zeros(s, dtype=np.int64)
    for q in rows:
        cnt[q % s] += 1
    score += cnt[((N0 + kmin * M) % s + ks * (M % s)) % s]
score = np.minimum(score, 255)
sel = kept = tests = prps = 0
for k in (kmin + ks[score >= th]).tolist():
    sel += 1
    N = N0 + k * M
    al = alive(N)
    if len(al) > Ta:
        continue
    kept += 1
    for q in al:
        tests += 1
        if pow(2, N - q - 1, N - q) == 1:
            prps += 1
            break
mine = dict(members=kmax - kmin + 1, selected=sel, kept=kept, tests=tests, prps=prps)
theirs = {k: int(st[k]) for k in mine}
print(f"selection and Fermat: fscan {theirs}, replay {mine}: {'AGREE' if theirs == mine else 'DIFFER'}")
ok &= theirs == mine
print("ALL AGREE" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
