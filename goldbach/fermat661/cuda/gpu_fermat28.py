"""Base-2 Fermat tests on the GPU for n = cq[i] + k M, 24 limbs of 28 bits: a drop-in for gpu_fermat.kernel / Tester.

    from gpu_fermat28 import kernel, Tester, MultiTester, to_limbs

The kernel has the arguments and the limb layout of gpu_fermat.py's fermat2 (CQ rows and Mv: 21 u32 limbs, idx: int32, kv: u32,
out: u8 flags, T), so `self.k = kernel(limbs)` is the only change in MultiTester.  out[t] = 1 iff 2^(n-1) = 1 (mod n), 0 if not,
and 2 if n is outside 2^642 <= n < 2^668 or even (MultiTester checks the range of the whole pool when it is built).
Verified on the CPU against Python pow (test_fermat28.py: the same source compiled with g++); never run on a GPU by its author.
"""
import os

import numpy as np
import cupy as cp

HERE = os.path.dirname(os.path.abspath(__file__))
_HEAD = "typedef unsigned int u32;\ntypedef unsigned long long u64;\n"
_K = {}


def source(step_file="fermat28_step.cuh"):
    return _HEAD + open(os.path.join(HERE, step_file)).read() + open(os.path.join(HERE, "fermat28_kernel.cuh")).read()


def persist_source(step_file="fermat28_step.cuh"):
    """The source of the persistent pool kernel `fermat28_persist` (fermat28_persist_kernel.cuh): fermat28_kernel.cuh's kernel body turned into a device function fm28_test(cq, Mv, k, dbg) by
    exact text replacements (each must match once: the test IS the production kernel's code), followed by the persistent kernel.  The production kernel `fermat28` is not in this module."""
    kern = open(os.path.join(HERE, "fermat28_kernel.cuh")).read()
    i = kern.index('extern "C" __global__ void fermat28(')
    head, body = kern[:i], kern[i:]
    old_head = ('extern "C" __global__ void fermat28(const u32 *CQ, const u32 *Mv, const int *idx, const u32 *kv,\n'
                '                                    unsigned char *out, int T) {\n'
                '    int tid = blockIdx.x * blockDim.x + threadIdx.x;\n'
                '    if (tid >= T) return;\n'
                '    const u32 *cq = CQ + (size_t)idx[tid] * L32;\n'
                '    const u32 k = kv[tid];\n')
    new_head = '__device__ __forceinline__ int fm28_test(const u32 *cq, const u32 *Mv, const u32 k, const int tid) {\n'
    for old, new in ((old_head, new_head), ("{ out[tid] = 2; return; }", "return 2;"), ("    out[tid] = (unsigned char)one;\n}", "    return one;\n}")):
        assert body.count(old) == 1, f"fermat28_kernel.cuh changed: {old[:60]!r}"
        body = body.replace(old, new)
    return _HEAD + open(os.path.join(HERE, step_file)).read() + head + body + open(os.path.join(HERE, "fermat28_persist_kernel.cuh")).read()


def kernel(limbs=21, step_file="fermat28_step.cuh", asm_mad=False, maxreg=None):
    """step_file: fermat28_step_s1.cuh / fermat28_step.cuh (2) / fermat28_step_s4.cuh = 1, 2 or 4 independent accumulators per
    column; fermat28_step_s1r.cuh / fermat28_step_r.cuh are the same with redundant limbs (no carry chain after the doubling, see
    FERMAT28.md).  asm_mad=True writes every product as PTX mad.wide.u32 instead of leaving the choice to the compiler.
    maxreg: NVRTC --maxrregcount (try 96, 128, 160 if the kernel uses many registers and occupancy is low)."""
    assert limbs == 21, "fermat28 is built for 21 x u32 input limbs (n < 2^672)"
    key = (step_file, asm_mad, maxreg)
    if key not in _K:
        opts = (("-DFM28_ASM=1",) if asm_mad else ()) + ((f"--maxrregcount={maxreg}",) if maxreg else ())
        _K[key] = cp.RawKernel(source(step_file), "fermat28", options=opts)
        carve = os.environ.get("FERMAT_CARVEOUT", "")
        if carve:                       # FERMAT_CARVEOUT=100: ask for the largest shared-memory carve-out of the SM's L1 / shared memory, the configuration the sieve kernels (64 KB of shared memory a CTA)
            try:                        # need: a kernel that asks for none may leave an SM configured so that a sieve CTA cannot sit beside the Fermat CTAs (see sieve200/cuda/DEEPSIEVE.md, overlap)
                _K[key].preferred_shared_memory_carveout = int(carve)
            except Exception as e:      # an old cupy or a driver that refuses: the hint is optional
                print(f"FERMAT_CARVEOUT={carve} ignored: {e}", flush=True)
    return _K[key]


def persist_kernel(limbs=21, step_file="fermat28_step.cuh", asm_mad=False, maxreg=None):
    """the persistent pool kernel `fermat28_persist` (persist_source), compiled and cached like kernel(); its registers: persist_kernel(...).attributes['num_regs']"""
    assert limbs == 21, "fermat28 is built for 21 x u32 input limbs (n < 2^672)"
    key = ("persist", step_file, asm_mad, maxreg)
    if key not in _K:
        opts = (("-DFM28_ASM=1",) if asm_mad else ()) + ((f"--maxrregcount={maxreg}",) if maxreg else ())
        _K[key] = cp.RawKernel(persist_source(step_file), "fermat28_persist", options=opts)
    return _K[key]


def persist_ctas_per_sm(regs, threads=128):
    """how many CTAs of `threads` threads and `regs` registers a thread fit on an SM (registers are allocated in units of 8 a thread): the grid of the persistent kernel is this many CTAs an SM"""
    at = cp.cuda.Device().attributes
    per_cta = -(-int(regs) // 8) * 8 * threads
    return max(1, min(at.get("MaxRegistersPerMultiprocessor", 65536) // per_cta, at.get("MaxThreadsPerMultiProcessor", 1536) // threads))


def persist_pool(tester, kv, cnt, cols, run_rest, cta_sm=None, threads=128):
    """One flush of a pool with the persistent kernel, the members it leaves undecided (the queue ran empty) finished by `run_rest(tester, kv, cnt, cols)` = search_gpu5's round-based run_pool.
    Arguments and return value as run_pool: members kv[m] (int64) with their rows cols[indptr[m]:indptr[m+1]] (global rows of tester.cq, ascending q; cnt[m] of them), returns per member the rows
    tested (up to and including the first PRP; cnt for a success), PRP found, success, the global row of the first PRP (-1 if none), the tests computed, the launches.
    tester needs .cq, .M (device arrays), .kp (persist_kernel(...)) and .kp_regs (its registers, for the grid)."""
    n = int(kv.size)
    if n == 0:
        z = cp.zeros(0, cp.int64)
        return z, cp.zeros(0, cp.bool_), cp.zeros(0, cp.bool_), z, 0, 0
    cnt64 = cnt.astype(cp.int64)
    indptr = cp.concatenate([cp.zeros(1, cp.int64), cp.cumsum(cnt64)])
    cols32 = cols if cols.dtype == cp.int32 else cols.astype(cp.int32)
    counter = cp.zeros(1, dtype=cp.int32)
    tests = cp.empty(n, dtype=cp.int32)
    state = cp.empty(n, dtype=cp.uint8)
    frow = cp.empty(n, dtype=cp.int32)
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    grid = min(nsm * (cta_sm or persist_ctas_per_sm(tester.kp_regs, threads)), -(-n // threads))
    tester.kp((grid,), (threads,), (tester.cq, tester.M, kv.astype(cp.uint32), cnt.astype(cp.int32), indptr, cols32, np.int32(n), counter, tests, state, frow))
    if bool((state == 3).any()):
        raise RuntimeError("kernel 28 flagged an n outside its range")
    tests_m = tests.astype(cp.int64)
    prp_m = state == 1
    succ_m = state == 2
    frow_m = frow.astype(cp.int64)
    gtests, launches = int(tests_m.sum()), 1                      # (every row tested so far is a test computed: no waste)
    unf = cp.nonzero(state == 0)[0]
    if int(unf.size):
        pos_u = tests_m[unf]
        lens = cnt64[unf] - pos_u
        offs = cp.cumsum(lens)
        total = int(offs[-1])
        seg = cp.searchsorted(offs, cp.arange(total), side="right")
        cols_u = cols32[(indptr[unf] + pos_u)[seg] + (cp.arange(total) - (offs - lens)[seg])]
        t_u, p_u, s_u, f_u, g_u, l_u = run_rest(tester, kv[unf], lens, cols_u)
        tests_m[unf] = pos_u + t_u
        prp_m[unf] = p_u
        succ_m[unf] = s_u
        frow_m[unf] = f_u
        gtests += int(g_u); launches += int(l_u)
    return tests_m, prp_m, succ_m, frow_m, gtests, launches


def to_limbs(x, limbs=21):
    return np.frombuffer(int(x).to_bytes(4 * limbs, "little"), dtype=np.uint32)


def _check_range(N0, M, U, kmax, kmin=0):
    lo = int(N0) - max(int(q) for q in U) + int(kmin) * int(M)
    hi = int(N0) + int(kmax) * int(M)
    if not (1 << 641) <= lo or hi >= (1 << 668):
        raise ValueError(f"n spans {lo.bit_length()}..{hi.bit_length()} bits; fermat28 needs 642..668")


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
