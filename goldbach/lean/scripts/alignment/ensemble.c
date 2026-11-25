// The residue-vector ensemble of a miniature: the same joint histogram as truth2.c, but over class vectors drawn
// uniformly at random (nonzero classes for the primes up to ZMEM, any class beyond) instead of over the even N below X.
// If the N below X are a fair sample of the class vectors (the assumption behind every count made by reweighting
// class vectors), the two histograms agree level by level, in the tail as in the bulk.
//   gcc -O3 -march=native -o ensemble ensemble.c
//   ./ensemble Q Z1 ZMEM Z SAMPLES SEED OUT      writes OUT.hist (text: k1 k2 count 0)
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define W 5
typedef struct { uint64_t w[W]; } mask_t;
static inline int pc(const mask_t *m) { int s = 0; for (int i = 0; i < W; i++) s += __builtin_popcountll(m->w[i]); return s; }
static uint64_t st[4];
static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static inline uint64_t rnd(void) { uint64_t r = rotl(st[1] * 5, 7) * 9, t = st[1] << 17; st[2] ^= st[0]; st[3] ^= st[1]; st[1] ^= st[2]; st[0] ^= st[3]; st[2] ^= t; st[3] = rotl(st[3], 45); return r; }
static uint64_t sm(uint64_t *x) { uint64_t z = (*x += 0x9e3779b97f4a7c15ULL); z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; return z ^ (z >> 31); }
int main(int argc, char **argv) {
    long Q = atol(argv[1]); int z1 = atoi(argv[2]), zmem = atoi(argv[3]), z = atoi(argv[4]);
    unsigned long long n = strtoull(argv[5], 0, 10), seed = strtoull(argv[6], 0, 10); char path[512];
    for (int i = 0; i < 4; i++) st[i] = sm((uint64_t *)&seed);
    int lim = 4000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    int rows[320], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    if (nrows > 64 * W) return 1;
    int ns = 0, sp[128]; for (int i = 1; i < np && pr[i] <= z; i++) sp[ns++] = pr[i];
    mask_t *mk[128]; for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int n1 = 0; while (n1 < ns && sp[n1] <= z1) n1++;
    int nmem = 0; while (nmem < ns && sp[nmem] <= zmem) nmem++;
    mask_t full; memset(&full, 0, sizeof full); for (int j = 0; j < nrows; j++) full.w[j >> 6] |= 1ULL << (j & 63);
    static long cnt[330][330];
    for (unsigned long long it = 0; it < n; it++) {
        mask_t m = full; int k1 = 0;
        for (int i = 0; i < ns; i++) {
            int a = i < nmem ? 1 + (int)(((__uint128_t)rnd() * (uint64_t)(sp[i] - 1)) >> 64) : (int)(((__uint128_t)rnd() * (uint64_t)sp[i]) >> 64);
            const mask_t *cm = &mk[i][a]; for (int t = 0; t < W; t++) m.w[t] &= ~cm->w[t]; if (i == n1 - 1) k1 = pc(&m); }
        cnt[k1][pc(&m)]++;
    }
    snprintf(path, 512, "%s.hist", argv[7]); FILE *fh = fopen(path, "w");
    for (int a = 0; a < 330; a++) for (int b = 0; b < 330; b++) if (cnt[a][b]) fprintf(fh, "%d %d %ld 0\n", a, b, cnt[a][b]);
    fclose(fh); return 0;
}
