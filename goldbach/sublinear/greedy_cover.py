# How far does a plain greedy choice of classes strike every prime?  For the odd primes r <= x in increasing order take the
# nonzero class holding the most primes below y not yet struck; G(x) = the largest y for which nothing is left (bisection).
#   python3 greedy_cover.py x [x ...]
# Being struck is not exactly monotone in y, so the y found by bisection is a value for which the greedy vector strikes
# everything, not necessarily the largest such value.
import sys, math
import numpy as np
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
def left(x, y, PR, order="up"):
    mods = PR[(PR >= 3) & (PR <= x)]
    if order == "down_tail":                       # small primes first, the upper half in decreasing order
        k = len(mods) // 2; mods = np.concatenate((mods[:k], mods[k:][::-1]))
    T = PR[(PR >= 3) & (PR < y)]
    for r in mods:
        if len(T) == 0: break
        res = T % r
        cnt = np.bincount(res, minlength=r); cnt[0] = 0
        a = int(np.argmax(cnt))
        T = T[res != a]
    return len(T)
C0 = 1.3494
for x in map(int, sys.argv[1:]):
    hi_guess = int(12 * x * math.log(x)) + 100
    PR = primes_upto(hi_guess)
    lo, hi = x, hi_guess
    while left(x, hi, PR) == 0: hi *= 2; PR = primes_upto(hi)
    while hi - lo > max(2, lo // 400):
        mid = (lo + hi) // 2
        if left(x, mid, PR) == 0: lo = mid
        else: hi = mid
    r = lo / (x * math.log(x))
    print(f"x = {x}: greedy strikes every odd prime below about {lo}; ratio to x ln x: {r:.2f}; to 1.349 x ln x: {r / C0:.2f}; ln x / ln ln x = {math.log(x) / math.log(math.log(x)):.2f}", flush=True)
