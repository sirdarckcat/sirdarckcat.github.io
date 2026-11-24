// ngen.c -- an N generator for A025018.  It walks the even numbers N = 4, 6, 8, ... and prints N the moment
// its least Goldbach summand g(N) (the least prime q with N - q prime) is larger than that of every even
// number before it.  It is the walker of GoldbachGaps/RecordWalk.lean (`walk`, proved to announce exactly the
// terms of A025018), made fast.
//
//   gcc -O3 -march=native -fopenmp -o ngen ngen.c -lm
//   ./ngen [limit]          prints "N g(N)" for every term N <= limit, in order, as they are found
//                           (limit 0 or absent: runs until it is stopped)
//   ./ngen limit from G     the same walk taken up at the even number `from` >= 2^20, G being the largest
//                           least summand below `from`: the two numbers of a "# state" line on stderr
//
// What it keeps while walking:
//   G        the largest least summand so far (one number);
//   strikers the odd primes up to G (a few hundred to a few thousand numbers);
//   a window the primes among the last QMAX odd numbers below N, as bits;
//   wheels   the primes up to sqrt(N), used only to mark the primes of the next stretch (Eratosthenes).
// The question asked of N: is one of N - 3, N - 5, N - 7, N - 11, ..., N - (largest striker) a prime?  If not,
// N is announced.  The question is put to 64 consecutive even numbers at once: bit i of `un` says that
// N = B + 2 i has not met a prime yet, and one striker q removes from `un` the 64 window bits at B - q.
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define QMAX (1 << 17)            // width of the window; the program stops if some g(N) is not below it
#define N1 (1L << 20)             // below this the plain walker; from here on 64 numbers at a time
#define SEGBITS (1L << 21)        // even numbers per stretch

typedef struct { long N; int g; } cand_t;
typedef struct { cand_t *v; long n, cap; } list_t;

static int *wheel; static long nwheel, wheel_lim;      // the odd primes up to wheel_lim
static int qp[QMAX], hq[QMAX], nq;                     // the odd primes q below QMAX, and (q - 1) / 2

static void make_wheels(long lim) {                    // the odd primes up to lim
    free(wheel);
    char *c = calloc(lim + 1, 1); long cap = 1024; wheel = malloc(cap * sizeof(int)); nwheel = 0;
    for (long i = 3; i <= lim; i += 2) if (!c[i]) {
        if (nwheel == cap) { cap *= 2; wheel = realloc(wheel, cap * sizeof(int)); }
        wheel[nwheel++] = (int)i;
        for (long j = i * i; j <= lim; j += 2 * i) c[j] = 1;
    }
    free(c); wheel_lim = lim;
}

static void push(list_t *l, long N, int g) {
    if (l->n == l->cap) { l->cap = l->cap ? 2 * l->cap : 64; l->v = realloc(l->v, l->cap * sizeof(cand_t)); }
    l->v[l->n].N = N; l->v[l->n].g = g; l->n++;
}

static inline uint64_t get64(const uint64_t *bm, long k) {     // the 64 bits from position k on
    long w = k >> 6; int s = k & 63;
    return s ? (bm[w] >> s) | (bm[w + 1] << (64 - s)) : bm[w];
}

// The even N in [lo, hi) that no striker qp[0 .. m0) hits, each with its least summand.  lo >= N1.
static void stretch(long lo, long hi, int m0, uint64_t *bm, list_t *out) {
    long start = lo - QMAX - 1;                        // odd; bit k of the window is the number start + 2 k
    long nbits = (hi - start) / 2 + 1;
    memset(bm, 0xff, ((nbits >> 6) + 3) * 8);
    for (long i = 0; i < nwheel; i++) {                // mark the primes of the stretch
        long p = wheel[i]; if (p * p >= hi) break;
        long j = (start + p - 1) / p * p; if (j < p * p) j = p * p; if (!(j & 1)) j += p;
        for (long k = (j - start) >> 1; k < nbits; k += p) bm[k >> 6] &= ~(1ULL << (k & 63));
    }
    for (long B = lo; B < hi; B += 128) {              // the 64 even numbers B, B + 2, ..., B + 126
        long left = (hi - B) / 2;
        uint64_t un = left < 64 ? (1ULL << left) - 1 : ~0ULL;
        long base = (B - 1 - start) >> 1;              // position of B - 1; B - q is at base - (q - 1) / 2
        for (int j = 0; j < m0 && un; j++) un &= ~get64(bm, base - hq[j]);
        while (un) {                                   // these beat every striker so far: find their summand
            int i = __builtin_ctzll(un); un &= un - 1;
            int g = 0;
            for (int j = m0; j < nq; j++) { long k = base + i - hq[j]; if (bm[k >> 6] >> (k & 63) & 1) { g = qp[j]; break; } }
            if (!g) { printf("%ld has no Goldbach summand below %d\n", B + 2 * i, QMAX); fflush(stdout); exit(2); }
            push(out, B + 2 * i, g);
        }
    }
}

int main(int argc, char **argv) {
    long limit = argc > 1 ? atol(argv[1]) : 0;         // 0: no limit
    long from = argc > 3 ? atol(argv[2]) : N1;
    if (from < N1 || (from & 1)) { fprintf(stderr, "from must be an even number >= %ld\n", N1); return 1; }
    double t0 = omp_get_wtime(), tlast = t0;
    // the plain walker, for N < N1
    char *c = calloc(N1 + 1, 1); c[0] = c[1] = 1;
    for (long i = 2; i * i <= N1; i++) if (!c[i]) for (long j = i * i; j <= N1; j += i) c[j] = 1;
    for (long i = 3; i < QMAX; i += 2) if (!c[i]) { qp[nq] = (int)i; hq[nq] = (int)((i - 1) / 2); nq++; }
    int G = argc > 3 ? atoi(argv[3]) : 0;
    if (argc <= 3) for (long N = 4; N < N1 && (!limit || N <= limit); N += 2) {
        int g = 0;
        if (N == 4) g = 2;
        else for (int j = 0; j < nq && qp[j] <= N - 2; j++) if (!c[N - qp[j]]) { g = qp[j]; break; }
        if (!g) { printf("%ld has no Goldbach summand\n", N); return 2; }
        if (g > G) { G = g; printf("%ld %d\n", N, g); fflush(stdout); }
    }
    free(c);
    // from N1 on: stretches of SEGBITS even numbers, several at a time
    int nt = omp_get_max_threads(), ns = 4 * nt;
    uint64_t **bm = malloc(nt * sizeof(*bm));
    for (int t = 0; t < nt; t++) bm[t] = malloc(((2 * SEGBITS + QMAX) / 128 + 8) * 8);
    list_t *out = calloc(ns, sizeof(list_t));
    long lo = from;
    for (; !limit || lo <= limit; lo += ns * 2 * SEGBITS) {
        long top = lo + ns * 2 * SEGBITS;
        if (wheel_lim * wheel_lim < top) make_wheels(2 * (long)sqrt((double)top) + 16);
        int m0 = 0; while (m0 < nq && qp[m0] <= G) m0++;          // the strikers: the odd primes up to G
        #pragma omp parallel for schedule(dynamic, 1)
        for (int s = 0; s < ns; s++) {
            long a = lo + s * 2 * SEGBITS, b = a + 2 * SEGBITS;
            out[s].n = 0;
            if (limit && b > limit + 1) b = limit + 1;
            if (a < b) stretch(a, b, m0, bm[omp_get_thread_num()], &out[s]);
        }
        for (int s = 0; s < ns; s++) for (long i = 0; i < out[s].n; i++)       // in order of N
            if (out[s].v[i].g > G) { G = out[s].v[i].g; printf("%ld %d\n", out[s].v[i].N, G); fflush(stdout); }
        double t = omp_get_wtime();
        if (t - tlast > 60 && (!limit || top <= limit)) {
            tlast = t; fprintf(stderr, "# state %ld %d   (every even N below %ld is done; %.0f s)\n", top, G, top, t - t0); }
    }
    fprintf(stderr, "# done: every even N <= %ld, largest least summand %d, %.1f s\n", limit, G, omp_get_wtime() - t0);
    return 0;
}
