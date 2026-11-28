# Follow-up to additive_chars.py: where are the large additive characters of U modulo the later primes, what makes them, and what
# share of the score's variance do they carry? For a cover's rows U and a prime s, the class counts c_s(a) have Fourier power
# |F_s(h)|^2/|U| at h. A peak at (s, h) is explained if h/s lies within ~1/G of a rational c/d where U's own transform on R/Z,
# T(x) = sum_{q in U} e(q x), is large (d built from small cover moduli, where U sits in few classes).
#   python3 additive_peaks.py > additive_peaks.out
import numpy as np, math
from fractions import Fraction
G = 200000
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
odd = primes_upto(G); odd = odd[odd > 2]
lines = [l for l in open("../covers/q200000_m89.txt") if l.startswith("COVER")]
def rows(line):
    cov = [tuple(map(int, w.split(":"))) for w in line.split() if ":" in w]
    alive = np.ones(len(odd), bool)
    for r, a in cov: alive &= (odd % r) != a
    return odd[alive], cov
later = [int(p) for p in primes_upto(1999) if p > 463]
DIVS = sorted({a * b * c * d * e * f for a in (1, 2) for b in (1, 3) for c in (1, 5) for d in (1, 7) for e in (1, 11) for f in (1, 13)} - {1})

def T(U, x):            # U's transform at a real frequency x
    return complex(np.sum(np.exp(2j * np.pi * U.astype(float) * x)))

tot_share1 = []; tot_share5 = []
for ci in range(3):
    U, cov = rows(lines[ci]); n = len(U)
    peaks = []; var_tot = 0.0; var_top1 = 0.0; var_top5 = 0.0
    for s in later:
        c = np.bincount(U % s, minlength=s).astype(float)
        F = np.fft.fft(c); pw = np.abs(F[1:(s + 1) // 2]) ** 2 / n
        v = np.sum(np.abs(F[1:]) ** 2) / s ** 2            # variance of c_s over the classes
        o = np.argsort(-pw)
        v1 = 2 * pw[o[0]] * n / s ** 2; v5 = 2 * np.sum(pw[o[:5]]) * n / s ** 2
        var_tot += v; var_top1 += v1; var_top5 += v5
        peaks.append((pw[o[0]] / math.log(s), s, int(o[0]) + 1, pw[o[0]]))
    peaks.sort(reverse=True)
    tot_share1.append(var_top1 / var_tot); tot_share5.append(var_top5 / var_tot)
    print(f"cover {ci}: |U| = {n}; score variance over the 213 primes (sum of per-prime class-count variances) {var_tot:.1f}"
          f" (sd {math.sqrt(var_tot):.2f} rows); share in each prime's top frequency {100*var_top1/var_tot:.2f}%, top 5: {100*var_top5/var_tot:.2f}%")
    for pl, s, h, p in peaks[:6]:
        x = h / s
        # explanation: the rational c/d with d | 2*3*5*7*11*13 nearest to h/s among those where U's own transform is large
        best = None
        for d in DIVS:
            cc = round(x * d)
            if cc == 0 or math.gcd(cc, d) != 1: continue
            Td = abs(T(U, cc / d)) ** 2 / n
            if Td < 50: continue
            dist = G * abs(x - cc / d)
            if best is None or dist < best[0]: best = (dist, cc, d, Td)
        expl = (f"h/s within {best[0]:.2f}/G of {best[1]}/{best[2]}, where |T|^2/|U| = {best[3]:.0f}" if best else "no c/d with |T|^2/|U| >= 50")
        print(f"   s = {s}, h = {h}: power {p:.1f} = {pl:.2f} ln s; {expl}")
print(f"\nover 3 covers: share of the score variance in the top frequency of each prime {100*np.mean(tot_share1):.2f}%, top 5 {100*np.mean(tot_share5):.2f}%")
# U's own transform at small denominators d | 3*5*7*11*13: the peaks of T on R/Z
U, cov = rows(lines[0]); n = len(U)
print("\nU's transform at rationals c/d (cover 0), the largest |T|^2/|U| for each small d:")
for d in (3, 5, 7, 15, 21, 35, 105, 1155, 15015):
    best = max(((abs(T(U, c / d)) ** 2 / n), c) for c in range(1, d) if math.gcd(c, d) == 1)
    print(f"   d = {d}: max over c of |T(c/d)|^2/|U| = {best[0]:.0f} (c = {best[1]})")

# noise baseline for the variance share in each prime's top frequency: random subsets of the odd primes of the same size
rng = np.random.default_rng(7); sh = []
for _ in range(20):
    R = np.sort(rng.choice(odd, n, replace=False)); vt = 0.0; v1 = 0.0
    for s in later:
        c = np.bincount(R % s, minlength=s).astype(float); F = np.fft.fft(c); pw = np.abs(F[1:(s + 1) // 2]) ** 2 / n
        vt += np.sum(np.abs(F[1:]) ** 2) / s ** 2; v1 += 2 * pw.max() * n / s ** 2
    sh.append(v1 / vt)
print(f"\nbaseline (20 random subsets of the odd primes, same size): share in each prime's top frequency {100*np.mean(sh):.2f}%")
# the largest possible gain from aligning every prime's top wave at once: sum over primes of the wave amplitude 2|F|/s, in rows
U, cov = rows(lines[0]); amp = 0.0
for s in later:
    c = np.bincount(U % s, minlength=s).astype(float); F = np.fft.fft(c)[1:(s + 1) // 2]; amp += 2 * np.abs(F).max() / s
print(f"cover 0: sum over the 213 primes of each top wave's amplitude 2|F_s(h)|/s = {amp:.2f} rows (the score's sd is about 16 rows)")
