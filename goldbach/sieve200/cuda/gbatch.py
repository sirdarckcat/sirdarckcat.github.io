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
import time

import numpy as np
import cupy as cp

import gbig
from gpu_sieve import GpuFeeder


def _np(a):
    """a cupy array on the host (numpy arrays pass through: the CPU test replaces cupy by numpy)"""
    return a.get() if hasattr(a, "get") else np.asarray(a)

HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = "".join(open(os.path.join(HERE, f)).read() for f in ("gsieve_kernels.cuh", "gbig_kernels.cuh", "gbatch_kernels.cuh", "ghead_kernels.cuh"))
_BCACHE = {}
_NAMES = ("s200g_count", "s200g_select", "s200g_rows", "s200g_rows2", "s200g_fin_sums", "s200g_fin_main", "s200g_rowmask", "s200g_rowlist", "s200g_rows_nost", "s200g_rows_nold", "s200g_order", "s200g_rows_ord", "s200g_rows_ord2", "s200g_rows_ord_nost", "s200g_n0m", "s200g_finalize", "s200g_prep", "s200g_prep_tiles", "s200g_tile", "gbig_gen", "gbig_gen_st", "gbig_apply", "ghead_gen", "ghead_apply")


def _batch_kernels(ks_log, llog, nthreads, tile_log, rg, ppt, stage_cap=8192, rcta=2, tile_lb=None, tile_unroll=1, tile_prefetch=0, bin_pack=False, gen_hoist=False, gen_unroll=1, gen_flush2=False, gen_order=False,
                   tile_pipe=None, gen_lean=()):
    """tile_lb: None, or (threads, min CTAs an SM) for __launch_bounds__ of the tile kernel: DEEP_TILE_MAXREG=32 with 128-thread tile CTAs makes a CTA that needs 128 x 32 = 4,096 registers, which is what
    5 resident Fermat CTAs (92 registers x 128 threads, 12,288 each) leave free on an SM of 65,536"""
    key = (ks_log, llog, nthreads, tile_log, rg, ppt, stage_cap, rcta, tile_lb, tile_unroll, tile_prefetch, bool(bin_pack), bool(gen_hoist), gen_unroll, bool(gen_flush2), bool(gen_order), tile_pipe, tuple(gen_lean))
    if key not in _BCACHE:
        head = (f"#define S200G_DYNSHARED(type, name) extern __shared__ type name[]\n#define KLOG {ks_log}\n#define LLOG {llog}\n#define NTHREADS {nthreads}\n"
                f"#define S200G_UNROLL 1\n#define TILE_LOG {tile_log}\n#define KS_LOG {ks_log}\n#define RG {rg}\n#define PPT {ppt}\n"
                f"#define STAGE_CAP {stage_cap}\n#define RCTA {rcta}\n#define RCTA_LOG {rcta.bit_length() - 1}\n"
                + (f"#define TILE_LB __launch_bounds__({tile_lb[0]}, {tile_lb[1]})\n" if tile_lb else "") + (f"#define TILE_UNROLL {tile_unroll}\n" if tile_unroll > 1 else "") + (f"#define TILE_PREFETCH_KB {tile_prefetch}\n" if tile_prefetch > 0 else "") + ("#define BIN_PACK 1\n" if bin_pack else "") + ("#define GEN_HOIST 1\n" if gen_hoist else "") + (f"#define GEN_UNROLL {gen_unroll}\n" if gen_unroll > 1 else "") + ("#define GEN_FLUSH2 1\n" if gen_flush2 else "") + ("#define GEN_ORDER 1\n" if gen_order else "") + gbig.defines(gen_lean)
                + (f"#define TILE_PIPE 1\n#define TILE_PIPE_AT {tile_pipe[0]}\n#define TILE_PIPE_CH {tile_pipe[1]}\n" if tile_pipe else ""))
        mod = cp.RawModule(code=head + _SRC)
        _BCACHE[key] = {n: mod.get_function(n) for n in _NAMES + (("s200g_tile_pipe",) if tile_pipe else ())}
    return _BCACHE[key]


class BatchFeeder(GpuFeeder):
    def __init__(self, S, INV, U, N0M, ks_log=25, tile_log=19, llog=15, f=0.97, p_est=0.055, nthreads=256, split=None, rg=16, ppt=4, gen_threads=256, tile_threads=256,
                 shared=None, max_rows=None, staged=False, rcta=2, stage_cap=8192):
        assert ks_log >= tile_log and 1 <= rg <= 64
        maxreg = int(os.environ.get("DEEP_TILE_MAXREG", "0"))                    # 0: the compiler's choice (40 registers on sm_120)
        tile_lb = (int(tile_threads), max(1, 65536 // (int(tile_threads) * maxreg))) if maxreg else None
        tile_pipe = None                                                          # DEEP_TILE_PIPE=1: (apply threads, chunk words): the tile kernel streams its bin through shared memory beside the small-prime marks (gbatch_kernels.cuh, "pipelined tile")
        if os.environ.get("DEEP_TILE_PIPE", "0") == "1":
            tile_pipe = (int(os.environ.get("DEEP_TILE_PIPE_AT", "128")), int(os.environ.get("DEEP_TILE_PIPE_CH", "4092")))
            assert tile_pipe[0] % 32 == 0 and tile_pipe[1] % 12 == 0 and int(tile_threads) >= tile_pipe[0] + 32 and int(tile_threads) % 32 == 0, "DEEP_TILE_PIPE: apply threads and tile threads whole warps, tile threads >= apply + 32, chunk a multiple of 12 words"
        pack = bool(int(os.environ.get("DEEP_BIN_PACK", "0")))                    # 1: packed bins (5 marks of 19 bits in 3 words: 2.4 bytes a mark instead of 4); the staged kernel only
        assert not pack or (staged and tile_log <= 19 and int(rcta) >= 1), "DEEP_BIN_PACK=1 needs the staged large-prime kernel (DEEP_STAGED=1) and tiles of at most 2^19 bits"
        super().__init__(S, INV, U, N0M, klog=ks_log, llog=llog, f=f, p_est=p_est, nthreads=nthreads, shared=shared, plain_sieve=False,
                         kernels=_batch_kernels(ks_log, llog, nthreads, tile_log, rg, ppt, stage_cap, rcta, tile_lb, int(os.environ.get("DEEP_TILE_UNROLL", "1")), int(os.environ.get("DEEP_TILE_PREFETCH", "0")), pack, os.environ.get("DEEP_GEN_HOIST", "0") == "1", int(os.environ.get("DEEP_GEN_UNROLL", "1")), os.environ.get("DEEP_GEN_FLUSH2", "0") == "1", os.environ.get("DEEP_GEN_ORDER", "0") == "1", tile_pipe, gbig.lean_flags()), max_rows=max_rows)
        self.tile_log, self.rg, self.tile_threads = tile_log, rg, tile_threads
        self.staged, self.rcta, self.stage_cap, self.ppt, self.pack = bool(staged), int(rcta), int(stage_cap), int(ppt), pack
        self.ntiles = 1 << (ks_log - tile_log)
        Sh = _np(self.sh["S64"])
        split = (1 << tile_log) if split is None else split
        self.n_small = int((Sh <= split).sum())
        self.n_large = int(Sh.size - self.n_small)
        self.tabt = cp.empty((self.ntiles * max(self.n_small, 1), 4), dtype=cp.uint32)      # {s, M^-1, invp, c0 of the tile} a (tile, small prime)
        self.tabl = cp.empty((max(self.n_large, 1), 4), dtype=cp.uint32)                    # the large primes, c0 of the batch
        self.big = gbig.BigStage(self.U, self.tabl, ks_log=ks_log, tile_log=tile_log, rg=rg, ppt=ppt, threads=gen_threads, S=Sh[self.n_small:], kernels=self.k,
                                staged=self.staged, rcta=self.rcta, stage_cap=self.stage_cap, pack=pack) if self.n_large else None
        self.tile_kernel = "s200g_tile_pipe" if tile_pipe else "s200g_tile"
        self.tile_smem = 4 * ((1 << tile_log) // 32 + (2 * tile_pipe[1] if tile_pipe else 0))
        if self.tile_smem > 48 * 1024:
            self.k[self.tile_kernel].max_dynamic_shared_size_bytes = self.tile_smem
        self._zero = (cp.zeros(rg * self.ntiles + 1, dtype=cp.uint32), cp.zeros(1, dtype=cp.uint32))     # no large primes: empty bins
        # How the host checks the large-prime stage's bin-overflow flag (see window()): 1 = after EVERY row group (a blocking round trip each: the sieve stream idles for a moment after each group and the
        # sieve trickles in short bursts), N >= 2 = after every N-th group, 0 = never during the window (the flag is read once at its end: the groups are launched back to back and the sieve runs flat out).
        # Measured on an RTX PRO 6000 beside the Fermat rounds (23 Nov 08:37Z, pipeline depth 2): 1 -> batches of 1.55-1.60 s, 0 -> 1.73-1.76 s (= no overlap: the flat-out sieve at the highest stream priority
        # takes the SMs and the Fermat rounds wait), so the DEFAULT is 1.  GBATCH_DEFER_CHECK=1 is the old name of 0, =0 of 1.
        env = os.environ
        self.sync_every = int(env["GBATCH_SYNC_EVERY"]) if "GBATCH_SYNC_EVERY" in env else (0 if env.get("GBATCH_DEFER_CHECK", "0") == "1" else 1)
        self.group_delay = float(env.get("GBATCH_GROUP_DELAY_US", "0")) * 1e-6    # seconds the host waits after a checked group before it launches the tile kernel: the sieve stream is idle meanwhile
        self._ovf = cp.zeros(1, dtype=cp.uint32)
        self._defer = None
        self.window_retries = 0                                                  # windows repeated because a bin overflowed (the cap then grows; expected: never after the first windows)

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

    def window(self, k0, f=None, timings=False):
        """GpuFeeder.window with the large-prime stage's bin-overflow check deferred to the end of the window: the groups are launched back to back (no host round trip a group: ~80 a window
        before, each of which idled the stream and needed the GIL back from the driver's main thread when the sieve runs in a thread beside the Fermat rounds).  The window ends with host
        reads (the survivor count, the statistics), so reading the flag afterwards waits for nothing.  A set flag (a bin overflowed the capacity: practically never) repeats the window the
        old way, group by group, which grows the capacity.  sync_every (GBATCH_SYNC_EVERY) = 1, the default, is the old way throughout."""
        if self.sync_every == 1 or not self.n_large:
            return super().window(k0, f=f, timings=timings)
        self._ovf[:] = 0
        self._defer = self._ovf
        try:
            w = super().window(k0, f=f, timings=timings)
        finally:
            self._defer = None
        if int(self._ovf[0]) == 0:
            return w
        self.window_retries += 1
        return super().window(k0, f=f, timings=timings)

    def _sieve_phase(self, k0, ev):
        sh = self.sh
        nSs, nL, snt = self.n_small, self.n_large, self.sieve_threads
        if nSs:
            self.k["s200g_prep_tiles"](((nSs + 255) // 256,), (256,), (sh["S"], sh["INV"], sh["INVP"], self.N0M, np.uint64(k0), np.int32(nSs), self.tabt))
        if nL:
            self.k["s200g_prep"](((nL + 255) // 256,), (256,), (sh["S"][nSs:], sh["INV"][nSs:], sh["INVP"][nSs:], self.N0M[nSs:], np.uint64(k0), np.int32(nL), self.tabl))
        if ev is not None:
            ev[1].record()
        for gi, row0 in enumerate(range(0, self.nU, self.rg)):
            nrows = min(self.rg, self.nU - row0)
            if nL:
                defer = self._defer
                if defer is not None and self.sync_every > 1 and (gi + 1) % self.sync_every == 0:
                    defer = None                                                  # this group is checked by the host (it waits for everything launched before it too)
                bins = self.big.gen_group(row0, nrows, U=self.U, defer=defer)
                if defer is None and self.group_delay:
                    time.sleep(self.group_delay)                                  # the generate is done and the tile kernel is not launched yet: the stream idles for this long
                gcnt, cap = self.big.gcnt, self.big.cap
            else:
                gcnt, bins, cap = self._zero[0], self._zero[1], 1
            self.k[self.tile_kernel]((nrows, self.ntiles), (self.tile_threads,), (self.U, np.int32(row0), self.tabt, np.int32(nSs), gcnt, bins, np.uint32(cap), self.bits),
                                 shared_mem=self.tile_smem)
