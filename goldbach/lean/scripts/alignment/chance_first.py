"""Chance first against cover first in a miniature.

In the inspection game (what depends on the cover is free, the later classes of a member are hidden) the best order
for finding a member with at most t rows left is the decreasing order of the chance P_c that a member of the cover c
is one, computed from the cover alone.  Cover first orders by the number of rows the cover leaves, which is the mean
of the later count; the chance also depends on its spread.  Here: for a cover with left rows R,
   mean_c = sum over R of w_q,       var_c = sum over R of w_q (1 - w_q) + sum over pairs of R of (P(both left) - w_q w_q'),
both exact for uniform later classes (a quadratic form in the indicator of R), and the score
   (t + 1/2 - mean_c) / sd_c         (the two-moment form of the chance).
Compared on the true members: what share of all members must be examined, in each order, to collect a given share of
the tier (the members with at most t rows left at full depth).
  python chance_first.py Q LINE ZMEM DEPTH X TIER CONTROLS FILE.top ..."""
import math, sys
import numpy as np
Q, LINE, ZMEM, DEPTH, X, TIER, NCTL = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(float(sys.argv[5])), int(sys.argv[6]), int(sys.argv[7])
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
ROWS = np.array([p for p in primes_upto(Q - 1) if p > 2]); SP = [p for p in primes_upto(DEPTH) if p > 2]
COVER = [p for p in SP if p <= LINE]; LATER = [p for p in SP if p > LINE]; n = len(ROWS)
w = np.ones(n); both = np.ones((n, n))
for s in LATER:
    res = ROWS % s
    pi = np.where(res != 0, 1.0 / (s - 1), 0.0) if s <= ZMEM else np.full(n, 1.0 / s)
    w *= 1 - pi; same = res[:, None] == res[None, :]
    both *= 1 - pi[:, None] - pi[None, :] + np.where(same, pi[:, None], 0.0)
A = both - w[:, None] * w[None, :]; np.fill_diagonal(A, w * (1 - w))
def left_sets(N):
    x = np.ones((len(N), n), dtype=bool)
    for s in COVER: x &= (ROWS % s)[None, :] != (N % s)[:, None]
    return x
def scores(N):
    x = left_sets(N).astype(np.float64); k1 = x.sum(axis=1); mean = x @ w; var = np.einsum("ij,ij->i", x @ A, x)
    return k1, mean, var, (TIER + 0.5 - mean) / np.sqrt(var)
tier = []
for f in sys.argv[8:]:
    for line in open(f):
        a = line.split()
        if int(a[2]) <= TIER: tier.append(int(a[0]))
tier = np.array(sorted(tier), dtype=np.int64)
rng = np.random.default_rng(7); ctl = []
while sum(len(c) for c in ctl) < NCTL:
    N = 2 * rng.integers((Q + DEPTH + 2) // 2, X // 2, size=NCTL, dtype=np.int64); ok = np.ones(len(N), dtype=bool)
    for s in SP:
        if s <= ZMEM: ok &= N % s != 0
    ctl.append(N[ok])
ctl = np.concatenate(ctl)[:NCTL]
k1c, mc, vc, sc = scores(ctl); k1t, mt, vt, st = scores(tier)
print(f"# Q = {Q}, line {LINE}, depth {DEPTH}, X = {X:.0e}; tier: at most {TIER} rows left, {len(tier):,d} members; controls: {len(ctl):,d} random members")
print(f"# controls: rows left by the cover {k1c.mean():.2f} +- {k1c.std():.2f}; mean of the later count given the cover {mc.mean():.2f} +- {mc.std():.2f}; its sd given the cover {np.sqrt(vc).mean():.3f} +- {np.sqrt(vc).std():.3f}")
print(f"# at a fixed number of rows left by the cover, the sd of the later count varies by {np.mean([np.sqrt(vc[k1c == k]).std() for k in np.unique(k1c) if (k1c == k).sum() > 1000]):.3f} from cover to cover")
print(f"# tier:     rows left by the cover {k1t.mean():.2f} +- {k1t.std():.2f}; mean given the cover {mt.mean():.2f}; sd given the cover {np.sqrt(vt).mean():.3f}")
def quantile(ctl_key, tier_key):                 # share of the controls examined before the member; ties are examined in random order
    srt = np.sort(ctl_key); lo = np.searchsorted(srt, tier_key, side="left"); hi = np.searchsorted(srt, tier_key, side="right")
    return (lo + rng.random(len(tier_key)) * (hi - lo) + 0.5) / (len(srt) + 1)
ua = quantile(k1c + 0.0, k1t + 0.0); ub = quantile(-sc, -st); um = quantile(mc, mt); qa, qb, qm = np.sort(ua), np.sort(ub), np.sort(um)
print("share of the tier collected | share of the members examined: cover first | by the mean alone | chance first (mean and spread) | gain of chance first over cover first, nats")
for f in (0.1, 0.25, 0.5, 0.75, 0.9):
    i = int(f * len(tier)) - 1
    print(f"{f:.2f} | {qa[i]:.5f} | {qm[i]:.5f} | {qb[i]:.5f} | {math.log(qa[i] / qb[i]):+.3f}")
la, lb, lm = np.log(qa), np.log(qb), np.log(qm); se = lambda x: x.std() / math.sqrt(len(x))
print(f"# mean over the tier of ln(share of the members examined before it): cover first {la.mean():.3f} +- {se(la):.3f}; by the mean alone {lm.mean():.3f} +- {se(lm):.3f}; chance first {lb.mean():.3f} +- {se(lb):.3f}")
d = np.log(ua) - np.log(ub)
print(f"# gain of chance first over cover first, member by member: {d.mean():+.3f} +- {se(d):.3f} nats")
# what the spread could be worth: the score changes by z x (relative change of the sd) for a cover at fixed mean
zt = (mt - (TIER + 0.5)) / np.sqrt(vt); rel = np.mean([np.sqrt(vc[k1c == k]).std() / np.sqrt(vc[k1c == k]).mean() for k in np.unique(k1c) if (k1c == k).sum() > 1000])
print(f"# the tier sits {zt.mean():.2f} sd below the mean of its covers; one sd of the cover-to-cover variation of the spread ({rel:.2%}) moves the log chance by about z^2 x that = {zt.mean() ** 2 * rel:.3f} nats")
