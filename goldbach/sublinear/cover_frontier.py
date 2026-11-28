#!/usr/bin/env python3
"""The closeness frontier: the cheapest way to hold g(N) >= f * ceiling(N) with N of exactly d digits (model; nothing found here).

    python3 cover_frontier.py f d [d ...]          f = 0.10, 0.25, 0.50, ...

closeness = g(N)/ceiling(N), the ceiling at N's own size (../closeness.py).  A number of d digits lies in [10^(d-1), 10^d),
and the ceiling grows by 4 to 10% across that range, so the cheap members are the ones just above 10^(d-1): scan
10^(d-1) < N <= c 10^(d-1) with the target Q = f * ceiling(c 10^(d-1)); every hit then has closeness >= f.  A small c
lowers Q and leaves fewer members to a cover (so fewer moduli fit, or more covers are needed).  For each d the table
gives the c (from a grid) with the fewest members per hit, when a cover keeps at least 2^24 members in the range:

    moduli = the odd primes with 2 prod r <= (c - 1) 10^(d-1) / 2^24,   rows = the recursion's floor at Q on them
    (cover_price.floor; covers found sit 1 to 7% above it at these ratios of Q to the end of complete covers),
    p = 2 prod r/(r-1) / ln N,   one member in (1 - p)^-rows is a hit.
"""
import sys, math
sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), ".."))
import closeness
import cover_price as cp

CS = (1.1, 1.2, 1.35, 1.5, 2.0, 3.0, 5.0, 10.0)
LOGMEM = 24 * math.log(2)

def point(f, d, c):
    lo = (d - 1) * math.log(10); hi = lo + math.log(c); Q = int(math.ceil(f * closeness.ceiling(hi)))
    room = lo + math.log(c - 1) - LOGMEM; th = math.log(2); mods = []
    for r in cp.P:
        if th + math.log(r) > room: break
        th += math.log(r); mods.append(r)
    if len(mods) < 3: return None
    x = mods[-1]; piq, crisis, best = cp.floor(x, Q)
    rows = max(crisis[1] if crisis else 0.0, best)
    lnN = lo + math.log((1 + c) / 2); p = 2 * math.prod(r / (r - 1) for r in mods) / lnN
    E = -rows * math.log(1 - p)
    return dict(c=c, Q=Q, n=len(mods), x=x, rows=rows, p=p, E=E, logmem=room + LOGMEM - th)

if __name__ == "__main__":
    f = float(sys.argv[1])
    print(f"# closeness >= {f:g}: digits | c (scan 10^(d-1) < N <= c 10^(d-1)) | target Q | moduli (largest) | floor rows | p | log10 members per hit | "
          f"log2 members to a cover | covers per hit | the same with c = 10: Q, log10 members per hit")
    for d in [int(a) for a in sys.argv[2:]]:
        pts = [q for q in (point(f, d, c) for c in CS) if q]
        b = min(pts, key=lambda q: q["E"]); t = pts[-1]
        print(f"{d} | {b['c']:g} | {b['Q']} | {b['n']} ({b['x']}) | {b['rows']:.0f} | {b['p']:.5f} | {b['E'] / math.log(10):.2f} | {b['logmem'] / math.log(2):.1f} | "
              f"{math.exp(b['E'] - b['logmem']):.3g} | {t['Q']}, {t['E'] / math.log(10):.2f}", flush=True)
