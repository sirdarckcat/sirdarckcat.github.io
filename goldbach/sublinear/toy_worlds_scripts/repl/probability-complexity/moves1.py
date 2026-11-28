#!/usr/bin/env python3
"""moves1.py DEPTH: correlations of the exact sieve count S(k) (rows of member k with no factor in (463, DEPTH]) between
a member and its translate k + D, on the whole real window of the 200,000 cover; variance shares of single primes."""
import sys, numpy as np, math
depth = sys.argv[1]; pre = sys.argv[2] if len(sys.argv) > 2 else "S"
S = np.fromfile(f"{pre}.{depth}.u16", dtype=np.uint16).astype(np.float64); K = len(S)
mu, var = S.mean(), S.var(); sd = math.sqrt(var)
print(f"depth {depth}: K {K} mean {mu:.3f} sd {sd:.3f} var {var:.2f} min {S.min():.0f} max {S.max():.0f}")
Z = (S - mu) / sd
def share(p):
    c = np.arange(K) % p
    cnt = np.bincount(c, minlength=p); sm = np.bincount(c, weights=Z, minlength=p); gm = sm / cnt
    raw = float((cnt * gm ** 2).sum() / K)            # between-class variance share, biased up by (p-1)/K
    return raw - (p - 1) / K
def primes(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
PRS = [int(p) for p in primes(3000) if p > 463]
sh = {p: share(p) for p in PRS}
print("variance share v_p of single later primes (x1e3):", " ".join(f"{p}:{1e3*sh[p]:.3f}" for p in PRS[:12]))
print(f"sum of v_p, p in (463,1000]: {sum(v for p,v in sh.items() if p<=1000):.4f}; (463,2000]: {sum(v for p,v in sh.items() if p<=2000):.4f}; (463,3000]: {sum(sh.values()):.4f}")
def corr(D):
    return float((Z[:-D] * Z[D:]).mean()), 1 / math.sqrt(K - D)
tests = [("1", 1), ("2", 2), ("210", 210), ("463 (cover prime)", 463), ("467", 467), ("479", 479), ("2*467", 934), ("1009", 1009), ("10007", 10007), ("100003", 100003),
         ("467*479", 467 * 479), ("3*467*479", 3 * 467 * 479), ("467*487", 467 * 487), ("479*487", 479 * 487), ("1009*1013", 1009 * 1013), ("467*10007", 467 * 10007),
         ("467^2", 467 * 467), ("random 1234567", 1234567), ("random 7654321", 7654321), ("4999999 (prime)", 4999999)]
print("move k -> k+D | measured corr(S(k),S(k+D)) | +-1sd noise | predicted sum of v_p over later primes p | D")
def pred(D):
    t = 0.0
    for p in PRS:
        if D % p == 0: t += sh[p]
    return t
for name, D in tests:
    c, e = corr(D); print(f"  {name:22s} {c:+.5f}  +-{e:.5f}  pred {pred(D):.5f}")
# conditional tail: P(S(k+D) <= t | S(k) <= t) / P(S <= t)
D = 467 * 479
for qf in (0.015, 0.001, 0.0001):
    t = np.quantile(S, qf); a = S[:-D] <= t; b = S[D:] <= t
    pa, pb, pab = a.mean(), b.mean(), (a & b).mean()
    lift = pab / (pa * pb); n = (a & b).sum()
    print(f"keep {qf}: threshold S<={t:.0f} (z={(t-mu)/sd:.2f}); pairs at D=467*479 both kept {n}; lift {lift:.4f} (ln {math.log(lift) if n else float('nan'):+.4f} +- {1/math.sqrt(max(n,1)):.4f}); Gaussian prediction ln lift ~ rho z^2 = {pred(D)*((t-mu)/sd)**2:.4f}")
    # all neighbours sharing 467*479: mean S of the D-neighbours of kept members
    print(f"     mean S of the D-neighbours of kept members minus mean: {S[D:][a].mean()-mu:+.3f} rows (prediction rho*(mean kept - mu) = {pred(D)*(S[:-D][a].mean()-mu):+.3f})")
np.save(f"hist.{depth}.npy", np.bincount(S.astype(int)))
