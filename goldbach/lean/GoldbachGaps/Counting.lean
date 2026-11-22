import GoldbachGaps.Basic

/-!
# The counting bound for least Goldbach summands

A pure counting argument: each prime `p` is a Goldbach summand of at most `π(Y)`
numbers `n ≤ Y`, so at most `π(z) · π(Y)` numbers `n ≤ Y` have a Goldbach summand `≤ z`.
With Chebyshev's bound on `π` this yields, for all large `X`, an even `n` in `(X, 2X]`
with no Goldbach summand below `log X · log log X / 48`.

This is asymptotically stronger than the rate in Theorem `thm:lower` of
`slop/goldbach/paper.tex` (the transfer from large prime gaps), and it does not use
covering systems at all. It is a statement of the paper's type (a): "no small prime is
a summand". It does not assert that `n` has a Goldbach partition.
-/

open Finset Filter

namespace GoldbachGaps

/-- Union bound. A set of numbers `n ≤ Y`, each having a Goldbach summand `≤ z`, has at
most `π(z) · π(Y)` elements: `n ↦ (p, n - p)` injects it into pairs of primes. -/
theorem card_le_of_forall_exists_summand (Y z : ℕ) (S : Finset ℕ)
    (hS : ∀ n ∈ S, n ≤ Y ∧ ∃ p ≤ z, IsSummand n p) :
    #S ≤ Nat.primeCounting z * Nat.primeCounting Y := by
  calc #S ≤ #((Nat.primesLE z ×ˢ Nat.primesLE Y).image fun pq : ℕ × ℕ => pq.1 + pq.2) := by
        refine card_le_card fun n hn => ?_
        obtain ⟨hnY, p, hpz, hp, hq⟩ := hS n hn
        have h2 := hq.two_le
        refine mem_image.mpr ⟨(p, n - p), mem_product.mpr
          ⟨Nat.mem_primesLE.mpr ⟨hpz, hp⟩, Nat.mem_primesLE.mpr ⟨by omega, hq⟩⟩, ?_⟩
        show p + (n - p) = n
        omega
    _ ≤ #(Nat.primesLE z ×ˢ Nat.primesLE Y) := card_image_le
    _ = Nat.primeCounting z * Nat.primeCounting Y := by
        rw [card_product, Nat.primesLE_card_eq_primeCounting,
          Nat.primesLE_card_eq_primeCounting]

/-- Pigeonhole form: if `π(z) · π(2X) < X / 2`, some even `n` in `(X, 2X]` has no
Goldbach summand `≤ z`. -/
theorem exists_even_forall_not_isSummand {X z : ℕ}
    (h : Nat.primeCounting z * Nat.primeCounting (2 * X) < X / 2) :
    ∃ n, X < n ∧ n ≤ 2 * X ∧ Even n ∧ ∀ p ≤ z, ¬ IsSummand n p := by
  by_contra hcon
  push Not at hcon
  have hinj : Function.Injective fun m : ℕ => 2 * m := fun a b hab => by
    simp only at hab
    omega
  have key := card_le_of_forall_exists_summand (2 * X) z ((Ioc (X / 2) X).image fun m => 2 * m)
    (fun n hn => by
      obtain ⟨m, hm, rfl⟩ := mem_image.mp hn
      rw [mem_Ioc] at hm
      exact ⟨by omega, hcon (2 * m) (by omega) (by omega) (even_two_mul m)⟩)
  rw [card_image_of_injective _ hinj, Nat.card_Ioc] at key
  omega

/-- Rate form of the counting bound: for all sufficiently large `X` there is an even `n`
with `X < n ≤ 2X` none of whose Goldbach summands is `≤ log X · log log X / 48`.
(The constant is far from optimal; the counting argument gives `1/2 + o(1)` for `n ≤ X`.) -/
theorem eventually_exists_even_forall_not_isSummand :
    ∀ᶠ X : ℕ in atTop, ∃ n, X < n ∧ n ≤ 2 * X ∧ Even n ∧
      ∀ p : ℕ, (p : ℝ) ≤ Real.log X * Real.log (Real.log X) / 48 → ¬ IsSummand n p := by
  have hC : Real.log 4 + 1 ≤ 12 / 5 := by
    have h4 : Real.log 4 = 2 * Real.log 2 := by
      rw [show (4 : ℝ) = 2 ^ 2 by norm_num, Real.log_pow]
      norm_num
    have := Real.log_two_lt_d9
    linarith
  have hcheb := Chebyshev.eventually_primeCounting_le (ε := 1) one_pos
  have hL : Tendsto (fun X : ℕ => Real.log X) atTop atTop :=
    Real.tendsto_log_atTop.comp tendsto_natCast_atTop_atTop
  have hz : Tendsto (fun X : ℕ => Real.log X * Real.log (Real.log X) / 48) atTop atTop :=
    (hL.atTop_mul_atTop₀ (Real.tendsto_log_atTop.comp hL)).atTop_div_const (by norm_num)
  have h2X : Tendsto (fun X : ℕ => ((2 * X : ℕ) : ℝ)) atTop atTop :=
    tendsto_natCast_atTop_atTop.comp
      (tendsto_atTop_mono (fun n => by show n ≤ 2 * n; omega) tendsto_id)
  filter_upwards [hz.eventually hcheb, h2X.eventually hcheb,
    hL.eventually_ge_atTop (Real.exp 48), eventually_ge_atTop 2] with X hzX h2 hLX hX2
  set L := Real.log X with hLdef
  set z := L * Real.log L / 48 with hzdef
  have hLpos : 0 < L := lt_of_lt_of_le (Real.exp_pos 48) hLX
  have hlogL : 48 ≤ Real.log L := (Real.le_log_iff_exp_le hLpos).mpr hLX
  have hLz : L ≤ z := by
    rw [hzdef, le_div_iff₀ (by norm_num)]
    nlinarith
  have hlogz : Real.log L ≤ Real.log z := Real.log_le_log hLpos hLz
  have hXpos : (0 : ℝ) < X := by
    have : (2 : ℝ) ≤ X := by exact_mod_cast hX2
    linarith
  -- bound on π(⌊z⌋)
  have h1 : (Nat.primeCounting ⌊z⌋₊ : ℝ) ≤ L / 20 := by
    have hzpos : 0 ≤ z := le_trans hLpos.le hLz
    calc (Nat.primeCounting ⌊z⌋₊ : ℝ) ≤ (Real.log 4 + 1) * z / Real.log z := hzX
      _ ≤ 12 / 5 * z / Real.log L := by
          have : (Real.log 4 + 1) * z ≤ 12 / 5 * z := mul_le_mul_of_nonneg_right hC hzpos
          have h48 : (0 : ℝ) < Real.log L := by linarith
          calc (Real.log 4 + 1) * z / Real.log z ≤ 12 / 5 * z / Real.log z :=
                div_le_div_of_nonneg_right this (le_trans h48.le hlogz)
            _ ≤ 12 / 5 * z / Real.log L :=
                div_le_div_of_nonneg_left (by positivity) h48 hlogz
      _ = L / 20 := by
          have h48 : Real.log L ≠ 0 := by linarith
          rw [hzdef]
          field_simp
          ring
  -- bound on π(2X)
  have h2' : (Nat.primeCounting (2 * X) : ℝ) ≤ 12 / 5 * (2 * X) / L := by
    rw [Nat.floor_natCast] at h2
    have hle : L ≤ Real.log ((2 * X : ℕ) : ℝ) := by
      apply Real.log_le_log hXpos
      push_cast
      linarith
    have hnum : (0 : ℝ) ≤ ((2 * X : ℕ) : ℝ) := by positivity
    calc (Nat.primeCounting (2 * X) : ℝ)
        ≤ (Real.log 4 + 1) * ((2 * X : ℕ) : ℝ) / Real.log ((2 * X : ℕ) : ℝ) := h2
      _ ≤ 12 / 5 * ((2 * X : ℕ) : ℝ) / Real.log ((2 * X : ℕ) : ℝ) :=
          div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_right hC hnum) (le_trans hLpos.le hle)
      _ ≤ 12 / 5 * ((2 * X : ℕ) : ℝ) / L :=
          div_le_div_of_nonneg_left (by positivity) hLpos hle
      _ = 12 / 5 * (2 * X) / L := by push_cast; ring
  -- combine
  have hprod : (Nat.primeCounting ⌊z⌋₊ : ℝ) * Nat.primeCounting (2 * X) ≤ 6 / 25 * X := by
    calc (Nat.primeCounting ⌊z⌋₊ : ℝ) * Nat.primeCounting (2 * X)
        ≤ L / 20 * (12 / 5 * (2 * X) / L) :=
          mul_le_mul h1 h2' (by positivity) (by positivity)
      _ = 6 / 25 * X := by
          field_simp
          ring
  have hhalf : ((X : ℝ) - 1) / 2 ≤ ((X / 2 : ℕ) : ℝ) := by
    have hnat : X ≤ 2 * (X / 2) + 1 := by omega
    have : (X : ℝ) ≤ 2 * ((X / 2 : ℕ) : ℝ) + 1 := by exact_mod_cast hnat
    linarith
  have hlt : Nat.primeCounting ⌊z⌋₊ * Nat.primeCounting (2 * X) < X / 2 := by
    have hX2' : (2 : ℝ) ≤ X := by exact_mod_cast hX2
    have : ((Nat.primeCounting ⌊z⌋₊ * Nat.primeCounting (2 * X) : ℕ) : ℝ) < ((X / 2 : ℕ) : ℝ) := by
      push_cast
      calc (Nat.primeCounting ⌊z⌋₊ : ℝ) * Nat.primeCounting (2 * X) ≤ 6 / 25 * X := hprod
        _ < ((X : ℝ) - 1) / 2 := by linarith
        _ ≤ ((X / 2 : ℕ) : ℝ) := hhalf
    exact_mod_cast this
  obtain ⟨n, hn1, hn2, hn3, hn4⟩ := exists_even_forall_not_isSummand hlt
  exact ⟨n, hn1, hn2, hn3, fun p hp => hn4 p (Nat.le_floor hp)⟩

end GoldbachGaps
