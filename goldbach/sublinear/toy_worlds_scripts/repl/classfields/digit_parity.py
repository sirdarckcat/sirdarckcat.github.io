#!/usr/bin/env python3
"""Does the function-field parity transfer through the digit map?  n = sum b_i 2^i  ->  f_n = sum b_i x^i in F_2[x]
(the binary digits are the Teichmuller digits of n in Z_2 = W(F_2)).  Swan's theorem gives the parity of the number of
irreducible factors of a squarefree f_n from a discriminant; is it (or irreducibility of f_n) correlated with the
Liouville function of n or with the primality of n?   Random odd n of B bits; also the subset with no prime factor < 100.
"""
import sys, random, math, flint
B = int(sys.argv[1]) if len(sys.argv) > 1 else 44
NS = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
random.seed(5)
def corr(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    c = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    va = sum((x - ma) ** 2 for x in a) / n; vb = sum((y - mb) ** 2 for y in b) / n
    return c / math.sqrt(va * vb) if va > 0 and vb > 0 else float("nan")
for base in (2, 3):
    lam = []; par = []; isp = []; irr = []; rough = []
    for _ in range(NS):
        n = random.getrandbits(B) | (1 << (B - 1)) | 1
        digs = []; m = n
        while m: digs.append(m % base); m //= base
        if digs[0] == 0: continue                       # x | f_n: skip
        fac = flint.fmpz(n).factor(); Om = sum(e for _, e in fac)
        pf = flint.nmod_poly(digs, base).factor()[1]; Op = sum(e for _, e in pf)
        lam.append((-1) ** Om); par.append((-1) ** Op); isp.append(1 if Om == 1 else 0); irr.append(1 if Op == 1 else 0)
        rough.append(min(int(p) for p, _ in fac) > 100)
    N = len(lam); se = 1 / math.sqrt(N)
    print(f"base {base}, {B}-bit odd n, {N} samples (standard error of a correlation {se:.4f})")
    print(f"  corr(lambda(n), (-1)^Omega(f_n))          = {corr(lam, par):+.4f}")
    print(f"  corr(n prime, f_n irreducible)             = {corr(isp, irr):+.4f}   [primes {sum(isp)}, irreducible {sum(irr)}, both {sum(a * b for a, b in zip(isp, irr))}, expected if independent {sum(isp) * sum(irr) / N:.1f}]")
    print(f"  corr(n prime, (-1)^Omega(f_n))             = {corr(isp, par):+.4f}")
    idx = [i for i in range(N) if rough[i]]
    l2 = [lam[i] for i in idx]; p2 = [par[i] for i in idx]; s2 = [isp[i] for i in idx]; r2 = [irr[i] for i in idx]
    print(f"  n with no prime factor below 100: {len(idx)} samples (se {1 / math.sqrt(len(idx)):.4f}): corr(lambda, parity of f) = {corr(l2, p2):+.4f}, corr(prime, parity of f) = {corr(s2, p2):+.4f}, corr(prime, irreducible) = {corr(s2, r2):+.4f}")
