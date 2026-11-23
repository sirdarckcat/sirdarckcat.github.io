import GoldbachGaps.FunctionField.ParityDesert

/-!
# The desert without a degree hypothesis

`desert` (in `ParityDesert`) assumes `deg Q < deg N`. For `N = c · V^p` with `V` divisible by
every irreducible polynomial of degree at most `J ≥ 1` this is automatic: `V` is then divisible
by `x^(q^J) - x`, so `deg V ≥ q^J > J + 1`.

* `dvd_of_squarefree_of_irreducible_dvd`: a squarefree polynomial all of whose irreducible
  factors divide `b` divides `b`.
* `card_pow_le_natDegree`: `q^J ≤ deg V`.
* `natDegree_lt_natDegree_desert`: `J + 1 < deg (c · V^p)`.
* `desert_of_one_le`: the desert as the research session states it: for `J ≥ 1`, `N - Q` is not
  irreducible for every monic irreducible `Q` of degree at most `J + 1`, the degree `J + 1`
  being allowed when `p` does not divide it.

For `J = 0` the statement is false: `V = 1`, `N = c` and `N - Q` is linear for `Q` linear.
-/

namespace GoldbachGaps.FunctionField

open Polynomial UniqueFactorizationMonoid

/-- A squarefree polynomial all of whose irreducible factors divide `b` divides `b`. -/
theorem dvd_of_squarefree_of_irreducible_dvd {F : Type*} [Field F] [DecidableEq F] {a b : F[X]}
    (ha : Squarefree a) (hb : b ≠ 0) (h : ∀ π : F[X], Irreducible π → π ∣ a → π ∣ b) : a ∣ b := by
  have ha0 : a ≠ 0 := ha.ne_zero
  rw [dvd_iff_normalizedFactors_le_normalizedFactors ha0 hb,
    Multiset.le_iff_subset ((squarefree_iff_nodup_normalizedFactors ha0).mp ha)]
  intro π hπ
  have hirr : Irreducible π := irreducible_of_normalized_factor π hπ
  have hπb : π ∣ b := h π hirr (dvd_of_mem_normalizedFactors hπ)
  exact (mem_normalizedFactors_iff' hb).mpr ⟨hirr, normalize_normalized_factor π hπ, hπb⟩

section FiniteField

variable {F : Type*} [Field F] [Fintype F] [DecidableEq F]

/-- If `V ≠ 0` is divisible by every irreducible polynomial of degree at most `J ≥ 1`, then
`x^(q^J) - x` divides `V`, so `q^J ≤ deg V`. -/
theorem card_pow_le_natDegree {V : F[X]} {J : ℕ} (hJ : 1 ≤ J) (hV0 : V ≠ 0)
    (hV : ∀ π : F[X], Irreducible π → π.natDegree ≤ J → π ∣ V) :
    Fintype.card F ^ J ≤ V.natDegree := by
  have : CharP F (ringChar F) := ringChar.charP F
  have hq1 : 1 < Fintype.card F := Fintype.one_lt_card
  have hqJ : 1 < Fintype.card F ^ J := Nat.one_lt_pow (by omega) hq1
  have hpq : ringChar F ∣ Fintype.card F ^ J := by
    have h0 : ((Fintype.card F : ℕ) : F) = 0 := Nat.cast_card_eq_zero F
    exact ((CharP.cast_eq_zero_iff F (ringChar F) _).mp h0).trans (dvd_pow_self _ (by omega))
  have hsq : Squarefree (X ^ (Fintype.card F ^ J) - X : F[X]) :=
    (galois_poly_separable (ringChar F) _ hpq).squarefree
  have hdvd : (X ^ (Fintype.card F ^ J) - X : F[X]) ∣ V := by
    refine dvd_of_squarefree_of_irreducible_dvd hsq hV0 (fun π hπ hπd => hV π hπ ?_)
    have hπd' : π ∣ X ^ Nat.card F ^ J - X := by
      rw [Nat.card_eq_fintype_card]
      exact hπd
    exact Nat.le_of_dvd (by omega) (hπ.natDegree_dvd_of_dvd_X_pow_card_pow_sub_X hπd')
  have h := natDegree_le_of_dvd hdvd hV0
  rwa [natDegree_X_pow_sub_X hqJ] at h

/-- `J + 1 < deg (c · V^p)` for `V` monic and divisible by every irreducible polynomial of
degree at most `J ≥ 1`, and `c ≠ 0`. -/
theorem natDegree_lt_natDegree_desert {V : F[X]} {J : ℕ} {c : F} (hJ : 1 ≤ J) (hVm : V.Monic)
    (hV : ∀ π : F[X], Irreducible π → π.natDegree ≤ J → π ∣ V) (hc : c ≠ 0) :
    J + 1 < (C c * V ^ ringChar F).natDegree := by
  have : CharP F (ringChar F) := ringChar.charP F
  have hp : (ringChar F).Prime := CharP.char_is_prime F (ringChar F)
  have hdeg : (C c * V ^ ringChar F).natDegree = ringChar F * V.natDegree := by
    rw [natDegree_C_mul hc, hVm.natDegree_pow]
  have h1 : Fintype.card F ^ J ≤ V.natDegree := card_pow_le_natDegree hJ hVm.ne_zero hV
  have h2 : 2 ^ J ≤ Fintype.card F ^ J := Nat.pow_le_pow_left Fintype.one_lt_card J
  have h3 : J < 2 ^ J := Nat.lt_two_pow_self
  have h4 : 2 * V.natDegree ≤ ringChar F * V.natDegree :=
    Nat.mul_le_mul_right _ hp.two_le
  rw [hdeg]
  omega

/-- **The desert, for `J ≥ 1`, with no condition on degrees other than `deg Q ≤ J + 1`.** Over a
finite field of odd characteristic `p` with a square number of elements, let `V` be monic and
divisible by every irreducible polynomial of degree at most `J` (for instance their product),
`c` a non-square, and `N = c · V^p`. Then `N - Q` is not irreducible for every monic irreducible
`Q` of degree at most `J + 1`, the degree `J + 1` being allowed when `p` does not divide it. -/
theorem desert_of_one_le (hF : ringChar F ≠ 2) (hq : IsSquare (Fintype.card F)) {V : F[X]}
    {J : ℕ} {c : F} (hJ : 1 ≤ J) (hVm : V.Monic)
    (hV : ∀ π : F[X], Irreducible π → π.natDegree ≤ J → π ∣ V) (hc : ¬IsSquare c)
    {Q : F[X]} (hQ : Q.Monic) (hQi : Irreducible Q) (hQJ : Q.natDegree ≤ J + 1)
    (hdeg : Q.natDegree ≤ J ∨ (Q.natDegree : F) ≠ 0) :
    ¬Irreducible (C c * V ^ ringChar F - Q) := by
  have hc0 : c ≠ 0 := fun h => hc (h ▸ IsSquare.zero)
  exact desert hF hq hVm hV hc hQ hQi hQJ hdeg
    (lt_of_le_of_lt hQJ (natDegree_lt_natDegree_desert hJ hVm hV hc0))

end FiniteField

end GoldbachGaps.FunctionField
