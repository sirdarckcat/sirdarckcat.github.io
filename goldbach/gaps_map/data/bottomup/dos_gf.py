# Density of states of covers near the optimum, first approximation: single-prime moves from the best cover, costs additive across primes.
# delta(r, c') = |U_r| - |A_r & class c'|, U_r = rows killed only by r, A_r = rows alive if the pin at r were removed.
import numpy as np, math, sys, time
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rows = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]
cls = np.load(sys.argv[1] if len(sys.argv) > 1 else '../lattice/cls_sa_11.npy')
cnt = np.zeros(len(rows), np.int32)
for p, c in zip(mods, cls): cnt[(rows % p) == c] += 1
n0 = int((cnt == 0).sum()); print('rows', len(rows), 'moduli', len(mods), 'alive rows of this cover', n0)
# per prime: spectrum of single-move costs
coef = {0: 1.0}      # generating function as dict exponent -> count (float, log not needed up to e^40)
spec = []
for p, c in zip(mods, cls):
    inc = (rows % p) == c
    A = (cnt - inc) == 0                 # alive if the pin at p were removed
    U = int((A & inc).sum())
    b = np.bincount(rows[A] % p, minlength=p)            # alive-if-removed rows per class
    d = U - b                            # cost of moving the pin to class c' (c' != c)
    d = np.delete(d, c)
    spec.append((p, U, d))
    if d.min() < 0: print('  local move gains at p=%d: %d' % (p, d.min()))
D = 120
G = np.zeros(D + 1); G[0] = 1.0
for p, U, d in spec:
    h = np.zeros(D + 1); h[0] = 1.0                                  # stay
    for x in d[d <= D]: h[int(x)] += 1.0
    G = np.convolve(G, h)[:D + 1]
cum = np.cumsum(G)
print('single moves with cost 0, <=1, <=2, <=5, <=10 over all primes:', *[int(sum((d <= t).sum() for _, _, d in spec)) for t in (0, 1, 2, 5, 10)])
print('independent-move estimate of ln #(covers with at most n0 + Delta alive rows):')
for Dl in (0, 1, 2, 3, 5, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100):
    print('   Delta = %3d rows: S = %6.2f nats (slope to next: %.2f nats per row)' % (Dl, math.log(cum[Dl]), (math.log(cum[min(Dl + 5, D)]) - math.log(cum[Dl])) / 5))
need = 19.7
for Dl in range(D + 1):
    if math.log(cum[Dl]) >= need: print('covers needed: e^%.1f = %.1e -> Delta = %d rows, cost %.2f nats of exponent (p = 0.02398)' % (need, math.exp(need), Dl, Dl * 0.02398)); break
