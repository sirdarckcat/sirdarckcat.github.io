/* gsieve_kernels.cuh -- the sieve, the counts, the selection and the survivor lists of search.run_block on a GPU.
 *
 * Compile-time: KLOG (a window sieves K = 2^KLOG members), LLOG (selection blocks of L = 2^LLOG members, LLOG <= KLOG, L <= 2^19),
 * NTHREADS is the CTA size of every kernel (a power of two, 64..1024).
 *
 *   s200g_sieve : one CTA per row r; the K-bit alive map of the row in shared memory; for every sieve prime s the first offset
 *                 j = ((q - N0) / M - k0) mod s with a Barrett reduction (mu = floor((2^64-1) / s)), then
 *                 atomicAnd clears j, j + s, ... < K.  bits[r][K/32] is written once.
 *   s200g_count : one thread per 32 members; the number of alive rows of each member by a carry-save adder tree over 16 rows
 *                 and a bit-sliced counter with 12 planes (up to 4095 rows); counts u16[K].
 *   s200g_select: one CTA per block of L members: histogram of the counts, the threshold count cth and `need` of the members
 *                 with count == cth (the first ones by index), the kept members in index order, then sorted by (count, index) with a
 *                 bitonic sort of the keys (count << 20 | index): exactly np.argsort(counts, kind="stable")[:nkeep].  Also
 *                 alive_total, hm_all = sum (1-p)^count over all members, hm_kept over the kept ones.
 *   s200g_rows  : one thread per kept member: its alive rows in increasing order, from the bit matrix, to rows[offs[i] ...].
 */
typedef unsigned int u32;
typedef unsigned long long u64;
typedef unsigned short u16;
typedef long long i64;
#define KW ((1u << KLOG) / 32u)
#define BLK_MEMBERS (1u << LLOG)
#ifndef MAXKEEP_SORT
#define MAXKEEP_SORT 8192u          /* the bitonic sort is done in shared memory up to this many kept members per block */
#endif

extern "C" __global__ void s200g_sieve(const u32 *U, const u32 *S, const u32 *INV, const u64 *MU, const u32 *N0M, const u32 *KM,
                                       int nS, u32 *bits) {
    S200G_DYNSHARED(u32, bm);
    const int r = blockIdx.x;
    const u32 q = U[r];
    for (u32 i = threadIdx.x; i < KW; i += blockDim.x) bm[i] = 0xFFFFFFFFu;
    __syncthreads();
    /* the constants of the next prime are loaded before the marks of this one are made, so that their latency overlaps the marks */
    int p = threadIdx.x;
    u32 s_n = 1, inv_n = 0, n0_n = 0, km_n = 0;
    u64 mu_n = 0;
    if (p < nS) { s_n = S[p]; inv_n = INV[p]; mu_n = MU[p]; n0_n = N0M[p]; km_n = KM[p]; }
    for (; p < nS; p += blockDim.x) {
        const u32 s = s_n, inv = inv_n, n0 = n0_n, km = km_n;
        const u64 mu = mu_n;
        const int pn = p + blockDim.x;
        if (pn < nS) { s_n = S[pn]; inv_n = INV[pn]; mu_n = MU[pn]; n0_n = N0M[pn]; km_n = KM[pn]; }
        const u32 qm = q < s ? q : q % s;
        u32 d = qm + s - n0;                                     /* (q - N0) mod s */
        if (d >= s) d -= s;
        const u64 x = (u64)d * inv;                              /* (q - N0) M^-1, below s^2 < 2^54 */
        const u64 qe = __umul64hi(x, mu);                        /* floor(x / s) or one less */
        u64 a = x - qe * (u64)s;
        if (a >= s) a -= s;
        u32 j = (u32)a + s - km;                                 /* (a - k0) mod s */
        if (j >= s) j -= s;
        for (; j < (1u << KLOG); j += s) atomicAnd(&bm[j >> 5], ~(1u << (j & 31)));
    }
    __syncthreads();
    for (u32 i = threadIdx.x; i < KW; i += blockDim.x) bits[(size_t)r * KW + i] = bm[i];
}

__device__ __forceinline__ void s200g_fa(u32 a, u32 b, u32 c, u32 *s, u32 *k) { u32 t = a ^ b; *s = t ^ c; *k = (a & b) | (t & c); }

extern "C" __global__ void s200g_count(const u32 *bits, int nU, u16 *counts) {
    const u32 w = blockIdx.x * blockDim.x + threadIdx.x;
    if (w >= KW) return;
    u32 P0 = 0, P1 = 0, P2 = 0, P3 = 0, P4 = 0, P5 = 0, P6 = 0, P7 = 0, P8 = 0, P9 = 0, P10 = 0, P11 = 0;
    int r = 0;
    for (; r + 16 <= nU; r += 16) {
        u32 R[16];
        #pragma unroll
        for (int i = 0; i < 16; i++) R[i] = bits[(size_t)(r + i) * KW + w];
        u32 sa, ca, sb, cb, sc, cc, sd, cd, se, ce, t1, u1, t2, u2, v, x1, y1, x2, y2, x3, y3, p, q;
        s200g_fa(R[0], R[1], R[2], &sa, &ca); s200g_fa(R[3], R[4], R[5], &sb, &cb); s200g_fa(R[6], R[7], R[8], &sc, &cc);
        s200g_fa(R[9], R[10], R[11], &sd, &cd); s200g_fa(R[12], R[13], R[14], &se, &ce);
        s200g_fa(sa, sb, sc, &t1, &u1); s200g_fa(sd, se, R[15], &t2, &u2);
        const u32 ones = t1 ^ t2; v = t1 & t2;
        s200g_fa(ca, cb, cc, &x1, &y1); s200g_fa(cd, ce, u1, &x2, &y2); s200g_fa(u2, v, x1, &x3, &y3);
        const u32 twos = x3 ^ x2, z = x3 & x2;
        s200g_fa(y1, y2, y3, &p, &q);
        const u32 fours = p ^ z, rr = p & z;
        const u32 eights = q ^ rr, sixteens = q & rr;
        u32 a, carry, s_;
        a = P0; P0 = a ^ ones; carry = a & ones;
        s200g_fa(P1, twos, carry, &s_, &carry); P1 = s_;
        s200g_fa(P2, fours, carry, &s_, &carry); P2 = s_;
        s200g_fa(P3, eights, carry, &s_, &carry); P3 = s_;
        s200g_fa(P4, sixteens, carry, &s_, &carry); P4 = s_;
        a = P5; P5 = a ^ carry; carry = a & carry;
        a = P6; P6 = a ^ carry; carry = a & carry;
        a = P7; P7 = a ^ carry; carry = a & carry;
        a = P8; P8 = a ^ carry; carry = a & carry;
        a = P9; P9 = a ^ carry; carry = a & carry;
        a = P10; P10 = a ^ carry; carry = a & carry;
        P11 ^= carry;
    }
    for (; r < nU; r++) {
        u32 carry = bits[(size_t)r * KW + w], a;
        a = P0; P0 = a ^ carry; carry = a & carry;
        a = P1; P1 = a ^ carry; carry = a & carry;
        a = P2; P2 = a ^ carry; carry = a & carry;
        a = P3; P3 = a ^ carry; carry = a & carry;
        a = P4; P4 = a ^ carry; carry = a & carry;
        a = P5; P5 = a ^ carry; carry = a & carry;
        a = P6; P6 = a ^ carry; carry = a & carry;
        a = P7; P7 = a ^ carry; carry = a & carry;
        a = P8; P8 = a ^ carry; carry = a & carry;
        a = P9; P9 = a ^ carry; carry = a & carry;
        a = P10; P10 = a ^ carry; carry = a & carry;
        P11 ^= carry;
    }
    #pragma unroll
    for (int b = 0; b < 32; b++)
        counts[(size_t)w * 32 + b] = (u16)(((P0 >> b) & 1) | (((P1 >> b) & 1) << 1) | (((P2 >> b) & 1) << 2) | (((P3 >> b) & 1) << 3)
            | (((P4 >> b) & 1) << 4) | (((P5 >> b) & 1) << 5) | (((P6 >> b) & 1) << 6) | (((P7 >> b) & 1) << 7)
            | (((P8 >> b) & 1) << 8) | (((P9 >> b) & 1) << 9) | (((P10 >> b) & 1) << 10) | (((P11 >> b) & 1) << 11));
}

/* One CTA per block of L members.  counts: the window's u16 counts.  maxc: the number of rows.  nkeep: members kept per block
   (<= L).  keys[blk * nkeep + i] (u32, count << 20 | index in the block) sorted ascending when nkeep <= MAXKEEP_SORT, otherwise in
   (count < cth ones by index, then class cth by index) order and the caller sorts them.  stats[blk] = {alive_total, hm_all,
   hm_kept} as three doubles.  Dynamic shared memory: (maxc + 2) u32 for the histogram, then the keys (nkeep u32 rounded up to a
   power of two when sorting, else nkeep), then NTHREADS u32 for the scan. */
extern "C" __global__ void s200g_select(const u16 *counts, int maxc, int nkeep, double p_est, u32 *keys, double *stats) {
    S200G_DYNSHARED(u32, sm);
    const int nb = maxc + 2;
    u32 *hist = sm;
    u32 *kbuf = sm + ((nb + 3) & ~3);
    __shared__ u32 scan[NTHREADS];
    __shared__ u32 cth_s, need_s, nlt_s;
    __shared__ double red[3][NTHREADS];
    u32 *const kb = ((u32)nkeep <= MAXKEEP_SORT) ? kbuf : keys + (size_t)blockIdx.x * nkeep;   /* too many to sort here: straight to global */
    for (int i = threadIdx.x; i < nb; i += blockDim.x) hist[i] = 0;
    __syncthreads();
    const u16 *c16 = counts + (size_t)blockIdx.x * BLK_MEMBERS;
    for (u32 i = threadIdx.x; i < BLK_MEMBERS; i += blockDim.x) atomicAdd(&hist[c16[i]], 1u);
    __syncthreads();
    /* thread t owns the bins t, t + NTHREADS, ...: here instead contiguous runs of `per` bins for a simple scan */
    const int per = (nb + blockDim.x - 1) / blockDim.x;
    const int b0 = threadIdx.x * per, b1 = b0 + per < nb ? b0 + per : nb;
    u32 mine = 0;
    double sa = 0, sh = 0;
    const double lq = log1p(-p_est);
    for (int b = b0; b < b1; b++) { mine += hist[b]; sa += (double)b * hist[b]; sh += hist[b] * exp(lq * b); }
    red[0][threadIdx.x] = sa; red[1][threadIdx.x] = sh;
    scan[threadIdx.x] = mine;
    __syncthreads();
    /* inclusive scan of the per-thread totals (Hillis-Steele) */
    for (u32 d = 1; d < blockDim.x; d <<= 1) {
        u32 v = scan[threadIdx.x] + (threadIdx.x >= d ? scan[threadIdx.x - d] : 0u);
        __syncthreads();
        scan[threadIdx.x] = v;
        __syncthreads();
    }
    const u32 before = scan[threadIdx.x] - mine;                  /* members in the bins of the earlier threads */
    if ((u32)nkeep > before && (u32)nkeep <= before + mine) {      /* the thread whose bins contain the nkeep-th member */
        u32 cum = before;
        for (int b = b0; b < b1; b++) {
            if ((u32)nkeep <= cum + hist[b]) { cth_s = b; need_s = nkeep - cum; nlt_s = cum; break; }
            cum += hist[b];
        }
    }
    if (nkeep == 0 && threadIdx.x == 0) { cth_s = 0; need_s = 0; nlt_s = 0; }
    __syncthreads();
    {
        double hkt = 0;                                           /* the bins below cth are kept whole */
        for (int b = b0; b < b1; b++) if ((u32)b < cth_s && nkeep > 0) hkt += hist[b] * exp(lq * b);
        red[2][threadIdx.x] = hkt;
    }
    __syncthreads();
    if (threadIdx.x == 0) {                                       /* statistics: the sums over the bins */
        double a = 0, h = 0, hk = 0;
        for (u32 t = 0; t < blockDim.x; t++) { a += red[0][t]; h += red[1][t]; hk += red[2][t]; }
        if (nkeep > 0) hk += need_s * exp(lq * cth_s);
        stats[blockIdx.x * 3 + 0] = a; stats[blockIdx.x * 3 + 1] = h; stats[blockIdx.x * 3 + 2] = hk;
    }
    const u32 cth = cth_s, need = need_s, nlt = nlt_s;
    __syncthreads();
    /* the kept members in index order: all with count < cth, then the first `need` with count == cth */
    __shared__ u32 run_lt, run_eq;
    if (threadIdx.x == 0) { run_lt = 0; run_eq = 0; }
    __syncthreads();
    for (u32 base = 0; base < BLK_MEMBERS; base += blockDim.x) {
        const u32 m = base + threadIdx.x;
        const u32 c = c16[m];
        const u32 lt = nkeep > 0 && c < cth, eq = nkeep > 0 && c == cth;
        scan[threadIdx.x] = lt | (eq << 16);
        __syncthreads();
        for (u32 d = 1; d < blockDim.x; d <<= 1) {
            u32 v = scan[threadIdx.x] + (threadIdx.x >= d ? scan[threadIdx.x - d] : 0u);
            __syncthreads();
            scan[threadIdx.x] = v;
            __syncthreads();
        }
        const u32 incl = scan[threadIdx.x], excl = incl - (lt | (eq << 16));
        const u32 lpos = run_lt + (excl & 0xFFFFu), epos = run_eq + (excl >> 16);
        if (lt) kb[lpos] = (c << 20) | m;
        if (eq && epos < need) kb[nlt + epos] = (c << 20) | m;
        __syncthreads();
        if (threadIdx.x == blockDim.x - 1) { run_lt += incl & 0xFFFFu; run_eq += incl >> 16; }
        __syncthreads();
    }
    /* sort the nkeep keys ascending: bitonic network in shared memory when they fit */
    if ((u32)nkeep <= MAXKEEP_SORT && nkeep > 1) {
        u32 n2 = 1;
        while (n2 < (u32)nkeep) n2 <<= 1;
        for (u32 i = nkeep + threadIdx.x; i < n2; i += blockDim.x) kbuf[i] = 0xFFFFFFFFu;
        __syncthreads();
        for (u32 k = 2; k <= n2; k <<= 1) {
            for (u32 j = k >> 1; j > 0; j >>= 1) {
                for (u32 i = threadIdx.x; i < n2; i += blockDim.x) {
                    const u32 ixj = i ^ j;
                    if (ixj > i) {
                        const u32 a = kbuf[i], b = kbuf[ixj];
                        const int up = (i & k) == 0;
                        if ((a > b) == up) { kbuf[i] = b; kbuf[ixj] = a; }
                    }
                }
                __syncthreads();
            }
        }
    }
    if ((u32)nkeep <= MAXKEEP_SORT)
        for (int i = threadIdx.x; i < nkeep; i += blockDim.x) keys[(size_t)blockIdx.x * nkeep + i] = kbuf[i];
}

/* the alive rows of the kept members: member i (0 <= i < nsel over all blocks) has key keys[i] in block blk[i] (u32 index of the
   block in the window); offs[i] where its rows start. */
extern "C" __global__ void s200g_rows(const u32 *bits, int nU, const u32 *member, const i64 *offs, int nsel, u16 *rows) {
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= nsel) return;
    const u32 m = member[i];                                       /* index of the member in the window */
    const u32 w = m >> 5, sh = m & 31;
    i64 o = offs[i];
    for (int r = 0; r < nU; r++)
        if ((bits[(size_t)r * KW + w] >> sh) & 1u) rows[o++] = (u16)r;
}

/* N0 mod s for every sieve prime, one thread per prime (so that a new variant costs no host time): N0L = nl limbs of 32 bits (little
   endian), Barrett with the same mu = floor((2^64-1)/s) as the sieve kernel; r * 2^32 + limb < 2^59 for s < 2^27. */
extern "C" __global__ void s200g_n0m(const u32 *N0L, int nl, const u32 *S, const u64 *MU, int nS, u32 *out) {
    const int p = blockIdx.x * blockDim.x + threadIdx.x;
    if (p >= nS) return;
    const u32 s = S[p];
    const u64 mu = MU[p];
    u32 r = 0;
    for (int i = nl - 1; i >= 0; i--) {
        const u64 x = ((u64)r << 32) | N0L[i];
        const u64 qe = __umul64hi(x, mu);
        u64 rr = x - qe * (u64)s;
        if (rr >= s) rr -= s;
        r = (u32)rr;
    }
    out[p] = r;
}

/* k0 mod s for every prime (one thread each): the offsets of the window's first member in every progression. */
extern "C" __global__ void s200g_km(const u32 *S, u64 k0, int nS, u32 *out) {
    const int p = blockIdx.x * blockDim.x + threadIdx.x;
    if (p < nS) out[p] = (u32)(k0 % S[p]);
}

/* After s200g_select: from the nsel = nb * nkeep sorted keys (block by block, nkeep each) the member index in the window, k, the count
   and the CSR offsets of the survivor rows (an exclusive scan of the counts), in one CTA of NTHREADS threads (each takes a run of
   consecutive keys).  total = offs[nsel] = number of survivor rows. */
extern "C" __global__ void s200g_finalize(const u32 *keys, int nsel, int nkeep, u64 k0, u16 *cnt, u32 *member, u64 *kout, i64 *offs, i64 *total) {
    __shared__ i64 part[NTHREADS];
    const int per = (nsel + blockDim.x - 1) / blockDim.x;
    const int i0 = threadIdx.x * per, i1 = i0 + per < nsel ? i0 + per : nsel;
    i64 sum = 0;
    for (int i = i0; i < i1; i++) {
        const u32 key = keys[i];
        const u32 m = ((u32)(i / nkeep) << LLOG) + (key & 0xFFFFFu);
        cnt[i] = (u16)(key >> 20);
        member[i] = m;
        kout[i] = k0 + m;
        sum += key >> 20;
    }
    part[threadIdx.x] = sum;
    __syncthreads();
    for (u32 d = 1; d < blockDim.x; d <<= 1) {                    /* inclusive scan of the run sums */
        const i64 v = part[threadIdx.x] + (threadIdx.x >= d ? part[threadIdx.x - d] : 0);
        __syncthreads();
        part[threadIdx.x] = v;
        __syncthreads();
    }
    i64 run = part[threadIdx.x] - sum;
    for (int i = i0; i < i1; i++) { offs[i] = run; run += keys[i] >> 20; }
    if (threadIdx.x == blockDim.x - 1) { offs[nsel] = run; *total = run; }
    if (nsel == 0 && threadIdx.x == 0) { offs[0] = 0; *total = 0; }
}
