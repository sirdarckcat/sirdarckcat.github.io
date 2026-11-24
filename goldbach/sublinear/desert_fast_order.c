// desert_fast_order.c -- research's desert_fast.c with ONE change (uarch, 24 Nov 2026): the children of a node are tried in the order of how many unstruck
// primes up to the incumbent their class strikes, most first (ties: desert_fast.c's order, largest modulus first), instead of largest modulus first.
// Everything else is desert_fast.c's code: an independent check of desert_fast3.c's D(n) by a minimal, auditable change of the original program.
// desert_fast.c -- D(n), the same search as desert.c, on bit sets, with the first two levels split over threads.
// D(n) = the largest, over residue vectors on the first n odd primes, of the least odd prime struck by no class.
// Depth-first on "which modulus strikes the smallest unstruck prime"; every vector once (a modulus tried earlier for a
// prime may not take that class later); a branch is cut when the unassigned moduli cannot strike all unstruck primes up to
// the best value so far (each strikes at most its fullest allowed class).  The struck primes of a partial vector are a
// bit set over the first 256 odd primes (up to 1621), the OR of one precomputed set per assigned class.
//   gcc -O2 -fopenmp -o desert_fast desert_fast.c ; OMP_NUM_THREADS=4 ./desert_fast n [known_value]
// known_value: a value known to be attained; the run then proves it is the maximum or finds better.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>
#define MAXN 24
#define NP 256
#define W 4
#define MAXR 128
static int nmod, mod_[MAXN];
static int primes[NP];
static unsigned char res[MAXN][NP];          /* res[m][i] = primes[i] mod mod_[m] */
static uint64_t mask[MAXN][MAXR][W];         /* mask[m][c]: the primes in class c of modulus m */
static volatile int best, bestidx; static int bestcls[MAXN];
typedef struct { int cls[MAXN]; unsigned char used[MAXN]; unsigned char forb[MAXN][MAXR]; long nodes; } st_t;
static void dfs(st_t *s, const uint64_t *st, int left) {
    s->nodes++;
    int i = -1;
    for (int w = 0; w < W; w++) if (~st[w]) { i = w * 64 + __builtin_ctzll(~st[w]); break; }
    if (i < 0) { fprintf(stderr, "every prime below %d struck: enlarge NP\n", primes[NP - 1]); exit(1); }
    if (left == 0) {
        int q = primes[i];
        if (q > best) {
            #pragma omp critical
            if (q > best) { best = q; bestidx = i; for (int m = 0; m < nmod; m++) bestcls[m] = s->cls[m]; }
        }
        return;
    }
    int bi = bestidx;
    if (i <= bi) {
        int U[NP], nu = 0;
        for (int w = i >> 6; w <= bi >> 6; w++) {
            uint64_t x = ~st[w];
            if (w == bi >> 6 && (bi & 63) != 63) x &= (2ull << (bi & 63)) - 1;
            while (x) { U[nu++] = w * 64 + __builtin_ctzll(x); x &= x - 1; }
        }
        int cap = 0;
        for (int m = nmod - 1; m >= 0 && cap < nu; m--) if (!s->used[m]) {
            unsigned char h[MAXR]; memset(h, 0, mod_[m]); int mx = 0; const unsigned char *r = res[m], *f = s->forb[m];
            for (int j = 0; j < nu; j++) { int c = r[U[j]]; if (!f[c] && ++h[c] > mx) mx = h[c]; }
            cap += mx;
        }
        if (cap < nu) return;
    }
    int tried[MAXN], nt = 0;
    int ord[MAXN], sc[MAXN], no = 0;                               /* the order of the children: most unstruck primes up to the incumbent struck first */
    {   uint64_t u[W]; const int lim = i <= bi ? bi : NP - 1;
        for (int w = 0; w < W; w++) { uint64_t x = ~st[w]; if (w * 64 > lim) x = 0; else if (w == lim >> 6 && (lim & 63) != 63) x &= (2ull << (lim & 63)) - 1; u[w] = x; }
        for (int m = nmod - 1; m >= 0; m--) {
            if (s->used[m]) continue;
            int v = 0, c = res[m][i]; for (int w = 0; w < W; w++) v += __builtin_popcountll(u[w] & mask[m][c][w]);
            int j = no++; while (j > 0 && sc[j - 1] < v) { sc[j] = sc[j - 1]; ord[j] = ord[j - 1]; j--; } sc[j] = v; ord[j] = m;
        }
    }
    for (int oi = 0; oi < no; oi++) {
        const int m = ord[oi];
        if (s->used[m]) continue;
        int c = res[m][i];
        if (s->forb[m][c]) continue;
        uint64_t nx[W]; for (int w = 0; w < W; w++) nx[w] = st[w] | mask[m][c][w];
        s->used[m] = 1; s->cls[m] = c;
        dfs(s, nx, left - 1);
        s->used[m] = 0;
        s->forb[m][c]++; tried[nt++] = m;
    }
    for (int j = 0; j < nt; j++) s->forb[tried[j]][res[tried[j]][i]]--;
}
int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 10; int known = argc > 2 ? atoi(argv[2]) : 0;
    static char comp[20000]; int np = 0;
    for (int i = 2; i < 20000 && np < NP; i++) if (!comp[i]) { if (i > 2) primes[np++] = i; for (int j = i * i; j < 20000; j += i) comp[j] = 1; }
    if (n > MAXN || primes[n - 1] >= MAXR) { fprintf(stderr, "n too large\n"); return 1; }
    nmod = n;
    for (int m = 0; m < n; m++) { mod_[m] = primes[m]; for (int i = 0; i < NP; i++) { res[m][i] = primes[i] % mod_[m]; mask[m][res[m][i]][i >> 6] |= 1ull << (i & 63); } }
    best = 0; bestidx = -1;
    if (known) for (int i = 1; i < NP; i++) if (primes[i] == known) { best = primes[i - 1]; bestidx = i - 1; }
    typedef struct { int m1, m2; } task_t; task_t *tasks = malloc(sizeof(task_t) * n * n); int ntask = 0;
    for (int a = n - 1; a >= 0; a--) for (int b = n - 1; b >= 0; b--) if (a != b) { tasks[ntask].m1 = a; tasks[ntask].m2 = b; ntask++; }
    long total = 1; double t0 = omp_get_wtime();                      /* the root */
    #pragma omp parallel for schedule(dynamic, 1) reduction(+:total)
    for (int t = 0; t < ntask; t++) {
        st_t *s = calloc(1, sizeof(st_t)); uint64_t st[W] = {0};
        int m1 = tasks[t].m1, m2 = tasks[t].m2;
        for (int m = n - 1; m > m1; m--) s->forb[m][res[m][0]]++;           /* siblings tried before m1 for the prime 3 */
        s->used[m1] = 1; s->cls[m1] = res[m1][0]; for (int w = 0; w < W; w++) st[w] |= mask[m1][res[m1][0]][w];
        int i = 0; while ((st[i >> 6] >> (i & 63)) & 1) i++;
        int ok = !s->forb[m2][res[m2][i]];
        for (int m = n - 1; m > m2 && ok; m--) if (!s->used[m] && !s->forb[m][res[m][i]]) s->forb[m][res[m][i]]++;   /* siblings tried before m2 */
        if (ok) { s->used[m2] = 1; s->cls[m2] = res[m2][i]; for (int w = 0; w < W; w++) st[w] |= mask[m2][res[m2][i]][w]; dfs(s, st, n - 2); }
        if (m2 == (m1 == n - 1 ? n - 2 : n - 1)) s->nodes++;               /* the level-1 node of this m1, counted once */
        total += s->nodes; free(s);
    }
    printf("n=%d r=%d D=%d nodes=%ld%s seconds=%.0f vector:", n, mod_[n - 1], best, total, known ? " (started from a known value)" : "", omp_get_wtime() - t0);
    for (int m = 0; m < n; m++) printf(" %d:%d", mod_[m], bestcls[m]);
    printf("\n");
    return 0;
}
