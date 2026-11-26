// Exact sieve count of every member of the real window: S_z(k) = rows q with N0 + kM - q free of primes in (463, z].
// Row-oriented: for each row a bitmap over k, bits set at k = (q - N0)/M mod s for each later prime s; bit-sliced counters.
// usage: sieve_exact z1 z2 z3   -> files S_<z>.u16 (rows left per member)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#define PL 11
int main(int argc, char **argv) {
    long K; int nr; long np;
    FILE *f = fopen("meta.txt", "r"); if (fscanf(f, "%ld %d %ld", &K, &nr, &np) != 3) return 1; fclose(f);
    uint32_t *ps = malloc(4 * np), *n0 = malloc(4 * np), *mi = malloc(4 * np), *rows = malloc(4 * nr);
    f = fopen("primes.bin", "rb"); if (fread(ps, 4, np, f) != (size_t)np) return 1; fclose(f);
    f = fopen("n0.bin", "rb"); if (fread(n0, 4, np, f) != (size_t)np) return 1; fclose(f);
    f = fopen("minv.bin", "rb"); if (fread(mi, 4, np, f) != (size_t)np) return 1; fclose(f);
    f = fopen("rows.bin", "rb"); if (fread(rows, 4, nr, f) != (size_t)nr) return 1; fclose(f);
    int nz = argc - 1; long z[8]; long zi[8];
    for (int a = 0; a < nz; a++) { z[a] = atol(argv[a + 1]); long i = 0; while (i < np && ps[i] <= z[a]) i++; zi[a] = i; }
    long W = (K + 63) / 64;
    uint64_t *bm = malloc(8 * W);
    uint64_t *cnt = calloc((size_t)nz * PL * W, 8);
    for (int r = 0; r < nr; r++) {
        memset(bm, 0, 8 * W);
        uint32_t q = rows[r]; long i = 0;
        for (int a = 0; a < nz; a++) {
            for (; i < zi[a]; i++) {
                uint64_t s = ps[i];
                uint64_t d = (q % s + s - n0[i]) % s;
                uint64_t c = d * mi[i] % s;
                for (uint64_t k = c; k < (uint64_t)K; k += s) bm[k >> 6] |= 1ULL << (k & 63);
            }
            uint64_t *C = cnt + (size_t)a * PL * W;
            for (long w = 0; w < W; w++) {          // add bitmap to bit-sliced counter
                uint64_t carry = bm[w];
                for (int p = 0; p < PL && carry; p++) { uint64_t t = C[(size_t)p * W + w]; C[(size_t)p * W + w] = t ^ carry; carry &= t; }
            }
        }
        if (r % 100 == 0) { fprintf(stderr, "row %d\n", r); }
    }
    uint16_t *S = malloc(2 * K);
    for (int a = 0; a < nz; a++) {
        uint64_t *C = cnt + (size_t)a * PL * W;
        for (long k = 0; k < K; k++) { int v = 0; for (int p = 0; p < PL; p++) v |= (int)((C[(size_t)p * W + (k >> 6)] >> (k & 63)) & 1) << p; S[k] = (uint16_t)(nr - v); }
        char name[64]; sprintf(name, "S_%ld.u16", z[a]); f = fopen(name, "wb"); fwrite(S, 2, K, f); fclose(f);
        double m = 0, v2 = 0; int mn = 9999; for (long k = 0; k < K; k++) { m += S[k]; v2 += (double)S[k] * S[k]; if (S[k] < mn) mn = S[k]; }
        m /= K; printf("z = %ld: mean rows left %.3f  sd %.3f  min %d\n", z[a], m, __builtin_sqrt(v2 / K - m * m), mn);
    }
    return 0;
}
