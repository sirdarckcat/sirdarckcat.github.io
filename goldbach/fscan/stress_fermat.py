#!/usr/bin/env python3
"""Structured differential test of the Fermat kernel binary against Python's pow(2, n-1, n).
Hex lines in, one 0/1 line per batch out (same protocol as test_fermat.c).  Batches mix sizes within a few bits."""
import random, subprocess, sys
import gmpy2
exe = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1; maxb = int(sys.argv[3]) if len(sys.argv) > 3 else 12
random.seed(seed)
M30 = (1 << 30) - 1; M26 = (1 << 26) - 1
cands = []
def add(v):
    v |= 1
    if 41 <= v.bit_length() <= 100: cands.append(v)
for b in range(41, 101):
    top = 1 << (b - 1)
    # near powers of two and all-ones limb patterns
    for d in range(0, 40, 2):
        add((1 << b) - 1 - d); add(top + 1 + d)
    for lw in (26, 30):
        m = (1 << lw) - 1
        pat = 0
        for k in range((b + lw - 1) // lw): pat |= m << (k * lw)
        pat &= (1 << b) - 1
        add(pat); add(pat ^ (1 << (b - 2))); add(pat & ~(1 << (lw)))
        add((pat >> 1) | top)
    # random with long runs of 1s or 0s
    for _ in range(40):
        v = random.getrandbits(b) | top
        mask = ((1 << random.randint(1, b - 1)) - 1) << random.randint(0, b // 2)
        add((v | mask) & ((1 << b) - 1) | top)
        add((v & ~mask) | top)
    # primes at several positions
    for _ in range(40):
        add(int(gmpy2.next_prime(random.getrandbits(b) | top)))
    add(int(gmpy2.prev_prime((1 << b) - 1))); add(int(gmpy2.next_prime(top)))
    # Mersenne-like / Proth-like / semiprimes with close factors
    for _ in range(6):
        p = int(gmpy2.next_prime(random.getrandbits(b // 2) | (1 << (b // 2 - 1))))
        q = int(gmpy2.next_prime(p + random.randint(2, 1000)))
        add(p * q)
# Carmichael numbers (Chernick): (6k+1)(12k+1)(18k+1) all prime -> base-2 Fermat pseudoprimes (composite, must give 1)
found = 0
k = 1
while found < 400 and k < 10**9:
    if gmpy2.is_prime(6*k+1) and gmpy2.is_prime(12*k+1) and gmpy2.is_prime(18*k+1):
        add((6*k+1)*(12*k+1)*(18*k+1)); found += 1
    k += random.randint(1, 200000) if k > 1000 else 1
cands = [v for v in cands if v % 2]
random.shuffle(cands)
# sort partially so batches contain similar sizes (as in the scanner) but also some mixing
cands.sort(key=lambda v: v.bit_length() + random.random() * 3)
batches = []; i = 0
while i < len(cands):
    sz = random.randint(1, maxb); batches.append(cands[i:i+sz]); i += sz
inp = "\n".join("\n".join(f"{v:x}" for v in b) + "\n" for b in batches)
out = subprocess.run([exe], input=inp, capture_output=True, text=True, check=True).stdout.split()
assert len(out) == len(batches), (len(out), len(batches))
tot = prp = bad = comp_prp = 0
for b, o in zip(batches, out):
    for v, c in zip(b, o):
        want = pow(2, v - 1, v) == 1
        tot += 1; prp += want; bad += want != (c == "1")
        if want and not gmpy2.is_prime(v): comp_prp += 1
print(f"{exe}: {tot} structured numbers, {prp} base-2 PRP ({comp_prp} composite pseudoprimes), {bad} mismatches")
sys.exit(bad != 0)
