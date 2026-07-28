"""Realizable frontier: candidates must be ENUMERABLE, not merely exist.

The set-valued optimum (entropy_frontier.py) drives E down by conditioning
~200 moduli with a product far above the size bound.  Solutions below the
bound still exist -- but finding which residue combination lands there is
a constrained-CRT / lattice problem, not a scan.  Free enumeration needs

    M1 = prod of conditioned moduli  <=  B,

so every residue combination yields ~B/M1 representatives below the bound
by simple progression scanning.  The candidate pool is then

    pool = (B / M1) * prod_r k_r  =  exp(rho + Lambda),
    rho    = ln B - ln M1        (k-room, classic)
    Lambda = sum_r ln k_r        (residue multiplicity, F4-style)

and a search succeeds when  rho + Lambda >= E.  Both terms buy candidates:
k-room costs modulus size (fewer moduli, weaker cover); multiplicity costs
coverage dilution (a diluted class is covered only 1/k of the time).  This
script measures which is cheaper, and the best realizable E per digit size.

Usage: realizable_frontier.py [--digits 100,140] [--rc RC] [--Q Q]
"""

import argparse
import json
import math

import numpy as np

import entropy_frontier as ef

LN10 = math.log(10)


def build_cover(f, size_budget):
    """Greedy classic (k=1) cover, stopping at sum(ln r) <= size_budget."""
    used_size = 0.0
    while True:
        tot = f.s.sum()
        best = None
        for r in f.mods:
            if f.k[r] < r:
                continue
            if used_size + math.log(r) > size_budget:
                continue
            w = np.bincount(f.resid[r], weights=f.s, minlength=r)
            a = int(np.argmax(w))
            gain = (r * w[a] - tot) / (r - 1)
            rate = gain / math.log(r)
            if best is None or rate > best[0]:
                best = (rate, r, a)
        if best is None or best[0] <= 0:
            break
        _, r, a = best
        f._apply(r, 1, np.array([a]))
        used_size += math.log(r)
    return used_size


def buy_multiplicity(f, mu, rounds=3, kmax=64):
    """Raise k on conditioned moduli; paid mu per nat of ln k."""
    cond = [r for r in f.mods if f.k[r] < r]
    for _ in range(rounds):
        changed = False
        for r in cond:
            sclean = f._clean(r)
            w = np.bincount(f.resid[r], weights=sclean, minlength=r)
            order = np.argsort(w)[::-1]
            cum = np.cumsum(w[order])
            ks = np.arange(1, min(kmax, r - 1) + 1)
            newsum = sclean.sum() - cum[ks - 1] / ks
            cur = f.s.sum()
            score = f.scale * (cur - newsum) + mu * (np.log(ks)
                                                     - math.log(f.k[r]))
            i = int(np.argmax(score))
            if score[i] > 1e-12 and int(ks[i]) != f.k[r]:
                f._apply(r, int(ks[i]), order[:ks[i]])
                changed = True
        if not changed:
            break
    lam = sum(math.log(f.k[r]) for r in cond)
    return lam


def realizable(digits, rc, q, rhos, mus, verbose=True):
    lnB = digits * LN10
    best = None
    for rho in rhos:
        f = ef.Frontier(digits, rc, q, classic_only=True)
        size = build_cover(f, lnB - rho)
        E0 = f.E()
        # classic point: multiplicity 0, need rho >= E
        cand = []
        if rho >= E0:
            cand.append({"rho": rho, "lam": 0.0, "E": E0, "mu": 0.0})
        for mu in mus:
            g = ef.Frontier(digits, rc, q, classic_only=True)
            build_cover(g, lnB - rho)
            lam = buy_multiplicity(g, mu)
            E = g.E()
            if rho + lam >= E:
                cand.append({"rho": rho, "lam": lam, "E": E, "mu": mu})
        if cand:
            b = min(cand, key=lambda c: c["E"])
            b["size_digits"] = size / LN10
            if best is None or b["E"] < best["E"]:
                best = b
            if verbose:
                print(f"  rho={rho:6.1f}  M={size / LN10:6.1f}d  E0={E0:6.2f}"
                      f"  -> best E={b['E']:6.2f} (Lambda={b['lam']:5.1f})",
                      flush=True)
        elif verbose:
            print(f"  rho={rho:6.1f}  M={size / LN10:6.1f}d  E0={E0:6.2f}"
                  f"  -> infeasible", flush=True)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--digits", default="100,140")
    ap.add_argument("--rc", type=int, default=3000)
    ap.add_argument("--Q", type=int, default=100003)
    ap.add_argument("--out")
    a = ap.parse_args()
    rows = []
    for d in [float(x) for x in a.digits.split(",")]:
        lnB = d * LN10
        rhos = [r for r in (10, 20, 30, 40, 50, 60, 70) if r < lnB]
        mus = [0.02, 0.05, 0.1, 0.2, 0.4, 0.8]
        print(f"\n=== D={d:g} digits (ln B={lnB:.1f}) ===")
        b = realizable(d, a.rc, a.Q, rhos, mus)
        if b:
            b["digits"] = d
            rows.append(b)
            print(f"REALIZABLE BEST: E={b['E']:.2f} -> 10^{b['E'] / LN10:.1f} "
                  f"candidates  (M={b['size_digits']:.0f}d, k-room "
                  f"e^{b['rho']:.0f}, multiplicity e^{b['lam']:.1f})")
        else:
            print("no realizable point")
    if a.out:
        json.dump(rows, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
