/* cover_ils.c -- iterated local search for residue covers of the odd primes below Q (the g >= Q game).
 *
 * Rows: odd primes q < Q.  A cover gives each modulus r (odd primes) one nonzero class a_r; row q is covered when
 * q = a_r (mod r) for some r.  k = number of uncovered rows.  (The energy of ../ptcover/ptcover_fast.c.)
 *
 * Local search: for a modulus m, the rows it would gain in class c are the uncovered rows with q = c (mod r): one pass
 * over the k uncovered rows gives the gain of every class at once; the rows it loses are those of its class covered by
 * nothing else.  A pass visits the moduli in random order and moves each to its best class when that lowers k (and, with
 * probability PSIDE, when it keeps k: plateau moves).  Passes repeat until one makes no strict improvement.
 * Iterated: a kick reassigns KICK random moduli (small moduli are picked with probability proportional to 1/r^ALPHA)
 * to random classes, then local search; the result is kept if k <= the current k + slack (slack drawn from an
 * exponential with mean TEMP), else the state is restored.  The best cover is printed as a BEST line.
 *
 *   gcc -O3 -march=native -o cover_ils cover_ils.c -lm
 *   ./cover_ils Q moduli.txt seconds [seed] [kick] [temp] [alpha]      (moduli.txt: "r" or "r a" per line)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>

#define MAXM 512
static int Q, nrows, nmod, mod_[MAXM], init_res[MAXM];
static int *rowq;
static uint16_t **rcls;          /* rcls[m][i] = rowq[i] % r */
static int **cstart, **crows;    /* rows of class c of modulus m */
static uint8_t *cnt;             /* covers of each row */
static int *ulist, *upos, nunc;  /* uncovered rows: list and position (-1 if covered) */
static int a[MAXM];
static uint64_t rs = 88172645463325252ull;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double rndu(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

static inline void unc_add(int i) { upos[i] = nunc; ulist[nunc++] = i; }
static inline void unc_del(int i) { int p = upos[i], j = ulist[--nunc]; ulist[p] = j; upos[j] = p; upos[i] = -1; }

static void set_class(int m, int c) {
    int o = a[m];
    if (o == c) return;
    for (int j = cstart[m][o]; j < cstart[m][o + 1]; j++) { int i = crows[m][j]; if (--cnt[i] == 0) unc_add(i); }
    for (int j = cstart[m][c]; j < cstart[m][c + 1]; j++) { int i = crows[m][j]; if (cnt[i]++ == 0) unc_del(i); }
    a[m] = c;
}
static void rebuild(void) {
    memset(cnt, 0, nrows);
    for (int m = 0; m < nmod; m++) for (int j = cstart[m][a[m]]; j < cstart[m][a[m] + 1]; j++) cnt[crows[m][j]]++;
    nunc = 0;
    for (int i = 0; i < nrows; i++) { upos[i] = -1; if (!cnt[i]) unc_add(i); }
}
static int gainbuf[200000];
/* best class for modulus m: returns delta (new k - old k) and the class */
static int best_move(int m, int *cbest, int allow_tie) {
    int r = mod_[m], o = a[m];
    int lose = 0;
    for (int j = cstart[m][o]; j < cstart[m][o + 1]; j++) lose += cnt[crows[m][j]] == 1;
    int *g = gainbuf;
    memset(g, 0, sizeof(int) * r);
    const uint16_t *rc = rcls[m];
    for (int t = 0; t < nunc; t++) g[rc[ulist[t]]]++;
    int bg = -1, bc = o, ties = 0;
    for (int c = 1; c < r; c++) {
        if (c == o) continue;
        if (g[c] > bg) { bg = g[c]; bc = c; ties = 1; }
        else if (g[c] == bg && allow_tie && (rnd() % ++ties) == 0) bc = c;
    }
    *cbest = bc;
    return lose - bg;
}
static int order[MAXM];
static void local_search(double pside) {
    for (;;) {
        int improved = 0;
        for (int t = nmod - 1; t > 0; t--) { int u = rnd() % (t + 1), x = order[t]; order[t] = order[u]; order[u] = x; }
        for (int t = 0; t < nmod; t++) {
            int m = order[t], c;
            int d = best_move(m, &c, 1);
            if (d < 0) { set_class(m, c); improved = 1; }
            else if (d == 0 && c != a[m] && rndu() < pside) set_class(m, c);
        }
        if (!improved) break;
    }
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: cover_ils Q moduli.txt seconds [seed] [kick] [temp] [alpha] [pside]\n"); return 1; }
    Q = atoi(argv[1]); double secs = atof(argv[3]);
    uint64_t seed = argc > 4 ? strtoull(argv[4], 0, 10) : 1;
    int kick = argc > 5 ? atoi(argv[5]) : 3;
    double temp = argc > 6 ? atof(argv[6]) : 1.0, alpha = argc > 7 ? atof(argv[7]) : 0.5, pside = argc > 8 ? atof(argv[8]) : 0.3;
    rs ^= seed * 0x9E3779B97F4A7C15ull; for (int i = 0; i < 20; i++) rnd();
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; }
    char line[256]; int have_init = 1;
    while (fgets(line, sizeof line, f)) {
        int r, x = -1, n = sscanf(line, "%d %d", &r, &x);
        if (n < 1) { /* maybe r:a tokens */ continue; }
        mod_[nmod] = r; init_res[nmod] = x; if (n < 2) have_init = 0; nmod++;
    }
    fclose(f);
    char *sv = calloc(Q + 1, 1); rowq = malloc(sizeof(int) * (Q / 2 + 2));
    for (int i = 2; i < Q; i++) if (!sv[i]) { if (i > 2) rowq[nrows++] = i; for (long j = (long)i * i; j < Q; j += i) sv[j] = 1; }
    rcls = malloc(sizeof(uint16_t *) * nmod); cstart = malloc(sizeof(int *) * nmod); crows = malloc(sizeof(int *) * nmod);
    for (int m = 0; m < nmod; m++) {
        int r = mod_[m];
        rcls[m] = malloc(2 * nrows); cstart[m] = calloc(r + 2, sizeof(int)); crows[m] = malloc(sizeof(int) * nrows);
        for (int i = 0; i < nrows; i++) { rcls[m][i] = rowq[i] % r; cstart[m][rcls[m][i] + 1]++; }
        for (int c = 0; c <= r; c++) cstart[m][c + 1] += cstart[m][c];
        int *pos = malloc(sizeof(int) * (r + 1)); memcpy(pos, cstart[m], sizeof(int) * (r + 1));
        for (int i = 0; i < nrows; i++) crows[m][pos[rcls[m][i]]++] = i;
        free(pos);
    }
    cnt = calloc(nrows, 1); ulist = malloc(sizeof(int) * nrows); upos = malloc(sizeof(int) * nrows);
    for (int m = 0; m < nmod; m++) { order[m] = m; a[m] = have_init ? init_res[m] : 1 + (int)(rnd() % (mod_[m] - 1)); }
    rebuild();
    fprintf(stderr, "Q=%d rows=%d moduli=%d start k=%d (%s)\n", Q, nrows, nmod, nunc, have_init ? "given cover" : "random");
    /* pick weights for kicks */
    double *w = malloc(sizeof(double) * nmod), wsum = 0;
    for (int m = 0; m < nmod; m++) { w[m] = pow(mod_[m], -alpha); wsum += w[m]; }
    local_search(pside);
    int cur = nunc, best = nunc, bestA[MAXM], saveA[MAXM];
    memcpy(bestA, a, sizeof a);
    double t0 = now(), tlast = t0; long it = 0, acc = 0;
    while (now() - t0 < secs) {
        memcpy(saveA, a, sizeof(int) * nmod);
        int kk = 1 + (int)(rnd() % kick);
        for (int t = 0; t < kk; t++) {
            double u = rndu() * wsum; int m = 0; while (m < nmod - 1 && (u -= w[m]) > 0) m++;
            set_class(m, 1 + (int)(rnd() % (mod_[m] - 1)));
        }
        local_search(pside);
        it++;
        double slack = temp > 0 ? -temp * log(1 - rndu()) : 0;
        if (nunc <= cur + slack) { cur = nunc; acc++; }
        else { for (int m = 0; m < nmod; m++) if (a[m] != saveA[m]) set_class(m, saveA[m]); cur = nunc; }
        if (cur < best) { best = cur; memcpy(bestA, a, sizeof a); fprintf(stderr, "%.1fs it %ld: best k %d\n", now() - t0, it, best); }
        if (now() - tlast > 30) { tlast = now(); fprintf(stderr, "%.0fs: %ld kicks (%.0f/s), accepted %.2f, current k %d, best %d\n", now() - t0, it, it / (now() - t0), (double)acc / it, cur, best); }
    }
    printf("# Q=%d moduli=%d kicks=%ld best k found: %d\n", Q, nmod, it, best);
    printf("BEST"); for (int m = 0; m < nmod; m++) printf(" %d:%d", mod_[m], bestA[m]); printf("\n");
    /* check */
    memcpy(a, bestA, sizeof a); rebuild();
    if (nunc != best) { fprintf(stderr, "CHECK FAILED %d %d\n", nunc, best); return 2; }
    return 0;
}
