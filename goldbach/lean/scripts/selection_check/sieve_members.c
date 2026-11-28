// Direct measurement for item 2: for COUNT consecutive members N = N0 + k M of one cover, starting at k = START, the
// number S of rows q with N - q free of prime factors in (463, B], for several B at once (the checkpoints).
// A prime s divides N - q exactly when q = N (mod s); the rows in that class are found by stepping q = c, c + s, ...
// Prints, per checkpoint: members, sum of S, sum of S^2 (to be combined across runs), mean and variance,
// and the histogram of S at the last checkpoint (lines "H value count").
//   gcc -O3 -march=native -o sieve_members sieve_members.c
//   ./sieve_members DIR Q START COUNT B1 B2 ...
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
static uint32_t *load(const char *dir, const char *name, long *n) {
    char p[1024]; snprintf(p, sizeof p, "%s/%s", dir, name); FILE *f = fopen(p, "rb"); if (!f) { perror(p); exit(1); }
    fseek(f, 0, SEEK_END); *n = ftell(f) / 4; fseek(f, 0, SEEK_SET); uint32_t *a = malloc(*n * 4 + 4); if (fread(a, 4, *n, f) != (size_t)*n) exit(1); fclose(f); return a; }
int main(int argc, char **argv) {
    long np, n1, n2, nrows; const char *dir = argv[1]; long Q = atol(argv[2]); unsigned long long start = strtoull(argv[3], 0, 10); long count = atol(argv[4]);
    uint32_t *pr = load(dir, "primes.u32", &np), *r0 = load(dir, "r0.u32", &n1), *m = load(dir, "m.u32", &n2), *rows = load(dir, "rows.u32", &nrows);
    int ncp = argc - 5; double cp[16]; for (int i = 0; i < ncp; i++) cp[i] = atof(argv[5 + i]);
    int32_t *idx = malloc(Q * sizeof(int32_t)); for (long i = 0; i < Q; i++) idx[i] = -1;
    for (long i = 0; i < nrows; i++) idx[rows[i]] = (int32_t)i;
    uint32_t *c = malloc(np * 4); for (long i = 0; i < np; i++) c[i] = (uint32_t)((r0[i] + (start % pr[i]) * (unsigned long long)m[i]) % pr[i]);
    long *stamp = calloc(nrows, sizeof(long)); double sum[16] = {0}, sum2[16] = {0}; long hist_last[4096] = {0};
    for (long k = 0; k < count; k++) { long struck = 0; int j = 0;
        for (long i = 0; i < np; i++) { uint32_t s = pr[i];
            while (j < ncp && s > cp[j]) { double S = (double)(nrows - struck); sum[j] += S; sum2[j] += S * S; j++; }
            for (long q = c[i]; q < Q; q += s) { int32_t t = idx[q]; if (t >= 0 && stamp[t] != k + 1) { stamp[t] = k + 1; struck++; } }
            uint32_t x = c[i] + m[i]; c[i] = x >= s ? x - s : x; }
        while (j < ncp) { double S = (double)(nrows - struck); sum[j] += S; sum2[j] += S * S; j++; }
        if (nrows - struck < 4096) hist_last[nrows - struck]++; }
    for (int j = 0; j < ncp; j++) { double mean = sum[j] / count, var = (sum2[j] - count * mean * mean) / (count - 1);
        printf("B %.6g members %ld sum %.17g sum2 %.17g mean %.4f var %.4f\n", cp[j], count, sum[j], sum2[j], mean, var); }
    for (int v = 0; v < 4096; v++) if (hist_last[v]) printf("H %d %ld\n", v, hist_last[v]);     // S at the last checkpoint
    return 0;
}
