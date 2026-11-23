import GoldbachGaps.Cap.Layers

/-!
# A lower bound for the largest least Goldbach summand, by covering

For an even `N` let `g(N)` be the least prime `q` with `N - q` prime. This file proves that
`max {g(N) : N ≤ X}` is at least `(c - ε) ln X ln ln X` in the following form, which does not
assume that `N` has a Goldbach partition:

  for all large `X` there is an even `N ≤ X` such that `N - q` is composite for every prime
  `q < c · ln X · ln ln X`.

* `eventually_exists_even_le_no_summand`: unconditionally, with `c = 0.73`.
* `eventually_exists_even_le_of_mertensThird`: with Mertens' third theorem
  (`ln w · ∏_{p ≤ w} (1 - 1/p) → e^{-γ}`, not in Mathlib, a named hypothesis `MertensThird`;
  formalised in the PNT+ project, see the docstring of `MertensThird`),
  for every `c < e^γ / (2 C₂) = 1.349…`, `C₂` the twin-prime constant; and
  `eventually_exists_even_le_of_mertensThird_explicit` with `c = 1.2` (from `γ > 1/2` and three
  factors of `C₂`).
* `eventually_exists_even_le_of_mertensUpper`: the general statement. If
  `∏_{3 ≤ r ≤ w} (r - 2)/(r - 1) ≤ (κ + ε) / ln w` for every `ε > 0` and all large `w`
  (`MertensUpper κ`), the conclusion holds for every `c < 1/κ`.

The order `ln X ln ln X` is already in `Counting.lean`, by counting pairs of primes; that
argument cannot give a constant above `1/2`. Here the number `N` is constructed (the proposal
of the research session, 22 and 23 November 2026). Take `y ≈ ln X`. Choose nonzero classes
modulo the odd primes `r ≤ δ y`: on average over the choices a row (an odd prime `q` below
the bound `Q`) stays uncovered with probability `∏ (r - 2)/(r - 1)`, so some choice leaves at
most that share of the rows (`Cap/FirstMoment.lean`). Give each remaining row its own prime
in `(δ y, y]`. The even `N` below `2 ∏_{r ≤ y} r` in all these classes has every `N - q`
divisible by a prime `r ≤ y < N - q`. The combinatorial skeleton is
`Cap.exists_even_le_of_layers`; what is added here is the estimation of its three counts:

* the rows and the mop-up primes, by the prime number theorem (Mathlib:
  `Nat.isEquivalent_primeCounting`);
* the size of the window, by `ln primorial n ~ n` (`Nat.tendsto_log_primorial_div_atTop`);
* the product. Elementary bound (`oddPrimeProd_le`): Euler's product against the harmonic
  sum gives `∏_{p ≤ w} (1 - 1/p) ≤ 1 / ln (w + 1)` (`log_le_prod_primesLE`), and the factor
  `∏ (1 - 1/(r - 1)²)` is at most its first three terms; together `κ = 1575/1152 = 1.367`.
  Mertens' third theorem replaces the `2` in `2/ln w` by `2 e^{-γ} = 1.123` and the three
  terms by the whole twin-prime constant, `κ = 2 C₂ e^{-γ} = 0.7413`.

Each mop-up prime covers one row. Covering two rows with one prime (pairs of rows congruent
modulo it) would double the constant, and several rows per prime would give a larger order;
neither is proved here.
-/

open Finset Filter

namespace GoldbachGaps

/-- The odd primes up to `w`. -/
def oddPrimesLE (w : ℕ) : Finset ℕ := (Nat.primesLE w).filter (· ≠ 2)

theorem mem_oddPrimesLE {w r : ℕ} : r ∈ oddPrimesLE w ↔ r ≤ w ∧ r.Prime ∧ r ≠ 2 := by
  rw [oddPrimesLE, Finset.mem_filter, Nat.mem_primesLE, and_assoc]

theorem three_le_of_mem_oddPrimesLE {w r : ℕ} (h : r ∈ oddPrimesLE w) : 3 ≤ r := by
  obtain ⟨-, hp, h2⟩ := mem_oddPrimesLE.mp h
  have := hp.two_le
  omega

/-- The proportion of rows that a random choice of nonzero classes modulo the odd primes up to
`w` leaves uncovered: `∏_{3 ≤ r ≤ w} (r - 2)/(r - 1)`. -/
noncomputable def oddPrimeProd (w : ℕ) : ℝ := ∏ r ∈ oddPrimesLE w, ((r : ℝ) - 2) / ((r : ℝ) - 1)

/-- A bound of Mertens type: `∏_{3 ≤ r ≤ w} (r - 2)/(r - 1) ≤ (κ + ε) / ln w` for every `ε > 0`
and all large `w`. Mertens' third theorem gives it with `κ = 2 C₂ e^{-γ}`. -/
def MertensUpper (κ : ℝ) : Prop :=
  ∀ ε > 0, ∀ᶠ w : ℕ in atTop, oddPrimeProd w ≤ (κ + ε) / Real.log w

/-- Euler's product, finite form: `ln (w + 1) ≤ ∏_{p ≤ w} (1 - 1/p)⁻¹`. Every `m ≤ w` is a
product of primes up to `w`, so the product of the geometric series exceeds the harmonic sum. -/
theorem log_le_prod_primesLE (w : ℕ) :
    Real.log (w + 1) ≤ ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹)⁻¹ := by
  let f : ℕ →* ℝ :=
    { toFun := fun n => (n : ℝ)⁻¹
      map_one' := by simp
      map_mul' := fun a b => by
        push_cast
        rw [mul_inv] }
  have hf : ∀ {p : ℕ}, p.Prime → ‖f p‖ < 1 := by
    intro p hp
    have h2 : (2 : ℝ) ≤ p := by exact_mod_cast hp.two_le
    show ‖(p : ℝ)⁻¹‖ < 1
    rw [Real.norm_of_nonneg (by positivity)]
    exact inv_lt_one_of_one_lt₀ (by linarith)
  have hsum := (EulerProduct.summable_and_hasSum_smoothNumbers_prod_primesBelow_geometric hf
    (w + 1)).2
  have hle := sum_le_hasSum ((Finset.Icc 1 w).subtype (· ∈ (w + 1).smoothNumbers))
    (fun m _ => by
      show (0 : ℝ) ≤ ((m : ℕ) : ℝ)⁻¹
      positivity) hsum
  have hfilter : (Finset.Icc 1 w).filter (· ∈ (w + 1).smoothNumbers) = Finset.Icc 1 w := by
    refine Finset.filter_true_of_mem fun m hm => ?_
    rw [Finset.mem_Icc] at hm
    exact Nat.mem_smoothNumbers_of_lt (by omega) (by omega)
  have hsub : ∑ m ∈ (Finset.Icc 1 w).subtype (· ∈ (w + 1).smoothNumbers), f (m : ℕ) =
      ∑ m ∈ Finset.Icc 1 w, (m : ℝ)⁻¹ := by
    rw [Finset.sum_subtype_eq_sum_filter (f := fun m : ℕ => f m), hfilter]
    rfl
  have hharm : ((harmonic w : ℚ) : ℝ) = ∑ m ∈ Finset.Icc 1 w, (m : ℝ)⁻¹ := by
    rw [harmonic_eq_sum_Icc]
    push_cast
    rfl
  have hlog := log_add_one_le_harmonic w
  rw [hharm] at hlog
  have hfinal : Real.log ((w + 1 : ℕ) : ℝ) ≤ ∏ p ∈ (w + 1).primesBelow, (1 - f p)⁻¹ := by
    rw [← hsub] at hlog
    exact hlog.trans hle
  rw [Nat.cast_add, Nat.cast_one] at hfinal
  exact hfinal

/-- `(r - 2)/(r - 1) = (1 - 1/r) (1 - 1/(r - 1)²)`. -/
theorem sub_two_div_sub_one {r : ℝ} (hr : 3 ≤ r) :
    (r - 2) / (r - 1) = (1 - r⁻¹) * (1 - 1 / (r - 1) ^ 2) := by
  have h1 : r ≠ 0 := by linarith
  have h2 : r - 1 ≠ 0 := by linarith
  field_simp
  ring

/-- The product over the odd primes of `1 - 1/r` is twice the product over all primes. -/
theorem prod_oddPrimesLE_one_sub_inv {w : ℕ} (hw : 2 ≤ w) :
    ∏ r ∈ oddPrimesLE w, (1 - (r : ℝ)⁻¹) = 2 * ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹) := by
  have h2 : 2 ∈ Nat.primesLE w := Nat.mem_primesLE.mpr ⟨hw, Nat.prime_two⟩
  have hsplit : Nat.primesLE w = insert 2 (oddPrimesLE w) := by
    ext r
    rw [Finset.mem_insert, mem_oddPrimesLE, Nat.mem_primesLE]
    constructor
    · intro h
      by_cases hr : r = 2
      · exact Or.inl hr
      · exact Or.inr ⟨h.1, h.2, hr⟩
    · rintro (rfl | h)
      · exact ⟨hw, Nat.prime_two⟩
      · exact ⟨h.1, h.2.1⟩
  have hnot : 2 ∉ oddPrimesLE w := fun h => (mem_oddPrimesLE.mp h).2.2 rfl
  rw [hsplit, Finset.prod_insert hnot]
  norm_num
  ring

/-- The elementary bound of Mertens type: `∏_{3 ≤ r ≤ w} (r - 2)/(r - 1) ≤ (1575/1152) / ln (w + 1)`
for `w ≥ 7`. The constant is `2 · (3/4)(15/16)(35/36)`: the factor `2` from Euler's product
against the harmonic sum (the true constant there is `2 e^{-γ} = 1.12`), the rest from the
first three factors of the twin-prime constant. -/
theorem oddPrimeProd_le {w : ℕ} (hw : 7 ≤ w) :
    oddPrimeProd w ≤ 1575 / 1152 / Real.log (w + 1) := by
  have hlogpos : 0 < Real.log ((w : ℝ) + 1) := Real.log_pos (by
    have : (7 : ℝ) ≤ w := by exact_mod_cast hw
    linarith)
  -- split each factor
  have hsplit : oddPrimeProd w =
      (∏ r ∈ oddPrimesLE w, (1 - (r : ℝ)⁻¹)) *
        ∏ r ∈ oddPrimesLE w, (1 - 1 / ((r : ℝ) - 1) ^ 2) := by
    rw [oddPrimeProd, ← Finset.prod_mul_distrib]
    refine Finset.prod_congr rfl fun r hr => ?_
    exact sub_two_div_sub_one (by exact_mod_cast three_le_of_mem_oddPrimesLE hr)
  -- the first product
  have hpos : ∀ p ∈ Nat.primesLE w, 0 < 1 - (p : ℝ)⁻¹ := by
    intro p hp
    have h2 : (2 : ℝ) ≤ p := by exact_mod_cast (Nat.mem_primesLE.mp hp).2.two_le
    have : (p : ℝ)⁻¹ ≤ 2⁻¹ := inv_anti₀ (by norm_num) h2
    linarith
  have hprodpos : 0 < ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹) := Finset.prod_pos hpos
  have h1 : ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹) ≤ 1 / Real.log (w + 1) := by
    have h := log_le_prod_primesLE w
    rw [Finset.prod_inv_distrib] at h
    rw [le_div_iff₀ hlogpos]
    have h' := mul_le_mul_of_nonneg_left h hprodpos.le
    rw [mul_inv_cancel₀ hprodpos.ne'] at h'
    exact h'
  -- the second product
  have hsub : ({3, 5, 7} : Finset ℕ) ⊆ oddPrimesLE w := by
    intro r hr
    simp only [Finset.mem_insert, Finset.mem_singleton] at hr
    rw [mem_oddPrimesLE]
    rcases hr with rfl | rfl | rfl
    · exact ⟨by omega, by norm_num, by norm_num⟩
    · exact ⟨by omega, by norm_num, by norm_num⟩
    · exact ⟨by omega, by norm_num, by norm_num⟩
  have hfac : ∀ r ∈ oddPrimesLE w, 0 ≤ 1 - 1 / ((r : ℝ) - 1) ^ 2 ∧
      1 - 1 / ((r : ℝ) - 1) ^ 2 ≤ 1 := by
    intro r hr
    have h3 : (3 : ℝ) ≤ r := by exact_mod_cast three_le_of_mem_oddPrimesLE hr
    have hsq : (1 : ℝ) ≤ ((r : ℝ) - 1) ^ 2 := by nlinarith
    have hle : 1 / ((r : ℝ) - 1) ^ 2 ≤ 1 := by
      rw [div_le_one (by positivity)]
      exact hsq
    have hnn : 0 ≤ 1 / ((r : ℝ) - 1) ^ 2 := by positivity
    exact ⟨by linarith, by linarith⟩
  have h2 : ∏ r ∈ oddPrimesLE w, (1 - 1 / ((r : ℝ) - 1) ^ 2) ≤ 1575 / 2304 := by
    have h := Finset.prod_le_prod_of_subset_of_le_one₀ hsub (fun r hr => (hfac r hr).1)
      (fun r hr _ => (hfac r hr).2)
    refine h.trans (le_of_eq ?_)
    rw [Finset.prod_insert (by decide), Finset.prod_insert (by decide), Finset.prod_singleton]
    norm_num
  have h2nn : 0 ≤ ∏ r ∈ oddPrimesLE w, (1 - 1 / ((r : ℝ) - 1) ^ 2) :=
    Finset.prod_nonneg fun r hr => (hfac r hr).1
  rw [hsplit, prod_oddPrimesLE_one_sub_inv (by omega)]
  have h3 : 2 * ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹) ≤ 2 * (1 / Real.log (w + 1)) := by linarith
  calc (2 * ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹)) *
        ∏ r ∈ oddPrimesLE w, (1 - 1 / ((r : ℝ) - 1) ^ 2)
      ≤ 2 * (1 / Real.log (w + 1)) * (1575 / 2304) :=
        mul_le_mul h3 h2 h2nn (by positivity)
    _ = 1575 / 1152 / Real.log (w + 1) := by ring

/-- The elementary instance of `MertensUpper`, with `κ = 1575/1152 = 1.367`. -/
theorem mertensUpper_elementary : MertensUpper (1575 / 1152) := by
  intro ε hε
  filter_upwards [eventually_ge_atTop 7] with w hw
  have hw7 : (7 : ℝ) ≤ w := by exact_mod_cast hw
  have hlog : 0 < Real.log (w : ℝ) := Real.log_pos (by linarith)
  have hle : Real.log (w : ℝ) ≤ Real.log ((w : ℝ) + 1) :=
    Real.log_le_log (by linarith) (by linarith)
  calc oddPrimeProd w ≤ 1575 / 1152 / Real.log (w + 1) := oddPrimeProd_le hw
    _ ≤ 1575 / 1152 / Real.log w := div_le_div_of_nonneg_left (by norm_num) hlog hle
    _ ≤ (1575 / 1152 + ε) / Real.log w := by
        apply div_le_div_of_nonneg_right _ hlog.le
        linarith

/-- The prime number theorem as two inequalities: for every `δ > 0` and all large `x`,
`(1 - δ) x / ln x ≤ π(x) ≤ (1 + δ) x / ln x`. -/
theorem eventually_primeCounting_bounds {δ : ℝ} (hδ : 0 < δ) :
    ∀ᶠ x : ℝ in atTop, (1 - δ) * (x / Real.log x) ≤ (Nat.primeCounting ⌊x⌋₊ : ℝ) ∧
      (Nat.primeCounting ⌊x⌋₊ : ℝ) ≤ (1 + δ) * (x / Real.log x) := by
  have hne : ∀ᶠ x : ℝ in atTop, x / Real.log x ≠ 0 := by
    filter_upwards [eventually_gt_atTop 1] with x hx
    exact div_ne_zero (by linarith) (Real.log_pos hx).ne'
  have h := (Asymptotics.isEquivalent_iff_tendsto_one hne).mp Nat.isEquivalent_primeCounting
  have h1 := h.eventually (eventually_gt_nhds (show (1 - δ : ℝ) < 1 by linarith))
  have h2 := h.eventually (eventually_lt_nhds (show (1 : ℝ) < 1 + δ by linarith))
  filter_upwards [h1, h2, eventually_gt_atTop 1] with x hx1 hx2 hx
  have hpos : 0 < x / Real.log x := div_pos (by linarith) (Real.log_pos hx)
  simp only [Pi.div_apply] at hx1 hx2
  constructor
  · have := (lt_div_iff₀ hpos).mp hx1
    linarith
  · have := (div_lt_iff₀ hpos).mp hx2
    linarith

/-- `oddPrimeProd` as a quotient of two natural numbers. -/
theorem oddPrimeProd_eq (w : ℕ) :
    oddPrimeProd w = ((∏ r ∈ oddPrimesLE w, (r - 2) : ℕ) : ℝ) / ((∏ r ∈ oddPrimesLE w, (r - 1) : ℕ) : ℝ) := by
  rw [oddPrimeProd, Nat.cast_prod, Nat.cast_prod, ← Finset.prod_div_distrib]
  refine Finset.prod_congr rfl fun r hr => ?_
  have h3 := three_le_of_mem_oddPrimesLE hr
  rw [Nat.cast_sub (by omega), Nat.cast_sub (by omega)]
  norm_num

/-- The choice of the slack: for `c κ < 1` there is `δ ∈ (0, 1/2]` with
`(1 + δ)(κ + δ) c + 2 (1 + δ) δ ≤ (1 - δ)²`. -/
theorem exists_slack {κ c : ℝ} (hκ : 0 < κ) (hc0 : 0 < c) (hc : c * κ < 1) :
    ∃ δ : ℝ, 0 < δ ∧ δ ≤ 1 / 2 ∧ (1 + δ) * (κ + δ) * c + 2 * (1 + δ) * δ ≤ (1 - δ) ^ 2 := by
  have hden : 0 < c * (κ + 2) + 5 := by positivity
  have hη : 0 < 1 - c * κ := by linarith
  refine ⟨min (1 / 2) ((1 - c * κ) / (c * (κ + 2) + 5)), lt_min (by norm_num) (div_pos hη hden),
    min_le_left _ _, ?_⟩
  set δ := min (1 / 2) ((1 - c * κ) / (c * (κ + 2) + 5)) with hδdef
  have hδ0 : 0 < δ := lt_min (by norm_num) (div_pos hη hden)
  have hδ1 : δ ≤ 1 / 2 := min_le_left _ _
  have hδ2 : δ * (c * (κ + 2) + 5) ≤ 1 - c * κ := by
    have h := min_le_right (1 / 2) ((1 - c * κ) / (c * (κ + 2) + 5))
    rw [← hδdef, le_div_iff₀ hden] at h
    exact h
  have hsq : δ ^ 2 ≤ δ / 2 := by nlinarith
  have hcδ : 0 ≤ c * δ := by positivity
  nlinarith [mul_nonneg hc0.le hδ0.le, mul_nonneg (mul_nonneg hc0.le hκ.le) hδ0.le,
    mul_nonneg hc0.le (sub_nonneg.mpr hsq)]

/-- **The cover, with its three counts.** If `∏_{3 ≤ r ≤ w} (r - 2)/(r - 1) ≤ (κ + ε)/ln w` for
large `w` and `c κ < 1`, then for every large `y` there is an even `N` with
`Q < N ≤ Q + y + primorial y` and no Goldbach summand below `Q = ⌊c y ln y⌋`. The pigeonhole layer is the odd primes up to
`δ y`, the mop-up layer the primes in `(δ y, y]`. -/
theorem eventually_exists_even_of_mertensUpper_nat {κ c : ℝ} (hκ : 0 < κ)
    (hM : MertensUpper κ) (hc0 : 0 < c) (hc : c * κ < 1) :
    ∀ᶠ y : ℕ in atTop, ∃ N, Even N ∧ ⌊c * y * Real.log y⌋₊ < N ∧
      N ≤ ⌊c * y * Real.log y⌋₊ + y + primorial y ∧
      ∀ q < ⌊c * y * Real.log y⌋₊, ¬ IsSummand N q := by
  classical
  obtain ⟨δ, hδ0, hδ1, hkey⟩ := exists_slack hκ hc0 hc
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hlog : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hx1 : Tendsto (fun y : ℕ => c * (y : ℝ) * Real.log y) atTop atTop :=
    (hcast.const_mul_atTop hc0).atTop_mul_atTop₀ hlog
  have hx2 : Tendsto (fun y : ℕ => δ * (y : ℝ)) atTop atTop := hcast.const_mul_atTop hδ0
  have hw : Tendsto (fun y : ℕ => ⌊δ * (y : ℝ)⌋₊) atTop atTop :=
    tendsto_nat_floor_atTop.comp hx2
  have hpnt := eventually_primeCounting_bounds hδ0
  filter_upwards [hx1.eventually hpnt, hx2.eventually hpnt, hcast.eventually hpnt,
    hw.eventually (hM δ hδ0), hw.eventually (eventually_ge_atTop 2),
    hlog.eventually_ge_atTop (1 / c), hlog.eventually_ge_atTop (Real.log (2 / δ) / δ),
    hlog.eventually_ge_atTop 1, hcast.eventually_ge_atTop (2 / δ), eventually_ge_atTop 2]
    with y h1 h2 h3 h4 hw2 hL1 hL2 hL3 hy1 hy2
  set L := Real.log (y : ℝ) with hLdef
  set Q := ⌊c * (y : ℝ) * L⌋₊ with hQdef
  set w := ⌊δ * (y : ℝ)⌋₊ with hwdef
  have hLpos : 0 < L := by linarith
  have hypos : (0 : ℝ) < y := by
    have : (2 : ℝ) ≤ y := by exact_mod_cast hy2
    linarith
  have hcL : 1 ≤ c * L := by
    have := mul_le_mul_of_nonneg_left hL1 hc0.le
    rwa [mul_one_div_cancel hc0.ne'] at this
  have hδL : Real.log (2 / δ) ≤ δ * L := by
    have := mul_le_mul_of_nonneg_left hL2 hδ0.le
    rwa [mul_div_cancel₀ _ hδ0.ne'] at this
  have hδy : 2 ≤ δ * (y : ℝ) := by
    have := mul_le_mul_of_nonneg_left hy1 hδ0.le
    rwa [mul_div_cancel₀ _ hδ0.ne'] at this
  have h1δ : 0 < 1 - δ := by linarith
  have hlog2δ : Real.log (2 / δ) = Real.log 2 - Real.log δ :=
    Real.log_div (by norm_num) hδ0.ne'
  have hlog2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  -- (a) rows
  have hA : (Nat.primeCounting Q : ℝ) ≤ (1 + δ) * c * y := by
    have hge : (y : ℝ) ≤ c * y * L := by nlinarith
    have hlogge : L ≤ Real.log (c * y * L) := Real.log_le_log hypos hge
    have hnum : 0 ≤ c * (y : ℝ) * L := by positivity
    calc (Nat.primeCounting Q : ℝ) ≤ (1 + δ) * (c * y * L / Real.log (c * y * L)) := h1.2
      _ ≤ (1 + δ) * (c * y * L / L) :=
          mul_le_mul_of_nonneg_left (div_le_div_of_nonneg_left hnum hLpos hlogge) (by linarith)
      _ = (1 + δ) * c * y := by
          field_simp
  -- (b) the primes of the pigeonhole layer
  have hW : (Nat.primeCounting w : ℝ) ≤ (1 + δ) * δ * y / ((1 - δ) * L) := by
    have hlogδy : Real.log (δ * y) = Real.log δ + L := Real.log_mul hδ0.ne' hypos.ne'
    have hge : (1 - δ) * L ≤ Real.log (δ * y) := by
      rw [hlogδy]
      linarith
    have hnum : 0 ≤ δ * (y : ℝ) := by positivity
    calc (Nat.primeCounting w : ℝ) ≤ (1 + δ) * (δ * y / Real.log (δ * y)) := h2.2
      _ ≤ (1 + δ) * (δ * y / ((1 - δ) * L)) :=
          mul_le_mul_of_nonneg_left
            (div_le_div_of_nonneg_left hnum (mul_pos h1δ hLpos) hge) (by linarith)
      _ = (1 + δ) * δ * y / ((1 - δ) * L) := by ring
  -- (c) the primes up to `y`
  have hY : (1 - δ) * ((y : ℝ) / L) ≤ (Nat.primeCounting y : ℝ) := by
    have := h3.1
    rwa [Nat.floor_natCast] at this
  -- (d) the product
  have hwreal : δ * (y : ℝ) / 2 ≤ (w : ℝ) := by
    have := Nat.sub_one_lt_floor (δ * (y : ℝ))
    linarith
  have hlogw : (1 - δ) * L ≤ Real.log (w : ℝ) := by
    have hpos : 0 < δ * (y : ℝ) / 2 := by positivity
    have h := Real.log_le_log hpos hwreal
    have e : Real.log (δ * (y : ℝ) / 2) = Real.log δ + L - Real.log 2 := by
      rw [Real.log_div (by positivity) (by norm_num), Real.log_mul hδ0.ne' hypos.ne']
    rw [e] at h
    linarith
  have hPi : oddPrimeProd w ≤ (κ + δ) / ((1 - δ) * L) :=
    h4.trans (div_le_div_of_nonneg_left (by linarith) (mul_pos h1δ hLpos) hlogw)
  have hPi0 : 0 ≤ oddPrimeProd w := Finset.prod_nonneg fun r hr => by
    have h3 : (3 : ℝ) ≤ r := by exact_mod_cast three_le_of_mem_oddPrimesLE hr
    exact div_nonneg (by linarith) (by linarith)
  -- (e) sizes
  have hwy : w ≤ y := by
    have h : δ * (y : ℝ) ≤ y := by nlinarith
    calc w ≤ ⌊(y : ℝ)⌋₊ := Nat.floor_le_floor h
      _ = y := Nat.floor_natCast y
  -- the layers
  set S := oddPrimesLE w with hSdef
  set T := (Nat.primesLE y).filter (w < ·) with hTdef
  have hS : ∀ r ∈ S, r.Prime ∧ r ≠ 2 := fun r hr => (mem_oddPrimesLE.mp hr).2
  have hT : ∀ r ∈ T, r.Prime ∧ r ≠ 2 := fun r hr => by
    obtain ⟨hr1, hr2⟩ := Finset.mem_filter.mp hr
    exact ⟨(Nat.mem_primesLE.mp hr1).2, by omega⟩
  have hB : ∀ r ∈ (∅ : Finset ℕ) ∪ S ∪ T, r ≤ y := fun r hr => by
    rcases Finset.mem_union.mp hr with h | h
    · rcases Finset.mem_union.mp h with h | h
      · exact absurd h (Finset.notMem_empty r)
      · exact (mem_oddPrimesLE.mp h).1.trans hwy
    · exact (Nat.mem_primesLE.mp (Finset.mem_filter.mp h).1).1
  have hST : Disjoint S T := Finset.disjoint_left.mpr fun r hr hr' => by
    have h1 := (mem_oddPrimesLE.mp hr).1
    have h2 := (Finset.mem_filter.mp hr').2
    omega
  -- the three counts, as natural numbers
  have hA' : #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
      ∀ r ∈ (∅ : Finset ℕ), ¬ q ≡ (fun _ : ℕ => 0) r [MOD r]} ≤ Nat.primeCounting Q := by
    rw [← Nat.primesLE_card_eq_primeCounting]
    refine Finset.card_le_card fun q hq => ?_
    obtain ⟨hq1, hq2, -⟩ := Finset.mem_filter.mp hq
    exact Nat.mem_primesLE.mpr ⟨(Finset.mem_range.mp hq1).le, hq2.1⟩
  have hZ' : #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} ≤ Nat.primeCounting w := by
    rw [← Nat.primesLE_card_eq_primeCounting]
    refine Finset.card_le_card fun q hq => ?_
    have hqS := (Finset.mem_filter.mp hq).2.2
    exact (Finset.mem_filter.mp hqS).1
  have hT' : Nat.primeCounting y ≤ Nat.primeCounting w + #T := by
    rw [← Nat.primesLE_card_eq_primeCounting, ← Nat.primesLE_card_eq_primeCounting]
    refine (Finset.card_le_card fun p hp => ?_).trans (Finset.card_union_le _ _)
    by_cases h : p ≤ w
    · exact Finset.mem_union.mpr (Or.inl (Nat.mem_primesLE.mpr ⟨h, (Nat.mem_primesLE.mp hp).2⟩))
    · exact Finset.mem_union.mpr (Or.inr (Finset.mem_filter.mpr ⟨hp, by omega⟩))
  have hP1pos : (0 : ℝ) < ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) := by
    have : 0 < ∏ r ∈ S, (r - 1) := Finset.prod_pos fun r hr => by
      have := three_le_of_mem_oddPrimesLE hr
      omega
    exact_mod_cast this
  have hcount : #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
        ∀ r ∈ (∅ : Finset ℕ), ¬ q ≡ (fun _ : ℕ => 0) r [MOD r]} * ∏ r ∈ S, (r - 2) +
      #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} * ∏ r ∈ S, (r - 1) ≤
      #T * ∏ r ∈ S, (r - 1) := by
    set A := #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
        ∀ r ∈ (∅ : Finset ℕ), ¬ q ≡ (fun _ : ℕ => 0) r [MOD r]} with hAdef
    set Zc := #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} with hZdef
    have hAr : (A : ℝ) ≤ (1 + δ) * c * y := le_trans (by exact_mod_cast hA') hA
    have hZr : (Zc : ℝ) ≤ (1 + δ) * δ * y / ((1 - δ) * L) :=
      le_trans (by exact_mod_cast hZ') hW
    have hTr : (1 - δ) * ((y : ℝ) / L) - (1 + δ) * δ * y / ((1 - δ) * L) ≤ (#T : ℝ) := by
      have h : (Nat.primeCounting y : ℝ) ≤ Nat.primeCounting w + #T := by exact_mod_cast hT'
      linarith
    have ha1 : 0 ≤ (1 + δ) * c * (y : ℝ) := by positivity
    have hmul : (A : ℝ) * oddPrimeProd w ≤ (1 + δ) * c * y * ((κ + δ) / ((1 - δ) * L)) :=
      mul_le_mul hAr hPi hPi0 ha1
    have hfrac : 0 ≤ (y : ℝ) / ((1 - δ) * L) := by positivity
    have hsum : (1 + δ) * c * y * ((κ + δ) / ((1 - δ) * L)) +
        2 * ((1 + δ) * δ * y / ((1 - δ) * L)) ≤ (1 - δ) * ((y : ℝ) / L) := by
      have e1 : (1 + δ) * c * y * ((κ + δ) / ((1 - δ) * L)) +
          2 * ((1 + δ) * δ * y / ((1 - δ) * L)) =
          (y : ℝ) / ((1 - δ) * L) * ((1 + δ) * (κ + δ) * c + 2 * (1 + δ) * δ) := by
        field_simp
      have e2 : (1 - δ) * ((y : ℝ) / L) = (y : ℝ) / ((1 - δ) * L) * (1 - δ) ^ 2 := by
        field_simp
      rw [e1, e2]
      exact mul_le_mul_of_nonneg_left hkey hfrac
    have hreal : (A : ℝ) * oddPrimeProd w + Zc ≤ (#T : ℝ) := by linarith
    have hfin : (A : ℝ) * ((∏ r ∈ S, (r - 2) : ℕ) : ℝ) + Zc * ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) ≤
        (#T : ℝ) * ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) := by
      have h := mul_le_mul_of_nonneg_right hreal hP1pos.le
      rw [oddPrimeProd_eq w] at h
      have e : ((A : ℝ) * (((∏ r ∈ S, (r - 2) : ℕ) : ℝ) / ((∏ r ∈ S, (r - 1) : ℕ) : ℝ)) + Zc) *
          ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) =
          (A : ℝ) * ((∏ r ∈ S, (r - 2) : ℕ) : ℝ) + Zc * ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) := by
        field_simp
      rw [← e]
      exact h
    exact_mod_cast hfin
  obtain ⟨N, hNe, hNlo, hNhi, hNq⟩ := Cap.exists_even_le_of_layers ∅ S T (fun _ => 0) Q y
    (fun r hr => absurd hr (Finset.notMem_empty r)) hS hT hB hy2
    (Finset.disjoint_empty_left _) (Finset.disjoint_empty_left _) hST hcount
  refine ⟨N, hNe, by omega, hNhi.trans ?_, hNq⟩
  -- the modulus is at most the primorial
  have h2not : 2 ∉ (∅ : Finset ℕ) ∪ S ∪ T := fun h => by
    rcases Finset.mem_union.mp h with h | h
    · rcases Finset.mem_union.mp h with h | h
      · exact absurd h (Finset.notMem_empty 2)
      · exact (hS 2 h).2 rfl
    · exact (hT 2 h).2 rfl
  have hsub : insert 2 ((∅ : Finset ℕ) ∪ S ∪ T) ⊆ (range (y + 1)).filter Nat.Prime := by
    intro r hr
    rw [Finset.mem_filter, Finset.mem_range]
    rcases Finset.mem_insert.mp hr with rfl | h
    · exact ⟨by omega, Nat.prime_two⟩
    · refine ⟨Nat.lt_succ_of_le (hB r h), ?_⟩
      rcases Finset.mem_union.mp h with h | h
      · rcases Finset.mem_union.mp h with h | h
        · exact absurd h (Finset.notMem_empty r)
        · exact (hS r h).1
      · exact (hT r h).1
  have hprim : 2 * ∏ r ∈ (∅ : Finset ℕ) ∪ S ∪ T, r ≤ primorial y := by
    calc 2 * ∏ r ∈ (∅ : Finset ℕ) ∪ S ∪ T, r = ∏ r ∈ insert 2 ((∅ : Finset ℕ) ∪ S ∪ T), r :=
          (Finset.prod_insert (f := fun r : ℕ => r) h2not).symm
      _ ≤ ∏ r ∈ (range (y + 1)).filter Nat.Prime, r :=
          Finset.prod_le_prod_of_subset_of_one_le hsub fun r hr _ =>
            (Finset.mem_filter.mp hr).2.one_le
      _ = primorial y := rfl
  omega

/-- `primorial n ≤ e^{(1 + δ) n}` for large `n` (the prime number theorem in the form
`ln primorial n ~ n`). -/
theorem eventually_primorial_le {δ : ℝ} (hδ : 0 < δ) :
    ∀ᶠ n : ℕ in atTop, (primorial n : ℝ) ≤ Real.exp ((1 + δ) * n) := by
  have h := Nat.tendsto_log_primorial_div_atTop.eventually
    (eventually_lt_nhds (show (1 : ℝ) < 1 + δ by linarith))
  filter_upwards [h, eventually_gt_atTop 0] with n hn hn0
  have hnpos : (0 : ℝ) < n := by exact_mod_cast hn0
  have hprim : (0 : ℝ) < primorial n := by exact_mod_cast primorial_pos n
  have hlt : Real.log (primorial n) < (1 + δ) * n := (div_lt_iff₀ hnpos).mp hn
  calc (primorial n : ℝ) = Real.exp (Real.log (primorial n)) := (Real.exp_log hprim).symm
    _ ≤ Real.exp ((1 + δ) * n) := Real.exp_le_exp.mpr hlt.le

/-- `1 + u³/27 ≤ e^u` for `u ≥ 0`. -/
theorem one_add_cube_le_exp {u : ℝ} (hu : 0 ≤ u) : 1 + u ^ 3 / 27 ≤ Real.exp u := by
  have h := Real.add_one_le_exp (u / 3)
  have h0 : 0 ≤ u / 3 + 1 := by positivity
  have h3 : (u / 3 + 1) ^ 3 ≤ Real.exp (u / 3) ^ 3 := pow_le_pow_left₀ h0 h 3
  have e : Real.exp (u / 3) ^ 3 = Real.exp u := by
    rw [← Real.exp_natCast_mul]
    congr 1
    push_cast
    ring
  rw [e] at h3
  nlinarith [mul_nonneg hu hu, hu]

/-- `E + s ≤ E G` when `E ≥ 1`, `G ≥ 1 + t` and `0 ≤ s ≤ t`. -/
theorem add_le_mul_of_one_add_le {E G t s : ℝ} (hE : 1 ≤ E) (hG : 1 + t ≤ G) (hst : s ≤ t)
    (hs : 0 ≤ s) : E + s ≤ E * G := by
  have h1 : 0 ≤ (E - 1) * t := mul_nonneg (sub_nonneg.mpr hE) (hs.trans hst)
  have h2 : E * (1 + t) ≤ E * G := mul_le_mul_of_nonneg_left hG (by linarith)
  nlinarith

/-- **A lower bound for `max g` by covering.** If `∏_{3 ≤ r ≤ w} (r - 2)/(r - 1) ≤ (κ + ε)/ln w`
for every `ε > 0` and all large `w`, then for every `c < 1/κ` and all large `X` there is an
even `N ≤ X`, larger than `c ln X ln ln X`, such that no prime `q < c ln X ln ln X` is a
Goldbach summand of `N`: every `N - q` is composite. -/
theorem eventually_exists_even_le_of_mertensUpper {κ c : ℝ} (hκ : 0 < κ) (hM : MertensUpper κ)
    (hc : c * κ < 1) :
    ∀ᶠ X : ℕ in atTop, ∃ N : ℕ, c * Real.log X * Real.log (Real.log X) < N ∧ N ≤ X ∧ Even N ∧
      ∀ q : ℕ, (q : ℝ) < c * Real.log X * Real.log (Real.log X) → ¬ IsSummand N q := by
  -- constants: `c₀ = max c 0 < c' < 1/κ`, then `c₀/c' < a₁ < a < θ < 1`
  set c₀ := max c 0 with hc₀def
  have hc₀0 : 0 ≤ c₀ := le_max_right _ _
  have hcc₀ : c ≤ c₀ := le_max_left _ _
  have hc₀κ : c₀ * κ < 1 := by
    rcases max_cases c 0 with ⟨h, -⟩ | ⟨h, -⟩
    · rw [hc₀def, h]
      exact hc
    · rw [hc₀def, h]
      simp
  have hc₀lt : c₀ < 1 / κ := by
    rw [lt_div_iff₀ hκ]
    exact hc₀κ
  set c' := (c₀ + 1 / κ) / 2 with hc'def
  have hc'0 : 0 < c' := by
    have : 0 < 1 / κ := by positivity
    rw [hc'def]
    linarith
  have hc₀c' : c₀ < c' := by
    rw [hc'def]
    linarith
  have hc'κ : c' * κ < 1 := by
    have h : c' < 1 / κ := by
      rw [hc'def]
      linarith
    rwa [lt_div_iff₀ hκ] at h
  set ρ := c₀ / c' with hρdef
  have hρ0 : 0 ≤ ρ := div_nonneg hc₀0 hc'0.le
  have hρ1 : ρ < 1 := by
    rw [hρdef, div_lt_one hc'0]
    exact hc₀c'
  set a := (1 + ρ) / 2 with hadef
  set a₁ := (a + ρ) / 2 with ha₁def
  set θ := (1 + a) / 2 with hθdef
  have ha0 : 0 < a := by rw [hadef]; linarith
  have ha1 : a < 1 := by rw [hadef]; linarith
  have hρa₁ : ρ < a₁ := by rw [ha₁def, hadef]; linarith
  have ha₁a : a₁ < a := by rw [ha₁def, hadef]; linarith
  have ha₁0 : 0 < a₁ := lt_of_le_of_lt hρ0 hρa₁
  have hθ1 : θ < 1 := by rw [hθdef]; linarith
  have hθ0 : 0 < θ := by rw [hθdef]; linarith
  have haθ : a < θ := by rw [hθdef]; linarith
  have hm : 0 < c' * a₁ - c₀ := by
    have h : c₀ = c' * ρ := by
      rw [hρdef]
      field_simp
    have : c' * ρ < c' * a₁ := mul_lt_mul_of_pos_left hρa₁ hc'0
    linarith
  set K := (c' * a₁ * (-Real.log a₁) + 1) / (c' * a₁ - c₀) with hKdef
  clear_value K θ a₁ a ρ c' c₀
  -- sequences
  have hcast : Tendsto (fun X : ℕ => (X : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hL : Tendsto (fun X : ℕ => Real.log (X : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hLL : Tendsto (fun X : ℕ => Real.log (Real.log (X : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL
  have hy : Tendsto (fun X : ℕ => ⌊a * Real.log (X : ℝ)⌋₊) atTop atTop :=
    tendsto_nat_floor_atTop.comp (hL.const_mul_atTop ha0)
  have hstage := eventually_exists_even_of_mertensUpper_nat hκ hM hc'0 hc'κ
  have hprim := eventually_primorial_le (show 0 < θ / a - 1 by
    rw [sub_pos, lt_div_iff₀ ha0]
    linarith)
  filter_upwards [hy.eventually hstage, hy.eventually hprim, hL.eventually_ge_atTop 1,
    hL.eventually_ge_atTop (1 / (a - a₁)), hL.eventually_ge_atTop (1 / a₁),
    hL.eventually_ge_atTop (27 * (c' + 1) / (1 - θ) ^ 3), hLL.eventually_ge_atTop K,
    hLL.eventually_ge_atTop 0, eventually_ge_atTop 1]
    with X hst hpr hL1 hL2 hL3 hL4 hLLK hLL0 hX1
  set L := Real.log (X : ℝ) with hLdef
  set y := ⌊a * L⌋₊ with hydef
  have hLpos : 0 < L := by linarith
  have hXpos : (0 : ℝ) < X := by exact_mod_cast hX1
  -- `a₁ L ≤ y ≤ a L`
  have hyle : (y : ℝ) ≤ a * L := Nat.floor_le (by positivity)
  have hyge : a₁ * L ≤ (y : ℝ) := by
    have h1 := Nat.sub_one_lt_floor (a * L)
    have h2 : 1 ≤ (a - a₁) * L := by
      have := mul_le_mul_of_nonneg_left hL2 (sub_pos.mpr ha₁a).le
      rwa [mul_one_div_cancel (sub_pos.mpr ha₁a).ne'] at this
    nlinarith
  have ha₁L : 1 ≤ a₁ * L := by
    have := mul_le_mul_of_nonneg_left hL3 ha₁0.le
    rwa [mul_one_div_cancel ha₁0.ne'] at this
  have hy1 : (1 : ℝ) ≤ y := ha₁L.trans hyge
  have hypos : (0 : ℝ) < y := by linarith
  clear_value y L
  -- (S2) the threshold in `X` is below the threshold in `y`
  have hlogy : Real.log a₁ + Real.log L ≤ Real.log (y : ℝ) := by
    rw [← Real.log_mul ha₁0.ne' hLpos.ne']
    exact Real.log_le_log (by positivity) hyge
  have hlogy0 : 0 ≤ Real.log a₁ + Real.log L := by
    rw [← Real.log_mul ha₁0.ne' hLpos.ne']
    exact Real.log_nonneg ha₁L
  have hS2 : c * L * Real.log L + 1 ≤ c' * y * Real.log y := by
    have h1 : c' * (a₁ * L) * (Real.log a₁ + Real.log L) ≤ c' * y * Real.log y := by
      have hA : c' * (a₁ * L) ≤ c' * y := mul_le_mul_of_nonneg_left hyge hc'0.le
      exact mul_le_mul hA hlogy hlogy0 (by positivity)
    have h2 : c * L * Real.log L ≤ c₀ * L * Real.log L := by
      have : 0 ≤ L * Real.log L := mul_nonneg hLpos.le hLL0
      nlinarith
    have h3 : (c' * a₁ * (-Real.log a₁) + 1) ≤ (c' * a₁ - c₀) * Real.log L := by
      have := mul_le_mul_of_nonneg_left hLLK hm.le
      rwa [hKdef, mul_div_cancel₀ _ hm.ne'] at this
    have h4 : L * (c' * a₁ * (-Real.log a₁) + 1) ≤ L * ((c' * a₁ - c₀) * Real.log L) :=
      mul_le_mul_of_nonneg_left h3 hLpos.le
    nlinarith
  -- (S3) the window fits below `X`
  have hprimle : (primorial y : ℝ) ≤ Real.exp (θ * L) := by
    refine hpr.trans (Real.exp_le_exp.mpr ?_)
    have e : (1 + (θ / a - 1)) * (y : ℝ) = θ / a * y := by ring
    rw [e]
    calc θ / a * (y : ℝ) ≤ θ / a * (a * L) :=
          mul_le_mul_of_nonneg_left hyle (div_nonneg hθ0.le ha0.le)
      _ = θ * L := by
          field_simp
  have hpoly : c' * (y : ℝ) * Real.log y + y ≤ (c' + 1) * L ^ 2 := by
    have hyL : (y : ℝ) ≤ L := hyle.trans (mul_le_of_le_one_left hLpos.le ha1.le)
    have hlogyL : Real.log (y : ℝ) ≤ L := by
      have h := Real.log_le_sub_one_of_pos hypos
      linarith
    have hlogy_nn : 0 ≤ Real.log (y : ℝ) := Real.log_nonneg hy1
    have h1 : c' * (y : ℝ) * Real.log y ≤ c' * L * L :=
      mul_le_mul (mul_le_mul_of_nonneg_left hyL hc'0.le) hlogyL hlogy_nn (by positivity)
    nlinarith
  have hexp : Real.exp (θ * L) + (c' + 1) * L ^ 2 ≤ (X : ℝ) := by
    have hu : 0 ≤ (1 - θ) * L := mul_nonneg (by linarith) hLpos.le
    have h1 := one_add_cube_le_exp hu
    have hθpos : 0 < 1 - θ := by linarith
    have h2 : 27 * (c' + 1) ≤ (1 - θ) ^ 3 * L := by
      have := mul_le_mul_of_nonneg_left hL4 (pow_pos hθpos 3).le
      rwa [mul_div_cancel₀ _ (pow_pos hθpos 3).ne'] at this
    have h3 : (c' + 1) * L ^ 2 ≤ ((1 - θ) * L) ^ 3 / 27 := by
      rw [le_div_iff₀ (by norm_num)]
      have hL2 : 0 ≤ L ^ 2 := by positivity
      nlinarith [mul_le_mul_of_nonneg_right h2 hL2]
    have h4 : (1 : ℝ) ≤ Real.exp (θ * L) := Real.one_le_exp (mul_nonneg hθ0.le hLpos.le)
    have hX : (X : ℝ) = Real.exp (θ * L) * Real.exp ((1 - θ) * L) := by
      rw [← Real.exp_add, hLdef]
      have : θ * Real.log (X : ℝ) + (1 - θ) * Real.log (X : ℝ) = Real.log (X : ℝ) := by ring
      rw [this, Real.exp_log hXpos]
    rw [hX]
    exact add_le_mul_of_one_add_le h4 h1 h3 (by positivity)
  obtain ⟨N, hNe, hNlo, hNhi, hNq⟩ := hst
  have hfloor : (⌊c' * (y : ℝ) * Real.log y⌋₊ : ℝ) ≤ c' * y * Real.log y :=
    Nat.floor_le (by
      have : 0 ≤ Real.log (y : ℝ) := Real.log_nonneg hy1
      positivity)
  have hQge : c * L * Real.log L + 1 ≤ ((⌊c' * (y : ℝ) * Real.log y⌋₊ + 1 : ℕ) : ℝ) := by
    have h := Nat.lt_floor_add_one (c' * (y : ℝ) * Real.log y)
    push_cast
    linarith
  refine ⟨N, ?_, ?_, hNe, fun q hq => hNq q ?_⟩
  · have h : ((⌊c' * (y : ℝ) * Real.log y⌋₊ + 1 : ℕ) : ℝ) ≤ N := by exact_mod_cast hNlo
    linarith
  · have h : (N : ℝ) ≤ X := by
      have h1 : (N : ℝ) ≤ ⌊c' * (y : ℝ) * Real.log y⌋₊ + y + primorial y := by exact_mod_cast hNhi
      linarith
    exact_mod_cast h
  · have h1 : (q : ℝ) + 1 ≤ c' * y * Real.log y := by linarith
    have h2 : q + 1 ≤ ⌊c' * (y : ℝ) * Real.log y⌋₊ := Nat.le_floor (by exact_mod_cast h1)
    omega

/-- **Unconditional.** For all large `X` there is an even `N ≤ X` (above the threshold) such
that `N - q` is composite for every prime `q < 0.73 · ln X · ln ln X`. The constant is
`1152/1575 = 0.7314…` rounded down; counting pairs of primes gives `1/2` and no more. -/
theorem eventually_exists_even_le_no_summand :
    ∀ᶠ X : ℕ in atTop, ∃ N : ℕ, 0.73 * Real.log X * Real.log (Real.log X) < N ∧ N ≤ X ∧ Even N ∧
      ∀ q : ℕ, (q : ℝ) < 0.73 * Real.log X * Real.log (Real.log X) → ¬ IsSummand N q :=
  eventually_exists_even_le_of_mertensUpper (by norm_num) mertensUpper_elementary (by norm_num)

/-- **Mertens' third theorem**: `ln w · ∏_{p ≤ w} (1 - 1/p) → e^{-γ}`. It is not in Mathlib (checkout
of 22 November 2026); it is a hypothesis of `eventually_exists_even_le_of_mertensThird` and of
its explicit form, and nothing else here uses it.

A formal proof exists outside Mathlib: the PNT+ project
(`github.com/AlexKontorovich/PrimeNumberTheoremAnd`, file
`PrimeNumberTheoremAnd/IEANTN/Mertens.lean`, commit `a4fb698`, Lean 4.35.0) has
`Mertens.prod_one_minus_div_prime_eq` (`∏_{p ≤ x} (1 - 1/p) = e^{-γ} e^{E₃(x)} / ln x`) and
`Mertens.E₃.bound''` (the product is asymptotic to `e^{-γ} / ln x`), from which this statement
follows by restricting to integers. That file was read on 23 November 2026 (2,460 lines, no
`sorry`) but not compiled here, and it is not a dependency of this library. -/
def MertensThird : Prop :=
  Tendsto (fun w : ℕ => Real.log w * ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹)) atTop
    (nhds (Real.exp (-Real.eulerMascheroniConstant)))

/-- The partial products `∏_{3 ≤ r ≤ w} (1 - 1/(r - 1)²)` of the twin-prime constant. -/
noncomputable def twinPartial (w : ℕ) : ℝ := ∏ r ∈ oddPrimesLE w, (1 - 1 / ((r : ℝ) - 1) ^ 2)

/-- The twin-prime constant `C₂ = ∏_{r ≥ 3} (1 - 1/(r - 1)²) = 0.66016…`, defined as the infimum
of its (decreasing) partial products. -/
noncomputable def twinPrimeConstant : ℝ := ⨅ w : ℕ, twinPartial w

theorem twinPartial_factor {r : ℕ} (hr : 3 ≤ r) :
    0 ≤ 1 - 1 / ((r : ℝ) - 1) ^ 2 ∧ 1 - 1 / ((r : ℝ) - 1) ^ 2 ≤ 1 := by
  have h3 : (3 : ℝ) ≤ r := by exact_mod_cast hr
  have hsq : (1 : ℝ) ≤ ((r : ℝ) - 1) ^ 2 := by nlinarith
  have hle : 1 / ((r : ℝ) - 1) ^ 2 ≤ 1 := by
    rw [div_le_one (by positivity)]
    exact hsq
  have hnn : 0 ≤ 1 / ((r : ℝ) - 1) ^ 2 := by positivity
  exact ⟨by linarith, by linarith⟩

theorem twinPartial_nonneg (w : ℕ) : 0 ≤ twinPartial w :=
  Finset.prod_nonneg fun _ hr => (twinPartial_factor (three_le_of_mem_oddPrimesLE hr)).1

theorem twinPartial_antitone : Antitone twinPartial := by
  intro w w' hww
  have hsub : oddPrimesLE w ⊆ oddPrimesLE w' := fun r hr => by
    rw [mem_oddPrimesLE] at hr ⊢
    exact ⟨hr.1.trans hww, hr.2⟩
  exact Finset.prod_le_prod_of_subset_of_le_one₀ hsub
    (fun r hr => (twinPartial_factor (three_le_of_mem_oddPrimesLE hr)).1)
    (fun _ hr _ => (twinPartial_factor (three_le_of_mem_oddPrimesLE hr)).2)

theorem twinPrimeConstant_nonneg : 0 ≤ twinPrimeConstant :=
  Real.iInf_nonneg twinPartial_nonneg

theorem tendsto_twinPartial : Tendsto twinPartial atTop (nhds twinPrimeConstant) :=
  tendsto_atTop_ciInf twinPartial_antitone ⟨0, fun _ ⟨w, hw⟩ => hw ▸ twinPartial_nonneg w⟩

/-- `∏_{3 ≤ r ≤ w} (r - 2)/(r - 1) = 2 ∏_{p ≤ w} (1 - 1/p) · ∏_{3 ≤ r ≤ w} (1 - 1/(r - 1)²)`. -/
theorem oddPrimeProd_eq_mul {w : ℕ} (hw : 2 ≤ w) :
    oddPrimeProd w = 2 * (∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹)) * twinPartial w := by
  rw [← prod_oddPrimesLE_one_sub_inv hw, twinPartial, oddPrimeProd, ← Finset.prod_mul_distrib]
  refine Finset.prod_congr rfl fun r hr => ?_
  exact sub_two_div_sub_one (by exact_mod_cast three_le_of_mem_oddPrimesLE hr)

/-- Mertens' third theorem gives the bound of Mertens type with the sharp constant
`κ = 2 C₂ e^{-γ} = 0.7413…`. -/
theorem mertensUpper_of_mertensThird (h : MertensThird) :
    MertensUpper (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) := by
  intro ε hε
  have hlim : Tendsto (fun w : ℕ => 2 * twinPartial w *
      (Real.log w * ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹))) atTop
      (nhds (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant))) :=
    (tendsto_twinPartial.const_mul 2).mul h
  have hev := hlim.eventually (eventually_lt_nhds
    (show 2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant) <
      2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant) + ε by linarith))
  filter_upwards [hev, eventually_ge_atTop 2] with w hw hw2
  have hlog : 0 < Real.log (w : ℝ) := Real.log_pos (by
    have : (2 : ℝ) ≤ w := by exact_mod_cast hw2
    linarith)
  rw [le_div_iff₀ hlog, oddPrimeProd_eq_mul hw2]
  have e : 2 * (∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹)) * twinPartial w * Real.log w =
      2 * twinPartial w * (Real.log w * ∏ p ∈ Nat.primesLE w, (1 - (p : ℝ)⁻¹)) := by ring
  rw [e]
  exact hw.le

/-- **With Mertens' third theorem: the constant `e^γ / (2 C₂) = 1.349…`.** If
`c · 2 C₂ e^{-γ} < 1`, then for all large `X` there is an even `N ≤ X` such that `N - q` is
composite for every prime `q < c · ln X · ln ln X`. -/
theorem eventually_exists_even_le_of_mertensThird (h : MertensThird) {c : ℝ}
    (hc : c * (2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant)) < 1) :
    ∀ᶠ X : ℕ in atTop, ∃ N : ℕ, c * Real.log X * Real.log (Real.log X) < N ∧ N ≤ X ∧ Even N ∧
      ∀ q : ℕ, (q : ℝ) < c * Real.log X * Real.log (Real.log X) → ¬ IsSummand N q := by
  set κ := 2 * twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant) with hκdef
  have hκ0 : 0 ≤ κ := by
    have := twinPrimeConstant_nonneg
    have := Real.exp_pos (-Real.eulerMascheroniConstant)
    positivity
  have hM := mertensUpper_of_mertensThird h
  rw [← hκdef] at hM
  -- a slightly larger `κ'` that is positive and still has `c κ' < 1`
  obtain ⟨κ', hκκ', hκ'0, hcκ'⟩ : ∃ κ' : ℝ, κ < κ' ∧ 0 < κ' ∧ c * κ' < 1 := by
    rcases le_or_gt c 0 with hc0 | hc0
    · refine ⟨κ + 1, by linarith, by linarith, ?_⟩
      have : c * (κ + 1) ≤ 0 := mul_nonpos_of_nonpos_of_nonneg hc0 (by linarith)
      linarith
    · refine ⟨(κ + 1 / c) / 2, ?_, ?_, ?_⟩
      · have : κ < 1 / c := by
          rw [lt_div_iff₀ hc0]
          linarith
        linarith
      · have : 0 < 1 / c := by positivity
        linarith
      · have h1 : c * ((κ + 1 / c) / 2) = (c * κ + 1) / 2 := by
          field_simp
        rw [h1]
        linarith
  have hM' : MertensUpper κ' := by
    intro ε hε
    filter_upwards [hM ε hε, eventually_ge_atTop 2] with w hw hw2
    have hlog : 0 < Real.log (w : ℝ) := Real.log_pos (by
      have : (2 : ℝ) ≤ w := by exact_mod_cast hw2
      linarith)
    exact hw.trans (div_le_div_of_nonneg_right (by linarith) hlog.le)
  exact eventually_exists_even_le_of_mertensUpper hκ'0 hM' hcκ'

/-- `C₂ ≤ (3/4)(15/16)(35/36)`: the infimum is at most the partial product over `3, 5, 7`. -/
theorem twinPrimeConstant_le : twinPrimeConstant ≤ 1575 / 2304 := by
  have h1 : twinPrimeConstant ≤ twinPartial 7 :=
    ciInf_le ⟨0, fun _ ⟨w, hw⟩ => hw ▸ twinPartial_nonneg w⟩ 7
  have hsub : ({3, 5, 7} : Finset ℕ) ⊆ oddPrimesLE 7 := by
    intro r hr
    simp only [Finset.mem_insert, Finset.mem_singleton] at hr
    rw [mem_oddPrimesLE]
    rcases hr with rfl | rfl | rfl
    · exact ⟨by omega, by norm_num, by norm_num⟩
    · exact ⟨by omega, by norm_num, by norm_num⟩
    · exact ⟨by omega, by norm_num, by norm_num⟩
  have h2 : twinPartial 7 ≤ ∏ r ∈ ({3, 5, 7} : Finset ℕ), (1 - 1 / ((r : ℝ) - 1) ^ 2) :=
    Finset.prod_le_prod_of_subset_of_le_one₀ hsub
      (fun r hr => (twinPartial_factor (three_le_of_mem_oddPrimesLE hr)).1)
      (fun _ hr _ => (twinPartial_factor (three_le_of_mem_oddPrimesLE hr)).2)
  refine h1.trans (h2.trans (le_of_eq ?_))
  rw [Finset.prod_insert (by decide), Finset.prod_insert (by decide), Finset.prod_singleton]
  norm_num

/-- `e^{-γ} < 0.6066`, from `γ > 1/2`. (The true value is `0.5615`.) -/
theorem exp_neg_eulerMascheroni_lt : Real.exp (-Real.eulerMascheroniConstant) < 0.6066 := by
  have hγ := Real.one_half_lt_eulerMascheroniConstant
  have h1 : Real.exp (-Real.eulerMascheroniConstant) < Real.exp (-(1 / 2)) :=
    Real.exp_lt_exp.mpr (by linarith)
  have h2 : Real.exp (-(1 / 2)) < 0.6066 := by
    have hsq : Real.exp (-(1 / 2)) ^ 2 = Real.exp (-1) := by
      rw [sq, ← Real.exp_add]
      norm_num
    have he : Real.exp (-1) < 0.3678794412 := Real.exp_neg_one_lt_d9
    have hpos : 0 < Real.exp (-(1 / 2)) := Real.exp_pos _
    by_contra hcon
    have hge : (0.6066 : ℝ) ≤ Real.exp (-(1 / 2)) := not_lt.mp hcon
    have : (0.6066 : ℝ) ^ 2 ≤ Real.exp (-(1 / 2)) ^ 2 := pow_le_pow_left₀ (by norm_num) hge 2
    rw [hsq] at this
    norm_num at this
    linarith
  exact h1.trans h2

/-- **With Mertens' third theorem, an explicit constant.** For all large `X` there is an even
`N ≤ X` such that `N - q` is composite for every prime `q < 1.2 · ln X · ln ln X`. (The crude
bounds `γ > 1/2` and `C₂ ≤ 0.684` are used; the limit of the method is `1.349`.) -/
theorem eventually_exists_even_le_of_mertensThird_explicit (h : MertensThird) :
    ∀ᶠ X : ℕ in atTop, ∃ N : ℕ, 1.2 * Real.log X * Real.log (Real.log X) < N ∧ N ≤ X ∧ Even N ∧
      ∀ q : ℕ, (q : ℝ) < 1.2 * Real.log X * Real.log (Real.log X) → ¬ IsSummand N q := by
  refine eventually_exists_even_le_of_mertensThird h ?_
  have h1 := twinPrimeConstant_le
  have h2 := exp_neg_eulerMascheroni_lt
  have h3 := twinPrimeConstant_nonneg
  have h4 := Real.exp_pos (-Real.eulerMascheroniConstant)
  have h5 : twinPrimeConstant * Real.exp (-Real.eulerMascheroniConstant) ≤
      1575 / 2304 * 0.6066 := mul_le_mul h1 h2.le h4.le (by norm_num)
  nlinarith

end GoldbachGaps
