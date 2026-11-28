"""Base-2 Fermat tests on the GPU for n = cq[i] + k M, 22 limbs of 31 bits (or 23 of 30): a drop-in for gpu_fermat28 / gpu_fermat.kernel / Tester.

    from gpu_fermat31 import kernel, Tester, MultiTester, to_limbs

The kernel has the arguments and the limb layout of gpu_fermat.py's fermat2 (CQ rows and Mv: 21 u32 limbs, idx: int32, kv: u32,
out: u8 flags, T), so `self.k = kernel(limbs)` is the only change in MultiTester.  out[t] = 1 iff 2^(n-1) = 1 (mod n), 0 if not,
and 2 if n is outside 2^642 <= n < 2^668 or even (MultiTester checks the range of the whole pool when it is built).
Verified on the CPU against Python pow (test_fermat31.py: the same source compiled with g++); never run on a GPU by its author.
"""
import os

import numpy as np
import cupy as cp

HERE = os.path.dirname(os.path.abspath(__file__))
_HEAD = "typedef unsigned int u32;\ntypedef unsigned long long u64;\n"
_K = {}


def source(step_file="fermat31_step.cuh"):
    return _HEAD + open(os.path.join(HERE, step_file)).read() + open(os.path.join(HERE, "fermat31_kernel.cuh")).read()


def kernel(limbs=21, step_file="fermat31_step.cuh", maxreg=None):
    """step_file: fermat31_step.cuh (22 limbs of 31 bits, 737 multiplications a step) or fermat30_step.cuh (23 limbs of 30 bits, 805).
    maxreg: NVRTC --maxrregcount (the kernel uses about 80-100 registers: try 64, 72, 80 if occupancy matters)."""
    assert limbs == 21, "fermat31 is built for 21 x u32 input limbs (n < 2^672)"
    key = (step_file, maxreg)
    if key not in _K:
        opts = (f"--maxrregcount={maxreg}",) if maxreg else ()
        _K[key] = cp.RawKernel(source(step_file), "fermat31", options=opts)
    return _K[key]


def to_limbs(x, limbs=21):
    return np.frombuffer(int(x).to_bytes(4 * limbs, "little"), dtype=np.uint32)


def _check_range(N0, M, U, kmax, kmin=0):
    lo = int(N0) - max(int(q) for q in U) + int(kmin) * int(M)
    hi = int(N0) + int(kmax) * int(M)
    if not (1 << 641) <= lo or hi >= (1 << 668):
        raise ValueError(f"n spans {lo.bit_length()}..{hi.bit_length()} bits; fermat31 needs 642..668")


class Tester:
    """Holds one spec's cq[i] = N0 - q_i and M on the GPU; test(idx, k) -> uint8 flags (on the GPU)."""
    def __init__(self, N0, M, U, limbs=21, kmax=1 << 32, kopts=None, kmin=0):
        _check_range(N0, M, U, kmax, kmin)
        self.L = limbs
        self.cq = cp.asarray(np.stack([to_limbs(int(N0) - int(q), limbs) for q in U]))
        self.M = cp.asarray(to_limbs(int(M), limbs))
        self.k = kernel(limbs, **(kopts or {}))

    def test(self, idx, kv, threads=128):
        idx = cp.asarray(idx, dtype=cp.int32)
        kv = cp.asarray(kv, dtype=cp.uint32)
        T = int(idx.size)
        out = cp.empty(T, dtype=cp.uint8)
        if T:
            self.k(((T + threads - 1) // threads,), (threads,), (self.cq, self.M, idx, kv, out, np.int32(T)))
        return out


class MultiTester:
    """cq rows N0_v - q of every variant in the batch (shared M); test(idx, k) -> uint8 flags (as search_gpu3.MultiTester)."""
    def __init__(self, specs, limbs=21, kmax=1 << 32, kopts=None, kmin=0):
        M = int(specs[0]["M"])
        assert all(int(s["M"]) == M for s in specs), "a pool needs one M"
        rows, self.off = [], []
        for s in specs:
            N0 = int(s["N0"])
            assert N0 > max(s["residual"]), "N0 - q must be positive"
            _check_range(N0, M, s["residual"], kmax, kmin)
            self.off.append(len(rows))
            rows.extend(to_limbs(N0 - int(q), limbs) for q in s["residual"])
        self.cq = cp.asarray(np.stack(rows))
        self.M = cp.asarray(to_limbs(M, limbs))
        self.k = kernel(limbs, **(kopts or {}))

    def test(self, idx, kv, threads=128):
        T = int(idx.size)
        out = cp.empty(T, dtype=cp.uint8)
        if T:
            self.k(((T + threads - 1) // threads,), (threads,), (self.cq, self.M, idx, kv, out, np.int32(T)))
        return out
