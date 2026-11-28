#!/usr/bin/env python3
"""A heuristic N generator for A025018.

It prints the numbers N at which it expects the least Goldbach summand to exceed that of every
smaller even number, and it never asks whether any N - q is prime.  Two rules, in turn.

Rule A, covering (no probability in it).  Take the first n odd primes as moduli and give each one
residue class.  A class a mod r "strikes" an odd prime q when q = a (mod r): then r divides N - q for
every N = a (mod r).  Among all choices of classes take those that strike the longest run of odd
primes 3, 5, 7, ..., and announce the least even number beyond the previous term that carries one
of them.  n = 0, 1, 2, 3 gives 6, 12, 30, 98.

Rule B, the clock.  After a term N with value G, every later even number M has, in the model of
model.py, a chance u(M, m) of escaping the m odd primes up to G.  The next term is announced where
the sum of these chances reaches 1.  Its value is the prime 1/h strikers after G, h being the mean
hit chance of an escaping number at that size.

    python3 -I hgen.py terms.txt 0.92 terms_68_69.txt > hgen.txt

The terms file is used only to print the real sequence next to the generated one.
"""
import itertools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model  # noqa: E402

STEP, NSTEP = 0.02, 900


def rule_a(nmax):
    """the terms the covering rule announces for n = 0 .. nmax moduli"""
    odd = [int(p) for p in model.ODD[:400]]
    out, prev = [], 4
    for n in range(nmax + 1):
        mods = odd[:n]
        best, vecs = 0, []
        for a in itertools.product(*[range(r) for r in mods]):
            q = next(q for q in odd if all(q % r != c for r, c in zip(mods, a)))
            if q > best: best, vecs = q, [a]
            elif q == best: vecs.append(a)
        period = 2 * math.prod(mods)
        cands = []
        for a in vecs:
            N = next(N for N in range(prev + 2, prev + 2 + 2 * period, 2) if all(N % r == c for r, c in zip(mods, a)))
            cands.append(N)
        prev = min(cands)
        out.append((n, mods, best, len(vecs), prev))
    return out


def next_by_clock(N0, m, c):
    """the point where the expected number of escaping even numbers after N0 reaches 1, and the
    mean hit chance of an escaping number there"""
    l0 = math.log(N0)
    ls = l0 + STEP * np.arange(NSTEP + 1)
    xs = np.exp(ls)
    mid = 0.5 * (ls[1:] + ls[:-1])
    dens = np.array([model.ubar(l, m, c) for l in mid])
    cum = np.concatenate(([0.0], np.cumsum(0.5 * (xs[1:] - xs[:-1]) * dens)))
    i = int(np.searchsorted(cum, 1.0))
    if i > NSTEP: return None, None
    f = (1.0 - cum[i - 1]) / (cum[i] - cum[i - 1])
    lnN = ls[i - 1] + f * STEP
    h = np.minimum(model.TWO_C2 * model.S_SAMPLES / lnN, 0.999999)
    w = np.exp(m * np.log1p(-h) - c * model.A_of(m) * m * h * h)
    return math.exp(lnN), float((w * h).sum() / w.sum())


def main():
    real = []
    for path in [sys.argv[1]] + sys.argv[3:]:
        real += [tuple(map(int, l.split())) for l in open(path) if l.strip() and not l.startswith('#')]
    c = float(sys.argv[2]) if len(sys.argv) > 2 else 0.92
    odd = [int(p) for p in model.ODD]

    print("Rule A: the best covering by the first n odd primes")
    print("   n  moduli              longest run ends before   best vectors   announced   real term")
    gen = [(4, 2)]
    for n, mods, best, nv, N in rule_a(4):
        k = len(gen)
        rn, rg = real[k]
        ok = "" if N == rn else "   <- the rule breaks here"
        print(f"   {n}  {str(mods):18s}  {best:10d} {nv:22d} {N:11d} {rn:11d}{ok}")
        if N == rn: gen.append((N, best))
    print(f"   Rule A is right for {len(gen)} terms: " + ", ".join(str(N) for N, _ in gen))

    print("\nRule B: the clock, started at the last term of rule A; no real term is used after that")
    print("   k        generated N   value")
    N, G = gen[-1]
    m = sum(1 for p in odd if p <= G)
    k = len(gen)
    limit = 4e18
    hist = list(gen)
    while True:
        x, h = next_by_clock(N, m, c)
        if x is None or x > limit: break
        N = 2 * int(round(x / 2))
        m += max(1, int(round(1 / h)))
        G = odd[m - 1]
        hist.append((N, G))
        print(f"  {k + 1:2d} {N:20d} {G:7d}")
        k += 1

    print("\nHow many terms up to X, and the largest value up to X")
    print("        X    generated terms   real terms    generated value   real value")
    for e in (3, 6, 9, 12, 15, 18):
        X = 10 ** e
        g1 = [g for n_, g in hist if n_ <= X]; r1 = [g for n_, g in real if n_ <= X]
        print(f"   10^{e:<3d} {len(g1):12d} {len(r1):14d} {max(g1):16d} {max(r1):12d}")
    X = limit
    g1 = [g for n_, g in hist if n_ <= X]; r1 = [g for n_, g in real if n_ <= X]
    print(f"   4*10^18 {len(g1):10d} {len(r1):14d} {max(g1):16d} {max(r1):12d}")
    realN = {n_ for n_, _ in real}
    exact = sum(1 for n_, _ in hist[len(gen):] if n_ in realN)
    print(f"\nnumbers generated by rule B that are real terms: {exact} of {len(hist) - len(gen)}")


if __name__ == "__main__":
    main()
