#!/usr/bin/env python3
"""The chance of a final record above G for each design level, from the covers in ../fscan/cover/starts (200 digits).

    python3 cover_design.py [budget = 31.08]

P(final record >= G) for a design level D: the cover is built for D, the sieve and the cut act on the rows below D, a member that passes them
is then decided beyond D by its remaining rows.  Budget: e^BUD effective members at the 170,000 design (so that e^(BUD - 30.30) design hits are left there).
The budget is the logarithm of the effective members left at the 170,000 design (31.08 on 25 November about noon:
2.19 design hits still expected); the sieve is taken as half the cost per member and proportional to the rows.
"""
import sys, math, numpy as np
from statistics import NormalDist
ND = NormalDist(); S = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'fscan', 'cover', 'starts', '')
BUD = float(sys.argv[1]) if len(sys.argv) > 1 else 31.08; QMAX = 260000
sv = np.ones(QMAX, dtype=bool); sv[:2] = False
for i in range(2, int(QMAX ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
sv[2] = False; q = np.nonzero(sv)[0]; L = 200 * math.log(10); w = math.log(463) / math.log(1e8); z0 = ND.inv_cdf(0.015)
def load(f):
    l = [x for x in open(S + f) if x.startswith("COVER")][0].split(); cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in l if ":" in t]
    alive = np.ones(len(q), dtype=bool)
    for r, a in cov: alive &= (q % r) != a
    return q[alive], 2 * math.prod(r / (r - 1) for r, _ in cov) / L
ref = None; res = {}
print(f"budget e^{BUD} effective members at the 170,000 design; sd of the survivors 0.962 of independent; cut at the emptiest 1.5%")
print("design | rows at design | exponent | tilt p'*sd | captured share at the cut | cost per member vs 170,000 | design hits expected | P(>=180k) | P(>=190k) | P(>=200k) | P(>=213,070)")
for D, f in ((170000, "q170000_m89.txt"), (180000, "q180000_m89.txt"), (190000, "q190000_m89.txt"), (200000, "q200000_m89.txt"), (213070, "q213070_m89.txt")):
    rows, p = load(f); n = int((rows < D).sum()); E = -n * math.log(1 - p)
    tau = (p / w) * 0.962 * math.sqrt(n * w * (1 - w)); cap = ND.cdf(z0 + tau); cost = 0.5 * n / 1248 + 0.5
    if ref is None: ref = cap
    hits = math.exp(BUD - E) * (cap / ref) / cost
    ps = []
    for G in (180000, 190000, 200000, 213070):
        extra = int(((rows >= D) & (rows < G)).sum()) if G > D else 0
        lam = hits * (1 - p) ** extra if G >= D else float("nan")
        ps.append(1 - math.exp(-lam) if G >= D else float("nan"))
    print(f"{D} | {n} | {E:.2f} | {tau:.3f} | {cap:.3f} | {cost:.3f} | {hits:.4f} | " + " | ".join(f"{100 * x:.3f}%" if x == x else "-" for x in ps))
