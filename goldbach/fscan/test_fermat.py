#!/usr/bin/env python3
"""Check fermat52.h (through ./test_fermat) against Python's pow on random numbers of 41 to 100 bits,
a quarter of them prime, with mixed sizes inside a batch."""
import random, subprocess, sys
import gmpy2
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
batches = []
for bits in range(41, 101):
    for _ in range(300):
        b = []
        for _ in range(random.randint(1, int(sys.argv[3]) if len(sys.argv) > 3 else 16)):
            w = max(41, bits - (random.randint(0, 5) if random.random() < 0.33 else 0))
            v = random.getrandbits(w) | (1 << (w - 1)) | 1
            if random.random() < 0.25:
                p = int(gmpy2.next_prime(v))
                if p.bit_length() <= 100:
                    v = p
            b.append(v)
        batches.append(b)
inp = "\n".join("\n".join(f"{v:x}" for v in b) + "\n" for b in batches)
out = subprocess.run([sys.argv[2] if len(sys.argv) > 2 else "./test_fermat"], input=inp, capture_output=True, text=True, check=True).stdout.split()
assert len(out) == len(batches), (len(out), len(batches))
tot = prp = bad = 0
for b, o in zip(batches, out):
    assert len(o) == len(b)
    for v, c in zip(b, o):
        want = pow(2, v - 1, v) == 1
        tot += 1; prp += want; bad += want != (c == "1")
print(f"{tot} numbers, {prp} base-2 probable primes, {bad} mismatches")
sys.exit(bad != 0)
