// ideal_tilt.c -- how many N have unusually few rows left, counted over ALL residue vectors: the density of states of
// "rows left after the primes up to z", by parallel tempering.  This is the cover problem with every odd prime up to z
// as a modulus (and class 0 allowed), sampled at all temperatures instead of only at the bottom.
//
//   state    a class a_s for every odd prime s <= z: any class for s > 29, a nonzero class for s <= 29
//            (states = residue vectors of N modulo prod s; N divisible by a prime below 30 has hundreds of rows
//            more and is left out, which changes nothing at the low end)
//   energy   k = number of rows (odd primes q < Q) with q != a_s (mod s) for every s  (rows of N with no factor <= z)
//
//   gcc -O3 -march=native -fopenmp -o ideal_tilt ideal_tilt.c -lm          (add -DBIGROWS for more than 65,535 rows, Q > 800,000)
//   ./ideal_tilt Q z betas.txt sweeps burn out.txt [seed]
//
// Output: one block per beta with the histogram of k after the burn-in, the acceptance rate of class changes by size
// of the modulus and the acceptance of exchanges.  ideal_tilt.py turns the histograms into ln g(k) (multi-histogram
// reweighting, normalised by the total number of states prod s) and into the cost of an ideal search.
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

#ifdef BIGROWS
typedef uint32_t row_t;
#define MAXROWS 2000000000
#else
typedef uint16_t row_t;
#define MAXROWS 65535
#endif
#define NBUCK 8
static const int buck_hi[NBUCK] = {32, 128, 512, 2048, 8192, 32768, 131072, 1 << 30};
typedef struct {
    uint16_t *a;        // class per modulus
    uint8_t *cnt;       // number of moduli covering each row
    int E;
    rng_t rng;
} rep_t;

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: %s Q z betas.txt sweeps burn out.txt [seed]\n", argv[0]); return 1; }
    int Q = atoi(argv[1]), z = atoi(argv[2]); long sweeps = atol(argv[4]), burn = atol(argv[5]);
    uint64_t seed = argc > 7 ? strtoull(argv[7], 0, 10) : 1;
    if (z > 65521) { fprintf(stderr, "z too large for 16-bit classes\n"); return 1; }
    // betas
    double beta[4096]; int nb = 0; { FILE *f = fopen(argv[3], "r"); if (!f) { perror(argv[3]); return 1; } while (nb < 4096 && fscanf(f, "%lf", &beta[nb]) == 1) nb++; fclose(f); }
    // primes
    int lim = Q > z + 1 ? Q : z + 1; char *comp = calloc(lim + 1, 1);
    for (int i = 2; (long)i * i <= lim; i++) if (!comp[i]) for (int j = i * i; j <= lim; j += i) comp[j] = 1;
    int nrows = 0, nmod = 0; for (int i = 3; i < Q; i++) if (!comp[i]) nrows++; for (int i = 3; i <= z; i++) if (!comp[i]) nmod++;
    if (nrows > MAXROWS) { fprintf(stderr, "too many rows: compile with -DBIGROWS\n"); return 1; }
    int *row = malloc(nrows * sizeof(int)), *mod = malloc(nmod * sizeof(int));
    nrows = 0; for (int i = 3; i < Q; i++) if (!comp[i]) row[nrows++] = i;
    nmod = 0; for (int i = 3; i <= z; i++) if (!comp[i]) mod[nmod++] = i;
    // rows by class, per modulus
    row_t **off = malloc(nmod * sizeof(*off)), **mem = malloc(nmod * sizeof(*mem)); int *buck = malloc(nmod * sizeof(int));
    double lnstates = 0;
    for (int m = 0; m < nmod; m++) {
        int s = mod[m]; lnstates += log((double)(s > 29 ? s : s - 1));
        off[m] = calloc(s + 1, sizeof(row_t)); mem[m] = malloc(nrows * sizeof(row_t));
        int *c = calloc(s + 1, sizeof(int));
        for (int i = 0; i < nrows; i++) c[row[i] % s + 1]++;
        for (int a = 0; a < s; a++) c[a + 1] += c[a];
        for (int a = 0; a <= s; a++) off[m][a] = (row_t)c[a];
        for (int i = 0; i < nrows; i++) mem[m][c[row[i] % s]++] = (row_t)i;
        free(c);
        int b = 0; while (s >= buck_hi[b]) b++; buck[m] = b;
    }
    fprintf(stderr, "Q=%d rows=%d z=%d moduli=%d ln(states)=%.3f betas=%d sweeps=%ld burn=%ld threads=%d\n", Q, nrows, z, nmod, lnstates, nb, sweeps, burn, omp_get_max_threads());
    // replicas
    rep_t *R = malloc(nb * sizeof(rep_t)); int *at = malloc(nb * sizeof(int));          // at[i] = replica sitting at beta i
    uint64_t sm = seed * 0x9E3779B97F4A7C15ULL + 12345;
    for (int i = 0; i < nb; i++) {
        R[i].a = malloc(nmod * sizeof(uint16_t)); R[i].cnt = calloc(nrows, 1);
        for (int j = 0; j < 4; j++) R[i].rng.s[j] = splitmix(&sm);
        for (int m = 0; m < nmod; m++) {
            int s = mod[m], a = s > 29 ? (int)(rnd(&R[i].rng) % (uint64_t)s) : 1 + (int)(rnd(&R[i].rng) % (uint64_t)(s - 1)); R[i].a[m] = (uint16_t)a;
            for (int j = off[m][a]; j < off[m][a + 1]; j++) R[i].cnt[mem[m][j]]++;
        }
        int E = 0; for (int r = 0; r < nrows; r++) E += R[i].cnt[r] == 0; R[i].E = E; at[i] = i;
    }
    long *hist = calloc((size_t)nb * (nrows + 1), sizeof(long));
    long *acc = calloc((size_t)nb * NBUCK, sizeof(long)), *tried = calloc((size_t)nb * NBUCK, sizeof(long));
    long *sw_ok = calloc(nb, sizeof(long)), *sw_try = calloc(nb, sizeof(long));
    int *minE = malloc(nb * sizeof(int)); for (int i = 0; i < nb; i++) minE[i] = nrows + 1;
    rng_t xr; for (int j = 0; j < 4; j++) xr.s[j] = splitmix(&sm);
    double t0 = omp_get_wtime();
    for (long sw = 0; sw < sweeps; sw++) {
        #pragma omp parallel for schedule(dynamic, 1)
        for (int i = 0; i < nb; i++) {
            rep_t *r = &R[at[i]]; double b = beta[i]; long la[NBUCK] = {0}, lt[NBUCK] = {0};
            for (int m = 0; m < nmod; m++) {
                int s = mod[m], a = r->a[m], a2;
                if (s > 29) a2 = (a + 1 + (int)(rnd(&r->rng) % (uint64_t)(s - 1))) % s;
                else if (s == 3) a2 = 3 - a;
                else a2 = 1 + (a + (int)(rnd(&r->rng) % (uint64_t)(s - 2))) % (s - 1);
                const row_t *o = off[m], *me = mem[m]; int lose = 0, gain = 0;
                for (int j = o[a]; j < o[a + 1]; j++) lose += r->cnt[me[j]] == 1;
                for (int j = o[a2]; j < o[a2 + 1]; j++) gain += r->cnt[me[j]] == 0;
                int dE = lose - gain; lt[buck[m]]++;
                if (dE <= 0 || rnd01(&r->rng) < exp(-b * dE)) {
                    for (int j = o[a]; j < o[a + 1]; j++) r->cnt[me[j]]--;
                    for (int j = o[a2]; j < o[a2 + 1]; j++) r->cnt[me[j]]++;
                    r->a[m] = (uint16_t)a2; r->E += dE; la[buck[m]]++;
                }
            }
            if (sw >= burn) { hist[(size_t)i * (nrows + 1) + r->E]++; for (int k = 0; k < NBUCK; k++) { acc[(size_t)i * NBUCK + k] += la[k]; tried[(size_t)i * NBUCK + k] += lt[k]; } }
            if (r->E < minE[i]) minE[i] = r->E;
        }
        for (int i = (int)(sw & 1); i + 1 < nb; i += 2) {
            double d = (beta[i + 1] - beta[i]) * (R[at[i + 1]].E - R[at[i]].E);
            int ok = d >= 0 || rnd01(&xr) < exp(d);
            if (sw >= burn) { sw_try[i]++; sw_ok[i] += ok; }
            if (ok) { int t = at[i]; at[i] = at[i + 1]; at[i + 1] = t; }
        }
        if ((sw + 1) % 2000 == 0) fprintf(stderr, "sweep %ld (%.0f s): k at the coldest beta %d, lowest seen there %d\n", sw + 1, omp_get_wtime() - t0, R[at[nb - 1]].E, minE[nb - 1]);
    }
    FILE *f = fopen(argv[6], "w");
    fprintf(f, "# Q=%d rows=%d z=%d moduli=%d ln(states)=%.6f betas=%d sweeps=%ld burn=%ld seed=%llu\n", Q, nrows, z, nmod, lnstates, nb, sweeps, burn, (unsigned long long)seed);
    fprintf(f, "# acceptance columns: moduli below"); for (int k = 0; k < NBUCK - 1; k++) fprintf(f, " %d", buck_hi[k]); fprintf(f, " and above\n");
    for (int i = 0; i < nb; i++) {
        long n = 0; double s1 = 0, s2 = 0; long *h = hist + (size_t)i * (nrows + 1);
        for (int e = 0; e <= nrows; e++) { n += h[e]; s1 += (double)h[e] * e; s2 += (double)h[e] * e * e; }
        double mean = n ? s1 / n : 0, sd = n ? sqrt(fmax(0, s2 / n - mean * mean)) : 0;
        fprintf(f, "BETA %.6f n %ld mean %.3f sd %.3f min %d swap %.3f acc", beta[i], n, mean, sd, minE[i], sw_try[i] ? (double)sw_ok[i] / sw_try[i] : -1.0);
        for (int k = 0; k < NBUCK; k++) fprintf(f, " %.4f", tried[(size_t)i * NBUCK + k] ? (double)acc[(size_t)i * NBUCK + k] / tried[(size_t)i * NBUCK + k] : -1.0);
        fprintf(f, "\nH");
        for (int e = 0; e <= nrows; e++) if (h[e]) fprintf(f, " %d:%ld", e, h[e]);
        fprintf(f, "\n");
    }
    fclose(f);
    return 0;
}
