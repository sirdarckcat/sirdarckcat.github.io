// Exact count, over F_9 = F_3[i]/(i^2+1): among the monic irreducible Q of degree d (d prime, d != 3),
// how many have a derivative Q' all of whose irreducible factors have degree <= J.
// Elements a + b i are coded a + 3 b.  No external library.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
static unsigned char ADD[9][9], MUL[9][9], NEG[9], INV[9];
typedef struct { int deg; unsigned char c[20]; } poly;   // deg = -1 for 0
static void init(void) {
    for (int x = 0; x < 9; x++) for (int y = 0; y < 9; y++) {
        int a = x % 3, b = x / 3, c = y % 3, d = y / 3;
        ADD[x][y] = (a + c) % 3 + 3 * ((b + d) % 3);
        int re = (a * c + 2 * b * d) % 3, im = (a * d + b * c) % 3;   // i^2 = -1 = 2
        MUL[x][y] = re + 3 * im;
    }
    for (int x = 0; x < 9; x++) { for (int y = 0; y < 9; y++) { if (ADD[x][y] == 0) NEG[x] = y; if (x && MUL[x][y] == 1) INV[x] = y; } }
}
static void norm(poly *p) { while (p->deg >= 0 && p->c[p->deg] == 0) p->deg--; }
static void pmod(poly *a, const poly *m) {            // a mod m, m != 0
    unsigned char li = INV[m->c[m->deg]];
    while (a->deg >= m->deg) {
        unsigned char f = MUL[a->c[a->deg]][li];
        if (f) { unsigned char nf = NEG[f]; int sh = a->deg - m->deg;
            for (int i = 0; i <= m->deg; i++) a->c[i + sh] = ADD[a->c[i + sh]][MUL[nf][m->c[i]]]; }
        a->deg--; norm(a);
    }
}
static void pmulmod(poly *r, const poly *a, const poly *b, const poly *m) {
    poly t; memset(&t, 0, sizeof t);
    if (a->deg < 0 || b->deg < 0) { r->deg = -1; return; }
    t.deg = a->deg + b->deg;
    for (int i = 0; i <= a->deg; i++) if (a->c[i]) for (int j = 0; j <= b->deg; j++)
        t.c[i + j] = ADD[t.c[i + j]][MUL[a->c[i]][b->c[j]]];
    norm(&t); pmod(&t, m); *r = t;
}
static void frob(poly *r, const poly *h, const poly *m) {   // h^9 mod m
    poly h2, h3, h6; pmulmod(&h2, h, h, m); pmulmod(&h3, &h2, h, m); pmulmod(&h6, &h3, &h3, m); pmulmod(r, &h6, &h3, m);
}
static void pgcd(poly *g, poly a, poly b) { while (b.deg >= 0) { pmod(&a, &b); poly t = a; a = b; b = t; } *g = a; }
static void pdivexact(poly *q, poly a, const poly *b) {   // a / b, exact
    poly r; memset(&r, 0, sizeof r); r.deg = a.deg - b->deg; unsigned char li = INV[b->c[b->deg]];
    while (a.deg >= b->deg) { unsigned char f = MUL[a.c[a.deg]][li]; int sh = a.deg - b->deg; r.c[sh] = f;
        unsigned char nf = NEG[f]; for (int i = 0; i <= b->deg; i++) a.c[i + sh] = ADD[a.c[i + sh]][MUL[nf][b->c[i]]];
        a.deg--; norm(&a); }
    *q = r;
}
static int is_smooth(poly D, int J) {     // every irreducible factor of D has degree <= J
    for (int k = 1; k <= J; k++) {
        for (;;) {
            if (D.deg <= 0) return 1;
            poly x; memset(&x, 0, sizeof x); x.deg = 1; x.c[1] = 1; pmod(&x, &D);
            poly h = x; for (int t = 0; t < k; t++) frob(&h, &h, &D);        // x^(9^k) mod D
            poly diff = h; int md = diff.deg > x.deg ? diff.deg : x.deg; diff.deg = md;
            for (int i = 0; i <= md; i++) diff.c[i] = ADD[i <= h.deg ? h.c[i] : 0][NEG[i <= x.deg ? x.c[i] : 0]];
            norm(&diff);
            poly g; if (diff.deg < 0) g = D; else pgcd(&g, D, diff);
            if (g.deg <= 0) break;
            poly q; pdivexact(&q, D, &g); D = q;
        }
    }
    return D.deg <= 0;
}
int main(int argc, char **argv) {
    init(); int d = atoi(argv[1]), J = atoi(argv[2]);
    long total = 1; for (int i = 0; i < d; i++) total *= 9;
    long irr = 0, smooth = 0;
    if (argc > 3) {
        long cnt = 0;
        #pragma omp parallel for reduction(+:cnt) schedule(dynamic, 4096)
        for (long idx = 0; idx < total; idx++) {
            poly Q; memset(&Q, 0, sizeof Q); Q.deg = d; Q.c[d] = 1; long t = idx; for (int i = 0; i < d; i++) { Q.c[i] = t % 9; t /= 9; }
            if (is_smooth(Q, J)) cnt++;
        }
        printf("self-test: %ld of the %ld monic polynomials of degree %d over F_9 are %d-smooth\n", cnt, total, d, J);
        return 0;
    }
    #pragma omp parallel for reduction(+:irr,smooth) schedule(dynamic, 4096)
    for (long idx = 0; idx < total; idx++) {
        poly Q; memset(&Q, 0, sizeof Q); Q.deg = d; Q.c[d] = 1; long t = idx; for (int i = 0; i < d; i++) { Q.c[i] = t % 9; t /= 9; }
        int root = 0;                                        // a root in F_9?
        for (int a = 0; a < 9 && !root; a++) { unsigned char v = 0; for (int i = d; i >= 0; i--) v = ADD[MUL[v][a]][Q.c[i]]; if (v == 0) root = 1; }
        if (root) continue;
        poly x; memset(&x, 0, sizeof x); x.deg = 1; x.c[1] = 1;
        poly h = x; for (int k = 0; k < d; k++) frob(&h, &h, &Q);   // x^(9^d) mod Q; d prime, so irreducible iff = x
        if (!(h.deg == 1 && h.c[1] == 1 && h.c[0] == 0)) continue;
        irr++;
        poly D; memset(&D, 0, sizeof D); D.deg = d - 1;
        for (int i = 1; i <= d; i++) { unsigned char m = i % 3; D.c[i - 1] = MUL[m][Q.c[i]]; }   // i * a_i, i reduced mod 3
        norm(&D);
        if (is_smooth(D, J)) smooth++;
    }
    printf("F_9, degree %d: %ld monic irreducible Q; %ld of them have a %d-smooth derivative (%.4f)\n", d, irr, smooth, J, (double)smooth / irr);
    return 0;
}
