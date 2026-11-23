#!/usr/bin/env python3
"""The least Goldbach summand without Goldbach calculations: a model, and its test on A025018.

Nothing here tests whether any N - q is prime.  The model uses only the Hardy-Littlewood
density: for an even N a prime q that does not divide N is a Goldbach summand with probability

        h(N) = 2 C2 S(N) / ln N,        S(N) = prod over odd primes p | N of (p - 1)/(p - 2),

and, at first, different q are treated as independent.  In the language of the generator
(GoldbachGaps/RecordGen.lean): h is the chance that a striker hits a given number.  Then

  (a) a number N is unstruck by the first m odd primes with probability
          u(N, m) = (1 - h(N))^m * exp(-c A_m m h(N)^2),      A_m = sum over the m strikers p of 1/(p - 2).
      c = 0 is the independent model.  The second factor is the dependence between the summands
      of one N: a prime p not dividing N kills the strikers of one class modulo p together and
      leaves the others with a higher chance, which makes the number of summands among the first
      m primes less dispersed than a Poisson variable.  To second order its factorial cumulant is
      -m h^2 (1 + A_m), i.e. c = 1/2; the scan to 10^12 asks for c close to 1 (fitted below, the
      only fitted number);
  (b) the front after m strikers is the first unstruck even number: the sum of u(N, m) over the
      even N from one front to the next is an exponential variable of mean 1;
  (c) the number of strikers a front N waits for is geometric with parameter h(N).

    python3 -I model.py terms.txt ../rank_records/hist_1e12.txt 1000000000000 \
        ../rank_records/hist_1e11.txt 100000000000 > model.txt

prints (0) the fitted c, (1) the predicted number of N <= X with least summand at least the m-th
odd prime against the count of the scan, up to 10^12 (where c is fitted) and up to 10^11 (not
used in the fit), (2) the test of (c) and (3) of (b) on the 67 known terms, (4) the record value
the model expects at each size, and (5) the same count at 10^200 against the research session's
sampler at its five targets.
"""
import math
import sys
import numpy as np

C2 = 0.6601618158468696
TWO_C2 = 2 * C2


def primes_upto(n):
    sv = np.ones(n + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]: sv[i * i::i] = False
    return np.nonzero(sv)[0]


SMALL = primes_upto(20000)
ODD = SMALL[SMALL > 2]
rng = np.random.default_rng(20261123)
NS = 200000
# the singular series of a random even N: each odd prime p divides it with probability 1/p
_S = np.ones(NS)
for p in ODD[ODD < 3000]:
    hit = rng.random(NS) < 1.0 / p
    _S[hit] *= (p - 1) / (p - 2)
S_SAMPLES = _S


def S_of(N):
    s, n = 1.0, N
    while n % 2 == 0: n //= 2
    for p in ODD:
        p = int(p)
        if p * p > n: break
        if n % p == 0:
            s *= (p - 1) / (p - 2)
            while n % p == 0: n //= p
    if n > 1 and n < 10 ** 9: s *= (n - 1) / (n - 2)
    return s


_A = np.concatenate(([0.0], np.cumsum(1.0 / (ODD - 2.0))))


def A_of(m):
    """sum of 1/(p - 2) over the first m odd primes (Mertens beyond the table)"""
    if m < len(_A): return float(_A[m])
    pm = m * (math.log(m) + math.log(math.log(m)) - 1)
    return float(_A[-1]) + math.log(math.log(pm) / math.log(float(ODD[-1])))


CORR = 0.0        # the constant c of the dependence correction; set by main()


def ubar(lnn, m, c=None):
    """mean over even N of size e^lnn of the chance to be unstruck by m strikers"""
    c = CORR if c is None else c
    h = np.minimum(TWO_C2 * S_SAMPLES / lnn, 0.999999)
    return float(np.mean(np.exp(m * np.log1p(-h) - c * A_of(m) * m * h * h)))


def unstruck_count(m, x_lo, x_hi, steps=200, c=None):
    """expected number of even N in (x_lo, x_hi] unstruck by m strikers"""
    if x_hi <= x_lo: return 0.0
    ls = np.linspace(math.log(x_lo), math.log(x_hi), steps + 1)
    mid = 0.5 * (ls[1:] + ls[:-1])
    w = np.exp(ls[1:]) - np.exp(ls[:-1])
    return float(sum(0.5 * wi * ubar(li, m, c) for wi, li in zip(w, mid)))


def read_tail(hist_path, idx):
    gs, cs = [], []
    for line in open(hist_path):
        if line.startswith('#'): continue
        g, c = line.split(); gs.append(int(g)); cs.append(int(c))
    full = np.zeros(len(ODD) + 2)
    for g, c in zip(gs, cs): full[idx[g]] = c
    return np.cumsum(full[::-1])[::-1]


def main():
    global CORR
    terms = [tuple(map(int, l.split())) for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
    hist_path, X = sys.argv[2], int(sys.argv[3])
    hist2 = sys.argv[4] if len(sys.argv) > 4 else None
    X2 = int(sys.argv[5]) if len(sys.argv) > 5 else None
    idx = {int(p): i + 1 for i, p in enumerate(ODD)}        # index among the odd primes
    tail = read_tail(hist_path, idx)

    # the one fitted number: c, on the scan up to X, m = 20 .. 320
    fit_ms = [m for m in (20, 40, 80, 120, 160, 200, 240, 280, 320) if tail[m] >= 1000]
    def err(c):
        return sum((math.log(unstruck_count(m - 1, 6, X, steps=120, c=c) / tail[m])) ** 2 for m in fit_ms)
    lo, hi = 0.0, 2.0
    for _ in range(18):                     # golden-section search
        a1 = lo + 0.382 * (hi - lo); a2 = lo + 0.618 * (hi - lo)
        if err(a1) < err(a2): hi = a2
        else: lo = a1
    cfit = 0.5 * (lo + hi)
    print(f"0. Dependence constant fitted on the scan up to {X} (m = {fit_ms[0]} .. {fit_ms[-1]}): c = {cfit:.2f}"
          f"   (second-order theory: 0.5; independent strikers: 0)")

    def section1(tl, Xs, label):
        print(f"   X = {Xs} ({label})")
        print("      m   prime          scan   independent ln(model/scan)   with dependence ln(model/scan)")
        for m in (2, 5, 10, 20, 40, 80, 120, 160, 200, 240, 280, 320, 360, 400, 440):
            if m >= len(tl) or tl[m] < 3: break
            p0 = unstruck_count(m - 1, 6, Xs, c=0.0); p1 = unstruck_count(m - 1, 6, Xs, c=cfit)
            print(f"   {m:4d} {int(ODD[m - 1]):6d} {tl[m]:14.0f} {p0:14.1f} {math.log(p0 / tl[m]):+6.2f}   {p1:14.1f} {math.log(p1 / tl[m]):+6.2f}")

    print("\n1. How many even N <= X have least summand at least the m-th odd prime (unstruck by m - 1 strikers)")
    print("   scan: ../rank_records; model: no primality of any N - q is used")
    section1(tail, X, "c was fitted here")
    if hist2:
        section1(read_tail(hist2, idx), X2, "not used in the fit")

    print("\n2. The hit law: a front N waits for a geometric number of strikers, parameter h(N) = 2 C2 S(N) / ln N")
    tot, us = 0.0, []
    for k in range(1, len(terms)):
        (N0, g0), (N, g) = terms[k - 1], terms[k]
        if N < 1000: continue
        n = sum(1 for q in ODD[(ODD > g0) & (ODD <= g)] if N % int(q) != 0)
        s = S_of(N); h = min(TWO_C2 * s / math.log(N), 0.999999)
        us.append(1 - (1 - h) ** n); tot += h * n
    K = len(us)
    print(f"   {K} terms from 1000 on: mean of h * (strikers faced) = {tot / K:.3f} (1 expected, standard error {1 / math.sqrt(K):.2f});"
          f" mean of P(wait <= observed) = {np.mean(us):.3f} (0.5 expected, standard error {1 / math.sqrt(12 * K):.3f})")

    print("\n3. The front law: the expected number of unstruck even numbers between consecutive fronts is exponential, mean 1")
    for label, c in (("independent strikers", 0.0), (f"with dependence, c = {cfit:.2f}", cfit)):
        lam = []
        for k in range(1, len(terms)):
            (N0, g0), (N, g) = terms[k - 1], terms[k]
            if N0 < 1000: continue
            lam.append(unstruck_count(idx[g0], N0, N, c=c))
        K = len(lam); lam = np.array(lam)
        print(f"   {label}: {K} jumps, mean {lam.mean():.2f} (1 expected, standard error {1 / math.sqrt(K):.2f}), median {np.median(lam):.2f} (0.69 expected),"
              f" mean of P(jump <= observed) = {np.mean(1 - np.exp(-lam)):.3f} (0.5 expected, standard error {1 / math.sqrt(12 * K):.3f})")
        if c:
            print("   the jumps with dependence, in order: " + " ".join(f"{x:.2f}" for x in lam))

    print("\n4. The record value the model expects at each size (one expected unstruck N <= X), against the largest term <= X")
    def expected_record(Xs, c):
        lo, hi = 1, len(ODD) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if unstruck_count(mid, 6, Xs, steps=120, c=c) > 1: lo = mid + 1
            else: hi = mid
        return int(ODD[lo - 1])
    print("      X     independent   with dependence   actual")
    for e in (4, 6, 8, 10, 12, 14, 16, 18):
        Xe = 10 ** e
        act = max((g for N, g in terms if N <= Xe), default=0)
        print(f"   10^{e:<3d} {expected_record(Xe, 0.0):9d} {expected_record(Xe, cfit):14d} {act:12d}")

    print("\n5. At 10^200, by the same count in logarithms, against the research session's sampler")
    print("   (goldbach/sublinear/README.md on branch ccr-d4a17dd0-7uu03r: parallel tempering over residue vectors)")
    lnX = 200 * math.log(10)
    big = primes_upto(2300000); bodd = big[big > 2]
    Abig = np.concatenate(([0.0], np.cumsum(1.0 / (bodd - 2.0))))
    def lnT(m, c):
        lam_ = TWO_C2 * m / lnX; h = TWO_C2 / lnX
        tilt = float(np.mean(np.exp(-lam_ * (S_SAMPLES - 1))))
        return lnX - math.log(2) + math.log(tilt) - lam_ - math.log(1 + lam_ / lnX) - c * Abig[m] * m * h * h
    print("   ln(number of even N < 10^200 with least summand >= Q):   independent   with dependence   sampler")
    for Q, rs in ((213070, 403.3), (245000, 395.7), (300000, 383.1), (350000, 371.5), (500000, 338.0)):
        m = int((bodd < Q).sum())
        print(f"      Q = {Q:7d} ({m:6d} strikers)                        {lnT(m, 0.0):7.1f}        {lnT(m, cfit):7.1f}       {rs}")
    for label, c in (("independent strikers", 0.0), (f"with dependence, c = {cfit:.2f}", cfit)):
        lo, hi = 1000, len(bodd) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if lnT(mid, c) > 0: lo = mid + 1
            else: hi = mid
        print(f"   {label}: one expected N at the {lo}-th odd prime, {int(bodd[lo - 1]):,}   (the campaign's ceiling: 2,130,704)")


if __name__ == "__main__":
    main()
