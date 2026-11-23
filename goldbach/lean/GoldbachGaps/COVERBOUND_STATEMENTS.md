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
