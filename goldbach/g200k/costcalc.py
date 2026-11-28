# expected cost of a g >= Q hit for a cover: digits, rows, raw members per hit, per-member cost at the best cut
import sys, math, json
from math import log, exp, sqrt, erf
from statistics import NormalDist
Phi = NormalDist().cdf; Phiinv = NormalDist().inv_cdf
def cover_rows(path, Q=200000):
    line = next(l for l in open(path) if l.startswith('BEST')).split()[1:]
    cov = [tuple(map(int, t.split(':'))) for t in line]
    sv = bytearray([1]) * Q; sv[0] = sv[1] = 0
    for i in range(2, int(Q ** .5) + 1):
        if sv[i]: sv[i*i::i] = bytearray(len(sv[i*i::i]))
    rows = [q for q in range(3, Q) if sv[q] and all(q % r != a for r, a in cov)]
    return cov, len(rows)
def cost(path, B=1e7, t_test=None, c_s=float(__import__("os").environ.get("C_S", "5e-6")), extra_digits=None):
    cov, R = cover_rows(path)
    pmax = max(r for r, _ in cov)
    lM = sum(math.log10(r) for r, _ in cov) + math.log10(2)
    d = lM + 8                                   # rough digits of the hit, refined below
    for _ in range(3):
        lnN = d * log(10)
        w = log(pmax) / log(B); pB = 1.78107 * log(B) / lnN
        beta = -log(1 - pB); sig = sqrt(R * w * (1 - w)); s = beta * sig
        Ev = exp(R * log(1 - w * pB) + 0.5 * beta ** 2 * sig ** 2 * 0)    # (1 - w p)^R is exact for a binomial a
        bits = d * 3.3219
        L = 1
        while 52 * L - 12 < bits: L += 1
        tt = t_test if t_test else {20: 36e-6, 21: 46e-6, 22: 70e-6, 23: 85e-6, 24: 95e-6, 25: 100e-6, 26: 105e-6}.get(L, 120e-6)
        T = tt / pB
        best = None
        for f in [x / 1000 for x in range(1, 300)]:
            h = Phi(Phiinv(f) + s)
            c = (c_s + f * T) / h
            if best is None or c < best[0]: best = (c, f, h)
        c, f, h = best
        kh = 1 / (Ev * h)
        d = lM + math.log10(kh)
    print(f"{path}: {len(cov)} moduli to {pmax}, {R} rows, log10 M {lM:.1f}; at ~{d:.1f} digits: p_B {pB:.4f}, s {s:.2f}, "
          f"raw members/hit 10^{-math.log10(Ev):.2f}; best cut f {f:.3f} (h {h:.3f}): {1e3 * c:.2f} ms per raw member, "
          f"{c / Ev / 3600:.1f} CPU-hours per hit; first found hit near k = 10^{math.log10(kh):.2f} (L = {L}, test {1e6 * tt:.0f} us)")
for p in sys.argv[1:]:
    cost(p)
