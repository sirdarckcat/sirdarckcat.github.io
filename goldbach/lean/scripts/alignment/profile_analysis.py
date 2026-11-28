"""Where the best members of a real cover get their rows: by range of primes beyond the line (sieve_profile.c).
Members of the first cover of q200000_m89.txt (1,502 rows, 200 digits), sieved to 1e8.  A tier is the members with the
fewest rows left at 1e8.  For each range of primes: the mean number of rows newly struck, all members and tier; the
information of that count about the tier (Kullback-Leibler divergence of its distribution in the tier from its
distribution over all members, with the usual bias (bins - 1)/(2 members) removed); per prime of the range; and the
strikes and repeats.
  python profile_analysis.py NROWS FILE..."""
import math, sys
import numpy as np
EDGES = [463, 1e3, 3e3, 1e4, 3e4, 1e5, 2e5, 1e6, 1e7, 1e8]
def primes_count(lo, hi):
    n = int(hi); s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    c = np.cumsum(s); return int(c[int(hi)] - c[int(lo)])
nrows = int(sys.argv[1]); data = np.concatenate([np.fromfile(f, dtype=np.uint16).reshape(-1, 9, 2) for f in sys.argv[2:]])
g = data[:, :, 0].astype(np.int64); h = data[:, :, 1].astype(np.int64); m = len(g); S = nrows - g.sum(axis=1)
print(f"# {m:,d} members; rows left at 1e8: mean {S.mean():.2f}, variance {S.var(ddof=1):.2f}, least {int(S.min())}")
counts = [primes_count(EDGES[j], EDGES[j + 1]) for j in range(9)]
def kl(a, b):
    lo = int(min(a.min(), b.min())); hi = int(max(a.max(), b.max())) + 1
    pa = np.bincount(a - lo, minlength=hi - lo) / len(a); pb = np.bincount(b - lo, minlength=hi - lo) / len(b); ok = pa > 0
    return float(np.sum(pa[ok] * np.log(pa[ok] / np.maximum(pb[ok], 1e-300)))) - (int(ok.sum()) - 1) / (2 * len(a))
for frac in (0.01, 0.001):
    cut = np.sort(S)[int(frac * m)]; tier = S <= cut; nt = int(tier.sum()); rar = math.log(m / nt)
    print(f"\n# tier: rows left <= {int(cut)}: {nt:,d} members, rarity {rar:.2f} nats; mean rows left {S[tier].mean():.1f}")
    print("primes | number of primes | mean rows newly struck, all members | tier | excess | information, nats | per prime | cumulative share | tilt (excess / variance)")
    infos = [kl(g[tier, j], g[:, j]) for j in range(9)]; tot = sum(infos); cum = 0.0
    for j in range(9):
        cum += infos[j]; va = g[:, j].var()
        print(f"({EDGES[j]:.0e}, {EDGES[j + 1]:.0e}] | {counts[j]:,d} | {g[:, j].mean():.2f} | {g[tier, j].mean():.2f} | {g[tier, j].mean() - g[:, j].mean():+.2f} | {infos[j]:.3f} | {infos[j] / counts[j]:.2e} | {cum / tot:.2f} | {(g[tier, j].mean() - g[:, j].mean()) / va:.3f}")
    print(f"# sum of the informations of the nine ranges: {tot:.2f} nats (rarity {rar:.2f})")
    H = h.sum(axis=1).astype(np.float64); U = g.sum(axis=1).astype(np.float64); U0 = nrows * (1 - (1 - 1 / nrows) ** H)
    print(f"# strikes (repeats included): all {H.mean():.1f}, tier {H[tier].mean():.1f}; distinct rows struck: all {U.mean():.1f}, tier {U[tier].mean():.1f}; "
          f"repeats: all {(H - U).mean():.1f}, tier {(H - U)[tier].mean():.1f}; repeats if every strike fell on a random row: all {(H - U0).mean():.1f}, tier {(H - U0)[tier].mean():.1f}")
    adv = U[tier].mean() - U.mean(); more = U0[tier].mean() - U0.mean(); fewer = (U - U0)[tier].mean() - (U - U0).mean()
    print(f"# advantage of the tier in distinct rows {adv:.1f} = more strikes {more:.1f} + fewer repeats {fewer:.1f} (share of fewer repeats {fewer / adv:.2f})")

# Innovations: the rows struck in a range depend on how many were left before it.  e_j = g_j - a_j L_j, with L_j the
# rows left before the range and a_j the share struck on average (regression through the origin): the part of the gain
# that the past does not explain.  Its information about the tier (Gaussian: mean^2 / (2 variance)) adds over ranges.
print("\n# innovations of the ranges (gain minus the share of the rows left that a range strikes on average)")
Lb = nrows - np.concatenate([np.zeros((m, 1), dtype=np.int64), np.cumsum(g, axis=1)[:, :-1]], axis=1)
a = (g * Lb).sum(axis=0) / (Lb * Lb).sum(axis=0); e = g - a[None, :] * Lb
print("# correlation matrix of the innovations, largest off-diagonal entry in absolute value: %.3f" % np.abs(np.corrcoef(e.T) - np.eye(9)).max())
for frac in (0.01, 0.001):
    cut = np.sort(S)[int(frac * m)]; tier = S <= cut; rar = math.log(m / int(tier.sum()))
    print(f"\n# tier rows left <= {int(cut)} (rarity {rar:.2f} nats)")
    print("primes | share struck a_j | sd of the innovation | mean innovation in the tier | in sd | information mean^2/(2 var) | per prime | cumulative share")
    info = [(e[tier, j].mean() ** 2) / (2 * e[:, j].var()) for j in range(9)]; tot = sum(info); cum = 0.0
    for j in range(9):
        cum += info[j]
        print(f"({EDGES[j]:.0e}, {EDGES[j + 1]:.0e}] | {a[j]:.4f} | {e[:, j].std():.2f} | {e[tier, j].mean():+.2f} | {e[tier, j].mean() / e[:, j].std():+.2f} | {info[j]:.3f} | {info[j] / counts[j]:.2e} | {cum / tot:.2f}")
    print(f"# sum {tot:.2f} nats; (mean excess)^2 / (2 Var S) = {(S.mean() - S[tier].mean()) ** 2 / (2 * S.var()):.2f}; rarity {rar:.2f}")
