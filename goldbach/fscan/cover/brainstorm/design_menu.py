# What each design level buys: chances of reaching far thresholds, and the expected final record.
#
#   python3 brainstorm/design_menu.py days rate record label:coverfile[:rows_ref] ...        (run from cover/)
#
# For every file the cover with the best expected final record is taken (model of rank_covers.py) and its line shows
# P(final record >= x) for a list of x, the expected and the median final record.  rate is the effective member rate
# of the present design; a design with more rows below its own level is slowed by the sieve's share of the work:
# rate * 1 / (1 - SIEVE + SIEVE * rows / ROWS0), rows = uncovered rows below the level the engine would run (the
# number after the second colon, default: the cover's rows below 170,000, i.e. no slowdown).
import math, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
from rank_covers import Model, read_covers
days, rate, hand = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
SIEVE = 0.5; ROWS0 = 1250.0
XS = (170000, 175000, 180000, 185000, 190000, 195000, 200000, 213070)
print(f"{days} days at {rate/1e6:.0f}M effective members/s for a 1,250-row design, record in hand {hand}; sieve share of the work {SIEVE}")
print("design | rows below 170,000 / below the design level | rate factor | " + " | ".join(f">= {x:,}" for x in XS) + " | expected | median")
for arg in sys.argv[4:]:
    t = arg.split(":"); label, f = t[0], t[1]; level = int(t[2]) if len(t) > 2 else 170000
    best = None
    M0 = Model(days, rate, hand, 170000)
    iL = int(np.searchsorted(M0.P, level))
    for c in read_covers(f):
        u = M0.uncovered(c); rows_level = int(u[:iL].sum()); fac = 1 / (1 - SIEVE + SIEVE * max(rows_level, ROWS0) / ROWS0)
        cum, m = M0.members_above(c); m = m * fac
        e = hand + float(np.sum(1 - np.exp(-m))) * 20
        if best is None or e > best[0]: best = (e, m, int(u[:M0.iQ].sum()), rows_level, fac)
    e, m, k170, kl, fac = best
    pr = [1 - math.exp(-float(m[np.searchsorted(M0.xs, x)])) for x in XS]
    med = int(M0.xs[np.searchsorted(-(1 - np.exp(-m)), -0.5)])
    print(f"{label} | {k170} / {kl} | {fac:.3f} | " + " | ".join(f"{p:.4f}" if p >= 0.001 else f"{p:.1e}" for p in pr) + f" | {e:,.0f} | {med:,}")
