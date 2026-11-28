import numpy as np, math, time, sys
sys.path.insert(0, '.')
from ev import Mini
KS = (1, 3, 10, 30, 100)
CH = 20_000_000

def keyed_counts(m, keyfun, nkeys):
    """keyfun(a, b) -> int keys for members [a,b); returns (member counts per key, success counts per key, success key array)."""
    counts = np.zeros(nkeys, dtype=np.int64); sk = []
    for a in range(0, m.M, CH):
        b = min(a + CH, m.M); key = keyfun(a, b)
        counts += np.bincount(key, minlength=nkeys)
        sm = np.asarray(m.s[a:b]) == 1
        if sm.any(): sk.append(key[sm])
    sk = np.concatenate(sk); return counts, np.bincount(sk, minlength=nkeys), sk

def group(counts, sc, sigma):
    """merge keys with equal sigma; return group-sorted (n, s) arrays"""
    u, inv = np.unique(sigma, return_inverse=True)
    scg = np.bincount(inv, weights=sc); return np.bincount(inv, weights=counts).astype(np.int64), (scg if np.issubdtype(np.asarray(sc).dtype, np.floating) else scg.astype(np.int64))

def cost_levels(n, s, targets=KS):
    """interpolated expected position of the t-th success (toy_compare convention); n, s are per-level in scanning order"""
    cn = np.cumsum(n); cs = np.cumsum(s); out = {}
    for t in targets:
        if cs[-1] < t: out[t] = np.nan; continue
        g = int(np.searchsorted(cs, t, side='left')); pn = cn[g - 1] if g else 0; ps = cs[g - 1] if g else 0
        out[t] = pn + (cn[g] - pn) * (t - ps) / (cs[g] - ps)
    return out

def cost_from(counts, sc, sigma, targets=KS):
    n, s = group(counts, sc, sigma); return cost_levels(n, s, targets)

def gain_boot(counts, sc, skeys, sig_base, sig_mech, B=300, seed=7, targets=KS):
    """point gain ln(E_base/E_mech) on the observed successes, and bootstrap mean/std over resampled success sets (paired)."""
    pb = cost_from(counts, sc, sig_base, targets); pm = cost_from(counts, sc, sig_mech, targets)
    pt = {t: math.log(pb[t] / pm[t]) for t in targets}
    rng = np.random.default_rng(seed); n = len(skeys); K = len(counts); bs = {t: [] for t in targets}
    for _ in range(B):
        scb = np.bincount(skeys[rng.integers(0, n, n)], minlength=K)
        eb = cost_from(counts, scb, sig_base, targets); em = cost_from(counts, scb, sig_mech, targets)
        for t in targets:
            if not (math.isnan(eb[t]) or math.isnan(em[t])): bs[t].append(math.log(eb[t] / em[t]))
    return pt, {t: (float(np.mean(bs[t])), float(np.std(bs[t]))) for t in targets}, pb, pm

def fit_logit(X, n, s, iters=80, ridge=1e-6):
    beta = np.zeros(X.shape[1]); beta[0] = math.log(max(s.sum(), 1) / n.sum())
    for _ in range(iters):
        eta = np.clip(X @ beta, -50, 50); p = 1 / (1 + np.exp(-eta)); W = n * p * (1 - p)
        g = X.T @ (s - n * p) - ridge * beta; H = (X * W[:, None]).T @ X + ridge * np.eye(X.shape[1])
        step = np.linalg.solve(H, g); beta += step
        if np.max(np.abs(step)) < 1e-10: break
    return beta

def fmt(pt, bs, targets=KS):
    return '  '.join(f'k={t}: {pt[t]:+.2f} (boot {bs[t][0]:+.2f}±{bs[t][1]:.2f})' for t in targets)
