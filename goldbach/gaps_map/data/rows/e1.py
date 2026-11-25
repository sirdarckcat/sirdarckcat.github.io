import numpy as np, math, time
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rows = P[P > 2].astype(np.int64); isp = np.zeros(Q + 5, bool); isp[P] = True
mods_all = [int(p) for p in primes_upto(463) if p > 2]
# forced-row count F(c) for N = a^2 + c : rows q = c + b^2 (b >= 0)
t0 = time.time(); best = []
b = np.arange(0, 448, dtype=np.int64); b2 = b * b
Fc = np.zeros(2 * Q - 1, dtype=np.int32)
for c in range(-(Q - 1), Q):
    q = c + b2; m = (q >= 3) & (q < Q); Fc[c + Q - 1] = int(isp[q[m]].sum())
print('F(c): computed in %.0fs; max %d at c=%d ; mean %.1f ; 99.9th pct %.0f' % (time.time() - t0, Fc.max(), int(Fc.argmax()) - (Q - 1), Fc.mean(), np.percentile(Fc, 99.9)))
top = np.argsort(-Fc)[:8] - (Q - 1); print('best c:', [(int(c), int(Fc[c + Q - 1])) for c in top])
def run_cover(c, mods, restrict, rows):
    """greedy then coordinate descent over the pinned moduli; classes restricted to c + squares if restrict; returns (alive generic rows after pinned primes, alive forced rows)."""
    forced = np.zeros(len(rows), bool)
    if restrict:
        d = rows - c; sq = np.sqrt(np.maximum(d, 0)).round().astype(np.int64); forced = (d >= 0) & (sq * sq == d)
    cnt = np.zeros(len(rows), np.int32); cls = {}; allowed = {}
    for p in mods:
        if restrict: allowed[p] = np.unique((c + np.arange(p) ** 2) % p)
        else: allowed[p] = np.arange(p)
    def best_class(p, alive_mask):
        bc = np.bincount(rows[alive_mask & ~forced] % p, minlength=p); al = allowed[p]; return int(al[bc[al].argmax()]), int(bc[al].max())
    for p in mods:
        alive = cnt == 0; c_, _ = best_class(p, alive); cls[p] = c_; cnt[(rows % p) == c_] += 1
    for ps in range(6):
        imp = 0
        for p in mods:
            cnt[(rows % p) == cls[p]] -= 1; alive = cnt == 0; c_, v = best_class(p, alive)
            old = int(np.bincount(rows[alive & ~forced] % p, minlength=p)[cls[p]])
            if v > old: imp += v - old
            cls[p] = c_; cnt[(rows % p) == c_] += 1
        if imp == 0: break
    alive = cnt == 0
    return int((alive & ~forced).sum()), int((alive & forced).sum()), int(forced.sum())
tail = lambda P0: float(np.prod([1 - 1 / p for p in mods_all if p > P0]))
P0 = 229; pinned = [p for p in mods_all if p <= P0]; print('pinned primes up to', P0, ':', len(pinned), '; unpinned', len(mods_all) - len(pinned), '; tail product %.4f' % tail(P0))
g89, f89, _ = run_cover(0, mods_all, False, rows); print('unrestricted, 89 pinned: alive', g89)
g49, f49, _ = run_cover(0, pinned, False, rows); r49 = g49 * tail(P0); print('unrestricted, 49 pinned + 40 random: alive %d -> %.0f after the unpinned primes' % (g49, r49))
for c in [int(x) for x in top[:4]] + [0, 1000, -1000]:
    Fcc = int(Fc[c + Q - 1]); g, f, nf = run_cover(c, pinned, True, rows); r = g * tail(P0)
    print('c=%7d forced rows %3d : restricted 49 pinned -> alive at risk %.0f (forced alive after pinned: %d) ; net rows vs 89 pinned: %+.0f  = %+.2f nats' % (c, nf, r, f, g89 - r, (g89 - r) * 0.02428))
