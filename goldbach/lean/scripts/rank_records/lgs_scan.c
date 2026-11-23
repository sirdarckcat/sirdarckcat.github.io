// lgs_scan.c -- the least Goldbach summand g(N) (least prime p with N - p prime) of every even N in [6, X],
// by a segmented sieve.  Prints every N whose g(N) is at least tau(N) = A ln(N)^2 - B (all N while that is
// <= 0; A and B are the 4th and 5th arguments, default 2.6 and 250): enough to reconstruct the running largest, second largest, ... values of g (rank_records.py checks
// that the k-th largest stays above the threshold).  Also prints the histogram of g to a second file.
//
//   gcc -O3 -march=native -fopenmp -o lgs_scan lgs_scan.c -lm
//   ./lgs_scan 10000000000 cand_1e10.txt hist_1e10.txt [A B]
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define QMAX (1 << 17)                 // the summands tried are below this; g(N) < QMAX is asserted
#define SEG (1L << 24)                 // even N per segment: 2 * SEG numbers
typedef struct { long N; int g; } cand_t;
int main(int argc, char **argv) {
    long X = atol(argv[1]); double A = argc > 4 ? atof(argv[4]) : 2.6, B = argc > 5 ? atof(argv[5]) : 250;
    long sq = (long)sqrt((double)X) + 2;
    char *c = calloc(sq + 1, 1); int nb = 0; int *bp = malloc((sq + 1) * sizeof(int));
    for (long i = 2; i <= sq; i++) if (!c[i]) { bp[nb++] = (int)i; for (long j = i * i; j <= sq; j += i) c[j] = 1; }
    char *c2 = calloc(QMAX + 1, 1); int nq = 0; int *qp = malloc(QMAX * sizeof(int));
    for (long i = 2; i <= QMAX; i++) if (!c2[i]) { if (i > 2) qp[nq++] = (int)i; for (long j = i * i; j <= QMAX; j += i) c2[j] = 1; }
    long nseg = (X - 6) / (2 * SEG) + 1;
    int nt = omp_get_max_threads();
    cand_t **buf = calloc(nt, sizeof(cand_t *)); long *cnt = calloc(nt, sizeof(long)), *cap = calloc(nt, sizeof(long));
    long *hist = calloc((size_t)nt * QMAX, sizeof(long));
    #pragma omp parallel
    {
        int t = omp_get_thread_num();
        long words = (2 * SEG + QMAX) / 128 + 4; uint64_t *bm = malloc(words * 8);
        long *h = hist + (size_t)t * QMAX;
        #pragma omp for schedule(dynamic, 1)
        for (long s = 0; s < nseg; s++) {
            long lo = 6 + s * 2 * SEG, hi = lo + 2 * SEG; if (hi > X + 1) hi = X + 1;     // even N in [lo, hi)
            long start = lo - QMAX; if (start < 1) start = 1; if (!(start & 1)) start--;   // odd; bit i <-> start + 2 i
            if (start < 1) start = 1;
            long nbits = (hi - start) / 2 + 1;
            memset(bm, 0xff, ((nbits >> 6) + 1) * 8);
            if (start == 1) bm[0] &= ~1ULL;
            for (int i = 1; i < nb; i++) { long p = bp[i]; if (p * p >= hi) break;
                long j = (start + p - 1) / p * p; if (j < p * p) j = p * p; if (!(j & 1)) j += p;
                for (long k = (j - start) >> 1; k < nbits; k += p) bm[k >> 6] &= ~(1ULL << (k & 63)); }
            double tau = 0;
            for (long N = lo; N < hi; N += 2) {
                if (N == lo || !(N & 8190)) { double lg = log((double)N); tau = A * lg * lg - B; }   // refreshed every 4096 N
                int g = 0;
                for (int i = 0; i < nq; i++) { long m = N - qp[i]; if (m < 2) break;
                    long k = (m - start) >> 1; if (bm[k >> 6] >> (k & 63) & 1) { g = qp[i]; break; } }
                if (g == 0) { fprintf(stderr, "no summand below %d for N = %ld\n", QMAX, N); exit(1); }
                h[g]++;
                if (g >= tau) { if (cnt[t] == cap[t]) { cap[t] = cap[t] ? 2 * cap[t] : 1 << 16; buf[t] = realloc(buf[t], cap[t] * sizeof(cand_t)); }
                    buf[t][cnt[t]].N = N; buf[t][cnt[t]].g = g; cnt[t]++; }
            }
        }
        free(bm);
    }
    long total = 0; for (int t = 0; t < nt; t++) total += cnt[t];
    cand_t *all = malloc((total + 1) * sizeof(cand_t)); long k = 0;
    for (int t = 0; t < nt; t++) { memcpy(all + k, buf[t], cnt[t] * sizeof(cand_t)); k += cnt[t]; }
    int cmp(const void *a, const void *b) { long x = ((cand_t *)a)->N, y = ((cand_t *)b)->N; return x < y ? -1 : x > y; }
    qsort(all, total, sizeof(cand_t), cmp);
    FILE *f = fopen(argv[2], "w"); for (long i = 0; i < total; i++) fprintf(f, "%ld %d\n", all[i].N, all[i].g); fclose(f);
    f = fopen(argv[3], "w"); fprintf(f, "# least Goldbach summand of the even N in [6, %ld]: g, number of N\n", X);
    for (int g = 0; g < QMAX; g++) { long v = 0; for (int t = 0; t < nt; t++) v += hist[(size_t)t * QMAX + g]; if (v) fprintf(f, "%d %ld\n", g, v); }
    fclose(f);
    fprintf(stderr, "X = %ld: %ld candidates written\n", X, total);
    return 0;
}
