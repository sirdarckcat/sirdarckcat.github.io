import numpy as np, math
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
x = 463; P = [int(p) for p in primes_upto(x)]
def covers(y):
    alive = np.ones(y, bool); n = np.arange(1, y + 1)
    for p in P:
        b = np.bincount(n[alive] % p, minlength=p); c = int(b.argmax()); alive &= (n % p != c)
        if not alive.any(): return True
    return not alive.any()
lo, hi = 100, 8000
while lo < hi - 1:
    mid = (lo + hi) // 2
    if covers(mid): lo = mid
    else: hi = mid
print('greedy: one class mod each prime <= 463 covers 1..y for y =', lo, '(x ln x = %.0f)' % (x * math.log(x)))
l2 = math.log(math.log(x)); l3 = math.log(l2)
print('ln x = %.3f, ln2 x = %.3f, ln3 x = %.3f' % (math.log(x), l2, l3))
print('x ln x/(ln2 x ln3 x) = %.0f ; Freiberg constant bound c < 1/(800 e^gamma) = %.2e -> guaranteed length ~ %.1f' % (x * math.log(x) / (l2 * l3), 1 / (800 * math.exp(0.5772156649)), x * math.log(x) / (l2 * l3) / (800 * math.exp(0.5772156649))))
# FGKMT smallness condition (4.1): delta <= (kappa^A/(C0 exp(A D)))^(10^(m+2)); Corollary 4 uses delta = x^(-1/20)
for (r, m, kappa, D) in ((1, 1, 0.5, 1.0), (3, 1, 0.5, 1.0), (3, 2, 0.5, 1.0)):
    A = 2 * r * m + 1; lg = 10 ** (m + 2) * (A * math.log(1 / kappa) + A * D)         # -ln of the bound with C0 = 1 (a lower bound on the requirement)
    print('r=%d m=%d kappa=%.1f D=%.0f: A=%d, ln(1/delta) >= %.2e -> x^(1/20) = 1/delta needs ln x >= %.2e (x = 463 has ln x = 6.1)' % (r, m, kappa, D, A, lg, 20 * lg))
