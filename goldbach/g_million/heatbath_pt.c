/* heatbath_pt.c -- T5: replica exchange with heat-bath moves for covers (fewest rows left), as the research session suggested.
 * Same move as heatbath.c (every visit to a modulus samples its new class over all r - 1 classes with weight exp(-beta * dk),
 * exactly), in nb chains at fixed betas (one sweep each per round), then exchanges of neighbouring chains with probability
 * min(1, exp((beta_i - beta_j)(k_i - k_j))). The chains run in parallel (OpenMP). The best cover seen is written out, with the
 * exchange acceptance per pair of neighbours.
 *   ./heatbath_pt Q start.txt betas.txt rounds seed out.txt
 *   gcc -O3 -march=native -fopenmp -o heatbath_pt heatbath_pt.c -lm
 */
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { uint64_t s; int *cls; uint8_t *cnt; int *ul, *upos, nu; int *g, *touched; double *wt; } chain_t;
static inline uint64_t rnd(uint64_t *s) { *s ^= *s << 13; *s ^= *s >> 7; *s ^= *s << 17; return *s; }
static inline double rndu(uint64_t *s) { return (rnd(s) >> 11) * (1.0 / 9007199254740992.0); }

static int nm, nr, *mod, *row, **off, **lst;

static void sweep(chain_t *C, double beta) {
    for (int oi = 0; oi < nm; oi++) {
        int m = rnd(&C->s) % nm, r = mod[m], a = C->cls[m];
        int loss = 0; for (int j = off[m][a]; j < off[m][a + 1]; j++) loss += C->cnt[lst[m][j]] == 1;
        int nt = 0;
        for (int u = 0; u < C->nu; u++) { int c = row[C->ul[u]] % r; if (!C->g[c]++) C->touched[nt++] = c; }
        double tot = 1.0; int nz = 0;
        for (int t = 0; t < nt; t++) { int c = C->touched[t]; double x = (c == 0 || c == a) ? 0.0 : exp(-beta * (loss - C->g[c])); C->wt[t] = x; tot += x; if (c != 0 && c != a) nz++; }
        int untouched = (r - 1) - nz - 1; double wb = untouched > 0 ? untouched * exp(-beta * loss) : 0.0; tot += wb;
        double x = rndu(&C->s) * tot; int newc = a;
        if (x >= 1.0) {
            x -= 1.0; int t = 0;
            for (; t < nt; t++) { if (x < C->wt[t]) break; x -= C->wt[t]; }
            if (t < nt) newc = C->touched[t];
            else if (untouched > 0) for (;;) { int c = 1 + rnd(&C->s) % (r - 1); if (c != a && C->g[c] == 0) { newc = c; break; } }
        }
        for (int t = 0; t < nt; t++) C->g[C->touched[t]] = 0;
        if (newc != a) {
            for (int j = off[m][a]; j < off[m][a + 1]; j++) { int i = lst[m][j]; if (--C->cnt[i] == 0) { C->upos[i] = C->nu; C->ul[C->nu++] = i; } }
            for (int j = off[m][newc]; j < off[m][newc + 1]; j++) { int i = lst[m][j]; if (C->cnt[i]++ == 0) { int p = C->upos[i], last = C->ul[--C->nu]; C->ul[p] = last; C->upos[last] = p; C->upos[i] = -1; } }
            C->cls[m] = newc;
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: heatbath_pt Q start.txt betas.txt rounds seed out.txt\n"); return 1; }
    int Q = atoi(argv[1]); long rounds = atol(argv[4]); uint64_t seed = (uint64_t)atoll(argv[5]);
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; }
    int cap = 4096; mod = malloc(4 * cap); int *cls0 = malloc(4 * cap); char w[64]; nm = 0;
    while (fscanf(f, "%63s", w) == 1) { int r, a; if (sscanf(w, "%d:%d", &r, &a) == 2) { if (nm == cap) { cap *= 2; mod = realloc(mod, 4 * cap); cls0 = realloc(cls0, 4 * cap); } mod[nm] = r; cls0[nm] = a; nm++; } }
    fclose(f);
    double beta[512]; int nb = 0; f = fopen(argv[3], "r"); if (!f) { perror(argv[3]); return 1; }
    while (nb < 512 && fscanf(f, "%lf", &beta[nb]) == 1) nb++; fclose(f);
    char *comp = calloc(Q + 1, 1); for (long i = 2; i * i <= Q; i++) if (!comp[i]) for (long j = i * i; j <= Q; j += i) comp[j] = 1;
    nr = 0; for (int i = 3; i < Q; i++) if (!comp[i]) nr++;
    row = malloc(4 * nr); nr = 0; for (int i = 3; i < Q; i++) if (!comp[i]) row[nr++] = i; free(comp);
    off = malloc(sizeof(int *) * nm); lst = malloc(sizeof(int *) * nm); int maxr = 0;
    for (int m = 0; m < nm; m++) {
        int r = mod[m]; if (r > maxr) maxr = r;
        int *c = calloc(r + 1, 4); for (int i = 0; i < nr; i++) c[row[i] % r + 1]++;
        for (int a = 0; a < r; a++) c[a + 1] += c[a];
        off[m] = malloc(4 * (r + 1)); memcpy(off[m], c, 4 * (r + 1)); lst[m] = malloc(4 * nr);
        for (int i = 0; i < nr; i++) lst[m][c[row[i] % r]++] = i;
        free(c);
    }
    chain_t *C = calloc(nb, sizeof(chain_t)); int *at = malloc(4 * nb);   /* at[i] = chain sitting at beta i */
    for (int b = 0; b < nb; b++) {
        chain_t *c = &C[b]; c->s = 0x9E3779B97F4A7C15ull * (seed + 1) + 7919ull * (b + 1);
        c->cls = malloc(4 * nm); memcpy(c->cls, cls0, 4 * nm); c->cnt = calloc(nr, 1);
        for (int m = 0; m < nm; m++) for (int j = off[m][c->cls[m]]; j < off[m][c->cls[m] + 1]; j++) c->cnt[lst[m][j]]++;
        c->ul = malloc(4 * nr); c->upos = malloc(4 * nr); c->nu = 0;
        for (int i = 0; i < nr; i++) { c->upos[i] = -1; if (!c->cnt[i]) { c->upos[i] = c->nu; c->ul[c->nu++] = i; } }
        c->g = calloc(maxr, 4); c->touched = malloc(4 * (size_t)(nr + 1)); c->wt = malloc(sizeof(double) * (size_t)(nr + 2)); at[b] = b;
    }
    int best = C[0].nu; int *bestcls = malloc(4 * nm); memcpy(bestcls, cls0, 4 * nm);
    long *acc = calloc(nb, sizeof(long)), *tries = calloc(nb, sizeof(long)); uint64_t xs = seed * 2654435761ull + 1;
    fprintf(stderr, "%d rows, %d moduli, %d chains (beta %.3f .. %.3f), %d threads; start: %d rows left\n", nr, nm, nb, beta[0], beta[nb - 1], omp_get_max_threads(), best);
    double t0 = omp_get_wtime();
    for (long rd = 0; rd < rounds; rd++) {
        #pragma omp parallel for schedule(dynamic, 1)
        for (int b = 0; b < nb; b++) sweep(&C[at[b]], beta[b]);
        for (int b = 0; b < nb; b++) if (C[at[b]].nu < best) { best = C[at[b]].nu; memcpy(bestcls, C[at[b]].cls, 4 * nm); }
        for (int b = (int)(rd & 1); b + 1 < nb; b += 2) {
            double d = (beta[b + 1] - beta[b]) * (C[at[b + 1]].nu - C[at[b]].nu);
            tries[b]++;
            if (d >= 0 || rndu(&xs) < exp(d)) { int t = at[b]; at[b] = at[b + 1]; at[b + 1] = t; acc[b]++; }
        }
        if ((rd + 1) % (rounds / 20 ? rounds / 20 : 1) == 0) {
            fprintf(stderr, "round %ld (%.0f s): best %d; k at beta:", rd + 1, omp_get_wtime() - t0, best);
            for (int b = 0; b < nb; b += (nb > 12 ? nb / 12 : 1)) fprintf(stderr, " %.2f:%d", beta[b], C[at[b]].nu);
            fprintf(stderr, " %.2f:%d\n", beta[nb - 1], C[at[nb - 1]].nu);
        }
    }
    FILE *o = fopen(argv[6], "w");
    fprintf(o, "# Q = %d; %d moduli; rows in no class: %d (heatbath_pt: %d chains beta %.3f..%.3f, %ld rounds, seed %s, from %s); exchange acceptance:", Q, nm, best, nb, beta[0], beta[nb - 1], rounds, argv[5], argv[2]);
    for (int b = 0; b + 1 < nb; b++) fprintf(o, " %.2f", tries[b] ? (double)acc[b] / tries[b] : -1.0);
    fprintf(o, "\n"); for (int m = 0; m < nm; m++) fprintf(o, "%d:%d ", mod[m], bestcls[m]); fprintf(o, "\n"); fclose(o);
    printf("best %d\n", best);
    return 0;
}
