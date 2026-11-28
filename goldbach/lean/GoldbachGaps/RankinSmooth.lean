import GoldbachGaps.CoverEveryConstant

/-!
# Rankin's `u^{-u}` smooth-number bound and unconditional iterated-log upgrade

This module formalises the elementary Rankin smooth-number estimate (`COHERENT_BLOCK.md` `(F4)`)
and upgrades `CoverEveryConstant.eventually_exists_even_le_log` unconditionally from
`log X · (log log X)² / (log log log X)²` to
`log X · (log log X)² · log log log log X / (log log log X)²` on `[X / 2, X]`.

It also exports a unified two-layer surviving-prime-count bound
(`eventually_exists_two_layer_classes`) and reusable CRT / partial-cover helpers shared with
`GoldbachGaps/IteratedLogBound.lean`.

Everything in this file is unconditional and uses only Lean's standard logical foundation
(`propext`, `Classical.choice`, `Quot.sound`).
-/

namespace GoldbachGaps

open Finset Filter
open scoped ArithmeticFunction.vonMangoldt

/-! ### Section A: Elementary Rankin `u^{-u}` smooth-number bound -/

private theorem inv_one_sub_le_exp_quad {t : ℝ} (_h0 : 0 ≤ t) (h1 : t ≤ 2 / 3) :
    (1 - t)⁻¹ ≤ Real.exp (t + 3 * t ^ 2) := by
  have hpos : 0 < 1 - t := by linarith
  rw [inv_le_iff_one_le_mul₀ hpos]
  have hexp : t + 3 * t ^ 2 + 1 ≤ Real.exp (t + 3 * t ^ 2) :=
    Real.add_one_le_exp (t + 3 * t ^ 2)
  have hpoly : 1 ≤ (t + 3 * t ^ 2 + 1) * (1 - t) := by
    have hfac : (t + 3 * t ^ 2 + 1) * (1 - t) - 1 = t ^ 2 * (2 - 3 * t) := by ring
    have hnn : 0 ≤ t ^ 2 * (2 - 3 * t) := mul_nonneg (sq_nonneg t) (by linarith)
    linarith
  exact hpoly.trans (mul_le_mul_of_nonneg_right hexp hpos.le)

private theorem rpow_neg_le_two_thirds {p : ℕ} (hp : p.Prime) {σ : ℝ} (hσ : 3 / 4 ≤ σ) :
    (p : ℝ) ^ (-σ) ≤ 2 / 3 := by
  have hp2 : (2 : ℝ) ≤ p := by exact_mod_cast hp.two_le
  have h1 : (p : ℝ) ^ (-σ) ≤ (2 : ℝ) ^ (-σ) :=
    Real.rpow_le_rpow_of_nonpos (by norm_num) hp2 (by linarith)
  have h2 : (2 : ℝ) ^ (-σ) ≤ (2 : ℝ) ^ (-(3 / 4 : ℝ)) :=
    Real.rpow_le_rpow_of_exponent_le (by norm_num) (by linarith)
  have h3 : (2 : ℝ) ^ (-(3 / 4 : ℝ)) ≤ 2 / 3 := by
    rw [Real.rpow_neg (by norm_num)]
    rw [inv_le_comm₀ (Real.rpow_pos_of_pos (by norm_num) _) (by norm_num)]
    refine le_of_pow_le_pow_left₀ (by norm_num : 4 ≠ 0) (Real.rpow_nonneg (by norm_num) _) ?_
    have hpow : ((2 : ℝ) ^ (3 / 4 : ℝ)) ^ (4 : ℕ) = (8 : ℝ) := by
      rw [← Real.rpow_natCast, ← Real.rpow_mul (by norm_num : (0 : ℝ) ≤ 2)]
      have h34 : (3 / 4 : ℝ) * (4 : ℕ) = ((3 : ℕ) : ℝ) := by norm_num
      rw [h34, Real.rpow_natCast]
      norm_num
    rw [hpow]
    norm_num
  linarith

private theorem rpow_neg_three_halves_le_sub_inv_sqrt {n : ℕ} (hn : 2 ≤ n) :
    (n : ℝ) ^ (-(3 / 2 : ℝ)) ≤
      2 * ((Real.sqrt ((n - 1 : ℕ) : ℝ))⁻¹ - (Real.sqrt (n : ℝ))⁻¹) := by
  have hn0 : (0 : ℝ) < n := by exact_mod_cast (by omega : 0 < n)
  have hn1 : (0 : ℝ) < ((n - 1 : ℕ) : ℝ) := by exact_mod_cast (by omega : 0 < n - 1)
  set a := Real.sqrt (n : ℝ)
  set b := Real.sqrt ((n - 1 : ℕ) : ℝ)
  have ha0 : 0 < a := Real.sqrt_pos.mpr hn0
  have hb0 : 0 < b := Real.sqrt_pos.mpr hn1
  have ha2 : a ^ 2 = (n : ℝ) := Real.sq_sqrt hn0.le
  have hb2 : b ^ 2 = (n : ℝ) - 1 := by
    rw [Real.sq_sqrt hn1.le, Nat.cast_sub (by omega : 1 ≤ n), Nat.cast_one]
  have hba : b ≤ a := Real.sqrt_le_sqrt (by exact_mod_cast Nat.sub_le n 1)
  have hrpow : (n : ℝ) ^ (-(3 / 2 : ℝ)) = (a ^ 3)⁻¹ := by
    rw [Real.rpow_neg hn0.le]
    congr 1
    have h1 : a ^ 3 = ((n : ℝ) ^ (1 / 2 : ℝ)) ^ (3 : ℕ) := by rw [← Real.sqrt_eq_rpow]
    rw [h1, ← Real.rpow_natCast, ← Real.rpow_mul hn0.le]
    congr 1
    norm_num
  have hdiff : (a - b) * (a + b) = 1 := by nlinarith [ha2, hb2]
  have hba2 : b * (a + b) ≤ 2 * a ^ 2 := by nlinarith
  have hkey : b ≤ 2 * a ^ 2 * (a - b) := by
    refine le_of_mul_le_mul_right ?_ (by linarith : 0 < a + b)
    nlinarith [hdiff, hba2]
  rw [hrpow]
  have hgoal1 : (a ^ 3)⁻¹ = b / (a ^ 3 * b) := by field_simp
  have hgoal2 : 2 * (b⁻¹ - a⁻¹) = (2 * a ^ 2 * (a - b)) / (a ^ 3 * b) := by
    field_simp
  rw [hgoal1, hgoal2]
  exact div_le_div_of_nonneg_right hkey (by positivity)

private theorem sum_Ico_telescope (f : ℕ → ℝ) (k : ℕ) :
    ∑ n ∈ Ico 2 (k + 2), (f (n - 1) - f n) = f 1 - f (k + 1) := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [show k + 1 + 2 = (k + 2) + 1 by omega, Finset.sum_Ico_succ_top (by omega), ih]
    have hsub : k + 2 - 1 = k + 1 := by omega
    rw [hsub]
    ring

private theorem sum_Ico_sub_inv_sqrt_le (N : ℕ) :
    ∑ n ∈ Ico 2 N, ((Real.sqrt ((n - 1 : ℕ) : ℝ))⁻¹ - (Real.sqrt (n : ℝ))⁻¹) ≤ 1 := by
  by_cases hN : N ≤ 2
  · rw [Finset.Ico_eq_empty (by omega), Finset.sum_empty]
    norm_num
  · have hEq : N = (N - 2) + 2 := by omega
    rw [hEq, sum_Ico_telescope (fun k => (Real.sqrt (k : ℝ))⁻¹)]
    have h1 : (Real.sqrt ((1 : ℕ) : ℝ))⁻¹ = 1 := by simp
    have hnn : 0 ≤ (Real.sqrt (((N - 2) + 1 : ℕ) : ℝ))⁻¹ := inv_nonneg.mpr (Real.sqrt_nonneg _)
    linarith

private theorem sum_primesBelow_rpow_neg_two_mul_le (N : ℕ) {σ : ℝ} (hσ : 3 / 4 ≤ σ) :
    ∑ p ∈ N.primesBelow, (p : ℝ) ^ (-(2 * σ)) ≤ 2 := by
  have hsub : N.primesBelow ⊆ Ico 2 N := by
    intro p hp
    exact Finset.mem_Ico.mpr
      ⟨(Nat.prime_of_mem_primesBelow hp).two_le, Nat.lt_of_mem_primesBelow hp⟩
  calc ∑ p ∈ N.primesBelow, (p : ℝ) ^ (-(2 * σ))
      ≤ ∑ p ∈ N.primesBelow, (p : ℝ) ^ (-(3 / 2 : ℝ)) := by
        refine Finset.sum_le_sum fun p hp => ?_
        have hp1 : (1 : ℝ) ≤ p := by exact_mod_cast (Nat.prime_of_mem_primesBelow hp).one_le
        exact Real.rpow_le_rpow_of_exponent_le hp1 (by linarith)
    _ ≤ ∑ n ∈ Ico 2 N, (n : ℝ) ^ (-(3 / 2 : ℝ)) :=
        Finset.sum_le_sum_of_subset_of_nonneg hsub fun n _ _ =>
          Real.rpow_nonneg (Nat.cast_nonneg n) _
    _ ≤ ∑ n ∈ Ico 2 N, 2 * ((Real.sqrt ((n - 1 : ℕ) : ℝ))⁻¹ - (Real.sqrt (n : ℝ))⁻¹) := by
        refine Finset.sum_le_sum fun n hn => ?_
        exact rpow_neg_three_halves_le_sub_inv_sqrt (Finset.mem_Ico.mp hn).1
    _ = 2 * ∑ n ∈ Ico 2 N, ((Real.sqrt ((n - 1 : ℕ) : ℝ))⁻¹ - (Real.sqrt (n : ℝ))⁻¹) := by
        rw [← Finset.mul_sum]
    _ ≤ 2 * 1 := mul_le_mul_of_nonneg_left (sum_Ico_sub_inv_sqrt_le N) (by norm_num)
    _ = 2 := by ring

private theorem sum_primesBelow_log_div_le (N : ℕ) (hN : 1 ≤ N) :
    ∑ p ∈ N.primesBelow, Real.log (p : ℝ) / (p : ℝ) ≤ Real.log (N : ℝ) + 6 := by
  have hsub : N.primesBelow ⊆ Ioc 0 N := by
    intro p hp
    exact Finset.mem_Ioc.mpr
      ⟨(Nat.prime_of_mem_primesBelow hp).pos, (Nat.lt_of_mem_primesBelow hp).le⟩
  have heq : ∑ p ∈ N.primesBelow, Real.log (p : ℝ) / (p : ℝ) =
      ∑ p ∈ N.primesBelow, Λ p / (p : ℝ) := by
    refine Finset.sum_congr rfl fun p hp => ?_
    rw [ArithmeticFunction.vonMangoldt_apply_prime (Nat.prime_of_mem_primesBelow hp)]
  have hle : ∑ p ∈ N.primesBelow, Λ p / (p : ℝ) ≤ ∑ n ∈ Ioc 0 N, Λ n / (n : ℝ) :=
    Finset.sum_le_sum_of_subset_of_nonneg hsub fun n _ _ =>
      div_nonneg ArithmeticFunction.vonMangoldt_nonneg (Nat.cast_nonneg n)
  have hm := (abs_le.mp (Mertens.abs_sum_lam_sub_log_le N hN)).2
  linarith

private theorem exp_mul_le_linear {η s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) :
    Real.exp (η * s) ≤ 1 + (Real.exp η - 1) * s := by
  have h := convexOn_exp.2 (Set.mem_univ (0 : ℝ)) (Set.mem_univ η)
    (by linarith : 0 ≤ 1 - s) hs0 (by ring : (1 - s) + s = 1)
  simp only [smul_eq_mul, mul_zero, zero_add, Real.exp_zero] at h
  rw [mul_comm η s]
  linarith

private theorem sum_primesBelow_rpow_neg_le {K₀ : ℝ}
    (hK₀ : ∀ w : ℕ, 2 ≤ w → ∑ p ∈ Nat.primesLE w, ((p : ℝ))⁻¹ ≤ Real.log (Real.log w) + K₀)
    {N : ℕ} (hN : 2 ≤ N) {u : ℝ} (hu : 1 ≤ u) :
    ∑ p ∈ N.primesBelow, (p : ℝ) ^ (-(1 - Real.log u / Real.log (N : ℝ))) ≤
      Real.log (Real.log (N : ℝ)) + K₀ + (u - 1) * (1 + 6 / Real.log (N : ℝ)) := by
  have hN1 : (1 : ℝ) < N := by exact_mod_cast (by omega : 1 < N)
  have hlogN : 0 < Real.log (N : ℝ) := Real.log_pos hN1
  have hu0 : 0 < u := by linarith
  have hterm : ∀ p ∈ N.primesBelow,
      (p : ℝ) ^ (-(1 - Real.log u / Real.log (N : ℝ))) ≤
        ((p : ℝ))⁻¹ + ((u - 1) / Real.log (N : ℝ)) * (Real.log (p : ℝ) / (p : ℝ)) := by
    intro p hp
    have hpp := Nat.prime_of_mem_primesBelow hp
    have hpN : p < N := Nat.lt_of_mem_primesBelow hp
    have hp0 : (0 : ℝ) < p := by exact_mod_cast hpp.pos
    have hp1 : (1 : ℝ) ≤ p := by exact_mod_cast hpp.one_le
    set s := Real.log (p : ℝ) / Real.log (N : ℝ)
    have hs0 : 0 ≤ s := div_nonneg (Real.log_nonneg hp1) hlogN.le
    have hs1 : s ≤ 1 :=
      (div_le_one hlogN).mpr (Real.log_le_log hp0 (by exact_mod_cast hpN.le))
    have hrew : (p : ℝ) ^ (-(1 - Real.log u / Real.log (N : ℝ))) =
        ((p : ℝ))⁻¹ * Real.exp (Real.log u * s) := by
      have hexp : -(1 - Real.log u / Real.log (N : ℝ)) = (-1 : ℝ) + Real.log u / Real.log (N : ℝ) := by
        ring
      rw [hexp, Real.rpow_add hp0, Real.rpow_neg_one, Real.rpow_def_of_pos hp0]
      congr 2
      simp only [s]
      ring
    rw [hrew]
    have hconv := exp_mul_le_linear (η := Real.log u) hs0 hs1
    rw [Real.exp_log hu0] at hconv
    have hmul := mul_le_mul_of_nonneg_left hconv (inv_nonneg.mpr hp0.le)
    refine hmul.trans (le_of_eq ?_)
    simp only [s]
    ring
  have hsub : N.primesBelow ⊆ Nat.primesLE N := by
    intro p hp
    exact Nat.mem_primesLE.mpr
      ⟨(Nat.lt_of_mem_primesBelow hp).le, Nat.prime_of_mem_primesBelow hp⟩
  have hsum1 : ∑ p ∈ N.primesBelow, ((p : ℝ))⁻¹ ≤ Real.log (Real.log (N : ℝ)) + K₀ :=
    (Finset.sum_le_sum_of_subset_of_nonneg hsub fun p _ _ => inv_nonneg.mpr (Nat.cast_nonneg p)).trans
      (hK₀ N hN)
  have hsum2 : ((u - 1) / Real.log (N : ℝ)) * ∑ p ∈ N.primesBelow, Real.log (p : ℝ) / (p : ℝ) ≤
      (u - 1) * (1 + 6 / Real.log (N : ℝ)) := by
    have hcoef : 0 ≤ (u - 1) / Real.log (N : ℝ) := div_nonneg (by linarith) hlogN.le
    calc ((u - 1) / Real.log (N : ℝ)) * ∑ p ∈ N.primesBelow, Real.log (p : ℝ) / (p : ℝ)
        ≤ ((u - 1) / Real.log (N : ℝ)) * (Real.log (N : ℝ) + 6) :=
          mul_le_mul_of_nonneg_left (sum_primesBelow_log_div_le N (by omega)) hcoef
      _ = (u - 1) * (1 + 6 / Real.log (N : ℝ)) := by
          field_simp
  calc ∑ p ∈ N.primesBelow, (p : ℝ) ^ (-(1 - Real.log u / Real.log (N : ℝ)))
      ≤ ∑ p ∈ N.primesBelow,
          (((p : ℝ))⁻¹ + ((u - 1) / Real.log (N : ℝ)) * (Real.log (p : ℝ) / (p : ℝ))) :=
        Finset.sum_le_sum hterm
    _ = ∑ p ∈ N.primesBelow, ((p : ℝ))⁻¹ +
          ((u - 1) / Real.log (N : ℝ)) * ∑ p ∈ N.primesBelow, Real.log (p : ℝ) / (p : ℝ) := by
        rw [Finset.sum_add_distrib, ← Finset.mul_sum]
    _ ≤ Real.log (Real.log (N : ℝ)) + K₀ + (u - 1) * (1 + 6 / Real.log (N : ℝ)) :=
        add_le_add hsum1 hsum2

private theorem prod_primesBelow_le_rankin {K₀ : ℝ}
    (hK₀ : ∀ w : ℕ, 2 ≤ w → ∑ p ∈ Nat.primesLE w, ((p : ℝ))⁻¹ ≤ Real.log (Real.log w) + K₀)
    {N : ℕ} (hN : 2 ≤ N) {u : ℝ} (hu : 1 ≤ u) (hσ4 : 4 * Real.log u ≤ Real.log (N : ℝ)) :
    ∏ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-(1 - Real.log u / Real.log (N : ℝ))))⁻¹ ≤
      Real.exp (K₀ + 6) * Real.log (N : ℝ) * Real.exp ((u - 1) * (1 + 6 / Real.log (N : ℝ))) := by
  have hN1 : (1 : ℝ) < N := by exact_mod_cast (by omega : 1 < N)
  have hlogN : 0 < Real.log (N : ℝ) := Real.log_pos hN1
  set σ := 1 - Real.log u / Real.log (N : ℝ)
  have hσ34 : 3 / 4 ≤ σ := by
    have hdiv : Real.log u / Real.log (N : ℝ) ≤ 1 / 4 := by
      rw [div_le_iff₀ hlogN]
      linarith
    linarith
  have hpos : ∀ p ∈ N.primesBelow, 0 ≤ (1 - (p : ℝ) ^ (-σ))⁻¹ := by
    intro p hp
    have := rpow_neg_le_two_thirds (Nat.prime_of_mem_primesBelow hp) hσ34
    exact inv_nonneg.mpr (by linarith)
  have hfac : ∀ p ∈ N.primesBelow,
      (1 - (p : ℝ) ^ (-σ))⁻¹ ≤ Real.exp ((p : ℝ) ^ (-σ) + 3 * (p : ℝ) ^ (-(2 * σ))) := by
    intro p hp
    have hpp := Nat.prime_of_mem_primesBelow hp
    have hp0 : (0 : ℝ) ≤ p := Nat.cast_nonneg p
    have hsq : ((p : ℝ) ^ (-σ)) ^ 2 = (p : ℝ) ^ (-(2 * σ)) := by
      rw [← Real.rpow_natCast, ← Real.rpow_mul hp0]
      congr 1
      push_cast
      ring
    rw [← hsq]
    exact inv_one_sub_le_exp_quad (Real.rpow_nonneg hp0 _) (rpow_neg_le_two_thirds hpp hσ34)
  have hsum1 := sum_primesBelow_rpow_neg_le hK₀ hN hu
  have hsum2 := sum_primesBelow_rpow_neg_two_mul_le N hσ34
  calc ∏ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-σ))⁻¹
      ≤ ∏ p ∈ N.primesBelow, Real.exp ((p : ℝ) ^ (-σ) + 3 * (p : ℝ) ^ (-(2 * σ))) :=
        Finset.prod_le_prod₀ hpos hfac
    _ = Real.exp (∑ p ∈ N.primesBelow, ((p : ℝ) ^ (-σ) + 3 * (p : ℝ) ^ (-(2 * σ)))) :=
        (Real.exp_sum _ _).symm
    _ ≤ Real.exp (Real.log (Real.log (N : ℝ)) + (K₀ + 6) +
          (u - 1) * (1 + 6 / Real.log (N : ℝ))) := by
        apply Real.exp_le_exp.mpr
        rw [Finset.sum_add_distrib, ← Finset.mul_sum]
        linarith
    _ = Real.exp (K₀ + 6) * Real.log (N : ℝ) *
          Real.exp ((u - 1) * (1 + 6 / Real.log (N : ℝ))) := by
        rw [Real.exp_add, Real.exp_add, Real.exp_log hlogN]
        ring

/-- **General elementary Rankin smooth-number bound (`(F4)`).** For `1 ≤ X`, `2 ≤ N`,
`u = ln X / ln N ≥ 1`, and `4 ln u ≤ ln N`, the number of `N`-smooth integers in `[1, X)` is at
most `C · X · ln N · exp (-u ln u + (u - 1)(1 + 6 / ln N))`. -/
theorem exists_rankin_smooth_general :
    ∃ C : ℝ, 0 < C ∧ ∀ (X N : ℕ) (u : ℝ), 1 ≤ X → 2 ≤ N →
      u = Real.log (X : ℝ) / Real.log (N : ℝ) →
      1 ≤ u → 4 * Real.log u ≤ Real.log (N : ℝ) →
      (#{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers N} : ℝ) ≤
        C * (X : ℝ) * Real.log (N : ℝ) *
          Real.exp (-u * Real.log u + (u - 1) * (1 + 6 / Real.log (N : ℝ))) := by
  obtain ⟨K₀, -, hK₀⟩ := exists_sum_primesLE_inv_le
  refine ⟨Real.exp (K₀ + 6), Real.exp_pos _, ?_⟩
  intro X N u hX hN hu_eq hu1 h4u
  have hX0 : (0 : ℝ) < X := by exact_mod_cast (by omega : 0 < X)
  have hN1 : (1 : ℝ) < N := by exact_mod_cast (by omega : 1 < N)
  have hlogN : 0 < Real.log (N : ℝ) := Real.log_pos hN1
  set σ := 1 - Real.log u / Real.log (N : ℝ)
  have hσ34 : 3 / 4 ≤ σ := by
    have hdiv : Real.log u / Real.log (N : ℝ) ≤ 1 / 4 := by
      rw [div_le_iff₀ hlogN]
      linarith
    linarith
  have hσ0 : 0 < σ := by linarith
  have hcard := Cap.card_smooth_le N X hσ0
  have hprod := prod_primesBelow_le_rankin hK₀ hN hu1 h4u
  have hXpow : (X : ℝ) ^ σ = (X : ℝ) * Real.exp (-u * Real.log u) := by
    have hexp : σ = 1 + -(Real.log u / Real.log (N : ℝ)) := by
      simp only [σ]
      ring
    rw [hexp, Real.rpow_add hX0, Real.rpow_one, Real.rpow_def_of_pos hX0]
    congr 2
    rw [hu_eq]
    field_simp
  calc (#{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers N} : ℝ)
      ≤ (X : ℝ) ^ σ * ∏ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-σ))⁻¹ := hcard
    _ ≤ ((X : ℝ) * Real.exp (-u * Real.log u)) *
          (Real.exp (K₀ + 6) * Real.log (N : ℝ) *
            Real.exp ((u - 1) * (1 + 6 / Real.log (N : ℝ)))) := by
        rw [hXpow]
        exact mul_le_mul_of_nonneg_left hprod (by positivity)
    _ = Real.exp (K₀ + 6) * (X : ℝ) * Real.log (N : ℝ) *
          Real.exp (-u * Real.log u + (u - 1) * (1 + 6 / Real.log (N : ℝ))) := by
        rw [Real.exp_add (-u * Real.log u) ((u - 1) * (1 + 6 / Real.log (N : ℝ)))]
        ring

/-- **Rankin's `u^{-u}` smooth-number bound (`COHERENT_BLOCK.md` `(F4)`).** Under the mild
condition `u ≤ ln N` (with `4 ln u ≤ ln N` and `1 ≤ u`), the number of `N`-smooth integers in
`[1, X)` is at most `C · X · ln N · exp (-u ln u + u)`. -/
theorem exists_rankin_smooth_bound :
    ∃ C : ℝ, 0 < C ∧ ∀ (X N : ℕ) (u : ℝ), 1 ≤ X → 2 ≤ N →
      u = Real.log (X : ℝ) / Real.log (N : ℝ) →
      1 ≤ u → 4 * Real.log u ≤ Real.log (N : ℝ) → u ≤ Real.log (N : ℝ) →
      (#{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers N} : ℝ) ≤
        C * (X : ℝ) * Real.log (N : ℝ) * Real.exp (-u * Real.log u + u) := by
  obtain ⟨C, hCpos, hC⟩ := exists_rankin_smooth_general
  refine ⟨C * Real.exp 5, mul_pos hCpos (Real.exp_pos 5), ?_⟩
  intro X N u hX hN hu_eq hu1 h4u huN
  have hN1 : (1 : ℝ) < N := by exact_mod_cast (by omega : 1 < N)
  have hlogN : 0 < Real.log (N : ℝ) := Real.log_pos hN1
  have hfrac : 6 * (u - 1) / Real.log (N : ℝ) ≤ 6 := by
    rw [div_le_iff₀ hlogN]
    linarith
  have hexp : -u * Real.log u + (u - 1) * (1 + 6 / Real.log (N : ℝ)) ≤
      5 + (-u * Real.log u + u) := by
    have heq : (u - 1) * (1 + 6 / Real.log (N : ℝ)) = (u - 1) + 6 * (u - 1) / Real.log (N : ℝ) := by
      ring
    linarith
  calc (#{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers N} : ℝ)
      ≤ C * (X : ℝ) * Real.log (N : ℝ) *
          Real.exp (-u * Real.log u + (u - 1) * (1 + 6 / Real.log (N : ℝ))) :=
        hC X N u hX hN hu_eq hu1 h4u
    _ ≤ C * (X : ℝ) * Real.log (N : ℝ) * Real.exp (5 + (-u * Real.log u + u)) := by
        exact mul_le_mul_of_nonneg_left (Real.exp_le_exp.mpr hexp) (by positivity)
    _ = C * Real.exp 5 * (X : ℝ) * Real.log (N : ℝ) * Real.exp (-u * Real.log u + u) := by
        rw [Real.exp_add]
        ring

/-! ### Section B: Unified two-layer surviving-prime-count theorem -/

private theorem four_mul_log_le_self {t : ℝ} (ht : 64 ≤ t) : 4 * Real.log t ≤ t := by
  have h1 : Real.log t ≤ t ^ (1 / 2 : ℝ) / (1 / 2 : ℝ) :=
    Real.log_le_rpow_div (by linarith) (by norm_num)
  rw [← Real.sqrt_eq_rpow] at h1
  have h2 : Real.log t ≤ 2 * Real.sqrt t := by linarith
  have h8 : 8 ≤ Real.sqrt t := Real.le_sqrt_of_sq_le (by linarith)
  have hsq : Real.sqrt t * Real.sqrt t = t := Real.mul_self_sqrt (by linarith)
  nlinarith [Real.sqrt_nonneg t]

/-- Smoothness cutoff for the Rankin-upgraded two-layer sieve:
`⌊exp (ln y · ln₃ y / (10 ln₂ y))⌋`. -/
noncomputable def rankinZ (y : ℕ) : ℕ :=
  ⌊Real.exp (Real.log (y : ℝ) * Real.log (Real.log (Real.log (y : ℝ))) /
    (10 * Real.log (Real.log (y : ℝ))))⌋₊

/-- For all large `y` and every `Q` with `y ≤ 2 Q` and `Q ≤ y (ln y)⁴`, the number of
`(rankinZ y + 1)`-smooth integers in `[1, 2 Q)` is at most `Q / (ln y)²`. -/
theorem eventually_card_smooth_rankin_le :
    ∀ᶠ y : ℕ in atTop, ∀ Q : ℕ, y ≤ 2 * Q → (Q : ℝ) ≤ (y : ℝ) * Real.log (y : ℝ) ^ 4 →
      (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers (rankinZ y + 1)} : ℝ) ≤
        (Q : ℝ) / Real.log (y : ℝ) ^ 2 := by
  obtain ⟨C, hCpos, hC⟩ := exists_rankin_smooth_bound
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hL : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hL2 : Tendsto (fun y : ℕ => Real.log (Real.log (y : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL
  have hL3 : Tendsto (fun y : ℕ => Real.log (Real.log (Real.log (y : ℝ)))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL2
  have ho4 := (Real.isLittleO_pow_log_id_atTop (n := 4)).def (show (0 : ℝ) < 1 / 2 by norm_num)
  have ho2 := (Real.isLittleO_pow_log_id_atTop (n := 2)).def (show (0 : ℝ) < 1 / 200 by norm_num)
  filter_upwards [eventually_ge_atTop 8, hcast.eventually ho4, hL.eventually ho2,
    hL.eventually_ge_atTop 100, hL2.eventually_ge_atTop (max (Real.log (2 * C)) 4),
    hL3.eventually_ge_atTop 64] with y hy8 h4 h2 hL100 hL2max hL3_64
  set L := Real.log (y : ℝ) with hLdef
  set L₂ := Real.log L with hL2def
  set L₃ := Real.log L₂ with hL3def
  set E := L * L₃ / (10 * L₂) with hEdef
  set z := rankinZ y with hzdef
  set N := z + 1 with hNdef
  have hL2_4 : 4 ≤ L₂ := (le_max_right _ _).trans hL2max
  have hL2_C : Real.log (2 * C) ≤ L₂ := (le_max_left _ _).trans hL2max
  have hy0 : (0 : ℝ) < y := by exact_mod_cast (by omega : 0 < y)
  have hL0 : 0 < L := by linarith
  have hL20 : 0 < L₂ := by linarith
  have hL30 : 0 < L₃ := by linarith
  have hL4y : 2 * L ^ 4 ≤ (y : ℝ) := by
    simp only [id, Real.norm_eq_abs] at h4
    rw [abs_of_nonneg hy0.le, abs_of_nonneg (by positivity : 0 ≤ L ^ 4)] at h4
    linarith
  have hL2L : 200 * L₂ ^ 2 ≤ L := by
    simp only [id, Real.norm_eq_abs] at h2
    rw [abs_of_nonneg hL0.le, abs_of_nonneg (by positivity : 0 ≤ L₂ ^ 2)] at h2
    linarith
  have hL3leL2 : L₃ ≤ L₂ := by
    have := Real.log_le_sub_one_of_pos hL20
    linarith
  have hE64 : 64 ≤ E := by
    have h1 : 1280 * L₂ ≤ E := by
      rw [hEdef, le_div_iff₀ (by positivity : 0 < 10 * L₂)]
      have hmul : 200 * L₂ ^ 2 * 64 ≤ L * L₃ :=
        mul_le_mul hL2L hL3_64 (by norm_num) hL0.le
      linarith
    linarith
  have hz7 : 7 ≤ z := by
    rw [hzdef, rankinZ]
    refine Nat.le_floor ?_
    have h1 := Real.add_one_le_exp E
    push_cast
    linarith
  have hN2 : 2 ≤ N := by omega
  have hNpos : (0 : ℝ) < N := by exact_mod_cast (by omega : 0 < N)
  have hNgt : Real.exp E < (N : ℝ) := by
    have := Nat.lt_floor_add_one (Real.exp E)
    simpa [hNdef, hzdef, rankinZ] using this
  have hNle : (N : ℝ) ≤ 2 * Real.exp E := by
    have hfl : (z : ℝ) ≤ Real.exp E := Nat.floor_le (Real.exp_pos E).le
    have h1 : (1 : ℝ) ≤ Real.exp E := Real.one_le_exp (by linarith)
    have hcastN : (N : ℝ) = (z : ℝ) + 1 := by exact_mod_cast rfl
    linarith
  have hlogN_gt : E < Real.log (N : ℝ) := by
    rw [← Real.log_exp E]
    exact Real.log_lt_log (Real.exp_pos E) hNgt
  have hlogN_le_65E : Real.log (N : ℝ) ≤ (6 / 5) * E := by
    have h1 : Real.log (N : ℝ) ≤ Real.log (2 * Real.exp E) := Real.log_le_log hNpos hNle
    rw [Real.log_mul (by norm_num) (Real.exp_pos E).ne', Real.log_exp] at h1
    have hlog2 : Real.log 2 < 1 := lt_trans Real.log_two_lt_d9 (by norm_num)
    linarith
  have hlogN_le_L : Real.log (N : ℝ) ≤ L := by
    have h1 : E ≤ L / 10 := by
      rw [hEdef, div_le_div_iff₀ (by positivity : 0 < 10 * L₂) (by norm_num : (0 : ℝ) < 10)]
      nlinarith
    linarith
  have hlogN_pos : 0 < Real.log (N : ℝ) := by linarith
  intro Q hy2Q hQle
  have h2Qpos : 1 ≤ 2 * Q := by omega
  have h2Qr_pos : (0 : ℝ) < ((2 * Q : ℕ) : ℝ) := by exact_mod_cast h2Qpos
  have hlog2Q_ge : L ≤ Real.log ((2 * Q : ℕ) : ℝ) :=
    Real.log_le_log hy0 (by exact_mod_cast hy2Q)
  have hlog2Q_le : Real.log ((2 * Q : ℕ) : ℝ) ≤ 2 * L := by
    have h1 : ((2 * Q : ℕ) : ℝ) ≤ (y : ℝ) ^ 2 := by
      push_cast
      have hmul : 2 * ((Q : ℝ)) ≤ (y : ℝ) * (2 * L ^ 4) := by linarith
      have hmul2 : (y : ℝ) * (2 * L ^ 4) ≤ (y : ℝ) * (y : ℝ) :=
        mul_le_mul_of_nonneg_left hL4y hy0.le
      nlinarith
    calc Real.log ((2 * Q : ℕ) : ℝ) ≤ Real.log ((y : ℝ) ^ 2) := Real.log_le_log h2Qr_pos h1
      _ = 2 * L := by rw [Real.log_pow]; push_cast; rfl
  set u := Real.log ((2 * Q : ℕ) : ℝ) / Real.log (N : ℝ)
  have hu_ge : (25 / 3 : ℝ) * (L₂ / L₃) ≤ u := by
    have h1 : L / ((6 / 5) * E) ≤ u :=
      div_le_div₀ (by linarith) hlog2Q_ge hlogN_pos hlogN_le_65E
    have heq : L / ((6 / 5) * E) = (25 / 3 : ℝ) * (L₂ / L₃) := by
      rw [hEdef]
      field_simp
      ring
    linarith
  have hu_le : u ≤ 20 * (L₂ / L₃) := by
    have h1 : u ≤ (2 * L) / E :=
      div_le_div₀ (by linarith) hlog2Q_le (by linarith : 0 < E) hlogN_gt.le
    have heq : (2 * L) / E = 20 * (L₂ / L₃) := by
      rw [hEdef]
      field_simp
      ring
    linarith
  have hL2divL3 : 1 ≤ L₂ / L₃ := (one_le_div hL30).mpr hL3leL2
  have hu1 : 1 ≤ u := by linarith
  have huN : u ≤ Real.log (N : ℝ) := by
    have h1 : 20 * (L₂ / L₃) ≤ 20 * L₂ := by
      have : L₂ / L₃ ≤ L₂ := div_le_self hL20.le (by linarith)
      linarith
    have h2 : 20 * L₂ ≤ E := by
      rw [hEdef, le_div_iff₀ (by positivity : 0 < 10 * L₂)]
      have : L * 1 ≤ L * L₃ := mul_le_mul_of_nonneg_left (by linarith) hL0.le
      linarith
    linarith
  have h4u : 4 * Real.log u ≤ Real.log (N : ℝ) := by
    have h1 : Real.log u ≤ Real.log (Real.log (N : ℝ)) := Real.log_le_log (by linarith) huN
    have h2 := four_mul_log_le_self (by linarith : 64 ≤ Real.log (N : ℝ))
    linarith
  have hmain := hC (2 * Q) N u h2Qpos hN2 rfl hu1 h4u huN
  have hlogu_ge : (3 / 4 : ℝ) * L₃ ≤ Real.log u := by
    have h1 : L₂ / L₃ ≤ u := by linarith
    have h2 : Real.log (L₂ / L₃) ≤ Real.log u :=
      Real.log_le_log (div_pos hL20 hL30) h1
    rw [Real.log_div hL20.ne' hL30.ne'] at h2
    have h3 := four_mul_log_le_self hL3_64
    linarith
  have hlogu_sub : (2 / 3 : ℝ) * Real.log u ≤ Real.log u - 1 := by linarith
  have hexp_le : -u * Real.log u + u ≤ -(25 / 6 : ℝ) * L₂ := by
    have hprod : (25 / 3 : ℝ) * (L₂ / L₃) * ((2 / 3 : ℝ) * ((3 / 4 : ℝ) * L₃)) ≤
        u * (Real.log u - 1) :=
      mul_le_mul hu_ge (by linarith) (by positivity) (by linarith)
    have hsimp : (25 / 3 : ℝ) * (L₂ / L₃) * ((2 / 3 : ℝ) * ((3 / 4 : ℝ) * L₃)) =
        (25 / 6 : ℝ) * L₂ := by
      field_simp
      ring
    linarith
  have h2C : 2 * C ≤ Real.exp L₂ := by
    rw [← Real.exp_log (by positivity : 0 < 2 * C)]
    exact Real.exp_le_exp.mpr hL2_C
  have hlogN_exp : Real.log (N : ℝ) ≤ Real.exp L₂ := by
    rw [hL2def, Real.exp_log hL0]
    exact hlogN_le_L
  have hfin : Real.exp (-2 * L₂) = 1 / L ^ 2 := by
    have hsq : Real.exp (2 * L₂) = L ^ 2 := by
      rw [show (2 : ℝ) * L₂ = L₂ + L₂ by ring, Real.exp_add, hL2def, Real.exp_log hL0]
      ring
    rw [show -2 * L₂ = -(2 * L₂) by ring, Real.exp_neg, hsq, one_div]
  calc (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers N} : ℝ)
      ≤ C * ((2 * Q : ℕ) : ℝ) * Real.log (N : ℝ) * Real.exp (-u * Real.log u + u) := hmain
    _ = (Q : ℝ) * ((2 * C) * Real.log (N : ℝ) * Real.exp (-u * Real.log u + u)) := by
        push_cast
        ring
    _ ≤ (Q : ℝ) * (Real.exp L₂ * Real.exp L₂ * Real.exp (-(25 / 6 : ℝ) * L₂)) := by
        refine mul_le_mul_of_nonneg_left ?_ (Nat.cast_nonneg Q)
        have hm1 : (2 * C) * Real.log (N : ℝ) ≤ Real.exp L₂ * Real.exp L₂ :=
          mul_le_mul h2C hlogN_exp hlogN_pos.le (Real.exp_pos L₂).le
        exact mul_le_mul hm1 (Real.exp_le_exp.mpr hexp_le) (Real.exp_pos _).le (by positivity)
    _ = (Q : ℝ) * Real.exp (-(13 / 6 : ℝ) * L₂) := by
        rw [← Real.exp_add, ← Real.exp_add]
        congr 2
        ring
    _ ≤ (Q : ℝ) * Real.exp (-2 * L₂) := by
        refine mul_le_mul_of_nonneg_left (Real.exp_le_exp.mpr ?_) (Nat.cast_nonneg Q)
        linarith
    _ = (Q : ℝ) / L ^ 2 := by
        rw [hfin]
        ring

set_option maxHeartbeats 800000 in
/-- **Unified two-layer surviving-prime-count theorem.** For all large `y` and every `Q` in
`[y, y (ln y)⁴]`, there exist residue classes `a` on the odd primes `≤ y / 4` leaving at most
`520 Q (ln₂ y)² / ((ln y)³ ln₃ y) + y / (20 ln y)` uncovered odd primes below `Q`.

This single bound feeds both the unconditional `RankinSmooth` cover (at `Q ≍ y (ln y)² ln₃ y / (ln₂ y)²`)
and the `IteratedLogBound` simultaneous-root upgrade (at `Q ≍ η y (ln y)³ ln₃ y / (ln₂ y)²`). -/
theorem eventually_exists_two_layer_classes :
    ∀ᶠ y : ℕ in atTop, ∀ Q : ℕ, y ≤ Q → (Q : ℝ) ≤ (y : ℝ) * Real.log (y : ℝ) ^ 4 →
      ∃ a : ℕ → ℕ,
        (#{q ∈ range Q | q.Prime ∧ q ≠ 2 ∧ ∀ r ∈ oddPrimesLE (y / 4), ¬ q ≡ a r [MOD r]} : ℝ) ≤
          520 * (Q : ℝ) * Real.log (Real.log (y : ℝ)) ^ 2 /
              (Real.log (y : ℝ) ^ 3 * Real.log (Real.log (Real.log (y : ℝ)))) +
            (y : ℝ) / (20 * Real.log (y : ℝ)) := by
  classical
  obtain ⟨x₀', hx₀'⟩ := eventually_atTop.mp (eventually_primeCounting_bounds (show (0 : ℝ) < 1 / 10 by norm_num))
  set x₀ := max x₀' 0
  have hx₀0 : 0 ≤ x₀ := le_max_right _ _
  have hx₀ : ∀ x : ℝ, x₀ ≤ x →
      (1 - 1 / 10) * (x / Real.log x) ≤ (Nat.primeCounting ⌊x⌋₊ : ℝ) ∧
        (Nat.primeCounting ⌊x⌋₊ : ℝ) ≤ (1 + 1 / 10) * (x / Real.log x) :=
    fun x hx => hx₀' x ((le_max_left _ _).trans hx)
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hL : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hL2 : Tendsto (fun y : ℕ => Real.log (Real.log (y : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL
  have hL3 : Tendsto (fun y : ℕ => Real.log (Real.log (Real.log (y : ℝ)))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL2
  have ho4 := (Real.isLittleO_pow_log_id_atTop (n := 4)).def (show (0 : ℝ) < 1 / 128 by norm_num)
  have ho2 := (Real.isLittleO_pow_log_id_atTop (n := 2)).def (show (0 : ℝ) < 1 / 200 by norm_num)
  filter_upwards [eventually_card_smooth_rankin_le, eventually_ge_atTop 8,
    hcast.eventually ho4, hL.eventually ho2, hL.eventually_ge_atTop 100,
    hL2.eventually_ge_atTop 4, hL3.eventually_ge_atTop 64,
    hcast.eventually_ge_atTop x₀, hcast.eventually_ge_atTop (8 * x₀ + 8)] with
    y hsmooth hy8 h4 h2 hL100 hL2_4 hL3_64 hyx₀ hwx₀
  set L := Real.log (y : ℝ) with hLdef
  set L₂ := Real.log L with hL2def
  set L₃ := Real.log L₂ with hL3def
  set E := L * L₃ / (10 * L₂) with hEdef
  set z := rankinZ y with hzdef
  set w := y / 4 with hwdef
  have hy0 : (0 : ℝ) < y := by exact_mod_cast (by omega : 0 < y)
  have hL0 : 0 < L := by linarith
  have hL20 : 0 < L₂ := by linarith
  have hL30 : 0 < L₃ := by linarith
  have h128 : 128 * L ^ 4 ≤ (y : ℝ) := by
    simp only [id, Real.norm_eq_abs] at h4
    rw [abs_of_nonneg hy0.le, abs_of_nonneg (by positivity : 0 ≤ L ^ 4)] at h4
    linarith
  have hL2L : 200 * L₂ ^ 2 ≤ L := by
    simp only [id, Real.norm_eq_abs] at h2
    rw [abs_of_nonneg hL0.le, abs_of_nonneg (by positivity : 0 ≤ L₂ ^ 2)] at h2
    linarith
  have hL3leL2 : L₃ ≤ L₂ := by
    have := Real.log_le_sub_one_of_pos hL20
    linarith
  have hE64 : 64 ≤ E := by
    have h1 : 1280 * L₂ ≤ E := by
      rw [hEdef, le_div_iff₀ (by positivity : 0 < 10 * L₂)]
      have hmul : 200 * L₂ ^ 2 * 64 ≤ L * L₃ :=
        mul_le_mul hL2L hL3_64 (by norm_num) hL0.le
      linarith
    linarith
  have hz7 : 7 ≤ z := by
    rw [hzdef, rankinZ]
    refine Nat.le_floor ?_
    have h1 := Real.add_one_le_exp E
    push_cast
    linarith
  have hEle : E ≤ L / 10 := by
    rw [hEdef, div_le_div_iff₀ (by positivity : 0 < 10 * L₂) (by norm_num : (0 : ℝ) < 10)]
    nlinarith
  have hzle : (z : ℝ) ≤ (y : ℝ) / (20 * L) := by
    rw [le_div_iff₀ (by positivity : 0 < 20 * L)]
    have hfl : (z : ℝ) ≤ Real.exp E := Nat.floor_le (Real.exp_pos E).le
    have h20L : 20 * L ≤ Real.exp (9 / 10 * L) := by
      have hlin : 9 / 20 * L ≤ Real.exp (9 / 20 * L) := by
        linarith [Real.add_one_le_exp (9 / 20 * L)]
      have hsq : (9 / 20 * L) ^ 2 ≤ Real.exp (9 / 20 * L) ^ 2 :=
        pow_le_pow_left₀ (by positivity) hlin 2
      have hexp2 : Real.exp (9 / 20 * L) ^ 2 = Real.exp (9 / 10 * L) := by
        rw [← Real.exp_natCast_mul]
        congr 1
        push_cast
        ring
      rw [hexp2] at hsq
      nlinarith
    have hprod : Real.exp E * (20 * L) ≤ Real.exp (L / 10) * Real.exp (9 / 10 * L) :=
      mul_le_mul (Real.exp_le_exp.mpr hEle) h20L (by positivity) (Real.exp_pos _).le
    have hexpy : Real.exp (L / 10) * Real.exp (9 / 10 * L) = (y : ℝ) := by
      rw [← Real.exp_add, show L / 10 + 9 / 10 * L = L by ring, hLdef, Real.exp_log hy0]
    have hmul := mul_le_mul_of_nonneg_right hfl (by positivity : 0 ≤ 20 * L)
    linarith
  have hw4 : 4 * w ≤ y := by omega
  have hw4' : y ≤ 4 * w + 3 := by omega
  have hw2 : 2 ≤ w := by omega
  have hwr2 : (y : ℝ) / 8 ≤ w := by
    have : (y : ℝ) ≤ 4 * w + 3 := by exact_mod_cast hw4'
    have hy8r : (8 : ℝ) ≤ y := by exact_mod_cast hy8
    linarith
  have hwx : x₀ ≤ (w : ℝ) := by linarith
  have hlogw : L / 2 ≤ Real.log (w : ℝ) := by
    have h1 : Real.log ((y : ℝ) / 8) ≤ Real.log (w : ℝ) :=
      Real.log_le_log (by positivity) hwr2
    rw [Real.log_div hy0.ne' (by norm_num)] at h1
    have hlog8 : Real.log 8 ≤ 7 := by
      linarith [Real.log_le_sub_one_of_pos (show (0 : ℝ) < 8 by norm_num)]
    linarith
  have hzw : z < w := by
    have h1 : (z : ℝ) < (w : ℝ) := by
      have h20 : (y : ℝ) / (20 * L) < (y : ℝ) / 8 := by
        rw [div_lt_div_iff₀ (by positivity) (by norm_num)]
        nlinarith
      linarith
    exact_mod_cast h1
  intro Q hyQ hQle
  have hQpos : 0 < Q := by omega
  have hQ0 : (0 : ℝ) < Q := by exact_mod_cast hQpos
  have h2Qw : 2 * Q ≤ w * w := by
    have h1 : ((2 * Q : ℕ) : ℝ) ≤ ((w * w : ℕ) : ℝ) := by
      push_cast
      have hsq : (y : ℝ) ^ 2 / 64 ≤ (w : ℝ) * (w : ℝ) := by nlinarith
      have hmul : 2 * (Q : ℝ) ≤ (y : ℝ) ^ 2 / 64 := by
        have := mul_le_mul_of_nonneg_left h128 hy0.le
        nlinarith
      linarith
    exact_mod_cast h1
  set F := Cap.primesIoc z w
  set S := oddPrimesLE z
  set P := {q ∈ range Q | q.Prime ∧ q ≠ 2}
  have hFsub : F ⊆ oddPrimesLE w := by
    intro r hr
    obtain ⟨⟨hzr, hrw⟩, hrp⟩ := Cap.mem_primesIoc.mp hr
    exact mem_oddPrimesLE.mpr ⟨hrw, hrp, by omega⟩
  have hSsub : S ⊆ oddPrimesLE w := by
    intro r hr
    obtain ⟨hrz, hrp, hr2⟩ := mem_oddPrimesLE.mp hr
    exact mem_oddPrimesLE.mpr ⟨by omega, hrp, hr2⟩
  have hFS : Disjoint F S := by
    refine Finset.disjoint_left.mpr fun r hrF hrS => ?_
    have h1 := (Cap.mem_primesIoc.mp hrF).1.1
    have h2 := (mem_oddPrimesLE.mp hrS).1
    omega
  -- Common integer `N₁` on the middle layer `F`
  obtain ⟨N₁, -, -, hN₁⟩ :=
    Cap.exists_common_integer F P hQpos (fun q hq => Finset.mem_range.mp (Finset.mem_filter.mp hq).1)
  set L₁ := #{q ∈ P | ∀ r ∈ F, ¬ q ≡ N₁ [MOD r]}
  set G := #{n ∈ Ico 1 (2 * Q) | ∀ r ∈ F, ¬ r ∣ n}
  -- Bound `#P` by PNT
  have hPr : (#P : ℝ) ≤ 11 / 10 * (Q : ℝ) / L := by
    have hPsub : P ⊆ Nat.primesLE Q := fun q hq => by
      obtain ⟨hqR, hqp, -⟩ := Finset.mem_filter.mp hq
      exact Nat.mem_primesLE.mpr ⟨(Finset.mem_range.mp hqR).le, hqp⟩
    have hPcard : #P ≤ Nat.primeCounting Q := by
      rw [← Nat.primesLE_card_eq_primeCounting]
      exact Finset.card_le_card hPsub
    have hQx₀ : x₀ ≤ (Q : ℝ) := hyx₀.trans (by exact_mod_cast hyQ)
    have hQpnt := (hx₀ (Q : ℝ) hQx₀).2
    rw [Nat.floor_natCast] at hQpnt
    have hlogQ : L ≤ Real.log (Q : ℝ) := Real.log_le_log hy0 (by exact_mod_cast hyQ)
    have h1 : (#P : ℝ) ≤ (Nat.primeCounting Q : ℝ) := by exact_mod_cast hPcard
    calc (#P : ℝ) ≤ (1 + 1 / 10) * ((Q : ℝ) / Real.log (Q : ℝ)) := h1.trans hQpnt
      _ ≤ (1 + 1 / 10) * ((Q : ℝ) / L) :=
          mul_le_mul_of_nonneg_left (div_le_div_of_nonneg_left hQ0.le hL0 hlogQ) (by norm_num)
      _ = 11 / 10 * (Q : ℝ) / L := by ring
  -- Bound `G` by `card_no_factor_le` + `eventually_card_smooth_rankin_le` + `sum_primeCounting_le`
  have hGr : (G : ℝ) ≤ 23 * (Q : ℝ) * L₂ / L := by
    have hno := Cap.card_no_factor_le (z := z) (w := w) (X := 2 * Q) (by omega) h2Qw
    have hsm := hsmooth Q (by omega) hQle
    have hsum := sum_primeCounting_le (δ := 1 / 10) (x₀ := x₀) (by norm_num)
      (fun x hx => (hx₀ x hx).2) (X := 2 * Q) hw2 hwx
    have hdiv_le : ((2 * Q / w : ℕ) : ℝ) ≤ 16 * L ^ 4 := by
      have h1 : ((2 * Q / w : ℕ) : ℝ) ≤ ((2 * Q : ℕ) : ℝ) / (w : ℝ) := Nat.cast_div_le
      have h2 : ((2 * Q : ℕ) : ℝ) / (w : ℝ) ≤ (2 * (y : ℝ) * L ^ 4) / ((y : ℝ) / 8) := by
        push_cast
        exact div_le_div₀ (by positivity) (by linarith) (by positivity) hwr2
      have h3 : (2 * (y : ℝ) * L ^ 4) / ((y : ℝ) / 8) = 16 * L ^ 4 := by
        field_simp
        ring
      linarith
    have hlogdiv : 1 + Real.log ((2 * Q / w : ℕ) : ℝ) ≤ 5 * L₂ := by
      have h1 : Real.log ((2 * Q / w : ℕ) : ℝ) ≤ Real.log (16 * L ^ 4) :=
        log_natCast_le_log (by
          have : 1 ≤ L ^ 4 := one_le_pow₀ (by linarith)
          linarith) hdiv_le
      have h16 : Real.log (16 * L ^ 4) = 4 * Real.log 2 + 4 * L₂ := by
        have h16eq : (16 : ℝ) = (2 : ℝ) ^ 4 := by norm_num
        rw [Real.log_mul (by norm_num) (by positivity), h16eq, Real.log_pow, Real.log_pow]
        push_cast
        rfl
      have hlog2 := Real.log_two_lt_d9
      linarith
    have hbig : ((∑ B ∈ Icc 1 (2 * Q / w), Nat.primeCounting (2 * Q / B) : ℕ) : ℝ) ≤
        22 * (Q : ℝ) * L₂ / L := by
      have h1 : (1 + 1 / 10 : ℝ) * ((2 * Q : ℕ) : ℝ) * (1 + Real.log ((2 * Q / w : ℕ) : ℝ)) /
          Real.log (w : ℝ) ≤
          (1 + 1 / 10 : ℝ) * ((2 * Q : ℕ) : ℝ) * (5 * L₂) / (L / 2) := by
        refine div_le_div₀ (by positivity) ?_ (by positivity) hlogw
        exact mul_le_mul_of_nonneg_left hlogdiv (by positivity)
      have h2 : (1 + 1 / 10 : ℝ) * ((2 * Q : ℕ) : ℝ) * (5 * L₂) / (L / 2) =
          22 * (Q : ℝ) * L₂ / L := by
        push_cast
        field_simp
        ring
      linarith
    have hsm_le : (Q : ℝ) / L ^ 2 ≤ (Q : ℝ) * L₂ / L := by
      rw [div_le_div_iff₀ (by positivity) hL0]
      have h1 : 1 ≤ L * L₂ := one_le_mul_of_one_le_of_one_le (by linarith) (by linarith)
      have h2 : (Q : ℝ) * L * 1 ≤ (Q : ℝ) * L * (L * L₂) :=
        mul_le_mul_of_nonneg_left h1 (by positivity)
      have heq : (Q : ℝ) * L * (L * L₂) = (Q : ℝ) * L₂ * L ^ 2 := by ring
      linarith
    have hGnat : (G : ℝ) ≤
        (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers (z + 1)} : ℝ) +
          ((∑ B ∈ Icc 1 (2 * Q / w), Nat.primeCounting (2 * Q / B) : ℕ) : ℝ) := by
      exact_mod_cast hno
    have hadd23 : (Q : ℝ) * L₂ / L + 22 * (Q : ℝ) * L₂ / L = 23 * (Q : ℝ) * L₂ / L := by ring
    have hsm' : (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers (z + 1)} : ℝ) ≤ (Q : ℝ) / L ^ 2 :=
      hsm
    linarith
  -- Deduce `L₁ ≤ 26 Q L₂ / L²`
  have hL₁r : (L₁ : ℝ) ≤ 26 * (Q : ℝ) * L₂ / L ^ 2 := by
    have hmul : (L₁ : ℝ) * (Q : ℝ) ≤ (#P : ℝ) * (G : ℝ) := by exact_mod_cast hN₁
    have hPG : (#P : ℝ) * (G : ℝ) ≤ (11 / 10 * (Q : ℝ) / L) * (23 * (Q : ℝ) * L₂ / L) :=
      mul_le_mul hPr hGr (Nat.cast_nonneg G) (by positivity)
    have hcalc : (11 / 10 * (Q : ℝ) / L) * (23 * (Q : ℝ) * L₂ / L) ≤
        (26 * (Q : ℝ) * L₂ / L ^ 2) * (Q : ℝ) := by
      have heq1 : (11 / 10 * (Q : ℝ) / L) * (23 * (Q : ℝ) * L₂ / L) =
          (253 / 10) * ((Q : ℝ) ^ 2 * L₂ / L ^ 2) := by
        field_simp
        ring
      have heq2 : (26 * (Q : ℝ) * L₂ / L ^ 2) * (Q : ℝ) =
          26 * ((Q : ℝ) ^ 2 * L₂ / L ^ 2) := by
        field_simp
      rw [heq1, heq2]
      have hnn : 0 ≤ (Q : ℝ) ^ 2 * L₂ / L ^ 2 := by positivity
      linarith
    exact le_of_mul_le_mul_right (hmul.trans (hPG.trans hcalc)) hQ0
  -- Pigeonhole on the small primes `S = oddPrimesLE z`
  set P₁ := {q ∈ P | q ∉ S ∧ ∀ r ∈ F, ¬ q ≡ N₁ [MOD r]}
  set Z := {q ∈ P | q ∈ S}
  have hP₁_le : #P₁ ≤ L₁ := by
    refine Finset.card_le_card fun q hq => ?_
    obtain ⟨hqP, -, hqF⟩ := Finset.mem_filter.mp hq
    exact Finset.mem_filter.mpr ⟨hqP, hqF⟩
  have hZ_le : #Z ≤ z := by
    have h1 : #Z ≤ #(Icc 1 z) := by
      refine Finset.card_le_card fun q hq => ?_
      have hqS := (Finset.mem_filter.mp hq).2
      obtain ⟨hqz, hqp, -⟩ := mem_oddPrimesLE.mp hqS
      exact Finset.mem_Icc.mpr ⟨hqp.one_le, hqz⟩
    rw [Nat.card_Icc] at h1
    omega
  have hS2 : ∀ r ∈ S, 2 ≤ r := fun r hr => (mem_oddPrimesLE.mp hr).2.1.two_le
  have hP₁nodvd : ∀ q ∈ P₁, ∀ r ∈ S, ¬ r ∣ q := by
    intro q hq r hr hrq
    obtain ⟨hqP, hqnotS, -⟩ := Finset.mem_filter.mp hq
    have hqp : q.Prime := (Finset.mem_filter.mp hqP).2.1
    have hrp : r.Prime := (mem_oddPrimesLE.mp hr).2.1
    have heq := (Nat.prime_dvd_prime_iff_eq hrp hqp).mp hrq
    exact hqnotS (heq ▸ hr)
  obtain ⟨b, hb, hrows⟩ := Cap.exists_rowsLeft_le S P₁ hS2 hP₁nodvd
  have hrows_r : (#(Cap.rowsLeft S P₁ b) : ℝ) ≤ 520 * (Q : ℝ) * L₂ ^ 2 / (L ^ 3 * L₃) := by
    have hprodpos : (0 : ℝ) < ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) := by
      have : 0 < ∏ r ∈ S, (r - 1) := Finset.prod_pos fun r hr => by
        have := three_le_of_mem_oddPrimesLE hr
        omega
      exact_mod_cast this
    have hrows_prod : (#(Cap.rowsLeft S P₁ b) : ℝ) ≤ (#P₁ : ℝ) * oddPrimeProd z := by
      rw [oddPrimeProd_eq z, ← mul_div_assoc, le_div_iff₀ hprodpos]
      exact_mod_cast hrows
    have hlogz1 : E < Real.log ((z : ℝ) + 1) := by
      rw [← Real.log_exp E]
      exact Real.log_lt_log (Real.exp_pos E) (by simpa [hzdef, rankinZ] using Nat.lt_floor_add_one (Real.exp E))
    have hPi : oddPrimeProd z ≤ 20 * L₂ / (L * L₃) := by
      have h1 := oddPrimeProd_le hz7
      have h2 : 1575 / 1152 / Real.log ((z : ℝ) + 1) ≤ 2 / E := by
        calc 1575 / 1152 / Real.log ((z : ℝ) + 1)
            ≤ 1575 / 1152 / E := div_le_div_of_nonneg_left (by norm_num) (by linarith) hlogz1.le
          _ ≤ 2 / E := div_le_div_of_nonneg_right (by norm_num) (by linarith)
      have h3 : 2 / E = 20 * L₂ / (L * L₃) := by
        rw [hEdef]
        field_simp
        ring
      linarith
    have hPi0 : 0 ≤ oddPrimeProd z := Finset.prod_nonneg fun r hr => by
      have h3 : (3 : ℝ) ≤ r := by exact_mod_cast three_le_of_mem_oddPrimesLE hr
      exact div_nonneg (by linarith) (by linarith)
    have hP₁r : (#P₁ : ℝ) ≤ 26 * (Q : ℝ) * L₂ / L ^ 2 :=
      le_trans (by exact_mod_cast hP₁_le) hL₁r
    calc (#(Cap.rowsLeft S P₁ b) : ℝ)
        ≤ (#P₁ : ℝ) * oddPrimeProd z := hrows_prod
      _ ≤ (26 * (Q : ℝ) * L₂ / L ^ 2) * (20 * L₂ / (L * L₃)) :=
          mul_le_mul hP₁r hPi hPi0 (by positivity)
      _ = 520 * (Q : ℝ) * L₂ ^ 2 / (L ^ 3 * L₃) := by
          field_simp
          ring
  -- Combine classes on `F` and `S`
  refine ⟨fun r => if r ∈ F then N₁ else if h : r ∈ S then b r h else 0, ?_⟩
  have hsub : {q ∈ range Q | q.Prime ∧ q ≠ 2 ∧
      ∀ r ∈ oddPrimesLE w, ¬ q ≡ (if r ∈ F then N₁ else if h : r ∈ S then b r h else 0) [MOD r]} ⊆
      Cap.rowsLeft S P₁ b ∪ Z := by
    intro q hq
    obtain ⟨hqR, hqp, hq2, hqcov⟩ := Finset.mem_filter.mp hq
    have hqP : q ∈ P := Finset.mem_filter.mpr ⟨hqR, hqp, hq2⟩
    by_cases hqS : q ∈ S
    · exact Finset.mem_union_right _ (Finset.mem_filter.mpr ⟨hqP, hqS⟩)
    · refine Finset.mem_union_left _ (Finset.mem_filter.mpr ⟨?_, ?_⟩)
      · refine Finset.mem_filter.mpr ⟨hqP, hqS, fun r hrF => ?_⟩
        have h1 := hqcov r (hFsub hrF)
        simpa [hrF] using h1
      · intro r hrS hmod
        have hrnotF : r ∉ F := fun h => Finset.disjoint_left.mp hFS h hrS
        have h1 := hqcov r (hSsub hrS)
        simp only [hrnotF, ↓reduceIte, hrS, ↓reduceDIte] at h1
        have hbr : b r hrS < r := (Finset.mem_Ico.mp ((Finset.mem_pi.mp hb) r hrS)).2
        apply h1
        show q % r = b r hrS % r
        rw [Nat.mod_eq_of_lt hbr, hmod]
  have hcard : #{q ∈ range Q | q.Prime ∧ q ≠ 2 ∧
      ∀ r ∈ oddPrimesLE w, ¬ q ≡ (if r ∈ F then N₁ else if h : r ∈ S then b r h else 0) [MOD r]} ≤
      #(Cap.rowsLeft S P₁ b) + #Z :=
    (Finset.card_le_card hsub).trans (Finset.card_union_le _ _)
  have hZr : (#Z : ℝ) ≤ (y : ℝ) / (20 * L) := (by exact_mod_cast hZ_le : (#Z : ℝ) ≤ (z : ℝ)).trans hzle
  have hcardr : (#{q ∈ range Q | q.Prime ∧ q ≠ 2 ∧
      ∀ r ∈ oddPrimesLE w, ¬ q ≡ (if r ∈ F then N₁ else if h : r ∈ S then b r h else 0) [MOD r]} : ℝ) ≤
      (#(Cap.rowsLeft S P₁ b) : ℝ) + (#Z : ℝ) := by exact_mod_cast hcard
  linarith

/-! ### Section C: Reusable CRT and partial-cover helpers -/

/-- For any set `R` of odd primes `≤ y` (with `2 ≤ y`), `2 * ∏ r ∈ R, r ∣ primorial y`. -/
theorem two_mul_prod_dvd_primorial {R : Finset ℕ} {y : ℕ}
    (hR : ∀ r ∈ R, r.Prime ∧ r ≠ 2) (hB : ∀ r ∈ R, r ≤ y) (hy2 : 2 ≤ y) :
    2 * ∏ r ∈ R, r ∣ primorial y := by
  have h2not : 2 ∉ R := fun h2 => (hR 2 h2).2 rfl
  have hsub : insert 2 R ⊆ (range (y + 1)).filter Nat.Prime := by
    intro r hr
    rcases Finset.mem_insert.mp hr with rfl | hrR
    · exact Finset.mem_filter.mpr ⟨Finset.mem_range.mpr (by omega), Nat.prime_two⟩
    · exact Finset.mem_filter.mpr ⟨Finset.mem_range.mpr (by have := hB r hrR; omega), (hR r hrR).1⟩
  have hins : 2 * ∏ r ∈ R, r = ∏ r ∈ insert 2 R, r :=
    (Finset.prod_insert (f := fun r : ℕ => r) h2not).symm
  rw [hins]
  exact Finset.prod_dvd_prod_of_subset (insert 2 R) ((range (y + 1)).filter Nat.Prime)
    (fun r : ℕ => r) hsub

/-- Extract an even base residue `b < primorial y` realizing all classes `a r` on a set `R` of
odd primes `≤ y`. Every shift `b + t * primorial y` is then even and inherits all congruences on `R`. -/
theorem exists_base_even_of_classes {R : Finset ℕ} {a : ℕ → ℕ} {y : ℕ}
    (hR : ∀ r ∈ R, r.Prime ∧ r ≠ 2) (hB : ∀ r ∈ R, r ≤ y) (hy2 : 2 ≤ y) :
    ∃ b : ℕ, Even b ∧ b < primorial y ∧ ∀ r ∈ R, b ≡ a r [MOD r] := by
  classical
  set M := ∏ r ∈ R, r with hM
  have hrM : ∀ r ∈ R, r ∣ M := fun r hr => Finset.dvd_prod_of_mem (fun r => r) hr
  have hpp : Set.Pairwise (R : Set ℕ) (Function.onFun Nat.Coprime fun r : ℕ => r) :=
    fun r hr r' hr' hne => (Nat.coprime_primes (hR r hr).1 (hR r' hr').1).mpr hne
  have hs0 : ∀ r ∈ R, (fun r : ℕ => r) r ≠ 0 := fun r hr => (hR r hr).1.ne_zero
  obtain ⟨x₀, hx₀⟩ := Nat.chineseRemainderOfFinset a (fun r => r) R hs0 hpp
  have hModd : M % 2 = 1 := by
    rcases Nat.mod_two_eq_zero_or_one M with h | h
    · exfalso
      have h2 : 2 ∣ M := Nat.dvd_of_mod_eq_zero h
      obtain ⟨r, hr, h2r⟩ := (Prime.dvd_finsetProd_iff Nat.prime_two.prime _).mp h2
      exact (hR r hr).2 ((Nat.prime_dvd_prime_iff_eq Nat.prime_two (hR r hr).1).mp h2r).symm
    · exact h
  obtain ⟨x, hxeven, hx⟩ : ∃ x, x % 2 = 0 ∧ ∀ r ∈ R, x ≡ a r [MOD r] := by
    rcases Nat.mod_two_eq_zero_or_one x₀ with h | h
    · exact ⟨x₀, h, hx₀⟩
    · refine ⟨x₀ + M, by omega, fun r hr => ?_⟩
      have h1 : x₀ + M ≡ x₀ [MOD r] := by
        obtain ⟨c, hc⟩ := hrM r hr
        show (x₀ + M) % r = x₀ % r
        rw [hc, Nat.add_mul_mod_self_left]
      exact h1.trans (hx₀ r hr)
  refine ⟨x % primorial y, ?_, Nat.mod_lt x (primorial_pos y), ?_⟩
  · have hmod2 : x % primorial y ≡ x [MOD 2] :=
      (Nat.mod_modEq x (primorial y)).of_dvd (Nat.prime_two.dvd_primorial_iff.mpr hy2)
    have h2eq : (x % primorial y) % 2 = x % 2 := hmod2
    exact Nat.even_iff.mpr (by omega)
  · intro r hr
    have hrP : r ∣ primorial y := (hR r hr).1.dvd_primorial_iff.mpr (hB r hr)
    exact ((Nat.mod_modEq x (primorial y)).of_dvd hrP).trans (hx r hr)

/-- Partial-cover kill lemma: any even `N > Q + y` realizing `a` on a set `R` of odd primes `≤ y`
eliminates `q = 2` and every `q < Q` covered by some `r ∈ R`. -/
theorem not_isSummand_of_partial_cover {R : Finset ℕ} {a : ℕ → ℕ} {N Q y : ℕ}
    (hR : ∀ r ∈ R, r.Prime ∧ r ≠ 2) (hB : ∀ r ∈ R, r ≤ y) (hy2 : 2 ≤ y)
    (hN : ∀ r ∈ R, N ≡ a r [MOD r]) (heven : Even N) (hbig : Q + y < N)
    {q : ℕ} (hqQ : q < Q) (hcov : q = 2 ∨ ∃ r ∈ R, q ≡ a r [MOD r]) :
    ¬ IsSummand N q := by
  rintro ⟨-, hNq⟩
  rcases hcov with rfl | ⟨r, hr, hqr⟩
  · have h2 : 2 ∣ N - 2 := Nat.dvd_sub (even_iff_two_dvd.mp heven) dvd_rfl
    have := (Nat.prime_dvd_prime_iff_eq Nat.prime_two hNq).mp h2
    omega
  · have hle : q ≤ N := by omega
    have hdvd : r ∣ N - q := (Nat.modEq_iff_dvd' hle).mp (hqr.trans (hN r hr).symm)
    have hr3 : 3 ≤ r := by
      have h1 := (hR r hr).1.two_le
      have h2 := (hR r hr).2
      omega
    have hry : r ≤ y := hB r hr
    rcases (Nat.dvd_prime hNq).mp hdvd with h1 | h1
    · omega
    · omega

/-- Place an even CRT realization of a complete cover inside any interval `[L₀, U₀]` of length
at least `primorial y` above `Q + y`. -/
theorem exists_even_in_Icc_of_cover {R : Finset ℕ} {a : ℕ → ℕ} {Q y L₀ U₀ : ℕ}
    (hR : ∀ r ∈ R, r.Prime ∧ r ≠ 2) (hB : ∀ r ∈ R, r ≤ y) (hy2 : 2 ≤ y)
    (hcover : ∀ q, q.Prime → q ≠ 2 → q < Q → ∃ r ∈ R, q ≡ a r [MOD r])
    (hL₀ : Q + y < L₀) (hwin : L₀ + primorial y ≤ U₀) :
    ∃ N : ℕ, L₀ ≤ N ∧ N ≤ U₀ ∧ Even N ∧ ∀ q < Q, ¬ IsSummand N q := by
  obtain ⟨b, hbe, hbP, hbres⟩ := exists_base_even_of_classes (a := a) hR hB hy2
  set P := primorial y with hPdef
  have hP0 : 0 < P := primorial_pos y
  set D := L₀ + P - 1 - b
  set t := D / P
  set N := b + P * t
  have h1 : P * t ≤ D := Nat.mul_div_le D P
  have h2 : D < P * (t + 1) := Nat.lt_mul_div_succ D hP0
  rw [Nat.mul_succ] at h2
  have hNL₀ : L₀ ≤ N := by omega
  have hNU₀ : N ≤ U₀ := by omega
  have hNmodP : N ≡ b [MOD P] := by
    show (b + P * t) % P = b % P
    rw [Nat.add_mul_mod_self_left]
  have hNeven : Even N := by
    have h2P : 2 ∣ P := Nat.prime_two.dvd_primorial_iff.mpr hy2
    have hmod2 : N ≡ b [MOD 2] := hNmodP.of_dvd h2P
    have h2eq : N % 2 = b % 2 := hmod2
    have hb0 : b % 2 = 0 := Nat.even_iff.mp hbe
    exact Nat.even_iff.mpr (by omega)
  have hNres : ∀ r ∈ R, N ≡ a r [MOD r] := fun r hr =>
    (hNmodP.of_dvd ((hR r hr).1.dvd_primorial_iff.mpr (hB r hr))).trans (hbres r hr)
  refine ⟨N, hNL₀, hNU₀, hNeven, fun q hqQ => ?_⟩
  exact not_isSummand_of_cover (fun r hr => (hR r hr).1.two_le) hcover hNres hNeven
    (fun r hr => by have := hB r hr; omega) (by omega) hqQ

/-! ### Section D: Unconditional upgraded iterated-log theorems -/

/-- **Unconditional `y`-scale complete cover with the Rankin `log₃ y` factor.** For all large `y`,
classes modulo odd primes `≤ y` cover every odd prime below
`⌊y · (ln y)² · ln₃ y / (2000 · (ln₂ y)²)⌋`. -/
theorem eventually_exists_classes_rankin :
    ∀ᶠ y : ℕ in atTop, 2 ≤ y ∧ ∃ a : ℕ → ℕ, ∀ q : ℕ, q.Prime → q ≠ 2 →
      q < ⌊(y : ℝ) * Real.log (y : ℝ) ^ 2 * Real.log (Real.log (Real.log (y : ℝ))) /
          (2000 * Real.log (Real.log (y : ℝ)) ^ 2)⌋₊ →
      ∃ r ∈ oddPrimesLE y, q ≡ a r [MOD r] := by
  classical
  obtain ⟨x₀', hx₀'⟩ := eventually_atTop.mp (eventually_primeCounting_bounds (show (0 : ℝ) < 1 / 10 by norm_num))
  set x₀ := max x₀' 0
  have hx₀ : ∀ x : ℝ, x₀ ≤ x →
      (1 - 1 / 10) * (x / Real.log x) ≤ (Nat.primeCounting ⌊x⌋₊ : ℝ) ∧
        (Nat.primeCounting ⌊x⌋₊ : ℝ) ≤ (1 + 1 / 10) * (x / Real.log x) :=
    fun x hx => hx₀' x ((le_max_left _ _).trans hx)
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hL : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hL2 : Tendsto (fun y : ℕ => Real.log (Real.log (y : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL
  have hL3 : Tendsto (fun y : ℕ => Real.log (Real.log (Real.log (y : ℝ)))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL2
  have ho2 := (Real.isLittleO_pow_log_id_atTop (n := 2)).def (show (0 : ℝ) < 1 / 2000 by norm_num)
  filter_upwards [eventually_exists_two_layer_classes, eventually_ge_atTop 16,
    hL.eventually ho2, hL.eventually_ge_atTop 100, hL2.eventually_ge_atTop 4,
    hL3.eventually_ge_atTop 2, hcast.eventually_ge_atTop x₀,
    hcast.eventually_ge_atTop (8 * x₀ + 8)] with
    y htwo hy16 h2 hL100 hL2_4 hL3_2 hyx₀ hwx₀
  set L := Real.log (y : ℝ) with hLdef
  set L₂ := Real.log L with hL2def
  set L₃ := Real.log L₂ with hL3def
  set R := (y : ℝ) * L ^ 2 * L₃ / (2000 * L₂ ^ 2)
  set Q := ⌊R⌋₊
  have hy0 : (0 : ℝ) < y := by exact_mod_cast (by omega : 0 < y)
  have hL0 : 0 < L := by linarith
  have hL20 : 0 < L₂ := by linarith
  have hL30 : 0 < L₃ := by linarith
  have hL2L : 2000 * L₂ ^ 2 ≤ L := by
    simp only [id, Real.norm_eq_abs] at h2
    rw [abs_of_nonneg hL0.le, abs_of_nonneg (by positivity : 0 ≤ L₂ ^ 2)] at h2
    linarith
  have hL3leL2 : L₃ ≤ L₂ := by
    have := Real.log_le_sub_one_of_pos hL20
    linarith
  have hL2leL : L₂ ≤ L := by
    have := Real.log_le_sub_one_of_pos hL0
    linarith
  have hRge : (y : ℝ) + 1 ≤ R := by
    have h1 : 2 * (y : ℝ) ≤ R := by
      rw [le_div_iff₀ (by positivity : 0 < 2000 * L₂ ^ 2)]
      have hmul : 2000 * L₂ ^ 2 * 2 ≤ L ^ 2 * L₃ := by
        have hLsq : L ≤ L ^ 2 := le_self_pow₀ (by linarith) (by norm_num)
        nlinarith
      nlinarith
    have hy16r : (16 : ℝ) ≤ y := by exact_mod_cast hy16
    linarith
  have hyQ : y ≤ Q := by
    apply Nat.le_floor
    linarith
  have hQleR : (Q : ℝ) ≤ R := Nat.floor_le (by positivity)
  have hQle : (Q : ℝ) ≤ (y : ℝ) * L ^ 4 := by
    have hRle : R ≤ (y : ℝ) * L ^ 4 := by
      rw [div_le_iff₀ (by positivity : 0 < 2000 * L₂ ^ 2)]
      have h1 : L₃ ≤ L ^ 2 := by
        have hLsq : L ≤ L ^ 2 := le_self_pow₀ (by linarith) (by norm_num)
        linarith
      have h2 : (1 : ℝ) ≤ 2000 * L₂ ^ 2 := by
        have hsq : (1 : ℝ) ≤ L₂ ^ 2 := one_le_pow₀ (by linarith)
        linarith
      have h3 : (y : ℝ) * L ^ 2 * L₃ ≤ (y : ℝ) * L ^ 2 * L ^ 2 :=
        mul_le_mul_of_nonneg_left h1 (by positivity)
      have h4 : ((y : ℝ) * L ^ 4) * 1 ≤ ((y : ℝ) * L ^ 4) * (2000 * L₂ ^ 2) :=
        mul_le_mul_of_nonneg_left h2 (by positivity)
      have heq : (y : ℝ) * L ^ 2 * L ^ 2 = (y : ℝ) * L ^ 4 := by ring
      linarith
    exact hQleR.trans hRle
  obtain ⟨a, ha⟩ := htwo Q hyQ hQle
  set w := y / 4
  set U := {q ∈ range Q | q.Prime ∧ q ≠ 2 ∧ ∀ r ∈ oddPrimesLE w, ¬ q ≡ a r [MOD r]}
  set T := (Nat.primesLE y).filter (w < ·)
  -- Bound `#U ≤ (31 / 100) y / L`
  have hUr : (#U : ℝ) ≤ 31 / 100 * ((y : ℝ) / L) := by
    have h1 : 520 * (Q : ℝ) * L₂ ^ 2 / (L ^ 3 * L₃) ≤ 520 * R * L₂ ^ 2 / (L ^ 3 * L₃) := by
      refine div_le_div_of_nonneg_right ?_ (by positivity)
      exact mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hQleR (by norm_num)) (by positivity)
    have h2 : 520 * R * L₂ ^ 2 / (L ^ 3 * L₃) = 26 / 100 * ((y : ℝ) / L) := by
      simp only [R]
      field_simp
      ring
    have h3 : (y : ℝ) / (20 * L) = 5 / 100 * ((y : ℝ) / L) := by ring
    linarith
  -- Bound `#T ≥ (7 / 20) y / L` by PNT
  have hw4 : 4 * w ≤ y := by omega
  have hw4' : y ≤ 4 * w + 3 := by omega
  have hwr1 : (w : ℝ) ≤ (y : ℝ) / 4 := by
    have : (4 : ℝ) * w ≤ y := by exact_mod_cast hw4
    linarith
  have hwr2 : (y : ℝ) / 8 ≤ (w : ℝ) := by
    have : (y : ℝ) ≤ 4 * w + 3 := by exact_mod_cast hw4'
    have hy16r : (16 : ℝ) ≤ y := by exact_mod_cast hy16
    linarith
  have hwx : x₀ ≤ (w : ℝ) := by linarith
  have hlogw : L / 2 ≤ Real.log (w : ℝ) := by
    have h1 : Real.log ((y : ℝ) / 8) ≤ Real.log (w : ℝ) :=
      Real.log_le_log (by positivity) hwr2
    rw [Real.log_div hy0.ne' (by norm_num)] at h1
    have hlog8 : Real.log 8 ≤ 7 := by
      linarith [Real.log_le_sub_one_of_pos (show (0 : ℝ) < 8 by norm_num)]
    linarith
  have hT' : Nat.primeCounting y ≤ Nat.primeCounting w + #T := by
    rw [← Nat.primesLE_card_eq_primeCounting, ← Nat.primesLE_card_eq_primeCounting]
    refine (Finset.card_le_card fun p hp => ?_).trans (Finset.card_union_le _ _)
    by_cases h : p ≤ w
    · exact Finset.mem_union.mpr (Or.inl (Nat.mem_primesLE.mpr ⟨h, (Nat.mem_primesLE.mp hp).2⟩))
    · exact Finset.mem_union.mpr (Or.inr (Finset.mem_filter.mpr ⟨hp, by omega⟩))
  have hTr : 7 / 20 * ((y : ℝ) / L) ≤ (#T : ℝ) := by
    have h1 : (Nat.primeCounting y : ℝ) ≤ Nat.primeCounting w + #T := by exact_mod_cast hT'
    have h2 : (1 - 1 / 10) * ((y : ℝ) / L) ≤ (Nat.primeCounting y : ℝ) := by
      have := (hx₀ (y : ℝ) hyx₀).1
      rwa [Nat.floor_natCast] at this
    have h3 : (Nat.primeCounting w : ℝ) ≤ 11 / 20 * ((y : ℝ) / L) := by
      have h4 := (hx₀ (w : ℝ) hwx).2
      rw [Nat.floor_natCast] at h4
      calc (Nat.primeCounting w : ℝ)
          ≤ (1 + 1 / 10) * ((w : ℝ) / Real.log (w : ℝ)) := h4
        _ ≤ (1 + 1 / 10) * (((y : ℝ) / 4) / (L / 2)) :=
            mul_le_mul_of_nonneg_left (div_le_div₀ (by positivity) hwr1 (by positivity) hlogw)
              (by norm_num)
        _ = 11 / 20 * ((y : ℝ) / L) := by
            field_simp
            ring
    linarith
  have hUT : #U ≤ #T := by
    have hUrTr : (#U : ℝ) ≤ (#T : ℝ) := by
      have : 0 ≤ (y : ℝ) / L := by positivity
      linarith
    exact_mod_cast hUrTr
  obtain ⟨g, hg⟩ := Cap.exists_assignment_of_card_le U T hUT
  refine ⟨by omega, fun r => if r ∈ oddPrimesLE w then a r else g r, ?_⟩
  intro q hqp hq2 hqQ
  by_cases hcov : ∃ r ∈ oddPrimesLE w, q ≡ a r [MOD r]
  · obtain ⟨r, hr, hqr⟩ := hcov
    have hru : r ∈ oddPrimesLE y := by
      obtain ⟨hrw, hrp, hr2⟩ := mem_oddPrimesLE.mp hr
      exact mem_oddPrimesLE.mpr ⟨by omega, hrp, hr2⟩
    refine ⟨r, hru, ?_⟩
    simpa [hr] using hqr
  · push Not at hcov
    have hqU : q ∈ U := Finset.mem_filter.mpr ⟨Finset.mem_range.mpr hqQ, hqp, hq2, hcov⟩
    obtain ⟨t, htT, hgt⟩ := hg q hqU
    obtain ⟨htP, htw⟩ := Finset.mem_filter.mp htT
    obtain ⟨hty, htp⟩ := Nat.mem_primesLE.mp htP
    have htnot : t ∉ oddPrimesLE w := fun h => by
      have := (mem_oddPrimesLE.mp h).1
      omega
    have htodd : t ∈ oddPrimesLE y := mem_oddPrimesLE.mpr ⟨hty, htp, by omega⟩
    refine ⟨t, htodd, ?_⟩
    simp only [htnot, ↓reduceIte, hgt]
    exact Nat.ModEq.refl q

set_option maxHeartbeats 800000 in
/-- **Unconditional Rankin-upgraded iterated-log lower bound on `[X / 2, X]`.** For all large `X`,
there is an even integer `N ∈ [X / 2, X]` with no Goldbach summand below
`ln X · (ln₂ X)² · ln₄ X / (65000 · (ln₃ X)²)`. -/
theorem eventually_exists_even_le_rankin :
    ∀ᶠ X : ℕ in atTop, ∃ N : ℕ, X / 2 ≤ N ∧ N ≤ X ∧ Even N ∧
      ∀ q : ℕ, (q : ℝ) < Real.log (X : ℝ) * Real.log (Real.log (X : ℝ)) ^ 2 *
          Real.log (Real.log (Real.log (Real.log (X : ℝ)))) /
          (65000 * Real.log (Real.log (Real.log (X : ℝ))) ^ 2) → ¬ IsSummand N q := by
  have hcast : Tendsto (fun X : ℕ => (X : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hL : Tendsto (fun X : ℕ => Real.log (X : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hLL : Tendsto (fun X : ℕ => Real.log (Real.log (X : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL
  have hLLL : Tendsto (fun X : ℕ => Real.log (Real.log (Real.log (X : ℝ)))) atTop atTop :=
    Real.tendsto_log_atTop.comp hLL
  have hLLLL : Tendsto (fun X : ℕ => Real.log (Real.log (Real.log (Real.log (X : ℝ))))) atTop atTop :=
    Real.tendsto_log_atTop.comp hLLL
  have hy : Tendsto (fun X : ℕ => ⌊Real.log (X : ℝ) / 2⌋₊) atTop atTop :=
    tendsto_nat_floor_atTop.comp (hL.atTop_div_const (by norm_num))
  filter_upwards [hy.eventually eventually_exists_classes_rankin,
    hy.eventually (eventually_primorial_le (show (0 : ℝ) < 1 / 4 by norm_num)),
    hL.eventually_ge_atTop 4160000, hLL.eventually_ge_atTop 6,
    hLLL.eventually_ge_atTop 2, hLLLL.eventually_ge_atTop 2, eventually_ge_atTop 8] with
    X hcl hpr hLbig hLL6 hLLL2 hLLLL2 hX8
  set L := Real.log (X : ℝ) with hLdef
  set LL := Real.log L with hLLdef
  set LLL := Real.log LL with hLLLdef
  set LLLL := Real.log LLL with hLLLLdef
  set y := ⌊L / 2⌋₊ with hydef
  obtain ⟨hy2, a, hcover⟩ := hcl
  have hLpos : 0 < L := by linarith
  have hXpos : (0 : ℝ) < X := by exact_mod_cast (by omega : 0 < X)
  have hyle : (y : ℝ) ≤ L / 2 := Nat.floor_le (by positivity)
  have hyge : L / 4 ≤ (y : ℝ) := by
    have := Nat.sub_one_lt_floor (L / 2)
    linarith
  have hypos : (0 : ℝ) < y := by linarith
  -- Iterate logarithm bounds at `y`
  set ly := Real.log (y : ℝ)
  set lly := Real.log ly
  set llly := Real.log lly
  have hly_le : ly ≤ LL := Real.log_le_log hypos (by linarith)
  have hly_ge : LL / 2 ≤ ly := by
    have h1 : Real.log (L / 4) ≤ ly := Real.log_le_log (by positivity) hyge
    rw [Real.log_div hLpos.ne' (by norm_num)] at h1
    have hlog4 : Real.log 4 ≤ 3 := by
      linarith [Real.log_le_sub_one_of_pos (show (0 : ℝ) < 4 by norm_num)]
    linarith
  have hly3 : 3 ≤ ly := by linarith
  have hlly_le : lly ≤ LLL := Real.log_le_log (by linarith) hly_le
  have hlly_ge : LLL / 2 ≤ lly := by
    have h1 : Real.log (LL / 2) ≤ lly := Real.log_le_log (by positivity) hly_ge
    rw [Real.log_div (by linarith) (by norm_num)] at h1
    have hlog2 : Real.log 2 ≤ 1 := by
      linarith [Real.log_le_sub_one_of_pos (show (0 : ℝ) < 2 by norm_num)]
    linarith
  have hlly1 : 1 ≤ lly := by linarith
  have hllly_ge : LLLL / 2 ≤ llly := by
    have h1 : Real.log (LLL / 2) ≤ llly := Real.log_le_log (by positivity) hlly_ge
    rw [Real.log_div (by linarith) (by norm_num)] at h1
    have hlog2 : Real.log 2 ≤ 1 := by
      linarith [Real.log_le_sub_one_of_pos (show (0 : ℝ) < 2 by norm_num)]
    linarith
  have hLLpos : 0 < LL := by linarith
  have hLLLpos : 0 < LLL := by linarith
  have hLLLLpos : 0 < LLLL := by linarith
  have hlypos : 0 < ly := by linarith
  have hllypos : 0 < lly := by linarith
  have hlllypos : 0 < llly := by linarith
  have hllly_le : llly ≤ lly := by
    have := Real.log_le_sub_one_of_pos (by linarith : 0 < lly)
    linarith
  have hLLL_le : LLL ≤ LL := by
    have := Real.log_le_sub_one_of_pos (by linarith : 0 < LL)
    linarith
  have hLL_le : LL ≤ L := by
    have := Real.log_le_sub_one_of_pos hLpos
    linarith
  set R := (y : ℝ) * ly ^ 2 * llly / (2000 * lly ^ 2)
  set Q := ⌊R⌋₊
  -- Lower bound on `R`
  have hRge : L * LL ^ 2 * LLLL / (64000 * LLL ^ 2) ≤ R := by
    have hnum1 : (L / 4) * (LL / 2) ^ 2 ≤ (y : ℝ) * ly ^ 2 :=
      mul_le_mul hyge (pow_le_pow_left₀ (by linarith) hly_ge 2) (by positivity) hypos.le
    have hnum : (L / 4) * (LL / 2) ^ 2 * (LLLL / 2) ≤ (y : ℝ) * ly ^ 2 * llly :=
      mul_le_mul hnum1 hllly_ge (by positivity) (by positivity)
    have hden : 2000 * lly ^ 2 ≤ 2000 * LLL ^ 2 := by
      have := pow_le_pow_left₀ (by linarith) hlly_le 2
      linarith
    have hdiv := div_le_div₀ (by positivity) hnum (by positivity : 0 < 2000 * lly ^ 2) hden
    have heq : (L / 4) * (LL / 2) ^ 2 * (LLLL / 2) / (2000 * LLL ^ 2) =
        L * LL ^ 2 * LLLL / (64000 * LLL ^ 2) := by
      field_simp
      ring
    linarith
  have hτ : L * LL ^ 2 * LLLL / (65000 * LLL ^ 2) + 1 ≤ R := by
    have heq : L * LL ^ 2 * LLLL / (64000 * LLL ^ 2) - L * LL ^ 2 * LLLL / (65000 * LLL ^ 2) =
        L * LL ^ 2 * LLLL / (4160000 * LLL ^ 2) := by
      field_simp
      ring
    have h1 : 1 ≤ L * LL ^ 2 * LLLL / (4160000 * LLL ^ 2) := by
      rw [le_div_iff₀ (by positivity), one_mul]
      have hsq : LLL ^ 2 ≤ LL ^ 2 := pow_le_pow_left₀ (by linarith) hLLL_le 2
      have hmul1 : 4160000 * LLL ^ 2 ≤ L * LLL ^ 2 :=
        mul_le_mul_of_nonneg_right hLbig (by positivity)
      have hmul2 : L * LLL ^ 2 ≤ L * LL ^ 2 := mul_le_mul_of_nonneg_left hsq hLpos.le
      have hmul3 : L * LL ^ 2 ≤ L * LL ^ 2 * LLLL := by nlinarith [pow_nonneg (by linarith : 0 ≤ LL) 2]
      linarith
    linarith
  -- Upper bound on `Q + y` showing `Q + y < X / 2`
  have hRle : R ≤ L ^ 4 := by
    have hlyL : ly ≤ L := hly_le.trans hLL_le
    have hlllyL : llly ≤ L := hllly_le.trans (hlly_le.trans (hLLL_le.trans hLL_le))
    have hnum : (y : ℝ) * ly ^ 2 * llly ≤ L * L ^ 2 * L := by
      have h1 : (y : ℝ) * ly ^ 2 ≤ L * L ^ 2 :=
        mul_le_mul (by linarith) (pow_le_pow_left₀ (by linarith) hlyL 2) (by positivity) hLpos.le
      exact mul_le_mul h1 hlllyL (by linarith) (by positivity)
    have hden : (1 : ℝ) ≤ 2000 * lly ^ 2 := by nlinarith
    have hdiv : R ≤ (y : ℝ) * ly ^ 2 * llly := div_le_self (by positivity) hden
    have e4 : L * L ^ 2 * L = L ^ 4 := by ring
    linarith
  have hQy_lt : Q + y < X / 2 := by
    have hQleR : (Q : ℝ) ≤ R := Nat.floor_le (by positivity)
    have hL5 : L ^ 5 / 8192 ≤ (X : ℝ) := by
      have h1 := one_add_pow_four_le_exp (show 0 ≤ L / 2 by positivity)
      have h2 : L / 2 ≤ Real.exp (L / 2) := by linarith [Real.add_one_le_exp (L / 2)]
      have hprod := mul_le_mul h1 h2 (by positivity) (Real.exp_pos _).le
      have hexpX : Real.exp (L / 2) * Real.exp (L / 2) = (X : ℝ) := by
        rw [← Real.exp_add, show L / 2 + L / 2 = L by ring, hLdef, Real.exp_log hXpos]
      have hlo : L ^ 5 / 8192 ≤ (1 + (L / 2) ^ 4 / 256) * (L / 2) := by
        have : (1 + (L / 2) ^ 4 / 256) * (L / 2) = L / 2 + L ^ 5 / 8192 := by ring
        linarith
      linarith
    have h4L4 : 4 * (2 * L ^ 4) ≤ (X : ℝ) := by
      have hL4nn : 0 ≤ L ^ 4 := by positivity
      have hcmp : 8 * L ^ 4 ≤ L ^ 5 / 8192 := by
        have e5 : L ^ 5 / 8192 = (L / 8192) * L ^ 4 := by ring
        rw [e5]
        exact mul_le_mul_of_nonneg_right (by linarith) hL4nn
      linarith
    have hQyr : ((Q + y : ℕ) : ℝ) < (X : ℝ) / 4 := by
      push_cast
      have hL1 : L ≤ L ^ 4 := le_self_pow₀ (by linarith) (by norm_num)
      have hposL4 : 0 < L ^ 4 := by positivity
      linarith
    have h4Qy : 4 * (Q + y) < X := by
      have : (4 : ℝ) * ((Q + y : ℕ) : ℝ) < (X : ℝ) := by linarith
      exact_mod_cast this
    omega
  -- Upper bound on `primorial y` showing `X / 2 + primorial y ≤ X`
  have hwin : X / 2 + primorial y ≤ X := by
    have hprX : 3 * (primorial y : ℝ) ≤ (X : ℝ) := by
      have h1 : (primorial y : ℝ) ≤ Real.exp (5 / 8 * L) :=
        hpr.trans (Real.exp_le_exp.mpr (by linarith))
      have h2 : (3 : ℝ) ≤ Real.exp (3 / 8 * L) := by
        linarith [Real.add_one_le_exp (3 / 8 * L)]
      have hprod := mul_le_mul h2 h1 (by positivity) (Real.exp_pos _).le
      have hexpX : Real.exp (3 / 8 * L) * Real.exp (5 / 8 * L) = (X : ℝ) := by
        rw [← Real.exp_add, show 3 / 8 * L + 5 / 8 * L = L by ring, hLdef, Real.exp_log hXpos]
      linarith
    have h3p : 3 * primorial y ≤ X := by exact_mod_cast hprX
    omega
  obtain ⟨N, hNlo, hNhi, hNeven, hNq⟩ :=
    exists_even_in_Icc_of_cover (R := oddPrimesLE y) (a := a) (Q := Q) (y := y) (L₀ := X / 2) (U₀ := X)
      (fun r hr => (mem_oddPrimesLE.mp hr).2) (fun r hr => (mem_oddPrimesLE.mp hr).1) hy2
      hcover hQy_lt hwin
  refine ⟨N, hNlo, hNhi, hNeven, fun q hq => hNq q ?_⟩
  have hq1 : (q : ℝ) + 1 ≤ R := by linarith
  have hq2 : q + 1 ≤ Q := Nat.le_floor (by exact_mod_cast hq1)
  omega

/-- **Existential form of the unconditional Rankin iterated-log lower bound.** -/
theorem exists_pos_eventually_exists_even_le_rankin :
    ∃ c : ℝ, 0 < c ∧ ∀ᶠ X : ℕ in atTop, ∃ N : ℕ, X / 2 ≤ N ∧ N ≤ X ∧ Even N ∧
      ∀ q : ℕ, (q : ℝ) < c * Real.log (X : ℝ) * Real.log (Real.log (X : ℝ)) ^ 2 *
          Real.log (Real.log (Real.log (Real.log (X : ℝ)))) /
          Real.log (Real.log (Real.log (X : ℝ))) ^ 2 → ¬ IsSummand N q := by
  refine ⟨1 / 65000, by norm_num, ?_⟩
  filter_upwards [eventually_exists_even_le_rankin] with X ⟨N, hlo, hhi, hev, hq⟩
  refine ⟨N, hlo, hhi, hev, fun q hlt => hq q ?_⟩
  convert hlt using 1
  ring

end GoldbachGaps
