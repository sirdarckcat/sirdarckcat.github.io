"""The batch-level sieve with a deep bound for a search_gpu5-style driver: ONE BatchFeeder (gbatch.py) for all the variants of a campaign.

    from deep_feeder import DeepSieve, deep_feeder_for
    ds = DeepSieve(M, cover_primes, B=100_000_000, ks_log=25, llog=15, f=0.97, p_est=0.055, split=1_000_000, rg=16, max_rows=1100)
    fd = ds.feeder(N0, rows)          # the feeder of the variant (N0, rows); same M, so the same primes
    w = fd.window(k0)                 # 2^ks_log members k0 .. k0 + 2^ks_log - 1 (k0 a multiple of 2^ks_log); the Window of gpu_sieve.GpuFeeder

or, as search_gpu5.py's feeder_for does (see DEEPSIEVE.md for the patch):  fd = deep_feeder_for(state_dict, spec, B=..., ks_log=..., ...)

What it saves over `search.init_spec` + `GpuFeeder.from_search_G`: the prime list and M^-1 mod s of 5.7M primes (B = 10^8) are made once per M with numpy (a few seconds; init_spec
loops in Python and takes minutes), N0 mod s for every prime is computed on the GPU per variant, and one bit matrix (max_rows rows x 2^ks_log bits: 4.4 GB for 1,100 rows at
2^25 members) and one large-prime stage are shared by all variants (retarget).  The primes are the same ones init_spec makes: 3 <= s < B, not a cover prime, not dividing M.
"""
import os
import time

import numpy as np

import gbig


def modinv_vec(a, m):
    """a^-1 mod m for int64 arrays (a, m coprime): vectorised extended Euclid"""
    a = a.astype(np.int64) % m
    r0, r1 = m.astype(np.int64).copy(), a.copy()
    t0, t1 = np.zeros_like(a), np.ones_like(a)
    while np.any(r1 != 0):
        nz = r1 != 0
        q = np.where(nz, r0 // np.where(nz, r1, 1), 0)
        r0, r1 = np.where(nz, r1, r0), np.where(nz, r0 - q * r1, r1)
        t0, t1 = np.where(nz, t1, t0), np.where(nz, t0 - q * t1, t1)
    return (t0 % m).astype(np.int64)


def mod_big(n, S):
    """n mod s for a Python integer n and an int64 array of primes below 2^31: Horner in 31-bit limbs"""
    limbs = []
    n = int(n)
    while n:
        limbs.append(n & 0x7FFFFFFF)
        n >>= 31
    r = np.zeros(S.shape, dtype=np.int64)
    for limb in reversed(limbs):
        r = (r * (1 << 31) + limb) % S
    return r


def prime_tables_M(M, cover, B):
    """(S, INV): the primes s with 3 <= s < B that are not cover primes and do not divide M (as search.init_spec), ascending, and M^-1 mod s; uint32 arrays"""
    S = gbig.primes_between(2, B - 1).astype(np.int64)
    S = S[(S >= 3) & ~np.isin(S, [int(c) for c in cover])]
    mm = mod_big(M, S)
    keep = mm != 0                                                      # an s dividing M cannot sieve
    S, mm = S[keep], mm[keep]
    INV = np.empty(S.size, dtype=np.uint32)
    for lo in range(0, S.size, 1 << 22):                                # chunks: the extended Euclid keeps ~8 temporaries of the chunk's size (50M primes at B = 1e9)
        INV[lo:lo + (1 << 22)] = modinv_vec(mm[lo:lo + (1 << 22)], S[lo:lo + (1 << 22)])
    return S.astype(np.uint32), INV


class DeepSieve:
    def __init__(self, M, cover, B, ks_log=25, tile_log=19, llog=15, f=0.97, p_est=0.055, split=1_000_000, rg=16, ppt=4, nthreads=256, gen_threads=256, tile_threads=256,
                 max_rows=1100, log=None, staged=None, rcta=None, stage_cap=None, head_b=0, head_rows=0):
        """staged / rcta / stage_cap: the staged large-prime kernel (gbig_gen_st); None = the environment variables DEEP_STAGED (0), DEEP_RCTA (2), DEEP_STAGE_CAP (8192), so that
        a driver script can switch it without a new patch.
        head_b / head_rows: the DEEP HEAD (ghead.py): the primes in (B, head_b] on the first head_rows rows, applied after the selection to the kept members' lists (0: none)"""
        from gbatch import BatchFeeder                                   # (imports cupy)
        tile_log = int(os.environ.get("DEEP_TILE_LOG", tile_log))         # DEEP_TILE_LOG=18: tiles of 2^18 bits (32 KB of shared memory: 3 tile CTAs an SM instead of 1); the driver passes no tile_log
        staged = bool(int(os.environ.get("DEEP_STAGED", "0"))) if staged is None else bool(staged)
        rcta = int(os.environ.get("DEEP_RCTA", "2")) if rcta is None else int(rcta)
        stage_cap = int(os.environ.get("DEEP_STAGE_CAP", "8192")) if stage_cap is None else int(stage_cap)
        t0 = time.time()
        S, INV = prime_tables_M(M, cover, B)
        t1 = time.time()
        U0 = np.ones(1, dtype=np.uint32)                                 # a placeholder variant: feeder() retargets it
        self.fd = BatchFeeder(S, INV, U0, np.zeros(S.size, dtype=np.uint32), ks_log=ks_log, tile_log=tile_log, llog=llog, f=f, p_est=p_est, nthreads=nthreads, split=split, rg=rg,
                              ppt=ppt, gen_threads=gen_threads, tile_threads=tile_threads, max_rows=max_rows, staged=staged, rcta=rcta, stage_cap=stage_cap)
        self.M, self.B, self.max_rows = int(M), int(B), int(max_rows)
        self.head_b, self.head_rows = int(head_b), int(head_rows)
        if self.head_b > self.B and self.head_rows > 0:
            import ghead
            th = time.time()
            S2, INV2 = ghead.prime_tables_range(M, cover, B, head_b)
            self.fd.head = ghead.HeadStage(S2, INV2, head_rows, ks_log, tile_log, rg, self.fd.k, threads=nthreads)
            if log:
                log(f"deep head: {S2.size:,} primes in ({B:,}, {head_b:,}] on the first {head_rows} rows, applied after the selection ({time.time() - th:.1f} s tables, {S2.size * 40 / 2**20:.0f} MB of device memory)")
        self.nprimes, self.n_small, self.n_large = int(S.size), self.fd.n_small, self.fd.n_large
        if log:
            log(f"deep sieve: {'staged' if staged else 'plain'} large-prime kernel{f' (rcta {rcta}, stage {stage_cap})' if staged else ''}; M with {len(cover)} cover primes excluded, {S.size:,} primes below {B:,} ({self.n_small:,} in the tile kernel, {self.n_large:,} in the large-prime stage), "
                f"batches of 2^{ks_log} members, bit matrix {max_rows} x {(1 << ks_log) // 8 / 2**20:.0f} MB; tables {t1 - t0:.1f} s, feeder {time.time() - t1:.1f} s")

    def feeder(self, N0, rows):
        """the BatchFeeder pointed at the variant (N0, rows) (same M as this DeepSieve): N0 mod s on the GPU, the rows replaced; the same object every time"""
        return self.fd.retarget(N0, rows)


def deep_feeder_for(state, spec, B, ks_log=25, tile_log=19, llog=15, f=0.97, p_est=0.055, split=1_000_000, rg=16, max_rows=1100, nthreads=256, gen_threads=256, tile_threads=256, log=print,
                    head_b=0, head_rows=0):
    """search_gpu5's feeder_for for the deep sieve: state is a dict kept by the caller (it holds the DeepSieve of the current M); spec a campaign spec (M, N0, residual, cover)."""
    M = int(spec["M"])
    ds = state.get("ds")
    if ds is None or ds.M != M:
        state.clear()
        cover = [int(r) for r, _ in spec.get("cover", [])]
        state["ds"] = ds = DeepSieve(M, cover, B, ks_log=ks_log, tile_log=tile_log, llog=llog, f=f, p_est=p_est, split=split, rg=rg, nthreads=nthreads, gen_threads=gen_threads,
                                      tile_threads=tile_threads, max_rows=max_rows, log=log, head_b=head_b, head_rows=head_rows)
    return ds.feeder(int(spec["N0"]), [int(q) for q in spec["residual"]])
