# For the lead and the user: the chance that the 200-digit campaign ends at or above G, and the expected final record, for design
# levels 170,000 (today), 180,000, 190,000 and 200,000. Written from the cover files, independently of the research session's
# cover_design.py, with today's corrections:
#   - the exponent averaged over members uniform in N (t = ln X - ln N is Exp(1)): E = -ln E_t[(1 - p(N))^n], p(N) = 2 prod r/(r-1)/ln N;
#   - the tilt is lambda' * sd, with lambda' = -ln(1 - p'), p' = p/c, c the exact product of (1 - 1/s) over the sieve primes to 1e8
#     (every odd prime that is not a modulus), and sd = 0.9836 * sqrt(n c (1 - c)) (the Lean session's pair correction);
#   - the rows the fleet runs, not the best: +5.5 above the best at 170,000 (the G4s sit at 1,249-1,250 against 1,245 and step to
#     1,251), +4.5 at 180,000-200,000 (about ten million covers within +5 rows);
#   - the cost per scanned member is 0.26 sieve (proportional to the rows) + 0.74 tests (the G4's measured split);
#   - the budget is 1.90 expected design hits at 170,000 as the fleet runs (GPU session, 16:05Z).
# A design hit at D is decided beyond D by the cover's remaining rows in [D, G), each composite with probability 1 - p (they are not
# sieved). For G below D the count needs each tested member's g, which the tests give for free if survivors are tested in increasing
# q (the first probable prime found is g). Two expected records are given: from design hits only, and with every tested member's g.
# The record held today is 160,357 (found by the fleet on the 24th on an 89-prime cover; the research session, 18:24Z).
#   python3 campaign_table.py [package_nats ...]
import sys, math
import numpy as np
from statistics import NormalDist
ND = NormalDist(); z0 = ND.inv_cdf(0.015); L = 200 * math.log(10); R0 = 160357; QMAX = 260000; B = 10 ** 8

def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

P8 = primes_upto(B); P8 = P8[P8 > 2]; lncall = float(np.sum(np.log1p(-1.0 / P8)))
Q = primes_upto(QMAX); Q = Q[Q > 2]
t = np.linspace(0, 14, 2801); wt = np.exp(-t); wt /= wt.sum()          # t = L - ln N, Exp(1), truncated far out

def window_E(n, C):
    """-ln of the window average of (1 - C/ln N)^n."""
    lam = -np.log1p(-C / (L - t))
    return float(-np.log(np.sum(wt * np.exp(-n * lam))))

def load(f):
    l = [x for x in open(f"covers/{f}.txt") if x.startswith("COVER")][0].split()
    cov = [tuple(map(int, w.split(":"))) for w in l if ":" in w]
    alive = np.ones(len(Q), bool)
    for r, a in cov: alive &= (Q % r) != a
    mods = [r for r, _ in cov]
    C = 2 * math.prod(r / (r - 1) for r in mods)
    c = math.exp(lncall - sum(math.log1p(-1.0 / r) for r in mods))
    return Q[alive], C, c

DESIGNS = [(170000, "q170000_m89r491", 5.5), (180000, "q180000_m89", 4.5), (190000, "q190000_m89", 4.5), (200000, "q200000_m89", 4.5)]
GS = [170000, 180000, 190000, 200000, 213070]

def table(package):
    rows_out = []; ref = None
    pre = {}
    for idx, (D, f, extra_run) in enumerate(DESIGNS):
        U, C, c = load(f); nbest = int((U < D).sum()); scale = (nbest + extra_run) / nbest
        p = C / L; pp = p / c; lamp = -math.log1p(-pp)
        def n_below(G, U=U, scale=scale): return float((U < G).sum()) * scale     # defaults bind this design's cover
        def sd(n, c=c): return 0.9836 * math.sqrt(n * c * (1 - c))
        nD = n_below(D); E_D = window_E(nD, C); delta = lamp * sd(nD); cap = ND.cdf(z0 + delta)
        pre[idx] = dict(U=U, C=C, c=c, scale=scale, nD=nD, E=E_D, cap=cap, delta=delta, lamp=lamp, sd=sd, n_below=n_below, p=p)
    n170 = pre[0]["nD"]                     # the first design is the reference: the 170,000 cover the fleet runs
    for idx in pre:
        pre[idx]["cost"] = 0.26 * pre[idx]["nD"] / n170 + 0.74
    r = pre[0]; M170 = 1.90 / (math.exp(-r["E"]) * r["cap"]); W = M170 * r["cost"] * math.exp(package)
    for idx, (D, f, extra_run) in enumerate(DESIGNS):
        r = pre[idx]; M = W / r["cost"]
        def Lam(G):
            if G >= D:      # design hits, decided beyond D by the unsieved remaining rows (each composite with probability 1 - p)
                extra = float(((r["U"] >= D) & (r["U"] < G)).sum()) * r["scale"]
                return M * math.exp(-r["E"]) * r["cap"] * math.exp(-extra * -math.log1p(-r["p"]))
            nG = r["n_below"](G); EG = window_E(nG, r["C"])     # tested members with g >= G (needs g from the tests)
            capG = ND.cdf(z0 + r["lamp"] * r["sd"](nG) ** 2 / r["sd"](r["nD"]))
            return M * math.exp(-EG) * capG
        hits = Lam(D)
        probs = {G: (1 - math.exp(-Lam(G))) if G >= D else None for G in GS}
        # expected final record: design hits only, and with every tested member's g (q-ordered tests)
        grid = np.arange(R0, 400001, 250)
        P_design = np.array([(1 - math.exp(-Lam(G))) if G >= D else (1 - math.exp(-hits)) for G in grid])
        P_all = np.array([1 - math.exp(-Lam(G)) for G in grid])
        rec_design = R0 + float(np.sum(P_design)) * 250; rec_all = R0 + float(np.sum(P_all)) * 250
        dist = {x: 1 - math.exp(-Lam(x)) for x in range(165000, 200001, 5000)}     # P(final >= x), every tested member's g counted
        rows_out.append((D, r["nD"], r["E"], r["delta"], r["cap"], r["cost"], hits, probs, rec_design, rec_all, dist))
    return rows_out

if __name__ == "__main__":
    packs = [float(x) for x in sys.argv[1:]] or [0.0, 0.35, 0.65]
    for pk in packs:
        print(f"\nengineering package {pk:+.2f} nats (budget: 1.90 design hits at 170,000 as the fleet runs, times e^{pk:.2f})")
        print("design | rows run | exponent (window avg) | tilt | captured at 1.5% | cost/member | design hits | " +
              " | ".join(f"P(>= {G:,})" for G in GS) + " | E[record], design hits only | E[record], g of every tested member")
        out = table(pk)
        for D, n, E, d, cap, cost, hits, probs, rd, ra, dist in out:
            ps = " | ".join(("%.3f%%" % (100 * probs[G])) if probs[G] is not None else "-" for G in GS)
            print(f"{D:,} | {n:.1f} | {E:.2f} | {d:.3f} | {cap:.3f} | {cost:.3f} | {hits:.4f} | {ps} | {rd:,.0f} | {ra:,.0f}")
        xs = sorted(out[0][10])
        print("distribution of the final record, every tested member's g counted (floor 160,357): P(final >= x)")
        print("design | " + " | ".join(f"{x:,}" for x in xs))
        for row in out:
            print(f"{row[0]:,} | " + " | ".join(f"{100 * row[10][x]:.2f}%" for x in xs))
