// toy_rem_check.c -- members of the same cover (N and N + 2*3*5*...*z1) in the miniature: do they share anything
// beyond the cover?  Correlation of the rows left at depth z between the two, within each value of the rows left at
// depth z1.   gcc -O3 -march=native -o toy_rem_check toy_rem_check.c -lm ; ./toy_rem_check 1000000000 1000 23 200
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]), z1 = atoi(argv[3]), z = atoi(argv[4]);
    int lim = Q > z ? Q : z; char *comp = calloc(lim + 2, 1);
    for (int i = 2; (long)i * i <= lim; i++) if (!comp[i]) for (int j = i * i; j <= lim; j += i) comp[j] = 1;
    int nrows = 0, *row = malloc((Q + 1) * sizeof(int)); for (int i = 3; i < Q; i++) if (!comp[i]) row[nrows++] = i;
    uint8_t *f = malloc(X + 1); memset(f, 11, X + 1);
    long L = 2; for (int s = 3; s <= z1; s++) if (!comp[s]) L *= s;
    for (int s = 3; s <= z; s++) if (!comp[s]) {
        uint8_t clear = 2; if (s <= z1) clear |= 1;
        for (long x = s; x <= X; x += s) f[x] &= ~clear;
        if (s <= 29) for (long x = s; x <= X; x += s) f[x] &= ~8;
    }
    double n[256] = {0}, sa[256] = {0}, sb[256] = {0}, sab[256] = {0}, saa[256] = {0}, sbb[256] = {0};
    for (long N = (Q + z + 1) & ~1L; N + L < X; N += 2) {
        if (!(f[N] & 8)) continue;
        int k1 = 0, a = 0, b = 0;
        for (int i = 0; i < nrows; i++) { uint8_t v = f[N - row[i]], w = f[N + L - row[i]]; k1 += v & 1; a += (v >> 1) & 1; b += (w >> 1) & 1; }
        n[k1]++; sa[k1] += a; sb[k1] += b; sab[k1] += (double)a * b; saa[k1] += (double)a * a; sbb[k1] += (double)b * b;
    }
    double tn = 0, cov = 0, va = 0, vb = 0;
    printf("step 2*3*...*%d = %ld; pairs (N, N + step) by rows left at depth %d: k1, pairs, mean k2, sd, correlation\n", z1, L, z1);
    for (int k = 0; k < 256; k++) if (n[k] > 1000) {
        double ma = sa[k] / n[k], mb = sb[k] / n[k], c = sab[k] / n[k] - ma * mb, v1 = saa[k] / n[k] - ma * ma, v2 = sbb[k] / n[k] - mb * mb;
        printf("  %3d %10.0f %7.2f %6.2f %7.4f\n", k, n[k], ma, sqrt(v1), c / sqrt(v1 * v2));
        tn += n[k]; cov += n[k] * c; va += n[k] * v1; vb += n[k] * v2;
    }
    printf("pooled within-stratum correlation: %.4f over %.0f pairs\n", cov / sqrt(va * vb), tn);
    return 0;
}
