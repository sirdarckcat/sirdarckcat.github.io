import GoldbachGaps.FunctionField.ParityDesert

/-!
# World 3 (`F_q[t]`): three mechanisms seen in the exhaustive enumerations

Members are the polynomials `N` of degree `n`, rows are the monic irreducibles `Q` of smaller degree, and a row
succeeds when `N - Q` is irreducible. `scripts/world3/` enumerates every member for `q = 3, 5, 7, 9`; the records
that are not generic are explained by the statements of this file.

## Cells are exactly equidistributed

* `card_monic_modByMonic_eq`: for `P` monic of degree at most `n` and `r` of degree below `deg P`, exactly
  `q^(n - deg P)` monic polynomials of degree `n` are `r` modulo `P`.
* `card_monic_cell`: the same for pairwise coprime monic moduli of total degree at most `n` with one residue each.
  This is the count that carries an error `± 1` in the integers (`Cap.card_good_sharing_le`).

## Symmetry: rows succeed in orbits

* `irreducible_sub_apply_iff`: if a ring automorphism `φ` fixes `N`, then `N - φ Q` is irreducible exactly when
  `N - Q` is.
* `irreducible_sub_comp_X_add_C_iff`: in particular for `N(t + c) = N(t)`: the rows `Q(t)` and `Q(t + c)` succeed
  together; `irreducible_comp_X_add_C_iff`, `natDegree_comp_X_add_C`, `monic_comp_X_add_C`: the translate of a row is
  a row of the same degree.

## Parity through the derivative

`discr (N - Q)` is a resultant with `N' - Q'`. Two extreme cases:

* `not_irreducible_of_derivative_eq_zero`: over a perfect field a polynomial with zero derivative is not
  irreducible; so a row with `Q' = N'` never succeeds (`not_irreducible_sub_of_derivative_eq`).
* `discr_of_derivative_eq_C`: if `f' = γ` is a non-zero constant and `n = deg f ≥ 2`, then
  `discr f = (-1)^(n(n-1)/2) · lc(f)^(n-2) · γ^n`.
* `parity_of_derivative_eq_C`: over a finite field of odd characteristic such an `f` is squarefree and the number
  `r` of its irreducible factors satisfies `(-1)^(n + r) = χ(-1)^(n(n-1)/2) · χ(lc f)^(n-2) · χ(γ)^n`.
* `not_irreducible_of_derivative_eq_C`: if moreover `n` is even and `χ(-1)^(n(n-1)/2) = 1`, `f` is not irreducible.
  For `N = G(t^p) + t² + c t + d` this applies to `N - Q` for every monic quadratic `Q` whose linear coefficient is
  not `c` (and the others have `Q' = N'`): every quadratic row fails at once. That is the record at `q = 9`, `n = 6`.
-/

namespace GoldbachGaps.FunctionField

open Polynomial

section Symmetry

/-- **Rows succeed in orbits.** If a ring automorphism fixes `N`, then `N - φ Q` is irreducible exactly when
`N - Q` is. -/
theorem irreducible_sub_apply_iff {R : Type*} [CommRing R] (φ : R ≃+* R) {N Q : R} (hN : φ N = N) :
    Irreducible (N - φ Q) ↔ Irreducible (N - Q) := by
  have h : φ (N - Q) = N - φ Q := by rw [map_sub, hN]
  rw [← h]
  exact MulEquiv.irreducible_iff φ.toMulEquiv

variable {F : Type*} [Field F]

theorem algEquivAevalXAddC_eq_comp (c : F) (p : F[X]) : algEquivAevalXAddC c p = p.comp (X + C c) := by
  rw [algEquivAevalXAddC_apply, comp_eq_aeval]

/-- The translate of an irreducible polynomial is irreducible. -/
theorem irreducible_comp_X_add_C_iff {Q : F[X]} (c : F) :
    Irreducible (Q.comp (X + C c)) ↔ Irreducible Q := by
  rw [← algEquivAevalXAddC_eq_comp]
  exact MulEquiv.irreducible_iff (algEquivAevalXAddC c).toRingEquiv.toMulEquiv

theorem natDegree_comp_X_add_C (Q : F[X]) (c : F) : (Q.comp (X + C c)).natDegree = Q.natDegree := by
  rw [natDegree_comp, natDegree_X_add_C, mul_one]

theorem monic_comp_X_add_C {Q : F[X]} (hQ : Q.Monic) (c : F) : (Q.comp (X + C c)).Monic :=
  hQ.comp_X_add_C c

/-- **Translation-invariant members.** If `N(t + c) = N(t)`, the rows `Q(t)` and `Q(t + c)` succeed together. -/
theorem irreducible_sub_comp_X_add_C_iff {N Q : F[X]} (c : F) (hN : N.comp (X + C c) = N) :
    Irreducible (N - Q.comp (X + C c)) ↔ Irreducible (N - Q) := by
  have h := irreducible_sub_apply_iff (algEquivAevalXAddC c).toRingEquiv (N := N) (Q := Q)
    (by
      show algEquivAevalXAddC c N = N
      rw [algEquivAevalXAddC_eq_comp, hN])
  have e : (algEquivAevalXAddC c).toRingEquiv Q = Q.comp (X + C c) := algEquivAevalXAddC_eq_comp c Q
  rwa [e] at h

end Symmetry

section Derivative

variable {F : Type*} [Field F]

/-- Over a perfect field, a polynomial with zero derivative is not irreducible. -/
theorem not_irreducible_of_derivative_eq_zero [PerfectField F] {f : F[X]} (hf : derivative f = 0) :
    ¬Irreducible f := by
  intro hirr
  have hsep : f.Separable := PerfectField.separable_of_irreducible hirr
  rw [separable_def, hf] at hsep
  exact hirr.not_isUnit (isCoprime_zero_right.mp hsep)

/-- A row with the derivative of `N` never succeeds. -/
theorem not_irreducible_sub_of_derivative_eq [PerfectField F] {N Q : F[X]}
    (h : derivative Q = derivative N) : ¬Irreducible (N - Q) :=
  not_irreducible_of_derivative_eq_zero (by rw [derivative_sub, h, sub_self])

/-- A polynomial whose derivative is a non-zero constant is squarefree. -/
theorem squarefree_of_derivative_eq_C {f : F[X]} {γ : F} (hγ : γ ≠ 0) (hf : derivative f = C γ) :
    Squarefree f := by
  apply Separable.squarefree
  rw [separable_def, hf]
  exact ⟨0, C γ⁻¹, by rw [zero_mul, zero_add, ← C_mul, inv_mul_cancel₀ hγ, C_1]⟩

/-- **The discriminant when the derivative is a non-zero constant.** If `f' = γ ≠ 0` and `n = deg f ≥ 2`, then
`discr f = (-1)^(n(n-1)/2) · lc(f)^(n-2) · γ^n`: it does not depend on the other coefficients of `f`. -/
theorem discr_of_derivative_eq_C {f : F[X]} {γ : F} (hγ : γ ≠ 0) (hf : derivative f = C γ)
    (hn : 2 ≤ f.natDegree) :
    discr f = (-1) ^ (f.natDegree * (f.natDegree - 1) / 2) * f.leadingCoeff ^ (f.natDegree - 2)
      * γ ^ f.natDegree := by
  have hQdeg : (-(C γ * X) : F[X]).natDegree = 1 := by
    rw [natDegree_neg, natDegree_C_mul_X γ hγ]
  have hQ' : derivative (-(C γ * X) : F[X]) = C (-γ) := by
    rw [derivative_neg, derivative_C_mul, derivative_X, mul_one, C_neg]
  have hQ'0 : derivative (-(C γ * X) : F[X]) ≠ 0 := by
    rw [hQ']
    exact C_ne_zero.mpr (neg_ne_zero.mpr hγ)
  have hN' : derivative (f - C γ * X) = 0 := by
    rw [derivative_sub, hf, derivative_C_mul, derivative_X, mul_one, sub_self]
  have hlt1 : (C γ * X : F[X]).natDegree < f.natDegree := by
    rw [natDegree_C_mul_X γ hγ]
    omega
  have hNdeg : (f - C γ * X).natDegree = f.natDegree := natDegree_sub_eq_left_of_natDegree_lt hlt1
  have hNlc : (f - C γ * X).leadingCoeff = f.leadingCoeff :=
    leadingCoeff_sub_of_degree_lt (degree_lt_degree hlt1)
  have hlt : (-(C γ * X) : F[X]).natDegree < (f - C γ * X).natDegree := by
    rw [hQdeg, hNdeg]
    omega
  have h := discr_sub_eq_resultant hN' hQ'0 hlt
  have e : f - C γ * X - -(C γ * X) = f := by ring
  rw [e, hNdeg, hNlc, hQ', natDegree_C, resultant_C_zero_left] at h
  rw [h, Nat.mul_zero, Nat.add_zero, Nat.sub_zero, pow_add, neg_pow γ]
  have hs : (-1 : F) ^ f.natDegree * (-1) ^ f.natDegree = 1 := by
    rw [← mul_pow]
    simp
  linear_combination ((-1 : F) ^ (f.natDegree * (f.natDegree - 1) / 2) * f.leadingCoeff ^ (f.natDegree - 2)
    * γ ^ f.natDegree) * hs

end Derivative

section FiniteField

open UniqueFactorizationMonoid

variable {F : Type*} [Field F] [Fintype F] [DecidableEq F]

/-- **Parity when the derivative is a non-zero constant.** Over a finite field of odd characteristic, with
`n = deg f ≥ 2`, `f' = γ ≠ 0` and `r` the number of irreducible factors of `f`:
`(-1)^(n + r) = χ(-1)^(n(n-1)/2) · χ(lc f)^(n-2) · χ(γ)^n`. -/
theorem parity_of_derivative_eq_C (hF : ringChar F ≠ 2) {f : F[X]} {γ : F} (hγ : γ ≠ 0)
    (hf : derivative f = C γ) (hn : 2 ≤ f.natDegree) :
    (-1 : ℤ) ^ (f.natDegree + Multiset.card (normalizedFactors f)) =
      quadraticChar F (-1) ^ (f.natDegree * (f.natDegree - 1) / 2)
        * quadraticChar F f.leadingCoeff ^ (f.natDegree - 2) * quadraticChar F γ ^ f.natDegree := by
  have h1 := stickelbergerSwan F hF f (squarefree_of_derivative_eq_C hγ hf)
  rw [← h1, discr_of_derivative_eq_C hγ hf hn, map_mul, map_mul, map_pow, map_pow, map_pow]

/-- If moreover the degree is even and `χ(-1)^(n(n-1)/2) = 1` (for instance `-1` a square, or `4 ∣ n`), the number
of irreducible factors is even. -/
theorem even_card_factors_of_derivative_eq_C (hF : ringChar F ≠ 2) {f : F[X]} {γ : F} (hγ : γ ≠ 0)
    (hf : derivative f = C γ) (hn : 2 ≤ f.natDegree) (heven : Even f.natDegree)
    (hsign : quadraticChar F (-1) ^ (f.natDegree * (f.natDegree - 1) / 2) = 1) :
    Even (Multiset.card (normalizedFactors f)) := by
  have h := parity_of_derivative_eq_C hF hγ hf hn
  have hlam : f.leadingCoeff ≠ 0 := by
    apply leadingCoeff_ne_zero.mpr
    rintro rfl
    simp at hn
  have hsq : ∀ a : F, a ≠ 0 → ∀ k, Even k → quadraticChar F a ^ k = 1 := by
    intro a ha k hk
    obtain ⟨j, hj⟩ := hk
    rw [hj, ← two_mul, pow_mul, quadraticChar_sq_one ha, one_pow]
  have hev2 : Even (f.natDegree - 2) := by
    obtain ⟨j, hj⟩ := heven
    exact ⟨j - 1, by omega⟩
  rw [hsign, hsq _ hlam _ hev2, hsq _ hγ _ heven, mul_one, mul_one, pow_add, heven.neg_one_pow, one_mul] at h
  exact (neg_one_pow_eq_one_iff_even (by norm_num)).mp h

/-- ... and so the polynomial is not irreducible. -/
theorem not_irreducible_of_derivative_eq_C (hF : ringChar F ≠ 2) {f : F[X]} {γ : F} (hγ : γ ≠ 0)
    (hf : derivative f = C γ) (hn : 2 ≤ f.natDegree) (heven : Even f.natDegree)
    (hsign : quadraticChar F (-1) ^ (f.natDegree * (f.natDegree - 1) / 2) = 1) :
    ¬Irreducible f := by
  intro hirr
  have h := even_card_factors_of_derivative_eq_C hF hγ hf hn heven hsign
  rw [normalizedFactors_irreducible hirr, Multiset.card_singleton] at h
  exact absurd h (by decide)

/-- The same for a row: if `N' - Q'` is a non-zero constant, `deg (N - Q)` is even and at least 2 and
`χ(-1)^(n(n-1)/2) = 1`, the row `Q` fails. -/
theorem not_irreducible_sub_of_derivative_sub_eq_C (hF : ringChar F ≠ 2) {N Q : F[X]} {γ : F} (hγ : γ ≠ 0)
    (h : derivative N - derivative Q = C γ) (hn : 2 ≤ (N - Q).natDegree) (heven : Even (N - Q).natDegree)
    (hsign : quadraticChar F (-1) ^ ((N - Q).natDegree * ((N - Q).natDegree - 1) / 2) = 1) :
    ¬Irreducible (N - Q) :=
  not_irreducible_of_derivative_eq_C hF hγ (by rw [derivative_sub, h]) hn heven hsign

end FiniteField

section Cells

variable {F : Type*} [Field F] [Fintype F]

/-- **A residue class holds exactly `q^(n - deg P)` monic polynomials of degree `n`.** -/
theorem card_monic_modByMonic_eq {P : F[X]} (hP : P.Monic) (r : F[X]) (hr : r.degree < P.degree) {n : ℕ}
    (hn : P.natDegree ≤ n) :
    Nat.card {M : F[X] // M.Monic ∧ M.natDegree = n ∧ M %ₘ P = r} =
      Fintype.card F ^ (n - P.natDegree) := by
  classical
  set d := n - P.natDegree with hd
  have hcard : Nat.card (degreeLT F d) = Fintype.card F ^ d := by
    rw [Nat.card_congr (degreeLTEquiv F d).toEquiv, Nat.card_fun, Nat.card_eq_fintype_card,
      Nat.card_eq_fintype_card, Fintype.card_fin]
  rw [← hcard]
  symm
  have hmonicA : ∀ B : degreeLT F d, (X ^ d + (B : F[X])).Monic := fun B =>
    monic_X_pow_add (mem_degreeLT.mp B.2)
  have hdegA : ∀ B : degreeLT F d, (X ^ d + (B : F[X])).natDegree = d := fun B => by
    rw [natDegree_add_eq_left_of_degree_lt (by rw [degree_X_pow]; exact mem_degreeLT.mp B.2), natDegree_X_pow]
  have hPA : ∀ B : degreeLT F d, (P * (X ^ d + (B : F[X]))).natDegree = n := fun B => by
    rw [hP.natDegree_mul (hmonicA B), hdegA B, hd]
    omega
  have hrlt : ∀ B : degreeLT F d, r.degree < (P * (X ^ d + (B : F[X]))).degree := fun B => by
    refine lt_of_lt_of_le hr ?_
    rw [degree_eq_natDegree hP.ne_zero, degree_eq_natDegree (hP.mul (hmonicA B)).ne_zero, hPA B]
    exact_mod_cast hn
  refine Nat.card_congr (Equiv.ofBijective
    (fun B : degreeLT F d => (⟨r + P * (X ^ d + (B : F[X])), ?_, ?_, ?_⟩ :
      {M : F[X] // M.Monic ∧ M.natDegree = n ∧ M %ₘ P = r})) ⟨?_, ?_⟩)
  · exact (hP.mul (hmonicA B)).add_of_right (hrlt B)
  · rw [natDegree_add_eq_right_of_degree_lt (hrlt B), hPA B]
  · exact (div_modByMonic_unique _ r hP ⟨rfl, hr⟩).2
  · intro B₁ B₂ h
    have h' : r + P * (X ^ d + (B₁ : F[X])) = r + P * (X ^ d + (B₂ : F[X])) := congrArg Subtype.val h
    have h'' := mul_left_cancel₀ hP.ne_zero (add_left_cancel h')
    exact Subtype.ext (add_left_cancel h'')
  · rintro ⟨M, hM, hMn, hMr⟩
    have hdeg : P.degree ≤ M.degree := by
      rw [degree_eq_natDegree hP.ne_zero, degree_eq_natDegree hM.ne_zero, hMn]
      exact_mod_cast hn
    have hAlc : (M /ₘ P).leadingCoeff = 1 := by
      rw [leadingCoeff_divByMonic_of_monic hP hdeg, hM.leadingCoeff]
    have hAdeg : (M /ₘ P).natDegree = d := by rw [natDegree_divByMonic M hP, hMn]
    have hA0 : M /ₘ P ≠ 0 := by
      intro h0
      rw [h0, leadingCoeff_zero] at hAlc
      exact zero_ne_one hAlc
    have hBlt : (M /ₘ P - X ^ d).degree < (d : WithBot ℕ) := by
      have h1 : (M /ₘ P).degree = (X ^ d : F[X]).degree := by
        rw [degree_X_pow, degree_eq_natDegree hA0, hAdeg]
      have h2 := degree_sub_lt_left h1 hA0 (by rw [hAlc, leadingCoeff_X_pow])
      rwa [degree_eq_natDegree hA0, hAdeg] at h2
    refine ⟨⟨M /ₘ P - X ^ d, mem_degreeLT.mpr hBlt⟩, Subtype.ext ?_⟩
    show r + P * (X ^ d + (M /ₘ P - X ^ d)) = M
    rw [add_sub_cancel, ← hMr]
    exact modByMonic_add_div M P

/-- Chinese remainders for pairwise coprime polynomials: some polynomial is congruent to `r i` modulo `P i` for
every `i` of a finite set. -/
theorem exists_forall_dvd_sub {F : Type*} [Field F] {ι : Type*} (s : Finset ι) (P r : ι → F[X])
    (hcop : (s : Set ι).Pairwise fun i j => IsCoprime (P i) (P j)) :
    ∃ r₀ : F[X], ∀ i ∈ s, P i ∣ r₀ - r i := by
  classical
  induction s using Finset.induction_on with
  | empty => exact ⟨0, by simp⟩
  | insert a s ha ih =>
    obtain ⟨r₀, hr₀⟩ := ih (hcop.mono (by simp))
    have hc : IsCoprime (P a) (∏ i ∈ s, P i) :=
      IsCoprime.prod_right fun i hi =>
        hcop (by simp) (by simp [hi]) (fun h => ha (h ▸ hi))
    obtain ⟨u, v, huv⟩ := hc
    refine ⟨r₀ * (u * P a) + r a * (v * ∏ i ∈ s, P i), ?_⟩
    intro i hi
    rcases Finset.mem_insert.mp hi with rfl | his
    · have e : r₀ * (u * P i) + r i * (v * ∏ j ∈ s, P j) - r i = P i * (u * (r₀ - r i)) := by
        linear_combination r i * huv
      rw [e]
      exact dvd_mul_right _ _
    · have hdvd : P i ∣ ∏ j ∈ s, P j := Finset.dvd_prod_of_mem P his
      have e : r₀ * (u * P a) + r a * (v * ∏ j ∈ s, P j) - r i =
          (r₀ - r i) + (∏ j ∈ s, P j) * (v * (r a - r₀)) := by
        linear_combination r₀ * huv
      rw [e]
      exact dvd_add (hr₀ i his) (dvd_mul_of_dvd_left hdvd _)

/-- **Cells are exactly equidistributed.** For pairwise coprime monic moduli of total degree at most `n`, with a
residue of smaller degree for each, exactly `q^(n - total degree)` monic polynomials of degree `n` have all
these residues. -/
theorem card_monic_cell {ι : Type*} (s : Finset ι) (P r : ι → F[X]) (hP : ∀ i ∈ s, (P i).Monic)
    (hcop : (s : Set ι).Pairwise fun i j => IsCoprime (P i) (P j))
    (hr : ∀ i ∈ s, (r i).degree < (P i).degree) {n : ℕ} (hn : ∑ i ∈ s, (P i).natDegree ≤ n) :
    Nat.card {M : F[X] // M.Monic ∧ M.natDegree = n ∧ ∀ i ∈ s, M %ₘ P i = r i} =
      Fintype.card F ^ (n - ∑ i ∈ s, (P i).natDegree) := by
  classical
  obtain ⟨r₀, hr₀⟩ := exists_forall_dvd_sub s P r hcop
  have hprod : (∏ i ∈ s, P i).Monic := monic_prod_of_monic s P hP
  have hproddeg : (∏ i ∈ s, P i).natDegree = ∑ i ∈ s, (P i).natDegree := natDegree_prod_of_monic s P hP
  have hiff : ∀ M : F[X], (∀ i ∈ s, M %ₘ P i = r i) ↔ M %ₘ (∏ i ∈ s, P i) = r₀ %ₘ (∏ i ∈ s, P i) := by
    intro M
    constructor
    · intro h
      have hdvd : ∏ i ∈ s, P i ∣ M - r₀ := by
        refine Finset.prod_dvd_of_coprime hcop fun i hi => ?_
        have h1 : P i ∣ M - r i := by
          rw [← modByMonic_eq_zero_iff_dvd (hP i hi), sub_modByMonic, h i hi,
            (modByMonic_eq_self_iff (hP i hi)).mpr (hr i hi), sub_self]
        have e : M - r₀ = (M - r i) - (r₀ - r i) := by ring
        rw [e]
        exact dvd_sub h1 (hr₀ i hi)
      have h2 := (modByMonic_eq_zero_iff_dvd hprod).mpr hdvd
      rw [sub_modByMonic] at h2
      exact sub_eq_zero.mp h2
    · intro h i hi
      have hdvd : ∏ j ∈ s, P j ∣ M - r₀ := by
        rw [← modByMonic_eq_zero_iff_dvd hprod, sub_modByMonic, h, sub_self]
      have h1 : P i ∣ M - r i := by
        have e : M - r i = (M - r₀) + (r₀ - r i) := by ring
        rw [e]
        exact dvd_add ((Finset.dvd_prod_of_mem P hi).trans hdvd) (hr₀ i hi)
      have h2 := (modByMonic_eq_zero_iff_dvd (hP i hi)).mpr h1
      rw [sub_modByMonic, (modByMonic_eq_self_iff (hP i hi)).mpr (hr i hi)] at h2
      exact sub_eq_zero.mp h2
  have hcard := card_monic_modByMonic_eq hprod (r₀ %ₘ ∏ i ∈ s, P i) (degree_modByMonic_lt r₀ hprod)
    (n := n) (by rw [hproddeg]; exact hn)
  rw [hproddeg] at hcard
  rw [← hcard]
  exact Nat.card_congr (Equiv.subtypeEquivRight fun M => by rw [hiff M])

end Cells

end GoldbachGaps.FunctionField
