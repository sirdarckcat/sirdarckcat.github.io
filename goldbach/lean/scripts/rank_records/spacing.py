#!/usr/bin/env python3
"""How fast large values of g(N) thin out, and how far apart the largest ones sit.

    python3 -I spacing.py cand.txt hist.txt X > spacing.txt

hist.txt: "g count" for every value of the least Goldbach summand over the even N <= X.
cand.txt: "N g" for the N above the scan threshold (enough to know the ten largest at any time).

1. Tail.  T(m) = number of even N <= X whose least summand is at least the m-th odd prime.
   Each further prime removes a fixed fraction: T(m + 1) / T(m) = exp(-r / (ln X - 1)), with r
   falling slowly from 2 (the mean of the Goldbach singular series) towards 2 C2 = 1.3203 (its
   least value, for N with no small odd prime factor), because the N that last are those with
   the fewest representations.
2. Spacing.  If the tail is geometric in the index of the prime, the largest values behave
   like the top order statistics of an exponential sample: with pi(g) the index of g,
   j * (pi(g_j) - pi(g_{j+1})) has mean (ln X - 1) / r for every j (g_1 >= g_2 >= ... the
   largest values up to X).  The table lists the ten largest values at each power of ten and
   the average of that quantity over j = 1..9.
"""
import math
import sys
import numpy as np

C2 = 0.6601618158468696


def primes_upto(n):
    sv = np.ones(n + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]: sv[i * i::i] = False
    return np.nonzero(sv)[0]


def main():
    cand, hist, X = sys.argv[1], sys.argv[2], int(float(sys.argv[3]))
    gs, cs = [], []
    for line in open(hist):
        if line.startswith('#'): continue
        g, c = line.split(); gs.append(int(g)); cs.append(int(c))
    odd = primes_upto(max(gs) + 10); odd = odd[odd > 2]
    idx = {int(p): i + 1 for i, p in enumerate(odd)}
    full = np.zeros(len(odd) + 2)
    for g, c in zip(gs, cs): full[idx[g]] = c
    tail = np.cumsum(full[::-1])[::-1]
    lnx = math.log(X) - 1
    print(f"# X = {X}: the mean of ln N over N <= X is ln X - 1 = {lnx:.2f}; 2 C2 = {2 * C2:.4f}")
    print("\n## 1. tail: m, m-th odd prime, T(m), r = (ln X - 1) * ln(T(m) / T(m + 20)) / 20")
    rates = {}
    for m in (5, 10, 20, 40, 60, 80, 100, 130, 160, 200, 240, 280, 320, 360, 400):
        if m + 20 >= len(tail) or tail[m + 20] < 100: break
        r = math.log(tail[m] / tail[m + 20]) / 20 * lnx; rates[m] = r
        print(f"{m:5d} {int(odd[m - 1]):6d} {tail[m]:16.0f}   {r:.3f}")

    print("\n## 2. the ten largest values at each power of ten; mean over j = 1..9 of j * (pi(g_j) - pi(g_{j+1})),")
    print("##    and the same divided by (ln X' - 1)   (X' the power of ten; 1 / r is expected)")
    rows = [tuple(map(int, line.split())) for line in open(cand)]
    e = 5
    top = []
    pos = 0
    allq = []
    while 10 ** e <= X:
        lim = 10 ** e
        while pos < len(rows) and rows[pos][0] <= lim:
            top.append(rows[pos][1]); pos += 1
        top = sorted(top, reverse=True)[:10]
        ii = [idx[g] for g in top]
        d = [j * (ii[j - 1] - ii[j]) for j in range(1, 10)]
        q = np.mean(d) / (math.log(lim) - 1); allq.append(q)
        print(f"10^{e}: {' '.join(map(str, top))}   mean {np.mean(d):6.2f}   / (ln X' - 1) = {q:.3f}")
        e += 1
    print(f"\naverage of the last column: {np.mean(allq):.3f}   (1 / r for r = 1.5: {1 / 1.5:.3f}; for r = 2 C2: {1 / (2 * C2):.3f})")


main()
