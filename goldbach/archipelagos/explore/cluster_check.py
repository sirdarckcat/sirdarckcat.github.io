# Do large g(N) come in groups?  g(N) = least odd prime p with N - p prime, N even.
# Computes g for L consecutive even N starting at N0 and measures:
#   1. lag enrichment R(d) = P(big(N) and big(N+d)) / P(big)^2, against the value predicted if
#      big(N) depended only on N mod 30030 (class rates estimated on the other half of the data,
#      so the prediction has no small-sample bias);
#   2. whether a big N signals a much bigger one nearby;
#   3. how well residue-only / sieve scores predict big(N).
# usage: python3 cluster_check.py N0 L [pct]
import sys, math
import numpy as np

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, math.isqrt(n) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

N0 = int(float(sys.argv[1])); N0 -= N0 % 2
L = int(float(sys.argv[2]))
PCT = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
PMAX = 40000
lo, hi = N0 - PMAX, N0 + 2 * L
seg = np.ones(hi - lo, dtype=bool)
for p in primes_upto(math.isqrt(hi) + 1):
    p = int(p); st = max(p * p, -(-lo // p) * p)
    seg[st - lo::p] = False
rows = primes_upto(PMAX); rows = rows[rows >= 3]

g = np.zeros(L, dtype=np.int32); un = np.arange(L, dtype=np.int64)
base = N0 - lo
for q in rows:
    q = int(q)
    hit = seg[base - q + 2 * un]
    g[un[hit]] = q; un = un[~hit]
    if un.size == 0: break
assert un.size == 0
print(f"N in [{N0:.4g}, {N0 + 2 * L:.4g}): {L:,} even N; mean g = {g.mean():.1f}; max g = {g.max()} at N = {N0 + 2 * int(g.argmax())}")

G1 = int(np.percentile(g, 100 - PCT)) + 1
G2 = int(np.percentile(g, 100 - PCT / 100)) + 1
big = g >= G1; huge = g >= G2; P = big.mean(); P2 = huge.mean()
print(f"big  := g >= {G1}  ({100 * P:.3f}% of N)")
print(f"huge := g >= {G2}  ({100 * P2:.4f}% of N, {int(huge.sum())} numbers)")

# 1. lag enrichment against a class-only model (mod 30030; rates from the other half)
idx = np.arange(L, dtype=np.int64)
cls = (N0 + 2 * idx) % 30030
h = L // 2
def rates(sel):
    c = np.bincount(cls[sel], minlength=30030).astype(float)
    return np.bincount(cls[sel], weights=big[sel], minlength=30030) / np.maximum(c, 1)
pA = rates(idx >= h); pB = rates(idx < h)          # pA used on the first half, pB on the second
pc_other = np.where(idx < h, pA[cls], pB[cls])     # P(big | class of N), estimated without N
def R(d):
    j = d // 2
    return (big[:-j] & big[j:]).mean() / (big[:-j].mean() * big[j:].mean())
def R_pred(d):
    j = d // 2
    # rate for N from one half, rate for N+d from the other half: independent estimates
    a = pA[cls[:-j]]; b = pB[(cls[:-j] + d) % 30030]
    return (a * b).mean() / (a.mean() * b.mean())
print("\n     lag d   R(d) measured   R(d) if only N mod 30030 mattered")
for d in [2, 4, 6, 8, 12, 18, 24, 30, 36, 42, 60, 90, 210, 420, 2310, 30030, 60060, 90090]:
    if d // 2 < L // 3:
        print(f"{d:>10}   {R(d):10.2f}      {R_pred(d):10.2f}")
far = [30030 * k for k in (7, 11, 13, 17)] + [30030 * k + 6 for k in (7, 11)] + [30030 * k + 30 for k in (7, 11)]
for d in far:
    if d // 2 < L // 3:
        print(f"{d:>10}   {R(d):10.2f}      {R_pred(d):10.2f}")

# 2. does a big N point to a huge one nearby?
lagset = [6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 90, 120, 150, 180, 210]
J = max(lagset) // 2
core = np.arange(J, L - J)
nb_huge = np.zeros(core.size, dtype=bool); nb_big = np.zeros(core.size, dtype=bool)
for d in lagset:
    j = d // 2
    nb_huge |= huge[core + j] | huge[core - j]
    nb_big |= big[core + j] | big[core - j]
bc = big[core]
print(f"\nneighbours N +- d, d in {{6,...,60,90,...,210}} ({2*len(lagset)} numbers):")
print(f"  P(some neighbour is huge | N big)  = {nb_huge[bc].mean():.5f}   vs  | N random: {nb_huge.mean():.5f}  ({nb_huge[bc].mean()/nb_huge.mean():.1f}x)")
hc = huge[core]
print(f"  P(some neighbour is big | N huge)  = {nb_big[hc].mean():.3f}     vs  | N random: {nb_big.mean():.3f}")
print(f"  huge N with no big neighbour: {int((hc & ~nb_big).sum())} of {int(hc.sum())}")

# 3. scores built from residues only: rows q < G1 whose N - q has no prime factor <= z
rq = rows[rows < G1]
print(f"\nscore u_z(N) = how many of the {len(rq)} rows q < {G1} have N - q free of primes <= z")
print("       z   share of the big N in the 1% / 5% of N with the lowest u_z (random: 1% / 5%)")
for z in (13, 100, 1000, 10000):
    rough = np.ones(hi - lo, dtype=np.int8)
    for s in primes_upto(z):
        s = int(s); st = -(-lo // s) * s
        rough[st - lo::s] = 0
    u = np.zeros(L, dtype=np.int32)
    for q in rq:
        a = base - int(q)
        u += rough[a:a + 2 * L:2][:L]
    order = np.argsort(u, kind="stable")
    out = [100 * big[order[:int(f * L)]].sum() / big.sum() for f in (0.01, 0.05)]
    hz = 100 * huge[order[:int(0.01 * L)]].sum() / huge.sum()
    print(f"{z:>8}   {out[0]:5.1f}% / {out[1]:5.1f}%   (huge N in the lowest 1%: {hz:5.1f}%)")
