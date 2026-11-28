// The tier of the residue-vector ensemble, prime by prime: class vectors drawn uniformly at random as in ensemble.c;
// for those with at most TIER rows left at full depth, the means of
//   before_s  rows left by the primes below s,          gain_s  rows of them in the class of s,
//   others_s  rows left by all the primes except s,     only_s  rows of them in the class of s (struck by s alone).
//   gcc -O3 -march=native -o ensemble_tier ensemble_tier.c
//   ./ensemble_tier Q ZMEM Z TIER SAMPLES SEED OUT      writes OUT.tier (text: s count sum_before sum_gain sum_others sum_only)
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
    long Q = atol(argv[1]); int zmem = atoi(argv[2]), z = atoi(argv[3]), tier = atoi(argv[4]);
    unsigned long long n = strtoull(argv[5], 0, 10), seed = strtoull(argv[6], 0, 10); char path[512];
    for (int i = 0; i < 4; i++) st[i] = sm((uint64_t *)&seed);
    int lim = 4000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    int rows[320], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    if (nrows > 64 * W) return 1;
    int ns = 0, sp[128]; for (int i = 1; i < np && pr[i] <= z; i++) sp[ns++] = pr[i];
    mask_t *mk[128]; for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int nmem = 0; while (nmem < ns && sp[nmem] <= zmem) nmem++;
    mask_t full; memset(&full, 0, sizeof full); for (int j = 0; j < nrows; j++) full.w[j >> 6] |= 1ULL << (j & 63);
    static long cnt, sb[128], sg[128], so[128], su[128]; int a[128]; mask_t pre[129], suf[129];
    for (unsigned long long it = 0; it < n; it++) {
        mask_t m = full;
        for (int i = 0; i < ns; i++) {
            a[i] = i < nmem ? 1 + (int)(((__uint128_t)rnd() * (uint64_t)(sp[i] - 1)) >> 64) : (int)(((__uint128_t)rnd() * (uint64_t)sp[i]) >> 64);
            const mask_t *cm = &mk[i][a[i]]; for (int t = 0; t < W; t++) m.w[t] &= ~cm->w[t]; }
        if (pc(&m) > tier) continue;
        cnt++; pre[0] = full; for (int i = 0; i < ns; i++) { for (int t = 0; t < W; t++) pre[i + 1].w[t] = pre[i].w[t] & ~mk[i][a[i]].w[t]; }
        suf[ns] = full; for (int i = ns - 1; i >= 0; i--) { for (int t = 0; t < W; t++) suf[i].w[t] = suf[i + 1].w[t] & ~mk[i][a[i]].w[t]; }
        for (int i = 0; i < ns; i++) { mask_t g, o, u; for (int t = 0; t < W; t++) { g.w[t] = pre[i].w[t] & mk[i][a[i]].w[t]; o.w[t] = pre[i].w[t] & suf[i + 1].w[t]; u.w[t] = o.w[t] & mk[i][a[i]].w[t]; }
            sb[i] += pc(&pre[i]); sg[i] += pc(&g); so[i] += pc(&o); su[i] += pc(&u); }
    }
    snprintf(path, 512, "%s.tier", argv[7]); FILE *fh = fopen(path, "w");
    for (int i = 0; i < ns; i++) fprintf(fh, "%d %ld %ld %ld %ld %ld\n", sp[i], cnt, sb[i], sg[i], so[i], su[i]);
    fclose(fh); return 0;
}
