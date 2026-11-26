# Statement C on a toy that can be solved exactly (research, 25 Nov): the knapsack in Z/P with the real weight tables of the
# 200,000 cover (../covers/q200000_m89.txt, 89 moduli, 1,502 rows), restricted to the first m later primes, in a window of K
# members. Member k (N = N0 + kM, N0 in the middle of the cover's k range) scores
#     S(k) = sum_i w_i(k mod s_i),   w_i(a) = #{rows q : N0 + aM = q (mod s_i)}   (rows struck, repeats counted: the additive form).
# This module builds the tables and the exact scores of the whole window (the scan, i.e. the ground truth).
import math, numpy as np
from sympy import primerange, nextprime

def load_cover(path):
    l = [x for x in open(path) if x.startswith("COVER")][0].split()
    return [tuple(map(int, w.split(":"))) for w in l if ":" in w]

def setup(cover_path, m, K, X=10 ** 200):
    cov = load_cover(cover_path)
    mods = [r for r, _ in cov]; M = 2 * math.prod(mods)
    # N0: N = a_r (mod r) for every modulus, N even
    N0, mod = 0, 2
    for r, a in cov:
        # solve N0 + mod*t = a (mod r)
        t = ((a - N0) * pow(mod, -1, r)) % r; N0 += mod * t; mod *= r
    assert N0 % 2 == 0 and all(N0 % r == a for r, a in cov)
    kmax = (X - N0) // M; k0 = kmax // 2 - K // 2; N0w = N0 + k0 * M          # the window in the middle of the k range
    Q = np.array(list(primerange(3, 200000)), dtype=np.int64)
    alive = np.ones(len(Q), bool)
    for r, a in cov: alive &= (Q % r) != a
    U = Q[alive]
    later = []; s = max(mods)
    while len(later) < m:
        s = nextprime(s)
        if s not in mods: later.append(s)
    W = []
    for s in later:
        Minv = pow(M % s, -1, s); n0 = N0w % s
        a = ((U % s - n0) % s) * Minv % s                                 # N0w + aM = q (mod s)
        W.append(np.bincount(a, minlength=s).astype(np.int64))
    return dict(U=U, later=later, W=W, M=M, N0w=N0w, K=K)

def scan(T):
    """exact scores of every member of the window."""
    K = T["K"]; k = np.arange(K, dtype=np.int64); S = np.zeros(K, np.int16)
    for s, w in zip(T["later"], T["W"]): S += w[k % s].astype(np.int16)
    return S

if __name__ == "__main__":
    T = setup("../covers/q200000_m89.txt", 10, 2 ** 20)
    print(f"rows {len(T['U'])}; later primes {T['later']}")
    for s, w in zip(T["later"], T["W"]):
        print(f"  s = {s}: mean {w.mean():.3f}, var {w.var():.3f}, max {w.max()}, classes at max {int((w == w.max()).sum())}")
