#!/usr/bin/env python3
"""Where the variance of the first-order score lives: Var over a uniform class of hit_s(c), summed over the later primes s
up to z, as a share of the sum over all later primes below 10^8 (for s > 200000 a class holds at most one row of R0 unless two
rows are congruent; Var = n0/s - (n0/s)^2 + pairs term, computed exactly up to 2*10^6 and by n0/s beyond).  Next to D(z)."""
import math, numpy as np, common as C
LNX = 200 * math.log(10)
pr = C.primes_upto(2 * 10 ** 6); pr = pr[pr > 463]
var = np.empty(len(pr))
for i, s in enumerate(pr):
    cnt = np.unique(C.R0 % s, return_counts=True)[1].astype(np.float64); var[i] = (cnt ** 2).sum() / s - (C.n0 / s) ** 2
cum = np.cumsum(var)
# tail 2e6..1e8: sum of n0/s over primes ~ n0 * (ln ln 1e8 - ln ln 2e6)
tail = C.n0 * (math.log(math.log(1e8)) - math.log(math.log(2e6)))
total = cum[-1] + tail
th = np.cumsum(np.log(pr.astype(np.float64))) + (LNX - 16.87791864582339)
print(f"sum of variances, later primes to 2*10^6: {cum[-1]:.1f} rows^2; estimated tail to 10^8: {tail:.1f}; total {total:.1f} (sd {math.sqrt(total):.1f} rows)")
print("    z   later primes   D(z)        variance captured (rows^2)   share    sd captured (rows)")
for z in (487, 491, 499, 503, 509, 541, 1000, 2000, 10 ** 4, 10 ** 5, 2 * 10 ** 5, 2 * 10 ** 6):
    i = np.searchsorted(pr, z, side="right") - 1
    print(f"{z:>8} {i + 1:>8}   {th[i] - LNX:>12.1f}   {cum[i]:>10.1f}                 {cum[i] / total:6.3f}   {math.sqrt(cum[i]):6.1f}")
