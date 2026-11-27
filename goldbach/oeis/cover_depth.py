#!/usr/bin/env python3
"""The cover depth D(n) of the first n odd primes, from scratch, and a check of witness vectors.

Definitions.  Give each of the first n odd primes r (3, 5, 7, ...) one residue class c_r modulo r.
This vector *strikes* an odd prime q when q = c_r (mod r) for at least one r.  D(n) is the largest,
over all vectors, of the least odd prime that the vector does not strike.  Equivalently, D(n) is
the least odd prime x such that no vector strikes every odd prime up to and including x.

Method (exhaustive and exact).  To decide whether some vector strikes every prime in a list T:
take the smallest prime q of T that the classes chosen so far do not strike.  Any vector that
strikes all of T strikes q with some modulus r that has no class yet, and then its class must be
c_r = q mod r.  So it is enough to try, for each such r, the choice c_r = q mod r, and recurse.
Moduli never used along a branch can keep any class; they do not matter.  This visits every
possible way to strike T, so "no branch succeeds" proves that no vector strikes all of T.
One cut keeps the tree small and loses nothing: a modulus r with no class yet can strike at most
max_c #(unstruck primes = c mod r) of the primes still unstruck; if the sum of these maxima over
the free moduli is smaller than the number of unstruck primes, the branch cannot succeed.

Usage:
    python3 cover_depth.py search 10      D(0), ..., D(10) from scratch (about a minute for 10)
    python3 cover_depth.py check FILE     recompute the reach of every vector in FILE
                                          (lines "n D r:c r:c ...", as in witness_vectors.txt)
"""
import sys


def odd_primes_up_to(x):
    sieve = bytearray([1]) * (x + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(x ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [p for p in range(3, x + 1) if sieve[p]]


def first_odd_primes(n):
    bound = 16
    while len(odd_primes_up_to(bound)) < n:
        bound *= 2
    return odd_primes_up_to(bound)[:n]


def can_strike_all(moduli, targets):
    """True if one class per modulus strikes every prime in targets (exhaustive search)."""
    full = (1 << len(targets)) - 1
    # masks[r][c]: the targets that leave remainder c on division by r, as a bit set
    masks = {r: [sum(1 << i for i, t in enumerate(targets) if t % r == c) for c in range(r)]
             for r in moduli}

    def dfs(unstruck, free):
        if unstruck == 0:
            return True
        if not free:
            return False
        capacity = sum(max((unstruck & m).bit_count() for m in masks[r]) for r in free)
        if capacity < unstruck.bit_count():
            return False
        low = unstruck & -unstruck
        q = targets[low.bit_length() - 1]          # the smallest unstruck target
        for r in free:
            rest = unstruck & ~masks[r][q % r]
            if dfs(rest, [s for s in free if s != r]):
                return True
        return False

    return dfs(full, list(moduli))


def depth(n, start=3):
    """D(n), found by raising x from start until no vector strikes every odd prime <= x."""
    moduli = first_odd_primes(n)
    primes = odd_primes_up_to(max(start, 3) * 4 + 100)
    x = start
    while True:
        while primes[-1] < x:
            primes = odd_primes_up_to(primes[-1] * 2)
        targets = [p for p in primes if p <= x]
        if not can_strike_all(moduli, targets):
            return x
        x = next(p for p in primes if p > x)


def reach(vector):
    """The least odd prime that the vector {r: c} does not strike."""
    q, bound = 3, 1024
    primes = odd_primes_up_to(bound)
    i = 0
    while True:
        if i == len(primes):
            bound *= 2
            primes = odd_primes_up_to(bound)
        q = primes[i]
        if not any(q % r == c for r, c in vector.items()):
            return q
        i += 1


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        prev = 3
        for n in range(int(sys.argv[2]) + 1):
            d = depth(n, prev)       # D(n) > D(n-1), so the search may start at D(n-1)
            print(n, d, flush=True)
            prev = d
    elif len(sys.argv) >= 3 and sys.argv[1] == "check":
        bad = 0
        for line in open(sys.argv[2]):
            if not line.strip() or line.startswith("#"):
                continue
            n, d, *pairs = line.split()
            vec = {int(a): int(b) for a, b in (p.split(":") for p in pairs)}
            ok_moduli = sorted(vec) == first_odd_primes(int(n))
            ok_classes = all(0 <= c < r for r, c in vec.items())
            got = reach(vec)
            ok = ok_moduli and ok_classes and got == int(d)
            bad += not ok
            print(n, d, "reach", got, "OK" if ok else "MISMATCH")
        print("all vectors check out" if bad == 0 else f"{bad} problems")
        sys.exit(1 if bad else 0)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
