/* CPU build of gbig_kernels.cuh: every CTA is run by blockDim.x pthreads with a real barrier for __syncthreads, atomics are GCC atomics.
   Used by test_gbig.py to check the kernel source bit for bit against a brute-force reference. */
#include <cstdint>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <pthread.h>
#define __global__
#define __device__
#define __forceinline__ inline __attribute__((always_inline))
#define __shared__ static
static inline unsigned __umulhi(unsigned a, unsigned b) { return (unsigned)(((unsigned long long)a * b) >> 32); }
static inline unsigned atomicAnd(unsigned *p, unsigned v) { return __atomic_fetch_and(p, v, __ATOMIC_RELAXED); }
static inline unsigned atomicAdd(unsigned *p, unsigned v) { return __atomic_fetch_add(p, v, __ATOMIC_RELAXED); }
struct uint4 { unsigned x, y, z, w; };
struct dim_t { unsigned x, y; };
static thread_local dim_t threadIdx;
static dim_t blockIdx, blockDim;
static pthread_barrier_t g_bar;
static unsigned char *g_dyn;
static void __syncthreads() { pthread_barrier_wait(&g_bar); }
static inline unsigned min(unsigned a, unsigned b) { return a < b ? a : b; }     /* CUDA's min(unsigned, unsigned) (GEN_MINRED) */
/* the shuffle of the CPU emulation: every thread of the CTA calls it at the same point (a CTA barrier is then a valid warp barrier) */
static unsigned g_shfl[1024];
static inline unsigned __shfl_up_sync(unsigned, unsigned v, unsigned d) {
    g_shfl[threadIdx.x] = v; __syncthreads();
    const unsigned lane = threadIdx.x & 31u, r = (lane >= d) ? g_shfl[threadIdx.x - d] : v;
    __syncthreads();
    return r;
}
#define S200G_DYNSHARED(type, name) type *name = (type *)g_dyn
/* GEN_ONEPASS: CTAs that used the overflow list, CTAs that took the fallback, overflow entries (read by test_gbig.py to see that every path ran) */
static unsigned long long g_1p[3];
#define GEN1P_STAT(n, fb) { if ((n) > 0) __atomic_fetch_add(&g_1p[0], 1ull, __ATOMIC_RELAXED); if (fb) __atomic_fetch_add(&g_1p[1], 1ull, __ATOMIC_RELAXED); __atomic_fetch_add(&g_1p[2], (unsigned long long)(n), __ATOMIC_RELAXED); }
#include "gbig_kernels.cuh"
extern "C" void cpu_1p_stats(unsigned long long *out) { for (int i = 0; i < 3; i++) { out[i] = g_1p[i]; g_1p[i] = 0; } }

typedef void (*kfn)(void *);
struct launch_t { kfn f; void *args; unsigned tid; };
static void *thr(void *a) { launch_t *l = (launch_t *)a; threadIdx.x = l->tid; l->f(l->args); return nullptr; }
static void run_grid(unsigned grid, unsigned block, size_t dyn_bytes, kfn f, void *args) {
    g_dyn = (unsigned char *)aligned_alloc(64, (dyn_bytes + 63) / 64 * 64 + 64);
    blockDim.x = block;
    for (unsigned b = 0; b < grid; b++) {
        blockIdx.x = b;
        pthread_barrier_init(&g_bar, nullptr, block);
        pthread_t *th = (pthread_t *)malloc(sizeof(pthread_t) * block);
        launch_t *l = (launch_t *)malloc(sizeof(launch_t) * block);
        for (unsigned t = 0; t < block; t++) { l[t] = {f, args, t}; pthread_create(&th[t], nullptr, thr, &l[t]); }
        for (unsigned t = 0; t < block; t++) pthread_join(th[t], nullptr);
        pthread_barrier_destroy(&g_bar);
        free(th); free(l);
    }
    free(g_dyn);
}
struct gen_args { const u32 *U; const uint4 *TAB; int nP, row0, nrows; u32 cap; u32 *gcnt; u32 *bins; };
static void gen_tramp(void *a) { gen_args *x = (gen_args *)a; gbig_gen(x->U, x->TAB, x->nP, x->row0, x->nrows, x->cap, x->gcnt, x->bins); }
extern "C" void cpu_gen(const u32 *U, const uint4 *TAB, int nP, int row0, int nrows, u32 cap, u32 *gcnt, u32 *bins, int threads) {
    gen_args a{U, TAB, nP, row0, nrows, cap, gcnt, bins};
    const int per = threads * PPT;
    run_grid((nP + per - 1) / per, threads, 0, gen_tramp, &a);
}
struct apply_args { const u32 *gcnt, *bins; u32 cap; u32 *out; };
static void apply_tramp(void *a) { apply_args *x = (apply_args *)a; gbig_apply(x->gcnt, x->bins, x->cap, x->out); }
extern "C" void cpu_apply(int nbins, const u32 *gcnt, const u32 *bins, u32 cap, u32 *out, int threads) {
    apply_args a{gcnt, bins, cap, out};
    run_grid(nbins, threads, (size_t)TILE_WORDS * 4, apply_tramp, &a);
}
struct gen_st_args { const u32 *U; const uint4 *TAB; const int *pstart; int row0, nrows; u32 cap; u32 *gcnt; u32 *bins; };
static void gen_st_tramp(void *a) { gen_st_args *x = (gen_st_args *)a; gbig_gen_st(x->U, x->TAB, x->pstart, x->row0, x->nrows, x->cap, x->gcnt, x->bins); }
/* the staged kernel has a 2-D grid (chunks, row pairs): the emulation runs the CTAs one after the other */
extern "C" void cpu_gen_st(const u32 *U, const uint4 *TAB, const int *pstart, int nchunks, int row0, int nrows, u32 cap, u32 *gcnt, u32 *bins, int threads) {
    gen_st_args a{U, TAB, pstart, row0, nrows, cap, gcnt, bins};
    const int ny = (nrows + RCTA - 1) / RCTA;
#if GEN_ORDER
    for (int c = 0; c < nchunks; c++) {                                 /* grid (row slices, chunks): blockIdx.x = slice, blockIdx.y = chunk */
        blockIdx.y = c;
        run_grid(ny, threads, 0, gen_st_tramp, &a);
    }
#else
    for (int y = 0; y < ny; y++) {
        blockIdx.y = y;
        run_grid(nchunks, threads, 0, gen_st_tramp, &a);
    }
#endif
}
extern "C" int cpu_nbins() { return NBINS; }
extern "C" int cpu_ntiles() { return NTILES; }
extern "C" int cpu_tile_words() { return TILE_WORDS; }
extern "C" int cpu_rg() { return RG; }
