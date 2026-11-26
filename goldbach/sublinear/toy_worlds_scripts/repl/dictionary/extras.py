import math, numpy as np, sympy, random
from common import setup
rows, cov, N0, M, K = setup()
rows_a = np.array(rows)
P = 0.024
# ---- (A) multiplicative ("F_1") tie: Stab(N) in Aut(N_{>0}, x) acts transitively on the primes not dividing N
LIM = 200000
sv = np.ones(LIM + 1, dtype=bool); sv[:2] = False
for i in range(2, int(LIM ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
pr = [int(p) for p in np.nonzero(sv)[0] if p > 2]
bad = []
for N in range(8, LIM + 1, 2):
    yes = no = False
    for q in pr:
        if q >= N - 1: break
        if N % q == 0: continue
        if sv[N - q]: yes = True
        else: no = True
        if yes and no: break
    if not (yes and no): bad.append(N)
print(f"(A) even N in [8, {LIM}]: N has primes q, q' not dividing N, q, q' < N - 1, with N - q prime and N - q' composite, except for N in {bad}")
# ---- (B) square targets N = M^2: classes restricted to squares, room halved
allp = np.array(list(sympy.primerange(3, 200000)))
def greedy(primes, squares_only):
    alive = np.ones(len(allp), dtype=bool); alive[np.isin(allp, primes)] = True
    for r in primes:
        res = allp[alive] % r
        cnt = np.bincount(res, minlength=r)
        cand = sorted(set((x * x) % r for x in range(1, r))) if squares_only else range(1, r)
        a = max(cand, key=lambda c: cnt[c])
        alive &= (allp % r) != a
    return int(alive.sum())
odd = list(sympy.primerange(3, 2000))
def take(room_nats):
    s = math.log(2); out = []
    for r in odd:
        if s + math.log(r) > room_nats: break
        s += math.log(r); out.append(r)
    return out, s
full, sf = take(200 * math.log(10) - 16.9)
half, sh = take(100 * math.log(10) - 16.9 / 2)     # M < 10^100, same number of members in the window (2^24.35 values of M)
g_full = greedy(full, False); g_half_sq = greedy(half, True); g_half = greedy(half, False)
print(f"(B) greedy covers, rows q < 200000 left: {len(full)} primes (to {full[-1]}), any classes: {g_full}; {len(half)} primes (to {half[-1]}), any classes: {g_half}; the same primes, square classes only (N = M^2): {g_half_sq}")
print(f"    exponent of N = M^2 against the generic design, greedy against greedy: {P * (g_half_sq - g_full):+.1f} nats (window of M of e^8.45 members: a further -8.45 nats of members; with the full window of e^16.9 values of M the cover has {len(take(100 * math.log(10) - 16.9)[0])} primes)")
# ---- (C) multiplicative families: room of the S-units below 10^200
def lnpsi(lnx, y):
    ps = [int(p) for p in sympy.primerange(2, y + 1)]
    f = lambda a: sum(math.log(p) / (p ** a - 1) for p in ps) - lnx
    lo, hi = 1e-6, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0: lo = mid
        else: hi = mid
    a = (lo + hi) / 2
    lz = -sum(math.log(1 - p ** -a) for p in ps)
    phi2 = sum(p ** a * math.log(p) ** 2 / (p ** a - 1) ** 2 for p in ps)
    return a * lnx + lz - math.log(a * math.sqrt(2 * math.pi * phi2)), a
for y in (463, 2000, 10 ** 4, 10 ** 5):
    v, a = lnpsi(200 * math.log(10), y)
    print(f"(C) ln #(integers below 10^200 with all prime factors <= {y}) = {v:.1f} nats (saddle point, alpha = {a:.3f}); all integers: 460.5")
# ---- (D) a multiplicative pin (the quadratic character of N at r) against an additive pin (the class of N at r)
print("(D) later prime r | rows in the best class, mean class | additive pin: nats gained, per nat of room (ln r) | |sum over rows of (q|r)| | character pin: nats gained, per nat of room (ln 2)")
ra = []; rm = []
for r in sympy.primerange(467, 1000):
    cnt = np.bincount(rows_a % r, minlength=r)[1:]
    best = cnt.max(); mean = len(rows) / (r - 1)
    add = P * (best - mean)
    S = sum(sympy.jacobi_symbol(int(q), r) for q in rows)
    mul = P * abs(S) / r
    ra.append(add / math.log(r)); rm.append(mul / math.log(2))
    if r < 500 or r > 980: print(f"    {r} | {best}, {mean:.2f} | {add:.3f}, {add / math.log(r):.4f} | {abs(S)} | {mul:.4f}, {mul / math.log(2):.4f}")
print(f"    primes 467 to 997: mean rate of an additive pin {np.mean(ra):.4f} nats per nat; of a quadratic-character pin {np.mean(rm):.4f} nats per nat (before its fixed price: N = c M^2 halves the room)")
