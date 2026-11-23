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

extern "C" __global__ void gbig_gen_st(const u32 *U, const uint4 *TAB, const int *pstart, int row0, int nrows, u32 cap, u32 *gcnt, u32 *bins) {
    __shared__ u32 stage[STAGE_CAP];
    __shared__ u32 cnt[NB], pos[NB], cur[NB], base[NB];
    __shared__ u32 over_s;
    const int tid = threadIdx.x;
    const int r0 = blockIdx.y * RCTA;                                   /* first row of this CTA in the group */
    const int nr = (nrows - r0 < RCTA) ? nrows - r0 : RCTA;
    const int p_lo = pstart[blockIdx.x], p_hi = pstart[blockIdx.x + 1];
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
                if (pi < np) t[u] = TAB[p_lo + pi]; else { t[u].x = 1; t[u].y = 0; t[u].z = 0; t[u].w = 0; }
            }
            #pragma unroll
            for (int u = 0; u < GEN_UNROLL; u++) {
                const u32 s = t[u].x;
                u32 a = qt * t[u].y - __umulhi(qt, t[u].z) * s;
                if (a >= s) a -= s;
                u32 jj = a + s - t[u].w;
                if (jj >= s) jj -= s;
                j[u] = (pb + u * pstep < np) ? jj : (u32)KS;
            }
            #pragma unroll
            for (int u = 0; u < GEN_UNROLL; u++)
                for (u32 jj = j[u]; jj < KS; jj += t[u].x) atomicAdd(&cnt[rbt + (jj >> TILE_LOG)], 1u);
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
            for (; j < KS; j += s) atomicAdd(&cnt[rbt + (j >> TILE_LOG)], 1u);
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
        const u32 rb = rr * NTILES;
        for (; j < KS; j += s) atomicAdd(&cnt[rb + (j >> TILE_LOG)], 1u);
    }
#endif
    __syncthreads();
    /* inclusive scan of the counts (Hillis-Steele): pos[b] = marks of bins 0 .. b; bin b's run is stage[pos[b] - cnt[b] .. pos[b]) */
    if (tid < NB) pos[tid] = cnt[tid];
    __syncthreads();
    for (int d = 1; d < NB; d <<= 1) {
        u32 v = 0;
        if (tid < NB && tid >= d) v = pos[tid - d];
        __syncthreads();
        if (tid < NB && tid >= d) pos[tid] += v;
        __syncthreads();
    }
    const u32 total = pos[NB - 1];
    if (tid < NB) {                                                     /* the room of bin b in global memory: [base, base + c) of bin (r0 NTILES + b) */
        const u32 c = cnt[tid];
#if BIN_PACK
        const u32 w = (total <= STAGE_CAP) ? 3u * ((c + 4u) / 5u) : 3u * c;     /* words: 3 a group of 5 marks (the last group padded with copies of the bin's last mark), or 3 a mark when the chunk is too big to stage */
#else
        const u32 w = c;
#endif
        const u32 bs = w ? atomicAdd(&gcnt[r0 * NTILES + tid], w) : 0u;
        base[tid] = bs;
        if (bs + w > cap) over_s = 1u;
        cur[tid] = (total <= STAGE_CAP) ? pos[tid] - c : 0u;
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
                    if (pi < np) t[u] = TAB[p_lo + pi]; else { t[u].x = 1; t[u].y = 0; t[u].z = 0; t[u].w = 0; }
                }
                #pragma unroll
                for (int u = 0; u < GEN_UNROLL; u++) {
                    const u32 s = t[u].x;
                    u32 a = qt * t[u].y - __umulhi(qt, t[u].z) * s;
                    if (a >= s) a -= s;
                    u32 jj = a + s - t[u].w;
                    if (jj >= s) jj -= s;
                    j[u] = (pb + u * pstep < np) ? jj : (u32)KS;
                }
                #pragma unroll
                for (int u = 0; u < GEN_UNROLL; u++)
                    for (u32 jj = j[u]; jj < KS; jj += t[u].x) stage[atomicAdd(&cur[rbt + (jj >> TILE_LOG)], 1u)] = jj & TILE_MASK;
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
                for (; j < KS; j += s) stage[atomicAdd(&cur[rbt + (j >> TILE_LOG)], 1u)] = j & TILE_MASK;
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
            const u32 rb = rr * NTILES;
            for (; j < KS; j += s) stage[atomicAdd(&cur[rb + (j >> TILE_LOG)], 1u)] = j & TILE_MASK;
        }
#endif
        __syncthreads();
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
