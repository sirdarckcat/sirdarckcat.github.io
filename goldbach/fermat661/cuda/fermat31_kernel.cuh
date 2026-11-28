/* fermat31_kernel.cuh -- the kernel around fm31_step (22 limbs of 31 bits, R = 2^682; or 23 limbs of 30 bits, R = 2^690).
 *
 * Same arguments and limb layout as fermat28 and gpu_fermat.py's fermat2: CQ rows and Mv are 21 little-endian u32 limbs, k is a u32,
 * out[t] = 1 iff 2^(n-1) = 1 (mod n).  Valid for odd n with 2^642 <= n < 2^668 (out[t] = 2 is written for any other n).
 *
 * Method (as fermat28_kernel.cuh, goldbach/fscan/fm_common.h): t = bits(n) - 7 steps of y -> 2^b y^2 / R, the start value is
 * y = 2^(RB-c), c = ceil((n + RB - 1) / 2^t) in [64, 130], and b runs through the t bits of c 2^t - (n + RB - 1), most significant
 * first; then y = 2^(1-n) mod n, which is 1 exactly when n is a base-2 probable prime.  (R is larger than 2^672, so one more
 * squaring is folded into the start value than in fermat28 (t = bits - 6 there): the start value must stay below 4n, i.e.
 * RB - c <= bits(n) + 1, which fails for c = 32 at RB = 682 and bits(n) = 642.)  All values stay below 4n; in fact below
 * 2.01 n, because 16 n < R with room to spare.  The step file (gen_fermat31.py) must be put in front of this one: it defines
 * FM31_W, FM31_NL, FM31_MASK and fm31_step.
 */
#define L32 21
#define NL FM31_NL
#define MASKW FM31_MASK
#define RB (FM31_W * FM31_NL)
#define BW 22                            /* words of the exponent buffer: 704 bits >= RB */
#define EXPSHIFT 7                       /* t = bits(n) - EXPSHIFT */

__device__ __forceinline__ int fm31_ge(const u32 *a, const u32 *b) {     /* a >= b, NL limbs */
    int ge = 1, decided = 0;
    #pragma unroll
    for (int i = NL - 1; i >= 0; i--) {
        int gt = a[i] > b[i], lt = a[i] < b[i];
        ge = decided ? ge : (gt ? 1 : (lt ? 0 : 1));
        decided = decided | gt | lt;
    }
    return ge;
}
__device__ __forceinline__ void fm31_sub(u32 *a, const u32 *b) {         /* a -= b, a >= b */
    u32 br = 0;
    #pragma unroll
    for (int i = 0; i < NL; i++) {
        u32 v = a[i] - b[i] - br;
        br = v >> 31;                                              /* limbs are below 2^31: a - b - br is in (-2^31 - 1, 2^31) */
        a[i] = v & MASKW;
    }
}

extern "C" __global__ void fermat31(const u32 *CQ, const u32 *Mv, const int *idx, const u32 *kv,
                                    unsigned char *out, int T) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= T) return;
    const u32 *cq = CQ + (size_t)idx[tid] * L32;
    const u32 k = kv[tid];
    /* n = cq + M k, 21 limbs of 32 bits */
    u32 n32[L32];
    {
        u64 c = 0;
        #pragma unroll
        for (int j = 0; j < L32; j++) { u64 s = (u64)Mv[j] * k + cq[j] + c; n32[j] = (u32)s; c = s >> 32; }
    }
    int bn = 0;
    #pragma unroll
    for (int j = 0; j < L32; j++) if (n32[j]) bn = 32 * j + 32 - __clz(n32[j]);
    if (bn < 642 || bn > 668 || !(n32[0] & 1u)) { out[tid] = 2; return; }
    const int t = bn - EXPSHIFT;
    /* limbs of FM31_W bits */
    u32 n[NL];
    #pragma unroll
    for (int i = 0; i < NL; i++) {
        const int p = FM31_W * i, w = p >> 5, b = p & 31;
        u32 v = n32[w] >> b;
        if (b > 32 - FM31_W && w + 1 < L32) v |= n32[w + 1] << (32 - b);
        n[i] = v & MASKW;
    }
    /* -n^-1 mod 2^32 (only the low FM31_W bits are used): three Newton steps from the 5-bit seed */
    u32 np;
    {
        u32 x = (3u * n32[0]) ^ 2u;
        x *= 2u - n32[0] * x; x *= 2u - n32[0] * x; x *= 2u - n32[0] * x;
        np = 0u - x;
    }
    /* E = n + RB - 1, c = ceil(E / 2^t) (7 bits + 1), B = c 2^t - E (0 <= B < 2^t), aligned so that its bit t-1 is bit 32 BW - 1 */
    u32 E[L32];
    {
        u32 cr = RB - 1;
        #pragma unroll
        for (int j = 0; j < L32; j++) { u32 v = n32[j] + cr; cr = v < cr; E[j] = v; }
    }
    const int tw = t >> 5, tb = t & 31;
    u32 clo = 0, chi = 0, rem = 0;
    #pragma unroll
    for (int j = 0; j < L32; j++) {
        if (j == tw) {
            clo = E[j] >> tb;
            chi = (tb && j + 1 < L32) ? E[j + 1] << (32 - tb) : 0u;
            rem |= tb ? (E[j] & ((1u << tb) - 1u)) : 0u;
        }
        if (j < tw) rem |= E[j];
    }
    const u32 c = (clo | chi) + (rem != 0);                      /* 64 <= c <= 130 */
    u32 bt[BW];
    {
        const u32 low = c << tb, high = tb ? c >> (32 - tb) : 0u;
        u32 br = 0, Bw[L32];
        #pragma unroll
        for (int j = 0; j < L32; j++) {
            const u32 cw = (j == tw) ? low : ((j == tw + 1) ? high : 0u);
            const u32 v = cw - E[j] - br;
            br = (cw < E[j]) | ((cw == E[j]) & br);
            Bw[j] = v;
        }
        const int sh = 32 * BW - t, ws = sh >> 5, bs = sh & 31;     /* 43 .. 69: shift by 1 or 2 whole words, then bs bits */
        #pragma unroll
        for (int j = 0; j < BW; j++) {
            const int j0 = j - ws, j1 = j - ws - 1;
            const u32 lo = (j0 >= 0 && j0 < L32) ? Bw[j0] : 0u;
            const u32 hi = (j1 >= 0 && j1 < L32) ? Bw[j1] : 0u;
            bt[j] = bs ? ((lo << bs) | (hi >> (32 - bs))) : lo;
        }
    }
    /* start value 2^(RB - c) */
    u32 x[NL];
    {
        const int e = RB - (int)c, ei = e / FM31_W, eb = e - FM31_W * ei;
        #pragma unroll
        for (int i = 0; i < NL; i++) x[i] = (i == ei) ? (1u << eb) : 0u;
    }
    int s = 0;
    for (int w = BW - 1; w >= 0 && s < t; w--) {
        u32 cur = bt[w];
        #pragma unroll 1
        for (int i = 0; i < 32 && s < t; i++, s++) {
            const u32 b = cur >> 31;
            cur <<= 1;
            fm31_step(x, n, np, b);
        }
    }
#ifdef FM31_DEBUG
    for (int i = 0; i < NL; i++) fm31_dbg[(size_t)tid * NL + i] = x[i];       /* the residue before the reduction (CPU test only) */
#endif
    /* y < 4n; reduce and compare with 1 */
    u32 n2[NL];
    {
        u32 cy = 0;
        #pragma unroll
        for (int i = 0; i < NL; i++) { u32 v = (n[i] << 1) + cy; n2[i] = v & MASKW; cy = v >> FM31_W; }
    }
    if (fm31_ge(x, n2)) fm31_sub(x, n2);                          /* y < 4n: 2n, then n */
    if (fm31_ge(x, n)) fm31_sub(x, n);
    int one = (x[0] == 1u);
    #pragma unroll
    for (int i = 1; i < NL; i++) one &= (x[i] == 0u);
    out[tid] = (unsigned char)one;
}
