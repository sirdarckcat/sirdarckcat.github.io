#!/usr/bin/env python3
"""fm28_step alone against big-integer arithmetic, on random and adversarial inputs (limbs all ones, values near 4n, n near
2^668): the output must be below 4n, have limbs below 2^28, and be congruent to 2^b X^2 2^-672 mod n."""
import ctypes, os, random, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_fermat28 import build
from fm_geom import geometry

STEPFILE = os.environ.get("FM28_STEP", "fermat28_step.cuh")
W, NLIMB, NMAX = geometry(STEPFILE)                  # (28, 24, 668) for the 28-bit steps; (29, 23, 663) for fermat29_step_*.cuh
RBITS = W * NLIMB
lib = ctypes.CDLL(build())
lib.step_test.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
lib.inv_test.argtypes = [ctypes.c_uint32]; lib.inv_test.restype = ctypes.c_uint32
M28 = (1 << W) - 1


def limbs(v):
    return np.array([(v >> (W * i)) & M28 for i in range(NLIMB)], dtype=np.uint32)


def val(l):
    return sum(int(v) << (W * i) for i, v in enumerate(l))


RED = "#define FM28_REDUNDANT" in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), STEPFILE)).read()
OUTBITS = 29 if RED else W                        # the redundant steps leave limbs below 2^29
rng = random.Random(11)
R = 1 << RBITS
bad = total = 0
worst = 0
def one(n, X, b):
    global bad, total, worst
    np_ = lib.inv_test(n & 0xFFFFFFFF)
    assert (n * (((1 << W) - np_) ) ) % (1 << W) == 1 or ((n * np_ + 1) % (1 << W) == 0)
    xo = np.zeros(NLIMB, dtype=np.uint32)
    xi, nl = limbs(X), limbs(n)
    lib.step_test(xi.ctypes.data, nl.ctypes.data, np_, b, xo.ctypes.data)
    Y = val(xo)
    good = Y < 4 * n and all(int(v) >> OUTBITS == 0 for v in xo) and (Y - ((1 << b) * X * X * pow(R, -1, n))) % n == 0
    total += 1
    bad += not good
    worst = max(worst, Y / n)
    if not good and bad < 4:
        print("FAIL bits", n.bit_length(), "b", b, "Y/n", Y / n)

for trial in range(6000):
    bits = rng.choice([642, 650, 660, NMAX - 4, NMAX - 3, NMAX - 1, NMAX, NMAX, NMAX])
    n = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
    kind = trial % 6
    if kind == 0: X = rng.randrange(0, 4 * n)
    elif kind == 1: X = 4 * n - 1 - rng.randrange(0, 1000)
    elif kind == 2: X = min(4 * n - 1, (1 << (RBITS - 2)) - 1) if (1 << (RBITS - 2)) - 1 < 4 * n else 4 * n - 1
    elif kind == 3: X = rng.randrange(0, 1 << 40)
    elif kind == 4: X = (rng.getrandbits(NLIMB * W) | sum(M28 << (W * i) for i in range(0, NLIMB, 2))) % (4 * n)
    else: X = rng.randrange(n, 4 * n)
    one(n, X, rng.randrange(2))
# n with all limbs ones: 2^668 - 1 style and X maxima
for n in ((1 << NMAX) - 1, (1 << NMAX) - 3, (1 << (NMAX - 1)) | 1, (1 << 642) | 1, (1 << NMAX) - (1 << 40) - 1):
    for X in (4 * n - 1, 4 * n - 2, 2 * n, n, 1, 0, (1 << RBITS) - 1 if (1 << RBITS) - 1 < 4 * n else 4 * n - 1):
        for b in (0, 1):
            one(n, X, b)
# the redundant-limb steps (fermat28_step_*r.cuh): inputs with limbs below 2^29 (the same value, some of the carries left in the limbs), outputs likewise
if RED:
    def redundant(X, mode):
        l = [int(v) for v in limbs(X)]
        if mode == 0:                                        # a random carry moved down into the limb below
            for i in range(22, -1, -1):
                if l[i + 1] >= 1 and rng.random() < 0.7:
                    l[i] += 1 << 28; l[i + 1] -= 1
        elif mode == 1:                                      # as many limbs as possible near 2^29 - 1
            for i in range(0, 23):
                if l[i + 1] >= 1:
                    l[i] += 1 << 28; l[i + 1] -= 1
        return l
    def one_r(n, l, b):
        global bad, total, worst
        X = sum(v << (28 * i) for i, v in enumerate(l))
        np_ = lib.inv_test(n & 0xFFFFFFFF)
        xo = np.zeros(24, dtype=np.uint32)
        xi, nl = np.array(l, dtype=np.uint32), limbs(n)
        lib.step_test(xi.ctypes.data, nl.ctypes.data, np_, b, xo.ctypes.data)
        Y = val(xo)
        good = Y < 4 * n and all(int(v) >> 29 == 0 for v in xo) and (Y - ((1 << b) * X * X * pow(R, -1, n))) % n == 0
        total += 1; bad += not good; worst = max(worst, Y / n)
        if not good and bad < 4:
            print("FAIL redundant: bits", n.bit_length(), "b", b, "Y/n", Y / n, "max limb", max(l) >> 28)
    for trial in range(6000):
        bits = rng.choice([642, 650, 660, 664, 665, 667, 668, 668])
        n = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        kind = trial % 4
        X = rng.randrange(0, 4 * n) if kind == 0 else (4 * n - 1 - rng.randrange(0, 1000) if kind == 1 else rng.randrange(n, 4 * n) if kind == 2 else rng.randrange(0, 1 << 600))
        one_r(n, redundant(X, trial % 2), rng.randrange(2))
    # the extremes of C3': limbs 0..21 at 2^29 - 1; and limbs 0..22 at 2^29 - 1 with the top limb as large as X < 4n allows
    for n in ((1 << 668) - 1, (1 << 668) - 3, (1 << 667) | 1, (1 << 650) | 1, (1 << 642) | 1):
        l = [(1 << 29) - 1] * 22 + [0, 0]
        if sum(v << (28 * i) for i, v in enumerate(l)) < 4 * n:
            for b in (0, 1):
                one_r(n, l, b)
        low = sum(((1 << 29) - 1) << (28 * i) for i in range(23))
        if low < 4 * n:
            top = min((1 << 29) - 1, (4 * n - 1 - low) >> (28 * 23))
            l = [(1 << 29) - 1] * 23 + [top]
            assert sum(v << (28 * i) for i, v in enumerate(l)) < 4 * n
            for b in (0, 1):
                one_r(n, l, b)
print(f"{total} steps, wrong {bad}, largest Y/n seen {worst:.4f}")
sys.exit(1 if bad else 0)
