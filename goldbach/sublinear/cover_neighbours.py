#!/usr/bin/env python3
"""What the neighbours N + s of a cover's members can hold (a bound on any search seeded by near-successes).

    python3 cover_neighbours.py cover.txt Q [index of the COVER/BEST line = 0] [p = 0.02398]

A member N of a cover (N = a_r mod r) succeeds when N - q is composite for every row q (the odd primes below Q outside
every class).  The neighbour N + s has the rows q' with q' - s outside every class, and its number N + s - q' is
N - (q' - s): already decided by N when q' - s is an odd prime below Q (it is then a row of N; "inherited"), new otherwise
("undecided", U(s)).  A search that starts from members with few prime rows and tests their neighbours on clean shifts
(the consultant session's mechanism, 25 November) finds, whatever it knows about the seeds, at most the successes that
the neighbours hold: per success in the cover, sum over s of exp(-p (rows(N + s) - rows(N))) with rows(N + s) = U + I.
Per shift, a member passes its I inherited rows with chance exp(-p I) and its neighbour is then worth
exp(p (rows(N) - U(s))) fresh members.
"""
import sys, math, numpy as np
f = sys.argv[1]; Q = int(sys.argv[2]); line = [l for l in open(f) if l.startswith("COVER") or l.startswith("BEST")][int(sys.argv[3]) if len(sys.argv) > 3 else 0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
sv = np.ones(Q, dtype=bool); sv[:2] = False
for i in range(2, int(Q ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
sv[2] = False                                   # odd primes only
OFF = Q                                         # index n + OFF for n in [-Q, 2Q)
n = np.arange(-Q, 2 * Q); avoid = np.ones(3 * Q, dtype=bool)
for r, a in cov: avoid &= (n % r) != a
pr = np.zeros(3 * Q); pr[OFF:OFF + Q] = sv      # odd primes in [0, Q)
rows = avoid & (pr > 0); print("moduli", len(cov), "rows of N:", int(rows.sum()))
und = (avoid & ~(pr > 0)).astype(float)         # outside every class and not an odd prime below Q: undecided numbers
inh = rows.astype(float)
# U(s) = sum_n und[n] * pr[n + s];  I(s) = sum_n inh[n] * pr[n + s]   (cross-correlations, by FFT)
L = 1 << 21
Fp = np.fft.rfft(pr, L)
U = np.fft.irfft(np.conj(np.fft.rfft(und, L)) * Fp, L); I = np.fft.irfft(np.conj(np.fft.rfft(inh, L)) * Fp, L)
ss = np.arange(-Q + 2, Q, 2); ss = ss[ss != 0]
Us = np.rint(U[ss % L]).astype(int); Is = np.rint(I[ss % L]).astype(int)
# direct check of a few shifts
for s in (2, 30030, -2310, 510):
    qs = np.nonzero(sv)[0]; nn = qs - s; ok = avoid[nn + OFF]; dec = (pr[nn + OFF] > 0)
    assert int((ok & ~dec).sum()) == int(Us[np.nonzero(ss == s)[0][0]]) and int((ok & dec).sum()) == int(Is[np.nonzero(ss == s)[0][0]])
k0 = int(rows.sum())
print(f"even shifts 0 < |s| < {Q}: undecided rows U(s): min {Us.min()} at s = {ss[Us.argmin()]}, 1st percentile {np.percentile(Us, 1):.0f}, median {np.median(Us):.0f};  rows of N itself: {k0}")
for lim in (1000, 10000, 40000, Q):
    m = np.abs(ss) <= lim; j = np.argmin(Us[m]); print(f"  |s| <= {lim}: min U = {Us[m][j]} at s = {ss[m][j]} (inherited there {Is[m][j]}); most inherited: {Is[m].max()} at s = {ss[m][np.argmax(Is[m])]} with U = {Us[m][np.argmax(Is[m])]}")
order = np.argsort(Us)[:12]; print("  twelve smallest U: " + ", ".join(f"s={ss[i]}: U={Us[i]}, inherited={Is[i]}" for i in order))
p = float(sys.argv[4]) if len(sys.argv) > 4 else 0.02398
T = Us + Is
print(f"rows of N + s in all (undecided + inherited): min {T.min()} at s = {ss[T.argmin()]}, median {np.median(T):.0f}")
print(f"p = {p}: sum over all even shifts of exp(-p (rows(N+s) - rows(N))) = {np.exp(-p * (T - k0)).sum():.3e}  (successes among all neighbours per success in the cover)")
print(f"   largest single term: exp(-p*{T.min() - k0}) = {math.exp(-p * (T.min() - k0)):.3e}")
best = np.argsort(Is * 0 + (p * Is) - p * (k0 - Us))[:5]
print("   per shift: chance that a member's inherited rows are all composite, exp(-p I), times the neighbour's advantage exp(p (rows(N) - U)):")
for i in np.argsort(-(np.exp(-p * Is) * np.exp(p * (k0 - Us))))[:6]:
    print(f"     s = {ss[i]}: I = {Is[i]}, U = {Us[i]}: {math.exp(-p * Is[i]):.2e} x {math.exp(p * (k0 - Us[i])):.2f}")
