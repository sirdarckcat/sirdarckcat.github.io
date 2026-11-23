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
#ifndef GEN_HOIST
#define GEN_HOIST 0  /* 1: gbig_gen_st takes the row of its items, its q and the pointer into the prime table out of the loops (a CTA's blockDim.x is a multiple of RCTA, so an item's row is the thread's): 24 -> ~15 instructions a visit */
#endif
#ifndef GEN_UNROLL
#define GEN_UNROLL 1 /* with GEN_HOIST: primes a thread sets up together in the visit loops of gbig_gen_st (their table entries and Shoup chains in flight at once, then their mark loops) */
#endif
#ifndef BIN_PACK
#define BIN_PACK 0   /* 1: packed bins (the STAGED kernel only): 5 marks of 19 bits in 3 words, 2.4 bytes a mark instead of 4: see "packed bins" below */
#endif
#ifndef GEN_ORDER
#define GEN_ORDER 0  /* 1: gbig_gen_st's grid is (row CTAs, chunks) instead of (chunks, row CTAs): the CTAs of one chunk (the RCTA-row slices of a row group) run together and the chunk's slice of the prime table
                        is read from DRAM once instead of once a slice: see "grid order" below */
#endif
#ifndef GEN_FLUSH2
#define GEN_FLUSH2 0 /* 1: gbig_gen_st stages the bin of a mark in its word (bin << TILE_LOG | offset = j + row * KS) and copies the staging buffer to the bins in one flat loop (a thread a word, or a group of
                        5 marks when packed) instead of a warp a bin: see "flat flush" below */
#endif
#ifndef FLUSH_UNROLL
#define FLUSH_UNROLL 4 /* GEN_FLUSH2: words (groups) a thread copies together */
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

/* ---- the staged variant of gbig_gen ----------------------------------------------------------------------------------------------------------------------------
 * gbig_gen writes every mark with a 4-byte store of its own into its bin: one L2 request a mark, into 430-790 MB of bins that do not fit the cache: 49 G marks/s (0.020 ns a
 * mark) on an RTX PRO 6000, 136-242 ms of the 373 ms a 2^25-member window at B = 1e8.  Here a CTA takes a CHUNK of primes whose marks for RCTA rows are about 3/4 of STAGE_CAP
 * (the host cuts the prime list so that every chunk has about the same expected marks: a prime s makes 2^KS_LOG / s marks a row), counts them by (row, tile) bin in shared memory,
 * reserves the room of every bin in global memory with one atomic a bin, writes the marks SORTED BY BIN into shared memory, and copies each bin's run to global memory with
 * consecutive threads on consecutive words (whole 128-byte lines: ~8x fewer L2 requests, no partial-sector traffic except at the two ends of a run).  A chunk with more than
 * STAGE_CAP marks (rare) is written the old way.  Same bins, same counts, same overflow protocol as gbig_gen (any bin over `cap`: gcnt[NBINS] = 1 and no writes).
 * Grid (nchunks, ceil(nrows / RCTA)), blockDim.x a multiple of 32 and >= NB = RCTA * NTILES; static shared memory 4 (STAGE_CAP + 4 NB) bytes (< 48 KB).
 * pstart[c] .. pstart[c + 1] - 1: the primes (indices into TAB) of chunk c.  RCTA is a power of two, RCTA_LOG its logarithm.
 */
#ifndef STAGE_CAP
#define STAGE_CAP 8192
#endif
#ifndef RCTA
#define RCTA 2
#endif
#ifndef RCTA_LOG
#define RCTA_LOG 1
#endif
#define NB (RCTA * NTILES)
#if GEN_FLUSH2
static_assert(((unsigned long long)RCTA << KS_LOG) <= (1ull << 32) && (unsigned long long)NB * (1ull << TILE_LOG) <= (1ull << 32), "GEN_FLUSH2: a staged word j + row * KS must fit 32 bits");
#endif

/* grid order (GEN_ORDER = 1): a row group's CTAs are (chunk, RCTA-row slice) pairs, and every slice of a chunk reads the same chunk of the prime table (pstart[c] .. pstart[c + 1], 16 bytes a prime).  With the
 * slice index as the SLOW dimension (the default grid (nchunks, slices)) a group streams the whole table, 92 MB at B = 1e8, once a slice, 4 times a group of 32 rows with rcta 8 (14 GB a window of 39 groups), and
 * the L2 (96-128 MB) holds none of it by the time the next slice comes, with the bins streaming through it.  With the slice index as the FAST dimension (grid (slices, nchunks)) the slices of a chunk are
 * launched together and the second to last read the chunk's table slice from the L2 the first one filled: 92 MB a group, 3.6 GB a window.  Same marks, same bins (as sets), same counts.
 *
 * flat flush (GEN_FLUSH2 = 1): the warp-a-bin flush below costs 36 (plain) / 80 (packed) SASS instructions a bin (every run starts with a 64-bit address setup and ends with a ragged tail) for runs of ~23
 * marks, 256 bins a CTA: ~19-20k warp instructions a CTA, more than pass A and pass B together (7k + 9k); at 1.0 M CTAs a window that is half of the kernel's 36 G warp instructions.  Here the staged word
 * carries its bin, (bin << TILE_LOG) | offset, which is j + row * KS (the loop variable of the item's marks, no extra instruction), the scan leaves one word a bin, dlt[b] = (the word index of the bin's run in
 * `bins`) - (the staging index of its run), and the flush is one flat loop, a thread a word: bins[i + dlt[stage[i] >> TILE_LOG]] = stage[i] & TILE_MASK, ~10 instructions a warp of 32 words.  Packed: every
 * run is padded to a multiple of 5 marks IN THE STAGING BUFFER (copies of its last mark, after pass B), so a group of 5 never straddles two bins, and a thread takes a group: 5 words in, 3 words out at
 * 3 g + dlt[b], dlt in groups of 3 words.  The words of a bin, its demand and its padding are those of the warp-a-bin flush.
 */
#if GEN_ORDER
#define GEN_CHUNK_ID blockIdx.y
#define GEN_RY_ID blockIdx.x
#else
#define GEN_CHUNK_ID blockIdx.x
#define GEN_RY_ID blockIdx.y
#endif

extern "C" __global__ void gbig_gen_st(const u32 *U, const uint4 *TAB, const int *pstart, int row0, int nrows, u32 cap, u32 *gcnt, u32 *bins) {
    __shared__ u32 stage[STAGE_CAP];
    __shared__ u32 cnt[NB], pos[NB], cur[NB], base[NB];
#if GEN_FLUSH2
    __shared__ u32 dlt[NB];
#endif
    __shared__ u32 over_s;
    const int tid = threadIdx.x;
    const int r0 = GEN_RY_ID * RCTA;                                    /* first row of this CTA in the group */
    const int nr = (nrows - r0 < RCTA) ? nrows - r0 : RCTA;
    const int p_lo = pstart[GEN_CHUNK_ID], p_hi = pstart[GEN_CHUNK_ID + 1];
    const int nitems = (p_hi - p_lo) << RCTA_LOG;                       /* (prime, row) pairs: item = prime * RCTA + row */
    for (int b = tid; b < NB; b += blockDim.x) cnt[b] = 0;
    if (tid == 0) over_s = 0;
    __syncthreads();
#if GEN_HOIST
    const int rrt = tid & (RCTA - 1);                                   /* the row of every item of this thread (blockDim.x is a multiple of RCTA): item = prime * RCTA + row */
    const bool live = rrt < nr;
    const u32 qt = live ? U[row0 + r0 + rrt] : 0u;
    const int pstep = (int)blockDim.x >> RCTA_LOG, np = p_hi - p_lo, pi0 = tid >> RCTA_LOG;
    const u32 rbt = (u32)rrt * NTILES;
#if GEN_FLUSH2
    const u32 rowS = (u32)rrt << KS_LOG, limS = KS + rowS;              /* the marks of an item: jw = j + row * KS < limS, bin = jw >> TILE_LOG */
#endif
#endif
    /* pass A: the marks of every bin of this CTA */
#if GEN_HOIST
    if (live) {
#if GEN_UNROLL > 1
        for (int pb = pi0; pb < np; pb += pstep * GEN_UNROLL) {
            uint4 t[GEN_UNROLL];
            u32 j[GEN_UNROLL];
            #pragma unroll
            for (int u = 0; u < GEN_UNROLL; u++) {
                const int pi = pb + u * pstep;
                t[u] = TAB[p_lo + (pi < np ? pi : np - 1)];                    /* clamped: an entry past the chunk is read (a valid address) and its marks are masked below */
            }
            #pragma unroll
            for (int u = 0; u < GEN_UNROLL; u++) {
                const u32 s = t[u].x;
                u32 a = qt * t[u].y - __umulhi(qt, t[u].z) * s;
                if (a >= s) a -= s;
                u32 jj = a + s - t[u].w;
                if (jj >= s) jj -= s;
#if GEN_FLUSH2
                j[u] = (pb + u * pstep < np) ? jj + rowS : limS;
#else
                j[u] = (pb + u * pstep < np) ? jj : (u32)KS;
#endif
            }
            #pragma unroll
            for (int u = 0; u < GEN_UNROLL; u++)
#if GEN_FLUSH2
                for (u32 jj = j[u]; jj < limS; jj += t[u].x) atomicAdd(&cnt[jj >> TILE_LOG], 1u);
#else
                for (u32 jj = j[u]; jj < KS; jj += t[u].x) atomicAdd(&cnt[rbt + (jj >> TILE_LOG)], 1u);
#endif
        }
#else
        const uint4 *tp = TAB + p_lo + pi0;
        for (int pi = pi0; pi < np; pi += pstep, tp += pstep) {
            const uint4 t = *tp;
            const u32 s = t.x;
            u32 a = qt * t.y - __umulhi(qt, t.z) * s;                    /* q M^-1 mod s, in [0, 2s) */
            if (a >= s) a -= s;
            u32 j = a + s - t.w;
            if (j >= s) j -= s;
#if GEN_FLUSH2
            for (j += rowS; j < limS; j += s) atomicAdd(&cnt[j >> TILE_LOG], 1u);
#else
            for (; j < KS; j += s) atomicAdd(&cnt[rbt + (j >> TILE_LOG)], 1u);
#endif
        }
#endif
    }
#else
    for (int it = tid; it < nitems; it += blockDim.x) {
        const int rr = it & (RCTA - 1);
        if (rr >= nr) continue;
        const uint4 t = TAB[p_lo + (it >> RCTA_LOG)];
        const u32 s = t.x, q = U[row0 + r0 + rr];
        u32 a = q * t.y - __umulhi(q, t.z) * s;                          /* q M^-1 mod s, in [0, 2s) */
        if (a >= s) a -= s;
        u32 j = a + s - t.w;
        if (j >= s) j -= s;
#if GEN_FLUSH2
        const u32 rowS = (u32)rr << KS_LOG;
        for (j += rowS; j < KS + rowS; j += s) atomicAdd(&cnt[j >> TILE_LOG], 1u);
#else
        const u32 rb = rr * NTILES;
        for (; j < KS; j += s) atomicAdd(&cnt[rb + (j >> TILE_LOG)], 1u);
#endif
    }
#endif
    __syncthreads();
    /* inclusive scan of the lengths (Hillis-Steele): pos[b] = staging words of bins 0 .. b; bin b's run is stage[pos[b] - len[b] .. pos[b]).  len = cnt, except in a packed flat flush: cnt rounded up to a multiple of 5 */
#if GEN_FLUSH2 && BIN_PACK
    if (tid < NB) pos[tid] = ((cnt[tid] + 4u) / 5u) * 5u;
#else
    if (tid < NB) pos[tid] = cnt[tid];
#endif
    __syncthreads();
    for (int d = 1; d < NB; d <<= 1) {
        u32 v = 0;
        if (tid < NB && tid >= d) v = pos[tid - d];
        __syncthreads();
        if (tid < NB && tid >= d) pos[tid] += v;
        __syncthreads();
    }
    const u32 total = pos[NB - 1];
    if (tid < NB) {                                                     /* the room of bin b in global memory: [base, base + w) of bin (r0 NTILES + b) */
        const u32 c = cnt[tid];
#if GEN_FLUSH2 && BIN_PACK
        const u32 len = ((c + 4u) / 5u) * 5u;
#else
        const u32 len = c;
#endif
#if BIN_PACK
        const u32 w = (total <= STAGE_CAP) ? 3u * ((c + 4u) / 5u) : 3u * c;     /* words: 3 a group of 5 marks (the last group padded with copies of the bin's last mark), or 3 a mark when the chunk is too big to stage */
#else
        const u32 w = c;
#endif
        const u32 bs = w ? atomicAdd(&gcnt[r0 * NTILES + tid], w) : 0u;
        base[tid] = bs;
        if (bs + w > cap) over_s = 1u;
        cur[tid] = (total <= STAGE_CAP) ? pos[tid] - len : 0u;
#if GEN_FLUSH2
#if BIN_PACK
        dlt[tid] = (u32)(r0 * NTILES + tid) * cap + bs - 3u * ((pos[tid] - len) / 5u);   /* (word of the bin's run in bins) - 3 (group of its run in the staging buffer): a group g of the buffer goes to 3 g + dlt */
#else
        dlt[tid] = (u32)(r0 * NTILES + tid) * cap + bs - (pos[tid] - len);               /* (word of the bin's run in bins) - (its staging index): word i goes to i + dlt */
#endif
#endif
    }
    __syncthreads();
    if (over_s) {
        if (tid == 0) gcnt[NBINS] = 1u;
        return;
    }
    if (total <= STAGE_CAP) {
        /* pass B: the same marks again, into the staging buffer at their place in bin order */
#if GEN_HOIST
        if (live) {
#if GEN_UNROLL > 1
            for (int pb = pi0; pb < np; pb += pstep * GEN_UNROLL) {
                uint4 t[GEN_UNROLL];
                u32 j[GEN_UNROLL];
                #pragma unroll
                for (int u = 0; u < GEN_UNROLL; u++) {
                    const int pi = pb + u * pstep;
                    t[u] = TAB[p_lo + (pi < np ? pi : np - 1)];                    /* clamped: an entry past the chunk is read (a valid address) and its marks are masked below */
                }
                #pragma unroll
                for (int u = 0; u < GEN_UNROLL; u++) {
                    const u32 s = t[u].x;
                    u32 a = qt * t[u].y - __umulhi(qt, t[u].z) * s;
                    if (a >= s) a -= s;
                    u32 jj = a + s - t[u].w;
                    if (jj >= s) jj -= s;
#if GEN_FLUSH2
                    j[u] = (pb + u * pstep < np) ? jj + rowS : limS;
#else
                    j[u] = (pb + u * pstep < np) ? jj : (u32)KS;
#endif
                }
                #pragma unroll
                for (int u = 0; u < GEN_UNROLL; u++)
#if GEN_FLUSH2
                    for (u32 jj = j[u]; jj < limS; jj += t[u].x) stage[atomicAdd(&cur[jj >> TILE_LOG], 1u)] = jj;
#else
                    for (u32 jj = j[u]; jj < KS; jj += t[u].x) stage[atomicAdd(&cur[rbt + (jj >> TILE_LOG)], 1u)] = jj & TILE_MASK;
#endif
            }
#else
            const uint4 *tp = TAB + p_lo + pi0;
            for (int pi = pi0; pi < np; pi += pstep, tp += pstep) {
                const uint4 t = *tp;
                const u32 s = t.x;
                u32 a = qt * t.y - __umulhi(qt, t.z) * s;
                if (a >= s) a -= s;
                u32 j = a + s - t.w;
                if (j >= s) j -= s;
#if GEN_FLUSH2
                for (j += rowS; j < limS; j += s) stage[atomicAdd(&cur[j >> TILE_LOG], 1u)] = j;
#else
                for (; j < KS; j += s) stage[atomicAdd(&cur[rbt + (j >> TILE_LOG)], 1u)] = j & TILE_MASK;
#endif
            }
#endif
        }
#else
        for (int it = tid; it < nitems; it += blockDim.x) {
            const int rr = it & (RCTA - 1);
            if (rr >= nr) continue;
            const uint4 t = TAB[p_lo + (it >> RCTA_LOG)];
            const u32 s = t.x, q = U[row0 + r0 + rr];
            u32 a = q * t.y - __umulhi(q, t.z) * s;
            if (a >= s) a -= s;
            u32 j = a + s - t.w;
            if (j >= s) j -= s;
#if GEN_FLUSH2
            const u32 rowS = (u32)rr << KS_LOG;
            for (j += rowS; j < KS + rowS; j += s) stage[atomicAdd(&cur[j >> TILE_LOG], 1u)] = j;
#else
            const u32 rb = rr * NTILES;
            for (; j < KS; j += s) stage[atomicAdd(&cur[rb + (j >> TILE_LOG)], 1u)] = j & TILE_MASK;
#endif
        }
#endif
        __syncthreads();
#if GEN_FLUSH2
#if BIN_PACK
        if (tid < NB) {                                                 /* pad every run to a multiple of 5 words with copies of its last word (the same mark: clearing a bit twice is harmless) */
            const u32 c = cnt[tid], len = ((c + 4u) / 5u) * 5u;
            if (len > c) {
                const u32 st = pos[tid] - len, last = stage[st + c - 1u];
                for (u32 e = c; e < len; e++) stage[st + e] = last;
            }
        }
        __syncthreads();
        const u32 ngr = total / 5u;                                     /* total is a multiple of 5: whole groups, a group inside one bin's run */
        for (u32 g0 = tid; g0 < ngr; g0 += blockDim.x * FLUSH_UNROLL) {
            u32 e[FLUSH_UNROLL][5];
            #pragma unroll
            for (int u = 0; u < FLUSH_UNROLL; u++) {
                const u32 g = g0 + u * blockDim.x;
                if (g < ngr) {
                    #pragma unroll
                    for (int k = 0; k < 5; k++) e[u][k] = stage[5u * g + k];
                }
            }
            #pragma unroll
            for (int u = 0; u < FLUSH_UNROLL; u++) {
                const u32 g = g0 + u * blockDim.x;
                if (g < ngr) {
                    const u32 d = dlt[e[u][0] >> TILE_LOG] + 3u * g;
                    const u32 m0 = e[u][0] & TILE_MASK, m1 = e[u][1] & TILE_MASK, m2 = e[u][2] & TILE_MASK, m3 = e[u][3] & TILE_MASK, m4 = e[u][4] & TILE_MASK;
                    bins[d] = m0 | (m1 << 19);
                    bins[d + 1u] = (m1 >> 13) | (m2 << 6) | (m3 << 25);
                    bins[d + 2u] = (m3 >> 7) | (m4 << 12);
                }
            }
        }
#else
        for (u32 i0 = tid; i0 < total; i0 += blockDim.x * FLUSH_UNROLL) {
            u32 w[FLUSH_UNROLL];
            #pragma unroll
            for (int u = 0; u < FLUSH_UNROLL; u++) {
                const u32 i = i0 + u * blockDim.x;
                if (i < total) w[u] = stage[i];
            }
            #pragma unroll
            for (int u = 0; u < FLUSH_UNROLL; u++) {
                const u32 i = i0 + u * blockDim.x;
                if (i < total) bins[i + dlt[w[u] >> TILE_LOG]] = w[u] & TILE_MASK;
            }
        }
#endif
#else
        /* flush: a warp a bin at a time, lane i on word i of the run */
        const int warp = tid >> 5, lane = tid & 31, nwarps = blockDim.x >> 5;
        for (int b = warp; b < NB; b += nwarps) {
            const u32 c = cnt[b];
            const u32 *src = stage + (pos[b] - c);
            u32 *dst = bins + (size_t)(r0 * NTILES + b) * cap + base[b];
#if BIN_PACK
            const u32 ng = (c + 4u) / 5u;                               /* a lane a group of 5 marks -> 3 words (the marks are 19-bit offsets, the last group repeats the last mark: clearing a bit twice is harmless) */
            for (u32 g = lane; g < ng; g += 32) {
                const u32 g5 = 5u * g, last = c - 1u;
                const u32 m0 = src[g5], m1 = src[g5 + 1u <= last ? g5 + 1u : last], m2 = src[g5 + 2u <= last ? g5 + 2u : last];
                const u32 m3 = src[g5 + 3u <= last ? g5 + 3u : last], m4 = src[g5 + 4u <= last ? g5 + 4u : last];
                dst[3u * g] = m0 | (m1 << 19);
                dst[3u * g + 1u] = (m1 >> 13) | (m2 << 6) | (m3 << 25);
                dst[3u * g + 2u] = (m3 >> 7) | (m4 << 12);
            }
#else
            for (u32 i = lane; i < c; i += 32) dst[i] = src[i];
#endif
        }
#endif
    } else {
        for (int it = tid; it < nitems; it += blockDim.x) {                 /* more marks than the buffer: one store a mark, as gbig_gen */
            const int rr = it & (RCTA - 1);
            if (rr >= nr) continue;
            const uint4 t = TAB[p_lo + (it >> RCTA_LOG)];
            const u32 s = t.x, q = U[row0 + r0 + rr];
            u32 a = q * t.y - __umulhi(q, t.z) * s;
            if (a >= s) a -= s;
            u32 j = a + s - t.w;
            if (j >= s) j -= s;
            const u32 rb = rr * NTILES;
            for (; j < KS; j += s) {
                const u32 b = rb + (j >> TILE_LOG);
#if BIN_PACK
                const u32 mk = j & TILE_MASK;                           /* one mark = one group of 5 copies of it (3 words) */
                u32 *d = bins + (size_t)(r0 * NTILES + b) * cap + base[b] + 3u * atomicAdd(&cur[b], 1u);
                d[0] = mk | (mk << 19);
                d[1] = (mk >> 13) | (mk << 6) | (mk << 25);
                d[2] = (mk >> 7) | (mk << 12);
#else
                bins[(size_t)(r0 * NTILES + b) * cap + base[b] + atomicAdd(&cur[b], 1u)] = j & TILE_MASK;
#endif
            }
        }
    }
}

/* Apply the n entries at e to the shared bitmap bm (every entry clears its bit).  e is 16-byte aligned (cap is a multiple of 32 words).  16-byte loads, GBIG_APPLY_UNROLL of
 * them in flight a thread: with one load at a time the apply is bound by the memory latency (1 CTA of 256 threads an SM keeps ~190 KB in flight, ~200 GB/s: measured 266 GB/s on an
 * RTX PRO 6000 against 1,460 GB/s of the device), so all the loads of an iteration are issued before the first atomic. */
#ifndef GBIG_APPLY_UNROLL
#define GBIG_APPLY_UNROLL 4
#endif
#define GBIG_CLEAR(bm, off) atomicAnd(&(bm)[(off) >> 5], ~(1u << ((off) & 31)))
#if BIN_PACK
/* packed bins: n words = n / 3 groups of 5 marks (19 bits each, bit 95 unused): w0 = m0 | m1 << 19, w1 = m1 >> 13 | m2 << 6 | m3 << 25, w2 = m3 >> 7 | m4 << 12.  A thread takes a group a step
   (3 word loads), GBIG_APPLY_UNROLL groups in flight. */
__device__ __forceinline__ void gbig_apply_entries(u32 *bm, const u32 *e, u32 n) {
    const u32 ng = __umulhi(n, 0xAAAAAAABu) >> 1;                       /* n / 3 (n is a multiple of 3: gcnt counts whole groups) */
    for (u32 i = threadIdx.x; i < ng; i += blockDim.x * GBIG_APPLY_UNROLL) {
        u32 w0[GBIG_APPLY_UNROLL], w1[GBIG_APPLY_UNROLL], w2[GBIG_APPLY_UNROLL];
        #pragma unroll
        for (int u = 0; u < GBIG_APPLY_UNROLL; u++) {
            const u32 g = i + u * blockDim.x;
            if (g < ng) { w0[u] = e[3u * g]; w1[u] = e[3u * g + 1u]; w2[u] = e[3u * g + 2u]; }
        }
        #pragma unroll
        for (int u = 0; u < GBIG_APPLY_UNROLL; u++) {
            if (i + u * blockDim.x < ng) {
                const u32 a = w0[u], b = w1[u], c = w2[u];
                GBIG_CLEAR(bm, a & 0x7FFFFu);
                GBIG_CLEAR(bm, ((a >> 19) | (b << 13)) & 0x7FFFFu);
                GBIG_CLEAR(bm, (b >> 6) & 0x7FFFFu);
                GBIG_CLEAR(bm, ((b >> 25) | (c << 7)) & 0x7FFFFu);
                GBIG_CLEAR(bm, (c >> 12) & 0x7FFFFu);
            }
        }
    }
}
#else
__device__ __forceinline__ void gbig_apply_entries(u32 *bm, const u32 *e, u32 n) {
    const uint4 *e4 = (const uint4 *)e;
    const u32 nv = n >> 2;
    for (u32 i = threadIdx.x; i < nv; i += blockDim.x * GBIG_APPLY_UNROLL) {
        uint4 v[GBIG_APPLY_UNROLL];
        #pragma unroll
        for (int u = 0; u < GBIG_APPLY_UNROLL; u++) {
            if (i + u * blockDim.x < nv) v[u] = e4[i + u * blockDim.x];
        }
        #pragma unroll
        for (int u = 0; u < GBIG_APPLY_UNROLL; u++) {
            if (i + u * blockDim.x < nv) { GBIG_CLEAR(bm, v[u].x); GBIG_CLEAR(bm, v[u].y); GBIG_CLEAR(bm, v[u].z); GBIG_CLEAR(bm, v[u].w); }
        }
    }
    for (u32 i = (nv << 2) + threadIdx.x; i < n; i += blockDim.x) { const u32 off = e[i]; GBIG_CLEAR(bm, off); }
}
#endif

/* one CTA a bin (row rr, tile): out[bin * TILE_WORDS ...] = the tile's bits, 1 = not marked */
extern "C" __global__ void gbig_apply(const u32 *gcnt, const u32 *bins, u32 cap, u32 *out) {
    S200G_DYNSHARED(u32, bm);
    const u32 bin = blockIdx.x;
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) bm[i] = 0xFFFFFFFFu;
    __syncthreads();
    u32 n = gcnt[bin];
    if (n > cap) n = cap;
    gbig_apply_entries(bm, bins + (size_t)bin * cap, n);
    __syncthreads();
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) out[(size_t)bin * TILE_WORDS + i] = bm[i];
}
