"""Combines the runs of sieve_members: per sieve depth B, the mean and variance of S over all members sieved, with the
sampling error of the variance, next to the formula (exact constants; and with w = ln 463/ln B, R = exp(-1/(463 ln 463))).
Then, from the measured histogram of S at the deepest B, what the variance is worth in hits: ln E (1 - p')^S against
(1 - p')^(E S), and the same for a funnel that keeps the best fraction f of the members.
  python combine.py Q FILE LINE  run1.txt run2.txt ..."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from covlib import primes_upto, read_covers, rows_of, base_probability

Q = int(sys.argv[1]); claimed, classes = read_covers(sys.argv[2])[int(sys.argv[3])]
rows = rows_of(classes, Q); n = len(rows); p = base_probability(classes)
agg = {}; hist = {}; blocks = {}
for f in sys.argv[4:]:
    for l in open(f):
        t = l.split()
        if t and t[0] == "B":
            B = float(t[1]); a = agg.setdefault(B, [0, 0.0, 0.0]); a[0] += int(t[3]); a[1] += float(t[5]); a[2] += float(t[7])
            blocks.setdefault(B, []).append(float(t[11]))
        elif t and t[0] == "H":
            hist[int(t[1])] = hist.get(int(t[1]), 0) + int(t[2])
PR = primes_upto(int(max(agg))); Z = 463
s0 = np.zeros(Q, dtype=np.int64)
for s in PR[(PR > Z) & (PR < Q)]: s0[s::s] = s
d = np.abs(rows[:, None] - rows[None, :]); s0d = s0[d]
print("B | members sieved | mean S measured | E S = n w | Var S measured (+- sampling sd) | variances of the blocks | formula, exact w and R | formula with w = ln 463/ln B, R = exp(-1/(463 ln 463)) | binomial n w (1 - w) | sd ratio measured | formula")
for B in sorted(agg):
    m, s1, s2 = agg[B]; mean = s1 / m; var = (s2 - m * mean * mean) / (m - 1)
    big = PR[(PR > Z) & (PR <= B)].astype(np.float64)
    w = math.exp(float(np.sum(np.log1p(-1.0 / big)))); R = math.exp(float(np.sum(np.log1p(-1.0 / (big - 1.0) ** 2))))
    T = float(np.where((s0d > 0) & (s0d <= B), 1.0 / np.maximum(s0d - 2, 1), 0.0).sum())
    ind = n * w * (1 - w); f_exact = ind + w * w * (n * (n - 1) * (R - 1) + R * T)
    wa = math.log(Z) / math.log(B); Ra = math.exp(-1.0 / (Z * math.log(Z))); f_appr = n * wa * (1 - wa) + wa * wa * (n * (n - 1) * (Ra - 1) + Ra * T)
    print(f"{B:.0e} | {m:,d} | {mean:.2f} | {n * w:.2f} | {var:.2f} (+- {var * math.sqrt(2 / m):.2f}) | {' '.join(f'{x:.1f}' for x in blocks[B])} | {f_exact:.2f} | {f_appr:.2f} | {ind:.2f} | {math.sqrt(var / ind):.4f} | {math.sqrt(f_exact / ind):.4f}")
if hist:
    B = max(agg); big = PR[(PR > Z) & (PR <= B)].astype(np.float64); w = math.exp(float(np.sum(np.log1p(-1.0 / big))))
    v = np.array(sorted(hist)); c = np.array([hist[x] for x in v], dtype=np.float64); m = c.sum()
    mean = (v * c).sum() / m; var = (c * (v - mean) ** 2).sum() / (m - 1); sd = math.sqrt(var)
    skew = (c * (v - mean) ** 3).sum() / m / sd ** 3; kurt = (c * (v - mean) ** 4).sum() / m / sd ** 4 - 3
    pp = p / w; th = -math.log(1 - pp)
    print(f"\n# histogram of S at B = {B:.0e}: {int(m):,d} members, mean {mean:.2f}, variance {var:.2f}, skewness {skew:+.3f}, excess kurtosis {kurt:+.3f}")
    print(f"# p = {p:.5f}; chance that a row left at B is prime p' = p / w = {pp:.5f}; theta = -ln(1 - p') = {th:.5f}; theta x sd = {th * sd:.4f}")
    mass = float((c * np.exp(-th * (v - mean))).sum() / m)
    print(f"# ln E (1-p')^(S - E S): measured {math.log(mass):.4f}; Gaussian theta^2 Var / 2 with the measured variance: {th * th * var / 2:.4f}")
    ind = n * w * (1 - w)
    from statistics import NormalDist
    nd = NormalDist()
    print("# what a larger spread would be worth, Gaussian S: ln of the hits captured by a funnel keeping the best fraction f, variance raised from the formula's value to the binomial value")
    PR2 = None
    big = PR[(PR > Z) & (PR <= B)].astype(np.float64); R = math.exp(float(np.sum(np.log1p(-1.0 / (big - 1.0) ** 2))))
    T = float(np.where((s0d > 0) & (s0d <= B), 1.0 / np.maximum(s0d - 2, 1), 0.0).sum()); fvar = ind + w * w * (n * (n - 1) * (R - 1) + R * T)
    for f in (1.0, 0.3, 0.1, 0.03, 0.01, 0.001):
        def cap(v_):
            sd_ = math.sqrt(v_); z = nd.inv_cdf(f) if f < 1 else float("inf")
            return th * th * v_ / 2 + (math.log(nd.cdf(z + th * sd_)) if f < 1 else 0.0)
        print(f"#   f = {f:g}: {cap(ind) - cap(fvar):+.4f} nats")
