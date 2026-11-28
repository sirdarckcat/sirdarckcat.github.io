import numpy as np, sys, math
sys.path.insert(0, '.')
from lib import *
SMALL = [3, 5, 7, 11, 13, 17, 19, 23, 29]
def allowed(N):
    ok = (N % 2 == 0)
    for p in SMALL: ok &= (N % p != 0)
    return ok
def primes_below(n):
    s = np.ones(n, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
def inheritance_rank(Q, H):
    P = primes_below(Q); P = P[P > 2]; ps = set(P.tolist()); f = {}
    for h in range(2, H + 1, 2):
        f[h] = sum(1 for q in P if (q + h) in ps)
    return f   # number of inherited rows for shift h (neighbour N+h or N-h)
def run(nm, Q, X, H, topm=None, reps=400, seed=3):
    m = Mini(nm); S = np.asarray(m.N(m.succ)); k1 = np.asarray(m.k[m.succ, 0]).astype(np.int64)
    n_all = np.bincount(np.asarray(m.k[:, 0]).astype(np.int64), minlength=64)
    before = np.concatenate([[0], np.cumsum(n_all)[:-1]])
    f = inheritance_rank(Q, H)
    hs = sorted(f, key=lambda h: -f[h]) if topm else list(f)
    if topm: hs = hs[:topm]
    shifts = np.array([s * h for h in hs for s in (1, -1)])
    Sset = {int(x): i for i, x in enumerate(S)}
    nbr_cost = np.zeros(len(S), dtype=int); nbr_succ = [[] for _ in S]
    for i, N in enumerate(S):
        cand = N + shifts; ok = allowed(cand) & (cand > 0) & (cand < X)
        nbr_cost[i] = int(ok.sum())
        for c in cand[ok]:
            j = Sset.get(int(c))
            if j is not None: nbr_succ[i].append(j)
    pairs = sum(len(x) for x in nbr_succ) // 2
    rng = np.random.default_rng(seed); g_b = {t: [] for t in KS}; g_n = {t: [] for t in KS}
    for r in range(reps):
        pos = before[k1] + rng.random(len(S)) * n_all[k1]
        order = np.argsort(pos); found = np.zeros(len(S), bool); times_nb = []; times_b = []; paid = 0
        for i in order:
            if found[i]: continue
            found[i] = True; queue = [i]; times_b.append(pos[i])
            # baseline stream-only discovery time recorded above; with neighbours:
            while queue:
                a = queue.pop(); paid += nbr_cost[a]; times_nb.append(pos[i] + paid)
                for j in nbr_succ[a]:
                    if not found[j]: found[j] = True; queue.append(j)
        # baseline: stream-only times of ALL successes in order
        tb = np.sort(pos); tn = np.sort(np.array(times_nb))
        for t in KS:
            if t <= len(tn): g_n[t].append(math.log(tb[t - 1] / tn[t - 1]))
    out = {t: (float(np.mean(g_n[t])), float(np.std(g_n[t]))) for t in KS if g_n[t]}
    return dict(n_succ=len(S), pairs=pairs, mean_cost=float(nbr_cost.mean()), gain=out, hs=len(hs))
if __name__ == '__main__':
    cfg = {'A': (1000, 10**9), 'B': (1000, 2 * 10**9), 'C': (900, 10**9)}
    for nm, (Q, X) in cfg.items():
        for H, topm in ((Q, None), (2 * Q, None), (Q, 30), (Q, 10)):
            r = run(nm, Q, X, H, topm)
            print(nm, f'H={H} top={topm}', 'succ', r['n_succ'], 'success pairs found', r['pairs'], 'neighbours scanned/seed', round(r['mean_cost'], 1),
                  'gain', {t: (round(v[0], 3), round(v[1], 3)) for t, v in r['gain'].items()}, flush=True)
