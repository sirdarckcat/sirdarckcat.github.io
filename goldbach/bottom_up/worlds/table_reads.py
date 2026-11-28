# W4.4: what an exact selection must read when the sieve depth y is above the window K.
# At a prime s > K each class occupied by the window holds one member, so the table of s is a list of members.
# Counts per member of the window, for |U| rows (the 200,000 cover's 1,502; everything scales with |U|):
#   classes the sieve computes: |U| (pi(y) - pi(466)) / K          (one modular product a row a prime)
#   of which at primes above K:  |U| (pi(y) - pi(K)) / K            (the lower bound of W4.4)
#   strikes at primes above K:   |U| sum_{K<s<=y} 1/s               (members named by those tables, with multiplicity)
#   marks at primes up to K:     |U| sum_{467<=s<=K} 1/s            (strikes that come in progressions)
#   rows newly struck above K:   |U| (prod_{s<=K}(1-1/s) - prod_{s<=y}(1-1/s)), product over 467 <= s
#   python3 table_reads.py > table_reads.out
import math
import numpy as np

U = 1502
YMAX = 10 ** 8
sv = np.ones(YMAX + 1, bool); sv[:2] = False
for i in range(2, int(YMAX ** 0.5) + 1):
    if sv[i]: sv[i * i::i] = False
P = np.nonzero(sv)[0]; P = P[P >= 467]

print(f"rows |U| = {U}; later primes from 467; pi(1e7) - pi(466) = {int(np.sum(P <= 10**7)):,}, pi(1e8) - pi(466) = {len(P):,}")
print("window K | ln K | depth y | classes the sieve computes | of which above K (bound) | strikes above K | marks up to K | "
      "rows alive at K -> at y | rows newly struck above K   (all per member)")
for K in (2 ** 24, 16121856, 21378978):
    for y in (10 ** 7, 10 ** 8):
        Py = P[P <= y]; small = Py[Py <= K]; big = Py[Py > K]
        comp = U * len(Py) / K
        above = U * len(big) / K
        strikes_big = U * float(np.sum(1.0 / big))
        marks = U * float(np.sum(1.0 / small))
        aK = math.exp(float(np.sum(np.log1p(-1.0 / small))))
        ay = math.exp(float(np.sum(np.log1p(-1.0 / Py))))
        print(f"{K:,} | {math.log(K):.2f} | {y:.0e} | {comp:.1f} | {above:.1f} | {strikes_big:.1f} | {marks:.1f} | "
              f"{U * aK:.1f} -> {U * ay:.1f} | {U * (aK - ay):.1f}")
# the largest saving over the sieve that an exact method can have in the model, (classes + c * marks) / bound
for K in (16121856, 21378978):
    Py = P; small = Py[Py <= K]; big = Py[Py > K]
    comp = U * len(Py) / K; above = U * len(big) / K; marks = U * float(np.sum(1.0 / small))
    print(f"K = {K:,}, y = 1e8: largest saving over the sieve, marks free: x{comp / above:.2f}; a mark as dear as a class: "
          f"x{(comp + marks) / above:.2f}")
# the lattice route: all q < Q with ((q - N0) M^-1 mod s) < K number about Q K / s; it beats |U| products only above Q K / |U|
for K in (16121856, 21378978):
    for Q in (160367, 200000):
        print(f"K = {K:,}, Q = {Q:,}: the lattice route costs less than |U| a prime only for s > Q K/|U| = {Q * K / U:.2e}")
