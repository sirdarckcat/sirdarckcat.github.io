#!/usr/bin/env python3
"""Forcing a generator for A025018 term by term.

A025018: the even numbers N >= 4 whose least Goldbach summand g(N) (least prime q with N - q
prime) is larger than that of every smaller even number.  Each rule below is a way to produce the
next term from what has been produced so far.  For each rule the script prints the terms it
generates and the first place where it leaves the true sequence: the term that forces the next
idea.  The last rule never leaves it, and GoldbachGaps/RecordGen.lean proves that.

    python3 -I ladder.py [number of terms, default 14]
"""
import sys

LIMIT = 200000


def sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return s


PR = sieve(LIMIT)
PRIMES = [i for i in range(LIMIT) if PR[i]]


def g(N):
    for q in PRIMES:
        if q > N - 2:
            return None
        if PR[N - q]:
            return q


def truth(n):
    out, best, N = [], 0, 4
    while len(out) < n:
        v = g(N)
        if v > best:
            best = v
            out.append((N, v))
        N += 2
    return out


def next_prime(q):
    q += 1
    while not PR[q]:
        q += 1
    return q


def run(rule, n):
    """rule(terms) -> next (N, value); terms is the list produced so far"""
    terms = [(4, 2)]
    while len(terms) < n:
        t = rule(terms)
        if t is None:
            break
        terms.append(t)
    return terms


def first_even(after, ok):
    N = after + 2
    while N < LIMIT - 2:
        if ok(N):
            return N
        N += 2
    return None


# Rule 1: the next even number; its value is the next prime.
def rule1(terms):
    N, v = terms[-1]
    return (N + 2, next_prime(v))


# Rule 2: the next even N for which N - v is composite, v the last value; value: the next prime.
def rule2(terms):
    N, v = terms[-1]
    M = first_even(N, lambda M: not PR[M - v])
    return (M, next_prime(v))


# Rule 3: N - v composite for every value v produced so far; value: the next prime.
def rule3(terms):
    N, v = terms[-1]
    vals = [x for _, x in terms]
    M = first_even(N, lambda M: all(not PR[M - x] for x in vals))
    return (M, next_prime(v))


# Rule 4: as rule 3, but the value is the first prime that hits the new number (primes can be skipped).
def rule4(terms):
    N, v = terms[-1]
    vals = [x for _, x in terms]
    M = first_even(N, lambda M: all(not PR[M - x] for x in vals))
    return (M, g(M))


# Rule 5: N - q composite for EVERY prime q up to the last value (the skipped ones included);
# value: the first prime that hits.  This is the sieve of translates.
def rule5(terms):
    N, v = terms[-1]
    qs = [q for q in PRIMES if q <= v]
    M = first_even(N, lambda M: all(not PR[M - q] for q in qs))
    return (M, g(M))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    T = truth(n)
    print("A025018 / A025019:", " ".join(f"{N}:{v}" for N, v in T))
    print()
    rules = [("1. next even number; value = next prime", rule1),
             ("2. next even N with N - (last value) composite; value = next prime", rule2),
             ("3. N - v composite for every earlier value v; value = next prime", rule3),
             ("4. as 3, value = first prime q with N - q prime", rule4),
             ("5. N - q composite for every prime q up to the last value; value = first prime that hits", rule5)]
    for name, rule in rules:
        out = run(rule, n)
        k = 0
        while k < len(out) and k < len(T) and out[k] == T[k]:
            k += 1
        print(f"rule {name}")
        print("   produces:", " ".join(f"{N}:{v}" for N, v in out[:min(len(out), k + 2)]), "..." if len(out) > k + 2 else "")
        if k < len(T) and k < len(out):
            N, v = out[k]
            tn, tv = T[k]
            why = []
            if N != tn:
                if N < tn:
                    why.append(f"{N} is not a term: {N} = {g(N)} + {N - g(N)}, so its least summand is {g(N)}")
                else:
                    why.append(f"it skips {tn}")
            elif v != tv:
                why.append(f"the value of {tn} is {tv}, not {v}: " + ", ".join(f"{tn} - {q} = {tn - q}" for q in PRIMES if v <= q < tv) + " are composite")
            print(f"   right for {k} terms; breaks at term {k + 1} (true {tn}:{tv}, rule {N}:{v}): " + "; ".join(why))
        else:
            print(f"   right for all {k} terms asked")
        print()
    # the trace of rule 5 as a sieve: strikers in order, hits and misses of the front
    print("The generator as a sieve.  Strikers q = 2, 3, 5, ... in order; the front is the smallest even")
    print("number not yet struck (N is struck by q when N - q is prime).  A striker that hits the front")
    print("makes it a term with value q, and the front moves to the next unstruck even number.")
    front, struck_by = 4, []
    shown = 0
    for q in PRIMES:
        if shown >= n:
            break
        struck_by.append(q)
        if q <= front - 2 and PR[front - q]:
            new = first_even(front, lambda M: all(not PR[M - r] for r in struck_by))
            def lpf(x):
                for p in PRIMES:
                    if x % p == 0:
                        return p
            cover = ", ".join(f"{new}-{r}={lpf(new - r)}*{(new - r) // lpf(new - r)}" for r in struck_by[1:8])
            print(f"  q = {q:4d} hits the front {front}: {front} = {q} + {front - q}.  Term {front}, value {q}.  New front {new}"
                  + (f"   ({cover}{', ...' if len(struck_by) > 8 else ''})" if len(struck_by) > 1 else ""))
            front = new
            shown += 1
        else:
            print(f"  q = {q:4d} misses the front {front}: {front} - {q} = {front - q} is composite")


main()
