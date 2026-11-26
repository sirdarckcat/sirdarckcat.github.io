import numpy as np, math, time, sys
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rows = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]
idx = {}
for p in mods:
    r = rows % p; order = np.argsort(r, kind='stable'); cnts = np.bincount(r, minlength=p); starts = np.concatenate([[0], np.cumsum(cnts)])
    idx[p] = [order[starts[c]:starts[c + 1]] for c in range(p)]
import os
cls = {p: int(c) for p, c in zip(mods, np.load(sys.argv[5] if len(sys.argv) > 5 else 'cls.npy'))}
cnt = np.zeros(len(rows), np.int32)
for p in mods: cnt[idx[p][cls[p]]] += 1
E = int((cnt == 0).sum()); best = E; bestcls = dict(cls); print('start alive', E, flush=True)
T0, T1 = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0, float(sys.argv[4]) if len(sys.argv) > 4 else 0.15; steps = int(sys.argv[3]) if len(sys.argv) > 3 else 600000; t0 = time.time()
for it in range(steps):
    T = T0 * (T1 / T0) ** (it / steps); p = mods[rng.integers(len(mods))]; c = cls[p]
    c2 = int(rng.integers(p))
    if c2 == c: continue
    a = idx[p][c]; b = idx[p][c2]
    gain = int((cnt[a] == 1).sum()); loss = int((cnt[b] == 0).sum()); d = gain - loss            # change in the number of alive rows
    if d <= 0 or rng.random() < math.exp(-d / T):
        cnt[a] -= 1; cnt[b] += 1; cls[p] = c2; E += d
        if E < best: best = E; bestcls = dict(cls)
    if it % 100000 == 0: print(it, 'T=%.2f' % T, 'E', E, 'best', best, round(time.time() - t0), 's', flush=True)
print('final best alive rows', best)
np.save('cls_sa_%s.npy' % (sys.argv[1] if len(sys.argv) > 1 else '1'), np.array([bestcls[p] for p in mods]))
