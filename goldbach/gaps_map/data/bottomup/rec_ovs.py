# Exact overshoot test on the record holders: N_k is a hit at level p_{k-1} (every odd prime <= p_{k-1} has N_k - p composite) and its overshoot is the number u of
# alive rows (primes q with p_{k-1} < q < p_k and N_k - q coprime to all odd r <= R) before the prime row p_k.  Under the model P(u >= m) = (1 - pi)^m,
# pi = 2 prod_{3<=r<=R} r/(r-1)/ln N_k.  The mid-PIT (1 - pi)^u (1 - pi/2) is uniform(0,1).
import numpy as np, math
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
recs = [tuple(map(int, l.split())) for l in open('records.txt')]
P = primes_upto(20000); P = P[P > 2]
for R in (23, 47, 97):
    rs = [int(r) for r in primes_upto(R) if r > 2]; c = 2 * np.prod([r / (r - 1) for r in rs])
    us, pis, ks = [], [], []
    for i in range(1, 67):
        k, N, p = recs[i]; kp, Np, pp = recs[i - 1]
        if N < 1e6: continue
        rows = P[(P > pp) & (P < p)]
        ok = np.ones(len(rows), bool)
        for r in rs: ok &= ((N - rows) % r != 0)
        us.append(int(ok.sum())); pis.append(c / math.log(N)); ks.append(k)
    us = np.array(us); pis = np.array(pis); ks = np.array(ks)
    mean_exp = (1 - pis) / pis; var_exp = (1 - pis) / pis ** 2; v = (1 - pis) ** us * (1 - pis / 2)
    z = (us.sum() - mean_exp.sum()) / math.sqrt(var_exp.sum())
    print('R = %3d: %d records (N >= 1e6): overshoot rows observed %d, model %.1f, ratio %.2f +- %.2f (z = %+.2f); mid-PIT mean %.3f (0.5, se %.3f); first half %.3f, second half %.3f' %
          (R, len(us), us.sum(), mean_exp.sum(), us.sum() / mean_exp.sum(), math.sqrt(var_exp.sum()) / mean_exp.sum(), z, v.mean(), 0.2887 / math.sqrt(len(v)), v[:len(v) // 2].mean(), v[len(v) // 2:].mean()))
