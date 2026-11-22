/* gbig_kernels.cuh -- the large-prime stage of a deep sieve: the marks of the primes above the tile (2^TILE_LOG bits, the shared bitmap of the
 * small-prime kernel), bucketed by (row, tile), then applied to the tile's shared bitmap.  A prototype to measure what one such mark costs.
 *
 * Why: a prime s above the tile hits a given (row, tile) with probability 2^TILE_LOG / s, so visiting every (row, prime) pair for every tile (what
 * the small-prime kernel does) costs s / 2^TILE_LOG visits a mark.  Here a pair is visited once per BATCH of 2^KS_LOG members (NTILES tiles), and each of its
 * marks (19-bit offset in its tile) is appended to the bin of (row, tile):
 *
 *   gbig_gen   : a CTA takes PPT * blockDim primes and RG rows.  Pass A counts the marks of every bin in a shared histogram; one global atomicAdd a bin
 *                reserves room in the bin (the capacity `cap` is checked once a CTA: gcnt[NBINS] is set on overflow, the CTA writes nothing and the host repeats with a larger cap);
 *                pass B generates the marks again and writes each offset to its place (runs of ~100 entries a bin and CTA) with one shared atomic a mark.  The first offset of a pair is
 *                j = ((q M^-1 mod s) - c0) mod s, by Shoup's multiplication by a constant, as s200g_sieve_sh (TAB = {s, M^-1, floor(M^-1 2^32 / s), c0}).
 *   gbig_apply : a CTA a (row, tile) bin: the tile's bitmap in shared memory is set to ones, every entry of the bin clears its bit (atomicAnd), the tile is written
 *                (out[bin][TILE_WORDS]); in the real pipeline the small-prime marks are made on the same shared bitmap first.
 *
 * Compile-time: TILE_LOG (19), KS_LOG (25: members of a batch = 2^KS_LOG), RG (rows a CTA group), PPT (primes a thread), S200G_DYNSHARED as in gsieve_kernels.cuh.
 */
typedef unsigned int u32;
typedef unsigned long long u64;
#ifndef TILE_LOG
#define TILE_LOG 19
#endif
#ifndef KS_LOG
#define KS_LOG 25
#endif
#ifndef RG
#define RG 16
#endif
#ifndef PPT
#define PPT 4
#endif
#define TILE_BITS (1u << TILE_LOG)
#define TILE_MASK (TILE_BITS - 1u)
#define TILE_WORDS (TILE_BITS / 32u)
#define NTILES (1u << (KS_LOG - TILE_LOG))
#define NBINS (RG * NTILES)
#define KS (1u << KS_LOG)

/* gcnt: NBINS + 1 words, zeroed by the host before a row group.  After the launch gcnt[b] is the DEMAND of bin b (the marks of all CTAs); if it exceeds `cap` for
   some bin, gcnt[NBINS] != 0 and the CTAs that found their reservation too large wrote nothing: the host repeats with cap >= max gcnt[b].  A CTA decides this once, after
   its reservations, so pass B has no capacity check.  bins: NBINS * cap words (NBINS * cap < 2^32).  nrows <= RG rows U[row0 .. row0 + nrows).  TAB: nP packed primes. */
extern "C" __global__ void gbig_gen(const u32 *U, const uint4 *TAB, int nP, int row0, int nrows, u32 cap, u32 *gcnt, u32 *bins) {
    __shared__ u32 st[NBINS];                  /* pass A: the marks of the bin in this CTA; then the next free index of the bin in `bins` */
    __shared__ u32 over_s;
    for (u32 b = threadIdx.x; b < NBINS; b += blockDim.x) st[b] = 0;
    if (threadIdx.x == 0) over_s = 0;
    __syncthreads();
    const int p0 = blockIdx.x * blockDim.x * PPT + threadIdx.x;
    /* pass A: count the marks of every bin of this CTA */
    for (int pi = 0; pi < PPT; pi++) {
        const int p = p0 + pi * blockDim.x;
        if (p >= nP) break;
        const uint4 t = TAB[p];
        const u32 s = t.x;
        for (int rr = 0; rr < nrows; rr++) {
            const u32 q = U[row0 + rr];
            u32 a = q * t.y - __umulhi(q, t.z) * s;                     /* q M^-1 mod s, in [0, 2s) */
            if (a >= s) a -= s;
            u32 j = a + s - t.w;
            if (j >= s) j -= s;
            const u32 rb = rr * NTILES;
            for (; j < KS; j += s) atomicAdd(&st[rb + (j >> TILE_LOG)], 1u);
        }
    }
    __syncthreads();
    for (u32 b = threadIdx.x; b < NBINS; b += blockDim.x) {
        const u32 c = st[b];
        const u32 base = c ? atomicAdd(&gcnt[b], c) : 0u;               /* this CTA's room in bin b: [base, base + c) */
        if (base + c > cap) over_s = 1u;
        st[b] = b * cap + base;
    }
    __syncthreads();
    if (over_s) {
        if (threadIdx.x == 0) gcnt[NBINS] = 1u;
        return;
    }
    /* pass B: the same marks, written: one shared atomic a mark gives the index in `bins` */
    for (int pi = 0; pi < PPT; pi++) {
        const int p = p0 + pi * blockDim.x;
        if (p >= nP) break;
        const uint4 t = TAB[p];
        const u32 s = t.x;
        for (int rr = 0; rr < nrows; rr++) {
            const u32 q = U[row0 + rr];
            u32 a = q * t.y - __umulhi(q, t.z) * s;
            if (a >= s) a -= s;
            u32 j = a + s - t.w;
            if (j >= s) j -= s;
            const u32 rb = rr * NTILES;
            for (; j < KS; j += s) bins[atomicAdd(&st[rb + (j >> TILE_LOG)], 1u)] = j & TILE_MASK;
        }
    }
}

/* one CTA a bin (row rr, tile): out[bin * TILE_WORDS ...] = the tile's bits, 1 = not marked */
extern "C" __global__ void gbig_apply(const u32 *gcnt, const u32 *bins, u32 cap, u32 *out) {
    S200G_DYNSHARED(u32, bm);
    const u32 bin = blockIdx.x;
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) bm[i] = 0xFFFFFFFFu;
    __syncthreads();
    u32 n = gcnt[bin];
    if (n > cap) n = cap;
    const u32 *e = bins + (size_t)bin * cap;
    for (u32 i = threadIdx.x; i < n; i += blockDim.x) {
        const u32 off = e[i];
        atomicAnd(&bm[off >> 5], ~(1u << (off & 31)));
    }
    __syncthreads();
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) out[(size_t)bin * TILE_WORDS + i] = bm[i];
}
