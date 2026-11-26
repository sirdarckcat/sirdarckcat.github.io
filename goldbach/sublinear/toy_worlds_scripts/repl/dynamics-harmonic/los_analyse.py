#!/usr/bin/env python3
"""(c): neighbouring rows of real 200-digit members.  Data from los_collect.py (rows sieved to 10^6, all survivors
Fermat-tested).  Null for every pair statistic: the prime flags shuffled inside each member (keeps each member's count)."""
import sys, math, numpy as np, gmpy2
from common import setup
cov, rows, N0, M, K = setup(); n = len(rows)
d = np.load(sys.argv[1] if len(sys.argv) > 1 else "los_data_1.npz"); ks = d["k"]; ptr = d["ptr"]; ridx = d["rowidx"]; fl = d["isprime"]; nm = len(ks)
S6 = np.fromfile("S_1000000.u16", dtype=np.uint16); cnt = np.diff(ptr)
print(f"members {nm}, tests {len(fl)}, primes {int(fl.sum())}; survivors per member agree with the C sieve at depth 1e6 for every member: {bool((S6[ks] == cnt).all())}")
# expected rate: 1 / (ln N * prod_{p<=1e6}(1-1/p))
sv = np.ones(10 ** 6 + 1, bool); sv[:2] = False
for i in range(2, 1001):
    if sv[i]: sv[i * i::i] = False
P6 = np.nonzero(sv)[0]; lp = float(np.sum(np.log1p(-1.0 / P6)))
lnN = np.array([float(gmpy2.log(gmpy2.mpz(N0) + int(k) * gmpy2.mpz(M))) for k in ks]); pm = 1 / (lnN * math.exp(lp)); exp = float((pm * cnt).sum())
print(f"primes found / expected (1/(ln N prod(1-1/p))): {fl.sum()/exp:.4f} +- {1/math.sqrt(fl.sum()):.4f}")
pc = np.add.reduceat(fl.astype(np.int64), ptr[:-1]); vb = float((cnt * pm * (1 - pm)).sum()); print(f"dispersion of primes per member / binomial: {((pc - cnt*pm)**2).sum()/vb:.4f} +- {math.sqrt(2/nm):.4f}")
memb = np.repeat(np.arange(nm), cnt); q = rows[ridx].astype(np.int64)
def pairstats(flags, maxlag=10):
    out = []
    for l in range(1, maxlag + 1):
        same = memb[l:] == memb[:-l]; out.append(int((flags[l:] & flags[:-l] & same).sum()))
    return np.array(out)
def distbins(flags):
    out = []
    for lo, hi in ((0, 100), (100, 300), (300, 1000), (1000, 3000)):
        tot = 0
        for l in range(1, 40):
            same = (memb[l:] == memb[:-l]); dq = q[l:] - q[:-l]; sel = same & (dq >= lo) & (dq < hi)
            if not sel.any(): continue
            tot += int((flags[l:] & flags[:-l] & sel).sum())
        out.append(tot)
    return np.array(out)
def resid_tables(flags, mods=(4, 5, 7, 8, 11, 13)):
    """consecutive successes inside a member: table of (q mod m, q' mod m)"""
    idx = np.nonzero(flags)[0]; a = idx[:-1]; b = idx[1:]; ok = memb[a] == memb[b]; a = a[ok]; b = b[ok]
    return {m: np.bincount((q[a] % m) * m + q[b] % m, minlength=m * m) for m in mods}, len(a)
rng = np.random.default_rng(11)
def shuffled():
    # permute flags inside each member: random keys, argsort within member blocks
    key = rng.random(len(fl)); o = np.lexsort((key, memb)); return fl[o]
obs_l = pairstats(fl); obs_d = distbins(fl); obs_t, npair = resid_tables(fl)
NP = 200; pl = np.zeros((NP, len(obs_l))); pd = np.zeros((NP, len(obs_d))); pt = {m: np.zeros((NP, m * m)) for m in obs_t}
for i in range(NP):
    f2 = shuffled(); pl[i] = pairstats(f2)
    if i < 60: pd[i] = distbins(f2)
    t, _ = resid_tables(f2)
    for m in t: pt[m][i] = t[m]
print("both prime, rows l apart among a member's survivors: lag | observed | null mean | ratio | z")
for l in range(len(obs_l)): print(f"  {l+1} | {obs_l[l]} | {pl[:, l].mean():.1f} | {obs_l[l]/pl[:, l].mean():.4f} | {(obs_l[l]-pl[:, l].mean())/pl[:, l].std():+.2f}")
tot = obs_l.sum(); tp = pl.sum(axis=1); print(f"  lags 1..10 pooled | {tot} | {tp.mean():.1f} | {tot/tp.mean():.4f} +- {tp.std()/tp.mean():.4f} | {(tot-tp.mean())/tp.std():+.2f}")
print("both prime, by distance q' - q: range | observed | null mean | ratio | z")
for i, (lo, hi) in enumerate(((0, 100), (100, 300), (300, 1000), (1000, 3000))): print(f"  [{lo},{hi}) | {obs_d[i]} | {pd[:60, i].mean():.1f} | {obs_d[i]/pd[:60, i].mean():.4f} | {(obs_d[i]-pd[:60, i].mean())/pd[:60, i].std():+.2f}")
print(f"consecutive successes of a member ({npair} pairs): residues (q mod m, q' mod m) against the shuffled null: m | chi2 over cells | null chi2 mean, 95% | share of pairs with q = q' mod m: observed, null, z")
for m in obs_t:
    mean = pt[m].mean(axis=0); sdv = pt[m].std(axis=0); ok = mean > 5
    chi = float((((obs_t[m] - mean) ** 2 / np.maximum(sdv, 1e-9) ** 2)[ok]).sum()); chin = (((pt[m] - mean) ** 2 / np.maximum(sdv, 1e-9) ** 2)[:, ok]).sum(axis=1)
    diag = np.arange(m) * (m + 1); od = obs_t[m][diag].sum(); nd = pt[m][:, diag].sum(axis=1)
    print(f"  {m} | {chi:.1f} ({int(ok.sum())} cells) | {chin.mean():.1f}, {np.quantile(chin, 0.95):.1f} | {od/npair:.4f}, {nd.mean()/npair:.4f}, {(od-nd.mean())/nd.std():+.2f}")
# quadratic characters of the row integers (Siegel / Chebyshev type bias): rate among chi=+1 against chi=-1
def legendre_table(D):
    t = -np.ones(D, dtype=np.int8); t[(np.arange(D, dtype=np.int64) ** 2) % D] = 1; t[0] = 0; return t
Ds = [int(p) for p in P6 if 467 <= p < 5000]; zs = []; best = None
for D in Ds:
    c = (N0 % D + ks.astype(np.int64) * (M % D)) % D; chi = legendre_table(D)[(c[memb] - q) % D]
    a = fl[chi == 1]; b = fl[chi == -1]; p0 = fl.mean(); zv = (a.mean() - b.mean()) / math.sqrt(p0 * (1 - p0) * (1 / len(a) + 1 / len(b))); zs.append(zv)
    if best is None or abs(zv) > abs(best[1]): best = (D, zv, a.mean() / b.mean())
zs = np.array(zs); print(f"Legendre symbol ((N-q)/D) for the {len(Ds)} primes D in [467,5000): prime rate at +1 against -1: mean z^2 {np.mean(zs**2):.3f}, largest |z| {np.abs(zs).max():.2f} at D={best[0]} (rate ratio {best[2]:.4f}); expected largest for noise {math.sqrt(2*math.log(len(Ds))):.2f}")
print(f"  so for each of these D a split (1-delta):(1+delta) of the prime rate is bounded by |delta| < {3/math.sqrt(fl.sum()):.4f} (3 sd)")
