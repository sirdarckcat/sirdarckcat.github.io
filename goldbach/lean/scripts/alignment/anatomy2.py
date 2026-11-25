"""Question 1, part B: the anatomy of the luck beyond the line.

For a member N and each prime s beyond the line (29..199, taken in increasing order) let R be the rows still left
before s and g_s the number of them in the class of N modulo s; then k2 = k1 - sum of the g_s.  Given R, a uniformly
random class of s holds g rows with the probability read off the class counts of R modulo s; that is the exact law of
g_s for an unselected member with the same past.  For a tier of best members:
  - the mean of g_s against its expectation L/s (L = #R) for the tier's own left sets;
  - the exponential tilt theta_s that turns the unselected law into the tier's (maximum likelihood, one parameter per
    prime), and the information it carries, E[theta g - ln Z];  their sum is set against the luck nats of part A;
  - what a list on the raw classes of s could see: the information of the class of N modulo s itself (not relative to
    the cover), for every prime 3..199;
  - incidences and overlaps: raw incidences with the primes beyond the line, incidences on the rows the cover left,
    distinct rows struck.
  python anatomy2.py TIER  (the tier is k2 <= TIER)"""
import math, os, sys
import numpy as np
D = os.environ.get("PPRIME_DATA", "../pprime_families/data")
N = np.memmap(f"{D}/N.u32", dtype=np.uint32, mode="r"); k1 = np.asarray(np.memmap(f"{D}/k1.u8", dtype=np.uint8, mode="r")); k2 = np.asarray(np.memmap(f"{D}/k2.u8", dtype=np.uint8, mode="r"))
n = len(k1); TIER = int(sys.argv[1]) if len(sys.argv) > 1 else 10
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
ROWS = [p for p in primes_upto(999) if p > 2]; SP = [p for p in primes_upto(199) if p > 2]; COVER = [p for p in SP if p <= 23]; DEEP = [p for p in SP if p > 23]
MASK = {}
for s in SP:
    m = np.zeros((s, 3), dtype=np.uint64)
    for j, q in enumerate(ROWS): m[q % s, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    MASK[s] = m
FULL = np.zeros(3, dtype=np.uint64)
for j in range(len(ROWS)): FULL[j >> 6] |= np.uint64(1) << np.uint64(j & 63)
def pc(x): return np.bitwise_count(x).sum(axis=-1).astype(np.int64)

def analyse(nn, want_counts):
    """for members nn: left mask at the line, gains g_s, and (optionally) for every later prime the class counts of the current left set"""
    left = np.broadcast_to(FULL, (len(nn), 3)).copy()
    for s in COVER: left &= ~MASK[s][nn % s]
    left23 = left.copy(); out = {"k1": pc(left), "g": {}, "L": {}, "K23": {}, "W": {}, "cnt": {}}
    for s in DEEP:
        cm = MASK[s][nn % s]
        out["L"][s] = pc(left); out["g"][s] = pc(left & cm); out["K23"][s] = pc(left23 & cm); out["W"][s] = pc(cm)
        if want_counts:
            cnt = np.empty((len(nn), s), dtype=np.int8)
            for a in range(s): cnt[:, a] = pc(left & MASK[s][a])
            out["cnt"][s] = cnt
        left &= ~cm
    out["k2"] = pc(left); return out

tier = np.nonzero(k2 <= TIER)[0]; nt = np.asarray(N[tier]).astype(np.int64)
A = analyse(nt, True)
assert np.array_equal(A["k1"], k1[tier]) and np.array_equal(A["k2"], k2[tier])
total = math.log(n / len(tier)); h_all = np.bincount(k1, minlength=64) / n; h = np.bincount(k1[tier], minlength=64) / len(tier)
cover = float(np.sum(np.where(h > 0, h * np.log(np.where(h > 0, h, 1) / np.where(h_all > 0, h_all, 1)), 0.0)))
print(f"# tier k2 <= {TIER}: {len(tier):,d} members; total rarity {total:.2f} nats = cover {cover:.2f} + luck {total - cover:.2f}")
# controls with the tier's distribution of k1
rng = np.random.default_rng(4); ctrl = []
for c in np.unique(k1[tier]):
    pool = np.nonzero(k1 == c)[0]; want = int(round(200000 * h[c])); 
    if want: ctrl.append(rng.choice(pool, size=min(want, len(pool)), replace=False))
ctrl = np.concatenate(ctrl); C = analyse(np.asarray(N[np.sort(ctrl)]).astype(np.int64), False)
print(f"# controls: {len(ctrl):,d} members with the same distribution of rows left at depth 23 (mean k1 {C['k1'].mean():.2f}, mean k2 {C['k2'].mean():.2f}; tier mean k1 {A['k1'].mean():.2f}, k2 {A['k2'].mean():.2f})")
print("\nprime s | rows left before s, tier (controls) | expected gain L/s for the tier's own left sets | mean gain g_s in the tier | in the controls | tilt theta_s | information, nats | cumulative | share of the luck")
info = {}; cumi = 0.0; rows_out = []
for s in DEEP:
    cnt = A["cnt"][s].astype(np.float64); g = A["g"][s].astype(np.float64)
    th = 0.0
    for _ in range(60):                                   # Newton on the concave log-likelihood sum(theta g - ln mean_a exp(theta cnt))
        e = np.exp(np.minimum(th * cnt, 500.0)); z = e.sum(axis=1); m1 = (e * cnt).sum(axis=1) / z; m2 = (e * cnt * cnt).sum(axis=1) / z
        grad = float((g - m1).sum()); hess = float((m2 - m1 * m1).sum())
        if hess <= 0: break
        step = max(-2.0, min(2.0, grad / hess)); th += step
        if abs(step) < 1e-10: break
    e = np.exp(th * cnt); lnz = np.log(e.mean(axis=1)); kl = float((th * g - lnz).mean()); info[s] = (th, kl)
    rows_out.append((s, A["L"][s].mean(), C["L"][s].mean(), (A["L"][s] / s).mean(), g.mean(), C["g"][s].mean(), th, kl))
luck = total - cover; tot_info = sum(v[1] for v in info.values())
for (s, La, Lc, exp_, ga, gc, th, kl) in rows_out:
    cumi += kl
    print(f"{s} | {La:.2f} ({Lc:.2f}) | {exp_:.3f} | {ga:.3f} | {gc:.3f} | {th:.3f} | {kl:.4f} | {cumi:.3f} | {cumi / tot_info:.3f}")
print(f"# sum of the informations of the 37 gains: {tot_info:.2f} nats; luck nats from part A: {luck:.2f}")
half = next(s for (s, *_r) in rows_out if sum(info[x][1] for x in DEEP if x <= s) >= 0.5 * tot_info)
print(f"# half of it is reached at the prime {half}; the first prime (29) carries {info[29][1] / tot_info:.3f}, the first three {sum(info[x][1] for x in DEEP[:3]) / tot_info:.3f}")
# gains per member: how concentrated
G = np.stack([A["g"][s] for s in DEEP], axis=1).astype(np.float64); E = np.stack([A["L"][s] / s for s in DEEP], axis=1)
exc = G - E; tot_exc = exc.sum(axis=1)
top3 = np.sort(exc, axis=1)[:, -3:].sum(axis=1)
print(f"# per member: total excess of the gains over expectation {tot_exc.mean():.2f} rows (sd {tot_exc.std():.2f}); of which the three luckiest primes of the member give {top3.mean():.2f}; "
      f"primes with a gain above expectation: {(exc > 0).sum(axis=1).mean():.1f} of 37 (controls: {(np.stack([C['g'][s] for s in DEEP], axis=1) - np.stack([C['L'][s] / s for s in DEEP], axis=1) > 0).sum(axis=1).mean():.1f})")
print(f"# largest single gain of a member: mean {G.max(axis=1).mean():.2f} (controls {np.stack([C['g'][s] for s in DEEP], axis=1).max(axis=1).mean():.2f})")
# incidences and overlaps
def summ(X):
    inc = sum(X["W"][s] for s in DEEP); k23 = sum(X["K23"][s] for s in DEEP); new = X["k1"] - X["k2"]
    return inc.mean(), k23.mean(), new.mean(), (k23 - new).mean()
a = summ(A); c = summ(C)
print("\n# incidences of the classes of the primes beyond the line: with all rows | with the rows the cover left | distinct rows of the cover's struck | repeats")
print(f"tier | {a[0]:.2f} | {a[1]:.2f} | {a[2]:.2f} | {a[3]:.2f}")
print(f"controls | {c[0]:.2f} | {c[1]:.2f} | {c[2]:.2f} | {c[3]:.2f}")
# what the raw class of each prime tells: information of N mod s in the tier against all members
print("\n# information of the class of N modulo each prime, tier against all members (nats; bias (classes - 1)/(2 members) removed)")
tot_cov = tot_deep = 0.0; line = []
for s in SP:
    cls = nt % s; m = s - 1 if s <= 29 else s
    p = np.bincount(cls, minlength=s) / len(nt); u = 1.0 / m
    kl = float(np.sum(np.where(p > 0, p * np.log(np.where(p > 0, p, 1) / u), 0.0))) - (m - 1) / (2 * len(nt))
    line.append((s, kl)); 
    if s <= 23: tot_cov += kl
    else: tot_deep += kl
print(" ".join(f"{s}:{kl:.3f}" for s, kl in line))
print(f"# sum over the cover primes 3..23: {tot_cov:.2f} nats (their joint information through k1: {cover:.2f}; pinning them all costs {sum(math.log(s - 1) for s in COVER):.2f});  sum over the 37 primes beyond the line: {tot_deep:.2f} nats, against {luck:.2f} of luck")
