// A second miniature without the member file: joint histogram of (rows left at the line, rows left at depth z) over the
// members, with the number of successes in each cell of the histogram, and the list of the best members.
// Rows: odd primes below Q.  Members: even N in [lo, hi) with no prime factor from 3 to ZMEM (lo at least Q + z + 1).
// k1 = rows left at depth Z1 (the line), k2 = rows left at depth Z; success: N - q composite for every row q.
// Processes the slice [A, B) of N; slices are added up by miniature2.py.
//   gcc -O3 -march=native -o truth2 truth2.c
//   ./truth2 Q Z1 ZMEM Z A B TIER OUT      writes OUT.hist (text) and OUT.top (text: N k1 k2 success, for k2 <= TIER)
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define W 5
typedef struct { uint64_t w[W]; } mask_t;
static inline int pc(const mask_t *m) { int s = 0; for (int i = 0; i < W; i++) s += __builtin_popcountll(m->w[i]); return s; }
int main(int argc, char **argv) {
    long Q = atol(argv[1]); int z1 = atoi(argv[2]), zmem = atoi(argv[3]), z = atoi(argv[4]);
    unsigned long long A = strtoull(argv[5], 0, 10), B = strtoull(argv[6], 0, 10); int tier = atoi(argv[7]); char path[512];
    int lim = 400000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    int rows[320], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    if (nrows > 64 * W) return 1;
    int ns = 0, sp[128]; for (int i = 1; i < np && pr[i] <= z; i++) sp[ns++] = pr[i];
    mask_t *mk[128]; for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int n1 = 0; while (n1 < ns && sp[n1] <= z1) n1++;
    int nmem = 0; while (nmem < ns && sp[nmem] <= zmem) nmem++;
    mask_t full; memset(&full, 0, sizeof full); for (int j = 0; j < nrows; j++) full.w[j >> 6] |= 1ULL << (j & 63);
    unsigned long long lo = (Q + z + 1) & ~1ULL; if (A < lo) A = lo; A += A & 1;
    // odd numbers in [A - Q - 2, B): bit set = prime
    unsigned long long base = (A > (unsigned long long)Q + 2 ? A - Q - 2 : 1) | 1; size_t nb = (B - base) / 2 + 2; uint64_t *bm = malloc((nb / 64 + 2) * 8); memset(bm, 0xff, (nb / 64 + 2) * 8);
    for (int i = 1; i < np && (unsigned long long)pr[i] * pr[i] < B; i++) { unsigned long long p = pr[i], x = ((base + p - 1) / p) * p; if (x < p * p) x = p * p; if (!(x & 1)) x += p;
        for (; x < B; x += 2 * p) { size_t b = (x - base) / 2; bm[b >> 6] &= ~(1ULL << (b & 63)); } }
    if (base == 1) bm[0] &= ~1ULL;
    static long cnt[330][330], suc[330][330];
    snprintf(path, 512, "%s.top", argv[8]); FILE *ft = fopen(path, "w");
    int r[128]; for (int i = 0; i < ns; i++) r[i] = (int)(A % sp[i]);
    for (unsigned long long N = A; N < B; N += 2) {
        int ok = 1; for (int i = 0; i < nmem; i++) if (r[i] == 0) { ok = 0; break; }
        if (ok) { mask_t m = full; int k1 = 0;
            for (int i = 0; i < ns; i++) { const mask_t *cm = &mk[i][r[i]]; for (int t = 0; t < W; t++) m.w[t] &= ~cm->w[t]; if (i == n1 - 1) k1 = pc(&m); }
            int k2 = pc(&m), s = 1;
            for (int t = 0; t < W && s; t++) { uint64_t x = m.w[t]; while (x) { int j = t * 64 + __builtin_ctzll(x); x &= x - 1; unsigned long long v = N - rows[j]; size_t b = (v - base) / 2; if (bm[b >> 6] >> (b & 63) & 1) { s = 0; break; } } }
            cnt[k1][k2]++; suc[k1][k2] += s; if (k2 <= tier) fprintf(ft, "%llu %d %d %d\n", N, k1, k2, s); }
        for (int i = 0; i < ns; i++) { r[i] += 2; if (r[i] >= sp[i]) r[i] -= sp[i]; }
    }
    fclose(ft); snprintf(path, 512, "%s.hist", argv[8]); FILE *fh = fopen(path, "w");
    for (int a = 0; a < 330; a++) for (int b = 0; b < 330; b++) if (cnt[a][b]) fprintf(fh, "%d %d %ld %ld\n", a, b, cnt[a][b], suc[a][b]);
    fclose(fh); return 0;
}
