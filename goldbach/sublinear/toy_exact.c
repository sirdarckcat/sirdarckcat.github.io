// toy_exact.c -- the search problem on an instance small enough to enumerate every N: an exact miniature of Result 3.
// For every even N in [Q + z, X) with no prime factor in 3..29:
//   k1 = number of rows q (odd primes < Q) with N - q free of odd prime factors <= z1   (z1: the Chinese-remainder
//        line, the largest prime with 2*3*5*...*z1 <= X; choosing N modulo these primes is the cover)
//   k2 = the same with z in place of z1                                                 (a deeper sieve)
//   success = no row q has N - q prime                                                 (g(N) >= Q, exactly)
// Output: the joint histogram.  toy_compare.py reads it.
//
//   gcc -O3 -march=native -fopenmp -o toy_exact toy_exact.c
//   ./toy_exact X Q z1 z > hist.txt
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s X Q z1 z\n", argv[0]); return 1; }
    long X = atol(argv[1]); int Q = atoi(argv[2]), z1 = atoi(argv[3]), z = atoi(argv[4]);
    int lim = 1; while ((long)lim * lim <= X) lim++; if (lim < Q) lim = Q; if (lim < z) lim = z;
    char *comp = calloc(lim + 2, 1);
    for (int i = 2; (long)i * i <= lim; i++) if (!comp[i]) for (int j = i * i; j <= lim; j += i) comp[j] = 1;
    int nrows = 0, *row = malloc((Q + 1) * sizeof(int)); for (int i = 3; i < Q; i++) if (!comp[i]) row[nrows++] = i;
    // bit 0: free of odd prime factors <= z1; bit 1: free of odd prime factors <= z; bit 2: prime; bit 3: N allowed
    uint8_t *f = malloc(X + 1); memset(f, 15, X + 1); f[0] = f[1] = 11;
    for (int s = 3; s <= lim; s++) if (!comp[s]) {
        uint8_t clear = 4; if (s <= z1) clear |= 1; if (s <= z) clear |= 2;
        for (long x = (long)s * (s <= z ? 1 : 2); x <= X; x += s) f[x] &= ~clear;      // x = s itself stays prime
        if (s <= z) f[s] |= 4;                                                         // ... also when s <= z
        if (s <= 29) for (long x = s; x <= X; x += s) f[x] &= ~8;
    }
    for (long x = 4; x <= X; x += 2) f[x] &= ~4;
    long (*hist)[2] = calloc((size_t)(nrows + 1) * (nrows + 1), sizeof(long[2]));
    #pragma omp parallel
    {
        long (*h)[2] = calloc((size_t)(nrows + 1) * (nrows + 1), sizeof(long[2]));
        #pragma omp for schedule(static)
        for (long N = (Q + z + 1) & ~1L; N < X; N += 2) {
            if (!(f[N] & 8)) continue;
            int k1 = 0, k2 = 0, pr = 0;
            for (int i = 0; i < nrows; i++) { uint8_t v = f[N - row[i]]; k1 += v & 1; k2 += (v >> 1) & 1; pr |= v & 4; }
            h[(size_t)k1 * (nrows + 1) + k2][pr ? 0 : 1]++;
        }
        #pragma omp critical
        for (size_t i = 0; i < (size_t)(nrows + 1) * (nrows + 1); i++) { hist[i][0] += h[i][0]; hist[i][1] += h[i][1]; }
        free(h);
    }
    printf("# X=%ld Q=%d z1=%d z=%d rows=%d ; columns: k1 k2 failures successes\n", X, Q, z1, z, nrows);
    for (int a = 0; a <= nrows; a++) for (int b = 0; b <= nrows; b++) {
        long *c = hist[(size_t)a * (nrows + 1) + b]; if (c[0] || c[1]) printf("%d %d %ld %ld\n", a, b, c[0], c[1]);
    }
    return 0;
}
