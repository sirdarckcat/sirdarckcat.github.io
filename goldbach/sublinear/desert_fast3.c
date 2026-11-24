// desert_fast3.c -- D(n), the exact search of desert.c / desert_fast.c, ~1000x faster from n = 15 on (uarch, 24 Nov 2026).
// D(n) = the largest, over residue vectors on the first n odd primes, of the least odd prime struck by no class (class 0 allowed: it strikes q = r).
// The same depth-first search ("which modulus strikes an unstruck prime", every vector once: a modulus tried for a prime in an earlier branch is
// forbidden that class in the later ones) with the same cut (the unassigned moduli, each at its fullest allowed class, cannot strike all unstruck
// primes up to the incumbent), and four changes:
//   1. child order (CORDER, default 2): the moduli that can strike the branching prime are tried by how many unstruck primes up to the incumbent
//      their class strikes, most first (1: smallest modulus first; 0: largest first, as desert_fast.c).  Because a modulus tried first is then
//      forbidden that class in its later siblings, trying the small moduli early takes away one of their few classes in all the later subtrees,
//      and the cut fires there almost at once: 1.39e9 -> 2.8e6 nodes at n = 14.  This is most of the gain.
//   2. branching prime (MRV, default 1): the unstruck prime up to the incumbent with the fewest moduli still able to strike it (bit-sliced
//      counts over the forbidden classes), else the smallest unstruck prime.  Any vector that beats the incumbent strikes that prime.  A prime
//      no modulus can strike any more cuts the node at once.
//   3. the cut's class histograms are carried down the path (a child copies its parent's rows and subtracts the few primes its class strikes)
//      instead of rebuilt at every node; the fullest allowed class is an AVX2 max over HR bytes (scalar fallback); a node rebuilds them when
//      another thread has improved the incumbent (a stale histogram is over fewer primes and can only cut less, never wrongly).
//   4. the first three levels are split into tasks (desert_fast.c: two) for the threads.
// Completeness of 1 and 2: a vector that beats the incumbent must strike every unstruck prime up to it, so it lies in the subtree of the first
// child (in whatever order) whose modulus strikes the branching prime in it; at a node with no such prime left the search branches on the
// smallest unstruck prime as before.  Checked: D(1..15) as published (desert_check.py), and D(16..18) agree between CORDER 1 and 2, with and
// without MRV, and (D(16)) with desert_fast2.c's original order.
//   gcc -O3 -march=native -fopenmp -o desert_fast3 desert_fast3.c ; OMP_NUM_THREADS=4 ./desert_fast3 n [known_value] [split_depth]
// known_value: a value known to be attained; the run then proves it is the maximum or finds better.  Moduli must be below HR (default 128: n <= 30;
// MAXN 24, NP 256 primes up to 1621).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>
#define MAXN 24
#define NP 256
#define W 4
#define MAXR 128
#ifndef HR
#define HR 128          /* histogram row: classes 0 .. HR - 1; needs every modulus < HR (n <= 30); -DHR=64 is a little faster for n <= 17 */
#endif
static int nmod, mod_[MAXN];
static int primes[NP];
static unsigned char res[MAXN][NP];          /* res[m][i] = primes[i] mod mod_[m] */
static uint64_t mask[MAXN][MAXR][W];         /* mask[m][c]: the primes in class c of modulus m */
static volatile int best, bestidx; static int bestcls[MAXN];
#ifndef MRV
#define MRV 1
#endif
#ifndef CORDER
#define CORDER 2
#endif
typedef struct { int cls[MAXN]; unsigned char used[MAXN]; unsigned char forb[MAXN][HR]; long nodes, rebuilds, zcuts; int nfree, freem[MAXN];
                 uint64_t F[MAXN][W]; } st_t;   /* freem: the unassigned moduli, descending; F[m]: the primes in the forbidden classes of m */
static inline void forb_inc(st_t *s, int m, int c) { if (s->forb[m][c]++ == 0) for (int w = 0; w < W; w++) s->F[m][w] |= mask[m][c][w]; }
static inline void forb_dec(st_t *s, int m, int c) { if (--s->forb[m][c] == 0) for (int w = 0; w < W; w++) s->F[m][w] &= ~mask[m][c][w]; }
typedef struct { unsigned char h[MAXN][HR]; int bi, nu; } hist_t;   /* bi = -2: not built */

static inline void ubits(const uint64_t *st, int bi, uint64_t *u) {  /* the unstruck primes with index <= bi */
    for (int w = 0; w < W; w++) {
        uint64_t x = ~st[w];
        if (w * 64 > bi) x = 0;
        else if (w == bi >> 6 && (bi & 63) != 63) x &= (2ull << (bi & 63)) - 1;
        u[w] = x;
    }
}
static void build(const st_t *s, const uint64_t *st, int bi, hist_t *H) {
    uint64_t u[W]; ubits(st, bi, u);
    int nu = 0;
    for (int k = 0; k < s->nfree; k++) memset(H->h[s->freem[k]], 0, HR);
    for (int w = 0; w < W; w++) {
        uint64_t x = u[w];
        while (x) {
            const int p = w * 64 + __builtin_ctzll(x); x &= x - 1; nu++;
            for (int k = 0; k < s->nfree; k++) { const int m = s->freem[k]; H->h[m][res[m][p]]++; }
        }
    }
    H->bi = bi; H->nu = nu;
}
#if defined(__AVX2__) && HR == 128
#include <immintrin.h>
static inline int maxallowed(const unsigned char *h, const unsigned char *f) {   /* max over the classes c with f[c] == 0 of h[c], 128 classes */
    const __m256i z = _mm256_setzero_si256();
    __m256i v = z;
    for (int q = 0; q < 4; q++) {
        const __m256i hh = _mm256_loadu_si256((const __m256i *)(h + 32 * q)), ff = _mm256_loadu_si256((const __m256i *)(f + 32 * q));
        v = _mm256_max_epu8(v, _mm256_and_si256(hh, _mm256_cmpeq_epi8(ff, z)));
    }
    __m128i x = _mm_max_epu8(_mm256_castsi256_si128(v), _mm256_extracti128_si256(v, 1));
    x = _mm_max_epu8(x, _mm_srli_si128(x, 8)); x = _mm_max_epu8(x, _mm_srli_si128(x, 4));
    x = _mm_max_epu8(x, _mm_srli_si128(x, 2)); x = _mm_max_epu8(x, _mm_srli_si128(x, 1));
    return _mm_cvtsi128_si32(x) & 0xFF;
}
static inline void copyrow(unsigned char *d, const unsigned char *s) {
    for (int q = 0; q < 4; q++) _mm256_storeu_si256((__m256i *)(d + 32 * q), _mm256_loadu_si256((const __m256i *)(s + 32 * q)));
}
#elif defined(__AVX2__) && HR == 64
#include <immintrin.h>
static inline int maxallowed(const unsigned char *h, const unsigned char *f) {   /* max over the classes c with f[c] == 0 of h[c] */
    const __m256i z = _mm256_setzero_si256();
    const __m256i h0 = _mm256_loadu_si256((const __m256i *)h), h1 = _mm256_loadu_si256((const __m256i *)(h + 32));
    const __m256i f0 = _mm256_loadu_si256((const __m256i *)f), f1 = _mm256_loadu_si256((const __m256i *)(f + 32));
    __m256i v = _mm256_max_epu8(_mm256_and_si256(h0, _mm256_cmpeq_epi8(f0, z)), _mm256_and_si256(h1, _mm256_cmpeq_epi8(f1, z)));
    __m128i x = _mm_max_epu8(_mm256_castsi256_si128(v), _mm256_extracti128_si256(v, 1));
    x = _mm_max_epu8(x, _mm_srli_si128(x, 8)); x = _mm_max_epu8(x, _mm_srli_si128(x, 4));
    x = _mm_max_epu8(x, _mm_srli_si128(x, 2)); x = _mm_max_epu8(x, _mm_srli_si128(x, 1));
    return _mm_cvtsi128_si32(x) & 0xFF;
}
static inline void copyrow(unsigned char *d, const unsigned char *s) {
    _mm256_storeu_si256((__m256i *)d, _mm256_loadu_si256((const __m256i *)s));
    _mm256_storeu_si256((__m256i *)(d + 32), _mm256_loadu_si256((const __m256i *)(s + 32)));
}
#else
static inline int maxallowed(const unsigned char *h, const unsigned char *f) {
    unsigned char mx = 0;
    for (int c = 0; c < HR; c++) { const unsigned char v = f[c] ? 0 : h[c]; mx = v > mx ? v : mx; }
    return mx;
}
static inline void copyrow(unsigned char *d, const unsigned char *s) { memcpy(d, s, HR); }
#endif
static void dfs(st_t *s, const uint64_t *st, int left, hist_t *H) {
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
    const int bi = bestidx;
    const int bounded = i <= bi;
    int br = i;                                                         /* the prime this node branches on */
    if (bounded) {
        {   /* options of the primes of U (unassigned moduli whose class for them is allowed), bit-sliced and saturating at 4:
               a prime with none can never be struck (cut); the branching prime is one with the fewest (the smallest among them) */
            uint64_t u[W]; ubits(st, bi, u);
            uint64_t c0[W] = {0}, c1[W] = {0}, c2[W] = {0};
            for (int k = 0; k < s->nfree; k++) {
                const uint64_t *f = s->F[s->freem[k]];
                for (int w = 0; w < W; w++) { const uint64_t a = u[w] & ~f[w], t0 = c0[w] & a, t1 = c1[w] & t0; c0[w] ^= a; c1[w] ^= t0; c2[w] |= t1; }
            }
            uint64_t z = 0; for (int w = 0; w < W; w++) z |= u[w] & ~(c0[w] | c1[w] | c2[w]);
            if (z) { s->zcuts++; return; }
#if MRV
            int pick = -1;
            for (int lvl = 1; lvl <= 3 && pick < 0; lvl++)
                for (int w = 0; w < W && pick < 0; w++) {
                    const uint64_t x = u[w] & ~c2[w] & ((lvl & 1) ? c0[w] : ~c0[w]) & ((lvl & 2) ? c1[w] : ~c1[w]);
                    if (x) pick = w * 64 + __builtin_ctzll(x);
                }
            if (pick >= 0) br = pick;
#endif
        }
        if (H->bi != bi) { build(s, st, bi, H); s->rebuilds++; }
        const int nu = H->nu;
        int cap = 0;
        for (int k = 0; k < s->nfree && cap < nu; k++) { const int m = s->freem[k]; cap += maxallowed(H->h[m], s->forb[m]); }
        if (cap < nu) return;
    }
    hist_t C;
    int tried[MAXN], nt = 0;
    int ord[MAXN], no = 0;
#if CORDER == 1
    for (int m = 0; m < nmod; m++) ord[no++] = m;
#elif CORDER == 2
    {   int sc[MAXN]; uint64_t uu[W]; ubits(st, bounded ? bi : NP - 1, uu);
        for (int m = nmod - 1; m >= 0; m--) { if (s->used[m]) continue; int c = res[m][br], v = 0; for (int w = 0; w < W; w++) v += __builtin_popcountll(uu[w] & mask[m][c][w]);
            int j = no++; while (j > 0 && sc[j - 1] < v) { sc[j] = sc[j - 1]; ord[j] = ord[j - 1]; j--; } sc[j] = v; ord[j] = m; } }
#else
    for (int m = nmod - 1; m >= 0; m--) ord[no++] = m;
#endif
    for (int oi = 0; oi < no; oi++) {
        const int m = ord[oi];
        if (s->used[m]) continue;
        int c = res[m][br];
        if (s->forb[m][c]) continue;
        uint64_t nx[W]; for (int w = 0; w < W; w++) nx[w] = st[w] | mask[m][c][w];
        s->used[m] = 1; s->cls[m] = c;
        int pos = 0; while (s->freem[pos] != m) pos++;                 /* take m out of the list (order kept) */
        for (int k = pos; k < s->nfree - 1; k++) s->freem[k] = s->freem[k + 1];
        s->nfree--;
        if (bounded && left > 1) {                                     /* the child's histograms: the parent's minus the primes of U this class strikes */
            uint64_t u[W]; ubits(st, bi, u);
            for (int k = 0; k < s->nfree; k++) copyrow(C.h[s->freem[k]], H->h[s->freem[k]]);
            int struck = 0;
            for (int w = 0; w < W; w++) {
                uint64_t x = u[w] & mask[m][c][w];
                while (x) {
                    const int p = w * 64 + __builtin_ctzll(x); x &= x - 1; struck++;
                    for (int k = 0; k < s->nfree; k++) { const int mm = s->freem[k]; C.h[mm][res[mm][p]]--; }
                }
            }
            C.bi = bi; C.nu = H->nu - struck;
        } else C.bi = -2;
        dfs(s, nx, left - 1, &C);
        for (int k = s->nfree; k > pos; k--) s->freem[k] = s->freem[k - 1];    /* put m back at its place */
        s->freem[pos] = m; s->nfree++;
        s->used[m] = 0;
        forb_inc(s, m, c); tried[nt++] = m;
    }
    for (int j = 0; j < nt; j++) forb_dec(s, tried[j], res[tried[j]][br]);
}

/* the parallel split: the first `depth` levels of the same search are enumerated serially (in the same order, with the same forbidden
   classes as the search would have at that point) into prefixes; each prefix is a task run by dfs() below it */
typedef struct { int len; int m[MAXN]; } prefix_t;
static prefix_t *pre; static int npre, cappre;
static void enum_prefixes(st_t *s, const uint64_t *st, int left, int depth, prefix_t *cur) {
    if (depth == 0 || left == 0) {
        if (npre == cappre) { cappre = cappre ? 2 * cappre : 1024; pre = realloc(pre, sizeof(prefix_t) * cappre); }
        pre[npre++] = *cur;
        return;
    }
    int i = -1;
    for (int w = 0; w < W; w++) if (~st[w]) { i = w * 64 + __builtin_ctzll(~st[w]); break; }
    int tried[MAXN], nt = 0;
    for (int m = nmod - 1; m >= 0; m--) {
        if (s->used[m]) continue;
        int c = res[m][i];
        if (s->forb[m][c]) continue;
        uint64_t nx[W]; for (int w = 0; w < W; w++) nx[w] = st[w] | mask[m][c][w];
        s->used[m] = 1; s->cls[m] = c;
        cur->m[cur->len++] = m;
        enum_prefixes(s, nx, left - 1, depth - 1, cur);
        cur->len--;
        s->used[m] = 0;
        s->forb[m][c]++; tried[nt++] = m;
    }
    for (int j = 0; j < nt; j++) s->forb[tried[j]][res[tried[j]][i]]--;
}
/* replay a prefix: the state (classes, used, forbidden classes) the serial search has when it enters that node; returns the struck set.
   The forbidden classes at a node are those of the siblings tried before it at every level above (and they are undone when that level
   is left, so only the path's levels matter). */
static void replay(st_t *s, const prefix_t *p, uint64_t *st) {
    memset(st, 0, sizeof(uint64_t) * W);
    for (int d = 0; d < p->len; d++) {
        int i = 0; while ((st[i >> 6] >> (i & 63)) & 1) i++;
        for (int m = nmod - 1; m > p->m[d]; m--)                        /* the siblings tried before this one at this level */
            if (!s->used[m] && !s->forb[m][res[m][i]]) forb_inc(s, m, res[m][i]);
        const int m = p->m[d], c = res[m][i];
        s->used[m] = 1; s->cls[m] = c;
        for (int w = 0; w < W; w++) st[w] |= mask[m][c][w];
    }
}
int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 10; int known = argc > 2 ? atoi(argv[2]) : 0; int split = argc > 3 ? atoi(argv[3]) : 3;
    static char comp[20000]; int np = 0;
    for (int i = 2; i < 20000 && np < NP; i++) if (!comp[i]) { if (i > 2) primes[np++] = i; for (int j = i * i; j < 20000; j += i) comp[j] = 1; }
    if (n > MAXN || primes[n - 1] >= MAXR || primes[n - 1] >= HR) { fprintf(stderr, "n too large (moduli must be below HR = %d: build with -DHR=128)\n", HR); return 1; }
    nmod = n;
    for (int m = 0; m < n; m++) { mod_[m] = primes[m]; for (int i = 0; i < NP; i++) { res[m][i] = primes[i] % mod_[m]; mask[m][res[m][i]][i >> 6] |= 1ull << (i & 63); } }
    best = 0; bestidx = -1;
    if (known) for (int i = 1; i < NP; i++) if (primes[i] == known) { best = primes[i - 1]; bestidx = i - 1; }
    if (split < 1) split = 1;
    if (split > n) split = n;
    { st_t *s = calloc(1, sizeof(st_t)); uint64_t st[W] = {0}; prefix_t cur = {0}; enum_prefixes(s, st, n, split, &cur); free(s); }
    long total = 0, rebuilds = 0, zcuts = 0; double t0 = omp_get_wtime();
    #pragma omp parallel for schedule(dynamic, 1) reduction(+:total, rebuilds, zcuts)
    for (int t = 0; t < npre; t++) {
        st_t *s = calloc(1, sizeof(st_t)); uint64_t st[W];
        replay(s, &pre[t], st);
        s->nfree = 0; for (int m = nmod - 1; m >= 0; m--) if (!s->used[m]) s->freem[s->nfree++] = m;
        hist_t *H = malloc(sizeof(hist_t)); H->bi = -2;
        dfs(s, st, n - pre[t].len, H);
        total += s->nodes; rebuilds += s->rebuilds; zcuts += s->zcuts; free(H); free(s);
    }
    printf("n=%d r=%d D=%d nodes=%ld (below the %d split prefixes) rebuilds=%ld zero-option cuts=%ld%s seconds=%.1f vector:", n, mod_[n - 1], best, total, npre, rebuilds, zcuts,
           known ? " (started from a known value)" : "", omp_get_wtime() - t0);
    for (int m = 0; m < n; m++) printf(" %d:%d", mod_[m], bestcls[m]);
    printf("\n");
    return 0;
}
