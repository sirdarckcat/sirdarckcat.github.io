"""The price, one prime at a time, with the other primes held fixed.

For a member and a later prime s let others_s be the rows left by every prime except s, and only_s the number of
them in the member's class modulo s (the rows that s alone strikes).  In a population weighted by
exp(-beta x rows left) the class modulo s, given all the other classes, has the law exp(beta x only_s) exactly: the
same beta at every prime.  So "the gain per later prime is (rows/s) times the price" is the statement that the best
members show one tilt beta at all primes, in the count only_s whose unselected mean is others_s / s.
For the tier (at most TIER rows left) of an exact miniature, from the lists of truth2.c: the means of others_s / s and
only_s, the tilt beta_s fitted to each prime by maximum likelihood against the exact class counts of others_s, and
one beta fitted to all primes together; with the file of ensemble_tier.c, the same means for random class vectors.
  python anatomy4.py Q LINE ZMEM DEPTH TIER [ENSEMBLE.tier,...] FILE.top ..."""
import math, sys
import numpy as np
Q, LINE, ZMEM, DEPTH, TIER = (int(x) for x in sys.argv[1:6])
ens = sys.argv[6].split(",") if sys.argv[6].endswith(".tier") else []
tops = sys.argv[7:] if ens else sys.argv[6:]
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
ROWS = [p for p in primes_upto(Q - 1) if p > 2]; SP = [p for p in primes_upto(DEPTH) if p > 2]; Wd = (len(ROWS) + 63) // 64
def mask(s):
    m = np.zeros((s, Wd), dtype=np.uint64)
    for j, q in enumerate(ROWS): m[q % s, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    return m
def pc(x): return np.bitwise_count(x).sum(axis=-1).astype(np.int64)
N = []
for f in tops:
    for line in open(f):
        a = line.split()
        if int(a[2]) <= TIER: N.append(int(a[0]))
N = np.array(sorted(N), dtype=np.int64); T = len(N); mk = {s: mask(s) for s in SP}
full = np.zeros((T, Wd), dtype=np.uint64)
for j in range(len(ROWS)): full[:, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
pre = [full]
for s in SP: pre.append(pre[-1] & ~mk[s][N % s])
suf = [full]
for s in reversed(SP): suf.append(suf[-1] & ~mk[s][N % s])
suf = suf[::-1]                                               # suf[i] = rows left by the primes SP[i:]
E = {}
for f in ens:
    for line in open(f):
        a = [int(x) for x in line.split()]; e = E.setdefault(a[0], np.zeros(5)); e += np.array(a[1:], dtype=float)
print(f"# Q = {Q}, line {LINE}, depth {DEPTH}; tier: at most {TIER} rows left, {T:,d} members" + (f"; ensemble tier: {int(E[SP[0]][0]):,d} class vectors" if E else ""))
print("prime s | rows left by the other primes | unselected mean of the rows s alone strikes | mean in the tier | ratio | tilt beta_s | " + ("ensemble tier: mean | ratio of the two means | " if E else "") + "sequential gain, exact" + (" | ensemble" if E else ""))
num = den = 0.0; tab = []; store = []
for i, s in enumerate(SP):
    if s <= LINE: continue
    oth = pre[i] & suf[i + 1]; L = pc(oth); m = mk[s]; cls = N % s
    cnt = np.empty((T, s))
    for a in range(s): cnt[:, a] = pc(oth & m[a])
    if s <= ZMEM: cnt[:, 0] = -1e9                              # class 0 is not available to a member
    u = cnt[np.arange(T), cls]; store.append((cnt, u))
    def fit(cn, uu):
        th = 0.0
        for _ in range(100):
            e = np.exp(np.clip(th * cn, -700, 500)); zz = e.sum(axis=1); m1 = (e * cn).sum(axis=1) / zz; m2 = (e * cn * cn).sum(axis=1) / zz
            g = float((uu - m1).sum()); h = float((m2 - m1 * m1).sum())
            if h <= 0: break
            st = max(-1.0, min(1.0, g / h)); th += st
            if abs(st) < 1e-10: break
        return th
    base = np.where(cnt >= 0, cnt, 0).sum(axis=1) / ((s - 1) if s <= ZMEM else s)
    row = [s, float(L.mean()), float(base.mean()), float(u.mean()), fit(cnt, u), float(pc(pre[i] & m[cls]).mean())]
    tab.append(row)
def fit_all():
    th = 0.0
    for _ in range(100):
        g = h = 0.0
        for cn, uu in store:
            e = np.exp(np.clip(th * cn, -700, 500)); zz = e.sum(axis=1); m1 = (e * cn).sum(axis=1) / zz; m2 = (e * cn * cn).sum(axis=1) / zz
            g += float((uu - m1).sum()); h += float((m2 - m1 * m1).sum())
        st = max(-1.0, min(1.0, g / h)); th += st
        if abs(st) < 1e-10: break
    return th
beta = fit_all()
pred = []
for cn, uu in store:
    e = np.exp(np.clip(beta * cn, -700, 500)); pred.append(float(((e * cn).sum(axis=1) / e.sum(axis=1)).mean()))
show = set([r[0] for r in tab][:3] + [41, 61, 89, 97, 127, 149, 173, 199])
for r, p in zip(tab, pred):
    s = r[0]
    if s not in show: continue
    line = f"{s} | {r[1]:.2f} | {r[2]:.4f} | {r[3]:.4f} | {r[3] / r[2]:.2f} | {r[4]:.3f} | "
    if E: e = E[s]; line += f"{e[4] / e[0]:.4f} | {r[3] / (e[4] / e[0]):.3f} | "
    line += f"{r[5]:.3f}" + (f" | {E[s][2] / E[s][0]:.3f}" if E else "")
    print(line)
b = np.array([r[4] for r in tab]); ratio = np.array([r[3] / r[2] for r in tab])
print(f"# tilt fitted prime by prime: least {b.min():.3f}, largest {b.max():.3f}, mean {b.mean():.3f}, sd over the {len(b)} primes {b.std():.3f}; one tilt fitted to all primes: beta = {beta:.3f}")
print(f"# with that one beta: predicted mean of the rows s alone strikes against the actual, over the primes: largest relative error {max(abs(p / r[3] - 1) for r, p in zip(tab, pred)):.3f}, sum predicted {sum(pred):.3f}, actual {sum(r[3] for r in tab):.3f}")
print(f"# ratio (mean in the tier) / (unselected mean): least {ratio.min():.2f}, largest {ratio.max():.2f}; e^beta = {math.exp(beta):.2f}")
if E:
    d = np.array([r[3] / (E[r[0]][4] / E[r[0]][0]) for r in tab]); d2 = np.array([r[5] / (E[r[0]][2] / E[r[0]][0]) for r in tab])
    print(f"# exact tier against ensemble tier, prime by prime: rows s alone strikes, ratio {d.min():.3f} to {d.max():.3f} (mean {d.mean():.3f}); sequential gain, ratio {d2.min():.3f} to {d2.max():.3f} (mean {d2.mean():.3f})")
