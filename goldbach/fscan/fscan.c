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
 *   3. FERMAT-test the rows of those members, 16 numbers at a time (fermat52.h, AVX-512 IFMA),
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
 *     keys: rref=R (default Rlo)   slice=i/n (every n-th subtree)   done=FILE (resume/progress log)
 *           sample=S (exact stage on every 2^S-th member for the mass estimate, default 12)
 *           dump=1 (print the vectors, no scan)   one=N0 (scan only the vector with this N0)
 *           hist=1 (print the score and a histograms)   threads=T   c2=X (pair term, see README)
 * Output: "S <N> <k> <N0> <R>" per success, "U ..." per finished subtree, then one "STATS" line.
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
    u64 hs[256], ha[257];
} stats_t;

typedef struct { u128 N; u64 m[4]; u64 k; } member_t;

typedef struct {
    u8 *cbuf;                         /* score tables: per prime s + CK bytes, periodic */
    u64 *mbuf;                        /* row masks: per prime s entries of 4 words */
    int rows[MAXROWS], nrows;
    u64 n0;
    member_t *queue; int qn, qcap;
    member_t slot[16]; int act[16];
    stats_t st;
    FILE *out;
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
        for (int i = 0; i < 16; i++) {
            if (!T->act[i] && T->qn) { T->slot[i] = T->queue[--T->qn]; T->act[i] = 1; }
            nact += T->act[i];
        }
        if (nact < need || nact == 0) return;
        u128 n[16], mx = 0; int row[16], first = -1;
        for (int i = 0; i < 16; i++) {
            if (!T->act[i]) continue;
            member_t *m = &T->slot[i];
            int w = 0; while (!m->m[w]) w++;
            row[i] = 64 * w + __builtin_ctzll(m->m[w]);
            n[i] = m->N - (u128)qs[T->rows[row[i]]];
            if (n[i] > mx) mx = n[i];
            if (first < 0) first = i;
        }
        int b = 0; for (u128 x = mx; x; x >>= 1) b++;
        int t = b - 6;
        f52_lanes LA, LB;
        for (int i = 0; i < 16; i++) {
            if (!T->act[i]) n[i] = n[first];
            if (i < 8) f52_setup(&LA, i, n[i], t); else f52_setup(&LB, i - 8, n[i], t);
        }
        unsigned res = f52_run(&LA, &LB, n, 16, t);
        for (int i = 0; i < 16; i++) {
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
    __m256i al = _mm256_set1_epi64x(-1);
    const u64 *mb = T->mbuf;
    for (int p = 0; p < ns; p++)
        al = _mm256_andnot_si256(_mm256_loadu_si256((const __m256i *)(mb + moff[p] + 4 * c[p])), al);
    _mm256_storeu_si256((__m256i *)mask, al);
    int R = T->nrows;                                   /* drop the bits beyond the last row */
    for (int w = 0; w < 4; w++) {
        int lo = 64 * w;
        if (R <= lo) mask[w] = 0;
        else if (R < lo + 64) mask[w] &= (1ull << (R - lo)) - 1;
    }
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
        for (int b = 0; b < 8; b++) {
            u64 bk = kc + 64 * b;
            if (do_hist) { u8 tmp[64]; _mm512_storeu_si512(tmp, sc[b]); for (int j = 0; j < 64; j++) if (bk + j >= kmin && bk + j <= kmax) st->hs[tmp[j]]++; }
            u64 mm = _mm512_cmpge_epu8_mask(sc[b], thv);
            /* every 2^sample_bits-th member also goes through the exact stage, for the mass estimate */
            u64 sm = 0;
            if (((bk + 63) & ~smask) >= bk) sm = 1ull << (((bk + 63) & ~smask) - bk);
            u64 todo = mm | sm;
            while (todo) {
                int j = __builtin_ctzll(todo); todo &= todo - 1;
                u64 k = bk + j;
                if (k < kmin || k > kmax) continue;
                u64 mask[4];
                int a = exact_stage(T, phi, 64 * b + j, mask);
                int issel = (mm >> j) & 1, issam = (sm >> j) & 1;
                if (issel) st->sel++;
                if (!issam && (!issel || a > Ta)) continue;
                double w = exp(l1 * a);
                if (issam) { st->samples++; st->mass_all += w; if (issel && a <= Ta) st->mass_cap += w; if (do_hist) st->ha[a]++; }
                if (!issel || a > Ta) continue;
                st->kept++; st->exp_tested += w; st->exp_corr += w * exp(c2 * odds2 * a * (a - 1) / 2);
                if (a == 0) { member_t m0 = {(u128)n0 + (u128)k * Mmod, {0, 0, 0, 0}, k}; success(T, &m0); continue; }
                if (T->qn == T->qcap) { T->qcap *= 2; T->queue = realloc(T->queue, T->qcap * sizeof(member_t)); }
                member_t *m = &T->queue[T->qn++];
                m->N = (u128)n0 + (u128)k * Mmod; m->k = k; memcpy(m->m, mask, 32);
            }
        }
        if (T->qn >= 64) fermat_drain(T, 16);
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

static void add_stats(stats_t *a, const stats_t *b) {
    a->vectors += b->vectors; a->members += b->members; a->sel += b->sel; a->kept += b->kept; a->tests += b->tests;
    a->prps += b->prps; a->found += b->found; a->samples += b->samples; a->exp_tested += b->exp_tested; a->exp_corr += b->exp_corr;
    a->mass_all += b->mass_all; a->mass_cap += b->mass_cap;
    for (int i = 0; i < 256; i++) a->hs[i] += b->hs[i];
    for (int i = 0; i < 257; i++) a->ha[i] += b->ha[i];
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

    /* work units: the subtrees given by the residues mod 3, 5, 7, 11, 13 */
    int nsub = 2 * 4 * 6 * 10 * 12;
    char *done = calloc(nsub, 1);
    stats_t total; memset(&total, 0, sizeof total);
    char tag[256];
    snprintf(tag, sizeof tag, "Q=%d L=%d R=%d..%d Xmax=%s theta=%d rref=%d Ta=%d", Q, L, Rlo, Rhi, argv[6], theta0, rref, Ta);
    if (donefile) {
        FILE *f = fopen(donefile, "r");
        if (f) {
            char line[2048];
            while (fgets(line, sizeof line, f)) {
                int id; char *p = strstr(line, " | ");
                if (line[0] != 'U' || !p || strncmp(p + 3, tag, strlen(tag))) continue;
                stats_t s; memset(&s, 0, sizeof s);
                if (sscanf(line, "U %d %lu %lu %lu %lu %lu %lu %lu %lu %lf %lf %lf %lf", &id, &s.vectors, &s.members, &s.sel, &s.kept,
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
    #pragma omp parallel num_threads(threads)
    {
        tls_t *T = aligned_alloc(64, (sizeof(tls_t) + 63) & ~(size_t)63);
        memset(T, 0, sizeof *T);
        T->cbuf = aligned_alloc(64, (ctot + 64 + 63) & ~63); T->mbuf = aligned_alloc(64, ((size_t)mtot * 8 + 63) & ~(size_t)63);
        T->qcap = 256; T->queue = malloc(T->qcap * sizeof(member_t));
        #pragma omp for schedule(dynamic, 1)
        for (int id = 0; id < nsub; id++) {
            if (done[id] || id % slice_n != slice_i) continue;
            int av[5] = {1 + id % 2, 1 + (id / 2) % 4, 1 + (id / 8) % 6, 1 + (id / 48) % 10, 1 + (id / 480) % 12};
            u64 al[NW]; u128 n0 = 0;
            for (int w = 0; w < NW; w++) al[w] = all[w];
            for (int j = 0; j < 5; j++) { for (int w = 0; w < NW; w++) al[w] &= ~cls[j][av[j]][w]; n0 += (u128)av[j] * Ebasis[j]; }
            int n = 0; for (int w = 0; w < NW; w++) n += __builtin_popcountll(al[w]);
            memset(&T->st, 0, sizeof T->st);
            /* the same bound as inside dfs(): skip the unit when no vector in it can be small enough */
            int later = 0;
            for (int j = 5; j < NR; j++) { int best = 0; for (int a = 1; a < RS[j]; a++) { int c = pcw(al, cls[j][a]); if (c > best) best = c; } later += best; }
            if (n - later <= Rhi) dfs(T, 5, al, n, n0);
            #pragma omp critical(out)
            {
                stats_t *s = &T->st;
                add_stats(&total, s);
                if (df && (s->vectors || !do_dump)) {
                    fprintf(df, "U %d %lu %lu %lu %lu %lu %lu %lu %lu %.9g %.9g %.9g %.9g | %s\n", id, s->vectors, s->members, s->sel, s->kept,
                            s->tests, s->prps, s->found, s->samples, s->exp_tested, s->exp_corr, s->mass_all, s->mass_cap, tag);
                    fflush(df);
                }
            }
        }
    }
    double dt = omp_get_wtime() - t0;
    double scale = (double)((u64)1 << sample_bits);
    printf("STATS %s | vectors=%lu members=%lu selected=%lu kept=%lu tests=%lu prps=%lu found=%lu expected=%.6g expected_raw=%.6g "
           "mass_all=%.6g mass_captured_sampled=%.6g samples=%lu seconds=%.1f threads=%d rate=%.4g\n",
           tag, total.vectors, total.members, total.sel, total.kept, total.tests, total.prps, total.found, total.exp_corr, total.exp_tested,
           total.mass_all * scale, total.mass_cap * scale, total.samples, dt, threads, total.members / (dt > 0 ? dt : 1));
    if (do_hist) {
        printf("HS"); for (int i = 0; i < 256; i++) if (total.hs[i]) printf(" %d:%lu", i, total.hs[i]); printf("\n");
        printf("HA"); for (int i = 0; i < 257; i++) if (total.ha[i]) printf(" %d:%lu", i, total.ha[i]); printf("\n");
    }
    return 0;
}
