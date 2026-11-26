#!/usr/bin/env python3
"""fm31_step alone against big-integer arithmetic (22 limbs of 31 bits, or 23 of 30 with FM31_W=30), on random and adversarial inputs
(limbs all ones, values near 4n, n near 2^668): the output must be below 4n, have limbs below 2^w, and be congruent to
2^b X^2 R^-1 mod n with R = 2^(w NL).

    python3 test_step31.py            # 31-bit limbs
    FM31_W=30 python3 test_step31.py  # 30-bit limbs
"""
import ctypes, os, random, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
W = int(os.environ.get("FM31_W", "31"))
STEP = "fermat31_step.cuh" if W == 31 else "fermat30_step.cuh"


def build(step=STEP):
    tag = os.path.splitext(step)[0].replace("fermat", "f")
    out = os.path.join(HERE, f"libfermat31_cpu_{tag}.so")
    srcs = [os.path.join(HERE, f) for f in ("fermat31_cpu.cpp", step)]
    if not os.path.exists(out) or os.path.getmtime(out) < max(os.path.getmtime(s) for s in srcs):
        subprocess.check_call(["g++", "-O2", f'-DSTEP_FILE="{step}"', "-Wno-unused", "-Wno-unknown-pragmas", "-shared", "-fPIC", "-o", out, srcs[0]])
    return out


if __name__ == "__main__":
    lib = ctypes.CDLL(build())
    lib.step_test.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    lib.inv_test.argtypes = [ctypes.c_uint32]; lib.inv_test.restype = ctypes.c_uint32
    NL = lib.limb_count()
    assert lib.limb_bits() == W
    MASK = (1 << W) - 1
    R = 1 << (W * NL)

    def limbs(v):
        return np.array([(v >> (W * i)) & MASK for i in range(NL)], dtype=np.uint32)

    def val(l):
        return sum(int(v) << (W * i) for i, v in enumerate(l))

    rng = random.Random(11)
    bad = total = 0
    worst = 0

    def one(n, X, b):
        global bad, total, worst
        np_ = lib.inv_test(n & 0xFFFFFFFF)
        assert (n * np_ + 1) % (1 << W) == 0
        xo = np.zeros(NL, dtype=np.uint32)
        xi, nl = limbs(X), limbs(n)
        lib.step_test(xi.ctypes.data, nl.ctypes.data, np_, b, xo.ctypes.data)
        Y = val(xo)
        good = Y < 4 * n and all(int(v) >> W == 0 for v in xo) and (Y - ((1 << b) * X * X * pow(R, -1, n))) % n == 0
        total += 1
        bad += not good
        worst = max(worst, Y / n)
        if not good and bad < 4:
            print("FAIL bits", n.bit_length(), "b", b, "Y/n", Y / n, "limbs ok", all(int(v) >> W == 0 for v in xo))

    for trial in range(6000):
        bits = rng.choice([642, 650, 660, 664, 665, 667, 668, 668, 668])
        n = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        kind = trial % 6
        if kind == 0: X = rng.randrange(0, 4 * n)
        elif kind == 1: X = 4 * n - 1 - rng.randrange(0, 1000)
        elif kind == 2: X = min(4 * n - 1, (1 << 670) - 1)
        elif kind == 3: X = rng.randrange(0, 1 << 40)
        elif kind == 4: X = (rng.getrandbits(NL * W) | sum(MASK << (W * i) for i in range(0, NL, 2))) % (4 * n)
        else: X = rng.randrange(n, 4 * n)
        one(n, X, rng.randrange(2))
    for n in ((1 << 668) - 1, (1 << 668) - 3, (1 << 667) | 1, (1 << 642) | 1, (1 << 668) - (1 << 40) - 1):
        for X in (4 * n - 1, 4 * n - 2, 2 * n, n, 1, 0, min(R - 1, 4 * n - 1)):
            for b in (0, 1):
                one(n, X, b)
    # every limb at its maximum 2^w - 1 (the value must still be below 4n: top limbs cut)
    for n in ((1 << 668) - 1, (1 << 667) | 1, (1 << 650) | 1):
        top = sum(MASK << (W * i) for i in range(0, 21))
        if top < 4 * n:
            for b in (0, 1):
                one(n, top, b)
    print(f"{W}-bit limbs x {NL}: {total} steps, wrong {bad}, largest Y/n seen {worst:.4f}")
    sys.exit(1 if bad else 0)
