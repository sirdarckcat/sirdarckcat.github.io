"""Congruence-cover optimizer for Goldbach-desert records.

Goal: an even N with no prime q < Q as a Goldbach summand.  We impose
congruences N == a_r (mod r) for odd primes r: any prime q == a_r (mod r)
then has r | N - q, so it is excluded for every member of the CRT
progression N = N0 + k*M, M = 2*prod(r).  The uncovered ("residual")
primes q must have N - q composite, which we test during a search over k.

Model: each residual complement N - q is odd and coprime to every cover
prime, so it is prime with probability about p = boost / ln N, where
    boost = 2 * prod_{r in cover} r/(r-1).
A value of k succeeds when *all* |U| residual complements are composite,
so successes have density exp(-E) with E = |U| * p, and the expected
first success is k* ~ exp(E).  Total size: digits(N) ~ digits(M) + E/ln10.

We therefore build the greedy path (max effective-coverage per log-cost)
and choose the shortest prefix whose self-consistent E is below the
search budget, then polish with coordinate descent.
"""

import json
import math
import sys

import numpy as np
from sympy import primerange

LN10 = math.log(10)


def _best_residue(r, alive):
    cnt = np.bincount(alive % r, minlength=r)
    a = int(cnt.argmax())
    return a, int(cnt[a])


def _stats(chosen, targets):
    covered = np.zeros(len(targets), dtype=bool)
    boost = 2.0
    logm = math.log(2)
    for r, a in chosen.items():
        covered |= (targets % r) == a
        boost *= r / (r - 1)
        logm += math.log(r)
    return covered, boost, logm


def self_consistent_D(m_digits, n_res, boost):
    """digits(N) ~ m_digits + E/ln10,  E = n_res*boost/(digits(N)*ln10)."""
    ub = n_res * boost
    D = (m_digits + math.sqrt(m_digits ** 2 + 4 * ub / (LN10 * LN10))) / 2
    E = ub / (D * LN10) if D > 0 else 0.0
    return D, E


def build_cover(Q, e_target=16.5, rmax=6000, verbose=True):
    targets = np.array(list(primerange(3, Q)), dtype=np.int64)
    cand = [int(r) for r in primerange(3, rmax)]

    chosen = {}
    covered = np.zeros(len(targets), dtype=bool)
    boost = 2.0
    logm = math.log(2)

    # ---- greedy phase: maximize effective gain per log-cost until E small --
    while True:
        alive = targets[~covered]
        nU = len(alive)
        D, E = self_consistent_D(logm / LN10, nU, boost)
        if E <= e_target or nU == 0:
            break
        best = None
        for r in cand:
            if r in chosen:
                continue
            a, gain = _best_residue(r, alive)
            # effective gain: covering `gain` primes, but boosting the
            # remaining residuals' prime-probability by r/(r-1)
            eff = gain - (nU - gain) / (r - 1)
            if eff <= 0:
                continue
            score = eff / math.log(r)
            if best is None or score > best[0]:
                best = (score, r, a)
        if best is None:
            break
        _, r, a = best
        chosen[r] = a
        boost *= r / (r - 1)
        logm += math.log(r)
        covered |= (targets % r) == a
        if verbose and len(chosen) % 25 == 0:
            print(f"  greedy {len(chosen):4d} congr  M~{logm/LN10:6.1f}d  "
                  f"|U|={int((~covered).sum()):5d}  E={E:6.2f}", flush=True)

    # ---- coordinate descent under the same E ceiling -----------------------
    for _ in range(8):
        improved = False
        for r in sorted(chosen, key=lambda x: -math.log(x)):
            a_old = chosen.pop(r)
            covered, boost, logm = _stats(chosen, targets)
            alive = targets[~covered]
            nU = len(alive)
            # option: stay dropped
            D0, E0 = self_consistent_D(logm / LN10, nU, boost)
            # option: re-add best residue (for r or any unused candidate)
            best = None
            for r2 in cand:
                if r2 in chosen:
                    continue
                a2, gain2 = _best_residue(r2, alive)
                if gain2 == 0:
                    continue
                d2 = (logm + math.log(r2)) / LN10
                b2 = boost * r2 / (r2 - 1)
                D2, E2 = self_consistent_D(d2, nU - gain2, b2)
                if E2 <= e_target and (best is None or D2 < best[0]):
                    best = (D2, r2, a2)
            if E0 <= e_target and (best is None or D0 <= best[0]):
                improved = improved or True  # r dropped for good
                if best is None or D0 <= best[0]:
                    continue
            if best is not None:
                _, r2, a2 = best
                chosen[r2] = a2
                if r2 != r or a2 != a_old:
                    improved = True
            else:
                chosen[r] = a_old
        if not improved:
            break

    covered, boost, logm = _stats(chosen, targets)
    residual = [int(q) for q in targets[~covered]]
    D, E = self_consistent_D(logm / LN10, len(residual), boost)
    return {
        "Q": int(Q),
        "cover": sorted((int(r), int(a)) for r, a in chosen.items()),
        "residual": residual,
        "boost": boost,
        "m_digits": logm / LN10,
        "E": E,
        "n_digits_est": D,
    }


def crt(cover):
    """N == 0 (mod 2), N == a_r (mod r) -> (N0, M)."""
    M, N0 = 2, 0
    for r, a in cover:
        inv = pow(M % r, -1, r)
        t = ((a - N0) * inv) % r
        N0 += M * t
        M *= r
    return N0 % M, M


def main():
    Q = int(sys.argv[1]) if len(sys.argv) > 1 else 100003
    e_target = float(sys.argv[2]) if len(sys.argv) > 2 else 16.5
    out = sys.argv[3] if len(sys.argv) > 3 else None
    res = build_cover(Q, e_target=e_target)
    N0, M = crt(res["cover"])
    print(f"Q={Q} congr={len(res['cover'])} M={res['m_digits']:.1f}d "
          f"|U|={len(res['residual'])} boost={res['boost']:.2f} "
          f"E={res['E']:.2f} est N~{res['n_digits_est']:.1f}d")
    if out:
        res["N0"] = str(N0)
        res["M"] = str(M)
        with open(out, "w") as f:
            json.dump(res, f)
        print("wrote", out)


if __name__ == "__main__":
    main()
