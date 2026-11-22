"""Batched base-2 Fermat tests on the GPU, version 3: dedicated squaring and lazy Montgomery reduction.

Same contract and interface as gpu_fermat.py (Tester3(N0, M, U).test(idx, k) -> uint8 flags, out = 1 iff
2^(n-1) == 1 (mod n) for n = (N0 - q_idx) + k*M), with one more precondition: n < 2^(32L - 7), so that
16n < R = 2^(32L). Below 10^200, n < 2^664.4, inside 2^665 = 2^(32*21 - 7).

Per exponent bit, against gpu_fermat.py's kernel:
- squaring: x^2 with the products x_i*x_j (i < j) once, doubled, plus the diagonal: L(L+1)/2 = 231 products
  instead of L^2 = 441; then Montgomery reduction of the 2L-limb square (L^2 products, as before);
- lazy reduction: no compare-and-subtract after a squaring or a doubling. Invariant: x < 4n before a
  squaring, x < 2n after it (x^2/R + n < 16n^2/R + n < 2n because 16n < R), x < 4n after a doubling.
At the end x (< 4n, congruent to 2^(n-1) R) is reduced once more by REDC with a zero upper half, giving
r <= n congruent to 2^(n-1); r is brought below n and compared with 1.
"""
import numpy as np
import cupy as cp

SRC = r'''
typedef unsigned int u32;
typedef unsigned long long u64;
#define L LIMBS

/* x <- REDC(x*x) = x^2 R^-1 mod n up to a multiple of n: for x < 4n the result is < 2n (16n < R). */
__device__ __forceinline__ void mont_sqr3(u32 *x, const u32 *n, u32 ninv) {
    u32 T[2 * L];
    #pragma unroll
    for (int i = 0; i < 2 * L; i++) T[i] = 0;
    /* off-diagonal products, each once */
    #pragma unroll
    for (int i = 0; i < L - 1; i++) {
        u64 c = 0; u32 xi = x[i];
        #pragma unroll
        for (int j = i + 1; j < L; j++) { u64 s = (u64)T[i + j] + (u64)xi * x[j] + c; T[i + j] = (u32)s; c = s >> 32; }
        T[i + L] = (u32)c;
    }
    /* double them */
    u32 top = 0;
    #pragma unroll
    for (int k = 0; k < 2 * L; k++) { u32 v = T[k]; T[k] = (v << 1) | top; top = v >> 31; }
    /* add the diagonal x_i^2 at 2i */
    {
        u64 c = 0;
        #pragma unroll
        for (int i = 0; i < L; i++) {
            u64 s = (u64)T[2 * i] + (u64)x[i] * x[i] + c; T[2 * i] = (u32)s; c = s >> 32;
            s = (u64)T[2 * i + 1] + c; T[2 * i + 1] = (u32)s; c = s >> 32;
        }
    }
    /* Montgomery reduction of the 2L-limb T: L rounds, each makes T[i] zero */
    u32 hi = 0;
    #pragma unroll
    for (int i = 0; i < L; i++) {
        u32 m = T[i] * ninv;
        u64 c = 0;
        #pragma unroll
        for (int j = 0; j < L; j++) { u64 s = (u64)T[i + j] + (u64)m * n[j] + c; T[i + j] = (u32)s; c = s >> 32; }
        u64 s = (u64)T[i + L] + c + hi; T[i + L] = (u32)s; hi = (u32)(s >> 32);
    }
    #pragma unroll
    for (int j = 0; j < L; j++) x[j] = T[L + j];      /* < 2n < R, so hi == 0 here */
}

/* x <- 2x without reduction (x < 2n gives 2x < 4n < R) */
__device__ __forceinline__ void dbl_lazy(u32 *x) {
    u32 carry = 0;
    #pragma unroll
    for (int j = 0; j < L; j++) { u32 v = x[j]; x[j] = (v << 1) | carry; carry = v >> 31; }
}

/* exact x <- 2x mod n for x < n (setup only) */
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

/* x <- x - n if x >= n */
__device__ __forceinline__ void cond_sub(u32 *x, const u32 *n) {
    int ge = 1;
    for (int j = L - 1; j >= 0; j--) { if (x[j] != n[j]) { ge = x[j] > n[j]; break; } }
    if (ge) { u64 br = 0;
        #pragma unroll
        for (int j = 0; j < L; j++) { u64 d = (u64)x[j] - n[j] - br; x[j] = (u32)d; br = (d >> 63) & 1; } }
}

extern "C" __global__ void fermat3(const u32 *CQ, const u32 *Mv, const int *idx, const u32 *kv,
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
    for (int i = 0; i < 32 * L; i++) dbl_mod(x, n);            /* x = R mod n, exactly */
    int top = L - 1;
    while (top > 0 && n[top] == 0) top--;
    int b = 31 - __clz(n[top]);
    dbl_mod(x, n);                                             /* 2R mod n: the top bit of n - 1 */
    for (int w = top; w >= 0; w--) {
        u32 word = n[w];
        if (w == 0) word &= ~1u;                               /* n odd: n - 1 clears bit 0 */
        int start = (w == top) ? b - 1 : 31;
        for (int i = start; i >= 0; i--) {
            mont_sqr3(x, n, ninv);                             /* x < 4n -> x < 2n */
            if ((word >> i) & 1u) dbl_lazy(x);                 /* x < 2n -> x < 4n */
        }
    }
    /* r = REDC(x) = x R^-1 mod n (up to n): T = (x, 0), r < (4n + R n)/R < n + 1 */
    {
        u32 T[2 * L];
        #pragma unroll
        for (int j = 0; j < L; j++) { T[j] = x[j]; T[L + j] = 0; }
        u32 hi = 0;
        #pragma unroll
        for (int i = 0; i < L; i++) {
            u32 m = T[i] * ninv;
            u64 cc = 0;
            #pragma unroll
            for (int j = 0; j < L; j++) { u64 s = (u64)T[i + j] + (u64)m * n[j] + cc; T[i + j] = (u32)s; cc = s >> 32; }
            u64 s = (u64)T[i + L] + cc + hi; T[i + L] = (u32)s; hi = (u32)(s >> 32);
        }
        #pragma unroll
        for (int j = 0; j < L; j++) x[j] = T[L + j];
    }
    cond_sub(x, n);                                            /* r <= n -> r < n (r == n only if x == 0 mod n) */
    int eq = (x[0] == 1u);
    #pragma unroll
    for (int j = 1; j < L; j++) eq &= (x[j] == 0u);
    out[t] = (unsigned char)eq;
}
'''

_K = {}


def kernel(limbs):
    if limbs not in _K:
        _K[limbs] = cp.RawKernel(f"#define LIMBS {limbs}\n" + SRC, "fermat3")
    return _K[limbs]


def to_limbs(x, limbs):
    return np.frombuffer(int(x).to_bytes(4 * limbs, "little"), dtype=np.uint32)


class Tester3:
    """As gpu_fermat.Tester; n_max is the largest n the caller will test (must be < 2^(32*limbs - 7))."""
    def __init__(self, N0, M, U, limbs=21, n_max=None):
        self.L = limbs
        if n_max is not None:
            assert int(n_max) < 1 << (32 * limbs - 7), "lazy reduction needs 16n < 2^(32L)"
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
