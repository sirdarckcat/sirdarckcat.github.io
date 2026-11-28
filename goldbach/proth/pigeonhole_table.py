"""Rigorous worst-case (pigeonhole) coverable count vs what greedy achieves.
T_pig(x): the largest t such that ANY set of t odd primes is fully covered by
choosing, for each odd prime r <= x in increasing order, a best class: the
best non-zero class always holds >= ceil((t-1)/(r-1)) of the t survivors
(at most one survivor is r itself), and >= 1 while t >= 1."""
import math, numpy as np

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

P = primes_upto(2_000_000)
odd = [int(p) for p in P[1:]]

def survives(t, x):
    for r in odd:
        if r > x or t == 0: break
        t -= max(1, -(-(t - 1) // (r - 1)))
    return max(t, 0)

def T_pig(x):
    lo, hi = 0, 10 ** 9
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if survives(mid, x) == 0: lo = mid
        else: hi = mid - 1
    return lo

def nth_prime_upper(k):   # crude p_k via PNT inversion (only for display)
    if k < 6: return [2,3,5,7,11,13][k]
    n = k
    return n * (math.log(n) + math.log(math.log(n)) - 1 + (math.log(math.log(n)) - 2) / math.log(n))

C2 = 0.6601618158468696; eg = math.exp(0.5772156649015329)
print("constant e^gamma/(2 C2) =", eg / (2 * C2))
rows = [(443, 1e4), (2393, 1e5), (15083, 1e6), (17431, 1.2e6), (26713, 2e6), (102983, 1e7), (755137, 1e8)]
print(f"{'x':>8} {'theta(x)':>10} {'T_pig':>9} {'Q_pig':>10} {'Qpig/(x ln x)':>14} {'Q_greedy':>10} {'Qg/(x ln x)':>12} {'Qg/(x ln^2 x)':>14}")
for x, Qg in rows:
    th = sum(math.log(r) for r in odd if r <= x) + math.log(2)
    t = T_pig(x)
    Qp = nth_prime_upper(t + 1)
    print(f"{x:8d} {th:10.1f} {t:9d} {Qp:10.0f} {Qp / (x * math.log(x)):14.3f} {Qg:10.0f} {Qg / (x * math.log(x)):12.2f} {Qg / (x * math.log(x) ** 2):14.3f}")
