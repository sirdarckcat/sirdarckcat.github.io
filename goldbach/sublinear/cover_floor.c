// cover_floor.c -- a floor under every cover: how few rows can ANY choice of classes leave?
//
// For a set of moduli (odd primes s) and a target Q, a cover is a class a_s for every s, and its energy is the number
// k of rows (odd primes q < Q) that lie in none of the classes.  The search programs find covers with few rows; this
// one measures, by parallel tempering at ALL temperatures, the partition function Z(b) = sum over all covers of
// exp(-b k).  Since Z(b) >= exp(-b kmin), every b gives a floor
//
//     kmin >= -ln Z(b) / b = <k>_b - S(b)/b
//
// (S(b) = ln Z(b) + b <k>_b, the logarithm of the effective number of covers at that temperature).  ln Z(0) is the
// logarithm of the number of covers, known exactly, and ln Z(b) follows from the samples (cover_floor.py).  The floor
// needs no search to succeed: it holds for every cover, found or not, as far as the samples up to that b are in
// equilibrium.  That is tested from both sides: a run started from random covers can only be too high in k where it
// is out of equilibrium, a run started from the best cover known (a start file) too low.
//
//   gcc -O3 -march=native -fopenmp -o cover_floor cover_floor.c -lm
//   ./cover_floor Q moduli.txt betas.txt sweeps burn out.txt [seed] [start.txt]
//
// moduli.txt: the moduli, white space between them.  start.txt: r:a pairs (other words are ignored), the cover every
// replica starts from; without it every replica starts from a random cover.  Every class of every modulus is
// allowed, zero included, so the states are all residue vectors and their number is the product of the moduli.
//
// Weighted rows: with the environment variable COVER_FLOOR_WEIGHTS=file ("q weight" lines, 64 = a full row, as
// written by ../fscan/cover/brainstorm/soft_weights.py) the rows are the primes of that file, whatever Q, and the
// energy is the weighted number of rows left, the campaign's measure of a cover.  Energies are then printed in rows
// with two decimals and the histogram is in bins of a quarter of a row, each printed at the mean energy of its samples.
// Output: per temperature the mean of k (also over four consecutive quarters of the run, to show drift), the
// histogram of k after the burn-in and the acceptance rates; with a start file also, per quarter, on how many of the
// first 12 moduli the replica at that temperature still has the class of the start cover.
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
typedef struct { uint64_t s[4]; } rng_t;
static inline uint64_t rnd(rng_t *r) {
    uint64_t *s = r->s, res = rotl(s[1] * 5, 7) * 9, t = s[1] << 17;
    s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]; s[2] ^= t; s[3] = rotl(s[3], 45);
    return res;
}
static inline double rnd01(rng_t *r) { return (rnd(r) >> 11) * (1.0 / 9007199254740992.0); }
static uint64_t splitmix(uint64_t *x) { uint64_t z = (*x += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }

#define MAXROWS 65535
#define NQ 4
#define NCORE 12
typedef struct { uint16_t *a; uint8_t *cnt; int E; rng_t rng; } rep_t;

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: %s Q moduli.txt betas.txt sweeps burn out.txt [seed] [start.txt]\n", argv[0]); return 1; }
    int Q = atoi(argv[1]); long sweeps = atol(argv[4]), burn = atol(argv[5]);
    uint64_t seed = argc > 7 ? strtoull(argv[7], 0, 10) : 1;
    int mod[4096], nmod = 0; { FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; } while (nmod < 4096 && fscanf(f, "%d", &mod[nmod]) == 1) nmod++; fclose(f); }
    double beta[4096]; int nb = 0; { FILE *f = fopen(argv[3], "r"); if (!f) { perror(argv[3]); return 1; } while (nb < 4096 && fscanf(f, "%lf", &beta[nb]) == 1) nb++; fclose(f); }
    if (nmod < 1 || nb < 2 || beta[0] != 0) { fprintf(stderr, "need moduli, and betas starting at 0\n"); return 1; }
    int nrows = 0, *row = NULL, *wt = NULL, weighted = 0; const char *wfile = getenv("COVER_FLOOR_WEIGHTS");
    if (wfile && *wfile) {
        FILE *f = fopen(wfile, "r"); if (!f) { perror(wfile); return 1; }
        row = malloc((MAXROWS + 1) * sizeof(int)); wt = malloc((MAXROWS + 1) * sizeof(int)); int q, w;
        while (nrows < MAXROWS && fscanf(f, "%d %d", &q, &w) == 2) if (w > 0) { row[nrows] = q; wt[nrows] = w; nrows++; }
        fclose(f); weighted = 1;
    } else {
        char *comp = calloc(Q + 1, 1);
        for (int i = 2; (long)i * i <= Q; i++) if (!comp[i]) for (int j = i * i; j <= Q; j += i) comp[j] = 1;
        for (int i = 3; i < Q; i++) if (!comp[i]) nrows++;
        if (nrows > MAXROWS) { fprintf(stderr, "too many rows\n"); return 1; }
        row = malloc(nrows * sizeof(int)); wt = malloc(nrows * sizeof(int)); nrows = 0; for (int i = 3; i < Q; i++) if (!comp[i]) { row[nrows] = i; wt[nrows] = 1; nrows++; }
        free(comp);
    }
    const int unit = weighted ? 64 : 1, binw = weighted ? 16 : 1;      // energy units per row; histogram bin width in energy units
    long wtot = 0; for (int i = 0; i < nrows; i++) wtot += wt[i];
    const long nbins = wtot / binw + 1;
    // rows by class, per modulus
    uint16_t **off = malloc(nmod * sizeof(*off)), **mem = malloc(nmod * sizeof(*mem));
    double lnstates = 0; int maxmod = 0;
    for (int m = 0; m < nmod; m++) {
        int s = mod[m]; if (s < 3 || s > 65521) { fprintf(stderr, "modulus %d out of range\n", s); return 1; }
        lnstates += log((double)s); if (s > maxmod) maxmod = s;
        off[m] = calloc(s + 1, sizeof(uint16_t)); mem[m] = malloc(nrows * sizeof(uint16_t));
        int *c = calloc(s + 1, sizeof(int));
        for (int i = 0; i < nrows; i++) c[row[i] % s + 1]++;
        for (int a = 0; a < s; a++) c[a + 1] += c[a];
        for (int a = 0; a <= s; a++) off[m][a] = (uint16_t)c[a];
        for (int i = 0; i < nrows; i++) mem[m][c[row[i] % s]++] = (uint16_t)i;
        free(c);
    }
    // start cover, if any
    int *start = NULL;
    if (argc > 8) {
        FILE *f = fopen(argv[8], "r"); if (!f) { perror(argv[8]); return 1; }
        start = malloc(nmod * sizeof(int)); for (int m = 0; m < nmod; m++) start[m] = -1;
        char w[64]; int r, a;
        while (fscanf(f, "%63s", w) == 1) if (sscanf(w, "%d:%d", &r, &a) == 2) for (int m = 0; m < nmod; m++) if (mod[m] == r && a >= 0 && a < r) start[m] = a;
        fclose(f);
        for (int m = 0; m < nmod; m++) if (start[m] < 0) { fprintf(stderr, "start file has no class for modulus %d\n", mod[m]); return 1; }
    }
    fprintf(stderr, "Q=%d rows=%d moduli=%d (largest %d) ln(states)=%.3f betas=%d sweeps=%ld burn=%ld threads=%d start=%s\n", Q, nrows, nmod, maxmod, lnstates, nb, sweeps, burn, omp_get_max_threads(), start ? argv[8] : "random");
    rep_t *R = malloc(nb * sizeof(rep_t)); int *at = malloc(nb * sizeof(int));          // at[i] = replica sitting at beta i
    uint64_t sm = seed * 0x9E3779B97F4A7C15ULL + 12345;
    for (int i = 0; i < nb; i++) {
        R[i].a = malloc(nmod * sizeof(uint16_t)); R[i].cnt = calloc(nrows, 1);
        for (int j = 0; j < 4; j++) R[i].rng.s[j] = splitmix(&sm);
        for (int m = 0; m < nmod; m++) {
            int s = mod[m], a = start ? start[m] : (int)(rnd(&R[i].rng) % (uint64_t)s); R[i].a[m] = (uint16_t)a;
            for (int j = off[m][a]; j < off[m][a + 1]; j++) R[i].cnt[mem[m][j]]++;
        }
        int E = 0; for (int r = 0; r < nrows; r++) if (R[i].cnt[r] == 0) E += wt[r]; R[i].E = E; at[i] = i;
    }
    if (start) fprintf(stderr, "start cover: k = %.2f\n", (double)R[0].E / unit);
    long *hist = calloc((size_t)nb * nbins, sizeof(long));
    float *hoff = weighted ? calloc((size_t)nb * nbins, sizeof(float)) : NULL;      // sum of (energy - start of the bin): the bin is printed at its mean energy
    long *acc = calloc(nb, sizeof(long)), *tried = calloc(nb, sizeof(long)), *sw_ok = calloc(nb, sizeof(long)), *sw_try = calloc(nb, sizeof(long));
    double *qsum = calloc((size_t)nb * NQ, sizeof(double)); long *qn = calloc((size_t)nb * NQ, sizeof(long));
    double *csum = calloc((size_t)nb * NQ, sizeof(double)); int ncore = nmod < NCORE ? nmod : NCORE;   // agreement with the start cover on the first moduli
    int *minE = malloc(nb * sizeof(int)); for (int i = 0; i < nb; i++) minE[i] = (int)wtot + 1;
    double *esum = calloc(nb, sizeof(double)), *esum2 = calloc(nb, sizeof(double)); long *en = calloc(nb, sizeof(long));
    rng_t xr; for (int j = 0; j < 4; j++) xr.s[j] = splitmix(&sm);
    double t0 = omp_get_wtime();
    for (long sw = 0; sw < sweeps; sw++) {
        int quarter = sw >= burn ? (int)((sw - burn) * NQ / (sweeps - burn)) : -1;
        #pragma omp parallel for schedule(dynamic, 1)
        for (int i = 0; i < nb; i++) {
            rep_t *r = &R[at[i]]; double b = beta[i] / unit; long la = 0;
            for (int m = 0; m < nmod; m++) {
                int s = mod[m], a = r->a[m], a2 = (a + 1 + (int)(rnd(&r->rng) % (uint64_t)(s - 1))) % s;
                const uint16_t *o = off[m], *me = mem[m]; int lose = 0, gain = 0;
                if (weighted) {
                    for (int j = o[a]; j < o[a + 1]; j++) if (r->cnt[me[j]] == 1) lose += wt[me[j]];
                    for (int j = o[a2]; j < o[a2 + 1]; j++) if (r->cnt[me[j]] == 0) gain += wt[me[j]];
                } else {
                    for (int j = o[a]; j < o[a + 1]; j++) lose += r->cnt[me[j]] == 1;
                    for (int j = o[a2]; j < o[a2 + 1]; j++) gain += r->cnt[me[j]] == 0;
                }
                int dE = lose - gain;
                if (dE <= 0 || rnd01(&r->rng) < exp(-b * dE)) {
                    for (int j = o[a]; j < o[a + 1]; j++) r->cnt[me[j]]--;
                    for (int j = o[a2]; j < o[a2 + 1]; j++) r->cnt[me[j]]++;
                    r->a[m] = (uint16_t)a2; r->E += dE; la++;
                }
            }
            if (quarter >= 0) {
                hist[(size_t)i * nbins + r->E / binw]++; if (hoff) hoff[(size_t)i * nbins + r->E / binw] += (float)(r->E % binw); acc[i] += la; tried[i] += nmod; qsum[(size_t)i * NQ + quarter] += r->E; qn[(size_t)i * NQ + quarter]++;
                esum[i] += r->E; esum2[i] += (double)r->E * r->E; en[i]++;
                if (start) { int c = 0; for (int m = 0; m < ncore; m++) c += r->a[m] == start[m]; csum[(size_t)i * NQ + quarter] += c; }
            }
            if (r->E < minE[i]) minE[i] = r->E;
        }
        for (int i = (int)(sw & 1); i + 1 < nb; i += 2) {
            double d = (beta[i + 1] - beta[i]) * (R[at[i + 1]].E - R[at[i]].E) / unit;
            int ok = d >= 0 || rnd01(&xr) < exp(d);
            if (quarter >= 0) { sw_try[i]++; sw_ok[i] += ok; }
            if (ok) { int t = at[i]; at[i] = at[i + 1]; at[i + 1] = t; }
        }
        if ((sw + 1) % 5000 == 0) fprintf(stderr, "sweep %ld (%.0f s): k at the coldest beta %.2f, lowest seen there %.2f\n", sw + 1, omp_get_wtime() - t0, (double)R[at[nb - 1]].E / unit, (double)minE[nb - 1] / unit);
    }
    FILE *f = fopen(argv[6], "w");
    fprintf(f, "# Q=%d rows=%d moduli=%d largest=%d ln(states)=%.6f betas=%d sweeps=%ld burn=%ld seed=%llu start=%s weighted=%d\n", Q, nrows, nmod, maxmod, lnstates, nb, sweeps, burn, (unsigned long long)seed, start ? "given" : "random", weighted);
    for (int i = 0; i < nb; i++) {
        long n = en[i]; long *h = hist + (size_t)i * nbins;
        double mean = n ? esum[i] / n / unit : 0, sd = n ? sqrt(fmax(0, esum2[i] / n - (esum[i] / n) * (esum[i] / n))) / unit : 0;
        fprintf(f, "BETA %.6f n %ld mean %.3f sd %.3f min %.2f swap %.3f acc %.5f quarters", beta[i], n, mean, sd, (double)minE[i] / unit, sw_try[i] ? (double)sw_ok[i] / sw_try[i] : -1.0, tried[i] ? (double)acc[i] / tried[i] : -1.0);
        for (int k = 0; k < NQ; k++) fprintf(f, " %.3f", qn[(size_t)i * NQ + k] ? qsum[(size_t)i * NQ + k] / qn[(size_t)i * NQ + k] / unit : -1.0);
        if (start) { fprintf(f, " core%d", ncore); for (int k = 0; k < NQ; k++) fprintf(f, " %.3f", qn[(size_t)i * NQ + k] ? csum[(size_t)i * NQ + k] / qn[(size_t)i * NQ + k] : -1.0); }
        fprintf(f, "\nH");
        for (long e = 0; e < nbins; e++) if (h[e]) { if (weighted) fprintf(f, " %.4f:%ld", (e * binw + (double)hoff[(size_t)i * nbins + e] / h[e]) / unit, h[e]); else fprintf(f, " %ld:%ld", e, h[e]); }
        fprintf(f, "\n");
    }
    fclose(f);
    return 0;
}
