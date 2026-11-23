// hgen2.c -- the heuristic N generator with a depth knob, measured against the real sequence.
//
// The heuristic at depth z sees an even number N only through its residues modulo the primes up to z.
// For a striker q (an odd prime up to the current record G) it can tell whether N - q has a prime factor
// <= z (then q is "struck": N - q is certainly composite) or not (q is "open": N - q is prime or a product
// of primes above z, the heuristic cannot know which).  Its score for N is the number of open strikers,
//
//      c_z(N) = #{ q <= G odd prime : N - q has no prime factor <= z },
//
// and the fewer, the likelier that N beats G: the chance is about (1 - rho)^c with rho the density of primes
// among the z-rough numbers near N.  With z >= sqrt(N) the score is 0 exactly for the numbers that beat G:
// the heuristic has become the real thing.
//
// For every stretch between two consecutive real terms (N_k, G_k) -> N_{k+1} and every depth z = N_{k+1}^theta
// this program prints the score c* of the real next term and how many even N of the stretch before it score
// at least as well: that count + 1 is the place of the real term in the heuristic's order of preference.
//
//   gcc -O3 -march=native -fopenmp -o hgen2 hgen2.c -lm
//   ./hgen2 terms.txt 100000 110000000000 0.5 0.45 0.4 0.35 0.3 0.25 0.2 0.15 0.1 > hgen2.txt
//           (terms file; stretches starting at terms >= the second argument and ending at terms <= the third)
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SEGBITS (1L << 20)             // even numbers per segment
#define QMAXP (1 << 15)                // strikers are below this
#define MAXB 9

static int *wheel; static long nwheel;
static int qp[QMAXP], hq[QMAXP], nq;

static inline uint64_t get64(const uint64_t *bm, long k) {
    long w = k >> 6; int s = k & 63;
    return s ? (bm[w] >> s) | (bm[w + 1] << (64 - s)) : bm[w];
}

// Scores of the even N in [lo, hi): hist[c] += number of N with c open strikers, counted exactly below
// 2^B - 1 and lumped together from there on.  Only one block of 64 numbers in `samp` is looked at.
static void stretch(long lo, long hi, int m0, long zlim, long margin, int B, long samp, uint64_t *bm, long *hist) {
    long start = lo - margin - 1;                      // odd; bit k of the window is the number start + 2 k
    long nbits = (hi - start) / 2 + 1;
    memset(bm, 0xff, ((nbits >> 6) + 3) * 8);
    for (long i = 0; i < nwheel; i++) {                // strike out the multiples of the primes up to z
        long p = wheel[i]; if (p > zlim || p * p >= hi) break;
        long j = (start + p - 1) / p * p; if (j < p * p) j = p * p; if (!(j & 1)) j += p;
        for (long k = (j - start) >> 1; k < nbits; k += p) bm[k >> 6] &= ~(1ULL << (k & 63));
    }
    int top = (1 << B) - 1;
    for (long B0 = lo; B0 < hi; B0 += 128) {
        if (samp > 1 && (B0 / 128) % samp) continue;
        long left = (hi - B0) / 2;
        uint64_t valid = left < 64 ? (1ULL << left) - 1 : ~0ULL, c[MAXB] = {0};
        long base = (B0 - 1 - start) >> 1;
        for (int j = 0; j < m0; j++) {
            uint64_t carry = get64(bm, base - hq[j]);  // bit i: striker j is open for N = B0 + 2 i
            for (int b = 0; b < B && carry; b++) { uint64_t t = c[b] & carry; c[b] ^= carry; carry = t; }
            if (carry) for (int b = 0; b < B; b++) c[b] |= carry;       // stay at the top value
            if ((j & 7) == 7) { uint64_t sat = valid; for (int b = 0; b < B; b++) sat &= c[b]; if (sat == valid) break; }
        }
        uint64_t sat = valid; for (int b = 0; b < B; b++) sat &= c[b];
        hist[top] += __builtin_popcountll(sat);
        uint64_t ns = valid & ~sat;
        while (ns) { int i = __builtin_ctzll(ns); ns &= ns - 1;
            int cnt = 0; for (int b = 0; b < B; b++) cnt |= (int)((c[b] >> i) & 1) << b;
            hist[cnt]++; }
    }
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: hgen2 terms.txt from to theta...\n"); return 1; }
    long from = atol(argv[2]), to = atol(argv[3]);
    static long tN[128]; static int tg[128]; int nt = 0;
    FILE *f = fopen(argv[1], "r"); char line[256];
    while (fgets(line, sizeof line, f)) if (line[0] != '#' && sscanf(line, "%ld %d", &tN[nt], &tg[nt]) == 2) nt++;
    fclose(f);
    long wmax = (long)sqrt((double)to) + 100;
    char *cs = calloc(wmax + 1, 1); wheel = malloc((wmax / 2 + 16) * sizeof(int));
    for (long i = 3; i <= wmax; i += 2) if (!cs[i]) { wheel[nwheel++] = (int)i; for (long j = i * i; j <= wmax; j += 2 * i) cs[j] = 1; }
    for (long i = 3; i < QMAXP; i += 2) if (i > wmax || !cs[i]) {
        int ok = 1; for (long d = 3; d * d <= i; d += 2) if (i % d == 0) { ok = 0; break; }
        if (ok) { qp[nq] = (int)i; hq[nq] = (int)((i - 1) / 2); nq++; } }
    int nth = omp_get_max_threads();
    uint64_t **bm = malloc(nth * sizeof(*bm));
    for (int t = 0; t < nth; t++) bm[t] = malloc(((2 * SEGBITS + QMAXP + 64) / 128 + 8) * 8);
    printf("# stretch: from the real term N_k (value G_k) to the next real term; m = number of strikers (odd primes <= G_k)\n");
    printf("# c* = open strikers of the real next term at depth z = N^theta; place = 1 + number of earlier N of the stretch with at most c* open strikers\n");
    printf("# (~ marks a place estimated from one block of 64 numbers in 64)\n");
    printf("# %14s %6s %5s %14s |", "N_k", "G_k", "m", "even N");
    for (int a = 4; a < argc; a++) printf("  theta=%-5s z      c*        place |", argv[a]);
    printf("\n");
    for (int k = 0; k + 1 < nt; k++) {
        if (tN[k] < from || tN[k + 1] > to) continue;
        long Nk = tN[k], Nn = tN[k + 1]; int G = tg[k];
        int m0 = 0; while (m0 < nq && qp[m0] <= G) m0++;
        long margin = 2 * (G / 2 + 2);
        printf("  %14ld %6d %5d %14ld |", Nk, G, m0, (Nn - Nk) / 2 - 1);
        for (int a = 4; a < argc; a++) {
            double theta = atof(argv[a]);
            long zlim = (long)pow((double)Nn, theta) + 1;
            long h1[1 << MAXB]; memset(h1, 0, sizeof h1);
            stretch(Nn, Nn + 2, m0, zlim, margin, MAXB, 1, bm[0], h1);
            int cstar = 0; while (!h1[cstar]) cstar++;
            int B = 1; while ((1 << B) - 1 < cstar + 1) B++;
            long samp = cstar >= 16 ? 64 : 1;
            long nseg = (Nn - (Nk + 2) + 2 * SEGBITS - 1) / (2 * SEGBITS);
            long *hist = calloc((size_t)nth << MAXB, sizeof(long));
            #pragma omp parallel for schedule(dynamic, 4)
            for (long s = 0; s < nseg; s++) {
                long lo = Nk + 2 + s * 2 * SEGBITS, hi = lo + 2 * SEGBITS; if (hi > Nn) hi = Nn;
                int t = omp_get_thread_num();
                if (lo < hi) stretch(lo, hi, m0, zlim, margin, B, samp, bm[t], hist + ((size_t)t << MAXB));
            }
            long better = 0;
            for (int t = 0; t < nth; t++) for (int c = 0; c <= cstar; c++) better += hist[((size_t)t << MAXB) + c];
            free(hist);
            printf("  %11ld %4d %s%12ld |", zlim, cstar, samp > 1 ? "~" : " ", better * samp + 1);
            fflush(stdout);
        }
        printf("\n");
    }
    return 0;
}
