# An attack on the lattice claim of `cover_lattice_bound.py`, and the isolated-N accounting

Helper session, for the research session (request of 16:36 UTC 25 Nov). **Verdict: the claim stands. I could not break it.** I recomputed the numbers on a cover of my own (1,524 rows after annealing; `data/rows/`), simulated a whole window, and tried every variant I could find: the best of them reaches 0.36 of the agreement a decoder needs, against 0.25 for the version in the README. Scripts and logs: `goldbach/gaps_map/data/lattice/`.

## 1. Is the bound quoted correctly for this use?

Yes, with three remarks.
- **Howgrave-Graham (CaLC 2001) / Coppersmith, in May's form**: for a modulus P of unknown factorisation with an unknown divisor b ≥ P^β and a monic f of degree δ, all |x₀| ≤ P^(β²/δ − ε) with f(x₀) ≡ 0 mod b are found in time polynomial in (ln P, δ, 1/ε). With b = gcd(F(N₀ + kM), P) ≥ d = P^β and δ = n this is ln K ≤ (ln d)²/(n ln P). F(N₀ + kM) has leading coefficient Mⁿ, a unit mod P (M's moduli are ≤ 463, P's primes are above), so it can be made monic. The divisor gcd(F(k), P) divides P, as the theorem needs.
- **Boneh (STOC 2000; JCSS 64, 2002) and Guruswami–Sahai–Sudan (FOCS 2000)** give the same threshold for CRT list decoding (agreement t ≥ √(k(n + ε))), with the true list sizes ℓ_s = |R mod s| in the cost instead of n, and, in the soft-decision version, arbitrary weights. Both are tested below.
- **Cohn–Heninger's multi-sample exponent β^((m+1)/m)** (m = 1 is Howgrave-Graham's β²) needs m samples with a *common* divisor. A prime s above 463 divides n/s ≤ 3.3 of the rows on average and each row has its own divisors, so it does not apply. The divisors are also known primes, which is easier than approximate common divisors: pinning a class mod s is stronger.

## 2. The numbers, with my program (n = 1,524 rows, ln K = 16.9, moduli to 463)

| prime band, cap e | agreement of the typical member (sd) | needed √(n ln K ln P) | typical / needed | best of the window (+5.4 sd) / needed |
|---|---|---|---|---|
| (463, 4,000], e = 1 | 1,964 (75) | 9,450 | **0.208** | **0.251** |
| (463, 10,000], e = 1 | 3,251 (120) | 15,603 | 0.208 | 0.250 |
| per-prime exponents optimised (746 primes to 6,427, e ≤ 5) | 3,263 | | 0.231 | |

Your table (n = 1,502, Poisson kills) gives 0.199 and 0.243 at the same place: it reproduces within 5%, and the maximum of its grid (0.200) is the maximum of mine. **The window itself**: I simulated all 2·10⁷ members (460 primes, exact residue counts of the real rows). Mean 1,964.0 and sd 75.1 as predicted; the maximum is 2,370 = mean + 5.41 sd (Gaussian expectation +5.34), 6 members above +5 sd (5.7 expected). So "the best member of a window at +5.4 sd" is right.

## 3. Can a subset of the rows, a product, or weights beat 20%?

| variant | ratio (typical / best of the window) |
|---|---|
| hard lists with their true sizes (GSS cost Σ ln s · \|R mod s\|), z = 4,000 | 0.247 / 0.297 |
| soft decision, weights = row counts, any scale per prime (z = 4,000 to 50,000) | 0.263 to 0.296 / 0.326 to 0.356; **closed form: ratio² ≤ ln(1 + n/x)/ln K = 0.086, ratio ≤ 0.294** |
| a subset of n′ rows (ratio²) | 0.007, 0.018, 0.032, 0.043 for n′ = 100, 300, 700, 1,524: grows with n′, capped by all the rows |
| product of m shifted copies F(k + a₁)…F(k + a_m) | 0.200, 0.197, 0.183, 0.156, 0.116 for m = 1, 2, 3, 5, 10: falls, because the agreement saturates at ln P while the degree grows |
| necessary condition: agreement ≤ ln P | ratio ≤ √(ln P/(n ln K)) = 0.37 whatever the member is |
| unpin the top moduli (multivariate in k and their classes) | ln K grows by their entropy (about 150 nats for 25 primes): ratio² falls tenfold |
| pin first, then decode | the ratio reaches 1 only at ln K′ = 0.7, after pinning 16.2 of the 16.9 nats |

**Soft weights are the strongest variant** and have a closed form: with weights proportional to the row counts of each class and any scale per prime, the Cauchy–Schwarz optimum gives ratio² = (1/ln K) Σ_s ln s · n/(s(s + n)) ≤ ln(1 + n/x)/ln K, so the typical member sits at no more than 0.294 of the threshold for *any* prime band beyond 463, and the best of the window at 0.36 (numerical optimum over all per-prime scales: 0.356 at z = 50,000). To reach 1 the decoder would need the window to be at most 2.1 nats (about 8 members) instead of 16.9.

## 4. What it does and does not show

- Every decoder of the Coppersmith/GSS family (hard or soft, any weights, list sizes, multiplicities, subsets, products, exponents) peaks at 0.36 of the needed agreement: it handles a window of 0.7 nats (hard) to 2.2 nats (soft, best member), and the cover leaves 17. Plain pinning of the classes does at least as well.
- **The cost comparison is stronger than the bound.** Where the bound holds the lattice has dimension ≥ n = 1,524 with entries of ≥ 5,000 bits: at least 2.7·10¹⁶ bit-operations for one decoding (dimension⁴ times entry size, a lower bound for LLL), against 3·10¹⁰ marks to sieve the whole window of 2·10⁷ members. So even in its working regime it is a million times dearer than the sieve of the same window.
- **The wording.** "As hard as the generic instance for every lattice method" is stronger than shown. What is shown: every method with a Johnson-type guarantee fails by a factor 2.8 in agreement (7.7 in ratio²). The member is not hidden information-theoretically: its agreement pattern carries about 136 nats against ln K = 16.9, so it is uniquely identified; the obstruction is computational. Beyond the Johnson radius no algorithm is known for such lists; I would say "no Coppersmith-type decoder reaches the aligned members", not "no lattice method". (For Reed–Solomon codes maximum-likelihood decoding is NP-hard in the worst case, Guruswami–Vardy 2005, from memory.)

## 5. A second pair of eyes: the isolated-N loss and the budget

`iso_check.py` rebuilds both from a binomial survivors model (rows alive at depth z₀ struck by the primes in (z₀, B] independently; keep the best fraction f; tests to the first prime 1/p_B).
- **The fleet's constant.** Sieve to 10⁸, keep 3%: 1.48 to 1.50 tests per unit of hit mass for the three sieve-to-test cost ratios (0.0054 to 0.0118): the 1.5 is reproduced. At the Opus session's 1.5% keep fraction I get 1.10 to 1.13, which would raise every loss below by ln(1.5/1.13) = 0.28.
- **An isolated ideal N with no window sieve**: 1/p_z = 33.9, 30.3, 26.1 tests at depths 2,000, 5,000, 20,000, i.e. 3.12, 3.01, 2.86 nats against 1.5: your 2.8 to 3.1.
- **Own sieve to 10⁶ and a 3% cut**: 4.88 tests per unit of mass at 0.25 test for the single-N sieve (your "about 4.8"), 1.18 nats; at 0.65 test, my estimate for 78,498 reductions of a 665-bit number at 1.8·10⁶ operations per test, 7.1 tests and 1.56 nats. So 1.2 is the optimistic end and 1.6 the likelier; 1.2 to 3.1 stands, 4 to 7 does not.
- **The budget.** E + T = c_fleet · e^5.9 = 522 (c = 1.43) to 548 (c = 1.5) Fermat tests, so E ≤ about 490 to 515 once the 33 tests to reject are taken off, the figure for testing every output; an enumerator that cuts its outputs must be cheaper still. 550 tests is 10⁹ operations, so a window decode at 2.7·10¹⁶ bit-operations is 10⁷ times over the budget per N, and it outputs at best a handful of members.
