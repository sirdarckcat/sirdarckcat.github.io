// evalN.c -- evaluate a given list of members (N/2 as uint32) on the miniature.
// usage: ./evalN X Q members.u32 out.bin
// record (12 bytes): idx u32, k1 u8 (rows alive after odd primes <=23), k199 u8, fsq23 u8, fsq199 u8 (rows forced composite by a square-gap factorisation that are still alive), coh u8, succ u8, pad2
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef struct { uint64_t w[3]; } mask_t;
typedef struct { uint32_t idx; uint8_t k1, k199, f23, f199, coh, s, p0, p1; } rec_t;
static int is_sq(long v) { if (v <= 0) return 0; long r = (long)sqrtl((long double)v); while (r * r > v) r--; while ((r + 1) * (r + 1) <= v) r++; return r * r == v; }
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]);
    FILE *fi = fopen(argv[3], "rb"); fseek(fi, 0, SEEK_END); long M = ftell(fi) / 4; fseek(fi, 0, SEEK_SET); uint32_t *mem = malloc(M * 4); fread(mem, 4, M, fi); fclose(fi);
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    size_t nb = (X >> 1) + 1; uint64_t *bm = malloc((nb / 64 + 1) * 8); memset(bm, 0xff, (nb / 64 + 1) * 8); bm[0] &= ~1ULL;
    for (int i = 1; i < np && (long)pr[i] * pr[i] <= X; i++) { long p = pr[i]; for (long x = p * p; x <= X; x += 2 * p) bm[(x >> 1) >> 6] &= ~(1ULL << ((x >> 1) & 63)); }
    int rows[300], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= 199; i++) sp[ns++] = pr[i];
    mask_t **mk = malloc(ns * sizeof(mask_t *));
    for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int nsh = 0; while (nsh < ns && sp[nsh] <= 23) nsh++;
    int n31 = 0; while (n31 < ns && sp[n31] < 31) n31++;
    rec_t *out = malloc(M * sizeof(rec_t));
    #pragma omp parallel for schedule(static)
    for (long u = 0; u < M; u++) {
        long N = (long)mem[u] * 2; mask_t m = {{0, 0, 0}}; int k1 = 0;
        for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N % sp[i]]; m.w[0] |= e->w[0]; m.w[1] |= e->w[1]; m.w[2] |= e->w[2];
            if (i + 1 == nsh) k1 = nrows - (__builtin_popcountll(m.w[0]) + __builtin_popcountll(m.w[1]) + __builtin_popcountll(m.w[2])); if (i + 1 == nsh) { /* snapshot */ } }
        // recompute snapshots for forced-row accounting
        mask_t m23 = {{0, 0, 0}}; for (int i = 0; i < nsh; i++) { const mask_t *e = &mk[i][N % sp[i]]; m23.w[0] |= e->w[0]; m23.w[1] |= e->w[1]; m23.w[2] |= e->w[2]; }
        int k199 = nrows - (__builtin_popcountll(m.w[0]) + __builtin_popcountll(m.w[1]) + __builtin_popcountll(m.w[2]));
        long mm = (long)sqrtl((long double)N); while (mm * mm > N) mm--; while ((mm + 1) * (mm + 1) <= N) mm++;
        long cab = N - mm * mm, cbe = (mm + 1) * (mm + 1) - N; int f23 = 0, f199 = 0;
        for (int j = 0; j < nrows; j++) { long q = rows[j]; int forced = 0;
            if (cab < Q && is_sq(q - cab)) forced = 1; if (cbe < Q && is_sq(q + cbe)) forced = 1;
            if (forced) { int bit = (m23.w[j >> 6] >> (j & 63)) & 1; if (!bit) f23++; int b2 = (m.w[j >> 6] >> (j & 63)) & 1; if (!b2) f199++; } }
        // coherence index: max over t in (Q, 2Q] of #{primes 31..199 dividing N - t}
        static __thread unsigned char cntt[2100]; memset(cntt, 0, sizeof(cntt)); int coh = 0;
        for (int i = n31; i < ns; i++) { int p = sp[i]; int r = (int)(N % p); int t0 = Q + 1; int off = ((r - t0) % p + p) % p; for (int t = t0 + off; t <= 2 * Q; t += p) { if (++cntt[t] > coh) coh = cntt[t]; } }
        int anyprime = 0; for (int j = 0; j < nrows; j++) { long v = N - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) { anyprime = 1; break; } }
        rec_t r = { mem[u], (uint8_t)k1, (uint8_t)k199, (uint8_t)f23, (uint8_t)f199, (uint8_t)coh, (uint8_t)(!anyprime), 0, 0 }; out[u] = r;
    }
    FILE *fo = fopen(argv[4], "wb"); fwrite(out, sizeof(rec_t), M, fo); fclose(fo); return 0;
}
