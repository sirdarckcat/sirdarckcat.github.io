/* heatbath_w.c -- heat-bath annealing of a cover for a weighted target. Rows: odd primes q < Qmax; a row q < Qlo weighs 1, a row
 * Qlo <= q < Qmax weighs w. The objective is the weighted count of rows in no class. The move is heatbath2.c's: every visit to a
 * modulus samples its new class over all r - 1 nonzero classes with weight exp(-beta * dk), exactly, where dk = loss - gain(c), loss is
 * the weight of the rows of the current class covered by this modulus alone, and gain(c) is the weight of the rows in no class that
 * lie in class c. The classes holding no such row form one bucket. Weights are taken relative to the best option, so nothing
 * overflows. The best cover seen is written out, with its weighted count and the plain count of rows below Qlo and below Qmax.
 *   ./heatbath_w Qlo Qmax w start.txt sweeps beta0 beta1 seed out.txt
 *   gcc -O3 -march=native -o heatbath_w heatbath_w.c -lm
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t rs;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double rndu(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

int main(int argc, char **argv) {
    if (argc < 10) { fprintf(stderr, "usage: heatbath_w Qlo Qmax w start.txt sweeps beta0 beta1 seed out.txt\n"); return 1; }
    int Qlo = atoi(argv[1]), Q = atoi(argv[2]); double wq = atof(argv[3]); long sweeps = atol(argv[5]);
    double b0 = atof(argv[6]), b1 = atof(argv[7]); rs = 0x9E3779B97F4A7C15ull ^ (uint64_t)atoll(argv[8]);
    FILE *f = fopen(argv[4], "r"); if (!f) { perror(argv[4]); return 1; }
    int cap = 4096, nm = 0; int *mod = malloc(4 * cap), *cls = malloc(4 * cap); char w[64];
    while (fscanf(f, "%63s", w) == 1) { int r, a; if (sscanf(w, "%d:%d", &r, &a) == 2) { mod[nm] = r; cls[nm] = a; nm++; } }
    fclose(f);
    char *comp = calloc(Q + 1, 1); for (long i = 2; i * i <= Q; i++) if (!comp[i]) for (long j = i * i; j <= Q; j += i) comp[j] = 1;
    int nr = 0; for (int i = 3; i < Q; i++) if (!comp[i]) nr++;
    int *row = malloc(4 * nr); double *wt_row = malloc(sizeof(double) * nr); nr = 0;
    for (int i = 3; i < Q; i++) if (!comp[i]) { row[nr] = i; wt_row[nr] = i < Qlo ? 1.0 : wq; nr++; }
    free(comp);
    int **off = malloc(sizeof(int *) * nm), **lst = malloc(sizeof(int *) * nm); int maxr = 0;
    for (int m = 0; m < nm; m++) {
        int r = mod[m]; if (r > maxr) maxr = r;
        int *c = calloc(r + 1, 4); for (int i = 0; i < nr; i++) c[row[i] % r + 1]++;
        for (int a = 0; a < r; a++) c[a + 1] += c[a];
        off[m] = malloc(4 * (r + 1)); memcpy(off[m], c, 4 * (r + 1)); lst[m] = malloc(4 * nr);
        for (int i = 0; i < nr; i++) lst[m][c[row[i] % r]++] = i;
        free(c);
    }
    uint8_t *cnt = calloc(nr, 1);
    for (int m = 0; m < nm; m++) for (int j = off[m][cls[m]]; j < off[m][cls[m] + 1]; j++) cnt[lst[m][j]]++;
    int *ul = malloc(4 * nr), *upos = malloc(4 * nr), nu = 0; double obj = 0;
    for (int i = 0; i < nr; i++) { upos[i] = -1; if (!cnt[i]) { upos[i] = nu; ul[nu++] = i; obj += wt_row[i]; } }
    double *g = calloc(maxr, sizeof(double)); int *seen = calloc(maxr, 4); int *touched = malloc(4 * (size_t)(nr + 1));
    double *wt = malloc(sizeof(double) * (size_t)(nr + 2));
    double best = obj; int *bestcls = malloc(4 * nm); memcpy(bestcls, cls, 4 * nm);
    fprintf(stderr, "%d rows (%d below %d), %d moduli; start: weighted %.2f (%d rows in no class)\n", nr, Qlo, Qlo, nm, obj, nu);
    int *order = malloc(4 * nm); for (int m = 0; m < nm; m++) order[m] = m;
    for (long sw = 0; sw < sweeps; sw++) {
        double beta = b0 * pow(b1 / b0, sweeps > 1 ? (double)sw / (sweeps - 1) : 1.0);
        for (int m = nm - 1; m > 0; m--) { int j = rnd() % (m + 1), t = order[m]; order[m] = order[j]; order[j] = t; }
        for (int oi = 0; oi < nm; oi++) {
            int m = order[oi], r = mod[m], a = cls[m];
            double loss = 0; for (int j = off[m][a]; j < off[m][a + 1]; j++) { int i = lst[m][j]; if (cnt[i] == 1) loss += wt_row[i]; }
            int nt = 0;
            for (int u = 0; u < nu; u++) { int i = ul[u]; int c = row[i] % r; if (!seen[c]) { seen[c] = 1; touched[nt++] = c; } g[c] += wt_row[i]; }
            double dmin = 0; int nz = 0;                                   /* the best option: stay (0), a class, or the bucket (loss) */
            for (int t = 0; t < nt; t++) { int c = touched[t]; if (c != 0 && c != a) { nz++; if (loss - g[c] < dmin) dmin = loss - g[c]; } }
            int untouched = (r - 1) - nz - 1;
            double wstay = exp(-beta * (0 - dmin)), tot = wstay;
            for (int t = 0; t < nt; t++) { int c = touched[t]; double x = (c == 0 || c == a) ? 0.0 : exp(-beta * (loss - g[c] - dmin)); wt[t] = x; tot += x; }
            double wb = untouched > 0 ? untouched * exp(-beta * (loss - dmin)) : 0.0; tot += wb;
            double x = rndu() * tot; int newc = a;
            if (x >= wstay) {
                x -= wstay; int t = 0;
                for (; t < nt; t++) { if (x < wt[t]) break; x -= wt[t]; }
                if (t < nt) newc = touched[t];
                else if (untouched > 0) for (;;) { int c = 1 + rnd() % (r - 1); if (c != a && !seen[c]) { newc = c; break; } }
            }
            for (int t = 0; t < nt; t++) { g[touched[t]] = 0; seen[touched[t]] = 0; }
            if (newc != a) {
                for (int j = off[m][a]; j < off[m][a + 1]; j++) { int i = lst[m][j]; if (--cnt[i] == 0) { upos[i] = nu; ul[nu++] = i; obj += wt_row[i]; } }
                for (int j = off[m][newc]; j < off[m][newc + 1]; j++) { int i = lst[m][j]; if (cnt[i]++ == 0) { int p = upos[i], last = ul[--nu]; ul[p] = last; upos[last] = p; upos[i] = -1; obj -= wt_row[i]; } }
                cls[m] = newc;
                if (obj < best - 1e-9) { best = obj; memcpy(bestcls, cls, 4 * nm); }
            }
        }
        if ((sw + 1) % (sweeps / 10 ? sweeps / 10 : 1) == 0) fprintf(stderr, "sweep %ld beta %.3f: weighted %.2f, best %.2f\n", sw + 1, beta, obj, best);
    }
    /* plain counts of the best cover */
    int below_lo = 0, below_q = 0;
    for (int i = 0; i < nr; i++) {
        int alive = 1; for (int m = 0; m < nm && alive; m++) if (row[i] % mod[m] == bestcls[m]) alive = 0;
        if (alive) { below_q++; if (row[i] < Qlo) below_lo++; }
    }
    FILE *o = fopen(argv[9], "w");
    fprintf(o, "# weighted target: rows below %d weigh 1, rows in [%d, %d) weigh %g; weighted rows in no class %.2f; rows below %d: %d, below %d: %d (heatbath_w: %ld sweeps, beta %.2f -> %.2f, seed %s, from %s)\n",
            Qlo, Qlo, Q, wq, best, Qlo, below_lo, Q, below_q, sweeps, b0, b1, argv[8], argv[4]);
    fprintf(o, "COVER %d ", below_lo);
    for (int m = 0; m < nm; m++) fprintf(o, "%d:%d ", mod[m], bestcls[m]);
    fprintf(o, "\n"); fclose(o);
    printf("best weighted %.2f; rows below %d: %d; below %d: %d\n", best, Qlo, below_lo, Q, below_q);
    return 0;
}
