#!/usr/bin/env python3
"""Can a cover be chosen for the sieve's selection?  The variance of the survivors per member from the pairs of rows.

    python3 cover_selection.py covers.txt Q [sieve limit = 1e8] [covers to read = 40]

S = rows of a member with no prime factor in (x, B].  Var(S) = sum_i w(1-w) + sum_{i != j} cov_ij,
cov_ij = w^2 (rho_ij - 1), rho_ij = prod_{x<s<=B} (1 - nu_s/s)/(1 - 1/s)^2, nu_s = 1 if s | q_i - q_j else 2.
A difference below Q < 467^2 has at most one prime factor s above x = 463, so rho_ij = C0 * (1 + 1/(s-1))/(1 - 1/(s-1)^2) if it has one, else C0,
C0 = prod_{x<s<=B} (1 - 1/(s-1)^2).  The sum over pairs = sum over primes s of sum over classes a of n_a (n_a - 1) (...).
"""
import sys, math, numpy as np
f, Q = sys.argv[1], int(sys.argv[2]); B = float(sys.argv[3]) if len(sys.argv) > 3 else 1e8; nmax = int(sys.argv[4]) if len(sys.argv) > 4 else 40
sv = np.ones(Q, dtype=bool); sv[:2] = False
for i in range(2, int(Q ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
sv[2] = False; q = np.nonzero(sv)[0]; ps = [int(s) for s in q if s > 463]
lines = [l.split() for l in open(f) if l.startswith("COVER") or l.startswith("BEST")][:nmax]
x = 463; L = 200 * math.log(10)
# exact products over the primes in (x, B] (segmented sieve); the first version of this file used w = ln x/ln B and
# C0 = exp(-1/(x ln x)), which put the sd at 0.962 of independent where it is 0.984 (found by the Lean session, which
# also measured the variance on real members: 326.98 +- 1.14 at 10^8 against 324.51 from this formula)
def exact_products(B):
    B = int(B); small = np.ones(int(B ** .5) + 2, dtype=bool); small[:2] = False
    for i in range(2, int(len(small) ** .5) + 1):
        if small[i]: small[i * i::i] = False
    sp = np.nonzero(small)[0]; lw = 0.0; lc = 0.0; seg = 1 << 24
    for lo in range(x + 1, B + 1, seg):
        hi = min(lo + seg, B + 1); m = np.ones(hi - lo, dtype=bool)
        for p_ in sp:
            if p_ * p_ >= hi: break
            st = max(p_ * p_, (lo + p_ - 1) // p_ * p_); m[st - lo::p_] = False
        pr = (np.nonzero(m)[0] + lo).astype(float)
        lw += float(np.log1p(-1 / pr).sum()); lc += float(np.log1p(-1 / (pr - 1) ** 2).sum())
    return math.exp(lw), math.exp(lc)
w, C0 = exact_products(B)
out = []
for l in lines:
    cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in l if ":" in t]; alive = np.ones(len(q), dtype=bool)
    for r, a in cov: alive &= (q % r) != a
    rows = q[alive]; n = len(rows); tot = 0.0; vs = []
    for s in ps:
        c = np.bincount(rows % s, minlength=s).astype(float); pairs = float((c * (c - 1)).sum())          # ordered pairs with s | q_i - q_j
        tot += pairs * (C0 * (1 + 1 / (s - 1)) / (1 - 1 / (s - 1) ** 2) - C0)
        if s < 1000: vs.append(c[1:].var() / c[1:].mean())
    allpairs = n * (n - 1); covsum = w * w * (allpairs * (C0 - 1) + tot)
    var = n * w * (1 - w) + covsum; p = 2 * math.prod(r / (r - 1) for r, _ in cov) / L; pp = p / w
    out.append((n, var, n * w * (1 - w), float(np.mean(vs)), pp * math.sqrt(var)))
out = np.array(out)
print(f"{len(out)} covers of {f.split('/')[-1]}, Q = {Q}, sieve to {B:g}: w = {w:.6f}, prod (1 - 1/(s-1)^2) = {C0:.8f}")
print("rows | Var(S) predicted | binomial | ratio of sd | mean variance/mean of the class counts modulo the primes 467..997 | p' * sd(S), nats per sd")
for r in out[:6]: print(f"{int(r[0])} | {r[1]:.1f} | {r[2]:.1f} | {math.sqrt(r[1] / r[2]):.4f} | {r[3]:.3f} | {r[4]:.4f}")
print(f"over the {len(out)} covers: sd(S)/binomial sd: mean {np.sqrt(out[:,1]/out[:,2]).mean():.4f}, min {np.sqrt(out[:,1]/out[:,2]).min():.4f}, max {np.sqrt(out[:,1]/out[:,2]).max():.4f};  p'*sd: {out[:,4].min():.4f} to {out[:,4].max():.4f}")
