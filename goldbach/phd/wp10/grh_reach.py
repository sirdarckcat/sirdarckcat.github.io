#!/usr/bin/env python3
"""WP10: reach of RH/GRH, and of the remark.pdf toolkit, at this programme's
bottlenecks. Every number quoted in phd/wp10_grh_remark.md is printed here.

    python3 goldbach/phd/wp10/grh_reach.py            # all sections, < 1 min
    python3 goldbach/phd/wp10/grh_reach.py --no-bench # skip modexp timing (C)

A  analytic reach  RH short-interval / GRH progression guarantees vs the
                   window [N-g, N] and the scanned progression of each record
B  sieve floors    linear-sieve exponent s for the 150-digit and Door-1 covers
C  certification   Miller's test (a proof under GRH, Bach 1990) vs ECPP
D  Door-1 lifts    Sherali-Adams/Lasserre sizes; Bonferroni depth needed

Inputs: the committed record.json files and phd/wp9/door1/instance_q122k.json.
Nothing is fitted. Every approximation is chosen to favour RH/GRH (or the
sieve), so each shortfall printed here is a lower bound on the real one.
"""
import argparse
import json
import math
import random
import time
from pathlib import Path

import numpy as np

try:
    import gmpy2

    def powmod(b, e, m):
        return gmpy2.powmod(b, e, m)

    BACKEND = "gmpy2 " + gmpy2.version() + " / GMP " + gmpy2.mp_version()
except ImportError:  # pure-Python fallback, ~3-10x slower at large sizes
    def powmod(b, e, m):
        return pow(b, e, m)

    BACKEND = "python int (install gmpy2 for GMP timings)"

GB = Path(__file__).resolve().parents[2]  # .../goldbach
EULER_GAMMA = 0.5772156649015329
LN10 = math.log(10)


def load(rel):
    with open(GB / rel) as fh:
        return json.load(fh)


def cover_moduli(rec):
    return sorted({int(r) for r, _ in rec["cover"]})


def boost_of(M, moduli):
    """M/phi(M) over the primes dividing M (2 and the cover moduli)."""
    b = 1.0
    for p in [2] + moduli:
        if M % p == 0:
            b *= p / (p - 1)
    return b


# --------------------------------------------------------------------------
# A. Analytic reach
# --------------------------------------------------------------------------
def section_a():
    print("== A. Analytic reach of RH / GRH at the records ==")
    print("RH window: under RH there is a prime in (x - (22/25) sqrt(x) ln x, x]")
    print("  for x >= 4 (Carneiro-Milinovich-Soundararajan 2019, a Guinand-Weil")
    print("  positivity argument). Nothing shorter is guaranteed; a desert needs")
    print("  control of the window [N-g, N].")
    print("GRH progression: pi(x; M, a) = li(x)/phi(M) + O(sqrt(x) log^2 x). Here the")
    print("  error is taken as sqrt(x) with all log factors dropped (generous).")
    rows = [
        ("T(10^5) incumbent", "threshold_150digit_g104527", 7.5e10,
         "full k-round [0, 7.5e10) scanned (RESULTS.md)"),
        ("<10^200 record", "budget_1e200_200digit_g112249", "bound200",
         "all progression terms below 10^200"),
        ("megagap (Game 1)", "megagap_2692digit_g1134871", None,
         "unbounded game; wall is certification (section C)"),
    ]
    out = {}
    for label, d, T, note in rows:
        rec = load(f"records/{d}/record.json")
        N, M, N0 = int(rec["N"]), int(rec["M"]), int(rec["N0"])
        g, k = int(rec["g"]), int(rec["k"])
        assert N == N0 + k * M, f"{d}: N != N0 + k*M"
        mods = cover_moduli(rec)
        lnN = math.log(N)
        log10N = math.log10(N)
        # RH window, in log10, vs the desert length g
        lw = math.log10(22 / 25) + 0.5 * log10N + math.log10(lnN)
        rh_short = lw - math.log10(g)
        print(f"\n[{label}] {rec['digits']} digits, g = {g}, M has "
              f"{len(str(M))} digits, {len(mods)} cover moduli")
        print(f"  RH window (22/25)sqrt(N)lnN = 10^{lw:.1f}  vs  g = 10^"
              f"{math.log10(g):.2f}   -> short by 10^{rh_short:.1f}")
        res = {"digits": rec["digits"], "g": g, "rh_window_log10": lw,
               "rh_short_log10": rh_short}
        if T is not None:
            if T == "bound200":
                T = (10 ** 200 - N0) // M + 1
            T = float(T)
            b = boost_of(M, mods)
            x_log10 = math.log10(N0 + int(T) * M)
            main = T * b / (x_log10 * LN10)  # expected primes among T terms
            err_log10 = 0.5 * x_log10         # sqrt(x), logs dropped
            short = err_log10 - math.log10(main)
            # T at which sqrt(T*M) <= T*b/ln x, i.e. T >= M (ln x / b)^2
            lnx_need = math.log(M) * 2  # x ~ T*M ~ M^2 at the crossover
            t_need_log10 = math.log10(M) + 2 * math.log10(lnx_need / b)
            print(f"  GRH progression ({note}): T = 10^{math.log10(T):.2f}, "
                  f"boost M/phi(M) = {b:.2f}")
            print(f"    expected prime terms per residual = 10^"
                  f"{math.log10(main):.2f}; GRH error >= sqrt(x) = 10^"
                  f"{err_log10:.1f} -> short by 10^{short:.1f}")
            print(f"    GRH bites only for T >= M (ln x/boost)^2 = 10^"
                  f"{t_need_log10:.1f}  (x ~ M^2, i.e. ~{2 * len(str(M))} "
                  f"digits instead of {rec['digits']})")
            res.update({"T_log10": math.log10(T), "boost": b,
                        "grh_short_log10": short,
                        "T_needed_log10": t_need_log10})
        out[label] = res
    return out


# --------------------------------------------------------------------------
# B. Sieve floors
# --------------------------------------------------------------------------
TWO_EG = 2 * math.exp(EULER_GAMMA)


def _simpson(fn, a, b, n=400):
    if b <= a:
        return 0.0
    h = (b - a) / n
    s = fn(a) + fn(b)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * fn(a + i * h)
    return s * h / 3


def F_lin(s):
    """Linear-sieve upper function F(s): exact on (0, 5]; for s > 5 it is
    replaced by its infimum 1 (generous: F bounds the kills from above)."""
    if s <= 3:
        return TWO_EG / s
    if s <= 5:
        return TWO_EG / s * (1 + _simpson(lambda t: math.log(t - 1) / t,
                                          2, s - 1))
    return 1.0


def f_lin(s):
    """Linear-sieve lower function f(s): exact on (0, 6]; for s > 6 it is
    replaced by its supremum 1 (generous: f is the guaranteed residue)."""
    if s <= 2:
        return 0.0
    if s <= 4:
        return TWO_EG * math.log(s - 1) / s
    if s <= 6:
        inner = lambda t: _simpson(lambda u: math.log(u - 1) / u, 2, t - 1,
                                   100) / t
        return TWO_EG / s * (math.log(s - 1) + _simpson(inner, 3, s - 1, 100))
    return 1.0


def sieve_floor(Q, R, D):
    """Best certified floor, as a fraction of pi(Q), from: linear lower-bound
    sieve on the moduli <= z' at level D, minus the kills of every modulus
    r > z' bounded by the upper-bound sieve on primes = a_r (mod r) at level
    D/r (or trivially by their share pi(Q)/(r-1)). Remainder terms and eps
    are dropped and f, F are capped generously, so a real argument can only
    do worse. Only cuts with f(s') > 0 are considered."""
    best = None
    for zp in R:
        sp = math.log(D) / math.log(zp)
        if f_lin(sp) <= 0:
            continue
        V = math.prod(1 - 1 / (r - 1) for r in R if r <= zp)
        kills = 0.0
        for r in R:
            if r <= zp:
                continue
            sr = math.log(D / r) / math.log(zp) if D > r else 0.0
            share = V * F_lin(sr) if sr > 0 else float("inf")
            kills += min(1.0, share) / (r - 1)
        val = V * f_lin(sp) - kills
        if best is None or val > best[0]:
            best = (val, zp, sp, V)
    return best


def section_b():
    print("\n== B. Sieve floors (can a level-of-distribution argument certify a "
          "residual?) ==")
    print("Sifted set: primes q < Q; one class removed mod each cover modulus r;")
    print("dimension kappa = 1. Lower bound X V(z) (f(s) - eps) - R(D) with")
    print("s = ln D / ln z, and f(s) = 0 for s <= 2 (sharp: Selberg's parity")
    print("examples). Levels: D = Q^(1/2), which GRH gives and which")
    print("Bombieri-Vinogradov ALREADY gives unconditionally for sieve sums")
    print("(max over classes included), and D = Q (Elliott-Halberstam and")
    print("beyond; not implied by GRH): the ceiling for any level argument.")
    rec = load("records/threshold_150digit_g104527/record.json")
    inst = load("phd/wp9/door1/instance_q122k.json")
    covers = [("150-digit record cover", int(rec["Q"]), cover_moduli(rec)),
              ("Door-1 instance c1", int(inst["Q"]),
               sorted(int(r) for r in inst["moduli"]))]
    out = {}
    for label, Q, R in covers:
        z = max(R)
        lam = sum(1 / (r - 1) for r in R)
        s_bv = math.log(math.sqrt(Q)) / math.log(z)
        s_eh = math.log(Q) / math.log(z)
        print(f"\n[{label}] Q = {Q}, {len(R)} moduli, z = max r = {z} "
              f"(sqrt(Q) = {math.sqrt(Q):.0f}), kill mass sum 1/(r-1) = "
              f"{lam:.3f}")
        print(f"  one-shot sieve: s(D=Q^1/2) = {s_bv:.3f}, s(D=Q) = "
              f"{s_eh:.3f}  -> both <= 2, f(s) = 0 at every level D <= Q")
        res = {"Q": Q, "z": z, "kill_mass": lam, "s_bv": s_bv, "s_eh": s_eh}
        for name, D in (("Q^1/2 (GRH = BV)", math.sqrt(Q)), ("Q (EH+)", Q)):
            val, zp, sp, V = sieve_floor(Q, R, D)
            n = val * len_primes_below(Q)
            verdict = "vacuous" if val <= 0 else f"floor ~ {n:.0f} residuals"
            print(f"  truncated sieve at level {name:>16}: best cut z' = "
                  f"{zp:>3} (s' = {sp:.2f}), floor = {val:+.4f} pi(Q) "
                  f"-> {verdict}")
            res[name] = {"floor_frac": val, "cut": zp, "s": sp,
                         "floor_count": n}
        out[label] = res
    return out


def len_primes_below(Q):
    s = np.ones(Q, dtype=bool)
    s[:2] = False
    for p in range(2, math.isqrt(Q - 1) + 1):
        if s[p]:
            s[p * p::p] = False
    return int(s.sum())


# --------------------------------------------------------------------------
# C. Certification: Miller's test under GRH vs ECPP
# --------------------------------------------------------------------------
def odd_sieve(n):
    """is_prime for odd numbers 2i+1 <= n (index i)."""
    m = (n - 1) // 2 + 1
    s = np.ones(m, dtype=bool)
    s[0] = False  # 1 is not prime
    for i in range(1, (math.isqrt(n) - 1) // 2 + 1):
        if s[i]:
            p = 2 * i + 1
            s[(p * p - 1) // 2::p] = False
    return s


def time_modexp(digits, reps_min=2, budget=1.5):
    rng = random.Random(20261121 + digits)
    bits = math.ceil(digits * math.log2(10))
    n = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
    e = n - 1
    if "gmpy2" in BACKEND:
        n = gmpy2.mpz(n)
        e = gmpy2.mpz(e)
    reps, t0 = 0, time.perf_counter()
    while reps < reps_min or time.perf_counter() - t0 < budget:
        powmod(3, e, n)
        reps += 1
        if reps >= 200:
            break
    return (time.perf_counter() - t0) / reps


def section_c(bench):
    print("\n== C. Certification: GRH makes Miller's test a proof ==")
    print("Bach (1990): under GRH, an odd n passing the strong test for every")
    print("prime base a < 2 ln^2 n is prime. No certificate results: checking")
    print("the claim means redoing every modexp. Backend:", BACKEND)
    sizes = [150, 200, 2480, 2692, 4000]
    xmax = int(2 * (max(sizes) * LN10) ** 2) + 1
    s = odd_sieve(xmax)
    out = {}
    print(f"\n  {'digits':>6} {'bases<2ln^2n':>13} {'prime bases':>12} "
          f"{'ms/modexp':>10} {'total':>14}")
    for D in sizes:
        lnn = D * LN10
        X = int(2 * lnn * lnn)
        nprime = 1 + int(s[: (X - 1) // 2 + 1].sum())  # +1 for base 2
        t = time_modexp(D) if bench else float("nan")
        tot = nprime * t
        if tot != tot:
            tot_s = "n/a"
        elif tot < 120:
            tot_s = f"{tot:.1f} s"
        elif tot < 2 * 86400:
            tot_s = f"{tot / 3600:.1f} core-h"
        else:
            tot_s = f"{tot / 86400:.0f} core-d"
        print(f"  {D:>6} {X:>13,} {nprime:>12,} {1e3 * t:>10.3f} {tot_s:>14}")
        out[D] = {"bases": X, "prime_bases": nprime, "s_per_modexp": t,
                  "total_core_s": tot}
    print("  repo ECPP reference (SOK s2): minutes to 200 digits; ~2 h at 2,480")
    print("  digits, then verification of a compact certificate in minutes.")
    return out


# --------------------------------------------------------------------------
# D. Door-1 lifts (the 'positivity via determinants' motif)
# --------------------------------------------------------------------------
def esym(vals, K):
    e = [1] + [0] * K
    for v in vals:
        for j in range(K, 0, -1):
            e[j] += e[j - 1] * v
    return e


def section_d():
    print("\n== D. Door-1 lifts: what a positivity hierarchy would have to "
          "solve ==")
    inst = load("phd/wp9/door1/instance_q122k.json")
    R = sorted(int(r) for r in inst["moduli"])
    er = esym(R, 5)  # monomials with k distinct moduli, one class each
    p = [1 / (r - 1) for r in R]
    ep = esym(p, 9)
    exact = 1 - math.prod(1 - x for x in p)
    print(f"  instance: {len(R)} moduli (3..{max(R)}), {sum(R):,} (modulus, "
          f"class) variables, Q = {inst['Q']}")
    print("  degree-k monomials e_k(r):  " + ", ".join(
        f"k={k}: 10^{math.log10(er[k]):.1f}" for k in range(1, 6)))
    print(f"  Lasserre moment matrix side: level 1 = {1 + er[1]:,}; "
          f"level 2 = 10^{math.log10(1 + er[1] + er[2]):.1f}")
    print("  Bonferroni truncations of P(q covered) under the random "
          f"assignment (exact = {exact:.4f}):")
    acc, rows = 0.0, []
    for k in range(1, 10):
        acc += (-1) ** (k + 1) * ep[k]
        kind = "upper" if k % 2 else "lower"
        rows.append((k, kind, acc))
        print(f"    depth {k} ({kind}): {acc:.4f}" +
              ("   <- still >= 1, vacuous" if kind == "upper" and acc >= 1
               else ""))
    first = next(k for k, kind, a in rows if kind == "upper" and a < 1)
    print(f"  first informative odd depth: {first}; a level-{first} lift has "
          f"~10^{math.log10(er[first]):.0f} monomials")
    return {"moduli": len(R), "e_k_log10": [math.log10(er[k])
                                           for k in range(1, 6)],
            "bonferroni": rows, "exact_random_cover": exact,
            "first_informative_depth": first}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--no-bench", action="store_true",
                    help="skip the modexp benchmark in section C")
    ap.add_argument("--json", help="also write all numbers to this file")
    a = ap.parse_args()
    res = {"A": section_a(), "B": section_b(), "C": section_c(not a.no_bench),
           "D": section_d()}
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(res, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
