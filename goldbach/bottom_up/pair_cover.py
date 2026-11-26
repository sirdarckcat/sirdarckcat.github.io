# Bottom-up round: the shift-robust pair. One cover (classes a_r for the 89 odd primes up to 463) chosen so that both N and N + d are
# good members: N's rows are the primes q < Q in no class; N + d's are the primes q with q - d in no class (N + d - q = N - (q - d)).
# The rows of the two members that are the same integer are the q in N's residual with q + d prime; they are tested once.
# Greedy in increasing order of the moduli, then 1-flip descent, on the union of the two target sets, against the single cover
# (targets P alone).
#   python3 pair_cover.py [d]
import sys, math
import numpy as np
Q, d = 200000, int(sys.argv[1]) if len(sys.argv) > 1 else 30
s = np.ones(Q + 64, bool); s[:2] = False
for i in range(2, int((Q + 64) ** 0.5) + 1):
    if s[i]: s[i * i::i] = False
P = np.nonzero(s[:Q])[0]; P = P[P > 2]
mods = [r for r in range(3, 464) if s[r]]
lam = -math.log(1 - 2 * math.prod(r / (r - 1) for r in mods) / (200 * math.log(10)))

def optimize(targets, weights):
    """classes minimizing the weighted count of targets in no class: greedy, then descent."""
    T = np.asarray(targets); w = np.asarray(weights, float); R = [T % r for r in mods]
    cls = [0] * len(mods); cnt = np.zeros(len(T), np.int32)
    for i, r in enumerate(mods):
        alive = cnt == 0
        g = np.bincount(R[i][alive], weights=w[alive], minlength=r); g[0] = -1
        cls[i] = int(np.argmax(g)); cnt += (R[i] == cls[i])
    improved = True
    while improved:
        improved = False
        for i, r in enumerate(mods):
            cnt -= (R[i] == cls[i]); alive = cnt == 0
            g = np.bincount(R[i][alive], weights=w[alive], minlength=r); g[0] = -1
            b = int(np.argmax(g))
            if g[b] > g[cls[i]] + 1e-9: cls[i] = b; improved = True
            cnt += (R[i] == cls[i])
    return cls

def residual(cls, targets):
    T = np.asarray(targets); unc = np.ones(len(T), bool)
    for r, a in zip(mods, cls): unc &= (T % r) != a
    return T[unc]

single = optimize(P, np.ones(len(P)))
U = residual(single, P)
print(f"single cover (greedy + descent): {len(U)} rows (the tempered best is 1,502); E = {lam * len(U):.2f}")
T2 = P - d; T2 = T2[T2 > 0]
union = np.union1d(P, T2)
pair = optimize(union, np.ones(len(union)))
U1 = residual(pair, P); U2n = residual(pair, T2)          # N + d's rows, as integers n = q - d in N's frame
shared = np.intersect1d(U1, U2n)
f = len(shared) / len(U1)
print(f"pair cover for d = {d}: N has {len(U1)} rows, N + d has {len(U2n)}, {len(shared)} shared ({100 * f:.1f}% of N's)")
hit_single = math.exp(-lam * len(U)); hit_pair = math.exp(-lam * len(U1)) + math.exp(-lam * len(U2n))
cost_ratio = 2 - f                                         # tests to reject both, against one member: shared primes reject both
gain = math.log(hit_pair / hit_single) - math.log(cost_ratio)
print(f"hits per test against the single cover: {gain:+.2f} nats (pair hit mass {math.log(hit_pair / hit_single):+.2f}, cost {cost_ratio:.2f} tests per pair)")
