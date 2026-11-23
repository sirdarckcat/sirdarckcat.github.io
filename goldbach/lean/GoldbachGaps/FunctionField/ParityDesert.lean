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

end FiniteField

end GoldbachGaps.FunctionField
