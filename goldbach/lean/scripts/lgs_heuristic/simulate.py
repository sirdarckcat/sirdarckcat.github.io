#!/usr/bin/env python3
"""A generator for sequences like A025018 / A025019 that never looks at a prime of the size of N.

It follows the two laws of model.py from a starting term (N, g):

    next front : the first point of a Poisson process whose intensity is the model's density of
                 unstruck even numbers (m strikers so far), started at N;
    its value  : the front is hit by each further striker with probability h = 2 C2 S / ln N,
                 S drawn from the model's distribution of S among unstruck numbers; the value is
                 the prime at which the first hit occurs.

The output is random: it is not A025018.  The question it answers is whether A025018 looks like
a typical output.

    python3 -I simulate.py terms.txt RUNS [c] > simulate.txt       (c: dependence constant, default 0.92)
"""
import math
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))    # model.py, next to this file
import model as M

def run(rng, N0, m0, xmax, c):
    """one synthetic sequence from the term (N0, m0-th odd prime) up to xmax: list of (ln N, m)"""
    out = []
    lnN, m = math.log(N0), m0
    while True:
        # next front: cumulative expected unstruck even numbers on a log grid beyond N
        E = rng.exponential(1.0)
        grid = np.linspace(lnN, lnN + 14.0, 281)
        acc, found = 0.0, None
        for a, b in zip(grid[:-1], grid[1:]):
            mid = 0.5 * (a + b)
            piece = 0.5 * (math.exp(b) - math.exp(a)) * M.ubar(mid, m, c)
            if acc + piece >= E:
                frac = (E - acc) / piece
                found = math.log(math.exp(a) + frac * (math.exp(b) - math.exp(a)))
                break
            acc += piece
        if found is None or found > math.log(xmax):
            return out
        lnN = found
        # its singular series, among unstruck numbers, and the wait for the hit
        h_all = np.minimum(M.TWO_C2 * M.S_SAMPLES / lnN, 0.999999)
        w = np.exp(m * np.log1p(-h_all) - c * M.A_of(m) * m * h_all * h_all)
        S = rng.choice(M.S_SAMPLES, p=w / w.sum())
        h = min(M.TWO_C2 * S / lnN, 0.999999)
        m += int(rng.geometric(h))
        out.append((lnN, m))

def main():
    terms = [tuple(map(int, l.split())) for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
    runs = int(sys.argv[2]); c = float(sys.argv[3]) if len(sys.argv) > 3 else 0.92
    idx = {int(p): i + 1 for i, p in enumerate(M.ODD)}
    start = next(t for t in terms if t[0] >= 1000)            # 2642, value 103
    xmax = terms[-1][0]
    real = [(N, g) for N, g in terms if N > start[0]]
    rng = np.random.default_rng(7)
    counts, finals, at = [], [], {e: [] for e in (6, 9, 12, 15)}
    sample_runs = []
    for r in range(runs):
        seq = run(rng, start[0], idx[start[1]], xmax, c)
        counts.append(len(seq)); finals.append(int(M.ODD[seq[-1][1] - 1]) if seq else start[1])
        for e in at:
            ms = [m for lnN, m in seq if lnN <= e * math.log(10)]
            at[e].append(int(M.ODD[ms[-1] - 1]) if ms else start[1])
        if r < 3: sample_runs.append(seq)
    counts = np.array(counts); finals = np.array(finals)
    print(f"start: the term {start[0]} with value {start[1]}; end: {xmax} (the 67th term); dependence constant c = {c}")
    print(f"{runs} synthetic sequences against the real one")
    print(f"  number of terms after the start, up to the end:  synthetic mean {counts.mean():.1f}, sd {counts.std():.1f}, "
          f"5% to 95%: {np.percentile(counts, 5):.0f} to {np.percentile(counts, 95):.0f};   real {len(real)}")
    print(f"  largest value at the end:                         synthetic median {np.median(finals):.0f}, "
          f"5% to 95%: {np.percentile(finals, 5):.0f} to {np.percentile(finals, 95):.0f};   real {real[-1][1]}")
    for e in at:
        v = np.array(at[e]); act = max(g for N, g in terms if N <= 10 ** e)
        print(f"  largest value up to 10^{e}:                       synthetic median {np.median(v):.0f}, "
              f"5% to 95%: {np.percentile(v, 5):.0f} to {np.percentile(v, 95):.0f};   real {act}")
    print("\nthree synthetic sequences (N rounded to two digits : value), and the real one:")
    for seq in sample_runs:
        print("  " + " ".join(f"{float(f'{math.exp(lnN):.2g}'):.2g}:{int(M.ODD[m - 1])}" for lnN, m in seq[:40]) + (" ..." if len(seq) > 40 else ""))
    print("  real: " + " ".join(f"{float(f'{N:.2g}'):.2g}:{g}" for N, g in real[:40]) + " ...")

main()
