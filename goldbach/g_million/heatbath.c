/* heatbath.c -- T5: annealing of a cover (fewest rows left) with heat-bath moves.
 * Rows: odd primes q < Q. Moduli: from the start cover (r:a pairs). For a modulus r with class a: loss = rows of class a covered
 * only by r; gain(c) = uncovered rows in class c. Moving to c changes k (rows left) by loss - gain(c) (0 for c = a). Every visit
 * samples c with weight exp(-beta * dk), exactly (the classes with no uncovered row form one bucket of equal weight), so the cost
 * of a visit is one pass over the uncovered rows. beta goes from beta0 to beta1 geometrically over the sweeps; the best cover seen
 * is written out. Class 0 is never used.
 *   ./heatbath Q start.txt sweeps beta0 beta1 seed out.txt
 *   gcc -O3 -march=native -o heatbath heatbath.c -lm
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
    if (argc < 8) { fprintf(stderr, "usage: heatbath Q start.txt sweeps beta0 beta1 seed out.txt\n"); return 1; }
    int Q = atoi(argv[1]); long sweeps = atol(argv[3]); double b0 = atof(argv[4]), b1 = atof(argv[5]); rs = 0x9E3779B97F4A7C15ull ^ (uint64_t)atoll(argv[6]);
    /* start cover */
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; }
    int cap = 4096, nm = 0; int *mod = malloc(4 * cap), *cls = malloc(4 * cap); char w[64];
    while (fscanf(f, "%63s", w) == 1) { int r, a; if (sscanf(w, "%d:%d", &r, &a) == 2) { if (nm == cap) { cap *= 2; mod = realloc(mod, 4 * cap); cls = realloc(cls, 4 * cap); } mod[nm] = r; cls[nm] = a; nm++; } }
    fclose(f);
    /* rows */
    char *comp = calloc(Q + 1, 1); for (long i = 2; i * i <= Q; i++) if (!comp[i]) for (long j = i * i; j <= Q; j += i) comp[j] = 1;
    int nr = 0; for (int i = 3; i < Q; i++) if (!comp[i]) nr++;
    int *row = malloc(4 * nr); nr = 0; for (int i = 3; i < Q; i++) if (!comp[i]) row[nr++] = i;
    free(comp);
    /* rows by class for every modulus (CSR) */
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
    /* uncovered rows: a list with positions */
    int *ul = malloc(4 * nr), *upos = malloc(4 * nr), nu = 0;
    for (int i = 0; i < nr; i++) { upos[i] = -1; if (!cnt[i]) { upos[i] = nu; ul[nu++] = i; } }
    int *g = calloc(maxr, 4), *touched = malloc(4 * (size_t)(nr + 1)); double *wt = malloc(sizeof(double) * (size_t)(nr + 2));
    int best = nu; int *bestcls = malloc(4 * nm); memcpy(bestcls, cls, 4 * nm);
    fprintf(stderr, "%d rows, %d moduli; start: %d rows left\n", nr, nm, nu);
    int *order = malloc(4 * nm); for (int m = 0; m < nm; m++) order[m] = m;
    for (long sw = 0; sw < sweeps; sw++) {
        double beta = b0 * pow(b1 / b0, sweeps > 1 ? (double)sw / (sweeps - 1) : 1.0);
        for (int m = nm - 1; m > 0; m--) { int j = rnd() % (m + 1), t = order[m]; order[m] = order[j]; order[j] = t; }
        for (int oi = 0; oi < nm; oi++) {
            int m = order[oi], r = mod[m], a = cls[m];
            int loss = 0; for (int j = off[m][a]; j < off[m][a + 1]; j++) loss += cnt[lst[m][j]] == 1;
            int nt = 0;
            for (int u = 0; u < nu; u++) { int c = row[ul[u]] % r; if (!g[c]++) touched[nt++] = c; }
            /* weights: stay (dk = 0), each touched class c != 0, a (dk = loss - g[c]), and the bucket of untouched classes (dk = loss) */
            double tot = 1.0; int nz = 0;
            for (int t = 0; t < nt; t++) { int c = touched[t]; double x = (c == 0 || c == a) ? 0.0 : exp(-beta * (loss - g[c])); wt[t] = x; tot += x; if (c != 0 && c != a) nz++; }
            int untouched = (r - 1) - nz - 1;             /* nonzero classes other than a with no uncovered row */
            double wb = untouched > 0 ? untouched * exp(-beta * loss) : 0.0; tot += wb;
            double x = rndu() * tot; int newc = a;
            if (x >= 1.0) {
                x -= 1.0; int t = 0;
                for (; t < nt; t++) { if (x < wt[t]) break; x -= wt[t]; }
                if (t < nt) newc = touched[t];
                else if (untouched > 0) {                   /* a random nonzero class, not a, with no uncovered row */
                    for (;;) { int c = 1 + rnd() % (r - 1); if (c != a && g[c] == 0) { newc = c; break; } }
                }
            }
            for (int t = 0; t < nt; t++) g[touched[t]] = 0;
            if (newc != a) {
                for (int j = off[m][a]; j < off[m][a + 1]; j++) { int i = lst[m][j]; if (--cnt[i] == 0) { upos[i] = nu; ul[nu++] = i; } }
                for (int j = off[m][newc]; j < off[m][newc + 1]; j++) { int i = lst[m][j]; if (cnt[i]++ == 0) { int p = upos[i], last = ul[--nu]; ul[p] = last; upos[last] = p; upos[i] = -1; } }
                cls[m] = newc;
                if (nu < best) { best = nu; memcpy(bestcls, cls, 4 * nm); }
            }
        }
        if ((sw + 1) % (sweeps / 20 ? sweeps / 20 : 1) == 0) fprintf(stderr, "sweep %ld beta %.3f: %d rows left, best %d\n", sw + 1, beta, nu, best);
    }
    FILE *o = fopen(argv[7], "w");
    fprintf(o, "# Q = %d; %d moduli; rows in no class: %d (heatbath: %ld sweeps, beta %.3f -> %.3f, seed %s, from %s)\n", Q, nm, best, sweeps, b0, b1, argv[6], argv[2]);
    for (int m = 0; m < nm; m++) fprintf(o, "%d:%d ", mod[m], bestcls[m]);
    fprintf(o, "\n"); fclose(o);
    printf("best %d\n", best);
    return 0;
}
