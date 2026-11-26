// list the best numbers of the miniature: every even N (no prime factor 3..29) with k2 <= kmax, and every true success
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]), z1 = atoi(argv[3]), z = atoi(argv[4]), kmax = atoi(argv[5]);
    int lim = 1; while ((long)lim * lim <= X) lim++; if (lim < Q) lim = Q; if (lim < z) lim = z;
    char *comp = calloc(lim + 2, 1);
    for (int i = 2; (long)i * i <= lim; i++) if (!comp[i]) for (int j = i * i; j <= lim; j += i) comp[j] = 1;
    int nrows = 0, *row = malloc((Q + 1) * sizeof(int)); for (int i = 3; i < Q; i++) if (!comp[i]) row[nrows++] = i;
    uint8_t *f = malloc(X + 1); memset(f, 15, X + 1); f[0] = f[1] = 11;
    for (int s = 3; s <= lim; s++) if (!comp[s]) {
        uint8_t clear = 4; if (s <= z1) clear |= 1; if (s <= z) clear |= 2;
        for (long x = (long)s * (s <= z ? 1 : 2); x <= X; x += s) f[x] &= ~clear;
        if (s <= z) f[s] |= 4;
        if (s <= 29) for (long x = s; x <= X; x += s) f[x] &= ~8;
    }
    for (long x = 4; x <= X; x += 2) f[x] &= ~4;
    #pragma omp parallel for schedule(static)
    for (long N = (Q + z + 1) & ~1L; N < X; N += 2) {
        if (!(f[N] & 8)) continue;
        int k1 = 0, k2 = 0, pr = 0;
        for (int i = 0; i < nrows; i++) { uint8_t v = f[N - row[i]]; k1 += v & 1; k2 += (v >> 1) & 1; pr |= v & 4; }
        if (k2 <= kmax || !pr) {
            #pragma omp critical
            printf("%ld %d %d %d\n", N, k1, k2, pr ? 0 : 1);
        }
    }
    return 0;
}
