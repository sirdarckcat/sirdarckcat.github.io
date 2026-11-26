#!/usr/bin/env python3
"""What the luck of the fixed-gap game costs on a processor: CPU-hours per hit, every member tested and only the emptiest.

    python3 cover_dual_cpu.py rows p x digits [log10 B = 7] [microseconds per test] [microseconds of sieve per member]
    python3 cover_dual_cpu.py table                  the sizes of the README, with the covers found and the kernels at hand

A member of a cover has `rows` numbers N - q left by the cover.  A sieve by the primes from the largest modulus x up to B
leaves each with chance w = ln x/ln B, so the survivors S are binomial (rows, w) (the Opus session measured sd(S) =
0.69 sqrt(mean) at B = 10^7, which is sqrt(1 - w); a first version of this file had them Poisson and overstated what the
cut gains).  A survivor is prime with chance p' = p/w, p = 2 prod r/(r-1) / ln N; the member is a hit when all S are
composite, chance (1 - p')^S, on average (1 - p)^rows = e^-E.  Base-2 Fermat tests run until one passes:
(1 - (1 - p')^S)/p' tests on average.

  every member tested:  cost per hit = [c_sieve + c_tests] e^E
  only the emptiest:    members with S <= tau are tested; cost per hit =
                        [c_sieve + sum_{S<=tau} P(S) tests(S) t] / sum_{S<=tau} P(S) (1 - p')^S, smallest over tau.

Test times: gmpy2 on one core here (0.106 ms at 200 digits ... 51 ms at 2,000), or the uarch session's fmw kernel
(AVX-512 IFMA, 8 numbers at a time; 31.8 microseconds at 1,028 bits here, 105.7 at 1,340 bits there).  Sieve: measured here with
that session's sieve200 on 1,026 rows, windows of 2^20 members: 3.9, 5.6 and 20.5 microseconds a member at B = 10^6, 10^7,
10^8 on a loaded machine (about 3 at 10^7 on a free one), in proportion to the rows.
"""
import sys, math
T_MS = [(200, 0.106), (250, 0.198), (300, 0.295), (350, 0.484), (400, 0.659), (500, 1.114), (600, 2.136), (800, 4.272),
        (1000, 11.63), (1200, 15.55), (1500, 29.94), (2000, 50.73), (2480, 93.70)]
def t_gmpy2(d):
    for (a, ta), (b, tb) in zip(T_MS, T_MS[1:]):
        if d <= b: return 1e-3 * ta * (tb / ta) ** (math.log(d / a) / math.log(b / a))
    return 1e-3 * T_MS[-1][1] * (d / T_MS[-1][0]) ** 2.5
def sieve_us(rows, log10B):
    pts = [(6, 3.9), (7, 5.6), (8, 20.5), (9, 60.0)]
    for (a, ua), (b, ub) in zip(pts, pts[1:]):
        if log10B <= b: return (ua * (ub / ua) ** ((log10B - a) / (b - a))) * rows / 1026
    return pts[-1][1] * rows / 1026
def cost(rows, p, x, lnB, cs, t):
    w = math.log(x) / lnB; pp = p / w; E = -rows * math.log(1 - p)
    mu = rows * w; sd = math.sqrt(rows * w * (1 - w))
    logP = lambda S: math.lgamma(rows + 1) - math.lgamma(S + 1) - math.lgamma(rows - S + 1) + S * math.log(w) + (rows - S) * math.log(1 - w)
    plain = (cs + (1 - math.exp(-E)) / pp * t) * math.exp(E)
    num = cs; den = 0.0; frac = 0.0; best = None
    for S in range(max(0, int(mu - 12 * sd)), min(rows, int(mu + 12 * sd)) + 1):
        pr = math.exp(logP(S)); q = (1 - pp) ** S
        num += pr * (1 - q) / pp * t; den += pr * q; frac += pr
        if best is None or num / den < best[0]: best = (num / den, (S - mu) / sd, frac, den * math.exp(E))
    return E, pp, mu, sd, plain, best
def line(name, rows, p, x, d, log10B, t, cs=None):
    cs = sieve_us(rows, log10B) * 1e-6 if cs is None else cs
    E, pp, mu, sd, plain, (c, cut, frac, kept) = cost(rows, p, x, log10B * math.log(10), cs, t)
    return (f"{name} | {rows} | {E / math.log(10):.2f} | 10^{log10B:g} | {1e3 * t:.3f} | {mu:.0f}, {sd:.1f} | {plain / 3600:.3g} | {c / 3600:.3g} | "
            f"{cut:+.1f} | {frac:.4f} | {kept:.3f} | {(E - math.log(kept)) / math.log(10):.2f}")
HEAD = "case | rows | log10 members per hit | sieve to | ms per test | survivors: mean, sd | every member tested: CPU-hours per hit | only the emptiest: CPU-hours | cut, sd below the mean | share of members tested | share of hits kept | log10 members sieved per hit"
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "table":
        print("# cover_dual_cpu.py table. 25 November 2026.  p from cover_dual.txt; rows: the recursion's floor and the covers found"); print(HEAD)
        FMW = {300: 31.8e-6, 350: 60e-6, 400: 105.7e-6}       # 350: between the two measured sizes
        for d, x, p, floor_rows, found in ((400, 941, 0.01330, 943, 1010), (350, 823, 0.01491, 1050, 1113), (300, 701, 0.01701, 1168, 1218), (260, 607, 0.01918, 1285, None)):
            for label, rows in (("floor", floor_rows), ("found", found)):
                if rows is None: continue
                print(line(f"gap 200,000, {d} digits, {label}, gmpy2", rows, p, x, d, 7, t_gmpy2(d)))
                if d in FMW: print(line(f"gap 200,000, {d} digits, {label}, fmw", rows, p, x, d, 7, FMW[d]))
        for d, x, p, floor_rows, found in ((2480, 5791, 0.00271, 1683, 2524), (2190, 5113, 0.00300, 2039, 2595), (2000, 4657, 0.00327, 2315, 2829), (1500, 3527, 0.00422, 3130, None)):
            for label, rows in (("floor", floor_rows), ("found so far", found)):
                if rows is None: continue
                print(line(f"gap 1,000,000, {d} digits, {label}, gmpy2", rows, p, x, d, 9, t_gmpy2(d)))
        sys.exit(0)
    rows, p, x, d = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    log10B = float(sys.argv[5]) if len(sys.argv) > 5 else 7.0
    t = float(sys.argv[6]) * 1e-6 if len(sys.argv) > 6 else t_gmpy2(d)
    cs = float(sys.argv[7]) * 1e-6 if len(sys.argv) > 7 else None
    print(HEAD); print(line(f"{d} digits", rows, p, x, d, log10B, t, cs))
