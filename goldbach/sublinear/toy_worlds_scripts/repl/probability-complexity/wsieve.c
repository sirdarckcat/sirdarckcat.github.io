// wsieve IN.bin OUTPREFIX cp1 cp2 ... : exact number of rows of each member k < K with no prime factor in (463, cp]
// at each checkpoint depth cp (ascending), written as uint16 arrays OUTPREFIX.<cp>.u16
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint64_t u64; typedef uint32_t u32;
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb"); u64 h[3]; if (fread(h, 8, 3, f) != 3) return 1;
    u64 nr = h[0], np = h[1], K = h[2];
    u32 *rows = malloc(4 * nr), *P = malloc(4 * np), *n0 = malloc(4 * np), *mi = malloc(4 * np);
    if (fread(rows, 4, nr, f) != nr || fread(P, 4, np, f) != np || fread(n0, 4, np, f) != np || fread(mi, 4, np, f) != np) return 1;
    int ncp = argc - 3; u64 cp[16]; u64 cpi[16];
    for (int c = 0; c < ncp; c++) { cp[c] = strtoull(argv[3 + c], 0, 10); u64 i = 0; while (i < np && P[i] <= cp[c]) i++; cpi[c] = i; }
    u64 W = (K + 63) / 64; int NPL = 11;
    u64 *B = malloc(8 * W); u64 **pl = malloc(sizeof(u64*) * ncp * NPL);
    for (int i = 0; i < ncp * NPL; i++) pl[i] = calloc(W, 8);
    double *pinv = malloc(8 * np); for (u64 i = 0; i < np; i++) pinv[i] = 1.0 / P[i];
    for (u64 r = 0; r < nr; r++) {
        memset(B, 0, 8 * W); u64 q = rows[r]; u64 i = 0;
        for (int c = 0; c < ncp; c++) {
            for (; i < cpi[c]; i++) {
                u64 p = P[i]; u64 a = (q % p + p - n0[i]) % p; u64 b = mi[i];
                u64 ab = a * b; u64 t = (u64)((double)a * (double)b * pinv[i]); int64_t k0 = (int64_t)(ab - t * p);
                while (k0 < 0) k0 += p; while ((u64)k0 >= p) k0 -= p;
                for (u64 k = k0; k < K; k += p) B[k >> 6] |= 1ULL << (k & 63);
            }
            u64 **pp = pl + c * NPL;
            for (u64 w = 0; w < W; w++) { u64 carry = ~B[w]; for (int j = 0; j < NPL && carry; j++) { u64 t = pp[j][w] & carry; pp[j][w] ^= carry; carry = t; } }
        }
        if (r % 100 == 0) { fprintf(stderr, "row %lu/%lu\n", (unsigned long)r, (unsigned long)nr); }
    }
    uint16_t *S = malloc(2 * K);
    for (int c = 0; c < ncp; c++) {
        u64 **pp = pl + c * NPL;
        for (u64 k = 0; k < K; k++) { unsigned v = 0; for (int j = 0; j < NPL; j++) v |= ((pp[j][k >> 6] >> (k & 63)) & 1) << j; S[k] = v; }
        char name[512]; snprintf(name, 512, "%s.%lu.u16", argv[2], (unsigned long)cp[c]); FILE *g = fopen(name, "wb"); fwrite(S, 2, K, g); fclose(g);
    }
    return 0;
}
