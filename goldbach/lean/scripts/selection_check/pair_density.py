"""Why the same-class pair sum T is about 0.856 of its value for rows placed at random, for every cover.

Model: the number of pairs of rows (q, q + d) is proportional to (Q - d) G(d), G the product over the moduli r <= 463
of the number of classes of q modulo r allowed by the four conditions "q and q + d are not 0, q and q + d are not a_r
(mod r)": r minus the number of distinct classes among 0, -d, a_r, a_r - d.  That is r - 2 when r divides d, r - 3
when d = +-a_r (mod r), and r - 4 otherwise; averaged over the classes of d not divisible by r it is
(r - 2)(r - 3)/(r - 1) whatever a_r is, so a difference divisible by r carries (r - 1)/(r - 3) times the average.
A difference with a prime factor above 463 is s0 k with k <= Q/s0 < 429: it has few small prime factors, hence fewer
pairs of rows than the average difference, and the classes of the cover enter only through which differences fall on
+-a_r.  Prediction:
   T / T_random = sum_d (Q - d) G(d) [d has a prime factor s0 > 463] / (s0 - 2)
                  / ( sum_d (Q - d) G(d) x sum_{463 < s < Q} 1/((s - 1)(s - 2)) ).
  python pair_density.py FILE Q [LINE]        also prints the measured value and the pair counts against the model"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from covlib import primes_upto, read_covers, rows_of

path = sys.argv[1]; Q = int(sys.argv[2]); line = int(sys.argv[3]) if len(sys.argv) > 3 else 0; Z = 463
claimed, classes = read_covers(path)[line]
PR = primes_upto(Q); d = np.arange(Q)
G = np.ones(Q); Gavg = np.zeros(Q); Gavg[6::6] = 1.0
for r, a in classes.items():
    dm = d % r
    allowed = np.where(dm == 0, r - 2, np.where((dm == a % r) | (dm == (-a) % r), r - 3, r - 4)).astype(np.float64)
    if a % r == 0: allowed = np.where(dm == 0, r - 1, r - 2).astype(np.float64)          # a class 0 excludes nothing new
    G *= allowed / r
    if r >= 5: Gavg[r::r] *= (r - 1.0) / (r - 3.0)
G[1::2] = 0.0                                                                           # q and q + d both odd
s0 = np.zeros(Q, dtype=np.int64)
for s in PR[(PR > Z) & (PR < Q)]: s0[s::s] = s
big = PR[(PR > Z) & (PR < Q)].astype(np.float64); Srand = float(np.sum(1.0 / ((big - 1) * (big - 2))))
inv = np.where(s0 > 0, 1.0 / np.maximum(s0 - 2, 1), 0.0)
for name, g in (("exact local factors of this cover", G), ("class-free average, (r - 1)/(r - 3) for each r >= 5 dividing d", Gavg)):
    wgt = (Q - d) * g; wgt[0] = 0
    print(f"model with the {name}: T / T_random = {float((wgt * inv).sum()) / (float(wgt.sum()) * Srand):.4f}")
rows = rows_of(classes, Q); n = len(rows)
diff = np.abs(rows[:, None] - rows[None, :]); C = np.bincount(diff.ravel(), minlength=Q).astype(np.float64); C[0] = 0     # ordered pairs by difference
print(f"measured on line {line} ({n} rows): T / T_random = {float((C * inv).sum()) / (n * (n - 1) * Srand):.4f}")
print(f"ordered pairs of rows at a difference not divisible by 6: {int(C[d % 6 != 0].sum())} of {n * (n - 1)}")
wgt = (Q - d) * G; wgt[0] = 0; scale = C.sum() / wgt.sum(); rel = G / G[G > 0].mean()
print("pairs of rows against the model, by the size of the local factor relative to its mean over the differences that can occur")
print("relative G from | to | differences | pairs of rows (ordered) | model | of which at differences with a prime factor above 463: pairs | model")
for lo, hi in ((0, 0.5), (0.5, 0.75), (0.75, 1), (1, 1.5), (1.5, 2.5), (2.5, 1e9)):
    m = (rel >= lo) & (rel < hi) & (G > 0); mb = m & (s0 > 0)
    print(f"{lo:g} | {hi:g} | {int(m.sum())} | {int(C[m].sum())} | {scale * wgt[m].sum():.0f} | {int(C[mb].sum())} | {scale * wgt[mb].sum():.0f}")
