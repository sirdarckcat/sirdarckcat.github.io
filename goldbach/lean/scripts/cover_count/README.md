# The number of complete covers: what is proved, and one constant

The research session (`goldbach/sublinear/README.md` on branch `ccr-d4a17dd0-7uu03r`, section "How
many complete covers there are: a law, and where they end") measures

    ln g0(x, Q) = θ(x) - c · Q / ln² x,      c near 1,

where `g0(x, Q)` is the number of class vectors modulo the odd primes up to `x` that cover every odd
prime below `Q`. It asked three optional things of the Lean side. This directory and
`GoldbachGaps/CoverCount.lean`, `GoldbachGaps/CoverCountRun.lean` are the answers.

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
* In the range of the research session's theorem (a cover of the odd primes below `Q` exists on the
  odd primes up to `x'` when `Q ≤ 1.349 x' ln x'`), it reads: the loss is at most `θ(x')` with
  `x' ln x' = Q / 1.349`, about `Q / (1.349 ln Q)`. That is a consequence of that theorem and
  `prod_le_g0`; the theorem itself is not formalised here.
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
