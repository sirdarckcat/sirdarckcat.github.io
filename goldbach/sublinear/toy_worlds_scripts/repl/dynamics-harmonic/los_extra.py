#!/usr/bin/env python3
"""(c) continued: orthogonality of the prime flags to additive characters of the row (Kronecker/Davenport type), to
quadratic phases, row totals, parity of k, and real characters to moduli just above 400,000."""
import math, numpy as np, gmpy2
from common import setup
cov, rows, N0, M, K = setup(); n = len(rows); Q = 200000
d = np.load("los_data_1.npz"); ks = d["k"]; ptr = d["ptr"]; ridx = d["rowidx"]; fl = d["isprime"]; nm = len(ks); cnt = np.diff(ptr); memb = np.repeat(np.arange(nm), cnt); q = rows[ridx].astype(np.int64)
pcm = np.add.reduceat(fl.astype(np.int64), ptr[:-1]) / cnt; e = fl - pcm[memb]          # centred inside each member
v = (pcm * (1 - pcm))[memb]
# row totals
num = np.bincount(ridx, weights=e, minlength=n); den = np.bincount(ridx, weights=v, minlength=n); chi = float((num ** 2 / den).sum())
print(f"row totals: chi2 over the {n} rows {chi:.1f} (expected {n} +- {math.sqrt(2*n):.0f}); largest |z| of a row {np.abs(num/np.sqrt(den)).max():.2f} (noise maximum {math.sqrt(2*math.log(n)):.2f})")
# additive characters e(j q / L), L = 2^18
L = 1 << 18; D = np.bincount(q, weights=e, minlength=L); F = np.fft.rfft(D); Pw = (F.real ** 2 + F.imag ** 2)[1:L // 2] / v.sum()
print(f"additive characters e(jq/2^18), j=1..{L//2-1}: mean power {Pw.mean():.4f} (1 = independent flags), largest {Pw.max():.2f} at j={int(Pw.argmax())+1} (noise maximum about {math.log(L/2):.2f} +- 1.3); share of power in the 100 largest {np.sort(Pw)[-100:].sum()/Pw.sum():.5f} (white: {100/(L/2)*(1-math.log(100/(L/2))):.5f})")
# small denominators: e(a q / m), m <= 60
big = 0; arg = None
for m in range(2, 61):
    for a in range(1, m):
        if math.gcd(a, m) != 1: continue
        z = np.abs(np.sum(e * np.exp(2j * math.pi * a * (q % m) / m))) ** 2 / v.sum()
        if z > big: big = z; arg = (a, m)
print(f"e(aq/m), m <= 60 ({sum(1 for m in range(2,61) for a in range(1,m) if math.gcd(a,m)==1)} characters): largest power {big:.2f} at a/m = {arg}")
# quadratic phases e(alpha q^2), 2000 random alpha, and e(a q^2 / m)
rng = np.random.default_rng(2); big = 0; pw = []
for al in rng.random(2000):
    z = np.abs(np.sum(e * np.exp(2j * math.pi * ((al * q) % 1.0) * q))) ** 2 / v.sum(); pw.append(z)
pw = np.array(pw); print(f"quadratic phases e(alpha q^2), 2000 random alpha: mean power {pw.mean():.3f}, largest {pw.max():.2f} (noise maximum about {math.log(2000):.2f})")
# parity of k
ev = (ks % 2 == 0); re = fl[ev[memb]].mean(); ro = fl[~ev[memb]].mean(); se = math.sqrt(fl.mean() * (1 - fl.mean()) * (1 / ev[memb].sum() + 1 / (~ev[memb]).sum()))
print(f"prime rate, even k {re:.5f}, odd k {ro:.5f}: ratio - 1 = {re/ro-1:+.4f} +- {se/fl.mean():.4f}")
# N - q mod 4 and mod 8
Nm8 = np.array([int((N0 + int(k) * M) % 8) for k in ks]); r8 = (Nm8[memb] - q) % 8
for cls in (1, 3, 5, 7): print(f"  N-q = {cls} mod 8: rate {fl[r8 == cls].mean():.5f} ({int((r8 == cls).sum())} tests)")
# real characters to prime moduli just above 400,000 (first 300 primes)
D0 = 400000; Ds = []; x = D0
while len(Ds) < 300:
    x = int(gmpy2.next_prime(x)); Ds.append(x)
zs = []
for Dm in Ds:
    c = (N0 % Dm + ks.astype(np.int64) * (M % Dm)) % Dm; a = (c[memb] - q) % Dm
    t = -np.ones(Dm, dtype=np.int8); t[(np.arange(Dm, dtype=np.int64) ** 2) % Dm] = 1; t[0] = 0; ch = t[a]
    A = fl[ch == 1]; B = fl[ch == -1]; p0 = fl.mean(); zs.append((A.mean() - B.mean()) / math.sqrt(p0 * (1 - p0) * (1 / len(A) + 1 / len(B))))
zs = np.array(zs); print(f"Legendre symbols to the 300 primes after 400,000: mean z^2 {np.mean(zs**2):.3f}, largest |z| {np.abs(zs).max():.2f} (noise maximum {math.sqrt(2*math.log(300)):.2f})")
# what an exceptional real character would be worth as a pin: best class a mod D of sum over rows chi(a - q)
for Dm in (Ds[0], 1000003):
    t = -np.ones(Dm); t[(np.arange(Dm, dtype=np.int64) ** 2) % Dm] = 1; t[0] = 0
    ind = np.zeros(Dm); ind[rows % Dm] += 1
    corr = np.fft.irfft(np.fft.rfft(t) * np.conj(np.fft.rfft(ind)), Dm) if Dm % 2 == 0 else np.real(np.fft.ifft(np.fft.fft(t) * np.conj(np.fft.fft(ind))))
    # corr[s] = sum_c t(c+s) ind(c) = sum_q chi(q + s); we need sum_q chi(a - q) = chi(-1) sum_q chi(q - a) -> max of |corr| with sign
    best = np.max(np.abs(corr)); print(f"  D={Dm}: max over classes a of |sum_rows chi(a-q)| = {best:.0f} (sqrt(2 n ln D) = {math.sqrt(2*n*math.log(Dm)):.0f}); worth 0.0243*delta*{best:.0f} = {0.0243*best:.2f}*delta nats for ln D = {math.log(Dm):.1f} nats of room")
