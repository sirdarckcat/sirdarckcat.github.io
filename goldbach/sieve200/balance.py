#!/usr/bin/env python3
"""Which sieve bound B, and which kept fraction f, for a host with a CPU feeder and a GPU tester?

A host sieves R_c = threads / cost(B) members a second (the feeder) and tests R_g tests a second on its GPU.  Testing the emptiest
fraction (1 - f) of the members costs (1 - f) T(B) w tests a member, T(B) = 1 / p_B tests until a member's first probable prime, w the
tests computed after it (waste); so the GPU fixes f: 1 - f = R_g / (R_c T w).  The hit mass of the emptiest fraction follows from
the survivor counts (mean mu, sd sigma, near Gaussian): a member succeeds with probability (1 - p_B)^count, so the share of the hit
mass in the emptiest fraction keep is Phi(Phi^-1(keep) + lambda sigma), lambda = -ln(1 - p_B).  The figure of merit is
R_c x hit share, in million members a second.

    python3 balance.py --threads 31 --gpu 22.9          # a G4 host: 48 vCPUs ~ 31 thread-equivalents, RTX PRO 6000 + fermat28
    python3 balance.py --threads 9 --gpu 4.0            # an L4 host
Inputs measured on one Sapphire Rapids core (867-row cover, K = 2^19..2^20, microseconds a member, scaled by rows / 867).
"""
import argparse
import math
from statistics import NormalDist

COST = {3000: 0.24, 10000: 0.34, 30000: 0.44, 100000: 0.52, 300000: 0.58, 1000000: 0.64, 3000000: 0.95, 10000000: 1.7, 30000000: 3.0}


def table(threads, gpu, rows, sigma, waste, lnN, cost):
    N = NormalDist()
    print(f"{threads:g} thread-equivalents, GPU {gpu:g} M tests/s, {rows} rows, sd {sigma:g}, waste {waste:g}")
    print(f"{'B':>9} {'us/member':>9} {'Rc M/s':>7} {'p_B':>7} {'T':>5} {'f':>7} {'hit share':>9} {'Rc*hit':>7}")
    best = None
    for B, c in sorted(cost.items()):
        c *= rows / 867
        Rc = threads / c
        p = math.exp(0.5772156649) * math.log(B) / lnN
        T = 1 / p
        keep = min(1.0, gpu / (Rc * T * waste))
        lam = -math.log(1 - p)
        share = N.cdf(N.inv_cdf(keep) + lam * sigma) if keep < 1 else 1.0
        rate = Rc * share
        best = max(best or (0, B), (rate, B))
        print(f"{B:9.0e} {c:9.3f} {Rc:7.1f} {p:7.4f} {T:5.1f} {1 - keep:7.4f} {share:9.4f} {rate:7.2f}")
    print(f"best B = {best[1]:.0e}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=float, default=31)
    ap.add_argument("--gpu", type=float, default=22.9)
    ap.add_argument("--rows", type=int, default=1011)
    ap.add_argument("--sd", type=float, default=15.5)
    ap.add_argument("--waste", type=float, default=1.07)
    ap.add_argument("--digits", type=float, default=199.5)
    a = ap.parse_args()
    table(a.threads, a.gpu, a.rows, a.sd, a.waste, math.log(10) * a.digits, COST)
