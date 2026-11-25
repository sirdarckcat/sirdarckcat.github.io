/* cover_price_prefix.c -- the two passes of the weighted price recursion (see cover_price_prefix.py).
 *   gcc -O2 -shared -fPIC -o libcover_price_prefix.so cover_price_prefix.c -lm        (done by the Python file on first use)
 * Backward: p = beta after the last modulus; before modulus s the price is p - (1/(s-1)) [p k'(t) - w (t k'(t) - k(t))],
 * t = min(p/w, ln(s-1)/v), k(t) = (e^{vt} - 1)/v (when t = p/w this is p - (w/(s-1)) k(p/w)).  Forward: the rows alive
 * before s, the entropy of the level ln(s-1) - (alive/(s-1)) (t k'(t) - k(t)), and the rows the tilted class strikes.
 * Returns D = sum w ln(s-1) - p_start piQ. */
#include <math.h>
double passes(int n, const int *mods, const double *vs, double piQ, double beta, const double *w, double *taus, double *ents, double *alive_end) {
    double p = beta, D = 0.0;
    for (int i = n - 1; i >= 0; i--) {
        double s = mods[i], v = vs[i], t = p / w[i], top = log(s - 1) / v;
        if (t > top) t = top;
        taus[i] = t;
        double kp = exp(v * t), k = expm1(v * t) / v;
        p = p - (p * kp - w[i] * (t * kp - k)) / (s - 1);
        D += w[i] * log(s - 1);
    }
    D -= p * piQ;
    double alive = piQ;
    for (int i = 0; i < n; i++) {
        double s = mods[i], v = vs[i], t = taus[i], mu = alive / (s - 1), kp = exp(v * t);
        ents[i] = log(s - 1) - mu * (t * kp - expm1(v * t) / v);
        alive -= mu * kp;
    }
    *alive_end = alive;
    return D;
}
