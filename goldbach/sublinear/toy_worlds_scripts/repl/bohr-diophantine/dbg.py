import math, numpy as np
from flint import fmpz_mat
from base import *
from lists_scan import lists, scan, LATER
from lists_lll import lattice
L = lists(6, 0.10); Ls = [(s, G) for s, G, _, _ in L]
rows, idx, P, lam = lattice(Ls); n = len(idx)
B = fmpz_mat(rows).lll(delta=0.99, eta=0.51)
out = []
for i in range(B.nrows()):
    v = [int(B[i, t]) for t in range(n + 2)]
    nz = [(idx[t][0], idx[t][1], v[t] // lam) for t in range(n) if v[t]]
    out.append((math.sqrt(sum(x * x for x in v)) / lam, nz, v[n] / lam, v[n + 1] // lam))
out.sort(key=lambda t: t[0])
for o in out[:6]: print(o)
print(out[len(out)//2]); print(out[-1])
print("rank", B.rank(), "rows", B.nrows(), "zero rows", sum(1 for o in out if o[0] == 0))
