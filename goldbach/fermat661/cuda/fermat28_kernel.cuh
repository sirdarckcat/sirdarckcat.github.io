/* fermat28_kernel.cuh -- the kernel around fm28_step: one thread tests n = CQ[idx] + M * k for the base-2 Fermat property.
 *
 * Same arguments and limb layout as gpu_fermat.py's fermat2: CQ rows and Mv are 21 little-endian u32 limbs, k is a u32,
 * out[t] = 1 iff 2^(n-1) = 1 (mod n).  Valid for odd n with 2^642 <= n < 2^668 (out[t] = 2 is written for any other n).
 *
 * Method (the construction of goldbach/fscan/fm_common.h): R = 2^672, t = bits(n) - 6 steps of y -> 2^b y^2 / R, where the
 * start value is y = 2^(672-c), c = ceil((n + 671) / 2^t), and b runs through the t bits of c 2^t - (n + 671), most
 * significant first; then y = 2^(1-n) mod n, which is 1 exactly when n is a base-2 probable prime.  No Montgomery
 * conversion, no R mod n.  All values stay below 4n (see FERMAT28.md), so a step needs no compare and subtract.
 */
#define L32 21
#define NL 24
#ifndef MASK28
#define MASK28 0x0FFFFFFFu
#endif
#define RB 672

__device__ __forceinline__ u32 fm28_inv_neg28(u32 lo) {          /* -lo^-1 mod 2^28, lo odd */
    u32 x = (3u * lo) ^ 2u;
    x *= 2u - lo * x; x *= 2u - lo * x; x *= 2u - lo * x;
    return (0u - x) & MASK28;
}

__device__ __forceinline__ int fm28_ge(const u32 *a, const u32 *b) {     /* a >= b, 24 limbs */
    int ge = 1, decided = 0;
    #pragma unroll
    for (int i = NL - 1; i >= 0; i--) {
        int gt = a[i] > b[i], lt = a[i] < b[i];
        ge = decided ? ge : (gt ? 1 : (lt ? 0 : 1));
        decided = decided | gt | lt;
    }
    return ge;
}
__device__ __forceinline__ void fm28_sub(u32 *a, const u32 *b) {         /* a -= b, a >= b */
    u32 br = 0;
    #pragma unroll
    for (int i = 0; i < NL; i++) {
        u32 v = a[i] - b[i] - br;
        br = (v >> 31) & 1u;
        a[i] = v & MASK28;
    }
}

extern "C" __global__ void fermat28(const u32 *CQ, const u32 *Mv, const int *idx, const u32 *kv,
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
    const int t = bn - 6;
    /* limbs of 28 bits */
    u32 n[NL];
    #pragma unroll
    for (int i = 0; i < NL; i++) {
        const int p = 28 * i, w = p >> 5, b = p & 31;
        u32 v = n32[w] >> b;
        if (b > 4 && w + 1 < L32) v |= n32[w + 1] << (32 - b);
        n[i] = v & MASK28;
    }
    const u32 np = fm28_inv_neg28(n32[0]);
    /* E = n + 671, c = ceil(E / 2^t), B = c 2^t - E (0 <= B < 2^t), aligned so that its bit t-1 is bit 671 */
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
    const u32 c = (clo | chi) + (rem != 0);                      /* 32 <= c <= 65 */
    u32 bt[L32];
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
        const int sh = RB - t, ws = sh >> 5, bs = sh & 31;         /* 9 .. 36: shift by 0 or 1 whole words, then bs bits */
        #pragma unroll
        for (int j = 0; j < L32; j++) {
            const u32 lo = ws ? (j > 0 ? Bw[j - 1] : 0u) : Bw[j];
            const u32 hi = ws ? (j > 1 ? Bw[j - 2] : 0u) : (j > 0 ? Bw[j - 1] : 0u);
            bt[j] = bs ? ((lo << bs) | (hi >> (32 - bs))) : lo;
        }
    }
    /* start value 2^(672 - c) */
    u32 x[NL];
    {
        const int e = RB - (int)c, ei = e / 28, eb = e - 28 * ei;
        #pragma unroll
        for (int i = 0; i < NL; i++) x[i] = (i == ei) ? (1u << eb) : 0u;
    }
    int s = 0;
    for (int w = L32 - 1; w >= 0 && s < t; w--) {
        u32 cur = bt[w];
        #pragma unroll 1
        for (int i = 0; i < 32 && s < t; i++, s++) {
            const u32 b = cur >> 31;
            cur <<= 1;
            fm28_step(x, n, np, b);
        }
    }
#ifdef FM28_DEBUG
    for (int i = 0; i < NL; i++) fm28_dbg[(size_t)tid * NL + i] = x[i];       /* the residue before the reduction (CPU test only) */
#endif
#ifdef FM28_REDUNDANT
    {                                                             /* the steps leave limbs below 2^29: one carry chain brings them below 2^28 */
        u32 cy = 0;
        #pragma unroll
        for (int i = 0; i < NL; i++) { const u32 v = x[i] + cy; x[i] = v & MASK28; cy = v >> 28; }
    }
#endif
    /* y < 4n; reduce and compare with 1 */
    u32 n2[NL];
    {
        u32 cy = 0;
        #pragma unroll
        for (int i = 0; i < NL; i++) { u32 v = (n[i] << 1) + cy; n2[i] = v & MASK28; cy = v >> 28; }
    }
    if (fm28_ge(x, n2)) fm28_sub(x, n2);                          /* y < 4n: 2n, then n */
    if (fm28_ge(x, n)) fm28_sub(x, n);
    int one = (x[0] == 1u);
    #pragma unroll
    for (int i = 1; i < NL; i++) one &= (x[i] == 0u);
    out[tid] = (unsigned char)one;
}
