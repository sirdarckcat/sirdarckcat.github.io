// desert_fast5.c -- D(n), the exact search of desert_fast4.c with three cuts from one lemma, and a cheaper node (uarch, 24 Nov 2026).
// D(n) = the largest, over residue vectors on the first n odd primes, of the least odd prime struck by no class (class 0 allowed: it strikes q = r).
//
// The lemma.  At a node let U be the unstruck primes up to the incumbent (index <= bi), nu = |U|, h[m][c] the primes of U in class c of a free
// modulus m, mx[m] its fullest allowed class and cap = sum of mx (desert_fast4's cut is cap < nu).  A vector below the node that beats the
// incumbent strikes all of U with its free moduli, so sum_m h[m][c_m] >= nu, and with h[m][c_m] <= mx[m] for the others:
//     h[m][c_m] >= nu - (cap - mx[m]) = mx[m] - margin,   margin = cap - nu,
// for EVERY free modulus m.  Call the allowed classes of m with h >= mx[m] - margin its qualifying classes.  Then:
//   LOOK   a child (m, c) of the branching prime with h[m][c] < mx[m] - margin cannot hold such a vector: it is not created (its class is still
//          forbidden in the later siblings, as if it had been searched).  The parent's mx and cap are updated as the siblings' classes are
//          forbidden, so later siblings are tested against the smaller cap.  At n = 17: 72% of desert_fast4's nodes were children cut at once.
//   EOPT   a prime of U struck by no qualifying class of any free modulus cuts the node (desert_fast4 cut only on a prime struck by no allowed
//          class); the branching prime is the one struck by the fewest qualifying classes ("effective options").
//   FORCE  a free modulus with a single qualifying class is put in it (one child, nothing forbidden): no other class of it can beat the incumbent.
//   MBR    else, when some free modulus has a positive threshold, the node branches on the free modulus with the fewest qualifying classes,
//          over those classes (the children differ in its class: disjoint, nothing forbidden); otherwise on the prime with the fewest effective
//          options as before.  (MBRPOL 0: only when the modulus has fewer children than that prime, 1: also on ties, 2 (default): always.
//          Proof nodes n = 23: 36.2M, 21.7M, 5.2M; CPU 26.3, 17.4, 5.2 s.)
//   ARGM   a child (m, c) striking T = U & class(m, c) lowers by >= 1 the fullest class of every other free modulus whose single fullest class T
//          meets, so its cap is at most cap - mx[m] - (those moduli); if that is below nu - |T| the child would be cut at once and is not created
//          (one 32-byte compare per prime of T against the moduli's fullest classes).  It removes only such children: the dead, forced and
//          modulus-branching counts are unchanged.
//   MATCH  two free moduli whose single fullest classes share a prime of U strike at most mx_a + mx_b - 1 primes of U together (in those classes
//          they overlap; in any other class one is below its max).  Over a greedy matching M of such pairs the classes strike at most cap - |M|:
//          the margin drops by |M| (below 0: the node is cut), and the qualifying threshold becomes mx - margin' for an unmatched modulus,
//          mx - margin' - 1 for a matched one (its partner bounded by its max).  Proof nodes n = 22: 21.1M -> 7.1M.
//   QSKIP  at prime branching, a child whose class does not qualify at the node is not created (the node's lemma holds in each later
//          sibling's subtree, a subset of the node's).
// Every vector below a node is still met at most once (prime branching forbids the tried classes in later siblings as before; forced and
// modulus children are disjoint by the modulus's class), and none that beats the incumbent is lost: completeness, so D, the count mode and the
// proof mode keep their meaning.  Count mode holds the incumbent just below D, so "beats" = reaches D and the same lemma applies.
// Nodes of the proof runs (known = the next prime after D), desert_fast4 -> desert_fast5: n = 21: 1.19G -> 0.27M; n = 22: 5.02G -> 0.96M;
// n = 24: 18.1M (12.6 s at 2 threads).  Finding D(22) from scratch: 8.41G nodes, 964 s (desert_fast4) -> 1.4M nodes, 0.9 s (2 threads).
// Node cost: the child order reads the histograms (no popcounts) and is made only for prime branching, the fullest class reads only the
// 32-byte vectors a modulus has, the residues of a prime are one 32-byte row (resT) for the child's histogram update, and the
// zero/forced/qualifying masks are AVX2 compares.  Instructions, n = 20 proof (callgrind): 11.68G before ARGM and these two, 9.72G after.
//   gcc -O3 -march=native -fopenmp -o desert_fast5 desert_fast5.c ; OMP_NUM_THREADS=4 ./desert_fast5 n [known_value] [split_depth] [count]
// known_value: a value known to be attained; the run then proves it is the maximum or finds better.  If no vector reaches it the run says so
// ("not attained"): with known_value = the next prime after D that is the optimality proof.  "count": the number of optimal vectors (known = D(n)).
// Options (all on by default; -DX=0 turns one off for an A/B check): LOOK, ARGM, MATCH, QSKIP, EOPT, FORCE, MBR (MBRPOL), MRV, CORDER (2: by
// struck primes, as desert_fast4).
// Fix (24 Nov, 16:40Z): the modulus-branching children were listed in ord[MAXN] (32 entries); a modulus with more than 32 qualifying classes
// overflowed it into the frame's other arrays.  ord is now MAXR long, and the run prints how many modulus branchings had more than 32
// classes ("over 32 classes"): a run of the old program is the same search as the fixed one exactly when that count is 0.
// Needs AVX2.  Moduli must be below 128 (n <= 30); MAXN 32; NP 512 primes (D < 3,671).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>
#define MAXN 32
#define NP 512
#define W (NP / 64)
#define MAXR 128
#define HR 128          /* histogram row: classes 0 .. 127 (moduli below 128, n <= 30) */
static int nmod, mod_[MAXN];
static int primes[NP];
static unsigned char res[MAXN][NP];          /* res[m][i] = primes[i] mod mod_[m] */
static unsigned char resT[NP][MAXN];         /* resT[i][m] = res[m][i]: the residues of one prime, contiguous */
static int nvec[MAXN];                       /* nvec[m]: 32-byte vectors that hold the classes of modulus m */
static uint64_t mask[MAXN][MAXR][W];         /* mask[m][c]: the primes in class c of modulus m */
static volatile int best, bestidx; static int bestcls[MAXN];
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
typedef struct { int cls[MAXN]; unsigned char used[MAXN]; unsigned char forb[MAXN][HR]; long nodes, rebuilds, zcuts, nopt, nabove, skips, forced, mbr, wide; int nfree, freem[MAXN];
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
    __m256i v;
    { const __m256i hh = _mm256_load_si256((const __m256i *)h), ff = _mm256_loadu_si256((const __m256i *)f);
      v = _mm256_and_si256(hh, _mm256_cmpeq_epi8(ff, z)); }
    if (nv > 1) { { const __m256i hh = _mm256_load_si256((const __m256i *)(h + 32)), ff = _mm256_loadu_si256((const __m256i *)(f + 32));
                    v = _mm256_max_epu8(v, _mm256_and_si256(hh, _mm256_cmpeq_epi8(ff, z))); }
        if (nv > 2) { { const __m256i hh = _mm256_load_si256((const __m256i *)(h + 64)), ff = _mm256_loadu_si256((const __m256i *)(f + 64));
                        v = _mm256_max_epu8(v, _mm256_and_si256(hh, _mm256_cmpeq_epi8(ff, z))); }
            if (nv > 3) { const __m256i hh = _mm256_load_si256((const __m256i *)(h + 96)), ff = _mm256_loadu_si256((const __m256i *)(f + 96));
                          v = _mm256_max_epu8(v, _mm256_and_si256(hh, _mm256_cmpeq_epi8(ff, z))); } } }
    __m128i x = _mm_max_epu8(_mm256_castsi256_si128(v), _mm256_extracti128_si256(v, 1));
    x = _mm_max_epu8(x, _mm_srli_epi16(x, 8));                                  /* the low byte of each 16-bit lane: the max of its two bytes */
    x = _mm_minpos_epu16(_mm_andnot_si128(x, _mm_set1_epi16(0xFF)));             /* 255 - max, minimized */
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
static inline void copyrow(unsigned char *d, const unsigned char *s, int nv) {    /* explicit: a loop here becomes a memcpy call */
    _mm256_store_si256((__m256i *)d, _mm256_load_si256((const __m256i *)s));
    if (nv > 1) { _mm256_store_si256((__m256i *)(d + 32), _mm256_load_si256((const __m256i *)(s + 32)));
        if (nv > 2) { _mm256_store_si256((__m256i *)(d + 64), _mm256_load_si256((const __m256i *)(s + 64)));
            if (nv > 3) _mm256_store_si256((__m256i *)(d + 96), _mm256_load_si256((const __m256i *)(s + 96))); } }
}
static void dfs(st_t *s, const uint64_t *st, int left, hist_t *H) {
    s->nodes++;
    int i = -1;
    for (int w = 0; w < W; w++) if (~st[w]) { i = w * 64 + __builtin_ctzll(~st[w]); break; }
    if (i < 0) { fprintf(stderr, "every prime below %d struck: enlarge NP\n", primes[NP - 1]); exit(1); }
    if (left == 0) {
        int q = primes[i];
        if (count_mode) {                                               /* best stays just below the target: count the vectors reaching it */
            if (q >= target) {
                if (q == target) s->nopt++; else s->nabove++;
                if (!found) {
                    #pragma omp critical
                    if (!found) { found = 1; for (int m = 0; m < nmod; m++) bestcls[m] = s->cls[m]; }
                }
            }
            return;
        }
        if (q > best) {
            #pragma omp critical
            if (q > best) { best = q; bestidx = i; found = 1; for (int m = 0; m < nmod; m++) bestcls[m] = s->cls[m]; }
        }
        return;
    }
    const int bi = bestidx;
    const int bounded = i <= bi;
    int mx[MAXN], cap = 0, nu = 0;                                      /* mx[m]: modulus m's fullest allowed class over U; cap = their sum */
    int br = i;                                                         /* the prime this node branches on */
    uint32_t qual[MAXN][4];                                             /* QSKIP: the qualifying classes of each free modulus (bounded nodes) */
    unsigned char av[MAXN] __attribute__((aligned(32))); int have_av = 0;   /* the single fullest class of each free modulus (0xFF: none or several) */
    int have_qual = 0;
    int forced_m = -1, forced_c = -1;                                   /* or a forced modulus and its class */
    int mbr_m = -1; uint32_t mbr_qb[4] = {0};                           /* or a modulus to branch on, over its qualifying classes */
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
            int fm = -1, fc = -1, bm = -1, bnq = 99; uint32_t bqb[4] = {0};
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
                if (thr <= 0) { for (int w = 0; w < wb; w++) e[w] = u[w] & ~f[w]; qual[m][0] = qual[m][1] = qual[m][2] = qual[m][3] = ~0u; }
                else {              /* qualifying: allowed, h >= thr; disqualified: allowed, 0 < h < thr.  e = U's primes in qualifying classes */
                    uint32_t qb[4] = {0}, db[4] = {0}; int nq = 0, nd = 0;
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
                    qual[m][0] = qb[0]; qual[m][1] = qb[1]; qual[m][2] = qb[2]; qual[m][3] = qb[3];
                    if (nq == 1 && fm < 0) { fm = m; for (int q = 0; q < nvec[m]; q++) if (qb[q]) { fc = 32 * q + __builtin_ctz(qb[q]); break; } }
                    if (nq < bnq) { bnq = nq; bm = m; for (int q = 0; q < 4; q++) bqb[q] = qb[q]; }
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
                if (MBRPOL >= 2 || bnq < lv + MBRPOL) { mbr_m = bm; for (int q = 0; q < 4; q++) mbr_qb[q] = bqb[q]; }
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
    int ord[MAXR], no = 0;                                             /* MAXR: a modulus branching has up to r children (not MAXN) */
    int mcls[MAXR], nmc = 0;
    if (forced_m >= 0) { s->forced++; no = 1; ord[0] = forced_m; }
    else if (mbr_m >= 0) {
        s->mbr++;
        for (int q = 0; q < 4; q++) for (uint32_t b = mbr_qb[q]; b; b &= b - 1) {
            const int c = 32 * q + __builtin_ctz(b), v = H->h[mbr_m][c];
            int j = nmc++; while (j > 0 && H->h[mbr_m][mcls[j - 1]] < v) { mcls[j] = mcls[j - 1]; j--; } mcls[j] = c;
        }
        if (nmc > MAXN) s->wide++;                                      /* (desert_fast5 before this fix overflowed ord[MAXN] here) */
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

/* the parallel split: the first `depth` levels of the same search are enumerated serially (in the same order, with the same forbidden
   classes as the search would have at that point) into prefixes; each prefix is a task run by dfs() below it */
typedef struct { int len; int m[MAXN]; } prefix_t;
static int prefix_lim = NP - 1;                                         /* the incumbent's index when the prefixes are made (NP - 1: none) */
/* the moduli that can strike prime i at this state (unassigned, class not forbidden), in the search's child order: by how many unstruck primes up to
   prefix_lim their class strikes, most first; ties in desert_fast.c's order (largest modulus first).  Used by the enumeration and the replay alike. */
static int child_order(const st_t *s, const uint64_t *st, int i, int *ord) {
    uint64_t uu[W]; ubits(st, prefix_lim, uu);
    int sc[MAXN], no = 0;
    for (int m = nmod - 1; m >= 0; m--) {
        const int c = res[m][i];
        if (s->used[m] || s->forb[m][c]) continue;
        int v = 0; for (int w = 0; w < W; w++) v += __builtin_popcountll(uu[w] & mask[m][c][w]);
        int j = no++; while (j > 0 && sc[j - 1] < v) { sc[j] = sc[j - 1]; ord[j] = ord[j - 1]; j--; } sc[j] = v; ord[j] = m;
    }
    return no;
}
static prefix_t *pre; static int npre, cappre;
static void enum_prefixes(st_t *s, const uint64_t *st, int left, int depth, prefix_t *cur) {
    if (depth == 0 || left == 0) {
        if (npre == cappre) { cappre = cappre ? 2 * cappre : 1024; pre = realloc(pre, sizeof(prefix_t) * cappre); }
        pre[npre++] = *cur;
        return;
    }
    int i = -1;
    for (int w = 0; w < W; w++) if (~st[w]) { i = w * 64 + __builtin_ctzll(~st[w]); break; }
    int tried[MAXN], nt = 0, ord[MAXN];
    const int no = child_order(s, st, i, ord);
    for (int oi = 0; oi < no; oi++) {
        const int m = ord[oi], c = res[m][i];
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
        int ord[MAXN]; const int no = child_order(s, st, i, ord);       /* the siblings tried before this one at this level, in the enumeration's order */
        for (int oi = 0; oi < no && ord[oi] != p->m[d]; oi++) forb_inc(s, ord[oi], res[ord[oi]][i]);
        const int m = p->m[d], c = res[m][i];
        s->used[m] = 1; s->cls[m] = c;
        for (int w = 0; w < W; w++) st[w] |= mask[m][c][w];
    }
}
int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 10; int known = argc > 2 ? atoi(argv[2]) : 0; int split = argc > 3 ? atoi(argv[3]) : 3;
    count_mode = argc > 4 && !strcmp(argv[4], "count"); target = known;
    if (count_mode && !known) { fprintf(stderr, "count mode needs D as the known value\n"); return 1; }
    static char comp[20000]; int np = 0;
    for (int i = 2; i < 20000 && np < NP; i++) if (!comp[i]) { if (i > 2) primes[np++] = i; for (int j = i * i; j < 20000; j += i) comp[j] = 1; }
    if (n > MAXN || primes[n - 1] >= MAXR || primes[n - 1] >= HR) { fprintf(stderr, "n too large (moduli must be below HR = %d: build with -DHR=128)\n", HR); return 1; }
    nmod = n;
    for (int m = 0; m < n; m++) { mod_[m] = primes[m]; nvec[m] = (mod_[m] + 31) / 32;
        for (int i = 0; i < NP; i++) { res[m][i] = resT[i][m] = primes[i] % mod_[m]; mask[m][res[m][i]][i >> 6] |= 1ull << (i & 63); } }
    best = 0; bestidx = -1;
    if (known) for (int i = 1; i < NP; i++) if (primes[i] == known) { best = primes[i - 1]; bestidx = i - 1; }
    if (bestidx >= 0) prefix_lim = bestidx;
    if (split < 1) split = 1;
    if (split > n) split = n;
    { st_t *s = calloc(1, sizeof(st_t)); uint64_t st[W] = {0}; prefix_t cur = {0}; enum_prefixes(s, st, n, split, &cur); free(s); }
    long total = 0, rebuilds = 0, zcuts = 0, nopt = 0, nabove = 0, skips = 0, forced = 0, mbr = 0, wide = 0; double t0 = omp_get_wtime();
    #pragma omp parallel for schedule(dynamic, 1) reduction(+:total, rebuilds, zcuts, nopt, nabove, skips, forced, mbr, wide)
    for (int t = 0; t < npre; t++) {
        st_t *s = calloc(1, sizeof(st_t)); uint64_t st[W];
        replay(s, &pre[t], st);
        s->nfree = 0; for (int m = nmod - 1; m >= 0; m--) if (!s->used[m]) s->freem[s->nfree++] = m;
        hist_t *H = aligned_alloc(64, sizeof(hist_t)); H->bi = -2;
        dfs(s, st, n - pre[t].len, H);
        total += s->nodes; rebuilds += s->rebuilds; zcuts += s->zcuts; nopt += s->nopt; nabove += s->nabove; skips += s->skips; forced += s->forced; mbr += s->mbr; wide += s->wide; free(H); free(s);
    }
    char stats[200];
    snprintf(stats, sizeof stats, "dead=%ld skipped=%ld forced=%ld modulus-branchings=%ld (over %d classes: %ld) rebuilds=%ld", zcuts, skips, forced, mbr, MAXN, wide, rebuilds);
    const double secs = omp_get_wtime() - t0;
    if (count_mode) {
        printf("n=%d r=%d COUNT D=%d optimal vectors=%ld above D=%ld nodes=%ld (below the %d split prefixes) %s seconds=%.1f%s vector:", n, mod_[n - 1], target, nopt, nabove, total, npre,
               stats, secs, nabove ? " D IS NOT THE MAXIMUM" : "");
    } else if (!found) {
        printf("n=%d r=%d NOT ATTAINED: no vector strikes every odd prime below %d, so D(%d) < %d; nodes=%ld (below the %d split prefixes) %s seconds=%.1f\n", n, mod_[n - 1], known, n, known,
               total, npre, stats, secs);
        return 0;
    } else {
        printf("n=%d r=%d D=%d nodes=%ld (below the %d split prefixes) %s%s seconds=%.1f vector:", n, mod_[n - 1], best, total, npre, stats,
               known ? " (started from a known value)" : "", secs);
    }
    for (int m = 0; m < n; m++) printf(" %d:%d", mod_[m], bestcls[m]);
    printf("\n");
    return 0;
}
