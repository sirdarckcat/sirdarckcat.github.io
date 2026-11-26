"""The deep head (ghead_kernels.cuh): the primes in (B, B2] applied to the FIRST `rows` rows of a window, after the count / select / finalize, to the kept members' row lists.

    head = HeadStage(S2, INV2, rows=64, ks_log=24, tile_log=19, rg=32, kernels=feeder.k)       # S2 / INV2: the primes in (B, B2] and M^-1 mod s (numpy uint32)
    head.retarget(N0)                                                                          # N0 mod s for these primes, on the GPU (once a variant)
    cnt, offs, total = head.apply(feeder, k0, member, cnt, offs, total, nsel)                  # inside GpuFeeder.window, between finalize and the rows kernel

What changes for the caller: bits of the first `rows` rows of the batch matrix are cleared where a head prime divides N0 - q + k M (those rows are composite), and the kept members' counts and CSR offsets
are recomputed (a member's list has the surviving rows only).  The kept members, alive_total, hm_all and hm_kept (the B sieve's) are NOT touched: the statistics and the selection stay what the B sieve says,
and a member's first PRP row, its success flag and its near-misses are those of the run without the head: only composite rows leave the lists.
"""
import numpy as np
import cupy as cp

import gbig


def prime_tables_range(M, cover, lo, hi):
    """(S, INV) for the primes s with lo < s <= hi that are not cover primes and do not divide M, ascending (uint32 arrays), and M^-1 mod s.  Same selection rule as deep_feeder.prime_tables_M; a numpy
    sieve to hi (1e9: ~1 GB of bool and ~1 minute)."""
    from deep_feeder import mod_big, modinv_vec
    S = gbig.primes_between(lo, hi).astype(np.int64)
    S = S[(S >= 3) & ~np.isin(S, [int(c) for c in cover])]
    mm = mod_big(M, S)
    keep = mm != 0
    S, mm = S[keep], mm[keep]
    INV = np.empty(S.size, dtype=np.uint32)
    for a in range(0, S.size, 1 << 22):
        INV[a:a + (1 << 22)] = modinv_vec(mm[a:a + (1 << 22)], S[a:a + (1 << 22)])
    return S.astype(np.uint32), INV


class HeadStage:
    def __init__(self, S, INV, rows, ks_log, tile_log, rg, kernels, threads=256, hppt=4):
        S = np.asarray(S, dtype=np.uint32)
        INV = np.asarray(INV, dtype=np.uint32)
        assert S.size and S.size == INV.size and int(S.min()) > (1 << ks_log), "the head primes must exceed the batch (at most one mark a row and window)"
        self.nP, self.rows, self.ks_log, self.tile_log, self.rg, self.threads, self.hppt = int(S.size), int(rows), ks_log, tile_log, rg, threads, hppt
        self.K, self.ntiles = 1 << ks_log, 1 << (ks_log - tile_log)
        self.tile_words = (1 << tile_log) // 32
        self.nbins = rg * self.ntiles
        self.k = kernels
        S64 = S.astype(np.uint64)
        self.S = cp.asarray(S)
        self.INV = cp.asarray(INV)
        self.INVP = cp.asarray(((INV.astype(np.uint64) << np.uint64(32)) // S64).astype(np.uint32))        # Shoup's constant floor(M^-1 2^32 / s)
        self.MU = cp.asarray(np.uint64(2 ** 64 - 1) // S64)                                                # for N0 mod s (s200g_n0m)
        self.expected_cap = gbig.expected_cap(S, tile_log)
        self.cap = self.expected_cap
        self.N0M = cp.empty(self.nP, dtype=cp.uint32)
        self.tab = cp.empty((self.nP, 4), dtype=cp.uint32)                                                  # {s, M^-1, invp, c0 of the window}
        self.gcnt = cp.zeros(self.nbins + 1, dtype=cp.uint32)
        self._bins = None
        self.apply_smem = 4 * self.tile_words
        if self.apply_smem > 48 * 1024:
            self.k["ghead_apply"].max_dynamic_shared_size_bytes = self.apply_smem
        self.retries = 0
        self.head_rows_applied = 0

    def retarget(self, N0):
        """N0 mod s for the head primes (the same GPU kernel as the main stage's)"""
        limbs = cp.asarray(np.frombuffer(int(N0).to_bytes(4 * 24, "little"), dtype=np.uint32).copy())
        nt = 256
        self.k["s200g_n0m"](((self.nP + nt - 1) // nt,), (nt,), (limbs, np.int32(24), self.S, self.MU, np.int32(self.nP), self.N0M))
        return self

    def _bins_buf(self, cap):
        need = self.nbins * cap
        assert need < (1 << 32), "bins index would overflow 32 bits"
        if self._bins is None or self._bins.size < need:
            self._bins = None
            self._bins = cp.empty(need, dtype=cp.uint32)
        return self._bins

    def _run_groups(self, fd, slot_of, dcnt):
        """prep (c0 of the window) is done by the caller; every group of rg rows: gen, then apply.  Returns the overflow flag (host int) and the largest demand"""
        nrows_head = min(self.rows, fd.nU)
        self.gcnt[:] = 0
        ovf = 0
        need = 0
        for row0 in range(0, nrows_head, self.rg):
            nr = min(self.rg, nrows_head - row0)
            bins = self._bins_buf(self.cap)
            self.gcnt[:] = 0
            grid = (self.nP + self.threads * self.hppt - 1) // (self.threads * self.hppt)
            self.k["ghead_gen"]((grid,), (self.threads,), (fd.U, self.tab, np.int32(self.nP), np.int32(row0), np.int32(nr), np.uint32(self.cap), self.gcnt, bins))
            self.k["ghead_apply"]((nr, self.ntiles), (self.threads,), (np.int32(row0), self.gcnt, bins, np.uint32(self.cap), fd.bits, slot_of, dcnt), shared_mem=self.apply_smem)
            c = cp.asnumpy(self.gcnt)                                       # one wait a group: the demand of every bin and the overflow flag
            ovf |= int(c[self.nbins])
            need = max(need, int(c[:self.nbins].max()))
        return ovf, need

    def apply(self, fd, k0, member, cnt, offs, total, nsel):
        """Clear the head primes' marks in the first `rows` rows of fd.bits and shorten the kept members' lists.  member: the kept members' k offsets in the window (uint32[nsel]); cnt, offs, total as GpuFeeder.window
        has them after finalize.  Returns (cnt, offs, total) of the shortened lists (cnt a new uint16 array, offs a new int64[nsel + 1], total a new int64[1])."""
        if nsel == 0 or self.rows <= 0:
            return cnt, offs, total
        sh = fd.sh
        self.k["s200g_prep"](((self.nP + 255) // 256,), (256,), (self.S, self.INV, self.INVP, self.N0M, np.uint64(k0), np.int32(self.nP), self.tab))
        slot_of = cp.full(self.K, -1, dtype=cp.int32)
        slot_of[member.astype(cp.int64)] = cp.arange(nsel, dtype=cp.int32)
        dcnt = cp.zeros(nsel, dtype=cp.uint32)
        while True:
            ovf, need = self._run_groups(fd, slot_of, dcnt)
            if not ovf:
                break
            self.cap = int(-(-(need + 64) // 32) * 32)                                  # a bin overflowed: repeat with the capacity the demand asks for (marks are idempotent: dcnt counts only 1 -> 0 transitions)
            self.retries += 1
        cnt2 = (cnt.astype(cp.int32) - dcnt.astype(cp.int32)).astype(cp.uint16)
        offs2 = cp.zeros(nsel + 1, dtype=cp.int64)
        offs2[1:] = cp.cumsum(cnt2.astype(cp.int64))
        total2 = offs2[-1:].copy()
        return cnt2, offs2, total2
