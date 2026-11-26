/* fround_kernels.cuh -- the bookkeeping of the Fermat rounds (run_pool in search_gpu5.py) as a few device kernels.
 *
 * run_pool spends each round on ~100 small cupy kernels (gathers, cumsum, searchsorted, scatter_min, boolean-mask indexing ...) and ~6 host syncs around the one Fermat kernel; beside the sieve
 * (whose grids have the higher stream priority) every small kernel can queue behind a burst of sieve CTAs, and a round's host code takes ~2.2 ms without any sieve (run_pool wall 1.375 s against
 * 1.277 s of Fermat kernels for 44 rounds, the GPU session's profile-pool probe 04:08Z; 0.13 s a batch more beside the sieve).  A round here is 5 launches + 2 cumsums + ONE host read:
 *
 *   fr_plan    per active slot a: take = min(cnt[m] - pos[m], D), D = clamp(target / nact, 1, dmax)  (run_pool's D without its rem.max(): take is the same)
 *   cumsum     ends = inclusive scan of take (cupy)
 *   fr_info    ctl[2] = total tests of the round = ends[nb - 1]; the host reads ctl[0:3] = (nact, error flags, total) in one copy
 *   fr_expand  per test t < total: the slot a with ends[a - 1] <= t < ends[a] (binary search), row = cols[indptr[m] + pos[m] + (t - start)], k = kv[m]    -> the Fermat kernel's (idx, kv) inputs
 *   (the Fermat kernel itself, unchanged: MultiTester.test)
 *   fr_post    per active slot: scan the member's flags: ascending-rows check, flag > 1 (kernel 28 range) check, first PRP, tests counted, first-PRP row, success, keep[a]
 *   cumsum     kcs = inclusive scan of keep
 *   fr_compact act2[kcs[a] - 1] = act[a] for kept slots (order preserved), ctl[0] = the new nact
 *
 * The test lists of every round, the counted tests, the first-PRP rows, the successes, the computed tests and the rounds are those of run_pool (test_fround_cpu.py compares them on random pools).
 * ctl: int32[4]: [0] active members entering the round, [1] error flags (bit 0: a member's rows not ascending, bit 1: a flag > 1), [2] total tests of the round.
 */
extern "C" __global__ void fr_plan(const int *act, const long long *cnt, const int *pos, const int *ctl, int nb, int target, int dmax, int *takes) {
    const int a = blockIdx.x * blockDim.x + threadIdx.x;
    if (a >= nb) return;
    const int nact = ctl[0];
    if (a >= nact) { takes[a] = 0; return; }
    int D = target / nact;
    if (D > dmax) D = dmax;
    if (D < 1) D = 1;
    const int m = act[a];
    const long long rem = cnt[m] - (long long)pos[m];
    takes[a] = (int)(rem < (long long)D ? rem : (long long)D);
}

extern "C" __global__ void fr_info(const int *ends, int nb, int *ctl) {
    if (blockIdx.x == 0 && threadIdx.x == 0) ctl[2] = ends[nb - 1];
}

extern "C" __global__ void fr_expand(const int *act, const int *ends, const int *takes, const long long *indptr, const int *pos, const int *cols, const long long *kv,
                                     int nb, int total, int *rowsv, unsigned int *kvals) {
    const int t = blockIdx.x * blockDim.x + threadIdx.x;
    if (t >= total) return;
    int lo = 0, hi = nb - 1;                                   /* the first slot with ends[slot] > t (ends[nb - 1] = total > t) */
    while (lo < hi) {
        const int mid = (lo + hi) >> 1;
        if (ends[mid] > t) hi = mid; else lo = mid + 1;
    }
    const int m = act[lo];
    const int off = t - (ends[lo] - takes[lo]);
    rowsv[t] = cols[indptr[m] + (long long)pos[m] + off];
    kvals[t] = (unsigned int)kv[m];
}

extern "C" __global__ void fr_post(const int *act, const int *ends, const int *takes, const int *rowsv, const unsigned char *flags, int *pos, int *last, const long long *cnt,
                                   int *tests_m, unsigned char *prp_m, unsigned char *succ_m, int *frow, int *keep, int *ctl, int nb, int check_range) {
    const int a = blockIdx.x * blockDim.x + threadIdx.x;
    if (a >= nb) return;
    const int nact = ctl[0];
    if (a >= nact) { keep[a] = 0; return; }
    const int m = act[a], take = takes[a], start = ends[a] - take;
    int prev = last[m], first = -1, err = 0;
    for (int j = 0; j < take; j++) {
        const int row = rowsv[start + j];
        if (row <= prev) err |= 1;                              /* every tested row above the member's previous one (run_pool's check, over the whole block) */
        prev = row;
        const unsigned int f = flags[start + j];
        if (check_range && f > 1u) err |= 2;
        if (f == 1u && first < 0) first = j;
    }
    if (err) atomicOr(&ctl[1], err);
    last[m] = prev;
    if (first >= 0) {                                           /* the first PRP of the block: tests counted up to it, the member is done */
        tests_m[m] += first + 1;
        prp_m[m] = 1;
        frow[m] = rowsv[start + first];
        keep[a] = 0;
    } else {
        tests_m[m] += take;
        const int p = pos[m] + take;
        pos[m] = p;
        if ((long long)p == cnt[m]) { succ_m[m] = 1; keep[a] = 0; } else keep[a] = 1;
    }
}

extern "C" __global__ void fr_compact(const int *act, const int *keep, const int *kcs, int *act2, int *ctl, int nb) {
    const int a = blockIdx.x * blockDim.x + threadIdx.x;
    if (a >= nb) return;
    if (keep[a]) act2[kcs[a] - 1] = act[a];
    if (a == nb - 1) ctl[0] = kcs[nb - 1];
}
