/* covergen.c -- many distinct covers of a given quality, by a capped random walk from known good covers.
 *
 * ptcover finds covers with few uncovered rows; a search that uses up one cover's progression in minutes needs
 * thousands of them.  Near the optimum the covers with at most kcap uncovered rows form large connected sets under
 * the move "change the class of one modulus": this program walks in such a set and prints every cover it visits
 * once.  A move is accepted exactly when it leaves at most kcap rows uncovered, so the walk is uniform on the part
 * of the set it can reach, and no cover printed is worse than kcap.
 *
 *   gcc -O3 -march=native -fopenmp -o covergen covergen.c -lm
 *   ./covergen Q start.txt kcap count [seed] [gap] > covers.txt
 *
 * start.txt: lines "COVER k r:a r:a ..." or "BEST r:a r:a ..." (the output and PT_DUMP format of ptcover), all on
 * the same moduli in the same order; only those with at most kcap uncovered rows are used as starting points.  One
 * walker per thread; a walker starts from a random one of them and moves on to another when 4,000 visits in a row
 * brought nothing new.  Between two visits a walker attempts gap * (number of moduli) moves (default gap = 1).  Output: "COVER k r:a ..." lines, all different, also different
 * from every start line; make_specs.py turns them into search specs.  The program stops after count covers, or when
 * no new cover has appeared for COVERGEN_STALL seconds (environment, default 30): the reachable set is then used up
 * and a higher kcap or other starting points are needed.  COVERGEN_TIME (seconds) limits the whole run.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

#define MAXM 256
static int Q, nrows, nmod;
static int *rowq;
static int mod_[MAXM];
static int **cstart, **crows;

typedef struct { uint64_t s; } rng_t;
static inline uint64_t rnd(rng_t *r) { r->s ^= r->s << 13; r->s ^= r->s >> 7; r->s ^= r->s << 17; return r->s; }

static uint64_t hash_cover(const int *a) {
    uint64_t h = 1469598103934665603ull;
    for (int m = 0; m < nmod; m++) { h ^= (uint64_t)a[m] + 0x9E37ull * m; h *= 1099511628211ull; }
    return h ? h : 1;
}
static size_t hcap = 1 << 24, hn = 0; static uint64_t *hset;
static int seen_or_add(uint64_t h) {          /* 1 if h was present */
    size_t p = h & (hcap - 1); while (hset[p] && hset[p] != h) p = (p + 1) & (hcap - 1);
    if (hset[p]) return 1;
    hset[p] = h; hn++; return 0;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: covergen Q start.txt kcap count [seed] [gap]\n"); return 1; }
    Q = atoi(argv[1]); int kcap = atoi(argv[3]); long want = atol(argv[4]);
    uint64_t seed = argc > 5 ? strtoull(argv[5], 0, 10) : 1; int gap = argc > 6 ? atoi(argv[6]) : 1;
    char *sv = calloc(Q + 1, 1); rowq = malloc(sizeof(int) * (Q / 2 + 2));
    for (int i = 2; i < Q; i++) if (!sv[i]) { if (i > 2) rowq[nrows++] = i; for (long j = (long)i * i; j < Q; j += i) sv[j] = 1; }
    /* start covers */
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; }
    static char line[1 << 16]; int nstart = 0, cap = 0; int (*start)[MAXM] = NULL;
    hset = calloc(hcap, 8);
    while (fgets(line, sizeof line, f)) {
        char *tok = strtok(line, " \t\n"); if (!tok) continue;
        int isc = !strcmp(tok, "COVER"), isb = !strcmp(tok, "BEST"); if (!isc && !isb) continue;
        if (isc) strtok(NULL, " \t\n");
        int a[MAXM], r[MAXM], n = 0;
        while ((tok = strtok(NULL, " \t\n")) && n < MAXM) if (sscanf(tok, "%d:%d", &r[n], &a[n]) == 2) n++;
        if (!nmod) { nmod = n; memcpy(mod_, r, sizeof(int) * n); }
        if (n != nmod || memcmp(r, mod_, sizeof(int) * n)) { fprintf(stderr, "start covers must share their moduli\n"); return 1; }
        if (nstart == cap) { cap = cap ? 2 * cap : 64; start = realloc(start, sizeof(*start) * cap); }
        memcpy(start[nstart++], a, sizeof(int) * n);
    }
    fclose(f);
    if (!nstart) { fprintf(stderr, "no cover in %s\n", argv[2]); return 1; }
    cstart = malloc(sizeof(int *) * nmod); crows = malloc(sizeof(int *) * nmod);
    for (int m = 0; m < nmod; m++) {
        int r = mod_[m];
        cstart[m] = calloc(r + 2, sizeof(int)); crows[m] = malloc(sizeof(int) * nrows);
        for (int i = 0; i < nrows; i++) cstart[m][rowq[i] % r + 1]++;
        for (int c = 0; c <= r; c++) cstart[m][c + 1] += cstart[m][c];
        int *pos = malloc(sizeof(int) * (r + 1)); memcpy(pos, cstart[m], sizeof(int) * (r + 1));
        for (int i = 0; i < nrows; i++) crows[m][pos[rowq[i] % r]++] = i;
        free(pos);
    }
    /* keep the starts that are good enough; all starts count as seen */
    int ngood = 0; uint8_t *cnt0 = malloc(nrows);
    for (int s = 0; s < nstart; s++) {
        memset(cnt0, 0, nrows);
        for (int m = 0; m < nmod; m++) for (int j = cstart[m][start[s][m]]; j < cstart[m][start[s][m] + 1]; j++) cnt0[crows[m][j]]++;
        int k = 0; for (int i = 0; i < nrows; i++) k += cnt0[i] == 0;
        seen_or_add(hash_cover(start[s]));
        if (k <= kcap) memcpy(start[ngood++], start[s], sizeof(int) * nmod);
    }
    if (!ngood) { fprintf(stderr, "no start cover with at most %d uncovered rows\n", kcap); return 1; }
    fprintf(stderr, "Q=%d rows=%d moduli=%d; %d of %d start covers have at most %d uncovered rows; %d walkers\n", Q, nrows, nmod, ngood, nstart, kcap, omp_get_max_threads());
    long written = 0; int stop = 0; long hist[8] = {0};
    double stall = getenv("COVERGEN_STALL") ? atof(getenv("COVERGEN_STALL")) : 30, last_new = omp_get_wtime();
    double tmax = getenv("COVERGEN_TIME") ? atof(getenv("COVERGEN_TIME")) : 1e18, t_start = last_new;
    #pragma omp parallel
    {
        int w = omp_get_thread_num(); rng_t g = { seed * 0x9E3779B97F4A7C15ull + 0x1234567ull * (w + 1) }; for (int j = 0; j < 20; j++) rnd(&g);
        int a[MAXM], k = 0, stale = 1 << 30; uint8_t *cnt = malloc(nrows);
        while (!stop) {
            if (stale > 4000) {             /* nothing new around here: go on from another starting point */
                memcpy(a, start[rnd(&g) % ngood], sizeof(int) * nmod); memset(cnt, 0, nrows);
                for (int m = 0; m < nmod; m++) for (int j = cstart[m][a[m]]; j < cstart[m][a[m] + 1]; j++) cnt[crows[m][j]]++;
                k = 0; for (int i = 0; i < nrows; i++) k += cnt[i] == 0;
                stale = 0;
            }
            for (int t = 0; t < gap * nmod; t++) {
                int m = rnd(&g) % nmod, r = mod_[m];
                int c = 1 + rnd(&g) % (r - 2); if (c >= a[m]) c++;
                int lose = 0, gain = 0, o = a[m];
                for (int j = cstart[m][o]; j < cstart[m][o + 1]; j++) lose += cnt[crows[m][j]] == 1;
                for (int j = cstart[m][c]; j < cstart[m][c + 1]; j++) gain += cnt[crows[m][j]] == 0;
                if (k + lose - gain > kcap) continue;
                for (int j = cstart[m][o]; j < cstart[m][o + 1]; j++) cnt[crows[m][j]]--;
                for (int j = cstart[m][c]; j < cstart[m][c + 1]; j++) cnt[crows[m][j]]++;
                a[m] = c; k += lose - gain;
            }
            uint64_t h = hash_cover(a);
            stale++;
            #pragma omp critical
            {
                if (!stop && hn * 2 < hcap && !seen_or_add(h)) {
                    stale = 0;
                    printf("COVER %d", k); for (int m = 0; m < nmod; m++) printf(" %d:%d", mod_[m], a[m]); printf("\n");
                    if (kcap - k < 8) hist[kcap - k]++;
                    last_new = omp_get_wtime();
                    if (++written >= want) stop = 1;
                }
                if (omp_get_wtime() - last_new > stall || omp_get_wtime() - t_start > tmax) stop = 1;
            }
        }
        free(cnt);
    }
    fprintf(stderr, "%ld covers written; by uncovered rows:", written);
    for (int d = 7; d >= 0; d--) if (hist[d]) fprintf(stderr, " %d: %ld", kcap - d, hist[d]);
    fprintf(stderr, "\n");
    return 0;
}
