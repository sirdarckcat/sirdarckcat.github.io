/* ptcover_fast2.c -- ptcover_fast.c plus one output line: the first sweep at which the best k over all replicas reached each
 * value ("# first sweep with best k <= j").  It only reads best_k, so the run, the tables and BEST are those of ptcover_fast.
 *   gcc -O3 -march=native -fopenmp -o ptcover_fast2 ptcover_fast2.c -lm
 * ptcover_fast.c -- goldbach/fscan/cover/ptcover.c (branch ccr-d4a17dd0-7uu03r) made 1.8-2.1x faster with identical output.
 *
 * Same command line, same random numbers, same moves, so the same tables, the same BEST and the same PT_DUMP file for a given seed
 * (ptcover_ref.c is the original; test_identical.sh compares them).  What changed, all in the evaluation of a move (the number of
 * rows a move loses, those with exactly one cover in the old class, and gains, those with none in the new class):
 *   - the class lists of the large moduli are scanned sixteen rows at a time with an AVX-512 gather (count_eq);
 *   - in the cold replicas (beta >= BCUT) the classes of the moduli up to SMALLR are bit sets over the rows, and a replica keeps
 *     two more bit sets, the rows with no cover and with exactly one: lose and gain become a popcount of an AND of 214 words,
 *     instead of a walk over up to 4,300 rows (the moduli 3 to 61 are 73% of the walk).  The hot replicas accept most moves and
 *     would pay more for keeping the bit sets than they save: they run without, and a state that arrives from a hot slot by an
 *     exchange rebuilds its bit sets before its first move;
 *   - exp(-beta d) from a table (d < 130).
 *   gcc -O3 -march=native -fopenmp -o ptcover_fast ptcover_fast.c -lm
 */
/* ptcover.c -- parallel tempering on residue covers, and an entropy estimate of the best possible cover.
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
#if defined(__AVX512VPOPCNTDQ__) || defined(__AVX512F__)
#include <immintrin.h>
#endif

#define MAXM 256
static int Q, nrows, nmod;
static int *rowq;
static int mod_[MAXM], init_res[MAXM];
static int **cstart;        /* cstart[m][c] .. cstart[m][c+1]: rows of class c of modulus m */
static int **crows;
static uint16_t **rcls;     /* rcls[m][i] = rowq[i] % mod_[m] */
#ifndef BCUT
#define BCUT 0.6            /* replicas colder than this (beta >= BCUT) evaluate small moduli on bit sets; hotter ones accept too often for them to pay */
#endif
#ifndef SMALLR
#define SMALLR 61           /* moduli up to this one keep their classes as bit sets: the rows a move loses or gains are a popcount */
#endif
static int nwords;          /* 64-bit words of a bit set over the rows, a multiple of 8 */
static uint64_t ***cmask;   /* cmask[m][c]: the rows of class c of modulus m, for the small moduli */

typedef struct { uint64_t s; } rng_t;
static inline uint64_t rnd(rng_t *r) { r->s ^= r->s << 13; r->s ^= r->s >> 7; r->s ^= r->s << 17; return r->s; }
static inline double rndu(rng_t *r) { return (rnd(r) >> 11) * (1.0 / 9007199254740992.0); }

typedef struct { double beta; int k; int a[MAXM]; uint8_t *cnt; uint64_t *b0, *b1; int valid; double ex[130]; rng_t rng; double sk, skk; long n, acc, tries; int best_k; int best_a[MAXM]; } rep_t;

/* the number of j in [0, n) with cnt[idx[j]] == val: sixteen indices at a time with a gather (cnt has 3 bytes of padding) */
static inline int count_eq(const int *idx, int n, const uint8_t *cnt, int val) {
#ifdef __AVX512F__
    const __m512i vv = _mm512_set1_epi32(val), ff = _mm512_set1_epi32(0xFF);
    int total = 0, j = 0;
    for (; j + 16 <= n; j += 16) {
        const __m512i g = _mm512_i32gather_epi32(_mm512_loadu_si512((const void *)(idx + j)), (const int *)cnt, 1);
        total += __builtin_popcount(_mm512_cmpeq_epi32_mask(_mm512_and_si512(g, ff), vv));
    }
    if (j < n) {
        const __mmask16 tm = (__mmask16)((1u << (n - j)) - 1);
        const __m512i g = _mm512_mask_i32gather_epi32(_mm512_setzero_si512(), tm, _mm512_maskz_loadu_epi32(tm, idx + j), (const int *)cnt, 1);
        total += __builtin_popcount(_mm512_mask_cmpeq_epi32_mask(tm, _mm512_and_si512(g, ff), vv));
    }
    return total;
#else
    int total = 0;
    for (int j = 0; j < n; j++) total += cnt[idx[j]] == val;
    return total;
#endif
}
static inline int popc_and(const uint64_t *x, const uint64_t *y) {
#ifdef __AVX512VPOPCNTDQ__
    __m512i acc = _mm512_setzero_si512();
    for (int w = 0; w < nwords; w += 8) acc = _mm512_add_epi64(acc, _mm512_popcnt_epi64(_mm512_and_si512(_mm512_load_si512((const void *)(x + w)), _mm512_load_si512((const void *)(y + w)))));
    return (int)_mm512_reduce_add_epi64(acc);
#else
    int n = 0;
    for (int w = 0; w < nwords; w++) n += __builtin_popcountll(x[w] & y[w]);
    return n;
#endif
}
static void rebuild_bits(rep_t *R) {
    memset(R->b0, 0, 8 * nwords); memset(R->b1, 0, 8 * nwords);
    for (int i = 0; i < nrows; i++) { if (R->cnt[i] == 0) R->b0[i >> 6] |= 1ull << (i & 63); else if (R->cnt[i] == 1) R->b1[i >> 6] |= 1ull << (i & 63); }
}
static int energy(rep_t *R) {
    memset(R->cnt, 0, nrows);
    for (int m = 0; m < nmod; m++) for (int j = cstart[m][R->a[m]]; j < cstart[m][R->a[m] + 1]; j++) R->cnt[crows[m][j]]++;
    int k = 0; for (int i = 0; i < nrows; i++) k += R->cnt[i] == 0;
    rebuild_bits(R); R->valid = 1;
    return k;
}
static void sweep(rep_t *R) {
    const int bits = R->beta >= BCUT;
    if (bits && !R->valid) { rebuild_bits(R); R->valid = 1; }
    for (int t = 0; t < nmod; t++) {
        int m = rnd(&R->rng) % nmod, r = mod_[m];
        int c = 1 + rnd(&R->rng) % (r - 2); if (c >= R->a[m]) c++;        /* a nonzero class other than the current one */
        int lose = 0, gain = 0, o = R->a[m];
        if (bits && cmask[m]) { lose = popc_and(cmask[m][o], R->b1); gain = popc_and(cmask[m][c], R->b0); }
        else {
            lose = count_eq(crows[m] + cstart[m][o], cstart[m][o + 1] - cstart[m][o], R->cnt, 1);
            gain = count_eq(crows[m] + cstart[m][c], cstart[m][c + 1] - cstart[m][c], R->cnt, 0);
        }
        int d = lose - gain;
        R->tries++;
        if (d <= 0 || rndu(&R->rng) < (d < 130 ? R->ex[d] : exp(-R->beta * d))) {
            if (bits) {
                for (int j = cstart[m][o]; j < cstart[m][o + 1]; j++) {
                    int i = crows[m][j]; int v = --R->cnt[i];
                    if (v == 0) { R->b1[i >> 6] &= ~(1ull << (i & 63)); R->b0[i >> 6] |= 1ull << (i & 63); }
                    else if (v == 1) R->b1[i >> 6] |= 1ull << (i & 63);
                }
                for (int j = cstart[m][c]; j < cstart[m][c + 1]; j++) {
                    int i = crows[m][j]; int v = ++R->cnt[i];
                    if (v == 1) { R->b0[i >> 6] &= ~(1ull << (i & 63)); R->b1[i >> 6] |= 1ull << (i & 63); }
                    else if (v == 2) R->b1[i >> 6] &= ~(1ull << (i & 63));
                }
            } else {
                for (int j = cstart[m][o]; j < cstart[m][o + 1]; j++) R->cnt[crows[m][j]]--;
                for (int j = cstart[m][c]; j < cstart[m][c + 1]; j++) R->cnt[crows[m][j]]++;
                R->valid = 0;
            }
            R->a[m] = c; R->k += d; R->acc++;
            if (R->k < R->best_k) { R->best_k = R->k; memcpy(R->best_a, R->a, sizeof(int) * nmod); }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: ptcover Q moduli.txt sweeps [seed] [betas.txt]   (env PT_DUMP=file PT_KDUMP=k)\n"); return 1; }
    Q = atoi(argv[1]); long sweeps = atol(argv[3]); uint64_t seed = argc > 4 ? strtoull(argv[4], 0, 10) : 1;
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; }
    char line[256]; int have_init = 1;
    while (fgets(line, sizeof line, f)) { int r, a = -1; int n = sscanf(line, "%d %d", &r, &a); if (n < 1) continue; mod_[nmod] = r; init_res[nmod] = a; if (n < 2) have_init = 0; nmod++; }
    fclose(f);
    char *sv = calloc(Q + 1, 1); rowq = malloc(sizeof(int) * (Q / 2 + 2));
    for (int i = 2; i < Q; i++) if (!sv[i]) { if (i > 2) rowq[nrows++] = i; for (long j = (long)i * i; j < Q; j += i) sv[j] = 1; }
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
    nwords = (nrows + 511) / 512 * 8;
    cmask = calloc(nmod, sizeof(uint64_t **));
    for (int m = 0; m < nmod; m++) if (mod_[m] <= SMALLR) {
        int r = mod_[m];
        cmask[m] = malloc(sizeof(uint64_t *) * r);
        for (int c = 0; c < r; c++) {
            cmask[m][c] = aligned_alloc(64, 8 * nwords); memset(cmask[m][c], 0, 8 * nwords);
            for (int j = cstart[m][c]; j < cstart[m][c + 1]; j++) { int i = crows[m][j]; cmask[m][c][i >> 6] |= 1ull << (i & 63); }
        }
    }
    /* temperature ladder */
    double betas[128]; int nrep = 0;
    if (argc > 5) { FILE *g = fopen(argv[5], "r"); double b; while (g && fscanf(g, "%lf", &b) == 1) betas[nrep++] = b; if (g) fclose(g); }
    else { double b[] = {0, .01, .02, .03, .045, .06, .08, .1, .125, .15, .18, .21, .25, .3, .35, .4, .46, .53, .6, .7, .8, .9, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0, 2.4, 3.0, 4.0, 6.0}; nrep = sizeof b / sizeof *b; memcpy(betas, b, sizeof b); }
    rep_t *R = calloc(nrep, sizeof(rep_t));
    for (int i = 0; i < nrep; i++) {
        R[i].beta = betas[i]; R[i].cnt = calloc(nrows + 4, 1); R[i].b0 = aligned_alloc(64, 8 * nwords); R[i].b1 = aligned_alloc(64, 8 * nwords);
        for (int d = 0; d < 130; d++) R[i].ex[d] = exp(-R[i].beta * d); R[i].rng.s = seed * 0x9E3779B97F4A7C15ull + 0x1234567ull * (i + 1); for (int j = 0; j < 20; j++) rnd(&R[i].rng);
        for (int m = 0; m < nmod; m++) R[i].a[m] = (have_init && i == nrep - 1) ? init_res[m] : 1 + (int)(rnd(&R[i].rng) % (mod_[m] - 1));
        R[i].k = energy(&R[i]); R[i].best_k = R[i].k; memcpy(R[i].best_a, R[i].a, sizeof(int) * nmod);
    }
    fprintf(stderr, "Q=%d rows=%d moduli=%d ln(#covers)=%.2f replicas=%d; k of the given cover: %d\n", Q, nrows, nmod, S0, nrep, have_init ? R[nrep - 1].k : -1);
    long burn = sweeps / 4, sw_acc = 0, sw_try = 0; int gbest = 1 << 30; rng_t xr = { seed ^ 0xABCDEFull };
    int gtrack = 1 << 30; long first_le[65]; for (int j = 0; j < 65; j++) first_le[j] = -1;
    FILE *dump = getenv("PT_DUMP") ? fopen(getenv("PT_DUMP"), "a") : NULL; int kdump = getenv("PT_KDUMP") ? atoi(getenv("PT_KDUMP")) : -1;
    size_t hcap = 1 << 22, hn = 0; uint64_t *hset = calloc(hcap, 8); long ndump = 0;
    for (long s = 0; s < sweeps; s++) {
        #pragma omp parallel for schedule(dynamic, 1)
        for (int i = 0; i < nrep; i++) { for (int u = 0; u < 4; u++) sweep(&R[i]); if (s >= burn) { R[i].sk += R[i].k; R[i].skk += (double)R[i].k * R[i].k; R[i].n++; } }
        for (int i = (int)(s & 1); i + 1 < nrep; i += 2) {               /* replica exchange: swap the temperatures' states */
            double d = (R[i].beta - R[i + 1].beta) * (R[i].k - R[i + 1].k);
            sw_try++;
            if (d >= 0 || rndu(&xr) < exp(d)) {
                int tk = R[i].k; R[i].k = R[i + 1].k; R[i + 1].k = tk;
                uint8_t *tc = R[i].cnt; R[i].cnt = R[i + 1].cnt; R[i + 1].cnt = tc;
                uint64_t *t0 = R[i].b0; R[i].b0 = R[i + 1].b0; R[i + 1].b0 = t0; t0 = R[i].b1; R[i].b1 = R[i + 1].b1; R[i + 1].b1 = t0;
                int tv = R[i].valid; R[i].valid = R[i + 1].valid; R[i + 1].valid = tv;
                int ta[MAXM]; memcpy(ta, R[i].a, sizeof ta); memcpy(R[i].a, R[i + 1].a, sizeof ta); memcpy(R[i + 1].a, ta, sizeof ta);
                sw_acc++;
            }
        }
        for (int i = 0; i < nrep; i++) if (R[i].k < R[i].best_k) { R[i].best_k = R[i].k; memcpy(R[i].best_a, R[i].a, sizeof(int) * nmod); }
        { int b = 1 << 30; for (int i = 0; i < nrep; i++) if (R[i].best_k < b) b = R[i].best_k;
          if (b < gtrack) { for (int j = b; j < gtrack && j < 65; j++) if (first_le[j] < 0) first_le[j] = s + 1; gtrack = b; } }
        if (dump) for (int i = 0; i < nrep; i++) if (R[i].k <= kdump && hn * 2 < hcap) {
            uint64_t h = 1469598103934665603ull; for (int m = 0; m < nmod; m++) { h ^= (uint64_t)R[i].a[m] + 0x9E37ull * m; h *= 1099511628211ull; } if (!h) h = 1;
            size_t p = h & (hcap - 1); while (hset[p] && hset[p] != h) p = (p + 1) & (hcap - 1);
            if (!hset[p]) { hset[p] = h; hn++; ndump++; fprintf(dump, "COVER %d", R[i].k); for (int m = 0; m < nmod; m++) fprintf(dump, " %d:%d", mod_[m], R[i].a[m]); fprintf(dump, "\n"); }
        }
        if ((s + 1) % (sweeps / 10 ? sweeps / 10 : 1) == 0) {
            int b = 1 << 30; for (int i = 0; i < nrep; i++) if (R[i].best_k < b) b = R[i].best_k;
            if (b < gbest) gbest = b;
            fprintf(stderr, "sweep %ld: best k so far %d; k now at the coldest replicas: %d %d %d\n", s + 1, gbest, R[nrep - 3].k, R[nrep - 2].k, R[nrep - 1].k);
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
    printf("# best k found: %d\n", R[bi].best_k);
    printf("# first sweep with best k <= j (j:sweep):"); for (int j = 0; j < 65 && j <= gtrack + 8; j++) if (first_le[j] >= 0) printf(" %d:%ld", j, first_le[j]); printf("\n");
    if (dump) { fclose(dump); printf("# distinct covers with k <= %d written: %ld\n", kdump, ndump); }
    printf("BEST"); for (int m = 0; m < nmod; m++) printf(" %d:%d", mod_[m], R[bi].best_a[m]); printf("\n");
    return 0;
}
