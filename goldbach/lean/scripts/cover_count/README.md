# The number of complete covers: what is proved, and one constant

The research session (`goldbach/sublinear/README.md` on branch `ccr-d4a17dd0-7uu03r`, section "How
many complete covers there are: a law, and where they end") measures

    ln g0(x, Q) = θ(x) - c · Q / ln² x,      c near 1,

where `g0(x, Q)` is the number of class vectors modulo the odd primes up to `x` that cover every odd
prime below `Q`. It asked three optional things of the Lean side. This directory and
`GoldbachGaps/CoverCount.lean`, `GoldbachGaps/CoverCountRun.lean`,
`GoldbachGaps/CoverCountAsymptotic.lean` are the answers; section 4 (`GoldbachGaps/CoverPairs.lean`)
is the exact step of the derivation it sent afterwards.

## 1. The identity behind the count (proved in Lean)

`GoldbachGaps/CoverCount.lean` defines `coverCount mods rows` for any finite sets of moduli and rows,
and `g0 x Q` as the case above. Proved, on the three standard axioms:

| theorem | statement |
|---|---|
| `coverCount_div_prod_eq_sum` | `coverCount / ∏ r = ∑ over T ⊆ rows of (-1)^|T| ∏ r (1 - ν_r(T)/r)`, `ν_r(T)` the number of residues of `T` modulo `r` |
| `coverCount_eq_sum` | the same in integers: `∑ (-1)^|T| ∏ (r - ν_r(T))` |
| `card_uncovered` | the class vectors that cover no row of `T`: `∏ (r - ν_r(T))` of them |
| `coverCount_empty`, `g0_zero` | no rows: the count is `∏ r` |
| `coverCount_anti`, `g0_anti` | more rows, fewer covers |
| `coverCount_pos_iff`, `coversBelow_iff_coverCount_pos` | the count is positive exactly when a cover exists (`CoversBelow` of `CoverDepth.lean`) |
| `isDepth_iff_coverCount`, `isDepth_iff_g0` | the cover depth `D` is where the count reaches zero |

So "the number of complete covers" is now a defined quantity next to the depth, and the depth is its
last positive point.

## 2. A lower bound (proved in Lean; not the shape of the law)

`coverCount_mul_prod_le`: a cover on a subset of the moduli stays a cover whatever classes the other
moduli take. Hence (`prod_le_g0`), whenever the odd primes up to `x'` can cover the odd primes below
`Q`,

    ln g0(x, Q) ≥ θ(x) - θ(x')      for every x ≥ x'.

`GoldbachGaps/CoverCountRun.lean` states this for the certified covers:

| `x'` | moduli | `Q` | bound on the loss `θ(x) - ln g0(x, Q)` | the law's `Q / ln² x` at `x = x'` |
|---:|---:|---:|---:|---:|
| 97 | 24 | 1,471 | θ(97) = 83.0 | 70.3 |
| 199 | 45 | 4,909 | θ(199) = 187.9 | 175.2 |
| 293 | 61 | 8,311 | θ(293) = 276.3 | 257.6 |
| 463 | 89 | 15,907 | θ(463) = 442.9 | 422.3 |
| 491 | 93 | 16,981 | θ(491) = 467.6 | 442.3 |
| 997 | 167 | 40,111 | θ(997) = 955.6 | 841.3 |
| 2,999 | 429 | 135,511 | θ(2999) = 2,931.7 | 2,114.2 |
| 9,973 | 1,228 | 614,101 | θ(9973) = 9,895.3 | 7,243.4 |

(θ here is over the odd primes, which is what the moduli are; the last two columns are floating
point, for orientation, and are not part of any theorem.)

What this is and is not:

* It is rigorous and holds for every `x ≥ x'`, so it is a statement about `g0` away from its end.
* It has the law's form only in the sense that the best `x'` for a given `Q` is the inverse of the
  depth, and at `x = x'` the law itself says `θ(x') = c Q / ln² x'`. For `x` much larger than `x'`
  the law's loss `Q / ln² x` is smaller than this bound by the factor `ln² x / ln² x'`.
* In the range of the covering bound it is a theorem with no data in it
  (`GoldbachGaps/CoverCountAsymptotic.lean`, `eventually_prod_le_g0`): for every `c < e^γ/(2 C₂) =
  1.349…`, all large `y` and every `x ≥ y`,

      ln g0(x, c y ln y) ≥ θ(x) - θ(y),

  so the loss is at most `θ(y)`, about `Q / (c ln Q)` for `Q = c y ln y`. It rests on the depth form
  of the covering bound, which `GoldbachGaps/CoverBound.lean` now states
  (`eventually_exists_classes_of_mul_lt_one`: classes modulo the odd primes up to `y` that cover
  every odd prime below `c y ln y`). The explicit `c = 1.2` is `eventually_prod_le_g0_six_fifths`.
* A bound of the law's shape for all `x` (loss at most a constant times `Q / ln² x`) would put the
  depth at `x ln² x` or beyond, which nothing here proves.

## 3. The constant K (exact rational arithmetic, not Lean)

    K = exp(2 L),     L = lim as y → 0+ of [ ∫ from y to ∞ of dt / (t + e^t - 1)  +  (1/2) ln y ]

`K_enclosure.py` brackets it with exact rational arithmetic (`K_enclosure.txt`):

    K = 1.51645 16079 59502 58505 11213 12…      (enclosure of width 1.2 · 10^-28)
    L = 0.20818 65686 45416 45788 67824 31…

The method (the docstring has every step and its justification):

* `L = ∫₀¹ f + ∫₁^∞ g` with `g(t) = 1/(t + e^t - 1)` and `f(t) = g(t) - 1/(2t)`.
* `f(t) = -φ(t) / (4 + 2tφ(t))`, `φ(t) = (e^t - 1 - t)/t²`: its Taylor coefficients are rational, given
  by a recurrence, and bounded by `(3/8)(2/3)^n` (induction); 151 terms are integrated term by term
  and the rest is bounded.
* `∫₁^∞ g = ∑ (-1)^k k! e^-(k+1) / (k+1)^(k+1)`, an alternating series with decreasing terms.
* `e^-1` and the final exponential are bracketed by partial sums of their series.

The script also evaluates the definition directly in floating point for three values of `y`; the
values approach the enclosure at the expected rate `y/8`.

This is a computation with proved error bounds, not a kernel-checked theorem. A Lean proof of, say,
`1.5164 < K < 1.5165` is possible along the same lines and has not been written.

    python3 -I K_enclosure.py > K_enclosure.txt

## 4. The exact step of the derivation: two rows in one class (proved in Lean)

The research session's derivation of the law (its message of 24 November, 18:00 UTC) starts from two
odd primes `q`, `q + d` in one class of a modulus `s`, and says that the weight of the pair, times the
Hardy–Littlewood density of prime pairs, has mean exactly `6 s/(s - 1)` over the differences
`d = 6 s j`, "because for every prime `t ≥ 5` the local factors cancel identically".
`GoldbachGaps/CoverPairs.lean` proves this:

| theorem | statement |
|---|---|
| `card_free_nonzero_classes` | two rows in nonzero classes modulo `t` leave `t - 1 - ν_t(d)` nonzero classes free, `ν_t(d)` = 1 if `t ∣ d`, else 2 |
| `card_pair_uncovered`, `card_single_uncovered` | over a set of moduli, the class vectors with nonzero classes that leave both rows uncovered number `∏ (t - 1 - ν_t(d))`; one row, `∏ (t - 2)` |
| `prod_rho_eq` | `∏ rho` is (vectors leaving both uncovered) · (all vectors) / (vectors leaving one uncovered)² |
| `rho_of_dvd`, `rho_of_not_dvd` | the pair weight `(1 - ν/(t-1)) / (1 - 1/(t-1))²` is `(t-1)/(t-2)` if `t ∣ d`, `1 - 1/(t-2)²` if not (at `t = 3`: `2` and `0`) |
| `sigma_of_dvd`, `sigma_of_not_dvd` | the Hardy–Littlewood factor `(1 - ν/t) / (1 - 1/t)²` is `t/(t-1)` if `t ∣ d`, `1 - 1/(t-1)²` if not |
| `local_cancellation_below`, `local_cancellation_above` | the two rational identities, as the research session wrote them |
| `sum_rho_mul_sigma`, `sum_sigma` | over a period, `rho · sigma` (a modulus below `s`) and `sigma` (a prime above `s`) have mean exactly 1 |
| `sum_range_prod` | the Chinese remainder theorem for sums |
| `sum_pair_weight` | for a prime `s ≥ 5`, any finite set `B` of primes `≥ 5` other than `s` and any `A ⊆ B`: the sum over `j < ∏ B` of `rho 3 · ∏_A rho · sigma 2 · sigma 3 · sigma s · ∏_B sigma` at `d = 6 s j` is `6 s/(s - 1) · ∏ B` |

The mean is the same for every truncation of the two products, so no statement about convergence is
involved. The next step of the derivation, the second-order term of the average of singular series,
rests on the Hardy–Littlewood conjecture and is not formalised.

## 5. Exact counts for small sets of moduli

`g0_exact.c` goes through every class vector modulo the first `n` odd primes, records the first odd
prime each one fails to cover, and prints `g0(x, Q)` for every `Q` at once. It is `∏ r` steps, so it
stops at about ten moduli (3.2·10^9 vectors for `n = 9`, two seconds on four cores).

    gcc -O3 -march=native -fopenmp -o g0_exact g0_exact.c -lm
    ./g0_exact 9 > g0_exact_n9.txt

What it shows:

* It reproduces the cover depths `D(2), …, D(9) = 7, 19, 31, 43, 67, 103, 163, 181` that
  `GoldbachGaps/CoverDepth.lean` and `CoverDepthRun.lean` prove in the kernel.
* The number of class vectors that cover every odd prime below the depth is
  `2, 1, 2, 2, 6, 6, 1, 2` for `n = 2, …, 9`. For `n = 3` the single vector is that of the term `98`
  of A025018; this count is also proved in the kernel (`g0_7_19 : g0 7 19 = 1 ∧ g0 7 20 = 0` in
  `GoldbachGaps/CoverCountRun.lean`), as is `coverCount {3, 5} {3, 5} = 2`.
* `g0_exact_n9.txt`: the whole curve for nine moduli. The loss `θ - ln g0`, measured in units of
  `Q / ln² x` with `x = 29`, is `1.41, 1.26, 1.19, 1.33` at `Q = 53, 101, 151, 181`. The research
  session finds `1.09` to `1.15` at `x = 73` and values near `1` from `x = 463` on; nine moduli are far
  too few for a law, and the figures are given only as exact data at a size where everything can be
  counted.

These tables are exact, but the program is not a proof; the kernel-checked statements are the ones
named above.
