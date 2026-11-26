// Exact hits of the miniature (even N < X with no prime p < Q such that N - p is prime) and their exact g(N), for the overshoot test.
// gcc -O3 -march=native -fopenmp -o ovs ovs.c ; ./ovs X Q > hits_X_Q.txt     (lines: N g)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
static uint64_t *bits;     // bit i set = 2i+1 is composite (odd numbers only)
static inline int is_prime(uint64_t n) { if (n < 2) return 0; if (n == 2) return 1; if (!(n & 1)) return 0; return !((bits[(n >> 1) >> 6] >> ((n >> 1) & 63)) & 1); }
int main(int argc, char **argv) {
    uint64_t X = (uint64_t)atof(argv[1]); uint64_t Q = (uint64_t)atof(argv[2]);
    uint64_t nw = ((X >> 1) >> 6) + 2; bits = calloc(nw, 8);
    for (uint64_t i = 3; i * i <= X; i += 2) if (is_prime(i)) for (uint64_t j = i * i; j <= X; j += 2 * i) bits[(j >> 1) >> 6] |= 1ULL << ((j >> 1) & 63);
    uint32_t pr[200000]; int np = 0; for (uint64_t p = 3; p < 400000 && np < 200000; p += 2) if (is_prime(p)) pr[np++] = (uint32_t)p;
    int nq = 0; while (nq < np && pr[nq] < Q) nq++;
    #pragma omp parallel for schedule(dynamic, 1000000)
    for (uint64_t N = 2 * Q + 2; N < X; N += 2) {
        int hit = 1; for (int i = 0; i < nq; i++) { if (is_prime(N - pr[i])) { hit = 0; break; } }
        if (!hit) continue;
        int j = nq; while (j < np && !is_prime(N - pr[j])) j++;
        #pragma omp critical
        printf("%llu %u\n", (unsigned long long)N, j < np ? pr[j] : 0);
    }
    return 0;
}
