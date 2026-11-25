import GoldbachGaps.Cap.Budget

/-!
# Lists of classes below a bound, families and information, and the smallest instance

The bottom-up round of 25 November 2026 asked for exact statements about *soft* constraints: lists
of several classes per prime, as opposed to pinning one class.

* **Counting.** `card_residues_in_le_sub`: the number of `N < X` whose residue modulo every modulus
  of `S` lies in a list is at most `(∏_{r ∈ S'} |A r|) · (X / ∏_{r ∈ S'} r + 1)` for *every* subfamily
  `S' ⊆ S`, so the bound to use is the least over the subfamilies and not the product over all of
  them. `card_residues_in_le_of_le`: a modulus `r ≥ X` allows at most `|A r|` numbers below `X`,
  whatever the other lists are, so when every modulus exceeds the bound at most `min |A r|` numbers
  lie in all the lists. `exists_lists_holding`: and that is attained, since any `ℓ` numbers below
  `X` lie in lists of at most `ℓ` classes. Beyond the window the number of primes listed buys
  nothing in the worst case: the count is governed by the shortest list.

* **Information.** `sum_mul_log_div_le` (the log-sum inequality), `binary_kl_le` and
  `family_rarity_le`, `family_enrichment_le`, `exp_neg_kl_le_of_holds_all`: let `p` be the law of
  the best members and `q` the law of all members on
  whatever a family is allowed to read (the classes modulo some primes, the cover). A family `F`
  that holds the share `p(F)` of the best members has `p(F) · ln (1 / q(F)) ≤ KL(p ‖ q) + ln 2`.
  So a family cannot be rarer than the information in what it reads allows, however its lists are
  shaped; `scripts/alignment/` measures that information in the miniature, about a fifth of a nat
  for each prime beyond the line.

* **The smallest instance.** `Example840`: rows the 36 odd primes below 160, moduli 3, 5, 7, 11,
  13, candidates the even `N < 840`. The least number of rows left is 6, at `N = 578` only. For
  each of the seven sets of moduli that can be pinned below 840 and not enlarged, every candidate
  in a best class of that set is left with at least 7 rows: pinning, with a full scan of the best
  windows, does not find the optimum, whose own class is one row short of the best in every one of
  the seven designs.
-/

open Finset Real

namespace GoldbachGaps.Cap

/-! ### Counting -/

/-- The budget law for a subfamily: constraints outside `S'` are dropped. -/
theorem card_residues_in_le_sub {S S' : Finset ℕ} (hS : S' ⊆ S) (A : ℕ → Finset ℕ) (X : ℕ)
    (hpos : ∀ r ∈ S', 0 < r) (hcop : (S' : Set ℕ).Pairwise Nat.Coprime) :
    #{N ∈ range X | ∀ r ∈ S, N % r ∈ A r} ≤ (∏ r ∈ S', #(A r)) * (X / (∏ r ∈ S', r) + 1) := by
  refine le_trans (Finset.card_le_card ?_) (card_residues_in_le S' A X hpos hcop)
  intro N hN
  rw [Finset.mem_filter] at hN ⊢
  exact ⟨hN.1, fun r hr => hN.2 r (hS hr)⟩

/-- A modulus at least as large as the bound: its list alone caps the count. -/
theorem card_residues_in_le_of_le {S : Finset ℕ} (A : ℕ → Finset ℕ) {X r : ℕ} (hr : r ∈ S)
    (hX : X ≤ r) : #{N ∈ range X | ∀ r ∈ S, N % r ∈ A r} ≤ #(A r) := by
  refine Finset.card_le_card ?_
  intro N hN
  rw [Finset.mem_filter, Finset.mem_range] at hN
  have h := hN.2 r hr
  rwa [Nat.mod_eq_of_lt (lt_of_lt_of_le hN.1 hX)] at h

/-- Any set of numbers below `X` lies in lists no longer than itself. -/
theorem exists_lists_holding (S : Finset ℕ) {X : ℕ} (𝒩 : Finset ℕ) (h𝒩 : 𝒩 ⊆ range X) :
    ∃ A : ℕ → Finset ℕ, (∀ r, #(A r) ≤ #𝒩) ∧ #𝒩 ≤ #{N ∈ range X | ∀ r ∈ S, N % r ∈ A r} := by
  refine ⟨fun r => 𝒩.image (· % r), fun r => Finset.card_image_le, Finset.card_le_card ?_⟩
  intro N hN
  rw [Finset.mem_filter]
  exact ⟨h𝒩 hN, fun r _ => Finset.mem_image_of_mem _ hN⟩

/-! ### Families and information -/

/-- The log-sum inequality on a finite set, with positive `q`. -/
theorem sum_mul_log_div_le {Ω : Type*} (F : Finset Ω) (p q : Ω → ℝ) (hp : ∀ ω ∈ F, 0 ≤ p ω)
    (hq : ∀ ω ∈ F, 0 < q ω) :
    (∑ ω ∈ F, p ω) * log ((∑ ω ∈ F, p ω) / ∑ ω ∈ F, q ω) ≤ ∑ ω ∈ F, p ω * log (p ω / q ω) := by
  rcases F.eq_empty_or_nonempty with rfl | hne
  · simp
  have hQ : 0 < ∑ ω ∈ F, q ω := Finset.sum_pos hq hne
  have hJ := Real.convexOn_mul_log.map_sum_le (t := F) (w := fun ω => q ω / ∑ ω ∈ F, q ω)
    (p := fun ω => p ω / q ω) (fun ω hω => div_nonneg (hq ω hω).le hQ.le)
    (by rw [← Finset.sum_div, div_self hQ.ne'])
    (fun ω hω => Set.mem_Ici.mpr (div_nonneg (hp ω hω) (hq ω hω).le))
  have e1 : ∑ ω ∈ F, (q ω / ∑ ω ∈ F, q ω) • (p ω / q ω) = (∑ ω ∈ F, p ω) / ∑ ω ∈ F, q ω := by
    rw [Finset.sum_div]
    refine Finset.sum_congr rfl fun ω hω => ?_
    have := (hq ω hω).ne'
    simp only [smul_eq_mul]
    field_simp
  have e2 : ∑ ω ∈ F, (q ω / ∑ ω ∈ F, q ω) • (p ω / q ω * log (p ω / q ω)) =
      (∑ ω ∈ F, p ω * log (p ω / q ω)) / ∑ ω ∈ F, q ω := by
    rw [Finset.sum_div]
    refine Finset.sum_congr rfl fun ω hω => ?_
    have := (hq ω hω).ne'
    simp only [smul_eq_mul]
    field_simp
  rw [e1, e2] at hJ
  have := mul_le_mul_of_nonneg_left hJ hQ.le
  calc (∑ ω ∈ F, p ω) * log ((∑ ω ∈ F, p ω) / ∑ ω ∈ F, q ω)
      = (∑ ω ∈ F, q ω) * ((∑ ω ∈ F, p ω) / (∑ ω ∈ F, q ω) *
          log ((∑ ω ∈ F, p ω) / ∑ ω ∈ F, q ω)) := by field_simp
    _ ≤ (∑ ω ∈ F, q ω) * ((∑ ω ∈ F, p ω * log (p ω / q ω)) / ∑ ω ∈ F, q ω) := this
    _ = ∑ ω ∈ F, p ω * log (p ω / q ω) := by field_simp

/-- An event cannot separate two laws by more than their divergence: for `p`, `q` on a finite
space and any `F`, the divergence of the two-point laws `(p F, p Fᶜ)`, `(q F, q Fᶜ)` is at most
`KL(p ‖ q)`. -/
theorem binary_kl_le {Ω : Type*} [Fintype Ω] [DecidableEq Ω] (p q : Ω → ℝ) (hp : ∀ ω, 0 ≤ p ω)
    (hq : ∀ ω, 0 < q ω) (F : Finset Ω) :
    (∑ ω ∈ F, p ω) * log ((∑ ω ∈ F, p ω) / ∑ ω ∈ F, q ω) +
        (∑ ω ∈ Fᶜ, p ω) * log ((∑ ω ∈ Fᶜ, p ω) / ∑ ω ∈ Fᶜ, q ω) ≤
      ∑ ω, p ω * log (p ω / q ω) := by
  have h1 := sum_mul_log_div_le F p q (fun ω _ => hp ω) (fun ω _ => hq ω)
  have h2 := sum_mul_log_div_le Fᶜ p q (fun ω _ => hp ω) (fun ω _ => hq ω)
  have h3 : ∑ ω, p ω * log (p ω / q ω) =
      ∑ ω ∈ F, p ω * log (p ω / q ω) + ∑ ω ∈ Fᶜ, p ω * log (p ω / q ω) :=
    (Finset.sum_add_sum_compl F _).symm
  linarith

/-- **Families and information.** `p` the law of the best members and `q` the law of all members
on what a family may read, both of total mass one, `q` positive. A family `F` satisfies
`p(F) · ln (1 / q(F)) ≤ KL(p ‖ q) + ln 2`: holding a share of the best members costs rarity only up
to the information available. -/
theorem family_rarity_le {Ω : Type*} [Fintype Ω] [DecidableEq Ω] (p q : Ω → ℝ) (hp : ∀ ω, 0 ≤ p ω)
    (hq : ∀ ω, 0 < q ω) (hp1 : ∑ ω, p ω = 1) (hq1 : ∑ ω, q ω = 1) (F : Finset Ω) :
    (∑ ω ∈ F, p ω) * log (1 / ∑ ω ∈ F, q ω) ≤ ∑ ω, p ω * log (p ω / q ω) + log 2 := by
  have hb := binary_kl_le p q hp hq F
  set P := ∑ ω ∈ F, p ω with hP
  set Qf := ∑ ω ∈ F, q ω with hQf
  have hPc : ∑ ω ∈ Fᶜ, p ω = 1 - P := by rw [← hp1, hP]; linarith [Finset.sum_add_sum_compl F p]
  have hQc : ∑ ω ∈ Fᶜ, q ω = 1 - Qf := by rw [← hq1, hQf]; linarith [Finset.sum_add_sum_compl F q]
  rw [hPc, hQc] at hb
  have hP0 : 0 ≤ P := Finset.sum_nonneg fun ω _ => hp ω
  have hP1 : P ≤ 1 := by
    have : 0 ≤ ∑ ω ∈ Fᶜ, p ω := Finset.sum_nonneg fun ω _ => hp ω
    linarith
  have hQ0 : 0 ≤ Qf := Finset.sum_nonneg fun ω _ => (hq ω).le
  have hQ1 : Qf ≤ 1 := by
    have : 0 ≤ ∑ ω ∈ Fᶜ, q ω := Finset.sum_nonneg fun ω _ => (hq ω).le
    linarith
  -- the entropy of the two-point law is at most ln 2
  have hent : -log 2 ≤ P * log P + (1 - P) * log (1 - P) := by
    have := Real.binEntropy_le_log_two (p := P)
    rw [Real.binEntropy_eq_negMulLog_add_negMulLog_one_sub] at this
    simp only [Real.negMulLog] at this
    linarith
  -- the two terms of the divergence
  have t1 : P * log (P / Qf) = P * log P + P * log (1 / Qf) := by
    rcases eq_or_lt_of_le hP0 with h | h
    · rw [← h]; simp
    have h' : 0 < Qf := by
      rcases F.eq_empty_or_nonempty with hF | hF
      · rw [hP, hF] at h; simp at h
      · exact Finset.sum_pos (fun ω _ => hq ω) hF
    rw [div_eq_mul_one_div, Real.log_mul h.ne' (one_div_pos.mpr h').ne']; ring
  have t2 : (1 - P) * log (1 - P) ≤ (1 - P) * log ((1 - P) / (1 - Qf)) := by
    rcases eq_or_lt_of_le (sub_nonneg.mpr hP1) with h | h
    · rw [← h]; simp
    rcases eq_or_lt_of_le (sub_nonneg.mpr hQ1) with h' | h'
    · rw [← h']; simp
      exact mul_nonpos_of_nonneg_of_nonpos h.le (Real.log_nonpos (by linarith) (by linarith))
    refine mul_le_mul_of_nonneg_left (Real.log_le_log h ?_) h.le
    rw [le_div_iff₀ h']
    nlinarith
  linarith

/-- The same as a bound on the enrichment: a family that holds the share `p(F) > 0` of the best
members is at most `exp ((KL(p ‖ q) + ln 2) / p(F))` times denser in them than the population is. -/
theorem family_enrichment_le {Ω : Type*} [Fintype Ω] [DecidableEq Ω] (p q : Ω → ℝ)
    (hp : ∀ ω, 0 ≤ p ω) (hq : ∀ ω, 0 < q ω) (hp1 : ∑ ω, p ω = 1) (hq1 : ∑ ω, q ω = 1)
    (F : Finset Ω) (hF : 0 < ∑ ω ∈ F, p ω) :
    (∑ ω ∈ F, p ω) / (∑ ω ∈ F, q ω) ≤
      exp ((∑ ω, p ω * log (p ω / q ω) + log 2) / ∑ ω ∈ F, p ω) := by
  have h := family_rarity_le p q hp hq hp1 hq1 F
  have hne : F.Nonempty := by
    rcases F.eq_empty_or_nonempty with h0 | h0
    · rw [h0] at hF; simp at hF
    · exact h0
  have hQ : 0 < ∑ ω ∈ F, q ω := Finset.sum_pos (fun ω _ => hq ω) hne
  have hP1 : ∑ ω ∈ F, p ω ≤ 1 := by
    have : 0 ≤ ∑ ω ∈ Fᶜ, p ω := Finset.sum_nonneg fun ω _ => hp ω
    linarith [Finset.sum_add_sum_compl F p]
  have h2 : log (1 / ∑ ω ∈ F, q ω) ≤ (∑ ω, p ω * log (p ω / q ω) + log 2) / ∑ ω ∈ F, p ω := by
    rw [le_div_iff₀ hF]; linarith
  have h3 : 1 / ∑ ω ∈ F, q ω ≤ exp ((∑ ω, p ω * log (p ω / q ω) + log 2) / ∑ ω ∈ F, p ω) := by
    have := Real.exp_le_exp.mpr h2
    rwa [Real.exp_log (one_div_pos.mpr hQ)] at this
  calc (∑ ω ∈ F, p ω) / (∑ ω ∈ F, q ω) = (∑ ω ∈ F, p ω) * (1 / ∑ ω ∈ F, q ω) := by ring
    _ ≤ 1 * (1 / ∑ ω ∈ F, q ω) := mul_le_mul_of_nonneg_right hP1 (one_div_pos.mpr hQ).le
    _ ≤ _ := by rw [one_mul]; exact h3

/-- A family that holds *all* the best members has density at least `exp (- KL(p ‖ q))`: it is at
most `exp (KL)` times denser in them than the population. -/
theorem exp_neg_kl_le_of_holds_all {Ω : Type*} [Fintype Ω] [DecidableEq Ω] (p q : Ω → ℝ)
    (hp : ∀ ω, 0 ≤ p ω) (hq : ∀ ω, 0 < q ω) (hp1 : ∑ ω, p ω = 1) (F : Finset Ω)
    (hF : ∑ ω ∈ F, p ω = 1) :
    exp (-∑ ω, p ω * log (p ω / q ω)) ≤ ∑ ω ∈ F, q ω := by
  have hb := binary_kl_le p q hp hq F
  have hPc : ∑ ω ∈ Fᶜ, p ω = 0 := by linarith [Finset.sum_add_sum_compl F p]
  rw [hF, hPc, zero_mul, add_zero, one_mul] at hb
  have hne : F.Nonempty := by
    rcases F.eq_empty_or_nonempty with h0 | h0
    · rw [h0] at hF; simp at hF
    · exact h0
  have hQ : 0 < ∑ ω ∈ F, q ω := Finset.sum_pos (fun ω _ => hq ω) hne
  rw [Real.log_div one_ne_zero hQ.ne', Real.log_one, zero_sub] at hb
  have : -∑ ω, p ω * log (p ω / q ω) ≤ log (∑ ω ∈ F, q ω) := by linarith
  calc exp (-∑ ω, p ω * log (p ω / q ω)) ≤ exp (log (∑ ω ∈ F, q ω)) := Real.exp_le_exp.mpr this
    _ = ∑ ω ∈ F, q ω := Real.exp_log hQ

/-! ### The smallest instance found: target 160, bound 840 -/

namespace Example840

/-- The rows: the 36 odd primes below 160. -/
def rows : List ℕ :=
  [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
   101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157]

/-- The moduli. -/
def moduli : List ℕ := [3, 5, 7, 11, 13]

/-- The rows left at `N` by the moduli of `T`: the rows not congruent to `N` modulo any of them. -/
def left (T : List ℕ) (N : ℕ) : ℕ :=
  (rows.filter fun q => T.all fun r => decide (q % r ≠ N % r)).length

/-- The candidates: the even `N < 840`. -/
def cands : List ℕ := (List.range 420).map (2 * ·)

/-- A set of moduli that can be pinned below 840 (every vector of classes occurs among the
candidates) and cannot be enlarged. -/
def Pinnable (T : List ℕ) : Prop :=
  2 * T.prod ≤ 840 ∧ ∀ r ∈ moduli, r ∉ T → 840 < 2 * T.prod * r

instance (T : List ℕ) : Decidable (Pinnable T) := by unfold Pinnable; infer_instance

/-- The seven maximal pinnable sets, each with its design value (the least number of rows its
classes can leave). -/
def designs : List (List ℕ × ℕ) :=
  [([3, 5, 7], 9), ([3, 5, 11], 10), ([3, 5, 13], 10), ([3, 7, 11], 12), ([3, 7, 13], 12),
   ([5, 7, 11], 17), ([11, 13], 27)]

theorem rows_are_the_odd_primes : ∀ q < 160, (q ∈ rows ↔ q.Prime ∧ q ≠ 2) := by decide +kernel

/-- These are exactly the sets of moduli that can be pinned and not enlarged. -/
theorem pinnable_iff : ∀ T ∈ moduli.sublists, (Pinnable T ↔ T ∈ designs.map Prod.fst) := by
  decide +kernel

/-- **The optimum.** Every candidate is left with at least 6 rows, and `578` is the only one left
with 6. -/
theorem optimum : (∀ N ∈ cands, 6 ≤ left moduli N) ∧ left moduli 578 = 6 ∧
    ∀ N ∈ cands, left moduli N = 6 → N = 578 := by
  decide +kernel

/-- The design values are what they are said to be. -/
theorem design_values : ∀ d ∈ designs, (∀ N ∈ cands, d.2 ≤ left d.1 N) ∧
    ∃ N ∈ cands, left d.1 N = d.2 := by
  decide +kernel

/-- **Pinning does not reach the optimum.** In each of the seven designs, every candidate that lies
in a best class of the design is left with at least 7 rows by the five moduli together. -/
theorem pinning_misses : ∀ d ∈ designs, ∀ N ∈ cands, left d.1 N = d.2 → 7 ≤ left moduli N := by
  decide +kernel

/-- The optimum's own class is one row short of the best in every design. -/
theorem optimum_second_best : ∀ d ∈ designs, left d.1 578 = d.2 + 1 := by decide +kernel

end Example840

end GoldbachGaps.Cap
