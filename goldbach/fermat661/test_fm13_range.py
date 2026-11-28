#!/usr/bin/env python3
"""fm13's exact range, against gmpy2: residues y = 2^(1-n) mod n and verdicts.

    python3 test_fm13_range.py [record.json]

1. Random odd numbers (400) and primes (40) at every bit length 660..680 and at 690, 700, 704: exact up to 672 bits; from 673
   bits wrong residues, and the verdicts that go wrong are false composites (primes reported composite), never false PRPs.
   Reason: a step maps {A < 4n} to itself while 16 n < R = 2^676 (Y < 2 (n + 16 n^2 / R)), i.e. for n < 2^672.
2. 100,000 random odd n in [2^664, 10^200) and 5,000 primes there (the 665-bit numbers of the 200-digit campaigns): exact.
3. With a record.json (N, g, Q): every N - q for the odd primes q < Q, and N - g: exact.
"""
import json, random, sys, time
import numpy as np, gmpy2
import fm13
lib = fm13.load(); NW = fm13.NW


def run(ns):
    buf = np.concatenate([fm13.words(n) for n in ns]); vd = np.zeros(len(ns), dtype=np.uint8); y = np.zeros(len(ns) * NW, dtype=np.uint64)
    lib.fm13_test(len(ns), buf.ctypes.data, vd.ctypes.data, y.ctypes.data)
    return vd, [int.from_bytes(y[i * NW:(i + 1) * NW].tobytes(), "little") for i in range(len(ns))]


def check(ns, label):
    bad_v = bad_y = fp = fn = prp = 0
    for i in range(0, len(ns), 4096):
        part = ns[i:i + 4096]
        vd, ys = run(part)
        for n, v, y in zip(part, vd, ys):
            r = int(gmpy2.powmod(2, n - 1, n)); ref = r == 1; prp += ref
            if bool(v) != ref:
                bad_v += 1; fp += bool(v) and not ref; fn += ref and not bool(v)
            if (y * r) % n != 1:                       # y = 2^(1-n) mod n  <=>  y * 2^(n-1) = 1 (mod n)
                bad_y += 1
    print(f"{label}: {len(ns)} numbers ({prp} base-2 PRP), verdict mismatches {bad_v} (false PRP {fp}, false composite {fn}), "
          f"residue mismatches {bad_y}", flush=True)
    return bad_v, bad_y, fp


rng = random.Random(2026)
exact_to = None
for b in list(range(660, 681)) + [690, 700, 704]:
    ns = [rng.getrandbits(b) | (1 << (b - 1)) | 1 for _ in range(400)]
    ps = [p for p in (int(gmpy2.next_prime(rng.getrandbits(b - 1) | (3 << (b - 2)))) for _ in range(40)) if p.bit_length() == b]
    bv, by, fp = check(ns + ps, f"{b} bits")
    assert fp == 0, "a false PRP"
    if bv == 0 and by == 0 and (exact_to is None or exact_to == b - 1):
        exact_to = b
assert exact_to is not None and exact_to >= 672, exact_to
lo, hi = 1 << 664, 10 ** 200
assert check([rng.randrange(lo, hi) | 1 for _ in range(100000)], "random odd n in [2^664, 10^200)")[:2] == (0, 0)
ps = []
while len(ps) < 5000:
    p = int(gmpy2.next_prime(rng.randrange(lo, hi - 10 ** 190)))
    if p < hi:
        ps.append(p)
assert check(ps, "primes in [2^664, 10^200)")[:2] == (0, 0)
if len(sys.argv) > 1:
    r = json.load(open(sys.argv[1])); N, g, Q = int(r["N"]), int(r["g"]), int(r["Q"])
    qs = [q for q in range(3, Q) if gmpy2.is_prime(q)]
    assert check([N - q for q in qs], f"record N ({N.bit_length()} bits): N - q for the {len(qs)} odd primes q < {Q}")[:2] == (0, 0)
    vd, _ = run([N - g]); assert vd[0] == 1
    print(f"N - g ({g}): PRP")
print(f"all ok: exact up to {exact_to} bits in the scan")
