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

The research session's statement of 26 November 2026, in its notation (`u r` an integer inverse of `P / r` modulo
`r`, classes not reduced after the multiplication, `X` real):

* `int_sum_crt_modEq` (S1): for every integer `x`, `x ≡ ∑ r, (x mod r) · u r · (P / r)` modulo `P`;
  `exists_int_sum_mul_div_eq`: `∑ r, (x mod r) · u r / r - x / P` is an integer;
* `lt_iff_fract_sum_mul_div_lt` (S2): for `N < P` and real `X`, `N < X` iff the fractional part of
  `∑ r, (N mod r) · u r / r` is below `X / P`;
* the two facts under the dynamic programme over partial sums (S3): `eq_of_partial_sum_modEq` (on a subset `t` of
  the moduli the partial assignments have pairwise different partial sums modulo the partial product, so a grid
  finer than `1 / P_t` loses nothing) and `sum_sub_sum_eq_of_agree` (two assignments that agree outside `t` have
  full sums differing by exactly the difference of their partial sums over `t`).
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

/-! ### The same in the notation of the research session's statement (S1, S2), and the two facts behind (S3) -/

/-- **(S1).** For every integer `x`, `x ≡ ∑ r, (x mod r) · u r · (P / r)` modulo `P`, `u r` an inverse of `P / r`
modulo `r`. -/
theorem int_sum_crt_modEq {s : Finset ℕ} (hcop : (s : Set ℕ).Pairwise Nat.Coprime) (u : ℕ → ℤ)
    (hu : ∀ r ∈ s, u r * (∏ r' ∈ s.erase r, (r' : ℤ)) ≡ 1 [ZMOD (r : ℤ)]) (x : ℤ) :
    ∑ r ∈ s, (x % (r : ℤ)) * u r * (∏ r' ∈ s.erase r, (r' : ℤ)) ≡ x [ZMOD ∏ r ∈ s, (r : ℤ)] := by
  have key : ∀ r₀ ∈ s,
      ∑ r ∈ s, (x % (r : ℤ)) * u r * (∏ r' ∈ s.erase r, (r' : ℤ)) ≡ x [ZMOD (r₀ : ℤ)] := by
    intro r₀ hr₀
    rw [← Finset.add_sum_erase s _ hr₀]
    have hothers : ∑ r ∈ s.erase r₀, (x % (r : ℤ)) * u r * (∏ r' ∈ s.erase r, (r' : ℤ)) ≡ 0
        [ZMOD (r₀ : ℤ)] := by
      apply (Int.modEq_zero_iff_dvd).mpr
      apply Finset.dvd_sum
      intro r hr
      have hmem : r₀ ∈ s.erase r := Finset.mem_erase.mpr ⟨(Finset.ne_of_mem_erase hr).symm, hr₀⟩
      exact Dvd.dvd.mul_left (Finset.dvd_prod_of_mem (fun r' : ℕ => (r' : ℤ)) hmem) _
    have hmain : (x % (r₀ : ℤ)) * u r₀ * (∏ r' ∈ s.erase r₀, (r' : ℤ)) ≡ x [ZMOD (r₀ : ℤ)] := by
      have h1 : (x % (r₀ : ℤ)) * (u r₀ * ∏ r' ∈ s.erase r₀, (r' : ℤ)) ≡ x * 1 [ZMOD (r₀ : ℤ)] :=
        (Int.mod_modEq x r₀).mul (hu r₀ hr₀)
      rwa [mul_one, ← mul_assoc] at h1
    simpa using hmain.add hothers
  rw [Int.modEq_iff_dvd]
  refine Finset.prod_dvd_of_coprime (fun a ha b hb hab => ?_) fun r hr => ?_
  · exact Nat.isCoprime_iff_coprime.mpr (hcop ha hb hab)
  · exact (Int.modEq_iff_dvd).mp (key r hr)

/-- **(S1), divided by `P`.** `∑ r, (x mod r) · u r / r - x / P` is an integer. -/
theorem exists_int_sum_mul_div_eq {s : Finset ℕ} (hpos : ∀ r ∈ s, 0 < r)
    (hcop : (s : Set ℕ).Pairwise Nat.Coprime) (u : ℕ → ℤ)
    (hu : ∀ r ∈ s, u r * (∏ r' ∈ s.erase r, (r' : ℤ)) ≡ 1 [ZMOD (r : ℤ)]) (x : ℤ) :
    ∃ k : ℤ, ∑ r ∈ s, ((x % (r : ℤ) : ℤ) : ℝ) * (u r : ℝ) / (r : ℝ) =
      (x : ℝ) / ((∏ r ∈ s, r : ℕ) : ℝ) + k := by
  have hP : ((∏ r ∈ s, r : ℕ) : ℝ) ≠ 0 := by
    exact_mod_cast (Finset.prod_pos hpos).ne'
  obtain ⟨k, hk⟩ := (Int.modEq_iff_dvd).mp (int_sum_crt_modEq hcop u hu x)
  refine ⟨-k, ?_⟩
  have hterm : ∀ r ∈ s, ((x % (r : ℤ) : ℤ) : ℝ) * (u r : ℝ) / (r : ℝ) =
      (((x % (r : ℤ)) * u r * (∏ r' ∈ s.erase r, (r' : ℤ)) : ℤ) : ℝ) / ((∏ r ∈ s, r : ℕ) : ℝ) := by
    intro r hr
    have hr0 : (r : ℝ) ≠ 0 := by exact_mod_cast (hpos r hr).ne'
    rw [← Finset.mul_prod_erase s (fun r => r) hr]
    push_cast
    have he : ((∏ r' ∈ s.erase r, (r' : ℝ))) ≠ 0 := by
      refine Finset.prod_ne_zero_iff.mpr fun r' hr' => ?_
      exact_mod_cast (hpos r' (Finset.mem_of_mem_erase hr')).ne'
    field_simp
  rw [Finset.sum_congr rfl hterm, ← Finset.sum_div, div_add' _ _ _ hP, div_left_inj₀ hP]
  have hk' := congrArg (fun z : ℤ => (z : ℝ)) hk
  push_cast at hk' ⊢
  linarith

/-- **(S2).** For `0 ≤ N < P` and any real `X`: `N < X` exactly when the fractional part of
`∑ r, (N mod r) · u r / r` is below `X / P`. -/
theorem lt_iff_fract_sum_mul_div_lt {s : Finset ℕ} (hpos : ∀ r ∈ s, 0 < r)
    (hcop : (s : Set ℕ).Pairwise Nat.Coprime) (u : ℕ → ℤ)
    (hu : ∀ r ∈ s, u r * (∏ r' ∈ s.erase r, (r' : ℤ)) ≡ 1 [ZMOD (r : ℤ)]) {N : ℕ}
    (hN : N < ∏ r ∈ s, r) (X : ℝ) :
    (N : ℝ) < X ↔
      Int.fract (∑ r ∈ s, ((N % r : ℕ) : ℝ) * (u r : ℝ) / (r : ℝ)) < X / ((∏ r ∈ s, r : ℕ) : ℝ) := by
  have hP : (0 : ℝ) < ((∏ r ∈ s, r : ℕ) : ℝ) := by exact_mod_cast Finset.prod_pos hpos
  obtain ⟨k, hk⟩ := exists_int_sum_mul_div_eq hpos hcop u hu (N : ℤ)
  have hsum : ∑ r ∈ s, ((N % r : ℕ) : ℝ) * (u r : ℝ) / (r : ℝ) =
      (N : ℝ) / ((∏ r ∈ s, r : ℕ) : ℝ) + k := by
    have e : ∀ r ∈ s, ((((N : ℤ) % (r : ℤ) : ℤ)) : ℝ) = ((N % r : ℕ) : ℝ) := by
      intro r _
      rw [← Int.natCast_mod, Int.cast_natCast]
    rw [Finset.sum_congr rfl (fun r hr => by rw [e r hr]), Int.cast_natCast] at hk
    exact hk
  have hfr : Int.fract ((N : ℝ) / ((∏ r ∈ s, r : ℕ) : ℝ)) = (N : ℝ) / ((∏ r ∈ s, r : ℕ) : ℝ) := by
    rw [Int.fract_eq_self]
    refine ⟨div_nonneg (Nat.cast_nonneg _) hP.le, ?_⟩
    rw [div_lt_one hP]
    exact_mod_cast hN
  rw [hsum, Int.fract_add_intCast, hfr, div_lt_div_iff_of_pos_right hP]

/-- **(S3), first fact: nothing is lost on a part of the moduli.** For a subset `t` of the moduli, two class
vectors on `t` whose partial sums `∑ r ∈ t, b r · u r · (P_t / r)` agree modulo the partial product `P_t` are equal:
the `P_t` partial assignments have `P_t` different partial sums `∑ r ∈ t, b r · u r / r` modulo 1, all multiples of
`1 / P_t`. -/
theorem eq_of_partial_sum_modEq {s t : Finset ℕ} (hts : t ⊆ s) (hcop : (s : Set ℕ).Pairwise Nat.Coprime)
    (u : ℕ → ℤ) (hu : ∀ r ∈ s, u r * (∏ r' ∈ s.erase r, (r' : ℤ)) ≡ 1 [ZMOD (r : ℤ)])
    (b b' : ℕ → ℕ) (hb : ∀ r ∈ t, b r < r) (hb' : ∀ r ∈ t, b' r < r)
    (h : ∑ r ∈ t, (b r : ℤ) * u r * (∏ r' ∈ t.erase r, (r' : ℤ)) ≡
      ∑ r ∈ t, (b' r : ℤ) * u r * (∏ r' ∈ t.erase r, (r' : ℤ)) [ZMOD ∏ r ∈ t, (r : ℤ)]) :
    ∀ r ∈ t, b r = b' r := by
  intro r₀ hr₀
  have hmod : ∀ c : ℕ → ℕ, ∑ r ∈ t, (c r : ℤ) * u r * (∏ r' ∈ t.erase r, (r' : ℤ)) ≡
      (c r₀ : ℤ) * u r₀ * (∏ r' ∈ t.erase r₀, (r' : ℤ)) [ZMOD (r₀ : ℤ)] := by
    intro c
    rw [← Finset.add_sum_erase t _ hr₀]
    have hothers : ∑ r ∈ t.erase r₀, (c r : ℤ) * u r * (∏ r' ∈ t.erase r, (r' : ℤ)) ≡ 0
        [ZMOD (r₀ : ℤ)] := by
      apply (Int.modEq_zero_iff_dvd).mpr
      apply Finset.dvd_sum
      intro r hr
      have hmem : r₀ ∈ t.erase r := Finset.mem_erase.mpr ⟨(Finset.ne_of_mem_erase hr).symm, hr₀⟩
      exact Dvd.dvd.mul_left (Finset.dvd_prod_of_mem (fun r' : ℕ => (r' : ℤ)) hmem) _
    simpa using (Int.ModEq.refl ((c r₀ : ℤ) * u r₀ * (∏ r' ∈ t.erase r₀, (r' : ℤ)))).add hothers
  have hdvd : (r₀ : ℤ) ∣ ∏ r ∈ t, (r : ℤ) := Finset.dvd_prod_of_mem (fun r : ℕ => (r : ℤ)) hr₀
  have h0 : (b r₀ : ℤ) * u r₀ * (∏ r' ∈ t.erase r₀, (r' : ℤ)) ≡
      (b' r₀ : ℤ) * u r₀ * (∏ r' ∈ t.erase r₀, (r' : ℤ)) [ZMOD (r₀ : ℤ)] :=
    ((hmod b).symm.trans (h.of_dvd hdvd)).trans (hmod b')
  -- `u r₀` and the partial product without `r₀` are units modulo `r₀`
  have hcu : IsCoprime (u r₀) (r₀ : ℤ) := by
    obtain ⟨k, hk⟩ := (Int.modEq_iff_dvd).mp (hu r₀ (hts hr₀))
    exact ⟨∏ r' ∈ s.erase r₀, (r' : ℤ), k, by linarith⟩
  have hcE : IsCoprime (∏ r' ∈ t.erase r₀, (r' : ℤ)) (r₀ : ℤ) :=
    IsCoprime.prod_left fun r' hr' =>
      Nat.isCoprime_iff_coprime.mpr
        (hcop (hts (Finset.mem_of_mem_erase hr')) (hts hr₀) (Finset.ne_of_mem_erase hr'))
  have hdiv : (r₀ : ℤ) ∣ ((b' r₀ : ℤ) - b r₀) * (u r₀ * ∏ r' ∈ t.erase r₀, (r' : ℤ)) := by
    have := (Int.modEq_iff_dvd).mp h0
    have e : (b' r₀ : ℤ) * u r₀ * (∏ r' ∈ t.erase r₀, (r' : ℤ)) -
        (b r₀ : ℤ) * u r₀ * (∏ r' ∈ t.erase r₀, (r' : ℤ)) =
        ((b' r₀ : ℤ) - b r₀) * (u r₀ * ∏ r' ∈ t.erase r₀, (r' : ℤ)) := by ring
    rwa [e] at this
  have hdiv' : (r₀ : ℤ) ∣ (b' r₀ : ℤ) - b r₀ :=
    (IsCoprime.mul_left hcu hcE).symm.dvd_of_dvd_mul_right hdiv
  have h1 := hb r₀ hr₀
  have h2 := hb' r₀ hr₀
  obtain ⟨k, hk⟩ := hdiv'
  have hk0 : k = 0 := by
    by_contra hne
    rcases lt_or_gt_of_ne hne with hlt | hgt
    · have : (r₀ : ℤ) * k ≤ -(r₀ : ℤ) := by nlinarith [Int.natCast_nonneg r₀]
      omega
    · have : (r₀ : ℤ) ≤ (r₀ : ℤ) * k := by nlinarith [Int.natCast_nonneg r₀]
      omega
  rw [hk0, mul_zero] at hk
  omega

/-- **(S3), second fact: a bucket is safe.** If two assignments agree outside `t`, their full sums differ by
exactly as much as their partial sums over `t`: two partial assignments in one bucket of width `η` stay within `η`
of each other under every common completion. -/
theorem sum_sub_sum_eq_of_agree {s t : Finset ℕ} (hts : t ⊆ s) (f g : ℕ → ℝ) (hfg : ∀ r ∈ s \ t, f r = g r) :
    ∑ r ∈ s, f r - ∑ r ∈ s, g r = ∑ r ∈ t, f r - ∑ r ∈ t, g r := by
  rw [← Finset.sum_sdiff hts, ← Finset.sum_sdiff (f := g) hts, Finset.sum_congr rfl hfg]
  ring

end GoldbachGaps.Worlds
