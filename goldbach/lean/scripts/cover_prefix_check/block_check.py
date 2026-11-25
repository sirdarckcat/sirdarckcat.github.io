#!/usr/bin/env python3
"""Rows left by a block of moduli that all take the class of one common integer, against random classes.

Rows: the odd primes q < Q.  Block: the odd primes t in (z, w].  Classes a_t = N1 mod t for one integer N1 >= Q, the
same for the whole block.  Then q is struck by the block exactly when N1 - q has a prime factor in (z, w], so the rows
left are those with N1 - q free of prime factors in (z, w]:  N1 - q is z-smooth, or (when w^2 > N1) m p with one
prime p > w and m <= N1/w.  Random nonzero classes leave rows * prod (1 - 1/(t-1)).

    python3 block_check.py Q            a table over z and w at one Q (exact counts), N1 = the next power of two
    python3 block_check.py limit        the leading-order ratio of the two, by size
    python3 block_check.py capacity     what the write-up's count for the top moduli allows after each kind of prefix
"""
import math
import sys

import numpy as np


def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]


def dickman(umax=12.0, h=1e-4):
    """rho on a grid of step h: rho = 1 on [0, 1], u rho'(u) = -rho(u - 1)"""
    n = int(round(umax / h)); k = int(round(1 / h)); r = np.ones(n + 1)
    for i in range(k, n):            # trapezoid for rho(u + h) = rho(u) - int_u^{u+h} rho(t - 1)/t dt
        u = i * h
        r[i + 1] = r[i] - 0.5 * h * (r[i - k] / u + r[i + 1 - k] / (u + h))
    return r, h


def main():
    r, h = dickman()
    if sys.argv[1] == "limit":
        print("# block_check.py limit: rows left by the block (z, w] with a common integer, divided by the rows left by random classes for the same block,")
        print("# at leading order:  (rho(u) + ln(ln Q/ln w)) / (ln z/ln w),  u = ln Q/ln z,  minimised over z < w;  w = x/4")
        print("ln x | Q = x ln^2 x: ln(ln Q/ln w) | best u | ratio common integer / random | Q = x ln^3 x: best u | ratio")
        for lx in (9.21, 13.8, 20.7, 34.5, 50.0, 69.0, 100.0, 230.0, 500.0, 1000.0, 10000.0):
            out = []
            for A in (2, 3):
                lQ = lx + A * math.log(lx); lw = lx - math.log(4); eta = math.log(lQ / lw)
                us = np.arange(lQ / lw + 0.01, 12.0, 0.01); val = (r[np.rint(us / h).astype(int)] + eta) * us * lw / lQ; i = int(val.argmin())
                out.append((eta, us[i], val[i]))
            print(f"{lx:g} | {out[0][0]:.4f} | {out[0][1]:.2f} | {out[0][2]:.3f} | {out[1][1]:.2f} | {out[1][2]:.3f}")
        return
    if sys.argv[1] == "capacity":
        # the write-up's count for the top moduli: (3/4) x/ln x of them in (x/4, x], each striking ln x/ln ln x rows;
        # how large may Q be for the rows left by the moduli up to x/4 to fit?  Leading order throughout.
        print("# block_check.py capacity: the largest Q for which the rows left by the moduli up to x/4 fit the write-up's count for the top moduli")
        print("# (0.75 x/ln ln x rows), with random classes below x/4 and with the block (z, x/4] on a common integer (the best z); pi(Q) = Q/ln Q")
        print("ln x | random classes below the top: Q/(x ln^2 x) | block with a common integer: Q/(x ln^2 x) | best u = ln Q/ln z | ratio")
        for lx in (9.21, 13.8, 20.7, 34.5, 50.0, 69.0, 100.0, 230.0, 350.0, 500.0, 1000.0, 10000.0):
            lw = lx - math.log(4); cap = 0.75 / math.log(lx)                       # rows that fit, in units of x
            def left_random(lQ): return math.exp(lQ - lx) / lQ * 0.7413 / lw       # rows left, in units of x
            def left_block(lQ):
                us = np.arange(lQ / lw + 0.01, 12.0, 0.01)
                val = math.exp(lQ - lx) / lQ * (r[np.rint(us / h).astype(int)] + math.log(lQ / lw)) * 0.7413 * us / lQ
                i = int(val.argmin()); return float(val[i]), float(us[i])
            out = []
            for f in (left_random, lambda q: left_block(q)[0]):
                lo, hi = lx, lx + 8 * math.log(lx)
                for _ in range(60):
                    mid = 0.5 * (lo + hi)
                    if f(mid) <= cap: lo = mid
                    else: hi = mid
                out.append(lo)
            a, b = (math.exp(q - lx) / lx ** 2 for q in out)
            print(f"{lx:g} | {a:.3f} | {b:.3f} | {left_block(out[1])[1]:.2f} | {b / a:.2f}")
        return
    Q = int(sys.argv[1]); N1 = 1 << int(math.ceil(math.log2(Q)))
    P = primes_upto(N1); odd = P[(P > 2) & (P < Q)]; rows = len(odd)
    ws = [int(a) for a in sys.argv[2:]] or [int(Q ** 0.5), Q // 4096, Q // 1024, Q // 256, Q // 64]
    print(f"# block_check.py {Q}: {rows} rows (odd primes below Q), common integer N1 = 2^{int(math.log2(N1))} = {N1}")
    print("z | w | moduli in the block | rows left, common integer | fraction | rows left by random classes (expected) | fraction | ratio | leading order rho(u) + ln(ln N1/ln w) (given when w^2 > N1 and N1/w <= z)")
    for w in ws:
        for z in (int(N1 ** (1 / 5)), int(N1 ** (1 / 4)), int(N1 ** (1 / 3)), int(N1 ** 0.4), int(N1 ** 0.5)):
            if z >= w: continue
            block = P[(P > z) & (P <= w)]
            hit = np.zeros(N1 + 1, dtype=bool)
            for t in block: hit[int(t)::int(t)] = True
            left = int(np.count_nonzero(~hit[N1 - odd]))
            rnd = rows * float(np.prod(1 - 1 / (block - 1.0)))
            u = math.log(N1) / math.log(z); lead = r[int(round(u / h))] + math.log(math.log(N1) / math.log(w))
            ok = w * w > N1 and N1 / w <= z
            print(f"{z} | {w} | {len(block)} | {left} | {left / rows:.4f} | {rnd:.0f} | {rnd / rows:.4f} | {left / rnd:.3f} | " + (f"{lead:.4f}" if ok else "-"), flush=True)


if __name__ == "__main__":
    main()
