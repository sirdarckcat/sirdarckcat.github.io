/* fermat28_persist_kernel.cuh -- a persistent, work-stealing Fermat kernel for a POOL of members (goldbach/phd/campaign3_gpu/search_gpu5.py).  Appended by gpu_fermat28.persist_source()
 * to fm28_test(), which is fermat28_kernel.cuh's kernel body turned into a device function by an exact text transformation (so it is the SAME code as the production kernel).
 *
 * Every thread takes a member from a queue (one atomicAdd on `counter`), tests its rows IN ORDER (cols[indptr[m] + 0, 1, ...]: global row ids of CQ, ascending q) until the first probable
 * prime, writes the result and takes the next member.  No host round trip, no row tested past the first PRP (the round-based run_pool computes ~3% such tests), no kernel launch a round.
 * Threads of a warp are at different steps of different tests: the step code is branch free (the exponent bit is a shift), so they stay converged inside the step loop and only the
 * setup / final code of a test that starts or ends is run by part of the warp.  When the queue is empty, a thread that has finished a test of a member that is not decided stops and
 * leaves the member to the caller (state 0, tests[m] = rows already tested, all composite): the caller finishes those with the round-based code (the members in flight at that moment:
 * a few percent of the work, since the remaining length of a member is memoryless).
 *   cnt[m]    rows of member m (0: nothing to test, a success)       indptr[m]  offset of its first row in cols (int64)       kv[m]  its k
 *   tests[m]  rows tested: the first PRP's index + 1; cnt[m] for a success; the rows done so far for a member left to the caller
 *   state[m]  1 = a PRP was found (frow[m] = its global row), 2 = every row composite (a success, frow = -1), 0 = left to the caller, 3 = an n outside the kernel's range (the caller raises)
 * counter must be 0 at the start; tests / state / frow need no initialisation (every member is written exactly once). */
extern "C" __global__ void fermat28_persist(const u32 *CQ, const u32 *Mv, const u32 *kv, const int *cnt, const long long *indptr, const int *cols, const int nMembers,
                                            int *counter, int *tests, unsigned char *state, int *frow) {
    int m = -1, pos = 0, cm = 0;
    long long base = 0;
    u32 km = 0;
    for (;;) {
        if (m < 0) {
            if (*(volatile int *)counter >= nMembers) break;                  /* the queue is empty */
            m = atomicAdd(counter, 1);
            if (m >= nMembers) break;
            cm = cnt[m]; base = indptr[m]; km = kv[m]; pos = 0;
            if (cm == 0) { tests[m] = 0; frow[m] = -1; state[m] = 2; m = -1; continue; }
        }
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
