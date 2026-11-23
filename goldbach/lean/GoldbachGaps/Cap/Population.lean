import GoldbachGaps.Basic

/-!
# The capped game: what a population of members can hold, and what a list merge can deliver

**The population bound.** Model: for a random member, row `j` is left by the sieve with
probability `s j`, independently of the other rows (`patternWeight`), and a member with `R`
rows left succeeds with probability `y^R`, `y = 1 - p`.

* `sum_patternWeight_mul_pow`: `E [x^R] = ∏ (1 - s_j + s_j x)`.
* `sum_patternWeight_le`: for `0 < u ≤ 1`, the part of `E [y^R]` that comes from members with
  at most `k` rows left is at most `u^(-k) ∏ (1 - s_j + s_j y u)` (large-deviation form; `y = 1`
  gives the probability of at most `k` rows left).
* `prob_patternRows_le`: with `μ = ∑ s_j` the mean number of rows left, a member has at most
  `μ - a` rows left with probability at most `exp (-a² / (2 μ))`. So in a population of `e^F`
  members no member is expected more than `√(2 F μ)` rows below the mean.
* `hitMass_selected_le`: whichever `m` members of a population are tested, their hit mass is at
  most `m y^k` plus the hit mass of the members with fewer than `k` rows left. With the bound
  above: `m` tests on a population of `e^F` members expect at most
  `m y^k + e^F u^(-k) ∏ (1 - s_j + s_j y u)` successes, for every `k` and `u`. This is the most
  that any method of finding good members can deliver, however it finds them.

**List merges.** `sum_window_card`: a set `S` of residues modulo `P` has on average `K |S| / P`
elements in a window of `K` consecutive members. `mitm_cost` and `mitm_condition`: merging two
lists of `a` and `b` residue combinations costs at least `a + b ≥ 2 √(a b)` and yields on
average `K a b / P` members, so the cost per member found is at least `2 P / (K √(a b))`; it
stays below `c` only if `P ≤ (c/2) K √(a b)`. In logarithms, with `F = ln K`, `H = ln (a b)`
the entropy of the lists and `C = ln P - H` the information they carry: `ln P ≤ F + H / 2`,
that is `ln P ≤ 2 F - C` (`mitm_condition_log`). Plain enumeration of the combinations has
`ln P ≤ F`. So a merge lets the constrained primes exceed the population by `F - C` nats and
no more.
-/

namespace GoldbachGaps.Cap

open Finset

section Model

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- The probability of the pattern `ω` of rows left (`ω j = true`: row `j` is left), when row
`j` is left with probability `s j`, independently. -/
def patternWeight (s : ι → ℝ) (ω : ι → Bool) : ℝ := ∏ j, if ω j then s j else 1 - s j

/-- The number of rows left in the pattern `ω`. -/
def patternRows (ω : ι → Bool) : ℕ := #(univ.filter fun j => ω j = true)

omit [DecidableEq ι] in
theorem patternWeight_nonneg {s : ι → ℝ} (hs0 : ∀ j, 0 ≤ s j) (hs1 : ∀ j, s j ≤ 1)
    (ω : ι → Bool) : 0 ≤ patternWeight s ω := by
  refine Finset.prod_nonneg fun j _ => ?_
  by_cases h : ω j = true
  · simp [h, hs0 j]
  · simp only [h]
    simp
    linarith [hs1 j]

/-- The generating function of the number of rows left: `E [x^R] = ∏ (1 - s_j + s_j x)`. -/
theorem sum_patternWeight_mul_pow (s : ι → ℝ) (x : ℝ) :
    ∑ ω : ι → Bool, patternWeight s ω * x ^ patternRows ω = ∏ j, (1 - s j + s j * x) := by
  have h1 : ∀ ω : ι → Bool, patternWeight s ω * x ^ patternRows ω =
      ∏ j, (if ω j then s j * x else 1 - s j) := by
    intro ω
    have hx : x ^ patternRows ω = ∏ j, (if ω j = true then x else 1) := by
      rw [Finset.prod_ite, Finset.prod_const_one, mul_one, Finset.prod_const, patternRows]
    rw [hx, patternWeight, ← Finset.prod_mul_distrib]
    refine Finset.prod_congr rfl fun j _ => ?_
    by_cases h : ω j = true <;> simp [h]
  simp_rw [h1]
  rw [← Fintype.prod_sum (fun j (b : Bool) => if b then s j * x else 1 - s j)]
  refine Finset.prod_congr rfl fun j _ => ?_
  rw [Fintype.sum_bool]
  simp
  ring

/-- **The large-deviation bound.** For `0 < u ≤ 1` and `0 ≤ y`: the contribution to `E [y^R]`
of the patterns with at most `k` rows left is at most `u^(-k) ∏ (1 - s_j + s_j y u)`. -/
theorem sum_patternWeight_le {s : ι → ℝ} (hs0 : ∀ j, 0 ≤ s j) (hs1 : ∀ j, s j ≤ 1)
    {y u : ℝ} (hy : 0 ≤ y) (hu0 : 0 < u) (hu1 : u ≤ 1) (k : ℕ) :
    ∑ ω ∈ univ.filter (fun ω : ι → Bool => patternRows ω ≤ k), patternWeight s ω * y ^ patternRows ω ≤
      (u ^ k)⁻¹ * ∏ j, (1 - s j + s j * (y * u)) := by
  rw [← sum_patternWeight_mul_pow, Finset.mul_sum]
  have hstep : ∀ ω ∈ univ.filter (fun ω : ι → Bool => patternRows ω ≤ k),
      patternWeight s ω * y ^ patternRows ω ≤
        (u ^ k)⁻¹ * (patternWeight s ω * (y * u) ^ patternRows ω) := by
    intro ω hω
    have hR : patternRows ω ≤ k := (Finset.mem_filter.mp hω).2
    have hw := patternWeight_nonneg hs0 hs1 ω
    have hpow : u ^ k ≤ u ^ patternRows ω := pow_le_pow_of_le_one hu0.le hu1 hR
    have huk : 0 < u ^ k := pow_pos hu0 k
    have h1 : (1 : ℝ) ≤ (u ^ k)⁻¹ * u ^ patternRows ω := by
      rw [← div_eq_inv_mul, le_div_iff₀ huk]
      linarith
    have h2 : 0 ≤ patternWeight s ω * y ^ patternRows ω := mul_nonneg hw (pow_nonneg hy _)
    calc patternWeight s ω * y ^ patternRows ω
        ≤ patternWeight s ω * y ^ patternRows ω * ((u ^ k)⁻¹ * u ^ patternRows ω) :=
          le_mul_of_one_le_right h2 h1
      _ = (u ^ k)⁻¹ * (patternWeight s ω * (y * u) ^ patternRows ω) := by
          rw [mul_pow]
          ring
  refine (Finset.sum_le_sum hstep).trans ?_
  refine Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset _ _) fun ω _ _ => ?_
  exact mul_nonneg (inv_nonneg.mpr (pow_nonneg hu0.le k))
    (mul_nonneg (patternWeight_nonneg hs0 hs1 ω) (pow_nonneg (mul_nonneg hy hu0.le) _))

omit [DecidableEq ι] in
/-- `∏ (1 - s_j + s_j v) ≤ exp (-(1 - v) ∑ s_j)` for `v ≥ 0`. -/
theorem prod_le_exp_neg {s : ι → ℝ} (hs0 : ∀ j, 0 ≤ s j) (hs1 : ∀ j, s j ≤ 1) {v : ℝ}
    (hv0 : 0 ≤ v) :
    ∏ j, (1 - s j + s j * v) ≤ Real.exp (-(1 - v) * ∑ j, s j) := by
  rw [Finset.mul_sum, Real.exp_sum]
  refine Finset.prod_le_prod₀ (fun j _ => ?_) fun j _ => ?_
  · nlinarith [hs0 j, hs1 j, mul_nonneg (hs0 j) hv0]
  · have h := Real.add_one_le_exp (-(1 - v) * s j)
    linarith

/-- `e^(-θ) ≤ 1 - θ + θ²/2` for `θ ≥ 0`. -/
theorem exp_neg_le_quadratic {θ : ℝ} (hθ : 0 ≤ θ) : Real.exp (-θ) ≤ 1 - θ + θ ^ 2 / 2 := by
  have h1 := Real.quadratic_le_exp_of_nonneg hθ
  have hpos : 0 < 1 + θ + θ ^ 2 / 2 := by positivity
  have h2 : Real.exp (-θ) ≤ (1 + θ + θ ^ 2 / 2)⁻¹ := by
    rw [Real.exp_neg]
    exact inv_anti₀ hpos h1
  refine h2.trans ?_
  rw [inv_le_iff_one_le_mul₀ hpos]
  nlinarith [sq_nonneg (θ ^ 2)]

/-- **Few rows left is rare.** With `μ = ∑ s_j > 0` the mean number of rows left: a member has
at most `k ≤ μ - a` rows left with probability at most `exp (-a² / (2 μ))`. -/
theorem prob_patternRows_le {s : ι → ℝ} (hs0 : ∀ j, 0 ≤ s j) (hs1 : ∀ j, s j ≤ 1) {a : ℝ}
    (ha : 0 ≤ a) (hμ : 0 < ∑ j, s j) (k : ℕ) (hk : (k : ℝ) ≤ ∑ j, s j - a) :
    ∑ ω ∈ univ.filter (fun ω : ι → Bool => patternRows ω ≤ k), patternWeight s ω ≤
      Real.exp (-(a ^ 2) / (2 * ∑ j, s j)) := by
  set μ := ∑ j, s j with hμdef
  have hk0 : (0 : ℝ) ≤ k := Nat.cast_nonneg k
  have haμ : a ≤ μ := by linarith
  set θ := a / μ with hθdef
  have hθ0 : 0 ≤ θ := div_nonneg ha hμ.le
  have hu0 : 0 < Real.exp (-θ) := Real.exp_pos _
  have hu1 : Real.exp (-θ) ≤ 1 := Real.exp_le_one_iff.mpr (by linarith)
  have h := sum_patternWeight_le hs0 hs1 (y := 1) (by norm_num) hu0 hu1 k
  simp only [one_pow, mul_one, one_mul] at h
  refine h.trans ?_
  have h2 := prod_le_exp_neg hs0 hs1 hu0.le
  have h3 : (Real.exp (-θ) ^ k)⁻¹ = Real.exp (θ * k) := by
    rw [← Real.exp_natCast_mul, ← Real.exp_neg]
    congr 1
    ring
  rw [h3]
  have h4 : Real.exp (θ * k) * ∏ j, (1 - s j + s j * Real.exp (-θ)) ≤
      Real.exp (θ * k) * Real.exp (-(1 - Real.exp (-θ)) * μ) :=
    mul_le_mul_of_nonneg_left h2 (Real.exp_pos _).le
  refine h4.trans ?_
  rw [← Real.exp_add]
  apply Real.exp_le_exp.mpr
  have h5 := exp_neg_le_quadratic hθ0
  have hθμ : θ * μ = a := by
    rw [hθdef]
    field_simp
  have h6 : θ * k ≤ θ * (μ - a) := mul_le_mul_of_nonneg_left hk hθ0
  have h7 : -(1 - Real.exp (-θ)) * μ ≤ -(θ - θ ^ 2 / 2) * μ := by nlinarith
  have h8 : θ ^ 2 * μ = a ^ 2 / μ := by
    rw [hθdef]
    field_simp
  have h9 : -(a ^ 2) / (2 * μ) = -(a ^ 2 / μ) / 2 := by
    field_simp
  rw [h9]
  nlinarith

end Model

section Selected

/-- **No selection beats the population.** `R t` is the number of rows left for member `t`,
`y^(R t)` its chance of success. Whichever members `S` of the population are tested, their hit
mass is at most `|S| y^k` plus the hit mass of all members with fewer than `k` rows left. -/
theorem hitMass_selected_le {T : Type*} (pop S : Finset T) (hS : S ⊆ pop) (R : T → ℕ) {y : ℝ}
    (hy0 : 0 ≤ y) (hy1 : y ≤ 1) (k : ℕ) :
    ∑ t ∈ S, y ^ R t ≤ #S * y ^ k + ∑ t ∈ pop.filter (fun t => R t < k), y ^ R t := by
  classical
  rw [← Finset.sum_filter_add_sum_filter_not S (fun t => k ≤ R t)]
  refine add_le_add ?_ ?_
  · calc ∑ t ∈ S.filter (fun t => k ≤ R t), y ^ R t
        ≤ ∑ _t ∈ S.filter (fun t => k ≤ R t), y ^ k :=
          Finset.sum_le_sum fun t ht =>
            pow_le_pow_of_le_one hy0 hy1 (Finset.mem_filter.mp ht).2
      _ = #(S.filter (fun t => k ≤ R t)) * y ^ k := by rw [Finset.sum_const, nsmul_eq_mul]
      _ ≤ #S * y ^ k := by
          refine mul_le_mul_of_nonneg_right ?_ (pow_nonneg hy0 k)
          exact_mod_cast Finset.card_le_card (Finset.filter_subset _ _)
  · refine Finset.sum_le_sum_of_subset_of_nonneg (fun t ht => ?_) fun t _ _ => pow_nonneg hy0 _
    obtain ⟨htS, hnot⟩ := Finset.mem_filter.mp ht
    exact Finset.mem_filter.mpr ⟨hS htS, not_le.mp hnot⟩

end Selected

section Merge

/-- Every residue modulo `P` lies in exactly `K` of the `P` windows `x, x + 1, …, x + K - 1`:
a set `S` of residues has on average `K |S| / P` elements in a window. -/
theorem sum_window_card (P K : ℕ) [NeZero P] (S : Finset (ZMod P)) :
    ∑ x : ZMod P, #((Finset.range K).filter fun i : ℕ => x + (i : ZMod P) ∈ S) = K * #S := by
  classical
  simp_rw [Finset.card_filter]
  rw [Finset.sum_comm]
  have h : ∀ i ∈ Finset.range K, (∑ x : ZMod P, if x + (i : ZMod P) ∈ S then 1 else 0) = #S := by
    intro i _
    rw [← Finset.card_filter]
    refine Finset.card_bij (fun x _ => x + (i : ZMod P)) ?_ ?_ ?_
    · intro x hx
      exact (Finset.mem_filter.mp hx).2
    · intro x _ x' _ hxx
      exact add_right_cancel hxx
    · intro b hb
      exact ⟨b - (i : ZMod P), Finset.mem_filter.mpr ⟨Finset.mem_univ _, by simpa using hb⟩,
        by simp⟩
  rw [Finset.sum_congr rfl h, Finset.sum_const, Finset.card_range, smul_eq_mul]

/-- Merging two lists of `a` and `b` entries costs at least `a + b`, and `a + b ≥ 2 √(a b)`;
the merge yields `K a b / P` members on average. So the cost per member found is at least
`2 P / (K √(a b))`. -/
theorem mitm_cost {a b P K : ℝ} (ha : 0 < a) (hb : 0 < b) (hP : 0 < P) (hK : 0 < K) :
    2 * P / (K * Real.sqrt (a * b)) ≤ (a + b) / (K * (a * b) / P) := by
  have hab : 0 < a * b := mul_pos ha hb
  have hs : 0 < Real.sqrt (a * b) := Real.sqrt_pos.mpr hab
  have hss : Real.sqrt (a * b) * Real.sqrt (a * b) = a * b := Real.mul_self_sqrt hab.le
  have hamgm : 2 * Real.sqrt (a * b) ≤ a + b := by
    nlinarith [sq_nonneg (a - b), sq_nonneg (a + b - 2 * Real.sqrt (a * b)), mul_pos ha hb]
  rw [div_le_div_iff₀ (mul_pos hK hs) (div_pos (mul_pos hK hab) hP)]
  have e1 : 2 * P * (K * (a * b) / P) = 2 * K * (a * b) := by
    field_simp
  rw [e1]
  have e2 : 2 * K * (a * b) = K * Real.sqrt (a * b) * (2 * Real.sqrt (a * b)) := by
    linear_combination (-2 * K) * hss
  rw [e2, mul_comm (a + b)]
  exact mul_le_mul_of_nonneg_left hamgm (mul_pos hK hs).le

/-- **The condition for a merge.** If the cost per member found is at most `c`, then
`P ≤ (c / 2) K √(a b)`. -/
theorem mitm_condition {a b P K c : ℝ} (ha : 0 < a) (hb : 0 < b) (hP : 0 < P) (hK : 0 < K)
    (h : (a + b) / (K * (a * b) / P) ≤ c) : P ≤ c / 2 * K * Real.sqrt (a * b) := by
  have hab : 0 < a * b := mul_pos ha hb
  have hs : 0 < Real.sqrt (a * b) := Real.sqrt_pos.mpr hab
  have h1 := (mitm_cost ha hb hP hK).trans h
  rw [div_le_iff₀ (mul_pos hK hs)] at h1
  linarith

/-- The same in logarithms: with `H` the entropy of the lists, `C` the information they carry
and `ln P = H + C`, the condition `ln P ≤ F + H / 2` is `ln P ≤ 2 F - C`. -/
theorem mitm_condition_log {lnP F H C : ℝ} (hH : lnP = H + C) (h : lnP ≤ F + H / 2) :
    lnP ≤ 2 * F - C := by
  linarith

end Merge

end GoldbachGaps.Cap
