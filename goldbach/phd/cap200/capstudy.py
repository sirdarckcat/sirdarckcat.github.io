import json, math, sys, time
import numpy as np

SPEC = sys.argv[1]
b = json.load(open(SPEC)); b = b[0] if isinstance(b, list) else b
Q = b["Q"]; cover = [(int(r), int(a)) for r, a in b["cover"]]; residual = sorted(int(x) for x in b["residual"])
LN = 199 * math.log(10)

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

P = primes_upto(Q - 1); P = P[P >= 3].astype(np.int64)
mods = [r for r, _ in cover]
print("Q", Q, "rows (odd primes < Q)", len(P), "moduli", len(mods), "largest", max(mods), "all odd primes <= max:", mods == [int(x) for x in primes_upto(max(mods)) if x > 2])
res = {r: P % r for r in mods}
cnt = np.zeros(len(P), dtype=np.int32)
for r, a in cover: cnt += (res[r] == a)
# a row q equal to a modulus r with a = 0 class etc: rows that are moduli themselves
left = P[cnt == 0]
print("rows left by the campaign cover:", len(left), "matches spec residual:", sorted(left.tolist()) == residual)
boost = 2.0
for r in mods: boost *= r / (r - 1)
k = len(left); p1 = boost / LN
print("boost %.4f  p1 %.5f  E = k*p1 = %.3f   exact -k*ln(1-p1) = %.3f" % (boost, p1, k * p1, -k * math.log(1 - p1)))
logM = math.log(2) + sum(math.log(r) for r in mods)
print("ln M %.2f nats = %.2f digits; members per vector below 1e200: %.3g, below 1e199: %.3g; e^E = %.3g" % (logM, logM / math.log(10), math.exp(200 * math.log(10) - logM), math.exp(199 * math.log(10) - logM), math.exp(k * p1)))

# first-moment law: exact mean over nonzero residue vectors (rows not among the moduli)
rows_not_mod = [q for q in P.tolist() if q not in set(mods)]
mean = len(rows_not_mod) * math.prod((r - 2) / (r - 1) for r in mods)
# rows that are moduli: q = r is left iff no other modulus kills it (it is never killed by itself for a nonzero class)
mean += sum(math.prod((r - 2) / (r - 1) for r in mods if r != q) for q in mods)
print("exact mean rows left over nonzero residue vectors: %.1f ; mean*p1 = %.2f nats ; 2*C2-type product %.4f" % (mean, mean * p1, 2 * math.prod(1 - 1 / (r - 1) ** 2 for r in mods)))

# Monte Carlo: distribution of rows left over uniformly random nonzero residue vectors
rng = np.random.default_rng(1)
t0 = time.time(); vals = []
for it in range(4000):
    c = np.zeros(len(P), dtype=bool)
    for r in mods:
        c |= (res[r] == rng.integers(1, r))
    vals.append(int((~c).sum()))
vals = np.array(vals)
print("MC 4000 random vectors: mean %.1f sd %.2f min %d max %d  (%.1fs)" % (vals.mean(), vals.std(), vals.min(), vals.max(), time.time() - t0))
z = (vals.mean() - k) / vals.std()
nvec = sum(math.log(r - 1) for r in mods)
print("campaign cover is %.1f sd below the mean; ln(#vectors) = %.1f nats; Gaussian first-moment floor: mean - sd*sqrt(2 ln #vectors) = %.0f" % (z, nvec, vals.mean() - vals.std() * math.sqrt(2 * nvec)))

# marginal value of each modulus in the campaign cover
print("\nmodulus r: class, rows only r kills (u), E without r, gain in E, gain per nat of ln r")
tot_gain = 0
rows = []
for r, a in cover:
    only = int(((cnt == 1) & (res[r] == a)).sum())
    E_with = k * p1
    E_wo = (k + only) * (boost * (r - 1) / r) / LN
    rows.append((r, a, only, E_wo - E_with, (E_wo - E_with) / math.log(r)))
for r, a, only, g, rate in rows:
    if r <= 13 or r in (29, 53, 101, 151, 199, 251, 307, 349, 401, 431, 443, 449, 457, 461):
        print("  r=%3d class %3d  u=%4d  gain %.3f nats  rate %.4f per nat" % (r, a, only, g, rate))
print("  sum of single-removal gains over the 20 largest moduli: %.2f nats for %.1f nats of ln r (rate %.4f)" % (sum(x[3] for x in rows[-20:]), sum(math.log(x[0]) for x in rows[-20:]), sum(x[3] for x in rows[-20:]) / sum(math.log(x[0]) for x in rows[-20:])))

# value of extra moduli beyond the cover (best class inside the rows left)
print("\nextra modulus s: best class count in rows left, E after adding, gain, rate per nat")
L = left
for s in [463, 467, 479, 487, 491, 499, 503, 509, 521, 601, 701, 809, 907, 1009, 2003, 5003]:
    c = np.bincount(L % s, minlength=s); n = int(c.max())
    E_new = (k - n) * (boost * s / (s - 1)) / LN
    print("  s=%5d  best class %2d rows (mean %.2f)  E %.3f  gain %.3f  rate %.4f" % (s, n, k / (s - 1), E_new, k * p1 - E_new, (k * p1 - E_new) / math.log(s)))
np.save("left.npy", left)
