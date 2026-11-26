import Mathlib

/-!
# World 5: in the product of the `ℤ/r`, the integers below `X` are an arc of one character

For pairwise coprime moduli `r ∈ s` with product `P`, let `c r` be an inverse of `P / r` modulo `r` and relabel the
class of `N` at `r` as `b r = c r · (N mod r) mod r`. Then

* `sum_crt_modEq`: `∑ r, b r · (P / r) ≡ N (mod P)` (Chinese remainders, explicitly);
* `exists_int_sum_div_eq`: `∑ r, b r / r = N / P + k` for an integer `k`: the class vector determines `N / P`
  modulo 1 through one additive character;
* `fract_sum_div_eq`: for `N < P` the fractional part of `∑ r, b r / r` is `N / P`;
* `lt_iff_fract_sum_div_lt`: so, for `N < P`, `N < X` exactly when that fractional part is below `X / P`.

The integers below `X` are therefore the class vectors whose character lies in an arc of length `X / P`: a separable
score on the classes is constrained by one additive condition of precision `X / P`.
-/

namespace GoldbachGaps.Worlds

open Finset

/-- **Chinese remainders, explicitly.** With `c r` an inverse of `∏ (s.erase r)` modulo `r`, the number `N` is
recovered modulo the product from the relabelled classes `c r · (N mod r) mod r`. -/
theorem sum_crt_modEq {s : Finset ℕ} (hcop : (s : Set ℕ).Pairwise Nat.Coprime) (c : ℕ → ℕ)
    (hc : ∀ r ∈ s, c r * (∏ r' ∈ s.erase r, r') ≡ 1 [MOD r]) (N : ℕ) :
    ∑ r ∈ s, ((c r * (N % r)) % r) * (∏ r' ∈ s.erase r, r') ≡ N [MOD ∏ r ∈ s, r] := by
  have key : ∀ r₀ ∈ s,
      ∑ r ∈ s, ((c r * (N % r)) % r) * (∏ r' ∈ s.erase r, r') ≡ N [MOD r₀] := by
    intro r₀ hr₀
    rw [← Finset.add_sum_erase s _ hr₀]
    have hothers : ∑ r ∈ s.erase r₀, ((c r * (N % r)) % r) * (∏ r' ∈ s.erase r, r') ≡ 0 [MOD r₀] := by
      apply (Nat.modEq_zero_iff_dvd).mpr
      apply Finset.dvd_sum
      intro r hr
      have hmem : r₀ ∈ s.erase r := Finset.mem_erase.mpr ⟨(Finset.ne_of_mem_erase hr).symm, hr₀⟩
      exact Dvd.dvd.mul_left (Finset.dvd_prod_of_mem _ hmem) _
    have hmain : ((c r₀ * (N % r₀)) % r₀) * (∏ r' ∈ s.erase r₀, r') ≡ N [MOD r₀] := by
      have h1 : ((c r₀ * (N % r₀)) % r₀) * (∏ r' ∈ s.erase r₀, r') ≡
          (c r₀ * (N % r₀)) * (∏ r' ∈ s.erase r₀, r') [MOD r₀] := (Nat.mod_modEq _ _).mul_right _
      have h2 : (c r₀ * (N % r₀)) * (∏ r' ∈ s.erase r₀, r') =
          (c r₀ * ∏ r' ∈ s.erase r₀, r') * (N % r₀) := by ring
      have h3 : (c r₀ * ∏ r' ∈ s.erase r₀, r') * (N % r₀) ≡ 1 * (N % r₀) [MOD r₀] :=
        (hc r₀ hr₀).mul_right _
      rw [h2] at h1
      rw [one_mul] at h3
      exact (h1.trans h3).trans (Nat.mod_modEq _ _)
    simpa using hmain.add hothers
  rw [Nat.modEq_iff_dvd]
  push_cast
  refine Finset.prod_dvd_of_coprime (fun a ha b hb hab => ?_) fun r hr => ?_
  · exact Nat.isCoprime_iff_coprime.mpr (hcop ha hb hab)
  · have h := (Nat.modEq_iff_dvd).mp (key r hr)
    push_cast at h
    exact h

/-- **The character.** The relabelled classes determine `N / P` modulo 1:
`∑ r, (c r · (N mod r) mod r) / r = N / P + k` for an integer `k`. -/
theorem exists_int_sum_div_eq {s : Finset ℕ} (hpos : ∀ r ∈ s, 0 < r)
    (hcop : (s : Set ℕ).Pairwise Nat.Coprime) (c : ℕ → ℕ)
    (hc : ∀ r ∈ s, c r * (∏ r' ∈ s.erase r, r') ≡ 1 [MOD r]) (N : ℕ) :
    ∃ k : ℤ, ∑ r ∈ s, (((c r * (N % r)) % r : ℕ) : ℚ) / r = (N : ℚ) / (∏ r ∈ s, r : ℕ) + k := by
  have hP : ((∏ r ∈ s, r : ℕ) : ℚ) ≠ 0 := by
    exact_mod_cast (Finset.prod_pos hpos).ne'
  obtain ⟨k, hk⟩ := (Nat.modEq_iff_dvd).mp (sum_crt_modEq hcop c hc N)
  refine ⟨-k, ?_⟩
  have hterm : ∀ r ∈ s, (((c r * (N % r)) % r : ℕ) : ℚ) / r =
      ((((c r * (N % r)) % r) * (∏ r' ∈ s.erase r, r') : ℕ) : ℚ) / (∏ r ∈ s, r : ℕ) := by
    intro r hr
    have hr0 : (r : ℚ) ≠ 0 := by exact_mod_cast (hpos r hr).ne'
    rw [← Finset.mul_prod_erase s (fun r => r) hr]
    push_cast
    have he : ((∏ r' ∈ s.erase r, (r' : ℚ))) ≠ 0 := by
      refine Finset.prod_ne_zero_iff.mpr fun r' hr' => ?_
      exact_mod_cast (hpos r' (Finset.mem_of_mem_erase hr')).ne'
    field_simp
  rw [Finset.sum_congr rfl hterm, ← Finset.sum_div]
  have hk' : ((N : ℤ) : ℚ) - ((∑ r ∈ s, ((c r * (N % r)) % r) * (∏ r' ∈ s.erase r, r') : ℕ) : ℚ) =
      ((∏ r ∈ s, r : ℕ) : ℚ) * (k : ℚ) := by
    have := congrArg (fun z : ℤ => (z : ℚ)) hk
    push_cast at this ⊢
    exact this
  rw [div_add' _ _ _ hP, div_left_inj₀ hP]
  push_cast at hk' ⊢
  linarith

/-- For `N` below the product, the fractional part of the character is `N / P`. -/
theorem fract_sum_div_eq {s : Finset ℕ} (hpos : ∀ r ∈ s, 0 < r)
    (hcop : (s : Set ℕ).Pairwise Nat.Coprime) (c : ℕ → ℕ)
    (hc : ∀ r ∈ s, c r * (∏ r' ∈ s.erase r, r') ≡ 1 [MOD r]) {N : ℕ} (hN : N < ∏ r ∈ s, r) :
    Int.fract (∑ r ∈ s, (((c r * (N % r)) % r : ℕ) : ℚ) / r) = (N : ℚ) / (∏ r ∈ s, r : ℕ) := by
  obtain ⟨k, hk⟩ := exists_int_sum_div_eq hpos hcop c hc N
  have hP : (0 : ℚ) < ((∏ r ∈ s, r : ℕ) : ℚ) := by exact_mod_cast Finset.prod_pos hpos
  rw [hk, Int.fract_add_intCast, Int.fract_eq_self]
  refine ⟨div_nonneg (Nat.cast_nonneg _) hP.le, ?_⟩
  rw [div_lt_one hP]
  exact_mod_cast hN

/-- **The integers below `X` are an arc.** For `N` below the product `P` of the moduli, `N < X` exactly when the
fractional part of the character of its class vector is below `X / P`. -/
theorem lt_iff_fract_sum_div_lt {s : Finset ℕ} (hpos : ∀ r ∈ s, 0 < r)
    (hcop : (s : Set ℕ).Pairwise Nat.Coprime) (c : ℕ → ℕ)
    (hc : ∀ r ∈ s, c r * (∏ r' ∈ s.erase r, r') ≡ 1 [MOD r]) {N : ℕ} (hN : N < ∏ r ∈ s, r) (X : ℕ) :
    N < X ↔ Int.fract (∑ r ∈ s, (((c r * (N % r)) % r : ℕ) : ℚ) / r) < (X : ℚ) / (∏ r ∈ s, r : ℕ) := by
  have hP : (0 : ℚ) < ((∏ r ∈ s, r : ℕ) : ℚ) := by exact_mod_cast Finset.prod_pos hpos
  rw [fract_sum_div_eq hpos hcop c hc hN, div_lt_div_iff_of_pos_right hP]
  exact_mod_cast Iff.rfl

end GoldbachGaps.Worlds
