// desert.c -- how far the first n odd primes can strike every prime, with no luck.
//
// D(n) = the maximum, over all residue vectors (a_r mod r), r the first n odd primes, of the least odd prime q with
// q != a_r (mod r) for every r.  For N = a_r (mod r), N - q is divisible by some r for every odd prime q < D(n): the
// least Goldbach summand of such an N is at least D(n) whatever happens beyond the first n odd primes (when N - q is not
// r itself), and D(n) is the first prime that no choice of N strikes.  Class 0 is allowed; it strikes q = r only.
//
// Exact, by depth-first search on "which modulus strikes the smallest unstruck prime".  Every vector is reached once (a
// modulus tried earlier for a prime may not take that class in the later branches), and a branch is cut when the unassigned
// moduli cannot strike all the unstruck primes up to the best value found so far (each strikes at most its fullest class).
//
//   gcc -O2 -o desert desert.c ; ./desert nmax [nmin=1]        prints n, r_n, D(n), nodes visited, one optimal vector
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 40
#define MAXP 100000
#define MAXR 512
static int nmod, mod_[MAXN], cls[MAXN], used[MAXN];
static int primes[MAXP], np;
static int best, bestidx, bestcls[MAXN];
static long nodes;
static unsigned char forb[MAXN][MAXR];      /* forbidden classes per modulus */
static int struck(int q) { for (int m = 0; m < nmod; m++) if (used[m] && q % mod_[m] == cls[m]) return 1; return 0; }
static void dfs(int from, int left) {
    nodes++;
    int i = from; while (struck(primes[i])) i++;
    int q = primes[i];
    if (left == 0) { if (q > best) { best = q; bestidx = i; memcpy(bestcls, cls, sizeof(int) * nmod); } return; }
    if (i <= bestidx) {                          /* can the unassigned moduli strike everything up to the incumbent? */
        static int U[MAXP]; int nu = 0;
        for (int j = i; j <= bestidx; j++) if (!struck(primes[j])) U[nu++] = primes[j];
        int cap = 0;
        for (int m = 0; m < nmod && cap < nu; m++) if (!used[m]) {
            int cnt[MAXR] = {0}, mx = 0, r = mod_[m];
            for (int j = 0; j < nu; j++) { int c = U[j] % r; if (!forb[m][c] && ++cnt[c] > mx) mx = cnt[c]; }
            cap += mx;
        }
        if (cap < nu) return;
    }
    int tried[MAXN], nt = 0;
    for (int m = nmod - 1; m >= 0; m--) {        /* large moduli first */
        if (used[m]) continue;
        int c = q % mod_[m];
        if (forb[m][c]) continue;
        used[m] = 1; cls[m] = c;
        dfs(i + 1, left - 1);
        used[m] = 0;
        forb[m][c]++; tried[nt++] = m;
    }
    for (int j = 0; j < nt; j++) forb[tried[j]][q % mod_[tried[j]]]--;
}
int main(int argc, char **argv) {
    int nmax = argc > 1 ? atoi(argv[1]) : 10, nmin = argc > 2 ? atoi(argv[2]) : 1;
    static char comp[2000000];
    for (int i = 2; i < 2000000 && np < MAXP; i++) if (!comp[i]) { if (i > 2) primes[np++] = i; for (long j = (long)i * i; j < 2000000; j += i) comp[j] = 1; }
    for (int n = nmin; n <= nmax; n++) {
        nmod = n; for (int m = 0; m < n; m++) mod_[m] = primes[m];
        memset(used, 0, sizeof used); memset(forb, 0, sizeof forb); best = 0; bestidx = -1; nodes = 0;
        dfs(0, n);
        printf("n=%d r=%d D=%d nodes=%ld vector:", n, mod_[n - 1], best, nodes);
        for (int m = 0; m < n; m++) printf(" %d:%d", mod_[m], bestcls[m]);
        printf("\n"); fflush(stdout);
    }
    return 0;
}
