"""The same-class pair sum averaged over ALL covers, exactly.

For a cover with a nonzero class a_r for every odd prime r <= 463, an odd prime q < Q is a row when q != a_r (mod r)
for every r.  For two distinct primes q, q' the number of nonzero classes a_r that leave both is
   r - 1 - #({q mod r, q' mod r} minus {0}),
that is r - 2 when r divides q - q' (or one of them is r itself) and r - 3 otherwise, and the classes of different
moduli are free.  So, averaged over all class vectors, the number of ordered pairs of rows (q, q') equals the sum over
ordered pairs of primes of  prod_r (r - 1 - nu_r)/(r - 1),  with no cover in it; the same with any weight on the pair.
This script evaluates the averages of n, n(n-1) and T = sum over pairs with a common class modulo s0 > 463 of
1/(s0 - 2), and the ratio  E T / (E n(n-1) x sum_{463 < s < Q} 1/((s-1)(s-2)))  to set against the measured covers.
  python class_average.py [Q]"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from covlib import primes_upto

Q = int(sys.argv[1]) if len(sys.argv) > 1 else 200000; Z = 463
PR = primes_upto(Q - 1); odd = PR[1:]; MODS = [int(r) for r in odd if r <= Z]
s0 = np.zeros(Q, dtype=np.int64)
for s in PR[(PR > Z) & (PR < Q)]: s0[s::s] = s
inv = np.where(s0 > 0, 1.0 / np.maximum(s0 - 2, 1), 0.0)
big = PR[(PR > Z) & (PR < Q)].astype(np.float64); Srand = float(np.sum(1.0 / ((big - 1) * (big - 2))))
# weight of a pair of primes above 463 by its difference
d = np.arange(Q); wd = np.ones(Q)
for r in MODS: wd *= np.where(d % r == 0, (r - 2.0) / (r - 1.0), (r - 3.0) / (r - 1.0))
single = math.prod((r - 2.0) / (r - 1.0) for r in MODS)
hi = odd[odd > Z]; ind = np.zeros(Q); ind[hi] = 1.0
L = 1 << int(math.ceil(math.log2(2 * Q))); F = np.fft.rfft(ind, L); C = np.rint(np.fft.irfft(F * np.conj(F), L)[:Q])       # ordered pairs q' - q = d > 0
C[0] = 0
En = len(hi) * single; Epairs = 2 * float((C * wd).sum()); ET = 2 * float((C * wd * inv).sum())
# pairs with a prime up to 463 (itself a modulus): done directly
lo = [int(q) for q in odd if q <= Z]
def wpair(q, others):
    w = np.ones(len(others))
    for r in MODS:
        a = q % r; b = others % r
        nu = (b != 0).astype(np.int64) + (1 if a != 0 else 0) - ((b == a) & (b != 0)).astype(np.int64) * (1 if a != 0 else 0)
        w *= (r - 1.0 - nu) / (r - 1.0)
    return w
for i, q in enumerate(lo):
    En += math.prod((r - 2.0) / (r - 1.0) for r in MODS if r != q)
    others = np.array([x for x in odd if x != q and (x > Z or x > q)], dtype=np.int64)      # each unordered pair once
    w = wpair(q, others); dd = np.abs(others - q)
    Epairs += 2 * float(w.sum()); ET += 2 * float((w * inv[dd]).sum())
print(f"Q = {Q:,d}, moduli 3..{Z} ({len(MODS)}), odd primes below Q: {len(odd):,d}")
print(f"average over all covers: rows E n = {En:.2f}; ordered pairs E n(n-1) = {Epairs:.1f} (E n squared {En * En:.1f}); same-class pair sum E T = {ET:.3f}")
print(f"E T / (E n(n-1) x sum 1/((s-1)(s-2))) = {ET / (Epairs * Srand):.4f}     [rows placed at random would give 1]")
print(f"sum over 463 < s < Q of 1/((s-1)(s-2)) = {Srand:.6e}")
