import Mathlib

/-!
# Column sums of a product of two limb arrays

Pure algebra used by the proof of the `fermat28` step (`Gpu28.Step`): the value `V Bs L f`
of `L` limbs in base `Bs`, the `k`-th column `conv a b L k = Σ_{i + j = k} a_i b_j` of the
product of two `L`-limb numbers, the identity `Σ_k conv a b L k · Bs^k = V a · V b`, and the
way a squaring collects its column (`conv_self`: twice the products with `i < k - i`, plus
the diagonal term when `k` is even).
-/

namespace Gpu28

open Finset

/-- The value of the first `L` limbs of `f` in base `Bs`. -/
def V (Bs L : ℕ) (f : ℕ → ℕ) : ℕ := ∑ i ∈ range L, f i * Bs ^ i

theorem V_succ (Bs L : ℕ) (f : ℕ → ℕ) : V Bs (L + 1) f = V Bs L f + f L * Bs ^ L := by
  unfold V
  rw [Finset.sum_range_succ]

theorem V_congr {Bs L : ℕ} {f g : ℕ → ℕ} (h : ∀ i < L, f i = g i) : V Bs L f = V Bs L g := by
  unfold V
  exact Finset.sum_congr rfl fun i hi => by rw [h i (Finset.mem_range.mp hi)]

theorem V_lt {Bs : ℕ} {f : ℕ → ℕ} : ∀ (L : ℕ), (∀ i < L, f i < Bs) → V Bs L f < Bs ^ L
  | 0, _ => by simp [V]
  | L + 1, h => by
    have ih := V_lt L fun i hi => h i (by omega)
    have hL := h L (by omega)
    rw [V_succ, pow_succ]
    have h1 : f L * Bs ^ L + Bs ^ L ≤ Bs ^ L * Bs := by
      have := Nat.mul_le_mul_right (Bs ^ L) (show f L + 1 ≤ Bs by omega)
      have e : (f L + 1) * Bs ^ L = f L * Bs ^ L + Bs ^ L := by ring
      rw [e] at this
      rw [mul_comm (Bs ^ L) Bs]
      exact this
    omega

/-- Column `k` of the product of the `L`-limb arrays `a` and `b`. -/
def conv (a b : ℕ → ℕ) (L k : ℕ) : ℕ :=
  ∑ i ∈ range (k + 1), if i < L ∧ k - i < L then a i * b (k - i) else 0

/-- **The columns add up to the product.** -/
theorem sum_conv (Bs : ℕ) (a b : ℕ → ℕ) (L : ℕ) :
    ∑ k ∈ range (2 * L - 1), conv a b L k * Bs ^ k = V Bs L a * V Bs L b := by
  classical
  rcases Nat.eq_zero_or_pos L with rfl | hL
  · simp [V]
  set P : Polynomial ℕ := ∑ i ∈ range L, Polynomial.C (a i) * Polynomial.X ^ i with hP
  set Q : Polynomial ℕ := ∑ i ∈ range L, Polynomial.C (b i) * Polynomial.X ^ i with hQ
  have hPe : P.eval Bs = V Bs L a := by
    simp [hP, V, Polynomial.eval_finsetSum]
  have hQe : Q.eval Bs = V Bs L b := by
    simp [hQ, V, Polynomial.eval_finsetSum]
  have hcoef : ∀ (c : ℕ → ℕ) (i : ℕ),
      (∑ j ∈ range L, Polynomial.C (c j) * Polynomial.X ^ j : Polynomial ℕ).coeff i =
        if i < L then c i else 0 := by
    intro c i
    rw [Polynomial.finsetSum_coeff]
    simp only [Polynomial.coeff_C_mul_X_pow]
    rw [Finset.sum_ite_eq (range L) i c]
    simp [Finset.mem_range]
  have hdegP : ∀ (c : ℕ → ℕ),
      (∑ j ∈ range L, Polynomial.C (c j) * Polynomial.X ^ j : Polynomial ℕ).natDegree ≤ L - 1 := by
    intro c
    refine Polynomial.natDegree_sum_le_of_forall_le _ _ fun j hj => ?_
    exact (Polynomial.natDegree_C_mul_X_pow_le _ _).trans (by
      have := Finset.mem_range.mp hj
      omega)
  have hdeg : (P * Q).natDegree < 2 * L - 1 := by
    have := Polynomial.natDegree_mul_le (p := P) (q := Q)
    have h1 := hdegP a
    have h2 := hdegP b
    rw [← hP] at h1
    rw [← hQ] at h2
    omega
  rw [← hPe, ← hQe, ← Polynomial.eval_mul, Polynomial.eval_eq_sum_range' hdeg]
  refine Finset.sum_congr rfl fun k _ => ?_
  congr 1
  rw [Polynomial.coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ
    (fun i j => P.coeff i * Q.coeff j) k]
  unfold conv
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [hP, hQ, hcoef a i, hcoef b (k - i)]
  by_cases h1 : i < L <;> by_cases h2 : k - i < L <;> simp [h1, h2]

/-- **A squaring collects its column**: twice the products with `i < k - i`, plus the square
of the middle limb when `k` is even. -/
theorem conv_self (x : ℕ → ℕ) (L k : ℕ) :
    conv x x L k =
      (∑ i ∈ range (k + 1), if i < k - i ∧ k - i < L then 2 * x i * x (k - i) else 0) +
        (if k % 2 = 0 ∧ k / 2 < L then x (k / 2) * x (k / 2) else 0) := by
  set g : ℕ → ℕ := fun i => if i < L ∧ k - i < L then x i * x (k - i) else 0 with hg
  have hsym : ∀ i ∈ range (k + 1), g (k - i) = g i := by
    intro i hi
    have hik : i ≤ k := by
      have := Finset.mem_range.mp hi
      omega
    have e : k - (k - i) = i := by omega
    simp only [hg, e]
    by_cases h1 : i < L <;> by_cases h2 : k - i < L <;> simp [h1, h2, mul_comm]
  -- the three parts
  have hsplit : ∀ i, g i = (if i < k - i then g i else 0) + (if i = k - i then g i else 0) +
      (if k - i < i then g i else 0) := by
    intro i
    split_ifs <;> first | (exfalso; omega) | simp
  have h3 : (∑ i ∈ range (k + 1), if k - i < i then g i else 0) =
      ∑ i ∈ range (k + 1), if i < k - i then g i else 0 := by
    rw [← Finset.sum_range_reflect (fun i => if k - i < i then g i else 0) (k + 1)]
    refine Finset.sum_congr rfl fun i hi => ?_
    have hik : i ≤ k := by
      have := Finset.mem_range.mp hi
      omega
    have e1 : k + 1 - 1 - i = k - i := by omega
    have e2 : k - (k - i) = i := by omega
    simp only [e1, e2]
    rw [hsym i hi]
  have h2 : (∑ i ∈ range (k + 1), if i = k - i then g i else 0) =
      if k % 2 = 0 ∧ k / 2 < L then x (k / 2) * x (k / 2) else 0 := by
    by_cases hk : k % 2 = 0
    · have hmem : k / 2 ∈ range (k + 1) := Finset.mem_range.mpr (by omega)
      rw [Finset.sum_eq_single_of_mem (k / 2) hmem]
      · have e : k - k / 2 = k / 2 := by omega
        simp only [hg, e, hk, true_and, and_self]
        simp
      · intro i hi hne
        have hik := Finset.mem_range.mp hi
        have : ¬ i = k - i := by omega
        simp [this]
    · rw [Finset.sum_eq_zero]
      · simp [hk]
      · intro i hi
        have hik := Finset.mem_range.mp hi
        have : ¬ i = k - i := by omega
        simp [this]
  have h1 : (∑ i ∈ range (k + 1), if i < k - i then g i else 0) +
      (∑ i ∈ range (k + 1), if i < k - i then g i else 0) =
      ∑ i ∈ range (k + 1), if i < k - i ∧ k - i < L then 2 * x i * x (k - i) else 0 := by
    rw [← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun i _ => ?_
    by_cases ha : i < k - i
    · by_cases hb : k - i < L
      · have hc : i < L := by omega
        simp only [hg, ha, hb, hc, and_self, ↓reduceIte]
        ring
      · simp [hg, ha, hb]
    · simp [ha]
  unfold conv
  calc (∑ i ∈ range (k + 1), if i < L ∧ k - i < L then x i * x (k - i) else 0)
      = ∑ i ∈ range (k + 1), g i := rfl
    _ = ∑ i ∈ range (k + 1), ((if i < k - i then g i else 0) + (if i = k - i then g i else 0) +
          (if k - i < i then g i else 0)) := Finset.sum_congr rfl fun i _ => hsplit i
    _ = (∑ i ∈ range (k + 1), if i < k - i then g i else 0) +
          (∑ i ∈ range (k + 1), if i = k - i then g i else 0) +
          (∑ i ∈ range (k + 1), if k - i < i then g i else 0) := by
        rw [Finset.sum_add_distrib, Finset.sum_add_distrib]
    _ = _ := by
        rw [h3, h2, ← h1]
        ring

/-- A column is at most `L` products. -/
theorem conv_le {a b : ℕ → ℕ} {C : ℕ} (h : ∀ i j, a i * b j ≤ C) (L k : ℕ) :
    conv a b L k ≤ L * C := by
  unfold conv
  calc (∑ i ∈ range (k + 1), if i < L ∧ k - i < L then a i * b (k - i) else 0)
      ≤ ∑ i ∈ range (k + 1), if i < L then C else 0 := by
        refine Finset.sum_le_sum fun i _ => ?_
        by_cases h1 : i < L <;> by_cases h2 : k - i < L <;> simp [h1, h2, h]
    _ ≤ L * C := by
        rw [← Finset.sum_filter, Finset.sum_const, smul_eq_mul]
        refine Nat.mul_le_mul_right C ?_
        calc #({i ∈ range (k + 1) | i < L}) ≤ #(range L) :=
              Finset.card_le_card fun i hi => Finset.mem_range.mpr (Finset.mem_filter.mp hi).2
          _ = L := Finset.card_range L

/-- The sum of a mapped, filtered range as a sum with a condition. -/
theorem sum_map_filter_range (p : ℕ → Bool) (f : ℕ → ℕ) : ∀ N : ℕ,
    (((List.range N).filter p).map f).sum = ∑ i ∈ range N, if p i = true then f i else 0
  | 0 => by simp
  | N + 1 => by
    rw [List.range_succ, List.filter_append, List.map_append, List.sum_append,
      sum_map_filter_range p f N, Finset.sum_range_succ]
    congr 1
    by_cases h : p N = true <;> simp [h]

end Gpu28
