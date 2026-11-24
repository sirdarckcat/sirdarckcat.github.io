import GoldbachGaps.CoverBound
import GoldbachGaps.CoverCount

/-!
# The number of complete covers in the range of the covering bound

`GoldbachGaps/CoverBound.lean` proves, for every `c < e^γ / (2 C₂) = 1.349…`, that for all large
`y` some classes modulo the odd primes up to `y` cover every odd prime below `c y ln y`
(`eventually_exists_classes_of_mul_lt_one`, the depth form of that file's theorem). With
`GoldbachGaps/CoverCount.lean` this says that the count `g0` is positive there, and the monotone
bound `prod_le_g0` turns it into a lower bound for every larger set of moduli:

* `eventually_g0_pos`: `g0(y, ⌊c y ln y⌋) > 0` for all large `y`.
* `eventually_prod_le_g0`: for all large `y` and every `x ≥ y`, `g0(x, ⌊c y ln y⌋)` is at least
  the product of the odd primes in `(y, x]`. In logarithms: **`ln g0(x, Q) ≥ θ(x) - θ(y)` for
  `Q = c y ln y`**, so the loss `θ(x) - ln g0(x, Q)` is at most `θ(y)`, about `Q / (c ln Q)`.
* `eventually_g0_pos_six_fifths`, `eventually_prod_le_g0_six_fifths`: the same with the explicit
  `c = 1.2`.

This is a lower bound for the count in the range `Q ≤ 1.349 y ln y`. The law the research session
measures, loss `≈ Q / ln² x`, is smaller than this bound and is not proved.
-/

namespace GoldbachGaps.CoverCount

open Finset Filter

/-- **`g0(y, ⌊c y ln y⌋) > 0` for all large `y`**, for every `c > 0` with `c · 2 C₂ e^{-γ} < 1`,
that is `c < 1.349…`. -/
theorem eventually_g0_pos {c : ℝ} (hc0 : 0 < c)
    (hc : c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1) :
    ∀ᶠ y : ℕ in atTop, 0 < g0 y ⌊c * y * Real.log y⌋₊ := by
  filter_upwards [eventually_exists_classes_of_mul_lt_one hc0 hc] with y ⟨a, ha⟩
  refine (coverCount_pos_iff _ _ fun r hr => (mem_rowsBelow.1 hr).1.pos).2 ⟨a, fun q hq => ?_⟩
  obtain ⟨hq1, hq2, hq3⟩ := mem_rowsBelow.1 hq
  obtain ⟨r, ⟨hr1, hr2, hr3⟩, hqr⟩ := ha q hq1 hq2 hq3
  exact ⟨r, mem_rowsBelow.2 ⟨hr1, hr2, by omega⟩, hqr⟩

/-- **A lower bound for the number of complete covers in the range of the covering bound.** For
every `c < 1.349…`, all large `y` and every `x ≥ y`: among the class vectors modulo the odd
primes up to `x`, at least the product of the odd primes in `(y, x]` cover every odd prime below
`⌊c y ln y⌋`. In logarithms, `ln g0(x, c y ln y) ≥ θ(x) - θ(y)`. -/
theorem eventually_prod_le_g0 {c : ℝ} (hc0 : 0 < c)
    (hc : c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1) :
    ∀ᶠ y : ℕ in atTop, ∀ x ≥ y,
      ∏ r ∈ rowsBelow (x + 1) \ rowsBelow (y + 1), r ≤ g0 x ⌊c * y * Real.log y⌋₊ := by
  filter_upwards [eventually_g0_pos hc0 hc] with y hy x hx
  exact prod_le_g0 hx hy

/-- `c = 1.2` is in the range: `1.2 · 2 C₂ e^{-γ} < 1`. -/
theorem six_fifths_mul_lt_one :
    (1.2 : ℝ) * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1 := by
  have h1 := twinPrimeConstant_le
  have h2 := exp_neg_eulerMascheroni_lt
  have h3 := twinPrimeConstant_nonneg
  have h4 := Real.exp_pos (-Real.eulerMascheroniConstant)
  have h5 : twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant) ≤
      1575 / 2304 * 0.6066 := mul_le_mul h1 h2.le h4.le (by norm_num)
  nlinarith

/-- `g0(y, ⌊1.2 y ln y⌋) > 0` for all large `y`. -/
theorem eventually_g0_pos_six_fifths :
    ∀ᶠ y : ℕ in atTop, 0 < g0 y ⌊(1.2 : ℝ) * y * Real.log y⌋₊ :=
  eventually_g0_pos (by norm_num) six_fifths_mul_lt_one

/-- For all large `y` and every `x ≥ y`: `ln g0(x, 1.2 y ln y) ≥ θ(x) - θ(y)`. -/
theorem eventually_prod_le_g0_six_fifths :
    ∀ᶠ y : ℕ in atTop, ∀ x ≥ y,
      ∏ r ∈ rowsBelow (x + 1) \ rowsBelow (y + 1), r ≤ g0 x ⌊(1.2 : ℝ) * y * Real.log y⌋₊ :=
  eventually_prod_le_g0 (by norm_num) six_fifths_mul_lt_one

end GoldbachGaps.CoverCount
