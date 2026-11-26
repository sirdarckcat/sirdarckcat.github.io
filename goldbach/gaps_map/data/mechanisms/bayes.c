// bayes.c -- Bayes-optimal "shallow statistic" bound on the miniature.
// For every allowed even N < X with k1 <= k1max (k1 = rows alive after odd primes 3..23) compute
//   L(R) = ln E_c [ (1-rho)^{k(R,c)} ],  c = uniform random residues mod the primes 29..199 (29: nonzero classes only),
// i.e. the best possible estimate of log P(success) that can be made from the residues mod 3..23 alone (under H1 + calibration),
// by Monte Carlo with S samples. Output: histograms counts[k1][bin], succ[k1][bin], bin = floor((L+14)*40).
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef struct { uint64_t w[3]; } mask_t;
#define NBIN 800
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]); int k1max = atoi(argv[3]); int S = atoi(argv[4]); double q1r = atof(argv[5]); char *out = argv[6];
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    size_t nb = (X >> 1) + 1; uint64_t *bm = malloc((nb / 64 + 1) * 8); memset(bm, 0xff, (nb / 64 + 1) * 8); bm[0] &= ~1ULL;
    for (int i = 1; i < np && (long)pr[i] * pr[i] <= X; i++) { long p = pr[i]; for (long x = p * p; x <= X; x += 2 * p) bm[(x >> 1) >> 6] &= ~(1ULL << ((x >> 1) & 63)); }
    int rows[300], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= 199; i++) sp[ns++] = pr[i];
    mask_t **mk = malloc(ns * sizeof(mask_t *));
    for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int nsh = 0; while (nsh < ns && sp[nsh] <= 23) nsh++;      // shallow primes 3..23
    int nsmall = 0; while (nsmall < ns && sp[nsmall] <= 29) nsmall++;
    double pw[256]; for (int k = 0; k < 256; k++) pw[k] = pow(1.0 - q1r, k);
    long Nlo = (Q + 200 + 1) & ~1L; long total = (X - Nlo) / 2 + 1;
    int nth = omp_get_max_threads(); long *cnt = calloc((size_t)nth * 64 * NBIN, sizeof(long)), *scn = calloc((size_t)nth * 64 * NBIN, sizeof(long));
    #pragma omp parallel
    {
        int t = omp_get_thread_num(); uint64_t st = 88172645463325252ULL + 0x9E3779B97F4A7C15ULL * (t + 1);
        long *cc = cnt + (size_t)t * 64 * NBIN, *ss = scn + (size_t)t * 64 * NBIN;
        #pragma omp for schedule(dynamic, 1000000)
        for (long u = 0; u < total; u++) {
            long N = Nlo + 2 * u; int ok = 1; for (int i = 0; i < nsmall; i++) if (N % sp[i] == 0) { ok = 0; break; } if (!ok) continue;
            mask_t m = {{0, 0, 0}}; for (int i = 0; i < nsh; i++) { const mask_t *e = &mk[i][N % sp[i]]; m.w[0] |= e->w[0]; m.w[1] |= e->w[1]; m.w[2] |= e->w[2]; }
            mask_t A = {{~m.w[0], ~m.w[1], ~m.w[2]}}; // alive rows (bits beyond nrows must be cleared)
            for (int b = nrows; b < 192; b++) A.w[b >> 6] &= ~(1ULL << (b & 63));
            int k1 = __builtin_popcountll(A.w[0]) + __builtin_popcountll(A.w[1]) + __builtin_popcountll(A.w[2]); if (k1 > k1max) continue;
            double acc = 0;
            for (int s = 0; s < S; s++) {
                uint64_t a0 = A.w[0], a1 = A.w[1], a2 = A.w[2];
                for (int i = nsh; i < ns; i++) {
                    st ^= st >> 12; st ^= st << 25; st ^= st >> 27; uint64_t r = (st * 2685821657736338717ULL) >> 32;
                    int cl = (sp[i] == 29) ? 1 + (int)((r * 28) >> 32) : (int)((r * sp[i]) >> 32);
                    const mask_t *e = &mk[i][cl]; a0 &= ~e->w[0]; a1 &= ~e->w[1]; a2 &= ~e->w[2];
                }
                acc += pw[__builtin_popcountll(a0) + __builtin_popcountll(a1) + __builtin_popcountll(a2)];
            }
            double L = log(acc / S); int bin = (int)((L + 14.0) * 40.0); if (bin < 0) bin = 0; if (bin >= NBIN) bin = NBIN - 1;
            int anyprime = 0; for (int j = 0; j < nrows; j++) { long mm = N - rows[j]; if ((bm[(mm >> 1) >> 6] >> ((mm >> 1) & 63)) & 1) { anyprime = 1; break; } }
            cc[k1 * NBIN + bin]++; if (!anyprime) ss[k1 * NBIN + bin]++;
        }
    }
    FILE *f = fopen(out, "wb");
    for (int k = 0; k < 64; k++) for (int b = 0; b < NBIN; b++) { long a = 0, s2 = 0; for (int t = 0; t < nth; t++) { a += cnt[((size_t)t * 64 + k) * NBIN + b]; s2 += scn[((size_t)t * 64 + k) * NBIN + b]; } fwrite(&a, 8, 1, f); fwrite(&s2, 8, 1, f); }
    fclose(f); return 0;
}
