// cover_lns.c -- a large-neighbourhood search for complete covers (uarch, 24 Nov 2026): a vector (one class per modulus) on a given set of
// moduli (complete_cover_*.txt BEST line) that strikes every odd prime below Q; it tries to raise Q.
// Step: Q = the first odd prime the vector leaves unstruck.  Free k random moduli, keep the others; U = the primes below the next prime after Q
// that no kept modulus strikes (Q among them).  desert_fast5's exact search (the same lemma cuts, MATCH, ARGM, modulus branching) looks for
// classes of the freed moduli striking all of U; a hit gives a vector striking every odd prime up to Q (and the new Q is at least the next prime).
// The freed moduli's classes are re-indexed to the classes holding a prime of U (at most 255), U has at most 255 primes; a node limit bounds a step.
//   gcc -O3 -march=native -fno-tree-loop-distribute-patterns -o cover_lns cover_lns.c
//   ./cover_lns cover.txt k node_limit seed steps [out.txt]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#define MAXN 32
#define NP 256
#define W (NP / 64)
#define MAXR 256
#define HR 256          /* local classes 0 .. 254 (255: none) */
static int nmod, mod_[MAXN];
static int primes[NP];
static unsigned char res[MAXN][NP];          /* res[m][i] = primes[i] mod mod_[m] */
static unsigned char resT[NP][MAXN];         /* resT[i][m] = res[m][i]: the residues of one prime, contiguous */
static int nvec[MAXN];                       /* nvec[m]: 32-byte vectors that hold the classes of modulus m */
static uint64_t mask[MAXN][MAXR][W];         /* mask[m][c]: the primes in class c of modulus m */
static int best, bestidx; static int bestcls[MAXN]; static long node_limit; static int done; static int randomize;
static unsigned rng_state = 1;
static inline unsigned rnd(void) { rng_state = rng_state * 1103515245u + 12345u; return rng_state >> 8; }
static int count_mode, target, found;                      /* count_mode: best fixed just below target; found: a vector was recorded */
#ifndef MRV
#define MRV 1
#endif
#ifndef EOPT
#define EOPT 1
#endif
#ifndef FORCE
#define FORCE 1
#endif
#ifndef MBR
#define MBR 1
#endif
#ifndef MBRPOL
#define MBRPOL 2        /* modulus branching: 0 when it has fewer children than the prime, 1 also on ties, 2 always (when a modulus qualifies) */
#endif
#ifndef QSKIP
#define QSKIP 1
#endif
#ifndef MATCH
#define MATCH 1
#endif
#ifndef ARGM
#define ARGM 1
#endif
#ifndef LOOK
#define LOOK 1
#endif
#ifndef CORDER
#define CORDER 2
#endif
typedef struct { int cls[MAXN]; unsigned char used[MAXN]; unsigned char forb[MAXN][HR]; long nodes, rebuilds, zcuts, nopt, nabove, skips, forced, mbr; int nfree, freem[MAXN];
                 uint64_t F[MAXN][W]; } st_t;   /* freem: the unassigned moduli, descending; F[m]: the primes in the forbidden classes of m */
static inline void forb_inc(st_t *s, int m, int c) { if (s->forb[m][c]++ == 0) for (int w = 0; w < W; w++) s->F[m][w] |= mask[m][c][w]; }
static inline void forb_dec(st_t *s, int m, int c) { if (--s->forb[m][c] == 0) for (int w = 0; w < W; w++) s->F[m][w] &= ~mask[m][c][w]; }
typedef struct { unsigned char h[MAXN][HR] __attribute__((aligned(64))); int bi, nu; } hist_t;   /* bi = -2: not built */

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
            for (int k = 0; k < s->nfree; k++) { const int m = s->freem[k]; H->h[m][resT[p][m]]++; }
        }
    }
    H->bi = bi; H->nu = nu;
}
#include <immintrin.h>
static inline int maxallowed(const unsigned char *h, const unsigned char *f, int nv) {   /* max over the classes c < 32 nv with f[c] == 0 of h[c] */
    const __m256i z = _mm256_setzero_si256();
    __m256i v = z;
    for (int q = 0; q < nv; q++) {
        const __m256i hh = _mm256_load_si256((const __m256i *)(h + 32 * q)), ff = _mm256_loadu_si256((const __m256i *)(f + 32 * q));
        v = _mm256_max_epu8(v, _mm256_and_si256(hh, _mm256_cmpeq_epi8(ff, z)));
    }
    __m128i x = _mm_max_epu8(_mm256_castsi256_si128(v), _mm256_extracti128_si256(v, 1));
    x = _mm_max_epu8(x, _mm_srli_epi16(x, 8));
    x = _mm_minpos_epu16(_mm_andnot_si128(x, _mm_set1_epi16(0xFF)));
    return 255 - (_mm_cvtsi128_si32(x) & 0xFFFF);
}
/* the class of a modulus's row holding its fullest allowed count mxv, if exactly one does (0xFF otherwise, and when mxv = 0) */
static inline int argmax1(const unsigned char *h, const unsigned char *f, int nv, int mxv) {
    if (mxv == 0) return 0xFF;
    const __m256i z = _mm256_setzero_si256(), mv = _mm256_set1_epi8((char)mxv);
    int cnt = 0, pos = -1;
    for (int q = 0; q < nv; q++) {
        const __m256i hh = _mm256_load_si256((const __m256i *)(h + 32 * q)), ff = _mm256_loadu_si256((const __m256i *)(f + 32 * q));
        const uint32_t b = (uint32_t)_mm256_movemask_epi8(_mm256_cmpeq_epi8(_mm256_and_si256(hh, _mm256_cmpeq_epi8(ff, z)), mv));
        if (b) { cnt += __builtin_popcount(b); if (pos < 0) pos = 32 * q + __builtin_ctz(b); }
    }
    return cnt == 1 ? pos : 0xFF;
}
static inline void copyrow(unsigned char *d, const unsigned char *s, int nv) {
    for (int q = 0; q < nv; q++) _mm256_store_si256((__m256i *)(d + 32 * q), _mm256_load_si256((const __m256i *)(s + 32 * q)));
}
static void dfs(st_t *s, const uint64_t *st, int left, hist_t *H) {
    if (done || s->nodes >= node_limit) return;
    s->nodes++;
    int i = -1;
    for (int w = 0; w < W; w++) if (~st[w]) { i = w * 64 + __builtin_ctzll(~st[w]); break; }
    if (i < 0 || i > bestidx) {                                         /* every prime of U struck: a cover (the sentinel is never struck) */
        done = 1; found = 1; for (int m = 0; m < nmod; m++) bestcls[m] = s->used[m] ? s->cls[m] : -1;
        return;
    }
    if (left == 0) return;
    const int bi = bestidx;
    const int bounded = i <= bi;
    int mx[MAXN], cap = 0, nu = 0;                                      /* mx[m]: modulus m's fullest allowed class over U; cap = their sum */
    int br = i;                                                         /* the prime this node branches on */
    uint32_t qual[MAXN][8];                                             /* QSKIP: the qualifying classes of each free modulus (bounded nodes) */
    unsigned char av[MAXN] __attribute__((aligned(32))); int have_av = 0;   /* the single fullest class of each free modulus (0xFF: none or several) */
    int have_qual = 0;
    int forced_m = -1, forced_c = -1;                                   /* or a forced modulus and its class */
    int mbr_m = -1; uint32_t mbr_qb[8] = {0};                           /* or a modulus to branch on, over its qualifying classes */
    if (bounded) {
        if (H->bi != bi) { build(s, st, bi, H); s->rebuilds++; }
        nu = H->nu;
        int k = 0;
        for (; k < s->nfree && cap < nu; k++) { const int m = s->freem[k]; cap += (mx[m] = maxallowed(H->h[m], s->forb[m], nvec[m])); }
        if (cap < nu) return;
#if LOOK || EOPT                                                       /* both need every mx[m] and the whole cap */
        for (; k < s->nfree; k++) { const int m = s->freem[k]; cap += (mx[m] = maxallowed(H->h[m], s->forb[m], nvec[m])); }
#endif
        {   /* options of the primes of U (unassigned moduli whose class for them is allowed), bit-sliced and saturating at 4:
               a prime with none can never be struck (cut); the branching prime is one with the fewest (the smallest among them) */
            uint64_t u[W]; ubits(st, bi, u); const int wb = (bi >> 6) + 1;   /* words holding U */
            uint64_t c0[W] = {0}, c1[W] = {0}, c2[W] = {0}, cov[W] = {0}, eS[MAXN][W];
#if EOPT
            /* every vector below this node that beats the incumbent covers U, so its classes strike >= nu primes of U in all; a free modulus m
               in class c strikes h[m][c] and each other one at most its fullest allowed class, so h[m][c] >= nu - (cap - mx[m]) = mx[m] - margin:
               in such a vector every free modulus is in one of its "qualifying" classes.  A prime of U struck by no qualifying class cuts the
               node; one free modulus with a single qualifying class is forced into it. */
            int margin = cap - nu;
            int fm = -1, fc = -1, bm = -1, bnq = 99; uint32_t bqb[8] = {0};
            unsigned char mt[MAXN] = {0};                                   /* MATCH: m is in a matched pair (its threshold is 1 lower) */
#if MATCH
            /* two free moduli whose single fullest classes share a prime of U strike together at most mx_a + mx_b - 1 primes of U (in their
               fullest classes they overlap; in any other class one of them is below its max).  Over a set of disjoint such pairs (a greedy
               matching) the union of all the classes is at most cap - |M|: margin -|M| (< 0 cuts); a matched modulus's qualifying threshold is
               mx - margin' - 1 (its partner bounded by its max), an unmatched one's mx - margin'. */
            {   int L[MAXN], nl = 0; unsigned char am[MAXN];
                memset(av, 0xFF, sizeof av); have_av = 1;
                for (int k = 0; k < s->nfree; k++) { const int m = s->freem[k]; const int a = argmax1(H->h[m], s->forb[m], nvec[m], mx[m]); av[m] = (unsigned char)a; if (a != 0xFF) { L[nl] = m; am[nl] = (unsigned char)a; nl++; } }
                int nmt = 0;
                for (int i = 0; i < nl; i++) {
                    if (mt[L[i]]) continue;
                    const uint64_t *mi = mask[L[i]][am[i]];
                    for (int j = i + 1; j < nl; j++) {
                        if (mt[L[j]]) continue;
                        const uint64_t *mj = mask[L[j]][am[j]];
                        uint64_t o = 0; for (int w = 0; w < wb; w++) o |= u[w] & mi[w] & mj[w];
                        if (o) { mt[L[i]] = mt[L[j]] = 1; nmt++; break; }
                    }
                }
                margin -= nmt;
                if (margin < 0) { s->zcuts++; return; }
            }
#endif
#endif
            for (int k = 0; k < s->nfree; k++) {
                const int m = s->freem[k];
                const uint64_t *f = s->F[m];
                uint64_t e[W];                                                 /* the primes of U this modulus can still strike (EOPT: in a qualifying class) */
#if !EOPT
                for (int w = 0; w < wb; w++) e[w] = u[w] & ~f[w];
#else
                const int thr = mx[m] - margin - mt[m];
                if (thr <= 0) { for (int w = 0; w < wb; w++) e[w] = u[w] & ~f[w]; for (int q = 0; q < 8; q++) qual[m][q] = ~0u; }
                else {              /* qualifying: allowed, h >= thr; disqualified: allowed, 0 < h < thr.  e = U's primes in qualifying classes */
                    uint32_t qb[8] = {0}, db[8] = {0}; int nq = 0, nd = 0;
                    const __m256i z = _mm256_setzero_si256(), tv = _mm256_set1_epi8((char)thr);
                    for (int q = 0; q < nvec[m]; q++) {
                        const __m256i hh = _mm256_load_si256((const __m256i *)(H->h[m] + 32 * q)), ff = _mm256_loadu_si256((const __m256i *)(s->forb[m] + 32 * q));
                        const __m256i al = _mm256_cmpeq_epi8(ff, z), ge = _mm256_cmpeq_epi8(_mm256_max_epu8(hh, tv), hh), zr = _mm256_cmpeq_epi8(hh, z);
                        qb[q] = (uint32_t)_mm256_movemask_epi8(_mm256_and_si256(al, ge));
                        db[q] = (uint32_t)_mm256_movemask_epi8(_mm256_andnot_si256(_mm256_or_si256(ge, zr), al));
                        nq += __builtin_popcount(qb[q]); nd += __builtin_popcount(db[q]);
                    }
                    if (nq <= nd) {
                        uint64_t o[W] = {0};
                        for (int q = 0; q < nvec[m]; q++) for (uint32_t b = qb[q]; b; b &= b - 1) { const uint64_t *mk = mask[m][32 * q + __builtin_ctz(b)]; for (int w = 0; w < wb; w++) o[w] |= mk[w]; }
                        for (int w = 0; w < wb; w++) e[w] = u[w] & o[w];
                    } else {
                        for (int w = 0; w < wb; w++) e[w] = u[w] & ~f[w];
                        for (int q = 0; q < nvec[m]; q++) for (uint32_t b = db[q]; b; b &= b - 1) { const uint64_t *mk = mask[m][32 * q + __builtin_ctz(b)]; for (int w = 0; w < wb; w++) e[w] &= ~mk[w]; }
                    }
                    for (int q = 0; q < 8; q++) qual[m][q] = qb[q];
                    if (nq == 1 && fm < 0) { fm = m; for (int q = 0; q < nvec[m]; q++) if (qb[q]) { fc = 32 * q + __builtin_ctz(qb[q]); break; } }
                    if (nq < bnq) { bnq = nq; bm = m; for (int q = 0; q < 8; q++) bqb[q] = qb[q]; }
                }
#endif
                for (int w = 0; w < wb; w++) { cov[w] |= e[w]; eS[k][w] = e[w]; }
            }
            have_qual = EOPT;
            uint64_t z = 0; for (int w = 0; w < wb; w++) z |= u[w] & ~cov[w];
            if (z) { s->zcuts++; return; }
#if EOPT
            if (!(fm >= 0) && !(MBR && MBRPOL >= 2 && bm >= 0))                /* the counts: for the branching prime (MRV) and lv */
#endif
                for (int k = 0; k < s->nfree; k++)
                    for (int w = 0; w < wb; w++) { const uint64_t a = eS[k][w], t0 = c0[w] & a, t1 = c1[w] & t0; c0[w] ^= a; c1[w] ^= t0; c2[w] |= t1; }
#if FORCE && EOPT
            if (fm >= 0) { forced_m = fm; forced_c = fc; }
#endif
#if MBR && EOPT
            if (forced_m < 0 && bm >= 0) {   /* the prime's effective options: 1..3 at the MRV level found, else >= 4 */
                int lv = 4;
                for (int w = 0; w < wb; w++) {
                    const uint64_t ua = u[w] & ~c2[w];
                    if (ua & c0[w] & ~c1[w]) { lv = 1; break; }
                    if (ua & ~c0[w] & c1[w]) lv = lv < 2 ? lv : 2;
                    else if (ua & c0[w] & c1[w]) lv = lv < 3 ? lv : 3;
                }
                if (MBRPOL >= 2 || bnq < lv + MBRPOL) { mbr_m = bm; for (int q = 0; q < 8; q++) mbr_qb[q] = bqb[q]; }
            }
#endif
#if MRV
            int pick = -1;
            for (int lvl = 1; lvl <= 3 && pick < 0; lvl++)
                for (int w = 0; w < wb && pick < 0; w++) {
                    const uint64_t x = u[w] & ~c2[w] & ((lvl & 1) ? c0[w] : ~c0[w]) & ((lvl & 2) ? c1[w] : ~c1[w]);
                    if (x) pick = w * 64 + __builtin_ctzll(x);
                }
            if (pick >= 0) br = pick;
#endif
        }
    }
    hist_t C;
    int tried[MAXN], nt = 0;
    int ord[MAXR], no = 0;
    int mcls[MAXR], nmc = 0;
    if (forced_m >= 0) { s->forced++; no = 1; ord[0] = forced_m; }
    else if (mbr_m >= 0) {
        s->mbr++;
        for (int q = 0; q < 8; q++) for (uint32_t b = mbr_qb[q]; b; b &= b - 1) {
            const int c = 32 * q + __builtin_ctz(b), v = H->h[mbr_m][c];
            int j = nmc++; while (j > 0 && H->h[mbr_m][mcls[j - 1]] < v) { mcls[j] = mcls[j - 1]; j--; } mcls[j] = c;
        }
        if (randomize) for (int j = nmc - 1; j > 0; j--) { const int t = rnd() % (j + 1), x = mcls[j]; mcls[j] = mcls[t]; mcls[t] = x; }
        no = nmc; for (int j = 0; j < nmc; j++) ord[j] = mbr_m;
    } else {                                                            /* prime branching: the moduli striking br, in the child order */
#if CORDER == 1
    for (int m = 0; m < nmod; m++) ord[no++] = m;
#elif CORDER == 2
    {   int sc[MAXN]; uint64_t uu[W]; if (!bounded) ubits(st, NP - 1, uu);
        for (int m = nmod - 1; m >= 0; m--) { if (s->used[m]) continue; int c = res[m][br], v = 0; if (s->forb[m][c]) continue;
            if (bounded) v = H->h[m][c]; else for (int w = 0; w < W; w++) v += __builtin_popcountll(uu[w] & mask[m][c][w]);
            int j = no++; while (j > 0 && sc[j - 1] < v) { sc[j] = sc[j - 1]; ord[j] = ord[j - 1]; j--; } sc[j] = v; ord[j] = m; } }
#else
    for (int m = nmod - 1; m >= 0; m--) ord[no++] = m;
#endif
    if (randomize) for (int j = no - 1; j > 0; j--) { const int t = rnd() % (j + 1), x = ord[j]; ord[j] = ord[t]; ord[t] = x; }
    }
#if ARGM && LOOK
    /* ARGM: av[m] = the single class holding m's fullest allowed count (0xFF: none or several).  A child (m, c) striking T = U & class (m, c)
       lowers by >= 1 the fullest class of every other free modulus whose single fullest class T meets (its other classes are below it), so the
       child's cap is at most cap - mx[m] - (those moduli): when that is below nu - |T| the child would be cut at once. */
    uint64_t uB[W];
    if (bounded) {
        if (!have_av) { memset(av, 0xFF, sizeof av); for (int k = 0; k < s->nfree; k++) { const int m = s->freem[k]; av[m] = (unsigned char)argmax1(H->h[m], s->forb[m], nvec[m], mx[m]); } }
        ubits(st, bi, uB);
    }
#endif
    for (int oi = 0; oi < no; oi++) {
        const int m = ord[oi];
        if (s->used[m]) continue;
        int c = forced_m >= 0 ? forced_c : mbr_m >= 0 ? mcls[oi] : res[m][br];
        if (s->forb[m][c]) continue;
#if LOOK
        /* the child's cut, bounded from the parent's histograms: the child's cap is at most the other free moduli's fullest allowed classes in the
           parent's rows (the child's rows are these minus the primes m's class strikes, and its forbidden classes include these), and it needs
           nu minus the primes of U this class strikes, H->h[m][c].  A child that fails it would be cut at once: skip it, but forbid its class in
           the later siblings as if it had been searched (its subtree holds no vector beating the incumbent). */
        int cut = bounded && cap - mx[m] + H->h[m][c] < nu;
#if QSKIP
        /* the node's lemma holds in every later sibling's subtree too (a subset of this node's): a class that did not qualify here never will */
        if (!cut && have_qual && !((qual[m][c >> 5] >> (c & 31)) & 1)) cut = 1;
#endif
#if ARGM
        if (bounded && !cut && left > 1) {
            const __m256i avv = _mm256_load_si256((const __m256i *)av);
            __m256i hit = _mm256_setzero_si256();
            for (int w = 0; w <= (bi >> 6); w++) {
                uint64_t x = uB[w] & mask[m][c][w];
                while (x) { const int p = w * 64 + __builtin_ctzll(x); x &= x - 1;
                            hit = _mm256_or_si256(hit, _mm256_cmpeq_epi8(_mm256_loadu_si256((const __m256i *)resT[p]), avv)); }
            }
            const int r1 = __builtin_popcount((uint32_t)_mm256_movemask_epi8(hit) & ~(1u << m));
            cut = cap - mx[m] - r1 < nu - H->h[m][c];
        }
#endif
        if (cut) {
            s->skips++;
            if (forced_m >= 0 || mbr_m >= 0) continue;                  /* a forced or modulus child: nothing to forbid */
            forb_inc(s, m, c); tried[nt++] = m;
            const int nm = maxallowed(H->h[m], s->forb[m], nvec[m]); cap += nm - mx[m]; mx[m] = nm;
#if ARGM
            av[m] = (unsigned char)argmax1(H->h[m], s->forb[m], nvec[m], nm);
#endif
            continue;
        }
#endif
        uint64_t nx[W]; for (int w = 0; w < W; w++) nx[w] = st[w] | mask[m][c][w];
        s->used[m] = 1; s->cls[m] = c;
        int pos = 0; while (s->freem[pos] != m) pos++;                 /* take m out of the list (order kept) */
        for (int k = pos; k < s->nfree - 1; k++) s->freem[k] = s->freem[k + 1];
        s->nfree--;
        if (bounded && left > 1) {                                     /* the child's histograms: the parent's minus the primes of U this class strikes */
            uint64_t u[W]; ubits(st, bi, u);
            for (int k = 0; k < s->nfree; k++) { const int mm = s->freem[k]; copyrow(C.h[mm], H->h[mm], nvec[mm]); }
            int struck = 0;
            for (int w = 0; w < W; w++) {
                uint64_t x = u[w] & mask[m][c][w];
                while (x) {
                    const int p = w * 64 + __builtin_ctzll(x); x &= x - 1; struck++;
                    const unsigned char *rp = resT[p]; for (int k = 0; k < s->nfree; k++) { const int mm = s->freem[k]; C.h[mm][rp[mm]]--; }
                }
            }
            C.bi = bi; C.nu = H->nu - struck;
        } else C.bi = -2;
        dfs(s, nx, left - 1, &C);
        for (int k = s->nfree; k > pos; k--) s->freem[k] = s->freem[k - 1];    /* put m back at its place */
        s->freem[pos] = m; s->nfree++;
        s->used[m] = 0;
        if (forced_m >= 0) break;
        if (mbr_m >= 0) continue;                                       /* modulus branching: the children differ in m's class, nothing to forbid */
        forb_inc(s, m, c); tried[nt++] = m;
#if LOOK
        if (bounded) { const int nm = maxallowed(H->h[m], s->forb[m], nvec[m]); cap += nm - mx[m]; mx[m] = nm;
#if ARGM
                       av[m] = (unsigned char)argmax1(H->h[m], s->forb[m], nvec[m], nm);
#endif
        }
#endif
    }
    for (int j = 0; j < nt; j++) forb_dec(s, tried[j], res[tried[j]][br]);
}


/* ---- the cover and the step ---- */
static int NM, MODS[160], CLS[160];                                     /* the full cover: moduli (ascending) and their classes */
static int PR[5000], NPR;                                               /* odd primes below 45,000 */
static int clsval[MAXN][256];                                           /* local class -> residue, per freed modulus */
static int first_uncovered(void) {
    for (int t = 0; t < NPR; t++) { const int p = PR[t]; int hit = 0; for (int m = 0; m < NM && !hit; m++) hit = p % MODS[m] == CLS[m]; if (!hit) return p; }
    return -1;
}
/* the step's instance: the freed moduli fs[0..k-1] (indices into MODS, ascending), U = the primes below X no kept modulus strikes; -1 if |U| > 255 */
static int build_instance(const int *fs, int k, int X) {
    static unsigned char isfree[160]; memset(isfree, 0, sizeof isfree); for (int j = 0; j < k; j++) isfree[fs[j]] = 1;
    int NU = 0;
    for (int t = 0; t < NPR && PR[t] < X; t++) {
        const int p = PR[t]; int hit = 0;
        for (int m = 0; m < NM && !hit; m++) if (!isfree[m]) hit = p % MODS[m] == CLS[m];
        if (!hit) { if (NU == NP - 1) return -1; primes[NU++] = p; }
    }
    nmod = k;
    for (int j = 0; j < k; j++) {
        const int r = MODS[fs[j]]; mod_[j] = r;
        int loc[512]; for (int c = 0; c < r; c++) loc[c] = -1;
        int L = 0;
        for (int i = 0; i < NU; i++) { const int c = primes[i] % r; if (loc[c] < 0) { loc[c] = L; clsval[j][L] = c; L++; } res[j][i] = resT[i][j] = (unsigned char)loc[c]; }
        for (int i = NU; i < NP; i++) res[j][i] = resT[i][j] = 255;     /* the sentinel and beyond: in no class */
        nvec[j] = L ? (L + 31) / 32 : 1;
        for (int c = 0; c < HR; c++) for (int w = 0; w < W; w++) mask[j][c][w] = 0;
        for (int i = 0; i < NU; i++) mask[j][res[j][i]][i >> 6] |= 1ull << (i & 63);
    }
    for (int j = k; j < MAXN; j++) for (int i = 0; i < NP; i++) resT[i][j] = 0;   /* not 0xFF: ARGM's "no single fullest class" */
    primes[NU] = X;
    bestidx = NU - 1; best = NU ? primes[NU - 1] : 0;
    return NU;
}
int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: cover_lns cover.txt k node_limit seed steps [out.txt]\n"); return 1; }
    const int k = atoi(argv[2]); node_limit = atol(argv[3]); const unsigned seed = (unsigned)atoi(argv[4]); const long steps = atol(argv[5]);
    const char *out = argc > 6 ? argv[6] : NULL;
    if (k < 1 || k > MAXN) { fprintf(stderr, "k must be 1..%d\n", MAXN); return 1; }
    FILE *f = fopen(argv[1], "r"); if (!f) { perror(argv[1]); return 1; }
    char line[20000]; int got = 0;
    while (fgets(line, sizeof line, f)) if (!strncmp(line, "BEST", 4) || !strncmp(line, "COVER", 5)) { got = 1; break; }
    fclose(f); if (!got) { fprintf(stderr, "no BEST/COVER line\n"); return 1; }
    char *p = line; while (*p && *p != ' ') p++;
    if (!strncmp(line, "COVER", 5)) { while (*p == ' ') p++; while (*p && *p != ' ') p++; }     /* COVER k r:a ... */
    NM = 0; int r, a, nchar;
    while (sscanf(p, " %d:%d%n", &r, &a, &nchar) == 2) { MODS[NM] = r; CLS[NM] = a; NM++; p += nchar; }
    static char comp[45001]; NPR = 0;
    for (int i = 2; i <= 45000; i++) if (!comp[i]) { if (i > 2) PR[NPR++] = i; for (long j = (long)i * i; j <= 45000; j += i) comp[j] = 1; }
    for (int m = 0; m < NM; m++) if (MODS[m] > 511 || CLS[m] < 0 || CLS[m] >= MODS[m]) { fprintf(stderr, "bad modulus %d:%d\n", MODS[m], CLS[m]); return 1; }
    int Q = first_uncovered();
    printf("start: %d moduli up to %d, every odd prime below %d struck; k = %d, node limit %ld, seed %u\n", NM, MODS[NM - 1], Q, k, node_limit, seed); fflush(stdout);
    srand(seed);
    long tot = 0, big = 0, hits = 0, capped = 0; const time_t t0 = time(NULL);
    for (long step = 0; step < steps; step++) {
#ifdef SANITY
        int X = Q;                                                      /* sanity: the cover's own classes are a solution */
        const int side = 0; randomize = getenv("SIDE") != NULL; rng_state = (unsigned)step * 2654435761u + seed;   /* SIDE: also randomized */
#else
        int X = Q + 2; while (comp[X]) X += 2;                          /* the next prime after Q: strike every odd prime up to Q */
        const int side = getenv("SIDE") && (step & 1);                  /* SIDE: odd steps move sideways (target Q, random order) */
        if (side) X = Q;
        randomize = side; rng_state = (unsigned)step * 2654435761u + seed;
#endif
        int fs[MAXN], nf = 0; static unsigned char pick[160]; memset(pick, 0, sizeof pick);
        static int pool[160], npool = 0, pool_Q = -1;
        if (pool_Q != Q) {                                              /* rank the moduli by the primes below X only they strike */
            static int uniq[160]; memset(uniq, 0, sizeof uniq);
            for (int t = 0; t < NPR && PR[t] < X; t++) { int who = -1, c = 0; for (int m = 0; m < NM; m++) if (PR[t] % MODS[m] == CLS[m]) { who = m; c++; } if (c == 1) uniq[who]++; }
            for (int m = 0; m < NM; m++) pool[m] = m;
            for (int a = 1; a < NM; a++) { const int v = pool[a]; int b = a; while (b > 0 && uniq[pool[b - 1]] > uniq[v]) { pool[b] = pool[b - 1]; b--; } pool[b] = v; }
            const char *e = getenv("POOL"); npool = e ? atoi(e) : NM; if (npool < k) npool = k; if (npool > NM) npool = NM;
            pool_Q = Q;
        }
        while (nf < k) { const int m = pool[rand() % npool]; if (!pick[m]) { pick[m] = 1; nf++; } }
        nf = 0; for (int m = 0; m < NM; m++) if (pick[m]) fs[nf++] = m;
        const int NU = build_instance(fs, k, X);
        if (NU < 0) { big++; continue; }
        st_t *s = calloc(1, sizeof(st_t));
        for (int j = k - 1; j >= 0; j--) s->freem[s->nfree++] = j;
        hist_t *H = aligned_alloc(64, sizeof(hist_t)); H->bi = -2;
        uint64_t st[W] = {0};
        done = 0; found = 0;
        dfs(s, st, k, H);
        tot += s->nodes; if (s->nodes >= node_limit) capped++;
#ifdef SANITY
        if (found) {   /* check the solution strikes all of U, count it, change nothing */
            int ok = 1;
            for (int i = 0; i < NU && ok; i++) { int hit = 0; for (int j = 0; j < k && !hit; j++) hit = bestcls[j] >= 0 && primes[i] % mod_[j] == clsval[j][bestcls[j]]; ok = hit; }
            if (!ok) { fprintf(stderr, "BUG: step %ld: the solution misses a prime of U\n", step); return 2; }
            hits++;
        }
        free(H); free(s);
        continue;
#endif
        if (found) {
            for (int j = 0; j < k; j++) if (bestcls[j] >= 0) CLS[fs[j]] = clsval[j][bestcls[j]];
            const int Q2 = first_uncovered();
            if (side) { if (Q2 < Q) { fprintf(stderr, "BUG: sideways step %ld lost Q (%d < %d)\n", step, Q2, Q); return 2; } if (Q2 == Q) { free(H); free(s); continue; } }
            if (Q2 <= Q) { fprintf(stderr, "BUG: step %ld gave Q %d after %d\n", step, Q2, Q); return 2; }
            hits++;
            printf("step %ld: |U| = %d, %ld nodes: every odd prime below %d struck (was %d)  [%ld steps, %ld capped, %ld too big, %ld nodes, %lds]\n",
                   step, NU, s->nodes, Q2, Q, step + 1, capped, big, tot, (long)(time(NULL) - t0));
            Q = Q2;
            if (out) { FILE *g = fopen(out, "w"); fprintf(g, "BEST"); for (int m = 0; m < NM; m++) fprintf(g, " %d:%d", MODS[m], CLS[m]); fprintf(g, "\n"); fclose(g); }
            fflush(stdout);
        }
        free(H); free(s);
    }
    printf("end: every odd prime below %d struck; %ld steps, %ld improvements, %ld capped, %ld too big, %ld nodes, %lds\nBEST", Q, steps, hits, capped, big, tot, (long)(time(NULL) - t0));
    for (int m = 0; m < NM; m++) printf(" %d:%d", MODS[m], CLS[m]);
    printf("\n");
    return 0;
}
