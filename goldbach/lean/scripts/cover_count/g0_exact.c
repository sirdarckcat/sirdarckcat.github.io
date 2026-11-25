// g0_exact.c -- the exact number of complete covers, by going through every class vector.
//
// Moduli: the first n odd primes 3, 5, 7, ...  A class vector gives each modulus r one class a_r in
// [0, r).  It covers a row q (an odd prime) when q = a_r (mod r) for some r.  For every class vector
// this program finds the first row it does not cover and counts the vectors by that row.  Then
//
//      g0(x, Q) = number of class vectors that cover every odd prime below Q
//               = number of vectors whose first uncovered row is >= Q,
//
// the quantity `g0 x Q` of GoldbachGaps/CoverCount.lean (x the largest modulus), exactly, for all Q
// at once.  The last Q with g0 > 0 is the cover depth D(n) of GoldbachGaps/CoverDepth.lean.
//
// The work is prod r steps (3.2e9 for n = 9, 1.0e11 for n = 10), so this is for small n only.
//
//   gcc -O3 -march=native -fopenmp -o g0_exact g0_exact.c
//   ./g0_exact 9 > g0_exact_n9.txt
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define MAXN 16
#define NROWS 63                       // rows are the first 63 odd primes (3 .. 311)

static int mod[MAXN], n;
static int row[NROWS];
static uint64_t cls[MAXN][64];         // cls[j][c]: the rows in class c of modulus j

static int is_prime(int v) { if (v < 2) return 0; for (int d = 2; d * d <= v; d++) if (v % d == 0) return 0; return 1; }

// moduli 1 .. n-2 by recursion (modulus 0 is the parallel loop), modulus n-1 in the inner loop
static void rec(int j, uint64_t mask, uint64_t *hist) {
    if (j == n - 1) {
        const uint64_t *c = cls[j];
        for (int a = 0; a < mod[j]; a++) hist[__builtin_ctzll(~(mask | c[a]))]++;
        return;
    }
    for (int a = 0; a < mod[j]; a++) rec(j + 1, mask | cls[j][a], hist);
}

int main(int argc, char **argv) {
    n = argc > 1 ? atoi(argv[1]) : 9;
    if (n < 2 || n > MAXN) { fprintf(stderr, "usage: g0_exact n   (2 <= n <= %d moduli)\n", MAXN); return 1; }
    int k = 0;
    for (int v = 3; k < NROWS; v += 2) if (is_prime(v)) row[k++] = v;
    // the largest modulus goes last (inner loop), the second largest first (parallel loop)
    int pr[MAXN]; for (int j = 0; j < n; j++) pr[j] = row[j];
    mod[n - 1] = pr[n - 1]; mod[0] = pr[n - 2];
    for (int j = 1; j < n - 1; j++) mod[j] = pr[j - 1];
    for (int j = 0; j < n; j++) for (int i = 0; i < NROWS; i++) cls[j][row[i] % mod[j]] |= 1ULL << i;

    uint64_t total[64] = {0};
    #pragma omp parallel
    {
        uint64_t hist[64] = {0};
        #pragma omp for schedule(dynamic, 1)
        for (int a = 0; a < mod[0]; a++) rec(1, cls[0][a], hist);
        #pragma omp critical
        for (int i = 0; i < 64; i++) total[i] += hist[i];
    }
    double lnall = 0; unsigned __int128 all = 1;
    for (int j = 0; j < n; j++) { lnall += log((double)pr[j]); all *= (unsigned)pr[j]; }
    unsigned __int128 seen = 0; for (int i = 0; i < 64; i++) seen += total[i];
    printf("# moduli: the first %d odd primes, 3 .. %d; class vectors: %llu (ln = %.6f)\n", n, pr[n - 1], (unsigned long long)all, lnall);
    printf("# vectors counted: %llu%s\n", (unsigned long long)seen, seen == all ? " (all of them)" : "  MISMATCH");
    printf("# Q = an odd prime; first = vectors whose first uncovered row is Q; g0 = vectors covering every odd prime below Q\n");
    printf("# %5s %14s %14s %12s %12s\n", "Q", "first", "g0(x,Q)", "ln g0", "loss");
    unsigned __int128 g0 = all;
    for (int i = 0; i < NROWS && g0 > 0; i++) {
        printf("  %5d %14llu %14llu %12.6f %12.6f\n", row[i], (unsigned long long)total[i], (unsigned long long)g0,
               log((double)g0), lnall - log((double)g0));
        g0 -= total[i];
        if (g0 == 0) printf("# no class vector covers every odd prime up to %d: the cover depth is D(%d) = %d\n", row[i], n, row[i]);
    }
    return 0;
}
