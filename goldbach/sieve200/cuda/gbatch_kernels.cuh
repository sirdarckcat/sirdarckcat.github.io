/* gbatch_kernels.cuh -- the tile kernel of a batch (needs gsieve_kernels.cuh, compiled with KLOG = KS_LOG, and gbig_kernels.cuh before it).
 *
 * A batch is 2^KS_LOG members (NTILES tiles of 2^TILE_LOG).  For a group of rows gbig_gen has put the marks of the large primes (above the split) into bins of (row, tile);
 * s200g_tile does the rest of one (row, tile): the shared bitmap of the tile is set to ones, the marks of the small primes are made (Shoup set-up, as s200g_sieve_sh, from the table of
 * this tile: c0 includes the tile's offset), the bin's entries are applied, and the tile is written into the batch matrix bits[row][2^KS_LOG / 32] that the count, select and rows
 * kernels read (KLOG = KS_LOG).  s200g_prep_tiles builds the per-tile tables once a batch.
 */
#ifndef TILE_LB
#define TILE_LB   /* a driver may define __launch_bounds__(threads, minCTAs) (DEEP_TILE_MAXREG) so that a tile CTA fits in the registers resident Fermat CTAs leave free */
#endif
#ifndef TILE_PREFETCH_KB
#define TILE_PREFETCH_KB 0   /* DEEP_TILE_PREFETCH: KB of this CTA's bin to ask the L2 for at kernel start (prefetch.global.L2), so that the apply, which reads the bin AFTER the small primes' marks, finds it there */
#endif
#ifndef TILE_UNROLL
#define TILE_UNROLL 1   /* primes a thread sets up together in the small-prime loop (DEEP_TILE_UNROLL): 1 = the original loop, 2 / 4 = the table loads and the Shoup chains of that many primes in flight at once */
#endif
#ifndef TILE_PIPE
#define TILE_PIPE 0     /* DEEP_TILE_PIPE=1: the tile kernel streams its bin through shared memory with cp.async WHILE the other warps make the small primes' marks (see "pipelined tile" below) */
#endif
#ifndef TILE_PIPE_AT
#define TILE_PIPE_AT 128    /* threads (whole warps) that apply the bin; the others make the small primes' marks */
#endif
#ifndef TILE_PIPE_CH
#define TILE_PIPE_CH 4092   /* words of a bin chunk (a multiple of 12: whole 16-byte copies and whole groups of 3 words); two chunks of 16 KB are in flight */
#endif
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

/* grid (nrows, NTILES): row rr of the group = row0 + rr, tile blockIdx.y.  nS small primes (the table of every tile), gcnt / bins / cap from gbig_gen.  If a bin of the group overflowed `cap`
   (gcnt[NBINS] != 0) its entries are incomplete and some slots were never written (stale or uninitialised: an entry is a bit index, read blindly): none is applied and the rows of the group
   are wrong; the host learns of it from the flag (BigStage.gen_group(defer=...) accumulates it, read once a window) and repeats the window the old way (no round trip a group). */
extern "C" __global__ void TILE_LB s200g_tile(const u32 *U, int row0, const uint4 *TABT, int nS, const u32 *gcnt, const u32 *bins, u32 cap, u32 *bits) {
    S200G_DYNSHARED(u32, bm);
    const int rr = blockIdx.x;
    const int tile = blockIdx.y;
    const u32 q = U[row0 + rr];
    const uint4 *tab = TABT + (size_t)tile * nS;
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) bm[i] = 0xFFFFFFFFu;
#if TILE_PREFETCH_KB > 0 && (defined(__CUDA_ARCH__) || defined(__CUDACC_RTC__))
    {   /* the bin of this (row, tile) is read only after the marks of the small primes (~100 us of shared-memory atomics a CTA): its first TILE_PREFETCH_KB KB are fetched from DRAM meanwhile */
        const u32 pb_bin = (u32)rr * NTILES + tile;
        u32 pn_ = gcnt[pb_bin];
        if (gcnt[NBINS] != 0u) pn_ = 0u;
        u32 pbytes = pn_ * 4u;
        if (pbytes > TILE_PREFETCH_KB * 1024u) pbytes = TILE_PREFETCH_KB * 1024u;
        const char *pbase = (const char *)(bins + (size_t)pb_bin * cap);
        for (u32 off = threadIdx.x * 128u; off < pbytes; off += blockDim.x * 128u) asm volatile("prefetch.global.L2 [%0];" :: "l"(pbase + off));
    }
#endif
    __syncthreads();
#if TILE_UNROLL > 1
    /* The loop below has one dependent chain a prime (a table load, the Shoup product, two conditional subtractions, then a data-dependent loop of marks) and a CTA has only 16 warps, 4 a scheduler:
       the SM issues ~0.36 warp-instructions a cycle (SASS: 129 instructions for 16 marks, 37 a prime; the shared-memory atomics run at ~12 marks a clock an SM and the kernel at ~0.8).  Here
       TILE_UNROLL primes' entries are loaded together, their start offsets computed together (independent chains), then their mark loops run one after the other: the same marks, the same bits. */
    for (int pb = threadIdx.x; pb < nS; pb += blockDim.x * TILE_UNROLL) {
        uint4 t[TILE_UNROLL];
        #pragma unroll
        for (int u = 0; u < TILE_UNROLL; u++) {
            const int pp = pb + u * (int)blockDim.x;
            t[u] = tab[pp < nS ? pp : nS - 1];                                 /* clamped: the (out of range) entry is read and its marks are masked below (nS >= 1 here) */
        }
        u32 j[TILE_UNROLL];
        #pragma unroll
        for (int u = 0; u < TILE_UNROLL; u++) {
            const u32 s = t[u].x;
            u32 a = q * t[u].y - __umulhi(q, t[u].z) * s;
            if (a >= s) a -= s;
            u32 jj = a + s - t[u].w;
            if (jj >= s) jj -= s;
            j[u] = (pb + u * (int)blockDim.x < nS) ? jj : (u32)TILE_BITS;      /* past the table: no marks */
        }
        #pragma unroll
        for (int u = 0; u < TILE_UNROLL; u++) {
            const u32 s = t[u].x;
            for (u32 jj = j[u]; jj < TILE_BITS; jj += s) atomicAnd(&bm[jj >> 5], __funnelshift_l(0xFFFFFFFEu, 0xFFFFFFFEu, jj));
        }
    }
#else
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
#endif
    __syncthreads();
    const u32 bin = rr * NTILES + tile;
    u32 n = gcnt[bin];
    if (gcnt[NBINS] != 0u) n = 0u;
    gbig_apply_entries(bm, bins + (size_t)bin * cap, n);
    __syncthreads();
    u32 *dst = bits + (size_t)(row0 + rr) * (KS / 32u) + (size_t)tile * TILE_WORDS;
    for (u32 i = threadIdx.x; i < TILE_WORDS; i += blockDim.x) dst[i] = bm[i];
}

/* ---- pipelined tile (TILE_PIPE = 1) ------------------------------------------------------------------------------------------------------------------------------------------------------
 * The plain kernel does three things one after the other with one CTA an SM (the 64 KB bitmap fills the shared memory): the small primes' marks (~38 us a CTA, issue / L2 bound), then the bin's
 * apply (360 KB read from DRAM: the 188 CTAs of a wave read 68 MB, ~45 us at the DRAM rate, though PF=256 asks the L2 for most of it earlier), then the write.  DRAM sits idle for the first
 * phase and the SMs for most of the second: the kernel moves 17 GB in 20.9 ms (54% of the DRAM rate) and is 11.9 ms without any bin.  The marks of the small primes and the entries of the bin
 * are both atomicAnd on the same bitmap, so they may happen in ANY order and at the same time.  Here TILE_PIPE_AT threads (4 warps of 16) are the apply role: they stream the bin through two
 * shared-memory buffers of TILE_PIPE_CH words with cp.async (16 bytes a copy, straight from the memory system into shared memory), wait for a chunk, apply it (named barrier 1 among them
 * only), and refill the buffer; the other warps run the small-prime loop of the unrolled kernel (TILE_UNROLL, with their thread indices shifted) and never wait for them.  At the end the usual barrier.
 * Shared memory: bitmap + 2 TILE_PIPE_CH words (96 KB at the defaults: dynamic, host: BatchFeeder.tile_smem).  The bits are the same: the same atomicAnd of the same set of bit indices.
 */
#if TILE_PIPE
#if defined(__CUDA_ARCH__) || defined(__CUDACC_RTC__)
__device__ __forceinline__ void tp_cp16(u32 *dst, const u32 *src) {
    asm volatile("cp.async.cg.shared.global [%0], [%1], 16;" :: "r"((u32)__cvta_generic_to_shared(dst)), "l"(src) : "memory");
}
__device__ __forceinline__ void tp_commit() { asm volatile("cp.async.commit_group;" ::: "memory"); }
__device__ __forceinline__ void tp_wait1() { asm volatile("cp.async.wait_group 1;" ::: "memory"); }
__device__ __forceinline__ void tp_wait0() { asm volatile("cp.async.wait_group 0;" ::: "memory"); }
__device__ __forceinline__ void tp_bar() { asm volatile("bar.sync 1, %0;" :: "n"(TILE_PIPE_AT) : "memory"); }
#else      /* the CPU emulation (gsieve_cpu.cpp): the copy is immediate, the named barrier is a second pthread barrier among the apply threads */
static inline void tp_cp16(u32 *dst, const u32 *src) { memcpy(dst, src, 16); }
static inline void tp_commit() {}
static inline void tp_wait1() {}
static inline void tp_wait0() {}
static inline void tp_bar() { pthread_barrier_wait(&g_bar1); }
#endif

__device__ __forceinline__ void tp_issue(u32 *sb, const u32 *eb, u32 n, u32 c, u32 tid) {      /* copy chunk c of the bin into buffer c & 1 (16-byte copies, the last may run past n inside the bin's cap) */
    const u32 w0 = c * TILE_PIPE_CH;
    const u32 cn = (n - w0 < TILE_PIPE_CH) ? n - w0 : TILE_PIPE_CH;
    u32 *dst = sb + (c & 1u) * TILE_PIPE_CH;
    for (u32 v = tid; v < (cn + 3u) / 4u; v += TILE_PIPE_AT) tp_cp16(dst + 4u * v, eb + w0 + 4u * v);
}

extern "C" __global__ void TILE_LB s200g_tile_pipe(const u32 *U, int row0, const uint4 *TABT, int nS, const u32 *gcnt, const u32 *bins, u32 cap, u32 *bits) {
    S200G_DYNSHARED(u32, bm);
    u32 *sb = bm + TILE_WORDS;
    const int rr = blockIdx.x;
    const int tile = blockIdx.y;
    const u32 tid = threadIdx.x;
    const u32 bin = rr * NTILES + tile;
    u32 n = gcnt[bin];
    if (gcnt[NBINS] != 0u) n = 0u;
    const u32 *eb = bins + (size_t)bin * cap;
    const u32 nch = (n + TILE_PIPE_CH - 1u) / TILE_PIPE_CH;
    if (tid < TILE_PIPE_AT) {                                           /* the first two chunks are on their way before the bitmap is even initialised */
        if (nch > 0u) { tp_issue(sb, eb, n, 0u, tid); tp_commit(); }
        if (nch > 1u) { tp_issue(sb, eb, n, 1u, tid); tp_commit(); }
    }
    for (u32 i = tid; i < TILE_WORDS; i += blockDim.x) bm[i] = 0xFFFFFFFFu;
    __syncthreads();
    if (tid < TILE_PIPE_AT) {
        for (u32 c = 0; c < nch; c++) {
            if (c + 1u < nch) tp_wait1(); else tp_wait0();              /* this thread's copies of chunk c are done ... */
            tp_bar();                                                   /* ... and everybody's */
            const u32 cn = (n - c * TILE_PIPE_CH < TILE_PIPE_CH) ? n - c * TILE_PIPE_CH : TILE_PIPE_CH;
            gbig_apply_words(bm, sb + (c & 1u) * TILE_PIPE_CH, cn, tid, TILE_PIPE_AT);
            tp_bar();                                                   /* the buffer is free again */
            if (c + 2u < nch) { tp_issue(sb, eb, n, c + 2u, tid); tp_commit(); }
        }
    } else {
        const u32 q = U[row0 + rr];
        const uint4 *tab = TABT + (size_t)tile * nS;
        const int ts = (int)tid - TILE_PIPE_AT, nts = (int)blockDim.x - TILE_PIPE_AT;
        for (int pb = ts; pb < nS; pb += nts * TILE_UNROLL) {
            uint4 t[TILE_UNROLL];
            #pragma unroll
            for (int u = 0; u < TILE_UNROLL; u++) {
                const int pp = pb + u * nts;
                t[u] = tab[pp < nS ? pp : nS - 1];
            }
            u32 j[TILE_UNROLL];
            #pragma unroll
            for (int u = 0; u < TILE_UNROLL; u++) {
                const u32 s = t[u].x;
                u32 a = q * t[u].y - __umulhi(q, t[u].z) * s;
                if (a >= s) a -= s;
                u32 jj = a + s - t[u].w;
                if (jj >= s) jj -= s;
                j[u] = (pb + u * nts < nS) ? jj : (u32)TILE_BITS;
            }
            #pragma unroll
            for (int u = 0; u < TILE_UNROLL; u++) {
                const u32 s = t[u].x;
                for (u32 jj = j[u]; jj < TILE_BITS; jj += s) atomicAnd(&bm[jj >> 5], __funnelshift_l(0xFFFFFFFEu, 0xFFFFFFFEu, jj));
            }
        }
    }
    __syncthreads();
    u32 *dst = bits + (size_t)(row0 + rr) * (KS / 32u) + (size_t)tile * TILE_WORDS;
    for (u32 i = tid; i < TILE_WORDS; i += blockDim.x) dst[i] = bm[i];
}
#endif

