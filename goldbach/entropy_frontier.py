"""Set-valued conditioning frontier: how small can E be for N < 10^D?

A classic cover pins N mod r to ONE residue, spending ln r nats of the
ln B = D*ln10 "size budget" (the CRT modulus must stay under the bound
or no representative exists below it).  Generalisation: constrain N mod r
to a SET A_r of k residues, spending only ln(r/k) nats.  k = 1 is the
classic cover; k = r is free and buys nothing.

Because N mod r are independent (CRT), the survival model is exact:

    s_q = prod_r P(r does not divide N - q)
    P   = 1 - [q mod r in A_r]/k_r   for a conditioned r
        = 1 - 1/r                    otherwise
    E   = e^gamma * ln(RC) / ln(N) * sum_q s_q

which reproduces the validated E = |U|*boost/ln N when every k_r = 1.

Feasibility of a search below 10^D is  H + E <= D*ln10:  H nats of
conditioning leave exp(ln B - H) admissible N under the bound, and each
wins the desert lottery with probability e^-E.

The frontier is traced by a Lagrangian sweep: for a nat-price lambda,
coordinate-descend each modulus to the k maximising (gain - lambda*cost),
then lower lambda.  Sweeping lambda from high to low walks from "spend
nothing" to "spend everything".

Usage: entropy_frontier.py [digits] [--classic] [--rc RC] [--Q Q]
"""

import argparse
import json
import math

import numpy as np
from sympy import primerange

LN10 = math.log(10)
EULER = 0.5772156649015329


class Frontier:
    def __init__(self, digits, rc, q_target, classic_only=False):
        self.lnN = digits * LN10
        self.lnB = digits * LN10
        self.digits = digits
        self.classic = classic_only
        self.targets = np.array(list(primerange(3, q_target)), dtype=np.int64)
        self.mods = [int(r) for r in primerange(3, rc)]
        self.resid = {r: (self.targets % r).astype(np.int32)
                      for r in self.mods}
        n = len(self.targets)
        # s = prod of per-modulus factors; k=1 makes exact zeros, so keep
        # the nonzero part and a zero-count separately (division-safe).
        self.prod_nz = np.ones(n, dtype=np.float64)
        self.zcnt = np.zeros(n, dtype=np.int32)
        for r in self.mods:
            self.prod_nz *= 1.0 - 1.0 / r
        self.scale = math.exp(EULER) * math.log(rc) / self.lnN
        self.k = {r: r for r in self.mods}       # k = r means unconditioned
        self.A = {r: None for r in self.mods}

    # ---- E and H ---------------------------------------------------------
    @property
    def s(self):
        return np.where(self.zcnt == 0, self.prod_nz, 0.0)

    def E(self):
        return self.scale * self.s.sum()

    def H(self):
        return sum(math.log(r / k) for r, k in self.k.items() if k < r)

    # ---- factor vector of one modulus ------------------------------------
    def _factor(self, r):
        k = self.k[r]
        if k >= r:
            return np.full(len(self.targets), 1.0 - 1.0 / r)
        inA = np.isin(self.resid[r], self.A[r])
        return np.where(inA, 1.0 - 1.0 / k, 1.0)

    def _clean(self, r):
        """s with modulus r's factor removed (division-safe)."""
        f = self._factor(r)
        z = f == 0.0
        nz = self.zcnt - z.astype(np.int32)
        return np.where(nz == 0, self.prod_nz / np.where(z, 1.0, f), 0.0)

    def _apply(self, r, k, keep):
        fold = self._factor(r)
        zold = fold == 0.0
        self.prod_nz /= np.where(zold, 1.0, fold)
        self.zcnt -= zold.astype(np.int32)
        if k >= r:
            fnew = np.full(len(self.targets), 1.0 - 1.0 / r)
            self.k[r], self.A[r] = r, None
        else:
            inA = np.isin(self.resid[r], keep)
            fnew = np.where(inA, 1.0 - 1.0 / k, 1.0)
            self.k[r], self.A[r] = k, keep
        znew = fnew == 0.0
        self.prod_nz *= np.where(znew, 1.0, fnew)
        self.zcnt += znew.astype(np.int32)

    def best_k(self, r, lam):
        """Best k for modulus r at nat-price lam; returns (score, k, keep)."""
        sclean = self._clean(r)
        w = np.bincount(self.resid[r], weights=sclean, minlength=r)
        tot = sclean.sum()
        order = np.argsort(w)[::-1]
        cum = np.cumsum(w[order])
        ks = np.array([1]) if self.classic else np.arange(1, r)
        # sum(s) after conditioning to top-k:  tot - cum_k/k
        newsum = tot - cum[ks - 1] / ks
        cost = np.log(r / ks)
        cur = self.s.sum()
        cur_cost = math.log(r / self.k[r]) if self.k[r] < r else 0.0
        # score = reduction in E minus lam * extra nats
        score = self.scale * (cur - newsum) - lam * (cost - cur_cost)
        i = int(np.argmax(score))
        return float(score[i]), int(ks[i]), order[:ks[i]]

    def sweep(self, lam, rounds=4):
        for _ in range(rounds):
            changed = False
            for r in self.mods:
                score, k, keep = self.best_k(r, lam)
                if score > 1e-12 and k != self.k[r]:
                    self._apply(r, k, keep)
                    changed = True
            if not changed:
                break


def run(digits, rc, q_target, classic_only, lams, verbose=True):
    f = Frontier(digits, rc, q_target, classic_only)
    print(f"D={digits:g}  lnB={f.lnB:.1f}  E(random N)={f.E():.2f}  "
          f"{'CLASSIC k=1' if classic_only else 'SET-VALUED'}", flush=True)
    trace = []
    for lam in lams:
        f.sweep(lam)
        H, E = f.H(), f.E()
        used = sum(1 for r, k in f.k.items() if k < r)
        k1 = sum(1 for r, k in f.k.items() if k == 1)
        trace.append({"lam": lam, "H": H, "E": E, "used": used, "k1": k1})
        if verbose:
            flag = "OK " if H + E <= f.lnB else "   "
            print(f"  lam={lam:8.4f}  H={H:7.1f}  E={E:6.2f}  H+E={H + E:7.1f}"
                  f" {flag} moduli={used:4d} (k=1: {k1:3d})", flush=True)
    ok = [t for t in trace if t["H"] + t["E"] <= f.lnB]
    print()
    if ok:
        b = min(ok, key=lambda t: t["E"])
        print(f"BEST FEASIBLE: E={b['E']:.2f}  H={b['H']:.1f}  "
              f"(H+E={b['H'] + b['E']:.1f} <= {f.lnB:.1f}) -> "
              f"e^{b['E']:.1f} = 10^{b['E'] / LN10:.1f} candidates")
    else:
        b = min(trace, key=lambda t: t["H"] + t["E"])
        print(f"INFEASIBLE: best H+E={b['H'] + b['E']:.1f} > {f.lnB:.1f}")
    return f, trace


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("digits", nargs="?", type=float, default=100.0)
    ap.add_argument("--classic", action="store_true")
    ap.add_argument("--rc", type=int, default=5000)
    ap.add_argument("--Q", type=int, default=100003)
    ap.add_argument("--out")
    a = ap.parse_args()
    lams = [3.0, 2.0, 1.5, 1.0, 0.7, 0.5, 0.35, 0.25, 0.18, 0.12,
            0.08, 0.05, 0.03, 0.02, 0.012, 0.007, 0.004, 0.002, 0.001]
    f, trace = run(a.digits, a.rc, a.Q, a.classic, lams)
    if a.out:
        json.dump({"digits": a.digits, "Q": a.Q, "rc": a.rc,
                   "classic": a.classic, "trace": trace},
                  open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
