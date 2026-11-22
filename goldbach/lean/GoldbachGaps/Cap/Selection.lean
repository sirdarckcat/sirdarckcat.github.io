import GoldbachGaps.Basic

/-!
# The capped game: the bookkeeping of selected members

In the model of the search, after the sieve each row that is left for a member is prime with
probability `p`, independently of the others. The scanner tests only a selected set `T` of
members (those with few rows left, say) and logs the "hit mass" `Σ_{k ∈ T} (1 - p)^(rows left
for k)`.

`expected_hits` proves that this is exactly the expected number of successes among the
selected members, for every set `T` and every assignment of rows to members: with
independent coordinates `ω i ∈ {prime, composite}` of probability `p` and `1 - p`,

  `E [ #{k ∈ T : every row of k is composite} ] = Σ_{k ∈ T} (1 - p)^{|A k|}`.

Only the independence of the rows of one member is used (different members may even share
rows). The independence itself is the model and not a theorem.
-/

namespace GoldbachGaps.Cap

open Finset

variable {ι κ : Type*} [Fintype ι] [DecidableEq ι]

/-- The probability of the outcome `ω` when coordinate `i` is `true` ("prime") with
probability `p`, independently. -/
def bern (p : ℝ) (ω : ι → Bool) : ℝ := ∏ i, if ω i then p else 1 - p

/-- The probability that all coordinates in `A` are `false` ("composite") is
`(1 - p)^|A|`. -/
theorem sum_bern_all_false (p : ℝ) (A : Finset ι) :
    ∑ ω : ι → Bool, bern p ω * (∏ i ∈ A, if ω i then (0 : ℝ) else 1) = (1 - p) ^ #A := by
  have h1 : ∀ ω : ι → Bool,
      bern p ω * (∏ i ∈ A, if ω i then (0 : ℝ) else 1) =
        ∏ i, (if ω i then p else 1 - p) * (if i ∈ A then (if ω i then (0 : ℝ) else 1) else 1) := by
    intro ω
    rw [Finset.prod_mul_distrib, bern]
    congr 1
    rw [Finset.prod_ite_mem, Finset.univ_inter]
  simp_rw [h1]
  rw [← Fintype.prod_sum (fun i (b : Bool) =>
    (if b then p else 1 - p) * (if i ∈ A then (if b then (0 : ℝ) else 1) else 1))]
  have h2 : ∀ i, (∑ b : Bool,
      (if b then p else 1 - p) * (if i ∈ A then (if b then (0 : ℝ) else 1) else 1)) =
        if i ∈ A then 1 - p else 1 := by
    intro i
    rw [Fintype.sum_bool]
    by_cases hi : i ∈ A <;> simp [hi]
  simp_rw [h2]
  rw [Finset.prod_ite_mem, Finset.univ_inter, Finset.prod_const]

/-- The probabilities of all outcomes add up to `1`. -/
theorem sum_bern (p : ℝ) : ∑ ω : ι → Bool, bern (ι := ι) p ω = 1 := by
  have := sum_bern_all_false (ι := ι) p ∅
  simpa using this

/-- **The logged hit mass is the expected number of successes.** For every set `T` of
selected members, member `k` having the rows `A k` left:
`E [number of k ∈ T all of whose rows are composite] = Σ_{k ∈ T} (1 - p)^{|A k|}`. -/
theorem expected_hits (p : ℝ) (T : Finset κ) (A : κ → Finset ι) :
    ∑ ω : ι → Bool, bern p ω * (∑ k ∈ T, ∏ i ∈ A k, if ω i then (0 : ℝ) else 1) =
      ∑ k ∈ T, (1 - p) ^ #(A k) := by
  simp_rw [Finset.mul_sum]
  rw [Finset.sum_comm]
  exact Finset.sum_congr rfl fun k _ => sum_bern_all_false p (A k)

end GoldbachGaps.Cap
