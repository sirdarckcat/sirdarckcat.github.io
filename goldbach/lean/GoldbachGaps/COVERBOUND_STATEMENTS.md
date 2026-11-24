# The lower bound for `max g` by covering, as it stands in Lean

File `CoverBound.lean` (namespace `GoldbachGaps`); the counting bound it is compared with is in
`Counting.lean`. Every theorem depends on `propext`, `Classical.choice` and `Quot.sound` only.
Below: the definitions (`#print`) and the statements (`#check`), unedited.

In words. `IsSummand N q` is "`q` is prime and `N - q` is prime". The main theorems say: for all
large `X` there is an even `N` with `c · ln X · ln ln X < N ≤ X` such that no natural number
`q < c · ln X · ln ln X` is a Goldbach summand of `N`,

* for every `c` with `c · 2 C₂ e^{-γ} < 1`, that is `c < 1.349…`, with no hypothesis
  (`eventually_exists_even_le_of_mul_lt_one`), and for `c = 1.2` with the numerical bounds on
  `γ` and `C₂` that are proved (`eventually_exists_even_le_no_summand_six_fifths`). These rest
  on Mertens' third theorem, which is not in Mathlib and is proved from Mathlib in `Mertens.lean`
  (`Mertens.mertens_third`, restated as `mertensThird : MertensThird`);
* for `c = 0.73` by an elementary bound that does not use Mertens' theorem
  (`eventually_exists_even_le_no_summand`);
* the same two statements with Mertens' third theorem as a hypothesis, as first proved
  (`eventually_exists_even_le_of_mertensThird`, `…_explicit`);
* for every `c` with `c κ < 1` under `MertensUpper κ` (`eventually_exists_even_le_of_mertensUpper`).

The counting bound of `Counting.lean` (`eventually_exists_even_forall_not_isSummand`) has the
constant `1/48`; that method cannot exceed `1/2`.

```lean
Mertens.mertens_third : Filter.Tendsto (fun w => Real.log ↑w * ∏ p ∈ w.primesLE, (1 - (↑p)⁻¹)) Filter.atTop
  (nhds (Real.exp (-Real.eulerMascheroniConstant)))
mertensThird : MertensThird
@eventually_exists_even_le_of_mul_lt_one : ∀ {c : ℝ},
  c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1 →
    ∀ᶠ (X : ℕ) in Filter.atTop,
      ∃ N,
        c * Real.log ↑X * Real.log (Real.log ↑X) < ↑N ∧
          N ≤ X ∧ Even N ∧ ∀ (q : ℕ), ↑q < c * Real.log ↑X * Real.log (Real.log ↑X) → ¬IsSummand N q
eventually_exists_even_le_no_summand_six_fifths : ∀ᶠ (X : ℕ) in Filter.atTop,
  ∃ N,
    1.2 * Real.log ↑X * Real.log (Real.log ↑X) < ↑N ∧
      N ≤ X ∧ Even N ∧ ∀ (q : ℕ), ↑q < 1.2 * Real.log ↑X * Real.log (Real.log ↑X) → ¬IsSummand N q
eventually_exists_even_le_no_summand : ∀ᶠ (X : ℕ) in Filter.atTop,
  ∃ N,
    0.73 * Real.log ↑X * Real.log (Real.log ↑X) < ↑N ∧
      N ≤ X ∧ Even N ∧ ∀ (q : ℕ), ↑q < 0.73 * Real.log ↑X * Real.log (Real.log ↑X) → ¬IsSummand N q
eventually_exists_even_le_of_mertensThird : MertensThird →
  ∀ {c : ℝ},
    c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1 →
      ∀ᶠ (X : ℕ) in Filter.atTop,
        ∃ N,
          c * Real.log ↑X * Real.log (Real.log ↑X) < ↑N ∧
            N ≤ X ∧ Even N ∧ ∀ (q : ℕ), ↑q < c * Real.log ↑X * Real.log (Real.log ↑X) → ¬IsSummand N q
eventually_exists_even_le_of_mertensThird_explicit : MertensThird →
  ∀ᶠ (X : ℕ) in Filter.atTop,
    ∃ N,
      1.2 * Real.log ↑X * Real.log (Real.log ↑X) < ↑N ∧
        N ≤ X ∧ Even N ∧ ∀ (q : ℕ), ↑q < 1.2 * Real.log ↑X * Real.log (Real.log ↑X) → ¬IsSummand N q
@eventually_exists_even_le_of_mertensUpper : ∀ {κ c : ℝ},
  0 < κ →
    MertensUpper κ →
      c * κ < 1 →
        ∀ᶠ (X : ℕ) in Filter.atTop,
          ∃ N,
            c * Real.log ↑X * Real.log (Real.log ↑X) < ↑N ∧
              N ≤ X ∧ Even N ∧ ∀ (q : ℕ), ↑q < c * Real.log ↑X * Real.log (Real.log ↑X) → ¬IsSummand N q
@eventually_exists_even_of_mertensUpper_nat : ∀ {κ c : ℝ},
  0 < κ →
    MertensUpper κ →
      0 < c →
        c * κ < 1 →
          ∀ᶠ (y : ℕ) in Filter.atTop,
            ∃ N,
              Even N ∧
                ⌊c * ↑y * Real.log ↑y⌋₊ < N ∧
                  N ≤ ⌊c * ↑y * Real.log ↑y⌋₊ + y + primorial y ∧ ∀ q < ⌊c * ↑y * Real.log ↑y⌋₊, ¬IsSummand N q
mertensUpper_elementary : MertensUpper (1575 / 1152)
mertensUpper_of_mertensThird : MertensThird →
  MertensUpper (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant))
@oddPrimeProd_le : ∀ {w : ℕ}, 7 ≤ w → oddPrimeProd w ≤ 1575 / 1152 / Real.log (↑w + 1)
log_le_prod_primesLE : ∀ (w : ℕ), Real.log (↑w + 1) ≤ ∏ p ∈ w.primesLE, (1 - (↑p)⁻¹)⁻¹
tendsto_twinPartial : Filter.Tendsto twinPartial Filter.atTop (nhds twinPrimeConstant)
twinPrimeConstant_le : twinPrimeConstant ≤ 1575 / 2304
eventually_exists_even_forall_not_isSummand : ∀ᶠ (X : ℕ) in Filter.atTop,
  ∃ n, X < n ∧ n ≤ 2 * X ∧ Even n ∧ ∀ (p : ℕ), ↑p ≤ Real.log ↑X * Real.log (Real.log ↑X) / 48 → ¬IsSummand n p
def GoldbachGaps.MertensUpper : ℝ → Prop :=
fun κ ↦ ∀ ε > 0, ∀ᶠ (w : ℕ) in Filter.atTop, oddPrimeProd w ≤ (κ + ε) / Real.log ↑w
def GoldbachGaps.MertensThird : Prop :=
Filter.Tendsto (fun w ↦ Real.log ↑w * ∏ p ∈ w.primesLE, (1 - (↑p)⁻¹)) Filter.atTop
  (nhds (Real.exp (-Real.eulerMascheroniConstant)))
def GoldbachGaps.oddPrimeProd : ℕ → ℝ :=
fun w ↦ ∏ r ∈ oddPrimesLE w, (↑r - 2) / (↑r - 1)
def GoldbachGaps.oddPrimesLE : ℕ → Finset ℕ :=
fun w ↦ {x ∈ w.primesLE | x ≠ 2}
def GoldbachGaps.twinPartial : ℕ → ℝ :=
fun w ↦ ∏ r ∈ oddPrimesLE w, (1 - 1 / (↑r - 1) ^ 2)
def GoldbachGaps.twinPrimeConstant : ℝ :=
⨅ w, twinPartial w
def GoldbachGaps.IsSummand : ℕ → ℕ → Prop :=
fun N p ↦ Nat.Prime p ∧ Nat.Prime (N - p)
```

## The depth form, and the number of complete covers (24 November 2026)

The proof builds a cover before it builds `N`. `CoverBound.lean` now states that cover: for every
`c` with `0 < c < 1.349…` and all large `y` there are classes modulo the odd primes up to `y` such
that every odd prime below `⌊c y ln y⌋` lies in one of them
(`eventually_exists_classes_of_mul_lt_one`; under `MertensUpper κ`,
`eventually_exists_classes_of_mertensUpper_nat`). In the words of `CoverDepth.lean`: the cover depth
of the odd primes up to `y` is at least `c y ln y`. `eventually_layers_of_mertensUpper_nat` is the
common part of the two proofs (the two layers and their count), and `Cap.exists_classes_of_layers`
the combinatorial step.

`CoverCountAsymptotic.lean` (namespace `GoldbachGaps.CoverCount`) reads this as a statement about
the number `g0 x Q` of class vectors modulo the odd primes up to `x` that cover every odd prime
below `Q` (`CoverCount.lean`): it is positive at `Q = ⌊c y ln y⌋`, `x = y`, and for every `x ≥ y` it
is at least the product of the odd primes in `(y, x]`.

```lean
@eventually_exists_classes_of_mul_lt_one : ∀ {c : ℝ},
  0 < c →
    c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1 →
      ∀ᶠ (y : ℕ) in Filter.atTop,
        ∃ a,
          ∀ (q : ℕ),
            Nat.Prime q → q ≠ 2 → q < ⌊c * ↑y * Real.log ↑y⌋₊ → ∃ r, (Nat.Prime r ∧ r ≠ 2 ∧ r ≤ y) ∧ q ≡ a r [MOD r]
@eventually_g0_pos : ∀ {c : ℝ},
  0 < c →
    c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1 →
      ∀ᶠ (y : ℕ) in Filter.atTop, 0 < g0 y ⌊c * ↑y * Real.log ↑y⌋₊
@eventually_prod_le_g0 : ∀ {c : ℝ},
  0 < c →
    c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1 →
      ∀ᶠ (y : ℕ) in Filter.atTop, ∀ x ≥ y, ∏ r ∈ rowsBelow (x + 1) \ rowsBelow (y + 1), r ≤ g0 x ⌊c * ↑y * Real.log ↑y⌋₊
eventually_prod_le_g0_six_fifths : ∀ᶠ (y : ℕ) in Filter.atTop,
  ∀ x ≥ y, ∏ r ∈ rowsBelow (x + 1) \ rowsBelow (y + 1), r ≤ g0 x ⌊1.2 * ↑y * Real.log ↑y⌋₊
def GoldbachGaps.CoverCount.g0 : ℕ → ℕ → ℕ :=
fun x Q => coverCount (rowsBelow (x + 1)) (rowsBelow Q)
def GoldbachGaps.CoverCount.rowsBelow : ℕ → Finset ℕ :=
fun y => {q ∈ Finset.range y | Nat.Prime q ∧ q ≠ 2}
def GoldbachGaps.CoverCount.coverCount : Finset ℕ → Finset ℕ → ℕ :=
fun mods rows => {a | ∀ q ∈ rows, Covers a q}.card
```

## Mertens' third theorem (`Mertens.lean`, namespace `GoldbachGaps.Mertens`)

The steps, with `A(t) = ∑_{n ≤ t} Λ(n)/n` and `B(t) = ∑_{n ≤ t} Λ(n)/(n ln n)`:

```lean
@Mertens.abs_A_sub_log_le : ∀ {t : ℝ}, 1 ≤ t → |Mertens.A t - Real.log t| ≤ 7
Mertens.tendsto_B_sub_log_log : Filter.Tendsto (fun b => Mertens.B b - Real.log (Real.log b)) Filter.atTop
  (nhds Mertens.limitB)
Mertens.limit_eq_eulerMascheroni : Mertens.limitB = Real.eulerMascheroniConstant
```

and `log_zeta_eq_integral` (`ln ζ(s) = (s - 1) ∫_1^∞ B(t) t^{-s} dt` for `s > 1`),
`tendsto_abel` (the Abelian limit as `s → 1`), `tendsto_sum_log_add_B`
(`∑_{p ≤ w} ln (1 - 1/p) + B(w) → 0`). From Mathlib it uses
`Real.eulerMascheroniConstant_eq_neg_integral_log_log`, `log_riemannZeta_eq`,
`riemannZeta_residue_one`, Abel summation (`sum_mul_eq_sub_integral_mul₁`,
`tendsto_sum_mul_atTop_nhds_one_sub_integral₀`), `Chebyshev.psi_le_const_mul_self` and
`Real.le_sum_log_nat`.
