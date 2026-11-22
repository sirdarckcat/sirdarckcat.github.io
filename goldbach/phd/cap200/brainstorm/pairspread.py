# Ideas 5 and 64 of the brainstorm: how much does the pair term of the Hardy-Littlewood model
# vary among near-optimal covers, and can a cover have "twice the expected number" of pairs of
# uncovered rows that are congruent modulo the first sieve primes?
#   ln P(no prime row) = sum ln(1 - p) + p^2 * sum over pairs of ln S(q, q') + ...
#   ln S = sum over primes s outside the cover of [ln((s-1)/(s-2)) if s | q - q'] + ln((1 - 2/s)/(1 - 1/s)^2)
#   usage: python3 -I pairspread.py POOL.json [max vectors]
import json, math, sys
import numpy as np
d = json.load(open(sys.argv[1])); NV = int(sys.argv[2]) if len(sys.argv) > 2 else 64
Q = d["Q"]; mods = [int(r) for r in d["mods"]]; pool = d["pool"][:NV]
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
allp = [int(x) for x in primes_upto(Q) if x >= 3]
P = np.array(allp, dtype=np.int64); P = P[P < Q]
free = [s for s in allp if s not in set(mods)]
LNX = 200 * math.log(10); p = 2 * math.prod(r / (r - 1) for r in mods) / LNX
lnC = sum(math.log((1 - 2 / s) / (1 - 1 / s) ** 2) for s in free) - 1 / (Q * math.log(Q))
gain = {s: math.log((s - 1) / (s - 2)) for s in free}
out = []
for k0, cls in pool:
    alive = np.ones(len(P), dtype=bool)
    for r, c in zip(mods, cls): alive &= (P % r != c)
    U = P[alive]; k = len(U)
    extra = 0.0; pairs5000 = 0; exp5000 = 0.0
    for s in free:
        _, cnt = np.unique(U % s, return_counts=True)
        c2 = int((cnt * (cnt - 1) // 2).sum())
        extra += c2 * gain[s]
        if s <= 5000: pairs5000 += c2; exp5000 += k * (k - 1) / 2 / (s - 1)
    corr = p * p * (k * (k - 1) / 2 * lnC + extra)
    out.append((k, corr, pairs5000, exp5000))
a = np.array(out)
print("Q = %d, %d covers with %d to %d rows left, p = %.5f" % (Q, len(out), a[:, 0].min(), a[:, 0].max(), p))
print("pair term of ln P(success), nats: mean %+.4f, sd %.4f, min %+.4f, max %+.4f" % (a[:, 1].mean(), a[:, 1].std(), a[:, 1].min(), a[:, 1].max()))
r = a[:, 2] / a[:, 3]
print("pairs of uncovered rows congruent modulo a non-cover prime <= 5000, observed / expected: mean %.4f, sd %.4f, min %.4f, max %.4f (mean count %.0f)" % (r.mean(), r.std(), r.min(), r.max(), a[:, 2].mean()))
k = a[:, 0].mean()
print("what 'twice the expected number' would be worth: %+.3f nats" % (p * p * a[:, 3].mean() * np.mean([gain[s] * (s - 1) for s in free if s <= 5000]) / 1.0 * 0 + p * p * sum(k * (k - 1) / 2 / (s - 1) * gain[s] for s in free if s <= 5000)))
print("and how many sd of the pool that is: %.0f" % ((2 - r.mean()) / max(r.std(), 1e-12)))
