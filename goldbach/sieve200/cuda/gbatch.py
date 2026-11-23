"""A batch-level feeder: the window of a GpuFeeder is a BATCH of 2^ks_log members (2^25: one production batch of 32 slices), and the primes above `split` are not marked
by the sieve kernel for every window of 2^tile_log members but by gbig_gen once per batch and applied to the bitmap of each (row, tile) by the tile kernel (gbatch_kernels.cuh).
Everything after the sieve (count, select, finalize, rows) is GpuFeeder's: the same Window comes out, over 2^ks_log members, selection in blocks of 2^llog.

    from gbatch import BatchFeeder
    fd = BatchFeeder.from_search_G(search.G, ks_log=25, tile_log=19, llog=15, f=0.99, split=1_000_000, rg=16)     # after search.init_spec(spec, B_big, block)
    w = fd.window(k0)          # 2^25 members k0 .. k0 + 2^25 - 1, k0 a multiple of 2^25

The prime list is search.G["S"] up to B_big, ascending: the primes <= split go through the tile kernel, the others through gbig.  Identical output to a GpuFeeder over the same
primes and the same window (test_gbatch_cpu.py against sieve200's CPU Feeder).  A prototype: see DEEPSIEVE.md.
"""
import os

import numpy as np
import cupy as cp

import gbig
from gpu_sieve import GpuFeeder


def _np(a):
    """a cupy array on the host (numpy arrays pass through: the CPU test replaces cupy by numpy)"""
    return a.get() if hasattr(a, "get") else np.asarray(a)

HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = "".join(open(os.path.join(HERE, f)).read() for f in ("gsieve_kernels.cuh", "gbig_kernels.cuh", "gbatch_kernels.cuh"))
_BCACHE = {}
_NAMES = ("s200g_count", "s200g_select", "s200g_rows", "s200g_n0m", "s200g_finalize", "s200g_prep", "s200g_prep_tiles", "s200g_tile", "gbig_gen", "gbig_gen_st", "gbig_apply")


def _batch_kernels(ks_log, llog, nthreads, tile_log, rg, ppt, stage_cap=8192, rcta=2):
    key = (ks_log, llog, nthreads, tile_log, rg, ppt, stage_cap, rcta)
    if key not in _BCACHE:
        head = (f"#define S200G_DYNSHARED(type, name) extern __shared__ type name[]\n#define KLOG {ks_log}\n#define LLOG {llog}\n#define NTHREADS {nthreads}\n"
                f"#define S200G_UNROLL 1\n#define TILE_LOG {tile_log}\n#define KS_LOG {ks_log}\n#define RG {rg}\n#define PPT {ppt}\n"
                f"#define STAGE_CAP {stage_cap}\n#define RCTA {rcta}\n#define RCTA_LOG {rcta.bit_length() - 1}\n")
        mod = cp.RawModule(code=head + _SRC)
        _BCACHE[key] = {n: mod.get_function(n) for n in _NAMES}
    return _BCACHE[key]


class BatchFeeder(GpuFeeder):
    def __init__(self, S, INV, U, N0M, ks_log=25, tile_log=19, llog=15, f=0.97, p_est=0.055, nthreads=256, split=None, rg=16, ppt=4, gen_threads=256, tile_threads=256,
                 shared=None, max_rows=None, staged=False, rcta=2, stage_cap=8192):
        assert ks_log >= tile_log and 1 <= rg <= 64
        super().__init__(S, INV, U, N0M, klog=ks_log, llog=llog, f=f, p_est=p_est, nthreads=nthreads, shared=shared, plain_sieve=False,
                         kernels=_batch_kernels(ks_log, llog, nthreads, tile_log, rg, ppt, stage_cap, rcta), max_rows=max_rows)
        self.tile_log, self.rg, self.tile_threads = tile_log, rg, tile_threads
        self.staged, self.rcta, self.stage_cap, self.ppt = bool(staged), int(rcta), int(stage_cap), int(ppt)
        self.ntiles = 1 << (ks_log - tile_log)
        Sh = _np(self.sh["S64"])
        split = (1 << tile_log) if split is None else split
        self.n_small = int((Sh <= split).sum())
        self.n_large = int(Sh.size - self.n_small)
        self.tabt = cp.empty((self.ntiles * max(self.n_small, 1), 4), dtype=cp.uint32)      # {s, M^-1, invp, c0 of the tile} a (tile, small prime)
        self.tabl = cp.empty((max(self.n_large, 1), 4), dtype=cp.uint32)                    # the large primes, c0 of the batch
        self.big = gbig.BigStage(self.U, self.tabl, ks_log=ks_log, tile_log=tile_log, rg=rg, ppt=ppt, threads=gen_threads, S=Sh[self.n_small:], kernels=self.k,
                                staged=self.staged, rcta=self.rcta, stage_cap=self.stage_cap) if self.n_large else None
        self.tile_smem = 4 * ((1 << tile_log) // 32)
        if self.tile_smem > 48 * 1024:
            self.k["s200g_tile"].max_dynamic_shared_size_bytes = self.tile_smem
        self._zero = (cp.zeros(rg * self.ntiles + 1, dtype=cp.uint32), cp.zeros(1, dtype=cp.uint32))     # no large primes: empty bins

    def with_variant(self, n0m, U):
        # same primes, tables and compiled kernels; the big stage, the tile tables and the matrix are rebuilt for the new feeder
        return BatchFeeder(None, None, U, n0m, ks_log=self.klog, tile_log=self.tile_log, llog=self.llog, f=self.f, p_est=self.p_est, nthreads=self.nthreads,
                           split=int(_np(self.sh["S64"])[self.n_small - 1]) if self.n_small else 0, rg=self.rg, gen_threads=self.big.threads if self.big else 256,
                           tile_threads=self.tile_threads, shared=self.sh, staged=self.staged, rcta=self.rcta, stage_cap=self.stage_cap, ppt=self.ppt)

    def with_N0(self, N0, U):
        """as GpuFeeder.with_N0: N0 mod s for every prime is computed on the GPU (a new feeder: its own bit matrix and large-prime stage; use retarget() to reuse this one)"""
        n0m = self._n0m(N0)
        return BatchFeeder(None, None, U, n0m, ks_log=self.klog, tile_log=self.tile_log, llog=self.llog, f=self.f, p_est=self.p_est, nthreads=self.nthreads,
                           split=int(_np(self.sh["S64"])[self.n_small - 1]) if self.n_small else 0, rg=self.rg, gen_threads=self.big.threads if self.big else 256,
                           tile_threads=self.tile_threads, shared=self.sh, staged=self.staged, rcta=self.rcta, stage_cap=self.stage_cap, ppt=self.ppt)

    def _sieve_phase(self, k0, ev):
        sh = self.sh
        nSs, nL, snt = self.n_small, self.n_large, self.sieve_threads
        if nSs:
            self.k["s200g_prep_tiles"](((nSs + 255) // 256,), (256,), (sh["S"], sh["INV"], sh["INVP"], self.N0M, np.uint64(k0), np.int32(nSs), self.tabt))
        if nL:
            self.k["s200g_prep"](((nL + 255) // 256,), (256,), (sh["S"][nSs:], sh["INV"][nSs:], sh["INVP"][nSs:], self.N0M[nSs:], np.uint64(k0), np.int32(nL), self.tabl))
        if ev is not None:
            ev[1].record()
        for row0 in range(0, self.nU, self.rg):
            nrows = min(self.rg, self.nU - row0)
            if nL:
                bins = self.big.gen_group(row0, nrows, U=self.U)
                gcnt, cap = self.big.gcnt, self.big.cap
            else:
                gcnt, bins, cap = self._zero[0], self._zero[1], 1
            self.k["s200g_tile"]((nrows, self.ntiles), (snt,), (self.U, np.int32(row0), self.tabt, np.int32(nSs), gcnt, bins, np.uint32(cap), self.bits),
                                 shared_mem=self.tile_smem)
