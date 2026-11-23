#!/usr/bin/env python3
"""Where the ideal-search cutoff sits in temperature, the exponent that independent thinning
predicts for the fall of the cutoff with depth, the cutoffs of the deeper tables predicted
from a shallower one, and the sub-Poisson deficit of the row count.

Usage: python3 -I envelope.py ideal_tilt_213070.txt   (same input as thin.py)

Independent thinning gives for S(tau, k) = ln #{N : k rows left at depth z}, tau = ln ln z,
        dS/dtau = k (exp(dS/dk) - 1)                     (Hamilton-Jacobi)
with characteristics  (1 - exp(-beta)) / ln z = const,  k exp(beta) ln z = const,
S - beta k = const  (beta = dS/dk).  Along the cutoff S = p_z k of the ideal search this gives
        -dln k / dln ln z = (exp(beta) - 1 - p) / (beta - p).
"""
import sys, math, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # thin.py, next to this file
from thin import read_tables, primes_upto, theta

LNPOP = 458.67      # ln(number of even N < 10^200 in the state space), from the tables

def cutoff(betas, ks, lnZs, p):
    """canonical estimate of the cutoff: ln(pop) + ln Z + beta k = p k"""
    g = LNPOP + lnZs + betas * ks - p * ks
    for i in range(len(betas) - 1):
        if g[i] > 0 >= g[i + 1]:
            t = g[i] / (g[i] - g[i + 1])
            return betas[i] + t * (betas[i + 1] - betas[i]), ks[i] + t * (ks[i + 1] - ks[i])
    return float('nan'), float('nan')

if __name__ == "__main__":
    tab = read_tables(sys.argv[1]); P = primes_upto(60000); zs = sorted(tab)
    print("1. Temperature at the cutoff, and the exponent independent thinning predicts there")
    print("        z  k_cut  beta_c  e^beta_c  (e^b-1-p)/(b-p)   measured -dln k_cut/dln ln z to the next depth")
    for i, z in enumerate(zs):
        t = tab[z]; b = float(np.interp(-t["cut"], -t["k"], t["beta"]))
        E = (math.exp(b) - 1 - t["p"]) / (b - t["p"]); meas = ""
        if i + 1 < len(zs):
            z2 = zs[i + 1]
            meas = f"{-math.log(tab[z2]['cut'] / t['cut']) / math.log(math.log(z2) / math.log(z)):.2f}  ({z} -> {z2})"
        print(f"   {z:6d}  {t['cut']:5d}   {b:5.2f}    {math.exp(b):5.2f}       {E:5.2f}          {meas}")

    print("\n2. Cutoff of the deeper table predicted from a shallower one by independent thinning")
    print("   (canonical estimate; 'direct' is the same estimate on the deeper table itself; 'file' is the")
    print("   research session's figure from the histograms; ln cost = p_z' * k_cut in brackets)")
    for i, z in enumerate(zs):
        for z2 in zs[i + 1:]:
            th = theta(P, z, z2); par, ch = tab[z], tab[z2]
            bps = np.linspace(0.02, 5.0, 2000)
            x = 1 - th * (1 - np.exp(-bps)); b = -np.log(x)
            lnZ = np.interp(b, par["beta"], par["lnZ"]); kch = np.interp(b, par["beta"], par["k"]) * th * np.exp(-bps) / x
            bpred, kpred = cutoff(bps, kch, lnZ, ch["p"])
            bdir, kdir = cutoff(ch["beta"], ch["k"], ch["lnZ"], ch["p"])
            bpar = -math.log(1 - th * (1 - math.exp(-bpred)))
            print(f"   {z:6d} -> {z2:6d}: theta {th:.3f}  predicted {kpred:7.1f} ({ch['p'] * kpred:5.2f}; beta' {bpred:4.2f}, shallower beta {bpar:4.2f})"
                  f"   direct {kdir:7.1f} ({ch['p'] * kdir:5.2f})   file {ch['cut']} ({ch['cost']:5.2f})")

    print("\n3. beta = 0: mean and (mean - variance) of the row count; binomial thinning multiplies them by theta and theta^2")
    prev = None
    for z in zs:
        t = tab[z]; d = t["k"][0] - t["sd"][0] ** 2
        line = f"   z={z:6d}  mean {t['k'][0]:7.1f}  sd {t['sd'][0]:5.1f}  mean - var {d:7.1f}"
        if prev is not None:
            zp, dp = prev; th = theta(P, zp, z)
            line += f"   thinned from z={zp}: mean {tab[zp]['k'][0] * th:7.1f}, mean - var {dp * th ** 2:7.1f}"
        print(line); prev = (z, d)
