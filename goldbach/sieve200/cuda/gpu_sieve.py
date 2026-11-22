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
prime tables (S, M^-1 mod s, mu) are shared: GpuFeeder.with_variant(n0m, U) returns a feeder that shares them.
"""
import math
import os

import numpy as np
import cupy as cp

HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = open(os.path.join(HERE, "gsieve_kernels.cuh")).read()
_KCACHE = {}


def _kernels(klog, llog, nthreads):
    key = (klog, llog, nthreads)
    if key not in _KCACHE:
        head = (f"#define S200G_DYNSHARED(type, name) extern __shared__ type name[]\n#define KLOG {klog}\n#define LLOG {llog}\n"
                f"#define NTHREADS {nthreads}\n")
        mod = cp.RawModule(code=head + _SRC)
        _KCACHE[key] = {n: mod.get_function(n) for n in ("s200g_sieve", "s200g_count", "s200g_select", "s200g_rows", "s200g_n0m", "s200g_km", "s200g_finalize")}
    return _KCACHE[key]


class Window:
    __slots__ = ("k", "cnt", "offs", "rows", "block", "alive_total", "hm_all", "hm_kept", "k0", "L")


class GpuFeeder:
    def __init__(self, S, INV, U, N0M, B=None, klog=18, llog=15, f=0.97, p_est=0.055, nthreads=256, shared=None):
        assert llog <= klog and llog <= 19 and (1 << llog) % nthreads == 0
        self.klog, self.llog, self.K, self.L = klog, llog, 1 << klog, 1 << llog
        self.f, self.p_est, self.nthreads = float(f), float(p_est), nthreads
        if shared is None:
            S = np.asarray(S, dtype=np.int64)
            shared = dict(S=cp.asarray(S.astype(np.uint32)), INV=cp.asarray(np.asarray(INV, dtype=np.uint32)),
                          MU=cp.asarray((np.uint64(2 ** 64 - 1) // S.astype(np.uint64)).astype(np.uint64)),
                          S64=cp.asarray(S), nS=int(S.size))
        self.sh = shared
        self.U = cp.asarray(np.asarray(U, dtype=np.uint32))
        self.N0M = N0M.astype(cp.uint32) if isinstance(N0M, cp.ndarray) else cp.asarray(np.asarray(N0M, dtype=np.uint32))
        self.nU = int(self.U.size)
        assert self.nU < 4096
        self.k = _kernels(klog, llog, nthreads)
        self.bits = cp.empty((self.nU, self.K // 32), dtype=cp.uint32)
        self.counts = cp.empty(self.K, dtype=cp.uint16)
        need = 4 * (self.K // 32)
        if need > 48 * 1024:
            self.k["s200g_sieve"].max_dynamic_shared_size_bytes = need

    @classmethod
    def from_search_G(cls, G, **kw):
        """After search.init_spec: G["S"], G["inv"] (M^-1 mod s), G["n0m"] (N0 mod s), G["U"] (the rows)."""
        return cls(G["S"], G["inv"], G["U"], G["n0m"], **kw)

    def with_N0(self, N0, U):
        """The feeder of the variant with this N0 (same M): N0 mod s for every prime is computed on the GPU, nothing on the host."""
        limbs = cp.asarray(np.frombuffer(int(N0).to_bytes(4 * 24, "little"), dtype=np.uint32).copy())      # 24 limbs: N0 < 2^768
        sh = self.sh
        n0m = cp.empty(sh["nS"], dtype=cp.uint32)
        nt = 256
        self.k["s200g_n0m"](((sh["nS"] + nt - 1) // nt,), (nt,), (limbs, np.int32(24), sh["S"], sh["MU"], np.int32(sh["nS"]), n0m))
        return GpuFeeder(None, None, U, n0m, klog=self.klog, llog=self.llog, f=self.f, p_est=self.p_est, nthreads=self.nthreads, shared=sh)

    def with_variant(self, n0m, U):
        return GpuFeeder(None, None, U, n0m, klog=self.klog, llog=self.llog, f=self.f, p_est=self.p_est, nthreads=self.nthreads, shared=self.sh)

    def window(self, k0, f=None):
        """Six launches and two small synchronisations: k0 mod s, sieve, counts, select, finalize (k, counts, CSR offsets), then once the
        number of survivor rows is known the rows kernel."""
        sh, K, L, nt = self.sh, self.K, self.L, self.nthreads
        f = self.f if f is None else float(f)
        nkeep = int(math.ceil(L * (1.0 - f)))
        nb = K // L
        nsel = nb * nkeep
        nS = sh["nS"]
        KM = cp.empty(nS, dtype=cp.uint32)
        self.k["s200g_km"](((nS + nt - 1) // nt,), (nt,), (sh["S"], np.uint64(k0), np.int32(nS), KM))
        self.k["s200g_sieve"]((self.nU,), (nt,), (self.U, sh["S"], sh["INV"], sh["MU"], self.N0M, KM, np.int32(nS), self.bits),
                              shared_mem=4 * (K // 32))
        self.k["s200g_count"](((K // 32 + nt - 1) // nt,), (nt,), (self.bits, np.int32(self.nU), self.counts))
        w = Window()
        w.k0, w.L = k0, L
        stats = cp.empty((nb, 3), dtype=cp.float64)
        keys = cp.empty((nb, max(nkeep, 1)), dtype=cp.uint32)
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
        cnt = cp.empty(nsel, dtype=cp.uint16)
        member = cp.empty(nsel, dtype=cp.uint32)
        kv = cp.empty(nsel, dtype=cp.uint64)
        offs = cp.empty(nsel + 1, dtype=cp.int64)
        total = cp.empty(1, dtype=cp.int64)
        self.k["s200g_finalize"]((1,), (nt,), (keys, np.int32(nsel), np.int32(max(nkeep, 1)), np.uint64(k0), cnt, member, kv, offs, total))
        tot = int(total[0])                                        # the one wait for the device before the rows can be allocated
        rows = cp.empty(tot, dtype=cp.uint16)
        if nsel:
            self.k["s200g_rows"]((((nsel + nt - 1) // nt),), (nt,), (self.bits, np.int32(self.nU), member, offs, np.int32(nsel), rows))
        st = cp.asnumpy(stats)
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
