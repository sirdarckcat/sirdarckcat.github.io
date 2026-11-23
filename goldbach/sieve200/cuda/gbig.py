"""The large-prime stage of a deep sieve on a GPU (cupy): marks by primes above the tile (2^tile_log bits), bucketed by (row, tile) and applied to the tile's bitmap.
A prototype with a benchmark, bench_bigprimes.py; see gbig_kernels.cuh for the method.

    from gbig import BigStage, make_table
    st = BigStage(U, TAB, ks_log=25, rg=16)           # U: the rows (u32), TAB: [nP, 4] u32 = {s, M^-1 mod s, floor(M^-1 2^32 / s), c0} of the primes above the tile
    out = st.run_group(row0, nrows)                   # cupy u32 [nrows, 2^ks_log / 32]: bit j of row r is 0 iff a prime of TAB kills member j of row0 + r in the batch
"""
import math
import os

import numpy as np
import cupy as cp

from bigchunks import make_chunks

HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = open(os.path.join(HERE, "gbig_kernels.cuh")).read()
_KCACHE = {}


def _kernels(tile_log, ks_log, rg, ppt, stage_cap=8192, rcta=2):
    key = (tile_log, ks_log, rg, ppt, stage_cap, rcta)
    if key not in _KCACHE:
        head = (f"#define S200G_DYNSHARED(type, name) extern __shared__ type name[]\n#define TILE_LOG {tile_log}\n#define KS_LOG {ks_log}\n"
                f"#define RG {rg}\n#define PPT {ppt}\n#define STAGE_CAP {stage_cap}\n#define RCTA {rcta}\n#define RCTA_LOG {rcta.bit_length() - 1}\n")
        mod = cp.RawModule(code=head + _SRC)
        _KCACHE[key] = {n: mod.get_function(n) for n in ("gbig_gen", "gbig_gen_st", "gbig_apply")}
    return _KCACHE[key]


def primes_between(lo, hi):
    """primes p with lo < p <= hi (numpy sieve; 2^28 takes a few seconds and 270 MB)"""
    s = np.ones(hi + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(hi ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    idx = np.nonzero(s)[0]
    return idx[np.searchsorted(idx, lo, side="right"):].astype(np.uint32)


def make_table(S, M=None, N0=None, k0=0, rng=None):
    """TAB [nP, 4] u32 for the primes S.  With M and N0 the true values (M^-1 mod s, c0 = (N0 M^-1 + k0) mod s: a Python loop, for tests); without them random
    values with the same distribution (a benchmark does not need the true roots: the roots of (row, prime) pairs are uniform in [0, s) either way)."""
    S = np.asarray(S, dtype=np.uint32)
    if M is not None:
        INV = np.array([pow(M % int(s), -1, int(s)) for s in S], dtype=np.uint32)
        C0 = np.array([(N0 * int(i) + k0) % int(s) for i, s in zip(INV, S)], dtype=np.uint32)
    else:
        rng = rng or np.random.default_rng(1)
        INV = (rng.random(S.size) * (S - 1)).astype(np.uint32) + 1
        C0 = (rng.random(S.size) * S).astype(np.uint32)
    INVP = ((INV.astype(np.uint64) << np.uint64(32)) // S.astype(np.uint64)).astype(np.uint32)
    return np.ascontiguousarray(np.stack([S, INV, INVP, C0], axis=1))


def expected_cap(S, tile_log, margin=1.08):
    """a bin capacity: the expected marks of a (row, tile) bin, tile_bits * sum 1/s, plus a margin and 6 standard deviations"""
    e = (1 << tile_log) * float(np.sum(1.0 / S.astype(np.float64)))
    return int(math.ceil((e * margin + 6.0 * math.sqrt(e) + 64) / 32.0)) * 32


class BigStage:
    def __init__(self, U, TAB, ks_log=25, tile_log=19, rg=16, ppt=4, threads=256, cap=None, S=None, kernels=None, staged=False, rcta=2, stage_cap=8192):
        """TAB: a numpy [nP, 4] table (copied to the device) or a cupy one that the caller rebuilds each batch (then pass S, the host array of its primes, for the capacity).
        staged: the staged generate kernel (gbig_gen_st: a CTA takes a chunk of primes and rcta rows, sorts the marks by bin in shared memory and writes whole runs; threads >= rcta x tiles)"""
        self.U = U.astype(cp.uint32) if isinstance(U, cp.ndarray) else cp.asarray(np.asarray(U, dtype=np.uint32))     # U may already be on the device (BatchFeeder passes its own)
        self.TAB = TAB if isinstance(TAB, cp.ndarray) else cp.asarray(np.ascontiguousarray(TAB, dtype=np.uint32))
        self.nP = int(self.TAB.shape[0])
        self.ks_log, self.tile_log, self.rg, self.ppt, self.threads = ks_log, tile_log, rg, ppt, threads
        self.ntiles = 1 << (ks_log - tile_log)
        self.nbins = rg * self.ntiles
        self.tile_words = (1 << tile_log) // 32
        self.staged, self.rcta, self.stage_cap = bool(staged), int(rcta), int(stage_cap)
        assert self.rcta >= 1 and self.rcta & (self.rcta - 1) == 0, "rcta must be a power of two"
        self.k = kernels if kernels is not None else _kernels(tile_log, ks_log, rg, ppt, self.stage_cap, self.rcta)
        if S is None:
            S = self.TAB[:, 0].get() if hasattr(self.TAB, "get") else self.TAB[:, 0]
        self.cap = cap or expected_cap(S, tile_log)
        if self.staged:
            assert threads % 32 == 0 and threads >= self.rcta * self.ntiles, "the staged kernel needs a CTA of at least rcta x tiles threads (one thread a bin for the scan)"
            self.pstart = cp.asarray(make_chunks(S, ks_log, 0.75 * self.stage_cap / self.rcta))      # chunks of primes with ~3/4 of the staging buffer in marks
            self.nchunks = int(self.pstart.size) - 1
        assert self.cap % 4 == 0, "a bin must start 16-byte aligned (the apply loads 16 bytes at a time)"
        self.apply_smem = 4 * self.tile_words
        if self.apply_smem > 48 * 1024:
            self.k["gbig_apply"].max_dynamic_shared_size_bytes = self.apply_smem
        self.gcnt = cp.zeros(self.nbins + 1, dtype=cp.uint32)
        self.out = cp.empty(self.nbins * self.tile_words, dtype=cp.uint32)
        self._bins = None
        self.retries = 0

    def _bins_for(self, cap):
        need = self.nbins * cap
        assert need < (1 << 32), "bins index would overflow 32 bits: use fewer rows a group or a smaller cap"
        if self._bins is None or self._bins.size < need:
            self._bins = None
            self._bins = cp.empty(need, dtype=cp.uint32)
        return self._bins

    def gen_group(self, row0, nrows, timings=None, U=None, defer=None):
        """gbig_gen for rows row0 .. row0 + nrows - 1 (nrows <= rg), repeated with the capacity the demand asks for if a bin overflowed.  Leaves self.gcnt, the bins and self.cap
        for gbig_apply / the tile kernel; returns (event before, event after) when timings is a dict (the generate time is added to timings['gen']).
        defer: a device array of one u32 that the caller zeroed before the window.  Without it the host waits for the device after EVERY group to read the overflow flag gcnt[NBINS] (~80 round
        trips a window, each of which leaves the stream idle and, in an overlapped driver, needs the GIL back from the main thread).  With it the flag is OR-ed into `defer` by a one-word kernel and
        the call returns at once: the caller reads `defer` once after the window and, if it is set, repeats the window with defer=None (the tile kernel applies no bin of an overflowed group,
        so nothing stale is read meanwhile)."""
        assert 1 <= nrows <= self.rg
        U = self.U if U is None else U
        grid = (self.nP + self.threads * self.ppt - 1) // (self.threads * self.ppt)
        use_events = timings is not None
        while True:
            bins = self._bins_for(self.cap)
            self.gcnt[:] = 0
            if use_events:
                e0, e1 = cp.cuda.Event(), cp.cuda.Event()
                e0.record()
            if self.staged:
                self.k["gbig_gen_st"]((self.nchunks, (nrows + self.rcta - 1) // self.rcta), (self.threads,),
                                      (U, self.TAB, self.pstart, np.int32(row0), np.int32(nrows), np.uint32(self.cap), self.gcnt, bins))
            else:
                self.k["gbig_gen"]((grid,), (self.threads,), (U, self.TAB, np.int32(self.nP), np.int32(row0), np.int32(nrows), np.uint32(self.cap), self.gcnt, bins))
            if use_events:
                e1.record()
            if defer is not None:
                defer |= self.gcnt[self.nbins:self.nbins + 1]
                if use_events:
                    e1.synchronize()
                    timings["gen"] = timings.get("gen", 0.0) + cp.cuda.get_elapsed_time(e0, e1)
                return bins
            if int(self.gcnt[self.nbins]) == 0:
                break
            need = int(self.gcnt[:self.nbins].max())                     # the demand of the fullest bin: the size that works
            if use_events:
                e1.synchronize()
                timings["gen_retry"] = timings.get("gen_retry", 0.0) + cp.cuda.get_elapsed_time(e0, e1)
            self.cap = int(math.ceil((need + 64) / 32.0)) * 32
            self.retries += 1
        if use_events:
            e1.synchronize()
            timings["gen"] = timings.get("gen", 0.0) + cp.cuda.get_elapsed_time(e0, e1)
        return bins

    def run_group(self, row0, nrows, timings=None):
        """marks of rows row0 .. row0 + nrows - 1 (nrows <= rg): returns the bit matrix [nrows, 2^ks_log / 32] (a view of an internal buffer, valid until the next call).
        timings: a dict that receives the ms of the generate and the apply kernels (all attempts' generate time is added to 'gen_retry')."""
        bins = self.gen_group(row0, nrows, timings)
        if timings is not None:
            e1, e2 = cp.cuda.Event(), cp.cuda.Event()
            e1.record()
        self.k["gbig_apply"]((nrows * self.ntiles,), (self.threads,), (self.gcnt, bins, np.uint32(self.cap), self.out), shared_mem=self.apply_smem)
        if timings is not None:
            e2.record(); e2.synchronize()
            timings["apply"] = timings.get("apply", 0.0) + cp.cuda.get_elapsed_time(e1, e2)
        return self.out[:nrows * self.ntiles * self.tile_words].reshape(nrows, self.ntiles * self.tile_words)

    def pass_a_ms(self, row0, nrows, reps=3):
        """ms of gbig_gen with cap = 0: every CTA counts its marks and reserves (pass A), finds the reservation too large and writes nothing (no pass B): the time of the visits
        and the counting.  gcnt is garbage afterwards (run_group zeroes it)."""
        grid = (self.nP + self.threads * self.ppt - 1) // (self.threads * self.ppt)
        bins = self._bins_for(self.cap)
        best = None
        for _ in range(reps):
            self.gcnt[:] = 0
            e0, e1 = cp.cuda.Event(), cp.cuda.Event()
            e0.record()
            if self.staged:
                self.k["gbig_gen_st"]((self.nchunks, (nrows + self.rcta - 1) // self.rcta), (self.threads,),
                                      (self.U, self.TAB, self.pstart, np.int32(row0), np.int32(nrows), np.uint32(0), self.gcnt, bins))
            else:
                self.k["gbig_gen"]((grid,), (self.threads,), (self.U, self.TAB, np.int32(self.nP), np.int32(row0), np.int32(nrows), np.uint32(0), self.gcnt, bins))
            e1.record(); e1.synchronize()
            ms = cp.cuda.get_elapsed_time(e0, e1)
            best = ms if best is None else min(best, ms)
        return best

    def marks(self, nrows):
        return int(self.gcnt[:nrows * self.ntiles].astype(cp.uint64).sum())
