import GoldbachGaps.Basic

/-!
# Mertens' third theorem

`ln w · ∏_{p ≤ w} (1 - 1/p) → e^{-γ}` (`mertens_third`), proved from Mathlib.

Mathlib (November 2026) has the analytic ingredients but not the theorem: the integral
`(s - 1) ∫_1^∞ ln ln t · t^{-s} dt = -γ - ln (s - 1)`
(`Real.eulerMascheroniConstant_eq_neg_integral_log_log`), `ln ζ(s) = ∑ Λ(n) / (n^s ln n)`
(`log_riemannZeta_eq`), the residue of `ζ` at `1`, Abel summation and Chebyshev's bound for `ψ`.
The proof here is the classical one (Hardy and Wright, An Introduction to the Theory of
Numbers, §22.7 and §22.8; the statement is their Theorem 429):

* `abs_A_sub_log_le` (Mertens' first theorem): `A(t) = ∑_{n ≤ t} Λ(n)/n = ln t + O(1)`, from
  `ln N! = ∑_{n ≤ N} Λ(n) ⌊N/n⌋` and `ψ(N) = O(N)`;
* `tendsto_B_sub_log_log`: `B(t) = ∑_{n ≤ t} Λ(n)/(n ln n)` satisfies `B(t) - ln ln t → c` for some
  `c`, by Abel summation;
* `log_zeta_eq_integral`: `ln ζ(s) = (s - 1) ∫_1^∞ B(t) t^{-s} dt` for `s > 1`, by Abel summation
  again;
* `limit_eq_eulerMascheroni`: comparing with the integral for `γ` as `s → 1`, `c = γ`;
* `tendsto_sum_log_add_B`: `∑_{p ≤ w} ln (1 - 1/p) + B(w) → 0`, since the two differ by the
  prime powers above `w`;
* `mertens_third`.
-/

namespace GoldbachGaps.Mertens

open Finset Filter MeasureTheory
open scoped ArithmeticFunction.vonMangoldt Topology

/-- `Λ(k) / k`. -/
noncomputable def lam (k : ℕ) : ℝ := Λ k / k

/-- `A(t) = ∑_{k ≤ t} Λ(k) / k`. -/
noncomputable def A (t : ℝ) : ℝ := ∑ k ∈ Icc 0 ⌊t⌋₊, lam k

theorem lam_zero : lam 0 = 0 := by simp [lam]

theorem lam_one : lam 1 = 0 := by simp [lam]

theorem lam_nonneg (k : ℕ) : 0 ≤ lam k :=
  div_nonneg ArithmeticFunction.vonMangoldt_nonneg (Nat.cast_nonneg k)

/-- **Mertens' first theorem** at the integers: `|∑_{n ≤ N} Λ(n)/n - ln N| ≤ 6`. -/
theorem abs_sum_lam_sub_log_le (N : ℕ) (hN : 1 ≤ N) :
    |∑ n ∈ Ioc 0 N, Λ n / n - Real.log N| ≤ 6 := by
  have hNpos : (0 : ℝ) < N := by exact_mod_cast hN
  have key : ∑ n ∈ Ioc 0 N, Λ n * ((N / n : ℕ) : ℝ) = ∑ n ∈ Ioc 0 N, Real.log n := by
    rw [← ArithmeticFunction.sum_Ioc_mul_zeta_eq_sum, ArithmeticFunction.vonMangoldt_mul_zeta]
    simp [ArithmeticFunction.log_apply]
  have hup : ∑ n ∈ Ioc 0 N, Λ n * ((N / n : ℕ) : ℝ) ≤ N * ∑ n ∈ Ioc 0 N, Λ n / n := by
    rw [Finset.mul_sum]
    refine Finset.sum_le_sum fun n hn => ?_
    calc Λ n * ((N / n : ℕ) : ℝ) ≤ Λ n * ((N : ℝ) / n) :=
          mul_le_mul_of_nonneg_left Nat.cast_div_le ArithmeticFunction.vonMangoldt_nonneg
      _ = N * (Λ n / n) := by ring
  have hlow : N * ∑ n ∈ Ioc 0 N, Λ n / n - ∑ n ∈ Ioc 0 N, Λ n
      ≤ ∑ n ∈ Ioc 0 N, Λ n * ((N / n : ℕ) : ℝ) := by
    rw [Finset.mul_sum, ← Finset.sum_sub_distrib]
    refine Finset.sum_le_sum fun n hn => ?_
    have hn0' : 0 < n := (Finset.mem_Ioc.mp hn).1
    have hn0 : (0 : ℝ) < n := by exact_mod_cast hn0'
    have h1 : (N : ℝ) < n * (((N / n : ℕ) : ℝ) + 1) := by
      exact_mod_cast Nat.lt_mul_div_succ N hn0'
    have h2 : (N : ℝ) / n - 1 ≤ ((N / n : ℕ) : ℝ) := by
      rw [sub_le_iff_le_add, div_le_iff₀ hn0]
      linarith
    have h3 := mul_le_mul_of_nonneg_left h2 (ArithmeticFunction.vonMangoldt_nonneg (n := n))
    calc N * (Λ n / n) - Λ n = Λ n * ((N : ℝ) / n - 1) := by ring
      _ ≤ _ := h3
  have hψ : ∑ n ∈ Ioc 0 N, Λ n ≤ (Real.log 4 + 4) * N := by
    have h := Chebyshev.psi_le_const_mul_self (x := (N : ℝ)) (by positivity)
    simpa [Chebyshev.psi] using h
  have hfl : N * Real.log N - N ≤ ∑ n ∈ Ioc 0 N, Real.log n := Real.le_sum_log_nat N
  have hfu : ∑ n ∈ Ioc 0 N, Real.log n ≤ N * Real.log N := by
    have h := Real.sum_log_le' (x := (N : ℝ)) (by exact_mod_cast hN)
    simpa using h
  have hlog4 : Real.log 4 ≤ 2 := by
    have h4 : Real.log 4 = 2 * Real.log 2 := by
      rw [show (4 : ℝ) = 2 ^ (2 : ℕ) by norm_num, Real.log_pow]
      norm_num
    have := Real.log_two_lt_d9
    linarith
  set S := ∑ n ∈ Ioc 0 N, Λ n / n with hS
  rw [abs_le]
  constructor
  · have h : (N : ℝ) * (Real.log N - 1) ≤ N * S := by linarith
    have := le_of_mul_le_mul_left h hNpos
    linarith
  · have h : (N : ℝ) * S ≤ N * (Real.log N + 6) := by nlinarith
    have := le_of_mul_le_mul_left h hNpos
    linarith

theorem A_eq_sum_Ioc (t : ℝ) : A t = ∑ n ∈ Ioc 0 ⌊t⌋₊, Λ n / n := by
  rw [A, ← Finset.add_sum_Ioc_eq_sum_Icc (Nat.zero_le _), lam_zero, zero_add]
  rfl

/-- **Mertens' first theorem**: `|A(t) - ln t| ≤ 7` for `t ≥ 1`. -/
theorem abs_A_sub_log_le {t : ℝ} (ht : 1 ≤ t) : |A t - Real.log t| ≤ 7 := by
  have hN : 1 ≤ ⌊t⌋₊ := Nat.one_le_floor_iff _ |>.mpr ht
  have hNpos : (0 : ℝ) < ⌊t⌋₊ := by exact_mod_cast hN
  have h := abs_sum_lam_sub_log_le ⌊t⌋₊ hN
  rw [← A_eq_sum_Ioc] at h
  have h1 : (⌊t⌋₊ : ℝ) ≤ t := Nat.floor_le (by linarith)
  have h2 : t < ⌊t⌋₊ + 1 := Nat.lt_floor_add_one t
  have h3 : Real.log ⌊t⌋₊ ≤ Real.log t := Real.log_le_log hNpos h1
  have h4 : Real.log t ≤ Real.log ⌊t⌋₊ + 1 := by
    have h5 : t ≤ 2 * ⌊t⌋₊ := by
      have : (1 : ℝ) ≤ ⌊t⌋₊ := by exact_mod_cast hN
      linarith
    have h6 := Real.log_le_log (by linarith) h5
    rw [Real.log_mul (by norm_num) hNpos.ne'] at h6
    have := Real.log_two_lt_d9
    linarith
  rw [abs_le] at h ⊢
  constructor <;> linarith [h.1, h.2]

/-! ### `B(t) - ln ln t` converges -/

/-- `Λ(k) / (k ln k)`. -/
noncomputable def lamLog (k : ℕ) : ℝ := Λ k / (k * Real.log k)

/-- `B(t) = ∑_{k ≤ t} Λ(k) / (k ln k)`. -/
noncomputable def B (t : ℝ) : ℝ := ∑ k ∈ Icc 0 ⌊t⌋₊, lamLog k

theorem lamLog_eq (k : ℕ) : lamLog k = (Real.log k)⁻¹ * lam k := by
  rw [lamLog, lam, ← div_div, div_eq_inv_mul]

theorem lamLog_nonneg (k : ℕ) : 0 ≤ lamLog k := by
  rw [lamLog_eq]
  exact mul_nonneg (inv_nonneg.mpr (Real.log_natCast_nonneg k)) (lam_nonneg k)

/-- The remainder integrand `(A(t) - ln t) / (t ln² t)`. -/
noncomputable def rho (t : ℝ) : ℝ := (A t - Real.log t) * (t⁻¹ / Real.log t ^ 2)

theorem measurable_A : Measurable A :=
  (measurable_from_nat (f := fun n : ℕ => ∑ k ∈ Icc 0 n, lam k)).comp Nat.measurable_floor

theorem integrableOn_inv_div_log_sq :
    IntegrableOn (fun t : ℝ => t⁻¹ / Real.log t ^ 2) (Set.Ioi 2) := by
  have hderiv : ∀ x ∈ Set.Ioi (2 : ℝ),
      HasDerivAt (fun t => -(Real.log t)⁻¹) (x⁻¹ / Real.log x ^ 2) x := by
    intro x hx
    have hx' : (2 : ℝ) < x := hx
    have hd : DifferentiableAt ℝ (fun t => (Real.log t)⁻¹) x :=
      (Real.differentiableAt_log (by linarith)).inv (Real.log_pos (by linarith)).ne'
    have h := hd.hasDerivAt.neg
    rwa [Real.deriv_inv_log_apply, neg_div, neg_neg] at h
  refine integrableOn_Ioi_deriv_of_nonneg (g := fun t => -(Real.log t)⁻¹) (l := 0) ?_ hderiv ?_ ?_
  · exact ((Real.continuousAt_log (by norm_num)).inv₀
      (Real.log_pos (by norm_num)).ne').neg.continuousWithinAt
  · intro x hx
    have hx0 : (0 : ℝ) < x := by linarith [show (2 : ℝ) < x from hx]
    positivity
  · have h : Tendsto (fun t : ℝ => (Real.log t)⁻¹) atTop (𝓝 0) :=
      tendsto_inv_atTop_zero.comp Real.tendsto_log_atTop
    simpa using h.neg

theorem integrableOn_rho : IntegrableOn rho (Set.Ioi 2) := by
  refine Integrable.mono' (integrableOn_inv_div_log_sq.const_mul 7) ?_ ?_
  · exact ((measurable_A.sub Real.measurable_log).mul
      (measurable_inv.div (Real.measurable_log.pow_const 2))).aestronglyMeasurable
  · filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
    have ht2 : (2 : ℝ) < t := ht
    have ht0 : (0 : ℝ) < t := by linarith
    have h7 := abs_A_sub_log_le (t := t) (by linarith)
    have hpos : 0 ≤ t⁻¹ / Real.log t ^ 2 := by positivity
    rw [rho, norm_mul, Real.norm_eq_abs, Real.norm_eq_abs, abs_of_nonneg hpos]
    exact mul_le_mul_of_nonneg_right h7 hpos

/-- Abel summation: `B(b) = A(b) / ln b + ∫_2^b A(t) / (t ln² t) dt`. -/
theorem B_abel (b : ℝ) :
    B b = (Real.log b)⁻¹ * A b + ∫ t in Set.Ioc 2 b, t⁻¹ / Real.log t ^ 2 * A t := by
  have hdiff : ∀ t ∈ Set.Icc 2 b, DifferentiableAt ℝ (fun t : ℝ => (Real.log t)⁻¹) t := by
    intro t ht
    have ht2 : (2 : ℝ) ≤ t := ht.1
    exact (Real.differentiableAt_log (by linarith)).inv (Real.log_pos (by linarith)).ne'
  have hint : IntegrableOn (deriv fun t : ℝ => (Real.log t)⁻¹) (Set.Icc 2 b) := by
    rw [Real.deriv_inv_log]
    refine ContinuousOn.integrableOn_Icc ?_
    refine ContinuousOn.div (ContinuousOn.neg (continuousOn_inv₀.mono ?_))
      ((Real.continuousOn_log.mono ?_).pow 2) ?_
    · intro t ht
      have : (2 : ℝ) ≤ t := ht.1
      simp only [Set.mem_compl_iff, Set.mem_singleton_iff]
      linarith
    · intro t ht
      have : (2 : ℝ) ≤ t := ht.1
      simp only [Set.mem_compl_iff, Set.mem_singleton_iff]
      linarith
    · intro t ht
      have : (2 : ℝ) ≤ t := ht.1
      exact pow_ne_zero 2 (Real.log_pos (by linarith)).ne'
  have h := sum_mul_eq_sub_integral_mul₁ lam lam_zero lam_one b hdiff hint
  have e1 : B b = ∑ k ∈ Icc 0 ⌊b⌋₊, (Real.log k)⁻¹ * lam k :=
    Finset.sum_congr rfl fun k _ => lamLog_eq k
  rw [e1, h, Real.deriv_inv_log]
  have e2 : ∀ t : ℝ, -t⁻¹ / Real.log t ^ 2 * ∑ k ∈ Icc 0 ⌊t⌋₊, lam k
      = -(t⁻¹ / Real.log t ^ 2 * A t) := by
    intro t
    rw [A]
    ring
  simp_rw [e2, integral_neg, sub_neg_eq_add]
  rfl

theorem B_eq {b : ℝ} (hb : 2 ≤ b) :
    B b - Real.log (Real.log b) =
      1 - Real.log (Real.log 2) + (A b - Real.log b) / Real.log b + ∫ t in (2 : ℝ)..b, rho t := by
  have hlogb : 0 < Real.log b := Real.log_pos (by linarith)
  have hcont : ContinuousOn (fun t : ℝ => t⁻¹ / Real.log t) (Set.Icc 2 b) := by
    refine ContinuousOn.div (continuousOn_inv₀.mono ?_) (Real.continuousOn_log.mono ?_) ?_
    · intro t ht
      have : (2 : ℝ) ≤ t := ht.1
      simp only [Set.mem_compl_iff, Set.mem_singleton_iff]
      linarith
    · intro t ht
      have : (2 : ℝ) ≤ t := ht.1
      simp only [Set.mem_compl_iff, Set.mem_singleton_iff]
      linarith
    · intro t ht
      have : (2 : ℝ) ≤ t := ht.1
      exact (Real.log_pos (by linarith)).ne'
  have hsplit : ∫ t in Set.Ioc 2 b, t⁻¹ / Real.log t ^ 2 * A t =
      (∫ t in Set.Ioc 2 b, t⁻¹ / Real.log t) + ∫ t in Set.Ioc 2 b, rho t := by
    rw [← integral_add (hcont.integrableOn_Icc.mono_set Set.Ioc_subset_Icc_self)
      (integrableOn_rho.mono_set Set.Ioc_subset_Ioi_self)]
    refine setIntegral_congr_fun measurableSet_Ioc fun t ht => ?_
    have ht2 : (2 : ℝ) < t := ht.1
    have hl : 0 < Real.log t := Real.log_pos (by linarith)
    simp only [rho]
    field_simp
    ring
  rw [B_abel b, hsplit, ← intervalIntegral.integral_of_le hb, ← intervalIntegral.integral_of_le hb,
    integral_inv_div_log (by norm_num) (by linarith)]
  field_simp
  ring

/-- The limit of `B(t) - ln ln t`. It is Euler's constant (`limit_eq_eulerMascheroni`). -/
noncomputable def limitB : ℝ := 1 - Real.log (Real.log 2) + ∫ t in Set.Ioi 2, rho t

theorem tendsto_B_sub_log_log :
    Tendsto (fun b : ℝ => B b - Real.log (Real.log b)) atTop (𝓝 limitB) := by
  have h1 : Tendsto (fun b : ℝ => (A b - Real.log b) / Real.log b) atTop (𝓝 0) := by
    refine squeeze_zero_norm' ?_
      ((tendsto_const_nhds (x := (7 : ℝ))).div_atTop Real.tendsto_log_atTop)
    filter_upwards [eventually_ge_atTop 2] with b hb
    have hl : 0 < Real.log b := Real.log_pos (by linarith)
    rw [norm_div, Real.norm_eq_abs, Real.norm_eq_abs, abs_of_pos hl]
    exact div_le_div_of_nonneg_right (abs_A_sub_log_le (by linarith)) hl.le
  have h2 : Tendsto (fun b : ℝ => ∫ t in (2 : ℝ)..b, rho t) atTop
      (𝓝 (∫ t in Set.Ioi 2, rho t)) :=
    intervalIntegral_tendsto_integral_Ioi 2 integrableOn_rho tendsto_id
  have h3 := ((tendsto_const_nhds (x := 1 - Real.log (Real.log 2))).add h1).add h2
  rw [add_zero] at h3
  refine h3.congr' ?_
  filter_upwards [eventually_ge_atTop 2] with b hb
  rw [B_eq hb]

theorem exists_bound_B_sub_log_log :
    ∃ K : ℝ, ∀ b : ℝ, 2 ≤ b → |B b - Real.log (Real.log b)| ≤ K := by
  refine ⟨|1 - Real.log (Real.log 2)| + 7 / Real.log 2 + ∫ t in Set.Ioi 2, ‖rho t‖,
    fun b hb => ?_⟩
  rw [B_eq hb]
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  have hl : Real.log 2 ≤ Real.log b := Real.log_le_log (by norm_num) hb
  have h1 : |(A b - Real.log b) / Real.log b| ≤ 7 / Real.log 2 := by
    rw [abs_div, abs_of_pos (by linarith : 0 < Real.log b)]
    exact div_le_div₀ (by norm_num) (abs_A_sub_log_le (by linarith)) hl2 hl
  have h2 : |∫ t in (2 : ℝ)..b, rho t| ≤ ∫ t in Set.Ioi 2, ‖rho t‖ := by
    rw [intervalIntegral.integral_of_le hb]
    calc |∫ t in Set.Ioc 2 b, rho t| ≤ ∫ t in Set.Ioc 2 b, ‖rho t‖ :=
          norm_integral_le_integral_norm _
      _ ≤ ∫ t in Set.Ioi 2, ‖rho t‖ :=
          setIntegral_mono_set integrableOn_rho.norm (ae_of_all _ fun t => norm_nonneg _)
            (Filter.Eventually.of_forall fun _ hx => Set.Ioc_subset_Ioi_self hx)
  calc _ ≤ |1 - Real.log (Real.log 2)| + |(A b - Real.log b) / Real.log b|
        + |∫ t in (2 : ℝ)..b, rho t| := abs_add_three _ _ _
    _ ≤ _ := by linarith

/-! ### `ln ζ(s) = (s - 1) ∫_1^∞ B(t) t^{-s} dt` -/

theorem B_nonneg (t : ℝ) : 0 ≤ B t := Finset.sum_nonneg fun k _ => lamLog_nonneg k

theorem B_le {t : ℝ} (ht : 1 ≤ t) : B t ≤ (Real.log t + 7) / Real.log 2 := by
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  have h1 : B t ≤ (Real.log 2)⁻¹ * A t := by
    rw [B, A, Finset.mul_sum]
    refine Finset.sum_le_sum fun k _ => ?_
    rw [lamLog_eq]
    rcases Nat.lt_or_ge k 2 with hk | hk
    · interval_cases k <;> simp [lam_zero, lam_one]
    · have h : Real.log 2 ≤ Real.log k := Real.log_le_log (by norm_num) (by exact_mod_cast hk)
      exact mul_le_mul_of_nonneg_right (inv_anti₀ hl2 h) (lam_nonneg k)
  have h2 := (abs_le.mp (abs_A_sub_log_le ht)).2
  calc B t ≤ (Real.log 2)⁻¹ * A t := h1
    _ ≤ (Real.log 2)⁻¹ * (Real.log t + 7) :=
        mul_le_mul_of_nonneg_left (by linarith) (inv_nonneg.mpr hl2.le)
    _ = _ := by rw [inv_mul_eq_div]

theorem B_le_rpow {σ t : ℝ} (hσ : 0 < σ) (ht : 1 ≤ t) :
    B t ≤ (2 / σ + 7) / Real.log 2 * t ^ (σ / 2) := by
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  have h2 : Real.log t ≤ t ^ (σ / 2) / (σ / 2) := Real.log_le_rpow_div (by linarith) (by linarith)
  have h3 : (1 : ℝ) ≤ t ^ (σ / 2) := Real.one_le_rpow ht (by linarith)
  have h4 : t ^ (σ / 2) / (σ / 2) = 2 / σ * t ^ (σ / 2) := by
    field_simp
  calc B t ≤ (Real.log t + 7) / Real.log 2 := B_le ht
    _ ≤ ((2 / σ + 7) * t ^ (σ / 2)) / Real.log 2 :=
        div_le_div_of_nonneg_right (by nlinarith) hl2.le
    _ = _ := by ring

theorem measurable_B : Measurable B :=
  (measurable_from_nat (f := fun n : ℕ => ∑ k ∈ Icc 0 n, lamLog k)).comp Nat.measurable_floor

theorem B_mul_rpow_le {s t : ℝ} (hs : 1 < s) (ht : 1 ≤ t) :
    B t * t ^ (-s) ≤ (2 / (s - 1) + 7) / Real.log 2 * t ^ (-1 - (s - 1) / 2) := by
  have ht0 : 0 < t := by linarith
  calc B t * t ^ (-s) ≤ (2 / (s - 1) + 7) / Real.log 2 * t ^ ((s - 1) / 2) * t ^ (-s) :=
        mul_le_mul_of_nonneg_right (B_le_rpow (by linarith) ht) (Real.rpow_nonneg ht0.le _)
    _ = (2 / (s - 1) + 7) / Real.log 2 * t ^ (-1 - (s - 1) / 2) := by
        rw [mul_assoc, ← Real.rpow_add ht0]
        congr 2
        ring

theorem integrableOn_B_mul_rpow {s : ℝ} (hs : 1 < s) :
    IntegrableOn (fun t : ℝ => B t * t ^ (-s)) (Set.Ioi 1) := by
  refine Integrable.mono' ((integrableOn_Ioi_rpow_of_lt (a := -1 - (s - 1) / 2) (by linarith)
    zero_lt_one).const_mul ((2 / (s - 1) + 7) / Real.log 2)) ?_ ?_
  · exact (measurable_B.mul (measurable_id.pow_const _)).aestronglyMeasurable
  · filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
    have ht1 : (1 : ℝ) < t := ht
    have ht0 : 0 < t := by linarith
    rw [norm_mul, Real.norm_eq_abs, Real.norm_eq_abs, abs_of_nonneg (B_nonneg t),
      abs_of_nonneg (Real.rpow_nonneg ht0.le _)]
    exact B_mul_rpow_le hs ht1.le

/-- For `s > 1`, `ln ζ(s) = (s - 1) ∫_1^∞ B(t) t^{-s} dt` (Abel summation of
`∑ Λ(n) / (n^s ln n)`). -/
theorem log_zeta_eq_integral {s : ℝ} (hs : 1 < s) :
    Real.log (riemannZeta (s : ℂ)).re = (s - 1) * ∫ t in Set.Ioi 1, B t * t ^ (-s) := by
  have hσ0 : 0 < s - 1 := by linarith
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  have hf_diff : ∀ t ∈ Set.Ici (1 : ℝ), DifferentiableAt ℝ (fun t : ℝ => t ^ (-(s - 1))) t :=
    fun t ht => Real.differentiableAt_rpow_const_of_ne _
      (by have : (1 : ℝ) ≤ t := ht; linarith)
  have hderiv : ∀ t : ℝ, deriv (fun t : ℝ => t ^ (-(s - 1))) t = -(s - 1) * t ^ (-s) := by
    intro t
    rw [Real.deriv_rpow_const]
    congr 2
    ring
  have hf_int : LocallyIntegrableOn (deriv fun t : ℝ => t ^ (-(s - 1))) (Set.Ici 1) := by
    refine ContinuousOn.locallyIntegrableOn ?_ measurableSet_Ici
    refine ContinuousOn.congr (f := fun t : ℝ => -(s - 1) * t ^ (-s)) ?_ (fun t _ => hderiv t)
    exact continuousOn_const.mul (ContinuousOn.rpow_const continuousOn_id
      (fun t ht => Or.inl (by have : (1 : ℝ) ≤ t := ht; exact (show (0 : ℝ) < t by linarith).ne')))
  have h_lim : Tendsto (fun n : ℕ => (n : ℝ) ^ (-(s - 1)) * ∑ k ∈ Icc 0 n, lamLog k) atTop
      (𝓝 0) := by
    have hg : Tendsto (fun n : ℕ => (2 / (s - 1) + 7) / Real.log 2 * (n : ℝ) ^ (-((s - 1) / 2)))
        atTop (𝓝 0) := by
      have h := (tendsto_rpow_neg_atTop (by linarith : 0 < (s - 1) / 2)).comp
        tendsto_natCast_atTop_atTop
      simpa using h.const_mul ((2 / (s - 1) + 7) / Real.log 2)
    refine squeeze_zero' ?_ ?_ hg
    · filter_upwards with n
      exact mul_nonneg (Real.rpow_nonneg (Nat.cast_nonneg n) _)
        (Finset.sum_nonneg fun k _ => lamLog_nonneg k)
    · filter_upwards [eventually_ge_atTop 1] with n hn
      have hn1 : (1 : ℝ) ≤ n := by exact_mod_cast hn
      have hn0 : (0 : ℝ) < n := by linarith
      have hB : ∑ k ∈ Icc 0 n, lamLog k = B n := by rw [B, Nat.floor_natCast]
      rw [hB]
      calc (n : ℝ) ^ (-(s - 1)) * B n
          ≤ (n : ℝ) ^ (-(s - 1)) * ((2 / (s - 1) + 7) / Real.log 2 * (n : ℝ) ^ ((s - 1) / 2)) :=
            mul_le_mul_of_nonneg_left (B_le_rpow hσ0 hn1) (Real.rpow_nonneg hn0.le _)
        _ = (2 / (s - 1) + 7) / Real.log 2 * (n : ℝ) ^ (-((s - 1) / 2)) := by
            rw [mul_left_comm, ← Real.rpow_add hn0]
            congr 2
            ring
  have hg_dom : (fun t : ℝ => deriv (fun t : ℝ => t ^ (-(s - 1))) t * ∑ k ∈ Icc 0 ⌊t⌋₊, lamLog k)
      =O[atTop] fun t : ℝ => t ^ (-1 - (s - 1) / 2) := by
    refine Asymptotics.IsBigO.of_bound ((s - 1) * ((2 / (s - 1) + 7) / Real.log 2)) ?_
    filter_upwards [eventually_ge_atTop 1] with t ht
    have ht0 : 0 < t := by linarith
    have hB : ∑ k ∈ Icc 0 ⌊t⌋₊, lamLog k = B t := rfl
    rw [hB, hderiv, norm_mul, norm_mul, Real.norm_eq_abs, Real.norm_eq_abs, Real.norm_eq_abs,
      Real.norm_eq_abs, abs_neg, abs_of_pos hσ0, abs_of_nonneg (Real.rpow_nonneg ht0.le _),
      abs_of_nonneg (B_nonneg t), abs_of_nonneg (Real.rpow_nonneg ht0.le _)]
    have h := B_mul_rpow_le hs ht
    calc (s - 1) * t ^ (-s) * B t = (s - 1) * (B t * t ^ (-s)) := by ring
      _ ≤ (s - 1) * ((2 / (s - 1) + 7) / Real.log 2 * t ^ (-1 - (s - 1) / 2)) :=
          mul_le_mul_of_nonneg_left h hσ0.le
      _ = _ := by ring
  have hg_int : IntegrableAtFilter (fun t : ℝ => t ^ (-1 - (s - 1) / 2)) atTop :=
    integrableAtFilter_rpow_atTop_iff.mpr (by linarith)
  have hT := tendsto_sum_mul_atTop_nhds_one_sub_integral₀ lamLog (by simp [lamLog]) hf_diff hf_int
    h_lim hg_dom hg_int
  have hval : (0 : ℝ) - ∫ t in Set.Ioi 1,
      deriv (fun t : ℝ => t ^ (-(s - 1))) t * ∑ k ∈ Icc 0 ⌊t⌋₊, lamLog k
      = (s - 1) * ∫ t in Set.Ioi 1, B t * t ^ (-s) := by
    rw [zero_sub, ← integral_neg, ← integral_const_mul]
    refine setIntegral_congr_fun measurableSet_Ioi fun t _ => ?_
    simp only [hderiv, B]
    ring
  rw [hval] at hT
  have hterm : ∀ k : ℕ, (k : ℝ) ^ (-(s - 1)) * lamLog k = Λ k / ((k : ℝ) ^ s * Real.log k) := by
    intro k
    rcases Nat.lt_or_ge k 2 with hk | hk
    · interval_cases k <;> simp [lamLog]
    · have hk0 : (0 : ℝ) < k := by positivity
      have hlk : 0 < Real.log k := Real.log_pos (by exact_mod_cast hk)
      have e : (k : ℝ) ^ s = (k : ℝ) ^ (s - 1) * k := by
        rw [← Real.rpow_add_one hk0.ne']
        congr 1
        ring
      rw [lamLog, e, Real.rpow_neg hk0.le]
      have : (0 : ℝ) < (k : ℝ) ^ (s - 1) := Real.rpow_pos_of_pos hk0 _
      field_simp
  have hnn : ∀ k : ℕ, 0 ≤ Λ k / ((k : ℝ) ^ s * Real.log k) := fun k =>
    div_nonneg ArithmeticFunction.vonMangoldt_nonneg
      (mul_nonneg (Real.rpow_nonneg (Nat.cast_nonneg k) _) (Real.log_natCast_nonneg k))
  have hsum : HasSum (fun k : ℕ => Λ k / ((k : ℝ) ^ s * Real.log k))
      ((s - 1) * ∫ t in Set.Ioi 1, B t * t ^ (-s)) := by
    rw [hasSum_iff_tendsto_nat_of_nonneg hnn, ← tendsto_add_atTop_iff_nat 1]
    refine hT.congr fun n => ?_
    rw [Nat.range_succ_eq_Icc_zero]
    exact Finset.sum_congr rfl fun k _ => hterm k
  rw [log_riemannZeta_eq hs, hsum.tsum_eq]

/-! ### The limit is Euler's constant -/

theorem integrableOn_log_log_Ioc (T : ℝ) :
    IntegrableOn (fun t : ℝ => Real.log (Real.log t)) (Set.Ioc 1 T) := by
  have h2 := (Real.integrableOn_log_log_mul_rpow (s := 2) one_lt_two).mono_set
    (Set.Ioc_subset_Ioi_self : Set.Ioc (1 : ℝ) T ⊆ Set.Ioi 1)
  refine Integrable.mono' ((h2.norm).const_mul (T ^ (2 : ℝ))) ?_ ?_
  · exact (Real.measurable_log.comp Real.measurable_log).aestronglyMeasurable
  · filter_upwards [ae_restrict_mem measurableSet_Ioc] with t ht
    have ht1 : (1 : ℝ) < t := ht.1
    have htT : t ≤ T := ht.2
    have ht0 : 0 < t := by linarith
    have hT0 : 0 < T := by linarith
    have h1 : (1 : ℝ) ≤ T ^ (2 : ℝ) * t ^ (-(2 : ℝ)) := by
      rw [Real.rpow_neg ht0.le, ← div_eq_mul_inv, le_div_iff₀ (Real.rpow_pos_of_pos ht0 _), one_mul]
      exact Real.rpow_le_rpow ht0.le htT (by norm_num)
    rw [norm_mul, Real.norm_eq_abs (t ^ (-(2 : ℝ))), abs_of_nonneg (Real.rpow_nonneg ht0.le _)]
    calc ‖Real.log (Real.log t)‖ = ‖Real.log (Real.log t)‖ * 1 := (mul_one _).symm
      _ ≤ ‖Real.log (Real.log t)‖ * (T ^ (2 : ℝ) * t ^ (-(2 : ℝ))) :=
          mul_le_mul_of_nonneg_left h1 (norm_nonneg _)
      _ = T ^ (2 : ℝ) * (‖Real.log (Real.log t)‖ * t ^ (-(2 : ℝ))) := by ring

theorem integrableOn_B_Ioc (T : ℝ) : IntegrableOn B (Set.Ioc 1 T) := by
  refine Measure.integrableOn_of_bounded (M := (Real.log T + 7) / Real.log 2)
    measure_Ioc_lt_top.ne measurable_B.aestronglyMeasurable ?_
  filter_upwards [ae_restrict_mem measurableSet_Ioc] with t ht
  have ht1 : (1 : ℝ) < t := ht.1
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  rw [Real.norm_eq_abs, abs_of_nonneg (B_nonneg t)]
  refine (B_le ht1.le).trans (div_le_div_of_nonneg_right ?_ hl2.le)
  have := Real.log_le_log (by linarith) ht.2
  linarith

/-- The Abelian step: `(s - 1) ∫_1^∞ (B(t) - ln ln t) t^{-s} dt → lim (B(t) - ln ln t)` as
`s → 1` from above. -/
theorem tendsto_abel :
    Tendsto (fun s : ℝ => (s - 1) * ∫ t in Set.Ioi 1, (B t - Real.log (Real.log t)) * t ^ (-s))
      (𝓝[>] 1) (𝓝 limitB) := by
  rw [Metric.tendsto_nhds]
  intro ε hε
  obtain ⟨T, hT2, hT⟩ : ∃ T : ℝ, 2 ≤ T ∧
      ∀ t, T ≤ t → |B t - Real.log (Real.log t) - limitB| ≤ ε / 4 := by
    have h := tendsto_B_sub_log_log.eventually
      (Metric.closedBall_mem_nhds limitB (by positivity : 0 < ε / 4))
    obtain ⟨T₀, hT₀⟩ := eventually_atTop.mp h
    refine ⟨max T₀ 2, le_max_right _ _, fun t ht => ?_⟩
    have h1 := hT₀ t (le_trans (le_max_left _ _) ht)
    rwa [Real.dist_eq] at h1
  have hT1 : (1 : ℝ) ≤ T := by linarith
  have hT0 : (0 : ℝ) < T := by linarith
  -- the part of the integral below `T`
  have hintK : IntegrableOn (fun t : ℝ => |B t - Real.log (Real.log t) - limitB|) (Set.Ioc 1 T) :=
    (((integrableOn_B_Ioc T).sub (integrableOn_log_log_Ioc T)).sub
      (integrableOn_const (C := limitB) (hs := measure_Ioc_lt_top.ne))).norm
  set K := ∫ t in Set.Ioc 1 T, |B t - Real.log (Real.log t) - limitB| with hK
  have hK0 : 0 ≤ K := integral_nonneg fun t => abs_nonneg _
  have hev : ∀ᶠ s : ℝ in 𝓝[>] 1, 1 < s ∧ (s - 1) * K < ε / 4 := by
    have hc : ContinuousAt (fun s : ℝ => (s - 1) * K) 1 := by fun_prop
    have h0 : (fun s : ℝ => (s - 1) * K) 1 < ε / 4 := by
      simp only [sub_self, zero_mul]
      positivity
    have h1 : ∀ᶠ s : ℝ in 𝓝 1, (s - 1) * K < ε / 4 := hc.eventually_lt continuousAt_const h0
    filter_upwards [eventually_mem_nhdsWithin, nhdsWithin_le_nhds h1] with s hs1 hs2
    exact ⟨hs1, hs2⟩
  filter_upwards [hev] with s ⟨hs1, hsK⟩
  have hσ : 0 < s - 1 := by linarith
  rw [Real.dist_eq]
  -- integrability
  have hI1 : IntegrableOn (fun t : ℝ => (B t - Real.log (Real.log t)) * t ^ (-s)) (Set.Ioi 1) := by
    have := (integrableOn_B_mul_rpow hs1).sub (Real.integrableOn_log_log_mul_rpow hs1)
    refine this.congr (Eventually.of_forall fun t => ?_)
    simp only [Pi.sub_apply]
    ring
  have hI2 : IntegrableOn (fun t : ℝ => t ^ (-s)) (Set.Ioi 1) :=
    integrableOn_Ioi_rpow_of_lt (by linarith) zero_lt_one
  have hI3 : IntegrableOn (fun t : ℝ => (B t - Real.log (Real.log t) - limitB) * t ^ (-s))
      (Set.Ioi 1) := by
    have := hI1.sub (hI2.const_mul limitB)
    refine this.congr (Eventually.of_forall fun t => ?_)
    simp only [Pi.sub_apply]
    ring
  have hint1 : ∫ t in Set.Ioi 1, t ^ (-s) = 1 / (s - 1) := by
    rw [integral_Ioi_rpow_of_lt (by linarith) zero_lt_one, Real.one_rpow]
    rw [neg_div, ← div_neg]
    congr 1
    ring
  have key : (s - 1) * (∫ t in Set.Ioi 1, (B t - Real.log (Real.log t)) * t ^ (-s)) - limitB
      = (s - 1) * ∫ t in Set.Ioi 1, (B t - Real.log (Real.log t) - limitB) * t ^ (-s) := by
    have e : ∫ t in Set.Ioi 1, (B t - Real.log (Real.log t) - limitB) * t ^ (-s)
        = (∫ t in Set.Ioi 1, (B t - Real.log (Real.log t)) * t ^ (-s))
          - limitB * ∫ t in Set.Ioi 1, t ^ (-s) := by
      rw [← integral_const_mul, ← integral_sub hI1 (hI2.const_mul limitB)]
      refine integral_congr_ae (Eventually.of_forall fun t => ?_)
      simp only
      ring
    rw [e, hint1]
    field_simp
  rw [key]
  -- split at `T`
  have hsplit : ∫ t in Set.Ioi 1, (B t - Real.log (Real.log t) - limitB) * t ^ (-s)
      = (∫ t in Set.Ioc 1 T, (B t - Real.log (Real.log t) - limitB) * t ^ (-s))
        + ∫ t in Set.Ioi T, (B t - Real.log (Real.log t) - limitB) * t ^ (-s) := by
    rw [← setIntegral_union (Set.Ioc_disjoint_Ioi le_rfl) measurableSet_Ioi
      (hI3.mono_set Set.Ioc_subset_Ioi_self) (hI3.mono_set (Set.Ioi_subset_Ioi hT1)),
      Set.Ioc_union_Ioi_eq_Ioi hT1]
  have hb1 : |∫ t in Set.Ioc 1 T, (B t - Real.log (Real.log t) - limitB) * t ^ (-s)| ≤ K := by
    rw [← Real.norm_eq_abs]
    refine norm_integral_le_of_norm_le hintK ?_
    filter_upwards [ae_restrict_mem measurableSet_Ioc] with t ht
    have ht1 : (1 : ℝ) < t := ht.1
    have ht0 : 0 < t := by linarith
    rw [norm_mul, Real.norm_eq_abs, Real.norm_eq_abs, abs_of_nonneg (Real.rpow_nonneg ht0.le _)]
    exact mul_le_of_le_one_right (abs_nonneg _)
      (Real.rpow_le_one_of_one_le_of_nonpos ht1.le (by linarith))
  have hI4 : IntegrableOn (fun t : ℝ => t ^ (-s)) (Set.Ioi T) :=
    integrableOn_Ioi_rpow_of_lt (by linarith) hT0
  have hint2 : ∫ t in Set.Ioi T, t ^ (-s) ≤ 1 / (s - 1) := by
    rw [integral_Ioi_rpow_of_lt (by linarith) hT0, neg_div, ← div_neg]
    have e : -(-s + 1) = s - 1 := by ring
    rw [e]
    exact div_le_div_of_nonneg_right
      (Real.rpow_le_one_of_one_le_of_nonpos hT1 (by linarith)) hσ.le
  have hb2 : |∫ t in Set.Ioi T, (B t - Real.log (Real.log t) - limitB) * t ^ (-s)|
      ≤ ε / 4 * (1 / (s - 1)) := by
    have h1 : ‖∫ t in Set.Ioi T, (B t - Real.log (Real.log t) - limitB) * t ^ (-s)‖
        ≤ ∫ t in Set.Ioi T, ε / 4 * t ^ (-s) := by
      refine norm_integral_le_of_norm_le (hI4.const_mul (ε / 4)) ?_
      filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
      have htT : T < t := ht
      have ht0 : 0 < t := by linarith
      rw [norm_mul, Real.norm_eq_abs, Real.norm_eq_abs, abs_of_nonneg (Real.rpow_nonneg ht0.le _)]
      exact mul_le_mul_of_nonneg_right (hT t htT.le) (Real.rpow_nonneg ht0.le _)
    rw [integral_const_mul] at h1
    exact h1.trans (mul_le_mul_of_nonneg_left hint2 (by positivity))
  rw [hsplit, abs_mul, abs_of_pos hσ]
  calc (s - 1) * |(∫ t in Set.Ioc 1 T, (B t - Real.log (Real.log t) - limitB) * t ^ (-s))
          + ∫ t in Set.Ioi T, (B t - Real.log (Real.log t) - limitB) * t ^ (-s)|
      ≤ (s - 1) * (K + ε / 4 * (1 / (s - 1))) :=
        mul_le_mul_of_nonneg_left ((abs_add_le _ _).trans (add_le_add hb1 hb2)) hσ.le
    _ = (s - 1) * K + ε / 4 := by
        field_simp
    _ < ε := by linarith

/-- `ln ζ(s) + ln (s - 1) → 0` as `s → 1` from above. -/
theorem tendsto_log_zeta_add_log :
    Tendsto (fun s : ℝ => Real.log (riemannZeta (s : ℂ)).re + Real.log (s - 1)) (𝓝[>] 1)
      (𝓝 0) := by
  have hc : Tendsto (fun s : ℝ => (s : ℂ)) (𝓝[>] 1) (𝓝[≠] 1) := by
    refine tendsto_nhdsWithin_of_tendsto_nhds_of_eventually_within _ ?_ ?_
    · have h := (Complex.continuous_ofReal.tendsto (1 : ℝ)).mono_left
        (nhdsWithin_le_nhds (s := Set.Ioi (1 : ℝ)))
      simpa using h
    · filter_upwards [eventually_mem_nhdsWithin] with s hs
      have hs1 : (1 : ℝ) < s := hs
      simp only [Set.mem_compl_iff, Set.mem_singleton_iff]
      intro h
      have : s = 1 := by exact_mod_cast h
      linarith
  have h1 : Tendsto (fun s : ℝ => (s - 1) * (riemannZeta (s : ℂ)).re) (𝓝[>] 1) (𝓝 1) := by
    have h := (Complex.continuous_re.tendsto _).comp (riemannZeta_residue_one.comp hc)
    simp only [Complex.one_re] at h
    refine h.congr fun s => ?_
    simp only [Function.comp_apply]
    rw [show ((s : ℂ) - 1) = ((s - 1 : ℝ) : ℂ) by push_cast; ring, Complex.re_ofReal_mul]
  have h2 : Tendsto (fun s : ℝ => Real.log ((s - 1) * (riemannZeta (s : ℂ)).re)) (𝓝[>] 1)
      (𝓝 0) := by
    have h := (Real.continuousAt_log one_ne_zero).tendsto.comp h1
    rw [Real.log_one] at h
    exact h
  refine h2.congr' ?_
  have hpos : ∀ᶠ s : ℝ in 𝓝[>] 1, 0 < (s - 1) * (riemannZeta (s : ℂ)).re :=
    h1.eventually (lt_mem_nhds zero_lt_one)
  filter_upwards [hpos, eventually_mem_nhdsWithin] with s hs hs1
  have hs1' : (1 : ℝ) < s := hs1
  have hσ : 0 < s - 1 := by linarith
  have hz : (riemannZeta (s : ℂ)).re ≠ 0 := by
    intro h0
    rw [h0, mul_zero] at hs
    exact lt_irrefl _ hs
  rw [Real.log_mul hσ.ne' hz]
  ring

/-- The limit of `B(t) - ln ln t` is Euler's constant. -/
theorem limit_eq_eulerMascheroni : limitB = Real.eulerMascheroniConstant := by
  have hH : ∀ s : ℝ, 1 < s →
      (s - 1) * ∫ t in Set.Ioi 1, (B t - Real.log (Real.log t)) * t ^ (-s)
        = Real.log (riemannZeta (s : ℂ)).re + Real.log (s - 1) + Real.eulerMascheroniConstant := by
    intro s hs
    have hJ := Real.eulerMascheroniConstant_eq_neg_integral_log_log hs
    have hI := log_zeta_eq_integral hs
    have e : ∫ t in Set.Ioi 1, (B t - Real.log (Real.log t)) * t ^ (-s)
        = (∫ t in Set.Ioi 1, B t * t ^ (-s))
          - ∫ t in Set.Ioi 1, Real.log (Real.log t) * t ^ (-s) := by
      rw [← integral_sub (integrableOn_B_mul_rpow hs) (Real.integrableOn_log_log_mul_rpow hs)]
      refine integral_congr_ae (Eventually.of_forall fun t => ?_)
      simp only
      ring
    rw [e, mul_sub, ← hI]
    linarith
  have h2 : Tendsto (fun s : ℝ => Real.log (riemannZeta (s : ℂ)).re + Real.log (s - 1)
      + Real.eulerMascheroniConstant) (𝓝[>] 1) (𝓝 (0 + Real.eulerMascheroniConstant)) :=
    tendsto_log_zeta_add_log.add_const _
  have h3 : Tendsto (fun s : ℝ => (s - 1) * ∫ t in Set.Ioi 1,
      (B t - Real.log (Real.log t)) * t ^ (-s)) (𝓝[>] 1)
      (𝓝 (0 + Real.eulerMascheroniConstant)) := by
    refine h2.congr' ?_
    filter_upwards [eventually_mem_nhdsWithin] with s hs
    exact (hH s hs).symm
  have h := tendsto_nhds_unique tendsto_abel h3
  rw [zero_add] at h
  exact h

/-! ### From prime powers to the product over primes -/

theorem lamLog_prime_pow {p : ℕ} (hp : p.Prime) (i : ℕ) :
    lamLog (p ^ (i + 1)) = ((p : ℝ)⁻¹) ^ (i + 1) / (i + 1) := by
  have hp1 : (1 : ℝ) < p := by exact_mod_cast hp.one_lt
  have hlp : 0 < Real.log p := Real.log_pos hp1
  have hp0 : (0 : ℝ) < p := by linarith
  rw [lamLog, ArithmeticFunction.vonMangoldt_apply_pow (Nat.succ_ne_zero i),
    ArithmeticFunction.vonMangoldt_apply_prime hp, Nat.cast_pow, Real.log_pow, inv_pow]
  push_cast
  field_simp

/-- `B(w)` regrouped prime by prime: the prime powers `p^k ≤ w` are the `p^(i+1)` with
`i < log_p w`. -/
theorem B_natCast_eq (w : ℕ) :
    B w = ∑ p ∈ Nat.primesLE w, ∑ i ∈ range (Nat.log p w), lamLog (p ^ (i + 1)) := by
  rw [B, Nat.floor_natCast, Finset.sum_sigma']
  symm
  refine Finset.sum_bij_ne_zero (fun x _ _ => x.1 ^ (x.2 + 1)) ?_ ?_ ?_ ?_
  · rintro ⟨p, i⟩ hx _
    simp only [Finset.mem_sigma, Nat.mem_primesLE, Finset.mem_range] at hx
    obtain ⟨⟨hpw, hp⟩, hi⟩ := hx
    have hw0 : w ≠ 0 := by have := hp.two_le; omega
    simp only [Finset.mem_Icc, Nat.zero_le, true_and]
    exact (Nat.pow_le_pow_right hp.pos hi).trans (Nat.pow_log_le_self p hw0)
  · rintro ⟨p₁, i₁⟩ h₁ _ ⟨p₂, i₂⟩ h₂ _ heq
    simp only [Finset.mem_sigma, Nat.mem_primesLE, Finset.mem_range] at h₁ h₂
    obtain ⟨hpp, hii⟩ := h₁.1.2.pow_inj' h₂.1.2 (Nat.succ_ne_zero _) (Nat.succ_ne_zero _) heq
    have hii' : i₁ = i₂ := Nat.succ.inj hii
    subst hpp
    subst hii'
    rfl
  · intro n hn hne
    have hΛ : Λ n ≠ 0 := by
      intro h0
      apply hne
      simp [lamLog, h0]
    obtain ⟨p, k, hp, hk, rfl⟩ :=
      (isPrimePow_nat_iff n).mp (ArithmeticFunction.vonMangoldt_ne_zero_iff.mp hΛ)
    have hle : p ^ k ≤ w := (Finset.mem_Icc.mp hn).2
    have hpw : p ≤ w := (Nat.le_self_pow hk.ne' p).trans hle
    have hkL : k ≤ Nat.log p w := Nat.le_log_of_pow_le hp.one_lt hle
    have hk1 : k - 1 + 1 = k := Nat.sub_add_cancel hk
    refine ⟨⟨p, k - 1⟩, ?_, ?_, ?_⟩
    · simp only [Finset.mem_sigma, Nat.mem_primesLE, Finset.mem_range]
      exact ⟨⟨hpw, hp⟩, by omega⟩
    · simpa only [hk1] using hne
    · simp only [hk1]
  · intro a _ _
    rfl

theorem abs_sum_lamLog_add_log_le {p : ℕ} (hp : p.Prime) (L : ℕ) :
    |(∑ i ∈ range L, lamLog (p ^ (i + 1))) + Real.log (1 - (p : ℝ)⁻¹)|
      ≤ 2 * ((p : ℝ)⁻¹) ^ (L + 1) := by
  have hp2 : (2 : ℝ) ≤ p := by exact_mod_cast hp.two_le
  have hx0 : 0 < (p : ℝ)⁻¹ := by positivity
  have hx1 : (p : ℝ)⁻¹ ≤ 1 / 2 := by
    rw [inv_eq_one_div]
    exact one_div_le_one_div_of_le (by norm_num) hp2
  have habs : |(p : ℝ)⁻¹| < 1 := by
    rw [abs_of_pos hx0]
    linarith
  have h := Real.abs_log_sub_add_sum_range_le habs L
  rw [abs_of_pos hx0] at h
  have e : ∑ i ∈ range L, lamLog (p ^ (i + 1))
      = ∑ i ∈ range L, ((p : ℝ)⁻¹) ^ (i + 1) / (i + 1) :=
    Finset.sum_congr rfl fun i _ => lamLog_prime_pow hp i
  rw [e]
  refine h.trans ?_
  rw [div_le_iff₀ (by linarith)]
  have h0 : 0 ≤ ((p : ℝ)⁻¹) ^ (L + 1) := by positivity
  nlinarith [mul_nonneg h0 (by linarith : (0 : ℝ) ≤ 1 / 2 - (p : ℝ)⁻¹)]

theorem inv_pow_log_succ_le {p w : ℕ} (hp : p.Prime) (hpw : p ≤ w) :
    ((p : ℝ)⁻¹) ^ (Nat.log p w + 1) ≤ (p : ℝ)⁻¹ * (Real.sqrt w)⁻¹ := by
  have hL1 : 1 ≤ Nat.log p w := Nat.log_pos hp.one_lt hpw
  have hp0 : (0 : ℝ) < p := by exact_mod_cast hp.pos
  have hw0 : (0 : ℝ) < w := by exact_mod_cast (hp.pos.trans_le hpw)
  have hlt : w < p ^ (Nat.log p w + 1) := Nat.lt_pow_succ_log_self hp.one_lt w
  have hsq : (w : ℝ) ≤ ((p : ℝ) ^ Nat.log p w) ^ 2 := by
    have h1 : p ^ (Nat.log p w + 1) ≤ (p ^ Nat.log p w) ^ 2 := by
      rw [← pow_mul]
      exact Nat.pow_le_pow_right hp.pos (by omega)
    exact_mod_cast hlt.le.trans h1
  have hsqrt : Real.sqrt w ≤ (p : ℝ) ^ Nat.log p w :=
    (Real.sqrt_le_left (by positivity)).mpr hsq
  have hs0 : 0 < Real.sqrt w := Real.sqrt_pos.mpr hw0
  rw [pow_succ', inv_pow]
  exact mul_le_mul_of_nonneg_left (inv_anti₀ hs0 hsqrt) (inv_nonneg.mpr hp0.le)

theorem sum_primesLE_inv_le (w : ℕ) (hw : 1 ≤ w) :
    ∑ p ∈ Nat.primesLE w, (p : ℝ)⁻¹ ≤ (Real.log w + 7) / Real.log 2 := by
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  have h1 : ∑ p ∈ Nat.primesLE w, (p : ℝ)⁻¹ ≤ ∑ p ∈ Nat.primesLE w, lam p / Real.log 2 := by
    refine Finset.sum_le_sum fun p hp => ?_
    have hpp := (Nat.mem_primesLE.mp hp).2
    have hp2 : (2 : ℝ) ≤ p := by exact_mod_cast hpp.two_le
    have hp0 : (0 : ℝ) < p := by linarith
    rw [lam, ArithmeticFunction.vonMangoldt_apply_prime hpp, le_div_iff₀ hl2, inv_mul_eq_div]
    exact div_le_div_of_nonneg_right (Real.log_le_log (by norm_num) hp2) hp0.le
  have h2 : ∑ p ∈ Nat.primesLE w, lam p ≤ A w := by
    rw [A, Nat.floor_natCast]
    refine Finset.sum_le_sum_of_subset_of_nonneg ?_ (fun k _ _ => lam_nonneg k)
    intro p hp
    exact Finset.mem_Icc.mpr ⟨Nat.zero_le _, (Nat.mem_primesLE.mp hp).1⟩
  have h3 := (abs_le.mp (abs_A_sub_log_le (t := (w : ℝ)) (by exact_mod_cast hw))).2
  calc ∑ p ∈ Nat.primesLE w, (p : ℝ)⁻¹ ≤ ∑ p ∈ Nat.primesLE w, lam p / Real.log 2 := h1
    _ = (∑ p ∈ Nat.primesLE w, lam p) / Real.log 2 := by rw [Finset.sum_div]
    _ ≤ (Real.log w + 7) / Real.log 2 := div_le_div_of_nonneg_right (by linarith) hl2.le

/-- `∑_{p ≤ w} ln (1 - 1/p)` and `-B(w)` differ by the prime powers above `w` only. -/
theorem abs_sum_log_add_B_le (w : ℕ) (hw : 1 ≤ w) :
    |(∑ p ∈ Nat.primesLE w, Real.log (1 - (p : ℝ)⁻¹)) + B w|
      ≤ 2 * (Real.sqrt w)⁻¹ * ((Real.log w + 7) / Real.log 2) := by
  rw [B_natCast_eq, ← Finset.sum_add_distrib]
  calc |∑ p ∈ Nat.primesLE w,
          (Real.log (1 - (p : ℝ)⁻¹) + ∑ i ∈ range (Nat.log p w), lamLog (p ^ (i + 1)))|
      ≤ ∑ p ∈ Nat.primesLE w,
          |Real.log (1 - (p : ℝ)⁻¹) + ∑ i ∈ range (Nat.log p w), lamLog (p ^ (i + 1))| :=
        Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ p ∈ Nat.primesLE w, 2 * ((p : ℝ)⁻¹ * (Real.sqrt w)⁻¹) := by
        refine Finset.sum_le_sum fun p hp => ?_
        obtain ⟨hpw, hpp⟩ := Nat.mem_primesLE.mp hp
        rw [add_comm]
        exact (abs_sum_lamLog_add_log_le hpp _).trans
          (mul_le_mul_of_nonneg_left (inv_pow_log_succ_le hpp hpw) (by norm_num))
    _ = 2 * (Real.sqrt w)⁻¹ * ∑ p ∈ Nat.primesLE w, (p : ℝ)⁻¹ := by
        rw [Finset.mul_sum]
        exact Finset.sum_congr rfl fun p _ => by ring
    _ ≤ _ := mul_le_mul_of_nonneg_left (sum_primesLE_inv_le w hw) (by positivity)

theorem tendsto_sum_log_add_B :
    Tendsto (fun w : ℕ => (∑ p ∈ Nat.primesLE w, Real.log (1 - (p : ℝ)⁻¹)) + B w) atTop
      (𝓝 0) := by
  have h1 : Tendsto (fun x : ℝ => Real.log x / x ^ (1 / 2 : ℝ)) atTop (𝓝 0) :=
    (isLittleO_log_rpow_atTop (by norm_num)).tendsto_div_nhds_zero
  have h2 : Tendsto (fun x : ℝ => x ^ (-(1 / 2) : ℝ)) atTop (𝓝 0) :=
    tendsto_rpow_neg_atTop (by norm_num)
  have h3 : Tendsto (fun x : ℝ => 2 / Real.log 2 *
      (Real.log x / x ^ (1 / 2 : ℝ) + 7 * x ^ (-(1 / 2) : ℝ))) atTop (𝓝 0) := by
    have h := (h1.add (h2.const_mul 7)).const_mul (2 / Real.log 2)
    simpa using h
  refine squeeze_zero_norm' ?_ (h3.comp tendsto_natCast_atTop_atTop)
  filter_upwards [eventually_ge_atTop 1] with w hw
  have hw0 : (0 : ℝ) < w := by exact_mod_cast hw
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  rw [Real.norm_eq_abs]
  refine (abs_sum_log_add_B_le w hw).trans (le_of_eq ?_)
  simp only [Function.comp_apply]
  rw [Real.sqrt_eq_rpow, Real.rpow_neg hw0.le]
  have : (0 : ℝ) < (w : ℝ) ^ (1 / 2 : ℝ) := Real.rpow_pos_of_pos hw0 _
  field_simp

/-- `ln ln w + ∑_{p ≤ w} ln (1 - 1/p) → -γ`. -/
theorem tendsto_log_log_add_sum :
    Tendsto (fun w : ℕ => Real.log (Real.log w) + ∑ p ∈ Nat.primesLE w, Real.log (1 - (p : ℝ)⁻¹))
      atTop (𝓝 (-Real.eulerMascheroniConstant)) := by
  have h1 : Tendsto (fun w : ℕ => B w - Real.log (Real.log w)) atTop
      (𝓝 Real.eulerMascheroniConstant) := by
    have h := tendsto_B_sub_log_log.comp tendsto_natCast_atTop_atTop
    rw [limit_eq_eulerMascheroni] at h
    exact h
  have h3 := tendsto_sum_log_add_B.sub h1
  rw [zero_sub] at h3
  refine h3.congr fun w => ?_
  ring

/-- **Mertens' third theorem**: `ln w · ∏_{p ≤ w} (1 - 1/p) → e^{-γ}`. -/
theorem mertens_third :
    Tendsto (fun w : ℕ => Real.log w * ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹)) atTop
      (𝓝 (Real.exp (-Real.eulerMascheroniConstant))) := by
  have h := (Real.continuous_exp.tendsto _).comp tendsto_log_log_add_sum
  refine h.congr' ?_
  filter_upwards [eventually_ge_atTop 3] with w hw
  have hw3 : (3 : ℝ) ≤ w := by exact_mod_cast hw
  have hlw : 0 < Real.log w := Real.log_pos (by linarith)
  simp only [Function.comp_apply]
  rw [Real.exp_add, Real.exp_log hlw, Real.exp_sum]
  congr 1
  refine Finset.prod_congr rfl fun p hp => ?_
  have hpp := (Nat.mem_primesLE.mp hp).2
  have hp2 : (2 : ℝ) ≤ p := by exact_mod_cast hpp.two_le
  have hx : (p : ℝ)⁻¹ ≤ 1 / 2 := by
    rw [inv_eq_one_div]
    exact one_div_le_one_div_of_le (by norm_num) hp2
  exact Real.exp_log (by linarith)

end GoldbachGaps.Mertens
