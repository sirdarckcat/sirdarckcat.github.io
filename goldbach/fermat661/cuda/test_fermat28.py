#!/usr/bin/env python3
"""The CUDA kernel source (fermat28_step.cuh + fermat28_kernel.cuh) compiled for the CPU, against Python pow.

    python3 test_fermat28.py [--count N]

Same inputs as gpu_fermat.py's fermat2: CQ rows (21 u32 limbs of N0 - q), Mv (21 limbs of M), idx, kv; n = CQ[idx] + M k.
"""
import argparse, ctypes, json, os, random, subprocess, sys
import numpy as np
import gmpy2

HERE = os.path.dirname(os.path.abspath(__file__))


def build():
    step = os.environ.get("FM28_STEP", "fermat28_step.cuh")          # which generated step to test, e.g. fermat28_step_s1r.cuh
    tag = os.path.splitext(step)[0].replace("fermat28_", "")
    out = os.path.join(HERE, f"libfermat28_cpu_{tag}.so")
    srcs = [os.path.join(HERE, f) for f in ("fermat28_cpu.cpp", step, "fermat28_kernel.cuh")]
    if not os.path.exists(out) or os.path.getmtime(out) < max(os.path.getmtime(s) for s in srcs):
        subprocess.check_call(["g++", "-O2", f'-DSTEP_FILE="{step}"', "-Wno-unused", "-Wno-unknown-pragmas", "-shared", "-fPIC", "-o", out, srcs[0]])
    return out


def to_limbs(x, limbs=21):
    return np.frombuffer(int(x).to_bytes(4 * limbs, "little"), dtype=np.uint32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    lib = ctypes.CDLL(build())
    lib.run_cpu.argtypes = [ctypes.c_void_p] * 5 + [ctypes.c_int]
    lib.set_dbg.argtypes = [ctypes.c_void_p]
    rng = random.Random(a.seed)
    ok = True

    def run(CQ, Mv, idx, kv):
        out = np.zeros(len(idx), dtype=np.uint8)
        CQ = np.ascontiguousarray(CQ, dtype=np.uint32); Mv = np.ascontiguousarray(Mv, dtype=np.uint32)
        idx = np.ascontiguousarray(idx, dtype=np.int32); kv = np.ascontiguousarray(kv, dtype=np.uint32)
        lib.run_cpu(CQ.ctypes.data, Mv.ctypes.data, idx.ctypes.data, kv.ctypes.data, out.ctypes.data, len(idx))
        return out

    def check_numbers(name, ns):
        nonlocal ok
        CQ = np.stack([to_limbs(n) for n in ns])
        got = run(CQ, to_limbs(0), np.arange(len(ns)), np.zeros(len(ns), dtype=np.uint32))
        bad = pos = 0
        for n, g in zip(ns, got):
            bl = n.bit_length()
            if not (642 <= bl <= 668) or n % 2 == 0:
                exp = 2
            else:
                exp = 1 if pow(2, n - 1, n) == 1 else 0
            pos += exp == 1
            bad += int(g) != exp
        print(f"  {name:<44s} {len(ns):5d} numbers  positives {pos:4d}  wrong {bad}", flush=True)
        ok &= bad == 0

    def rnd(bits):  # noqa
        return rng.getrandbits(bits) | (1 << (bits - 1)) | 1

    # the residue itself: y = 2^(1-n) mod n for many random n (a wrong carry shows up here even when the verdict is 0 anyway)
    print("final residue 2^(1-n) mod n (kernel y before the last reduction), random n")
    nres = max(a.count * 10, 1000)
    ns = [rnd(rng.randint(642, 668)) for _ in range(nres)]
    dbg = np.zeros((nres, 24), dtype=np.uint32)
    lib.set_dbg(dbg.ctypes.data)
    CQ = np.stack([to_limbs(n) for n in ns])
    run(CQ, to_limbs(0), np.arange(nres), np.zeros(nres, dtype=np.uint32))
    bad = 0
    for n, row in zip(ns, dbg):
        y = sum(int(v) << (28 * i) for i, v in enumerate(row))
        bad += (y >= 4 * n) or (y % n != pow(2, -(n - 1), n))
    print(f"  {'residues, 642..668 bits':<44s} {nres:5d} numbers  wrong {bad}")
    ok &= bad == 0
    print("arbitrary numbers (M = 0, k = 0)")
    for bits in (668, 665, 664, 663, 661, 660, 655, 650, 646, 642, 669):
        check_numbers(f"random odd, {bits} bits", [rnd(bits) for _ in range(a.count // 3)])
    check_numbers("out of range: 641, 670, 672 bits, even", [rnd(641), rnd(670), rnd(672), rnd(664) - 1, rnd(650) + 1 if False else rnd(650) - 1])
    check_numbers("primes 642..668 bits", [int(gmpy2.next_prime(gmpy2.mpz(rnd(rng.randint(642, 667))))) for _ in range(a.count // 3)])
    ps = []
    while len(ps) < 12:
        p = int(gmpy2.next_prime(gmpy2.mpz(rnd(330))))
        for kk in range(2, 600, 2):
            q = kk * (p - 1) + 1
            n = p * q
            if q > 2 and gmpy2.is_prime(q) and pow(2, n - 1, n) == 1 and 642 <= n.bit_length() <= 668:
                ps.append(n)
                break
    check_numbers("base-2 pseudoprimes", ps)
    check_numbers("edge values", [(1 << 664) - 1, (1 << 664) + 1, (1 << 665) - 1, (1 << 668) - 1, (1 << 668) + 3, (1 << 642) | 1,
                                  (1 << 643) - 1, (1 << 663) + 7, (1 << 669) - 1])
    # campaign 3 style: n = N0 - q + k M
    print("campaign 3 style: n = N0 - q + k M with 21 x u32 limbs")
    camp = json.load(open(os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")))
    N0, M = int(camp["N0"]), int(camp["M"])
    U = camp["residual"]
    CQ = np.stack([to_limbs(N0 - q) for q in U])
    for name, lo, hi, cnt in (("k in [2^31, 2^32)", 1 << 31, 1 << 32, a.count), ("k small", 0, 1 << 20, a.count // 2),
                              ("k in [2^28, 2^31)", 1 << 28, 1 << 31, a.count // 2)):
        kv = np.array([rng.randrange(lo, hi) for _ in range(cnt)], dtype=np.uint32)
        idx = np.array([rng.randrange(len(U)) for _ in range(cnt)], dtype=np.int32)
        got = run(CQ, to_limbs(M), idx, kv)
        bad = pos = oor = 0
        for i, k, g in zip(idx.tolist(), kv.tolist(), got):
            n = N0 - U[i] + k * M
            if not (642 <= n.bit_length() <= 668):
                exp = 2; oor += 1
            else:
                exp = 1 if pow(2, n - 1, n) == 1 else 0
            pos += exp == 1
            bad += int(g) != exp
        print(f"  {name:<44s} {cnt:5d} tests    positives {pos:4d}  out-of-range {oor}  wrong {bad}", flush=True)
        ok &= bad == 0
    # members of one progression that are prime: N0 - q + kM for the prime ones
    prs = []
    k = 1 << 31
    while len(prs) < 40:
        i = rng.randrange(len(U))
        n = N0 - U[i] + k * M
        if gmpy2.is_prime(n):
            prs.append((i, k))
        k += rng.randrange(1, 5000)
    got = run(CQ, to_limbs(M), np.array([p[0] for p in prs]), np.array([p[1] for p in prs], dtype=np.uint32))
    print(f"  {'real primes N0 - q + kM':<44s} {len(prs):5d} tests    all pass: {bool(got.all())}")
    ok &= bool(got.all())
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
