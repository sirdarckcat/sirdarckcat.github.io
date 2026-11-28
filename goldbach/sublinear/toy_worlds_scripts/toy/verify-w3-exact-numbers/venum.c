// venum.c -- independent verifier enumeration for Goldbach in F_q[x], q in {3,5,7,9}
// ./venum q n outprefix [-dump] [-list file] [-L R1 R2 ...]
// Monic degree-m polynomial <-> index v = sum_{k<m} c_k q^k. q=9: label a+3b = a+b*i, i^2=-1.
// Sieve: for each irreducible P (deg d <= m/2) enumerate all multiples P*b by an additive odometer on chunked digit vectors.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int q, p, f, n, k, B;
static uint8_t fadd[9][9], fsub[9][9], fmul[9][9];
static uint16_t *ADDT, *SUBT;
static uint64_t pw[40];
static uint8_t *comp[40];           // degrees < n : 1 = composite
static uint8_t *A, *C;              // degree n
static int NT; static int Kt[8]; static char Kname[8][64];
static int troom, tlin, tdeg2, tdeg3;
// list of small irreducibles
static int nsm = 0, smcap = 0; static uint32_t *sm_v; static uint8_t *sm_d;
static void add_sm(uint32_t v, int d) { if (nsm == smcap) { smcap = smcap ? 2 * smcap : 1024; sm_v = realloc(sm_v, 4 * smcap); sm_d = realloc(sm_d, smcap); } sm_v[nsm] = v; sm_d[nsm] = d; nsm++; }
static void to_chunks(const uint8_t *dig, uint16_t *ch) { for (int c = 0; c < 4; c++) { int x = 0; for (int t = k - 1; t >= 0; t--) x = x * q + dig[c * k + t]; ch[c] = (uint16_t)x; } }
static uint16_t W[80][4]; static uint16_t cur[4];
static int smode, sm_m, sdeg, scode;
static inline void leaf(void) {
    uint64_t v = cur[0] + (uint64_t)B * (cur[1] + (uint64_t)B * (cur[2] + (uint64_t)B * cur[3]));
    if (smode == 0) comp[sm_m][v] = 1;
    else if (smode == 1) { A[v] = (uint8_t)((A[v] + sdeg) ^ 0x20); if (C && C[v] == 0) C[v] = (uint8_t)(scode + 1); }
    else A[v] |= 0x40;
}
static void rec(int jj) {
    for (int t = 0; t < p; t++) {
        if (jj == 0) leaf(); else rec(jj - 1);
        for (int c = 0; c < 4; c++) cur[c] = ADDT[(int)cur[c] * B + W[jj][c]];
    }
}
// multiples of monic P (digits Pd[0..d], Pd[d]=1) of degree m
static void sieve_multiples(const uint8_t *Pd, int d, int m, int mode) {
    int e = m - d; uint8_t dig[64];
    smode = mode; sm_m = m;
    memset(dig, 0, sizeof dig); for (int t = 0; t < d; t++) dig[e + t] = Pd[t];
    to_chunks(dig, cur);
    for (int j = 0; j < e; j++) for (int s = 0; s < f; s++) {
        int w = (s == 0) ? 1 : 3;   // basis element 1 or i (label 3)
        memset(dig, 0, sizeof dig); for (int t = 0; t <= d; t++) dig[j + t] = fmul[w][Pd[t]];
        to_chunks(dig, W[j * f + s]);
    }
    if (e == 0) leaf(); else rec(e * f - 1);
}
static void digits(uint64_t v, int d, uint8_t *dig) { for (int t = 0; t < d; t++) { dig[t] = v % q; v /= q; } dig[d] = 1; }

static uint64_t nrows; static uint16_t *rowc; static uint8_t *rownch, *rowdeg; static uint32_t *rowv; static uint64_t rows_below[40];
static uint8_t *T;
static uint64_t slowG(uint64_t v, int *cntS, int *cntO, int R) {   // generic; optional counts over first R rows by code
    uint16_t nc[4]; uint64_t x = v; for (int c = 0; c < 4; c++) { nc[c] = x % B; x /= B; }
    uint64_t G = nrows; int hit = 0;
    for (uint64_t i = 0; i < nrows; i++) {
        const uint16_t *qc = rowc + 4 * i;
        uint64_t idx = SUBT[(int)nc[0] * B + qc[0]] + (uint64_t)B * (SUBT[(int)nc[1] * B + qc[1]] + (uint64_t)B * (SUBT[(int)nc[2] * B + qc[2]] + (uint64_t)B * SUBT[(int)nc[3] * B + qc[3]]));
        uint8_t b = T[idx];
        if (cntS && i < (uint64_t)R) { cntS[b & 7]++; if (b & 0x40) cntO[b & 7]++; }
        if ((b & 0x80) && !hit) { hit = 1; G = i; }
        if (hit && (!cntS || i + 1 >= (uint64_t)R)) break;
    }
    return G;
}
typedef struct { uint64_t cnt, hits, tall, todd; } bin_t;
int main(int argc, char **argv) {
    if (argc < 4) return 1;
    q = atoi(argv[1]); n = atoi(argv[2]); const char *pre = argv[3];
    int dump = 0; const char *listfn = NULL; int L = 0; int RL[16];
    for (int a = 4; a < argc; a++) {
        if (!strcmp(argv[a], "-dump")) dump = 1;
        else if (!strcmp(argv[a], "-list")) listfn = argv[++a];
        else if (!strcmp(argv[a], "-L")) { for (a++; a < argc; a++) RL[L++] = atoi(argv[a]); }
    }
    p = (q == 9) ? 3 : q; f = (q == 9) ? 2 : 1;
    k = (q == 3) ? 6 : (q == 5) ? 4 : 3; B = 1; for (int t = 0; t < k; t++) B *= q;
    if (4 * k < n || n > 31) return 2;
    for (int a = 0; a < q; a++) for (int b = 0; b < q; b++) {
        if (q != 9) { fadd[a][b] = (a + b) % q; fsub[a][b] = (a + q - b) % q; fmul[a][b] = (a * b) % q; }
        else { int a0 = a % 3, a1 = a / 3, b0 = b % 3, b1 = b / 3;
            fadd[a][b] = (a0 + b0) % 3 + 3 * ((a1 + b1) % 3); fsub[a][b] = (a0 + 3 - b0) % 3 + 3 * ((a1 + 3 - b1) % 3);
            fmul[a][b] = (a0 * b0 + 2 * a1 * b1) % 3 + 3 * ((a0 * b1 + a1 * b0) % 3); }
    }
    ADDT = malloc(2 * (size_t)B * B); SUBT = malloc(2 * (size_t)B * B);
    for (int a = 0; a < B; a++) for (int b = 0; b < B; b++) {
        int x = a, y = b, ra = 0, rs = 0, m = 1;
        for (int t = 0; t < k; t++) { ra += fadd[x % q][y % q] * m; rs += fsub[x % q][y % q] * m; x /= q; y /= q; m *= q; }
        ADDT[(size_t)a * B + b] = ra; SUBT[(size_t)a * B + b] = rs;
    }
    pw[0] = 1; for (int t = 1; t < 40; t++) pw[t] = pw[t - 1] * q;
    for (int m = 1; m < n; m++) comp[m] = calloc(pw[m], 1);
    A = calloc(pw[n], 1); if (L) C = calloc(pw[n], 1);
    uint8_t Pd[64];
    // degrees < n
    for (int m = 1; m < n; m++) {
        for (int r = 0; r < nsm && 2 * sm_d[r] <= m; r++) { digits(sm_v[r], sm_d[r], Pd); sieve_multiples(Pd, sm_d[r], m, 0); }
        if (2 * m <= n) for (uint64_t v = 0; v < pw[m]; v++) if (!comp[m][v]) add_sm((uint32_t)v, m);
    }
    // thresholds
    int I[4] = {0, 0, 0, 0}; for (int r = 0; r < nsm; r++) if (sm_d[r] <= 3) I[sm_d[r]]++;
    int room = 0, tot = 0; while (room < nsm && tot + sm_d[room] <= n) tot += sm_d[room++];
    { int cand[5] = {0, I[1], room, I[1] + I[2], I[1] + I[2] + I[3]}; const char *cn[5] = {"none", "lin", "room", "deg2", "deg3"};
      int idx[5] = {0, 1, 2, 3, 4};
      for (int a = 0; a < 5; a++) for (int b = a + 1; b < 5; b++) if (cand[idx[b]] < cand[idx[a]]) { int t = idx[a]; idx[a] = idx[b]; idx[b] = t; }
      NT = 0; int where[5];
      for (int a = 0; a < 5; a++) { int c = idx[a];
          if (NT && Kt[NT - 1] == cand[c]) { strcat(Kname[NT - 1], "="); strcat(Kname[NT - 1], cn[c]); }
          else { Kt[NT] = cand[c]; strcpy(Kname[NT], cn[c]); NT++; }
          where[c] = NT - 1; }
      tlin = where[1]; troom = where[2]; tdeg2 = where[3]; tdeg3 = where[4]; }
    // degree n
    for (int r = 0; r < nsm; r++) {
        int d = sm_d[r]; digits(sm_v[r], d, Pd);
        sdeg = d; scode = 0; for (int t = 0; t < NT; t++) if (r >= Kt[t]) scode++;
        sieve_multiples(Pd, d, n, 1);
        uint8_t P2[64]; memset(P2, 0, sizeof P2);
        for (int a = 0; a <= d; a++) for (int b = 0; b <= d; b++) P2[a + b] = fadd[P2[a + b]][fmul[Pd[a]][Pd[b]]];
        sieve_multiples(P2, 2 * d, n, 2);
    }
    T = A; uint64_t nirr = 0, nodd = 0, nsqf = 0; uint64_t rough[8] = {0}, roughodd[8] = {0};
    for (uint64_t v = 0; v < pw[n]; v++) {
        int a = A[v], ds = a & 31, par = (a >> 5) & 1, nsq = (a >> 6) & 1;
        int irr = (ds == 0); int odd = (!nsq) && ((par ^ (ds < n)) & 1);
        int code = irr ? NT : (C ? C[v] - 1 : 0);
        if (irr) nirr++; if (odd) nodd++; if (!nsq) nsqf++;
        if (C) for (int t = 0; t < code; t++) { rough[t]++; if (odd) roughodd[t]++; }
        T[v] = (uint8_t)((irr << 7) | (odd << 6) | code);
    }
    if (C) { free(C); }
    // rows
    nrows = 0; for (int d = 1; d < n; d++) { rows_below[d] = nrows; for (uint64_t v = 0; v < pw[d]; v++) if (!comp[d][v]) nrows++; } rows_below[n] = nrows;
    rowc = malloc(8 * nrows); rownch = malloc(nrows); rowdeg = malloc(nrows); rowv = malloc(4 * nrows);
    { uint64_t r = 0; uint8_t dig[64];
      for (int d = 1; d < n; d++) for (uint64_t v = 0; v < pw[d]; v++) if (!comp[d][v]) {
          memset(dig, 0, sizeof dig); digits(v, d, dig); to_chunks(dig, rowc + 4 * r); rownch[r] = d / k + 1; rowdeg[r] = d; rowv[r] = (uint32_t)v; r++; } }
    char fn[600]; snprintf(fn, sizeof fn, "%s.txt", pre); FILE *fo = fopen(fn, "w");
    fprintf(fo, "q %d n %d total %llu irr_n %llu odd %llu squarefree %llu nrows %llu\n", q, n, (unsigned long long)pw[n], (unsigned long long)nirr, (unsigned long long)nodd, (unsigned long long)nsqf, (unsigned long long)nrows);
    fprintf(fo, "rows_below"); for (int d = 1; d <= n; d++) fprintf(fo, " %llu", (unsigned long long)rows_below[d]); fprintf(fo, "\n");
    fprintf(fo, "NT %d troom %d tlin %d tdeg2 %d tdeg3 %d room_totdeg %d\n", NT, troom, tlin, tdeg2, tdeg3, tot);
    if (L) for (int t = 0; t < NT; t++) fprintf(fo, "THR %d K %d %s rough %llu roughodd %llu\n", t, Kt[t], Kname[t], (unsigned long long)rough[t], (unsigned long long)roughodd[t]);
    fflush(fo);
    // main loop
    int GH = (int)(nrows < 8191 ? nrows + 1 : 8192);
    uint64_t *gh = calloc(GH, 8), *gh0 = calloc(GH, 8); uint64_t dh[40] = {0}, dh0[40] = {0};
    bin_t **bins = NULL; uint32_t **mg = NULL; uint64_t **jss = NULL;
    if (L) { bins = malloc(sizeof(void *) * L * NT); mg = malloc(sizeof(void *) * L * NT); jss = malloc(sizeof(void *) * L);
        for (int l = 0; l < L; l++) { size_t R1 = RL[l] + 1; for (int t = 0; t < NT; t++) { bins[l * NT + t] = calloc(R1 * R1, sizeof(bin_t)); mg[l * NT + t] = calloc(R1, 4); } jss[l] = calloc(R1 * R1, 8); } }
    uint16_t *gd = NULL; if (dump) gd = malloc(2 * pw[n]);
    #define NTOP 400
    uint64_t topv[NTOP + 1]; uint32_t topg[NTOP + 1]; int ntop = 0;
    uint16_t nc[4] = {0, 0, 0, 0}; uint8_t Nd[40]; memset(Nd, 0, sizeof Nd);
    for (uint64_t v = 0; v < pw[n]; v++) {
        const uint16_t *S0 = SUBT + (size_t)nc[0] * B, *S1 = SUBT + (size_t)nc[1] * B, *S2 = SUBT + (size_t)nc[2] * B, *S3 = SUBT + (size_t)nc[3] * B;
        uint64_t h1 = v - nc[0], h2 = h1 - (uint64_t)B * nc[1], h3 = h2 - (uint64_t)B * B * nc[2];
        uint64_t G = nrows, i = 0; int hit = 0;
        #define IDX(i_, out) { const uint16_t *qc = rowc + 4 * (i_); switch (rownch[i_]) { \
            case 1: out = h1 + S0[qc[0]]; break; \
            case 2: out = h2 + S0[qc[0]] + (uint64_t)B * S1[qc[1]]; break; \
            case 3: out = h3 + S0[qc[0]] + (uint64_t)B * (S1[qc[1]] + (uint64_t)B * S2[qc[2]]); break; \
            default: out = S0[qc[0]] + (uint64_t)B * (S1[qc[1]] + (uint64_t)B * (S2[qc[2]] + (uint64_t)B * S3[qc[3]])); } }
        if (L) {
            uint16_t cnt[16], snap[16]; memset(cnt, 0, sizeof cnt); uint16_t sroom_l[16];
            for (int l = 0; l < L; l++) {
                for (; i < (uint64_t)RL[l]; i++) {
                    uint64_t x; IDX(i, x); uint8_t b = T[x]; cnt[(b & 7) | ((b >> 3) & 8)]++;
                    if ((b & 0x80) && !hit) { hit = 1; G = i; memcpy(snap, cnt, sizeof cnt); }
                }
                size_t R1 = RL[l] + 1; unsigned s = 0, o = 0, ts = 0, to = 0; unsigned sv[8], ov[8];
                for (int t = NT - 1; t >= 0; t--) {
                    s += cnt[t + 1] + cnt[t + 9]; o += cnt[t + 9];
                    if (hit) { ts += snap[t + 1] + snap[t + 9]; to += snap[t + 9]; } else { ts = s; to = o; }
                    sv[t] = s; ov[t] = o;
                    bin_t *b = &bins[l * NT + t][s * R1 + o]; b->cnt++; if (!hit) b->hits++; b->tall += ts; b->todd += to;
                }
                sroom_l[l] = sv[troom]; (void)ov;
                jss[l][sv[troom] * R1 + sv[NT - 1]]++;
                // remember s for maxG: store in sv arrays -> handled below via recompute
                for (int t = 0; t < NT; t++) cnt[0] = cnt[0]; 
                // stash
                for (int t = 0; t < NT; t++) { /* maxG needs final G; store s in a temp */ }
                // temp store
                static uint16_t stash[16][8]; for (int t = 0; t < NT; t++) stash[l][t] = sv[t];
                if (l == L - 1) {
                    if (!hit) for (; i < nrows; i++) { uint64_t x; IDX(i, x); if (T[x] & 0x80) { hit = 1; G = i; break; } }
                    for (int l2 = 0; l2 < L; l2++) for (int t = 0; t < NT; t++) { uint32_t *m = &mg[l2 * NT + t][stash[l2][t]]; if (G + 1 > *m) *m = (uint32_t)(G + 1); }
                }
            }
            (void)sroom_l;
        } else {
            for (; i < nrows; i++) { uint64_t x; IDX(i, x); if (T[x] & 0x80) { G = i; break; } }
        }
        int D = (G < nrows) ? rowdeg[G] : n;
        int z = 1; for (int t = 1; t < n; t++) if (t % p && Nd[t]) { z = 0; break; }   // N' = 0 ?
        uint64_t Gc = G < (uint64_t)GH ? G : (uint64_t)GH - 1;
        gh[Gc]++; dh[D]++; if (z) { gh0[Gc]++; dh0[D]++; }
        if (gd) gd[v] = (uint16_t)(G > 65535 ? 65535 : G);
        if (ntop < NTOP || G > topg[ntop - 1]) {
            int j = ntop < NTOP ? ntop++ : NTOP - 1;
            while (j > 0 && topg[j - 1] < G) { topg[j] = topg[j - 1]; topv[j] = topv[j - 1]; j--; }
            topg[j] = (uint32_t)G; topv[j] = v;
        }
        // increment
        for (int t = 0; t < n; t++) { if (++Nd[t] < q) break; Nd[t] = 0; }
        if (++nc[0] == B) { nc[0] = 0; if (++nc[1] == B) { nc[1] = 0; if (++nc[2] == B) { nc[2] = 0; ++nc[3]; } } }
    }
    for (int g = 0; g < GH; g++) if (gh[g]) fprintf(fo, "GH %d %llu %llu\n", g, (unsigned long long)gh[g], (unsigned long long)gh0[g]);
    for (int d = 0; d <= n; d++) if (dh[d]) fprintf(fo, "DH %d %llu %llu\n", d, (unsigned long long)dh[d], (unsigned long long)dh0[d]);
    for (int j = 0; j < ntop; j++) fprintf(fo, "TOP %llu %u\n", (unsigned long long)topv[j], topg[j]);
    for (int l = 0; l < L; l++) { size_t R1 = RL[l] + 1;
        for (int t = 0; t < NT; t++) {
            for (size_t s = 0; s < R1; s++) for (size_t o = 0; o < R1; o++) { bin_t *b = &bins[l * NT + t][s * R1 + o];
                if (b->cnt) fprintf(fo, "BIN %d %d %d %zu %zu %llu %llu %llu %llu\n", l, RL[l], t, s, o, (unsigned long long)b->cnt, (unsigned long long)b->hits, (unsigned long long)b->tall, (unsigned long long)b->todd); }
            for (size_t s = 0; s < R1; s++) if (mg[l * NT + t][s]) fprintf(fo, "MAXG %d %d %d %zu %u\n", l, RL[l], t, s, mg[l * NT + t][s] - 1);
        }
        for (size_t a = 0; a < R1; a++) for (size_t b = 0; b < R1; b++) if (jss[l][a * R1 + b]) fprintf(fo, "JSS %d %d %zu %zu %llu\n", l, RL[l], a, b, (unsigned long long)jss[l][a * R1 + b]);
    }
    if (listfn) { FILE *fl = fopen(listfn, "r"); unsigned long long v; char tag[64];
        while (fl && fscanf(fl, "%63s %llu", tag, &v) == 2) {
            int cs[8] = {0}, co[8] = {0}; int R = L ? RL[L - 1] : 0;
            uint64_t G = slowG(v, L ? cs : NULL, L ? co : NULL, R);
            fprintf(fo, "LIST %s %llu G %llu D %d", tag, v, (unsigned long long)G, G < nrows ? rowdeg[G] : n);
            if (L) { int s = 0, o = 0; fprintf(fo, " R %d so", R); int sv[8], ov[8]; for (int t = NT - 1; t >= 0; t--) { s += cs[t + 1]; o += co[t + 1]; sv[t] = s; ov[t] = o; } for (int t = 0; t < NT; t++) fprintf(fo, " %d:%d", sv[t], ov[t]); }
            fprintf(fo, "\n"); }
        if (fl) fclose(fl); }
    fclose(fo);
    if (gd) { snprintf(fn, sizeof fn, "%s.g16", pre); FILE *fb = fopen(fn, "wb"); fwrite(gd, 2, pw[n], fb); fclose(fb); }
    return 0;
}
