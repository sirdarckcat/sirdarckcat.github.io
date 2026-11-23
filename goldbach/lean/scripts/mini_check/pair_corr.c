// Independent replication of the "no local moves" measurement in the miniature:
// pairs N, N + M0 (M0 = 2*3*5*...*23, the same cover), both even, coprime to 3..29, in [Q+z, X).
// Correlation of the rows left at depth z between the two, within each value of the rows left at depth 23.
#include <omp.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { uint64_t w[3]; } mask_t;
static int ns, n1, nsmall, nrows, sp[64], rows[200]; static mask_t **mk;
static int score(long N, int *k1, int *k2) {            // 0 if N has a prime factor in 3..29
    mask_t m1 = {{0,0,0}}, m2;
    for (int i = 0; i < nsmall; i++) { int a = N % sp[i]; if (a == 0) return 0;
        if (i < n1) { m1.w[0] |= mk[i][a].w[0]; m1.w[1] |= mk[i][a].w[1]; m1.w[2] |= mk[i][a].w[2]; } }
    m2 = m1;
    for (int i = n1; i < ns; i++) { int a = N % sp[i]; m2.w[0] |= mk[i][a].w[0]; m2.w[1] |= mk[i][a].w[1]; m2.w[2] |= mk[i][a].w[2]; }
    *k1 = nrows - (__builtin_popcountll(m1.w[0]) + __builtin_popcountll(m1.w[1]) + __builtin_popcountll(m1.w[2]));
    *k2 = nrows - (__builtin_popcountll(m2.w[0]) + __builtin_popcountll(m2.w[1]) + __builtin_popcountll(m2.w[2]));
    return 1;
}
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]), z1 = atoi(argv[3]), z = atoi(argv[4]);
    int lim = 2000; char *c = calloc(lim, 1); int np = 0, pr[400];
    for (int i = 2; i < lim; i++) if (!c[i]) { pr[np++] = i; for (int j = i * i; j < lim; j += i) c[j] = 1; }
    for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    for (int i = 1; i < np && pr[i] <= z; i++) sp[ns++] = pr[i];
    mk = malloc(ns * sizeof(mask_t *));
    for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t));
        for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    while (n1 < ns && sp[n1] <= z1) n1++;
    while (nsmall < ns && sp[nsmall] <= 29) nsmall++;
    long M0 = 2; for (int i = 0; i < n1; i++) M0 *= sp[i];
    int D = nrows + 1;
    double *acc = calloc((size_t)D * 6, sizeof(double));      // per k1: n, sx, sy, sxx, syy, sxy
    #pragma omp parallel
    { double *a = calloc((size_t)D * 6, sizeof(double));
      long Nend = X - M0;
      #pragma omp for schedule(static)
      for (long N = (Q + z + 1) & ~1L; N < Nend; N += 2) {
          int k1, k2, j1, j2;
          if (!score(N, &k1, &k2)) continue;
          if (!score(N + M0, &j1, &j2)) continue;
          if (j1 != k1) { fprintf(stderr, "cover mismatch\n"); exit(1); }
          double *g = a + (size_t)k1 * 6; g[0] += 1; g[1] += k2; g[2] += j2; g[3] += (double)k2 * k2; g[4] += (double)j2 * j2; g[5] += (double)k2 * j2;
      }
      #pragma omp critical
      for (int i = 0; i < D * 6; i++) acc[i] += a[i];
    }
    double n = 0, cxy = 0, cxx = 0, cyy = 0;
    for (int k = 0; k < D; k++) { double *g = acc + (size_t)k * 6; if (g[0] < 2) continue;
        n += g[0]; cxy += g[5] - g[1] * g[2] / g[0]; cxx += g[3] - g[1] * g[1] / g[0]; cyy += g[4] - g[2] * g[2] / g[0]; }
    printf("M0 = %ld; %.0f pairs N, N + M0; correlation of the rows left at depth %d within each value of the rows left at depth %d: %.4f\n",
           M0, n, z, z1, cxy / sqrt(cxx * cyy));
    for (int k = 22; k <= 44; k += 2) { double *g = acc + (size_t)k * 6; if (g[0] < 100) continue;
        double vxy = g[5] - g[1] * g[2] / g[0], vxx = g[3] - g[1] * g[1] / g[0], vyy = g[4] - g[2] * g[2] / g[0];
        printf("  rows left at depth %d = %d: %.0f pairs, correlation %.4f\n", z1, k, g[0], vxy / sqrt(vxx * vyy)); }
    return 0;
}
