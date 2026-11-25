"""What any selection on the classes of the primes beyond the line could give at best, if it were free: every member
scored by its incidences with the primes 29..199 (the sum, over those primes, of the rows in the class of N), which is
the quantity that class lists, weighted lists and bucketing schemes select on.  Orders compared, all members:
  incidences alone;  cover first with ties broken by incidences;  rows left at depth 23 minus lambda times incidences."""
import math
import numpy as np
import pp
from classes import DEEP, W, RANK

N = np.asarray(pp.N); k1 = np.asarray(pp.K1).astype(np.int64); su = np.asarray(pp.SUCC)
inc = np.zeros(len(N), dtype=np.int16); hits3 = np.zeros(len(N), dtype=np.int8)
CH = 1 << 24
for a in range(0, len(N), CH):
    n = N[a:a + CH].astype(np.int64); t = np.zeros(len(n), dtype=np.int64); h = np.zeros(len(n), dtype=np.int64)
    for s in DEEP:
        r = n % s; t += W[s][r]; h += (RANK[s][r] < s // 3)
    inc[a:a + CH] = t; hits3[a:a + CH] = h
np.save("data/inc_deep.npy", inc)
print("# incidences with the primes 29..199: mean %.2f, sd %.2f over all members" % (inc.mean(), inc.std()))
def row(name, key):
    ex = pp.examined(key, su)
    g = [(math.log(pp.COVER[t] / ex[t]) if math.isfinite(ex[t]) else float("-inf")) for t in pp.TARGETS]
    print(f"{name} | " + " | ".join(f"{ex[t]:,.0f}" for t in pp.TARGETS) + " | " + " | ".join(f"{x:+.2f}" for x in g), flush=True)
print("order of all members | N examined for 1 | 3 | 10 | 30 successes | gain in nats over cover first at 1 | 3 | 10 | 30")
row("rows left at depth 23 (cover first)", k1)
row("rows left at depth 200 (ideal)", np.asarray(pp.K2).astype(np.int64))
imax = int(inc.max())
row("incidences with 29..199 alone, most first", (imax - inc).astype(np.int64))
row("number of primes 29..199 with N in the best third of classes, most first", (37 - hits3).astype(np.int64))
row("cover first, ties broken by incidences", k1 * 200 + (imax - inc))
for lam in (0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0):
    key = np.rint((k1 - lam * (inc - 75.0) + 60) * 20).astype(np.int64); key -= key.min()
    row(f"rows left at depth 23 - {lam} x (incidences - 75)", key)
