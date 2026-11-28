/* enumv.c -- count the residue vectors on the cover primes by residual size.
 *
 *   gcc -O3 -march=native -fopenmp -o enumv enumv.c
 *   ./enumv Q limit            e.g. ./enumv 10007 198
 *
 * Same enumeration as tscan/variants.py (depth first over the primes 3..43, nonzero residues only,
 * pruned with the exact bound "each later prime removes at most its largest class of the primes
 * still alive"), in C with bitsets so that tens of millions of vectors take seconds.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
typedef uint64_t u64;
#define NW 24                       /* 64*NW bits >= number of odd primes below Q */
#define NR 13
static const int RS[NR] = {3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43};
static u64 cls[NR][44][NW];
static int nq, qs[64 * NW], limit;
static long hist[512];
#pragma omp threadprivate(hist)

static inline int pc(const u64 *a, const u64 *b) {
    int c = 0;
    for (int i = 0; i < NW; i++) c += __builtin_popcountll(a[i] & b[i]);
    return c;
}

static void dfs(int i, const u64 *alive, int n) {
    if (i == NR) { hist[n]++; return; }
    int later = 0;
    for (int j = i + 1; j < NR; j++) {
        int best = 0;
        for (int a = 1; a < RS[j]; a++) { int c = pc(alive, cls[j][a]); if (c > best) best = c; }
        later += best;
    }
    int r = RS[i], cnt[44], ord[44];
    for (int a = 1; a < r; a++) { cnt[a] = pc(alive, cls[i][a]); ord[a - 1] = a; }
    for (int x = 1; x < r - 1; x++) {                      /* insertion sort, largest class first */
        int v = ord[x], y = x;
        while (y > 0 && cnt[ord[y - 1]] < cnt[v]) { ord[y] = ord[y - 1]; y--; }
        ord[y] = v;
    }
    for (int x = 0; x < r - 1; x++) {
        int a = ord[x];
        if (n - cnt[a] - later > limit) break;
        u64 next[NW];
        for (int w = 0; w < NW; w++) next[w] = alive[w] & ~cls[i][a][w];
        dfs(i + 1, next, n - cnt[a]);
    }
}

int main(int argc, char **argv) {
    int Q = atoi(argv[1]); limit = atoi(argv[2]);
    char *sv = calloc(Q, 1);
    for (int p = 3; p < Q; p += 2) {
        if (sv[p]) continue;
        qs[nq++] = p;
        for (long m = (long)p * p; m < Q; m += 2 * p) sv[m] = 1;
    }
    if (nq > 64 * NW) return 1;
    for (int j = 0; j < NR; j++)
        for (int x = 0; x < nq; x++) cls[j][qs[x] % RS[j]][x >> 6] |= 1ull << (x & 63);
    /* note: the cover primes themselves (3..43 < Q) sit in class 0 and are never removed: they stay residual */
    u64 all[NW] = {0};
    for (int x = 0; x < nq; x++) all[x >> 6] |= 1ull << (x & 63);
    long tot[512] = {0};
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        memset(hist, 0, sizeof hist);
        #pragma omp for schedule(dynamic, 1) collapse(3)
        for (int a3 = 1; a3 < 3; a3++)
            for (int a5 = 1; a5 < 5; a5++)
                for (int a7 = 1; a7 < 7; a7++) {
                    u64 al[NW];
                    for (int w = 0; w < NW; w++) al[w] = all[w] & ~cls[0][a3][w] & ~cls[1][a5][w] & ~cls[2][a7][w];
                    int n = 0;
                    for (int w = 0; w < NW; w++) n += __builtin_popcountll(al[w]);
                    dfs(3, al, n);
                }
        #pragma omp critical
        for (int x = 0; x < 512; x++) tot[x] += hist[x];
    }
    long cum = 0;
    printf("Q=%d odd primes %d; vectors by residual size (limit %d), %.1fs:\n", Q, nq, limit, omp_get_wtime() - t0);
    for (int x = 0; x < 512; x++) if (tot[x]) { cum += tot[x]; printf("  %d: %ld  (cum %ld)\n", x, tot[x], cum); }
    return 0;
}
