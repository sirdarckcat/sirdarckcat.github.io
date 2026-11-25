#!/usr/bin/env python3
"""What folding the next primes into the modulus buys (the lead's question (e)/(d), 25 November).

    python3 cover_fold.py cover.txt Q [index of the COVER/BEST line = 0]

A member of a cover has `rows` rows at Q; a random member lies in a random class modulo the next prime s and loses
rows/s of them, a member in the best class loses K_max.  Folding s into the modulus with that class is the same
selection the deep sieve makes inside a window, moved into the construction: it changes the exponent by
p (K_max - (rows - K_max)/(s - 1)) nats and divides the window by s.
"""
import sys, math, numpy as np
f, Q = sys.argv[1], int(sys.argv[2]); idx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
line = [l for l in open(f) if l.startswith("COVER") or l.startswith("BEST")][idx].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
sv = np.ones(Q, dtype=bool); sv[:2] = False
for i in range(2, int(Q ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
sv[2] = False
q = np.nonzero(sv)[0]; alive = np.ones(len(q), dtype=bool)
for r, a in cov: alive &= (q % r) != a
rows = q[alive]; L = 200 * math.log(10); p = 2 * math.prod(r / (r - 1) for r, _ in cov) / L
print(f"{len(cov)} moduli up to {cov[-1][0]}, rows at {Q}: {len(rows)}, p = {p:.5f}, exponent {-len(rows) * math.log(1 - p):.2f}")
allp = np.nonzero(np.concatenate([[False] * 3, np.ones(3000 - 3, dtype=bool)]))[0]
ps = [s for s in range(465, 1500, 2) if all(s % d for d in range(3, int(s ** .5) + 1, 2))]
cur = rows.copy(); tot = 0.0; lnwin = L - math.log(2) - sum(math.log(r) for r, _ in cov)
print(f"window: ln(X/M) = {lnwin:.1f} nats = 2^{lnwin / math.log(2):.1f} members")
print("prime s | rows before | mean class | best class K_max | gain, nats (sequential: each prime folded after the previous ones) | cumulative | members left per vector, log2")
for s in ps[:12]:
    c = np.bincount(cur % s, minlength=s); c[0] = 0; a = int(np.argmax(c)); K = int(c[a])
    gain = p * (K - (len(cur) - K) / (s - 1)); tot += gain; lnwin -= math.log(s)
    print(f"{s} | {len(cur)} | {len(cur) / (s - 1):.2f} | {K} | {gain:.3f} | {tot:.3f} | {lnwin / math.log(2):.1f}")
    cur = cur[cur % s != a]; p *= s / (s - 1)
