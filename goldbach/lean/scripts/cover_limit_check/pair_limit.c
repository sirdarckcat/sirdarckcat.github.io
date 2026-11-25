// pair_limit.c -- exact sums behind steps 1 and 2 of the research session's limit of the counting law
// (goldbach/sublinear/README.md on branch ccr-d4a17dd0-7uu03r, "Where the constant ends up").
//
// For a prime s >= 5 put  u_t = 2/(t - 3) for the primes 5 <= t < s,  u_t = 1/(t - 2) for the primes t > s,
// and no factor for t = 2, 3, s.  For n = 1 .. X this program forms, by a segmented sieve,
//
//     u(n) = prod of u_t over the primes of n      if n is squarefree and prime to 6 s, else 0,
//     f(n) = prod of (1 + u_t) over the primes t of n other than 2, 3, s        (so f = sum of u over divisors),
//
// and prints at checkpoints m the three sums
//
//     M(m) = sum_{d <= m} u(d),      S1(m) = sum_{d <= m} u(d)/d,      F(m) = sum_{j <= m} f(j).
//
// With a = 6 s/(s - 1) and c = prod over the primes t of (1 + u_t/t)^-1 the pair weight of
// GoldbachGaps/CoverPairSums.lean is W(j) = a c f(j), so R(m) = a m - a c F(m); c is printed too
// (primes up to PMAX exactly, the rest by the integral of 1/(t^2 ln t)).
//
// R(m) at a single m carries an oscillation of a few units that depends on the small prime factors of m
// (R(m) = a c sum_d u(d) {m/d}, and {m/d} = 0 when d divides m), so the last column is the mean of R over
// the WIN integers ending at m.
//
// s = 0 stands for "s infinite": u_t = 2/(t - 3) for every prime t >= 5 and a = 6.
//
//   gcc -O3 -march=native -fopenmp -o pair_limit pair_limit.c -lm
//   ./pair_limit s X > out.txt          checkpoints: powers 10^(k/2) and s^rho for rho = 0.25, 0.5, ..., up to X
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SEG (1 << 18)
#define WIN 65536                      // R is also averaged over the WIN integers ending at a checkpoint
#define PMAX 1000000000ULL             // primes up to here enter the product c exactly

static int cmp64(const void *a, const void *b) { uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b; return x < y ? -1 : x > y; }

static double ut(uint64_t t, uint64_t s) { return (s == 0 || t < s) ? 2.0 / ((double)t - 3.0) : 1.0 / ((double)t - 2.0); }

// E1(y) = int_y^oo e^-v/v dv by its continued fraction (y > 1)
static long double e1(long double y) {
    long double b = y + 1, c = 1e300L, d = 1 / b, h = d;
    for (int i = 1; i < 500; i++) { long double an = -(long double)i * i; b += 2; d = 1 / (an * d + b); c = b + an / c; long double del = c * d; h *= del; if (fabsl(del - 1) < 1e-19L) break; }
    return h * expl(-y);
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: pair_limit s X\n"); return 1; }
    uint64_t s = strtoull(argv[1], 0, 10), X = strtoull(argv[2], 0, 10);
    uint64_t B = (uint64_t)sqrtl((long double)X) + 2;
    // small primes up to max(B, 2)
    char *cs = calloc(B + 1, 1); uint32_t *pr = malloc((B / 2 + 16) * sizeof(uint32_t)); int np = 0;
    for (uint64_t i = 2; i <= B; i++) if (!cs[i]) { pr[np++] = (uint32_t)i; for (uint64_t j = i * i; j <= B; j += i) cs[j] = 1; }
    // checkpoints
    uint64_t cp[512]; int ncp = 0;
    for (int k = 2; ; k++) { long double v = powl(10.0L, k / 2.0L); if (v > X * 1.0000001L) break; cp[ncp++] = (uint64_t)llroundl(v); }
    if (s) for (int k = 1; k <= 40; k++) { long double v = powl((long double)s, k / 4.0L); if (v > X * 1.0000001L) break; if (v >= 2) cp[ncp++] = (uint64_t)llroundl(v); }
    cp[ncp++] = X;
    qsort(cp, ncp, sizeof(uint64_t), cmp64);
    int m2 = 0; for (int i = 0; i < ncp; i++) if (cp[i] <= X && (m2 == 0 || cp[i] != cp[m2 - 1])) cp[m2++] = cp[i]; ncp = m2;
    // cut points: m + 1 for every checkpoint m, and m - WIN + 1 (the start of its window)
    uint64_t cut[1100]; int ncut = 0;
    for (int i = 0; i < ncp; i++) { cut[ncut++] = cp[i] + 1; if (cp[i] >= 2 * (uint64_t)WIN) cut[ncut++] = cp[i] - WIN + 1; }
    qsort(cut, ncut, sizeof(uint64_t), cmp64);
    // segments: [lo, hi), never across a cut point
    size_t nseg = 0, cap = X / SEG + 2 * ncp + 8; uint64_t *slo = malloc(cap * 8), *shi = malloc(cap * 8);
    { uint64_t lo = 1; int ic = 0; while (lo <= X) { uint64_t hi = lo + SEG; while (ic < ncut && cut[ic] <= lo) ic++; if (ic < ncut && cut[ic] < hi) hi = cut[ic]; if (hi > X + 1) hi = X + 1; slo[nseg] = lo; shi[nseg] = hi; nseg++; lo = hi; } }
    long double *sM = calloc(nseg, sizeof(long double)), *sS = calloc(nseg, sizeof(long double)), *sF = calloc(nseg, sizeof(long double)), *sP = calloc(nseg, sizeof(long double));
    #pragma omp parallel
    {
        uint64_t *pw = malloc(SEG * 8); double *uv = malloc(SEG * 8), *fv = malloc(SEG * 8); uint8_t *dead = malloc(SEG);
        #pragma omp for schedule(dynamic, 16)
        for (size_t g = 0; g < nseg; g++) {
            uint64_t lo = slo[g], hi = shi[g]; size_t n = hi - lo;
            for (size_t i = 0; i < n; i++) { pw[i] = 1; uv[i] = 1; fv[i] = 1; dead[i] = 0; }
            for (int k = 0; k < np; k++) {
                uint64_t t = pr[k]; if (t * t > hi && t > hi) break;
                if (t >= hi) break;
                int special = (t == 2 || t == 3 || (s && t == s)); double u = special ? 0 : ut(t, s);
                uint64_t j = (lo + t - 1) / t * t;
                if (special) for (; j < hi; j += t) { pw[j - lo] *= t; dead[j - lo] = 1; }
                else for (; j < hi; j += t) { pw[j - lo] *= t; uv[j - lo] *= u; fv[j - lo] *= 1 + u; }
                for (uint64_t q = t * t; q < hi; q *= t) {           // higher powers: the smooth part, and not squarefree
                    for (uint64_t j2 = (lo + q - 1) / q * q; j2 < hi; j2 += q) { pw[j2 - lo] *= t; dead[j2 - lo] = 1; }
                    if (q > hi / t) break;
                }
            }
            long double aM = 0, aS = 0, aF = 0, aP = 0;
            for (size_t i = 0; i < n; i++) {
                uint64_t v = lo + i; double u = uv[i], f = fv[i]; int dd = dead[i];
                if (pw[i] < v) { uint64_t lp = v / pw[i];           // the prime factor above sqrt(X), if any
                    if (s && lp == s) dd = 1; else { double ul = ut(lp, s); u *= ul; f *= 1 + ul; } }
                if (!dd) { aM += u; aS += (long double)u / v; }
                aF += f; aP += aF;                                   // aP: the sum over the segment of its own partial sums of f
            }
            sM[g] = aM; sS[g] = aS; sF[g] = aF; sP[g] = aP;
        }
        free(pw); free(uv); free(fv); free(dead);
    }
    // the constant c: primes up to PMAX exactly (segmented), the tail by E1
    long double lnc = 0; uint64_t npr = 0;
    {
        uint64_t Bc = (uint64_t)sqrtl((long double)PMAX) + 2; char *c2 = calloc(Bc + 1, 1); uint32_t *p2 = malloc((Bc / 2 + 16) * 4); int n2 = 0;
        for (uint64_t i = 2; i <= Bc; i++) if (!c2[i]) { p2[n2++] = (uint32_t)i; for (uint64_t j = i * i; j <= Bc; j += i) c2[j] = 1; }
        size_t ns = PMAX / SEG + 1; long double *part = calloc(ns, sizeof(long double)); uint64_t *cnt = calloc(ns, 8);
        #pragma omp parallel
        {
            uint8_t *sv = malloc(SEG);
            #pragma omp for schedule(dynamic, 16)
            for (size_t g = 0; g < ns; g++) {
                uint64_t lo = (uint64_t)g * SEG, hi = lo + SEG; if (hi > PMAX + 1) hi = PMAX + 1; if (lo >= hi) continue;
                memset(sv, 1, hi - lo);
                for (int k = 0; k < n2; k++) { uint64_t t = p2[k]; if (t * t >= hi) break; uint64_t j = (lo + t - 1) / t * t; if (j < t * t) j = t * t; for (; j < hi; j += t) sv[j - lo] = 0; }
                long double a = 0; uint64_t c0 = 0;
                for (uint64_t v = lo < 2 ? 2 : lo; v < hi; v++) if (sv[v - lo]) { c0++; if (v >= 5 && !(s && v == s)) a -= log1pl((long double)ut(v, s) / v); }
                part[g] = a; cnt[g] = c0;
            }
            free(sv);
        }
        for (size_t g = 0; g < ns; g++) { lnc += part[g]; npr += cnt[g]; }
    }
    // the primes above PMAX: sum of u_t/t ~ int dt/(t^2 ln t) = E1(ln .), twice that while t < s
    long double tail = (s == 0) ? 2 * e1(logl((long double)PMAX))
                     : (s > PMAX) ? 2 * e1(logl((long double)PMAX)) - e1(logl((long double)s)) : e1(logl((long double)PMAX));
    lnc -= tail;
    long double c = expl(lnc), a = s ? 6.0L * s / (s - 1) : 6.0L;
    printf("# s = %llu, X = %llu; a = 6s/(s-1) = %.15Lf; c = %.15Lf (primes to %llu: %llu of them; tail %.3Le)\n",
           (unsigned long long)s, (unsigned long long)X, a, c, (unsigned long long)PMAX, (unsigned long long)npr, tail);
    printf("# m, M(m) = sum u(d), S1(m) = sum u(d)/d, F(m) = sum f(j), R(m) = a m - a c F(m), mean of R over the %d integers ending at m\n", WIN);
    // G[g] = sum over n in segment g of F(n) = F(before the segment) * length + sP[g]
    long double *Fb = malloc(nseg * sizeof(long double)); { long double F0 = 0; for (size_t g = 0; g < nseg; g++) { Fb[g] = F0; F0 += sF[g]; } }
    long double M = 0, S = 0, F = 0; int ic = 0;
    for (size_t g = 0; g < nseg; g++) {
        M += sM[g]; S += sS[g]; F += sF[g];
        while (ic < ncp && cp[ic] + 1 <= shi[g]) {
            if (cp[ic] + 1 == shi[g]) {
                uint64_t m = cp[ic]; long double rbar = NAN;
                if (m >= 2 * (uint64_t)WIN) {                         // the window (m - WIN, m] is a union of segments ending with g
                    long double sumF = 0; size_t h = g;
                    for (;; h--) { sumF += Fb[h] * (long double)(shi[h] - slo[h]) + sP[h]; if (slo[h] == m - WIN + 1) break; }
                    rbar = a * ((long double)m - (WIN - 1) / 2.0L) - a * c * sumF / WIN;
                }
                printf("%llu %.12Lf %.15Lf %.6Lf %.9Lf %.9Lf\n", (unsigned long long)m, M, S, F, a * m - a * c * F, rbar);
            }
            ic++;
        }
    }
    return 0;
}
