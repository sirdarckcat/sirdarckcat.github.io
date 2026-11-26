// exact sieve count S_z(k) = #{rows q : N0 + k M - q has no prime factor r, 463 < r <= z}, every k < K, several depths z
// usage: ./sieve params.txt Z   -> writes S_<depth>.u16 for depths 1e3,1e4,...,<=Z
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef uint64_t u64; typedef uint32_t u32; typedef unsigned __int128 u128;
static char buf[1 << 22];
static u32 limbsN[64], limbsM[64]; static int nN, nM;
static int hex2limbs(const char *s, u32 *L) { // most significant first
    int len = strlen(s); while (len && (s[len-1] == '\n' || s[len-1] == ' ')) len--;
    int n = (len + 7) / 8, pos = 0, first = len - 8 * (n - 1);
    for (int i = 0; i < n; i++) { int w = i ? 8 : first; char t[9]; memcpy(t, s + pos, w); t[w] = 0; L[i] = (u32)strtoul(t, 0, 16); pos += w; }
    return n; }
static u32 modlimbs(const u32 *L, int n, u32 r) { u64 x = 0; for (int i = 0; i < n; i++) x = ((x << 32) | L[i]) % r; return (u32)x; }
static u32 invmod(u32 a, u32 r) { int64_t t = 0, nt = 1, x = r, nx = a; while (nx) { int64_t q = x / nx, tmp = t - q * nt; t = nt; nt = tmp; tmp = x - q * nx; x = nx; nx = tmp; } if (t < 0) t += r; return (u32)t; }
typedef struct { u32 r, n0, inv; u64 mu; } __attribute__((packed)) P;
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); u64 Z = strtoull(argv[2], 0, 10);
    fgets(buf, sizeof buf, f); nN = hex2limbs(buf, limbsN); fgets(buf, sizeof buf, f); nM = hex2limbs(buf, limbsM);
    u64 K; int nr; fscanf(f, "%lu %d", &K, &nr); u32 *rows = malloc(4 * nr); for (int i = 0; i < nr; i++) fscanf(f, "%u", rows + i);
    // primes 467..Z
    char *sv = calloc(Z + 1, 1); u64 np = 0; for (u64 i = 2; i * i <= Z; i++) if (!sv[i]) for (u64 j = i * i; j <= Z; j += i) sv[j] = 1;
    for (u64 i = 467; i <= Z; i++) if (!sv[i]) np++;
    P *pr = malloc(np * sizeof(P)); np = 0;
    for (u64 i = 467; i <= Z; i++) if (!sv[i]) { u32 r = i; pr[np].r = r; pr[np].n0 = modlimbs(limbsN, nN, r); pr[np].inv = invmod(modlimbs(limbsM, nM, r), r); pr[np].mu = (u64)(((u128)1 << 64) / r); np++; }
    free(sv); fprintf(stderr, "K=%lu rows=%d primes=%lu\n", K, nr, np);
    u64 depths[8]; int nd = 0; for (u64 d = 1000; d <= Z; d *= 10) depths[nd++] = d;
    u64 W = (K + 63) / 64; u64 *B = malloc(8 * W); int NP = 11;
    u64 *pl = calloc((u64)nd * NP * W, 8);
    for (int qi = 0; qi < nr; qi++) {
        u32 q = rows[qi]; memset(B, 0, 8 * W); int d = 0;
        for (u64 i = 0; i <= np; i++) {
            while (d < nd && (i == np || pr[i].r > depths[d])) { // accumulate struck bits into counter d
                u64 *base = pl + (u64)d * NP * W;
                for (u64 w = 0; w < W; w++) { u64 c = B[w]; for (int j = 0; c && j < NP; j++) { u64 t = base[(u64)j * W + w]; base[(u64)j * W + w] = t ^ c; c &= t; } }
                d++; }
            if (i == np) break;
            u32 r = pr[i].r; u32 a = q % r; a = a >= pr[i].n0 ? a - pr[i].n0 : a + r - pr[i].n0;
            u64 x = (u64)a * pr[i].inv; u64 qq = (u64)(((u128)x * pr[i].mu) >> 64); u64 k = x - qq * r; if (k >= r) k -= r;
            for (; k < K; k += r) B[k >> 6] |= 1ULL << (k & 63);
        }
        if (qi % 100 == 0) fprintf(stderr, "row %d\n", qi);
    }
    unsigned short *S = malloc(2 * K);
    for (int d = 0; d < nd; d++) { u64 *base = pl + (u64)d * NP * W; double s = 0, s2 = 0; int mn = 1 << 30;
        for (u64 k = 0; k < K; k++) { int c = 0; for (int j = 0; j < NP; j++) c |= ((base[(u64)j * W + (k >> 6)] >> (k & 63)) & 1) << j; c = nr - c; S[k] = c; s += c; s2 += (double)c * c; if (c < mn) mn = c; }
        char nm[64]; sprintf(nm, "S_%lu.u16", depths[d]); FILE *o = fopen(nm, "wb"); fwrite(S, 2, K, o); fclose(o);
        printf("depth %lu mean %.4f sd %.4f min %d\n", depths[d], s / K, __builtin_sqrt(s2 / K - (s / K) * (s / K)), mn); }
    return 0; }
