# A1 (dual) and A2 (geometry) numbers on my 1,524-row cover: rough positions of the window, expected overlap, and the exchange rate of a pin at a prime above 463.
import numpy as np, math
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
Q = 200000; P = primes_upto(Q - 1); rowsall = P[P > 2].astype(np.int64)
mods = [int(p) for p in primes_upto(463) if p > 2]; cls = np.load('../lattice/cls_sa_11.npy')
alive = np.ones(len(rowsall), bool)
for p, c in zip(mods, cls): alive &= (rowsall % p != c)
R = rowsall[alive]; n = len(R); lnN = 200 * math.log(10)
pi = 2 * np.prod([p / (p - 1) for p in mods]) / lnN
# rough positions: j in (0, Q) with j !== c_r (mod r) for all r and j odd
j = np.arange(1, Q); ok = (j % 2 == 1)
for p, c in zip(mods, cls): ok &= (j % p != c)
print('A1: window length Q = %d = (ln N)^%.3f ; primes expected in the window Q/ln N = %.1f' % (Q, math.log(Q) / math.log(lnN), Q / lnN))
print('    rough positions (odd, outside the pinned classes) R = %d (%.1f%% of the window); alive rows (prime offsets among them) n = %d = %.1f%% of them' % (ok.sum(), 100 * ok.sum() / Q, n, 100 * n / ok.sum()))
print('    prime probability of a rough position pi = %.5f; expected primes in the window R*pi = %.0f; expected primes at forbidden positions n*pi = %.2f (exponent)' % (pi, ok.sum() * pi, n * pi))
print('    probability that a window has no prime at all: exp(-%.0f) against exp(-%.1f) for g(N) >= Q' % (Q / lnN, n * pi))
print('\nA2: exchange rate of one extra pin at a prime s > 463 at its best class, on this cover (rows struck, nats of exponent per nat of entropy ln s):')
print('       s   ln s  best class rows  exponent gain (0.02398 per row)  gain per nat')
for s in (467, 479, 503, 541, 701, 1009, 2003, 5003, 20011, 100003, 200003):
    b = np.bincount(R % s, minlength=s); w = int(b.max()); print('%8d %6.2f %9d %24.3f %17.4f' % (s, math.log(s), w, w * 0.02398, w * 0.02398 / math.log(s)))
print('    for comparison the cover itself: the 89 pins cost 443.6 nats and take the random-cover mean 2,151 alive rows down to %d (%.3f nats of exponent per nat)' % (n, (2151 - n) * 0.02398 / 443.6))
