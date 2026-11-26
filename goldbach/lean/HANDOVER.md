# Handover: least Goldbach summands, checked by Lean

For an even number N, its *least Goldbach summand* g(N) is the smallest prime p such that N − p is also prime. For
example g(98) = 19: 98 − 3, 98 − 5, …, 98 − 17 are all composite and 98 − 19 = 79 is prime. Goldbach's conjecture says
that g(N) always exists. The project asked how large g(N) can be when N has at most 200 digits.

This directory is a library for Lean 4, a *proof assistant*: a program with a small core, the *kernel*, that checks
every step of a proof. Everything listed below has passed that check. Files are under `GoldbachGaps/`, and a theorem
called `x` there has the full name `GoldbachGaps.x`. The root file `GoldbachGaps.lean` has a longer map of every
file.

## What is proved

**The records.** Each record file contains the number N itself and a certificate that the kernel replays. "Exactly"
means both halves are proved: N − g is prime, through a primality certificate, and N − p is composite for every
prime p below g.

| N | g(N) | theorem (file) |
|---|---|---|
| 200 digits, starting 953471068180 (the record as of 26 November) | exactly 160,357 | `exists_lt_ten_pow_200_least_summand_160357` (`Records.lean`; the number is in `Record200_g160357.lean`) |
| three earlier 200-digit records | exactly 158,209, 157,837 and 146,191 | `exists_lt_ten_pow_200_least_summand_158209` and the same with `157837`, `146191` |
| three 199-digit records | exactly 133,981, 125,269 and 119,419 | `exists_lt_ten_pow_199_least_summand_133981`, `…_125269`, `exists_lt_ten_pow_199_least_summand_eq` |
| a 150-digit record | exactly 104,527 | `exists_lt_ten_pow_150_least_summand_gt` (the statement says "more than 100,000") |
| 111308182437581302718351168 (27 digits) | exactly 11,467 | `closeness_27digit_11467` (`Closeness.lean`) |
| 10492156463590001369800256, 10621579671744600348710546, 5471513744131872011405456 | exactly 10,303, 10,159, 10,357 | `closeness_26digit_10303`, `closeness_26digit_10159`, `closeness_25digit_10357` |
| 54284735534856910692542, 30625623272505310405982, 35505990484772441527442 (23 digits) | exactly 11,701, 10,729, 10,771 | `Record23_g11701.record` and the same in `Record23_g10729`, `Record23_g10771` |

A second game fixed the bound and asked for as few digits as possible. Here only one half is proved: no prime below
the bound is a summand (`FixedGap.lean`). For the bound 200,000: 319 digits (no summand below 207,307,
`exists_319_digit_no_summand_below_207307`), 347 digits (below 216,289) and 400 digits (below 200,293 and 206,593).
For one million: 1,797 digits (below 1,021,897, `exists_1797_digit_no_summand_below_1021897`), 1,997 digits (below
1,008,589) and 2,196 digits (below 1,001,491).

**Lower bounds for the largest least summand.** Here log is the natural logarithm and "for all large X" means from
some point on.

- `least_summand_unbounded` (`Basic.lean`): g(N) takes arbitrarily large values; in fact every odd prime is the least
  summand of arbitrarily large even numbers (`exists_isLeastSummand`).
- `eventually_exists_even_forall_not_isSummand` (`Counting.lean`): for all large X, some even number between X and
  2X has no summand below log X · log log X / 48.
- `eventually_exists_even_le_of_mul_lt_one` (`CoverBound.lean`): for every constant c below e^γ / (2 C₂) ≈ 1.349,
  and all large X, some even N ≤ X has no summand below c · log X · log log X (γ ≈ 0.5772 is Euler's constant and
  C₂ ≈ 0.6602 the twin-prime constant). The proof needs Mertens' third theorem, which Mathlib, Lean's library of
  mathematics, did not have; it is proved here (`Mertens.mertens_third`, `Mertens.lean`).
- `eventually_exists_even_le_every_constant` (`CoverEveryConstant.lean`): the same for every constant, so the
  largest least summand up to X outgrows every fixed multiple of log X · log log X.
- `eventually_exists_even_le_log` (same file): for all large X some even N ≤ X has no summand below
  log X · (log log X)² / (150000 · (log log log X)²).

**Complete covers and cover depths.** A *cover* picks one remainder for each of a list of small primes r so that
every prime q below a bound Q leaves one of the picked remainders. Any N with those remainders has N − q divisible by
some r for every prime q < Q, so no primality test is needed.

- `exists_lt_ten_pow_200_complete_cover_16981` (`Records.lean`): some even N below 10^200 has N − q divisible by a
  prime at most 491 for every prime q below 16,981, the largest bound proved by divisibility alone;
  `exists_progression_complete_cover_15907` gives 21,378,978 such numbers below 10^200 for the bound 15,907.
- `isDepth_0` to `isDepth_9` (`CoverDepthRun.lean`): the *cover depth* of the first k odd primes (the smallest prime
  q such that no choice of their remainders covers all the odd primes up to q) is exactly 3, 5, 7, 19, 31, 43, 67,
  103, 163, 181 for k = 0 to 9; `coversBelow_10` to `coversBelow_35` (also `CoverDepthMore.lean`) are lower bounds for 10
  to 35 primes.
- `coversBelow_41659` (`CoverCountRun.lean`) and `coversBelow_614101` (`CoverDepthGreedy.lean`): the odd primes up to
  997 cover every odd prime below 41,659, and the odd primes below 10,000 every odd prime below 614,101.
- `exists_isSummand_of_lt_961` (`CoverDepthRun.lean`): every even number from 6 to 960 has a summand at most 181,
  proved from the cover depth without testing any N − q for primality.
- `isDepth_iff_coverCount` (`CoverCount.lean`): the number of covers has an exact inclusion–exclusion formula, and
  the depth is where it reaches zero.
- `sat_iff_coversList` (`Cap/Hardness.lean`): if arbitrary numbers replace the primes to be covered, deciding whether
  a cover exists is as hard as the satisfiability problem of logic.

**Function fields.** Polynomials whose coefficients come from a finite field (a number system with finitely many
elements, such as the remainders modulo 3) behave like the integers, with irreducible polynomials (those that do not
factor) in the role of primes, and some questions can be settled there exactly.

- `stickelbergerSwan` (`FunctionField/Stickelberger.lean`): Stickelberger's theorem, which Mathlib does not have: over
  a finite field with an odd number of elements, one number computed from the coefficients of a polynomial without
  repeated factors (its discriminant) tells whether its number of irreducible factors is even or odd.
- `desert` and `desert_of_one_le` (`ParityDesert.lean`, `DesertDegree.lean`): explicit N for which N − Q factors for
  every irreducible Q (with leading coefficient 1) up to a given degree, proved through that parity without naming any
  factor; `discr_sub_eq_resultant` extends the parity rule to every N built from powers of t^p, p the characteristic.
- `card_monic_cell`, `irreducible_sub_comp_X_add_C_iff`, `not_irreducible_sub_of_aligned` (`Families.lean`): the
  polynomials with prescribed remainders are counted exactly; if N is unchanged by t ↦ t + c then N − Q and
  N − Q(t + c) are irreducible together; and one polynomial R used as the remainder for every small modulus rules out
  every Q of the next degree except the R − c.

**The rest.**

- `exists_summand_le` and `isRecordHolder_iff` (`RankSieve.lean`): every even number from 6 to 33,554,430 is a
  sum of two primes the smaller of which is at most 997, and the even numbers in that range whose least summand
  beats that of every smaller one are exactly the 26 listed in the file.
- `mem_records` (`RecordGen.lean`) and `goldbach_iff_records_unbounded` (`RecordInfinite.lean`): a program listing
  those record-setting numbers (sequences A025018 and A025019 of the OEIS) is proved correct, and its list is
  infinite exactly when Goldbach's conjecture is true.
- `prime_of_stepCheck` (`ECPP.lean`): one step of an elliptic-curve primality certificate, of the kind the records
  of 23 to 200 digits use to prove N − g prime, is sound (the 25- to 27-digit numbers use Mathlib's own check).
- `fermat28r_correct` (`Gpu28/Kernel.lean`), `fermat2_correct` (`Gpu/Fermat.lean`) and the `Fscan` files: the
  arithmetic of the graphics-card and processor programs used in the searches computes the Fermat test
  2^(n−1) ≡ 1 (mod n) correctly, for a model of the code.
- `searchCost_le_of_perm` (`Cap/Inspection.lean`): when looking for one good candidate among independent groups,
  examining the groups in decreasing order of their chance is the cheapest order; the other `Cap/*.lean` files state
  exact facts of the same kind about the cost of the search.
- `exists_best_list_candidates` (`Worlds/NoCoupling.lean`) and `lt_iff_fract_sum_mul_div_lt` (`Worlds/Arc.lean`):
  without a constraint linking the choices of remainders, the k best choices come out at a cost proportional to k;
  and among the numbers below the product P of the moduli, those below X are exactly the remainder patterns whose one
  combined "angle" lies in an arc of length X/P.
- `exists_isLeastSummand_le_of_linnik` (`Effective.lean`): assuming Linnik's theorem on primes in progressions (a
  hypothesis of the statement; it is not in Mathlib), every odd prime is the least summand of an even number below
  an explicit bound.

## What "proved in the kernel" does and does not guarantee

It guarantees, provided Lean's kernel itself is correct, that each statement follows from Mathlib's definitions and
three standard axioms of Lean's mathematics: `propext` (equivalent statements are equal), `Classical.choice` (the axiom of choice) and `Quot.sound`
(about quotients). No theorem uses `sorry` (an unproved step) or `native_decide` (which trusts compiled code). This is
checked for all 7,978 declarations of the 209 modules, 6,460 of them theorems, by `scripts/check_axioms.lean`.

It does not guarantee that a statement says what its name or this note says. Lean checked the proofs; whether the
statements are the intended ones is for a person to read: the line after `theorem`, with the definitions of
`IsSummand` and `IsLeastSummand` in `Basic.lean`. Statements with a hypothesis prove only "if the hypothesis holds,
then …": `Effective.lean` assumes Linnik's theorem, and the hardware files assume that the machine instructions do
what their specification says. For the 1,797-digit number, and for every number of the fixed-bound game, primality
of N − b, b the bound, is not proved (it passed probable-prime tests only), so the exact least summand is not
certified. The
measurements in `scripts/` (searches, heuristics, enumerations) are not proofs unless a theorem says so.

## How to build and check it

Install `elan` (Lean's version manager). In `goldbach/lean`, run `lake exe cache get` (it downloads the compiled
Mathlib for the pinned version) and then `lake build`. The toolchain is Lean v4.37.0-rc1 (`lean-toolchain`).
Most files take seconds; the record and certificate files take minutes each and up to about 7 GB of memory each.
(A timed clean build of the whole library is in progress; its numbers will replace this sentence.)
Then `lake env lean scripts/check_axioms.lean` (about 5 seconds, 4.5 GB) prints the axioms used by the whole
library; for one theorem, write `import GoldbachGaps` and `#print axioms GoldbachGaps.<name>` in a file and run
`lake env lean` on it.

## Started but not finished

- A search for a new 200-digit record over 3,000 covers of one family stopped after 796 covers, with no find
  (`scripts/scan200/README.md`).
- Exact cover depths from 10 primes on are not proved; only the lower bounds above are.
- For the bound one million, a 1,700-digit attempt by another session was paused on 25 November; no certificate exists.
- The 2,480-digit number with g = 1,157,341 (`slop/goldbach/records/g1`) is not checked: the kernel's elliptic-curve
  check is far too slow at that size.
- The toy-world programme of 26 November: the statements of Worlds 1, 3 and 5 are proved; the lower bound for the
  World 5 algorithm rests on a published result whose statement was not checked, and the other worlds were not
  formalised.
- Laws that were measured but not proved: the size of the number of covers (`CoverCount.lean`), the steps of its
  derivation that rest on the Hardy–Littlewood conjecture (`CoverPairs.lean`), and the regularities of
  `scripts/world3/`.
