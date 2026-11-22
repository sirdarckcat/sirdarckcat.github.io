/* gbatch_kernels.cuh -- the tile kernel of a batch (needs gsieve_kernels.cuh, compiled with KLOG = KS_LOG, and gbig_kernels.cuh before it).
 *
 * A batch is 2^KS_LOG members (NTILES tiles of 2^TILE_LOG).  For a group of rows gbig_gen has put the marks of the large primes (above the split) into bins of (row, tile);
 * s200g_tile does the rest of one (row, tile): the shared bitmap of the tile is set to ones, the marks of the small primes are made (Shoup set-up, as s200g_sieve_sh, from the table of
 * this tile: c0 includes the tile's offset), the bin's entries are applied, and the tile is written into the batch matrix bits[row][2^KS_LOG / 32] that the count, select and rows
 * kernels read (KLOG = KS_LOG).  s200g_prep_tiles builds the per-tile tables once a batch.
 */
/* TABT[tile * nS + p] = {s, M^-1, invp, c0 of the tile}: c0 = (N0 M^-1 + k0 + tile 2^TILE_LOG) mod s */
extern "C" __global__ void s200g_prep_tiles(const u32 *S, const u32 *INV, const u32 *INVP, const u32 *N0M, u64 k0, int nS, uint4 *TABT) {
    const int p = blockIdx.x * blockDim.x + threadIdx.x;
    if (p >= nS) return;
    const u32 s = S[p], inv = INV[p], invp = INVP[p], n0 = N0M[p];
    u32 r = n0 * inv - __umulhi(n0, invp) * s;                          /* N0 M^-1 mod s */
    if (r >= s) r -= s;
    for (u32 t = 0; t < NTILES; t++) {
        u32 c0 = r + (u32)((k0 + ((u64)t << TILE_LOG)) % s);
        if (c0 >= s) c0 -= s;
        uint4 v;
        v.x = s; v.y = inv; v.z = invp; v.w = c0;
        TABT[(size_t)t * nS + p] = v;
    }
}

/* grid (nrows, NTILES): row rr of the group = row0 + rr, tile blockIdx.y.  nS small primes (the table of every tile), gcnt / bins / cap from gbig_gen (no overflow). */
extern "C" __global__ void s200g_tile(const u32 *U, int row0, const uint4 *TABT, int nS, const u32 *gcnt, const u32 *bins, u32 cap, u32 *bits) {
    S200G_DYNSHARED(u32, bm);
    const int rr = blockIdx.x;
    const int tile = blockIdx.y;
    const u32 q = U[row0 + rr];
    const uint4 *tab = TABT + (size_t)tile * nS;
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) bm[i] = 0xFFFFFFFFu;
    __syncthreads();
    int p = threadIdx.x;
    uint4 t_n;
    t_n.x = 1; t_n.y = 0; t_n.z = 0; t_n.w = 0;
    if (p < nS) t_n = tab[p];
    for (; p < nS; p += blockDim.x) {
        const uint4 t = t_n;
        const int pn = p + blockDim.x;
        if (pn < nS) t_n = tab[pn];
        const u32 s = t.x;
        u32 a = q * t.y - __umulhi(q, t.z) * s;
        if (a >= s) a -= s;
        u32 j = a + s - t.w;
        if (j >= s) j -= s;
        for (; j < TILE_BITS; j += s) atomicAnd(&bm[j >> 5], __funnelshift_l(0xFFFFFFFEu, 0xFFFFFFFEu, j));
    }
    __syncthreads();
    const u32 bin = rr * NTILES + tile;
    const u32 n = gcnt[bin];
    const u32 *e = bins + (size_t)bin * cap;
    for (u32 i = threadIdx.x; i < n; i += blockDim.x) {
        const u32 off = e[i];
        atomicAnd(&bm[off >> 5], ~(1u << (off & 31)));
    }
    __syncthreads();
    u32 *dst = bits + (size_t)(row0 + rr) * (KS / 32u) + (size_t)tile * TILE_WORDS;
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) dst[i] = bm[i];
}
