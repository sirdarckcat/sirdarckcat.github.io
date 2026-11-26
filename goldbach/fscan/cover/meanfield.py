# Mean-field prediction of the smallest residual of a cover, refined: class counts of primes modulo m are less spread
# than Poisson by the factor d(m) = min(1, ln m / ln Q) (the Barban-Davenport-Halberstam / Montgomery-Hooley law).
# For modulus r_j the relevant m is the product of the moduli used so far including r_j.
import math, sys
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
def D(x, a):
    if x >= 1: return -math.log(a)
    return x * math.log(x / a) + (1 - x) * math.log((1 - x) / (1 - a))
def predict(nrows, Q, moduli, power=1.0):
    alpha = 1.0; lnm = 0.0; lnQ = math.log(Q)
    for r in sorted(moduli):
        lnm += math.log(r)
        d = min(1.0, lnm / lnQ) ** power
        N = nrows / (r - 1); target = d * math.log(r - 1)
        if alpha >= 1 - 1e-12: alpha -= 1 / (r - 1); continue
        lo, hi = alpha, 1.0
        if N * D(1.0, alpha) <= target: x = 1.0
        else:
            for _ in range(80):
                mid = (lo + hi) / 2
                if N * D(mid, alpha) <= target: lo = mid
                else: hi = mid
            x = lo
        alpha -= x / (r - 1)
    return nrows * alpha
P = primes_upto(200000)
c3 = [p for p in P if 3 <= p <= 439] + [467, 487, 491, 683]
odd = [p for p in P if p >= 3]
def rows(Q): return sum(1 for p in P if 3 <= p < Q)
cases = [("13 moduli Q=10007", 10007, odd[:13], 186)] + [(f"88 moduli Q={Q}", Q, c3, b) for Q, b in ((122000, 851), (130000, 921), (140000, 1011), (150000, 1093), (160000, 1185))] + \
        [(f"first {n} Q=122000", 122000, odd[:n], b) for n, b in ((86, 870), (88, 856), (90, 842))]
for power in (1.0, 2.0):
    print(f"dispersion exponent {power}:")
    for name, Q, mods, best in cases:
        p = predict(rows(Q), Q, mods, power)
        print(f"   {name:24s} rows {rows(Q):6d}  predicted {p:7.1f}  optimum found {best:5d}  ratio {p/best:.3f}")
