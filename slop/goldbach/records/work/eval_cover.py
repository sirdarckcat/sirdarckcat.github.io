#!/usr/bin/env python3
"""Score a cover: exact p1 (per-residual prime probability), expected search
exponent p1*k, expected t to first success, CPU estimate, t-range fit."""
import json, math, sys

def main(path, target_lnN=None):
    c = json.load(open(path))
    k = c["k"]; spent = c["spent"]
    lnM = spent + math.log(2)
    lnN = target_lnN or (lnM + math.log(3e6))       # assume t ~ 3e6 typical
    # p1 = P(random residual complement is prime) with coprimality to all moduli
    corr = 1.0
    for r, _ in c["classes"]:
        corr *= 1 / (1 - 1 / r)
    corr *= 2  # N-p odd (p odd, N even => complement odd): factor 2/(1-1/2)... complement never even
    p1 = corr / lnN
    exp_t = math.exp(p1 * k)
    print(f"cover {path}: Q={c['Q']} k={k} moduli={len(c['classes'])} "
          f"lnM={lnM:.1f} ({lnM/math.log(10):.1f} digits)")
    print(f"  p1={p1:.5f}  p1*k={p1*k:.2f}  E[t to success]≈{exp_t:.3g}")
    print(f"  E[PRP tests/t (fail-fast, no sieve)]≈{1/p1:.0f}")
    lnstar = 457.6747343080371
    print(f"  t-range to N*: {math.exp(max(0,lnstar-lnM)):.3g}  "
          f"E[hits in range]={math.exp(max(0,lnstar-lnM))/exp_t:.2f}")

if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else None)
