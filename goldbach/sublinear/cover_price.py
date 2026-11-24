#!/usr/bin/env python3
"""The counting law for complete covers from a price recursion, with nothing fitted.

    python3 cover_price.py            the constant of the law at the sizes measured, and where complete covers end
    python3 cover_price.py ends big   the same with the ends up to x = 100,000 (ten minutes)

Count the class vectors that strike every odd prime below Q modulus by modulus, smallest first.  If V(s, A) is the
logarithm of the number of ways the moduli from s on can finish when A rows are alive, then
V(s, A) = ln sum over the classes c of exp(V(s+, A - K_c)), K_c the alive rows in class c.  With V = const - p A
(a price p per alive row) this is

    p_s = p_{s+} - kappa_s(p_{s+}) / (s - 1),       mu kappa_s(p) = ln E exp(p K),   mu = A/(s - 1).

Class counts with variance v times the mean: kappa = (exp(v p) - 1)/v.  The dispersion index v follows from the
Hardy-Littlewood count of prime pairs: for two primes in one class of s the chance that both are alive after the
smaller moduli, summed over the pairs, is the Poisson value at leading order, and the second-order term of the
average of singular series (-(H/2) ln H in sum_{h<=H} (H - h) S(h), Montgomery and Soundararajan) gives

    v_s = 1 - 6 phi(s) (s/(s - 1)) (pi(Q)/Q) ln(Q/(6 s)),       phi(s) = prod over odd primes t < s of (1 - 1/(t - 1)).

The price before the first modulus is the largest for which the recursion can be carried through every modulus (the
price after the last one is then as large as it can be: a row left alive at the end is not allowed).  The loss is
that price times pi(Q):  ln g0(Q) = sum ln(s - 1) - p_start pi(Q).
"""
import math, sys, bisect
from scipy.special import expi

def sieve(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(3, n + 1) if s[i]]

P = sieve(2000000)

def odd_primes_below(Q):
    return bisect.bisect_left(P, Q) if Q <= P[-1] else expi(math.log(Q)) - 1.0

def dispersion(s, phi, Q, piQ):
    return min(1.0, max(0.02, 1 - 6 * phi * (s / (s - 1)) * (piQ / Q) * math.log(max(Q / (6 * s), 1.0))))

def start_price(mods, phis, Q, poisson=False):
    piQ = odd_primes_below(Q)
    vs = [1.0 if poisson else dispersion(s, phi, Q, piQ) for s, phi in zip(mods, phis)]
    def run(p):
        for s, v in zip(mods, vs):
            top = math.log(s - 1) / v                       # where p - kappa(p)/(s-1) is largest
            if p > top - math.expm1(v * top) / (v * (s - 1)): return False
            lo, hi = p, top
            for _ in range(50):
                mid = 0.5 * (lo + hi)
                if mid - math.expm1(v * mid) / (v * (s - 1)) < p: lo = mid
                else: hi = mid
            p = 0.5 * (lo + hi)
        return True
    lo, hi = 0.0, 5.0
    for _ in range(45):
        mid = 0.5 * (lo + hi)
        if run(mid): lo = mid
        else: hi = mid
    return lo, piQ, vs

def setup(x):
    mods = [p for p in P if p <= x]; phis = []; phi = 1.0
    for s in mods: phis.append(phi); phi *= 1 - 1 / (s - 1)
    return mods, phis

if __name__ == "__main__":
    measured = [(463, 10000, 171.78), (463, 14000, 61.69), (997, 15000, 640.1), (997, 25000, 435.6), (997, 38000, 153.6),
                (2999, 50000, 2160.1), (2999, 100000, 1342.5), (9973, 100000, 8709.1), (9973, 300000, 6313.2)]
    print("x | Q | loss measured (theta - ln g0) | loss by the recursion | by the first moment (rows independent) | constant c' = loss ln^2 x/(pi(Q) ln Q): measured, recursion, first moment")
    for x, Q, S in measured:
        mods, phis = setup(x); th_all = sum(math.log(s) for s in mods)
        p, piQ, _ = start_price(mods, phis, Q); first = -math.log(1 - phis[-1] * (1 - 1 / (mods[-1] - 1)))   # a row is left by random nonzero classes with probability prod (1 - 1/(s-1))
        k = math.log(x) ** 2 / (piQ * math.log(Q)); junk = th_all - sum(math.log(s - 1) for s in mods)      # vectors with a zero class are not complete covers
        print(f"{x} | {Q} | {th_all - S:.1f} | {p * piQ + junk:.1f} | {first * piQ + junk:.1f} | {(th_all - S) * k:.3f}, {(p * piQ + junk) * k:.3f}, {(first * piQ + junk) * k:.3f}")
    xs = (73, 107, 199, 463, 997, 2999, 9973) + ((30000, 100000) if "big" in sys.argv else ())
    print("\nx | moduli | end of complete covers by the recursion | / (x ln^2 x) | by the first moment | / (x ln^2 x)")
    for x in xs:
        mods, phis = setup(x); th = sum(math.log(s - 1) for s in mods); out = []
        first = -math.log(1 - phis[-1] * (1 - 1 / (mods[-1] - 1)))
        for pois in (False, True):
            lo, hi = float(x), 40.0 * x * math.log(x) ** 2
            for _ in range(40):
                mid = math.sqrt(lo * hi)
                if pois: loss = first * odd_primes_below(mid)
                else: p, piQ, _ = start_price(mods, phis, mid); loss = p * piQ
                if loss < th: lo = mid
                else: hi = mid
            out.append(lo)
        sc = x * math.log(x) ** 2
        print(f"{x} | {len(mods)} | {out[0]:,.0f} | {out[0] / sc:.3f} | {out[1]:,.0f} | {out[1] / sc:.3f}", flush=True)
