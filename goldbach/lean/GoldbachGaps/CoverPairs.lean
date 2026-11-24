import GoldbachGaps.CoverCount

/-!
# Two rows in one class: the pair weight and its exact mean

The research session's derivation of the law for the number of complete covers
(`goldbach/sublinear/README.md`, branch `ccr-d4a17dd0-7uu03r`, message of 24 November 2026,
18:00 UTC) starts from pairs of rows. Take two odd primes `q`, `q' = q + d` in one class of a
modulus `s`, so `6 s ∣ d`. Each smaller modulus `t` draws its class among the `t - 1` nonzero
ones; the two rows occupy `ν_t(d)` of them (`nuPair`: one if `t ∣ d`, two otherwise).

* `card_free_nonzero_classes`: the classes of `t` that contain neither row number
  `t - 1 - ν_t(d)`. So both rows stay uncovered by `t` with probability `1 - ν_t(d)/(t - 1)`,
  and over a set of moduli the class vectors leaving both rows uncovered number
  `∏ (t - 1 - ν_t(d))` (`card_pair_uncovered`; one row: `∏ (t - 2)`, `card_single_uncovered`).
  Relative to independence the pair carries the weight
  `rho t d = (1 - ν_t(d)/(t - 1)) / (1 - 1/(t - 1))²`, the ratio of these counts (`prod_rho_eq`):
  `(t - 1)/(t - 2)` if `t ∣ d` and `1 - 1/(t - 2)²` if not (`rho_of_dvd`, `rho_of_not_dvd`; at
  `t = 3` these are `2` and `0`, the research session's "zero unless `3 ∣ d`, then `2`").
* `sigma t d = (1 - ν_t(d)/t) / (1 - 1/t)²` is the factor of `t` in the Hardy–Littlewood density
  of the prime pairs `(q, q + d)`: `t/(t - 1)` if `t ∣ d` and `1 - 1/(t - 1)²` if not
  (`sigma_of_dvd`, `sigma_of_not_dvd`).
* `local_cancellation_below`, `local_cancellation_above`: the two rational identities of the
  research session, as it wrote them.
* `sum_rho_mul_sigma`, `sum_sigma`: what they mean. Over one period of `d`, the weight of a prime
  `t` not dividing `6 s` has mean exactly `1`: `rho · sigma` for a modulus below `s`, `sigma`
  alone for a prime above it.
* `sum_range_prod`: the Chinese remainder theorem for sums, `∑_{n < ∏ t} ∏_t f_t(n mod t)
  = ∏_t ∑_{a < t} f_t(a)` for pairwise coprime `t`.
* `sum_pair_weight`: **the mean of the pair weight is exactly `6 s/(s - 1)`.** For a prime
  `s ≥ 5`, any finite set `B` of primes `≥ 5` other than `s` and any subset `A` of it (the moduli
  below `s`; nothing in the proof needs them to be below), the weight
  `rho 3 · ∏_{t ∈ A} rho t · sigma 2 · sigma 3 · sigma s · ∏_{t ∈ B} sigma t` summed over
  `d = 6 s j`, `j < ∏ B`, is `6 s/(s - 1) · ∏ B`. The constant is `2 · 2 · (3/2) · s/(s - 1)`,
  from `rho 3`, `sigma 2`, `sigma 3`, `sigma s`. Every truncation of the two products has this
  mean, so nothing about convergence is needed.

This is the exact step of the derivation: at leading order the rows of a class are spread as
independent rows would be. The departure the research session then uses (the second-order term
of the average of singular series) rests on the Hardy–Littlewood conjecture and is not touched
here.
-/

namespace GoldbachGaps.CoverPairs

open Finset

/-- The number of residue classes modulo `t` that two numbers differing by `d` occupy. -/
def nuPair (t d : ℕ) : ℕ := if t ∣ d then 1 else 2

theorem nuPair_of_dvd {t d : ℕ} (h : t ∣ d) : nuPair t d = 1 := by
  simp [nuPair, h]

theorem nuPair_of_not_dvd {t d : ℕ} (h : ¬ t ∣ d) : nuPair t d = 2 := by
  simp [nuPair, h]

/-- Two rows `q`, `q + d` in nonzero classes modulo `t` occupy `ν_t(d)` of the `t - 1` nonzero
classes; `t - 1 - ν_t(d)` nonzero classes contain neither. -/
theorem card_free_nonzero_classes {t q d : ℕ} (hq : q % t ≠ 0) (hq' : (q + d) % t ≠ 0) :
    #{c ∈ range t | c ≠ 0 ∧ c ≠ q % t ∧ c ≠ (q + d) % t} = t - 1 - nuPair t d := by
  rcases Nat.eq_zero_or_pos t with rfl | ht
  · simp
  have hqt : q % t < t := Nat.mod_lt _ ht
  have hqt' : (q + d) % t < t := Nat.mod_lt _ ht
  have hsame : (q + d) % t = q % t ↔ t ∣ d := by
    have h := Nat.modEq_iff_dvd' (n := t) (Nat.le_add_right q d)
    rw [Nat.add_sub_cancel_left] at h
    exact ⟨fun e => h.1 e.symm, fun e => (h.2 e).symm⟩
  have hset : ({c ∈ range t | c ≠ 0 ∧ c ≠ q % t ∧ c ≠ (q + d) % t} : Finset ℕ) =
      (((range t).erase 0).erase (q % t)).erase ((q + d) % t) := by
    ext c
    simp only [mem_filter, mem_erase, mem_range]
    tauto
  rw [hset]
  have h1 : q % t ∈ (range t).erase 0 := mem_erase.2 ⟨hq, mem_range.2 hqt⟩
  by_cases hd : t ∣ d
  · rw [nuPair_of_dvd hd, hsame.2 hd, erase_idem, card_erase_of_mem h1,
      card_erase_of_mem (mem_range.2 ht), card_range]
  · have hne : (q + d) % t ≠ q % t := fun e => hd (hsame.1 e)
    have h2 : (q + d) % t ∈ ((range t).erase 0).erase (q % t) :=
      mem_erase.2 ⟨hne, mem_erase.2 ⟨hq', mem_range.2 hqt'⟩⟩
    rw [nuPair_of_not_dvd hd, card_erase_of_mem h2, card_erase_of_mem h1,
      card_erase_of_mem (mem_range.2 ht), card_range]
    omega

/-- **The pair weight of a modulus `t`** whose class is drawn among the `t - 1` nonzero ones: the
probability that neither of two rows differing by `d` is covered, divided by the square of that
probability for one row. -/
def rho (t d : ℕ) : ℚ := (1 - (nuPair t d : ℚ) / ((t : ℚ) - 1)) / (1 - 1 / ((t : ℚ) - 1)) ^ 2

/-- **The factor of `t` in the Hardy–Littlewood density of prime pairs `(q, q + d)`**: the share
of residues `q` modulo `t` with `t ∤ q (q + d)`, divided by the square of the share with
`t ∤ q`. -/
def sigma (t d : ℕ) : ℚ := (1 - (nuPair t d : ℚ) / (t : ℚ)) / (1 - 1 / (t : ℚ)) ^ 2

theorem rho_of_dvd {t d : ℕ} (ht : 3 ≤ t) (h : t ∣ d) :
    rho t d = ((t : ℚ) - 1) / ((t : ℚ) - 2) := by
  have h3 : (3 : ℚ) ≤ t := by exact_mod_cast ht
  have h1 : (t : ℚ) - 1 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 1).ne'
  have h2 : (t : ℚ) - 2 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 2).ne'
  rw [rho, nuPair_of_dvd h]
  have e : (1 : ℚ) - 1 / ((t : ℚ) - 1) = ((t : ℚ) - 2) / ((t : ℚ) - 1) := by
    field_simp
    ring
  rw [Nat.cast_one, e]
  field_simp

theorem rho_of_not_dvd {t d : ℕ} (ht : 3 ≤ t) (h : ¬ t ∣ d) :
    rho t d = 1 - 1 / ((t : ℚ) - 2) ^ 2 := by
  have h3 : (3 : ℚ) ≤ t := by exact_mod_cast ht
  have h1 : (t : ℚ) - 1 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 1).ne'
  have h2 : (t : ℚ) - 2 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 2).ne'
  rw [rho, nuPair_of_not_dvd h]
  have e : (1 : ℚ) - 1 / ((t : ℚ) - 1) = ((t : ℚ) - 2) / ((t : ℚ) - 1) := by
    field_simp
    ring
  rw [e]
  push_cast
  field_simp
  ring

theorem sigma_of_dvd {t d : ℕ} (ht : 2 ≤ t) (h : t ∣ d) :
    sigma t d = (t : ℚ) / ((t : ℚ) - 1) := by
  have h2 : (2 : ℚ) ≤ t := by exact_mod_cast ht
  have h0 : (t : ℚ) ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ)).ne'
  have h1 : (t : ℚ) - 1 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 1).ne'
  rw [sigma, nuPair_of_dvd h]
  have e : (1 : ℚ) - 1 / (t : ℚ) = ((t : ℚ) - 1) / (t : ℚ) := by
    field_simp
  rw [Nat.cast_one, e]
  field_simp

theorem sigma_of_not_dvd {t d : ℕ} (ht : 2 ≤ t) (h : ¬ t ∣ d) :
    sigma t d = 1 - 1 / ((t : ℚ) - 1) ^ 2 := by
  have h2 : (2 : ℚ) ≤ t := by exact_mod_cast ht
  have h0 : (t : ℚ) ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ)).ne'
  have h1 : (t : ℚ) - 1 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 1).ne'
  rw [sigma, nuPair_of_not_dvd h]
  have e : (1 : ℚ) - 1 / (t : ℚ) = ((t : ℚ) - 1) / (t : ℚ) := by
    field_simp
  rw [e]
  push_cast
  field_simp
  ring

/-- Counting the classes modulo `t` with a property: over `Fin t` or over `range t`. -/
theorem card_fin_filter (t : ℕ) (p : ℕ → Prop) [DecidablePred p] :
    #{c : Fin t | p c.1} = #{c ∈ range t | p c} := by
  rw [← card_map Fin.valEmbedding]
  congr 1
  ext x
  simp only [mem_map, mem_filter, mem_univ, true_and, Fin.valEmbedding_apply, mem_range]
  constructor
  · rintro ⟨c, hc, rfl⟩
    exact ⟨c.2, hc⟩
  · rintro ⟨hx, h⟩
    exact ⟨⟨x, hx⟩, h, rfl⟩

open CoverCount in
/-- **Both rows stay uncovered: the exact count.** Among the class vectors on `mods` with nonzero
classes, those that cover neither `q` nor `q + d` number `∏ t (t - 1 - ν_t(d))`, when neither row
is divisible by a modulus. Divided by the `∏ (t - 1)` vectors with nonzero classes this is the
research session's `∏ (1 - ν_t/(t - 1))`. -/
theorem card_pair_uncovered (mods : Finset ℕ) {q d : ℕ} (hq : ∀ t ∈ mods, q % t ≠ 0)
    (hq' : ∀ t ∈ mods, (q + d) % t ≠ 0) :
    #{a : ClassVector mods | (∀ t, (a t).1 ≠ 0) ∧ ¬ Covers a q ∧ ¬ Covers a (q + d)} =
      ∏ t ∈ mods, (t - 1 - nuPair t d) := by
  have h : ({a : ClassVector mods | (∀ t, (a t).1 ≠ 0) ∧ ¬ Covers a q ∧ ¬ Covers a (q + d)} :
      Finset (ClassVector mods)) =
      Fintype.piFinset fun t : mods =>
        {c : Fin t.1 | c.1 ≠ 0 ∧ c.1 ≠ q % t.1 ∧ c.1 ≠ (q + d) % t.1} := by
    ext a
    simp only [mem_filter, mem_univ, true_and, Fintype.mem_piFinset, Covers, not_exists]
    constructor
    · rintro ⟨h0, h1, h2⟩ t
      exact ⟨h0 t, fun e => h1 t e.symm, fun e => h2 t e.symm⟩
    · intro h
      exact ⟨fun t => (h t).1, fun t e => (h t).2.1 e.symm, fun t e => (h t).2.2 e.symm⟩
  rw [h, Fintype.card_piFinset]
  have hfac : ∀ t : mods, #{c : Fin t.1 | c.1 ≠ 0 ∧ c.1 ≠ q % t.1 ∧ c.1 ≠ (q + d) % t.1} =
      t.1 - 1 - nuPair t.1 d := fun t => by
    rw [card_fin_filter t.1 fun c => c ≠ 0 ∧ c ≠ q % t.1 ∧ c ≠ (q + d) % t.1]
    exact card_free_nonzero_classes (hq t.1 t.2) (hq' t.1 t.2)
  simp only [hfac]
  exact prod_coe_sort mods fun t => t - 1 - nuPair t d

open CoverCount in
/-- **One row stays uncovered: the exact count**, `∏ t (t - 2)` of the `∏ t (t - 1)` class
vectors with nonzero classes. This is the product `∏ (r - 2)/(r - 1)` of
`GoldbachGaps/CoverBound.lean`. -/
theorem card_single_uncovered (mods : Finset ℕ) {q : ℕ} (hq : ∀ t ∈ mods, q % t ≠ 0) :
    #{a : ClassVector mods | (∀ t, (a t).1 ≠ 0) ∧ ¬ Covers a q} = ∏ t ∈ mods, (t - 2) := by
  have h := card_pair_uncovered mods (q := q) (d := 0) hq hq
  simp only [Nat.add_zero, and_self, nuPair_of_dvd (dvd_zero _)] at h
  rw [h]
  exact prod_congr rfl fun t _ => by omega

/-- **The pair weight as a ratio of exact counts**: (vectors leaving both rows uncovered) times
(all vectors with nonzero classes), over the square of (vectors leaving one row uncovered). -/
theorem prod_rho_eq (mods : Finset ℕ) (h3 : ∀ t ∈ mods, 3 ≤ t) (d : ℕ) :
    ∏ t ∈ mods, rho t d =
      (∏ t ∈ mods, ((t - 1 - nuPair t d : ℕ) : ℚ)) * (∏ t ∈ mods, ((t - 1 : ℕ) : ℚ)) /
        (∏ t ∈ mods, ((t - 2 : ℕ) : ℚ)) ^ 2 := by
  rw [← prod_mul_distrib, ← prod_pow, ← prod_div_distrib]
  refine prod_congr rfl fun t ht => ?_
  have ht3 := h3 t ht
  have h3q : (3 : ℚ) ≤ t := by exact_mod_cast ht3
  have h2 : (t : ℚ) - 2 ≠ 0 := (by linarith : (0 : ℚ) < (t : ℚ) - 2).ne'
  have c1 : ((t - 1 : ℕ) : ℚ) = (t : ℚ) - 1 := by
    rw [Nat.cast_sub (by omega)]
    norm_num
  have c2 : ((t - 2 : ℕ) : ℚ) = (t : ℚ) - 2 := by
    rw [Nat.cast_sub (by omega)]
    norm_num
  by_cases hd : t ∣ d
  · have c3 : ((t - 1 - nuPair t d : ℕ) : ℚ) = (t : ℚ) - 2 := by
      rw [nuPair_of_dvd hd, Nat.sub_sub, Nat.cast_sub (by omega)]
      norm_num
    rw [rho_of_dvd ht3 hd, c1, c2, c3]
    field_simp
  · have c3 : ((t - 1 - nuPair t d : ℕ) : ℚ) = (t : ℚ) - 3 := by
      rw [nuPair_of_not_dvd hd, Nat.sub_sub, Nat.cast_sub (by omega)]
      norm_num
    rw [rho_of_not_dvd ht3 hd, c1, c2, c3]
    field_simp
    ring

/-- **The local cancellation for a modulus below `s`**, as the research session states it: the
pair weight off the multiples of `t`, times the correction for the multiples, times the
Hardy–Littlewood factor, is `1`. -/
theorem local_cancellation_below {t : ℚ} (h0 : t ≠ 0) (h1 : t ≠ 1) (h2 : t ≠ 2) (h3 : t ≠ 3) :
    (1 - 1 / (t - 2) ^ 2) * (1 + 2 / (t * (t - 3))) * (t * (t - 2) / (t - 1) ^ 2) = 1 := by
  have e1 : t - 1 ≠ 0 := sub_ne_zero.2 h1
  have e2 : t - 2 ≠ 0 := sub_ne_zero.2 h2
  have e3 : t - 3 ≠ 0 := sub_ne_zero.2 h3
  field_simp
  ring

/-- **The local cancellation for a prime above `s`**, as the research session states it. -/
theorem local_cancellation_above {t : ℚ} (h0 : t ≠ 0) (h1 : t ≠ 1) (h2 : t ≠ 2) :
    (1 - 1 / (t - 1) ^ 2) * (1 + 1 / (t * (t - 2))) = 1 := by
  have e1 : t - 1 ≠ 0 := sub_ne_zero.2 h1
  have e2 : t - 2 ≠ 0 := sub_ne_zero.2 h2
  field_simp
  ring

/-- Among `c · 0, c · 1, …, c · (t - 1)` only the first is a multiple of `t`, when `c` is prime
to `t`. -/
theorem not_dvd_mul_succ {k c j : ℕ} (hc : Nat.Coprime (k + 1) c) (hj : j < k) :
    ¬ k + 1 ∣ c * (j + 1) := fun hdvd => by
  have h : k + 1 ∣ j + 1 := hc.dvd_of_dvd_mul_left hdvd
  have := Nat.le_of_dvd (by omega) h
  omega

/-- **The Hardy–Littlewood factor has mean `1`** over a period, for a prime (or any `t ≥ 2`)
not dividing the step `c`. -/
theorem sum_sigma {t c : ℕ} (ht : 2 ≤ t) (hc : Nat.Coprime t c) :
    ∑ j ∈ range t, sigma t (c * j) = t := by
  obtain ⟨k, rfl⟩ : ∃ k, t = k + 1 := ⟨t - 1, by omega⟩
  rw [sum_range_succ']
  have h0 : sigma (k + 1) (c * 0) = ((k + 1 : ℕ) : ℚ) / (((k + 1 : ℕ) : ℚ) - 1) :=
    sigma_of_dvd ht (by simp)
  have hj : ∀ j ∈ range k, sigma (k + 1) (c * (j + 1)) = 1 - 1 / (((k + 1 : ℕ) : ℚ) - 1) ^ 2 :=
    fun j hj => sigma_of_not_dvd ht (not_dvd_mul_succ hc (mem_range.1 hj))
  rw [sum_congr rfl hj, h0, sum_const, card_range, nsmul_eq_mul]
  have hk : (k : ℚ) ≠ 0 := by
    have : 1 ≤ k := by omega
    exact_mod_cast (by omega : k ≠ 0)
  have e : ((k + 1 : ℕ) : ℚ) - 1 = k := by
    push_cast
    ring
  rw [e]
  push_cast
  field_simp
  ring

/-- **The pair weight times the Hardy–Littlewood factor has mean `1`** over a period, for a
modulus `t ≥ 3` not dividing the step `c`. -/
theorem sum_rho_mul_sigma {t c : ℕ} (ht : 3 ≤ t) (hc : Nat.Coprime t c) :
    ∑ j ∈ range t, rho t (c * j) * sigma t (c * j) = t := by
  obtain ⟨k, rfl⟩ : ∃ k, t = k + 1 := ⟨t - 1, by omega⟩
  rw [sum_range_succ']
  have h0 : rho (k + 1) (c * 0) * sigma (k + 1) (c * 0) =
      (((k + 1 : ℕ) : ℚ) - 1) / (((k + 1 : ℕ) : ℚ) - 2) *
        (((k + 1 : ℕ) : ℚ) / (((k + 1 : ℕ) : ℚ) - 1)) := by
    rw [rho_of_dvd ht (by simp), sigma_of_dvd (by omega) (by simp)]
  have hj : ∀ j ∈ range k, rho (k + 1) (c * (j + 1)) * sigma (k + 1) (c * (j + 1)) =
      (1 - 1 / (((k + 1 : ℕ) : ℚ) - 2) ^ 2) * (1 - 1 / (((k + 1 : ℕ) : ℚ) - 1) ^ 2) :=
    fun j hj => by
      have hnd := not_dvd_mul_succ hc (mem_range.1 hj)
      rw [rho_of_not_dvd ht hnd, sigma_of_not_dvd (by omega) hnd]
  rw [sum_congr rfl hj, h0, sum_const, card_range, nsmul_eq_mul]
  have hk2 : (2 : ℚ) ≤ k := by
    have : 2 ≤ k := by omega
    exact_mod_cast this
  have hk : (k : ℚ) ≠ 0 := (by linarith : (0 : ℚ) < (k : ℚ)).ne'
  have hk1 : (k : ℚ) - 1 ≠ 0 := (by linarith : (0 : ℚ) < (k : ℚ) - 1).ne'
  have e1 : ((k + 1 : ℕ) : ℚ) - 1 = k := by
    push_cast
    ring
  have e2 : ((k + 1 : ℕ) : ℚ) - 2 = (k : ℚ) - 1 := by
    push_cast
    ring
  rw [e1, e2]
  push_cast
  field_simp
  ring

/-- The Chinese remainder theorem for sums, two moduli. -/
theorem sum_range_mul_of_coprime {m n : ℕ} (h : Nat.Coprime m n) (F G : ℕ → ℚ) :
    ∑ x ∈ range (m * n), F (x % m) * G (x % n) =
      (∑ a ∈ range m, F a) * (∑ b ∈ range n, G b) := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · simp
  rw [sum_mul_sum, ← sum_product']
  refine sum_bij (fun x _ => (x % m, x % n)) (fun x _ => ?_) (fun x hx y hy hxy => ?_)
    (fun p hp => ?_) (fun x _ => rfl)
  · exact mem_product.2 ⟨mem_range.2 (Nat.mod_lt _ hm), mem_range.2 (Nat.mod_lt _ hn)⟩
  · have h1 : x ≡ y [MOD m] := congrArg Prod.fst hxy
    have h2 : x ≡ y [MOD n] := congrArg Prod.snd hxy
    exact ((Nat.modEq_and_modEq_iff_modEq_mul h).1 ⟨h1, h2⟩).eq_of_lt_of_lt (mem_range.1 hx)
      (mem_range.1 hy)
  · obtain ⟨hp1, hp2⟩ := mem_product.1 hp
    have hlt := Nat.chineseRemainder_lt_mul h p.1 p.2 hm.ne' hn.ne'
    obtain ⟨hk1, hk2⟩ := (Nat.chineseRemainder h p.1 p.2).2
    have e1 : (Nat.chineseRemainder h p.1 p.2 : ℕ) % m = p.1 % m := hk1
    have e2 : (Nat.chineseRemainder h p.1 p.2 : ℕ) % n = p.2 % n := hk2
    refine ⟨(Nat.chineseRemainder h p.1 p.2 : ℕ), mem_range.2 hlt, Prod.ext ?_ ?_⟩
    · exact e1.trans (Nat.mod_eq_of_lt (mem_range.1 hp1))
    · exact e2.trans (Nat.mod_eq_of_lt (mem_range.1 hp2))

/-- **The Chinese remainder theorem for sums.** For pairwise coprime moduli and functions `w t`
of period `t`, the sum over one common period of the product is the product of the sums. -/
theorem sum_range_prod (B : Finset ℕ) (hB : ∀ t ∈ B, ∀ u ∈ B, t ≠ u → Nat.Coprime t u)
    (w : ℕ → ℕ → ℚ) (hw : ∀ t ∈ B, ∀ j, w t j = w t (j % t)) :
    ∑ j ∈ range (∏ t ∈ B, t), ∏ t ∈ B, w t j = ∏ t ∈ B, ∑ a ∈ range t, w t a := by
  classical
  induction B using Finset.induction_on with
  | empty => simp
  | insert t B htB ih =>
    have hB' : ∀ u ∈ B, ∀ v ∈ B, u ≠ v → Nat.Coprime u v := fun u hu v hv huv =>
      hB u (mem_insert_of_mem hu) v (mem_insert_of_mem hv) huv
    have hw' : ∀ u ∈ B, ∀ j, w u j = w u (j % u) := fun u hu j => hw u (mem_insert_of_mem hu) j
    have hcop : Nat.Coprime t (∏ u ∈ B, u) :=
      Nat.Coprime.prod_right fun u hu =>
        hB t (mem_insert_self t B) u (mem_insert_of_mem hu) fun e => htB (e ▸ hu)
    rw [prod_insert htB, prod_insert htB, ← ih hB' hw',
      ← sum_range_mul_of_coprime hcop (w t) fun b => ∏ u ∈ B, w u b]
    refine sum_congr rfl fun j _ => ?_
    rw [prod_insert htB, ← hw t (mem_insert_self t B) j]
    congr 1
    refine prod_congr rfl fun u hu => ?_
    rw [hw' u hu j, hw' u hu (j % ∏ v ∈ B, v), Nat.mod_mod_of_dvd _ (dvd_prod_of_mem _ hu)]

/-- **The mean of the pair weight is exactly `6 s/(s - 1)`.** Let `s ≥ 5` be prime, `B` a finite
set of primes `≥ 5` other than `s`, and `A ⊆ B`. The pair weights of the moduli `3` and `A`, times
the Hardy–Littlewood factors of `2`, `3`, `s` and `B`, summed over the differences `d = 6 s j`
with `j` in one period `∏ B`, give `6 s/(s - 1)` per term. -/
theorem sum_pair_weight {s : ℕ} (hs : s.Prime) (hs5 : 5 ≤ s) (A B : Finset ℕ) (hAB : A ⊆ B)
    (hB : ∀ t ∈ B, t.Prime ∧ 5 ≤ t ∧ t ≠ s) :
    ∑ j ∈ range (∏ t ∈ B, t),
        (rho 3 (6 * s * j) * ∏ t ∈ A, rho t (6 * s * j)) *
          (sigma 2 (6 * s * j) * sigma 3 (6 * s * j) * sigma s (6 * s * j) *
            ∏ t ∈ B, sigma t (6 * s * j)) =
      6 * (s : ℚ) / ((s : ℚ) - 1) * ∏ t ∈ B, (t : ℚ) := by
  classical
  -- the weight of a prime of `B`
  set w : ℕ → ℕ → ℚ := fun t j =>
    (if t ∈ A then rho t (6 * s * j) else 1) * sigma t (6 * s * j) with hwdef
  have hcop : ∀ t ∈ B, Nat.Coprime t (6 * s) := fun t ht => by
    obtain ⟨htp, ht5, hts⟩ := hB t ht
    refine Nat.Coprime.mul_right ?_ ((Nat.coprime_primes htp hs).2 hts)
    have h2 : Nat.Coprime t 2 := (Nat.coprime_primes htp Nat.prime_two).2 (by omega)
    have h3 : Nat.Coprime t 3 := (Nat.coprime_primes htp Nat.prime_three).2 (by omega)
    exact Nat.Coprime.mul_right h2 h3
  -- periodicity
  have hdvd : ∀ t j : ℕ, (t ∣ 6 * s * j ↔ t ∣ 6 * s * (j % t)) := fun t j => by
    have h : 6 * s * j ≡ 6 * s * (j % t) [MOD t] := (Nat.mod_modEq j t).symm.mul_left (6 * s)
    exact h.dvd_iff dvd_rfl
  have hnu : ∀ t j : ℕ, nuPair t (6 * s * j) = nuPair t (6 * s * (j % t)) := fun t j => by
    unfold nuPair
    rw [if_congr (hdvd t j) rfl rfl]
  have hw : ∀ t ∈ B, ∀ j, w t j = w t (j % t) := fun t _ j => by
    simp only [hwdef, rho, sigma, hnu t j]
  -- the local sums
  have hlocal : ∀ t ∈ B, ∑ a ∈ range t, w t a = t := fun t ht => by
    obtain ⟨_, ht5, _⟩ := hB t ht
    by_cases hA : t ∈ A
    · simp only [hwdef, hA, ite_true]
      exact sum_rho_mul_sigma (by omega) (hcop t ht)
    · simp only [hwdef, hA, ite_false, one_mul]
      exact sum_sigma (by omega) (hcop t ht)
  -- the four constant factors
  have hs2 : (2 : ℚ) ≤ s := by exact_mod_cast (by omega : 2 ≤ s)
  have hs1 : (s : ℚ) - 1 ≠ 0 := (by linarith : (0 : ℚ) < (s : ℚ) - 1).ne'
  have hterm : ∀ j : ℕ,
      (rho 3 (6 * s * j) * ∏ t ∈ A, rho t (6 * s * j)) *
          (sigma 2 (6 * s * j) * sigma 3 (6 * s * j) * sigma s (6 * s * j) *
            ∏ t ∈ B, sigma t (6 * s * j)) =
        6 * (s : ℚ) / ((s : ℚ) - 1) * ∏ t ∈ B, w t j := fun j => by
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
    have hprod : ∏ t ∈ B, w t j = (∏ t ∈ A, rho t (6 * s * j)) * ∏ t ∈ B, sigma t (6 * s * j) := by
      simp only [hwdef]
      rw [prod_mul_distrib, prod_ite_mem, inter_eq_right.2 hAB]
    rw [e3, f2, f3, fs, hprod]
    field_simp
    ring
  rw [sum_congr rfl fun j _ => hterm j, ← mul_sum,
    sum_range_prod B (fun t ht u hu htu => (Nat.coprime_primes (hB t ht).1 (hB u hu).1).2 htu) w hw,
    prod_congr rfl hlocal]

end GoldbachGaps.CoverPairs
