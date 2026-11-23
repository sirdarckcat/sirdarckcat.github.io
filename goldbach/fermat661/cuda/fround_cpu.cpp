/* CPU build of fround_kernels.cuh (test_fround_cpu.py): every kernel as a loop over blocks and threads, no shared memory, no barriers, atomicOr as a plain or (the loops are sequential). */
#include <cstddef>
struct Dim3 { unsigned x, y, z; };
static Dim3 blockIdx, threadIdx, blockDim, gridDim;
#define __global__
static inline int atomicOr(int *p, int v) { int o = *p; *p = o | v; return o; }
#include "fround_kernels.cuh"
#define RUN(grid, block, call) for (unsigned b_ = 0; b_ < (unsigned)(grid); b_++) for (unsigned t_ = 0; t_ < (unsigned)(block); t_++) { blockIdx.x = b_; threadIdx.x = t_; blockDim.x = (block); call; }
extern "C" void cpu_fr_plan(int grid, int block, const int *act, const long long *cnt, const int *pos, const int *ctl, int nb, int target, int dmax, int *takes) {
    RUN(grid, block, fr_plan(act, cnt, pos, ctl, nb, target, dmax, takes));
}
extern "C" void cpu_fr_info(int grid, int block, const int *ends, int nb, int *ctl) {
    RUN(grid, block, fr_info(ends, nb, ctl));
}
extern "C" void cpu_fr_expand(int grid, int block, const int *act, const int *ends, const int *takes, const long long *indptr, const int *pos, const int *cols, const long long *kv,
                              int nb, int total, int *rowsv, unsigned int *kvals) {
    RUN(grid, block, fr_expand(act, ends, takes, indptr, pos, cols, kv, nb, total, rowsv, kvals));
}
extern "C" void cpu_fr_post(int grid, int block, const int *act, const int *ends, const int *takes, const int *rowsv, const unsigned char *flags, int *pos, int *last, const long long *cnt,
                            int *tests_m, unsigned char *prp_m, unsigned char *succ_m, int *frow, int *keep, int *ctl, int nb, int check_range) {
    RUN(grid, block, fr_post(act, ends, takes, rowsv, flags, pos, last, cnt, tests_m, prp_m, succ_m, frow, keep, ctl, nb, check_range));
}
extern "C" void cpu_fr_compact(int grid, int block, const int *act, const int *keep, const int *kcs, int *act2, int *ctl, int nb) {
    RUN(grid, block, fr_compact(act, keep, kcs, act2, ctl, nb));
}
