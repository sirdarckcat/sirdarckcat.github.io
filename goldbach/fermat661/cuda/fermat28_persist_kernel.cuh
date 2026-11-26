/* fermat28_persist_kernel.cuh -- a persistent, work-stealing Fermat kernel for a POOL of members (goldbach/phd/campaign3_gpu/search_gpu5.py).  Appended by gpu_fermat28.persist_source()
 * to fm28_test(), which is fermat28_kernel.cuh's kernel body turned into a device function by an exact text transformation (so it is the SAME code as the production kernel).
 *
 * Every thread takes a member from a queue (one atomicAdd on `counter`), tests its rows IN ORDER (cols[indptr[m] + 0, 1, ...]: global row ids of CQ, ascending q) until the first probable
 * prime, writes the result and takes the next member.  No host round trip, no row tested past the first PRP (the round-based run_pool computes ~3% such tests), no kernel launch a round.
 * Threads of a warp are at different tests of different members, but every test has the same length (the exponent bit is a shift, so the step is branch free), so the warp's lanes finish
 * a test together and only the bookkeeping / fetch of a member that ends is run by part of the warp.
 *
 * WARP CONVERGENCE (the first version of this file had none, and measured ~1 s a batch SLOWER than the round-based path on an RTX PRO 6000 although its SASS is the production step loop):
 * the fetch of a new member (a global atomic and four dependent loads, a few microseconds) is done by the ~7% of lanes whose member just ended; the other lanes branch past it and, on
 * Volta and later (independent thread scheduling), nothing makes the two groups meet again before the test: the compiler put its convergence barrier only at the END of the loop body (SASS:
 * `BSSY.RELIABLE B1` at the loop head, `BSYNC.RELIABLE B1` at the bottom), so the lanes that did not fetch can start the 660-step test alone, the fetching lanes arrive later at the same
 * code and the two sub-warps then issue every instruction of the step loop separately (each instruction serves only its own lanes): up to 2x the instructions for the same tests.
 * `__syncwarp()` (FM28_PSYNC=1, the default) makes the whole warp meet before each test (WARPSYNC in the SASS); the cost is one fetch latency (a few us) a test of ~5 ms.
 * FM28_PSYNC=0 compiles the first version, for comparison (gpu_fermat28.persist_kernel: environment FERMAT_PERSIST_SYNC=0).
 *
 * When the queue is empty, a thread that has finished a test of a member that is not decided stops and leaves the member to the caller (state 0, tests[m] = rows already tested, all
 * composite): the caller finishes those with the round-based code (the members in flight at that moment: a few percent of the work, since the remaining length of a member is memoryless).
 *   cnt[m]    rows of member m (0: nothing to test, a success)       indptr[m]  offset of its first row in cols (int64)       kv[m]  its k
 *   tests[m]  rows tested: the first PRP's index + 1; cnt[m] for a success; the rows done so far for a member left to the caller
 *   state[m]  1 = a PRP was found (frow[m] = its global row), 2 = every row composite (a success, frow = -1), 0 = left to the caller, 3 = an n outside the kernel's range (the caller raises)
 * counter must be 0 at the start; tests / state / frow need no initialisation (every member is written exactly once). */
#ifndef FM28_PSYNC
#define FM28_PSYNC 1
#endif
#if FM28_PSYNC
#define FM28_WARPSYNC() __syncwarp()
#else
#define FM28_WARPSYNC() ((void)0)
#endif
extern "C" __global__ void fermat28_persist(const u32 *CQ, const u32 *Mv, const u32 *kv, const int *cnt, const long long *indptr, const int *cols, const int nMembers,
                                            int *counter, int *tests, unsigned char *state, int *frow) {
    int m = -1, pos = 0, cm = 0;
    long long base = 0;
    u32 km = 0;
    for (;;) {
        FM28_WARPSYNC();                                                      /* the whole warp is here: a new round of the loop starts together */
        if (m < 0) {                                                          /* this lane needs a member */
            for (;;) {
                if (*(volatile int *)counter >= nMembers) break;              /* the queue is empty */
                m = atomicAdd(counter, 1);
                if (m >= nMembers) { m = -1; break; }
                cm = cnt[m];
                if (cm > 0) { base = indptr[m]; km = kv[m]; pos = 0; break; }
                tests[m] = 0; frow[m] = -1; state[m] = 2; m = -1;             /* a member without rows: a success, nothing to test; take the next */
            }
            if (m < 0) break;                                                 /* queue empty: this thread is done (exited lanes are not waited for by __syncwarp) */
        }
        FM28_WARPSYNC();                                                      /* the lanes that fetched a member and the lanes that did not meet before the test */
        const int row = cols[base + pos];
        const int r = fm28_test(CQ + (size_t)row * L32, Mv, km, 0);
        pos++;
        if (r != 0) {                                                         /* 1: the first PRP; 2: n outside the range */
            tests[m] = pos; frow[m] = row; state[m] = (unsigned char)(r == 1 ? 1 : 3); m = -1;
        } else if (pos == cm) {                                               /* every row composite */
            tests[m] = pos; frow[m] = -1; state[m] = 2; m = -1;
        } else if (*(volatile int *)counter >= nMembers) {                    /* the queue is empty: leave the member to the caller */
            tests[m] = pos; frow[m] = -1; state[m] = 0; m = -1; break;
        }
    }
}
