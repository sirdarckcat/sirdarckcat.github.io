// The anatomy of the position on the real cover: for COUNT consecutive members N = N0 + k M (k from START) of one
// cover at 200 digits, the rows struck in each range of primes beyond the line.  For every member and every
// checkpoint B_j the program writes two uint16: the number of rows newly struck by the primes in (B_{j-1}, B_j]
// (new rows only) and the number of strikes by those primes (repeats included, on all rows of the cover).
//   gcc -O3 -march=native -o sieve_profile sieve_profile.c
//   ./sieve_profile DIR Q START COUNT OUT B1 B2 ...      (DIR as written by members.py)
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
static uint32_t *load(const char *dir, const char *name, long *n) {
    char p[1024]; snprintf(p, sizeof p, "%s/%s", dir, name); FILE *f = fopen(p, "rb"); if (!f) { perror(p); exit(1); }
    fseek(f, 0, SEEK_END); *n = ftell(f) / 4; fseek(f, 0, SEEK_SET); uint32_t *a = malloc(*n * 4 + 4); if (fread(a, 4, *n, f) != (size_t)*n) exit(1); fclose(f); return a; }
int main(int argc, char **argv) {
    long np, n1, n2, nrows; const char *dir = argv[1]; long Q = atol(argv[2]); unsigned long long start = strtoull(argv[3], 0, 10); long count = atol(argv[4]);
    FILE *out = fopen(argv[5], "wb");
    uint32_t *pr = load(dir, "primes.u32", &np), *r0 = load(dir, "r0.u32", &n1), *m = load(dir, "m.u32", &n2), *rows = load(dir, "rows.u32", &nrows);
    int ncp = argc - 6; double cp[16]; for (int i = 0; i < ncp; i++) cp[i] = atof(argv[6 + i]);
    int32_t *idx = malloc(Q * sizeof(int32_t)); for (long i = 0; i < Q; i++) idx[i] = -1;
    for (long i = 0; i < nrows; i++) idx[rows[i]] = (int32_t)i;
    uint32_t *c = malloc(np * 4); for (long i = 0; i < np; i++) c[i] = (uint32_t)((r0[i] + (start % pr[i]) * (unsigned long long)m[i]) % pr[i]);
    long *stamp = calloc(nrows, sizeof(long));
    for (long k = 0; k < count; k++) { uint16_t rec[32]; int j = 0; uint16_t newr = 0, hits = 0;
        for (long i = 0; i < np; i++) { uint32_t s = pr[i];
            while (j < ncp && s > cp[j]) { rec[2 * j] = newr; rec[2 * j + 1] = hits; newr = hits = 0; j++; }
            for (long q = c[i]; q < Q; q += s) { int32_t t = idx[q]; if (t >= 0) { hits++; if (stamp[t] != k + 1) { stamp[t] = k + 1; newr++; } } }
            uint32_t x = c[i] + m[i]; c[i] = x >= s ? x - s : x; }
        while (j < ncp) { rec[2 * j] = newr; rec[2 * j + 1] = hits; newr = hits = 0; j++; }
        fwrite(rec, 2, 2 * ncp, out); }
    fclose(out); return 0;
}
