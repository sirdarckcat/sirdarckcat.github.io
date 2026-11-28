import GoldbachGaps.CoverBound
import GoldbachGaps.Cap.CommonInteger

/-!
# Every constant, and the order: the covering bound with a fixed layer on a common integer

`GoldbachGaps/CoverBound.lean` covers the odd primes below `c · y ln y` by classes modulo the odd
primes up to `y` for every `c < e^γ / (2 C₂) = 1.349…`: random classes below `δ y`, one row for each
prime above. Here the same is proved for **every** constant `A`.

The cover has three layers (`Cap.exists_classes_of_layers`):

* the *fixed layer*: every prime `r` in `(z, y/4]` takes the class of one common integer `N₁`. A row
  `q` is left by it only if `N₁ - q` has no prime factor in `(z, y/4]`, that is, if `N₁ - q` is
  `z`-smooth or of the form `B · p'` with `p' > y/4` prime;
* the *pigeonhole layer*: the odd primes up to `z = ⌊ln y⌋^K - 1`, which leave the share
  `∏ (r - 2)/(r - 1) = O(1 / ln z)` of what the fixed layer left;
* the *mop-up layer*: the primes in `(y/4, y]`, one row each.

The common integer is not fixed in advance: averaged over `N₁ ∈ [Q, 2Q)`, the fixed layer leaves at
most the share of the integers below `2Q` that have no prime factor in `(z, y/4]`
(`Cap.exists_common_integer`). So the count is a count of integers: Rankin's bound for the smooth
ones (`Cap.card_smooth_le_exp`), and the prime number theorem with a harmonic sum for the others.
That share is `O(ln ln y / ln y)`, against `ln z / ln y` for random classes; with `ln z` a large
multiple of `ln ln y` the three layers cover `A · y ln y` rows.

* `eventually_card_smooth_le`: for all large `y` and `2Q ≥ y`, at most `Q / ln² y` of the integers
  in `[1, 2Q)` are `⌊ln y⌋^K`-smooth.
* `sum_primeCounting_le`: `∑_{B ≤ X/w} π(X/B) ≤ (1 + δ) X (1 + ln (X/w)) / ln w`.
* `layers_common_integer_core`: the count of the three layers at one `y`, with every size
  condition explicit; `A` and `K` need not be the same for different `y`.
* `eventually_exists_classes_every_constant`, `eventually_exists_even_le_every_constant`: **every
  constant** (`K` fixed, `K = ⌈300 A⌉ + 1`).

With the exponent growing, `K = ⌊ln y / (14 (ln ln y)²)⌋` (so that `z` is a power of `y` with
exponent about `1 / (14 ln ln y)`), the same three layers give the order of the bound:

* `eventually_exists_classes_log`: for all large `y`, classes modulo the odd primes up to `y` cover
  every odd prime below `y ln² y / (9000 (ln ln y)²)`.
* `eventually_exists_even_le_log`: **for all large `X` there is an even `N ≤ X` with no Goldbach
  summand below `ln X (ln ln X)² / (150000 (ln ln ln X)²)`.** This is the order of Rankin's theorem
  for gaps between primes with one more logarithm (short of it by a factor `ln ln ln ln X`, which
  a sharper count of smooth numbers would give).
* `card_smooth_le_of_log_le`: the smooth numbers for that `z`, by Rankin's bound with
  `σ = 1 - 1/ln N` and Mertens' bound `∑_{p ≤ w} 1/p ≤ ln ln w + K₀`
  (`exists_sum_primesLE_inv_le`, from `GoldbachGaps/Mertens.lean`).
-/

namespace GoldbachGaps

open Finset Filter

/-- **Smooth numbers are rare.** For `K ≥ 1`, all large `y` and every `Q` with `y ≤ 2Q`: at most
`Q / ln² y` of the integers in `[1, 2Q)` are `⌊ln y⌋^K`-smooth (Rankin's bound with
`σ = 1 - 1/(2K)`). -/
theorem eventually_card_smooth_le (K : ℕ) (hK : 1 ≤ K) :
    ∀ᶠ y : ℕ in atTop, ∀ Q : ℕ, y ≤ 2 * Q →
      (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers (⌊Real.log y⌋₊ ^ K)} : ℝ) ≤
        Q / Real.log y ^ 2 := by
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hlog : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hKr : (1 : ℝ) ≤ K := by exact_mod_cast hK
  set U₀ : ℝ := 2 * K * (16 * K + 13) with hU₀
  have hU0 : 0 ≤ U₀ := by positivity
  have hU1 : 1 ≤ U₀ := by
    rw [hU₀]
    nlinarith
  filter_upwards [hlog.eventually_ge_atTop (U₀ ^ 4), hlog.eventually_ge_atTop 1,
    eventually_ge_atTop 1] with y hL4 hL1 hy1
  intro Q hQ
  set L := Real.log (y : ℝ) with hLdef
  have hLpos : 0 < L := by linarith
  have hypos : (0 : ℝ) < y := by exact_mod_cast hy1
  set m := ⌊L⌋₊ with hmdef
  have hm1 : 1 ≤ m := Nat.floor_pos.mpr hL1
  have hmL : (m : ℝ) ≤ L := Nat.floor_le hLpos.le
  have hm0 : (0 : ℝ) < m := by exact_mod_cast hm1
  set σ : ℝ := 1 - 1 / (2 * K) with hσdef
  have hσ : 1 / 2 ≤ σ := by
    have : 1 / (2 * (K : ℝ)) ≤ 1 / 2 :=
      div_le_div_of_nonneg_left (by norm_num) (by norm_num) (by linarith)
    rw [hσdef]
    linarith
  have hσ1 : σ ≤ 1 := by
    have : 0 ≤ 1 / (2 * (K : ℝ)) := by positivity
    rw [hσdef]
    linarith
  have h := Cap.card_smooth_le_exp (m ^ K) (2 * Q) hσ hσ1
  -- `u = L^(1/4)`: every quantity is a polynomial in `u`
  set u : ℝ := L ^ (1 / 4 : ℝ) with hudef
  have hu0 : 0 ≤ u := Real.rpow_nonneg hLpos.le _
  have hu4 : u ^ 4 = L := by
    rw [hudef, ← Real.rpow_natCast, ← Real.rpow_mul hLpos.le]
    norm_num
  have huU : U₀ ≤ u := by
    have h1 : (U₀ ^ 4) ^ (1 / 4 : ℝ) ≤ L ^ (1 / 4 : ℝ) :=
      Real.rpow_le_rpow (by positivity) hL4 (by norm_num)
    rw [← Real.rpow_natCast, ← Real.rpow_mul hU0] at h1
    norm_num at h1
    exact h1
  have hu1 : 1 ≤ u := hU1.trans huU
  have hsqrt : L ^ (1 / 2 : ℝ) = u ^ 2 := by
    rw [hudef, ← Real.rpow_natCast, ← Real.rpow_mul hLpos.le]
    norm_num
  have hlogL : Real.log L ≤ 4 * u := by
    have h1 := Real.log_le_rpow_div hLpos.le (show (0 : ℝ) < 1 / 4 by norm_num)
    rw [hudef]
    linarith
  -- the three ingredients of Rankin's bound
  have hN : (((m ^ K : ℕ) : ℝ)) ^ (1 - σ) ≤ u ^ 2 := by
    have e : (1 - σ) = 1 / (2 * K) := by
      rw [hσdef]
      ring
    have e2 : (K : ℝ) * (1 / (2 * K)) = 1 / 2 := by
      field_simp
    rw [e, Nat.cast_pow, ← Real.rpow_natCast (m : ℝ) K, ← Real.rpow_mul hm0.le, e2, ← hsqrt]
    exact Real.rpow_le_rpow hm0.le hmL (by norm_num)
  have hN0 : 0 ≤ (((m ^ K : ℕ) : ℝ)) ^ (1 - σ) := Real.rpow_nonneg (Nat.cast_nonneg _) _
  have hlogN0 : 0 ≤ Real.log ((m ^ K : ℕ) : ℝ) := by
    apply Real.log_nonneg
    have : 1 ≤ m ^ K := Nat.one_le_pow _ _ hm1
    exact_mod_cast this
  have hlogN : Real.log ((m ^ K : ℕ) : ℝ) ≤ K * (4 * u) := by
    rw [Nat.cast_pow, Real.log_pow]
    have h1 : Real.log m ≤ Real.log L := Real.log_le_log hm0 hmL
    have hK0 : (0 : ℝ) ≤ K := by positivity
    exact mul_le_mul_of_nonneg_left (h1.trans hlogL) hK0
  have hQpos : (0 : ℝ) < ((2 * Q : ℕ) : ℝ) := by
    have : 0 < 2 * Q := by omega
    exact_mod_cast this
  have hX : ((2 * Q : ℕ) : ℝ) ^ σ ≤ ((2 * Q : ℕ) : ℝ) * Real.exp (-(L / (2 * K))) := by
    have e : σ = 1 + (-(1 / (2 * K))) := by
      rw [hσdef]
      ring
    rw [e, Real.rpow_add hQpos, Real.rpow_one]
    refine mul_le_mul_of_nonneg_left ?_ hQpos.le
    have hyQ : (y : ℝ) ≤ ((2 * Q : ℕ) : ℝ) := by exact_mod_cast hQ
    have hneg : -(1 / (2 * (K : ℝ))) ≤ 0 := by
      have : 0 ≤ 1 / (2 * (K : ℝ)) := by positivity
      linarith
    calc ((2 * Q : ℕ) : ℝ) ^ (-(1 / (2 * (K : ℝ)))) ≤ (y : ℝ) ^ (-(1 / (2 * (K : ℝ)))) :=
          Real.rpow_le_rpow_of_nonpos hypos hyQ hneg
      _ = Real.exp (-(L / (2 * K))) := by
          rw [Real.rpow_def_of_pos hypos]
          congr 1
          rw [hLdef]
          ring
  -- the exponent
  have hexp : -(L / (2 * K)) + 4 * (u ^ 2 * (1 + K * (4 * u))) ≤
      -(Real.log 2 + 2 * Real.log L) := by
    have hlog2 : Real.log 2 ≤ 1 := by
      have := Real.log_le_sub_one_of_pos (show (0 : ℝ) < 2 by norm_num)
      linarith
    have hK0 : (0 : ℝ) < K := by linarith
    have hu2 : u ^ 2 ≤ u ^ 3 := pow_le_pow_right₀ hu1 (by norm_num)
    have hu1' : u ≤ u ^ 3 := le_self_pow₀ hu1 (by norm_num)
    have hu3 : 1 ≤ u ^ 3 := one_le_pow₀ hu1
    have hu3' : 0 ≤ u ^ 3 := by positivity
    have h3 : 2 * K * (16 * K + 13) * u ^ 3 ≤ u ^ 4 := by
      have := mul_le_mul_of_nonneg_right huU hu3'
      rw [hU₀] at this
      nlinarith [this]
    have h4 : 4 * u ^ 2 + 16 * K * u ^ 3 + 1 + 8 * u ≤ (16 * K + 13) * u ^ 3 := by nlinarith
    have h5 : 2 * K * (4 * u ^ 2 + 16 * K * u ^ 3 + 1 + 8 * u) ≤ u ^ 4 := by
      have := mul_le_mul_of_nonneg_left h4 (by positivity : (0 : ℝ) ≤ 2 * K)
      nlinarith [this]
    have h6 : 4 * u ^ 2 + 16 * K * u ^ 3 + 1 + 8 * u ≤ L / (2 * K) := by
      rw [le_div_iff₀ (by positivity), ← hu4]
      nlinarith [h5]
    have e : 4 * (u ^ 2 * (1 + K * (4 * u))) = 4 * u ^ 2 + 16 * K * u ^ 3 := by ring
    rw [e]
    linarith
  have hfin : Real.exp (-(Real.log 2 + 2 * Real.log L)) = 1 / (2 * L ^ 2) := by
    have e : Real.exp (2 * Real.log L) = L ^ 2 := by
      rw [show (2 : ℝ) * Real.log L = Real.log L + Real.log L by ring, Real.exp_add,
        Real.exp_log hLpos]
      ring
    rw [Real.exp_neg, Real.exp_add, Real.exp_log (by norm_num : (0 : ℝ) < 2), e, one_div]
  calc (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers (m ^ K)} : ℝ)
      ≤ ((2 * Q : ℕ) : ℝ) ^ σ *
          Real.exp (4 * ((((m ^ K : ℕ) : ℝ)) ^ (1 - σ) * (1 + Real.log ((m ^ K : ℕ) : ℝ)))) := h
    _ ≤ (((2 * Q : ℕ) : ℝ) * Real.exp (-(L / (2 * K)))) *
          Real.exp (4 * (u ^ 2 * (1 + K * (4 * u)))) := by
        refine mul_le_mul hX ?_ (Real.exp_pos _).le (by positivity)
        apply Real.exp_le_exp.mpr
        refine mul_le_mul_of_nonneg_left ?_ (by norm_num)
        exact mul_le_mul hN (by linarith) (by linarith) (by positivity)
    _ = ((2 * Q : ℕ) : ℝ) * Real.exp (-(L / (2 * K)) + 4 * (u ^ 2 * (1 + K * (4 * u)))) := by
        rw [mul_assoc, ← Real.exp_add]
    _ ≤ ((2 * Q : ℕ) : ℝ) * Real.exp (-(Real.log 2 + 2 * Real.log L)) :=
        mul_le_mul_of_nonneg_left (Real.exp_le_exp.mpr hexp) hQpos.le
    _ = Q / L ^ 2 := by
        rw [hfin]
        push_cast
        field_simp

/-- **The integers with a large prime factor.** If `π(x) ≤ (1 + δ) x / ln x` for `x ≥ x₀` and
`w ≥ max 2 x₀`, then `∑_{1 ≤ B ≤ X/w} π(X/B) ≤ (1 + δ) X (1 + ln (X/w)) / ln w`. -/
theorem sum_primeCounting_le {δ x₀ : ℝ} (hδ : 0 ≤ δ)
    (hpnt : ∀ x : ℝ, x₀ ≤ x → (Nat.primeCounting ⌊x⌋₊ : ℝ) ≤ (1 + δ) * (x / Real.log x))
    {X w : ℕ} (hw : 2 ≤ w) (hwx : x₀ ≤ (w : ℝ)) :
    ((∑ B ∈ Icc 1 (X / w), Nat.primeCounting (X / B) : ℕ) : ℝ) ≤
      (1 + δ) * X * (1 + Real.log ((X / w : ℕ) : ℝ)) / Real.log w := by
  have hw1 : (1 : ℝ) < w := by
    have : 1 < w := by omega
    exact_mod_cast this
  have hlogw : 0 < Real.log w := Real.log_pos hw1
  have hterm : ∀ B ∈ Icc 1 (X / w), (Nat.primeCounting (X / B) : ℝ) ≤
      (1 + δ) * X / Real.log w * ((B : ℝ))⁻¹ := by
    intro B hB
    obtain ⟨hB1, hBM⟩ := Finset.mem_Icc.mp hB
    have hB0 : (0 : ℝ) < B := by exact_mod_cast hB1
    have hwle : w ≤ X / B := by
      have h1 : B * w ≤ X := (Nat.le_div_iff_mul_le (by omega : 0 < w)).mp hBM
      exact (Nat.le_div_iff_mul_le hB1).mpr (by rwa [mul_comm] at h1)
    have hwle' : (w : ℝ) ≤ ((X / B : ℕ) : ℝ) := by exact_mod_cast hwle
    have h1 := hpnt ((X / B : ℕ) : ℝ) (hwx.trans hwle')
    rw [Nat.floor_natCast] at h1
    have hxle : ((X / B : ℕ) : ℝ) ≤ (X : ℝ) / B := Nat.cast_div_le
    have hlogle : Real.log w ≤ Real.log ((X / B : ℕ) : ℝ) :=
      Real.log_le_log (by linarith) hwle'
    have hx0 : (0 : ℝ) ≤ ((X / B : ℕ) : ℝ) := Nat.cast_nonneg _
    calc (Nat.primeCounting (X / B) : ℝ)
        ≤ (1 + δ) * (((X / B : ℕ) : ℝ) / Real.log ((X / B : ℕ) : ℝ)) := h1
      _ ≤ (1 + δ) * (((X : ℝ) / B) / Real.log w) := by
          refine mul_le_mul_of_nonneg_left ?_ (by linarith)
          exact div_le_div₀ (by positivity) hxle hlogw hlogle
      _ = (1 + δ) * X / Real.log w * ((B : ℝ))⁻¹ := by
          field_simp
  have hharm : ∑ B ∈ Icc 1 (X / w), ((B : ℝ))⁻¹ ≤ 1 + Real.log ((X / w : ℕ) : ℝ) := by
    have h1 := harmonic_le_one_add_log (X / w)
    rw [harmonic_eq_sum_Icc] at h1
    push_cast at h1
    exact h1
  have hcoef : 0 ≤ (1 + δ) * X / Real.log w := by positivity
  calc ((∑ B ∈ Icc 1 (X / w), Nat.primeCounting (X / B) : ℕ) : ℝ)
      = ∑ B ∈ Icc 1 (X / w), (Nat.primeCounting (X / B) : ℝ) := by push_cast; rfl
    _ ≤ ∑ B ∈ Icc 1 (X / w), (1 + δ) * X / Real.log w * ((B : ℝ))⁻¹ := Finset.sum_le_sum hterm
    _ = (1 + δ) * X / Real.log w * ∑ B ∈ Icc 1 (X / w), ((B : ℝ))⁻¹ := by rw [Finset.mul_sum]
    _ ≤ (1 + δ) * X / Real.log w * (1 + Real.log ((X / w : ℕ) : ℝ)) :=
        mul_le_mul_of_nonneg_left hharm hcoef
    _ = (1 + δ) * X * (1 + Real.log ((X / w : ℕ) : ℝ)) / Real.log w := by ring

/-- `ln M ≤ ln c` for a natural number `M ≤ c` with `c ≥ 1` (also when `M = 0`). -/
theorem log_natCast_le_log {M : ℕ} {c : ℝ} (hc : 1 ≤ c) (h : (M : ℝ) ≤ c) :
    Real.log (M : ℝ) ≤ Real.log c := by
  rcases Nat.eq_zero_or_pos M with h0 | h0
  · rw [h0, Nat.cast_zero, Real.log_zero]
    exact Real.log_nonneg hc
  · exact Real.log_le_log (by exact_mod_cast h0) h

set_option maxHeartbeats 1600000 in
/-- **The three layers at one `y`.** The finite statement behind the theorems of this file, with
every size condition explicit. Given the prime number theorem with `δ = 1/10` for `x ≥ x₀`, the
elementary bound for `∏ (r - 2)/(r - 1)` for `w ≥ w₀`, and the bound for the smooth numbers
(`hsmooth`): if `300 A ≤ K - 1` and `y` is large enough in the ways listed, then there are an
integer `N₁`, a fixed layer `F` (the primes in `(z, y/4]`, each with the class of `N₁`), a
pigeonhole layer `S` (the odd primes up to `z = ⌊ln y⌋^K - 1`) and a mop-up layer `T` (the primes
in `(y/4, y]`) that satisfy the count of `Cap.exists_classes_of_layers` for the rows below
`⌊A y ln y⌋`. Neither `A` nor `K` has to be the same for different `y`. -/
theorem layers_common_integer_core {A x₀ : ℝ} {K w₀ y : ℕ} (hA : 1 ≤ A) (hK2 : 2 ≤ K)
    (hKA : 300 * A ≤ ((K - 1 : ℕ) : ℝ)) (hx₀0 : 0 ≤ x₀)
    (hx₀ : ∀ x : ℝ, x₀ ≤ x →
      (1 - 1 / 10) * (x / Real.log x) ≤ (Nat.primeCounting ⌊x⌋₊ : ℝ) ∧
        (Nat.primeCounting ⌊x⌋₊ : ℝ) ≤ (1 + 1 / 10) * (x / Real.log x))
    (hw₀ : ∀ w : ℕ, w₀ ≤ w → oddPrimeProd w ≤ (1575 / 1152 + 1 / 10) / Real.log w)
    (hsmooth : ∀ Q : ℕ, y ≤ 2 * Q →
      (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers (⌊Real.log y⌋₊ ^ K)} : ℝ) ≤
        Q / Real.log y ^ 2)
    (hgrowy : Real.log (y : ℝ) ^ (K + 1) ≤ (y : ℝ) / 20)
    (hQx₀ : x₀ ≤ A * (y : ℝ) * Real.log y) (hyx₀ : x₀ ≤ (y : ℝ)) (hwx₀ : 8 * x₀ + 8 ≤ (y : ℝ))
    (hLw₀ : (w₀ : ℝ) + 2 ≤ Real.log (y : ℝ)) (hL7A : 7 * A ≤ Real.log (y : ℝ))
    (hL14 : 14 ≤ Real.log (y : ℝ))
    (hLL1 : 1 + Real.log (16 * A) ≤ Real.log (Real.log (y : ℝ)))
    (hLL2 : 2 ≤ Real.log (Real.log (y : ℝ))) (hy8 : 8 ≤ y) :
    2 ≤ y ∧ ∃ (N₁ : ℕ) (F S T : Finset ℕ),
      (∀ r ∈ F, r.Prime ∧ r ≠ 2) ∧ (∀ r ∈ S, r.Prime ∧ r ≠ 2) ∧ (∀ r ∈ T, r.Prime ∧ r ≠ 2) ∧
      (∀ r ∈ F ∪ S ∪ T, r ≤ y) ∧ Disjoint F S ∧ Disjoint F T ∧ Disjoint S T ∧
      #{q ∈ range ⌊A * y * Real.log y⌋₊ | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
          ∀ r ∈ F, ¬ q ≡ (fun _ : ℕ => N₁) r [MOD r]} * ∏ r ∈ S, (r - 2) +
        #{q ∈ range ⌊A * y * Real.log y⌋₊ | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} * ∏ r ∈ S, (r - 1) ≤
        #T * ∏ r ∈ S, (r - 1) := by
  classical
  have hA0 : 0 < A := by linarith
  have hK1 : 1 ≤ K := by omega
  set L := Real.log (y : ℝ) with hLdef
  set lnL := Real.log L with hlnLdef
  set Q := ⌊A * (y : ℝ) * L⌋₊ with hQdef
  set w := y / 4 with hwdef
  set m := ⌊L⌋₊ with hmdef
  set z := m ^ K - 1 with hzdef
  have hLpos : 0 < L := by linarith
  have hL1 : 1 ≤ L := by linarith
  have hy8r : (8 : ℝ) ≤ y := by exact_mod_cast hy8
  have hypos : (0 : ℝ) < y := by linarith
  have hlnL2 : 2 ≤ lnL := hLL2
  -- `m = ⌊L⌋`
  have hm2 : 2 ≤ m := Nat.le_floor (by push_cast; linarith)
  have hmL : (m : ℝ) ≤ L := Nat.floor_le hLpos.le
  have hmL' : L - 1 < m := Nat.sub_one_lt_floor L
  have hm0 : (0 : ℝ) < m := by
    have : 0 < m := by omega
    exact_mod_cast this
  -- `z + 1 = m^K`
  have hmK : 1 ≤ m ^ K := Nat.one_le_pow _ _ (by omega)
  have hz1 : z + 1 = m ^ K := by omega
  have hzm : m ^ (K - 1) ≤ z := by
    have e : m ^ K = m ^ (K - 1) * m := by
      rw [← pow_succ, Nat.sub_add_cancel hK1]
    have h1 : 1 ≤ m ^ (K - 1) := Nat.one_le_pow _ _ (by omega)
    have h2 : m ^ (K - 1) * 2 ≤ m ^ (K - 1) * m := Nat.mul_le_mul_left _ hm2
    omega
  have hz3 : 3 ≤ z := by
    have h1 : m ^ 2 ≤ m ^ K := Nat.pow_le_pow_right (by omega) hK2
    have h2 : 2 ^ 2 ≤ m ^ 2 := Nat.pow_le_pow_left hm2 2
    omega
  -- sizes: `y ≥ 140 A L`, `z ≤ y/(20 L)`
  have hL2 : L ^ 2 ≤ L ^ (K + 1) := pow_le_pow_right₀ hL1 (by omega)
  have hyAL : 140 * A * L ≤ y := by
    have h1 : 7 * A * L ≤ L * L := mul_le_mul_of_nonneg_right hL7A hLpos.le
    have e : L ^ 2 = L * L := sq L
    linarith
  have hLK : L ^ K * (20 * L) ≤ y := by
    have e : L ^ (K + 1) = L ^ K * L := pow_succ L K
    linarith
  have hzr : (z : ℝ) * (20 * L) ≤ y := by
    have h1 : (z : ℝ) ≤ ((m ^ K : ℕ) : ℝ) := by
      have : z ≤ m ^ K := by omega
      exact_mod_cast this
    have h2 : ((m ^ K : ℕ) : ℝ) ≤ L ^ K := by
      push_cast
      exact pow_le_pow_left₀ hm0.le hmL K
    have h3 : (z : ℝ) * (20 * L) ≤ L ^ K * (20 * L) :=
      mul_le_mul_of_nonneg_right (h1.trans h2) (by positivity)
    linarith
  have hzy : (z : ℝ) ≤ y / (20 * L) := by
    rw [le_div_iff₀ (by positivity)]
    exact hzr
  -- `w = y/4`
  have hw4 : 4 * w ≤ y := by omega
  have hw4' : y ≤ 4 * w + 3 := by omega
  have hw2 : 2 ≤ w := by omega
  have hwr1 : (w : ℝ) ≤ y / 4 := by
    have : (4 : ℝ) * w ≤ y := by exact_mod_cast hw4
    linarith
  have hwr2 : (y : ℝ) / 8 ≤ w := by
    have : (y : ℝ) ≤ 4 * w + 3 := by exact_mod_cast hw4'
    linarith
  have hwx : x₀ ≤ (w : ℝ) := by
    have : (y : ℝ) ≤ 4 * w + 3 := by exact_mod_cast hw4'
    linarith
  have hwpos : (0 : ℝ) < w := by linarith
  have hlogw : L / 2 ≤ Real.log (w : ℝ) := by
    have h1 : Real.log ((y : ℝ) / 8) ≤ Real.log (w : ℝ) := Real.log_le_log (by positivity) hwr2
    have h2 : Real.log ((y : ℝ) / 8) = L - Real.log 8 :=
      Real.log_div hypos.ne' (by norm_num)
    have h3 : Real.log 8 ≤ 7 := by
      have := Real.log_le_sub_one_of_pos (show (0 : ℝ) < 8 by norm_num)
      linarith
    linarith
  have hlogwpos : 0 < Real.log (w : ℝ) := by linarith
  have hzw : z < w := by
    have h1 : (z : ℝ) < w := by
      have h0 : (z : ℝ) * 20 ≤ (z : ℝ) * (20 * L) :=
        mul_le_mul_of_nonneg_left (by linarith) (Nat.cast_nonneg z)
      linarith
    exact_mod_cast h1
  -- `Q = ⌊A y L⌋`
  have hAL : 1 ≤ A * L := by
    have := mul_le_mul hA hL1 (by norm_num) hA0.le
    linarith
  have hAyL : (y : ℝ) ≤ A * y * L := by
    calc (y : ℝ) = y * 1 := by ring
      _ ≤ y * (A * L) := mul_le_mul_of_nonneg_left hAL hypos.le
      _ = A * y * L := by ring
  have hQy : y ≤ Q := Nat.le_floor hAyL
  have hQpos : 0 < Q := by omega
  have hQr : (Q : ℝ) ≤ A * y * L := Nat.floor_le (by positivity)
  have hQr0 : (0 : ℝ) < Q := by exact_mod_cast hQpos
  have hQww : 2 * Q ≤ w * w := by
    have h1 : (2 : ℝ) * Q ≤ (w : ℝ) * w := by
      have h2 : (y : ℝ) / 8 * ((y : ℝ) / 8) ≤ (w : ℝ) * w :=
        mul_le_mul hwr2 hwr2 (by positivity) hwpos.le
      have h3 : 128 * A * L * y ≤ y * y :=
        mul_le_mul_of_nonneg_right (by linarith [mul_pos hA0 hLpos]) hypos.le
      linarith
    exact_mod_cast h1
  -- the layers
  set F := Cap.primesIoc z w with hFdef
  set S := oddPrimesLE z with hSdef
  set T := (Nat.primesLE y).filter (w < ·) with hTdef
  have hF : ∀ r ∈ F, r.Prime ∧ r ≠ 2 := fun r hr => by
    obtain ⟨⟨h1, -⟩, h2⟩ := Cap.mem_primesIoc.mp hr
    exact ⟨h2, by omega⟩
  have hS : ∀ r ∈ S, r.Prime ∧ r ≠ 2 := fun r hr => (mem_oddPrimesLE.mp hr).2
  have hT : ∀ r ∈ T, r.Prime ∧ r ≠ 2 := fun r hr => by
    obtain ⟨hr1, hr2⟩ := Finset.mem_filter.mp hr
    exact ⟨(Nat.mem_primesLE.mp hr1).2, by omega⟩
  have hB : ∀ r ∈ F ∪ S ∪ T, r ≤ y := fun r hr => by
    rcases Finset.mem_union.mp hr with h | h
    · rcases Finset.mem_union.mp h with h | h
      · obtain ⟨⟨-, h1⟩, -⟩ := Cap.mem_primesIoc.mp h
        omega
      · have := (mem_oddPrimesLE.mp h).1
        omega
    · exact (Nat.mem_primesLE.mp (Finset.mem_filter.mp h).1).1
  have hFS : Disjoint F S := Finset.disjoint_left.mpr fun r hr hr' => by
    obtain ⟨⟨h1, -⟩, -⟩ := Cap.mem_primesIoc.mp hr
    have h2 := (mem_oddPrimesLE.mp hr').1
    omega
  have hFT : Disjoint F T := Finset.disjoint_left.mpr fun r hr hr' => by
    obtain ⟨⟨-, h1⟩, -⟩ := Cap.mem_primesIoc.mp hr
    have h2 := (Finset.mem_filter.mp hr').2
    omega
  have hST : Disjoint S T := Finset.disjoint_left.mpr fun r hr hr' => by
    have h1 := (mem_oddPrimesLE.mp hr).1
    have h2 := (Finset.mem_filter.mp hr').2
    omega
  -- the rows, and the common integer
  set P := {q ∈ range Q | q.Prime ∧ q ≠ 2} with hPdef
  have hPQ : ∀ q ∈ P, q < Q := fun q hq => Finset.mem_range.mp (Finset.mem_filter.mp hq).1
  obtain ⟨N₁, -, -, hcomm⟩ := Cap.exists_common_integer F P hQpos hPQ
  set G := #{n ∈ Ico 1 (2 * Q) | ∀ r ∈ F, ¬ r ∣ n} with hGdef
  set L₁ := #{q ∈ P | ∀ r ∈ F, ¬ q ≡ N₁ [MOD r]} with hL₁def
  -- (a) the integers below `2Q` with no prime factor in `(z, w]`
  have hG1 := Cap.card_no_factor_le (z := z) (w := w) (X := 2 * Q) (by omega) hQww
  rw [hz1] at hG1
  have hPsi := hsmooth Q (by omega)
  have hSum := sum_primeCounting_le (δ := 1 / 10) (x₀ := x₀) (by norm_num)
    (fun x hx => (hx₀ x hx).2) (X := 2 * Q) hw2 hwx
  have hM : ((2 * Q / w : ℕ) : ℝ) ≤ 16 * A * L := by
    have h1 : ((2 * Q / w : ℕ) : ℝ) ≤ ((2 * Q : ℕ) : ℝ) / w := Nat.cast_div_le
    have h2 : ((2 * Q : ℕ) : ℝ) / w ≤ 16 * A * L := by
      rw [div_le_iff₀ hwpos]
      push_cast
      have h3 : 16 * A * L * ((y : ℝ) / 8) ≤ 16 * A * L * w :=
        mul_le_mul_of_nonneg_left hwr2 (by positivity)
      linarith
    exact h1.trans h2
  have h16 : 1 ≤ 16 * A * L := by linarith
  have hlogM : 1 + Real.log ((2 * Q / w : ℕ) : ℝ) ≤ 2 * lnL := by
    have h1 := log_natCast_le_log h16 hM
    have h2 : Real.log (16 * A * L) = Real.log (16 * A) + lnL :=
      Real.log_mul (by positivity) hLpos.ne'
    linarith
  have hSum' : ((∑ B ∈ Icc 1 (2 * Q / w), Nat.primeCounting (2 * Q / B) : ℕ) : ℝ) ≤
      44 / 5 * Q * lnL / L := by
    refine hSum.trans ?_
    have hnum : (1 + 1 / 10) * ((2 * Q : ℕ) : ℝ) * (1 + Real.log ((2 * Q / w : ℕ) : ℝ)) ≤
        (1 + 1 / 10) * ((2 * Q : ℕ) : ℝ) * (2 * lnL) :=
      mul_le_mul_of_nonneg_left hlogM (by positivity)
    calc (1 + 1 / 10) * ((2 * Q : ℕ) : ℝ) * (1 + Real.log ((2 * Q / w : ℕ) : ℝ)) / Real.log w
        ≤ (1 + 1 / 10) * ((2 * Q : ℕ) : ℝ) * (2 * lnL) / (L / 2) :=
          div_le_div₀ (by positivity) hnum (by positivity) hlogw
      _ = 44 / 5 * Q * lnL / L := by
          push_cast
          field_simp
          ring
  have hGr : (G : ℝ) ≤ Q * (1 / L ^ 2 + 44 / 5 * lnL / L) := by
    have h1 : (G : ℝ) ≤ (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers (m ^ K)} : ℝ) +
        ((∑ B ∈ Icc 1 (2 * Q / w), Nat.primeCounting (2 * Q / B) : ℕ) : ℝ) := by
      exact_mod_cast hG1
    calc (G : ℝ) ≤ Q / L ^ 2 + 44 / 5 * Q * lnL / L := by linarith
      _ = Q * (1 / L ^ 2 + 44 / 5 * lnL / L) := by ring
  -- (b) the rows
  have hPr : (#P : ℝ) ≤ 11 / 10 * A * y := by
    have h1 : #P ≤ Nat.primeCounting Q := by
      rw [← Nat.primesLE_card_eq_primeCounting]
      refine Finset.card_le_card fun q hq => ?_
      obtain ⟨hq1, hq2, -⟩ := Finset.mem_filter.mp hq
      exact Nat.mem_primesLE.mpr ⟨(Finset.mem_range.mp hq1).le, hq2⟩
    have hlogge : L ≤ Real.log (A * y * L) := Real.log_le_log hypos hAyL
    have hnum : 0 ≤ A * (y : ℝ) * L := by positivity
    calc (#P : ℝ) ≤ (Nat.primeCounting Q : ℝ) := by exact_mod_cast h1
      _ ≤ (1 + 1 / 10) * (A * y * L / Real.log (A * y * L)) := (hx₀ _ hQx₀).2
      _ ≤ (1 + 1 / 10) * (A * y * L / L) :=
          mul_le_mul_of_nonneg_left (div_le_div_of_nonneg_left hnum hLpos hlogge) (by norm_num)
      _ = 11 / 10 * A * y := by
          field_simp
          ring
  -- (c) what the fixed layer leaves
  have hL₁r : (L₁ : ℝ) ≤ 11 / 10 * A * y * (1 / L ^ 2 + 44 / 5 * lnL / L) := by
    have h1 : (L₁ : ℝ) * Q ≤ (#P : ℝ) * G := by exact_mod_cast hcomm
    have hbr : 0 ≤ 1 / L ^ 2 + 44 / 5 * lnL / L := by positivity
    have h2 : (#P : ℝ) * G ≤ 11 / 10 * A * y * (Q * (1 / L ^ 2 + 44 / 5 * lnL / L)) :=
      mul_le_mul hPr hGr (Nat.cast_nonneg _) (by positivity)
    have h3 : (L₁ : ℝ) * Q ≤ 11 / 10 * A * y * (1 / L ^ 2 + 44 / 5 * lnL / L) * Q := by
      calc (L₁ : ℝ) * Q ≤ 11 / 10 * A * y * (Q * (1 / L ^ 2 + 44 / 5 * lnL / L)) := h1.trans h2
        _ = 11 / 10 * A * y * (1 / L ^ 2 + 44 / 5 * lnL / L) * Q := by ring
    exact le_of_mul_le_mul_right h3 hQr0
  -- (d) the product over the pigeonhole layer
  set Kr : ℝ := ((K - 1 : ℕ) : ℝ) with hKrdef
  have hKr0 : 0 < Kr := by linarith
  have hlogz : Kr * (lnL / 2) ≤ Real.log (z : ℝ) := by
    have h1 : Real.log (((m ^ (K - 1) : ℕ)) : ℝ) ≤ Real.log (z : ℝ) := by
      apply Real.log_le_log
      · have : 0 < m ^ (K - 1) := Nat.pos_of_ne_zero (by positivity)
        exact_mod_cast this
      · exact_mod_cast hzm
    have h2 : Real.log (((m ^ (K - 1) : ℕ)) : ℝ) = Kr * Real.log m := by
      rw [Nat.cast_pow, Real.log_pow]
    have h3 : lnL / 2 ≤ Real.log m := by
      have h4 : L / 2 ≤ (m : ℝ) := by linarith
      have h5 : Real.log (L / 2) ≤ Real.log m := Real.log_le_log (by positivity) h4
      have h6 : Real.log (L / 2) = lnL - Real.log 2 := Real.log_div hLpos.ne' (by norm_num)
      have h7 : Real.log 2 ≤ 1 := by
        have := Real.log_le_sub_one_of_pos (show (0 : ℝ) < 2 by norm_num)
        linarith
      linarith
    have h8 : Kr * (lnL / 2) ≤ Kr * Real.log m := mul_le_mul_of_nonneg_left h3 hKr0.le
    linarith
  have hzw₀ : w₀ ≤ z := by
    have h1 : w₀ + 1 ≤ m := Nat.le_floor (by push_cast; linarith)
    have h2 : m ≤ m ^ K := Nat.le_self_pow (by omega) m
    omega
  have hPi : oddPrimeProd z ≤ 3 / (Kr * lnL) := by
    have h1 := hw₀ z hzw₀
    have hden : 0 < Kr * (lnL / 2) := by positivity
    calc oddPrimeProd z ≤ (1575 / 1152 + 1 / 10) / Real.log (z : ℝ) := h1
      _ ≤ (1575 / 1152 + 1 / 10) / (Kr * (lnL / 2)) :=
          div_le_div_of_nonneg_left (by norm_num) hden hlogz
      _ ≤ (3 / 2) / (Kr * (lnL / 2)) :=
          div_le_div_of_nonneg_right (by norm_num) hden.le
      _ = 3 / (Kr * lnL) := by
          field_simp
  have hPi0 : 0 ≤ oddPrimeProd z := Finset.prod_nonneg fun r hr => by
    have h3 : (3 : ℝ) ≤ r := by exact_mod_cast three_le_of_mem_oddPrimesLE hr
    exact div_nonneg (by linarith) (by linarith)
  -- (e) the mop-up layer
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
      calc (Nat.primeCounting w : ℝ) ≤ (1 + 1 / 10) * ((w : ℝ) / Real.log w) := h4
        _ ≤ (1 + 1 / 10) * (((y : ℝ) / 4) / (L / 2)) :=
            mul_le_mul_of_nonneg_left (div_le_div₀ (by positivity) hwr1 (by positivity) hlogw)
              (by norm_num)
        _ = 11 / 20 * ((y : ℝ) / L) := by
            field_simp
            ring
    linarith
  -- (f) the count
  have hA' : #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
      ∀ r ∈ F, ¬ q ≡ (fun _ : ℕ => N₁) r [MOD r]} ≤ L₁ := by
    refine Finset.card_le_card fun q hq => ?_
    obtain ⟨hq1, hq2, -, hq3⟩ := Finset.mem_filter.mp hq
    exact Finset.mem_filter.mpr ⟨Finset.mem_filter.mpr ⟨hq1, hq2⟩, hq3⟩
  have hZ' : #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} ≤ z := by
    have h1 : #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} ≤ #(Icc 1 z) := by
      refine Finset.card_le_card fun q hq => ?_
      have hqS := (Finset.mem_filter.mp hq).2.2
      obtain ⟨h1, h2, -⟩ := mem_oddPrimesLE.mp hqS
      exact Finset.mem_Icc.mpr ⟨h2.one_le, h1⟩
    rw [Nat.card_Icc] at h1
    omega
  have hP1pos : (0 : ℝ) < ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) := by
    have : 0 < ∏ r ∈ S, (r - 1) := Finset.prod_pos fun r hr => by
      have := three_le_of_mem_oddPrimesLE hr
      omega
    exact_mod_cast this
  have hcount : #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
        ∀ r ∈ F, ¬ q ≡ (fun _ : ℕ => N₁) r [MOD r]} * ∏ r ∈ S, (r - 2) +
      #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} * ∏ r ∈ S, (r - 1) ≤
      #T * ∏ r ∈ S, (r - 1) := by
    set A' := #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
        ∀ r ∈ F, ¬ q ≡ (fun _ : ℕ => N₁) r [MOD r]} with hA'def
    set Zc := #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} with hZdef
    have hAr : (A' : ℝ) ≤ 11 / 10 * A * y * (1 / L ^ 2 + 44 / 5 * lnL / L) :=
      le_trans (by exact_mod_cast hA') hL₁r
    have hZr : (Zc : ℝ) ≤ 1 / 20 * ((y : ℝ) / L) := by
      have h1 : (Zc : ℝ) ≤ z := by exact_mod_cast hZ'
      have h2 : (y : ℝ) / (20 * L) = 1 / 20 * ((y : ℝ) / L) := by
        field_simp
      linarith
    have hB1 : 0 ≤ 11 / 10 * A * (y : ℝ) * (1 / L ^ 2 + 44 / 5 * lnL / L) := by positivity
    have hmul : (A' : ℝ) * oddPrimeProd z ≤
        11 / 10 * A * y * (1 / L ^ 2 + 44 / 5 * lnL / L) * (3 / (Kr * lnL)) :=
      mul_le_mul hAr hPi hPi0 hB1
    have hprod : 11 / 10 * A * y * (1 / L ^ 2 + 44 / 5 * lnL / L) * (3 / (Kr * lnL)) ≤
        11 / 100 * ((y : ℝ) / L) := by
      have hlnL0 : 0 < lnL := by linarith
      have e : 11 / 10 * A * y * (1 / L ^ 2 + 44 / 5 * lnL / L) * (3 / (Kr * lnL)) =
          A / Kr * ((y : ℝ) / L) * (33 / 10 / (L * lnL) + 726 / 25) := by
        field_simp
        ring
      have h3 : A / Kr ≤ 1 / 300 := by
        rw [div_le_iff₀ hKr0]
        linarith
      have h4 : 33 / 10 / (L * lnL) + 726 / 25 ≤ 33 / 10 + 726 / 25 := by
        have h5 : 1 ≤ L * lnL := one_le_mul_of_one_le_of_one_le hL1 (by linarith)
        have h6 : (33 / 10 : ℝ) / (L * lnL) ≤ 33 / 10 := div_le_self (by norm_num) h5
        linarith
      have hyL : 0 ≤ (y : ℝ) / L := by positivity
      have h7 : A / Kr * ((y : ℝ) / L) ≤ 1 / 300 * ((y : ℝ) / L) :=
        mul_le_mul_of_nonneg_right h3 hyL
      have h8 : A / Kr * ((y : ℝ) / L) * (33 / 10 / (L * lnL) + 726 / 25) ≤
          1 / 300 * ((y : ℝ) / L) * (33 / 10 + 726 / 25) :=
        mul_le_mul h7 h4 (by positivity) (by positivity)
      rw [e]
      linarith
    have hyL : 0 ≤ (y : ℝ) / L := by positivity
    have hreal : (A' : ℝ) * oddPrimeProd z + Zc ≤ (#T : ℝ) := by linarith
    have hfin : (A' : ℝ) * ((∏ r ∈ S, (r - 2) : ℕ) : ℝ) + Zc * ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) ≤
        (#T : ℝ) * ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) := by
      have h := mul_le_mul_of_nonneg_right hreal hP1pos.le
      rw [oddPrimeProd_eq z] at h
      have e : ((A' : ℝ) * (((∏ r ∈ S, (r - 2) : ℕ) : ℝ) / ((∏ r ∈ S, (r - 1) : ℕ) : ℝ)) + Zc) *
          ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) =
          (A' : ℝ) * ((∏ r ∈ S, (r - 2) : ℕ) : ℝ) + Zc * ((∏ r ∈ S, (r - 1) : ℕ) : ℝ) := by
        field_simp
      rw [← e]
      exact h
    exact_mod_cast hfin
  exact ⟨by omega, N₁, F, S, T, hF, hS, hT, hB, hFS, hFT, hST, hcount⟩


/-- **The three layers for every constant.** For `A ≥ 1` and every large `y` there are an integer
`N₁` and a splitting of odd primes up to `y` into a fixed layer `F` (the primes in `(z, y/4]`, each
with the class of `N₁`), a pigeonhole layer `S` (the odd primes up to `z`) and a mop-up layer `T`
(the primes in `(y/4, y]`) that satisfy the count of `Cap.exists_classes_of_layers` for the rows
below `Q = ⌊A y ln y⌋`. Here `z = ⌊ln y⌋^K - 1` with `K = ⌈300 A⌉ + 1`. -/
theorem eventually_layers_common_integer {A : ℝ} (hA : 1 ≤ A) :
    ∀ᶠ y : ℕ in atTop, 2 ≤ y ∧ ∃ (N₁ : ℕ) (F S T : Finset ℕ),
      (∀ r ∈ F, r.Prime ∧ r ≠ 2) ∧ (∀ r ∈ S, r.Prime ∧ r ≠ 2) ∧ (∀ r ∈ T, r.Prime ∧ r ≠ 2) ∧
      (∀ r ∈ F ∪ S ∪ T, r ≤ y) ∧ Disjoint F S ∧ Disjoint F T ∧ Disjoint S T ∧
      #{q ∈ range ⌊A * y * Real.log y⌋₊ | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
          ∀ r ∈ F, ¬ q ≡ (fun _ : ℕ => N₁) r [MOD r]} * ∏ r ∈ S, (r - 2) +
        #{q ∈ range ⌊A * y * Real.log y⌋₊ | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} * ∏ r ∈ S, (r - 1) ≤
        #T * ∏ r ∈ S, (r - 1) := by
  classical
  have hA0 : 0 < A := by linarith
  -- the exponent of the pigeonhole layer
  set K : ℕ := ⌈300 * A⌉₊ + 1 with hKdef
  have hceil : 0 < ⌈300 * A⌉₊ := Nat.ceil_pos.mpr (by positivity)
  have hK1 : 1 ≤ K := by omega
  have hK2 : 2 ≤ K := by omega
  have hKA : 300 * A ≤ ((K - 1 : ℕ) : ℝ) := by
    have e : K - 1 = ⌈300 * A⌉₊ := by omega
    rw [e]
    exact Nat.le_ceil _
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hlog : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hloglog : Tendsto (fun y : ℕ => Real.log (Real.log (y : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hlog
  have hx1 : Tendsto (fun y : ℕ => A * (y : ℝ) * Real.log y) atTop atTop :=
    (hcast.const_mul_atTop hA0).atTop_mul_atTop₀ hlog
  -- the prime number theorem with `δ = 1/10`, for `x ≥ x₀`
  obtain ⟨x₁, hx₁⟩ := Filter.eventually_atTop.mp
    (eventually_primeCounting_bounds (δ := 1 / 10) (by norm_num))
  set x₀ : ℝ := max x₁ 0 with hx₀def
  have hx₀0 : 0 ≤ x₀ := le_max_right _ _
  have hx₀ : ∀ x : ℝ, x₀ ≤ x →
      (1 - 1 / 10) * (x / Real.log x) ≤ (Nat.primeCounting ⌊x⌋₊ : ℝ) ∧
        (Nat.primeCounting ⌊x⌋₊ : ℝ) ≤ (1 + 1 / 10) * (x / Real.log x) :=
    fun x hx => hx₁ x ((le_max_left _ _).trans hx)
  -- the elementary bound for the product, for `w ≥ w₀`
  obtain ⟨w₀, hw₀⟩ := Filter.eventually_atTop.mp (mertensUpper_elementary (1 / 10) (by norm_num))
  -- `(ln y)^(K+1) ≤ y/20`
  have hgrow : ∀ᶠ y : ℕ in atTop, Real.log (y : ℝ) ^ (K + 1) ≤ (y : ℝ) / 20 := by
    have h := (Real.isLittleO_pow_log_id_atTop (n := K + 1)).def
      (show (0 : ℝ) < 1 / 20 by norm_num)
    filter_upwards [hcast.eventually h] with y hy
    simp only [id, Real.norm_eq_abs] at hy
    rw [(abs_of_nonneg (Nat.cast_nonneg y) : |(y : ℝ)| = y)] at hy
    have := le_abs_self (Real.log (y : ℝ) ^ (K + 1))
    linarith
  filter_upwards [eventually_card_smooth_le K hK1, hgrow, hx1.eventually_ge_atTop x₀,
    hcast.eventually_ge_atTop x₀, hcast.eventually_ge_atTop (8 * x₀ + 8),
    hlog.eventually_ge_atTop ((w₀ : ℝ) + 2), hlog.eventually_ge_atTop (7 * A),
    hlog.eventually_ge_atTop 14, hloglog.eventually_ge_atTop (1 + Real.log (16 * A)),
    hloglog.eventually_ge_atTop 2, eventually_ge_atTop 8]
    with y hsmooth hgrowy hQx₀ hyx₀ hwx₀ hLw₀ hL7A hL14 hLL1 hLL2 hy8
  exact layers_common_integer_core hA hK2 hKA hx₀0 hx₀ hw₀ hsmooth hgrowy hQx₀ hyx₀ hwx₀ hLw₀
    hL7A hL14 hLL1 hLL2 hy8

/-- **Every constant: the depth form.** For every real `A` and every large `y` there are classes
`a r` modulo the odd primes `r ≤ y` such that every odd prime below `⌊A y ln y⌋` lies in one of
them. (`eventually_exists_classes_of_mul_lt_one` is the case `A < e^γ / (2 C₂)`, by a different
cover.) -/
theorem eventually_exists_classes_every_constant (A : ℝ) :
    ∀ᶠ y : ℕ in atTop, ∃ a : ℕ → ℕ, ∀ q : ℕ, q.Prime → q ≠ 2 → q < ⌊A * y * Real.log y⌋₊ →
      ∃ r : ℕ, (r.Prime ∧ r ≠ 2 ∧ r ≤ y) ∧ q ≡ a r [MOD r] := by
  classical
  filter_upwards [eventually_layers_common_integer (le_max_right A 1), eventually_ge_atTop 1]
    with y ⟨_, N₁, F, S, T, hF, hS, hT, hB, hFS, hFT, hST, hcount⟩ hy1
  obtain ⟨a, -, ha⟩ := Cap.exists_classes_of_layers F S T (fun _ => N₁) _ hS hFS hFT hST hcount
  refine ⟨a, fun q hq hq2 hqQ => ?_⟩
  have hle : ⌊A * (y : ℝ) * Real.log y⌋₊ ≤ ⌊max A 1 * (y : ℝ) * Real.log y⌋₊ := by
    apply Nat.floor_le_floor
    have h1 : (0 : ℝ) ≤ y * Real.log y :=
      mul_nonneg (Nat.cast_nonneg y) (Real.log_nonneg (by exact_mod_cast hy1))
    have h2 := mul_le_mul_of_nonneg_right (le_max_left A 1) h1
    linarith
  obtain ⟨r, hr, hqr⟩ := ha q hq hq2 (lt_of_lt_of_le hqQ hle)
  have hr' : r.Prime ∧ r ≠ 2 := by
    rcases Finset.mem_union.mp hr with h | h
    · rcases Finset.mem_union.mp h with h | h
      · exact hF r h
      · exact hS r h
    · exact hT r h
  exact ⟨r, ⟨hr'.1, hr'.2, hB r hr⟩, hqr⟩

/-- **The number behind three layers.** If the layers `F`, `S`, `T` of odd primes up to `y` satisfy
the count of `Cap.exists_even_le_of_layers` for the rows below `Q`, there is an even `N` with
`Q < N ≤ Q + y + primorial y` and no Goldbach summand below `Q`. -/
theorem exists_even_of_layers_count {y Q N₁ : ℕ} {F S T : Finset ℕ} (hy2 : 2 ≤ y)
    (hF : ∀ r ∈ F, r.Prime ∧ r ≠ 2) (hS : ∀ r ∈ S, r.Prime ∧ r ≠ 2)
    (hT : ∀ r ∈ T, r.Prime ∧ r ≠ 2) (hB : ∀ r ∈ F ∪ S ∪ T, r ≤ y)
    (hFS : Disjoint F S) (hFT : Disjoint F T) (hST : Disjoint S T)
    (hcount : #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
          ∀ r ∈ F, ¬ q ≡ (fun _ : ℕ => N₁) r [MOD r]} * ∏ r ∈ S, (r - 2) +
        #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} * ∏ r ∈ S, (r - 1) ≤
        #T * ∏ r ∈ S, (r - 1)) :
    ∃ N, Even N ∧ Q < N ∧ N ≤ Q + y + primorial y ∧ ∀ q < Q, ¬ IsSummand N q := by
  classical
  obtain ⟨N, hNe, hNlo, hNhi, hNq⟩ := Cap.exists_even_le_of_layers F S T (fun _ => N₁) Q y
    hF hS hT hB hy2 hFS hFT hST hcount
  refine ⟨N, hNe, by omega, hNhi.trans ?_, hNq⟩
  -- the modulus is at most the primorial
  have hR : ∀ r ∈ F ∪ S ∪ T, r.Prime ∧ r ≠ 2 := by
    intro r hr
    rcases Finset.mem_union.mp hr with h | h
    · rcases Finset.mem_union.mp h with h | h
      · exact hF r h
      · exact hS r h
    · exact hT r h
  have h2not : 2 ∉ F ∪ S ∪ T := fun h => (hR 2 h).2 rfl
  have hsub : insert 2 (F ∪ S ∪ T) ⊆ (range (y + 1)).filter Nat.Prime := by
    intro r hr
    rw [Finset.mem_filter, Finset.mem_range]
    rcases Finset.mem_insert.mp hr with rfl | h
    · exact ⟨by omega, Nat.prime_two⟩
    · exact ⟨Nat.lt_succ_of_le (hB r h), (hR r h).1⟩
  have hprim : 2 * ∏ r ∈ F ∪ S ∪ T, r ≤ primorial y := by
    calc 2 * ∏ r ∈ F ∪ S ∪ T, r = ∏ r ∈ insert 2 (F ∪ S ∪ T), r :=
          (Finset.prod_insert (f := fun r : ℕ => r) h2not).symm
      _ ≤ ∏ r ∈ (range (y + 1)).filter Nat.Prime, r :=
          Finset.prod_le_prod_of_subset_of_one_le hsub fun r hr _ =>
            (Finset.mem_filter.mp hr).2.one_le
      _ = primorial y := rfl
  omega

/-- **The number behind the cover.** For `A ≥ 1` and every large `y` there is an even `N` with
`Q < N ≤ Q + y + primorial y`, `Q = ⌊A y ln y⌋`, and no Goldbach summand below `Q`. -/
theorem eventually_exists_even_every_constant_nat {A : ℝ} (hA : 1 ≤ A) :
    ∀ᶠ y : ℕ in atTop, ∃ N, Even N ∧ ⌊A * y * Real.log y⌋₊ < N ∧
      N ≤ ⌊A * y * Real.log y⌋₊ + y + primorial y ∧
      ∀ q < ⌊A * y * Real.log y⌋₊, ¬ IsSummand N q := by
  filter_upwards [eventually_layers_common_integer hA] with y
    ⟨hy2, N₁, F, S, T, hF, hS, hT, hB, hFS, hFT, hST, hcount⟩
  exact exists_even_of_layers_count hy2 hF hS hT hB hFS hFT hST hcount

/-- **Every constant.** For every real `A` and all large `X` there is an even `N ≤ X`, larger than
`A ln X ln ln X`, such that no `q < A ln X ln ln X` is a Goldbach summand of `N`: `N - q` is
composite for every prime `q` below `A ln X ln ln X`. So the largest least Goldbach summand
below `X` is not `O(ln X ln ln X)`. -/
theorem eventually_exists_even_le_every_constant (A : ℝ) :
    ∀ᶠ X : ℕ in atTop, ∃ N : ℕ, A * Real.log X * Real.log (Real.log X) < N ∧ N ≤ X ∧ Even N ∧
      ∀ q : ℕ, (q : ℝ) < A * Real.log X * Real.log (Real.log X) → ¬ IsSummand N q := by
  have h0 : 0 ≤ max A 0 := le_max_right _ _
  exact eventually_exists_even_le_of_stage (c := A) (c' := max A 0 + 1) (by linarith)
    (by linarith) (eventually_exists_even_every_constant_nat (by linarith))

/-! ### Beyond every constant: the exponent `K` grows with `y` -/

/-- Mertens' second theorem, the upper half: `∑_{p ≤ w} 1/p ≤ ln ln w + K₀` for some `K₀ ≥ 0` and
all `w ≥ 2` (from `Mertens.exists_bound_B_sub_log_log`). -/
theorem exists_sum_primesLE_inv_le :
    ∃ K₀ : ℝ, 0 ≤ K₀ ∧ ∀ w : ℕ, 2 ≤ w →
      ∑ p ∈ Nat.primesLE w, ((p : ℝ))⁻¹ ≤ Real.log (Real.log w) + K₀ := by
  obtain ⟨K₁, hK₁⟩ := Mertens.exists_bound_B_sub_log_log
  refine ⟨max K₁ 0, le_max_right _ _, fun w hw => ?_⟩
  have h1 : ∑ p ∈ Nat.primesLE w, ((p : ℝ))⁻¹ ≤ Mertens.B w := by
    rw [Mertens.B, Nat.floor_natCast]
    calc ∑ p ∈ Nat.primesLE w, ((p : ℝ))⁻¹ = ∑ p ∈ Nat.primesLE w, Mertens.lamLog p := by
          refine Finset.sum_congr rfl fun p hp => ?_
          have hpp := (Nat.mem_primesLE.mp hp).2
          have h := Mertens.lamLog_prime_pow hpp 0
          simp only [zero_add, pow_one, Nat.cast_zero, div_one] at h
          exact h.symm
      _ ≤ ∑ k ∈ Icc 0 w, Mertens.lamLog k :=
          Finset.sum_le_sum_of_subset_of_nonneg
            (fun p hp => Finset.mem_Icc.mpr ⟨Nat.zero_le _, (Nat.mem_primesLE.mp hp).1⟩)
            (fun k _ _ => Mertens.lamLog_nonneg k)
  have h2 := (abs_le.mp (hK₁ (w : ℝ) (by exact_mod_cast hw))).2
  have h3 : K₁ ≤ max K₁ 0 := le_max_left _ _
  linarith

/-- **Smooth numbers are rare, with the smoothness bound a power of `y`.** Let
`∑_{p ≤ w} 1/p ≤ ln ln w + K₀`. If `ln N ≤ ln y / (14 ln ln y)`, `N ≥ 8`, `y ≤ 2Q` and
`ln ln y ≥ 11 K₀ + 1`, then at most `Q / ln² y` of the integers in `[1, 2Q)` are `N`-smooth.
(Rankin's bound with `σ = 1 - 1/ln N`, where `N^{1-σ} = e`.) -/
theorem card_smooth_le_of_log_le {K₀ : ℝ} (hK₀0 : 0 ≤ K₀)
    (hK₀ : ∀ w : ℕ, 2 ≤ w → ∑ p ∈ Nat.primesLE w, ((p : ℝ))⁻¹ ≤ Real.log (Real.log w) + K₀)
    {N Q y : ℕ} (hy1 : 1 ≤ y) (hQ : y ≤ 2 * Q) (hN : 8 ≤ N)
    (hNL : Real.log N * (14 * Real.log (Real.log y)) ≤ Real.log y)
    (hbig : 11 * K₀ + 1 ≤ Real.log (Real.log y)) :
    (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers N} : ℝ) ≤ Q / Real.log y ^ 2 := by
  classical
  set L := Real.log (y : ℝ) with hLdef
  set lnL := Real.log L with hlnLdef
  set ℓ := Real.log (N : ℝ) with hℓdef
  have hlnL1 : 1 ≤ lnL := by linarith
  have hL0 : 0 ≤ L := Real.log_natCast_nonneg y
  have hLne : L ≠ 0 := by
    intro h
    rw [hlnLdef, h, Real.log_zero] at hlnL1
    linarith
  have hLpos : 0 < L := lt_of_le_of_ne hL0 (Ne.symm hLne)
  have hypos : (0 : ℝ) < y := by exact_mod_cast hy1
  have hN0 : (0 : ℝ) < N := by
    have : 0 < N := by omega
    exact_mod_cast this
  have he : Real.exp 1 < 2.75 := by
    have := Real.exp_one_lt_d9
    linarith
  -- `ℓ = ln N ≥ 2`
  have hℓ2 : 2 ≤ ℓ := by
    have h8 : (8 : ℝ) ≤ N := by exact_mod_cast hN
    have h1 : Real.exp 2 ≤ 8 := by
      have e2 : Real.exp 2 = Real.exp 1 * Real.exp 1 := by
        rw [← Real.exp_add]
        norm_num
      have hpos := Real.exp_pos 1
      rw [e2]
      nlinarith
    exact (Real.le_log_iff_exp_le hN0).mpr (h1.trans h8)
  have hℓpos : 0 < ℓ := by linarith
  -- `ℓ ≤ L` and `14 lnL ≤ L/ℓ`
  have hℓL : ℓ ≤ L := by
    have h1 : ℓ * 1 ≤ ℓ * (14 * lnL) := mul_le_mul_of_nonneg_left (by linarith) hℓpos.le
    linarith
  have hratio : 14 * lnL ≤ L / ℓ := by
    rw [le_div_iff₀ hℓpos]
    linarith
  have hlogℓ : Real.log ℓ ≤ lnL := Real.log_le_log hℓpos hℓL
  -- Rankin's bound with `σ = 1 - 1/ℓ`
  set σ : ℝ := 1 - 1 / ℓ with hσdef
  have hinv : 1 / ℓ ≤ 1 / 2 := div_le_div_of_nonneg_left (by norm_num) (by norm_num) hℓ2
  have hinv0 : 0 ≤ 1 / ℓ := by positivity
  have hσ : 1 / 2 ≤ σ := by
    rw [hσdef]
    linarith
  have hσ1 : σ ≤ 1 := by
    rw [hσdef]
    linarith
  have hS : ∑ p ∈ N.primesBelow, ((p : ℝ))⁻¹ ≤ Real.log ℓ + K₀ := by
    have hsub : N.primesBelow ⊆ Nat.primesLE N := fun p hp =>
      Nat.mem_primesLE.mpr ⟨(Nat.lt_of_mem_primesBelow hp).le, Nat.prime_of_mem_primesBelow hp⟩
    exact (Finset.sum_le_sum_of_subset_of_nonneg hsub fun p _ _ => by positivity).trans
      (hK₀ N (by omega))
  have h := Cap.card_smooth_le_exp_of_sum N (2 * Q) hσ hσ1 hS
  have hNpow : (N : ℝ) ^ (1 - σ) = Real.exp 1 := by
    have e : (1 - σ) = 1 / ℓ := by
      rw [hσdef]
      ring
    rw [e, Real.rpow_def_of_pos hN0, ← hℓdef, mul_one_div_cancel hℓpos.ne']
  have hQpos : (0 : ℝ) < ((2 * Q : ℕ) : ℝ) := by
    have : 0 < 2 * Q := by omega
    exact_mod_cast this
  have hX : ((2 * Q : ℕ) : ℝ) ^ σ ≤ ((2 * Q : ℕ) : ℝ) * Real.exp (-(L / ℓ)) := by
    have e : σ = 1 + (-(1 / ℓ)) := by
      rw [hσdef]
      ring
    rw [e, Real.rpow_add hQpos, Real.rpow_one]
    refine mul_le_mul_of_nonneg_left ?_ hQpos.le
    have hyQ : (y : ℝ) ≤ ((2 * Q : ℕ) : ℝ) := by exact_mod_cast hQ
    calc ((2 * Q : ℕ) : ℝ) ^ (-(1 / ℓ)) ≤ (y : ℝ) ^ (-(1 / ℓ)) :=
          Real.rpow_le_rpow_of_nonpos hypos hyQ (by linarith)
      _ = Real.exp (-(L / ℓ)) := by
          rw [Real.rpow_def_of_pos hypos]
          congr 1
          rw [hLdef]
          ring
  -- the exponent
  have hsum0 : 0 ≤ lnL + K₀ := by linarith
  have hexp : -(L / ℓ) + 4 * (Real.exp 1 * (Real.log ℓ + K₀)) ≤
      -(Real.log 2 + 2 * lnL) := by
    have hlog2 : Real.log 2 ≤ 1 := by
      have := Real.log_le_sub_one_of_pos (show (0 : ℝ) < 2 by norm_num)
      linarith
    have h1 : Real.exp 1 * (Real.log ℓ + K₀) ≤ Real.exp 1 * (lnL + K₀) :=
      mul_le_mul_of_nonneg_left (by linarith) (Real.exp_pos 1).le
    have h2 : Real.exp 1 * (lnL + K₀) ≤ 2.75 * (lnL + K₀) :=
      mul_le_mul_of_nonneg_right he.le hsum0
    linarith
  have hfin : Real.exp (-(Real.log 2 + 2 * lnL)) = 1 / (2 * L ^ 2) := by
    have e : Real.exp (2 * lnL) = L ^ 2 := by
      rw [show (2 : ℝ) * lnL = lnL + lnL by ring, Real.exp_add, hlnLdef, Real.exp_log hLpos]
      ring
    rw [Real.exp_neg, Real.exp_add, Real.exp_log (by norm_num : (0 : ℝ) < 2), e, one_div]
  calc (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers N} : ℝ)
      ≤ ((2 * Q : ℕ) : ℝ) ^ σ * Real.exp (4 * ((N : ℝ) ^ (1 - σ) * (Real.log ℓ + K₀))) := h
    _ ≤ (((2 * Q : ℕ) : ℝ) * Real.exp (-(L / ℓ))) *
          Real.exp (4 * (Real.exp 1 * (Real.log ℓ + K₀))) := by
        rw [hNpow]
        exact mul_le_mul_of_nonneg_right hX (Real.exp_pos _).le
    _ = ((2 * Q : ℕ) : ℝ) * Real.exp (-(L / ℓ) + 4 * (Real.exp 1 * (Real.log ℓ + K₀))) := by
        rw [mul_assoc, ← Real.exp_add]
    _ ≤ ((2 * Q : ℕ) : ℝ) * Real.exp (-(Real.log 2 + 2 * lnL)) :=
        mul_le_mul_of_nonneg_left (Real.exp_le_exp.mpr hexp) hQpos.le
    _ = Q / L ^ 2 := by
        rw [hfin]
        push_cast
        field_simp

/-- The exponent of the pigeonhole layer when it grows with `y`: `⌊ln y / (14 (ln ln y)²)⌋`. -/
noncomputable def logK (y : ℕ) : ℕ := ⌊Real.log y / (14 * Real.log (Real.log y) ^ 2)⌋₊

/-- The factor in front of `y ln y` that the three layers reach with the exponent `logK y`. -/
noncomputable def logA (y : ℕ) : ℝ := ((logK y - 1 : ℕ) : ℝ) / 300

/-- `(ln ln y)² ≤ ln y / 4214` for all large `y`. -/
theorem eventually_sq_log_log_le :
    ∀ᶠ y : ℕ in atTop, 4214 * Real.log (Real.log (y : ℝ)) ^ 2 ≤ Real.log (y : ℝ) := by
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hlog : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have h := (Real.isLittleO_pow_log_id_atTop (n := 2)).def (show (0 : ℝ) < 1 / 4214 by norm_num)
  filter_upwards [hlog.eventually h, hlog.eventually_ge_atTop 0] with y hy hL0
  simp only [id, Real.norm_eq_abs] at hy
  rw [(abs_of_nonneg hL0 : |Real.log (y : ℝ)| = Real.log (y : ℝ))] at hy
  have := le_abs_self (Real.log (Real.log (y : ℝ)) ^ 2)
  linarith

/-- The size of `logA`: for all large `y`,
`ln y / (9000 (ln ln y)²) ≤ logA y ≤ ln y / 4200`. -/
theorem eventually_logA_bounds :
    ∀ᶠ y : ℕ in atTop, Real.log y / (9000 * Real.log (Real.log y) ^ 2) ≤ logA y ∧
      logA y ≤ Real.log y / 4200 := by
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hlog : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hloglog : Tendsto (fun y : ℕ => Real.log (Real.log (y : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hlog
  filter_upwards [eventually_sq_log_log_le, hlog.eventually_ge_atTop 14,
    hloglog.eventually_ge_atTop 2] with y hsqy hL14 hLL2
  set L := Real.log (y : ℝ) with hLdef
  set lnL := Real.log L with hlnLdef
  have hLpos : 0 < L := by linarith
  have hsq4 : 4 ≤ lnL ^ 2 := by nlinarith
  have hden : 0 < 14 * lnL ^ 2 := by positivity
  have hK301 : 301 ≤ logK y := by
    rw [logK]
    apply Nat.le_floor
    rw [le_div_iff₀ hden]
    push_cast
    linarith
  have hKr : ((logK y - 1 : ℕ) : ℝ) = (logK y : ℝ) - 1 := by
    rw [Nat.cast_sub (by omega)]
    simp
  have hKle : (logK y : ℝ) ≤ L / (14 * lnL ^ 2) := Nat.floor_le (by positivity)
  have hKgt : L / (14 * lnL ^ 2) < (logK y : ℝ) + 1 := Nat.lt_floor_add_one _
  constructor
  · rw [logA, hKr, le_div_iff₀ (by norm_num : (0 : ℝ) < 300)]
    have e1 : L / (9000 * lnL ^ 2) * 300 = L / (30 * lnL ^ 2) := by
      field_simp
      ring
    rw [e1]
    -- `L/(14 lnL²) - L/(30 lnL²) ≥ 2`
    have h1 : L / (14 * lnL ^ 2) - L / (30 * lnL ^ 2) = 4 * L / (105 * lnL ^ 2) := by
      field_simp
      ring
    have h2 : 2 ≤ 4 * L / (105 * lnL ^ 2) := by
      rw [le_div_iff₀ (by positivity)]
      linarith
    linarith
  · rw [logA, hKr]
    have h1 : L / (14 * lnL ^ 2) ≤ L / 14 := by
      apply div_le_div_of_nonneg_left hLpos.le (by norm_num)
      linarith
    linarith

set_option maxHeartbeats 800000 in
/-- **The three layers with a growing exponent.** For every large `y` the count of
`Cap.exists_classes_of_layers` holds for the rows below `⌊logA y · y ln y⌋`, with the pigeonhole
layer the odd primes up to `⌊ln y⌋^K - 1`, `K = logK y = ⌊ln y / (14 (ln ln y)²)⌋`: a power of `y`
with exponent about `1 / (14 ln ln y)`. -/
theorem eventually_layers_log :
    ∀ᶠ y : ℕ in atTop, 2 ≤ y ∧ ∃ (N₁ : ℕ) (F S T : Finset ℕ),
      (∀ r ∈ F, r.Prime ∧ r ≠ 2) ∧ (∀ r ∈ S, r.Prime ∧ r ≠ 2) ∧ (∀ r ∈ T, r.Prime ∧ r ≠ 2) ∧
      (∀ r ∈ F ∪ S ∪ T, r ≤ y) ∧ Disjoint F S ∧ Disjoint F T ∧ Disjoint S T ∧
      #{q ∈ range ⌊logA y * y * Real.log y⌋₊ | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧
          ∀ r ∈ F, ¬ q ≡ (fun _ : ℕ => N₁) r [MOD r]} * ∏ r ∈ S, (r - 2) +
        #{q ∈ range ⌊logA y * y * Real.log y⌋₊ | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} *
          ∏ r ∈ S, (r - 1) ≤
        #T * ∏ r ∈ S, (r - 1) := by
  classical
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hlog : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hloglog : Tendsto (fun y : ℕ => Real.log (Real.log (y : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hlog
  obtain ⟨x₁, hx₁⟩ := Filter.eventually_atTop.mp
    (eventually_primeCounting_bounds (δ := 1 / 10) (by norm_num))
  set x₀ : ℝ := max x₁ 0 with hx₀def
  have hx₀0 : 0 ≤ x₀ := le_max_right _ _
  have hx₀ : ∀ x : ℝ, x₀ ≤ x →
      (1 - 1 / 10) * (x / Real.log x) ≤ (Nat.primeCounting ⌊x⌋₊ : ℝ) ∧
        (Nat.primeCounting ⌊x⌋₊ : ℝ) ≤ (1 + 1 / 10) * (x / Real.log x) :=
    fun x hx => hx₁ x ((le_max_left _ _).trans hx)
  obtain ⟨w₀, hw₀⟩ := Filter.eventually_atTop.mp (mertensUpper_elementary (1 / 10) (by norm_num))
  obtain ⟨K₀, hK₀0, hK₀⟩ := exists_sum_primesLE_inv_le
  filter_upwards [eventually_sq_log_log_le, eventually_logA_bounds, hcast.eventually_ge_atTop x₀,
    hcast.eventually_ge_atTop (8 * x₀ + 8), hlog.eventually_ge_atTop ((w₀ : ℝ) + 2),
    hlog.eventually_ge_atTop 14, hloglog.eventually_ge_atTop 2,
    hloglog.eventually_ge_atTop (11 * K₀ + 1), eventually_ge_atTop 8]
    with y hsqy hAb hyx₀ hwx₀ hLw₀ hL14 hLL2 hLLK hy8
  set L := Real.log (y : ℝ) with hLdef
  set lnL := Real.log L with hlnLdef
  set K := logK y with hKdef
  set A := logA y with hAdef
  have hLpos : 0 < L := by linarith
  have hy8r : (8 : ℝ) ≤ y := by exact_mod_cast hy8
  have hypos : (0 : ℝ) < y := by linarith
  have hsq4 : 4 ≤ lnL ^ 2 := by nlinarith
  have hlnsq : lnL ≤ lnL ^ 2 := by nlinarith
  have hden : 0 < 14 * lnL ^ 2 := by positivity
  -- `K ≥ 301` and `K · 14 (ln ln y)² ≤ ln y`
  have hK301 : 301 ≤ K := by
    rw [hKdef, logK]
    apply Nat.le_floor
    rw [le_div_iff₀ hden]
    push_cast
    linarith
  have hK2 : 2 ≤ K := by omega
  have hKle : (K : ℝ) * (14 * lnL ^ 2) ≤ L := by
    have h : (K : ℝ) ≤ L / (14 * lnL ^ 2) := Nat.floor_le (by positivity)
    rwa [le_div_iff₀ hden] at h
  have hK0 : (0 : ℝ) ≤ K := Nat.cast_nonneg K
  have hKlnL : (K : ℝ) * lnL * 14 ≤ L := by
    have h1 : (K : ℝ) * 14 * lnL ≤ (K : ℝ) * 14 * lnL ^ 2 :=
      mul_le_mul_of_nonneg_left hlnsq (by positivity)
    linarith
  have hKr : ((K - 1 : ℕ) : ℝ) = (K : ℝ) - 1 := by
    rw [Nat.cast_sub (by omega)]
    simp
  -- `A = (K - 1)/300`
  have hAeq : 300 * A = ((K - 1 : ℕ) : ℝ) := by
    rw [hAdef, logA, ← hKdef]
    field_simp
  have hA1 : 1 ≤ A := by
    have h301 : (301 : ℝ) ≤ K := by exact_mod_cast hK301
    linarith
  have hAle : A ≤ L / 4200 := hAb.2
  have hL7A : 7 * A ≤ L := by linarith
  have hLL1 : 1 + Real.log (16 * A) ≤ lnL := by
    have h16 : 16 * A ≤ L / 3 := by linarith
    have h1 : Real.log (16 * A) ≤ Real.log (L / 3) := Real.log_le_log (by linarith) h16
    have h2 : Real.log (L / 3) = lnL - Real.log 3 := Real.log_div hLpos.ne' (by norm_num)
    have h3 : 1 ≤ Real.log 3 := by
      rw [Real.le_log_iff_exp_le (by norm_num)]
      have := Real.exp_one_lt_d9
      linarith
    linarith
  have hQx₀ : x₀ ≤ A * (y : ℝ) * L := by
    have h1 : 1 ≤ A * L := by
      have := mul_le_mul hA1 (by linarith : (1 : ℝ) ≤ L) (by norm_num) (by linarith)
      linarith
    have h2 : (y : ℝ) * 1 ≤ y * (A * L) := mul_le_mul_of_nonneg_left h1 hypos.le
    linarith
  -- `(ln y)^(K+1) ≤ y/20`
  have hgrowy : L ^ (K + 1) ≤ (y : ℝ) / 20 := by
    have h1 : (((K + 1 : ℕ) : ℝ)) * lnL ≤ L - 3 := by
      push_cast
      linarith
    have h2 : L ^ (K + 1) = Real.exp ((((K + 1 : ℕ) : ℝ)) * lnL) := by
      rw [Real.exp_natCast_mul, hlnLdef, Real.exp_log hLpos]
    have he3 : (20 : ℝ) ≤ Real.exp 3 := by
      have e3 : Real.exp 3 = Real.exp 1 * Real.exp 1 * Real.exp 1 := by
        rw [← Real.exp_add, ← Real.exp_add]
        norm_num
      have h := Real.exp_one_gt_d9
      have ha2 : 7.38 ≤ Real.exp 1 * Real.exp 1 := by nlinarith
      rw [e3]
      nlinarith
    rw [h2]
    calc Real.exp ((((K + 1 : ℕ) : ℝ)) * lnL) ≤ Real.exp (L - 3) := Real.exp_le_exp.mpr h1
      _ = (y : ℝ) / Real.exp 3 := by
          rw [Real.exp_sub, hLdef, Real.exp_log hypos]
      _ ≤ (y : ℝ) / 20 := div_le_div_of_nonneg_left hypos.le (by norm_num) he3
  -- the smooth numbers
  have hm2 : 2 ≤ ⌊L⌋₊ := Nat.le_floor (by push_cast; linarith)
  have hmL : ((⌊L⌋₊ : ℕ) : ℝ) ≤ L := Nat.floor_le hLpos.le
  have hm0 : (0 : ℝ) < ((⌊L⌋₊ : ℕ) : ℝ) := by
    have : 0 < ⌊L⌋₊ := by omega
    exact_mod_cast this
  have hsmooth : ∀ Q : ℕ, y ≤ 2 * Q →
      (#{n ∈ Ico 1 (2 * Q) | n ∈ Nat.smoothNumbers (⌊L⌋₊ ^ K)} : ℝ) ≤ Q / L ^ 2 := by
    intro Q hQ
    refine card_smooth_le_of_log_le hK₀0 hK₀ (by omega) hQ ?_ ?_ hLLK
    · calc 8 = 2 ^ 3 := by norm_num
        _ ≤ ⌊L⌋₊ ^ 3 := Nat.pow_le_pow_left hm2 3
        _ ≤ ⌊L⌋₊ ^ K := Nat.pow_le_pow_right (by omega) (by omega)
    · rw [Nat.cast_pow, Real.log_pow]
      have hlogm : Real.log ((⌊L⌋₊ : ℕ) : ℝ) ≤ lnL := Real.log_le_log hm0 hmL
      have hlogm0 : 0 ≤ Real.log ((⌊L⌋₊ : ℕ) : ℝ) :=
        Real.log_nonneg (by exact_mod_cast (by omega : 1 ≤ ⌊L⌋₊))
      have h1 : (K : ℝ) * Real.log ((⌊L⌋₊ : ℕ) : ℝ) * (14 * lnL) ≤ (K : ℝ) * lnL * (14 * lnL) :=
        mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hlogm hK0) (by positivity)
      have e : (K : ℝ) * lnL * (14 * lnL) = (K : ℝ) * (14 * lnL ^ 2) := by ring
      linarith
  exact layers_common_integer_core hA1 hK2 hAeq.le hx₀0 hx₀ hw₀ hsmooth hgrowy hQx₀ hyx₀ hwx₀ hLw₀
    hL7A hL14 hLL1 hLL2 hy8

/-- **The depth form with its order.** For every large `y` there are classes `a r` modulo the odd
primes `r ≤ y` such that every odd prime below `y ln² y / (9000 (ln ln y)²)` lies in one of them:
the cover depth of the odd primes up to `y` is at least `y ln² y / (9000 (ln ln y)²)`. -/
theorem eventually_exists_classes_log :
    ∀ᶠ y : ℕ in atTop, ∃ a : ℕ → ℕ, ∀ q : ℕ, q.Prime → q ≠ 2 →
      q < ⌊(y : ℝ) * Real.log y ^ 2 / (9000 * Real.log (Real.log y) ^ 2)⌋₊ →
      ∃ r : ℕ, (r.Prime ∧ r ≠ 2 ∧ r ≤ y) ∧ q ≡ a r [MOD r] := by
  classical
  filter_upwards [eventually_layers_log, eventually_logA_bounds, eventually_ge_atTop 1]
    with y ⟨_, N₁, F, S, T, hF, hS, hT, hB, hFS, hFT, hST, hcount⟩ hAb hy1
  obtain ⟨a, -, ha⟩ := Cap.exists_classes_of_layers F S T (fun _ => N₁) _ hS hFS hFT hST hcount
  refine ⟨a, fun q hq hq2 hqQ => ?_⟩
  have hle : ⌊(y : ℝ) * Real.log y ^ 2 / (9000 * Real.log (Real.log y) ^ 2)⌋₊ ≤
      ⌊logA y * (y : ℝ) * Real.log y⌋₊ := by
    apply Nat.floor_le_floor
    have h1 : (0 : ℝ) ≤ y * Real.log y :=
      mul_nonneg (Nat.cast_nonneg y) (Real.log_nonneg (by exact_mod_cast hy1))
    have h2 := mul_le_mul_of_nonneg_right hAb.1 h1
    have e : Real.log (y : ℝ) / (9000 * Real.log (Real.log y) ^ 2) * ((y : ℝ) * Real.log y) =
        (y : ℝ) * Real.log y ^ 2 / (9000 * Real.log (Real.log y) ^ 2) := by ring
    linarith
  obtain ⟨r, hr, hqr⟩ := ha q hq hq2 (lt_of_lt_of_le hqQ hle)
  have hr' : r.Prime ∧ r ≠ 2 := by
    rcases Finset.mem_union.mp hr with h | h
    · rcases Finset.mem_union.mp h with h | h
      · exact hF r h
      · exact hS r h
    · exact hT r h
  exact ⟨r, ⟨hr'.1, hr'.2, hB r hr⟩, hqr⟩

/-- The number behind that cover: for every large `y` there is an even `N` with
`Q < N ≤ Q + y + primorial y`, `Q = ⌊logA y · y ln y⌋`, and no Goldbach summand below `Q`. -/
theorem eventually_exists_even_log_nat :
    ∀ᶠ y : ℕ in atTop, ∃ N, Even N ∧ ⌊logA y * y * Real.log y⌋₊ < N ∧
      N ≤ ⌊logA y * y * Real.log y⌋₊ + y + primorial y ∧
      ∀ q < ⌊logA y * y * Real.log y⌋₊, ¬ IsSummand N q := by
  filter_upwards [eventually_layers_log] with y
    ⟨hy2, N₁, F, S, T, hF, hS, hT, hB, hFS, hFT, hST, hcount⟩
  exact exists_even_of_layers_count hy2 hF hS hT hB hFS hFT hST hcount

/-- `1 + u⁴/256 ≤ e^u` for `u ≥ 0`. -/
theorem one_add_pow_four_le_exp {u : ℝ} (hu : 0 ≤ u) : 1 + u ^ 4 / 256 ≤ Real.exp u := by
  have h := Real.add_one_le_exp (u / 4)
  have h0 : 0 ≤ u / 4 + 1 := by positivity
  have h4 : (u / 4 + 1) ^ 4 ≤ Real.exp (u / 4) ^ 4 := pow_le_pow_left₀ h0 h 4
  have e : Real.exp (u / 4) ^ 4 = Real.exp u := by
    rw [← Real.exp_natCast_mul]
    congr 1
    push_cast
    ring
  rw [e] at h4
  have e2 : (u / 4 + 1) ^ 4 = 1 + u ^ 4 / 256 + (u + 3 * u ^ 2 / 8 + u ^ 3 / 16) := by ring
  have h5 : 0 ≤ u + 3 * u ^ 2 / 8 + u ^ 3 / 16 := by positivity
  linarith

set_option maxHeartbeats 800000 in
/-- **The order of the lower bound.** For all large `X` there is an even `N ≤ X` such that no
`q < ln X · (ln ln X)² / (150000 (ln ln ln X)²)` is a Goldbach summand of `N`: `N - q` is composite
for every prime `q` below that bound. So the largest least Goldbach summand below `X` is at least
of the order `ln X (ln ln X)² / (ln ln ln X)²`. (Take `y = ⌊ln X / 2⌋` in
`eventually_exists_even_log_nat`.) -/
theorem eventually_exists_even_le_log :
    ∀ᶠ X : ℕ in atTop, ∃ N : ℕ,
      Real.log X * Real.log (Real.log X) ^ 2 /
          (150000 * Real.log (Real.log (Real.log X)) ^ 2) < N ∧
      N ≤ X ∧ Even N ∧
      ∀ q : ℕ, (q : ℝ) < Real.log X * Real.log (Real.log X) ^ 2 /
          (150000 * Real.log (Real.log (Real.log X)) ^ 2) → ¬ IsSummand N q := by
  have hcast : Tendsto (fun X : ℕ => (X : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hL : Tendsto (fun X : ℕ => Real.log (X : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hLL : Tendsto (fun X : ℕ => Real.log (Real.log (X : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL
  have hy : Tendsto (fun X : ℕ => ⌊Real.log (X : ℝ) / 2⌋₊) atTop atTop :=
    tendsto_nat_floor_atTop.comp (hL.atTop_div_const (by norm_num))
  filter_upwards [hy.eventually eventually_exists_even_log_nat,
    hy.eventually eventually_logA_bounds,
    hy.eventually (eventually_primorial_le (show (0 : ℝ) < 1 / 4 by norm_num)),
    hL.eventually_ge_atTop 3600000, hLL.eventually_ge_atTop 6, eventually_ge_atTop 1]
    with X hst hAb hpr hL1 hLL6 hX1
  set L := Real.log (X : ℝ) with hLdef
  set LL := Real.log L with hLLdef
  set LLL := Real.log LL with hLLLdef
  set y := ⌊L / 2⌋₊ with hydef
  have hLpos : 0 < L := by linarith
  have hXpos : (0 : ℝ) < X := by exact_mod_cast hX1
  -- `L/4 ≤ y ≤ L/2`
  have hyle : (y : ℝ) ≤ L / 2 := Nat.floor_le (by positivity)
  have hyge : L / 4 ≤ (y : ℝ) := by
    have := Nat.sub_one_lt_floor (L / 2)
    linarith
  have hypos : (0 : ℝ) < y := by linarith
  -- `ln y` between `LL/2` and `LL`
  have hly_le : Real.log (y : ℝ) ≤ LL := Real.log_le_log hypos (by linarith)
  have hly_ge : LL / 2 ≤ Real.log (y : ℝ) := by
    have h1 : Real.log (L / 4) ≤ Real.log (y : ℝ) := Real.log_le_log (by positivity) hyge
    have h2 : Real.log (L / 4) = LL - Real.log 4 := Real.log_div hLpos.ne' (by norm_num)
    have h3 : Real.log 4 ≤ 3 := by
      have := Real.log_le_sub_one_of_pos (show (0 : ℝ) < 4 by norm_num)
      linarith
    linarith
  have hly3 : 3 ≤ Real.log (y : ℝ) := by linarith
  -- `0 < ln ln y ≤ LLL ≤ LL`
  have hlly_le : Real.log (Real.log (y : ℝ)) ≤ LLL := Real.log_le_log (by linarith) hly_le
  have hlly_pos : 0 < Real.log (Real.log (y : ℝ)) := Real.log_pos (by linarith)
  have hLLL_pos : 0 < LLL := lt_of_lt_of_le hlly_pos hlly_le
  have hLLL_le : LLL ≤ LL := by
    have := Real.log_le_sub_one_of_pos (show (0 : ℝ) < LL by linarith)
    linarith
  have hLL_le : LL ≤ L := by
    have := Real.log_le_sub_one_of_pos hLpos
    linarith
  obtain ⟨N, hNe, hNlo, hNhi, hNq⟩ := hst
  obtain ⟨hA1, hA2⟩ := hAb
  set ly := Real.log (y : ℝ) with hlydef
  set lly := Real.log ly with hllydef
  set R := logA y * (y : ℝ) * ly with hRdef
  have hyly : 0 ≤ (y : ℝ) * ly := mul_nonneg hypos.le (by linarith)
  have e3 : logA y * ((y : ℝ) * ly) = R := by
    rw [hRdef]
    ring
  -- the lower bound for `R`
  have hRge : L * LL ^ 2 / (144000 * LLL ^ 2) ≤ R := by
    have h1 : ly / (9000 * lly ^ 2) * ((y : ℝ) * ly) ≤ logA y * ((y : ℝ) * ly) :=
      mul_le_mul_of_nonneg_right hA1 hyly
    have h2 : L / 4 * (LL / 2) ^ 2 ≤ (y : ℝ) * ly ^ 2 :=
      mul_le_mul hyge (pow_le_pow_left₀ (by linarith) hly_ge 2) (by positivity) hypos.le
    have h3 : lly ^ 2 ≤ LLL ^ 2 := pow_le_pow_left₀ hlly_pos.le hlly_le 2
    have hllysq : 0 < lly ^ 2 := by positivity
    have h4 : L / 4 * (LL / 2) ^ 2 / (9000 * LLL ^ 2) ≤ (y : ℝ) * ly ^ 2 / (9000 * lly ^ 2) :=
      div_le_div₀ (by positivity) h2 (by positivity) (by linarith)
    have e1 : L * LL ^ 2 / (144000 * LLL ^ 2) = L / 4 * (LL / 2) ^ 2 / (9000 * LLL ^ 2) := by
      field_simp
      ring
    have e2 : ly / (9000 * lly ^ 2) * ((y : ℝ) * ly) = (y : ℝ) * ly ^ 2 / (9000 * lly ^ 2) := by
      ring
    linarith
  have hR0 : 0 ≤ R := le_trans (by positivity) hRge
  -- the threshold of the statement is at most `R - 1`
  have hτ : L * LL ^ 2 / (150000 * LLL ^ 2) + 1 ≤ R := by
    have e : L * LL ^ 2 / (144000 * LLL ^ 2) - L * LL ^ 2 / (150000 * LLL ^ 2) =
        L * LL ^ 2 / (3600000 * LLL ^ 2) := by
      field_simp
      ring
    have h1 : 1 ≤ L * LL ^ 2 / (3600000 * LLL ^ 2) := by
      rw [le_div_iff₀ (by positivity), one_mul]
      have h2 : LLL ^ 2 ≤ LL ^ 2 := pow_le_pow_left₀ hLLL_pos.le hLLL_le 2
      have h3 : 3600000 * LLL ^ 2 ≤ L * LLL ^ 2 :=
        mul_le_mul_of_nonneg_right hL1 (by positivity)
      have h4 : L * LLL ^ 2 ≤ L * LL ^ 2 := mul_le_mul_of_nonneg_left h2 hLpos.le
      linarith
    linarith
  -- the window ends below `X`
  have hRle : R ≤ L ^ 3 := by
    have h1 : logA y * ((y : ℝ) * ly) ≤ ly / 4200 * ((y : ℝ) * ly) :=
      mul_le_mul_of_nonneg_right hA2 hyly
    have hlyL : ly ≤ L := hly_le.trans hLL_le
    have h2 : ly ^ 2 ≤ L ^ 2 := pow_le_pow_left₀ (by linarith) hlyL 2
    have h3 : (y : ℝ) * ly ^ 2 ≤ L * L ^ 2 :=
      mul_le_mul (by linarith) h2 (by positivity) hLpos.le
    have h4 : ly / 4200 * ((y : ℝ) * ly) = (y : ℝ) * ly ^ 2 / 4200 := by ring
    have h5 : (y : ℝ) * ly ^ 2 / 4200 ≤ (y : ℝ) * ly ^ 2 :=
      div_le_self (by positivity) (by norm_num)
    have e : L * L ^ 2 = L ^ 3 := by ring
    linarith
  have hexp : Real.exp (5 / 8 * L) + (L ^ 3 + L) ≤ (X : ℝ) := by
    have hu : 0 ≤ 3 / 8 * L := by positivity
    have h1 := one_add_pow_four_le_exp hu
    have h3 : L ^ 3 + L ≤ (3 / 8 * L) ^ 4 / 256 := by
      have e : (3 / 8 * L) ^ 4 / 256 = 81 / 1048576 * L * L ^ 3 := by ring
      have hL3 : 0 ≤ L ^ 3 := by positivity
      have h5 : 2 * L ^ 3 ≤ 81 / 1048576 * L * L ^ 3 :=
        mul_le_mul_of_nonneg_right (by linarith) hL3
      have h6 : L ≤ L ^ 3 := le_self_pow₀ (by linarith) (by norm_num)
      linarith
    have h4 : (1 : ℝ) ≤ Real.exp (5 / 8 * L) := Real.one_le_exp (by positivity)
    have hX : (X : ℝ) = Real.exp (5 / 8 * L) * Real.exp (3 / 8 * L) := by
      rw [← Real.exp_add, hLdef]
      have : 5 / 8 * Real.log (X : ℝ) + 3 / 8 * Real.log (X : ℝ) = Real.log (X : ℝ) := by ring
      rw [this, Real.exp_log hXpos]
    rw [hX]
    exact add_le_mul_of_one_add_le h4 h1 h3 (by positivity)
  have hprimle : (primorial y : ℝ) ≤ Real.exp (5 / 8 * L) := by
    refine hpr.trans (Real.exp_le_exp.mpr ?_)
    linarith
  have hfloor : (⌊R⌋₊ : ℝ) ≤ R := Nat.floor_le hR0
  refine ⟨N, ?_, ?_, hNe, fun q hq => hNq q ?_⟩
  · have h : R < (⌊R⌋₊ : ℝ) + 1 := Nat.lt_floor_add_one R
    have h2 : ((⌊R⌋₊ + 1 : ℕ) : ℝ) ≤ N := by exact_mod_cast hNlo
    push_cast at h2
    linarith
  · have h1 : (N : ℝ) ≤ ⌊R⌋₊ + y + primorial y := by exact_mod_cast hNhi
    have h : (N : ℝ) ≤ X := by linarith
    exact_mod_cast h
  · have h1 : (q : ℝ) + 1 ≤ R := by linarith
    have h2 : q + 1 ≤ ⌊R⌋₊ := Nat.le_floor (by exact_mod_cast h1)
    omega

end GoldbachGaps
