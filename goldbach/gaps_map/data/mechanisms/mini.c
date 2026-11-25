// mini.c -- per-candidate data for the miniature (every even N < X with no prime factor in 3..29).
// For each such N writes: N/2 (uint32), rows left (k) at depths DEPTHS[], success flag (g(N) >= Q).
// rows left at depth d = number of odd primes q < Q with N - q free of odd prime factors <= d.
// usage: ./mini X Q outprefix        (writes outprefix.idx.u32, outprefix.k.u8 (ND bytes per N), outprefix.s.u8)
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { uint64_t w[3]; } mask_t;
static const int DEPTHS[] = {23, 31, 43, 61, 97, 199};
#define ND 6
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]); char *pre = argv[3];
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    size_t nb = (X >> 1) + 1; uint64_t *bm = malloc((nb / 64 + 1) * 8); memset(bm, 0xff, (nb / 64 + 1) * 8);
    bm[0] &= ~1ULL;                                        // bit i <-> odd number 2i+1 is prime (until crossed out); 1 is not prime
    for (int i = 1; i < np && (long)pr[i] * pr[i] <= X; i++) { long p = pr[i];
        for (long x = p * p; x <= X; x += 2 * p) bm[(x >> 1) >> 6] &= ~(1ULL << ((x >> 1) & 63)); }
    int rows[300], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    if (nrows > 192) { fprintf(stderr, "too many rows\n"); return 1; }
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= 199; i++) sp[ns++] = pr[i];   // odd primes 3..199
    mask_t **mk = malloc(ns * sizeof(mask_t *));
    for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t));
        for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int nsmall = 0; while (nsmall < ns && sp[nsmall] <= 29) nsmall++;           // primes 3..29: N must avoid them
    int dstop[ND]; for (int d = 0; d < ND; d++) { int s = 0; while (s < ns && sp[s] <= DEPTHS[d]) s++; dstop[d] = s; }
    long Nlo = (Q + 200 + 1) & ~1L;
    long total = (X - Nlo) / 2 + 1;
    // pass 1: count allowed N per chunk
    int nth = omp_get_max_threads(); long chunk = (total + nth - 1) / nth;
    long *cnt = calloc(nth + 1, sizeof(long));
    #pragma omp parallel for
    for (int t = 0; t < nth; t++) { long a = Nlo + 2 * (t * chunk), b = Nlo + 2 * ((t + 1) * chunk); if (b > X) b = X; long n = 0;
        for (long N = a; N < b; N += 2) { int ok = 1; for (int i = 0; i < nsmall; i++) if (N % sp[i] == 0) { ok = 0; break; } n += ok; } cnt[t + 1] = n; }
    for (int t = 0; t < nth; t++) cnt[t + 1] += cnt[t];
    long M = cnt[nth];
    uint32_t *idx = malloc(M * 4); uint8_t *kk = malloc(M * ND); uint8_t *ss = malloc(M);
    #pragma omp parallel for
    for (int t = 0; t < nth; t++) {
        long a = Nlo + 2 * (t * chunk), b = Nlo + 2 * ((t + 1) * chunk); if (b > X) b = X; long o = cnt[t];
        for (long N = a; N < b; N += 2) {
            int ok = 1; for (int i = 0; i < nsmall; i++) if (N % sp[i] == 0) { ok = 0; break; } if (!ok) continue;
            mask_t m = {{0, 0, 0}}; int d = 0; uint8_t *kp = kk + o * ND;
            for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N % sp[i]]; m.w[0] |= e->w[0]; m.w[1] |= e->w[1]; m.w[2] |= e->w[2];
                while (d < ND && i + 1 == dstop[d]) { kp[d] = (uint8_t)(nrows - (__builtin_popcountll(m.w[0]) + __builtin_popcountll(m.w[1]) + __builtin_popcountll(m.w[2]))); d++; } }
            int anyprime = 0;
            for (int j = 0; j < nrows; j++) { long mm = N - rows[j]; if ((bm[(mm >> 1) >> 6] >> ((mm >> 1) & 63)) & 1) { anyprime = 1; break; } }
            idx[o] = (uint32_t)(N >> 1); ss[o] = anyprime ? 0 : 1; o++;
        }
    }
    char fn[512]; FILE *f;
    sprintf(fn, "%s.idx.u32", pre); f = fopen(fn, "wb"); fwrite(idx, 4, M, f); fclose(f);
    sprintf(fn, "%s.k.u8", pre); f = fopen(fn, "wb"); fwrite(kk, 1, (size_t)M * ND, f); fclose(f);
    sprintf(fn, "%s.s.u8", pre); f = fopen(fn, "wb"); fwrite(ss, 1, M, f); fclose(f);
    long succ = 0; for (long i = 0; i < M; i++) succ += ss[i];
    printf("X=%ld Q=%d rows=%d allowed=%ld successes=%ld depths:", X, Q, nrows, M, succ); for (int d = 0; d < ND; d++) printf(" %d", DEPTHS[d]); printf("\n");
    return 0;
}
