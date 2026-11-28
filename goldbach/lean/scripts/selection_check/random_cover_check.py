"""Does the variance deficit belong to the good covers or to any cover?  The same formula (exact constants, B = 1e8,
Q = 200,000) for: the first cover of the file; a greedy cover (each modulus 3..463 in turn takes the class holding the
most rows left); and covers with a random nonzero class for every modulus.  The pair sum scales like rows^2, so the
comparable number is  sum_{i != j} (rho_ij - 1) / rows^2."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from covlib import primes_upto, read_covers, rows_of

Q = 200000; B = 10 ** 8; Z = 463
PR = primes_upto(B); big = PR[PR > Z].astype(np.float64)
w = math.exp(float(np.sum(np.log1p(-1.0 / big)))); R = math.exp(float(np.sum(np.log1p(-1.0 / (big - 1.0) ** 2))))
s0 = np.zeros(Q, dtype=np.int64)
for s in PR[(PR > Z) & (PR < Q)]: s0[s::s] = s
inv = np.where(s0 > 0, 1.0 / np.maximum(s0 - 2, 1), 0.0)
ODD = primes_upto(Q - 1)[1:]; MODS = [int(x) for x in PR[(PR >= 3) & (PR <= Z)]]
Trand = float(np.sum(1.0 / ((big[big < Q] - 1) * (big[big < Q] - 2))))          # same-class pairs per ordered pair for rows placed at random

def report(name, classes):
    rows = rows_of(classes, Q, ODD); n = len(rows)
    out = []
    for start in range(0, n, 2000):                                             # in slices, the difference matrix of a large cover is big
        d = np.abs(rows[start:start + 2000, None] - rows[None, :]); out.append(float(inv[d].sum()))
    T = sum(out); pair = n * (n - 1) * (R - 1) + R * T; ind = n * w * (1 - w); var = ind + w * w * pair
    disp = []
    for s in [x for x in PR[(PR > Z) & (PR <= 997)]]:
        K = np.bincount(rows % int(s), minlength=int(s)).astype(np.float64)[1:]; disp.append(K.var() / K.mean())
    print(f"{name} | {n} | {T:.1f} | {n * (n - 1) * Trand:.1f} | {T / (n * (n - 1) * Trand):.4f} | {pair:+.1f} | {pair / n ** 2:+.3e} | {ind:.1f} | {var:.1f} | {math.sqrt(var / ind):.4f} | {np.mean(disp):.3f}", flush=True)

print("cover | rows | same-class pair sum T | T for rows placed at random | ratio | pair sum | pair sum / rows^2 | binomial variance | Var S | sd ratio | variance/mean of class counts, 467..997")
claimed, best = read_covers("data/q200000_m89.txt")[0]
report("best cover of the file", best)
# greedy cover
rows = ODD.copy(); greedy = {}
for r in MODS:
    cnt = np.bincount(rows % r, minlength=r); a = int(cnt.argmax()); greedy[r] = a; rows = rows[rows % r != a]
report("greedy cover", greedy)
rng = np.random.default_rng(2026)
for t in range(5):
    report(f"random classes {t + 1}", {r: int(rng.integers(1, r)) for r in MODS})
# no cover at all: every odd prime below Q that is not a modulus (the limit of a cover that strikes nothing)
report("no classes (all odd primes below Q)", {})
