/* CPU build of the very same step source (fermat31_step.cuh or fermat30_step.cuh from gen_fermat31.py), for the tests.  The two
   device-only pieces of the step, the PTX carry chain and mul.wide, have portable definitions here; everything else is the source
   the GPU compiles.  -DSTEP_FILE='"fermat30_step.cuh"' selects the 30-bit variant. */
#include <cstdint>
#include <cstddef>
typedef unsigned int u32;
typedef unsigned long long u64;
#define __device__
#define __forceinline__ inline __attribute__((always_inline))
#define __global__
static inline u32 __funnelshift_l(u32 lo, u32 hi, u32 s) { return (u32)((((u64)hi << 32) | lo) << (s & 31) >> 32); }
static inline u32 __funnelshift_r(u32 lo, u32 hi, u32 s) { return (u32)((((u64)hi << 32) | lo) >> (s & 31)); }
static inline void fm31_add96(u32 &s0, u32 &s1, u32 &s2, u32 glo, u32 ghi) {
    u64 t = (u64)s0 + glo; s0 = (u32)t;
    t = (u64)s1 + ghi + (t >> 32); s1 = (u32)t;
    s2 += (u32)(t >> 32);
}
#define FM31_ADD96(s0, s1, s2, glo, ghi) fm31_add96(s0, s1, s2, glo, ghi)
#define FM31_MULW(a, b) ((u64)(u32)(a) * (u32)(b))
#ifndef STEP_FILE
#define STEP_FILE "fermat31_step.cuh"
#endif
#include STEP_FILE
static inline int __clz(u32 x) { return __builtin_clz(x); }
struct { unsigned x; } blockIdx, blockDim, threadIdx;
#define FM31_DEBUG 1
static u32 *fm31_dbg;
#include "fermat31_kernel.cuh"
extern "C" void set_dbg(u32 *p) { fm31_dbg = p; }
extern "C" void run_cpu(const u32 *CQ, const u32 *Mv, const int *idx, const u32 *kv, unsigned char *out, int T) {
    blockDim.x = 1; blockIdx.x = 0;
    for (int t = 0; t < T; t++) { threadIdx.x = t; fermat31(CQ, Mv, idx, kv, out, T); }
}

extern "C" void step_test(const u32 *x_in, const u32 *n, u32 np, u32 b, u32 *x_out) {
    u32 x[FM31_NL], nn[FM31_NL];
    for (int i = 0; i < FM31_NL; i++) { x[i] = x_in[i]; nn[i] = n[i]; }
    fm31_step(x, nn, np, b);
    for (int i = 0; i < FM31_NL; i++) x_out[i] = x[i];
}
/* -n^-1 mod 2^32, n odd (Newton from the 5-bit seed (3 n) xor 2: 5 -> 10 -> 20 -> 40 bits), as in the kernel */
extern "C" u32 inv_test(u32 lo) {
    u32 x = (3u * lo) ^ 2u;
    x *= 2u - lo * x; x *= 2u - lo * x; x *= 2u - lo * x;
    return 0u - x;
}
extern "C" int limb_bits() { return FM31_W; }
extern "C" int limb_count() { return FM31_NL; }
