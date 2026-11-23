import GoldbachGaps.Basic

/-!
# What lattice decoding can and cannot do for the search problem

The search problem: members `N₀ + t M`, `t < K`; `k` rows `N₀ + t M - q`; find the `t` for which
unusually many rows have a prime factor `s ≤ z`. In coding terms `t ↦ (t mod s)_s` is a
Chinese-remainder code and each prime `s` comes with a list of classes that kill a row.
The polynomial-time decoders (Coppersmith, Howgrave-Graham, May; Goldreich–Ron–Sudan, Boneh,
Guruswami–Sahai–Sudan) work up to a Johnson-type radius. This file records, as inequalities,
that inside that radius they can do nothing the covering congruences do not already do.
The conditions under which the decoders work are quoted from the literature (they are the
hypotheses below); the theorems are the arithmetic.

* `lattice_radius`: finding every `t < K` for which `F(t) = ∏ (N₀ + t M - q)` has a divisor
  `≥ P^β` of `P = ∏_{s ≤ z} s` needs `ln K ≤ z β² / k` (`ln P ≈ z`). A typical `t` has
  `β_typ = (k/z)(1 + ln (z/k))`. So the method reaches `β = c β_typ` only if
  `c² ≥ e ln K / 4`, whatever `z` and `k`: `c ≥ 3.88` for `K = 2^32`
  (`lattice_radius_two_pow_32`). The best member among `K` exceeds the typical one by a few
  percent.
* `list_deficit`, `johnson_leaves_the_cover`: the same in list form. With lists of `ℓ_i`
  classes modulo `r_i` and multiplicities chosen optimally, the lattice method finds all
  `t < K` that meet every list when `∑ ln r_i / ℓ_i ≥ ln K`; a solution is expected only when
  `∑ ln (r_i / ℓ_i) ≤ ln K`. A singleton list has `ln r / ℓ = ln (r / ℓ)`: that is the
  Chinese remainder theorem, i.e. the cover. A list with `2 ≤ ℓ ≤ r/2` has
  `ln (r/ℓ) - ln r / ℓ ≥ ln 2 - 2 ln r / r > 0`, and only lists with more than half of the
  classes can make up for it, by at most `2 ln r / r` each. For `r ≥ 443`: at least 23
  such lists for every informative one (`informative_lists_le`).
-/

namespace GoldbachGaps.Cap

open Real

/-- `(1 + ln x)² ≤ (4/e) x` for `x ≥ 1/e`; equality at `x = e`. -/
theorem one_add_log_sq_le {x : ℝ} (hx : exp (-1) ≤ x) : (1 + log x) ^ 2 ≤ 4 / exp 1 * x := by
  have hx0 : 0 < x := lt_of_lt_of_le (exp_pos _) hx
  have hu : -1 ≤ log x := by
    have h := Real.log_le_log (exp_pos _) hx
    rwa [Real.log_exp] at h
  have h1 : 1 + (log x - 1) / 2 ≤ exp ((log x - 1) / 2) := by
    linarith [Real.add_one_le_exp ((log x - 1) / 2)]
  have h0 : 0 ≤ 1 + (log x - 1) / 2 := by linarith
  have h2 : (1 + (log x - 1) / 2) ^ 2 ≤ exp ((log x - 1) / 2) ^ 2 := pow_le_pow_left₀ h0 h1 2
  have h3 : exp ((log x - 1) / 2) ^ 2 = x / exp 1 := by
    rw [sq, ← Real.exp_add]
    have e : (log x - 1) / 2 + (log x - 1) / 2 = log x - 1 := by ring
    rw [e, Real.exp_sub, Real.exp_log hx0]
  have h4 : (1 + log x) ^ 2 = 4 * (1 + (log x - 1) / 2) ^ 2 := by ring
  rw [h4]
  calc 4 * (1 + (log x - 1) / 2) ^ 2 ≤ 4 * exp ((log x - 1) / 2) ^ 2 := by linarith
    _ = 4 / exp 1 * x := by rw [h3]; ring

/-- **The decoding radius of the lattice method.** `k` rows, sieve primes up to `z ≥ k/e`,
typical smooth exponent `β_typ = (k/z)(1 + ln (z/k))`. If the condition `ln K ≤ z β² / k` of
the method holds for `β = c β_typ`, then `c² ≥ e ln K / 4`. -/
theorem lattice_radius {k z c lnK : ℝ} (hk : 0 < k) (hz : k * exp (-1) ≤ z)
    (h : lnK ≤ z * (c * (k / z * (1 + log (z / k)))) ^ 2 / k) :
    exp 1 * lnK / 4 ≤ c ^ 2 := by
  have hz0 : 0 < z := lt_of_lt_of_le (mul_pos hk (exp_pos _)) hz
  have hx : exp (-1) ≤ z / k := by
    rw [le_div_iff₀ hk]
    linarith
  have hx0 : 0 < z / k := div_pos hz0 hk
  have h1 := one_add_log_sq_le hx
  have e : z * (c * (k / z * (1 + log (z / k)))) ^ 2 / k =
      c ^ 2 * ((1 + log (z / k)) ^ 2 / (z / k)) := by
    field_simp
  rw [e] at h
  have h2 : (1 + log (z / k)) ^ 2 / (z / k) ≤ 4 / exp 1 := by
    rw [div_le_iff₀ hx0]
    exact h1
  have h3 : lnK ≤ c ^ 2 * (4 / exp 1) :=
    h.trans (mul_le_mul_of_nonneg_left h2 (sq_nonneg c))
  have he : 0 < exp 1 := exp_pos 1
  have h4 : c ^ 2 * (4 / exp 1) = 4 * c ^ 2 / exp 1 := by ring
  rw [h4, le_div_iff₀ he] at h3
  linarith

/-- For `K = 2^32` members the lattice method needs a smooth part `3.88` times the typical
one. -/
theorem lattice_radius_two_pow_32 {k z c : ℝ} (hk : 0 < k) (hz : k * exp (-1) ≤ z) (hc : 0 ≤ c)
    (h : 32 * log 2 ≤ z * (c * (k / z * (1 + log (z / k)))) ^ 2 / k) :
    3.88 ≤ c := by
  have h1 := lattice_radius hk hz h
  have he : (2.7182818283 : ℝ) < exp 1 := Real.exp_one_gt_d9
  have hl : (0.6931471803 : ℝ) < log 2 := Real.log_two_gt_d9
  by_contra hlt
  have hlt := not_le.mp hlt
  have h2 : c ^ 2 < 3.88 ^ 2 := by nlinarith
  have h3 : (3.88 : ℝ) ^ 2 < exp 1 * (32 * log 2) / 4 := by nlinarith
  linarith

/-- **An informative list is outside the radius.** A list of `ℓ` classes modulo `r` with
`2 ≤ ℓ ≤ r/2` carries `ln (r/ℓ)` nats of information and contributes `ln r / ℓ` to the lattice
condition; the first exceeds the second by at least `ln 2 - 2 ln r / r`. -/
theorem list_deficit {r l : ℝ} (hr : 16 ≤ r) (h2 : 2 ≤ l) (hl : l ≤ r / 2) :
    log r / l + (log 2 - 2 * log r / r) ≤ log (r / l) := by
  have hr0 : 0 < r := by linarith
  have hl0 : 0 < l := by linarith
  have hlogr : 4 * log 2 ≤ log r := by
    have h16 : log 16 = 4 * log 2 := by
      rw [show (16 : ℝ) = 2 ^ (4 : ℕ) by norm_num, Real.log_pow]
      norm_num
    rw [← h16]
    exact Real.log_le_log (by norm_num) hr
  have hlog2 : 0 < log 2 := Real.log_pos (by norm_num)
  -- `u = r / l` lies between `2` and `r / 2`
  set u := r / l with hu
  have hu2 : 2 ≤ u := by
    rw [hu, le_div_iff₀ hl0]
    linarith
  have hur : u ≤ r / 2 := by
    rw [hu, div_le_div_iff₀ hl0 (by norm_num)]
    nlinarith
  have hrl : log r / l = log r / r * u := by
    rw [hu]
    field_simp
  -- concavity of the logarithm on `[2, r/2]`
  have hd : 0 < r / 2 - 2 := by linarith
  set s := (u - 2) / (r / 2 - 2) with hs
  have hs0 : 0 ≤ s := div_nonneg (by linarith) hd.le
  have hs1 : s ≤ 1 := by
    rw [hs, div_le_one hd]
    linarith
  have hconc := (StrictConcaveOn.concaveOn strictConcaveOn_log_Ioi).2
    (show (2 : ℝ) ∈ Set.Ioi 0 by norm_num) (show r / 2 ∈ Set.Ioi 0 by
      simp only [Set.mem_Ioi]; linarith)
    (show 0 ≤ 1 - s by linarith) hs0 (by ring)
  have hsmul : s * (r / 2 - 2) = u - 2 := by rw [hs, div_mul_cancel₀ _ hd.ne']
  have hcomb : (1 - s) • (2 : ℝ) + s • (r / 2) = u := by
    simp only [smul_eq_mul]
    linear_combination hsmul
  rw [hcomb] at hconc
  simp only [smul_eq_mul] at hconc
  have hlogr2 : log (r / 2) = log r - log 2 := Real.log_div hr0.ne' (by norm_num)
  rw [hlogr2] at hconc
  -- the affine part
  have hu' : u = 2 + s * (r / 2 - 2) := by linarith
  have hη : 0 ≤ log r / r := div_nonneg (by linarith) hr0.le
  have hfinal : log r / r * u + (log 2 - 2 * log r / r) ≤
      (1 - s) * log 2 + s * (log r - log 2) := by
    have e1 : log r / r * u + (log 2 - 2 * log r / r) =
        log 2 + s * (log r / r * (r / 2 - 2)) := by
      rw [hu']
      ring
    have e2 : log r / r * (r / 2 - 2) = log r / 2 - 2 * (log r / r) := by
      field_simp
    have e3 : (1 - s) * log 2 + s * (log r - log 2) = log 2 + s * (log r - 2 * log 2) := by ring
    rw [e1, e2, e3]
    have h5 : log r / 2 - 2 * (log r / r) ≤ log r - 2 * log 2 := by linarith
    nlinarith [mul_le_mul_of_nonneg_left h5 hs0]
  rw [hrl]
  exact hfinal.trans hconc

/-- **Inside the Johnson radius only the cover is left.** Lists of `l i` classes modulo `r i`,
`r i ≥ 16`. If the lattice condition `∑ ln r_i / ℓ_i ≥ L` holds and a solution is expected,
`∑ ln (r_i / ℓ_i) ≤ L`, then the deficits of the informative lists (`2 ≤ ℓ ≤ r/2`) are paid by
the lists with more than half of the classes, which give at most `2 ln r / r` each.
Singleton lists (the Chinese remainder theorem) neither pay nor cost. -/
theorem johnson_leaves_the_cover {ι : Type*} (s : Finset ι) (r : ι → ℝ) (l : ι → ℕ) (L : ℝ)
    (hr : ∀ i ∈ s, 16 ≤ r i) (hl1 : ∀ i ∈ s, 1 ≤ l i) (hlr : ∀ i ∈ s, (l i : ℝ) ≤ r i)
    (hD : L ≤ ∑ i ∈ s, log (r i) / l i) (hS : ∑ i ∈ s, log (r i / l i) ≤ L) :
    ∑ i ∈ s.filter (fun i => 2 ≤ l i ∧ (l i : ℝ) ≤ r i / 2), (log 2 - 2 * log (r i) / r i) ≤
      ∑ i ∈ s.filter (fun i => r i / 2 < (l i : ℝ)), 2 * log (r i) / r i := by
  classical
  rw [Finset.sum_filter, Finset.sum_filter, ← sub_nonpos, ← Finset.sum_sub_distrib]
  have hsum : ∑ i ∈ s, (log (r i / l i) - log (r i) / l i) ≤ 0 := by
    rw [Finset.sum_sub_distrib]
    linarith
  refine le_trans (Finset.sum_le_sum fun i hi => ?_) hsum
  have hri := hr i hi
  have hr0 : 0 < r i := by linarith
  have hlogr : 0 ≤ log (r i) := Real.log_nonneg (by linarith)
  have hl0 : (0 : ℝ) < l i := by exact_mod_cast hl1 i hi
  rcases Nat.lt_or_ge (l i) 2 with hlt | hge
  · -- a singleton list
    have h1 : l i = 1 := le_antisymm (by omega) (hl1 i hi)
    have hnot : ¬(2 ≤ l i ∧ (l i : ℝ) ≤ r i / 2) := fun h => by omega
    have hnot' : ¬(r i / 2 < (l i : ℝ)) := by
      rw [h1]
      push_cast
      linarith
    simp only [hnot, hnot', ↓reduceIte]
    rw [h1]
    simp
  · by_cases hhalf : (l i : ℝ) ≤ r i / 2
    · -- an informative list
      have hnot' : ¬(r i / 2 < (l i : ℝ)) := not_lt.mpr hhalf
      have hyes : 2 ≤ l i ∧ (l i : ℝ) ≤ r i / 2 := ⟨hge, hhalf⟩
      simp only [hyes, hnot', and_self, ↓reduceIte]
      have h2 : (2 : ℝ) ≤ l i := by exact_mod_cast hge
      have := list_deficit hri h2 hhalf
      linarith
    · -- more than half of the classes
      have hgt : r i / 2 < (l i : ℝ) := not_le.mp hhalf
      have hnot : ¬(2 ≤ l i ∧ (l i : ℝ) ≤ r i / 2) := fun h => hhalf h.2
      simp only [hnot, hgt, ↓reduceIte]
      have h3 : 0 ≤ log (r i / l i) :=
        Real.log_nonneg (by rw [le_div_iff₀ hl0]; linarith [hlr i hi])
      have h4 : log (r i) / l i ≤ 2 * log (r i) / r i := by
        rw [div_le_div_iff₀ hl0 hr0]
        nlinarith
      linarith

/-- For moduli `r ≥ 443` (the primes above the cover): under the two conditions of
`johnson_leaves_the_cover` there are at least 23 lists with more than half of the classes for
every informative list. -/
theorem informative_lists_le {ι : Type*} (s : Finset ι) (r : ι → ℝ) (l : ι → ℕ) (L : ℝ)
    (hr : ∀ i ∈ s, 443 ≤ r i) (hl1 : ∀ i ∈ s, 1 ≤ l i) (hlr : ∀ i ∈ s, (l i : ℝ) ≤ r i)
    (hD : L ≤ ∑ i ∈ s, log (r i) / l i) (hS : ∑ i ∈ s, log (r i / l i) ≤ L) :
    23 * (s.filter (fun i => 2 ≤ l i ∧ (l i : ℝ) ≤ r i / 2)).card ≤
      (s.filter (fun i => r i / 2 < (l i : ℝ))).card := by
  have hmain := johnson_leaves_the_cover s r l L (fun i hi => by linarith [hr i hi]) hl1 hlr hD hS
  have hl2 : (0.6931471803 : ℝ) < log 2 := Real.log_two_gt_d9
  have hl2' : log 2 < (0.6931471808 : ℝ) := Real.log_two_lt_d9
  -- `2 ln r / r ≤ 0.0282` for `r ≥ 443`
  have hη : ∀ i ∈ s, 2 * log (r i) / r i ≤ 0.0282 := by
    intro i hi
    have hri := hr i hi
    have hanti := Real.log_div_self_antitoneOn
      (show exp 1 ≤ (443 : ℝ) by linarith [Real.exp_one_lt_d9])
      (show exp 1 ≤ r i by linarith [Real.exp_one_lt_d9]) hri
    have h443 : log 443 ≤ 9 * log 2 := by
      have h : log 443 ≤ log (2 ^ (9 : ℕ)) := Real.log_le_log (by norm_num) (by norm_num)
      rwa [Real.log_pow] at h
    have h5 : log (r i) / r i ≤ log 443 / 443 := hanti
    have h6 : log 443 / 443 ≤ 0.0141 := by
      rw [div_le_iff₀ (by norm_num)]
      linarith
    have h7 : 2 * log (r i) / r i = 2 * (log (r i) / r i) := by ring
    rw [h7]
    linarith
  have hB : (0.664 : ℝ) * (s.filter (fun i => 2 ≤ l i ∧ (l i : ℝ) ≤ r i / 2)).card ≤
      ∑ i ∈ s.filter (fun i => 2 ≤ l i ∧ (l i : ℝ) ≤ r i / 2),
        (log 2 - 2 * log (r i) / r i) := by
    rw [mul_comm, ← nsmul_eq_mul, ← Finset.sum_const]
    refine Finset.sum_le_sum fun i hi => ?_
    have := hη i (Finset.mem_filter.mp hi).1
    linarith
  have hC : ∑ i ∈ s.filter (fun i => r i / 2 < (l i : ℝ)), 2 * log (r i) / r i ≤
      (0.0282 : ℝ) * (s.filter (fun i => r i / 2 < (l i : ℝ))).card := by
    rw [mul_comm, ← nsmul_eq_mul, ← Finset.sum_const]
    exact Finset.sum_le_sum fun i hi => hη i (Finset.mem_filter.mp hi).1
  have hfin : (23 : ℝ) * (s.filter (fun i => 2 ≤ l i ∧ (l i : ℝ) ≤ r i / 2)).card ≤
      (s.filter (fun i => r i / 2 < (l i : ℝ))).card := by
    have hc0 : (0 : ℝ) ≤ (s.filter (fun i => 2 ≤ l i ∧ (l i : ℝ) ≤ r i / 2)).card :=
      Nat.cast_nonneg _
    nlinarith
  exact_mod_cast hfin

end GoldbachGaps.Cap
