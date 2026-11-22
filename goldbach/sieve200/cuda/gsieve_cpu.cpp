/* CPU build of gsieve_kernels.cuh: every CTA is run by blockDim.x pthreads with a real barrier for __syncthreads, atomics are
   GCC atomics.  Used by test_gsieve.py to check the kernel source bit for bit against sieve200.c. */
#include <cstdint>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <pthread.h>
#define __global__
#define __device__
#define __forceinline__ inline __attribute__((always_inline))
#define __shared__ static
static inline unsigned long long __umul64hi(unsigned long long a, unsigned long long b) { return (unsigned long long)(((unsigned __int128)a * b) >> 64); }
static inline unsigned atomicAnd(unsigned *p, unsigned v) { return __atomic_fetch_and(p, v, __ATOMIC_RELAXED); }
static inline unsigned atomicAdd(unsigned *p, unsigned v) { return __atomic_fetch_add(p, v, __ATOMIC_RELAXED); }
struct dim_t { unsigned x; };
static thread_local dim_t threadIdx;
static dim_t blockIdx, blockDim;
static pthread_barrier_t g_bar;
static unsigned char *g_dyn;
static void __syncthreads() { pthread_barrier_wait(&g_bar); }
#define S200G_DYNSHARED(type, name) type *name = (type *)g_dyn
#ifndef KLOG
#define KLOG 12
#endif
#ifndef LLOG
#define LLOG 11
#endif
#ifndef NTHREADS
#define NTHREADS 64
#endif
#include "gsieve_kernels.cuh"

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

struct sieve_args { const u32 *U, *S, *INV; const u64 *MU; const u32 *N0M, *KM; int nS; u32 *bits; };
static void sieve_tramp(void *a) { sieve_args *x = (sieve_args *)a; s200g_sieve(x->U, x->S, x->INV, x->MU, x->N0M, x->KM, x->nS, x->bits); }
extern "C" void cpu_sieve(int nU, const u32 *U, const u32 *S, const u32 *INV, const u64 *MU, const u32 *N0M, const u32 *KM, int nS, u32 *bits) {
    sieve_args a{U, S, INV, MU, N0M, KM, nS, bits};
    run_grid(nU, NTHREADS, (size_t)KW * 4, sieve_tramp, &a);
}
struct count_args { const u32 *bits; int nU; u16 *counts; };
static void count_tramp(void *a) { count_args *x = (count_args *)a; s200g_count(x->bits, x->nU, x->counts); }
extern "C" void cpu_count(const u32 *bits, int nU, u16 *counts) {
    count_args a{bits, nU, counts};
    run_grid((KW + NTHREADS - 1) / NTHREADS, NTHREADS, 0, count_tramp, &a);
}
struct select_args { const u16 *counts; int maxc, nkeep; double p; u32 *keys; double *stats; };
static void select_tramp(void *a) { select_args *x = (select_args *)a; s200g_select(x->counts, x->maxc, x->nkeep, x->p, x->keys, x->stats); }
extern "C" void cpu_select(const u16 *counts, int maxc, int nkeep, double p_est, u32 *keys, double *stats) {
    select_args a{counts, maxc, nkeep, p_est, keys, stats};
    const unsigned nb = ((maxc + 2) + 3) & ~3u;
    unsigned n2 = 1; while (n2 < (unsigned)nkeep) n2 <<= 1;
    run_grid(1u << (KLOG - LLOG), NTHREADS, 4 * (nb + (n2 > (unsigned)nkeep ? n2 : (unsigned)nkeep) + 8), select_tramp, &a);
}
struct rows_args { const u32 *bits; int nU; const u32 *member; const i64 *offs; int nsel; u16 *rows; };
static void rows_tramp(void *a) { rows_args *x = (rows_args *)a; s200g_rows(x->bits, x->nU, x->member, x->offs, x->nsel, x->rows); }
extern "C" void cpu_rows(const u32 *bits, int nU, const u32 *member, const i64 *offs, int nsel, u16 *rows) {
    rows_args a{bits, nU, member, offs, nsel, rows};
    run_grid((nsel + NTHREADS - 1) / NTHREADS, NTHREADS, 0, rows_tramp, &a);
}
extern "C" unsigned cpu_kw() { return KW; }
