// nbr5.c -- near-success seeded neighbour search, scored by the success-mass model (works for Q beyond what can be counted).
// usage: ./nbr5 X Q kmax J cmin H rho
// model: P(success) ~ c * (1-rho)^{k199 - a} where k199 = rows alive after all odd primes <=199 and a = inherited rows (known composite, clean shift).
// prints: population per-k1 counts and masses (all members), stream/seed/scan counts, predicted neighbour mass, and exact counted successes for validation.
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#ifndef NW
#define NW 6
#endif
typedef struct { uint64_t w[NW]; } mask_t;
static inline int pc(const mask_t *m) { int s = 0; for (int i = 0; i < NW; i++) s += __builtin_popcountll(m->w[i]); return s; }
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]); int kmax = atoi(argv[3]); int J = atoi(argv[4]); int cmin = atoi(argv[5]); int H = atoi(argv[6]); double rho = atof(argv[7]);
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    size_t nb = (X >> 1) + 1; uint64_t *bm = malloc((nb / 64 + 1) * 8); memset(bm, 0xff, (nb / 64 + 1) * 8); bm[0] &= ~1ULL;
    for (int i = 1; i < np && (long)pr[i] * pr[i] <= X; i++) { long p = pr[i]; for (long x = p * p; x <= X; x += 2 * p) bm[(x >> 1) >> 6] &= ~(1ULL << ((x >> 1) & 63)); }
    int rows[400], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i]; if (nrows > 64 * NW) { fprintf(stderr, "too many rows\n"); return 1; }
    char *isr = calloc(Q + 2 * H + 10, 1); int *rowidx = malloc((Q + 2 * H + 10) * sizeof(int)); for (int j = 0; j < nrows; j++) { isr[rows[j]] = 1; rowidx[rows[j]] = j; }
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= 199; i++) sp[ns++] = pr[i];
    int nsh23 = 0; while (nsh23 < ns && sp[nsh23] <= 23) nsh23++;
    mask_t **mk = malloc(ns * sizeof(mask_t *)); for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    mask_t rowmask; memset(&rowmask, 0, sizeof(rowmask)); for (int j = 0; j < nrows; j++) rowmask.w[j >> 6] |= 1ULL << (j & 63);
    int small[9] = {3, 5, 7, 11, 13, 17, 19, 23, 29};
    static int shifts[8000]; static mask_t inh[8000]; int nsh = 0;
    for (int s = -H; s <= H; s += 2) { if (s == 0) continue; int cnt = 0; mask_t im; memset(&im, 0, sizeof(im));
        for (int j = 0; j < nrows; j++) { int q = rows[j] - s; if (q >= 3 && q < Q && isr[q]) { cnt++; im.w[j >> 6] |= 1ULL << (j & 63); } }
        if (cnt >= cmin) { shifts[nsh] = s; inh[nsh] = im; nsh++; } }
    double pw[512]; for (int k = 0; k < 512; k++) pw[k] = pow(1.0 - rho, k);
    long Nlo = (Q + 200 + 1) & ~1L, total = (X - Nlo) / 2 + 1; uint64_t *scn = calloc((X >> 7) + 2, 8);
    int nth = omp_get_max_threads();
    long *pcnt = calloc((size_t)nth * 128, sizeof(long)), *pobs = calloc((size_t)nth * 128, sizeof(long)); double *pmass = calloc((size_t)nth * 128, sizeof(double));
    long *nst = calloc(nth, sizeof(long)), *sst = calloc(nth, sizeof(long)), *seeds = calloc(nth, sizeof(long)), *scans = calloc(nth, sizeof(long)), *nbobs = calloc(nth, sizeof(long)); double *stm = calloc(nth, sizeof(double)), *nbm = calloc(nth, sizeof(double));
    #pragma omp parallel
    {
        int t = omp_get_thread_num();
        #pragma omp for schedule(dynamic, 1000000)
        for (long u = 0; u < total; u++) {
            long N = Nlo + 2 * u; int ok = 1; for (int i = 0; i < 9; i++) if (N % small[i] == 0) { ok = 0; break; } if (!ok) continue;
            mask_t m; memset(&m, 0, sizeof(m)); int k1 = 0;
            for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N % sp[i]]; for (int w = 0; w < NW; w++) m.w[w] |= e->w[w]; if (i + 1 == nsh23) k1 = nrows - pc(&m); }
            int k199 = nrows - pc(&m); pcnt[t * 128 + k1]++; pmass[t * 128 + k1] += pw[k199];
            int Pr[16], jp = 0; int isstream = (k1 <= kmax);
            if (!isstream) { // counted success only for population calibration
                continue; }
            nst[t]++; stm[t] += pw[k199];
            for (int j = 0; j < nrows && jp <= J; j++) { long v = N - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) Pr[jp++] = rows[j]; }
            if (jp == 0) sst[t]++; if (jp > J) continue; seeds[t]++;
            for (int si = 0; si < nsh; si++) { int s = shifts[si]; int clean = 1; for (int a = 0; a < jp; a++) { int q = Pr[a] + s; if (q >= 3 && q < Q && isr[q]) { clean = 0; break; } } if (!clean) continue;
                long N2 = N + s; if (N2 < Nlo || N2 >= X) continue; int ok2 = 1; for (int i = 0; i < 9; i++) if (N2 % small[i] == 0) { ok2 = 0; break; } if (!ok2) continue;
                mask_t m2; memset(&m2, 0, sizeof(m2)); int k12 = 0; for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N2 % sp[i]]; for (int w = 0; w < NW; w++) m2.w[w] |= e->w[w]; if (i + 1 == nsh23) k12 = nrows - pc(&m2); }
                if (k12 <= kmax) continue;
                long ix = N2 >> 1; uint64_t bit = 1ULL << (ix & 63); uint64_t was = __atomic_fetch_or(&scn[ix >> 6], bit, __ATOMIC_RELAXED); if (was & bit) continue;
                scans[t]++; mask_t A; int k199b = 0, a = 0; for (int w = 0; w < NW; w++) { A.w[w] = ~m2.w[w] & rowmask.w[w]; k199b += __builtin_popcountll(A.w[w]); a += __builtin_popcountll(A.w[w] & inh[si].w[w]); }
                nbm[t] += pw[k199b - a];
                int pf = 0; for (int j = 0; j < nrows; j++) { long v = N2 - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) { pf = 1; break; } } if (!pf) nbobs[t]++; }
        }
    }
    // success counts per k1 for calibration need a second light pass over successes only: do it by full scan of the bitmap rows (rare): skip; calibration done in python from the mini data when available.
    long n_s = 0, s_s = 0, sd = 0, sc = 0, nbo = 0; double smass = 0, nmass = 0; for (int t = 0; t < nth; t++) { n_s += nst[t]; s_s += sst[t]; sd += seeds[t]; sc += scans[t]; nbo += nbobs[t]; smass += stm[t]; nmass += nbm[t]; }
    printf("STREAM %ld SUCC %ld SEEDS %ld SCANS %ld NBOBS %ld STREAMMASS %.6g NBMASS %.6g NSHIFTS %d\n", n_s, s_s, sd, sc, nbo, smass, nmass, nsh);
    for (int k = 0; k < 128; k++) { long a = 0; double ms = 0; for (int t = 0; t < nth; t++) { a += pcnt[t * 128 + k]; ms += pmass[t * 128 + k]; } if (a) printf("POP %d %ld %.8g\n", k, a, ms); }
    return 0;
}
