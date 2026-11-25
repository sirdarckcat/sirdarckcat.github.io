"""Item 1, folded primes, recomputed from the cover file alone.
For s = 467, 479, 487, ... in turn: the class of s holding the most rows still left (K_max); the gain in nats by the
first-order formula  p (K_max - (rows - K_max)/(s - 1));  the same gain exactly, as the log of the ratio of the two
products of (1 - chance of a prime) over the rows; then those rows are removed, p is multiplied by s/(s - 1) and the
window (the number of members of the cover below 10^200) is divided by s.
  python fold_check.py FILE [Q] [LINE]"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from covlib import primes_upto, read_covers, rows_of, base_probability

path = sys.argv[1]; Q = int(sys.argv[2]) if len(sys.argv) > 2 else 200000; line = int(sys.argv[3]) if len(sys.argv) > 3 else 0
claimed, classes = read_covers(path)[line]
P = [int(x) for x in primes_upto(2000)]
mods = sorted(classes)
print(f"cover line {line}: {len(mods)} moduli, {mods[0]}..{mods[-1]}; they are the odd primes up to {mods[-1]}: {mods == [x for x in P if 3 <= x <= mods[-1]]}; "
      f"classes below their modulus: {all(0 <= classes[r] < r for r in mods)}")
rows = rows_of(classes, Q); n = len(rows)
print(f"rows (odd primes below {Q:,d} in none of the classes): {n} (the line says {claimed})")
p = base_probability(classes)
lnM = math.log(2) + sum(math.log(r) for r in mods)
window = 200 * math.log(10) - lnM
print(f"p = 2 prod r/(r-1) / (200 ln 10) = {p:.5f};  window = ln(10^200 / (2 prod r)) = {window:.2f} nats = 2^{window / math.log(2):.1f} members")
print(f"exponent of the cover: rows x p = {n * p:.2f} nats;  exactly, -rows x ln(1 - p) = {-n * math.log(1 - p):.2f}")
print("\ns | rows before | mean class rows/s | K_max | classes reaching K_max | gain, first order | gain, exact | ln(average member / (1-p)^rows) | p after | rows after | window after, log2 | cumulative gain")
cum = 0.0
for s in [x for x in P if x > mods[-1]][:8]:
    cnt = np.bincount(rows % s, minlength=s); K = int(cnt.max()); best = np.nonzero(cnt == K)[0]
    gain1 = p * (K - (n - K) / (s - 1))
    p2 = p * s / (s - 1)
    exact = (n - K) * math.log(1 - p2) - n * math.log(1 - p)
    # the average member (its class modulo s uniform) against the product (1 - p)^rows that the gain is measured from
    avg = math.log(float(np.mean((1 - p2) ** (n - cnt.astype(np.float64))))) - n * math.log(1 - p)
    c = int(best[0]); rows = rows[rows % s != c]; window -= math.log(s); cum += gain1
    print(f"{s} | {n} | {n / s:.2f} | {K} | {len(best)} | {gain1:+.4f} | {exact:+.4f} | {avg:+.5f} | {p2:.5f} | {len(rows)} | {window / math.log(2):+.1f} | {cum:+.3f}")
    n = len(rows); p = p2
