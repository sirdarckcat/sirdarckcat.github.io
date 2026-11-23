// List the needles of the miniature: even N in [Q+z, X), free of prime factors 3..29, with N - q composite for
// every odd prime q < Q.  Prints N, rows left at depth 23, rows left at depth 200.  Same method as mini_check.c.
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { uint64_t w[3]; } mask_t;
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]), z1 = atoi(argv[3]), z = atoi(argv[4]); int all = argc > 5;
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    size_t nb = (X >> 1) + 1; uint64_t *bm = malloc((nb / 64 + 1) * 8); memset(bm, 0xff, (nb / 64 + 1) * 8);
    bm[0] &= ~1ULL;
    for (int i = 1; i < np && (long)pr[i] * pr[i] <= X; i++) { long p = pr[i];
        for (long x = p * p; x <= X; x += 2 * p) bm[(x >> 1) >> 6] &= ~(1ULL << ((x >> 1) & 63)); }
    int rows[200], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= z; i++) sp[ns++] = pr[i];
    mask_t **mk = malloc(ns * sizeof(mask_t *));
    for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t));
        for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int n1 = 0; while (n1 < ns && sp[n1] <= z1) n1++;
    int nsmall = 0; while (nsmall < ns && sp[nsmall] <= 29) nsmall++;
    #pragma omp parallel for schedule(static)
    for (long N = (Q + z + 1) & ~1L; N < X; N += 2) {
        int ok = 1; mask_t m1 = {{0,0,0}}, m2;
        if (!all) { for (int i = 0; i < nsmall; i++) if (N % sp[i] == 0) { ok = 0; break; } if (!ok) continue; }
        int anyprime = 0;
        for (int j = 0; j < nrows; j++) { long m = N - rows[j]; if (bm[(m >> 1) >> 6] >> ((m >> 1) & 63) & 1) { anyprime = 1; break; } }
        if (anyprime) continue;
        for (int i = 0; i < ns; i++) { int a = N % sp[i];
            if (i < n1) { m1.w[0] |= mk[i][a].w[0]; m1.w[1] |= mk[i][a].w[1]; m1.w[2] |= mk[i][a].w[2]; } }
        m2 = m1;
        for (int i = n1; i < ns; i++) { int a = N % sp[i]; m2.w[0] |= mk[i][a].w[0]; m2.w[1] |= mk[i][a].w[1]; m2.w[2] |= mk[i][a].w[2]; }
        int k1 = nrows - (__builtin_popcountll(m1.w[0]) + __builtin_popcountll(m1.w[1]) + __builtin_popcountll(m1.w[2]));
        int k2 = nrows - (__builtin_popcountll(m2.w[0]) + __builtin_popcountll(m2.w[1]) + __builtin_popcountll(m2.w[2]));
        #pragma omp critical
        printf("%ld %d %d\n", N, k1, k2);
    }
    return 0;
}
