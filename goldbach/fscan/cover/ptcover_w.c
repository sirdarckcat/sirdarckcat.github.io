/* ptcover_w.c -- ptcover.c with a weight on every row: the energy of a cover is the sum of the weights of its
 * uncovered rows (64 = one full row).  With near-misses reported, a row at q matters in proportion to the chance
 * that the campaign's record ends above q, and brainstorm/soft_weights.py writes those weights.
 *
 *   gcc -O3 -march=native -fopenmp -o ptcover_w ptcover_w.c -lm
 *   ./ptcover_w weights.txt moduli.txt sweeps [seed] [betas.txt]        (weights.txt: lines "q weight", weight 0..64)
 *
 * Everything else is as in ptcover.c, whose header follows; k, <k> and sd(k) are printed in rows (weight / 64).
 *
 * ptcover.c -- parallel tempering on residue covers, and an entropy estimate of the best possible cover.
 *
 * Rows: the odd primes q < Q.  A cover gives one nonzero class a_r to each modulus r (odd primes);
 * row q is covered when q = a_r (mod r) for some r.  Energy = number of uncovered rows (the residual k).
 * A replica at inverse temperature beta makes single-modulus moves with the Metropolis rule; neighbouring
 * replicas are exchanged.  Besides the best cover found, the program prints <k> and var(k) per beta:
 * with S(0) = sum ln(r - 1) (all covers) and dS = beta d<k>, the entropy S(beta) reaches 0 near the
 * ground state, which estimates the smallest k that exists without having to find it.
 *
 *   gcc -O3 -march=native -fopenmp -o ptcover ptcover.c -lm
 *   ./ptcover Q moduli.txt sweeps [seed] [betas.txt]
 * moduli.txt: one modulus per line, optionally followed by a residue; when every line has one, the coldest
 * replica starts from that cover and the others at random.  A sweep is four passes of one attempted move per
 * modulus, in every replica, followed by one round of exchanges.
 * Environment: PT_DUMP=file PT_KDUMP=k appends every distinct cover with at most k uncovered rows that a
 * replica holds at the end of a sweep ("COVER k r:a r:a ..."), for use as independent residue vectors.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>

#define MAXM 256
static int Q, nrows, nmod;
static int *rowq, *roww;
static int mod_[MAXM], init_res[MAXM];
static int **cstart;        /* cstart[m][c] .. cstart[m][c+1]: rows of class c of modulus m */
static int **crows;
static uint16_t **rcls;     /* rcls[m][i] = rowq[i] % mod_[m] */

typedef struct { uint64_t s; } rng_t;
static inline uint64_t rnd(rng_t *r) { r->s ^= r->s << 13; r->s ^= r->s >> 7; r->s ^= r->s << 17; return r->s; }
static inline double rndu(rng_t *r) { return (rnd(r) >> 11) * (1.0 / 9007199254740992.0); }

typedef struct { double beta; int k; int a[MAXM]; uint8_t *cnt; rng_t rng; double sk, skk; long n, acc, tries; int best_k; int best_a[MAXM]; } rep_t;

static int energy(rep_t *R) {
    memset(R->cnt, 0, nrows);
    for (int m = 0; m < nmod; m++) for (int j = cstart[m][R->a[m]]; j < cstart[m][R->a[m] + 1]; j++) R->cnt[crows[m][j]]++;
    int k = 0; for (int i = 0; i < nrows; i++) if (R->cnt[i] == 0) k += roww[i];
    return k;
}
static void sweep(rep_t *R) {
    for (int t = 0; t < nmod; t++) {
        int m = rnd(&R->rng) % nmod, r = mod_[m];
        int c = 1 + rnd(&R->rng) % (r - 2); if (c >= R->a[m]) c++;        /* a nonzero class other than the current one */
        int lose = 0, gain = 0, o = R->a[m];
        for (int j = cstart[m][o]; j < cstart[m][o + 1]; j++) if (R->cnt[crows[m][j]] == 1) lose += roww[crows[m][j]];
        for (int j = cstart[m][c]; j < cstart[m][c + 1]; j++) if (R->cnt[crows[m][j]] == 0) gain += roww[crows[m][j]];
        int d = lose - gain;
        R->tries++;
        if (d <= 0 || rndu(&R->rng) < exp(-R->beta * d / 64.0)) {
            for (int j = cstart[m][o]; j < cstart[m][o + 1]; j++) R->cnt[crows[m][j]]--;
            for (int j = cstart[m][c]; j < cstart[m][c + 1]; j++) R->cnt[crows[m][j]]++;
            R->a[m] = c; R->k += d; R->acc++;
            if (R->k < R->best_k) { R->best_k = R->k; memcpy(R->best_a, R->a, sizeof(int) * nmod); }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: ptcover_w weights.txt moduli.txt sweeps [seed] [betas.txt]   (env PT_DUMP=file PT_KDUMP=k)\n"); return 1; }
    long sweeps = atol(argv[3]); uint64_t seed = argc > 4 ? strtoull(argv[4], 0, 10) : 1;
    { FILE *w = fopen(argv[1], "r"); if (!w) { perror(argv[1]); return 1; } int q, wt, cap = 1 << 16;
      rowq = malloc(sizeof(int) * cap); roww = malloc(sizeof(int) * cap);
      while (fscanf(w, "%d %d", &q, &wt) == 2) if (wt > 0) { if (nrows == cap) { cap *= 2; rowq = realloc(rowq, sizeof(int) * cap); roww = realloc(roww, sizeof(int) * cap); } rowq[nrows] = q; roww[nrows++] = wt; if (q >= Q) Q = q + 1; }
      fclose(w); }
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; }
    char line[256]; int have_init = 1;
    while (fgets(line, sizeof line, f)) { int r, a = -1; int n = sscanf(line, "%d %d", &r, &a); if (n < 1) continue; mod_[nmod] = r; init_res[nmod] = a; if (n < 2) have_init = 0; nmod++; }
    fclose(f);
    cstart = malloc(sizeof(int *) * nmod); crows = malloc(sizeof(int *) * nmod); rcls = malloc(sizeof(uint16_t *) * nmod);
    double S0 = 0;
    for (int m = 0; m < nmod; m++) {
        int r = mod_[m]; S0 += log(r - 1.0);
        cstart[m] = calloc(r + 2, sizeof(int)); crows[m] = malloc(sizeof(int) * nrows); rcls[m] = malloc(2 * nrows);
        for (int i = 0; i < nrows; i++) { rcls[m][i] = rowq[i] % r; cstart[m][rcls[m][i] + 1]++; }
        for (int c = 0; c <= r; c++) cstart[m][c + 1] += cstart[m][c];
        int *pos = malloc(sizeof(int) * (r + 1)); memcpy(pos, cstart[m], sizeof(int) * (r + 1));
        for (int i = 0; i < nrows; i++) crows[m][pos[rcls[m][i]]++] = i;
        free(pos);
    }
    /* temperature ladder */
    double betas[128]; int nrep = 0;
    if (argc > 5) { FILE *g = fopen(argv[5], "r"); double b; while (g && fscanf(g, "%lf", &b) == 1) betas[nrep++] = b; if (g) fclose(g); }
    else { double b[] = {0, .01, .02, .03, .045, .06, .08, .1, .125, .15, .18, .21, .25, .3, .35, .4, .46, .53, .6, .7, .8, .9, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0, 2.4, 3.0, 4.0, 6.0}; nrep = sizeof b / sizeof *b; memcpy(betas, b, sizeof b); }
    rep_t *R = calloc(nrep, sizeof(rep_t));
    for (int i = 0; i < nrep; i++) {
        R[i].beta = betas[i]; R[i].cnt = malloc(nrows); R[i].rng.s = seed * 0x9E3779B97F4A7C15ull + 0x1234567ull * (i + 1); for (int j = 0; j < 20; j++) rnd(&R[i].rng);
        for (int m = 0; m < nmod; m++) R[i].a[m] = (have_init && i == nrep - 1) ? init_res[m] : 1 + (int)(rnd(&R[i].rng) % (mod_[m] - 1));
        R[i].k = energy(&R[i]); R[i].best_k = R[i].k; memcpy(R[i].best_a, R[i].a, sizeof(int) * nmod);
    }
    fprintf(stderr, "rows=%d (up to %d) moduli=%d ln(#covers)=%.2f replicas=%d; weighted rows of the given cover: %.2f\n", nrows, Q - 1, nmod, S0, nrep, have_init ? R[nrep - 1].k / 64.0 : -1.0);
    long burn = sweeps / 4, sw_acc = 0, sw_try = 0; int gbest = 1 << 30; rng_t xr = { seed ^ 0xABCDEFull };
    FILE *dump = getenv("PT_DUMP") ? fopen(getenv("PT_DUMP"), "a") : NULL; int kdump = getenv("PT_KDUMP") ? atoi(getenv("PT_KDUMP")) : -1;
    size_t hcap = 1 << 22, hn = 0; uint64_t *hset = calloc(hcap, 8); long ndump = 0;
    for (long s = 0; s < sweeps; s++) {
        #pragma omp parallel for schedule(dynamic, 1)
        for (int i = 0; i < nrep; i++) { for (int u = 0; u < 4; u++) sweep(&R[i]); if (s >= burn) { R[i].sk += R[i].k / 64.0; R[i].skk += (double)R[i].k * R[i].k / 4096.0; R[i].n++; } }
        for (int i = (int)(s & 1); i + 1 < nrep; i += 2) {               /* replica exchange: swap the temperatures' states */
            double d = (R[i].beta - R[i + 1].beta) * (R[i].k - R[i + 1].k) / 64.0;
            sw_try++;
            if (d >= 0 || rndu(&xr) < exp(d)) {
                int tk = R[i].k; R[i].k = R[i + 1].k; R[i + 1].k = tk;
                uint8_t *tc = R[i].cnt; R[i].cnt = R[i + 1].cnt; R[i + 1].cnt = tc;
                int ta[MAXM]; memcpy(ta, R[i].a, sizeof ta); memcpy(R[i].a, R[i + 1].a, sizeof ta); memcpy(R[i + 1].a, ta, sizeof ta);
                sw_acc++;
            }
        }
        for (int i = 0; i < nrep; i++) if (R[i].k < R[i].best_k) { R[i].best_k = R[i].k; memcpy(R[i].best_a, R[i].a, sizeof(int) * nmod); }
        if (dump) for (int i = 0; i < nrep; i++) if (R[i].k <= kdump * 64 && hn * 2 < hcap) {
            uint64_t h = 1469598103934665603ull; for (int m = 0; m < nmod; m++) { h ^= (uint64_t)R[i].a[m] + 0x9E37ull * m; h *= 1099511628211ull; } if (!h) h = 1;
            size_t p = h & (hcap - 1); while (hset[p] && hset[p] != h) p = (p + 1) & (hcap - 1);
            if (!hset[p]) { hset[p] = h; hn++; ndump++; fprintf(dump, "COVER %.2f", R[i].k / 64.0); for (int m = 0; m < nmod; m++) fprintf(dump, " %d:%d", mod_[m], R[i].a[m]); fprintf(dump, "\n"); }
        }
        if ((s + 1) % (sweeps / 10 ? sweeps / 10 : 1) == 0) {
            int b = 1 << 30; for (int i = 0; i < nrep; i++) if (R[i].best_k < b) b = R[i].best_k;
            if (b < gbest) gbest = b;
            fprintf(stderr, "sweep %ld: best weighted rows so far %.2f; now at the coldest replicas: %.2f %.2f %.2f\n", s + 1, gbest / 64.0, R[nrep - 3].k / 64.0, R[nrep - 2].k / 64.0, R[nrep - 1].k / 64.0);
        }
    }
    /* thermodynamic integration: S(beta_i) = S0 + sum over steps of beta_mid * (E_i - E_{i-1}) */
    printf("# Q=%d rows=%d moduli=%d ln(#covers)=%.3f sweeps=%ld (4 passes each) swap acceptance %.2f\n", Q, nrows, nmod, S0, sweeps, (double)sw_acc / (sw_try ? sw_try : 1));
    printf("# beta   <k>      sd(k)   accept   S(beta)\n");
    double S = S0, Eprev = 0;
    for (int i = 0; i < nrep; i++) {
        double E = R[i].sk / R[i].n, V = R[i].skk / R[i].n - E * E;
        if (i) S += 0.5 * (R[i].beta + R[i - 1].beta) * (E - Eprev);
        Eprev = E;
        printf("%6.3f %9.2f %7.2f  %6.4f  %9.2f\n", R[i].beta, E, sqrt(V > 0 ? V : 0), (double)R[i].acc / R[i].tries, S);
    }
    int bi = 0; for (int i = 0; i < nrep; i++) if (R[i].best_k < R[bi].best_k) bi = i;
    printf("# best weighted rows found: %.2f\n", R[bi].best_k / 64.0);
    if (dump) { fclose(dump); printf("# distinct covers with k <= %d written: %ld\n", kdump, ndump); }
    printf("BEST"); for (int m = 0; m < nmod; m++) printf(" %d:%d", mod_[m], R[bi].best_a[m]); printf("\n");
    return 0;
}
