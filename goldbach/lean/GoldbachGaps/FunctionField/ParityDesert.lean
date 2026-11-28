import GoldbachGaps.FunctionField.Stickelberger

/-!
# A parity desert over `F_q[x]`

Toy setting for the Goldbach-gap problem: polynomials over a finite field in place of integers,
monic irreducible polynomials `Q` of small degree in place of the small primes `q`. The analogue
of "`N - q` is composite for every prime `q` below a bound" is "`N - Q` is reducible for every
monic irreducible `Q` of degree below a bound".

The first result (`discr_sub`) holds over any field. If `N' = 0` (in characteristic `p`: `N` is a
polynomial in `x^p`), `Q` is monic of degree `d < n = deg N` with `d ≠ 0` in the field, and every
irreducible factor of `Q'` divides `N`, then

  `discr (N - Q) = (-1)^(n(n-1)/2 + nd + (d-1) + d(d-1)/2) · λ^(n-d-1) · d^(n-d) · discr Q`,

`λ` the leading coefficient of `N`. So the discriminant of `N - Q` depends on `N` only through
`n` and `λ`.

Over a finite field of odd characteristic the quadratic character of a discriminant is the
parity of the number of irreducible factors (Stickelberger 1897, Swan 1962; Pellet's formula),
proved in `GoldbachGaps.FunctionField.Stickelberger`. With it, unconditionally:

* `parity_card_factors`: `N - Q` is squarefree and the parity of the number of its irreducible
  factors is given by `n`, `d` and the quadratic characters of `-1`, `λ` and `d`;
* `not_irreducible_sub`: if the field has a square number of elements and `λ` is not a square,
  `N - Q` is not irreducible, although no factor is exhibited;
* `desert`: for `V` monic and divisible by every irreducible of degree at most `J`, and `c` a
  non-square, `N = c · V^p` has `N - Q` reducible for every monic irreducible `Q` of degree at
  most `J + 1` (degree `J + 1` only if `p ∤ J + 1`).

The condition `d ≠ 0` in the field is not needed. With `e` and `ℓ` the degree and the leading
coefficient of `Q'` (so `e = d - 1`, `ℓ = d` when `p ∤ d`), `discr_sub_general` reads
`discr (N - Q) = (-1)^(n(n-1)/2 + n + ne + e + ed + d(d-1)/2) · λ^(n-2-e) · ℓ^(n-d) · discr Q`,
and over a field with a square number of elements and for a non-square `λ` the number of
irreducible factors of `N - Q` is even exactly when `(-1)^(d+1+e) χ(ℓ)^(n-d) = 1`
(`even_card_factors_iff`). This decides every row, including the degrees divisible by the
characteristic, where about half of the rows are killed (`desert_general`).

The desert is larger than the degrees up to `J + 1`. The hypothesis is only that every
irreducible factor of `Q'` divides `N`, so `N = c · V^p` kills every row, of any degree `d`
below `deg N` with `p ∤ d`, whose derivative has no irreducible factor of degree above `J`
(`desert_smooth`): a positive proportion of the rows of each such degree, and all but about
`1 / (J + 1)` of those of degree `J + 2`. For `p ∣ d` the rows killed are those that also meet
the sign criterion above (`desert_smooth_general`).

The statement and its numerical confirmation are the research session's
(`goldbach/sublinear/README.md`, Result 1).
-/

namespace GoldbachGaps.FunctionField

open Polynomial

section AnyField

variable {F : Type*} [Field F]

/-- If `h₁` and `h₂` agree at every root of `g` (every irreducible factor of `g` divides
`h₁ - h₂`), the resultants of `g` with `h₁` and with `h₂` differ only by the power of the
leading coefficient of `g` that accounts for the formal degrees. -/
theorem resultant_congr_of_roots {g h₁ h₂ : F[X]} {n₁ n₂ : ℕ} (h1 : h₁.natDegree ≤ n₁)
    (h2 : h₂.natDegree ≤ n₂) (hn : n₂ ≤ n₁)
    (hroots : ∀ π : F[X], Irreducible π → π ∣ g → π ∣ h₁ - h₂) :
    resultant g h₁ g.natDegree n₁ =
      g.leadingCoeff ^ (n₁ - n₂) * resultant g h₂ g.natDegree n₂ := by
  let φ : F →+* AlgebraicClosure F := algebraMap F (AlgebraicClosure F)
  apply φ.injective
  rw [map_mul, map_pow, ← resultant_map_map, ← resultant_map_map]
  have hdeg : (g.map φ).natDegree = g.natDegree := natDegree_map φ
  have hsplit : (g.map φ).Splits := IsAlgClosed.splits _
  have e1 := resultant_eq_prod_eval (g.map φ) (h₁.map φ) n₁ (natDegree_map_le.trans h1) hsplit
  have e2 := resultant_eq_prod_eval (g.map φ) (h₂.map φ) n₂ (natDegree_map_le.trans h2) hsplit
  rw [hdeg] at e1 e2
  rw [e1, e2, leadingCoeff_map]
  have hev : (g.map φ).roots.map (h₁.map φ).eval = (g.map φ).roots.map (h₂.map φ).eval := by
    refine Multiset.map_congr rfl fun b hb => ?_
    have hg0 : g.map φ ≠ 0 := ne_zero_of_mem_roots hb
    have hbg : aeval b g = 0 := by
      have := (mem_roots hg0).mp hb
      rwa [IsRoot.def, eval_map_algebraMap] at this
    have hint : IsIntegral F b := Algebra.IsIntegral.isIntegral b
    have hdvd := hroots (minpoly F b) (minpoly.irreducible hint) (minpoly.dvd F b hbg)
    have h0 : aeval b (h₁ - h₂) = 0 := by
      obtain ⟨c, hc⟩ := hdvd
      rw [hc, map_mul, minpoly.aeval, zero_mul]
    rw [map_sub, sub_eq_zero] at h0
    rw [eval_map_algebraMap, eval_map_algebraMap]
    exact h0
  rw [hev, ← mul_assoc, ← pow_add, Nat.sub_add_cancel hn]

/-- The derivative of a monic polynomial whose degree is not zero in the field has degree one
less and leading coefficient the degree. -/
theorem natDegree_derivative_of_monic {Q : F[X]} (hQ : Q.Monic) (hd : (Q.natDegree : F) ≠ 0) :
    (derivative Q).natDegree = Q.natDegree - 1 ∧
      (derivative Q).leadingCoeff = (Q.natDegree : F) := by
  have hd1 : 1 ≤ Q.natDegree := by
    rcases Nat.eq_zero_or_pos Q.natDegree with h | h
    · rw [h] at hd
      simp at hd
    · exact h
  have hc : (derivative Q).coeff (Q.natDegree - 1) = (Q.natDegree : F) := by
    rw [coeff_derivative, Nat.sub_add_cancel hd1, hQ.coeff_natDegree, one_mul]
    have : ((Q.natDegree - 1 : ℕ) : F) + 1 = (Q.natDegree : F) := by
      rw [← Nat.cast_succ, Nat.succ_eq_add_one, Nat.sub_add_cancel hd1]
    exact this
  have hdeg : (derivative Q).natDegree = Q.natDegree - 1 :=
    le_antisymm (natDegree_derivative_le Q) (le_natDegree_of_ne_zero (by rw [hc]; exact hd))
  exact ⟨hdeg, by rw [leadingCoeff, hdeg, hc]⟩

/-- The general discriminant identity with every degree and leading coefficient named: `e`
and `l` are the degree and the leading coefficient of `Q'`. -/
theorem discr_sub_general_aux {N Q : F[X]} {n d e : ℕ} {lam l : F} (hNn : N.natDegree = n)
    (hQd : Q.natDegree = d) (hNl : N.leadingCoeff = lam)
    (hQe : (derivative Q).natDegree = e) (hQl : (derivative Q).leadingCoeff = l)
    (hQ : Q.Monic) (hN : derivative N = 0) (hQ' : derivative Q ≠ 0) (hlt : d < n)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N) :
    discr (N - Q) =
      (-1) ^ (n * (n - 1) / 2 + n + n * e + e + e * d + d * (d - 1) / 2)
        * lam ^ (n - 2 - e) * l ^ (n - d) * discr Q := by
  have hd0 : Q.natDegree ≠ 0 := by
    intro h0
    apply hQ'
    rw [eq_C_of_natDegree_eq_zero h0, derivative_C]
  have hd1 : 1 ≤ d := by
    rw [← hQd]
    exact Nat.one_le_iff_ne_zero.mpr hd0
  have hed : e < d := by
    rw [← hQe, ← hQd]
    exact natDegree_derivative_lt hd0
  have hN0 : N ≠ 0 := by
    intro h
    rw [h, natDegree_zero] at hNn
    omega
  have hlam0 : lam ≠ 0 := by
    rw [← hNl]
    exact leadingCoeff_ne_zero.mpr hN0
  have hlt' : Q.natDegree < N.natDegree := by rw [hQd, hNn]; exact hlt
  -- the polynomial `f = N - Q`
  have hfn : (N - Q).natDegree = n := by
    rw [natDegree_sub_eq_left_of_natDegree_lt hlt', hNn]
  have hfl : (N - Q).leadingCoeff = lam := by
    rw [leadingCoeff_sub_of_degree_lt (degree_lt_degree hlt'), hNl]
  have hfc : (N - Q).coeff n = lam := by
    rw [← hfl, leadingCoeff, hfn]
  have hfpos : 0 < (N - Q).degree := by
    rw [← natDegree_pos_iff_degree_pos, hfn]
    omega
  have hfd : derivative (N - Q) = C (-1 : F) * derivative Q := by
    rw [derivative_sub, hN, zero_sub, C_neg, C_1, neg_one_mul]
  have hQpos : 0 < Q.degree := by
    rw [← natDegree_pos_iff_degree_pos, hQd]
    exact hd1
  have hQc : Q.coeff d = 1 := by
    rw [← hQd]
    exact hQ.coeff_natDegree
  -- the chain of resultants
  have eA : resultant (N - Q) (derivative (N - Q)) n (n - 1) =
      (-1) ^ (n * (n - 1) / 2) * lam * discr (N - Q) := by
    have h := resultant_deriv hfpos
    rwa [hfn, hfl] at h
  have hk : n - 1 = e + (n - 1 - e) := by omega
  have eB0 := resultant_add_right_deg (N - Q) (derivative Q) n e (n - 1 - e) (le_of_eq hQe)
  rw [← hk, hfc] at eB0
  have eB : resultant (N - Q) (derivative (N - Q)) n (n - 1) =
      (-1) ^ n * (lam ^ (n - 1 - e) * ((-1) ^ (n * e) *
        resultant (derivative Q) (N - Q) e n)) := by
    rw [hfd, resultant_C_mul_right, eB0, resultant_comm (N - Q) (derivative Q) n e]
  have eC : resultant (derivative Q) (N - Q) e n =
      l ^ (n - d) * resultant (derivative Q) (C (-1 : F) * Q) e d := by
    have h := resultant_congr_of_roots (g := derivative Q) (h₁ := N - Q) (h₂ := C (-1 : F) * Q)
      (n₁ := n) (n₂ := d) (le_of_eq hfn) ((natDegree_C_mul_le _ _).trans (le_of_eq hQd)) hlt.le
      (fun π hπ hπd => by
        have : N - Q - C (-1 : F) * Q = N := by
          rw [C_neg, C_1]
          ring
        rw [this]
        exact hrad π hπ hπd)
    rw [hQe, hQl] at h
    exact h
  have eD : resultant (derivative Q) (C (-1 : F) * Q) e d =
      (-1) ^ e * ((-1) ^ (e * d) * resultant Q (derivative Q) d e) := by
    rw [resultant_C_mul_right, resultant_comm (derivative Q) Q e d]
  have eE : resultant Q (derivative Q) d e = (-1) ^ (d * (d - 1) / 2) * discr Q := by
    have h := resultant_deriv hQpos
    rw [hQd, hQ.leadingCoeff, mul_one] at h
    have hk2 : d - 1 = e + (d - 1 - e) := by omega
    have h2 := resultant_add_right_deg Q (derivative Q) d e (d - 1 - e) (le_of_eq hQe)
    rw [← hk2, hQc, one_pow, one_mul] at h2
    rw [← h2]
    exact h
  -- signs
  have hs3 : (-1 : F) ^ (n * (n - 1) / 2) * (-1) ^ (n * (n - 1) / 2) = 1 := by
    rw [← mul_pow]
    simp
  have hpow : lam ^ (n - 1 - e) = lam ^ (n - 2 - e) * lam := by
    rw [← pow_succ]
    congr 1
    omega
  have key : (-1 : F) ^ (n * (n - 1) / 2) * lam * discr (N - Q) =
      (-1) ^ n * (lam ^ (n - 1 - e) * ((-1) ^ (n * e) * (l ^ (n - d) *
        ((-1) ^ e * ((-1) ^ (e * d) * ((-1) ^ (d * (d - 1) / 2) * discr Q)))))) := by
    rw [← eA, eB, eC, eD, eE]
  apply mul_left_cancel₀ hlam0
  rw [pow_add, pow_add, pow_add, pow_add, pow_add]
  linear_combination (-1 : F) ^ (n * (n - 1) / 2) * key - lam * discr (N - Q) * hs3
    + (-1 : F) ^ (n * (n - 1) / 2) * (-1) ^ n * (-1) ^ (n * e) * (-1) ^ e * (-1) ^ (e * d)
        * (-1) ^ (d * (d - 1) / 2) * l ^ (n - d) * discr Q * hpow

/-- The discriminant of `N - Q` for `N' = 0`, with no condition on the roots of `Q'`, in
terms of named degrees. -/
theorem discr_sub_eq_resultant_aux {N Q : F[X]} {n e : ℕ} {lam : F} (hNn : N.natDegree = n)
    (hNl : N.leadingCoeff = lam) (hQe : (derivative Q).natDegree = e)
    (hN : derivative N = 0) (hQ' : derivative Q ≠ 0) (hlt : Q.natDegree < n) :
    discr (N - Q) =
      (-1) ^ (n * (n - 1) / 2 + n + n * e) * lam ^ (n - 2 - e)
        * resultant (derivative Q) (N - Q) e n := by
  have hd0 : Q.natDegree ≠ 0 := by
    intro h0
    apply hQ'
    rw [eq_C_of_natDegree_eq_zero h0, derivative_C]
  have hed : e < Q.natDegree := by
    rw [← hQe]
    exact natDegree_derivative_lt hd0
  have hN0 : N ≠ 0 := by
    intro h
    rw [h, natDegree_zero] at hNn
    omega
  have hlam0 : lam ≠ 0 := by
    rw [← hNl]
    exact leadingCoeff_ne_zero.mpr hN0
  have hlt' : Q.natDegree < N.natDegree := by rw [hNn]; exact hlt
  have hfn : (N - Q).natDegree = n := by
    rw [natDegree_sub_eq_left_of_natDegree_lt hlt', hNn]
  have hfl : (N - Q).leadingCoeff = lam := by
    rw [leadingCoeff_sub_of_degree_lt (degree_lt_degree hlt'), hNl]
  have hfc : (N - Q).coeff n = lam := by
    rw [← hfl, leadingCoeff, hfn]
  have hfpos : 0 < (N - Q).degree := by
    rw [← natDegree_pos_iff_degree_pos, hfn]
    omega
  have hfd : derivative (N - Q) = C (-1 : F) * derivative Q := by
    rw [derivative_sub, hN, zero_sub, C_neg, C_1, neg_one_mul]
  have eA : resultant (N - Q) (derivative (N - Q)) n (n - 1) =
      (-1) ^ (n * (n - 1) / 2) * lam * discr (N - Q) := by
    have h := resultant_deriv hfpos
    rwa [hfn, hfl] at h
  have hk : n - 1 = e + (n - 1 - e) := by omega
  have eB0 := resultant_add_right_deg (N - Q) (derivative Q) n e (n - 1 - e) (le_of_eq hQe)
  rw [← hk, hfc] at eB0
  have eB : resultant (N - Q) (derivative (N - Q)) n (n - 1) =
      (-1) ^ n * (lam ^ (n - 1 - e) * ((-1) ^ (n * e) *
        resultant (derivative Q) (N - Q) e n)) := by
    rw [hfd, resultant_C_mul_right, eB0, resultant_comm (N - Q) (derivative Q) n e]
  have hs3 : (-1 : F) ^ (n * (n - 1) / 2) * (-1) ^ (n * (n - 1) / 2) = 1 := by
    rw [← mul_pow]
    simp
  have hpow : lam ^ (n - 1 - e) = lam ^ (n - 2 - e) * lam := by
    rw [← pow_succ]
    congr 1
    omega
  have key : (-1 : F) ^ (n * (n - 1) / 2) * lam * discr (N - Q) =
      (-1) ^ n * (lam ^ (n - 1 - e) * ((-1) ^ (n * e) *
        resultant (derivative Q) (N - Q) e n)) := by
    rw [← eA, eB]
  apply mul_left_cancel₀ hlam0
  rw [pow_add, pow_add]
  linear_combination (-1 : F) ^ (n * (n - 1) / 2) * key - lam * discr (N - Q) * hs3
    + (-1 : F) ^ (n * (n - 1) / 2) * (-1) ^ n * (-1) ^ (n * e)
        * resultant (derivative Q) (N - Q) e n * hpow

/-- **The discriminant of `N - Q` for `N' = 0`, in general.** Over any field, with no condition
on the roots of `Q'`: if `N' = 0`, `Q' ≠ 0` and `deg Q < n = deg N`, then with `λ` the leading
coefficient of `N` and `e = deg Q'`,
`discr (N - Q) = (-1)^(n(n-1)/2 + n + ne) · λ^(n-2-e) · Res(Q', N - Q)`.
So the discriminant, a quantity of degree `2n - 2` in the coefficients, is a resultant with the
derivative of the row, a polynomial of degree below `deg Q`. -/
theorem discr_sub_eq_resultant {N Q : F[X]} (hN : derivative N = 0) (hQ' : derivative Q ≠ 0)
    (hlt : Q.natDegree < N.natDegree) :
    discr (N - Q) =
      (-1) ^ (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree
          + N.natDegree * (derivative Q).natDegree)
        * N.leadingCoeff ^ (N.natDegree - 2 - (derivative Q).natDegree)
        * resultant (derivative Q) (N - Q) (derivative Q).natDegree N.natDegree :=
  discr_sub_eq_resultant_aux rfl rfl rfl hN hQ' hlt

/-- **The discriminant of `N - Q` depends on `N` only through its degree, its leading
coefficient and its residue modulo `Q'`** (for `N' = 0`). -/
theorem discr_sub_congr {N₁ N₂ Q : F[X]} (hN₁ : derivative N₁ = 0) (hN₂ : derivative N₂ = 0)
    (hQ' : derivative Q ≠ 0) (hlt : Q.natDegree < N₁.natDegree)
    (hdeg : N₁.natDegree = N₂.natDegree) (hlc : N₁.leadingCoeff = N₂.leadingCoeff)
    (hmod : derivative Q ∣ N₁ - N₂) :
    discr (N₁ - Q) = discr (N₂ - Q) := by
  have hlt₂ : Q.natDegree < N₂.natDegree := hdeg ▸ hlt
  rw [discr_sub_eq_resultant hN₁ hQ' hlt, discr_sub_eq_resultant hN₂ hQ' hlt₂, hdeg, hlc]
  congr 1
  have h := resultant_congr_of_roots (g := derivative Q) (h₁ := N₁ - Q) (h₂ := N₂ - Q)
    (n₁ := N₂.natDegree) (n₂ := N₂.natDegree)
    (by rw [natDegree_sub_eq_left_of_natDegree_lt hlt, hdeg])
    (by rw [natDegree_sub_eq_left_of_natDegree_lt hlt₂]) le_rfl
    (fun π _ hπd => by
      have e : N₁ - Q - (N₂ - Q) = N₁ - N₂ := by ring
      rw [e]
      exact hπd.trans hmod)
  rw [h, Nat.sub_self, pow_zero, one_mul]

/-- **The general discriminant identity.** Over any field: if `N' = 0`, `Q` is monic with
`Q' ≠ 0` and `deg Q < deg N`, and every irreducible factor of `Q'` divides `N`, then with
`n = deg N`, `d = deg Q`, `e = deg Q'`, `λ` and `ℓ` the leading coefficients of `N` and `Q'`:
`discr (N - Q) = (-1)^(n(n-1)/2 + n + ne + e + ed + d(d-1)/2) · λ^(n-2-e) · ℓ^(n-d) · discr Q`.
When `d ≠ 0` in the field this is `discr_sub` (`e = d - 1`, `ℓ = d`); it also covers the
degrees `d` divisible by the characteristic. -/
theorem discr_sub_general {N Q : F[X]} (hQ : Q.Monic) (hN : derivative N = 0)
    (hQ' : derivative Q ≠ 0) (hlt : Q.natDegree < N.natDegree)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N) :
    discr (N - Q) =
      (-1) ^ (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree
          + N.natDegree * (derivative Q).natDegree + (derivative Q).natDegree
          + (derivative Q).natDegree * Q.natDegree + Q.natDegree * (Q.natDegree - 1) / 2)
        * N.leadingCoeff ^ (N.natDegree - 2 - (derivative Q).natDegree)
        * (derivative Q).leadingCoeff ^ (N.natDegree - Q.natDegree) * discr Q :=
  discr_sub_general_aux rfl rfl rfl rfl rfl hQ hN hQ' hlt hrad

/-- The discriminant identity with the degrees and the leading coefficient named. -/
theorem discr_sub_aux {N Q : F[X]} {n d : ℕ} {lam : F} (hNn : N.natDegree = n)
    (hQd : Q.natDegree = d) (hNl : N.leadingCoeff = lam) (hQ : Q.Monic)
    (hN : derivative N = 0) (hd : (d : F) ≠ 0) (hlt : d < n)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N) :
    discr (N - Q) =
      (-1) ^ (n * (n - 1) / 2 + n * d + (d - 1) + d * (d - 1) / 2)
        * lam ^ (n - d - 1) * (d : F) ^ (n - d) * discr Q := by
  obtain ⟨hQ'deg, hQ'lc⟩ := natDegree_derivative_of_monic hQ (by rw [hQd]; exact hd)
  rw [hQd] at hQ'deg hQ'lc
  have hd1 : 1 ≤ d := by
    rcases Nat.eq_zero_or_pos d with h | h
    · rw [h] at hd
      simp at hd
    · exact h
  have hN0 : N ≠ 0 := by
    intro h
    rw [h, natDegree_zero] at hNn
    omega
  have hlam0 : lam ≠ 0 := by
    rw [← hNl]
    exact leadingCoeff_ne_zero.mpr hN0
  have hlt' : Q.natDegree < N.natDegree := by rw [hQd, hNn]; exact hlt
  -- the polynomial `f = N - Q`
  have hfn : (N - Q).natDegree = n := by
    rw [natDegree_sub_eq_left_of_natDegree_lt hlt', hNn]
  have hfl : (N - Q).leadingCoeff = lam := by
    rw [leadingCoeff_sub_of_degree_lt (degree_lt_degree hlt'), hNl]
  have hfc : (N - Q).coeff n = lam := by
    rw [← hfl, leadingCoeff, hfn]
  have hfpos : 0 < (N - Q).degree := by
    rw [← natDegree_pos_iff_degree_pos, hfn]
    omega
  have hfd : derivative (N - Q) = C (-1 : F) * derivative Q := by
    rw [derivative_sub, hN, zero_sub, C_neg, C_1, neg_one_mul]
  have hQpos : 0 < Q.degree := by
    rw [← natDegree_pos_iff_degree_pos, hQd]
    exact hd1
  -- the chain of resultants
  have eA : resultant (N - Q) (derivative (N - Q)) n (n - 1) =
      (-1) ^ (n * (n - 1) / 2) * lam * discr (N - Q) := by
    have h := resultant_deriv hfpos
    rwa [hfn, hfl] at h
  have hk : n - 1 = (d - 1) + (n - d) := by omega
  have eB : resultant (N - Q) (derivative (N - Q)) n (n - 1) =
      (-1) ^ n * (lam ^ (n - d) * ((-1) ^ (n * (d - 1)) *
        resultant (derivative Q) (N - Q) (d - 1) n)) := by
    rw [hfd, resultant_C_mul_right, hk,
      resultant_add_right_deg _ _ _ _ (n - d) (le_of_eq hQ'deg), hfc,
      resultant_comm (N - Q) (derivative Q) n (d - 1)]
  have eC : resultant (derivative Q) (N - Q) (d - 1) n =
      (d : F) ^ (n - d) * resultant (derivative Q) (C (-1 : F) * Q) (d - 1) d := by
    have h := resultant_congr_of_roots (g := derivative Q) (h₁ := N - Q) (h₂ := C (-1 : F) * Q)
      (n₁ := n) (n₂ := d) (le_of_eq hfn) ((natDegree_C_mul_le _ _).trans (le_of_eq hQd)) hlt.le
      (fun π hπ hπd => by
        have : N - Q - C (-1 : F) * Q = N := by
          rw [C_neg, C_1]
          ring
        rw [this]
        exact hrad π hπ hπd)
    rw [hQ'deg, hQ'lc] at h
    exact h
  have eD : resultant (derivative Q) (C (-1 : F) * Q) (d - 1) d =
      (-1) ^ (d - 1) * ((-1) ^ ((d - 1) * d) * resultant Q (derivative Q) d (d - 1)) := by
    rw [resultant_C_mul_right, resultant_comm (derivative Q) Q (d - 1) d]
  have eE : resultant Q (derivative Q) d (d - 1) = (-1) ^ (d * (d - 1) / 2) * discr Q := by
    have h := resultant_deriv hQpos
    rwa [hQd, hQ.leadingCoeff, mul_one] at h
  -- signs
  have hs1 : (-1 : F) ^ (n * (d - 1)) * (-1) ^ n = (-1) ^ (n * d) := by
    rw [← pow_add]
    congr 1
    calc n * (d - 1) + n = n * (d - 1 + 1) := by ring
      _ = n * d := by rw [Nat.sub_add_cancel hd1]
  have hs2 : (-1 : F) ^ ((d - 1) * d) = 1 := by
    rw [mul_comm]
    exact (Nat.even_mul_pred_self d).neg_one_pow
  have hs3 : (-1 : F) ^ (n * (n - 1) / 2) * (-1) ^ (n * (n - 1) / 2) = 1 := by
    rw [← mul_pow]
    simp
  have hpow : lam ^ (n - d) = lam ^ (n - d - 1) * lam := by
    rw [← pow_succ]
    congr 1
    omega
  have key : (-1 : F) ^ (n * (n - 1) / 2) * lam * discr (N - Q) =
      (-1) ^ n * (lam ^ (n - d) * ((-1) ^ (n * (d - 1)) * ((d : F) ^ (n - d) *
        ((-1) ^ (d - 1) * (1 * ((-1) ^ (d * (d - 1) / 2) * discr Q)))))) := by
    rw [← eA, eB, eC, eD, eE, hs2]
  apply mul_left_cancel₀ hlam0
  rw [pow_add, pow_add, pow_add]
  linear_combination (-1 : F) ^ (n * (n - 1) / 2) * key - lam * discr (N - Q) * hs3
    + (-1 : F) ^ (n * (n - 1) / 2) * (-1) ^ (d - 1) * (-1) ^ (d * (d - 1) / 2)
        * (d : F) ^ (n - d) * discr Q * lam ^ (n - d) * hs1
    + (-1 : F) ^ (n * (n - 1) / 2) * (-1) ^ (n * d) * (-1) ^ (d - 1) * (-1) ^ (d * (d - 1) / 2)
        * (d : F) ^ (n - d) * discr Q * hpow

/-- **The discriminant identity.** Over any field: if `N' = 0`, `Q` is monic of degree `d`
with `d ≠ 0` in the field and `d < n = deg N`, and every irreducible factor of `Q'` divides
`N`, then `discr (N - Q) = ± λ^(n-d-1) d^(n-d) discr Q` with the sign below. -/
theorem discr_sub {N Q : F[X]} (hQ : Q.Monic) (hN : derivative N = 0)
    (hd : (Q.natDegree : F) ≠ 0) (hlt : Q.natDegree < N.natDegree)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N) :
    discr (N - Q) =
      (-1) ^ (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree * Q.natDegree
          + (Q.natDegree - 1) + Q.natDegree * (Q.natDegree - 1) / 2)
        * N.leadingCoeff ^ (N.natDegree - Q.natDegree - 1)
        * (Q.natDegree : F) ^ (N.natDegree - Q.natDegree) * discr Q :=
  discr_sub_aux rfl rfl rfl hQ hN hd hlt hrad

/-- The derivative of a monic polynomial whose degree is not zero in the field is not zero. -/
theorem derivative_ne_zero_of_monic {Q : F[X]} (hQ : Q.Monic) (hd : (Q.natDegree : F) ≠ 0) :
    derivative Q ≠ 0 := by
  intro h
  have h2 := (natDegree_derivative_of_monic hQ hd).2
  rw [h, leadingCoeff_zero] at h2
  exact hd h2.symm

/-- `N - Q` is squarefree: an irreducible factor it shares with its derivative `-Q'` divides
`N`, hence `Q`, so it is `Q`; but `Q` does not divide `Q'`. -/
theorem squarefree_sub {N Q : F[X]} (hQi : Irreducible Q) (hN : derivative N = 0)
    (hQ' : derivative Q ≠ 0) (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N) :
    Squarefree (N - Q) := by
  apply Separable.squarefree
  rw [separable_def]
  have hfd : derivative (N - Q) = -derivative Q := by rw [derivative_sub, hN, zero_sub]
  rw [hfd]
  apply isCoprime_of_irreducible_dvd
  · rintro ⟨-, h⟩
    exact hQ' (neg_eq_zero.mp h)
  · intro z hz hzf hzQ'
    have hzQ' : z ∣ derivative Q := (dvd_neg).mp hzQ'
    have hzN := hrad z hz hzQ'
    have hzQ : z ∣ Q := by
      have h := dvd_sub hzN hzf
      rwa [sub_sub_cancel] at h
    have hass : Associated z Q := (hz.dvd_irreducible_iff_associated hQi).mp hzQ
    have hQQ' : Q ∣ derivative Q := hass.symm.dvd.trans hzQ'
    have hdeg := natDegree_le_of_dvd hQQ' hQ'
    have hlt := natDegree_derivative_lt (p := Q) (by
      intro h0
      apply hQ'
      rw [eq_C_of_natDegree_eq_zero h0, derivative_C])
    omega

end AnyField

section FiniteField

open UniqueFactorizationMonoid

variable {F : Type*} [Field F] [Fintype F] [DecidableEq F]

/-- **The parity theorem.** Under the hypotheses of `discr_sub`, with `Q` irreducible:
`N - Q` is squarefree, and the parity of the number `r` of its irreducible factors is
determined by `n = deg N`, `d = deg Q` and the quadratic characters of `-1`, of the leading
coefficient of `N` and of `d`. -/
theorem parity_card_factors (hF : ringChar F ≠ 2) {N Q : F[X]}
    (hQ : Q.Monic) (hQi : Irreducible Q) (hN : derivative N = 0)
    (hd : (Q.natDegree : F) ≠ 0) (hlt : Q.natDegree < N.natDegree)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N) :
    Squarefree (N - Q) ∧
      (-1 : ℤ) ^ (N.natDegree + Multiset.card (normalizedFactors (N - Q))) =
        quadraticChar F (-1) ^ (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree * Q.natDegree
            + (Q.natDegree - 1) + Q.natDegree * (Q.natDegree - 1) / 2)
          * quadraticChar F N.leadingCoeff ^ (N.natDegree - Q.natDegree - 1)
          * quadraticChar F (Q.natDegree : F) ^ (N.natDegree - Q.natDegree)
          * (-1) ^ (Q.natDegree + 1) := by
  have hsq := squarefree_sub hQi hN (derivative_ne_zero_of_monic hQ hd) hrad
  refine ⟨hsq, ?_⟩
  have h1 := stickelbergerSwan F hF (N - Q) hsq
  have h2 := stickelbergerSwan F hF Q hQi.squarefree
  rw [normalizedFactors_irreducible hQi, Multiset.card_singleton] at h2
  rw [natDegree_sub_eq_left_of_natDegree_lt hlt] at h1
  rw [← h1, discr_sub hQ hN hd hlt hrad, map_mul, map_mul, map_mul, map_pow, map_pow, map_pow,
    h2]

/-- If `-1` and `deg Q` are squares in the field and the leading coefficient of `N` is not,
the number of irreducible factors of `N - Q` is even. -/
theorem even_card_factors (hF : ringChar F ≠ 2) {N Q : F[X]}
    (hQ : Q.Monic) (hQi : Irreducible Q) (hN : derivative N = 0)
    (hd : (Q.natDegree : F) ≠ 0) (hlt : Q.natDegree < N.natDegree)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N)
    (hm1 : IsSquare (-1 : F)) (hdsq : IsSquare (Q.natDegree : F))
    (hlam : ¬IsSquare N.leadingCoeff) :
    Even (Multiset.card (normalizedFactors (N - Q))) := by
  obtain ⟨-, h⟩ := parity_card_factors hF hQ hQi hN hd hlt hrad
  rw [(quadraticChar_one_iff_isSquare (neg_ne_zero.mpr one_ne_zero)).mpr hm1,
    (quadraticChar_one_iff_isSquare hd).mpr hdsq,
    quadraticChar_neg_one_iff_not_isSquare.mpr hlam, one_pow, one_pow, one_mul, mul_one,
    ← pow_add] at h
  have e : N.natDegree - Q.natDegree - 1 + (Q.natDegree + 1) = N.natDegree := by omega
  rw [e, pow_add] at h
  have hn0 : (-1 : ℤ) ^ N.natDegree ≠ 0 := pow_ne_zero _ (by norm_num)
  have h1 : (-1 : ℤ) ^ Multiset.card (normalizedFactors (N - Q)) = 1 :=
    mul_left_cancel₀ hn0 (h.trans (mul_one _).symm)
  exact (neg_one_pow_eq_one_iff_even (by norm_num)).mp h1

/-- ... and so `N - Q` is not irreducible, although no factor is exhibited. -/
theorem not_irreducible_sub (hF : ringChar F ≠ 2) {N Q : F[X]}
    (hQ : Q.Monic) (hQi : Irreducible Q) (hN : derivative N = 0)
    (hd : (Q.natDegree : F) ≠ 0) (hlt : Q.natDegree < N.natDegree)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N)
    (hm1 : IsSquare (-1 : F)) (hdsq : IsSquare (Q.natDegree : F))
    (hlam : ¬IsSquare N.leadingCoeff) :
    ¬Irreducible (N - Q) := by
  intro hirr
  have h := even_card_factors hF hQ hQi hN hd hlt hrad hm1 hdsq hlam
  rw [normalizedFactors_irreducible hirr, Multiset.card_singleton] at h
  exact absurd h (by decide)

/-- In a finite field of odd characteristic with a square number of elements, every element
of the prime field is a square. -/
theorem isSquare_intCast_of_isSquare_card (hF : ringChar F ≠ 2)
    (hq : IsSquare (Fintype.card F)) (c : ℤ) : IsSquare (c : F) := by
  by_cases hc : (c : F) = 0
  · rw [hc]
    exact IsSquare.zero
  rw [FiniteField.isSquare_iff hF hc]
  obtain ⟨m, hm⟩ := hq
  have : CharP F (ringChar F) := ringChar.charP F
  obtain ⟨k, hp, hk⟩ := FiniteField.card F (ringChar F)
  have hmdvd : m ∣ ringChar F ^ (k : ℕ) := ⟨m, by rw [← hk, hm]⟩
  obtain ⟨j, -, rfl⟩ := (Nat.dvd_prime_pow hp).mp hmdvd
  have : ExpChar F (ringChar F) := ExpChar.prime hp
  have hfrob : (c : F) ^ (ringChar F ^ j) = c := by
    rw [← iterateFrobenius_def (R := F) (ringChar F) j, map_intCast]
  have hodd : Odd (ringChar F ^ j) := (hp.odd_of_ne_two hF).pow
  obtain ⟨t, ht⟩ := hodd
  have hc1 : (c : F) ^ (2 * t) = 1 := by
    have h : (c : F) ^ (2 * t) * c = 1 * c := by rw [← pow_succ, ← ht, hfrob, one_mul]
    exact mul_right_cancel₀ hc h
  have hhalf : Fintype.card F / 2 = 2 * t * (t + 1) := by
    rw [hm, ht]
    have h : (2 * t + 1) * (2 * t + 1) = 2 * (2 * t * (t + 1)) + 1 := by ring
    rw [h]
    omega
  rw [hhalf, pow_mul, hc1, one_pow]

/-- **Corollary.** Over a finite field of odd characteristic with a square number of elements:
if the leading coefficient of `N` is not a square, `N - Q` is not irreducible. -/
theorem not_irreducible_sub_of_isSquare_card (hF : ringChar F ≠ 2)
    (hq : IsSquare (Fintype.card F)) {N Q : F[X]}
    (hQ : Q.Monic) (hQi : Irreducible Q) (hN : derivative N = 0)
    (hd : (Q.natDegree : F) ≠ 0) (hlt : Q.natDegree < N.natDegree)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N)
    (hlam : ¬IsSquare N.leadingCoeff) :
    ¬Irreducible (N - Q) :=
  not_irreducible_sub hF hQ hQi hN hd hlt hrad
    (by simpa using isSquare_intCast_of_isSquare_card hF hq (-1))
    (by simpa using isSquare_intCast_of_isSquare_card hF hq (Q.natDegree : ℤ)) hlam

/-- **The desert.** Over a finite field of odd characteristic `p` with a square number of
elements, let `V` be monic and divisible by every irreducible polynomial of degree at most `J`
(for instance their product), `c` a non-square, and `N = c · V^p`. Then `N - Q` is not
irreducible for every monic irreducible `Q` of degree at most `J + 1` and less than `deg N`,
the degree `J + 1` being allowed when `p` does not divide it. For `deg Q ≤ J` the factor is
`Q` itself; for `deg Q = J + 1` no factor is exhibited. -/
theorem desert (hF : ringChar F ≠ 2)
    (hq : IsSquare (Fintype.card F)) {V : F[X]} {J : ℕ} {c : F} (hVm : V.Monic)
    (hV : ∀ π : F[X], Irreducible π → π.natDegree ≤ J → π ∣ V) (hc : ¬IsSquare c)
    {Q : F[X]} (hQ : Q.Monic) (hQi : Irreducible Q) (hQJ : Q.natDegree ≤ J + 1)
    (hdeg : Q.natDegree ≤ J ∨ (Q.natDegree : F) ≠ 0)
    (hlt : Q.natDegree < (C c * V ^ ringChar F).natDegree) :
    ¬Irreducible (C c * V ^ ringChar F - Q) := by
  have : CharP F (ringChar F) := ringChar.charP F
  have hp : (ringChar F).Prime := CharP.char_is_prime F (ringChar F)
  have hNl : (C c * V ^ ringChar F).leadingCoeff = c := by
    rw [leadingCoeff_mul, leadingCoeff_C, (hVm.pow _).leadingCoeff, mul_one]
  have hN' : derivative (C c * V ^ ringChar F) = 0 := by
    rw [derivative_C_mul, derivative_pow, CharP.cast_eq_zero F (ringChar F), C_0, zero_mul,
      zero_mul, mul_zero]
  by_cases hdJ : Q.natDegree ≤ J
  · intro hirr
    have hQN : Q ∣ C c * V ^ ringChar F :=
      ((hV Q hQi hdJ).trans (dvd_pow_self V hp.ne_zero)).mul_left _
    have hQf : Q ∣ C c * V ^ ringChar F - Q := dvd_sub hQN dvd_rfl
    have hass : Associated Q (C c * V ^ ringChar F - Q) :=
      (hQi.dvd_irreducible_iff_associated hirr).mp hQf
    have h := natDegree_eq_of_degree_eq (degree_eq_degree_of_associated hass)
    rw [natDegree_sub_eq_left_of_natDegree_lt hlt] at h
    omega
  · have hd : (Q.natDegree : F) ≠ 0 := hdeg.resolve_left hdJ
    refine not_irreducible_sub_of_isSquare_card hF hq hQ hQi hN' hd hlt ?_ ?_
    · intro π hπ hπQ'
      have h1 := natDegree_le_of_dvd hπQ' (derivative_ne_zero_of_monic hQ hd)
      have h2 := natDegree_derivative_le Q
      exact ((hV π hπ (by omega)).trans (dvd_pow_self V hp.ne_zero)).mul_left _
    · rw [hNl]
      exact hc

/-- **The parity theorem for every row.** As `parity_card_factors`, without the condition
that `deg Q` is not zero in the field: `e` and `ℓ` are the degree and the leading coefficient
of `Q'`. -/
theorem parity_card_factors_general (hF : ringChar F ≠ 2) {N Q : F[X]}
    (hQ : Q.Monic) (hQi : Irreducible Q) (hN : derivative N = 0)
    (hlt : Q.natDegree < N.natDegree)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N) :
    Squarefree (N - Q) ∧
      (-1 : ℤ) ^ (N.natDegree + Multiset.card (normalizedFactors (N - Q))) =
        quadraticChar F (-1) ^ (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree
            + N.natDegree * (derivative Q).natDegree + (derivative Q).natDegree
            + (derivative Q).natDegree * Q.natDegree + Q.natDegree * (Q.natDegree - 1) / 2)
          * quadraticChar F N.leadingCoeff ^ (N.natDegree - 2 - (derivative Q).natDegree)
          * quadraticChar F (derivative Q).leadingCoeff ^ (N.natDegree - Q.natDegree)
          * (-1) ^ (Q.natDegree + 1) := by
  have hQ' : derivative Q ≠ 0 :=
    (separable_iff_derivative_ne_zero hQi).mp (PerfectField.separable_of_irreducible hQi)
  have hsq := squarefree_sub hQi hN hQ' hrad
  refine ⟨hsq, ?_⟩
  have h1 := stickelbergerSwan F hF (N - Q) hsq
  have h2 := stickelbergerSwan F hF Q hQi.squarefree
  rw [normalizedFactors_irreducible hQi, Multiset.card_singleton] at h2
  rw [natDegree_sub_eq_left_of_natDegree_lt hlt] at h1
  rw [← h1, discr_sub_general hQ hN hQ' hlt hrad, map_mul, map_mul, map_mul, map_pow, map_pow,
    map_pow, h2]

/-- **Which rows are killed.** Over a finite field of odd characteristic with a square number
of elements, for `N` with a non-square leading coefficient: the number of irreducible factors
of `N - Q` is even exactly when `(-1)^(d + 1 + e) χ(ℓ)^(n - d) = 1`, with `e` and `ℓ` the degree
and the leading coefficient of `Q'`. For `d` not divisible by the characteristic that is
always so (`e = d - 1`, `ℓ = d`). -/
theorem even_card_factors_iff (hF : ringChar F ≠ 2) (hq : IsSquare (Fintype.card F))
    {N Q : F[X]} (hQ : Q.Monic) (hQi : Irreducible Q) (hN : derivative N = 0)
    (hlt : Q.natDegree < N.natDegree)
    (hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ N)
    (hlam : ¬IsSquare N.leadingCoeff) :
    Even (Multiset.card (normalizedFactors (N - Q))) ↔
      (-1 : ℤ) ^ (Q.natDegree + 1 + (derivative Q).natDegree)
        * quadraticChar F (derivative Q).leadingCoeff ^ (N.natDegree - Q.natDegree) = 1 := by
  have hQ' : derivative Q ≠ 0 :=
    (separable_iff_derivative_ne_zero hQi).mp (PerfectField.separable_of_irreducible hQi)
  have hd0 : Q.natDegree ≠ 0 := by
    intro h0
    apply hQ'
    rw [eq_C_of_natDegree_eq_zero h0, derivative_C]
  have hed : (derivative Q).natDegree < Q.natDegree := natDegree_derivative_lt hd0
  obtain ⟨-, h⟩ := parity_card_factors_general hF hQ hQi hN hlt hrad
  have hm1 : IsSquare (-1 : F) := by
    simpa using isSquare_intCast_of_isSquare_card hF hq (-1)
  rw [(quadraticChar_one_iff_isSquare (neg_ne_zero.mpr one_ne_zero)).mpr hm1,
    quadraticChar_neg_one_iff_not_isSquare.mpr hlam, one_pow, one_mul, pow_add] at h
  -- signs in `ℤ`
  have f1 : (-1 : ℤ) ^ N.natDegree =
      (-1) ^ (N.natDegree - 2 - (derivative Q).natDegree) * (-1) ^ (derivative Q).natDegree := by
    have e : N.natDegree =
        (N.natDegree - 2 - (derivative Q).natDegree + (derivative Q).natDegree) + 2 := by omega
    conv_lhs => rw [e, pow_add, pow_add]
    simp
  have f2 : (-1 : ℤ) ^ (N.natDegree - 2 - (derivative Q).natDegree)
      * (-1) ^ (N.natDegree - 2 - (derivative Q).natDegree) = 1 := by
    rw [← mul_pow]
    simp
  have f3 : (-1 : ℤ) ^ N.natDegree * (-1) ^ N.natDegree = 1 := by
    rw [← mul_pow]
    simp
  have hr : (-1 : ℤ) ^ Multiset.card (normalizedFactors (N - Q)) =
      (-1) ^ (Q.natDegree + 1 + (derivative Q).natDegree)
        * quadraticChar F (derivative Q).leadingCoeff ^ (N.natDegree - Q.natDegree) := by
    rw [pow_add (-1 : ℤ) (Q.natDegree + 1)]
    linear_combination
      (-((-1 : ℤ) ^ Multiset.card (normalizedFactors (N - Q)))) * f3
      + (-1 : ℤ) ^ N.natDegree * h
      + ((-1 : ℤ) ^ (N.natDegree - 2 - (derivative Q).natDegree)
          * quadraticChar F (derivative Q).leadingCoeff ^ (N.natDegree - Q.natDegree)
          * (-1) ^ (Q.natDegree + 1)) * f1
      + ((-1 : ℤ) ^ (derivative Q).natDegree
          * quadraticChar F (derivative Q).leadingCoeff ^ (N.natDegree - Q.natDegree)
          * (-1) ^ (Q.natDegree + 1)) * f2
  rw [← hr]
  exact (neg_one_pow_eq_one_iff_even (by norm_num)).symm

/-- **The desert, every row.** `N = c · V^p` as in `desert`. For a monic irreducible `Q` of
degree `d ≤ J + 1` (and `d < deg N`), `N - Q` is not irreducible if `d ≤ J`, or if
`(-1)^(d + 1 + e) χ(ℓ)^(n - d) = 1` where `e`, `ℓ` are the degree and the leading coefficient of
`Q'` and `n = deg N`. The second condition holds for every `d` not divisible by `p` and for
about half of the rows of a degree divisible by `p`. -/
theorem desert_general (hF : ringChar F ≠ 2)
    (hq : IsSquare (Fintype.card F)) {V : F[X]} {J : ℕ} {c : F} (hVm : V.Monic)
    (hV : ∀ π : F[X], Irreducible π → π.natDegree ≤ J → π ∣ V) (hc : ¬IsSquare c)
    {Q : F[X]} (hQ : Q.Monic) (hQi : Irreducible Q) (hQJ : Q.natDegree ≤ J + 1)
    (hlt : Q.natDegree < (C c * V ^ ringChar F).natDegree)
    (hsign : Q.natDegree ≤ J ∨
      (-1 : ℤ) ^ (Q.natDegree + 1 + (derivative Q).natDegree)
        * quadraticChar F (derivative Q).leadingCoeff
          ^ ((C c * V ^ ringChar F).natDegree - Q.natDegree) = 1) :
    ¬Irreducible (C c * V ^ ringChar F - Q) := by
  have : CharP F (ringChar F) := ringChar.charP F
  have hp : (ringChar F).Prime := CharP.char_is_prime F (ringChar F)
  have hNl : (C c * V ^ ringChar F).leadingCoeff = c := by
    rw [leadingCoeff_mul, leadingCoeff_C, (hVm.pow _).leadingCoeff, mul_one]
  have hN' : derivative (C c * V ^ ringChar F) = 0 := by
    rw [derivative_C_mul, derivative_pow, CharP.cast_eq_zero F (ringChar F), C_0, zero_mul,
      zero_mul, mul_zero]
  by_cases hdJ : Q.natDegree ≤ J
  · intro hirr
    have hQN : Q ∣ C c * V ^ ringChar F :=
      ((hV Q hQi hdJ).trans (dvd_pow_self V hp.ne_zero)).mul_left _
    have hQf : Q ∣ C c * V ^ ringChar F - Q := dvd_sub hQN dvd_rfl
    have hass : Associated Q (C c * V ^ ringChar F - Q) :=
      (hQi.dvd_irreducible_iff_associated hirr).mp hQf
    have h := natDegree_eq_of_degree_eq (degree_eq_degree_of_associated hass)
    rw [natDegree_sub_eq_left_of_natDegree_lt hlt] at h
    omega
  · have hs := hsign.resolve_left hdJ
    have hQ' : derivative Q ≠ 0 :=
      (separable_iff_derivative_ne_zero hQi).mp (PerfectField.separable_of_irreducible hQi)
    have hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ C c * V ^ ringChar F := by
      intro π hπ hπQ'
      have h1 := natDegree_le_of_dvd hπQ' hQ'
      have h2 := natDegree_derivative_le Q
      exact ((hV π hπ (by omega)).trans (dvd_pow_self V hp.ne_zero)).mul_left _
    have hev := (even_card_factors_iff hF hq hQ hQi hN' hlt hrad (by rw [hNl]; exact hc)).mpr hs
    intro hirr
    rw [normalizedFactors_irreducible hirr, Multiset.card_singleton] at hev
    exact absurd hev (by decide)

/-- **The desert reaches every degree.** `N = c · V^p` as in `desert`. The rows killed are not
only those of degree at most `J + 1`: `N - Q` is not irreducible for every monic irreducible
`Q` of any degree `d < deg N` with `d ≠ 0` in the field whose derivative has no irreducible
factor of degree above `J`. Among the rows of degree `d` these are a positive proportion
(the proportion of polynomials of degree `d - 1` that are `J`-smooth), e.g. all but about
`1 / (J + 1)` of the rows of degree `J + 2`. -/
theorem desert_smooth (hF : ringChar F ≠ 2)
    (hq : IsSquare (Fintype.card F)) {V : F[X]} {J : ℕ} {c : F} (hVm : V.Monic)
    (hV : ∀ π : F[X], Irreducible π → π.natDegree ≤ J → π ∣ V) (hc : ¬IsSquare c)
    {Q : F[X]} (hQ : Q.Monic) (hQi : Irreducible Q) (hd : (Q.natDegree : F) ≠ 0)
    (hlt : Q.natDegree < (C c * V ^ ringChar F).natDegree)
    (hsm : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π.natDegree ≤ J) :
    ¬Irreducible (C c * V ^ ringChar F - Q) := by
  have : CharP F (ringChar F) := ringChar.charP F
  have hp : (ringChar F).Prime := CharP.char_is_prime F (ringChar F)
  have hNl : (C c * V ^ ringChar F).leadingCoeff = c := by
    rw [leadingCoeff_mul, leadingCoeff_C, (hVm.pow _).leadingCoeff, mul_one]
  have hN' : derivative (C c * V ^ ringChar F) = 0 := by
    rw [derivative_C_mul, derivative_pow, CharP.cast_eq_zero F (ringChar F), C_0, zero_mul,
      zero_mul, mul_zero]
  refine not_irreducible_sub_of_isSquare_card hF hq hQ hQi hN' hd hlt ?_ ?_
  · intro π hπ hπQ'
    exact ((hV π hπ (hsm π hπ hπQ')).trans (dvd_pow_self V hp.ne_zero)).mul_left _
  · rw [hNl]
    exact hc

/-- The same for every row, with the sign criterion of `even_card_factors_iff` in place of
`d ≠ 0`. -/
theorem desert_smooth_general (hF : ringChar F ≠ 2)
    (hq : IsSquare (Fintype.card F)) {V : F[X]} {J : ℕ} {c : F} (hVm : V.Monic)
    (hV : ∀ π : F[X], Irreducible π → π.natDegree ≤ J → π ∣ V) (hc : ¬IsSquare c)
    {Q : F[X]} (hQ : Q.Monic) (hQi : Irreducible Q)
    (hlt : Q.natDegree < (C c * V ^ ringChar F).natDegree)
    (hsm : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π.natDegree ≤ J)
    (hsign : (-1 : ℤ) ^ (Q.natDegree + 1 + (derivative Q).natDegree)
        * quadraticChar F (derivative Q).leadingCoeff
          ^ ((C c * V ^ ringChar F).natDegree - Q.natDegree) = 1) :
    ¬Irreducible (C c * V ^ ringChar F - Q) := by
  have : CharP F (ringChar F) := ringChar.charP F
  have hp : (ringChar F).Prime := CharP.char_is_prime F (ringChar F)
  have hNl : (C c * V ^ ringChar F).leadingCoeff = c := by
    rw [leadingCoeff_mul, leadingCoeff_C, (hVm.pow _).leadingCoeff, mul_one]
  have hN' : derivative (C c * V ^ ringChar F) = 0 := by
    rw [derivative_C_mul, derivative_pow, CharP.cast_eq_zero F (ringChar F), C_0, zero_mul,
      zero_mul, mul_zero]
  have hrad : ∀ π : F[X], Irreducible π → π ∣ derivative Q → π ∣ C c * V ^ ringChar F :=
    fun π hπ hπQ' => ((hV π hπ (hsm π hπ hπQ')).trans (dvd_pow_self V hp.ne_zero)).mul_left _
  have hev := (even_card_factors_iff hF hq hQ hQi hN' hlt hrad (by rw [hNl]; exact hc)).mpr hsign
  intro hirr
  rw [normalizedFactors_irreducible hirr, Multiset.card_singleton] at hev
  exact absurd hev (by decide)

/-- **The parity of the number of irreducible factors of `N - Q` for `N' = 0`, in general.**
Over a finite field of odd characteristic, with no condition on the roots of `Q'`: if `N' = 0`,
`Q' ≠ 0`, `deg Q < n = deg N` and `N - Q` is squarefree, then with `r` the number of
irreducible factors of `N - Q`, `λ` the leading coefficient of `N` and `e = deg Q'`,
`(-1)^(n + r) = χ(-1)^(n(n-1)/2 + n + ne) · χ(λ)^(n-2-e) · χ(Res(Q', N - Q))`.
The last factor is a quadratic symbol of `N - Q` modulo `Q'`; it is what the parity filter of
the research session computes. -/
theorem parity_card_factors_resultant (hF : ringChar F ≠ 2) {N Q : F[X]}
    (hN : derivative N = 0) (hQ' : derivative Q ≠ 0) (hlt : Q.natDegree < N.natDegree)
    (hsq : Squarefree (N - Q)) :
    (-1 : ℤ) ^ (N.natDegree + Multiset.card (normalizedFactors (N - Q))) =
      quadraticChar F (-1) ^ (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree
          + N.natDegree * (derivative Q).natDegree)
        * quadraticChar F N.leadingCoeff ^ (N.natDegree - 2 - (derivative Q).natDegree)
        * quadraticChar F
            (resultant (derivative Q) (N - Q) (derivative Q).natDegree N.natDegree) := by
  have h1 := stickelbergerSwan F hF (N - Q) hsq
  rw [natDegree_sub_eq_left_of_natDegree_lt hlt] at h1
  rw [← h1, discr_sub_eq_resultant hN hQ' hlt, map_mul, map_mul, map_pow, map_pow]

/-- **The parity depends on `N` only through its degree, its leading coefficient and its
residue modulo `Q'`.** If `N₁` and `N₂` have zero derivative, the same degree `> deg Q` and the
same leading coefficient, and `Q'` divides `N₁ - N₂`, then `N₁ - Q` and `N₂ - Q` (both
squarefree) have numbers of irreducible factors of the same parity. -/
theorem parity_card_factors_congr (hF : ringChar F ≠ 2) {N₁ N₂ Q : F[X]}
    (hN₁ : derivative N₁ = 0) (hN₂ : derivative N₂ = 0) (hQ' : derivative Q ≠ 0)
    (hlt : Q.natDegree < N₁.natDegree) (hdeg : N₁.natDegree = N₂.natDegree)
    (hlc : N₁.leadingCoeff = N₂.leadingCoeff) (hmod : derivative Q ∣ N₁ - N₂)
    (hsq₁ : Squarefree (N₁ - Q)) (hsq₂ : Squarefree (N₂ - Q)) :
    (-1 : ℤ) ^ Multiset.card (normalizedFactors (N₁ - Q)) =
      (-1 : ℤ) ^ Multiset.card (normalizedFactors (N₂ - Q)) := by
  have hlt₂ : Q.natDegree < N₂.natDegree := hdeg ▸ hlt
  have h1 := stickelbergerSwan F hF (N₁ - Q) hsq₁
  have h2 := stickelbergerSwan F hF (N₂ - Q) hsq₂
  rw [natDegree_sub_eq_left_of_natDegree_lt hlt] at h1
  rw [natDegree_sub_eq_left_of_natDegree_lt hlt₂] at h2
  rw [discr_sub_congr hN₁ hN₂ hQ' hlt hdeg hlc hmod, h2, hdeg, pow_add, pow_add] at h1
  have hn0 : (-1 : ℤ) ^ N₂.natDegree ≠ 0 := pow_ne_zero _ (by norm_num)
  exact (mul_left_cancel₀ hn0 h1).symm

end FiniteField

end GoldbachGaps.FunctionField
