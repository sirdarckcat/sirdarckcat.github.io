// Independent re-enumeration of the research session's miniature (X = 1e9, Q = 1000, z1 = 23, z = 200).
// Different method from toy_exact.c: rows killed at depth z are found from the residues of N (a union of
// row-bitmasks, one per class of each prime), and primality of N - q from a segmented odd-only prime bitmap.
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { uint64_t w[3]; } mask_t;
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]), z1 = atoi(argv[3]), z = atoi(argv[4]);
    // small primes
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    // odd-only prime bitmap up to X: bit (n>>1) set iff n odd prime
    size_t nb = (X >> 1) + 1; uint64_t *bm = malloc((nb / 64 + 1) * 8); memset(bm, 0xff, (nb / 64 + 1) * 8);
    bm[0] &= ~1ULL; // 1 is not prime
    for (int i = 1; i < np && (long)pr[i] * pr[i] <= X; i++) { long p = pr[i];
        for (long x = p * p; x <= X; x += 2 * p) bm[(x >> 1) >> 6] &= ~(1ULL << ((x >> 1) & 63)); }
    int rows[200], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    // masks per (prime s <= z, class a)
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= z; i++) sp[ns++] = pr[i];
    mask_t **mk = malloc(ns * sizeof(mask_t *));
    for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t));
        for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int n1 = 0; while (n1 < ns && sp[n1] <= z1) n1++;
    int nsmall = 0; while (nsmall < ns && sp[nsmall] <= 29) nsmall++;
    long D = nrows + 1; long *hist = calloc(D * D * 2, sizeof(long)); long total = 0, succ = 0;
    #pragma omp parallel
    { long *h = calloc(D * D * 2, sizeof(long)); long t = 0, su = 0;
      #pragma omp for schedule(static)
      for (long N = (Q + z + 1) & ~1L; N < X; N += 2) {
          int ok = 1; mask_t m1 = {{0,0,0}}, m2;
          for (int i = 0; i < nsmall; i++) { int a = N % sp[i]; if (a == 0) { ok = 0; break; }
              if (i < n1) { m1.w[0] |= mk[i][a].w[0]; m1.w[1] |= mk[i][a].w[1]; m1.w[2] |= mk[i][a].w[2]; } }
          if (!ok) continue;
          m2 = m1;
          for (int i = n1; i < ns; i++) { int a = N % sp[i];
              if (i < nsmall && a == 0) { ok = 0; break; }
              m2.w[0] |= mk[i][a].w[0]; m2.w[1] |= mk[i][a].w[1]; m2.w[2] |= mk[i][a].w[2]; }
          int k1 = nrows - (__builtin_popcountll(m1.w[0]) + __builtin_popcountll(m1.w[1]) + __builtin_popcountll(m1.w[2]));
          int k2 = nrows - (__builtin_popcountll(m2.w[0]) + __builtin_popcountll(m2.w[1]) + __builtin_popcountll(m2.w[2]));
          int anyprime = 0;
          for (int j = 0; j < nrows; j++) { long m = N - rows[j]; if (bm[(m >> 1) >> 6] >> ((m >> 1) & 63) & 1) { anyprime = 1; break; } }
          h[(k1 * D + k2) * 2 + (anyprime ? 0 : 1)]++; t++; su += !anyprime;
      }
      #pragma omp critical
      { for (long i = 0; i < D * D * 2; i++) hist[i] += h[i]; total += t; succ += su; }
    }
    printf("# X=%ld Q=%d z1=%d z=%d rows=%d ; columns: k1 k2 failures successes\n", X, Q, z1, z, nrows);
    for (long a = 0; a < D; a++) for (long b = 0; b < D; b++) { long *cc = hist + (a * D + b) * 2; if (cc[0] || cc[1]) printf("%ld %ld %ld %ld\n", a, b, cc[0], cc[1]); }
    fprintf(stderr, "total N = %ld, successes = %ld\n", total, succ);
    return 0;
}
