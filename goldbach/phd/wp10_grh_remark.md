# WP10 — Would a proof of RH/GRH move the Goldbach-desert frontier?

Status: 2026-11-21. Prompted by a user question: does
https://alpo.ge/remark.pdf serve as inspiration for improving the
frontier? Every number below is printed by `wp10/grh_reach.py` (6 s,
reads the committed records and the Door-1 instance; nothing fitted).

## 0. What the document is

The document is a four-page personal announcement, dated 2026-11-20, of a
claimed proof of the Riemann Hypothesis and GRH (ERH "with more time"). It
says the proof was found with Claude and formalized in Lean. The Lean
source is a 14-part archive that we did not download or check here. The
mathematics appears only as narrative and a dated timeline:

- Stepanov's method moved to Z. Over a function field it uses an
  auxiliary divisor with multiplicity. Here the "multiplicity" is supplied
  by chains of theta lifts between definite unitary groups, one order per
  lift, with chain length about √X for a von Mangoldt sum of length X.
- Positivity comes from the Guinand–Weil explicit formula, with
  determinants for the Weil functional (GGP/Bessel periods), a seesaw
  argument and a relative trace formula.
- The rest is a "qN = M^k + R" sign-only argument for Weil/Deligne, an
  Iwasawa-tower step (using Behrend) and a weakened Vandiver.

Nothing in the document can be checked as written. **The analysis below
assumes the claim is true**, so the verdict does not depend on whether it
is.

## 1. Verdict: no lever moves

RH and GRH are statements of √x quality: the error term is about √x.
Every bottleneck in this programme lives at x^{o(1)} scale. The desert
window is 10^5 wide at height 10^150. The scanned progressions are
10^128 times shorter than their modulus. The closure theorem's
conditionals (H1, H2) are not statements about zeros at all.

| lever | what RH/GRH gives | measured gap |
|---|---|---|
| Search density, T(10^5) record (150 d): are the k residual complements composite? (H1) | RH: a prime in every (x − (22/25)√x ln x, x] (Carneiro–Milinovich–Soundararajan 2019, itself a Guinand–Weil positivity argument). GRH: π(x;M,a) = li(x)/φ(M) + O(√x log²x) | the RH window is 10^77.4 against a desert of g = 10^5.0, so it falls **10^72.4** short. Over the full scanned round (T = 10^10.9 terms, boost 10.4), each residual expects 10^9.35 prime terms while the GRH error is at least 10^75.0 even with all log factors dropped: **10^65.6** short. GRH starts to say something only at T ≥ 10^142.7, i.e. N of about 280 digits |
| Same, the 200-digit record below 10^200 | same | **10^97.1** (RH window) and **10^95.9** (GRH, using every progression term below 10^200) |
| Same, the 2,692-digit megagap | same | the RH window falls **10^1343** short |
| Door 1 floor via sieve (SoK §7.3, "large-sieve bound") | sieve level D = Q^{1/2}. Bombieri–Vinogradov already gives this level unconditionally for sieve remainder sums, maximum over classes included, so **for sieve purposes GRH is already free** | the cover moduli exceed √Q (613 > 316; 683 > 349), so the one-shot linear sieve has s = 0.90 and f(s) = 0. The best truncated sieve, with remainders dropped and f, F capped generously, gives **−0.46·π(Q) / −0.50·π(Q): vacuous**. Only level D = Q (beyond Elliott–Halberstam, and not implied by GRH) turns it positive, and then it certifies just **282 / 142 residuals against the 827 / 867 achieved**. So it cannot address Door 1's 0–2.6-nat question |
| Door 1 floor via positivity hierarchy (WP8 P3). This is the PDF's "positivity via determinants, more multiplicity per lift" motif in optimization form | — | the LP fails because the kill mass Σ1/(r−1) = 1.856 > 1. Bonferroni truncations of random-assignment coverage (exact value 0.880) stay ≥ 1 at depth 1 (1.856) and depth 3 (1.088). The first informative depth is 5 (0.891). A level-5 lift on the 88-modulus instance has **e₅ ≈ 10^19.2 monomials**, and even the level-2 Lasserre moment matrix has side 10^8.2. Not runnable |
| Door 2 throughput / H2 (a sub-modexp compositeness detector) | GRH changes the *correctness* status of Miller's test, not its *cost* | none. One base-2 Fermat modexp remains the primitive, and H2 is a complexity question GRH does not touch |
| Game 1 certification wall | Miller's test becomes a proof: test every prime base below 2 ln²n (Bach 1990) | **1.4 s at 150 digits**, on par with ECPP. **5.8 core-days at 2,480 digits** against ~2 h wall-clock for the repo's ECPP run at that size. **44 core-days at 4,000 digits.** It also yields *no certificate*: checking means redoing 3.9–9.5 M modexps, while an ECPP certificate verifies in minutes. Strictly worse |
| Closure theorem conditionals | — | **H1** (Hardy–Littlewood independence of shifted primes given the divisor data) is a k-tuple statement. Even full Grand RH does not imply twin primes, so H1 is untouched. **H2** is algorithmic and also untouched. §10's value-equidistribution inputs concern windows of relative width Q/X ≈ 10^−195, while √x-quality input (the best that GRH/ERH-type statements give) needs relative width ≫ X^−1/2. Untouched |
| Paper theorems (`slop/goldbach/paper.tex`) | the least prime in a progression mod m is ≪ (φ(m) log m)² (Bach–Sorenson; explicit form by Lamzouri–Li–Soundararajan) | **constants only**. Theorem `thm:dirichlet`'s g(N) ≥ (1/L − o(1)) ln N with Linnik's L ≤ 5 (Xylouris) becomes (1/2 − o(1)) ln N. `thm:lower` and `thm:coverdirichlet` gain the same factor L/2 in the implied constant. These bounds are of order ln N, while the records sit at g ≈ 303·ln N (150 digits) |

**SoK §7.3 sub-angle closed.** The "GRH-conditional explicit bound"
route is dead at record scale, however GRH's status is resolved: rows
1–4 show it falls 65–97 orders of magnitude short. A theorem of the
"make the walls theorems" type needs Hardy–Littlewood-strength input,
which is H1 itself. The upper-bound version ("every N < B has
g(N) ≤ f(B)") also stays out of reach, because it implies binary
Goldbach, which GRH does not.

## 2. The one transferable idea is methodological

The document avoids publishing an unreadable long proof and presents the
Lean development as its artifact. The analogous move here is SoK §7.8:
proof-carrying records. It is independent of the RH claim:

- The compositeness side is elementary. It consists of divisor witnesses
  and about 450 strong-base-2 witnesses of 500-bit numbers, which fit a
  kernel-checked `decide`/`norm_num` proof with GMP-backed Nat
  arithmetic.
- The primality side, for N − g, needs a checked ECPP certificate.
  Mathlib has Lucas/Pratt certificates, which need a factorization of
  p − 1 and are impractical at 150 digits. CoqPrime (Théry–Hanrot)
  already checks elliptic-curve certificates. We have not checked
  whether its tooling can ingest PARI's `primecert` format.

This raises the trust frontier, not the record frontier.

## 3. What still moves the records (unchanged)

Door 1 is the rounding gap: the 867 at Q = 122k is a locally exact
basin, and the prize is 0–2.6 nats. Door 2 is throughput: every 10× is
about +2.3 nats. That is exactly as `wp8_beyond_covering.md` §6 and
`wp9/wp9_closure_theorem.md` §14 state. Nothing in the document changes
that order, and nothing in it changes any record-table number.

## 4. Reproduction

```
pip install gmpy2 numpy          # gmpy2 optional (GMP-speed timings)
python3 goldbach/phd/wp10/grh_reach.py            # sections A–D
python3 goldbach/phd/wp10/grh_reach.py --no-bench # skip modexp timing
```

Approximations are all made in GRH's favour, or the sieve's: log factors
are dropped from error terms, remainders and ε are dropped, and f and F
are capped at 1. Each printed shortfall is therefore a lower bound on the
true one. Section C's timings come from a 2.1 GHz Xeon core (gmpy2
2.3.2 / GMP 6.3.0).
