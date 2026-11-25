import GoldbachGaps.Basic
import GoldbachGaps.Effective
import GoldbachGaps.Covering
import GoldbachGaps.Counting
import GoldbachGaps.Mertens
import GoldbachGaps.CoverBound
import GoldbachGaps.CoverEveryConstant
import GoldbachGaps.ECPP
import GoldbachGaps.Desert
import GoldbachGaps.DesertWitness
import GoldbachGaps.CompleteCover
import GoldbachGaps.Record150
import GoldbachGaps.Record199
import GoldbachGaps.Record199_g125269
import GoldbachGaps.Record199_g133981
import GoldbachGaps.Record200_g146191
import GoldbachGaps.Record200_g157837
import GoldbachGaps.Record200_g158209
import GoldbachGaps.Record200_g160357
import GoldbachGaps.Cover15907
import GoldbachGaps.Cover16381
import GoldbachGaps.Cover16747
import GoldbachGaps.Cover16981
import GoldbachGaps.Records
import GoldbachGaps.Gap200k_400digit_g200293
import GoldbachGaps.Gap200k_400digit_g206593
import GoldbachGaps.Gap200k_347digit_g216289
import GoldbachGaps.Gap200k_319digit_g207307
import GoldbachGaps.Gap1M_2196digit_g1001491
import GoldbachGaps.Gap1M_1997digit_g1008589
import GoldbachGaps.FixedGap
import GoldbachGaps.Needles
import GoldbachGaps.NeedlePairs
import GoldbachGaps.NeedleClusters
import GoldbachGaps.RankPatterns
import GoldbachGaps.RankData
import GoldbachGaps.RankTable
import GoldbachGaps.BitSieve
import GoldbachGaps.RankSieve
import GoldbachGaps.RecordGen
import GoldbachGaps.RecordGenRun
import GoldbachGaps.RecordInfinite
import GoldbachGaps.RecordWalk
import GoldbachGaps.CoverDepth
import GoldbachGaps.CoverDepthRun
import GoldbachGaps.CoverDepthMore
import GoldbachGaps.Cover1471
import GoldbachGaps.Cover4909
import GoldbachGaps.Cover8311
import GoldbachGaps.Cover32971
import GoldbachGaps.Cover40111
import GoldbachGaps.Cover40459
import GoldbachGaps.Cover41047
import GoldbachGaps.Cover41659
import GoldbachGaps.Cover135511
import GoldbachGaps.Cover614101
import GoldbachGaps.CoverDepthGreedy
import GoldbachGaps.CoverCount
import GoldbachGaps.CoverCountRun
import GoldbachGaps.CoverCountAsymptotic
import GoldbachGaps.CoverPairs
import GoldbachGaps.CoverPairSums
import GoldbachGaps.Record23_g11701
import GoldbachGaps.Record23_g10729
import GoldbachGaps.Record23_g10771
import GoldbachGaps.Fscan.Fermat52
import GoldbachGaps.Fscan.Fermat26
import GoldbachGaps.Fscan.Schedule
import GoldbachGaps.Fscan.Kernel52
import GoldbachGaps.Fscan.Kernel26
import GoldbachGaps.Fscan.Fermat30
import GoldbachGaps.Fscan.Kernel30
import GoldbachGaps.Fscan.ClassStage
import GoldbachGaps.Cap.Rows
import GoldbachGaps.Cap.Budget
import GoldbachGaps.Cap.FirstMoment
import GoldbachGaps.Cap.Poly
import GoldbachGaps.Cap.Transfer
import GoldbachGaps.Cap.Layers
import GoldbachGaps.Cap.CommonInteger
import GoldbachGaps.Cap.Selection
import GoldbachGaps.Cap.Brainstorm
import GoldbachGaps.Cap.Tilt
import GoldbachGaps.Cap.Radius
import GoldbachGaps.Cap.BlackBox
import GoldbachGaps.Cap.Population
import GoldbachGaps.Cap.ListGain
import GoldbachGaps.Cap.Thinning
import GoldbachGaps.Cap.Hardness
import GoldbachGaps.Gpu.Limbs
import GoldbachGaps.Gpu.MontSqr
import GoldbachGaps.Gpu.Fermat
import GoldbachGaps.Gpu28.Conv
import GoldbachGaps.Gpu28.Step
import GoldbachGaps.Gpu28.Final
import GoldbachGaps.Gpu28.Kernel
import GoldbachGaps.FunctionField.Stickelberger
import GoldbachGaps.FunctionField.ParityDesert
import GoldbachGaps.FunctionField.DesertDegree

/-!
# Least Goldbach summands in Lean

For an even `N`, the least Goldbach summand is `g(N) = min {p prime : N - p prime}`.
This library formalises the theorem-shaped parts of `goldbach/` and `slop/goldbach/`:

* `Basic`    – definitions; every odd prime is `g(N)` for arbitrarily large even `N`
               (paper Theorem `thm:dirichlet`), hence `g` is unbounded.
* `Effective` – with Linnik's theorem as a hypothesis (it is not in Mathlib), every odd prime
               `s` is `g(N)` for an even `N ≤ C · (primorial (s-1))^L + s`.
* `Covering` – the covering certificate and its unconditional realisation
               (paper Proposition `prop:cover`, Theorem `thm:coverdirichlet`).
* `Counting` – the counting bound: for large `X` some even `n` in `(X, 2X]` has no
               Goldbach summand below `log X · log log X / 48`.
* `Mertens`  – Mertens' third theorem, `log w · ∏_{p ≤ w} (1 - 1/p) → e^{-γ}`
               (`Mertens.mertens_third`), which is not in Mathlib (November 2026), proved from
               Mathlib by the classical route: Mertens' first theorem from `log N!` and
               Chebyshev's bound, Abel summation to `∑_{n ≤ t} Λ(n)/(n log n) - log log t → c`,
               the Dirichlet series `log ζ(s)` of the same sum, and the integral for `γ` as
               `s → 1` to get `c = γ`.
* `CoverBound` – the same order by a covering construction, with a better constant: for
               all large `X` there is an even `N ≤ X` with `N - q` composite for every prime
               `q < c · log X · log log X`, for every `c < e^γ / (2 C₂) = 1.349…`
               (`eventually_exists_even_le_of_mul_lt_one`, no hypothesis; counting pairs
               cannot exceed `1/2`), explicitly for `c = 1.2`
               (`eventually_exists_even_le_no_summand_six_fifths`), and for `c = 0.73` without
               Mertens' theorem (`eventually_exists_even_le_no_summand`). Inputs: the layered
               cover of `Cap.Layers`, the prime number theorem from Mathlib, `Mertens`, and an
               elementary bound `∏_{3 ≤ r ≤ w} (r - 2)/(r - 1) ≤ 1.367 / log w`.
* `CoverEveryConstant` – **every constant.** For every real `A` and all large `X` there is an
               even `N ≤ X` with `N - q` composite for every prime `q < A · log X · log log X`
               (`eventually_exists_even_le_every_constant`): the largest least Goldbach summand
               below `X` is not `O(log X · log log X)`. In depth form: for every `A` and all
               large `y`, classes modulo the odd primes up to `y` cover every odd prime below
               `A y ln y` (`eventually_exists_classes_every_constant`). The cover has three
               layers (`Cap.Layers`): the primes in `(z, y/4]` all take the class of one common
               integer `N₁`, the odd primes up to `z = ⌊ln y⌋^K - 1` take classes by the
               first-moment law, the primes in `(y/4, y]` take one row each. Averaged over
               `N₁ ∈ [Q, 2Q)` the fixed layer leaves at most the share of the integers below
               `2Q` with no prime factor in `(z, y/4]` (`Cap.exists_common_integer`), so no
               count of pairs of primes is needed: those integers are `z`-smooth (Rankin's
               bound, `Cap.card_smooth_le_exp`, from Mathlib's Euler product over smooth
               numbers) or `B · p'` with `p' > y/4` prime (the prime number theorem and a
               harmonic sum, `sum_primeCounting_le`). `Cap.CommonInteger` holds the finite
               counts. The device is that of Erdős and Rankin for gaps between primes.
               **The order.** With the exponent growing, `K = ⌊ln y / (14 (ln ln y)²)⌋`, the
               same layers cover every odd prime below `y ln² y / (9000 (ln ln y)²)`
               (`eventually_exists_classes_log`), and for all large `X` there is an even
               `N ≤ X` with no Goldbach summand below
               `ln X (ln ln X)² / (150000 (ln ln ln X)²)` (`eventually_exists_even_le_log`):
               Rankin's order with one more logarithm, short of it by `ln ln ln ln X`. The
               smooth numbers are then counted by Rankin's bound with `σ = 1 - 1/ln N` and
               Mertens' `∑_{p ≤ w} 1/p ≤ ln ln w + K₀` (`card_smooth_le_of_log_le`);
               `layers_common_integer_core` is the count at one `y` behind both theorems.
* `ECPP`     – a kernel-checkable elliptic-curve primality criterion (one Atkin–Morain
               step), proved sound against Mathlib's group law.
* `Desert`   – a kernel-checkable test that no prime in a block is a Goldbach summand.
* `CompleteCover` – the same test with no residuals read as divisibility: every prime `q`
               of a block has `N - q` divisible by a covering modulus, so the bound on the
               least summand needs no primality or compositeness test
               (`scripts/gen_cover.py` generates instances).
* `Cover15907` – generated instance: a 193-digit even `N` (and the 21,378,978 members
               `N + t M` of its progression below `10^200`) with `N - q` divisible by a prime
               `r ≤ 463` for each of the 1,853 primes `q < 15907`. It is the complete cover on
               the 89 odd primes up to 463 found by the research session
               (`goldbach/sublinear/complete_cover_15907.txt`, branch `ccr-d4a17dd0-7uu03r`,
               commit `9e99b06`), the best of three on 2026-11-23; the certificates of the
               earlier covers to 15787 and 15877 were at commits `8c061b4` and `7c4568c` of
               this branch and their statements are now corollaries. Closed statements in
               `Records`.
* `Cover16381`, `Cover16747`, `Cover16981` – generated instances on more primes, from the
               research session's files `complete_cover_16381_91primes.txt`,
               `…_16747_92primes.txt` and `…_16981_93primes.txt` (same branch, commit
               `10648a4`): even `N < 10^200` with `N - q` divisible by a prime `r ≤ 479`
               for the 1,898 odd primes `q < 16381` (198 digits, 95 members of the progression
               below `10^200`), by `r ≤ 487` for `q < 16747` and by `r ≤ 491` for the 1,956
               odd primes `q < 16981` (200 digits each, one member: the modulus exceeds
               `10^200`, so these were found by enumerating residue choices, not read off a
               progression). `16981` is the largest bound on the least summand proved here
               without any primality or compositeness test. Closed statements in `Records`.
* `Record150`, `Record199` – generated certificates (see `scripts/gen_record.py`) for the
               150-digit record `g = 104527` and the 199-digit record `g = 119419`.
* `Record199_g125269`, `Record199_g133981` – generated certificates for the two records of
               2026-11-22 below `10^199` (`goldbach/records/budget_1e200_199digit_g*` on
               branch `ccr-2ce9e63a-hn0fuw`): `g = 125269` and `g = 133981`.
* `Record200_g146191`, `Record200_g157837`, `Record200_g158209`, `Record200_g160357` –
               generated certificates for four records below `10^200`
               (`goldbach/records/budget_1e200_200digit_g146191`, `…_g157837` and `…_g158209` on
               the same branch, `…_g160357` on branch `ccr-8ffe9d7a-4ni11u`): 200-digit `N` with
               `g(N) = 146191`, `g(N) = 157837`, `g(N) = 158209` and, the standing record,
               `g(N) = 160357`.
* `Records`  – the bounded record games as closed theorems.
* `FixedGap`, `Gap200k_400digit_g200293`, `Gap200k_400digit_g206593`,
  `Gap200k_347digit_g216289` – the fixed-gap game (a
               given bound, as few digits as possible): two 400-digit even `N` with `N - q`
               composite for every prime `q < 200293` and `q < 206593`
               (`exists_400_digit_no_summand_below_200293`, `…_206593`,
               `exists_lt_ten_pow_400_no_summand_below_200000`), and a 347-digit one for
               every prime `q < 216289` (`exists_347_digit_no_summand_below_216289`,
               `exists_lt_ten_pow_347_no_summand_below_200000`), and a 319-digit one for every
               prime `q < 207307` (`Gap200k_319digit_g207307`,
               `exists_319_digit_no_summand_below_207307`,
               `exists_lt_ten_pow_319_no_summand_below_200000`). For the bound one million:
               `Gap1M_2196digit_g1001491` (with `…_Base` and 31 parts `…_0` to `…_30`), a
               2,196-digit even `N` from the Opus session with `N - q` composite for every
               prime `q < 1001491` (`exists_2196_digit_no_summand_below_1001491`,
               `exists_lt_ten_pow_2196_no_summand_below_1000000`), in the witness form, and
               `Gap1M_1997digit_g1008589` (same layout), a 1,997-digit one for every prime
               `q < 1008589` (`exists_1997_digit_no_summand_below_1008589`,
               `exists_lt_ten_pow_1997_no_summand_below_1000000`). Generated by
               `scripts/gen_desert.py` from the uarch session's records; the negative side
               only, with no primality proof, so the least summand itself is not certified.
* `DesertWitness` – the same check with a witness for every row (`rowCheck`,
               `witnessCheck`, `noSummandIn_of_witnessCheck`): a prime factor of `q`, a
               modulus dividing `N - q`, or the Fermat test, one division per row in the
               kernel; `scripts/gen_desert.py --witness` writes certificates in this form
               (three to four times faster at a bound of `200000`, and the form meant for a
               bound of `1000000`).
* `Needles`, `NeedlePairs`, `NeedleClusters` – what two needles (numbers with no Goldbach
               summand below `Q`) have in common. Rows are numbers: `N + h` inherits from a
               needle `N` every row `q'` with `q' - h` prime (`IsNeedle.add_of_forall`), 97 of
               168 rows for `Q = 1000`, `h = 30`; numbers at distance `Q` or more share no row
               (`row_ne_of_add_le`). Kernel-checked instances: four pairs of needles at level
               `1000` below `10^9` at distances 30, 30, 126, 210 (`needle_pairs_lt_1000`),
               where independent positions would give 0.09 such pairs among the 303 needles of
               the exhaustive enumeration (`scripts/mini_check/needle_pairs.txt`). Needles are
               not independent, and nothing here says they are random.
* `RankPatterns`, `RankData`, `RankTable` – the experiment of `scripts/rank_records`: the ten
               largest least Goldbach summands among the even numbers up to `10^12`, and the
               numbers that arrive at each rank. Proved: the relations that hold exactly
               (`3 ∣ N + g(N)` when `3 ∤ N`; `g(N + h) ≤ g(N) + h` when `g(N) + h` is prime,
               with equality as soon as the rows that are not inherited are composite; the
               least summand is at least the distance to the previous prime); the prime race
               behind the residue bias of the arrivals, in the kernel for every level up to
               4096 (class 2 against class 1 modulo 3) and 3528 (non-residues against residues
               modulo 5); the least summands of the 42 record holders up to `10^12`
               (`RankData.recordTable_spec`) and of the clustered arrivals (`shift_pairs`,
               `records_42_apart`). That the table is complete, and that record holders avoid
               multiples of 3 and prefer non-residue classes, are measurements beyond `2^25`;
               below `2^25` the first two are theorems (next entry).
* `BitSieve`, `RankSieve` – the rank experiment as theorems below `2^25 = 33554432`.
               `BitSieve`: a prime sieve on bitmasks that the kernel evaluates (the primes of an
               interval are the binary digits of one natural number; a digit left by the passes
               for all primes below `D` is a prime when the interval ends below `D²`; "some
               `N - q`, `q ≤ G`, is prime" is a union of shifts; a statement about every `N` of
               an interval divisible by `m` is one equality of big numbers). `RankSieve`
               (generated, 33 sieves of a million numbers; builds in about 90 s with 7 GB):
               every even `N` in `[6, 2^25)` is a sum of two primes with the smaller at most
               `997` (`exists_summand_le`); the record holders below `2^25` are exactly the 26
               numbers of the table (`isRecordHolder_iff`); a multiple of `3` has least summand
               at most `379`, of `5` at most `619`, of `7` `661`, of `11` `683`, of `13` `709`,
               of `15` `239`, of `21` `269`, of `35` `439`, of `105` `157`, each attained
               (`exists_summand_le_of_dvd_*`); and no multiple of `3` between `1362` and `2^25`
               enters the ten largest least summands (`notAmongTen_of_dvd_6`).
* `RecordGen`, `RecordGenRun` – a generator for OEIS A025018 / A025019 and the proof that it
               is correct. `IsRecord N g`: `N ≥ 4` even, `g` its least Goldbach summand, every
               smaller even number has a smaller one. `records X` builds the terms below `X`
               by a sieve of translates of the primes (strikers `q = 2, 3, 5, …`; the front is
               the smallest even number no striker has struck; a striker that hits the front
               makes it a term with value `q`), on bitmasks. `mem_records`: for every `X`,
               `(N, g) ∈ records X ↔ N < X ∧ IsRecord N g`; `records_sorted`: in increasing
               order; `isRecord_iff_front`: a term is a front that its striker hits;
               `testBit_primeMask`: the prime sieve inside is exact. `RecordGenRun`: the kernel
               runs the generator to `2^20` (21 terms), and what four simpler rules produce
               where they break (`8`, `14`, the value `11` for `98`, `124`) is proved not to
               be in the sequence. `scripts/record_gen`: those rules, each right for one term
               more than the last, and a runner (30 terms below `2^27` in 3 minutes).
* `RecordInfinite` – how far the generator goes. The front exists for every striker
               (`exists_isFront`, unconditional); the sequence is infinite, and `records X`
               grows beyond every length, if and only if Goldbach's conjecture holds
               (`goldbach_iff_records_unbounded`, `goldbach_iff_generator_never_stops`); if
               it fails, the front stops at the smallest counterexample
               (`isFront_of_counterexample`).
* `RecordWalk` – the same sequence as an N generator. `walk X` goes through the even numbers
               `N = 4, 6, 8, …` below `X`, keeps one number `G` (the largest least summand so
               far) and announces `N` when its least summand exceeds `G`. `mem_walk`: for
               every `X`, `N ∈ walk X ↔ N < X ∧ ∃ g, IsRecord N g`; `walk_sorted`;
               `walk_eq_map_records`: `walk X` is the list of numbers of `records X`, so
               walker and sieve are one generator; `walk_two_pow_20`: the 21 numbers
               announced below `2^20`. What the question "does `N` beat `G`?" looks at:
               the primes within `G` below `N` (`not_isSummand_iff_neighbours`), or `N`
               alone, through its residues modulo the primes up to `√N`, which must cover
               every prime `q ≤ G` (`beats_iff_wheels`). `scripts/record_gen/ngen.c`: the
               walker made fast (64 values of `N` per step; 10^11 in about a minute).
* `CoverDepth`, `CoverDepthRun` – the cover depth of a list of moduli (the research session's
               `D(n)` for the first `n` odd primes): the first odd prime that no residue
               vector strikes together with all smaller ones. A depth-first search decides
               it and is proved correct (`search_iff`); run in the kernel it gives the exact
               values `3, 5, 7, 19, 31, 43, 67, 103, 163, 181` for `0, …, 9` moduli
               (`isDepth_0` … `isDepth_9`; nine moduli in 72 kernel checks) and lower bounds
               `223, 271, 331, 419, 499, 613, 709, 739, 859` for `10, …, 18`
               (`coversBelow_10` … `coversBelow_18`). The depth increases with
               every new modulus (`IsDepth.lt_cons`). The least summand of an even `N` is
               at most the depth of the odd primes up to `√N` (`least_summand_le_depth`);
               if that depth is at most `N - 3`, `N` is a sum of two primes
               (`exists_isSummand_le_depth`), which gives Goldbach below `961` with no
               primality test of any `N - q` (`exists_isSummand_of_lt_841`,
               `exists_isSummand_of_lt_961`); arbitrarily
               large even numbers have least summand at least the depth
               (`exists_isLeastSummand_ge_depth`). The terms `6, 12, 30, 98` of A025018
               attain the depth of their small primes and `220` does not
               (`isRecord_and_isDepth`, `isRecord_220_and_isDepth`). The complete covers of
               the 200-digit search are lower bounds for 89 to 93 moduli
               (`coversBelow_15907` … `coversBelow_16981`). `scripts/cover_depth`: the
               search in C, the table to `n = 15`.
               `CoverDepthMore` (generated): lower bounds from explicit vectors for
               `19, …, 35` moduli, `907, 1051, 1213, 1279, 1381, 1471, 1567, 1669, 1801, 1933,
               2137, 2311, 2521, 2647, 2749, 2953, 3079` (`coversBelow_19` … `coversBelow_35`), the
               values the uarch session's exhaustive searches found; that no vector goes
               further is not checked here.
* `Cover32971`, `Cover40111`, `Cover135511`, `CoverDepthGreedy` – three generated
               certificates and their statements: the 167 odd primes up to `997` cover every
               odd prime below `32971` (`coversBelow_32971`, a greedy vector) and below `40111`
               (`coversBelow_40111`, the research session's tempered vector), and the 429 odd
               primes up to `2999` every odd prime below `135511` (`coversBelow_135511`,
               greedy); the greedy vectors are from `scripts/cover_depth/greedy.py`.
               `Cover614101`: a greedy vector on the 1228 odd primes up to `9973` covering
               every odd prime below `614101` (`coversBelow_614101`, with `mem_mods9973`: the
               moduli are exactly the odd primes below `10000`); the proved bound gives
               `123,900` there.
               `Cover1471`, `Cover4909`, `Cover8311`: three more tempered vectors of the
               research session, on the odd primes up to `97`, `199`, `293`
               (`coversBelow_1471`, `coversBelow_4909`, `coversBelow_8311`). The proved bound `1.349 x ln x` gives `9,290`
               and `32,390` there; the greedy reach follows `0.6` to `0.7` times `x ln² x` in
               everything computed.
* `CoverCount`, `CoverCountRun` – the number of complete covers: `coverCount mods rows`, the
               class vectors on `mods` (one residue class for each modulus) that cover every
               row, and `g0 x Q`, the research session's count for the odd primes up to `x`
               against the odd primes below `Q`. The exact identity behind the count is
               inclusion–exclusion over the sets `T` of rows left uncovered:
               `coverCount / ∏ r = ∑ (-1)^|T| ∏ (1 - ν_r(T)/r)`
               (`coverCount_div_prod_eq_sum`, `g0_div_prod_eq_sum`). The count is positive
               exactly when a cover exists, so the depth is where it reaches zero
               (`isDepth_iff_coverCount`, `isDepth_iff_g0`; `g0_29_181`: positive at `181`,
               zero at `182`, for nine moduli). A cover on fewer moduli gives a lower bound
               (`coverCount_mul_prod_le`, `prod_le_g0`): if the odd primes up to `x'` cover
               the odd primes below `Q`, then `ln g0(x, Q) ≥ θ(x) - θ(x')` for all `x ≥ x'`;
               stated for the certified covers (`prod_le_g0_15907` … `prod_le_g0_614101`).
               `Cover40459`, `Cover41047`, `Cover41659` (generated) and `coversBelow_40459`,
               `coversBelow_41047`, `coversBelow_41659`: three better covers on the 167 odd
               primes up to `997`, complete to `40459`, `41047` and `41659` (found by another
               session with the research session's sampler and by its own tempering); `41659`
               is the best known.
               The measured law `ln g0 = θ(x) - Q/ln² x` is not proved.
               `scripts/cover_count`: the constant `K` of the research session's heuristic,
               bracketed by exact rational arithmetic.
* `CoverCountAsymptotic` – the count in the range of the covering bound. `CoverBound` now also
               states its cover (`eventually_exists_classes_of_mul_lt_one`: for every
               `c < e^γ/(2 C₂) = 1.349…` and all large `y`, classes modulo the odd primes up to
               `y` cover every odd prime below `c y ln y`; the depth of the odd primes up to
               `y` is at least `c y ln y`). Hence `g0(y, ⌊c y ln y⌋) > 0` for all large `y`
               (`eventually_g0_pos`) and, for every `x ≥ y`,
               `ln g0(x, c y ln y) ≥ θ(x) - θ(y)` (`eventually_prod_le_g0`; with the explicit
               `c = 1.2`, `eventually_prod_le_g0_six_fifths`). At the same set of moduli
               (`eventually_prod_le_g0_self`): `ln g0(y, c y ln y) ≥ θ(y) - θ((c κ + ε) y)`
               with `κ = 2 C₂ e^{-γ}`, so the count is exponentially large in `y` there.
               For every constant `A` in place of `c`: `eventually_g0_pos_every_constant`,
               `eventually_prod_le_g0_every_constant`; and up to the order
               `y ln² y / (9000 (ln ln y)²)`: `eventually_g0_pos_log`.
* `CoverPairs` – two rows in one class of a modulus `s`: the exact step of the research
               session's derivation of the law. The pair weight `rho t d` of a smaller modulus
               (classes drawn among the `t - 1` nonzero ones; exact counts
               `card_free_nonzero_classes`, `card_pair_uncovered`, `prod_rho_eq`) and
               the Hardy–Littlewood factor `sigma t d`, the two local cancellations as that
               session wrote them (`local_cancellation_below`, `local_cancellation_above`),
               their meaning (`sum_rho_mul_sigma`, `sum_sigma`: mean `1` over a period), the
               Chinese remainder theorem for sums (`sum_range_prod`), and
               `sum_pair_weight`: summed over the differences `d = 6 s j` in one period, the
               pair weight times the Hardy–Littlewood factors has mean exactly `6 s/(s - 1)`,
               for every truncation of the two products. What the derivation does after this
               step rests on the Hardy–Littlewood conjecture and is not formalised.
* `CoverPairSums` – the pair weight in product form and its partial sums (the research
               session's items of 19:11 UTC). `pairWeight_eq_prod`:
               `W(j) = a · c · ∏_{t ∣ j} (1 + u_t)` with `a = 6 s/(s - 1)`, `u_t = 2/(t - 3)` for
               a modulus carrying a pair weight and `1/(t - 2)` otherwise, `c = ∏ (1 + u_t/t)⁻¹`
               (`prod_w0_mul_sum`). `sum_Ioc_pairWeight`: `∑_{j ≤ m} W(j) = a c ∑_D u(D) ⌊m/d(D)⌋`
               over the subsets `D` of the primes. `pairWeight_defect` and
               `sum_Ioc_pairWeight_le`: the defect `a m - ∑_{j ≤ m} W(j)` is a sum of
               nonnegative terms, so the partial sums never exceed the mean. The two local
               identities `local_ratio_below`, `local_ratio_above`; `C₂ ≥ 1/2`
               (`one_half_le_twinPrimeConstant`) and
               `∏_{5 ≤ t ≤ w} (t - 1)²/(t (t - 2)) → 3/(4 C₂)` (`tendsto_prod_sq_div`).
* `Record23_g11701`, `Record23_g10729`, `Record23_g10771` – generated certificates for three
               23-digit records of 2026-11-22 (`goldbach/records/threshold_23digit_*` on
               branch `ccr-2ce9e63a-hn0fuw`): `g(54284735534856910692542) = 11701`,
               `g(30625623272505310405982) = 10729`, `g(35505990484772441527442) = 10771`.
* `Fscan.*`  – correctness of the arithmetic kernels of the `goldbach/fscan` scanner (code
               at commit `a3ab69c` on branch `ccr-d4a17dd0-7uu03r`), one lane at a time:
               `Fermat52` / `Fermat26` are the Montgomery squaring steps `F52_STEP` and
               `FM_STEP` (relation, bounds, no 64-bit overflow); `Schedule` is the exponent
               schedule; `Kernel52` / `Kernel26` combine them into "the lane reports 1 iff
               `2^(n-1) ≡ 1 (mod n)`"; `ClassStage` is the division-free residue of
               `exact_stage`. `Fermat30` / `Kernel30` do the same for the 3-limb, 30-bit
               step `FM3_STEP` added at commit `1d8ab96` on branch `ccr-b8c25887-i6tn9f`.

* `Cap.*`    – the exact laws under the cost model of the capped game (largest `g(N)` for
               `N < 10^200`): `Rows` (a row `N - q` is composite iff `q ≡ N` modulo a prime
               `≤ √(N - q)`; prime moduli suffice; two rows share only divisors below `Q`),
               `Budget` (`N < X` with residues in prescribed sets `A r`: at most
               `∏ |A r| · (X / ∏ r + 1)`), `FirstMoment` (averaged over nonzero residue
               vectors exactly `|P| · ∏ (r - 2)/(r - 1)` rows are left, and the average of
               rows × boost is at least `|P| / 2` for every modulus set), `Poly` (`N = f(u)`
               makes the rows `f(c)` composite; at most `√Q + 1` of them and `√X + 1`
               members for degree `≥ 2`), `Transfer` (a prime desert gives a Goldbach gap),
               `Layers` (a fixed layer, a pigeonhole layer and a mop-up layer of moduli give
               an even `N` in an explicit window with no Goldbach summand below `Q` as soon
               as three counts allow it: the finite skeleton of lower bounds for
               `max {g(N) : N ≤ X}`, with the structure of the rows that survive a layer
               `N ≡ 1 (mod p)`), `Selection` (with independent rows, the logged hit mass
               `Σ (1 - p)^(rows left)` over any selected set of members is exactly the
               expected number of successes among them), `Brainstorm` (the statements with a
               proof among the 100 ideas of 2026-11-22: a zero class covers one row; two
               candidates that share a row value agree only on moduli of product below `g`;
               a move that keeps known factors pays for them in modulus; one exponent serves
               every row in a Fermat test; abandoning members never lowers the tests per
               success; faulty arithmetic costs false alarms, not successes; powers are
               sparse in a window; prescribed large divisors for 38 rows fix `N < 10^200`),
               `Tilt` (selection on a normal count of rows: weighting `N(μ, v)` by `e^{t x}`
               gives `e^{μ t + v t²/2} N(μ + v t, v)`, so the members with at most
               `μ - z √v` rows hold the fraction `Φ(λ - z)` of the successes,
               `λ = -√v ln(1 - p)`; a member `z` standard deviations below the mean is
               `e^(λ z - λ²/2)` times as likely to succeed as the average one, which caps what
               any search inside a progression can gain), `Radius` (lattice decoding and the
               search problem: reaching a smooth part `c` times the typical one needs
               `c² ≥ e ln K / 4`, so `c ≥ 3.88` for `K = 2^32`; in list form, a list of
               `2 ≤ ℓ ≤ r/2` classes modulo `r` carries `ln 2 - 2 ln r / r` more nats of
               information than it contributes to the lattice condition, so inside the
               Johnson radius only singleton lists, i.e. the cover, are left), `BlackBox` (a
               method that only asks members whether they are good finds one of the `g` good
               ones among `K` with `m` questions for at most the fraction `m g / K` of the
               instances), `Population` (independent rows left with probabilities `s_j`:
               `E [x^R] = ∏ (1 - s_j + s_j x)`; the members with at most `k` rows left
               contribute at most `u^(-k) ∏ (1 - s_j + s_j y u)` to `E [y^R]`; at most `μ - a`
               rows left has probability at most `exp (-a²/(2μ))`; whichever `m` members of a
               population are tested, their hit mass is at most `m y^k` plus that of the
               members with fewer than `k` rows; a merge of two lists of residue combinations
               costs at least `2 P / (K √(a b))` per member found, so the constrained primes
               can exceed the population by `F - C` nats and no more), `ListGain` (restricting
               `N` modulo one prime to a list of classes buys at most `(W - μ) / ln (W / μ)`
               rows for each nat it costs, `W` the most rows in a class and `μ` the average;
               for a prime above `Q = 213070` with at most 1609 rows left that is 0.207 rows a
               nat whatever the shape of the list), `Thinning` (moduli that separate the rows,
               in particular all moduli `≥ Q` for rows below `Q`: a class vector kills at most
               one row per modulus, so the sum over class vectors of `y^(rows left)` is at
               most `∏ m · (1 - (1 - y) θ)^k`, `θ = ∏ (1 - 1/m)`, the value for rows killed
               independently; hence the class vectors leaving at most `K` of `k` rows are at
               most the binomial Chernoff bound, and those leaving no row at most
               `∏ m · (1 - θ)^k`: inside the residue model the cost model's independence of
               the rows left is an inequality above `Q`. The research session's continuation of its
               prize table to depth `10^8` by independent rows is therefore a bound in a known
               direction above `Q`; `scripts/thinning_check/` tests the same law below `Q` on
               that session's tables and derives its `1/ln² z` regularity from it),
               `Hardness` (for arbitrary rows the cover question contains satisfiability:
               from a formula in conjunctive normal form with `n` variables and `m` clauses,
               `n` prime moduli and `m (n + 1)` rows of polynomial size such that the formula
               is satisfiable iff some residue vector covers every row, iff some `N` is
               congruent to every row modulo one of the moduli, iff the depth-first search of
               `CoverDepth` says so: `sat_iff_coversList`, `sat_iff_exists_number`,
               `sat_iff_search`. So a method that is fast for arbitrary rows would decide
               satisfiability; with `BlackBox`, a method that beats the present search has to
               use that the rows are the primes, and for that case nothing is proved).
* `Gpu.*`    – the GPU Fermat kernel `fermat2` of `goldbach/phd/campaign3_gpu/gpu_fermat.py`
               (commit `6ef621f`, branch `ccr-8ffe9d7a-4ni11u`), one thread, for any number
               of 32-bit limbs: `Limbs` (carry chain, borrow chain, comparison loop, shift),
               `MontSqr` (`mont_sqr` is a CIOS Montgomery squaring with result below `n`;
               `dbl_mod` doubles modulo `n`), `Fermat` (the Newton inverse modulo `2^32`,
               the word and bit loop, and `fermat2_correct`: the flag is `1` iff
               `2^(n-1) ≡ 1 (mod n)`, for `n = cq + k·M` odd, `> 1`, below `2^(32 L)`,
               `k < 2^32`).
* `Gpu28.*`  – the GPU Fermat kernel `fermat28` of `goldbach/fermat661/cuda/` (commits
               `560a2cf` and `fa7d9d1`, branch `ccr-b8c25887-i6tn9f`): 24 limbs of 28 bits,
               Montgomery squaring by columns with lazy 64-bit accumulators, values kept below
               `4n`, no `R mod n`. `Conv` (the column sums of a square), `Step` (the columns
               for input limbs below `2^29`: exact accumulators, `R · Y = X² + μ N`, `Y < 2N`;
               then the plain step with its carry chain and the redundant step
               `x_i = y_i << b`, both with `R · Y' = 2^b (X² + μ N)`, `Y' < 4N`), `Final` (the
               comparison loop, the borrow chain, the two conditional subtractions and the
               test against 1), `Kernel` (the Newton inverse with seed `(3·lo) xor 2`, the
               loop, and `fermat28_correct`: the lane reports `1` iff `2^(n-1) ≡ 1 (mod n)`,
               for odd `n` of 642 to 668 bits; `fermat28r_correct`: the same for the
               redundant-limb kernel in production, with its normalisation block). The set-up
               that derives the limbs, `c` and the bits of the schedule from `n` is a
               hypothesis, and the PTX instructions `mul.wide.u32`, `mad.wide.u32` are taken
               as the exact 32 × 32 → 64 product and multiply-add; `scripts/gpu28_check`
               compares the model with every generated step file compiled for the CPU, set-up
               included.
* `FunctionField.*` – the toy setting `F_q[x]` of the research programme in
               `goldbach/sublinear/` (branch `ccr-d4a17dd0-7uu03r`), where "`N - Q` is
               reducible for every monic irreducible `Q` of small degree" replaces a Goldbach
               gap. `Stickelberger`: Stickelberger's theorem in Swan's form (Pellet's formula),
               which is not in Mathlib: over a finite field of odd characteristic,
               `χ(discr g) = (-1)^(deg g - r)` for squarefree `g` with `r` irreducible factors
               (`stickelbergerSwan`), from `discr (f g) = discr f · discr g · Res(f, g)²`
               (`discr_mul`) and the action of the Frobenius on a Vandermonde determinant.
               `ParityDesert`: over any field, if `N' = 0`, `Q` is monic of degree
               `d < n = deg N` with `d ≠ 0` in the field and every irreducible factor of `Q'`
               divides `N`, then `discr (N - Q) = ± λ^(n-d-1) d^(n-d) discr Q` (`discr_sub`) and
               `N - Q` is squarefree; hence over a finite field the parity of the number of
               irreducible factors of `N - Q` (`parity_card_factors`); over a field with a
               square number of elements and for a non-square `λ`, `N - Q` is not irreducible
               (`not_irreducible_sub_of_isSquare_card`); and `N = c · V^p` has `N - Q`
               reducible for every monic irreducible `Q` of degree at most `J + 1` when `V` is
               divisible by all irreducibles of degree at most `J` (`desert`): a desert with
               no factor exhibited and no congruence paid for the top degree.
               The condition `d ≠ 0` is not needed: with `e`, `ℓ` the degree and leading
               coefficient of `Q'`, `discr (N - Q) = ± λ^(n-2-e) ℓ^(n-d) discr Q`
               (`discr_sub_general`), and the number of irreducible factors of `N - Q` is even
               exactly when `(-1)^(d+1+e) χ(ℓ)^(n-d) = 1` (`even_card_factors_iff`), which
               decides every row, also of a degree divisible by the characteristic
               (`desert_general`). The desert is not confined to the degrees up to `J + 1`:
               `N = c · V^p` kills every row of any degree `d < deg N` with `p ∤ d` whose
               derivative has no irreducible factor of degree above `J` (`desert_smooth`), a
               positive proportion of the rows of each such degree; for `p ∣ d`, those that
               also meet the sign criterion (`desert_smooth_general`). Without any condition
               on the roots of `Q'`: `discr (N - Q) = ± λ^(n-2-e) Res(Q', N - Q)` for every
               `N` with `N' = 0` (`discr_sub_eq_resultant`), so the parity of the number of
               factors of `N - Q` is a quadratic symbol of `N - Q` modulo `Q'`
               (`parity_card_factors_resultant`) and depends on `N` only through its degree,
               its leading coefficient and `N mod Q'` (`parity_card_factors_congr`).
               `DesertDegree`: for
               `J ≥ 1` the condition `deg Q < deg N` of `desert` is automatic, because
               `x^(q^J) - x` divides `V` (`desert_of_one_le`); for `J = 0` the statement is
               false. `scripts/parity_check/` compares the general formula
               with full factorisations over `F_3`, `F_5`, `F_7` (`gen_parity.py`) and checks
               the rows of higher degree with a smooth derivative (`smooth_rows.py`).

## Building

`lake exe cache get && lake build`. The record files with about 200 digits dominate: the
kernel replays the full certificates, several minutes and about 6 GB of memory for each.
No `sorry`, no `native_decide`, no extra axioms: `#print axioms` on any theorem here lists
only `propext`, `Classical.choice` and `Quot.sound`.

## Regenerating the record files

    python3 scripts/gen_record.py ../records/threshold_150digit_g104527 Record150 \
        GoldbachGaps/Record150.lean
    python3 scripts/gen_record.py ../../slop/goldbach/records/r200/record_r200_r1.json \
        Record199 GoldbachGaps/Record199.lean

## Not covered

The 2,480-digit height record (`slop/goldbach/records/g1`, `g = 1157341`). `ECPP` uses
affine coordinates with one modular inversion per group operation, recomputed inside the
kernel; that is fine at 200 digits and far too slow at 2,480. A projective-coordinate
checker would be needed for it.
-/
