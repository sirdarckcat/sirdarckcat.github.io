import GoldbachGaps.Basic

/-!
# Stickelberger's theorem in Swan's form (Pellet's formula)

Over a finite field `F` of odd characteristic, for a squarefree polynomial `g`,

  `quadraticChar F (discr g) = (-1)^(deg g - r)`,  `r` the number of irreducible factors of `g`

(`stickelbergerSwan`). Equivalently the Möbius function of `F[X]` is
`μ(g) = (-1)^(deg g) χ(discr g)`. Stickelberger (1897) for number fields, Pellet (1878) and
Swan (1962) for finite fields; it is not in Mathlib.

The proof here avoids Galois groups and cycle types.

* `discr_mul`: `discr (f g) = discr f · discr g · Res(f, g)²` for `f`, `g` of positive degree,
  and `discr_C_mul`: `discr (c f) = c^(2 deg f - 2) discr f`. Both from Mathlib's resultant
  calculus. They reduce the theorem to irreducible monic `g`
  (`UniqueFactorizationMonoid.induction_on_coprime`).
* `discr_nodal`: `discr (∏ i, (X - r i)) = (∏_{i<j} (r j - r i))²`.
* For `g` monic irreducible of degree `m` with a root `β` in the algebraic closure, the roots
  are `β, β^q, …, β^(q^(m-1))`, distinct, with `β^(q^m) = β` (Mathlib:
  `Irreducible.natDegree_dvd_iff_dvd_X_pow_card_pow_sub_X`). The Frobenius `x ↦ x^q` rotates
  the rows of their Vandermonde matrix, so its determinant `δ` satisfies
  `δ^q = (-1)^(m-1) δ` (`frob_det_vandermonde`), and by Euler's criterion
  `χ(discr g) = (discr g)^((q-1)/2) = δ^(q-1) = (-1)^(m-1)`
  (`quadraticChar_discr_of_irreducible_of_monic`).
-/

open Polynomial Finset

namespace GoldbachGaps.FunctionField

section Pairs

variable {R : Type*} [CommRing R]

/-- The number of pairs `i < j` in `Fin n`. -/
theorem sum_card_Ioi (n : ℕ) : ∑ i : Fin n, #(Ioi i) = n * (n - 1) / 2 := by
  simp_rw [Fin.card_Ioi]
  rw [Fin.sum_univ_eq_sum_range (fun i => n - 1 - i) n, Finset.sum_range_reflect (fun i => i) n,
    Finset.sum_range_id]

/-- The product over ordered pairs `i ≠ j` of `r i - r j` is `±` the square of the product
over `i < j` of `r j - r i`. -/
theorem prod_offDiag_sub (n : ℕ) (r : Fin n → R) :
    ∏ i, ∏ j ∈ ({i} : Finset (Fin n))ᶜ, (r i - r j) =
      (-1) ^ (n * (n - 1) / 2) * (∏ i, ∏ j ∈ Ioi i, (r j - r i)) ^ 2 := by
  rw [← Finset.prod_prod_Ioi_mul_eq_prod_prod_off_diag (fun a b => r b - r a)]
  have h : ∀ i : Fin n, ∏ j ∈ Ioi i, (r i - r j) * (r j - r i) =
      (-1) ^ #(Ioi i) * (∏ j ∈ Ioi i, (r j - r i)) ^ 2 := by
    intro i
    rw [← Finset.prod_pow, ← Finset.prod_const, ← Finset.prod_mul_distrib]
    refine Finset.prod_congr rfl fun j _ => ?_
    ring
  simp_rw [h]
  rw [Finset.prod_mul_distrib, Finset.prod_pow_eq_pow_sum, sum_card_Ioi, Finset.prod_pow]

end Pairs

section Nodal

variable {K : Type*} [Field K]

/-- The roots of `∏ i, (X - C (r i))`. -/
theorem roots_nodal_univ (n : ℕ) (r : Fin n → K) :
    (Lagrange.nodal univ r).roots = (univ : Finset (Fin n)).val.map r := by
  rw [Lagrange.nodal_eq, roots_prod _ _ (by rw [← Lagrange.nodal_eq]; exact Lagrange.nodal_ne_zero)]
  simp_rw [roots_X_sub_C]
  exact Multiset.bind_singleton _ r

/-- The discriminant of `∏ i, (X - C (r i))` is the square of the Vandermonde product. -/
theorem discr_nodal (n : ℕ) (hn : 1 ≤ n) (r : Fin n → K) :
    discr (Lagrange.nodal univ r) = (∏ i, ∏ j ∈ Ioi i, (r j - r i)) ^ 2 := by
  classical
  set G := Lagrange.nodal (univ : Finset (Fin n)) r with hG
  have hGm : G.Monic := Lagrange.nodal_monic
  have hGdeg : G.natDegree = n := by
    rw [hG, Lagrange.natDegree_nodal, Finset.card_univ, Fintype.card_fin]
  have hsplit : G.Splits := by
    rw [hG, Lagrange.nodal_eq]
    exact Splits.prod fun i _ => Splits.X_sub_C _
  have hpos : 0 < G.degree := by
    rw [← natDegree_pos_iff_degree_pos, hGdeg]
    exact hn
  have e1 := resultant_deriv hpos
  have e2 := resultant_eq_prod_eval G (derivative G) (n - 1)
    ((natDegree_derivative_le G).trans (by rw [hGdeg])) hsplit
  rw [hGdeg, hGm.leadingCoeff, mul_one] at e1
  rw [hGdeg, hGm.leadingCoeff, one_pow, one_mul, roots_nodal_univ, Multiset.map_map] at e2
  have e3 : (Multiset.map ((fun x => eval x (derivative G)) ∘ r) (univ : Finset (Fin n)).val).prod
      = ∏ i, ∏ j ∈ ({i} : Finset (Fin n))ᶜ, (r i - r j) := by
    rw [← Finset.prod_eq_multiset_prod]
    refine Finset.prod_congr rfl fun i _ => ?_
    rw [Function.comp_apply, hG, Lagrange.eval_nodal_derivative_eval_node_eq (Finset.mem_univ i),
      Lagrange.eval_nodal, Finset.compl_singleton]
  rw [e3, prod_offDiag_sub, e1] at e2
  have hs : ((-1 : K) ^ (n * (n - 1) / 2)) ≠ 0 := pow_ne_zero _ (neg_ne_zero.mpr one_ne_zero)
  exact mul_left_cancel₀ hs e2

end Nodal

section Frobenius

variable {K : Type*} [Field K]

/-- If `x ↦ x^q` is a ring homomorphism of `K` and `β^(q^(n+1)) = β`, it rotates the rows of the
Vandermonde matrix of `β, β^q, …, β^(q^n)`, so the determinant is multiplied by `(-1)^n`. -/
theorem frob_det_vandermonde (φ : K →+* K) (q n : ℕ) (hφ : ∀ x, φ x = x ^ q) (β : K)
    (hβ : β ^ q ^ (n + 1) = β) :
    (Matrix.vandermonde fun i : Fin (n + 1) => β ^ q ^ (i : ℕ)).det ^ q =
      (-1) ^ n * (Matrix.vandermonde fun i : Fin (n + 1) => β ^ q ^ (i : ℕ)).det := by
  have h1 : φ.mapMatrix (Matrix.vandermonde fun i : Fin (n + 1) => β ^ q ^ (i : ℕ)) =
      (Matrix.vandermonde fun i : Fin (n + 1) => β ^ q ^ (i : ℕ)).submatrix
        (finRotate (n + 1)) id := by
    ext i j
    simp only [RingHom.mapMatrix_apply, Matrix.map_apply, Matrix.vandermonde_apply,
      Matrix.submatrix_apply, id]
    rw [hφ, ← pow_mul, mul_comm, pow_mul]
    congr 1
    rw [← pow_mul, ← pow_succ]
    by_cases hi : i = Fin.last n
    · subst hi
      rw [finRotate_last, Fin.val_last, hβ]
      simp
    · rw [coe_finRotate_of_ne_last hi]
  rw [← hφ, RingHom.map_det, h1, Matrix.det_permute, sign_finRotate]
  simp

end Frobenius

section Multiplicative

variable {F : Type*} [Field F]

/-- Scaling: `discr (c f) = c^(2 deg f - 2) discr f` for `deg f ≥ 1`. -/
theorem discr_C_mul {c : F} (hc : c ≠ 0) {f : F[X]} (hf : 1 ≤ f.natDegree) :
    discr (C c * f) = c ^ (2 * f.natDegree - 2) * discr f := by
  have hf0 : f ≠ 0 := by
    intro h
    rw [h, natDegree_zero] at hf
    omega
  have hl0 : f.leadingCoeff ≠ 0 := leadingCoeff_ne_zero.mpr hf0
  have hn : (C c * f).natDegree = f.natDegree := natDegree_C_mul hc
  have hl : (C c * f).leadingCoeff = c * f.leadingCoeff := by
    rw [leadingCoeff_mul, leadingCoeff_C]
  have hposf : 0 < f.degree := natDegree_pos_iff_degree_pos.mp hf
  have hpos : 0 < (C c * f).degree := by
    rw [← natDegree_pos_iff_degree_pos, hn]
    exact hf
  have e1 := resultant_deriv hpos
  rw [hn, hl, derivative_C_mul, resultant_C_mul_left, resultant_C_mul_right,
    resultant_deriv hposf] at e1
  have hp : c ^ (f.natDegree - 1) * c ^ f.natDegree = c * c ^ (2 * f.natDegree - 2) := by
    rw [← pow_add, ← pow_succ']
    congr 1
    omega
  have hs : ((-1 : F) ^ (f.natDegree * (f.natDegree - 1) / 2)) ≠ 0 :=
    pow_ne_zero _ (neg_ne_zero.mpr one_ne_zero)
  apply mul_left_cancel₀ (mul_ne_zero hs (mul_ne_zero hc hl0))
  linear_combination -e1 +
    ((-1 : F) ^ (f.natDegree * (f.natDegree - 1) / 2) * f.leadingCoeff * discr f) * hp

/-- `C(m + n, 2) = C(m, 2) + C(n, 2) + n m`, written with products. -/
theorem pairs_add (m n : ℕ) :
    (m + n) * (m + n - 1) / 2 = m * (m - 1) / 2 + n * (n - 1) / 2 + n * m := by
  have h : (m + n) * (m + n - 1) = m * (m - 1) + n * (n - 1) + 2 * (n * m) := by
    rcases m with _ | m
    · simp
    rcases n with _ | n
    · simp
    simp only [Nat.add_sub_cancel]
    have e : m + 1 + (n + 1) - 1 = m + n + 1 := by omega
    rw [e]
    ring
  obtain ⟨a, ha⟩ := (Nat.even_mul_pred_self m).two_dvd
  obtain ⟨b, hb⟩ := (Nat.even_mul_pred_self n).two_dvd
  rw [h, ha, hb]
  omega

/-- One half of the product rule for discriminants: the resultant of `f` with `f' g`. -/
theorem resultant_derivative_mul (f g : F[X]) (hf : 1 ≤ f.natDegree) :
    resultant f (derivative f * g) f.natDegree (f.natDegree + g.natDegree - 1) =
      resultant f (derivative f) f.natDegree (f.natDegree - 1) * resultant f g := by
  have hd : (derivative f).natDegree ≤ f.natDegree - 1 := natDegree_derivative_le f
  have hk : f.natDegree + g.natDegree - 1 =
      ((derivative f).natDegree + g.natDegree) + (f.natDegree - 1 - (derivative f).natDegree) := by
    omega
  have hk' : f.natDegree - 1 =
      (derivative f).natDegree + (f.natDegree - 1 - (derivative f).natDegree) := by omega
  rw [hk, resultant_add_right_deg _ _ _ _ _ natDegree_mul_le,
    resultant_mul_right f (derivative f) g f.natDegree le_rfl]
  conv_rhs => rw [hk', resultant_add_right_deg _ _ _ _ _ le_rfl]
  ring

/-- **Multiplicativity of the discriminant**: `discr (f g) = discr f · discr g · Res(f, g)²`
for `f`, `g` of positive degree. -/
theorem discr_mul {f g : F[X]} (hf : 1 ≤ f.natDegree) (hg : 1 ≤ g.natDegree) :
    discr (f * g) = discr f * discr g * resultant f g ^ 2 := by
  have hf0 : f ≠ 0 := by
    intro h
    rw [h, natDegree_zero] at hf
    omega
  have hg0 : g ≠ 0 := by
    intro h
    rw [h, natDegree_zero] at hg
    omega
  have hlf : f.leadingCoeff ≠ 0 := leadingCoeff_ne_zero.mpr hf0
  have hlg : g.leadingCoeff ≠ 0 := leadingCoeff_ne_zero.mpr hg0
  have hdeg : (f * g).natDegree = f.natDegree + g.natDegree := natDegree_mul hf0 hg0
  have hpos : 0 < (f * g).degree := by
    rw [← natDegree_pos_iff_degree_pos, hdeg]
    omega
  have e0 := resultant_deriv hpos
  have hG : (derivative (f * g)).natDegree ≤ f.natDegree + g.natDegree - 1 := by
    rw [← hdeg]
    exact natDegree_derivative_le _
  rw [hdeg, leadingCoeff_mul, resultant_mul_left f g _ _ hG, derivative_mul] at e0
  -- the factor from `f`
  have ef : resultant f (derivative f * g + f * derivative g) f.natDegree
      (f.natDegree + g.natDegree - 1) =
      resultant f (derivative f) f.natDegree (f.natDegree - 1) * resultant f g := by
    rw [resultant_add_mul_right f _ _ _ _
      (by have := natDegree_derivative_le g; omega) le_rfl]
    exact resultant_derivative_mul f g hf
  -- the factor from `g`
  have eg : resultant g (derivative f * g + f * derivative g) g.natDegree
      (f.natDegree + g.natDegree - 1) =
      resultant g (derivative g) g.natDegree (g.natDegree - 1) * resultant g f := by
    have e : derivative f * g + f * derivative g = derivative g * f + g * derivative f := by ring
    rw [e, resultant_add_mul_right g _ _ _ _
      (by have := natDegree_derivative_le f; omega) le_rfl, add_comm f.natDegree]
    exact resultant_derivative_mul g f hg
  rw [ef, eg, resultant_deriv (natDegree_pos_iff_degree_pos.mp hf),
    resultant_deriv (natDegree_pos_iff_degree_pos.mp hg),
    resultant_comm g f g.natDegree f.natDegree, pairs_add, pow_add, pow_add] at e0
  have hs1 : ((-1 : F) ^ (f.natDegree * (f.natDegree - 1) / 2)) ≠ 0 :=
    pow_ne_zero _ (neg_ne_zero.mpr one_ne_zero)
  have hs2 : ((-1 : F) ^ (g.natDegree * (g.natDegree - 1) / 2)) ≠ 0 :=
    pow_ne_zero _ (neg_ne_zero.mpr one_ne_zero)
  have hs3 : ((-1 : F) ^ (g.natDegree * f.natDegree)) ≠ 0 :=
    pow_ne_zero _ (neg_ne_zero.mpr one_ne_zero)
  apply mul_left_cancel₀
    (mul_ne_zero (mul_ne_zero (mul_ne_zero hs1 hs2) hs3) (mul_ne_zero hlf hlg))
  linear_combination -e0

end Multiplicative

section Irreducible

variable {F : Type*} [Field F] [Fintype F] [DecidableEq F]

/-- **Stickelberger's theorem for an irreducible polynomial**: over a finite field of odd
characteristic, the discriminant of a monic irreducible polynomial of degree `m` has quadratic
character `(-1)^(m-1)`. The roots are `β, β^q, …`, the Frobenius rotates them, and the
Vandermonde determinant `δ` (a square root of the discriminant) satisfies
`δ^q = (-1)^(m-1) δ`. -/
theorem quadraticChar_discr_of_irreducible_of_monic (hF : ringChar F ≠ 2) {g : F[X]}
    (hg : Irreducible g) (hm : g.Monic) :
    quadraticChar F (discr g) = (-1) ^ (g.natDegree + 1) := by
  classical
  set q := Fintype.card F with hq
  obtain ⟨n, hn⟩ : ∃ n, g.natDegree = n + 1 :=
    Nat.exists_eq_succ_of_ne_zero (Irreducible.natDegree_pos hg).ne'
  obtain ⟨β, hβ⟩ := IsAlgClosed.exists_aeval_eq_zero (AlgebraicClosure F) g
    (degree_pos_of_irreducible hg).ne'
  set Φ := FiniteField.frobeniusAlgHom F (AlgebraicClosure F) with hΦdef
  have hΦ : ∀ x, Φ x = x ^ q := fun x => rfl
  -- every `β^(q^i)` is a root of `g`
  have hroot : ∀ i : ℕ, aeval (β ^ q ^ i) g = 0 := by
    intro i
    induction i with
    | zero => simpa using hβ
    | succ i ih => rw [pow_succ, pow_mul, ← hΦ, aeval_algHom_apply, ih, map_zero]
  -- `β^(q^(n+1)) = β`
  have hdvd : g ∣ X ^ Nat.card F ^ (n + 1) - X :=
    hg.natDegree_dvd_iff_dvd_X_pow_card_pow_sub_X.mp (by rw [hn])
  have hβq : β ^ q ^ (n + 1) = β := by
    obtain ⟨c, hc⟩ := hdvd
    have h := congrArg (aeval β) hc
    rw [map_mul, hβ, zero_mul, map_sub, map_pow, aeval_X, Nat.card_eq_fintype_card,
      sub_eq_zero] at h
    exact h
  -- the `n + 1` roots are distinct
  have hgmin : g = minpoly F β := minpoly.eq_of_irreducible_of_monic hg hβ hm
  have key : ∀ i j : ℕ, i < j → j < n + 1 → β ^ q ^ i ≠ β ^ q ^ j := by
    intro i j hij hj heq
    have e : β ^ q ^ j = (β ^ q ^ (j - i)) ^ q ^ i := by
      rw [← pow_mul, ← pow_add, Nat.sub_add_cancel hij.le]
    rw [e] at heq
    have hpow : ∀ x : AlgebraicClosure F, (Φ ^ i) x = x ^ q ^ i := by
      intro x
      rw [AlgHom.coe_pow, hΦdef, FiniteField.coe_frobeniusAlgHom, pow_iterate]
    have h2 : (Φ ^ i) β = (Φ ^ i) (β ^ q ^ (j - i)) := by
      rw [hpow, hpow]
      exact heq
    have h3 : β = β ^ q ^ (j - i) := (Φ ^ i).toRingHom.injective h2
    have h4 : aeval β (X ^ Nat.card F ^ (j - i) - X : F[X]) = 0 := by
      rw [map_sub, map_pow, aeval_X, Nat.card_eq_fintype_card, ← h3, sub_self]
    have h5 : g ∣ X ^ Nat.card F ^ (j - i) - X := by
      rw [hgmin]
      exact minpoly.dvd F β h4
    have h6 := hg.natDegree_dvd_of_dvd_X_pow_card_pow_sub_X h5
    rw [hn] at h6
    have h7 := Nat.le_of_dvd (by omega) h6
    omega
  set r : Fin (n + 1) → AlgebraicClosure F := fun i => β ^ q ^ (i : ℕ) with hr
  have hinj : Function.Injective r := by
    intro i j hij
    by_contra hne
    rcases lt_or_gt_of_ne (fun h => hne (Fin.ext h)) with h | h
    · exact key i j h j.isLt hij
    · exact key j i h i.isLt hij.symm
  -- `g` splits as the product of the `X - r i`
  have hgK0 : g.map (algebraMap F (AlgebraicClosure F)) ≠ 0 :=
    (hm.map _).ne_zero
  have hG : g.map (algebraMap F (AlgebraicClosure F)) = Lagrange.nodal univ r := by
    refine eq_of_monic_of_dvd_of_natDegree_le Lagrange.nodal_monic (hm.map _) ?_ ?_
    · have e : Lagrange.nodal univ r =
          (Multiset.map (fun a => X - C a) ((univ : Finset (Fin (n + 1))).val.map r)).prod := by
        rw [Lagrange.nodal_eq, Finset.prod_eq_multiset_prod, Multiset.map_map]
        rfl
      rw [e, Multiset.prod_X_sub_C_dvd_iff_le_roots hgK0,
        Multiset.le_iff_subset ((Multiset.nodup_map_iff_of_injective hinj).mpr (Finset.nodup _))]
      intro b hb
      obtain ⟨i, -, rfl⟩ := Multiset.mem_map.mp hb
      rw [mem_roots hgK0, IsRoot.def, eval_map_algebraMap]
      exact hroot i
    · rw [hm.natDegree_map, hn, Lagrange.natDegree_nodal, Finset.card_univ, Fintype.card_fin]
  -- the Vandermonde determinant
  set δ := (Matrix.vandermonde r).det with hδ
  have hδ0 : δ ≠ 0 := Matrix.det_vandermonde_ne_zero_iff.mpr hinj
  have hδq : δ ^ q = (-1) ^ n * δ := frob_det_vandermonde Φ.toRingHom q n hΦ β hβq
  -- the discriminant of `g` is `δ²`
  have hD : algebraMap F (AlgebraicClosure F) (discr g) = δ ^ 2 := by
    have e1 := resultant_deriv (degree_pos_of_irreducible hg)
    rw [hm.leadingCoeff, mul_one, hn] at e1
    have hpos : 0 < (Lagrange.nodal (univ : Finset (Fin (n + 1))) r).degree := by
      rw [← natDegree_pos_iff_degree_pos, Lagrange.natDegree_nodal, Finset.card_univ,
        Fintype.card_fin]
      omega
    have e2 := resultant_deriv hpos
    rw [Lagrange.natDegree_nodal, Finset.card_univ, Fintype.card_fin,
      (Lagrange.nodal_monic).leadingCoeff, mul_one, discr_nodal (n + 1) (by omega) r,
      ← Matrix.det_vandermonde] at e2
    have e3 := resultant_map_map g (derivative g) (n + 1) (n + 1 - 1)
      (algebraMap F (AlgebraicClosure F))
    rw [← derivative_map, hG, e2, e1, map_mul, map_pow, map_neg, map_one] at e3
    have hs : ((-1 : AlgebraicClosure F) ^ ((n + 1) * (n + 1 - 1) / 2)) ≠ 0 :=
      pow_ne_zero _ (neg_ne_zero.mpr one_ne_zero)
    exact (mul_left_cancel₀ hs e3).symm
  have hDne : discr g ≠ 0 := by
    intro h
    rw [h, map_zero] at hD
    exact pow_ne_zero 2 hδ0 hD.symm
  -- Euler's criterion
  have hqodd : q % 2 = 1 := FiniteField.odd_card_of_char_ne_two hF
  have hpow : discr g ^ (q / 2) = (-1) ^ n := by
    apply (algebraMap F (AlgebraicClosure F)).injective
    rw [map_pow, hD, ← pow_mul, map_pow, map_neg, map_one]
    have h2 : 2 * (q / 2) + 1 = q := by omega
    have h3 : δ ^ (2 * (q / 2)) * δ = (-1) ^ n * δ := by rw [← pow_succ, h2, hδq]
    exact mul_right_cancel₀ hδ0 h3
  have hχ := quadraticChar_eq_pow_of_char_ne_two' hF (discr g)
  rw [hpow] at hχ
  have hne : (-1 : F) ≠ 1 := Ring.neg_one_ne_one_of_char_ne_two hF
  have hgoal : (-1 : ℤ) ^ (g.natDegree + 1) = (-1) ^ n := by
    rw [hn, pow_add, pow_add]
    simp
  rw [hgoal]
  rcases quadraticChar_dichotomy hDne with h | h <;> rcases neg_one_pow_eq_or ℤ n with h' | h'
  · rw [h, h']
  · exfalso
    have h'' : (-1 : F) ^ n = -1 := by
      have := congrArg (Int.cast : ℤ → F) h'
      simpa using this
    rw [h, h''] at hχ
    simp at hχ
    exact hne hχ.symm
  · exfalso
    have h'' : (-1 : F) ^ n = 1 := by
      have := congrArg (Int.cast : ℤ → F) h'
      simpa using this
    rw [h, h''] at hχ
    simp at hχ
    exact hne hχ
  · rw [h, h']

end Irreducible

section Assembly

open UniqueFactorizationMonoid

variable {F : Type*} [Field F] [Fintype F] [DecidableEq F]

/-- A nonzero constant factor does not change the quadratic character of the discriminant. -/
theorem quadraticChar_discr_C_mul {c : F} (hc : c ≠ 0) (f : F[X]) :
    quadraticChar F (discr (C c * f)) = quadraticChar F (discr f) := by
  rcases Nat.eq_zero_or_pos f.natDegree with h0 | hpos
  · rw [eq_C_of_natDegree_eq_zero h0, ← C_mul, discr_C, discr_C]
  · rw [discr_C_mul hc hpos, map_mul, map_pow]
    have h2 : 2 * f.natDegree - 2 = 2 * (f.natDegree - 1) := by omega
    rw [h2, pow_mul, quadraticChar_sq_one hc, one_pow, one_mul]

/-- Stickelberger's theorem for an irreducible polynomial, monic or not. -/
theorem quadraticChar_discr_of_irreducible (hF : ringChar F ≠ 2) {p : F[X]}
    (hp : Irreducible p) : quadraticChar F (discr p) = (-1) ^ (p.natDegree + 1) := by
  have hl : p.leadingCoeff ≠ 0 := leadingCoeff_ne_zero.mpr hp.ne_zero
  have hmon : (C p.leadingCoeff⁻¹ * p).Monic :=
    monic_C_mul_of_mul_leadingCoeff_eq_one (inv_mul_cancel₀ hl)
  have hirr : Irreducible (C p.leadingCoeff⁻¹ * p) :=
    (irreducible_isUnit_mul (isUnit_C.mpr (IsUnit.mk0 _ (inv_ne_zero hl)))).mpr hp
  have hdeg : (C p.leadingCoeff⁻¹ * p).natDegree = p.natDegree :=
    natDegree_C_mul (inv_ne_zero hl)
  have hpe : C p.leadingCoeff * (C p.leadingCoeff⁻¹ * p) = p := by
    rw [← mul_assoc, ← C_mul, mul_inv_cancel₀ hl, C_1, one_mul]
  have h1 := quadraticChar_discr_C_mul hl (C p.leadingCoeff⁻¹ * p)
  rw [hpe] at h1
  rw [h1, quadraticChar_discr_of_irreducible_of_monic hF hirr hmon, hdeg]

/-- **Stickelberger's theorem in Swan's form** (Pellet's formula), for one finite field of odd
characteristic: the quadratic character of the discriminant of a squarefree polynomial `g` is
`(-1)^(deg g - r)`, `r` the number of irreducible factors of `g`. -/
def StickelbergerSwan (F : Type*) [Field F] [Fintype F] [DecidableEq F] : Prop :=
  ringChar F ≠ 2 → ∀ g : F[X], Squarefree g →
    quadraticChar F (discr g) = (-1) ^ (g.natDegree + Multiset.card (normalizedFactors g))

/-- Stickelberger's theorem in Swan's form holds for every finite field. -/
theorem stickelbergerSwan (F : Type*) [Field F] [Fintype F] [DecidableEq F] :
    StickelbergerSwan F := by
  intro hF g
  refine induction_on_coprime (P := fun g : F[X] => Squarefree g →
    quadraticChar F (discr g) = (-1) ^ (g.natDegree + Multiset.card (normalizedFactors g)))
    g ?_ ?_ ?_ ?_
  · intro h
    exact absurd h not_squarefree_zero
  · intro x hx _
    obtain ⟨c, hc, rfl⟩ := Polynomial.isUnit_iff.mp hx
    rw [discr_C, natDegree_C, normalizedFactors_of_isUnit hx, Multiset.card_zero, map_one]
    simp
  · intro p i hp hsq
    rcases i with _ | _ | i
    · rw [pow_zero, ← C_1, discr_C, natDegree_C, map_one, C_1, normalizedFactors_one,
        Multiset.card_zero]
      simp
    · rw [zero_add, pow_one, normalizedFactors_irreducible hp.irreducible,
        Multiset.card_singleton]
      exact quadraticChar_discr_of_irreducible hF hp.irreducible
    · exfalso
      have h := hsq p ⟨p ^ i, by ring⟩
      exact hp.not_isUnit h
  · intro x y hxy hx hy hsq
    have hx0 : x ≠ 0 := left_ne_zero_of_mul hsq.ne_zero
    have hy0 : y ≠ 0 := right_ne_zero_of_mul hsq.ne_zero
    have hxs := hsq.of_mul_left
    have hys := hsq.of_mul_right
    rw [normalizedFactors_mul hx0 hy0, Multiset.card_add, natDegree_mul hx0 hy0]
    rcases Nat.eq_zero_or_pos x.natDegree with hdx | hdx
    · obtain ⟨c, rfl⟩ := natDegree_eq_zero.mp hdx
      have hc : c ≠ 0 := fun h => hx0 (by rw [h, C_0])
      rw [quadraticChar_discr_C_mul hc, hy hys, natDegree_C,
        normalizedFactors_of_isUnit (isUnit_C.mpr (IsUnit.mk0 c hc)), Multiset.card_zero,
        zero_add, zero_add]
    rcases Nat.eq_zero_or_pos y.natDegree with hdy | hdy
    · obtain ⟨c, rfl⟩ := natDegree_eq_zero.mp hdy
      have hc : c ≠ 0 := fun h => hy0 (by rw [h, C_0])
      rw [mul_comm x (C c), quadraticChar_discr_C_mul hc, hx hxs, natDegree_C,
        normalizedFactors_of_isUnit (isUnit_C.mpr (IsUnit.mk0 c hc)), Multiset.card_zero,
        add_zero, add_zero]
    · rw [discr_mul hdx hdy, map_mul, map_mul,
        quadraticChar_sq_one' (resultant_ne_zero x y hxy.isCoprime), mul_one, hx hxs, hy hys,
        ← pow_add]
      congr 1
      ring

end Assembly

end GoldbachGaps.FunctionField
