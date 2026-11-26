import numpy as np, math
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.flatnonzero(s)
R = np.load('rows_alive.npy').astype(np.int64); n = len(R); print('alive rows', n)
pr = primes_upto(463); prod = float(np.prod([1 - 1 / p for p in pr]))
print('prod_{p<=463}(1-1/p) = %.5f ; e^-gamma/ln463 = %.5f' % (prod, math.exp(-0.5772156649) / math.log(463)))
for e in (198, 199, 199.7, 200):
    lnN = e * math.log(10); p = 1 / (lnN * prod); print('N=10^%.1f: p = %.5f, -ln(1-p) = %.5f, exponent for %d rows = %.2f' % (e, p, -math.log(1 - p), 1502, 1502 * -math.log(1 - p)))
# E3: size
for e in (198.0, 198.5, 199.0, 199.5, 200.0):
    lnN = e * math.log(10); p = 1 / (lnN * prod); print('  N=10^%.1f exponent (1502 rows) %.2f' % (e, 1502 * -math.log(1 - p)))
# E2: second order, exact on this alive set
p = 1 / (200 * math.log(10) * prod)
L = 4_000_000; big = primes_upto(L); big = big[big > 463]
A = float(np.sum(np.log1p(-1.0 / (big - 1.0) ** 2)))                 # sum over primes l>463 (l <= 4e6) of ln(1 - 1/(l-1)^2)
tail = 1.0 / (L * math.log(L)); A -= tail                            # tail of sum 1/l^2 beyond 4e6 (negligible)
print('A = sum_{l>463} ln(1-1/(l-1)^2) = %.6e   (1/(463 ln 463) = %.3e)' % (A, 1 / (463 * math.log(463))))
Dmax = 200000
# g(d) = sum over primes l | d, l > 463 of ln( (l/(l-1)) / (1-1/(l-1)^2) )
g = np.zeros(Dmax + 1)
for l in big[big < Dmax]:
    g[l::l] += math.log((l / (l - 1.0)) / (1 - 1.0 / (l - 1.0) ** 2))
d = np.abs(R[:, None] - R[None, :]); iu = np.triu_indices(n, 1); dd = d[iu]
hist = np.bincount(dd, minlength=Dmax + 1)
C1 = np.exp(A + g) - 1.0                                              # C(d) - 1
pairs = n * (n - 1) / 2; S2 = float((hist * C1).sum())
print('pairs %.0f ; sum over pairs of (C(d)-1) = %.3f ; mean (C-1) = %.3e' % (pairs, S2, S2 / pairs))
corr = p * p * S2 / (1 - p) ** 2
print('second-order correction to ln P(no prime row) = p^2 * sum / (1-p)^2 = %.5f nats   [one-sided pieces: negative part %.4f, positive part %.4f]' % (corr, p * p * pairs * A / (1 - p) ** 2, p * p * float((hist * (np.exp(A + g) - np.exp(A))).sum()) / (1 - p) ** 2))
# what a deliberately clumped alive set could give: maximum over l of the extra, bounded by the largest class sizes
cl = []
for l in big[big < 3000][:300]:
    b = np.bincount(R % l, minlength=l); cl.append((int(b.max()), int(l)))
print('largest class of the alive rows mod l, l in (463, 3000): max %s' % (max(cl),))
