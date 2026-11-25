# Check of the independent-move estimate: apply random sets of k single moves (each of cost <= 5) and compare the true number of alive rows with n0 + sum of the single costs.
import numpy as np, math, sys
rng = np.random.default_rng(5)
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rows = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]
cls = np.load('../lattice/cls_sa_11.npy')
cnt = np.zeros(len(rows), np.int32)
for p, c in zip(mods, cls): cnt[(rows % p) == c] += 1
n0 = int((cnt == 0).sum())
moves = []                       # (prime index, new class, single cost)
for i, (p, c) in enumerate(zip(mods, cls)):
    inc = (rows % p) == c; A = (cnt - inc) == 0; U = int((A & inc).sum()); b = np.bincount(rows[A] % p, minlength=p)
    for c2 in range(p):
        if c2 != c and U - b[c2] <= 5: moves.append((i, c2, int(U - b[c2])))
print('moves of cost <= 5:', len(moves), 'over', len(set(m[0] for m in moves)), 'primes')
def true_n(sel):
    cl = cls.copy()
    for i, c2, _ in sel: cl[i] = c2
    cn = np.zeros(len(rows), np.int32)
    for p, c in zip(mods, cl): cn[(rows % p) == c] += 1
    return int((cn == 0).sum())
for k in (2, 3, 4, 6, 8):
    diffs = []
    for _ in range(300):
        pick = rng.choice(len(moves), size=k, replace=False); sel = [moves[j] for j in pick]
        if len(set(m[0] for m in sel)) < k: continue
        pred = n0 + sum(m[2] for m in sel); diffs.append(true_n(sel) - pred)
    d = np.array(diffs); print('k = %d moves: true minus predicted alive rows: mean %+.2f, sd %.2f, min %d, max %d (n = %d sets)' % (k, d.mean(), d.std(), d.min(), d.max(), len(d)))
