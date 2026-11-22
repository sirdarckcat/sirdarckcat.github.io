/* fscan.c -- "score first" scanner for Goldbach deserts: small N with g(N) >= Q.
 *
 * Same search space as tscan/vscan (progressions N = N0 + k*M, M = 2*3*5*...*43, one progression per
 * residue vector on the 13 cover primes), different allocation of the work:
 *
 *   1. SCORE every member with one byte add per small prime s (the primes after 43 up to L): the
 *      number of residual rows q with s | N - q depends only on k mod s, so it is a periodic byte
 *      table, added 64 members at a time.  About half a cycle per member.
 *   2. For the few members whose score reaches the threshold, compute the EXACT set of rows that
 *      no prime <= L kills (one 256-bit mask per prime), and keep those with at most Ta rows left.
 *   3. FERMAT-test the rows of those members, 24 numbers at a time (fermat52.h, AVX-512 IFMA),
 *      one row per member per round, dropping a member at its first probable prime.
 *
 * tscan sieves every member to 131072 (about 400 cycles) and then tests the best 1.3%.  Here a
 * member costs a few cycles and only the best 0.1 to 0.3% are tested; the share of each
 * progression's successes that is reached is small (a few percent), which is made up for by taking
 * many more progressions.  The residue vectors are enumerated on the fly (as enumv.c / variants.py).
 *
 * A member is reported only when every row left by the primes <= L failed the base-2 Fermat test,
 * i.e. is proved composite; the other rows are divisible by a prime <= L.  check.py re-derives g(N).
 *
 *   gcc -O3 -march=native -fopenmp -o fscan fscan.c -lm
 *   ./fscan Q L Rlo Rhi Xmin Xmax theta Ta [key=value ...]
 *       Q          threshold (rows are the odd primes below Q)
 *       L          score primes are the primes in (43, L]
 *       Rlo Rhi    scan the vectors with Rlo <= residual size <= Rhi
 *       Xmin Xmax  members with Xmin < N <= Xmax (decimal or 1e23 style)
 *       theta      score threshold for residual size rref; a vector of size R uses theta + R - rref
 *       Ta         keep members with at most Ta rows left after the primes <= L
 *     keys: rref=R (default Rlo)   slice=i/n (every n-th work unit)   done=FILE (resume/progress log)
 *           sample=S (exact stage on every 2^S-th member for the mass estimate, default 12)
 *           dump=1 (print the vectors, no scan)   one=N0 (scan only the vector with this N0)
 *           hist=1 (print the score and a histograms)   threads=T   c2=X (pair term, see README)
 * Output: "S <N> <k> <N0> <R>" per success, then one "STATS" line; the done file gets one "W ..." line per finished unit.
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
#include "fermat52.h"

typedef uint64_t u64;
typedef uint16_t u16;
typedef uint8_t u8;

#define NW 24                         /* words of the alive bitset over the rows (odd primes < Q) */
#define NR 13
#define MAXS 256                      /* score primes */
#define CK 512                        /* members per chunk (8 zmm of byte scores) */
#define MAXROWS 256
static const int RS[NR] = {3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43};

static int Q, L, Rlo, Rhi, rref, theta0, Ta, nq, ns, sample_bits = 12, do_dump, do_hist;
static double c2 = -2.39e-4;        /* pair term per pair of rows left, see README (value for Q = 10007, L = 383) */
static int qs[64 * NW];
static u64 cls[NR][44][NW];
static u64 Mmod, Ebasis[NR];
static u128 Xmin, Xmax;
static int SP[MAXS], coff[MAXS], moff[MAXS], ckm[MAXS];
static u16 *qM[MAXS];                 /* qM[p][x] = qs[x] * M^-1 mod s */
static u64 minv[MAXS];
static double prodL;                  /* prod over primes r <= L of (1 - 1/r) */
static int ctot, mtot;
static u64 one_n0;
static int have_one, slice_i, slice_n = 1;

typedef struct {
    u64 vectors, members, sel, kept, tests, prps, found, samples;
    double exp_tested, exp_corr, mass_all, mass_cap;
} stats_t;

typedef struct { u128 N; u64 m[4]; u64 k; } member_t;

typedef struct {
    u8 *cbuf;                         /* score tables: per prime s + CK bytes, periodic */
    u64 *mbuf;                        /* row masks: per prime s entries of 4 words */
    int rows[MAXROWS], nrows;
    u64 rowmask[4];                   /* bits 0..nrows-1 */
    int rowq[MAXROWS];                /* the prime of each row */
    u64 n0;
    member_t *queue; int qn, qcap;
    member_t slot[F52_LANES]; int act[F52_LANES];
    stats_t st;
    u64 hs[256], ha[257];
} tls_t;

static u128 parse_big(const char *s) {
    if (strchr(s, 'e') || strchr(s, 'E')) { long double v = strtold(s, NULL); return (u128)v; }
    u128 v = 0; for (; *s >= '0' && *s <= '9'; s++) v = v * 10 + (*s - '0'); return v;
}
static void print_big(FILE *f, u128 v) {
    char b[48]; int i = 47; b[i] = 0;
    if (!v) b[--i] = '0';
    while (v) { b[--i] = '0' + (int)(v % 10); v /= 10; }
    fputs(b + i, f);
}
static u64 invmod(u64 a, u64 m) {     /* a^-1 mod m, m prime */
    u64 r = 1, e = m - 2, b = a % m;
    while (e) { if (e & 1) r = (u128)r * b % m; b = (u128)b * b % m; e >>= 1; }
    return r;
}
static inline int pcw(const u64 *a, const u64 *b) {
    int c = 0;
    for (int i = 0; i < NW; i++) c += __builtin_popcountll(a[i] & b[i]);
    return c;
}
static inline double eps_at(double lnN) { return 1.0 / (lnN * prodL); }

/* ---------------------------------------------------------------- Fermat stage */

static void success(tls_t *T, const member_t *m) {
    #pragma omp critical(out)
    {
        printf("S "); print_big(stdout, m->N); printf(" %llu %llu %d\n", (unsigned long long)m->k, (unsigned long long)T->n0, T->nrows);
        fflush(stdout);
    }
    T->st.found++;
}

/* run rounds until fewer than `need` members are active and the queue is empty */
static void fermat_drain(tls_t *T, int need) {
    for (;;) {
        int nact = 0;
        for (int i = 0; i < F52_LANES; i++) {
            if (!T->act[i] && T->qn) { T->slot[i] = T->queue[--T->qn]; T->act[i] = 1; }
            nact += T->act[i];
        }
        if (nact < need || nact == 0) return;
        u128 n[F52_LANES], mx = 0; int row[F52_LANES], first = -1;
        for (int i = 0; i < F52_LANES; i++) {
            if (!T->act[i]) continue;
            member_t *m = &T->slot[i];
            int w = 0; while (!m->m[w]) w++;
            row[i] = 64 * w + __builtin_ctzll(m->m[w]);
            n[i] = m->N - (u128)T->rowq[row[i]];
            if (n[i] > mx) mx = n[i];
            if (first < 0) first = i;
        }
        int b = 0; for (u128 x = mx; x; x >>= 1) b++;
        int t = b - 6;
        f52_lanes LL[3];
        for (int i = 0; i < F52_LANES; i++) {
            if (!T->act[i]) n[i] = n[first];
            f52_setup(&LL[i >> 3], i & 7, n[i], t);
        }
        unsigned res = f52_run(LL, n, F52_LANES, t);
        for (int i = 0; i < F52_LANES; i++) {
            if (!T->act[i]) continue;
            member_t *m = &T->slot[i];
            T->st.tests++;
            if ((res >> i) & 1) { T->st.prps++; T->act[i] = 0; continue; }
            m->m[row[i] >> 6] &= ~(1ull << (row[i] & 63));
            if (!(m->m[0] | m->m[1] | m->m[2] | m->m[3])) { success(T, m); T->act[i] = 0; }
        }
    }
}

/* ---------------------------------------------------------------- one vector */

static inline int exact_stage(tls_t *T, const u16 *phi, int d, u64 *mask) {
    u16 c[MAXS + 32] __attribute__((aligned(64)));
    extern u16 SPv[MAXS + 32], RECv[MAXS + 32];
    const __m512i dv = _mm512_set1_epi16((short)d);
    for (int p = 0; p < ns; p += 32) {
        __m512i x = _mm512_add_epi16(_mm512_loadu_si512(phi + p), dv);
        __m512i s = _mm512_load_si512(SPv + p);
        __m512i q = _mm512_mulhi_epu16(x, _mm512_load_si512(RECv + p));
        x = _mm512_sub_epi16(x, _mm512_mullo_epi16(q, s));
        x = _mm512_min_epu16(x, _mm512_sub_epi16(x, s));
        _mm512_store_si512(c + p, x);
    }
    const u64 *mb = T->mbuf;
    __m256i a0 = _mm256_loadu_si256((const __m256i *)T->rowmask), a1 = _mm256_set1_epi64x(-1), a2 = a1, a3 = a1;
    int p = 0;
    for (; p + 4 <= ns; p += 4) {
        a0 = _mm256_andnot_si256(_mm256_loadu_si256((const __m256i *)(mb + moff[p] + 4 * c[p])), a0);
        a1 = _mm256_andnot_si256(_mm256_loadu_si256((const __m256i *)(mb + moff[p + 1] + 4 * c[p + 1])), a1);
        a2 = _mm256_andnot_si256(_mm256_loadu_si256((const __m256i *)(mb + moff[p + 2] + 4 * c[p + 2])), a2);
        a3 = _mm256_andnot_si256(_mm256_loadu_si256((const __m256i *)(mb + moff[p + 3] + 4 * c[p + 3])), a3);
    }
    for (; p < ns; p++) a0 = _mm256_andnot_si256(_mm256_loadu_si256((const __m256i *)(mb + moff[p] + 4 * c[p])), a0);
    a0 = _mm256_and_si256(_mm256_and_si256(a0, a1), _mm256_and_si256(a2, a3));
    _mm256_storeu_si256((__m256i *)mask, a0);
    return __builtin_popcountll(mask[0]) + __builtin_popcountll(mask[1]) + __builtin_popcountll(mask[2]) + __builtin_popcountll(mask[3]);
}
u16 SPv[MAXS + 32] __attribute__((aligned(64))), RECv[MAXS + 32] __attribute__((aligned(64)));

static void scan_vector(tls_t *T) {
    int R = T->nrows;
    u64 n0 = T->n0;
    stats_t *st = &T->st;
    st->vectors++;
    if (do_dump) {
        #pragma omp critical(out)
        { printf("V %llu %d", (unsigned long long)n0, R); for (int j = 0; j < R; j++) printf(" %d", qs[T->rows[j]]); printf("\n"); }
        return;
    }
    /* tables */
    memset(T->mbuf, 0, (size_t)mtot * 8);
    for (int p = 0; p < ns; p++) {
        int s = SP[p];
        u8 *ct = T->cbuf + coff[p];
        memset(ct, 0, s);
        u64 a = (u128)(n0 % s) * minv[p] % s;
        const u16 *qm = qM[p];
        u64 *mk = T->mbuf + moff[p];
        for (int j = 0; j < R; j++) {
            int kap = (int)qm[T->rows[j]] - (int)a; if (kap < 0) kap += s;
            ct[kap]++;
            mk[4 * kap + (j >> 6)] |= 1ull << (j & 63);
        }
        for (int i = s; i < s + CK; i++) ct[i] = ct[i - s];
    }
    for (int w = 0; w < 4; w++) T->rowmask[w] = R >= 64 * w + 64 ? ~0ull : R > 64 * w ? (1ull << (R - 64 * w)) - 1 : 0;
    for (int j = 0; j < R; j++) T->rowq[j] = qs[T->rows[j]];
    int th = theta0 + R - rref; if (th < 0) th = 0; if (th > 255) th = 255;
    u128 lo = Xmin > n0 ? (Xmin - n0) / Mmod + 1 : 0;      /* first k with N > Xmin */
    if (Xmax < n0) return;
    u128 hi = (Xmax - n0) / Mmod;                           /* last k with N <= Xmax */
    if (hi < lo) return;
    u64 kmin = (u64)lo, kmax = (u64)hi;
    u64 kc = kmin & ~(u64)(CK - 1);
    u16 phi[MAXS + 32] __attribute__((aligned(64)));
    memset(phi, 0, sizeof phi);
    for (int p = 0; p < ns; p++) phi[p] = (u16)(kc % SP[p]);
    const __m512i thv = _mm512_set1_epi8((char)th);
    const u64 smask = ((u64)1 << sample_bits) - 1;
    for (; kc <= kmax; kc += CK) {
        __m512i sc[8];
        for (int b = 0; b < 8; b++) sc[b] = _mm512_setzero_si512();
        for (int p = 0; p < ns; p++) {
            const u8 *t = T->cbuf + coff[p] + phi[p];
            for (int b = 0; b < 8; b++) sc[b] = _mm512_adds_epu8(sc[b], _mm512_loadu_si512(t + 64 * b));
        }
        double lnN = log((double)((u128)n0 + (u128)kc * Mmod)), eps = eps_at(lnN), l1 = log1p(-eps);
        double odds2 = (eps / (1 - eps)) * (eps / (1 - eps));
        u16 todo_d[CK + 8]; int ntodo = 0;
        for (int b = 0; b < 8; b++) {
            u64 bk = kc + 64 * b;
            if (do_hist) { u8 tmp[64]; _mm512_storeu_si512(tmp, sc[b]); for (int j = 0; j < 64; j++) if (bk + j >= kmin && bk + j <= kmax) T->hs[tmp[j]]++; }
            u64 mm = _mm512_cmpge_epu8_mask(sc[b], thv);
            /* every 2^sample_bits-th member also goes through the exact stage, for the mass estimate */
            u64 sm = 0;
            if (((bk + 63) & ~smask) >= bk) sm = 1ull << (((bk + 63) & ~smask) - bk);
            u64 todo = mm | sm;
            while (todo) {
                int j = __builtin_ctzll(todo); todo &= todo - 1;
                todo_d[ntodo++] = (u16)(64 * b + j) | (u16)(((mm >> j) & 1) << 14) | (u16)(((sm >> j) & 1) << 15);
            }
        }
        for (int i = 0; i < ntodo; i++) {
            int d = todo_d[i] & 0x3fff, issel = (todo_d[i] >> 14) & 1, issam = todo_d[i] >> 15;
            u64 k = kc + d;
            if (k < kmin || k > kmax) continue;
            u64 mask[4];
            int a = exact_stage(T, phi, d, mask);
            if (issel) st->sel++;
            if (!issam && (!issel || a > Ta)) continue;
            double w = exp(l1 * a);
            if (issam) { st->samples++; st->mass_all += w; if (issel && a <= Ta) st->mass_cap += w; if (do_hist) T->ha[a]++; }
            if (!issel || a > Ta) continue;
            st->kept++; st->exp_tested += w; st->exp_corr += w * exp(c2 * odds2 * a * (a - 1) / 2);
            if (a == 0) { member_t m0 = {(u128)n0 + (u128)k * Mmod, {0, 0, 0, 0}, k}; success(T, &m0); continue; }
            if (T->qn == T->qcap) { T->qcap *= 2; T->queue = realloc(T->queue, T->qcap * sizeof(member_t)); }
            member_t *m = &T->queue[T->qn++];
            m->N = (u128)n0 + (u128)k * Mmod; m->k = k; memcpy(m->m, mask, 32);
        }
        if (T->qn >= 96) fermat_drain(T, F52_LANES);
        for (int p = 0; p < ns; p++) { int f = phi[p] + ckm[p]; if (f >= SP[p]) f -= SP[p]; phi[p] = (u16)f; }
    }
    st->members += kmax - kmin + 1;
    fermat_drain(T, 1);                                  /* finish this vector's members */
}

/* ---------------------------------------------------------------- enumeration */

static void dfs(tls_t *T, int i, const u64 *alive, int n, u128 n0) {
    if (i == NR) {
        if (n < Rlo) return;
        u64 v = (u64)(n0 % Mmod);
        if (have_one && v != one_n0) return;
        T->n0 = v; T->nrows = 0;
        for (int w = 0; w < NW; w++) { u64 x = alive[w]; while (x) { T->rows[T->nrows++] = 64 * w + __builtin_ctzll(x); x &= x - 1; } }
        scan_vector(T);
        return;
    }
    int later = 0;
    for (int j = i + 1; j < NR; j++) {
        int best = 0;
        for (int a = 1; a < RS[j]; a++) { int c = pcw(alive, cls[j][a]); if (c > best) best = c; }
        later += best;
    }
    int r = RS[i], cnt[44], ord[44];
    for (int a = 1; a < r; a++) { cnt[a] = pcw(alive, cls[i][a]); ord[a - 1] = a; }
    for (int x = 1; x < r - 1; x++) { int v = ord[x], y = x; while (y > 0 && cnt[ord[y - 1]] < cnt[v]) { ord[y] = ord[y - 1]; y--; } ord[y] = v; }
    for (int x = 0; x < r - 1; x++) {
        int a = ord[x];
        if (n - cnt[a] - later > Rhi) break;
        u64 next[NW];
        for (int w = 0; w < NW; w++) next[w] = alive[w] & ~cls[i][a][w];
        dfs(T, i + 1, next, n - cnt[a], n0 + (u128)a * Ebasis[i]);
    }
}

#define SPLIT 11
typedef struct { u64 alive[NW]; int n, unit; u128 n0; stats_t st; } node_t;
static node_t *nodes; static int nnodes, capnodes, cur_unit;
/* the nodes SPLIT primes deep of one unit that can still hold a vector with at most Rhi residual primes */
static void collect(int i, const u64 *alive, int n, u128 n0) {
    if (i == SPLIT) {
        if (nnodes == capnodes) { capnodes = capnodes ? 2 * capnodes : 1024; nodes = realloc(nodes, capnodes * sizeof(node_t)); }
        memcpy(nodes[nnodes].alive, alive, sizeof(u64) * NW); nodes[nnodes].n = n; nodes[nnodes].n0 = n0; nodes[nnodes].unit = cur_unit; nnodes++;
        return;
    }
    int later = 0;
    for (int j = i + 1; j < NR; j++) { int best = 0; for (int a = 1; a < RS[j]; a++) { int c = pcw(alive, cls[j][a]); if (c > best) best = c; } later += best; }
    int r = RS[i];
    for (int a = 1; a < r; a++) {
        int c = pcw(alive, cls[i][a]);
        if (n - c - later > Rhi) continue;
        u64 next[NW];
        for (int w = 0; w < NW; w++) next[w] = alive[w] & ~cls[i][a][w];
        collect(i + 1, next, n - c, n0 + (u128)a * Ebasis[i]);
    }
}

static void add_stats(stats_t *a, const stats_t *b) {
    a->vectors += b->vectors; a->members += b->members; a->sel += b->sel; a->kept += b->kept; a->tests += b->tests;
    a->prps += b->prps; a->found += b->found; a->samples += b->samples; a->exp_tested += b->exp_tested; a->exp_corr += b->exp_corr;
    a->mass_all += b->mass_all; a->mass_cap += b->mass_cap;
}

int main(int argc, char **argv) {
    if (argc < 9) { fprintf(stderr, "usage: fscan Q L Rlo Rhi Xmin Xmax theta Ta [key=value ...]\n"); return 2; }
    Q = atoi(argv[1]); L = atoi(argv[2]); Rlo = atoi(argv[3]); Rhi = atoi(argv[4]);
    Xmin = parse_big(argv[5]); Xmax = parse_big(argv[6]); theta0 = atoi(argv[7]); Ta = atoi(argv[8]);
    rref = Rlo;
    const char *donefile = NULL; int threads = omp_get_max_threads();
    for (int i = 9; i < argc; i++) {
        if (!strncmp(argv[i], "rref=", 5)) rref = atoi(argv[i] + 5);
        else if (!strncmp(argv[i], "slice=", 6)) sscanf(argv[i] + 6, "%d/%d", &slice_i, &slice_n);
        else if (!strncmp(argv[i], "done=", 5)) donefile = argv[i] + 5;
        else if (!strncmp(argv[i], "sample=", 7)) sample_bits = atoi(argv[i] + 7);
        else if (!strncmp(argv[i], "dump=", 5)) do_dump = atoi(argv[i] + 5);
        else if (!strncmp(argv[i], "hist=", 5)) do_hist = atoi(argv[i] + 5);
        else if (!strncmp(argv[i], "threads=", 8)) threads = atoi(argv[i] + 8);
        else if (!strncmp(argv[i], "c2=", 3)) c2 = atof(argv[i] + 3);
        else if (!strncmp(argv[i], "one=", 4)) { one_n0 = strtoull(argv[i] + 4, NULL, 10); have_one = 1; }
        else { fprintf(stderr, "unknown argument %s\n", argv[i]); return 2; }
    }
    if (Rhi > MAXROWS || Q > 64 * NW * 8) { fprintf(stderr, "Rhi or Q too large\n"); return 2; }
    /* rows */
    char *sv = calloc(Q > L + 1 ? Q : L + 1, 1);
    int lim = Q > L + 1 ? Q : L + 1;
    for (int p = 3; p < lim; p += 2) {
        if (sv[p]) continue;
        if (p < Q) { if (nq >= 64 * NW) { fprintf(stderr, "too many rows\n"); return 2; } qs[nq++] = p; }
        for (long m = (long)p * p; m < lim; m += 2 * p) sv[m] = 1;
    }
    for (int j = 0; j < NR; j++)
        for (int x = 0; x < nq; x++) cls[j][qs[x] % RS[j]][x >> 6] |= 1ull << (x & 63);
    Mmod = 2; for (int j = 0; j < NR; j++) Mmod *= RS[j];
    for (int j = 0; j < NR; j++) { u64 c = Mmod / RS[j]; Ebasis[j] = c * invmod(c % RS[j], RS[j]); }
    /* score primes */
    prodL = 0.5;
    for (int p = 3; p <= L; p += 2) {
        if (sv[p]) continue;
        prodL *= 1.0 - 1.0 / p;
        if (p <= RS[NR - 1]) continue;
        if (ns >= MAXS) { fprintf(stderr, "too many score primes\n"); return 2; }
        SP[ns] = p; coff[ns] = ctot; ctot += p + CK; moff[ns] = mtot; mtot += 4 * p; ckm[ns] = CK % p;
        minv[ns] = invmod(Mmod % p, p);
        qM[ns] = malloc(nq * sizeof(u16));
        for (int x = 0; x < nq; x++) qM[ns][x] = (u16)((u64)(qs[x] % p) * minv[ns] % p);
        SPv[ns] = (u16)p; RECv[ns] = (u16)(65536 / p);
        ns++;
    }
    for (int p = ns; p < MAXS + 32; p++) { SPv[p] = 1; RECv[p] = 0; }
    if (L + CK >= 65536) { fprintf(stderr, "L too large\n"); return 2; }

    /* work units: the subtrees given by the residues mod 3, 5, 7, 11, 13, 17, 19.  They are very unequal (the
       small vectors share the best classes of the small primes), so the threads share the subtrees SPLIT
       primes deep of a batch of units; a unit is written to the done file when its batch is finished. */
    int nsub = 2 * 4 * 6 * 10 * 12 * 16 * 18;
    char *done = calloc(nsub, 1);
    stats_t total; memset(&total, 0, sizeof total);
    char tag[256];
    snprintf(tag, sizeof tag, "Q=%d L=%d R=%d..%d Xmin=%s Xmax=%s theta=%d rref=%d Ta=%d units=7", Q, L, Rlo, Rhi, argv[5], argv[6], theta0, rref, Ta);
    if (donefile) {
        FILE *f = fopen(donefile, "r");
        if (f) {
            char line[2048];
            while (fgets(line, sizeof line, f)) {
                int id; char *p = strstr(line, " | ");
                if (line[0] != 'W' || !p || strncmp(p + 3, tag, strlen(tag))) continue;
                stats_t s; memset(&s, 0, sizeof s);
                if (sscanf(line, "W %d %lu %lu %lu %lu %lu %lu %lu %lu %lf %lf %lf %lf", &id, &s.vectors, &s.members, &s.sel, &s.kept,
                           &s.tests, &s.prps, &s.found, &s.samples, &s.exp_tested, &s.exp_corr, &s.mass_all, &s.mass_cap) == 13 && id >= 0 && id < nsub && !done[id]) {
                    done[id] = 1; add_stats(&total, &s);
                }
            }
            fclose(f);
        }
    }
    FILE *df = donefile ? fopen(donefile, "a") : NULL;
    u64 all[NW] = {0};
    for (int x = 0; x < nq; x++) all[x >> 6] |= 1ull << (x & 63);
    double t0 = omp_get_wtime();
    tls_t **TT = calloc(threads, sizeof(tls_t *));
    for (int t = 0; t < threads; t++) {
        tls_t *T = aligned_alloc(64, (sizeof(tls_t) + 63) & ~(size_t)63);
        memset(T, 0, sizeof *T);
        T->cbuf = aligned_alloc(64, (ctot + 64 + 63) & ~63); T->mbuf = aligned_alloc(64, ((size_t)mtot * 8 + 63) & ~(size_t)63);
        T->qcap = 256; T->queue = malloc(T->qcap * sizeof(member_t));
        TT[t] = T;
    }
    static const int UM[7] = {2, 4, 6, 10, 12, 16, 18};
    int *batch_units = NULL, nbatch = 0, capbatch = 0;
    nnodes = 0;
    for (int id = 0; id <= nsub; id++) {
        if (id < nsub) {
            if (done[id] || id % slice_n != slice_i) continue;
            u64 al[NW]; u128 n0 = 0;
            for (int w = 0; w < NW; w++) al[w] = all[w];
            for (int j = 0, x = id; j < 7; j++) {
                int a = 1 + x % UM[j]; x /= UM[j];
                for (int w = 0; w < NW; w++) al[w] &= ~cls[j][a][w];
                n0 += (u128)a * Ebasis[j];
            }
            int n = 0; for (int w = 0; w < NW; w++) n += __builtin_popcountll(al[w]);
            /* the same bound as inside dfs(): skip the unit when no vector in it can be small enough */
            int later = 0;
            for (int j = 7; j < NR; j++) { int best = 0; for (int a = 1; a < RS[j]; a++) { int c = pcw(al, cls[j][a]); if (c > best) best = c; } later += best; }
            if (n - later > Rhi) continue;
            cur_unit = id;
            int before = nnodes;
            collect(7, al, n, n0);
            if (nnodes == before) continue;
            if (nbatch == capbatch) { capbatch = capbatch ? 2 * capbatch : 4096; batch_units = realloc(batch_units, capbatch * sizeof(int)); }
            batch_units[nbatch++] = id;
            if (nnodes < 16384) continue;                  /* gather enough subtrees to keep every thread busy */
        }
        #pragma omp parallel for schedule(dynamic, 1) num_threads(threads)
        for (int i = 0; i < nnodes; i++) {
            tls_t *T = TT[omp_get_thread_num()];
            memset(&T->st, 0, sizeof(stats_t));
            dfs(T, SPLIT, nodes[i].alive, nodes[i].n, nodes[i].n0);
            nodes[i].st = T->st;
        }
        for (int u = 0, i = 0; u < nbatch; u++) {         /* the nodes of a unit are consecutive */
            stats_t us; memset(&us, 0, sizeof us);
            for (; i < nnodes && nodes[i].unit == batch_units[u]; i++) add_stats(&us, &nodes[i].st);
            add_stats(&total, &us);
            if (df && us.vectors && !do_dump) {
                fprintf(df, "W %d %lu %lu %lu %lu %lu %lu %lu %lu %.9g %.9g %.9g %.9g | %s\n", batch_units[u], us.vectors, us.members, us.sel, us.kept,
                        us.tests, us.prps, us.found, us.samples, us.exp_tested, us.exp_corr, us.mass_all, us.mass_cap, tag);
            }
        }
        if (df) fflush(df);
        nnodes = 0; nbatch = 0;
    }
    double dt = omp_get_wtime() - t0;
    double scale = (double)((u64)1 << sample_bits);
    printf("STATS %s | vectors=%lu members=%lu selected=%lu kept=%lu tests=%lu prps=%lu found=%lu expected=%.6g expected_raw=%.6g "
           "mass_all=%.6g mass_captured_sampled=%.6g samples=%lu seconds=%.1f threads=%d rate=%.4g\n",
           tag, total.vectors, total.members, total.sel, total.kept, total.tests, total.prps, total.found, total.exp_corr, total.exp_tested,
           total.mass_all * scale, total.mass_cap * scale, total.samples, dt, threads, total.members / (dt > 0 ? dt : 1));
    if (do_hist) {
        u64 hs[256] = {0}, ha[257] = {0};
        for (int t = 0; t < threads; t++) { for (int i = 0; i < 256; i++) hs[i] += TT[t]->hs[i]; for (int i = 0; i < 257; i++) ha[i] += TT[t]->ha[i]; }
        printf("HS"); for (int i = 0; i < 256; i++) if (hs[i]) printf(" %d:%lu", i, hs[i]); printf("\n");
        printf("HA"); for (int i = 0; i < 257; i++) if (ha[i]) printf(" %d:%lu", i, ha[i]); printf("\n");
    }
    return 0;
}
