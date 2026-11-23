/* CPU build of the persistent pool kernel (gpu_fermat28.persist_source(): fm28_test + fermat28_persist): `nlanes` real threads, each running the kernel once, taking members
 * from the queue with an atomic counter, exactly as the GPU threads do.  The source text is written by the test (PERSIST_SRC) from persist_source(). */
#include <cstdint>
#include <cstddef>
#include <thread>
#include <vector>
typedef unsigned int u32;
typedef unsigned long long u64;
#define __device__
#define __forceinline__ inline __attribute__((always_inline))
#define __global__
static inline int __clz(u32 x) { return __builtin_clz(x); }
static inline int atomicAdd(int *p, int v) { return __sync_fetch_and_add(p, v); }
#define FM28_MADN(acc, a, b) ((acc) += (u64)(u32)(a) * (u32)(b))
#ifndef PERSIST_SRC
#error "PERSIST_SRC must name the file written from gpu_fermat28.persist_source()"
#endif
/* persist_source() starts with the typedefs (repeated typedefs of the same type are legal in C++) */
#include PERSIST_SRC
extern "C" void run_persist_cpu(const u32 *CQ, const u32 *Mv, const u32 *kv, const int *cnt, const long long *indptr, const int *cols, int nMembers,
                                int *counter, int *tests, unsigned char *state, int *frow, int nlanes) {
    std::vector<std::thread> th;
    for (int i = 0; i < nlanes; i++) th.emplace_back([=]() { fermat28_persist(CQ, Mv, kv, cnt, indptr, cols, nMembers, counter, tests, state, frow); });
    for (auto &t : th) t.join();
}
