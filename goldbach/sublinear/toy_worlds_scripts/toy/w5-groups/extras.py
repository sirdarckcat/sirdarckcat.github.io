#!/usr/bin/env python3
"""(a) rows per nat of a pin (a list of one class: the best class of s) for the 30 primes after 463, to set beside ap_lists.txt.
(b) how far the separable (first-order) score is from the true number of rows left, on the points listed by the meet in the
    middle (files mitm_j*_s*_k*.pkl): distribution of exact - first-order."""
import math, pickle, glob, numpy as np, common as C
js = C.later_primes(30); lt = C.later_tables(js)
g = [(int(lt[s].max()) - C.n0 / s) for s in js]; nat = [math.log(s) for s in js]
print(f"(a) pin: best class minus mean, per prime {np.mean(g):.2f} rows for {np.mean(nat):.2f} nats = {sum(g) / sum(nat):.2f} rows per nat (first 8 later primes: {sum(g[:8]) / sum(nat[:8]):.2f})")
for f in sorted(glob.glob("mitm_j*_s*_k*.pkl")):
    pts = pickle.load(open(f, "rb"))[:1500]
    if not pts: continue
    j = int(f.split("_j")[1].split("_")[0]); ls = C.later_primes(j)
    d = np.array([len(C.rows_of([(r, x % r) for r, _ in C.cov] + [(s, x % s) for s in ls])) - s0 for s0, x in pts])
    ex = np.array([s0 for s0, x in pts]) + d
    print(f"(b) {f}: {len(pts)} points; exact - first-order: mean {d.mean():+.2f}, sd {d.std():.2f}, min {d.min():+d}, max {d.max():+d}; least exact rows {ex.min()} (least first-order {min(s0 for s0, x in pts)})")
