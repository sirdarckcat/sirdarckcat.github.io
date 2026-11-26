# proof_referee_a: referee notes on COHERENT_BLOCK.md (origin/ccr-cdb2641a-5zg8un, commit 519a31d)

Verdict: the Theorem (Q = floor(c x ln^2 x ln3 x/(ln2 x)^2)) IS proved by the text, modulo classical
inputs, and "beats every A ln N ln ln N" follows. No fatal or major error. Five minor/cosmetic defects,
all repairable in one line each. One simplification: Brun-Titchmarsh (F2) is not needed at all.

## Line by line

Parameters. w = x/4; ln z = ln x ln3 x/(3 ln2 x); M = 2Q/w = 8Q/x <= 8c ln^2 x ln3 x/(ln2 x)^2, so
ln M = ln 8c + 2 ln2 x + ln4 x - 2 ln3 x <= 2 ln2 x (for c <= 1/8 as soon as ln3 x > 0). OK.
z < w and 2Q < w^2 = x^2/16 for large x. OK.

Case split. N1 in (Q,2Q] integer, q odd prime < Q: n = N1-q in [2, 2Q-3]. No prime factor in (z,w] and
n < w^2 => at most one prime factor > w, to the first power => n z-smooth, or n = a p, p > w prime,
a = n/p < 2Q/w = M, a z-smooth. Exhaustive. (The count drops "a z-smooth"; an upper bound, fine.)
Numerically confirmed on real primes (toy.py asserts ti|tii on every survivor: x=2000, x=10000).

(i) pairs <= Psi(2Q,z) pi(Q): choose n, then q, N1 = n+q. OK.

(ii) pairs <-> triples (a,p,q), a<M, w<p<=2Q/a, q in (Q-ap, 2Q-ap], q<Q; unique by unique
factorisation. Text: "Each inner interval has length at most Q, so by (F2) holds at most 2Q/ln Q primes".
  - As a deduction from (F2) "interval of length h >= 2 contains at most 2h/ln h primes" this needs a
    word: the truncated interval can have length < 2 (ap near 2Q), and h/ln h is not monotone on (1,e).
    Correct reading: enlarge the interval to length Q, count only goes up. Fine.
  - SIMPLER: q < Q always, so the inner count is <= pi(Q) <= C0 Q/ln Q by (F1). (F2) is unnecessary.
    The whole proof then uses only Chebyshev, Mertens, Rankin's trick and pi(x)-pi(x/4) >> x/ln x.
  primes p: pi(2Q/a) <= C0 (2Q/a)/ln(2Q/a) <= 2 C0 Q/(a ln w) since 2Q/a > w. OK.
  Sum over a: 1 + ln M <= 1 + 2 ln2 x. Total O(Q^2 ln2 x/ln^2 x). OK.

(F4). Psi(X,z) <= X^sigma prod_{t<=z}(1-t^-sigma)^-1 for sigma>0 (Rankin). sigma = 1 - ln u/ln z -> 1.
X^sigma = X exp(-u ln u). sum t^-sigma <= sum 1/t + ((u-1)/ln z) sum ln t/t = ln ln z + O(1) + (u-1)(1+O(1/ln z)).
u/ln z -> 0 here, so Psi(X,z) <= C X ln z exp(-u ln u + u). OK.
Exponent: u >= u0 = 3 ln2 x/ln3 x; u0(ln u0 - 1) = 3 ln2 x (1 - (ln4 x - (ln 3 - 1))/ln3 x).
So Psi(2Q,z) <= 2C Q ln z (ln x)^(-3 + 3(ln4 x - 0.0986)/ln3 x): the claimed "(ln x)^(2-o(1))" is right,
with o(1) of size 3 ln4 x/ln3 x (very slow). Sharper and uniform: L - 3 ln L + 3 ln 3 - 3 >= 0 for all L>0
(equality at L = ln3 x = 3), i.e. u0 ln u0 - u0 >= 2 ln2 x for EVERY x. So Psi(2Q,z) <= C Q ln z/ln^2 x
with no o(1), and avg(i) <= C' Q ln3 x/(ln2 x ln^3 x)... precisely avg(i)/[Q ln2 x/ln^2 x] << ln3 x/(ln2 x)^2 -> 0.
(f4.py: exponent 3.30, 2.39, 2.11, 2.00, 2.09, 2.34, 2.57 at ln3 x = 1, 1.5, 2, 3, 5, 10, 20.)
"the condition z >= (ln X)^(1+eps)" in the checks paragraph is not needed for an upper bound by Rankin's trick.

Averaging. Q integers N1; min <= mean. |L(N1)| <= C1 Q ln2 x/ln^2 x with C1 = 5 C0^2 + 1, say.
QUANTIFIERS: C1 must not depend on c. It does not (for c <= 1/8 the bounds ln M <= 2 ln2 x, ln Q >= ln x,
and (F4) are uniform once x >= x0(c)); the text says only "c fixed at the end". Minor, presentational.

Step 2. Rows are primes, so only q = t is in class 0 mod t; fullest nonzero class >= (|S|-1)/(t-1);
|S'| <= |S|(1-1/(t-1)) + 1/(t-1) <= |S|(1-1/(t-1)) + 1. Accumulated slack <= pi(z) (in fact <= sum 1/(t-1)).
(F3): prod_{3<=t<=z}(1-1/(t-1)) <= prod (1-1/t) = 2 prod_{t<=z}(1-1/t) ~ 2e^-gamma/ln z. OK.
|S| <= C2 |L|/ln z + pi(z) = 3 C1 C2 Q (ln2 x)^2/(ln^3 x ln3 x) + z. OK (1/ln z = 3 ln2 x/(ln x ln3 x)).
toy.py asserts both the greedy lemma and the "+1" recursion at every step.

Step 3. pi(x)-pi(x/4) ~ 0.75 x/ln x >= 0.7 x/ln x. The "-1" is not needed (all primes in (w,x] are odd).
"by (F1)": it is the PNT half of (F1), fine. One row per top prime, class q mod t (0 if q = t). OK.

Step 4. 3 C1 C2 c x/ln x + z <= 0.7 x/ln x - 1 with c = 1/(8 C1 C2): 0.375 < 0.7, z = x^(ln3 x/(3 ln2 x)) = x^o(1). OK.

CRT paragraph. "N < 2 prod t, ln N = (1+o(1)) x, and N - q is divisible by a modulus t < N - q".
  - The least non-negative residue is not shown to exceed Q + x, nor to have ln N = (1+o(1))x. Take
    N in [2P, 4P), P = prod_{3<=t<=x} t (least even solution + 2P). Then N - q > t for all q<Q, t<=x,
    ln N = theta(x) + O(1) = (1+o(1)) x, and N -> infinity with x (infinitely many N).
  - q = 2 is not a row: N even, N - 2 even > 2. One sentence missing.
  - only ln N <= (1+o(1)) x is needed to convert Q(x) into the N-form (Q(x) increasing).
toy.py: CRT N built, every N-q has a modulus divisor t < N-q (x=2000,Q=20000; x=10000,Q=120000 and 150000).

Rankin comparison. Rankin: gaps >= c ln X ln2 X ln4 X/(ln3 X)^2; here ln N (ln2 N)^2 ln4 N/(ln3 N)^2 = Rankin x ln2 N.
Correct ("one more logarithm" = one more factor ln2 N, i.e. ln x in the x-scale, the density of primes).

Constant-free. Q/(A x ln x) = (c/A) ln x ln3 x/(ln2 x)^2 -> infinity; in N: (c/A) ln2 N ln4 N/(ln3 N)^2 -> infinity. Follows.
The D(n) form needs x = r exactly (not "r ~ x"): apply the Theorem at x = r.
Independent support: Lean branch GoldbachGaps/CoverEveryConstant.lean, theorem eventually_exists_classes_every_constant
(every A, rows below floor(A y ln y), same convention class 0 allowed; file has no sorry/admit/axiom string; NOT compiled by me).

## Not verified
- Novelty against the literature (this is the Erdos-Rankin construction with the set of primes as target).
- Numerical values of constants; the x0 beyond which the theorem holds (irrelevant below 10^200: section 3.2).
- Sections 3 and 4 (numbers, the consequences for LIMIT_CHECK.md) are other referees' job.

## Files
run/proof_referee_a/toy.py, run/proof_referee_a/f4.py
