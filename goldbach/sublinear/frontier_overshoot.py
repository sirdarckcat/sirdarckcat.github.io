#!/usr/bin/env python3
"""How far a hit runs beyond its target, against the model (the forecast's right tail rests on it).

    python3 frontier_overshoot.py <directory of the calibration runs' json files> [directory of the covers = dual_covers]

A member that reaches the target Q is then decided by the rows its cover leaves at and above Q, which the sieve did not touch:
each is prime with chance p = 2 prod r/(r-1) / ln N, so the number c of alive rows it survives beyond Q is geometric with mean
(1 - p)/p.  For every hit of a run (its k and its g; the cover gives the alive rows): c found against expected, and the mean of
the mid-PIT, which is 1/2 if the law is right.  The runs are the uarch session's calibration ladders at 100 and 150 digits
(goldbach/g200k/calib/*.json on ccr-b8c25887-i6tn9f: the cover's name, the target, and k and g of every hit), on the covers of
dual_covers/ here."""
import sys, json, math, re, os, numpy as np
DATA = sys.argv[1]; COV = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "dual_covers")
def primes(n):
    sv = np.ones(n, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if sv[i]: sv[i * i::i] = False
    sv[2] = False; return np.nonzero(sv)[0]
PR = primes(400000)
def cover(f):
    txt = open(f).read(); cov = [(int(a), int(b)) for a, b in re.findall(r"(\d+):(\d+)", txt)]
    if not cov:
        cov = [tuple(map(int, l.split()[:2])) for l in txt.splitlines() if l.strip() and l.split()[0].isdigit()]
    alive = np.ones(len(PR), dtype=bool)
    for r, a in cov: alive &= (PR % r) != a
    lnM = math.log(2) + sum(math.log(r) for r, _ in cov); C = 2 * math.prod(r / (r - 1) for r, _ in cov)
    return PR[alive], lnM, C, len(cov)
tot_c = tot_e = 0.0; pits = []; allz = []
print("run | target | hits | p a row | alive rows survived beyond the target: found, expected | ratio +- se | mean PIT (0.5 +- 0.289/sqrt n)")
for f in sorted(os.listdir(DATA)):
    d = json.load(open(os.path.join(DATA, f))); rows, lnM, C, nm = cover(os.path.join(COV, d["cover"])); Q = d["Q"]
    cs = []; es = []; ps = []
    for h in d["hits"]:
        lnN = lnM + math.log(h["k"] + 0.5); p = C / lnN
        c = int(((rows >= Q) & (rows < h["g"])).sum()); assert h["g"] in rows, (f, h)
        cs.append(c); es.append((1 - p) / p); ps.append(p)
        # randomized PIT of a geometric count: P(c' < c) + u P(c' = c)
        lo = 1 - (1 - p) ** c; hi = 1 - (1 - p) ** (c + 1); pits.append(0.5 * (lo + hi))
    cs = np.array(cs); es = np.array(es); n = len(cs)
    se = math.sqrt(sum((1 - p) / p ** 2 for p in ps)) / es.sum()
    print(f"{f[:-5]} | {Q} | {n} | {np.mean(ps):.4f} | {cs.sum()}, {es.sum():.0f} | {cs.sum() / es.sum():.3f} +- {se:.3f} | {np.mean(pits[-n:]):.3f} +- {0.289 / math.sqrt(n):.3f}")
    tot_c += cs.sum(); tot_e += es.sum(); allz.append((cs.sum(), es.sum(), sum((1 - p) / p ** 2 for p in ps), n))
var = sum(a[2] for a in allz); n = sum(a[3] for a in allz)
print(f"all | | {n} | | {tot_c:.0f}, {tot_e:.0f} | {tot_c / tot_e:.3f} +- {math.sqrt(var) / tot_e:.3f} | {np.mean(pits):.3f} +- {0.289 / math.sqrt(n):.3f}")
big = [a for a, f in zip(allz, sorted(os.listdir(DATA))) if not f.startswith("t_")]
c = sum(a[0] for a in big); e = sum(a[1] for a in big); v = sum(a[2] for a in big); print(f"without the 12,000 run | | {sum(a[3] for a in big)} | | {c:.0f}, {e:.0f} | {c / e:.3f} +- {math.sqrt(v) / e:.3f}")
