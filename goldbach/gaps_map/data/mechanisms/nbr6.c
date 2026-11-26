// nbr6.c -- neighbour search whose SEEDS are chosen by a sieve proxy: stream members with at most `theta` rows alive at depth 199.
// Only those members are fully verified (all alive rows tested: cost k199 tests); every other stream member is rejected at its first prime row (2.2 tests expected).
// usage: ./nbr6 X Q kmax theta J cmin H      (J = largest number of prime rows for which a shift set is generated; use 99 for "any")
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define NW 3
typedef struct { uint64_t w[NW]; } mask_t;
static inline int pc(const mask_t *m) { int s = 0; for (int i = 0; i < NW; i++) s += __builtin_popcountll(m->w[i]); return s; }
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]); int kmax = atoi(argv[3]); int theta = atoi(argv[4]); int J = atoi(argv[5]); int cmin = atoi(argv[6]); int H = atoi(argv[7]);
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    size_t nb = (X >> 1) + 1; uint64_t *bm = malloc((nb / 64 + 1) * 8); memset(bm, 0xff, (nb / 64 + 1) * 8); bm[0] &= ~1ULL;
    for (int i = 1; i < np && (long)pr[i] * pr[i] <= X; i++) { long p = pr[i]; for (long x = p * p; x <= X; x += 2 * p) bm[(x >> 1) >> 6] &= ~(1ULL << ((x >> 1) & 63)); }
    int rows[300], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    char *isr = calloc(Q + 2 * H + 10, 1); for (int j = 0; j < nrows; j++) isr[rows[j]] = 1;
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= 199; i++) sp[ns++] = pr[i];
    int nsh23 = 0; while (nsh23 < ns && sp[nsh23] <= 23) nsh23++;
    mask_t **mk = malloc(ns * sizeof(mask_t *)); for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int small[9] = {3, 5, 7, 11, 13, 17, 19, 23, 29};
    static int shifts[8000]; int nsh = 0; for (int s = -H; s <= H; s += 2) { if (s == 0) continue; int cnt = 0; for (int j = 0; j < nrows; j++) { int q = rows[j] - s; if (q >= 3 && q < Q && isr[q]) cnt++; } if (cnt >= cmin) shifts[nsh++] = s; }
    long Nlo = (Q + 200 + 1) & ~1L, total = (X - Nlo) / 2 + 1; uint64_t *scn = calloc((X >> 7) + 2, 8);
    int nth = omp_get_max_threads();
    long *nst = calloc(nth, sizeof(long)), *sst = calloc(nth, sizeof(long)), *cand = calloc(nth, sizeof(long)), *vt = calloc(nth, sizeof(long)), *seeds = calloc(nth, sizeof(long)), *scans = calloc(nth, sizeof(long)), *found = calloc(nth, sizeof(long));
    #pragma omp parallel
    {
        int t = omp_get_thread_num();
        #pragma omp for schedule(dynamic, 1000000)
        for (long u = 0; u < total; u++) {
            long N = Nlo + 2 * u; int ok = 1; for (int i = 0; i < 9; i++) if (N % small[i] == 0) { ok = 0; break; } if (!ok) continue;
            mask_t m; memset(&m, 0, sizeof(m)); int k1 = 0;
            for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N % sp[i]]; for (int w = 0; w < NW; w++) m.w[w] |= e->w[w]; if (i + 1 == nsh23) k1 = nrows - pc(&m); }
            if (k1 > kmax) continue; nst[t]++; int k199 = nrows - pc(&m);
            int Pr[100], jp = 0; int allrows = 0;
            // success flag of the stream member (free in the miniature; counted for the baseline comparison)
            { int pf = 0; for (int j = 0; j < nrows; j++) { long v = N - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) { pf = 1; break; } } if (!pf) sst[t]++; }
            if (k199 > theta) continue;                       // not a seed candidate: rejected at its first prime row, no further verification
            cand[t]++; vt[t] += k199;                         // seed candidate: every alive row is tested
            for (int j = 0; j < nrows && jp < 99; j++) { long v = N - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) Pr[jp++] = rows[j]; }
            if (jp > J) continue; seeds[t]++;
            for (int si = 0; si < nsh; si++) { int s = shifts[si]; int clean = 1; for (int a = 0; a < jp; a++) { int q = Pr[a] + s; if (q >= 3 && q < Q && isr[q]) { clean = 0; break; } } if (!clean) continue;
                long N2 = N + s; if (N2 < Nlo || N2 >= X) continue; int ok2 = 1; for (int i = 0; i < 9; i++) if (N2 % small[i] == 0) { ok2 = 0; break; } if (!ok2) continue;
                mask_t m2; memset(&m2, 0, sizeof(m2)); int k12 = 0; for (int i = 0; i < nsh23; i++) { const mask_t *e = &mk[i][N2 % sp[i]]; for (int w = 0; w < NW; w++) m2.w[w] |= e->w[w]; } k12 = nrows - pc(&m2); if (k12 <= kmax) continue;
                long ix = N2 >> 1; uint64_t bit = 1ULL << (ix & 63); uint64_t was = __atomic_fetch_or(&scn[ix >> 6], bit, __ATOMIC_RELAXED); if (was & bit) continue;
                scans[t]++; int pf = 0; for (int j = 0; j < nrows; j++) { long v = N2 - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) { pf = 1; break; } } if (!pf) found[t]++; }
        }
    }
    long a[7] = {0}; for (int t = 0; t < nth; t++) { a[0] += nst[t]; a[1] += sst[t]; a[2] += cand[t]; a[3] += vt[t]; a[4] += seeds[t]; a[5] += scans[t]; a[6] += found[t]; }
    printf("kmax=%d theta=%d J=%d cmin=%d: STREAM %ld SUCC %ld CAND %ld VERIFYTESTS %ld SEEDS %ld SCANS %ld FOUND %ld\n", kmax, theta, J, cmin, a[0], a[1], a[2], a[3], a[4], a[5], a[6]);
    return 0;
}
