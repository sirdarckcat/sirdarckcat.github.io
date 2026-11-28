#!/usr/bin/env python3
"""A toy world of characteristic 0 with an automorphism: the Goldbach game in Z[i].

    python3 gauss_ties.py [R = 5000] [largest row norm = 600]

Targets: the even Gaussian integers N = x + yi (x + y even) with 0 < |N| <= R, in the quarter plane x > 0, y >= 0.
Rows: every Gaussian prime pi (all associates), by norm.  g(N) = the least norm of a Gaussian prime pi with N - pi a
Gaussian prime.  The maps z -> u conj(z) (u a unit) are additive and send primes to primes, so for a target fixed by
one of them (the real axis, the diagonal) the rows pi and u conj(pi) succeed or fail together: N - u conj(pi) =
u conj(N - pi).  A fixed target has half the independent trials of a generic one at every norm.
Output: the survival counts #{g(N) > m} of the generic targets and of the targets on the two fixed lines, and the
ratio of the logarithms of the survival frequencies (2 if the trials are independent and the tie is the only effect).
"""
import sys, math, numpy as np
R = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
QN = int(sys.argv[2]) if len(sys.argv) > 2 else 600
LIM = (R + int(QN ** .5) + 2) ** 2 + 1
sv = np.ones(LIM + 1, dtype=bool); sv[:2] = False
for i in range(2, int(LIM ** .5) + 1):
    if sv[i]: sv[i * i::i] = False

def gprime(u, v):
    n = u.astype(np.int64) ** 2 + v.astype(np.int64) ** 2
    res = sv[n]
    ax = v == 0
    if ax.any(): a = np.abs(u[ax]); res[ax] = sv[a] & (a % 4 == 3)
    ax = u == 0
    if ax.any(): a = np.abs(v[ax]); res[ax] = sv[a] & (a % 4 == 3)
    return res

# rows by norm
rows = {}
B = int(QN ** .5) + 1
for a in range(-B, B + 1):
    for b in range(-B, B + 1):
        m = a * a + b * b
        if m < 2 or m > QN: continue
        if (a != 0 and b != 0 and sv[m]) or (b == 0 and sv[abs(a)] and abs(a) % 4 == 3) or (a == 0 and sv[abs(b)] and abs(b) % 4 == 3):
            rows.setdefault(m, []).append((a, b))
norms = sorted(rows)

xs = np.arange(1, R + 1, dtype=np.int32)
X, Y = np.meshgrid(xs, np.arange(0, R + 1, dtype=np.int32), indexing="ij")
keep = (X.astype(np.int64) ** 2 + Y.astype(np.int64) ** 2 <= R * R) & ((X + Y) % 2 == 0)
x = X[keep]; y = Y[keep]; del X, Y, keep
kind = np.zeros(len(x), dtype=np.int8); kind[y == 0] = 1; kind[x == y] = 2      # 0 generic, 1 real axis, 2 diagonal
tot = [int((kind == k).sum()) for k in range(3)]
print(f"# R = {R}: targets generic {tot[0]}, real axis {tot[1]}, diagonal {tot[2]}; rows to norm {QN}: {sum(len(v) for v in rows.values())}")
print("# norm m | rows of that norm | generic alive after m | real axis alive | diagonal alive | ln P(real)/ln P(generic) | ln P(diag)/ln P(generic)")
alive = np.arange(len(x))
best = {0: (0, None), 1: (0, None), 2: (0, None)}
g = np.zeros(len(x), dtype=np.int32)
for m in norms:
    xa = x[alive]; ya = y[alive]
    hit = np.zeros(len(alive), dtype=bool)
    for a, b in rows[m]:
        hit |= gprime(xa - a, ya - b)
    g[alive[hit]] = m
    alive = alive[~hit]
    c = [int((kind[alive] == k).sum()) for k in range(3)]
    lp = [math.log(c[k] / tot[k]) if c[k] else float("-inf") for k in range(3)]
    r1 = lp[1] / lp[0] if c[1] and c[0] and lp[0] < 0 else float("nan")
    r2 = lp[2] / lp[0] if c[2] and c[0] and lp[0] < 0 else float("nan")
    print(f"{m} | {len(rows[m])} | {c[0]} | {c[1]} | {c[2]} | {r1:.3f} | {r2:.3f}", flush=True)
    if len(alive) == 0: break
g[alive] = QN + 1
for k, name in ((0, "generic"), (1, "real axis"), (2, "diagonal")):
    sel = np.nonzero(kind == k)[0]; j = sel[np.argmax(g[sel])]
    print(f"# deepest {name}: g = {g[j]} at N = {x[j]} + {y[j]}i (of {tot[k]} targets; sqrt of the generic count = {tot[0] ** .5:.0f})")
