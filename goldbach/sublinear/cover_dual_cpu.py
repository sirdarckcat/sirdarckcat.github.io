#!/usr/bin/env python3
"""What the luck of cover_dual.txt costs on a processor: CPU-hours per hit at each size, tested plainly and with selection.

    python3 cover_dual_cpu.py [log10 B = 9] < cover_dual.txt

A member of a cover has `rows` numbers N - q left by the cover.  A sieve by the primes from the largest modulus x up to B
leaves S of them, S close to Poisson with mean mu = rows ln x/ln B, and each of those is prime with chance p' = p ln B/ln x
(so p' mu = p rows = E).  The member is a hit when all S are composite: chance (1 - p')^S.  Base-2 Fermat tests run until
one passes: (1 - (1 - p')^S)/p' tests on average, each t(d) (measured here with gmpy2, one core).

  plain:      every member is tested.               cost per hit = [c_sieve + c_tests] e^E
  selection:  only members with S <= tau are tested; cost per hit = [c_sieve + sum_{S<=tau} P(S) tests(S) t] / sum_{S<=tau} P(S) (1-p')^S,
              smallest over tau.  Hits have S centred at mu - E, so the cut keeps most hits while it discards most members.

c_sieve = rows (ln ln B - ln ln x) marks per member at 3 ns a mark (an assumption: a store that stays in cache; the set-up of
rows pi(B) residues per cover is left out, it is small next to the rest whenever a cover is used for 10^7 members or more).
"""
import sys, math
T_MS = [(200, 0.106), (250, 0.198), (300, 0.295), (350, 0.484), (400, 0.659), (500, 1.114), (600, 2.136), (800, 4.272),
        (1000, 11.63), (1200, 15.55), (1500, 29.94), (2000, 50.73), (2480, 93.70), (4000, 300.0)]   # last entry extrapolated
MARK = 3e-9
def t_test(d):
    for (a, ta), (b, tb) in zip(T_MS, T_MS[1:]):
        if d <= b: return 1e-3 * ta * (tb / ta) ** (math.log(d / a) / math.log(b / a))
    return 1e-3 * T_MS[-1][1] * (d / T_MS[-1][0]) ** 2.5
def cost(rows, p, x, d, lnB):
    E = p * rows; pp = p * lnB / math.log(x); mu = E / pp; t = t_test(d)
    cs = rows * (math.log(lnB) - math.log(math.log(x))) * MARK
    plain = (cs + (1 - math.exp(-E)) / pp * t) * math.exp(E)
    # Poisson weights around the mean, in logs
    best = (float("inf"), 0, 0.0); num = cs; den = 0.0
    lo = max(0, int(mu - 12 * math.sqrt(mu) - 20))
    logP = lambda S: -mu + S * math.log(mu) - math.lgamma(S + 1)
    for S in range(lo, int(mu + 12 * math.sqrt(mu)) + 20):
        w = math.exp(logP(S)); q = (1 - pp) ** S
        num += w * (1 - q) / pp * t; den += w * q
        if den > 0 and num / den < best[0]: best = (num / den, S, den * math.exp(E))
    return E, pp, mu, t, plain, best
if __name__ == "__main__":
    lnB = (float(sys.argv[1]) if len(sys.argv) > 1 else 9.0) * math.log(10)
    print(f"# cover_dual_cpu.py, sieve to 10^{lnB / math.log(10):.0f}: CPU-hours per hit from the rows of cover_dual.txt")
    print("Q | digits | rows | log10 members | p' after the sieve | mean survivors | ms per test | plain: CPU-hours per hit | selection: CPU-hours | cut at (S - mu)/sd | share of hits kept | members sieved per hit, log10")
    for l in sys.stdin:
        f = [a.strip() for a in l.split("|")]
        if len(f) < 11 or not f[0].isdigit() or "nan" in f[9]: continue
        Q, d, x, rows, p = int(f[0]), int(f[1]), int(f[3]), max(float(f[6]), float(f[7])), float(f[8])
        E, pp, mu, t, plain, (sel, tau, kept) = cost(rows, p, x, d, lnB)
        print(f"{Q} | {d} | {rows:.0f} | {E / math.log(10):.2f} | {pp:.4f} | {mu:.0f} | {1e3 * t:.2f} | {plain / 3600:.3g} | {sel / 3600:.3g} | {(tau - mu) / math.sqrt(mu):+.1f} | {kept:.3f} | {(E - math.log(kept)) / math.log(10):.2f}")
