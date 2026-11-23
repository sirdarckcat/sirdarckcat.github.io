/* CPU build of the very same kernel source (fermat28_step.cuh + fermat28_kernel.cuh), one "thread" after the other. */
#include <cstdint>
#include <cstddef>
typedef unsigned int u32;
typedef unsigned long long u64;
#define __device__
#define __forceinline__ inline __attribute__((always_inline))
#define __global__
static inline int __clz(u32 x) { return __builtin_clz(x); }
struct { unsigned x; } blockIdx, blockDim, threadIdx;
#define FM28_DEBUG 1
static u32 *fm28_dbg;
#define FM28_MADN(acc, a, b) ((acc) += (u64)(u32)(a) * (u32)(b))      /* the "mulw" steps use an explicit PTX mul.wide.u32 for m_i n_j: portable here */
#ifndef STEP_FILE
#define STEP_FILE "fermat28_step.cuh"
#endif
#include STEP_FILE
#include "fermat28_kernel.cuh"
extern "C" void set_dbg(u32 *p) { fm28_dbg = p; }
extern "C" void run_cpu(const u32 *CQ, const u32 *Mv, const int *idx, const u32 *kv, unsigned char *out, int T) {
    blockDim.x = 1; blockIdx.x = 0;
    for (int t = 0; t < T; t++) { threadIdx.x = t; fermat28(CQ, Mv, idx, kv, out, T); }
}

extern "C" void step_test(const u32 *x_in, const u32 *n, u32 np, u32 b, u32 *x_out) {
    u32 x[NL], nn[NL];
    for (int i = 0; i < NL; i++) { x[i] = x_in[i]; nn[i] = n[i]; }
    fm28_step(x, nn, np, b);
    for (int i = 0; i < NL; i++) x_out[i] = x[i];
}
#ifdef FM_TOPX
extern "C" u32 inv_test(u32 lo) { return fm28_inv_neg32(lo); }
#else
extern "C" u32 inv_test(u32 lo) { return fm28_inv_neg28(lo); }
#endif
