import GoldbachGaps.Basic

/-!
# Selection on a normal count of rows

The research session's claim (feedback of 2026-11-22, behind its ideas on the keep fraction
and the sieve depth): if the number `R` of rows left is normal over the members, with mean `μ`
and variance `v`, and a member with `R` rows succeeds with probability `(1 - p)^R`, then the
members with `R ≤ μ - z √v` hold the fraction `Φ(λ - z)` of all successes, where
`λ = -√v · ln(1 - p)` and `Φ` is the standard normal distribution function.

It is the exponential tilt of a Gaussian: weighting `N(μ, v)` by `e^{t x}` gives
`e^{μ t + v t²/2} · N(μ + v t, v)` (`setIntegral_exp_mul_gaussianReal`), here with
`t = ln(1 - p)`. `selection_fraction` is the claim, exactly.

`selection_fraction_two` is the same for a search that orders the members by an earlier count (the
rows left by the cover) while success depends on a later one (the rows left at full depth): if the
later count is `ρ x + c + e` with `e` normal and independent of the earlier count `x`, the members
with `x ≤ μ - z √v` hold the fraction `Φ(ρ λ₁ - z)` of the successes, `λ₁ = -√v ln (1 - p)`. In
terms of the correlation `r` of the two counts and of `λ = -sd(later count) · ln (1 - p)` this is
`Φ(r λ - z)`: ordering by the earlier count is ordering by a criterion whose `λ` is `r` times that
of the later one. So to collect the share `f` of the successes the ideal order examines the share
`Φ(Φ⁻¹(f) - λ)` of the members and cover first the share `Φ(Φ⁻¹(f) - r λ)`; their ratio is the prize
of the ideal order (`scripts/alignment/`, section 5, compares it with three exact enumerations).
-/

namespace GoldbachGaps.Cap

open MeasureTheory ProbabilityTheory Real
open scoped NNReal

/-- An exponential weight turns a Gaussian density into a shifted one. -/
theorem exp_mul_gaussianPDFReal (μ : ℝ) {v : ℝ≥0} (hv : v ≠ 0) (t x : ℝ) :
    rexp (t * x) * gaussianPDFReal μ v x =
      rexp (μ * t + v * t ^ 2 / 2) * gaussianPDFReal (μ + v * t) v x := by
  have hv' : (v : ℝ) ≠ 0 := by exact_mod_cast hv
  simp only [gaussianPDFReal_def]
  rw [mul_left_comm, ← Real.exp_add, mul_left_comm (rexp _), ← Real.exp_add]
  congr 2
  field_simp
  ring

/-- **The exponential tilt of a Gaussian**, on any measurable set. -/
theorem setIntegral_exp_mul_gaussianReal (μ : ℝ) {v : ℝ≥0} (hv : v ≠ 0) (t : ℝ) {S : Set ℝ}
    (hS : MeasurableSet S) :
    ∫ x in S, rexp (t * x) ∂(gaussianReal μ v) =
      rexp (μ * t + v * t ^ 2 / 2) * (gaussianReal (μ + v * t) v S).toReal := by
  rw [← integral_indicator hS, integral_gaussianReal_eq_integral_smul hv]
  have h1 : ∀ x, gaussianPDFReal μ v x • S.indicator (fun x => rexp (t * x)) x =
      S.indicator (fun x => rexp (μ * t + v * t ^ 2 / 2) * gaussianPDFReal (μ + v * t) v x) x := by
    intro x
    by_cases hx : x ∈ S
    · rw [Set.indicator_of_mem hx, Set.indicator_of_mem hx, smul_eq_mul, mul_comm,
        exp_mul_gaussianPDFReal μ hv]
    · rw [Set.indicator_of_notMem hx, Set.indicator_of_notMem hx, smul_zero]
  simp_rw [h1]
  rw [integral_indicator hS, integral_const_mul, gaussianReal_apply_eq_integral _ hv,
    ENNReal.toReal_ofReal (setIntegral_nonneg hS fun x _ => gaussianPDFReal_nonneg _ _ _)]

/-- The total weight: the moment generating function. -/
theorem integral_exp_mul_gaussianReal (μ : ℝ) {v : ℝ≥0} (hv : v ≠ 0) (t : ℝ) :
    ∫ x, rexp (t * x) ∂(gaussianReal μ v) = rexp (μ * t + v * t ^ 2 / 2) := by
  have := setIntegral_exp_mul_gaussianReal μ hv t MeasurableSet.univ
  simpa using this

/-- Standardising a Gaussian: `P(N(m, v) ≤ a) = Φ((a - m) / √v)`. -/
theorem gaussianReal_Iic (m : ℝ) {v : ℝ≥0} (hv : v ≠ 0) (a : ℝ) :
    gaussianReal m v (Set.Iic a) = gaussianReal 0 1 (Set.Iic ((a - m) / √(v : ℝ))) := by
  have hs : 0 < √(v : ℝ) := Real.sqrt_pos.mpr (by exact_mod_cast pos_of_ne_zero hv)
  have h1 : (gaussianReal 0 1).map (√(v : ℝ) * ·) = gaussianReal 0 v := by
    rw [gaussianReal_map_const_mul]
    congr 1
    · simp
    · ext
      simp [Real.sq_sqrt v.coe_nonneg]
  have h2 : (gaussianReal 0 v).map (· + m) = gaussianReal m v := by
    rw [gaussianReal_map_add_const, zero_add]
  rw [← h2, ← h1, Measure.map_apply (measurable_add_const m) measurableSet_Iic,
    Measure.map_apply (measurable_const_mul _) (measurable_add_const m measurableSet_Iic)]
  congr 1
  ext x
  simp only [Set.mem_preimage, Set.mem_Iic]
  rw [le_div_iff₀ hs]
  constructor <;> intro h <;> linarith

/-- **The selection identity.** `R ~ N(μ, v)` over members, success probability `(1 - p)^R`:
the members with `R ≤ μ - z √v` hold the fraction `Φ(λ - z)` of the successes,
`λ = -√v · ln(1 - p)`. -/
theorem selection_fraction (μ : ℝ) {v : ℝ≥0} (hv : v ≠ 0) {p : ℝ} (hp : p < 1) (z : ℝ) :
    (∫ r in Set.Iic (μ - z * √(v : ℝ)), (1 - p) ^ r ∂(gaussianReal μ v)) /
        (∫ r, (1 - p) ^ r ∂(gaussianReal μ v)) =
      (gaussianReal 0 1 (Set.Iic (-(√(v : ℝ) * Real.log (1 - p)) - z))).toReal := by
  have hpos : 0 < 1 - p := by linarith
  have hs : 0 < √(v : ℝ) := Real.sqrt_pos.mpr (by exact_mod_cast pos_of_ne_zero hv)
  have hpow : ∀ r : ℝ, (1 - p) ^ r = rexp (Real.log (1 - p) * r) :=
    fun r => Real.rpow_def_of_pos hpos r
  simp_rw [hpow]
  rw [setIntegral_exp_mul_gaussianReal μ hv _ measurableSet_Iic,
    integral_exp_mul_gaussianReal μ hv, mul_div_cancel_left₀ _ (Real.exp_pos _).ne',
    gaussianReal_Iic _ hv]
  have key : (μ - z * √(v : ℝ) - (μ + v * Real.log (1 - p))) / √(v : ℝ) =
      -(√(v : ℝ) * Real.log (1 - p)) - z := by
    rw [div_eq_iff hs.ne']
    have := Real.mul_self_sqrt v.coe_nonneg
    linear_combination (Real.log (1 - p)) * this
  rw [key]

/-- **What the best member is worth.** A member whose number of rows left is `z` standard
deviations below the mean is `e^(λ z - λ²/2)` times as likely to succeed as an average member,
`λ = -√v ln (1 - p)`. Among `K` members the best has `z ≈ √(2 ln K)`, so no search inside a
progression of `K` members gains more than about `λ √(2 ln K)` nats over testing at random. -/
theorem enrichment_at (μ : ℝ) {v : ℝ≥0} (hv : v ≠ 0) {p : ℝ} (hp : p < 1) (z : ℝ) :
    (1 - p) ^ (μ - z * √(v : ℝ)) / (∫ r, (1 - p) ^ r ∂(gaussianReal μ v)) =
      rexp (-(√(v : ℝ) * Real.log (1 - p)) * z - (√(v : ℝ) * Real.log (1 - p)) ^ 2 / 2) := by
  have hpos : 0 < 1 - p := by linarith
  have hpow : ∀ r : ℝ, (1 - p) ^ r = rexp (Real.log (1 - p) * r) :=
    fun r => Real.rpow_def_of_pos hpos r
  simp_rw [hpow]
  rw [integral_exp_mul_gaussianReal μ hv, ← Real.exp_sub]
  congr 1
  have := Real.mul_self_sqrt v.coe_nonneg
  linear_combination (Real.log (1 - p) ^ 2 / 2) * this

/-- **Selection on the earlier of two counts.** The earlier count is `x ~ N(μ, v)`; the later count
is `ρ x + c + e` with `e ~ N(0, w)` independent of `x`; a member succeeds with probability
`(1 - p)^(later count)`. Then the members with `x ≤ μ - z √v` hold the fraction `Φ(ρ λ₁ - z)` of
the successes, `λ₁ = -√v · ln (1 - p)`. -/
theorem selection_fraction_two (μ c ρ : ℝ) {v w : ℝ≥0} (hv : v ≠ 0) (hw : w ≠ 0) {p : ℝ}
    (hp : p < 1) (z : ℝ) :
    (∫ x in Set.Iic (μ - z * √(v : ℝ)), ∫ e, (1 - p) ^ (ρ * x + c + e) ∂(gaussianReal 0 w)
        ∂(gaussianReal μ v)) /
        (∫ x, ∫ e, (1 - p) ^ (ρ * x + c + e) ∂(gaussianReal 0 w) ∂(gaussianReal μ v)) =
      (gaussianReal 0 1 (Set.Iic (-(ρ * (√(v : ℝ) * Real.log (1 - p))) - z))).toReal := by
  have hpos : 0 < 1 - p := by linarith
  have hs : 0 < √(v : ℝ) := Real.sqrt_pos.mpr (by exact_mod_cast pos_of_ne_zero hv)
  set L := Real.log (1 - p) with hL
  set K := rexp (L * c) * rexp (0 * L + w * L ^ 2 / 2) with hK
  have hKpos : 0 < K := mul_pos (Real.exp_pos _) (Real.exp_pos _)
  have hinner : ∀ x : ℝ, ∫ e, (1 - p) ^ (ρ * x + c + e) ∂(gaussianReal 0 w) =
      K * rexp (ρ * L * x) := by
    intro x
    have h1 : ∀ e : ℝ, (1 - p) ^ (ρ * x + c + e) = rexp (L * (ρ * x + c)) * rexp (L * e) := by
      intro e
      rw [Real.rpow_def_of_pos hpos, ← Real.exp_add]
      congr 1
      ring
    simp_rw [h1]
    rw [integral_const_mul, integral_exp_mul_gaussianReal 0 hw, hK, ← Real.exp_add,
      ← Real.exp_add, ← Real.exp_add]
    congr 1
    ring
  simp_rw [hinner]
  rw [integral_const_mul, integral_const_mul, mul_div_mul_left _ _ hKpos.ne',
    setIntegral_exp_mul_gaussianReal μ hv _ measurableSet_Iic,
    integral_exp_mul_gaussianReal μ hv, mul_div_cancel_left₀ _ (Real.exp_pos _).ne',
    gaussianReal_Iic _ hv]
  have key : (μ - z * √(v : ℝ) - (μ + v * (ρ * L))) / √(v : ℝ) =
      -(ρ * (√(v : ℝ) * L)) - z := by
    rw [div_eq_iff hs.ne']
    have := Real.mul_self_sqrt v.coe_nonneg
    linear_combination (ρ * L) * this
  rw [key]

end GoldbachGaps.Cap
