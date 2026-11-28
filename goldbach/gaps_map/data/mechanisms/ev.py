import numpy as np, math
DEPTHS = [23, 31, 43, 61, 97, 199]
class Mini:
    def __init__(self, prefix, nd=6):
        self.idx = np.memmap(prefix + '.idx.u32', dtype=np.uint32, mode='r')
        self.k = np.memmap(prefix + '.k.u8', dtype=np.uint8, mode='r').reshape(-1, nd)
        self.s = np.memmap(prefix + '.s.u8', dtype=np.uint8, mode='r')
        self.M = len(self.s); self.succ = np.flatnonzero(self.s)
    def N(self, ix): return self.idx[ix].astype(np.int64) * 2

def cost_interp(key, s, order_sigma=None, targets=(1, 3, 10, 30, 100, 256)):
    """toy_compare.py's convention: levels sorted by sigma; E(t) = pn + (n - pn)*(t - ps)/(s - ps) inside the level where cumulative successes reach t."""
    K = int(key.max()) + 1
    counts = np.bincount(key, minlength=K).astype(np.int64); sc = np.bincount(key[s == 1], minlength=K).astype(np.int64)
    sigma = np.arange(K) if order_sigma is None else order_sigma
    o = np.argsort(sigma, kind='stable'); o = o[counts[o] > 0]
    cn = np.cumsum(counts[o]); cs = np.cumsum(sc[o]); out = {}
    for t in targets:
        t = min(t, int(cs[-1]))
        g = int(np.searchsorted(cs, t, side='left')); pn = cn[g - 1] if g else 0; ps = cs[g - 1] if g else 0
        out[t] = pn + (cn[g] - pn) * (t - ps) / (cs[g] - ps)
    return out

def positions_mc(key, s, sigma, reps=400, seed=1):
    """For the successes: expected-position model with uniform random tie-breaking inside equal-sigma groups.
    Returns array (reps, nsucc) of sorted success positions (1-based)."""
    K = int(key.max()) + 1
    counts = np.bincount(key, minlength=K).astype(np.int64)
    o = np.argsort(sigma, kind='stable'); rank_of_key = np.empty(K, dtype=np.int64); rank_of_key[o] = np.arange(K)
    cn = np.cumsum(counts[o]); before = np.concatenate([[0], cn[:-1]]); before_by_key = np.empty(K, dtype=np.int64); before_by_key[o] = before
    # groups of EQUAL sigma are tie groups: merge keys with equal sigma
    sig_sorted = sigma[o]; tie_start = np.concatenate([[True], sig_sorted[1:] != sig_sorted[:-1]])
    gid = np.cumsum(tie_start) - 1; gsize = np.bincount(gid, weights=counts[o]).astype(np.int64)
    gbefore = np.concatenate([[0], np.cumsum(gsize)[:-1]])
    g_of_key = np.empty(K, dtype=np.int64); g_of_key[o] = gid
    ks = key[s == 1]; gs = g_of_key[ks]
    less = gbefore[gs]; eq = gsize[gs]
    rng = np.random.default_rng(seed)
    pos = less[None, :] + rng.random((reps, len(ks))) * eq[None, :] + 0.5
    pos.sort(axis=1)
    return pos

def Ek(pos, ks=(1, 3, 10, 30, 100)):
    return {k: float(np.exp(np.mean(np.log(pos[:, k - 1])))) for k in ks}   # geometric mean over tie-breaking draws
