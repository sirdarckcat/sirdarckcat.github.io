import Mathlib

/-!
# A kernel-checkable elliptic-curve primality criterion

`stepCheck N a x y s q` is a Boolean test, computable by the kernel, such that

  `q` prime and `stepCheck N a x y s q = true`  imply  `N` prime

(`prime_of_stepCheck`). It checks one step of an Atkin–Morain (ECPP) certificate in the
form PARI/GP's `primecert` emits: on the curve `y² = x³ + a x + b` modulo `N` through the
point `P = (x, y)`, the point `R = [s]P` is computed, and then `[q - 1]R = -R`.

Soundness (Goldwasser–Kilian, with the trivial point count instead of Hasse's bound):
if `N` were composite, let `p ≤ √N` be its least prime factor. Every denominator used in
the computation is checked to be invertible modulo `N`, so the same computation is valid
in the group `E(𝔽_p)` and exhibits a point of exact order `q` there. But
`#E(𝔽_p) ≤ 2p + 1`, and the test requires `4N < (q - 1)²`, which forces `q > 2p + 1`.

Affine coordinates are used so that the connection to Mathlib's group law is direct; the
modular inverses are recomputed by `invAux`, which is untrusted (its output is checked).
-/

namespace GoldbachGaps.ECPP

/-! ### The computation (over `ℕ`, so that the kernel's GMP arithmetic applies) -/

/-- Recursion budget for the inverse and the scalar multiplication. -/
def fuel : ℕ := 4000

/-- A modular inverse of `a` modulo `m` by the recursive Euclidean identity
`a⁻¹ = m - (m · (m mod a)⁻¹ - 1) / a`. Untrusted: callers re-check the result. -/
def invAux : ℕ → ℕ → ℕ → ℕ
  | 0, _, _ => 0
  | k + 1, a, m => if a ≤ 1 then a else m - (m * invAux k (m % a) a - 1) / a

/-- Affine doubling on `y² = x³ + a x + b` modulo `N`; `none` if `2y` is not invertible. -/
def ecDbl (N a : ℕ) (P : ℕ × ℕ) : Option (ℕ × ℕ) :=
  let d := 2 * P.2 % N
  let i := invAux fuel d N
  if d * i % N = 1 then
    let lam := (3 * P.1 * P.1 + a) * i % N
    let x3 := (lam * lam + 2 * (N - P.1 % N)) % N
    some (x3, (lam * (P.1 + (N - x3 % N)) + (N - P.2 % N)) % N)
  else none

/-- Affine addition of points with distinct `x` modulo `N`; `none` if `x₁ - x₂` is not
invertible. -/
def ecAdd (N : ℕ) (P Q : ℕ × ℕ) : Option (ℕ × ℕ) :=
  let d := (P.1 + (N - Q.1 % N)) % N
  let i := invAux fuel d N
  if d * i % N = 1 then
    let lam := (P.2 + (N - Q.2 % N)) * i % N
    let x3 := (lam * lam + (N - P.1 % N) + (N - Q.1 % N)) % N
    some (x3, (lam * (P.1 + (N - x3 % N)) + (N - P.2 % N)) % N)
  else none

/-- `[k]P` for `k ≥ 1` by left-to-right double-and-add, using only the generic formulas. -/
def ecMul (N a : ℕ) (P : ℕ × ℕ) : ℕ → ℕ → Option (ℕ × ℕ)
  | 0, _ => none
  | f + 1, k =>
    if k ≤ 1 then some P else
      match ecMul N a P f (k / 2) with
      | none => none
      | some Q =>
        match ecDbl N a Q with
        | none => none
        | some D => if k % 2 = 1 then ecAdd N D P else some D

/-- One ECPP step: `R = [s](x, y)` exists, and `[q - 1]R = -R`, with all denominators
invertible modulo `N`, and `q` large enough for the point-count argument. -/
def stepCheck (N a x y s q : ℕ) : Bool :=
  decide (1 < N) && decide (1 ≤ s) && decide (4 * N < (q - 1) ^ 2) &&
  decide (2 * y % N * invAux fuel (2 * y % N) N % N = 1) &&
  match ecMul N a (x, y) fuel s with
  | none => false
  | some R =>
    match ecMul N a R fuel (q - 1) with
    | none => false
    | some Z => decide (Z.1 % N = R.1 % N) && decide ((Z.2 + R.2) % N = 0)

/-! ### Soundness -/

section Soundness

open WeierstrassCurve.Affine

variable {p : ℕ}

/-- The curve `y² = x³ + a x + b` over `ZMod p`. -/
def curve (p : ℕ) (a b : ZMod p) : WeierstrassCurve.Affine (ZMod p) := ⟨0, 0, 0, a, b⟩

@[simp] lemma curve_a₁ (a b : ZMod p) : (curve p a b).a₁ = 0 := rfl
@[simp] lemma curve_a₂ (a b : ZMod p) : (curve p a b).a₂ = 0 := rfl
@[simp] lemma curve_a₃ (a b : ZMod p) : (curve p a b).a₃ = 0 := rfl
@[simp] lemma curve_a₄ (a b : ZMod p) : (curve p a b).a₄ = a := rfl
@[simp] lemma curve_a₆ (a b : ZMod p) : (curve p a b).a₆ = b := rfl

variable [Fact p.Prime] {N : ℕ}

lemma cast_N (hpN : p ∣ N) : ((N : ℕ) : ZMod p) = 0 := (ZMod.natCast_eq_zero_iff N p).mpr hpN

lemma cast_mod (hpN : p ∣ N) (x : ℕ) : ((x % N : ℕ) : ZMod p) = x :=
  (ZMod.natCast_eq_natCast_iff _ _ _).mpr (Nat.ModEq.of_dvd hpN (Nat.mod_modEq x N))

lemma cast_neg (hpN : p ∣ N) (hN : 0 < N) (x : ℕ) : ((N - x % N : ℕ) : ZMod p) = -(x : ZMod p) := by
  rw [Nat.cast_sub (Nat.mod_lt x hN).le, cast_N hpN, cast_mod hpN, zero_sub]

/-- `P` (a pair of naturals) reduces modulo `p` to the affine point `T`. -/
def Rep (W : WeierstrassCurve.Affine (ZMod p)) (P : ℕ × ℕ) (T : W.Point) : Prop :=
  ∃ h : W.Nonsingular (P.1 : ZMod p) (P.2 : ZMod p), T = .some _ _ h

lemma rep_of_eq {W : WeierstrassCurve.Affine (ZMod p)} {x y : ZMod p} (h : W.Nonsingular x y)
    {P : ℕ × ℕ} (hx : (P.1 : ZMod p) = x) (hy : (P.2 : ZMod p) = y) :
    Rep W P (.some x y h) := by
  subst hx hy
  exact ⟨h, rfl⟩

lemma ecDbl_rep {a : ℕ} {b : ZMod p} (hpN : p ∣ N) (hN : 0 < N) {P D : ℕ × ℕ}
    {T : (curve p a b).Point} (hD : ecDbl N a P = some D) (hP : Rep (curve p a b) P T) :
    Rep (curve p a b) D (T + T) := by
  obtain ⟨h, rfl⟩ := hP
  simp only [ecDbl] at hD
  split_ifs at hD with hinv
  have hinv' := congrArg (Nat.cast : ℕ → ZMod p) hinv
  simp only [Nat.cast_mul, cast_mod hpN, Nat.cast_one, Nat.cast_ofNat] at hinv'
  have h2y : (2 : ZMod p) * (P.2 : ZMod p) ≠ 0 := left_ne_zero_of_mul_eq_one hinv'
  have hy : (P.2 : ZMod p) ≠ (curve p a b).negY (P.1 : ZMod p) (P.2 : ZMod p) := by
    intro hEq
    apply h2y
    simp only [negY, curve_a₁, curve_a₃, zero_mul, sub_zero] at hEq
    linear_combination hEq
  have hslope : (curve p a b).slope (P.1 : ZMod p) P.1 P.2 P.2 =
      (3 * (P.1 : ZMod p) * P.1 + a) * (invAux fuel (2 * P.2 % N) N : ZMod p) := by
    rw [slope_of_Y_ne rfl hy, div_eq_iff (sub_ne_zero.mpr hy)]
    simp only [negY, curve_a₁, curve_a₂, curve_a₃, curve_a₄]
    linear_combination (-(3 * (P.1 : ZMod p) * P.1 + a)) * hinv'
  rw [Point.add_self_of_Y_ne hy]
  obtain rfl := (Option.some.inj hD).symm
  apply rep_of_eq
  · simp only [Nat.cast_add, Nat.cast_mul, cast_mod hpN, cast_neg hpN hN, Nat.cast_ofNat,
      hslope, addX, curve_a₁, curve_a₂]
    ring
  · simp only [Nat.cast_add, Nat.cast_mul, cast_mod hpN, cast_neg hpN hN, Nat.cast_ofNat,
      hslope, addY, negAddY, addX, negY, curve_a₁, curve_a₂, curve_a₃]
    ring

lemma ecAdd_rep {a b : ZMod p} (hpN : p ∣ N) (hN : 0 < N) {P Q S : ℕ × ℕ}
    {T U : (curve p a b).Point} (hS : ecAdd N P Q = some S) (hP : Rep (curve p a b) P T)
    (hQ : Rep (curve p a b) Q U) : Rep (curve p a b) S (T + U) := by
  obtain ⟨h₁, rfl⟩ := hP
  obtain ⟨h₂, rfl⟩ := hQ
  simp only [ecAdd] at hS
  split_ifs at hS with hinv
  have hinv' := congrArg (Nat.cast : ℕ → ZMod p) hinv
  simp only [Nat.cast_mul, Nat.cast_add, cast_mod hpN, cast_neg hpN hN, Nat.cast_one] at hinv'
  have hd : (P.1 : ZMod p) + -(Q.1 : ZMod p) ≠ 0 := left_ne_zero_of_mul_eq_one hinv'
  have hx : (P.1 : ZMod p) ≠ (Q.1 : ZMod p) := fun hEq => hd (by rw [hEq, add_neg_cancel])
  have hslope : (curve p a b).slope (P.1 : ZMod p) Q.1 P.2 Q.2 =
      ((P.2 : ZMod p) + -Q.2) * (invAux fuel ((P.1 + (N - Q.1 % N)) % N) N : ZMod p) := by
    rw [slope_of_X_ne hx, div_eq_iff (sub_ne_zero.mpr hx)]
    linear_combination (-((P.2 : ZMod p) + -Q.2)) * hinv'
  rw [Point.add_of_X_ne hx]
  obtain rfl := (Option.some.inj hS).symm
  apply rep_of_eq
  · simp only [Nat.cast_add, Nat.cast_mul, cast_mod hpN, cast_neg hpN hN, hslope, addX,
      curve_a₁, curve_a₂]
    ring
  · simp only [Nat.cast_add, Nat.cast_mul, cast_mod hpN, cast_neg hpN hN, hslope, addY,
      negAddY, addX, negY, curve_a₁, curve_a₂, curve_a₃]
    ring

lemma ecMul_rep {a : ℕ} {b : ZMod p} (hpN : p ∣ N) (hN : 0 < N) {P : ℕ × ℕ}
    {T : (curve p a b).Point} (hP : Rep (curve p a b) P T) :
    ∀ (f k : ℕ) (S : ℕ × ℕ), 1 ≤ k → ecMul N a P f k = some S →
      Rep (curve p a b) S (k • T) := by
  intro f
  induction f with
  | zero =>
    intro k S _ h
    simp [ecMul] at h
  | succ f ih =>
    intro k S hk h
    rw [ecMul] at h
    split_ifs at h with hk1 hodd
    · obtain rfl := (Option.some.inj h).symm
      obtain rfl : k = 1 := by omega
      rwa [one_nsmul]
    · cases hQ : ecMul N a P f (k / 2) with
      | none => simp [hQ] at h
      | some Q =>
        simp only [hQ] at h
        have hQrep := ih (k / 2) Q (by omega) hQ
        cases hD : ecDbl N a Q with
        | none => simp [hD] at h
        | some D =>
          simp only [hD] at h
          have hSrep := ecAdd_rep hpN hN h (ecDbl_rep hpN hN hD hQrep) hP
          have hsmul : k • T = (k / 2) • T + (k / 2) • T + T := by
            conv_lhs => rw [show k = k / 2 + k / 2 + 1 by omega]
            rw [add_nsmul, add_nsmul, one_nsmul]
          rwa [hsmul]
    · cases hQ : ecMul N a P f (k / 2) with
      | none => simp [hQ] at h
      | some Q =>
        simp only [hQ] at h
        have hQrep := ih (k / 2) Q (by omega) hQ
        cases hD : ecDbl N a Q with
        | none => simp [hD] at h
        | some D =>
          simp only [hD] at h
          obtain rfl := (Option.some.inj h).symm
          have hsmul : k • T = (k / 2) • T + (k / 2) • T := by
            conv_lhs => rw [show k = k / 2 + k / 2 by omega]
            rw [add_nsmul]
          rw [hsmul]
          exact ecDbl_rep hpN hN hD hQrep

/-- The trivial point count: at most two points above each `x`, plus the point at infinity. -/
lemma point_finite_and_card (a b : ZMod p) :
    Finite (curve p a b).Point ∧ Nat.card (curve p a b).Point ≤ 2 * p + 1 := by
  classical
  let S : Finset (ZMod p × ZMod p) :=
    Finset.univ.filter fun xy => xy.2 ^ 2 = xy.1 ^ 3 + a * xy.1 + b
  have hS : S.card ≤ 2 * p := by
    have hsub : S ⊆ Finset.univ.biUnion fun x : ZMod p =>
        ((Polynomial.nthRoots 2 (x ^ 3 + a * x + b)).toFinset).image fun y => (x, y) := by
      intro xy hxy
      rw [Finset.mem_filter] at hxy
      refine Finset.mem_biUnion.mpr ⟨xy.1, Finset.mem_univ _, Finset.mem_image.mpr ⟨xy.2, ?_, rfl⟩⟩
      rw [Multiset.mem_toFinset, Polynomial.mem_nthRoots (by norm_num)]
      exact hxy.2
    calc S.card
        ≤ (Finset.univ.biUnion fun x : ZMod p =>
            ((Polynomial.nthRoots 2 (x ^ 3 + a * x + b)).toFinset).image fun y => (x, y)).card :=
          Finset.card_le_card hsub
      _ ≤ ∑ x : ZMod p,
            (((Polynomial.nthRoots 2 (x ^ 3 + a * x + b)).toFinset).image fun y => (x, y)).card :=
          Finset.card_biUnion_le
      _ ≤ ∑ _x : ZMod p, 2 := Finset.sum_le_sum fun x _ =>
          Finset.card_image_le.trans
            ((Multiset.toFinset_card_le _).trans (Polynomial.card_nthRoots 2 _))
      _ = 2 * p := by simp [ZMod.card, mul_comm]
  let f : (curve p a b).Point → Option S := fun P =>
    match P with
    | .zero => none
    | .some x y h => some ⟨(x, y), by
        rw [Finset.mem_filter]
        refine ⟨Finset.mem_univ _, ?_⟩
        have := (equation_iff _ _).mp ((nonsingular_iff _ _).mp h).1
        simpa using this⟩
  have hf : Function.Injective f := by
    rintro (_ | ⟨x, y, h⟩) (_ | ⟨x', y', h'⟩) hEq
    · rfl
    · simp [f] at hEq
    · simp [f] at hEq
    · simp only [f, Option.some.injEq, Subtype.mk.injEq, Prod.mk.injEq] at hEq
      obtain ⟨rfl, rfl⟩ := hEq
      rfl
  refine ⟨Finite.of_injective f hf, ?_⟩
  calc Nat.card (curve p a b).Point ≤ Nat.card (Option S) := Nat.card_le_card_of_injective f hf
    _ = S.card + 1 := by simp [Nat.card_eq_fintype_card]
    _ ≤ 2 * p + 1 := by omega

end Soundness

/-- **One ECPP step is sound.** If `q` is prime and `stepCheck N a x y s q` evaluates to
`true`, then `N` is prime. -/
theorem prime_of_stepCheck {N a x y s q : ℕ} (hq : q.Prime) (h : stepCheck N a x y s q = true) :
    N.Prime := by
  open WeierstrassCurve.Affine in
  simp only [stepCheck, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨hN1, hs⟩, hbound⟩, hy2⟩, hrest⟩ := h
  cases hR : ecMul N a (x, y) fuel s with
  | none => simp [hR] at hrest
  | some R =>
  simp only [hR] at hrest
  cases hZ : ecMul N a R fuel (q - 1) with
  | none => simp [hZ] at hrest
  | some Z =>
  simp only [hZ, Bool.and_eq_true, decide_eq_true_eq] at hrest
  obtain ⟨hZx, hZy⟩ := hrest
  by_contra hNp
  have hN0 : 0 < N := by omega
  have hp : N.minFac.Prime := Nat.minFac_prime (by omega)
  have hpN : N.minFac ∣ N := Nat.minFac_dvd N
  have hp2 : N.minFac ^ 2 ≤ N := Nat.minFac_sq_le_self hN0 hNp
  generalize N.minFac = p at hp hpN hp2
  have : Fact p.Prime := ⟨hp⟩
  -- the curve through `(x, y)` modulo `p`
  obtain ⟨b, hb⟩ : ∃ b : ZMod p, b = (y : ZMod p) ^ 2 - (x : ZMod p) ^ 3 - (a : ZMod p) * x :=
    ⟨_, rfl⟩
  have h2y : (2 : ZMod p) * (y : ZMod p) ≠ 0 := by
    have := congrArg (Nat.cast : ℕ → ZMod p) hy2
    simp only [Nat.cast_mul, cast_mod hpN, Nat.cast_one, Nat.cast_ofNat] at this
    exact left_ne_zero_of_mul_eq_one this
  have hns : (curve p a b).Nonsingular (x : ZMod p) (y : ZMod p) := by
    rw [nonsingular_iff]
    refine ⟨?_, Or.inr ?_⟩
    · rw [equation_iff]
      simp only [curve_a₁, curve_a₂, curve_a₃, curve_a₄, curve_a₆, hb]
      ring
    · simp only [curve_a₁, curve_a₃, zero_mul, sub_zero]
      intro hEq
      apply h2y
      linear_combination hEq
  have hT : Rep (curve p a b) (x, y) (.some _ _ hns) := ⟨hns, rfl⟩
  have hRrep := ecMul_rep hpN hN0 hT fuel s R hs hR
  have hq2 := hq.two_le
  have hZrep := ecMul_rep hpN hN0 hRrep fuel (q - 1) Z (by omega) hZ
  obtain ⟨hRns, hRU⟩ := hRrep
  obtain ⟨hZns, hZU⟩ := hZrep
  generalize s • (Point.some _ _ hns : (curve p a b).Point) = U at hRU hZU
  have hqU : q • U = 0 := by
    have hsucc : q • U = (q - 1) • U + U := by
      conv_lhs => rw [show q = q - 1 + 1 by omega]
      exact succ_nsmul U (q - 1)
    rw [hsucc, hZU]
    conv_lhs => rw [hRU]
    apply Point.add_of_Y_eq
    · have := congrArg (Nat.cast : ℕ → ZMod p) hZx
      simpa only [cast_mod hpN] using this
    · have := congrArg (Nat.cast : ℕ → ZMod p) hZy
      simp only [Nat.cast_add, cast_mod hpN, Nat.cast_zero] at this
      simp only [negY, curve_a₁, curve_a₃, zero_mul, sub_zero]
      linear_combination this
  have hU0 : U ≠ 0 := by
    rw [hRU]
    exact Point.some_ne_zero _
  have : Fact q.Prime := ⟨hq⟩
  have hord : addOrderOf U = q := addOrderOf_eq_prime hqU hU0
  obtain ⟨hfin, hcard⟩ := point_finite_and_card (p := p) (a : ZMod p) b
  have hdvd : q ∣ Nat.card (curve p a b).Point := hord ▸ addOrderOf_dvd_natCard U
  have hle : q ≤ 2 * p + 1 := (Nat.le_of_dvd Nat.card_pos hdvd).trans hcard
  have h3 : (q - 1) ^ 2 ≤ 4 * N :=
    calc (q - 1) ^ 2 ≤ (2 * p) ^ 2 := Nat.pow_le_pow_left (by omega) 2
      _ = 4 * p ^ 2 := by ring
      _ ≤ 4 * N := Nat.mul_le_mul_left 4 hp2
  exact absurd h3 (not_le.mpr hbound)

end GoldbachGaps.ECPP
