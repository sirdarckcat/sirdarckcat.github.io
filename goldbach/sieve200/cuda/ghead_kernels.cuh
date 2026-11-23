/* ghead_kernels.cuh -- the "deep head": a second large-prime stage for the FIRST rows only, applied AFTER the count / select / finalize of a window (needs gsieve_kernels.cuh, gbig_kernels.cuh,
 * gbatch_kernels.cuh before it, compiled with the same KS_LOG / TILE_LOG / RG).
 *
 * Why: the rows of a member are tested in ascending q until the first probable prime, so the first alive rows carry most of the Fermat tests (a row of index i is tested with probability
 * ~exp(-0.022 i): 90% of all tests are on the first ~100 rows), and an alive row (no factor below B = 1e8) of those rows has a prime factor in (B, B2] with probability 1 - ln B / ln B2 (11.1% for
 * B2 = 1e9).  Sieving ONLY the first R2 rows (64) by the primes in (B, B2] removes those composites from the kept members' row lists: ~8.6% fewer Fermat tests.  The count, the selection, the
 * statistics (hm_all, hm_kept, alive_total) stay on the B sieve, so the kept members, every member's first PRP row, the successes and the near-misses are the same as without the head: only
 * composite rows disappear from the lists, and cnt gets shorter (the Window keeps the old count as cnt_acc).
 *
 * The marks of these primes are RARE: a prime above KS = 2^KS_LOG makes at most one mark a row and a window (2^KS_LOG / s <= 17% of the pairs for s > 1e8), so there is no counting pass and no staging:
 *   ghead_gen   : a thread takes HEAD_PPT primes (a CTA of 256 threads: 1,024 primes), reads each prime's table entry ONCE and visits all the rows of the group (q values staged in shared memory); a mark is appended to
 *                 the bin of (row, tile) with one global atomic: slot = atomicAdd(&gcnt[bin], 1); bins[bin * cap + slot] = offset in the tile.  gcnt[bin] is the demand, gcnt[NBINS] the overflow flag (a slot >= cap is
 *                 not written: the host repeats the head stage with a larger cap; applying marks twice is harmless: a mark only clears a bit).
 *   ghead_apply : a CTA a (row, tile): the tile of the bit matrix (written by the tile kernel before) is read into shared memory, every mark clears its bit with atomicAnd, a bit that was still SET (an alive row of
 *                 a member the stage removes) is counted for the member if it is a kept one (slot_of[k] >= 0): dcnt[slot] += 1; the tile is written back.  A bit cleared twice (two head primes on one row) counts once.
 */
#ifndef HEAD_PPT
#define HEAD_PPT 4
#endif
extern "C" __global__ void ghead_gen(const u32 *U, const uint4 *TAB, int nP, int row0, int nrows, u32 cap, u32 *gcnt, u32 *bins) {
    __shared__ u32 q_s[RG];
    for (int i = threadIdx.x; i < nrows; i += blockDim.x) q_s[i] = U[row0 + i];
    __syncthreads();
    for (int pi = 0; pi < HEAD_PPT; pi++) {
        const int p = blockIdx.x * blockDim.x * HEAD_PPT + pi * blockDim.x + threadIdx.x;
        if (p >= nP) break;
        const uint4 t = TAB[p];
        const u32 s = t.x;
        for (int rr = 0; rr < nrows; rr++) {
            const u32 q = q_s[rr];
            u32 a = q * t.y - __umulhi(q, t.z) * s;                     /* q M^-1 mod s, in [0, 2s) */
            if (a >= s) a -= s;
            u32 j = a + s - t.w;
            if (j >= s) j -= s;
            for (; j < KS; j += s) {
                const u32 bin = (u32)rr * NTILES + (j >> TILE_LOG);
                const u32 slot = atomicAdd(&gcnt[bin], 1u);
                if (slot < cap) bins[(size_t)bin * cap + slot] = j & TILE_MASK;
                else gcnt[NBINS] = 1u;
            }
        }
    }
}

/* grid (nrows, NTILES), dynamic shared memory 4 TILE_WORDS bytes (64 KB at TILE_LOG = 19: max_dynamic_shared_size_bytes).  bits: the batch matrix [rows][KS / 32]; slot_of[k] = the kept slot of member k of
   the window, or -1; dcnt[slot] += the alive bits cleared in the member's column. */
extern "C" __global__ void ghead_apply(int row0, const u32 *gcnt, const u32 *bins, u32 cap, u32 *bits, const int *slot_of, u32 *dcnt) {
    S200G_DYNSHARED(u32, bm);
    const int rr = blockIdx.x;
    const u32 tile = blockIdx.y;
    u32 *seg = bits + (size_t)(row0 + rr) * (KS / 32u) + (size_t)tile * TILE_WORDS;
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) bm[i] = seg[i];
    __syncthreads();
    const u32 bin = (u32)rr * NTILES + tile;
    u32 n = gcnt[bin];
    if (n > cap) n = cap;
    const u32 *e = bins + (size_t)bin * cap;
    for (u32 i = threadIdx.x; i < n; i += blockDim.x) {
        const u32 j = e[i];
        const u32 old = atomicAnd(&bm[j >> 5], ~(1u << (j & 31)));
        if ((old >> (j & 31)) & 1u) {
            const int s = slot_of[(tile << TILE_LOG) + j];
            if (s >= 0) atomicAdd(&dcnt[s], 1u);
        }
    }
    __syncthreads();
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) seg[i] = bm[i];
}
