// toy_exact.c -- exact check of the counting behind Result 3 on an instance small enough to enumerate.
// For every even N in [Q + z, X) with no prime factor in 3..29, count the rows q (odd primes < Q) for which N - q has
// no odd prime factor <= z, and print the histogram.  ideal_tilt.c predicts the same histogram from the residue
// vectors alone (number of N with k rows left = g(k) * (X/2) / prod s); the two are compared by toy_compare.py.
//
//   gcc -O3 -march=native -fopenmp -o toy_exact toy_exact.c
//   ./toy_exact X Q z > hist.txt
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s X Q z\n", argv[0]); return 1; }
    long X = atol(argv[1]); int Q = atoi(argv[2]), z = atoi(argv[3]);
    int lim = Q > z ? Q : z; char *comp = calloc(lim + 2, 1);
    for (int i = 2; (long)i * i <= lim; i++) if (!comp[i]) for (int j = i * i; j <= lim; j += i) comp[j] = 1;
    int nrows = 0, *row = malloc(lim * sizeof(int)); for (int i = 3; i < Q; i++) if (!comp[i]) row[nrows++] = i;
    uint8_t *rough = malloc(X + 1); memset(rough, 1, X + 1);              // rough[x] = 1: no odd prime factor <= z
    for (int s = 3; s <= z; s++) if (!comp[s]) { for (long x = s; x <= X; x += s) rough[x] = 0; }
    uint8_t *okN = malloc(X + 1); memset(okN, 1, X + 1);                  // no prime factor in 3..29
    for (int s = 3; s <= 29; s++) if (!comp[s]) for (long x = s; x <= X; x += s) okN[x] = 0;
    long *hist = calloc(nrows + 1, sizeof(long)); long total = 0;
    #pragma omp parallel
    {
        long *h = calloc(nrows + 1, sizeof(long)); long t = 0;
        #pragma omp for schedule(static)
        for (long N = (Q + z + 1) & ~1L; N < X; N += 2) {
            if (!okN[N]) continue;
            int k = 0; for (int i = 0; i < nrows; i++) k += rough[N - row[i]];
            h[k]++; t++;
        }
        #pragma omp critical
        { for (int k = 0; k <= nrows; k++) hist[k] += h[k]; total += t; }
        free(h);
    }
    printf("# X=%ld Q=%d z=%d rows=%d even N in [%d, X) with no prime factor in 3..29: %ld\n", X, Q, z, nrows, (Q + z + 1) & ~1, total);
    for (int k = 0; k <= nrows; k++) if (hist[k]) printf("%d %ld\n", k, hist[k]);
    return 0;
}
