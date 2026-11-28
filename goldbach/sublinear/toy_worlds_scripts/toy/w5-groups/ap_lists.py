#!/usr/bin/env python3
"""How far are the real tables from the two solvable cases?  For each of the 30 primes s after 463 (tables hit_s(c) = rows of
the 200,000 cover in class c) and a list length l (one nat of constraint: l = s/e; and l = s/3):
   (all four are printed as the mean hits of a member whose class is in the list, minus n0/s)
   free   = rows in the best l classes (any list: what a dynamic programme or a scan can use)
   AP     = rows in the best list of the form {a + i d : 0 <= i < l} over all a and all d != 0 (what lattice methods can use)
   intv   = the same with d = 1 (intervals of classes)
   arc    = the same with d = P/s mod s, P = 2 * prod of all primes <= 599: an arc in the labelling c -> c u_s / s of the
            constraint character itself (what a dynamic programme of low precision could use)
   mean   = n0 * l / s
The same for random tables (1502 balls into s classes, 20 draws each).  Also the largest |Fourier coefficient| / sqrt(n0)."""
import math, numpy as np, common as C
rng = np.random.default_rng(7)
js = C.later_primes(30); lt = C.later_tables(js); P = C.M * math.prod(js)
def stats(h, s, l, dspec):
    srt = np.sort(h)[::-1]; free = int(srt[:l].sum()); best = 0; intv = 0; arc = 0
    idx = np.arange(s)
    for d in range(1, (s - 1) // 2 + 1):
        seq = h[(idx * d) % s]; cs = np.concatenate([[0], np.cumsum(np.concatenate([seq, seq[:l]]))])
        w = int((cs[l:l + s] - cs[:s]).max()); best = max(best, w)
        if d == 1: intv = w
        if d == dspec or d == s - dspec: arc = w
    return free, best, intv, arc
for frac_name, lf in (("l = s/e (1 nat)", lambda s: round(s / math.e)), ("l = s/3 (1.10 nats)", lambda s: round(s / 3)), ("l = s/20 (3 nats)", lambda s: round(s / 20))):
    acc = np.zeros(4); accr = np.zeros(4); nat = 0; mu = 0
    for s in js:
        l = lf(s); h = lt[s]; dspec = (P // s) % s; mean = C.n0 / s           # mean hits of a member at s
        acc += np.array(stats(h, s, l, dspec)) / l - mean; nat += math.log(s / l); mu += mean
        for _ in range(4):
            hr = np.bincount(rng.integers(0, s, C.n0), minlength=s)
            accr += (np.array(stats(hr, s, l, dspec)) / l - mean) / 4
    n = len(js)
    print(f"{frac_name}: expected rows hit by a member whose class lies in the list, above the mean ({mu / n:.2f}), per prime:"
          f"\n      real tables:    free list {acc[0] / n:5.2f}   best AP {acc[1] / n:5.2f}   interval {acc[2] / n:5.2f}   arc of the constraint character {acc[3] / n:5.2f}"
          f"\n      random tables:  free list {accr[0] / n:5.2f}   best AP {accr[1] / n:5.2f}   interval {accr[2] / n:5.2f}   arc {accr[3] / n:5.2f}"
          f"\n      rows per nat of constraint (real): free {acc[0] / nat:.2f}, AP {acc[1] / nat:.2f}, interval {acc[2] / nat:.2f}, arc {acc[3] / nat:.2f}; AP/free = {acc[1] / acc[0]:.2f}, arc/free = {acc[3] / acc[0]:.2f}")
mx = []; mxr = []
for s in js:
    F = np.abs(np.fft.fft(lt[s]))[1:]; mx.append(F.max() / math.sqrt(C.n0))
    hr = np.bincount(rng.integers(0, s, C.n0), minlength=s); mxr.append(np.abs(np.fft.fft(hr))[1:].max() / math.sqrt(C.n0))
print(f"largest additive Fourier coefficient / sqrt(n0): real {np.mean(mx):.2f} (max {np.max(mx):.2f}); random {np.mean(mxr):.2f} (max {np.max(mxr):.2f}); sqrt(ln s) = {math.sqrt(math.log(500)):.2f}")
