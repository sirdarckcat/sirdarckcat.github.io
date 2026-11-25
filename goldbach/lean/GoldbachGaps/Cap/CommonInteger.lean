import GoldbachGaps.Cap.Layers

/-!
# A fixed layer on one common integer: the finite counts

The fixed layer of `GoldbachGaps/Cap/Layers.lean` with the classes of one integer `N₁`: every modulus
`r` of the layer takes the class `N₁ mod r`. A row `q ≤ N₁` is then left by the layer exactly when
`N₁ - q` is divisible by none of its moduli.

* `exists_common_integer`: **averaging over the common integer.** For rows `P` below `Q` and any set
  `F` of moduli there is an `N₁` in `[Q, 2Q)` that leaves at most the share
  `#{1 ≤ n < 2Q : no r ∈ F divides n} / Q` of the rows. The proof is a double count: for a fixed
  row `q` the numbers `N₁ - q` are `Q` different integers in `[1, 2Q)`. So what the layer leaves is
  bounded by a count of integers, and no count of pairs of primes is needed.
* `card_no_factor_le`: for the layer of all primes in `(z, w]` and `X ≤ w²`, an integer in
  `[1, X)` with no prime factor in the layer is `z`-smooth or of the form `A · p'` with `p' > w`
  prime; their number is at most the number of `z`-smooth integers below `X` plus
  `∑_{A ≤ X/w} π(X/A)`.
* `card_smooth_le`, `prod_primesBelow_le_exp`, `card_smooth_le_exp`: Rankin's bound for smooth
  numbers. For `1/2 ≤ σ ≤ 1` the number of `N`-smooth integers in `[1, X)` is at most
  `X^σ · ∏_{p < N} (1 - p^{-σ})⁻¹ ≤ X^σ · exp (4 N^{1-σ} (1 + ln N))`; with a bound `S` for
  `∑_{p < N} 1/p` in place of the harmonic sum, `X^σ · exp (4 N^{1-σ} S)`
  (`card_smooth_le_exp_of_sum`).
-/

namespace GoldbachGaps.Cap

open Finset

/-- **Averaging over the common integer.** Let the rows `P` lie below `Q` and let `F` be any set of
moduli. Some `N₁` in `[Q, 2Q)` has: the rows that are in the class of `N₁` for no modulus of `F`
number at most `#P` times the share of the integers in `[1, 2Q)` that no modulus of `F` divides. -/
theorem exists_common_integer (F P : Finset ℕ) {Q : ℕ} (hQ : 0 < Q) (hP : ∀ q ∈ P, q < Q) :
    ∃ N₁, Q ≤ N₁ ∧ N₁ < 2 * Q ∧
      #{q ∈ P | ∀ r ∈ F, ¬ q ≡ N₁ [MOD r]} * Q ≤
        #P * #{n ∈ Ico 1 (2 * Q) | ∀ r ∈ F, ¬ r ∣ n} := by
  classical
  set G := #{n ∈ Ico 1 (2 * Q) | ∀ r ∈ F, ¬ r ∣ n} with hG
  -- for a fixed row, the common integers that leave it inject into the integers counted by `G`
  have hrow : ∀ q ∈ P, #{N₁ ∈ Ico Q (2 * Q) | ∀ r ∈ F, ¬ q ≡ N₁ [MOD r]} ≤ G := by
    intro q hq
    have hqQ := hP q hq
    refine Finset.card_le_card_of_injOn (fun N₁ => N₁ - q) ?_ ?_
    · intro N₁ hN
      simp only [Finset.coe_filter, Set.mem_ofPred_eq, Finset.mem_Ico] at hN ⊢
      obtain ⟨⟨h1, h2⟩, h3⟩ := hN
      refine ⟨⟨by omega, by omega⟩, fun r hr hdvd => h3 r hr ?_⟩
      exact (Nat.modEq_iff_dvd' (by omega : q ≤ N₁)).mpr hdvd
    · intro a ha b hb hab
      simp only [Finset.coe_filter, Set.mem_ofPred_eq, Finset.mem_Ico] at ha hb
      have hab' : a - q = b - q := hab
      omega
  -- double counting
  have hsum : ∑ N₁ ∈ Ico Q (2 * Q), #{q ∈ P | ∀ r ∈ F, ¬ q ≡ N₁ [MOD r]} ≤ #P * G := by
    calc ∑ N₁ ∈ Ico Q (2 * Q), #{q ∈ P | ∀ r ∈ F, ¬ q ≡ N₁ [MOD r]}
        = ∑ N₁ ∈ Ico Q (2 * Q), ∑ q ∈ P, if (∀ r ∈ F, ¬ q ≡ N₁ [MOD r]) then 1 else 0 := by
          refine Finset.sum_congr rfl fun N₁ _ => ?_
          rw [Finset.card_filter]
      _ = ∑ q ∈ P, ∑ N₁ ∈ Ico Q (2 * Q), if (∀ r ∈ F, ¬ q ≡ N₁ [MOD r]) then 1 else 0 :=
          Finset.sum_comm
      _ = ∑ q ∈ P, #{N₁ ∈ Ico Q (2 * Q) | ∀ r ∈ F, ¬ q ≡ N₁ [MOD r]} := by
          refine Finset.sum_congr rfl fun q _ => ?_
          rw [Finset.card_filter]
      _ ≤ ∑ q ∈ P, G := Finset.sum_le_sum hrow
      _ = #P * G := by rw [Finset.sum_const, smul_eq_mul]
  -- some common integer is at most the average
  by_contra hcon
  push Not at hcon
  have hne : (Ico Q (2 * Q)).Nonempty := ⟨Q, Finset.mem_Ico.mpr ⟨le_refl _, by omega⟩⟩
  have hlt : ∑ _N₁ ∈ Ico Q (2 * Q), #P * G <
      ∑ N₁ ∈ Ico Q (2 * Q), #{q ∈ P | ∀ r ∈ F, ¬ q ≡ N₁ [MOD r]} * Q :=
    Finset.sum_lt_sum_of_nonempty hne fun N₁ hN => by
      obtain ⟨h1, h2⟩ := Finset.mem_Ico.mp hN
      exact hcon N₁ h1 h2
  rw [Finset.sum_const, Nat.card_Ico, smul_eq_mul, ← Finset.sum_mul] at hlt
  have h2 : (2 * Q - Q) = Q := by omega
  rw [h2] at hlt
  have h3 := Nat.mul_le_mul_right Q hsum
  nlinarith [h3, hlt]

/-- The primes in `(z, w]`: the fixed layer. -/
def primesIoc (z w : ℕ) : Finset ℕ := {r ∈ Ioc z w | r.Prime}

theorem mem_primesIoc {z w r : ℕ} : r ∈ primesIoc z w ↔ (z < r ∧ r ≤ w) ∧ r.Prime := by
  simp [primesIoc]

/-- An integer in `[1, X)`, `X ≤ w²`, with no prime factor in `(z, w]` is `z`-smooth or of the form
`A · p'` with `p' > w` prime. So there are at most (the number of `z`-smooth integers below `X`)
`+ ∑_{1 ≤ A ≤ X/w} π(X/A)` of them. -/
theorem card_no_factor_le {z w X : ℕ} (hw : 0 < w) (hX : X ≤ w * w) :
    #{n ∈ Ico 1 X | ∀ r ∈ primesIoc z w, ¬ r ∣ n} ≤
      #{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers (z + 1)} +
        ∑ A ∈ Icc 1 (X / w), Nat.primeCounting (X / A) := by
  classical
  have hsub : {n ∈ Ico 1 X | ∀ r ∈ primesIoc z w, ¬ r ∣ n} ⊆
      {n ∈ Ico 1 X | n ∈ Nat.smoothNumbers (z + 1)} ∪
        (Icc 1 (X / w)).biUnion fun A => (Nat.primesLE (X / A)).image fun p => A * p := by
    intro n hn
    obtain ⟨hnI, hnF⟩ := Finset.mem_filter.mp hn
    obtain ⟨hn1, hnX⟩ := Finset.mem_Ico.mp hnI
    have hfac : ∀ p, p.Prime → p ∣ n → p ≤ z ∨ w < p := by
      intro p hp hd
      by_contra hcon
      exact hnF p (mem_primesIoc.mpr ⟨⟨by omega, by omega⟩, hp⟩) hd
    rcases smooth_or_large_prime_factor (by omega : 0 < n) (by omega : n < w * w) hfac with
      h | ⟨p', A, hp', hwp, hnA, -⟩
    · refine Finset.mem_union_left _ (Finset.mem_filter.mpr ⟨hnI, ?_⟩)
      exact Nat.mem_smoothNumbers'.mpr fun p hp hd => Nat.lt_succ_of_le (h p hp hd)
    · refine Finset.mem_union_right _ (Finset.mem_biUnion.mpr ⟨A, ?_, ?_⟩)
      · have hA0 : 0 < A := by
          rcases Nat.eq_zero_or_pos A with h0 | h0
          · rw [h0, zero_mul] at hnA
            omega
          · exact h0
        have hAw : A * w < X := by
          calc A * w < A * p' := Nat.mul_lt_mul_of_pos_left hwp hA0
            _ = n := hnA.symm
            _ < X := hnX
        have : A ≤ X / w := (Nat.le_div_iff_mul_le hw).mpr hAw.le
        exact Finset.mem_Icc.mpr ⟨hA0, this⟩
      · refine Finset.mem_image.mpr ⟨p', Nat.mem_primesLE.mpr ⟨?_, hp'⟩, hnA.symm⟩
        have hA0 : 0 < A := by
          rcases Nat.eq_zero_or_pos A with h0 | h0
          · rw [h0, zero_mul] at hnA
            omega
          · exact h0
        refine (Nat.le_div_iff_mul_le hA0).mpr ?_
        rw [mul_comm, ← hnA]
        exact hnX.le
  calc #{n ∈ Ico 1 X | ∀ r ∈ primesIoc z w, ¬ r ∣ n}
      ≤ #({n ∈ Ico 1 X | n ∈ Nat.smoothNumbers (z + 1)} ∪
          (Icc 1 (X / w)).biUnion fun A => (Nat.primesLE (X / A)).image fun p => A * p) :=
        Finset.card_le_card hsub
    _ ≤ #{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers (z + 1)} +
          #((Icc 1 (X / w)).biUnion fun A => (Nat.primesLE (X / A)).image fun p => A * p) :=
        Finset.card_union_le _ _
    _ ≤ #{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers (z + 1)} +
          ∑ A ∈ Icc 1 (X / w), Nat.primeCounting (X / A) := by
        refine Nat.add_le_add_left ?_ _
        refine Finset.card_biUnion_le.trans (Finset.sum_le_sum fun A _ => ?_)
        exact Finset.card_image_le.trans (Nat.primesLE_card_eq_primeCounting _).le

/-- The completely multiplicative function `n ↦ n^{-σ}`. -/
noncomputable def rpowHom (σ : ℝ) : ℕ →* ℝ where
  toFun n := (n : ℝ) ^ (-σ)
  map_one' := by simp
  map_mul' m n := by
    push_cast
    exact Real.mul_rpow (Nat.cast_nonneg m) (Nat.cast_nonneg n)

theorem rpowHom_apply (σ : ℝ) (n : ℕ) : rpowHom σ n = (n : ℝ) ^ (-σ) := rfl

theorem rpowHom_prime_lt_one {σ : ℝ} (hσ : 0 < σ) {p : ℕ} (hp : p.Prime) : ‖rpowHom σ p‖ < 1 := by
  rw [rpowHom_apply, Real.norm_of_nonneg (Real.rpow_nonneg (Nat.cast_nonneg p) _)]
  exact Real.rpow_lt_one_of_one_lt_of_neg (by exact_mod_cast hp.one_lt) (by linarith)

/-- **Rankin's bound.** For `σ > 0` the number of `N`-smooth integers in `[1, X)` is at most
`X^σ · ∏_{p < N} (1 - p^{-σ})⁻¹`. -/
theorem card_smooth_le (N X : ℕ) {σ : ℝ} (hσ : 0 < σ) :
    (#{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers N} : ℝ) ≤
      (X : ℝ) ^ σ * ∏ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-σ))⁻¹ := by
  classical
  set B := {n ∈ Ico 1 X | n ∈ Nat.smoothNumbers N} with hB
  obtain ⟨-, hsum⟩ := EulerProduct.summable_and_hasSum_smoothNumbers_prod_primesBelow_geometric
    (f := rpowHom σ) (fun {p} hp => rpowHom_prime_lt_one hσ hp) N
  -- the finite sum over `B` is at most the whole series
  have hle : ∑ n ∈ B, (n : ℝ) ^ (-σ) ≤ ∏ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-σ))⁻¹ := by
    have h1 : ∑ m ∈ B.subtype (· ∈ Nat.smoothNumbers N), rpowHom σ (m : ℕ) ≤
        ∏ p ∈ N.primesBelow, (1 - rpowHom σ p)⁻¹ :=
      sum_le_hasSum _ (fun m _ => Real.rpow_nonneg (Nat.cast_nonneg _) _) hsum
    have h2 : ∑ m ∈ B.subtype (· ∈ Nat.smoothNumbers N), rpowHom σ (m : ℕ) =
        ∑ n ∈ B, (n : ℝ) ^ (-σ) := by
      rw [Finset.sum_subtype_eq_sum_filter (f := fun n : ℕ => rpowHom σ n)]
      refine Finset.sum_congr ?_ fun n _ => rfl
      exact Finset.filter_true_of_mem fun n hn => (Finset.mem_filter.mp hn).2
    rw [h2] at h1
    exact h1
  -- each term is at least `X^{-σ}`
  have hterm : ∀ n ∈ B, (1 : ℝ) ≤ (X : ℝ) ^ σ * (n : ℝ) ^ (-σ) := by
    intro n hn
    obtain ⟨hnI, -⟩ := Finset.mem_filter.mp hn
    obtain ⟨hn1, hnX⟩ := Finset.mem_Ico.mp hnI
    have hn0 : (0 : ℝ) < n := by exact_mod_cast hn1
    have hnX' : (n : ℝ) ≤ X := by exact_mod_cast hnX.le
    rw [Real.rpow_neg hn0.le, ← div_eq_mul_inv, le_div_iff₀ (Real.rpow_pos_of_pos hn0 _), one_mul]
    exact Real.rpow_le_rpow hn0.le hnX' hσ.le
  calc (#B : ℝ) = ∑ _n ∈ B, (1 : ℝ) := by simp
    _ ≤ ∑ n ∈ B, (X : ℝ) ^ σ * (n : ℝ) ^ (-σ) := Finset.sum_le_sum hterm
    _ = (X : ℝ) ^ σ * ∑ n ∈ B, (n : ℝ) ^ (-σ) := by rw [Finset.mul_sum]
    _ ≤ (X : ℝ) ^ σ * ∏ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-σ))⁻¹ :=
        mul_le_mul_of_nonneg_left hle (Real.rpow_nonneg (Nat.cast_nonneg X) _)

/-- `(1 - t)⁻¹ ≤ exp (4 t)` for `0 ≤ t ≤ 3/4`. -/
theorem inv_one_sub_le_exp {t : ℝ} (h0 : 0 ≤ t) (h1 : t ≤ 3 / 4) :
    (1 - t)⁻¹ ≤ Real.exp (4 * t) := by
  have hpos : 0 < 1 - t := by linarith
  rw [inv_le_iff_one_le_mul₀ hpos]
  have h2 : 1 + 4 * t ≤ Real.exp (4 * t) := by linarith [Real.add_one_le_exp (4 * t)]
  nlinarith [mul_nonneg h0 (by linarith : (0 : ℝ) ≤ 3 - 4 * t)]

/-- For a prime `p` and `σ ≥ 1/2`: `p^{-σ} ≤ 3/4`. -/
theorem rpow_neg_le_three_quarters {p : ℕ} (hp : p.Prime) {σ : ℝ} (hσ : 1 / 2 ≤ σ) :
    (p : ℝ) ^ (-σ) ≤ 3 / 4 := by
  have hp2 : (2 : ℝ) ≤ p := by exact_mod_cast hp.two_le
  have h1 : (p : ℝ) ^ (-σ) ≤ (2 : ℝ) ^ (-σ) :=
    Real.rpow_le_rpow_of_nonpos (by norm_num) hp2 (by linarith)
  have h2 : (2 : ℝ) ^ (-σ) ≤ (2 : ℝ) ^ (-(1 / 2 : ℝ)) :=
    Real.rpow_le_rpow_of_exponent_le (by norm_num) (by linarith)
  have h3 : (2 : ℝ) ^ (-(1 / 2 : ℝ)) ≤ 3 / 4 := by
    rw [Real.rpow_neg (by norm_num), ← Real.sqrt_eq_rpow]
    rw [inv_le_comm₀ (Real.sqrt_pos.mpr (by norm_num)) (by norm_num)]
    apply Real.le_sqrt_of_sq_le
    norm_num
  linarith

/-- The Euler factor product of Rankin's bound: for `1/2 ≤ σ ≤ 1`, if `∑_{p < N} 1/p ≤ S` then
`∏_{p < N} (1 - p^{-σ})⁻¹ ≤ exp (4 N^{1-σ} S)`. -/
theorem prod_primesBelow_le_exp_of_sum (N : ℕ) {σ S : ℝ} (hσ : 1 / 2 ≤ σ) (hσ1 : σ ≤ 1)
    (hS : ∑ p ∈ N.primesBelow, ((p : ℝ))⁻¹ ≤ S) :
    ∏ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-σ))⁻¹ ≤ Real.exp (4 * ((N : ℝ) ^ (1 - σ) * S)) := by
  classical
  have hfac : ∀ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-σ))⁻¹ ≤ Real.exp (4 * (p : ℝ) ^ (-σ)) := by
    intro p hp
    have hpp := Nat.prime_of_mem_primesBelow hp
    exact inv_one_sub_le_exp (Real.rpow_nonneg (Nat.cast_nonneg p) _)
      (rpow_neg_le_three_quarters hpp hσ)
  have hpos : ∀ p ∈ N.primesBelow, 0 ≤ (1 - (p : ℝ) ^ (-σ))⁻¹ := by
    intro p hp
    have hpp := Nat.prime_of_mem_primesBelow hp
    have := rpow_neg_le_three_quarters hpp hσ
    exact inv_nonneg.mpr (by linarith)
  -- `p^{-σ} ≤ N^{1-σ} / p`
  have hterm : ∀ p ∈ N.primesBelow, (p : ℝ) ^ (-σ) ≤ (N : ℝ) ^ (1 - σ) * ((p : ℝ))⁻¹ := by
    intro p hp
    have hpp := Nat.prime_of_mem_primesBelow hp
    have hpN : p < N := Nat.lt_of_mem_primesBelow hp
    have hp0 : (0 : ℝ) < p := by exact_mod_cast hpp.pos
    have h1 : (p : ℝ) ^ (-σ) = (p : ℝ) ^ (1 - σ) * ((p : ℝ))⁻¹ := by
      rw [show (-σ : ℝ) = (1 - σ) + (-1) by ring, Real.rpow_add hp0, Real.rpow_neg_one]
    rw [h1]
    refine mul_le_mul_of_nonneg_right ?_ (inv_nonneg.mpr hp0.le)
    exact Real.rpow_le_rpow hp0.le (by exact_mod_cast hpN.le) (by linarith)
  calc ∏ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-σ))⁻¹
      ≤ ∏ p ∈ N.primesBelow, Real.exp (4 * (p : ℝ) ^ (-σ)) := Finset.prod_le_prod₀ hpos hfac
    _ = Real.exp (∑ p ∈ N.primesBelow, 4 * (p : ℝ) ^ (-σ)) := (Real.exp_sum _ _).symm
    _ ≤ Real.exp (4 * ((N : ℝ) ^ (1 - σ) * S)) := by
        apply Real.exp_le_exp.mpr
        rw [← Finset.mul_sum]
        refine mul_le_mul_of_nonneg_left ?_ (by norm_num)
        calc ∑ p ∈ N.primesBelow, (p : ℝ) ^ (-σ)
            ≤ ∑ p ∈ N.primesBelow, (N : ℝ) ^ (1 - σ) * ((p : ℝ))⁻¹ := Finset.sum_le_sum hterm
          _ = (N : ℝ) ^ (1 - σ) * ∑ p ∈ N.primesBelow, ((p : ℝ))⁻¹ := by rw [Finset.mul_sum]
          _ ≤ (N : ℝ) ^ (1 - σ) * S :=
              mul_le_mul_of_nonneg_left hS (Real.rpow_nonneg (Nat.cast_nonneg N) _)

/-- The same with the harmonic sum for `∑ 1/p`: for `1/2 ≤ σ ≤ 1`,
`∏_{p < N} (1 - p^{-σ})⁻¹ ≤ exp (4 N^{1-σ} (1 + ln N))`. -/
theorem prod_primesBelow_le_exp (N : ℕ) {σ : ℝ} (hσ : 1 / 2 ≤ σ) (hσ1 : σ ≤ 1) :
    ∏ p ∈ N.primesBelow, (1 - (p : ℝ) ^ (-σ))⁻¹ ≤
      Real.exp (4 * ((N : ℝ) ^ (1 - σ) * (1 + Real.log N))) := by
  classical
  refine prod_primesBelow_le_exp_of_sum N hσ hσ1 ?_
  have hsubset : N.primesBelow ⊆ Icc 1 N := by
    intro p hp
    have hpp := Nat.prime_of_mem_primesBelow hp
    have hpN : p < N := Nat.lt_of_mem_primesBelow hp
    exact Finset.mem_Icc.mpr ⟨hpp.one_le, hpN.le⟩
  calc ∑ p ∈ N.primesBelow, ((p : ℝ))⁻¹ ≤ ∑ p ∈ Icc 1 N, ((p : ℝ))⁻¹ :=
        Finset.sum_le_sum_of_subset_of_nonneg hsubset fun p _ _ => by positivity
    _ = (harmonic N : ℝ) := by
        rw [harmonic_eq_sum_Icc]
        push_cast
        rfl
    _ ≤ 1 + Real.log N := harmonic_le_one_add_log N

/-- **Rankin's bound, in closed form.** For `1/2 ≤ σ ≤ 1` the number of `N`-smooth integers in
`[1, X)` is at most `X^σ · exp (4 N^{1-σ} (1 + ln N))`. -/
theorem card_smooth_le_exp (N X : ℕ) {σ : ℝ} (hσ : 1 / 2 ≤ σ) (hσ1 : σ ≤ 1) :
    (#{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers N} : ℝ) ≤
      (X : ℝ) ^ σ * Real.exp (4 * ((N : ℝ) ^ (1 - σ) * (1 + Real.log N))) :=
  (card_smooth_le N X (by linarith)).trans
    (mul_le_mul_of_nonneg_left (prod_primesBelow_le_exp N hσ hσ1)
      (Real.rpow_nonneg (Nat.cast_nonneg X) _))

/-- **Rankin's bound with a bound for `∑ 1/p`.** For `1/2 ≤ σ ≤ 1`, if `∑_{p < N} 1/p ≤ S` then the
number of `N`-smooth integers in `[1, X)` is at most `X^σ · exp (4 N^{1-σ} S)`. -/
theorem card_smooth_le_exp_of_sum (N X : ℕ) {σ S : ℝ} (hσ : 1 / 2 ≤ σ) (hσ1 : σ ≤ 1)
    (hS : ∑ p ∈ N.primesBelow, ((p : ℝ))⁻¹ ≤ S) :
    (#{n ∈ Ico 1 X | n ∈ Nat.smoothNumbers N} : ℝ) ≤
      (X : ℝ) ^ σ * Real.exp (4 * ((N : ℝ) ^ (1 - σ) * S)) :=
  (card_smooth_le N X (by linarith)).trans
    (mul_le_mul_of_nonneg_left (prod_primesBelow_le_exp_of_sum N hσ hσ1 hS)
      (Real.rpow_nonneg (Nat.cast_nonneg X) _))

end GoldbachGaps.Cap
