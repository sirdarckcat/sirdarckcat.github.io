#!/usr/bin/env python3
"""Independent check of numbers reported by fscan: recompute g(N) from N alone.

    python3 check.py N [N ...]          or          ./fscan ... | python3 check.py -

g(N) is the least prime p with N - p prime.  Every N - q for the primes q < g is tested with
gmpy2.is_prime (BPSW plus Miller-Rabin rounds), and N - g with 40 extra rounds.  Prints one line per N:
N, digits, g, and the largest g expected below N from the model table when closeness.py is importable.
"""
import os
import sys

import gmpy2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
try:
    import closeness
except Exception:                       # the table is optional
    closeness = None


def g_of(N):
    assert N % 2 == 0 and N > 4
    q = 2
    while True:
        if gmpy2.is_prime(N - q, 25):
            return q
        q = int(gmpy2.next_prime(q))


def main():
    args = sys.argv[1:]
    if args == ["-"]:
        args = [l.split()[1] for l in sys.stdin if l.startswith("S ")]
    for a in args:
        N = int(a)
        g = g_of(N)
        assert gmpy2.is_prime(N - g, 65) and all(not gmpy2.is_prime(N - q) for q in range(3, g, 2) if gmpy2.is_prime(q))
        extra = ""
        if closeness is not None:
            try:
                extra = f"  closeness {100 * g / closeness.ceiling(closeness.ln_int(N)):.1f}%"
            except Exception:
                pass
        print(f"N={N} digits={len(str(N))} g={g}{extra}", flush=True)


if __name__ == "__main__":
    main()
