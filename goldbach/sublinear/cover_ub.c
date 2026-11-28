// cover_ub.c -- rigorous bounds for complete covers by one residue class per modulus (uarch, 24 Nov 2026).
// Rows: the odd primes below Y.  Moduli: the first M odd primes.  A vector: one class per modulus (class 0 allowed: it strikes r itself).
//   ./cover_ub M Y proof         does some vector strike every row?  "NO COVER" proves D(M) < Y; a cover found is printed (then D(M) >= Y).
//   ./cover_ub M Y floor j [inc] the least, over the nodes at depth j, of f = |U| - cap: every vector leaves at least that many rows unstruck.
//   ./cover_ub M Y count         at Y = D(M): the number of vectors striking every odd prime below Y (each uses every modulus: a free one could
//                                take Y's class and beat D(M); a cover reached with moduli free is reported, meaning Y is not D(M)).
// Node: U = the rows still unstruck, the free moduli, h[m][c] = |U & class (m, c)|, mx[m] = max_c h[m][c], cap = sum of mx over the free
// moduli; any vector below the node leaves >= f = |U| - cap rows unstruck.  A child that puts free modulus m in class c has
// f' >= f + mx[m] - h[m][c] (its U loses h[m][c] rows, its cap loses mx[m] at least), so f never decreases along a path, and with an
// incumbent inc (proof mode: inc = 1, a cover leaves 0 rows) a node with f >= inc is pruned and only the classes with
// h[m][c] > mx[m] - (inc - f) are tried ("qualifying").  The node branches on the free modulus with the fewest qualifying classes (the
// smallest such modulus on ties), over those classes: the children differ in that modulus's class, so every vector lies below exactly one
// node of each depth, and the floor at depth j (the least f over the depth-j nodes, pruned subtrees having f >= the final value) is a lower
// bound for every vector.  Proof mode also cuts a node with a row of U that no qualifying class of any free modulus strikes ("dead").
// FIXORDER=1 (environment): always branch on the smallest free modulus, so that floor mode's depth j means "the first j moduli fixed".
// DEADTEST=1 (compile): also cut a node with a row no qualifying class strikes (off by default: no node savings with ARGM, 21% slower).
//   gcc -O3 -march=native -fopenmp -o cover_ub cover_ub.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>
#include <immintrin.h>

#define MAXM 128
static long long ncover, nabove;                        /* count mode: covers with every modulus assigned; covers reached with moduli still free */
static int M, N, Y, mode, jdepth, fixorder;           /* mode 0: proof, 1: floor; fixorder (env FIXORDER=1): branch on the smallest free modulus */
static int rmod[MAXM], off[MAXM], len16[MAXM], HTOT;   /* modulus m's row: hist[off[m] .. off[m] + len16[m]) (classes >= r are 0) */
static int *prow;                                      /* the rows (odd primes below Y) */
static uint16_t *resT;                                 /* resT[p * MAXM + m] = prow[p] mod rmod[m] */
static uint16_t *idxT;                                 /* idxT[p * MAXM + m] = off[m] + resT[p * MAXM + m] (m < M): row p's entry in every histogram row */
#ifndef DEADTEST
#define DEADTEST 0     /* the dead-row cut (proof mode): valid, but at 89 moduli it saved < 1% of the nodes for 21% more time */
#endif
#ifndef ARGM
#define ARGM 1
#endif
static volatile int inc;                               /* incumbent: proof mode 1; floor mode the least depth-j f found */
static volatile int found; static int foundcls[MAXM];
static long long nodes_total, cut_f, cut_dead;

typedef struct { uint16_t *hist; int *U, *buf; int nu; } level_t;
typedef struct { level_t lv[MAXM + 1]; int cls[MAXM]; unsigned char freem[MAXM]; long long nodes, cf, cd, ca; } work_t;

static inline int rowmax16(const uint16_t *h, int n16) {
    __m256i v = _mm256_setzero_si256();
    for (int q = 0; q < n16; q += 16) v = _mm256_max_epu16(v, _mm256_load_si256((const __m256i *)(h + q)));
    __m128i x = _mm_max_epu16(_mm256_castsi256_si128(v), _mm256_extracti128_si256(v, 1));
    x = _mm_minpos_epu16(_mm_xor_si128(x, _mm_set1_epi16(-1)));          /* 65535 - max, minimized */
    return 65535 - (_mm_cvtsi128_si32(x) & 0xFFFF);
}
static inline int count_ge16(const uint16_t *h, int n16, int thr) {      /* classes with h >= thr (thr >= 1) */
    const __m256i t = _mm256_set1_epi16((short)thr);
    int c = 0;
    for (int q = 0; q < n16; q += 16) {
        const __m256i hh = _mm256_load_si256((const __m256i *)(h + q));
        c += __builtin_popcount((unsigned)_mm256_movemask_epi8(_mm256_cmpeq_epi16(_mm256_max_epu16(hh, t), hh)));
    }
    return c / 2;
}
static inline int argmax1_16(const uint16_t *h, int n16, int mxv) {
    if (mxv == 0) return 0xFFFF;
    const __m256i t = _mm256_set1_epi16((short)mxv);
    int cnt = 0, pos = -1;
    for (int q = 0; q < n16; q += 16) {
        const unsigned b = (unsigned)_mm256_movemask_epi8(_mm256_cmpeq_epi16(_mm256_load_si256((const __m256i *)(h + q)), t));
        if (b) { cnt += __builtin_popcount(b) / 2; if (pos < 0) pos = q + __builtin_ctz(b) / 2; }
    }
    return cnt == 1 ? pos : 0xFFFF;
}
static void build_root(level_t *L) {
    memset(L->hist, 0, sizeof(uint16_t) * HTOT);
    for (int p = 0; p < N; p++) { L->U[p] = p; for (int m = 0; m < M; m++) L->hist[off[m] + resT[(size_t)p * MAXM + m]]++; }
    L->nu = N;
}
/* the node at depth d of work w; prefix mode: stop at depth stopd and hand the node to save() */
static int stopd = -1; static void (*save)(work_t *, int);
static void dfs(work_t *w, int d) {
    if (found && mode != 2) return;
    level_t *L = &w->lv[d];
    w->nodes++;
    const int nu = L->nu;
    if (mode != 1 && nu == 0) {                                           /* every row struck: a cover */
        if (mode == 2) {                                                  /* count mode: at Y = D(n) a cover uses every modulus */
            int nf = 0; for (int m = 0; m < M; m++) nf += w->freem[m];
            #pragma omp critical
            { if (nf) nabove++; else ncover++;
              if (!found) { found = 1; for (int m = 0; m < M; m++) foundcls[m] = w->freem[m] ? -1 : w->cls[m]; } }
            return;
        }
        #pragma omp critical
        if (!found) { found = 1; for (int m = 0; m < M; m++) foundcls[m] = w->freem[m] ? -1 : w->cls[m]; }
        return;
    }
    int mx[MAXM], cap = 0, nfree = 0, fl[MAXM];
    for (int m = 0; m < M; m++) if (w->freem[m]) { fl[nfree++] = m; cap += (mx[m] = rowmax16(L->hist + off[m], len16[m])); }
    const int f = nu - cap;
    const int I = inc;
    if (f >= I) { w->cf++; return; }
    if (mode == 1 && d == jdepth) {                                       /* a depth-j node: its f is a candidate floor */
        #pragma omp critical
        if (f < inc) inc = f;
        return;
    }
    if (nfree == 0) { if (mode == 1) {
        #pragma omp critical
        if (nu < inc) inc = nu;
        } return; }
    if (d == stopd) { save(w, d); return; }
    const int slack = I - 1 - f;                                          /* >= 0: a class qualifies iff h >= mx - slack */
    int best = -1, bnq = 1 << 30, allpos = 1;
    for (int k = 0; k < nfree; k++) {
        const int m = fl[k], thr = mx[m] - slack;
        const int nq = thr <= 0 ? rmod[m] : count_ge16(L->hist + off[m], len16[m], thr);
        if (thr <= 0) allpos = 0;
        if (fixorder ? best < 0 : nq < bnq) { bnq = nq; best = m; }
    }
    if (mode == 0 && allpos && DEADTEST) {                                /* dead: a row no qualifying class strikes */
        for (int i = 0; i < nu; i++) {
            const uint16_t *rp = resT + (size_t)L->U[i] * MAXM; int ok = 0;
            for (int k = 0; k < nfree && !ok; k++) { const int m = fl[k]; ok = L->hist[off[m] + rp[m]] >= mx[m] - slack; }
            if (!ok) { w->cd++; return; }
        }
    }
    const int m = best, r = rmod[m], thr = mx[m] - slack;
    /* the children: the qualifying classes of m, fullest first; partition U by m's class */
    int cl[512], ncl = 0;
    for (int c = 0; c < r; c++) { const int h = L->hist[off[m] + c]; if (h >= thr) { int j = ncl++; while (j > 0 && L->hist[off[m] + cl[j - 1]] < h) { cl[j] = cl[j - 1]; j--; } cl[j] = c; } }
    int start[512 + 1]; memset(start, 0, sizeof(int) * (r + 1));
    for (int i = 0; i < nu; i++) start[resT[(size_t)L->U[i] * MAXM + m] + 1]++;
    for (int c = 0; c < r; c++) start[c + 1] += start[c];
    { int pos[512]; memcpy(pos, start, sizeof(int) * r); for (int i = 0; i < nu; i++) { const int p = L->U[i]; L->buf[pos[resT[(size_t)p * MAXM + m]]++] = p; } }
    w->freem[m] = 0;
    level_t *C = &w->lv[d + 1];
#if ARGM
    /* ARGM: a child (m, c) striking T lowers by >= 1 the fullest class of every other free modulus whose single fullest class T meets (its other
       classes are below it), so it leaves >= f + mx[m] - h[m][c] + (those moduli) rows: a child at or above the incumbent is not built */
    uint16_t av[MAXM] __attribute__((aligned(32)));
    for (int q = 0; q < MAXM; q++) av[q] = 0xFFFF;
    for (int k = 0; k < nfree; k++) { const int mm = fl[k]; if (mm != m) av[mm] = (uint16_t)argmax1_16(L->hist + off[mm], len16[mm], mx[mm]); }
#endif
    for (int t = 0; t < ncl && !(found && mode != 2); t++) {
        const int c = cl[t];
        if (mode == 1 && f + mx[m] - L->hist[off[m] + c] >= inc) continue;   /* the incumbent may have dropped since the list was made */
#if ARGM
        {   __m256i hit[MAXM / 16];
            for (int q = 0; q < MAXM / 16; q++) hit[q] = _mm256_setzero_si256();
            for (int i = start[c]; i < start[c + 1]; i++) {
                const uint16_t *rp = resT + (size_t)L->buf[i] * MAXM;
                for (int q = 0; q < MAXM / 16; q++)
                    hit[q] = _mm256_or_si256(hit[q], _mm256_cmpeq_epi16(_mm256_loadu_si256((const __m256i *)(rp + 16 * q)), _mm256_load_si256((const __m256i *)(av + 16 * q))));
            }
            int r1 = 0; for (int q = 0; q < MAXM / 16; q++) r1 += __builtin_popcount((unsigned)_mm256_movemask_epi8(hit[q])) / 2;
            if (f + mx[m] - L->hist[off[m] + c] + r1 >= inc) { w->ca++; continue; }
        }
#endif
        memcpy(C->hist, L->hist, sizeof(uint16_t) * HTOT);
        int nc = 0;
        for (int i = 0; i < start[c]; i++) C->U[nc++] = L->buf[i];
        for (int i = start[c + 1]; i < nu; i++) C->U[nc++] = L->buf[i];
        for (int i = start[c]; i < start[c + 1]; i++) {                    /* the rows class c strikes leave every histogram (an assigned modulus's row is not read) */
            const uint16_t *ip = idxT + (size_t)L->buf[i] * MAXM;
            for (int mm = 0; mm < M; mm++) C->hist[ip[mm]]--;
        }
        C->nu = nc;
        w->cls[m] = c;
        dfs(w, d + 1);
    }
    w->freem[m] = 1;
}
static work_t *new_work(void) {
    work_t *w = calloc(1, sizeof(work_t));
    for (int d = 0; d <= M; d++) {
        w->lv[d].hist = aligned_alloc(64, sizeof(uint16_t) * ((HTOT + 31) / 32 * 32));
        w->lv[d].U = malloc(sizeof(int) * (N + 1)); w->lv[d].buf = malloc(sizeof(int) * (N + 1));
    }
    return w;
}
/* prefixes: the nodes at depth stopd, saved with their state, then searched in parallel */
typedef struct { int d, nu, cls[MAXM]; unsigned char freem[MAXM]; uint16_t *hist; int *U; } pre_t;
static pre_t *pre; static int npre, cappre;
static void save_node(work_t *w, int d) {
    if (npre == cappre) { cappre = cappre ? 2 * cappre : 256; pre = realloc(pre, sizeof(pre_t) * cappre); }
    pre_t *P = &pre[npre++];
    P->d = d; P->nu = w->lv[d].nu; memcpy(P->cls, w->cls, sizeof P->cls); memcpy(P->freem, w->freem, sizeof P->freem);
    P->hist = aligned_alloc(64, sizeof(uint16_t) * ((HTOT + 31) / 32 * 32)); memcpy(P->hist, w->lv[d].hist, sizeof(uint16_t) * HTOT);
    P->U = malloc(sizeof(int) * (P->nu + 1)); memcpy(P->U, w->lv[d].U, sizeof(int) * P->nu);
}
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: cover_ub M Y proof | cover_ub M Y floor j [inc]\n"); return 1; }
    M = atoi(argv[1]); Y = atoi(argv[2]); mode = !strcmp(argv[3], "floor") ? 1 : !strcmp(argv[3], "count") ? 2 : 0;
    if (mode == 1) { jdepth = argc > 4 ? atoi(argv[4]) : 6; inc = argc > 5 ? atoi(argv[5]) : 1 << 30; } else inc = 1;
    fixorder = getenv("FIXORDER") && atoi(getenv("FIXORDER"));
    if (M < 1 || M > MAXM) { fprintf(stderr, "M must be 1..%d\n", MAXM); return 1; }
    char *comp = calloc(Y + 1, 1); int *pr = malloc(sizeof(int) * (Y / 2 + 2)), np = 0;
    for (long i = 2; i <= Y; i++) if (!comp[i]) { if (i > 2) pr[np++] = (int)i; for (long j = i * i; j <= Y; j += i) comp[j] = 1; }
    /* the moduli: the first M odd primes (need not be below Y) */
    { int k = 0; for (long i = 3; k < M; i += 2) { int isp = 1; for (long q = 3; q * q <= i; q += 2) if (i % q == 0) { isp = 0; break; } if (isp) rmod[k++] = (int)i; } }
    if (rmod[M - 1] > 511) { fprintf(stderr, "moduli must be below 512\n"); return 1; }
    N = 0; prow = malloc(sizeof(int) * (np + 1)); for (int i = 0; i < np; i++) if (pr[i] < Y) prow[N++] = pr[i];
    if (N > 65535) { fprintf(stderr, "too many rows for 16-bit counts\n"); return 1; }
    HTOT = 0; for (int m = 0; m < M; m++) { off[m] = HTOT; len16[m] = (rmod[m] + 15) / 16 * 16; HTOT += len16[m]; }
    resT = malloc(sizeof(uint16_t) * (size_t)N * MAXM);
    for (int p = 0; p < N; p++) for (int m = 0; m < MAXM; m++) resT[(size_t)p * MAXM + m] = m < M ? (uint16_t)(prow[p] % rmod[m]) : 0;
    idxT = malloc(sizeof(uint16_t) * (size_t)N * MAXM);
    for (int p = 0; p < N; p++) for (int m = 0; m < MAXM; m++) idxT[(size_t)p * MAXM + m] = m < M ? (uint16_t)(off[m] + resT[(size_t)p * MAXM + m]) : 0;
    if (HTOT > 65535) { fprintf(stderr, "histogram too long for 16-bit indices\n"); return 1; }
    const double t0 = omp_get_wtime();
    /* the prefixes: depth P with a few hundred nodes or more */
    work_t *w0 = new_work(); for (int m = 0; m < M; m++) w0->freem[m] = 1;
    build_root(&w0->lv[0]);
    int P = 0; save = save_node;
    for (P = 1; P <= M; P++) {
        for (int i = 0; i < npre; i++) { free(pre[i].hist); free(pre[i].U); }
        npre = 0; stopd = P; w0->nodes = w0->cf = w0->cd = w0->ca = 0; ncover = nabove = 0; dfs(w0, 0);
        if ((found && mode != 2) || npre >= 256 || (mode == 1 && P >= jdepth)) break;
    }
    long long nodes = w0->nodes, cf = w0->cf, cd = w0->cd, ca = w0->ca;
    stopd = -1;
    #pragma omp parallel
    {
        work_t *w = new_work();
        #pragma omp for schedule(dynamic, 1) reduction(+:nodes, cf, cd, ca)
        for (int t = 0; t < npre; t++) {
            if (found && mode != 2) continue;
            pre_t *Q = &pre[t];
            memcpy(w->cls, Q->cls, sizeof w->cls); memcpy(w->freem, Q->freem, sizeof w->freem);
            memcpy(w->lv[Q->d].hist, Q->hist, sizeof(uint16_t) * HTOT); memcpy(w->lv[Q->d].U, Q->U, sizeof(int) * Q->nu); w->lv[Q->d].nu = Q->nu;
            w->nodes = w->cf = w->cd = w->ca = 0;
            w->nodes--;                                                   /* the prefix node was counted when saved */
            dfs(w, Q->d);
            nodes += w->nodes; cf += w->cf; cd += w->cd; ca += w->ca;
        }
    }
    const double secs = omp_get_wtime() - t0;
    if (mode == 2) {
        printf("M=%d Y=%d COUNT: %lld vectors strike every odd prime below %d with every modulus used%s; nodes=%lld seconds=%.1f\n", M, Y, ncover, Y,
               nabove ? " AND SOME COVERS LEAVE MODULI FREE (Y is not D(M))" : "", nodes, secs);
    } else if (mode == 0) {
        if (found) {
            printf("M=%d Y=%d COVER FOUND (so D(%d) >= %d): nodes=%lld seconds=%.1f vector:", M, Y, M, Y, nodes, secs);
            for (int m = 0; m < M; m++) printf(" %d:%d", rmod[m], foundcls[m] < 0 ? 0 : foundcls[m]);
            printf("\n");
        } else printf("M=%d Y=%d NO COVER: no vector on the first %d odd primes strikes every odd prime below %d, so D(%d) < %d; nodes=%lld (cut by f: %lld, dead: %lld, children not built (ARGM): %lld; %d prefixes at depth %d) seconds=%.1f\n",
                      M, Y, M, Y, M, Y, nodes, cf, cd, ca, npre, P, secs);
    } else printf("M=%d Y=%d FLOOR depth %d%s: every vector leaves at least %d of the %d odd primes below %d unstruck; nodes=%lld (cut by f: %lld, ARGM: %lld; %d prefixes) seconds=%.1f\n",
                  M, Y, jdepth, fixorder ? " (the first j moduli)" : "", inc, N, Y, nodes, cf, ca, npre, secs);
    return 0;
}
