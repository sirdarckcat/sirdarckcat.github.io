// gfgold.c -- exact enumeration of the Goldbach problem in F_q[x], q in {3,5,7,9}.
//
//   ./gfgold q n outprefix [R_1 R_2 ... R_L]
//
// Objects.  Field elements are labelled 0..q-1 (q prime: integers mod q; q = 9: a + 3b <-> a + b*i, i^2 = -1).
// A monic polynomial of degree m with coefficients c_0..c_{m-1} (c_m = 1) has index v = sum c_k q^k.
// Rows = monic irreducibles Q of degree 1..n-1, ordered by degree, then by index.
// For every monic N of degree n:  G(N) = number of rows before the first row with N - Q irreducible
// (= number of rows of degree < n if there is none), D(N) = degree of that first row (n if none).
//
// Tables (built by a sieve, all monic polynomials of degree <= n): smallest irreducible factor (as an index in the
// ordered list of irreducibles of degree <= n/2), Moebius function mu.  For degree n only a "scan byte" is kept:
//   bits 0-2: class c = number of thresholds K_t with spfindex >= K_t (irreducible: all), bit 3: mu = -1, bit 4: irreducible.
// Thresholds K_t (on the index of the smallest irreducible factor): 0, all linear, the prefix of irreducibles whose
// total degree fits in n ("room"), all of degree <= 2, all of degree <= 3.
//   s_t(N;R) = #{i < R : N - Q_i has no irreducible factor among the first K_t irreducibles}
//   o_t(N;R) = the same, counting only rows with mu(N - Q_i) = -1 (squarefree, odd number of irreducible factors).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int q, n, p;
static uint8_t ADD[9][9], SUB[9][9], MUL[9][9];
static uint64_t pw[64], off[64];
static uint16_t *spf; static uint8_t *info;      // degrees 0..n-1 (info: bits 0-1 mu+1, bit 2 irreducible)
static uint8_t *sb;                              // degree n: scan byte (0 = unset during the sieve)
#define UNSET 0xFFFF
#define IRRBIG 0xFFFE
static int nsm = 0; static uint8_t sm_deg[70000]; static uint32_t sm_idx[70000];   // irreducibles of degree <= n/2
static int NT; static int Kt[8]; static const char *Kname[8]; static uint8_t cls_of[70000];

static void field_init(void) {
    for (int a = 0; a < q; a++) for (int b = 0; b < q; b++) {
        if (q != 9) { ADD[a][b] = (a + b) % q; SUB[a][b] = (a - b + q) % q; MUL[a][b] = (a * b) % q; }
        else {
            int a0 = a % 3, a1 = a / 3, b0 = b % 3, b1 = b / 3;
            ADD[a][b] = (a0 + b0) % 3 + 3 * ((a1 + b1) % 3);
            SUB[a][b] = (a0 - b0 + 3) % 3 + 3 * ((a1 - b1 + 3) % 3);
            MUL[a][b] = ((a0 * b0 - a1 * b1) % 3 + 3) % 3 + 3 * ((a0 * b1 + a1 * b0) % 3);
        }
    }
}

// ---- sieve ----
static int cur_m, cur_d, cur_e, cur_ia; static uint8_t cur_a[64];
static void leaf_set(uint64_t f, uint64_t bidx) {
    uint64_t be = off[cur_e] + bidx; int muB, spfB;
    if (cur_m < n) { if (spf[off[cur_m] + f] != UNSET) return; } else { if (sb[f]) return; }
    if (cur_e == 0) { muB = 1; spfB = UNSET; } else { muB = (int)(info[be] & 3) - 1; spfB = spf[be]; }
    int mu = (muB != 0 && spfB != cur_ia) ? -muB : 0;
    if (cur_m < n) { spf[off[cur_m] + f] = (uint16_t)cur_ia; info[off[cur_m] + f] = (uint8_t)(mu + 1); }
    else sb[f] = (uint8_t)(cls_of[cur_ia] | ((mu == -1) ? 8 : 0));
}
static void rec(int j, const uint8_t *prod, uint64_t bidx) {
    int d = cur_d, m = cur_m;
    if (j == 0) {
        uint64_t hi = 0; for (int k = m - 1; k > d; k--) hi = hi * q + prod[k];
        hi *= pw[d + 1];
        for (int b = 0; b < q; b++) {
            uint64_t lo = 0; const uint8_t *mb = MUL[b];
            for (int k = d; k >= 0; k--) lo = lo * q + ADD[prod[k]][mb[cur_a[k]]];
            leaf_set(hi + lo, bidx + b);
        }
        return;
    }
    uint8_t np[64];
    for (int b = 0; b < q; b++) {
        memcpy(np, prod, m + 1); const uint8_t *mb = MUL[b];
        for (int k = 0; k <= d; k++) np[j + k] = ADD[prod[j + k]][mb[cur_a[k]]];
        rec(j - 1, np, bidx + b * pw[j]);
    }
}
static void sieve_degree(int m) {
    cur_m = m;
    if (m < n) for (uint64_t v = 0; v < pw[m]; v++) spf[off[m] + v] = UNSET;
    for (int ia = 0; ia < nsm; ia++) {
        int d = sm_deg[ia]; if (2 * d > m) break;
        cur_d = d; cur_e = m - d; cur_ia = ia;
        uint64_t t = sm_idx[ia]; for (int k = 0; k < d; k++) { cur_a[k] = t % q; t /= q; } cur_a[d] = 1;
        uint8_t prod[64]; memset(prod, 0, sizeof prod);
        for (int k = 0; k <= d; k++) prod[cur_e + k] = cur_a[k];
        rec(cur_e - 1, prod, 0);
    }
    if (m < n) for (uint64_t v = 0; v < pw[m]; v++) if (spf[off[m] + v] == UNSET) {
        if (2 * m <= n) { sm_deg[nsm] = m; sm_idx[nsm] = (uint32_t)v; spf[off[m] + v] = (uint16_t)nsm; nsm++; }
        else spf[off[m] + v] = IRRBIG;
        info[off[m] + v] = 0 | 4;
    }
}

// ---- rows ----
static uint64_t nrows; static uint32_t *row_idx; static uint8_t *row_deg; static uint32_t **row_T; static uint64_t nfast;
static uint64_t rows_below[64];   // number of rows of degree < d

static inline uint64_t slow_idx(uint64_t v, const uint8_t *Nd, uint64_t i) {
    int d = row_deg[i]; uint64_t qi = row_idx[i]; int64_t r = (int64_t)v;
    for (int k = 0; k < d; k++) { int c = qi % q; qi /= q; r += ((int64_t)SUB[Nd[k]][c] - Nd[k]) * (int64_t)pw[k]; }
    r += ((int64_t)SUB[Nd[d]][1] - Nd[d]) * (int64_t)pw[d];
    return (uint64_t)r;
}

typedef struct { uint64_t cnt, hits, tall, todd; } bin_t;
#define FB 12
#define FM ((1u << FB) - 1)
typedef struct { uint64_t v; uint32_t G; } top_t;
static int cmp_top(const void *a, const void *b) {
    const top_t *x = a, *y = b; if (x->G != y->G) return x->G < y->G ? 1 : -1; return x->v < y->v ? -1 : (x->v > y->v);
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: gfgold q n outprefix [R_1 ... R_L]\n"); return 1; }
    q = atoi(argv[1]); n = atoi(argv[2]); const char *pre = argv[3];
    int L = argc - 4; int RL[16]; for (int l = 0; l < L; l++) RL[l] = atoi(argv[4 + l]);
    p = (q == 9) ? 3 : q; field_init();
    pw[0] = 1; for (int k = 1; k <= n + 1; k++) pw[k] = pw[k - 1] * q;
    off[0] = 0; for (int m = 1; m <= n; m++) off[m] = off[m - 1] + pw[m - 1];
    spf = malloc(off[n] * sizeof(uint16_t)); info = malloc(off[n]); sb = calloc(pw[n], 1);
    if (!spf || !info || !sb) { fprintf(stderr, "memory\n"); return 1; }
    spf[0] = UNSET; info[0] = 2;
    for (int m = 1; m < n; m++) sieve_degree(m);
    // thresholds
    int I[8] = {0}; for (int ia = 0; ia < nsm; ia++) if (sm_deg[ia] <= 3) I[sm_deg[ia]]++;
    int room = 0, tot = 0; while (room < nsm && tot + sm_deg[room] <= n) { tot += sm_deg[room]; room++; }
    int cand[5] = {0, I[1], room, I[1] + I[2], I[1] + I[2] + I[3]}; const char *cn[5] = {"none", "deg<=1", "room", "deg<=2", "deg<=3"};
    static char namebuf[8][64]; NT = 0;
    for (int pass = 0; pass < 5; pass++) {      // insertion in sorted order, merging duplicates
        int best = -1; for (int c = 0; c < 5; c++) if (cand[c] >= 0 && (best < 0 || cand[c] < cand[best])) best = c;
        if (NT > 0 && Kt[NT - 1] == cand[best]) { strcat(namebuf[NT - 1], "="); strcat(namebuf[NT - 1], cn[best]); }
        else { Kt[NT] = cand[best]; strcpy(namebuf[NT], cn[best]); Kname[NT] = namebuf[NT]; NT++; }
        cand[best] = -1;
    }
    for (int ia = 0; ia < nsm; ia++) { int c = 0; for (int t = 0; t < NT; t++) if (ia >= Kt[t]) c++; cls_of[ia] = (uint8_t)c; }
    sieve_degree(n);
    uint64_t nirr_n = 0;
    for (uint64_t v = 0; v < pw[n]; v++) if (!sb[v]) { sb[v] = (uint8_t)(NT | 8 | 16); nirr_n++; }
    // rows
    nrows = 0; for (int d = 1; d < n; d++) { rows_below[d] = nrows; for (uint64_t v = 0; v < pw[d]; v++) if (info[off[d] + v] & 4) nrows++; }
    rows_below[n] = nrows;
    row_idx = malloc(nrows * 4); row_deg = malloc(nrows); row_T = calloc(nrows, sizeof(uint32_t *));
    { uint64_t r = 0; for (int d = 1; d < n; d++) for (uint64_t v = 0; v < pw[d]; v++) if (info[off[d] + v] & 4) { row_idx[r] = (uint32_t)v; row_deg[r] = d; r++; } }
    int dcap = 0; nfast = 0;
    for (int d = 1; d < n; d++) {
        uint64_t cntd = rows_below[d + 1] - rows_below[d];
        if (cntd * pw[d + 1] > 16000000ull) break;
        dcap = d;
        for (uint64_t r = rows_below[d]; r < rows_below[d + 1]; r++) {
            uint32_t *T = malloc(pw[d + 1] * 4); uint8_t Qd[64]; uint64_t t = row_idx[r];
            for (int k = 0; k < d; k++) { Qd[k] = t % q; t /= q; } Qd[d] = 1;
            for (uint64_t lo = 0; lo < pw[d + 1]; lo++) {
                uint64_t x = lo, res = 0;
                for (int k = 0; k <= d; k++) { int c = x % q; x /= q; res += (uint64_t)SUB[c][Qd[k]] * pw[k]; }
                T[lo] = (uint32_t)res;
            }
            row_T[r] = T;
        }
        nfast = rows_below[d + 1];
    }
    char fn[512]; snprintf(fn, sizeof fn, "%s.txt", pre); FILE *fo = fopen(fn, "w");
    fprintf(fo, "q %d n %d p %d  monic N: %llu  irreducible of degree n: %llu  rows (deg<n): %llu  fast rows: %llu (deg<=%d)\n",
            q, n, p, (unsigned long long)pw[n], (unsigned long long)nirr_n, (unsigned long long)nrows, (unsigned long long)nfast, dcap);
    fprintf(fo, "rows_below:"); for (int d = 1; d <= n; d++) fprintf(fo, " %llu", (unsigned long long)rows_below[d]); fprintf(fo, "\n");
    // table checks and the rates rho_t
    { uint64_t cs[8] = {0}, co[8] = {0}, nsq = 0, nodd = 0;
      for (uint64_t v = 0; v < pw[n]; v++) { int b = sb[v], c = b & 7; for (int t = 0; t < c; t++) { cs[t]++; if (b & 8) co[t]++; } if (b & 8) nodd++; }
      (void)nsq;
      fprintf(fo, "check: mu=-1 count %llu (expect (q^n-q^(n-1))/2 = %llu)\n", (unsigned long long)nodd, (unsigned long long)((pw[n] - pw[n - 1]) / 2));
      for (int t = 0; t < NT; t++) fprintf(fo, "threshold %d K=%d (%s): rough %llu  rough&odd %llu  rho=%.8f rho_odd=%.8f\n", t, Kt[t], Kname[t],
              (unsigned long long)cs[t], (unsigned long long)co[t], (double)nirr_n / cs[t], (double)nirr_n / co[t]);
    }
    fflush(fo);
    // packed increments
    uint64_t incS[16], incO[16];
    for (int b = 0; b < 16; b++) { int c = b & 7; uint64_t x = 0; for (int t = 0; t < c && t < NT; t++) x += 1ull << (FB * t); incS[b] = x; incO[b] = (b & 8) ? x : 0; }
    // accumulators
    int GH = 8192; int NC = n + 2;   // deg N' class: 0 = (N' = 0), k+1 = deg N' = k ; extra class n+1 = family N' = 1
    uint64_t *Ghist = calloc((size_t)NC * GH, 8); uint64_t Dhist[64][64]; memset(Dhist, 0, sizeof Dhist);
    uint64_t exceptions = 0; uint32_t Gmax = 0; int Dmax = 0;
    bin_t **bins = NULL; uint32_t **maxG = NULL; uint64_t **jSS = NULL, **jSO = NULL; int troom = 0, tdeep = NT - 1;
    for (int t = 0; t < NT; t++) if (Kt[t] == room) troom = t;
    if (L) {
        bins = malloc(sizeof(bin_t *) * L * NT); maxG = malloc(sizeof(uint32_t *) * L * NT); jSS = malloc(sizeof(uint64_t *) * L); jSO = malloc(sizeof(uint64_t *) * L);
        for (int l = 0; l < L; l++) {
            size_t R1 = RL[l] + 1;
            for (int t = 0; t < NT; t++) { bins[l * NT + t] = calloc(R1 * R1, sizeof(bin_t)); maxG[l * NT + t] = calloc(R1, 4); }
            jSS[l] = calloc(R1 * R1, 8); jSO[l] = calloc(R1 * R1, 8);
        }
        if ((uint64_t)RL[L - 1] > nrows) { fprintf(stderr, "R too large\n"); return 1; }
    }
    size_t topcap = 200000, ntop = 0; top_t *top = malloc(sizeof(top_t) * (topcap + 1)); uint32_t topcut = 0;
    size_t dcapn = 200000, nd = 0; uint64_t *dlist = malloc(8 * dcapn); uint64_t ndtot = 0;
    uint8_t Nd[64]; memset(Nd, 0, sizeof Nd); Nd[n] = 1;
    uint64_t lo[64], hib[64]; memset(lo, 0, sizeof lo);
    int Rlast = L ? RL[L - 1] : 0;
    for (uint64_t v = 0; v < pw[n]; v++) {
        for (int d = 1; d <= dcap; d++) hib[d] = v - lo[d];
        uint64_t S = 0, O = 0, snapS = 0, snapO = 0; int hit = 0; uint64_t G = 0; uint64_t i = 0;
        uint16_t sf[16][8];
        for (int l = 0; l < L; l++) {
            for (; i < (uint64_t)RL[l]; i++) {
                uint64_t x = row_T[i] ? hib[row_deg[i]] + row_T[i][lo[row_deg[i]]] : slow_idx(v, Nd, i);
                int b = sb[x]; S += incS[b & 15]; O += incO[b & 15];
                if ((b & 16) && !hit) { hit = 1; G = i; snapS = S; snapO = O; }
            }
            size_t R1 = RL[l] + 1;
            for (int t = 0; t < NT; t++) {
                unsigned s = (S >> (FB * t)) & FM, o = (O >> (FB * t)) & FM; sf[l][t] = (uint16_t)s;
                bin_t *b = &bins[l * NT + t][s * R1 + o]; b->cnt++;
                if (!hit) { b->hits++; b->tall += s; b->todd += o; }
                else { b->tall += (snapS >> (FB * t)) & FM; b->todd += (snapO >> (FB * t)) & FM; }
            }
            { unsigned sr = (S >> (FB * troom)) & FM, sd = (S >> (FB * tdeep)) & FM, od = (O >> (FB * tdeep)) & FM;
              jSS[l][sr * R1 + sd]++; jSO[l][sr * R1 + od]++; }
        }
        if (!hit) {
            for (; i < nrows; i++) {
                uint64_t x = row_T[i] ? hib[row_deg[i]] + row_T[i][lo[row_deg[i]]] : slow_idx(v, Nd, i);
                if (sb[x] & 16) { hit = 1; G = i; break; }
            }
            if (!hit) { G = nrows; exceptions++; }
        }
        int D = (G < nrows) ? row_deg[G] : n;
        for (int l = 0; l < L; l++) for (int t = 0; t < NT; t++) { uint32_t *mg = &maxG[l * NT + t][sf[l][t]]; if (G + 1 > *mg) *mg = (uint32_t)(G + 1); }
        // derivative class
        int dc = 0; for (int k = n; k >= 1; k--) if (k % p != 0 && Nd[k] != 0) { dc = k; break; }   // dc = deg N' + 1, 0 if N' = 0
        uint64_t Gc = G < (uint64_t)GH ? G : (uint64_t)GH - 1;
        Ghist[(size_t)dc * GH + Gc]++; Dhist[dc][D]++;
        if (dc == 1 && Nd[1] == 1) { Ghist[(size_t)(n + 1) * GH + Gc]++; Dhist[n + 1][D]++; }
        if (G > Gmax) Gmax = (uint32_t)G;
        if (G >= topcut) {
            top[ntop].v = v; top[ntop].G = (uint32_t)G; ntop++;
            if (ntop >= topcap) { qsort(top, ntop, sizeof(top_t), cmp_top); ntop = topcap / 4; topcut = top[ntop - 1].G + 1; while (ntop > 0 && top[ntop - 1].G < topcut) ntop--; }
        }
        if (D > Dmax) { Dmax = D; nd = 0; ndtot = 0; }
        if (D == Dmax) { ndtot++; if (nd < dcapn) dlist[nd++] = v; }
        // increment N
        for (int k = 0; k < n; k++) { if (++Nd[k] < q) break; Nd[k] = 0; }
        for (int d = 1; d <= dcap; d++) if (++lo[d] == pw[d + 1]) lo[d] = 0;
    }
    // output
    fprintf(fo, "Gmax %u  Dmax %d  count(D=Dmax) %llu  exceptions(no row of degree<n works) %llu\n", Gmax, Dmax, (unsigned long long)ndtot, (unsigned long long)exceptions);
    fprintf(fo, "GHIST class(0:N'=0, k+1: deg N'=k, %d: N'=1) G count\n", n + 1);
    for (int c = 0; c < NC; c++) for (int g = 0; g < GH; g++) if (Ghist[(size_t)c * GH + g]) fprintf(fo, "GH %d %d %llu\n", c, g, (unsigned long long)Ghist[(size_t)c * GH + g]);
    for (int c = 0; c < NC; c++) for (int d = 0; d <= n; d++) if (Dhist[c][d]) fprintf(fo, "DH %d %d %llu\n", c, d, (unsigned long long)Dhist[c][d]);
    for (int l = 0; l < L; l++) {
        size_t R1 = RL[l] + 1;
        for (int t = 0; t < NT; t++) {
            for (size_t s = 0; s < R1; s++) for (size_t o = 0; o < R1; o++) { bin_t *b = &bins[l * NT + t][s * R1 + o];
                if (b->cnt) fprintf(fo, "BIN %d %d %d %zu %zu %llu %llu %llu %llu\n", l, RL[l], t, s, o, (unsigned long long)b->cnt, (unsigned long long)b->hits, (unsigned long long)b->tall, (unsigned long long)b->todd); }
            for (size_t s = 0; s < R1; s++) if (maxG[l * NT + t][s]) fprintf(fo, "MAXG %d %d %d %zu %u\n", l, RL[l], t, s, maxG[l * NT + t][s] - 1);
        }
        for (size_t a = 0; a < R1; a++) for (size_t b = 0; b < R1; b++) {
            if (jSS[l][a * R1 + b]) fprintf(fo, "JSS %d %d %zu %zu %llu\n", l, RL[l], a, b, (unsigned long long)jSS[l][a * R1 + b]);
            if (jSO[l][a * R1 + b]) fprintf(fo, "JSO %d %d %zu %zu %llu\n", l, RL[l], a, b, (unsigned long long)jSO[l][a * R1 + b]);
        }
    }
    fprintf(fo, "TROOM %d TDEEP %d\n", troom, tdeep);
    qsort(top, ntop, sizeof(top_t), cmp_top);
    for (size_t k = 0; k < ntop && k < 20000; k++) fprintf(fo, "TOP %llu %u\n", (unsigned long long)top[k].v, top[k].G);
    for (size_t k = 0; k < nd && k < 20000; k++) fprintf(fo, "DTOP %llu\n", (unsigned long long)dlist[k]);
    fclose(fo);
    return 0;
}
