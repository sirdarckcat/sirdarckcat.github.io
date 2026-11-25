import Mathlib

/-!
# Pairs of rows: the variance of the count left by a sieve, and the average over all covers

Three exact counting statements behind the "selection-aware covers" question (25 November 2026).

* `variance_leftCount`. Let the sieving moduli be `m i` and let `N` run over a full period, one class
  modulo every `m i`. For a finite set of rows, `leftCount m rows N` is the number of rows `q` with
  `N - q` divisible by none of the moduli. Its mean is `n w` and its variance is
  `n w (1 - w) + w² ∑_{q ≠ q'} (ρ(q, q') - 1)` with `w = ∏ (1 - 1/m i)` and
  `ρ(q, q') = ∏ (1 - ν_i/m i) / (1 - 1/m i)²`, `ν_i = 1` when `m i` divides `q - q'` and `2` otherwise.
  This is the formula the research session used; here it is an identity, with no model.

* `card_pair_avoid`, `card_pair_avoid_two`, `sum_card_pair_avoid`. Modulo one prime `r` of the cover
  with class `a ≠ 0`: the number of classes of `q` for which neither `q` nor `q + d` is `0` or `a` is
  `r - 2` when `d = 0`, `r - 3` when `d = ±a` and `r - 4` otherwise. So the class enters the count
  of pairs at difference `d` only through whether `d = ±a`; summed over `d` the count is
  `(r - 2)²` whatever `a` is.

* `sum_classes_pairs`. Summed over all vectors of nonzero classes, the number of pairs of rows with
  any given property (for instance a common class modulo a further prime) is a sum over pairs of
  the candidates of a product of local counts in which no class appears:
  `m r - #{0, q, q'}`, that is `r - 2` when `r` divides `q - q'` and `r - 3` otherwise.
  So the average cover has a pair structure fixed by the candidates alone.

`prime_of_not_dvd_of_lt_sq` is the remark that makes the rows a sieve set: below `(x + 1)²` a number
with no prime factor up to `x` is prime.

What is not here, and is not known: a bound for the worst choice of classes. The pair sum of a
particular cover is a count in a window that is tiny against the period of the cover, and no sieve
gives such counts with the right constant. For the best cover found, a greedy cover and covers with
random classes the measured pair sum is within 0.2% of the average
(`scripts/selection_check/`).
-/

open Finset

namespace GoldbachGaps.Cap

/-! ### Vectors avoiding a set in every coordinate -/

section Avoid

variable {ι : Type*} [Fintype ι] [DecidableEq ι] {α : ι → Type*} [∀ i, Fintype (α i)]
  [∀ i, DecidableEq (α i)]

/-- The vectors that avoid a given set in every coordinate: the product of the numbers of values
left. -/
theorem card_pi_avoid (F : ∀ i, Finset (α i)) :
    #{v : ∀ i, α i | ∀ i, v i ∉ F i} = ∏ i, (Fintype.card (α i) - #(F i)) := by
  have h : ({v : ∀ i, α i | ∀ i, v i ∉ F i} : Finset (∀ i, α i)) =
      Fintype.piFinset fun i => (F i)ᶜ := by
    ext v
    simp [Fintype.mem_piFinset]
  rw [h, Fintype.card_piFinset]
  simp [Finset.card_compl]

end Avoid

/-! ### The count left by a sieve over a full period -/

/-- The number of classes that `q` and `q'` occupy modulo `m i`. -/
def nu {ι : Type*} (m : ι → ℕ) (i : ι) (q q' : ℤ) : ℕ :=
  if (q : ZMod (m i)) = (q' : ZMod (m i)) then 1 else 2

theorem nu_eq {ι : Type*} (m : ι → ℕ) (i : ι) (q q' : ℤ) :
    nu m i q q' = if (m i : ℤ) ∣ q' - q then 1 else 2 := by
  unfold nu
  simp only [ZMod.intCast_eq_intCast_iff_dvd_sub]

theorem nu_self {ι : Type*} (m : ι → ℕ) (i : ι) (q : ℤ) : nu m i q q = 1 := by simp [nu]

theorem one_le_nu {ι : Type*} (m : ι → ℕ) (i : ι) (q q' : ℤ) : 1 ≤ nu m i q q' := by
  unfold nu; split_ifs <;> norm_num

theorem nu_le_two {ι : Type*} (m : ι → ℕ) (i : ι) (q q' : ℤ) : nu m i q q' ≤ 2 := by
  unfold nu; split_ifs <;> norm_num

section Sieve

variable {ι : Type*} [Fintype ι] [DecidableEq ι] (m : ι → ℕ) [∀ i, NeZero (m i)]

/-- The number of rows `q` left by the sieve at `N`: no modulus divides `N - q`. `N` is given by its
class modulo every modulus. -/
def leftCount (rows : Finset ℤ) (N : ∀ i, ZMod (m i)) : ℕ :=
  #{q ∈ rows | ∀ i, N i ≠ (q : ZMod (m i))}

theorem card_left_two (q q' : ℤ) :
    #{N : ∀ i, ZMod (m i) | ∀ i, N i ≠ (q : ZMod (m i)) ∧ N i ≠ (q' : ZMod (m i))} =
      ∏ i, (m i - nu m i q q') := by
  have h := card_pi_avoid (α := fun i => ZMod (m i))
    (fun i => ({(q : ZMod (m i)), (q' : ZMod (m i))} : Finset (ZMod (m i))))
  have h2 : ∀ i, #({(q : ZMod (m i)), (q' : ZMod (m i))} : Finset (ZMod (m i))) = nu m i q q' := by
    intro i
    unfold nu
    split_ifs with hq
    · rw [hq]; simp
    · exact Finset.card_pair hq
  simp only [Finset.mem_insert, Finset.mem_singleton, not_or, ZMod.card, h2] at h
  exact h

theorem card_left_one (q : ℤ) :
    #{N : ∀ i, ZMod (m i) | ∀ i, N i ≠ (q : ZMod (m i))} = ∏ i, (m i - 1) := by
  have h := card_left_two m q q
  simpa [nu_self] using h

/-- First moment: every row is left by `∏ (m i - 1)` of the `N`. -/
theorem sum_leftCount (rows : Finset ℤ) :
    ∑ N : ∀ i, ZMod (m i), leftCount m rows N = #rows * ∏ i, (m i - 1) := by
  unfold leftCount
  simp_rw [Finset.card_filter]
  rw [Finset.sum_comm]
  simp_rw [← Finset.card_filter, card_left_one]
  rw [Finset.sum_const, smul_eq_mul]

/-- Second moment: a pair of rows is left together by `∏ (m i - ν_i)` of the `N`. -/
theorem sum_leftCount_sq (rows : Finset ℤ) :
    ∑ N : ∀ i, ZMod (m i), leftCount m rows N ^ 2 =
      ∑ x ∈ rows ×ˢ rows, ∏ i, (m i - nu m i x.1 x.2) := by
  have h : ∀ N : ∀ i, ZMod (m i), leftCount m rows N ^ 2 =
      ∑ x ∈ rows ×ˢ rows,
        if (∀ i, N i ≠ (x.1 : ZMod (m i)) ∧ N i ≠ (x.2 : ZMod (m i))) then 1 else 0 := by
    intro N
    unfold leftCount
    rw [sq, ← Finset.card_product, ← Finset.filter_product, Finset.card_filter]
    refine Finset.sum_congr rfl fun x _ => ?_
    simp only [forall_and]
  simp_rw [h]
  rw [Finset.sum_comm]
  simp_rw [← Finset.card_filter, card_left_two]

/-- **The variance of the count left by the sieve**, over a full period: with `n` rows,
`w = ∏ (1 - 1/m i)` and `ρ(q, q') = ∏ (1 - ν_i/m i)/(1 - 1/m i)²`, the mean is `n w` and
`Var = n w (1 - w) + w² ∑_{q ≠ q'} (ρ(q, q') - 1)`. -/
theorem variance_leftCount (hm : ∀ i, 2 ≤ m i) (rows : Finset ℤ) :
    (∑ N : ∀ i, ZMod (m i),
        ((leftCount m rows N : ℚ) - #rows * ∏ i, (1 - 1 / (m i : ℚ))) ^ 2) / ∏ i, (m i : ℚ) =
      #rows * (∏ i, (1 - 1 / (m i : ℚ))) * (1 - ∏ i, (1 - 1 / (m i : ℚ))) +
        (∏ i, (1 - 1 / (m i : ℚ))) ^ 2 *
          ∑ x ∈ rows.offDiag,
            (∏ i, ((1 - (nu m i x.1 x.2 : ℚ) / m i) / (1 - 1 / (m i : ℚ)) ^ 2) - 1) := by
  set w : ℚ := ∏ i, (1 - 1 / (m i : ℚ)) with hw
  set M : ℚ := ∏ i, (m i : ℚ) with hM
  have hm0 : ∀ i, (m i : ℚ) ≠ 0 := fun i => by
    have := hm i; positivity
  have hw0 : ∀ i, (1 - 1 / (m i : ℚ)) ≠ 0 := fun i => by
    have h2 : (2 : ℚ) ≤ m i := by exact_mod_cast hm i
    have : 1 / (m i : ℚ) ≤ 1 / 2 := one_div_le_one_div_of_le (by norm_num) h2
    linarith
  have hMne : M ≠ 0 := Finset.prod_ne_zero_iff.mpr fun i _ => hm0 i
  -- the two local identities
  have h1 : ((∏ i, (m i - 1) : ℕ) : ℚ) = M * w := by
    rw [hM, hw, ← Finset.prod_mul_distrib, Nat.cast_prod]
    refine Finset.prod_congr rfl fun i _ => ?_
    rw [Nat.cast_sub (by have := hm i; omega)]
    have := hm0 i
    field_simp
    simp
  have h2 : ∀ q q' : ℤ, ((∏ i, (m i - nu m i q q') : ℕ) : ℚ) =
      M * (w ^ 2 * ∏ i, ((1 - (nu m i q q' : ℚ) / m i) / (1 - 1 / (m i : ℚ)) ^ 2)) := by
    intro q q'
    rw [hM, hw, ← Finset.prod_pow, ← Finset.prod_mul_distrib, ← Finset.prod_mul_distrib,
      Nat.cast_prod]
    refine Finset.prod_congr rfl fun i _ => ?_
    rw [Nat.cast_sub (by have := hm i; have := nu_le_two m i q q'; omega)]
    have := hm0 i
    have := hw0 i
    have hm1 : (m i : ℚ) - 1 ≠ 0 := by
      have h2 : (2 : ℚ) ≤ m i := by exact_mod_cast hm i
      linarith
    field_simp
  -- the moments, in `ℚ`
  have hS : (∑ N : ∀ i, ZMod (m i), (leftCount m rows N : ℚ)) = #rows * (M * w) := by
    rw [← h1]
    exact_mod_cast sum_leftCount m rows
  have hS2 : (∑ N : ∀ i, ZMod (m i), (leftCount m rows N : ℚ) ^ 2) =
      ∑ x ∈ rows ×ˢ rows, ((∏ i, (m i - nu m i x.1 x.2) : ℕ) : ℚ) := by
    exact_mod_cast sum_leftCount_sq m rows
  have hcard : (Fintype.card (∀ i, ZMod (m i)) : ℚ) = M := by
    rw [Fintype.card_pi, hM, Nat.cast_prod]
    simp [ZMod.card]
  -- split the pairs into the diagonal and the rest
  have hsplit : ∑ x ∈ rows ×ˢ rows, ((∏ i, (m i - nu m i x.1 x.2) : ℕ) : ℚ) =
      #rows * (M * w) + ∑ x ∈ rows.offDiag,
        M * (w ^ 2 * ∏ i, ((1 - (nu m i x.1 x.2 : ℚ) / m i) / (1 - 1 / (m i : ℚ)) ^ 2)) := by
    rw [← Finset.diag_union_offDiag, Finset.sum_union (Finset.disjoint_diag_offDiag rows),
      Finset.sum_diag]
    congr 1
    · simp only [nu_self, h1, Finset.sum_const, nsmul_eq_mul]
    · exact Finset.sum_congr rfl fun x _ => h2 x.1 x.2
  have hoff : (#rows.offDiag : ℚ) = #rows * #rows - #rows := by
    rw [Finset.offDiag_card, Nat.cast_sub (Nat.le_mul_self _)]
    push_cast; ring
  have hexpand : ∑ N : ∀ i, ZMod (m i), ((leftCount m rows N : ℚ) - #rows * w) ^ 2 =
      (∑ N : ∀ i, ZMod (m i), (leftCount m rows N : ℚ) ^ 2)
        - 2 * (#rows * w) * (∑ N : ∀ i, ZMod (m i), (leftCount m rows N : ℚ))
        + M * (#rows * w) ^ 2 := by
    have : ∀ N : ∀ i, ZMod (m i), ((leftCount m rows N : ℚ) - #rows * w) ^ 2 =
        (leftCount m rows N : ℚ) ^ 2 - 2 * (#rows * w) * (leftCount m rows N : ℚ)
          + (#rows * w) ^ 2 := fun N => by ring
    simp_rw [this]
    rw [Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum, Finset.sum_const,
      Finset.card_univ, nsmul_eq_mul, hcard]
  rw [hexpand, hS2, hsplit, hS, Finset.sum_sub_distrib, Finset.sum_const, nsmul_eq_mul, hoff,
    ← Finset.mul_sum, ← Finset.mul_sum]
  field_simp
  ring

end Sieve

/-! ### One modulus of the cover: pairs at a given difference -/

section Local

variable {r : ℕ} [NeZero r]

/-- Modulo `r`, with the classes of `A` excluded: the number of `q` for which neither `q` nor
`q + d` is excluded is `r - 2 #A` plus the number of `u ∈ A` with `u + d ∈ A`. -/
theorem card_pair_avoid (A : Finset (ZMod r)) (d : ZMod r) :
    #{q : ZMod r | q ∉ A ∧ q + d ∉ A} + 2 * #A = r + #{u ∈ A | u + d ∈ A} := by
  set B : Finset (ZMod r) := {q | q + d ∈ A} with hB
  have hBcard : #B = #A := by
    have : B = A.image (fun u => u - d) := by
      ext q
      simp only [hB, Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_image]
      constructor
      · intro h; exact ⟨q + d, h, by ring⟩
      · rintro ⟨u, hu, rfl⟩; simpa using hu
    rw [this, Finset.card_image_of_injective _ (sub_left_injective)]
  have hcompl : ({q : ZMod r | q ∉ A ∧ q + d ∉ A} : Finset (ZMod r)) = (A ∪ B)ᶜ := by
    ext q; simp [hB]
  have hinter : ({u ∈ A | u + d ∈ A} : Finset (ZMod r)) = A ∩ B := by
    ext q; simp [hB]
  rw [hcompl, hinter, Finset.card_compl, ZMod.card]
  have h1 := Finset.card_union_add_card_inter A B
  have h2 : #(A ∪ B) ≤ r := by simpa [ZMod.card] using Finset.card_le_univ (A ∪ B)
  omega

/-- Summed over every difference, the count does not depend on which classes are excluded, only on
how many. -/
theorem sum_card_pair_avoid (A : Finset (ZMod r)) :
    ∑ d : ZMod r, #{q : ZMod r | q ∉ A ∧ q + d ∉ A} = (r - #A) ^ 2 := by
  have hc : #Aᶜ = r - #A := by rw [Finset.card_compl, ZMod.card]
  have hq : ∀ q : ZMod r, #{d : ZMod r | q + d ∉ A} = r - #A := by
    intro q
    have : ({d : ZMod r | q + d ∉ A} : Finset (ZMod r)) = Aᶜ.image (fun u => u - q) := by
      ext d
      simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_image,
        Finset.mem_compl]
      constructor
      · intro h; exact ⟨q + d, h, by ring⟩
      · rintro ⟨u, hu, rfl⟩; simpa using hu
    rw [this, Finset.card_image_of_injective _ (sub_left_injective), hc]
  simp_rw [Finset.card_filter]
  rw [Finset.sum_comm]
  have : ∀ q : ZMod r, (∑ d : ZMod r, if q ∉ A ∧ q + d ∉ A then 1 else 0) =
      if q ∉ A then r - #A else 0 := by
    intro q
    by_cases h : q ∈ A
    · simp [h]
    · simp only [h, not_false_eq_true, true_and, ite_true]
      rw [← Finset.card_filter, hq]
  simp_rw [this]
  rw [← Finset.sum_filter, Finset.sum_const, smul_eq_mul, sq]
  congr 1
  rw [← hc]
  congr 1
  ext q; simp

/-- **One class of the cover.** With the classes `0` and `a ≠ 0` excluded modulo `r`
(`a ≠ -a`, as for an odd `r`): neither `q` nor `q + d` is excluded for `r - 2` classes of `q` when
`d = 0`, for `r - 3` when `d = a` or `d = -a`, and for `r - 4` otherwise. The class `a` enters only
through whether `d = ±a`. -/
theorem card_pair_avoid_two {a : ZMod r} (ha : a ≠ 0) (ha' : a ≠ -a) (d : ZMod r) :
    #{q : ZMod r | q ∉ ({0, a} : Finset (ZMod r)) ∧ q + d ∉ ({0, a} : Finset (ZMod r))} + 4 =
      r + (if d = 0 then 2 else if d = a ∨ d = -a then 1 else 0) := by
  have h := card_pair_avoid ({0, a} : Finset (ZMod r)) d
  have hA : #({0, a} : Finset (ZMod r)) = 2 := Finset.card_pair (Ne.symm ha)
  have key : #{u ∈ ({0, a} : Finset (ZMod r)) | u + d ∈ ({0, a} : Finset (ZMod r))} =
      (if d = 0 then 2 else if d = a ∨ d = -a then 1 else 0) := by
    by_cases hd0 : d = 0
    · subst hd0
      simp only [add_zero, ite_true]
      rw [Finset.filter_true_of_mem (fun x hx => hx)]
      exact hA
    · simp only [hd0, ite_false]
      by_cases hda : d = a
      · subst hda
        have : ({u ∈ ({0, d} : Finset (ZMod r)) | u + d ∈ ({0, d} : Finset (ZMod r))} :
            Finset (ZMod r)) = {0} := by
          ext u
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
          constructor
          · rintro ⟨hu | hu, h2⟩
            · exact hu
            · subst hu
              rcases h2 with h2 | h2
              · exact absurd (eq_neg_of_add_eq_zero_left h2) ha'
              · exact absurd (by simpa using h2) hd0
          · intro hu; subst hu; exact ⟨Or.inl rfl, by simp⟩
        rw [this]; simp
      · by_cases hdn : d = -a
        · subst hdn
          have : ({u ∈ ({0, a} : Finset (ZMod r)) | u + -a ∈ ({0, a} : Finset (ZMod r))} :
              Finset (ZMod r)) = {a} := by
            ext u
            simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
            constructor
            · rintro ⟨hu | hu, h2⟩
              · subst hu
                rcases h2 with h2 | h2
                · exact absurd (by simpa using h2) ha
                · exact absurd (by simpa using h2.symm) ha'
              · exact hu
            · intro hu; subst hu; exact ⟨Or.inr rfl, by simp⟩
          rw [this]; simp [hda]
        · have : ({u ∈ ({0, a} : Finset (ZMod r)) | u + d ∈ ({0, a} : Finset (ZMod r))} :
              Finset (ZMod r)) = ∅ := by
            ext u
            simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton,
              Finset.notMem_empty, iff_false, not_and, not_or]
            rintro (hu | hu)
            · subst hu; simp [hd0, hda]
            · subst hu
              refine ⟨fun h2 => hdn (eq_neg_of_add_eq_zero_right h2), fun h2 => hd0 ?_⟩
              simpa using h2
          rw [this]; simp [hda, hdn]
  rw [key, hA] at h
  omega

end Local

/-! ### All the covers at once -/

section Classes

variable {κ : Type*} [Fintype κ] [DecidableEq κ] (m : κ → ℕ) [∀ r, NeZero (m r)]

/-- `q` is in none of the classes `a`: the cover leaves it. -/
def IsLeft (a : ∀ r, ZMod (m r)) (q : ℤ) : Prop := ∀ r, a r ≠ (q : ZMod (m r))

instance (a : ∀ r, ZMod (m r)) (q : ℤ) : Decidable (IsLeft m a q) := by
  unfold IsLeft; infer_instance

/-- The vectors of nonzero classes that leave both `q` and `q'`: for each modulus, any class
outside `{0, q, q'}`. -/
theorem card_classes_left_two (q q' : ℤ) :
    #{a : ∀ r, ZMod (m r) | (∀ r, a r ≠ 0) ∧ IsLeft m a q ∧ IsLeft m a q'} =
      ∏ r, (m r - #({0, (q : ZMod (m r)), (q' : ZMod (m r))} : Finset (ZMod (m r)))) := by
  have h := card_pi_avoid (α := fun r => ZMod (m r))
    (fun r => ({0, (q : ZMod (m r)), (q' : ZMod (m r))} : Finset (ZMod (m r))))
  simp only [ZMod.card] at h
  rw [← h]
  refine congrArg Finset.card (Finset.filter_congr fun a _ => ?_)
  unfold IsLeft
  simp only [Finset.mem_insert, Finset.mem_singleton, not_or]
  constructor
  · rintro ⟨h0, h1, h2⟩ r; exact ⟨h0 r, h1 r, h2 r⟩
  · intro h; exact ⟨fun r => (h r).1, fun r => (h r).2.1, fun r => (h r).2.2⟩

/-- The number of excluded classes when `q` and `q'` are both nonzero modulo `r`: two if they
agree, three otherwise. So the local count is `r - 2` when `r` divides `q - q'` and `r - 3`
otherwise. -/
theorem card_zero_pair {r : ℕ} {u v : ZMod r} (hu : u ≠ 0) (hv : v ≠ 0) :
    #({0, u, v} : Finset (ZMod r)) = if u = v then 2 else 3 := by
  split_ifs with h
  · subst h
    rw [Finset.pair_eq_singleton, Finset.card_pair (Ne.symm hu)]
  · rw [Finset.card_insert_of_notMem (by simp [Ne.symm hu, Ne.symm hv]), Finset.card_pair h]

/-- **The average cover.** Summed over all vectors of nonzero classes, the number of ordered pairs
of candidates that the cover leaves and that have a given property `D` (a common class modulo a
further prime, say) is a sum over the pairs with `D` of a product of local counts. No class appears
on the right. -/
theorem sum_classes_pairs (P : Finset ℤ) (D : ℤ × ℤ → Prop) [DecidablePred D] :
    ∑ a ∈ ({a : ∀ r, ZMod (m r) | ∀ r, a r ≠ 0} : Finset (∀ r, ZMod (m r))),
        #{x ∈ P.offDiag | D x ∧ IsLeft m a x.1 ∧ IsLeft m a x.2} =
      ∑ x ∈ P.offDiag with D x,
        ∏ r, (m r - #({0, (x.1 : ZMod (m r)), (x.2 : ZMod (m r))} : Finset (ZMod (m r)))) := by
  simp_rw [Finset.card_filter]
  rw [Finset.sum_comm, Finset.sum_filter]
  refine Finset.sum_congr rfl fun x _ => ?_
  by_cases hD : D x
  · simp only [hD, true_and, ite_true]
    rw [← card_classes_left_two, Finset.card_filter, Finset.sum_filter]
    refine Finset.sum_congr rfl fun a _ => ?_
    by_cases h0 : ∀ r, a r ≠ 0 <;> simp [h0]
  · simp [hD]

end Classes

/-! ### Rows are a sieve set -/

/-- Below `(x + 1)²` a number with no prime factor up to `x` is prime. So for a cover on all the
primes up to `x` and a bound below `(x + 1)²`, the rows above `x` are exactly the integers that
avoid the classes `0` and `a_r` of every modulus: a sieve set, with no primality in it. -/
theorem prime_of_not_dvd_of_lt_sq {x q : ℕ} (h2 : 2 ≤ q) (hq : q < (x + 1) ^ 2)
    (h : ∀ r : ℕ, r.Prime → r ≤ x → ¬ r ∣ q) : q.Prime := by
  by_contra hnp
  have hmf : (Nat.minFac q).Prime := Nat.minFac_prime (by omega)
  have hx : x < Nat.minFac q := by
    by_contra hle
    exact h _ hmf (not_lt.mp hle) (Nat.minFac_dvd q)
  have hsq : Nat.minFac q ^ 2 ≤ q := Nat.minFac_sq_le_self (by omega) hnp
  have : (x + 1) ^ 2 ≤ Nat.minFac q ^ 2 := Nat.pow_le_pow_left hx 2
  omega

end GoldbachGaps.Cap
