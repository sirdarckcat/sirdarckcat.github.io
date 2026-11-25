"""Question 2, last part: do the best members of the miniature share anything?
For the tier k2 <= TIER: (1) the classes modulo the cover primes: the most frequent class and its share; (2) pairs of
tier members: the number of primes at which the two share a class, cover primes and later primes separately, against
what the one-prime distributions predict and against uniform; (3) the classes modulo 29 and 31 as points of the 29 x 31
grid: chi-square against the product of the two marginals; (4) which rows are still left at depth 200: how often each
row is left in the tier, against all members; (5) differences between tier members: the smallest ones.
  python optima.py TIER"""
import math, os, sys
import numpy as np
D = os.environ.get("PPRIME_DATA", "../pprime_families/data")
N = np.memmap(f"{D}/N.u32", dtype=np.uint32, mode="r"); k1 = np.asarray(np.memmap(f"{D}/k1.u8", dtype=np.uint8, mode="r")); k2 = np.asarray(np.memmap(f"{D}/k2.u8", dtype=np.uint8, mode="r"))
TIER = int(sys.argv[1]) if len(sys.argv) > 1 else 10
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
ROWS = [p for p in primes_upto(999) if p > 2]; SP = [p for p in primes_upto(199) if p > 2]; COVER = [p for p in SP if p <= 23]; DEEP = [p for p in SP if p > 23]
idx = np.nonzero(k2 <= TIER)[0]; nt = np.asarray(N[idx]).astype(np.int64); T = len(nt)
print(f"# tier k2 <= {TIER}: {T:,d} members")
print("# (1) classes modulo the cover primes: most frequent class, its share in the tier (1/(r-1) if uniform)")
for r in COVER + [29]:
    c = np.bincount(nt % r, minlength=r); a = int(c.argmax()); w = sum(1 for q in ROWS if q % r == a)
    print(f"  {r}: class {a} holds {c[a] / T:.3f} of the tier (uniform {1 / (r - 1):.3f}); that class strikes {w} rows, the best class of {r} strikes {max(sum(1 for q in ROWS if q % r == b) for b in range(1, r))}")
# (2) shared classes among pairs
def shared(primes):
    obs = 0.0; pred = 0.0; uni = 0.0
    for r in primes:
        c = np.bincount(nt % r, minlength=r).astype(np.float64); obs += float((c * (c - 1)).sum()) / (T * (T - 1)); p = c / T; pred += float((p * p).sum()); uni += 1.0 / (r - 1 if r <= 29 else r)
    return obs, pred, uni
o, p, u = shared(COVER); print(f"# (2) pairs of tier members: primes at which the two share a class. Cover primes 3..23: {o:.3f} per pair (uniform classes would give {u:.3f})")
o, p, u = shared(DEEP); print(f"#     later primes 29..199: {o:.4f} per pair (uniform {u:.4f})")
# exact count of pairs by number of shared later primes, against the Poisson-binomial of the marginals
cnt = np.zeros(40); R = np.stack([nt % r for r in DEEP], axis=1)
for i in range(T):
    s = (R[i + 1:] == R[i]).sum(axis=1); cnt += np.bincount(s, minlength=40)[:40]
tot = cnt.sum()
pr = [float(((np.bincount(nt % r, minlength=r) / T) ** 2).sum()) for r in DEEP]
dist = np.zeros(40); dist[0] = 1.0
for q in pr:
    dist[1:] = dist[1:] * (1 - q) + dist[:-1] * q; dist[0] *= (1 - q)
print("#     pairs by the number of later primes with a common class: observed share (independent primes with the tier's own class frequencies)")
print("     " + "  ".join(f"{j}: {cnt[j] / tot:.5f} ({dist[j]:.5f})" for j in range(6)))
# (3) the grid 29 x 31
a = nt % 29; b = nt % 31; tab = np.zeros((29, 31)); np.add.at(tab, (a, b), 1.0)
ex = np.outer(tab.sum(axis=1), tab.sum(axis=0)) / T; m = ex > 0
chi = float((((tab - ex) ** 2)[m] / ex[m]).sum()); dof = (28 - 1) * (31 - 1)
print(f"# (3) classes modulo 29 and 31 as points of the grid: chi-square against the product of the marginals {chi:.0f} on {dof} degrees of freedom (z = {(chi - dof) / math.sqrt(2 * dof):+.2f}); fullest point holds {int(tab.max())} members, mean {T / (28 * 31):.2f}")
# (4) rows left
MASK = {}
for s in SP:
    mk = np.zeros((s, 3), dtype=np.uint64)
    for j, q in enumerate(ROWS): mk[q % s, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    MASK[s] = mk
def leftmask(nn):
    left = np.zeros((len(nn), 3), dtype=np.uint64)
    for j in range(len(ROWS)): left[:, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    for s in SP: left &= ~MASK[s][nn % s]
    return left
def rowfreq(nn):
    L = leftmask(nn); return np.array([float(((L[:, j >> 6] >> np.uint64(j & 63)) & np.uint64(1)).mean()) for j in range(len(ROWS))])
rng = np.random.default_rng(8); ctrl = np.sort(rng.choice(len(k1), 400000, replace=False)); fa = rowfreq(np.asarray(N[ctrl]).astype(np.int64)); ft = rowfreq(nt)
print(f"# (4) rows still left at depth 200: a row is left in {ft.mean():.4f} of the tier members on average ({fa.mean():.4f} for all members)")
order = np.argsort(-ft)[:12]
print("#     rows most often left in the tier: " + ", ".join(f"{ROWS[j]} ({ft[j]:.3f}; all members {fa[j]:.3f})" for j in order))
small = [j for j, q in enumerate(ROWS) if q <= 199]; big = [j for j, q in enumerate(ROWS) if q > 199]
print(f"#     rows that are themselves moduli (3..199): left in {ft[small].mean():.4f} of the tier on average ({fa[small].mean():.4f} for all); rows above 199: {ft[big].mean():.4f} ({fa[big].mean():.4f})")
print(f"#     correlation between the two frequency profiles over the 167 rows: {np.corrcoef(ft, fa)[0, 1]:.3f}; ratio tier / all: {np.min(ft / fa):.3f} to {np.max(ft / fa):.3f}")
# (5) differences
s = np.sort(nt); d = np.diff(s); j = np.argsort(d)[:8]
print("# (5) closest pairs of tier members: " + ", ".join(f"{int(s[i])} and {int(s[i + 1])} (difference {int(d[i])})" for i in j))
print(f"#     expected number of pairs closer than 100,000 for {T} uniform points below 1e9: {T * (T - 1) / 2 * 2 * 1e5 / 1e9:.1f}; observed {int((d < 1e5).sum())} among neighbours")
