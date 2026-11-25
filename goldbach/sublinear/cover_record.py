#!/usr/bin/env python3
"""The distribution of the campaign's final record when every tested member's g counts (model; 200 digits).

    python3 cover_record.py [cover file ...]      default: the 170,000 to 200,000 covers of ../fscan/cover/starts

A kept member's survivors are tested in increasing q until the first probable prime, so the row of that prime is
the member's g, whether or not it reaches the design level D.  For a cover built for D (the sieve and the cut act
on the rows below D), with n(x) rows below x, lam = -ln(1 - p), lam' = -ln(1 - p/w) for a survivor:

    mu(x) = members * exp(-lam n(x)) * Phi(z0 + tau n(x)/n(D))            x <= D   (kept, and nothing prime below x)
    mu(x) = mu(D) * exp(-lam (n(x) - n(D)))                                x >  D   (rows beyond D are not sieved)
    P(final record >= x) = 1 - exp(-mu(x))   for x above the record held (160,357),

tau = lam' * 0.9836 sqrt(n(D) w (1 - w)) (the survivors' sd, as measured), z0 the 1.5% cut, w = 0.336642 the share
of rows that survive the sieve to 10^8.  The cut acts on all the rows below D, so a member whose rows below x are
all composite is kept more often than a random one by the part of the tilt that those rows carry.
Members: 1.90 expected design hits at 170,000 as the fleet runs (1,250.5 rows there, 5.5 above the best cover; 4.5
above the file's cover at the other levels), cost per member 26% sieve (proportional to the rows) and 74% tests,
exponent averaged over a window uniform in N (factor 36.54/36.46).  A file may be given as name:D to say what
level its cover is used at (the rows below D are sieved and counted for the cut), or name:D:extra.
"""
import sys, os, math, numpy as np
from statistics import NormalDist
ND = NormalDist(); HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(HERE, "..", "fscan", "cover", "starts", "")
QMAX = 260000; HELD = 160357; W = 0.336642; Z0 = ND.inv_cdf(0.015); LN = 200 * math.log(10); AVG = 36.54 / 36.46
sv = np.ones(QMAX, dtype=bool); sv[:2] = False
for i in range(2, int(QMAX ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
sv[2] = False; PR = np.nonzero(sv)[0]
GRID = np.arange(HELD + 1, 230001)

def load(f):
    l = [x for x in open(f) if x.startswith(("COVER", "BEST"))][0].split(); cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in l if ":" in t]
    alive = np.ones(len(PR), dtype=bool)
    for r, a in cov: alive &= (PR % r) != a
    return PR[alive], 2 * math.prod(r / (r - 1) for r, _ in cov) / LN

def curve(rows, p, D, extra, members):
    """mu(x) on GRID for a cover used at design level D; extra = rows above the best cover that the fleet runs"""
    lam = -math.log(1 - p) * AVG; lamp = -math.log(1 - p / W) * AVG
    nD = int((rows < D).sum()); scale = (nD + extra) / nD
    n = np.searchsorted(rows, GRID, side="left") * 1.0            # rows below x
    nrun = np.where(GRID <= D, n * scale, nD * scale + (n - nD))
    tau = lamp * 0.9836 * math.sqrt(nD * scale * W * (1 - W))
    share = np.minimum(n / nD, 1.0)
    cap = np.array([ND.cdf(Z0 + tau * s) for s in share])
    cost = 0.26 * nD * scale / 1250.5 + 0.74
    return members / cost * np.exp(-lam * nrun) * cap, nD * scale, tau

def budget():
    rows0, p0 = load(f"{S}q170000_m89.txt"); mu0, _, _ = curve(rows0, p0, 170000, 1250.5 - int((rows0 < 170000).sum()), 1.0)
    return 1.90 / mu0[170000 - HELD - 1]

def summary(mu):
    P = 1 - np.exp(-mu); E = HELD + P.sum()
    at = lambda x: P[x - HELD - 1]
    return E, [at(x) for x in (165000, 170000, 175000, 180000, 185000, 190000, 195000, 200000, 213070)]

if __name__ == "__main__":
    files = sys.argv[1:] or [f"{S}q{D}_m89.txt:{D}" for D in (170000, 175000, 180000, 190000, 200000)]
    members = budget()
    print("record held 160,357; 1.90 design hits expected at 170,000 as the fleet runs; every tested member's g counted")
    print("cover | design level | rows run | tilt | E[final record] | P(final >=) 165,000 | 170,000 | 175,000 | 180,000 | 185,000 | 190,000 | 195,000 | 200,000 | 213,070")
    curves = {}
    for a in files:
        t = a.split(":"); f = t[0]; rows, p = load(f); D = int(t[1]) if len(t) > 1 else int(os.path.basename(f)[1:7])
        extra = float(t[2]) if len(t) > 2 else (1250.5 - int((rows < D).sum()) if os.path.basename(f) == "q170000_m89.txt" and D == 170000 else 4.5)
        mu, n, tau = curve(rows, p, D, extra, members); curves[a] = mu
        E, ps = summary(mu)
        print(f"{os.path.basename(f)} | {D} | {n:.1f} | {tau:.3f} | {E:,.0f} | " + " | ".join(f"{100 * x:.2f}%" if x < 0.1 else f"{100 * x:.1f}%" for x in ps))
    if len(files) >= 2 and not sys.argv[1:]:
        a, b = files[0], files[-1]
        print("\nthe budget split between the first and the last cover (share on the last | E[final record] | P(>= 180,000) | P(>= 190,000) | P(>= 200,000))")
        for s in (0, 0.25, 0.5, 0.75, 1):
            E, ps = summary((1 - s) * curves[a] + s * curves[b])
            print(f"{s} | {E:,.0f} | {100 * ps[3]:.2f}% | {100 * ps[5]:.2f}% | {100 * ps[7]:.3f}%")
