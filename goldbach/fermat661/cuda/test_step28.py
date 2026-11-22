#!/usr/bin/env python3
"""fm28_step alone against big-integer arithmetic, on random and adversarial inputs (limbs all ones, values near 4n, n near
2^668): the output must be below 4n, have limbs below 2^28, and be congruent to 2^b X^2 2^-672 mod n."""
import ctypes, os, random, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_fermat28 import build

lib = ctypes.CDLL(build())
lib.step_test.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
lib.inv_test.argtypes = [ctypes.c_uint32]; lib.inv_test.restype = ctypes.c_uint32
M28 = (1 << 28) - 1


def limbs(v):
    return np.array([(v >> (28 * i)) & M28 for i in range(24)], dtype=np.uint32)


def val(l):
    return sum(int(v) << (28 * i) for i, v in enumerate(l))


rng = random.Random(11)
R = 1 << 672
bad = total = 0
worst = 0
def one(n, X, b):
    global bad, total, worst
    np_ = lib.inv_test(n & 0xFFFFFFFF)
    assert (n * (((1 << 28) - np_) ) ) % (1 << 28) == 1 or ((n * np_ + 1) % (1 << 28) == 0)
    xo = np.zeros(24, dtype=np.uint32)
    xi, nl = limbs(X), limbs(n)
    lib.step_test(xi.ctypes.data, nl.ctypes.data, np_, b, xo.ctypes.data)
    Y = val(xo)
    good = Y < 4 * n and all(int(v) >> 28 == 0 for v in xo) and (Y - ((1 << b) * X * X * pow(R, -1, n))) % n == 0
    total += 1
    bad += not good
    worst = max(worst, Y / n)
    if not good and bad < 4:
        print("FAIL bits", n.bit_length(), "b", b, "Y/n", Y / n)

for trial in range(6000):
    bits = rng.choice([642, 650, 660, 664, 665, 667, 668, 668, 668])
    n = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
    kind = trial % 6
    if kind == 0: X = rng.randrange(0, 4 * n)
    elif kind == 1: X = 4 * n - 1 - rng.randrange(0, 1000)
    elif kind == 2: X = min(4 * n - 1, (1 << 670) - 1) if (1 << 670) - 1 < 4 * n else 4 * n - 1
    elif kind == 3: X = rng.randrange(0, 1 << 40)
    elif kind == 4: X = (rng.getrandbits(24 * 28) | sum(M28 << (28 * i) for i in range(0, 24, 2))) % (4 * n)
    else: X = rng.randrange(n, 4 * n)
    one(n, X, rng.randrange(2))
# n with all limbs ones: 2^668 - 1 style and X maxima
for n in ((1 << 668) - 1, (1 << 668) - 3, (1 << 667) | 1, (1 << 642) | 1, (1 << 668) - (1 << 40) - 1):
    for X in (4 * n - 1, 4 * n - 2, 2 * n, n, 1, 0, (1 << 24 * 28) - 1 if (1 << 24 * 28) - 1 < 4 * n else 4 * n - 1):
        for b in (0, 1):
            one(n, X, b)
print(f"{total} steps, wrong {bad}, largest Y/n seen {worst:.4f}")
sys.exit(1 if bad else 0)
