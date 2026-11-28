import GoldbachGaps.CoverBound
import GoldbachGaps.CoverEveryConstant
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
* `eventually_prod_le_g0_self`: the count at the same set of moduli. With `κ = 2 C₂ e^{-γ}`, for
  every `ε > 0` and all large `y`, `g0(y, ⌊c y ln y⌋)` is at least the product of the odd primes
  in `((c κ + ε) y, y]`: `ln g0(y, Q) ≥ θ(y) - θ((c κ + ε) y)`, a loss of at most about
  `κ Q / ln y + ε y`. So in the range of the covering bound the number of complete covers is
  exponentially large in `y`, at least `e^{(1 - c κ - ε) y}` to leading order.
* `eventually_g0_pos_six_fifths`, `eventually_prod_le_g0_six_fifths`: the same with the explicit
  `c = 1.2`.

* `eventually_g0_pos_every_constant`, `eventually_prod_le_g0_every_constant`: the first two for
  **every** constant `A` in place of `c < 1.349…`, from the cover with a fixed layer on a common
  integer (`GoldbachGaps/CoverEveryConstant.lean`).
* `eventually_g0_pos_log`: `g0(y, Q) > 0` for `Q = ⌊y ln² y / (9000 (ln ln y)²)⌋`, the order that
  cover reaches.

These are lower bounds for the count in the range `Q ≤ A y ln y`. The law the research session
measures, loss `≈ Q / ln² x`, is smaller than these bounds and is not proved.
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

/-- **The count at the same set of moduli.** Write `κ = 2 C₂ e^{-γ} = 0.7413…`. For every `c > 0`
with `c κ < 1`, every `ε > 0` and all large `y`: among the class vectors modulo the odd primes up
to `y`, at least the product of the odd primes in `((c κ + ε) y, y]` cover every odd prime below
`⌊c y ln y⌋`. In logarithms `ln g0(y, Q) ≥ θ(y) - θ((c κ + ε) y)` for `Q = c y ln y`: the loss is
at most about `(c κ + ε) y = κ Q / ln y + ε y`, linear in `Q`, and the count is at least
`e^{(1 - c κ - ε) y (1 + o(1))}`. (Proof: the covering bound on the odd primes up to
`(c κ + ε) y`, with a constant slightly above `c / (c κ + ε)`, then `prod_le_g0`.) -/
theorem eventually_prod_le_g0_self {c ε : ℝ} (hc0 : 0 < c)
    (hc : c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1)
    (hε : 0 < ε) :
    ∀ᶠ y : ℕ in atTop,
      ∏ r ∈ rowsBelow (y + 1) \ rowsBelow
          (⌈(c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) + ε) * y⌉₊ + 1),
        r ≤ g0 y ⌊c * y * Real.log y⌋₊ := by
  set κ := 2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant) with hκdef
  have hκ0 : 0 ≤ κ := by
    have := twinPrimeConstant_nonneg
    have := Real.exp_pos (-Real.eulerMascheroniConstant)
    positivity
  have hcκ0 : 0 ≤ c * κ := mul_nonneg hc0.le hκ0
  set lam := c * κ + ε with hlamdef
  have hlam0 : 0 < lam := by linarith
  have hden : 0 < c * κ + ε / 2 := by linarith
  set c₀ := c / (c * κ + ε / 2) with hc₀def
  have hc₀0 : 0 < c₀ := div_pos hc0 hden
  have hc₀κ : c₀ * κ < 1 := by
    rw [hc₀def, div_mul_eq_mul_div, div_lt_one hden]
    linarith
  have hρ : c < c₀ * lam := by
    rw [hc₀def, div_mul_eq_mul_div, lt_div_iff₀ hden]
    nlinarith
  have hd : 0 < c₀ * lam - c := by linarith
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hmul : Tendsto (fun y : ℕ => lam * (y : ℝ)) atTop atTop := hcast.const_mul_atTop hlam0
  have htend : Tendsto (fun y : ℕ => ⌈lam * (y : ℝ)⌉₊) atTop atTop :=
    tendsto_nat_ceil_atTop.comp hmul
  have hlog : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  filter_upwards [htend.eventually (eventually_g0_pos hc₀0 hc₀κ), eventually_g0_pos hc0 hc,
    hlog.eventually_ge_atTop (c₀ * lam * (-Real.log lam) / (c₀ * lam - c)),
    hmul.eventually_ge_atTop 1, eventually_ge_atTop 1] with y hy hyy hL h1 hy1
  set y₀ := ⌈lam * (y : ℝ)⌉₊ with hy₀def
  by_cases hle : y₀ ≤ y
  · refine prod_le_g0 hle (lt_of_lt_of_le hy (g0_anti y₀ (Nat.floor_le_floor ?_)))
    have hy₀ge : lam * (y : ℝ) ≤ (y₀ : ℝ) := Nat.le_ceil _
    have hypos : (0 : ℝ) < y := by exact_mod_cast hy1
    have hlamy : 0 < lam * (y : ℝ) := mul_pos hlam0 hypos
    have hlogy₀ : Real.log (lam * (y : ℝ)) ≤ Real.log (y₀ : ℝ) := Real.log_le_log hlamy hy₀ge
    have hlogmul : Real.log (lam * (y : ℝ)) = Real.log lam + Real.log (y : ℝ) :=
      Real.log_mul hlam0.ne' hypos.ne'
    have hkey : c * Real.log (y : ℝ) ≤ c₀ * lam * (Real.log lam + Real.log (y : ℝ)) := by
      have h := (div_le_iff₀ hd).1 hL
      nlinarith
    calc c * (y : ℝ) * Real.log (y : ℝ) = (y : ℝ) * (c * Real.log (y : ℝ)) := by ring
      _ ≤ (y : ℝ) * (c₀ * lam * (Real.log lam + Real.log (y : ℝ))) :=
          mul_le_mul_of_nonneg_left hkey hypos.le
      _ = c₀ * (lam * (y : ℝ) * Real.log (lam * (y : ℝ))) := by
          rw [hlogmul]
          ring
      _ ≤ c₀ * ((y₀ : ℝ) * Real.log (y₀ : ℝ)) :=
          mul_le_mul_of_nonneg_left
            (mul_le_mul hy₀ge hlogy₀ (Real.log_nonneg h1) (Nat.cast_nonneg _)) hc₀0.le
      _ = c₀ * (y₀ : ℝ) * Real.log (y₀ : ℝ) := by ring
  · have hempty : rowsBelow (y + 1) \ rowsBelow (y₀ + 1) = ∅ :=
      sdiff_eq_empty_iff_subset.2 (rowsBelow_mono (by omega))
    rw [hempty, prod_empty]
    exact hyy

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

/-- **`g0(y, ⌊A y ln y⌋) > 0` for all large `y`, for every constant `A`.** -/
theorem eventually_g0_pos_every_constant (A : ℝ) :
    ∀ᶠ y : ℕ in atTop, 0 < g0 y ⌊A * y * Real.log y⌋₊ := by
  filter_upwards [eventually_exists_classes_every_constant A] with y ⟨a, ha⟩
  refine (coverCount_pos_iff _ _ fun r hr => (mem_rowsBelow.1 hr).1.pos).2 ⟨a, fun q hq => ?_⟩
  obtain ⟨hq1, hq2, hq3⟩ := mem_rowsBelow.1 hq
  obtain ⟨r, ⟨hr1, hr2, hr3⟩, hqr⟩ := ha q hq1 hq2 hq3
  exact ⟨r, mem_rowsBelow.2 ⟨hr1, hr2, by omega⟩, hqr⟩

/-- For every constant `A`, all large `y` and every `x ≥ y`: among the class vectors modulo the odd
primes up to `x`, at least the product of the odd primes in `(y, x]` cover every odd prime below
`⌊A y ln y⌋`. In logarithms, `ln g0(x, A y ln y) ≥ θ(x) - θ(y)`. -/
theorem eventually_prod_le_g0_every_constant (A : ℝ) :
    ∀ᶠ y : ℕ in atTop, ∀ x ≥ y,
      ∏ r ∈ rowsBelow (x + 1) \ rowsBelow (y + 1), r ≤ g0 x ⌊A * y * Real.log y⌋₊ := by
  filter_upwards [eventually_g0_pos_every_constant A] with y hy x hx
  exact prod_le_g0 hx hy

/-- **The count is positive up to the order of the bound**: `g0(y, Q) > 0` for all large `y` with
`Q = ⌊y ln² y / (9000 (ln ln y)²)⌋`. -/
theorem eventually_g0_pos_log :
    ∀ᶠ y : ℕ in atTop,
      0 < g0 y ⌊(y : ℝ) * Real.log y ^ 2 / (9000 * Real.log (Real.log y) ^ 2)⌋₊ := by
  filter_upwards [eventually_exists_classes_log] with y ⟨a, ha⟩
  refine (coverCount_pos_iff _ _ fun r hr => (mem_rowsBelow.1 hr).1.pos).2 ⟨a, fun q hq => ?_⟩
  obtain ⟨hq1, hq2, hq3⟩ := mem_rowsBelow.1 hq
  obtain ⟨r, ⟨hr1, hr2, hr3⟩, hqr⟩ := ha q hq1 hq2 hq3
  exact ⟨r, mem_rowsBelow.2 ⟨hr1, hr2, by omega⟩, hqr⟩

end GoldbachGaps.CoverCount
