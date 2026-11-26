#!/usr/bin/env python3
"""Illustration for the tie-ratio remark: in the Hurwitz order a central target N is fixed by every conjugation, and
nrd(N - pi) = N^2 - trd(pi) N + nrd(pi) depends on the row pi only through (trace, norm).
Counts rows of reduced norm p and the distinct trial integers they give (i.e. distinct traces)."""
import itertools, math
def hurwitz_of_norm(p):
    out = []
    # coordinates in half-integers: 2a,2b,2c,2d all even or all odd, a^2+b^2+c^2+d^2 = p
    m = int(2 * math.isqrt(p)) + 2
    for par in (0, 1):
        rng = [v for v in range(-m, m + 1) if v % 2 == par]
        for A in rng:
            for B in rng:
                for C in rng:
                    r = 4 * p - A * A - B * B - C * C
                    if r < 0: continue
                    D = math.isqrt(r)
                    if D * D == r and D % 2 == par:
                        out.append((A, B, C, D))
                        if D: out.append((A, B, C, -D))
    return out
print("p | Hurwitz quaternions of norm p | 24(p+1) | distinct traces = distinct trial integers | rows per trial")
for p in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
    H = hurwitz_of_norm(p); tr = {h[0] for h in H}
    print(f"{p} | {len(H)} | {24 * (p + 1)} | {len(tr)} | {len(H) / len(tr):.1f}")
