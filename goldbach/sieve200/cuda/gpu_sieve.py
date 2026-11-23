"""The sieve, the counts, the selection and the survivor lists of search.run_block on a GPU (cupy), for search_gpu3.

    from gpu_sieve import GpuFeeder
    fd = GpuFeeder.from_search_G(search.G, klog=18, llog=15, f=0.97, p_est=0.055)      # after search.init_spec(spec, B, block)
    w = fd.window(k0)          # K = 2^klog members k0 .. k0 + K - 1, selection in blocks of L = 2^llog members

w is a Window of device arrays over all the blocks of the window, block by block:
    w.k          u64[nsel]      absolute k of the selected members (per block ascending count, ties ascending k)
    w.cnt        u16[nsel]      their survivor counts
    w.offs       i64[nsel+1]    CSR offsets into w.rows
    w.rows       u16[tot]       alive rows (indices into the spec's residual list), ascending within a member
    w.block      i32[nsel]      block of each selected member (0 .. K/L-1)
    w.alive_total, w.hm_all, w.hm_kept   numpy arrays [K/L]: sum of counts over all L members of the block; sum of (1-p_est)^count
                                         over all members / over the selected ones (as search.run_block's hm)
Selection per block = np.argsort(counts, kind="stable")[:ceil(L (1-f))].  One GpuFeeder per variant (N0 mod s differs); the
prime tables (S, M^-1 mod s, mu, floor(M^-1 2^32 / s)) are shared: GpuFeeder.with_variant(n0m, U) returns a feeder that shares them.

Options (all give identical output):
    sieve_threads   CTA size of the sieve kernel (default nthreads).  The sieve likes 1024 on an A100 and an L4 (more warps hide its latency); the select / rows /
                    count / finalize kernels keep nthreads (256: their time grows with the CTA size).
    shoup=True      the 32-bit setup (s200g_prep + s200g_sieve_sh); False = the original kernel with a 64-bit Barrett, for A/B.
    unroll=1        marks a trip of the Shoup kernel's loop: 1, 2 (guarded second mark) or 3 (second mark to a dummy word); same output.
    window(k0, timings=True) puts w.timings = dict of ms: prep, sieve, count, select, finalize, wait1 (the GPU's idle gap while the host reads the number of
    survivor rows and allocates), rows, wait2 (host time reading the statistics after the rows kernel), wall (the whole call), host (wall minus the sum of the GPU parts).
"""
import math
import os
import time

import numpy as np
import cupy as cp

HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = open(os.path.join(HERE, "gsieve_kernels.cuh")).read()
_KCACHE = {}


def apply_carveout(kernels, env="DEEP_CARVEOUT"):
    """DEEP_CARVEOUT=100 (percent of an SM's shared-memory capacity): the same hint for every sieve kernel as FERMAT_CARVEOUT gives the Fermat kernel, so that, when the two run at once on
    different streams (search_gpu5 --overlap 1), the SM does not have to be reconfigured between a kernel that asked for little shared memory and one that needs 64 KB.  Unset: the driver's choice."""
    v = os.environ.get(env, "")
    if not v:
        return
    for name, f in kernels.items():
        try:
            f.preferred_shared_memory_carveout = int(v)
        except Exception as e:
            print(f"{env}={v} ignored for {name}: {e}", flush=True)
            return


def _kernels(klog, llog, nthreads, unroll=1):
    key = (klog, llog, nthreads, unroll)
    if key not in _KCACHE:
        head = (f"#define S200G_DYNSHARED(type, name) extern __shared__ type name[]\n#define KLOG {klog}\n#define LLOG {llog}\n"
                f"#define NTHREADS {nthreads}\n#define S200G_UNROLL {unroll}\n")
        mod = cp.RawModule(code=head + _SRC)
        _KCACHE[key] = {n: mod.get_function(n) for n in ("s200g_sieve", "s200g_sieve_sh", "s200g_prep", "s200g_count", "s200g_select", "s200g_rows", "s200g_n0m",
                                                         "s200g_km", "s200g_finalize")}
    return _KCACHE[key]


class Window:
    __slots__ = ("k", "cnt", "offs", "rows", "block", "alive_total", "hm_all", "hm_kept", "k0", "L", "timings")


class GpuFeeder:
    def __init__(self, S, INV, U, N0M, B=None, klog=18, llog=15, f=0.97, p_est=0.055, nthreads=256, shared=None, sieve_threads=None, shoup=True, unroll=1, plain_sieve=True, kernels=None,
                 max_rows=None):
        assert llog <= klog and llog <= 19 and (1 << llog) % nthreads == 0
        self.klog, self.llog, self.K, self.L = klog, llog, 1 << klog, 1 << llog
        self.f, self.p_est, self.nthreads = float(f), float(p_est), nthreads
        self.sieve_threads = int(sieve_threads or nthreads)
        assert 32 <= self.sieve_threads <= 1024 and self.sieve_threads % 32 == 0
        self.shoup, self.unroll = bool(shoup), int(unroll)
        if shared is None:
            S = np.asarray(S, dtype=np.int64)
            inv = np.asarray(INV, dtype=np.uint32)
            shared = dict(S=cp.asarray(S.astype(np.uint32)), INV=cp.asarray(inv),
                          INVP=cp.asarray(((inv.astype(np.uint64) << np.uint64(32)) // S.astype(np.uint64)).astype(np.uint32)),      # floor(M^-1 2^32 / s): Shoup's constant
                          MU=cp.asarray((np.uint64(2 ** 64 - 1) // S.astype(np.uint64)).astype(np.uint64)),
                          S64=cp.asarray(S), nS=int(S.size))
        self.sh = shared
        self.U = U.astype(cp.uint32) if isinstance(U, cp.ndarray) else cp.asarray(np.asarray(U, dtype=np.uint32))
        self.N0M = N0M.astype(cp.uint32) if isinstance(N0M, cp.ndarray) else cp.asarray(np.asarray(N0M, dtype=np.uint32))
        self.nU = int(self.U.size)
        assert self.nU < 4096
        self.k = kernels if kernels is not None else _kernels(klog, llog, nthreads, self.unroll)
        apply_carveout(self.k)
        self._bits_root = cp.empty((max(self.nU, int(max_rows or 0)), self.K // 32), dtype=cp.uint32)     # room for max_rows rows: retarget() may point the feeder at a variant with more rows
        self.bits = self._bits_root[:self.nU]
        self.counts = cp.empty(self.K, dtype=cp.uint16)
        self.smem = 4 * (self.K // 32 + (1 if self.unroll >= 3 else 0))           # the Shoup kernel with unroll 3 has a dummy word
        if plain_sieve and self.smem > 48 * 1024:                                  # (a BatchFeeder never launches the whole-window sieve kernels: 4 MB of shared memory)
            self.k["s200g_sieve"].max_dynamic_shared_size_bytes = self.smem
            self.k["s200g_sieve_sh"].max_dynamic_shared_size_bytes = self.smem
        self.tab = cp.empty((self.sh["nS"], 4), dtype=cp.uint32) if (self.shoup and plain_sieve) else None     # {s, M^-1, invp, c0} a prime
        self._tmp = {}

    @classmethod
    def from_search_G(cls, G, **kw):
        """After search.init_spec: G["S"], G["inv"] (M^-1 mod s), G["n0m"] (N0 mod s), G["U"] (the rows)."""
        return cls(G["S"], G["inv"], G["U"], G["n0m"], **kw)

    def _n0m(self, N0):
        """N0 mod s for every prime, computed on the GPU (N0 < 2^768)"""
        limbs = cp.asarray(np.frombuffer(int(N0).to_bytes(4 * 24, "little"), dtype=np.uint32).copy())      # 24 limbs
        sh = self.sh
        n0m = cp.empty(sh["nS"], dtype=cp.uint32)
        nt = 256
        self.k["s200g_n0m"](((sh["nS"] + nt - 1) // nt,), (nt,), (limbs, np.int32(24), sh["S"], sh["MU"], np.int32(sh["nS"]), n0m))
        return n0m

    def retarget(self, N0, U):
        """Point THIS feeder at another variant of the same M (same primes and M^-1 mod s): N0 mod s is computed on the GPU, the rows are replaced, and the bit matrix (room for
        max_rows rows, allocated once) is shared, so a campaign with variants of 1,092-1,096 rows needs one feeder, one bit matrix and one large-prime stage.  Returns self."""
        U = np.asarray(U.get() if isinstance(U, cp.ndarray) else U, dtype=np.uint32)
        assert 0 < U.size < 4096
        if U.size > self._bits_root.shape[0]:
            raise ValueError(f"{U.size} rows but the bit matrix was allocated for {self._bits_root.shape[0]} (max_rows)")
        self.U = cp.asarray(U)
        self.nU = int(U.size)
        self.bits = self._bits_root[:self.nU]
        self.N0M = self._n0m(N0)
        return self

    def with_N0(self, N0, U):
        """The feeder of the variant with this N0 (same M): N0 mod s for every prime is computed on the GPU, nothing on the host."""
        n0m = self._n0m(N0)
        return GpuFeeder(None, None, U, n0m, klog=self.klog, llog=self.llog, f=self.f, p_est=self.p_est, nthreads=self.nthreads, shared=self.sh,
                         sieve_threads=self.sieve_threads, shoup=self.shoup, unroll=self.unroll)

    def with_variant(self, n0m, U):
        return GpuFeeder(None, None, U, n0m, klog=self.klog, llog=self.llog, f=self.f, p_est=self.p_est, nthreads=self.nthreads, shared=self.sh,
                         sieve_threads=self.sieve_threads, shoup=self.shoup, unroll=self.unroll)

    def _buf(self, name, shape, dtype):
        """an internal temporary reused from window to window (the arrays the caller keeps are allocated afresh)"""
        k = (name, shape, dtype)
        if k not in self._tmp:
            self._tmp[k] = cp.empty(shape, dtype=dtype)
        return self._tmp[k]

    def _sieve_phase(self, k0, ev):
        """the per-prime table and the sieve: fills self.bits [nU, K / 32] (ev[1] is recorded after the table, when ev is not None; ev[2] by the caller)"""
        sh, K, nt, snt = self.sh, self.K, self.nthreads, self.sieve_threads
        nS = sh["nS"]
        if self.shoup:
            self.k["s200g_prep"](((nS + 255) // 256,), (256,), (sh["S"], sh["INV"], sh["INVP"], self.N0M, np.uint64(k0), np.int32(nS), self.tab))
            if ev is not None:
                ev[1].record()
            self.k["s200g_sieve_sh"]((self.nU,), (snt,), (self.U, self.tab, np.int32(nS), self.bits), shared_mem=self.smem)
        else:
            KM = cp.empty(nS, dtype=cp.uint32)
            self.k["s200g_km"](((nS + nt - 1) // nt,), (nt,), (sh["S"], np.uint64(k0), np.int32(nS), KM))
            if ev is not None:
                ev[1].record()
            self.k["s200g_sieve"]((self.nU,), (snt,), (self.U, sh["S"], sh["INV"], sh["MU"], self.N0M, KM, np.int32(nS), self.bits),
                                  shared_mem=4 * (K // 32))

    def window(self, k0, f=None, timings=False):
        """Six launches and two small synchronisations: the per-prime table (c0 = (N0 M^-1 + k0) mod s, or k0 mod s), sieve, counts, select, finalize (k, counts,
        CSR offsets), then once the number of survivor rows is known the rows kernel.  timings=True: see the module docstring."""
        sh, K, L, nt = self.sh, self.K, self.L, self.nthreads
        snt = self.sieve_threads
        f = self.f if f is None else float(f)
        nkeep = int(math.ceil(L * (1.0 - f)))
        nb = K // L
        nsel = nb * nkeep
        nS = sh["nS"]
        ev = [cp.cuda.Event() for _ in range(8)] if timings else None
        if timings:
            wall0 = time.perf_counter()
            ev[0].record()
        self._sieve_phase(k0, ev)
        if timings:
            ev[2].record()
        self.k["s200g_count"](((K // 32 + nt - 1) // nt,), (nt,), (self.bits, np.int32(self.nU), self.counts))
        if timings:
            ev[3].record()
        w = Window()
        w.k0, w.L = k0, L
        stats = self._buf("stats", (nb, 3), cp.float64)
        keys = self._buf("keys", (nb, max(nkeep, 1)), cp.uint32)
        nbins = (self.nU + 2 + 3) & ~3
        n2 = 1
        while n2 < nkeep:
            n2 <<= 1
        shared = 4 * (nbins + (n2 if nkeep <= 8192 else 0) + 8)
        if shared + 28 * nt + 64 > 48 * 1024:                      # static shared memory of the kernel: scan u32 + red 3 doubles a thread
            self.k["s200g_select"].max_dynamic_shared_size_bytes = shared
        self.k["s200g_select"]((nb,), (nt,), (self.counts, np.int32(self.nU), np.int32(nkeep), np.float64(self.p_est), keys, stats), shared_mem=shared)
        if nkeep > 8192:
            keys = cp.sort(keys, axis=1)                         # kept members came out unsorted: sort (count, index) as one key
        keys = cp.ascontiguousarray(keys[:, :nkeep])
        if timings:
            ev[4].record()
        cnt = cp.empty(nsel, dtype=cp.uint16)
        member = self._buf("member", (nsel,), cp.uint32)
        kv = cp.empty(nsel, dtype=cp.uint64)
        offs = cp.empty(nsel + 1, dtype=cp.int64)
        total = self._buf("total", (1,), cp.int64)
        self.k["s200g_finalize"]((1,), (nt,), (keys, np.int32(nsel), np.int32(max(nkeep, 1)), np.uint64(k0), cnt, member, kv, offs, total))
        if timings:
            ev[5].record()
        tot = int(total[0])                                        # the one wait for the device before the rows can be allocated
        rows = cp.empty(tot, dtype=cp.uint16)
        if timings:
            ev[6].record()
        if nsel:
            self.k["s200g_rows"]((((nsel + nt - 1) // nt),), (nt,), (self.bits, np.int32(self.nU), member, offs, np.int32(nsel), rows))
        if timings:
            ev[7].record()
            t_w2 = time.perf_counter()
        st = cp.asnumpy(stats)
        if timings:
            t_w2 = time.perf_counter() - t_w2
            wall = time.perf_counter() - wall0
            ms = lambda i, j: cp.cuda.get_elapsed_time(ev[i], ev[j])             # (cupy Events have no elapsed_time method)
            tm = dict(prep=ms(0, 1), sieve=ms(1, 2), count=ms(2, 3), select=ms(3, 4), finalize=ms(4, 5), wait1=ms(5, 6), rows=ms(6, 7), wait2=1e3 * t_w2, wall=1e3 * wall)
            tm["host"] = tm["wall"] - sum(tm[k] for k in ("prep", "sieve", "count", "select", "finalize", "wait1", "rows"))
            w.timings = tm
        else:
            w.timings = None
        w.alive_total = np.rint(st[:, 0]).astype(np.int64)
        w.hm_all, w.hm_kept = st[:, 1], st[:, 2]
        w.k, w.cnt, w.offs, w.rows = kv, cnt, offs, rows
        w.block = (cp.arange(nsel, dtype=cp.int32) // max(nkeep, 1)).astype(cp.int32)
        return w


def cq_rows(N0, U, limbs=21):
    """The rows N0 - q (q in U) as u32 limbs, [len(U), limbs]: what gpu_fermat's MultiTester builds with one Python to_limbs call a row
    (48 ms for 32 slices of 1,011 rows; this takes a quarter of that): the limbs of N0 as int64, q subtracted from the lowest, borrows
    carried up in numpy."""
    U = np.asarray(U, dtype=np.int64)
    base = np.frombuffer(int(N0).to_bytes(4 * limbs, "little"), dtype=np.uint32).astype(np.int64)
    m = np.tile(base, (len(U), 1))
    m[:, 0] -= U
    for j in range(limbs):
        neg = m[:, j] < 0
        m[:, j] += neg.astype(np.int64) << 32
        if j + 1 < limbs:
            m[neg, j + 1] -= 1
    assert not (m[:, limbs - 1] < 0).any(), "N0 - q is negative"
    return m.astype(np.uint32)
