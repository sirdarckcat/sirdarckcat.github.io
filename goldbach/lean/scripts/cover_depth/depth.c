// depth.c -- D(n): the largest, over residue vectors (a_i mod r_i) on the first n odd primes r_i, of the least
// odd prime q with q != a_i (mod r_i) for all i.  Plain depth-first search: strike the least unstruck prime
// with each remaining modulus in turn.  Optional pruning by capacity (argument 2 = 1).
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define W 6
#define NP (64 * W)
static int pr[NP], np;                 // odd primes
static int n, r[64];
static uint64_t cm[32][128][W];        // cm[i][c]: primes = c mod r[i]
static uint64_t upto[NP + 1][W];       // primes with index < k
static int best, bestvec[64], cur[64], prune;
static unsigned long long nodes;
static void dfs(unsigned rem, const uint64_t *U) {
    nodes++;
    int j = -1;
    for (int w = 0; w < W; w++) if (U[w]) { j = 64 * w + __builtin_ctzll(U[w]); break; }
    if (j < 0) { fprintf(stderr, "all primes struck: raise NP\n"); exit(1); }
    int q = pr[j];
    if (!rem) { if (q > best) { best = q; memcpy(bestvec, cur, sizeof cur); } return; }
    if (prune && q <= best) {
        // to beat `best`, every unstruck prime <= best must be struck by the remaining moduli
        int jb = 0; while (pr[jb] <= best) jb++;
        uint64_t T[W]; int need = 0;
        for (int w = 0; w < W; w++) { T[w] = U[w] & upto[jb][w]; need += __builtin_popcountll(T[w]); }
        int capsum = 0;
        for (int i = 0; i < n && capsum < need; i++) if (rem >> i & 1) {
            int mx = 0;
            for (int c = 0; c < r[i]; c++) { int k = 0; for (int w = 0; w < W; w++) k += __builtin_popcountll(T[w] & cm[i][c][w]); if (k > mx) mx = k; }
            capsum += mx;
        }
        if (capsum < need) return;
    }
    for (int i = 0; i < n; i++) if (rem >> i & 1) {
        uint64_t V[W]; int c = q % r[i];
        for (int w = 0; w < W; w++) V[w] = U[w] & ~cm[i][c][w];
        cur[i] = c;
        dfs(rem & ~(1u << i), V);
    }
}
int main(int argc, char **argv) {
    n = atoi(argv[1]); prune = argc > 2 ? atoi(argv[2]) : 0;
    for (int m = 3; np < NP; m += 2) { int ok = 1; for (int d = 3; d * d <= m; d += 2) if (m % d == 0) { ok = 0; break; } if (ok) pr[np++] = m; }
    for (int i = 0; i < n; i++) r[i] = pr[i];
    for (int i = 0; i < n; i++) for (int j = 0; j < np; j++) cm[i][pr[j] % r[i]][j >> 6] |= 1ULL << (j & 63);
    for (int k = 1; k <= np; k++) { memcpy(upto[k], upto[k - 1], sizeof upto[k]); upto[k][(k - 1) >> 6] |= 1ULL << ((k - 1) & 63); }
    uint64_t U[W]; memset(U, 0xff, sizeof U);
    dfs((1u << n) - 1, U);
    printf("n = %d  r_n = %d  D(n) = %d  nodes = %llu  vector:", n, r[n - 1], best, nodes);
    for (int i = 0; i < n; i++) printf(" %d:%d", r[i], bestvec[i]);
    printf("\n");
    return 0;
}
