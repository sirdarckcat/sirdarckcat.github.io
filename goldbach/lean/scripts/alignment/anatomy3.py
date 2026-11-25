"""The per-prime tilt of the best members of any miniature (generic form of anatomy2.py, from the lists of truth2.c).
For each later prime s: rows left before s (tier mean), expected gain L/s, mean gain, the tilt theta_s (maximum
likelihood against the exact law of the gain given the member's own left set), its information; and the prediction
"information = (rows left / s) x a function of the price": the information of a Poisson count of mean mu tilted by
theta is  mu (theta e^theta - e^theta + 1).
  python anatomy3.py Q LINE DEPTH TIER FILE.top ..."""
import math, sys
import numpy as np
Q, LINE, DEPTH, TIER = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
ROWS = [p for p in primes_upto(Q - 1) if p > 2]; SP = [p for p in primes_upto(DEPTH) if p > 2]; COVER = [p for p in SP if p <= LINE]; DEEP = [p for p in SP if p > LINE]
Wd = (len(ROWS) + 63) // 64
def mask(s):
    m = np.zeros((s, Wd), dtype=np.uint64)
    for j, q in enumerate(ROWS): m[q % s, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    return m
def pc(x): return np.bitwise_count(x).sum(axis=-1).astype(np.int64)
rowsN = []
for f in sys.argv[5:]:
    for line in open(f):
        a = line.split()
        if int(a[2]) <= TIER: rowsN.append(int(a[0]))
nt = np.array(sorted(rowsN), dtype=np.int64); T = len(nt)
left = np.zeros((T, Wd), dtype=np.uint64)
for j in range(len(ROWS)): left[:, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
for s in COVER: left &= ~mask(s)[nt % s]
k1 = pc(left)
print(f"# tier k2 <= {TIER}: {T:,d} members; mean rows left at the line {k1.mean():.2f}")
print("prime s | rows left before s | expected gain | mean gain | tilt theta_s | information | Poisson formula mu (theta e^theta - e^theta + 1) | cumulative share")
tot = 0.0; res = []
for s in DEEP:
    m = mask(s); cm = m[nt % s]; L = pc(left); g = pc(left & cm).astype(np.float64)
    cnt = np.empty((T, s)); 
    for a in range(s): cnt[:, a] = pc(left & m[a])
    th = 0.0
    for _ in range(80):
        e = np.exp(np.minimum(th * cnt, 500.0)); z = e.sum(axis=1); m1 = (e * cnt).sum(axis=1) / z; m2 = (e * cnt * cnt).sum(axis=1) / z
        grad = float((g - m1).sum()); hess = float((m2 - m1 * m1).sum())
        if hess <= 0: break
        step = max(-2.0, min(2.0, grad / hess)); th += step
        if abs(step) < 1e-10: break
    e = np.exp(np.minimum(th * cnt, 500.0)); kl = float((th * g - np.log(e.mean(axis=1))).mean()); mu = float((L / s).mean())
    res.append((s, float(L.mean()), mu, float(g.mean()), th, kl, mu * (th * math.exp(th) - math.exp(th) + 1))); tot += kl
    left &= ~cm
cum = 0.0
for (s, L, mu, g, th, kl, pois) in res:
    cum += kl
    if s in (DEEP[0], DEEP[1], DEEP[2]) or s in (41, 61, 89, 97, 149, 199) or s == DEEP[-1]:
        print(f"{s} | {L:.2f} | {mu:.3f} | {g:.3f} | {th:.3f} | {kl:.4f} | {pois:.4f} | {cum / tot:.3f}")
print(f"# sum of the informations of the {len(DEEP)} later primes: {tot:.2f} nats; sum of the Poisson formula: {sum(r[6] for r in res):.2f}; tilt: first prime {res[0][4]:.2f}, last {res[-1][4]:.2f}")
half = next(s for i, (s, *_r) in enumerate(res) if sum(x[5] for x in res[:i + 1]) >= tot / 2)
print(f"# half of the information is reached at the prime {half} (number {[r[0] for r in res].index(half) + 1} of {len(res)})")
