"""Question 1: where the best members of the miniature sit.  Part A: how much of their rarity is the cover.

Miniature: X = 1e9, Q = 1000 (167 rows), line 23, depth 200; members = even N in [1202, 1e9) with no prime factor
3..29.  k1 = rows left at depth 23 (a function of the class vector modulo 3..23), k2 = rows left at depth 200.
For each tier "k2 <= t":
  total rarity  ln(members / tier size);
  cover nats    KL(distribution of k1 inside the tier || distribution of k1 over all members): the part of the rarity
                that sits in the rows left by the cover;
  luck nats     the rest;
  where the tier sits in the cover-first order (quantile of k1), and how the windows of its members look (the other
  members of the same class vector modulo M0 = 2*3*...*23)."""
import math, os, sys
import numpy as np
D = os.environ.get("PPRIME_DATA", "../pprime_families/data")
N = np.memmap(f"{D}/N.u32", dtype=np.uint32, mode="r"); k1 = np.asarray(np.memmap(f"{D}/k1.u8", dtype=np.uint8, mode="r")); k2 = np.asarray(np.memmap(f"{D}/k2.u8", dtype=np.uint8, mode="r"))
su = np.asarray(np.memmap(f"{D}/succ.u8", dtype=np.uint8, mode="r")); M0 = 223092870; n = len(k1)
h_all = np.bincount(k1, minlength=64).astype(np.float64); cum = np.cumsum(h_all)
print(f"# members {n:,d}; rows left at depth 23: min {int(k1.min())}, mean {k1.mean():.2f}, sd {k1.std():.2f}; at depth 200: min {int(k2.min())}, mean {k2.mean():.2f}, sd {k2.std():.2f}")
print(f"# class vectors modulo 3..23: 36,495,360; members per class vector {n / 36495360:.2f}")
# conditional law of k2 given k1 (for the luck quantile)
joint = np.zeros((64, 64)); np.add.at(joint, (k1, k2), 1.0)
print("tier | members | total rarity, nats | cover nats | luck nats | k1 in the tier: min / 10% / median / 90% / max / mean | cover-first quantile of the median member | share of the tier inside the best 1% / 0.1% / 0.01% of the cover-first order | tier members with 22 rows left at depth 23, the least there is (14 members in all) | with at most 24 (888 in all)")
q1 = int(np.searchsorted(cum, 0.01 * n)); q01 = int(np.searchsorted(cum, 0.001 * n)); q001 = int(np.searchsorted(cum, 0.0001 * n))
tiers = {}
for t in (7, 8, 9, 10, 11, 12, 13, 14):
    idx = np.nonzero(k2 <= t)[0]; tiers[t] = idx; kk = k1[idx]; h = np.bincount(kk, minlength=64).astype(np.float64); p = h / h.sum(); pa = h_all / n
    cover = float(np.sum(np.where(p > 0, p * np.log(np.where(p > 0, p, 1) / np.where(pa > 0, pa, 1)), 0.0))); total = math.log(n / len(idx))
    med = int(np.median(kk)); quant = (cum[med - 1] + 0.5 * h_all[med]) / n
    # share inside cover-first quantiles: members of the tier with k1 below the cut level count fully, at the cut level proportionally
    def share(frac):
        target = frac * n; lev = int(np.searchsorted(cum, target)); below = cum[lev - 1] if lev > 0 else 0.0
        part = (target - below) / h_all[lev]; return (h[:lev].sum() + part * h[lev]) / h.sum()
    print(f"k2 <= {t} | {len(idx):,d} | {total:.2f} | {cover:.2f} | {total - cover:.2f} | {int(kk.min())} / {int(np.percentile(kk, 10))} / {med} / {int(np.percentile(kk, 90))} / {int(kk.max())} / {kk.mean():.2f} | "
          f"{quant:.4%} | {share(0.01):.3f} / {share(0.001):.3f} / {share(0.0001):.3f} | {int((kk == 22).sum())} | {int((kk <= 24).sum())}", flush=True)
# the same from the other side: what the cover-first prefix holds of each tier, and the luck quantile of tier members
print("\n# luck inside a cover level: for a member with k1 = c, the share of all members with that k1 having k2 at most its own")
print("tier | median over the tier of -ln(P(k2 <= own | k1)) | mean | the same for the cover: -ln(cover-first quantile), median | mean")
cj = np.cumsum(joint, axis=1)
for t, idx in tiers.items():
    kk1 = k1[idx].astype(int); kk2 = k2[idx].astype(int)
    luck = -np.log(cj[kk1, kk2] / h_all[kk1]); cov = -np.log((cum[kk1 - 1] + 0.5 * h_all[kk1]) / n)
    print(f"k2 <= {t} | {np.median(luck):.2f} | {luck.mean():.2f} | {np.median(cov):.2f} | {cov.mean():.2f}")
# windows: the other members of the same class vector
print("\n# windows (members with the same class vector modulo M0): how the siblings of tier members fare")
print("tier | members | mean window size | tier members that are the best of their window | mean k2 of the siblings | mean of E[k2 | k1] over the tier (what a sibling is expected to have) | siblings also in the tier")
Ek2 = (joint * np.arange(64)[None, :]).sum(axis=1) / np.maximum(h_all, 1)
Nall = np.asarray(N)
for t in (8, 9, 10, 11, 12):
    idx = tiers[t]; nn = Nall[idx].astype(np.int64); sizes = []; best = 0; sib_k2 = []; sib_in = 0
    for i, x in zip(idx, nn):
        r = x % M0; cand = r + M0 * np.arange(5); cand = cand[(cand < 10**9) & (cand != x)]
        j = np.searchsorted(Nall, cand.astype(np.uint32)); ok = (j < n) & (Nall[np.minimum(j, n - 1)] == cand); j = j[ok]
        sizes.append(len(j) + 1); s2 = k2[j]
        best += int(len(j) == 0 or k2[i] <= s2.min()); sib_k2.extend(s2.tolist()); sib_in += int((s2 <= t).sum())
    print(f"k2 <= {t} | {len(idx):,d} | {np.mean(sizes):.2f} | {best:,d} | {np.mean(sib_k2):.2f} | {Ek2[k1[idx]].mean():.2f} | {sib_in}", flush=True)
