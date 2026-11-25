import GoldbachGaps.CoverPairs
import GoldbachGaps.CoverBound

/-!
# The pair weight in product form, and its partial sums

`GoldbachGaps/CoverPairs.lean` proves that the pair weight of two rows in one class of a modulus
`s`, times the Hardy–Littlewood factors, has mean exactly `a = 6 s/(s - 1)` over the differences
`d = 6 s j`. The research session's computation of the spread of the rows of a class
(`goldbach/sublinear/cover_price_hl.py`, `cover_limit.py` on branch `ccr-d4a17dd0-7uu03r`; its
message of 24 November 2026, 19:11 UTC, items 3a and 3b) uses more: the weight is a product over
the primes dividing `j`, its partial sums are a finite sum with no cancellation, and they never
exceed the mean. This file proves those statements, for every truncation of the products
(`pairWeight s A B`, with `B` a finite set of primes `≥ 5` other than `s` and `A ⊆ B` the moduli
that carry a pair weight).

* `uw A t`: `u_t = 2/(t - 3)` for `t ∈ A` and `1/(t - 2)` otherwise; `w0 A t`: the weight of `t`
  at the differences it does not divide. `weight_eq`: the weight of `t` at `d = c j` is `w0` if
  `t ∤ j` and `w0 · (1 + u_t)` if `t ∣ j`. `w0_mul`: `w0 · (1 + u_t/t) = 1`.
* `pairWeight_eq_prod`: **the product form**, `W(j) = a · c · ∏_{t ∈ B, t ∣ j} (1 + u_t)` with
  `c = ∏_{t ∈ B} w0 = ∏ (1 + u_t/t)⁻¹` (`prod_w0_mul_sum`).
* `sum_Ioc_pairWeight`: **the partial sums**, `∑_{j ≤ m} W(j) = a c ∑_D u(D) ⌊m/d(D)⌋`, the sum
  over the subsets `D` of `B`, `u(D) = ∏_{t ∈ D} u_t`, `d(D) = ∏_{t ∈ D} t`.
* `pairWeight_defect`: `a m - ∑_{j ≤ m} W(j) = a c ∑_D u(D) (m/d(D) - ⌊m/d(D)⌋)`, and so
  `sum_Ioc_pairWeight_le`: **`∑_{j ≤ m} W(j) ≤ a m` for every `m`**. Every term of the defect is
  nonnegative; this is what lets the pair sum be computed without cancellation.
* `local_ratio_below`, `local_ratio_above`: the two local identities of item 3b, as written.
* `one_half_le_twinPrimeConstant`, `twinPrimeConstant_pos`: `C₂ ≥ 1/2`, from
  `Cap.prod_pred_sq_le`; `tendsto_prod_sq_div`: `∏_{5 ≤ t ≤ w} (t - 1)²/(t (t - 2)) → 3/(4 C₂)`.

What the research session does with these (the limit profile of the spread, the price equation,
the constant `1.1275`) is heuristic and is not formalised.
-/

namespace GoldbachGaps.CoverPairs

open Finset Filter

/-- The full pair weight at the difference `d = 6 s j`, truncated to the primes of `B`: the pair
weights of `3` and of the moduli `A`, times the Hardy–Littlewood factors of `2`, `3`, `s` and
`B`. -/
def pairWeight (s : ℕ) (A B : Finset ℕ) (j : ℕ) : ℚ :=
  (rho 3 (6 * s * j) * ∏ t ∈ A, rho t (6 * s * j)) *
    (sigma 2 (6 * s * j) * sigma 3 (6 * s * j) * sigma s (6 * s * j) *
      ∏ t ∈ B, sigma t (6 * s * j))

/-- `u_t`: how much more a multiple of `t` weighs. -/
def uw (A : Finset ℕ) (t : ℕ) : ℚ := if t ∈ A then 2 / ((t : ℚ) - 3) else 1 / ((t : ℚ) - 2)

/-- The weight of `t` at the differences it does not divide. -/
def w0 (A : Finset ℕ) (t : ℕ) : ℚ :=
  if t ∈ A then (1 - 1 / ((t : ℚ) - 2) ^ 2) * (1 - 1 / ((t : ℚ) - 1) ^ 2)
  else 1 - 1 / ((t : ℚ) - 1) ^ 2

theorem one_sub_inv_sq_nonneg {x : ℚ} (hx : 1 ≤ x) : 0 ≤ 1 - 1 / x ^ 2 := by
  have h1 : (1 : ℚ) ≤ x ^ 2 := by nlinarith
  have h2 : 1 / x ^ 2 ≤ 1 := by
    rw [div_le_one (by positivity)]
    exact h1
  linarith

theorem uw_nonneg (A : Finset ℕ) {t : ℕ} (ht : 4 ≤ t) : 0 ≤ uw A t := by
  have h4 : (4 : ℚ) ≤ t := by exact_mod_cast ht
  unfold uw
  split_ifs
  · exact div_nonneg (by norm_num) (by linarith)
  · exact div_nonneg (by norm_num) (by linarith)

theorem w0_nonneg (A : Finset ℕ) {t : ℕ} (ht : 4 ≤ t) : 0 ≤ w0 A t := by
  have h4 : (4 : ℚ) ≤ t := by exact_mod_cast ht
  unfold w0
  split_ifs
  · exact mul_nonneg (one_sub_inv_sq_nonneg (by linarith)) (one_sub_inv_sq_nonneg (by linarith))
  · exact one_sub_inv_sq_nonneg (by linarith)

/-- `w0 · (1 + u_t/t) = 1`: over a period the weight of `t` has mean one. -/
theorem w0_mul (A : Finset ℕ) {t : ℕ} (ht : 4 ≤ t) : w0 A t * (1 + uw A t / t) = 1 := by
  have h4 : (4 : ℚ) ≤ t := by exact_mod_cast ht
  have e0 : (t : ℚ) ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ)).ne'
  have e1 : (t : ℚ) - 1 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 1).ne'
  have e2 : (t : ℚ) - 2 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 2).ne'
  have e3 : (t : ℚ) - 3 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 3).ne'
  unfold w0 uw
  split_ifs
  · field_simp
    ring
  · field_simp
    ring

/-- The weight of `t` at the difference `c j`, for `t` prime to `c`: `w0` if `t ∤ j`, and
`w0 · (1 + u_t)` if `t ∣ j`. -/
theorem weight_eq (A : Finset ℕ) {t c : ℕ} (ht : 4 ≤ t) (hc : Nat.Coprime t c) (j : ℕ) :
    (if t ∈ A then rho t (c * j) else 1) * sigma t (c * j) =
      w0 A t * (if t ∣ j then 1 + uw A t else 1) := by
  have h4 : (4 : ℚ) ≤ t := by exact_mod_cast ht
  have e0 : (t : ℚ) ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ)).ne'
  have e1 : (t : ℚ) - 1 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 1).ne'
  have e2 : (t : ℚ) - 2 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 2).ne'
  have e3 : (t : ℚ) - 3 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 3).ne'
  have hdvd : t ∣ c * j ↔ t ∣ j := hc.dvd_mul_left
  by_cases hA : t ∈ A <;> by_cases hj : t ∣ j
  · rw [rho_of_dvd (by omega) (hdvd.2 hj), sigma_of_dvd (by omega) (hdvd.2 hj)]
    simp only [w0, uw, hA, hj, ↓reduceIte]
    field_simp
    ring
  · rw [rho_of_not_dvd (by omega) (fun h => hj (hdvd.1 h)),
      sigma_of_not_dvd (by omega) (fun h => hj (hdvd.1 h))]
    simp only [w0, hA, hj, ↓reduceIte, mul_one]
  · rw [sigma_of_dvd (by omega) (hdvd.2 hj)]
    simp only [w0, uw, hA, hj, ↓reduceIte, one_mul]
    field_simp
    ring
  · rw [sigma_of_not_dvd (by omega) (fun h => hj (hdvd.1 h))]
    simp only [w0, hA, hj, ↓reduceIte, one_mul, mul_one]

/-- Every prime of `B` is prime to `6 s`. -/
theorem coprime_six_mul {s : ℕ} (hs : s.Prime) {t : ℕ} (ht : t.Prime ∧ 5 ≤ t ∧ t ≠ s) :
    Nat.Coprime t (6 * s) := by
  obtain ⟨htp, ht5, hts⟩ := ht
  refine Nat.Coprime.mul_right ?_ ((Nat.coprime_primes htp hs).2 hts)
  have h2 : Nat.Coprime t 2 := (Nat.coprime_primes htp Nat.prime_two).2 (by omega)
  have h3 : Nat.Coprime t 3 := (Nat.coprime_primes htp Nat.prime_three).2 (by omega)
  exact Nat.Coprime.mul_right h2 h3

/-- **The pair weight in product form**: `W(j) = a · c · ∏ (1 + u_t)` over the primes of `B`
that divide `j`, with `a = 6 s/(s - 1)` and `c = ∏_{t ∈ B} w0`. -/
theorem pairWeight_eq_prod {s : ℕ} (hs : s.Prime) (hs5 : 5 ≤ s) (A B : Finset ℕ) (hAB : A ⊆ B)
    (hB : ∀ t ∈ B, t.Prime ∧ 5 ≤ t ∧ t ≠ s) (j : ℕ) :
    pairWeight s A B j =
      6 * (s : ℚ) / ((s : ℚ) - 1) * (∏ t ∈ B, w0 A t) * ∏ t ∈ B with t ∣ j, (1 + uw A t) := by
  classical
  have hs2 : (2 : ℚ) ≤ s := by exact_mod_cast (by omega : 2 ≤ s)
  have hs1 : (s : ℚ) - 1 ≠ 0 := (by linarith : (0 : ℚ) < (s : ℚ) - 1).ne'
  have e3 : rho 3 (6 * s * j) = 2 := by
    rw [rho_of_dvd (le_refl 3) ⟨2 * s * j, by ring⟩]
    norm_num
  have f2 : sigma 2 (6 * s * j) = 2 := by
    rw [sigma_of_dvd (le_refl 2) ⟨3 * s * j, by ring⟩]
    norm_num
  have f3 : sigma 3 (6 * s * j) = 3 / 2 := by
    rw [sigma_of_dvd (by norm_num) ⟨2 * s * j, by ring⟩]
    norm_num
  have fs : sigma s (6 * s * j) = (s : ℚ) / ((s : ℚ) - 1) := by
    rw [sigma_of_dvd (by omega) ⟨6 * j, by ring⟩]
  have hprod : (∏ t ∈ A, rho t (6 * s * j)) * ∏ t ∈ B, sigma t (6 * s * j) =
      (∏ t ∈ B, w0 A t) * ∏ t ∈ B with t ∣ j, (1 + uw A t) := by
    rw [prod_filter, ← prod_mul_distrib]
    have h1 : ∏ t ∈ A, rho t (6 * s * j) = ∏ t ∈ B, if t ∈ A then rho t (6 * s * j) else 1 := by
      rw [prod_ite_mem, inter_eq_right.2 hAB]
    rw [h1, ← prod_mul_distrib]
    exact prod_congr rfl fun t ht =>
      weight_eq A (by have := (hB t ht).2.1; omega) (coprime_six_mul hs (hB t ht)) j
  unfold pairWeight
  rw [e3, f2, f3, fs]
  calc (2 * ∏ t ∈ A, rho t (6 * s * j)) *
        (2 * (3 / 2) * ((s : ℚ) / ((s : ℚ) - 1)) * ∏ t ∈ B, sigma t (6 * s * j))
      = 6 * (s : ℚ) / ((s : ℚ) - 1) *
          ((∏ t ∈ A, rho t (6 * s * j)) * ∏ t ∈ B, sigma t (6 * s * j)) := by
        field_simp
        ring
    _ = 6 * (s : ℚ) / ((s : ℚ) - 1) * (∏ t ∈ B, w0 A t) * ∏ t ∈ B with t ∣ j, (1 + uw A t) := by
        rw [hprod]
        ring

/-- The subsets of the primes of `B` dividing `j` are the subsets of `B` whose product divides
`j`. -/
theorem powerset_filter_dvd (B : Finset ℕ) (hB : ∀ t ∈ B, t.Prime) (j : ℕ) :
    ({t ∈ B | t ∣ j} : Finset ℕ).powerset = {D ∈ B.powerset | (∏ t ∈ D, t) ∣ j} := by
  ext D
  simp only [mem_powerset, mem_filter]
  constructor
  · intro h
    refine ⟨fun t ht => (mem_filter.1 (h ht)).1, ?_⟩
    exact Finset.prod_primes_dvd j (fun t ht => (hB t (mem_filter.1 (h ht)).1).prime)
      fun t ht => (mem_filter.1 (h ht)).2
  · rintro ⟨hDB, hdvd⟩ t ht
    exact mem_filter.2 ⟨hDB ht, (dvd_prod_of_mem _ ht).trans hdvd⟩

/-- Summing `∏_{t ∣ j} (1 + u_t)` over `j ≤ m`: a sum over the subsets `D` of `B` of
`u(D) ⌊m/d(D)⌋`. -/
theorem sum_Ioc_prod_one_add (B : Finset ℕ) (hB : ∀ t ∈ B, t.Prime) (u : ℕ → ℚ) (m : ℕ) :
    ∑ j ∈ Ioc 0 m, ∏ t ∈ B with t ∣ j, (1 + u t) =
      ∑ D ∈ B.powerset, (∏ t ∈ D, u t) * ((m / ∏ t ∈ D, t : ℕ) : ℚ) := by
  have h1 : ∀ j, ∏ t ∈ B with t ∣ j, (1 + u t) =
      ∑ D ∈ B.powerset, if (∏ t ∈ D, t) ∣ j then ∏ t ∈ D, u t else 0 := fun j => by
    rw [prod_one_add, powerset_filter_dvd B hB j, sum_filter]
  rw [sum_congr rfl fun j _ => h1 j, sum_comm]
  refine sum_congr rfl fun D _ => ?_
  rw [← sum_filter, sum_const, Nat.Ioc_filter_dvd_card_eq_div, nsmul_eq_mul, mul_comm]

/-- `c · ∏ (1 + u_t/t) = 1`, with the product written as the sum over the subsets of `B`. -/
theorem prod_w0_mul_sum (A B : Finset ℕ) (hB : ∀ t ∈ B, 4 ≤ t) :
    (∏ t ∈ B, w0 A t) * ∑ D ∈ B.powerset, ∏ t ∈ D, (uw A t / t) = 1 := by
  rw [← prod_one_add, ← prod_mul_distrib]
  exact prod_eq_one fun t ht => w0_mul A (hB t ht)

/-- **The partial sums of the pair weight**: `∑_{j ≤ m} W(j) = a c ∑_D u(D) ⌊m/d(D)⌋`. -/
theorem sum_Ioc_pairWeight {s : ℕ} (hs : s.Prime) (hs5 : 5 ≤ s) (A B : Finset ℕ) (hAB : A ⊆ B)
    (hB : ∀ t ∈ B, t.Prime ∧ 5 ≤ t ∧ t ≠ s) (m : ℕ) :
    ∑ j ∈ Ioc 0 m, pairWeight s A B j =
      6 * (s : ℚ) / ((s : ℚ) - 1) * (∏ t ∈ B, w0 A t) *
        ∑ D ∈ B.powerset, (∏ t ∈ D, uw A t) * ((m / ∏ t ∈ D, t : ℕ) : ℚ) := by
  rw [sum_congr rfl fun j _ => pairWeight_eq_prod hs hs5 A B hAB hB j, ← mul_sum,
    sum_Ioc_prod_one_add B (fun t ht => (hB t ht).1)]

/-- **The defect of the partial sums**: `a m - ∑_{j ≤ m} W(j) = a c ∑_D u(D) (m/d(D) -
⌊m/d(D)⌋)`. -/
theorem pairWeight_defect {s : ℕ} (hs : s.Prime) (hs5 : 5 ≤ s) (A B : Finset ℕ) (hAB : A ⊆ B)
    (hB : ∀ t ∈ B, t.Prime ∧ 5 ≤ t ∧ t ≠ s) (m : ℕ) :
    6 * (s : ℚ) / ((s : ℚ) - 1) * m - ∑ j ∈ Ioc 0 m, pairWeight s A B j =
      6 * (s : ℚ) / ((s : ℚ) - 1) * (∏ t ∈ B, w0 A t) *
        ∑ D ∈ B.powerset, (∏ t ∈ D, uw A t) *
          ((m : ℚ) / (∏ t ∈ D, (t : ℚ)) - ((m / ∏ t ∈ D, t : ℕ) : ℚ)) := by
  have hc := prod_w0_mul_sum A B fun t ht => by have := (hB t ht).2.1; omega
  have hsplit : ∑ D ∈ B.powerset, (∏ t ∈ D, uw A t) *
        ((m : ℚ) / (∏ t ∈ D, (t : ℚ)) - ((m / ∏ t ∈ D, t : ℕ) : ℚ)) =
      (m : ℚ) * (∑ D ∈ B.powerset, ∏ t ∈ D, (uw A t / t)) -
        ∑ D ∈ B.powerset, (∏ t ∈ D, uw A t) * ((m / ∏ t ∈ D, t : ℕ) : ℚ) := by
    rw [mul_sum, ← sum_sub_distrib]
    refine sum_congr rfl fun D _ => ?_
    rw [prod_div_distrib]
    ring
  rw [sum_Ioc_pairWeight hs hs5 A B hAB hB m, hsplit, mul_sub]
  have e : 6 * (s : ℚ) / ((s : ℚ) - 1) * (∏ t ∈ B, w0 A t) *
      ((m : ℚ) * ∑ D ∈ B.powerset, ∏ t ∈ D, (uw A t / t)) =
      6 * (s : ℚ) / ((s : ℚ) - 1) * m *
        ((∏ t ∈ B, w0 A t) * ∑ D ∈ B.powerset, ∏ t ∈ D, (uw A t / t)) := by ring
  rw [e, hc, mul_one]

/-- **The partial sums never exceed the mean**: `∑_{j ≤ m} W(j) ≤ 6 s/(s - 1) · m` for every
`m`. -/
theorem sum_Ioc_pairWeight_le {s : ℕ} (hs : s.Prime) (hs5 : 5 ≤ s) (A B : Finset ℕ) (hAB : A ⊆ B)
    (hB : ∀ t ∈ B, t.Prime ∧ 5 ≤ t ∧ t ≠ s) (m : ℕ) :
    ∑ j ∈ Ioc 0 m, pairWeight s A B j ≤ 6 * (s : ℚ) / ((s : ℚ) - 1) * m := by
  have hdef := pairWeight_defect hs hs5 A B hAB hB m
  have hs2 : (2 : ℚ) ≤ s := by exact_mod_cast (by omega : 2 ≤ s)
  have ha : 0 ≤ 6 * (s : ℚ) / ((s : ℚ) - 1) := div_nonneg (by linarith) (by linarith)
  have hcn : 0 ≤ ∏ t ∈ B, w0 A t :=
    prod_nonneg fun t ht => w0_nonneg A (by have := (hB t ht).2.1; omega)
  have hsum : 0 ≤ ∑ D ∈ B.powerset, (∏ t ∈ D, uw A t) *
      ((m : ℚ) / (∏ t ∈ D, (t : ℚ)) - ((m / ∏ t ∈ D, t : ℕ) : ℚ)) := by
    refine sum_nonneg fun D hD => mul_nonneg ?_ ?_
    · exact prod_nonneg fun t ht =>
        uw_nonneg A (by have := (hB t (mem_powerset.1 hD ht)).2.1; omega)
    · have h := Nat.cast_div_le (α := ℚ) (m := m) (n := ∏ t ∈ D, t)
      rw [Nat.cast_prod] at h
      linarith
  have hnn := mul_nonneg (mul_nonneg ha hcn) hsum
  linarith

/-- The local identity of a modulus below `s` (item 3b of the research session): with
`u = 2/(t - 3)`, `(1 + u)(1 - 1/t)/(1 + u/t) = (t - 1)/(t - 2)`. -/
theorem local_ratio_below {t : ℚ} (h0 : t ≠ 0) (h1 : t ≠ 1) (h2 : t ≠ 2) (h3 : t ≠ 3) :
    (1 + 2 / (t - 3)) * (1 - 1 / t) / (1 + 2 / (t - 3) / t) = (t - 1) / (t - 2) := by
  have e1 : t - 1 ≠ 0 := sub_ne_zero.2 h1
  have e2 : t - 2 ≠ 0 := sub_ne_zero.2 h2
  have e3 : t - 3 ≠ 0 := sub_ne_zero.2 h3
  have e : 1 + 2 / (t - 3) / t = (t - 1) * (t - 2) / ((t - 3) * t) := by
    field_simp
    ring
  rw [e]
  field_simp
  ring

/-- The local identity of a prime above `s`: with `u = 1/(t - 2)`,
`(1 + u)(1 - 1/t)/(1 + u/t) = 1`. -/
theorem local_ratio_above {t : ℚ} (h0 : t ≠ 0) (h1 : t ≠ 1) (h2 : t ≠ 2) :
    (1 + 1 / (t - 2)) * (1 - 1 / t) / (1 + 1 / (t - 2) / t) = 1 := by
  have e1 : t - 1 ≠ 0 := sub_ne_zero.2 h1
  have e2 : t - 2 ≠ 0 := sub_ne_zero.2 h2
  have e : 1 + 1 / (t - 2) / t = (t - 1) ^ 2 / ((t - 2) * t) := by
    field_simp
    ring
  rw [e]
  field_simp
  ring

end GoldbachGaps.CoverPairs

namespace GoldbachGaps

open Finset Filter

/-- Every partial product of the twin-prime constant is at least `1/2`. -/
theorem one_half_le_twinPartial (w : ℕ) : 1 / 2 ≤ twinPartial w := by
  have h3 : ∀ r ∈ oddPrimesLE w, 3 ≤ r := fun r hr => three_le_of_mem_oddPrimesLE hr
  have hnat := Cap.prod_pred_sq_le (oddPrimesLE w) h3
  have hfac : ∀ r ∈ oddPrimesLE w, 1 - 1 / ((r : ℝ) - 1) ^ 2 =
      ((r * (r - 2) : ℕ) : ℝ) / (((r - 1) ^ 2 : ℕ) : ℝ) := fun r hr => by
    have hr3 := h3 r hr
    have h3r : (3 : ℝ) ≤ r := by exact_mod_cast hr3
    have e1 : (r : ℝ) - 1 ≠ 0 := (by linarith : (0 : ℝ) < (r : ℝ) - 1).ne'
    rw [Nat.cast_mul, Nat.cast_pow, Nat.cast_sub (by omega), Nat.cast_sub (by omega)]
    push_cast
    field_simp
    ring
  have hpos : (0 : ℝ) < ((∏ r ∈ oddPrimesLE w, (r - 1) ^ 2 : ℕ) : ℝ) := by
    have : 0 < ∏ r ∈ oddPrimesLE w, (r - 1) ^ 2 := Finset.prod_pos fun r hr => by
      have := h3 r hr
      exact pow_pos (by omega) 2
    exact_mod_cast this
  unfold twinPartial
  rw [Finset.prod_congr rfl hfac, Finset.prod_div_distrib, ← Nat.cast_prod, ← Nat.cast_prod,
    le_div_iff₀ hpos]
  have hcast : ((∏ r ∈ oddPrimesLE w, (r - 1) ^ 2 : ℕ) : ℝ) ≤
      ((2 * ∏ r ∈ oddPrimesLE w, (r * (r - 2)) : ℕ) : ℝ) := by exact_mod_cast hnat
  push_cast at hcast ⊢
  linarith

/-- **`C₂ ≥ 1/2`.** -/
theorem one_half_le_twinPrimeConstant : 1 / 2 ≤ twinPrimeConstant :=
  le_ciInf one_half_le_twinPartial

theorem twinPrimeConstant_pos : 0 < twinPrimeConstant := by
  have := one_half_le_twinPrimeConstant
  linarith

/-- **`∏_{5 ≤ t ≤ w} (t - 1)²/(t (t - 2)) → 3/(4 C₂)`**, the product over the primes `t`. -/
theorem tendsto_prod_sq_div :
    Tendsto (fun w : ℕ => ∏ t ∈ oddPrimesLE w with 5 ≤ t,
      ((t : ℝ) - 1) ^ 2 / ((t : ℝ) * ((t : ℝ) - 2))) atTop
      (nhds (3 / (4 * twinPrimeConstant))) := by
  have hC := twinPrimeConstant_pos
  have hlim : Tendsto (fun w : ℕ => 3 / (4 * twinPartial w)) atTop
      (nhds (3 / (4 * twinPrimeConstant))) :=
    (tendsto_const_nhds (x := (3 : ℝ))).div (tendsto_twinPartial.const_mul 4) (by positivity)
  refine hlim.congr' ?_
  filter_upwards [eventually_ge_atTop 3] with w hw
  -- split off the factor of `3`
  have hmem : 3 ∈ oddPrimesLE w := mem_oddPrimesLE.2 ⟨hw, Nat.prime_three, by norm_num⟩
  have hset : oddPrimesLE w = insert 3 {t ∈ oddPrimesLE w | 5 ≤ t} := by
    ext t
    simp only [mem_insert, mem_filter]
    constructor
    · intro ht
      have h3 := three_le_of_mem_oddPrimesLE ht
      by_cases h : t = 3
      · exact Or.inl h
      · refine Or.inr ⟨ht, ?_⟩
        have hp := (mem_oddPrimesLE.1 ht).2.1
        by_contra h5
        have h4 : t = 4 := by omega
        rw [h4] at hp
        exact absurd hp (by norm_num)
    · rintro (rfl | ⟨ht, -⟩)
      · exact hmem
      · exact ht
  have hnot : (3 : ℕ) ∉ ({t ∈ oddPrimesLE w | 5 ≤ t} : Finset ℕ) := fun h => by
    have := (mem_filter.1 h).2
    omega
  have hinv : ∀ t ∈ ({t ∈ oddPrimesLE w | 5 ≤ t} : Finset ℕ),
      1 - 1 / ((t : ℝ) - 1) ^ 2 = (((t : ℝ) - 1) ^ 2 / ((t : ℝ) * ((t : ℝ) - 2)))⁻¹ := fun t ht => by
    have h5 : (5 : ℝ) ≤ t := by exact_mod_cast (mem_filter.1 ht).2
    have e0 : (t : ℝ) ≠ 0 := (by linarith : (0 : ℝ) < (t : ℝ)).ne'
    have e1 : (t : ℝ) - 1 ≠ 0 := (by linarith : (0 : ℝ) < (t : ℝ) - 1).ne'
    have e2 : (t : ℝ) - 2 ≠ 0 := (by linarith : (0 : ℝ) < (t : ℝ) - 2).ne'
    field_simp
    ring
  have htw : twinPartial w = 3 / 4 * (∏ t ∈ oddPrimesLE w with 5 ≤ t,
      ((t : ℝ) - 1) ^ 2 / ((t : ℝ) * ((t : ℝ) - 2)))⁻¹ := by
    unfold twinPartial
    rw [hset, Finset.prod_insert hnot, ← hset, Finset.prod_congr rfl hinv, Finset.prod_inv_distrib]
    norm_num
  have hprodpos : 0 < ∏ t ∈ oddPrimesLE w with 5 ≤ t,
      ((t : ℝ) - 1) ^ 2 / ((t : ℝ) * ((t : ℝ) - 2)) := Finset.prod_pos fun t ht => by
    have h5 : (5 : ℝ) ≤ t := by exact_mod_cast (mem_filter.1 ht).2
    have : 0 < (t : ℝ) - 2 := by linarith
    have : 0 < (t : ℝ) - 1 := by linarith
    positivity
  rw [htw]
  field_simp

end GoldbachGaps
