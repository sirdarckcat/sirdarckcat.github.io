// Question 2: small instances, enumerated completely.
//
// Rows: the odd primes q < Q.  Moduli: the odd primes p_1 = 3 < p_2 < ... < p_k.  Candidates: every even N in [0, X).
// score_j(N) = number of rows q with N - q divisible by none of p_1 .. p_j  ("rows left at depth p_j").
// The line: l = the largest j with 2 p_1 ... p_j <= X; M = 2 p_1 ... p_l; a cell is a class of N modulo M (a vector of
// classes of the first l primes; every vector occurs), its design value is score_l, the same for all its members.
//
// For every depth j the program prints
//   OPT_j     the least score_j over all candidates below X (the true optimum), how many N reach it;
//   D_j       the least score_j over ALL class vectors of the first j primes (N below 2 p_1 ... p_j), when that is
//             small enough to enumerate: what a cover on j primes could do if X allowed it;
//   and, in terms of the cells: the best design value D_l; over the members of the best cells, the least, the mean
//   and the largest score_j (pinning with a full scan of the window, and pinning without a choice inside it); and
//   the design value of the best cell that contains a true optimum, with the number of cells at least as good
//   (how deep in the cover-first order the optimum sits).
// With a file name as last argument the optimal N of the deepest level are written there.
//   gcc -O3 -march=native -o tiny tiny.c
//   ./tiny Q X k [DEEPEST_FULL_TORUS_J] [OUTFILE]
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define W 4
typedef struct { uint64_t w[W]; } mask_t;
static inline int pc(const mask_t *m) { int s = 0; for (int i = 0; i < W; i++) s += __builtin_popcountll(m->w[i]); return s; }
int main(int argc, char **argv) {
    long Q = atol(argv[1]); unsigned long long X = strtoull(argv[2], 0, 10); int k = atoi(argv[3]); int fullj = argc > 4 ? atoi(argv[4]) : 0;
    static char comp[100000]; int pr[2000], np = 0; for (int i = 2; i < 100000 && np < 2000; i++) { if (!comp[i]) { pr[np++] = i; for (long j = (long)i * i; j < 100000; j += i) comp[j] = 1; } }
    int rows[256], n = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[n++] = pr[i];
    if (n > 64 * W) { fprintf(stderr, "too many rows\n"); return 1; }
    int p[64]; for (int j = 0; j < k; j++) p[j] = pr[j + 1];
    mask_t *mk[64]; for (int j = 0; j < k; j++) { mk[j] = calloc(p[j], sizeof(mask_t)); for (int i = 0; i < n; i++) mk[j][rows[i] % p[j]].w[i >> 6] |= 1ULL << (i & 63); }
    mask_t full; memset(&full, 0, sizeof full); for (int i = 0; i < n; i++) full.w[i >> 6] |= 1ULL << (i & 63);
    int l = 0; unsigned long long M = 2; while (l < k && M * p[l] <= X) { M *= p[l]; l++; }
    printf("Q = %ld (%d rows), moduli 3..%d (%d), X = %llu; line after %d (l = %d), M = %llu, window X/M = %.3f; next prime %d\n", Q, n, p[k - 1], k, X, l ? p[l - 1] : 2, l, M, (double)X / M, l < k ? p[l] : 0);
    // pass over all even N < X
    int opt[64]; long nopt[64]; for (int j = 0; j < k; j++) { opt[j] = 1 << 30; nopt[j] = 0; }
    static int best[260][64]; static long cnt[260]; static double sum[260][64]; static int worst[260][64];
    for (int d = 0; d < 260; d++) for (int j = 0; j < 64; j++) { best[d][j] = 1 << 30; worst[d][j] = -1; }
    int r[64]; for (int j = 0; j < k; j++) r[j] = 0;
    for (unsigned long long N = 0; N < X; N += 2) {
        mask_t m = full; int sc[64];
        for (int j = 0; j < k; j++) { const mask_t *c = &mk[j][r[j]]; for (int i = 0; i < W; i++) m.w[i] &= ~c->w[i]; sc[j] = pc(&m); }
        for (int j = 0; j < k; j++) { if (sc[j] < opt[j]) { opt[j] = sc[j]; nopt[j] = 1; } else if (sc[j] == opt[j]) nopt[j]++; }
        if (l > 0) { int d = sc[l - 1]; cnt[d]++; for (int j = l; j < k; j++) { if (sc[j] < best[d][j]) best[d][j] = sc[j]; if (sc[j] > worst[d][j]) worst[d][j] = sc[j]; sum[d][j] += sc[j]; } }
        for (int j = 0; j < k; j++) { r[j] += 2; if (r[j] >= p[j]) r[j] -= p[j]; }
    }
    int Dl = 0; while (l > 0 && cnt[Dl] == 0) Dl++;
    double mem_per_cell = (double)X / M;
    printf("best design value at the line D_l = %d: %ld members = %.1f cells\n", Dl, cnt[Dl], cnt[Dl] / mem_per_cell);
    // full torus optimum for depths beyond the line
    int Dfull[64]; for (int j = 0; j < k; j++) Dfull[j] = -1;
    for (int j = l; j < k && j < fullj; j++) { unsigned long long P = 2; for (int i = 0; i <= j; i++) P *= p[i];
        int rr[64]; for (int i = 0; i <= j; i++) rr[i] = 0; int bestv = 1 << 30;
        for (unsigned long long N = 0; N < P; N += 2) { mask_t m = full; for (int i = 0; i <= j; i++) { const mask_t *c = &mk[i][rr[i]]; for (int t = 0; t < W; t++) m.w[t] &= ~c->w[t]; }
            int v = pc(&m); if (v < bestv) bestv = v; for (int i = 0; i <= j; i++) { rr[i] += 2; if (rr[i] >= p[i]) rr[i] -= p[i]; } }
        Dfull[j] = bestv; }
    printf("depth | primes beyond the line | OPT (N reaching it) | best cover on these primes with no bound on N | best cells scanned: least | mean | largest | design value of the best cell holding an optimum | cells at least that good | members in them\n");
    for (int j = 0; j < k; j++) {
        if (j < l) { printf("%d | - | %d (%ld) | %d | | | | | |\n", p[j], opt[j], nopt[j], opt[j]); continue; }
        int dopt = Dl; while (best[dopt][j] != opt[j]) dopt++;
        long mem = 0; for (int d = 0; d <= dopt; d++) mem += cnt[d];
        char buf[64]; if (Dfull[j] >= 0) snprintf(buf, 32, "%d", Dfull[j]); else snprintf(buf, 32, "?");
        printf("%d | %d | %d (%ld) | %s | %d | %.2f | %d | %d | %.1f | %ld\n", p[j], j - l + 1, opt[j], nopt[j], buf, best[Dl][j], sum[Dl][j] / cnt[Dl], worst[Dl][j], dopt, mem / mem_per_cell, mem);
    }
    // optional: the optimal N of the deepest level
    if (argc > 5) { FILE *f = fopen(argv[5], "w"); for (int j = 0; j < k; j++) r[j] = 0;
        for (unsigned long long N = 0; N < X; N += 2) { mask_t m = full; int dl = -1;
            for (int j = 0; j < k; j++) { const mask_t *c = &mk[j][r[j]]; for (int i = 0; i < W; i++) m.w[i] &= ~c->w[i]; if (j == l - 1) dl = pc(&m); }
            if (pc(&m) == opt[k - 1]) { fprintf(f, "%llu %d", N, dl); for (int j = 0; j < k; j++) fprintf(f, " %d", r[j]); fprintf(f, "\n"); }
            for (int j = 0; j < k; j++) { r[j] += 2; if (r[j] >= p[j]) r[j] -= p[j]; } }
        fclose(f); }
    return 0;
}
