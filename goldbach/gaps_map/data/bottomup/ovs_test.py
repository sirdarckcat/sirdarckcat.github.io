# Overshoot test: after a hit at design level Q (all odd primes p < Q have N - p composite), the number u of 'alive' rows (primes q in [Q, g) with N - q coprime to all odd r <= R)
# that the member survives before its first prime row g is geometric: P(u >= m) = (1 - pi)^m, pi = 2 prod_{3<=r<=R} r/(r-1) / ln N.  Exact hits of the miniature, brute force.
import numpy as np, math, sys
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
fn = sys.argv[1]; Q = int(sys.argv[2])
H = np.array([list(map(int, l.split())) for l in open(fn)], dtype=np.int64); N = H[:, 0]; G = H[:, 1]
P = primes_upto(400000); P = P[P > 2]
print('%s: %d hits at Q = %d; g from %d to %d, median %d' % (fn, len(H), Q, G.min(), G.max(), int(np.median(G))))
for R in (23, 47, 97, 199):
    rs = [int(r) for r in primes_upto(R) if r > 2]; c = 2 * np.prod([r / (r - 1) for r in rs])
    us, pis = [], []
    for n, g in zip(N, G):
        rows = P[(P >= Q) & (P < g)]
        ok = np.ones(len(rows), bool)
        for r in rs: ok &= ((n - rows) % r != 0)
        us.append(int(ok.sum())); pis.append(c / math.log(n))
    us = np.array(us); pis = np.array(pis); mean_exp = ((1 - pis) / pis); var_exp = (1 - pis) / pis ** 2
    v = (1 - pis) ** us * (1 - pis / 2)       # mid-PIT, uniform(0,1) under the model
    z = (us.sum() - mean_exp.sum()) / math.sqrt(var_exp.sum())
    print('  R = %3d: mean pi %.3f | overshoot rows: observed mean %.2f, model mean %.2f, ratio %.2f +- %.2f (z = %+.2f) | mid-PIT mean %.3f (0.5, se %.3f)' %
          (R, pis.mean(), us.mean(), mean_exp.mean(), us.sum() / mean_exp.sum(), math.sqrt(var_exp.sum()) / mean_exp.sum(), z, v.mean(), 0.2887 / math.sqrt(len(v))))
