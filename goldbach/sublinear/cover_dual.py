#!/usr/bin/env python3
"""The other direction: a fixed gap Q and a number of d digits.  How much luck does g(N) >= Q cost at that size?

    python3 cover_dual.py Q d [d ...]

For each size: the odd primes that fit as moduli (their product, doubled, at most 10^d / 2^24), where complete covers
end on them, the rows left by random nonzero classes, the fewest rows a cover can leave at Q (the price recursion with
a finite end price, cover_price.floor: where its entropy reaches zero, and its largest floor), the chance p that N - q
is prime for a row that no modulus strikes, p = 2 prod r/(r-1) / ln N, and E = p * rows: one member in e^E succeeds.
At the campaign's points (200 digits, Q = 170,000 and 213,070) the row count comes out 2% below the best cover found.
"""
import sys, math
import cover_price as cp
Q = int(sys.argv[1]); LOGMEM = math.log(2.0 ** 24)        # leave 2^24 members to a cover
for d in [int(a) for a in sys.argv[2:]]:
    L = d * math.log(10); th = math.log(2); mods = []
    for r in cp.P:
        if th + math.log(r) > L - LOGMEM: break
        th += math.log(r); mods.append(r)
    x = mods[-1]; phis = []; phi = 1.0
    for s in mods: phis.append(phi); phi *= 1 - 1 / (s - 1)
    piQ = cp.odd_primes_below(Q); krand = piQ * phi
    p = 2 * math.prod(r / (r - 1) for r in mods) / L
    # where complete covers end on these moduli
    thm = sum(math.log(s - 1) for s in mods); lo, hi = float(x), 40.0 * x * math.log(x) ** 2
    for _ in range(40):
        mid = math.sqrt(lo * hi); pp, pq, _ = cp.start_price(mods, phis, mid)
        if pp * pq < thm: lo = mid
        else: hi = mid
    D = lo
    if D >= Q: k = 0.0; kb = 0.0
    else:
        piq, crisis, best = cp.floor(x, Q); k = crisis[1] if crisis else float("nan"); kb = best
    E = p * max(k, kb)
    print(f"{Q} | {d} | {len(mods)} | {x} | {D:.0f} | {krand:.0f} | {k:.0f} | {kb:.0f} | {p:.5f} | {E:.2f} | {E / math.log(10):.2f}", flush=True)
