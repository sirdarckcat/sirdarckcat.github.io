// The unit of work: one member scored at depth 200.  Times it on the first K members of the member file, two ways:
// from scratch (45 reductions modulo 3..199, 45 three-word ORs, popcount) and continuing from the line (the 37 primes
// 29..199 only, as when the residues up to 23 come with the cover).
//   gcc -O3 -march=native -o unit unit.c && ./unit data/N.u32 20000000
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
typedef struct { uint64_t w[3]; } mask_t;
int main(int argc, char **argv) {
    long K = atol(argv[2]); uint32_t *N = malloc(K * 4); FILE *f = fopen(argv[1], "rb"); if (fread(N, 4, K, f) != (size_t)K) return 1; fclose(f);
    char c[1000] = {0}; int pr[200], np = 0; for (int i = 2; i < 1000; i++) { if (!c[i]) { pr[np++] = i; for (int j = i * i; j < 1000; j += i) c[j] = 1; } }
    int rows[200], nrows = 0; for (int i = 1; i < np; i++) rows[nrows++] = pr[i];
    int sp[64], ns = 0; for (int i = 1; i < np && pr[i] <= 199; i++) sp[ns++] = pr[i];
    mask_t *mk[64]; for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    for (int from = 0; from <= 8; from += 8) { clock_t t0 = clock(); uint64_t sum = 0;
        for (long x = 0; x < K; x++) { uint32_t n = N[x]; mask_t m = {{0, 0, 0}};
            for (int i = from; i < ns; i++) { int a = n % sp[i]; m.w[0] |= mk[i][a].w[0]; m.w[1] |= mk[i][a].w[1]; m.w[2] |= mk[i][a].w[2]; }
            sum += nrows - (__builtin_popcountll(m.w[0]) + __builtin_popcountll(m.w[1]) + __builtin_popcountll(m.w[2])); }
        double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
        printf("%d primes from %d: %ld members in %.3f s, %.1f ns per member (check %llu)\n", ns - from, sp[from], K, sec, 1e9 * sec / K, (unsigned long long)sum); }
    return 0;
}
