import GoldbachGaps.Basic

/-!
# Thinning by moduli that separate the rows

Let `S` be the rows that an `N` still has after the primes up to `z` (`|S| = k`), and let
further moduli `m₁, …, m_r` act on them: `N` in the class `a` modulo `m` kills the rows
`q ≡ a (mod m)`. If every row were killed by `m` with probability `1/m` independently of the
others ("independent thinning"), the number of rows left would be binomial and

  `E y^(rows left) = (1 - (1 - y) θ)^k`,   `θ = ∏ (1 - 1/mᵢ)`.

This file proves that this is an **upper bound**, for every `0 ≤ y ≤ 1`, whenever the rows are
pairwise incongruent modulo each `mᵢ`; in particular for all moduli `≥ Q` when the rows are
below `Q`. The reason is one line: a modulus that separates the rows kills at most one of
them, so the exact generating function for one modulus is `y^k (1 + k u)` with
`u = (1 - y)/(m y)`, against `y^k (1 + u)^k` for independent thinning (Bernoulli's inequality).

* `sum_pow_card_thinned`: the exact one-modulus transfer,
  `∑_{a < m} y^(rows left) = k y^(k-1) + (m - k) y^k`.
* `sum_pow_card_thinned_le`: `… ≤ m (1 - (1 - y)(1 - 1/m))^k`.
* `thinSum_le`: the same for a list of moduli, by composition:
  `∑ over class vectors of y^(rows left) ≤ ∏ mᵢ · (1 - (1 - y) θ)^k`.
* `thinCount_le`: so the number of class vectors that leave at most `K` rows is at most
  `∏ mᵢ · (1 - (1 - y) θ)^k / y^K` for every `0 < y ≤ 1` (Markov), and
  `thinCount_le_chernoff` is the best `y`: the binomial Chernoff bound
  `(θ (k - K) / (K (1 - θ)))^K · ((1 - θ) k / (k - K))^k`, valid for `0 < K ≤ θ k`.
* `thinCount_le_of_lt`, `thinSum_le_of_lt`: the case of rows below `Q` and moduli `≥ Q`.

Use. The research session's table "what a perfect search would be worth"
(`goldbach/sublinear/README.md`, Result 3, branch `ccr-d4a17dd0-7uu03r`) continues each depth
`z` to `B = 10^8` by treating the rows beyond `z` as independent. For the primes above `Q` that
step is now a bound in a known direction: independent thinning can only overstate the number of
`N` with few rows left, so it can only understate the cost of the ideal search. Below `Q` two
rows can share a class and the inequality is not a theorem; the tables themselves show the same
direction there (`scripts/thinning_check/`).
-/

namespace GoldbachGaps.Cap

open Finset

/-- The rows of `S` left when `N` is in the class `a` modulo `m`: the `q` with `q % m ≠ a`
(for `q ≤ N`, `m ∣ N - q` exactly when `q % m = N % m`). -/
def thinned (S : Finset ℕ) (m a : ℕ) : Finset ℕ := S.filter fun q => q % m ≠ a

theorem thinned_subset (S : Finset ℕ) (m a : ℕ) : thinned S m a ⊆ S := filter_subset _ _

/-- A modulus that separates the rows kills exactly one row when `N` is in the class of a
row … -/
theorem card_thinned_of_mem {S : Finset ℕ} {m : ℕ} (hinj : Set.InjOn (fun q => q % m) S)
    {q : ℕ} (hq : q ∈ S) : #(thinned S m (q % m)) = #S - 1 := by
  have h : thinned S m (q % m) = S.erase q := by
    ext x
    simp only [thinned, mem_filter, mem_erase]
    constructor
    · rintro ⟨hx, hne⟩
      exact ⟨fun h => hne (by rw [h]), hx⟩
    · rintro ⟨hne, hx⟩
      exact ⟨hx, fun h => hne (hinj hx hq h)⟩
  rw [h, card_erase_of_mem hq]

/-- … and none when it is in another class. -/
theorem thinned_of_not_mem {S : Finset ℕ} {m a : ℕ} (ha : a ∉ S.image fun q => q % m) :
    thinned S m a = S := by
  apply filter_true_of_mem
  intro q hq h
  exact ha (mem_image.mpr ⟨q, hq, h⟩)

/-- **The exact one-modulus transfer.** If the `k` rows of `S` are pairwise incongruent
modulo `m`, then over the `m` classes of `N` the generating function of the number of rows
left is `k y^(k-1) + (m - k) y^k`. -/
theorem sum_pow_card_thinned {S : Finset ℕ} {m : ℕ} (hm : 0 < m)
    (hinj : Set.InjOn (fun q => q % m) S) (y : ℝ) :
    ∑ a ∈ range m, y ^ #(thinned S m a) = #S * y ^ (#S - 1) + ((m : ℝ) - #S) * y ^ #S := by
  classical
  have hTsub : (S.image fun q => q % m) ⊆ range m := by
    intro a ha
    obtain ⟨q, _, rfl⟩ := mem_image.mp ha
    exact mem_range.mpr (Nat.mod_lt _ hm)
  have hTcard : #(S.image fun q => q % m) = #S := card_image_of_injOn hinj
  have hle : #S ≤ m := by
    have := card_le_card hTsub
    rwa [hTcard, card_range] at this
  have h1 : ∑ a ∈ S.image (fun q => q % m), y ^ #(thinned S m a) = #S * y ^ (#S - 1) := by
    have : ∑ a ∈ S.image (fun q => q % m), y ^ #(thinned S m a) =
        ∑ _a ∈ S.image (fun q => q % m), y ^ (#S - 1) := by
      refine sum_congr rfl fun a ha => ?_
      obtain ⟨q, hq, rfl⟩ := mem_image.mp ha
      rw [card_thinned_of_mem hinj hq]
    rw [this, sum_const, nsmul_eq_mul, hTcard]
  have h2 : ∑ a ∈ range m \ S.image (fun q => q % m), y ^ #(thinned S m a) =
      ((m : ℝ) - #S) * y ^ #S := by
    have : ∑ a ∈ range m \ S.image (fun q => q % m), y ^ #(thinned S m a) =
        ∑ _a ∈ range m \ S.image (fun q => q % m), y ^ #S := by
      refine sum_congr rfl fun a ha => ?_
      rw [thinned_of_not_mem (mem_sdiff.mp ha).2]
    rw [this, sum_const, nsmul_eq_mul, card_sdiff_of_subset hTsub, hTcard, card_range,
      Nat.cast_sub hle]
  rw [← sum_sdiff hTsub, h1, h2]
  ring

/-- The first two terms of the binomial theorem are a lower bound, for nonnegative reals. -/
theorem pow_add_le_add_pow {y c : ℝ} (hy : 0 ≤ y) (hc : 0 ≤ c) (k : ℕ) :
    y ^ (k + 1) + (k + 1) * y ^ k * c ≤ (y + c) ^ (k + 1) := by
  induction k with
  | zero => simp
  | succ k ih =>
    have h2 : 0 ≤ y + c := add_nonneg hy hc
    have key : (y + c) * (y ^ (k + 1) + (k + 1) * y ^ k * c) =
        y ^ (k + 1 + 1) + ((k + 1 : ℕ) + 1) * y ^ (k + 1) * c + (k + 1) * y ^ k * c ^ 2 := by
      push_cast
      ring
    have hpos : 0 ≤ ((k : ℝ) + 1) * y ^ k * c ^ 2 := by positivity
    calc y ^ (k + 1 + 1) + ((k + 1 : ℕ) + 1) * y ^ (k + 1) * c
        ≤ (y + c) * (y ^ (k + 1) + (k + 1) * y ^ k * c) := by rw [key]; linarith
      _ ≤ (y + c) * (y + c) ^ (k + 1) := mul_le_mul_of_nonneg_left ih h2
      _ = (y + c) ^ (k + 1 + 1) := by ring

/-- **One modulus: independent thinning is an upper bound.** If the rows of `S` are pairwise
incongruent modulo `m`, then for `0 ≤ y ≤ 1` the generating function of the number of rows
left, over the `m` classes of `N`, is at most the one of independent thinning with survival
probability `1 - 1/m`. -/
theorem sum_pow_card_thinned_le {S : Finset ℕ} {m : ℕ} (hm : 0 < m)
    (hinj : Set.InjOn (fun q => q % m) S) {y : ℝ} (hy0 : 0 ≤ y) (hy1 : y ≤ 1) :
    ∑ a ∈ range m, y ^ #(thinned S m a) ≤ m * (1 - (1 - y) * (1 - 1 / (m : ℝ))) ^ #S := by
  rw [sum_pow_card_thinned hm hinj]
  have hm' : (0 : ℝ) < m := by exact_mod_cast hm
  have hbase : 1 - (1 - y) * (1 - 1 / (m : ℝ)) = y + (1 - y) / m := by
    field_simp
    ring
  rw [hbase]
  rcases Nat.eq_zero_or_pos #S with h0 | hpos
  · simp [h0]
  · obtain ⟨k, hk⟩ : ∃ k, #S = k + 1 := ⟨#S - 1, by omega⟩
    rw [hk]
    have hc : 0 ≤ (1 - y) / m := div_nonneg (by linarith) hm'.le
    have h := pow_add_le_add_pow hy0 hc k
    have heq : ((k + 1 : ℕ) : ℝ) * y ^ (k + 1 - 1) + ((m : ℝ) - (k + 1 : ℕ)) * y ^ (k + 1) =
        m * (y ^ (k + 1) + (k + 1) * y ^ k * ((1 - y) / m)) := by
      rw [Nat.add_sub_cancel]
      push_cast
      field_simp
      ring
    rw [heq]
    exact mul_le_mul_of_nonneg_left h hm'.le

/-- The sum, over all class vectors (one class for each modulus of the list), of
`y ^ (number of rows left)`. -/
def thinSum (y : ℝ) : List ℕ → Finset ℕ → ℝ
  | [], S => y ^ #S
  | m :: ms, S => ∑ a ∈ range m, thinSum y ms (thinned S m a)

/-- The chance that one row survives all the moduli of the list: `∏ (1 - 1/m)`. -/
noncomputable def survival (ms : List ℕ) : ℝ := (ms.map fun m : ℕ => 1 - 1 / (m : ℝ)).prod

theorem survival_nil : survival [] = 1 := by simp [survival]

theorem survival_cons (m : ℕ) (ms : List ℕ) :
    survival (m :: ms) = (1 - 1 / (m : ℝ)) * survival ms := by simp [survival]

theorem survival_mem_Icc : ∀ ms : List ℕ, (∀ m ∈ ms, 0 < m) → 0 ≤ survival ms ∧ survival ms ≤ 1
  | [], _ => by simp [survival_nil]
  | m :: ms, hpos => by
    have hm : (1 : ℝ) ≤ m := by exact_mod_cast hpos m List.mem_cons_self
    have ih := survival_mem_Icc ms fun m' h => hpos m' (List.mem_cons_of_mem _ h)
    have h0 : 0 ≤ 1 - 1 / (m : ℝ) := by
      rw [sub_nonneg, div_le_one (by linarith)]
      exact hm
    have h1 : 1 - 1 / (m : ℝ) ≤ 1 := by
      have : 0 ≤ 1 / (m : ℝ) := by positivity
      linarith
    rw [survival_cons]
    exact ⟨mul_nonneg h0 ih.1, by nlinarith [mul_nonneg (sub_nonneg.mpr h1) ih.1]⟩

/-- **Independent thinning is an upper bound.** If the rows of `S` are pairwise incongruent
modulo every modulus of the list, then for `0 ≤ y ≤ 1` the sum over all class vectors of
`y ^ (rows left)` is at most `∏ m · (1 - (1 - y) θ)^|S|`, `θ = ∏ (1 - 1/m)`: the value it
would have if every row were killed by every modulus independently. -/
theorem thinSum_le {y : ℝ} (hy0 : 0 ≤ y) (hy1 : y ≤ 1) :
    ∀ (ms : List ℕ) (S : Finset ℕ), (∀ m ∈ ms, 0 < m) →
      (∀ m ∈ ms, Set.InjOn (fun q => q % m) S) →
      thinSum y ms S ≤ (ms.prod : ℕ) * (1 - (1 - y) * survival ms) ^ #S
  | [], S, _, _ => by simp [thinSum, survival_nil]
  | m :: ms, S, hpos, hinj => by
    have hm : 0 < m := hpos m List.mem_cons_self
    have hpos' : ∀ m' ∈ ms, 0 < m' := fun m' h => hpos m' (List.mem_cons_of_mem _ h)
    obtain ⟨hθ0, hθ1⟩ := survival_mem_Icc ms hpos'
    have hg0 : 0 ≤ 1 - (1 - y) * survival ms := by nlinarith
    have hg1 : 1 - (1 - y) * survival ms ≤ 1 := by nlinarith
    have step : ∀ a ∈ range m, thinSum y ms (thinned S m a) ≤
        (ms.prod : ℕ) * (1 - (1 - y) * survival ms) ^ #(thinned S m a) := fun a _ =>
      thinSum_le hy0 hy1 ms (thinned S m a) hpos' fun m' h =>
        (hinj m' (List.mem_cons_of_mem _ h)).mono (by exact_mod_cast thinned_subset S m a)
    calc thinSum y (m :: ms) S = ∑ a ∈ range m, thinSum y ms (thinned S m a) := rfl
      _ ≤ ∑ a ∈ range m, (ms.prod : ℕ) * (1 - (1 - y) * survival ms) ^ #(thinned S m a) :=
          sum_le_sum step
      _ = (ms.prod : ℕ) * ∑ a ∈ range m, (1 - (1 - y) * survival ms) ^ #(thinned S m a) := by
          rw [mul_sum]
      _ ≤ (ms.prod : ℕ) *
            (m * (1 - (1 - (1 - (1 - y) * survival ms)) * (1 - 1 / (m : ℝ))) ^ #S) :=
          mul_le_mul_of_nonneg_left
            (sum_pow_card_thinned_le hm (hinj m List.mem_cons_self) hg0 hg1) (by positivity)
      _ = ((m :: ms).prod : ℕ) * (1 - (1 - y) * survival (m :: ms)) ^ #S := by
          rw [List.prod_cons, survival_cons, Nat.cast_mul]
          ring

/-- The number of class vectors (one class for each modulus of the list) that leave at most
`K` rows of `S`. -/
def thinCount (K : ℕ) : List ℕ → Finset ℕ → ℕ
  | [], S => if #S ≤ K then 1 else 0
  | m :: ms, S => ∑ a ∈ range m, thinCount K ms (thinned S m a)

/-- Markov's inequality for the count of class vectors leaving at most `K` rows. -/
theorem thinCount_mul_pow_le {y : ℝ} (hy0 : 0 ≤ y) (hy1 : y ≤ 1) (K : ℕ) :
    ∀ (ms : List ℕ) (S : Finset ℕ), (thinCount K ms S : ℝ) * y ^ K ≤ thinSum y ms S
  | [], S => by
    simp only [thinCount, thinSum]
    split_ifs with h
    · simpa using pow_le_pow_of_le_one hy0 hy1 h
    · simpa using pow_nonneg hy0 _
  | m :: ms, S => by
    simp only [thinCount, thinSum, Nat.cast_sum, sum_mul]
    exact sum_le_sum fun a _ => thinCount_mul_pow_le hy0 hy1 K ms _

/-- **The count of good class vectors is at most what independent thinning allows.** If the
rows of `S` are pairwise incongruent modulo every modulus of the list, the number of class
vectors that leave at most `K` rows is at most `∏ m · (1 - (1 - y) θ)^|S| / y^K`, for every
`0 < y ≤ 1`. -/
theorem thinCount_le {y : ℝ} (hy0 : 0 < y) (hy1 : y ≤ 1) (K : ℕ) (ms : List ℕ)
    (S : Finset ℕ) (hpos : ∀ m ∈ ms, 0 < m) (hinj : ∀ m ∈ ms, Set.InjOn (fun q => q % m) S) :
    (thinCount K ms S : ℝ) ≤ (ms.prod : ℕ) * ((1 - (1 - y) * survival ms) ^ #S / y ^ K) := by
  rw [← mul_div_assoc, le_div_iff₀ (pow_pos hy0 K)]
  exact (thinCount_mul_pow_le hy0.le hy1 K ms S).trans (thinSum_le hy0.le hy1 ms S hpos hinj)

/-- **The binomial Chernoff bound, exactly.** With `k = |S|` rows, survival chance
`θ = ∏ (1 - 1/m)` and `0 < K ≤ θ k`, the fraction of class vectors that leave at most `K` rows
is at most `(θ (k - K) / (K (1 - θ)))^K · ((1 - θ) k / (k - K))^k`, which is
`exp (-k · D(K/k ‖ θ))`. -/
theorem thinCount_le_chernoff (K : ℕ) (ms : List ℕ) (S : Finset ℕ) (hpos : ∀ m ∈ ms, 0 < m)
    (hinj : ∀ m ∈ ms, Set.InjOn (fun q => q % m) S) (hθ0 : 0 < survival ms)
    (hθ1 : survival ms < 1) (hK0 : 0 < K) (hK : (K : ℝ) ≤ survival ms * #S) :
    (thinCount K ms S : ℝ) ≤ (ms.prod : ℕ) *
      (((1 - survival ms) * #S / (#S - K)) ^ #S *
        (survival ms * (#S - K) / (K * (1 - survival ms))) ^ K) := by
  set θ := survival ms with hθ
  have hK' : (0 : ℝ) < K := by exact_mod_cast hK0
  have hk : (0 : ℝ) < #S := by
    by_contra h
    have : (#S : ℝ) = 0 := le_antisymm (not_lt.mp h) (Nat.cast_nonneg _)
    rw [this, mul_zero] at hK
    linarith
  have hkK : (0 : ℝ) < #S - K := by nlinarith
  have h1θ : 0 < 1 - θ := by linarith
  have hy0 : 0 < K * (1 - θ) / (θ * (#S - K)) := by positivity
  have hy1 : K * (1 - θ) / (θ * (#S - K)) ≤ 1 := by
    rw [div_le_one (by positivity)]
    nlinarith
  have h := thinCount_le hy0 hy1 K ms S hpos hinj
  have e1 : 1 - (1 - K * (1 - θ) / (θ * (#S - K))) * θ = (1 - θ) * #S / (#S - K) := by
    field_simp
    ring
  have e2 : (K * (1 - θ) / (θ * (#S - K))) ^ K = ((θ * (#S - K) / (K * (1 - θ))) ^ K)⁻¹ := by
    rw [← inv_pow, inv_div]
  rw [← hθ, e1, e2, div_inv_eq_mul] at h
  exact h

/-- Rows below `Q` are pairwise incongruent modulo any `m ≥ Q`. -/
theorem injOn_mod_of_lt {S : Finset ℕ} {Q m : ℕ} (hS : ∀ q ∈ S, q < Q) (hm : Q ≤ m) :
    Set.InjOn (fun q => q % m) S := by
  intro q hq q' hq' h
  have h1 : q % m = q := Nat.mod_eq_of_lt (lt_of_lt_of_le (hS q hq) hm)
  have h2 : q' % m = q' := Nat.mod_eq_of_lt (lt_of_lt_of_le (hS q' hq') hm)
  simp only at h
  rwa [h1, h2] at h

/-- **Above `Q` independent thinning is an upper bound.** For rows below `Q` and moduli
`≥ Q ≥ 1`: the sum over class vectors of `y ^ (rows left)` is at most
`∏ m · (1 - (1 - y) θ)^|S|` for `0 ≤ y ≤ 1`. -/
theorem thinSum_le_of_lt {y : ℝ} (hy0 : 0 ≤ y) (hy1 : y ≤ 1) {Q : ℕ} (hQ : 0 < Q)
    (ms : List ℕ) (S : Finset ℕ) (hms : ∀ m ∈ ms, Q ≤ m) (hS : ∀ q ∈ S, q < Q) :
    thinSum y ms S ≤ (ms.prod : ℕ) * (1 - (1 - y) * survival ms) ^ #S :=
  thinSum_le hy0 hy1 ms S (fun m h => lt_of_lt_of_le hQ (hms m h))
    fun m h => injOn_mod_of_lt hS (hms m h)

/-- **Above `Q` the count of good class vectors obeys the binomial bound.** For rows below
`Q` and moduli `≥ Q ≥ 1`, the number of class vectors leaving at most `K` rows is at most
`∏ m · (1 - (1 - y) θ)^|S| / y^K`, for every `0 < y ≤ 1`. -/
theorem thinCount_le_of_lt {y : ℝ} (hy0 : 0 < y) (hy1 : y ≤ 1) (K : ℕ) {Q : ℕ} (hQ : 0 < Q)
    (ms : List ℕ) (S : Finset ℕ) (hms : ∀ m ∈ ms, Q ≤ m) (hS : ∀ q ∈ S, q < Q) :
    (thinCount K ms S : ℝ) ≤ (ms.prod : ℕ) * ((1 - (1 - y) * survival ms) ^ #S / y ^ K) :=
  thinCount_le hy0 hy1 K ms S (fun m h => lt_of_lt_of_le hQ (hms m h))
    fun m h => injOn_mod_of_lt hS (hms m h)

end GoldbachGaps.Cap
