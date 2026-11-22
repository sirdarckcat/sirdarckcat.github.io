"""Batched base-2 Fermat tests on the GPU for campaign3's candidates n = cq[i] + k*M.

One thread per test: n is built from limbs of cq[i] = N0 - q_i and M times the 32-bit k, then
2^(n-1) mod n by left-to-right Montgomery squaring (CIOS, LIMBS 32-bit words; multiplying by the
base 2 is a doubling in the Montgomery domain). out[t] = 1 iff 2^(n-1) == 1 (mod n).
Requires n odd and n < 2^(32*LIMBS) (campaign3: n < 2^661, LIMBS = 21).
"""
import numpy as np
import cupy as cp

SRC = r'''
typedef unsigned int u32;
typedef unsigned long long u64;
#define L LIMBS

__device__ __forceinline__ void mont_sqr(u32 *x, const u32 *n, u32 ninv) {
    u32 t[L + 2];
    #pragma unroll
    for (int i = 0; i < L + 2; i++) t[i] = 0;
    for (int i = 0; i < L; i++) {
        u64 c = 0; u32 ai = x[i];
        #pragma unroll
        for (int j = 0; j < L; j++) { u64 s = (u64)t[j] + (u64)ai * x[j] + c; t[j] = (u32)s; c = s >> 32; }
        u64 s = (u64)t[L] + c; t[L] = (u32)s; t[L + 1] = (u32)(s >> 32);
        u32 m = t[0] * ninv;
        s = (u64)t[0] + (u64)m * n[0]; c = s >> 32;
        #pragma unroll
        for (int j = 1; j < L; j++) { s = (u64)t[j] + (u64)m * n[j] + c; t[j - 1] = (u32)s; c = s >> 32; }
        s = (u64)t[L] + c; t[L - 1] = (u32)s;
        t[L] = t[L + 1] + (u32)(s >> 32);
    }
    int ge = t[L] != 0;
    if (!ge) { ge = 1; for (int j = L - 1; j >= 0; j--) { if (t[j] != n[j]) { ge = t[j] > n[j]; break; } } }
    if (ge) { u64 br = 0;
        #pragma unroll
        for (int j = 0; j < L; j++) { u64 d = (u64)t[j] - n[j] - br; x[j] = (u32)d; br = (d >> 63) & 1; } }
    else {
        #pragma unroll
        for (int j = 0; j < L; j++) x[j] = t[j]; }
}

__device__ __forceinline__ void dbl_mod(u32 *x, const u32 *n) {
    u32 carry = 0;
    #pragma unroll
    for (int j = 0; j < L; j++) { u32 v = x[j]; x[j] = (v << 1) | carry; carry = v >> 31; }
    int ge = carry;
    if (!ge) { ge = 1; for (int j = L - 1; j >= 0; j--) { if (x[j] != n[j]) { ge = x[j] > n[j]; break; } } }
    if (ge) { u64 br = 0;
        #pragma unroll
        for (int j = 0; j < L; j++) { u64 d = (u64)x[j] - n[j] - br; x[j] = (u32)d; br = (d >> 63) & 1; } }
}

extern "C" __global__ void fermat2(const u32 *CQ, const u32 *Mv, const int *idx, const u32 *kv,
                                   unsigned char *out, int T) {
    int t = blockIdx.x * blockDim.x + threadIdx.x;
    if (t >= T) return;
    u32 n[L];
    const u32 *cq = CQ + (size_t)idx[t] * L;
    u32 k = kv[t];
    u64 c = 0;
    #pragma unroll
    for (int j = 0; j < L; j++) { u64 s = (u64)Mv[j] * k + cq[j] + c; n[j] = (u32)s; c = s >> 32; }
    u32 inv = n[0];
    #pragma unroll
    for (int i = 0; i < 5; i++) inv *= 2u - n[0] * inv;       /* n[0] * inv == 1 (mod 2^32) */
    u32 ninv = 0u - inv;
    u32 x[L];
    #pragma unroll
    for (int j = 0; j < L; j++) x[j] = 0;
    x[0] = 1;
    for (int i = 0; i < 32 * L; i++) dbl_mod(x, n);            /* x = R mod n = Montgomery 1 */
    u32 one[L];
    #pragma unroll
    for (int j = 0; j < L; j++) one[j] = x[j];
    int top = L - 1;
    while (top > 0 && n[top] == 0) top--;
    int b = 31 - __clz(n[top]);
    dbl_mod(x, n);                                             /* 2^1 for the top bit of n-1 */
    for (int w = top; w >= 0; w--) {
        u32 word = n[w];
        if (w == 0) word &= ~1u;                               /* n odd: n-1 clears bit 0 */
        int start = (w == top) ? b - 1 : 31;
        for (int i = start; i >= 0; i--) {
            mont_sqr(x, n, ninv);
            if ((word >> i) & 1u) dbl_mod(x, n);
        }
    }
    int eq = 1;
    #pragma unroll
    for (int j = 0; j < L; j++) eq &= (x[j] == one[j]);
    out[t] = (unsigned char)eq;
}
'''

_K = {}


def kernel(limbs):
    if limbs not in _K:
        _K[limbs] = cp.RawKernel(f"#define LIMBS {limbs}\n" + SRC, "fermat2")
    return _K[limbs]


def to_limbs(x, limbs):
    return np.frombuffer(int(x).to_bytes(4 * limbs, "little"), dtype=np.uint32)


class Tester:
    """Holds one spec's cq[i] = N0 - q_i and M on the GPU; test(idx, k) -> uint8 flags (on the GPU)."""
    def __init__(self, N0, M, U, limbs=21):
        self.L = limbs
        self.cq = cp.asarray(np.stack([to_limbs(int(N0) - int(q), limbs) for q in U]))
        self.M = cp.asarray(to_limbs(int(M), limbs))
        self.k = kernel(limbs)

    def test(self, idx, kv, threads=128):
        idx = cp.asarray(idx, dtype=cp.int32)
        kv = cp.asarray(kv, dtype=cp.uint32)
        T = int(idx.size)
        out = cp.empty(T, dtype=cp.uint8)
        if T:
            self.k(((T + threads - 1) // threads,), (threads,), (self.cq, self.M, idx, kv, out, np.int32(T)))
        return out
