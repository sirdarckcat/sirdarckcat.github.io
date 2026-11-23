import GoldbachGaps.Basic

/-!
# What a list of classes modulo one prime can buy

A design that restricts `N` modulo a prime `s` to a list `L` of classes pays `ln (s / |L|)` nats:
that is the factor by which the population shrinks. What it buys is a higher chance that `s`
divides a row. Write `w a` for the number of rows `N - q` that `s` divides when `N` is in the
class `a` (so `∑ w / s = μ` rows on average, and at most `W` in any class). For a member taken
uniformly from the list the average is `∑_{a ∈ L} w a / |L|`.

* `list_gain_le`: whatever the list,
  `∑_{a ∈ L} w a / |L| - μ ≤ (W - μ) / ln (W / μ) · ln (s / |L|)`.
  So a nat of constraint on `s` buys at most `(W - μ) / ln (W / μ)` rows. Equality needs every
  class of the list to hold exactly `W` rows and the list to hold all the rows.
* `list_gain_above_Q`: the case of a prime above `Q`. There every class holds at most one row
  (`W = 1`), and with at most 1609 rows left and `s ≥ 213070` a nat buys at most 0.207 rows,
  that is `0.207 · 0.02419 = 0.005` nats of success. The shape of the list does not enter:
  intervals, progressions and the set of rows itself all obey it. For comparison, the research
  session measures an extra covering prime just above 463 at about 0.2 nats of success for its
  6.1 nats (`goldbach/sublinear/README.md` on `ccr-d4a17dd0-7uu03r`), about six times more a nat.

Consequence for the search: the part of the prize that lies in the primes above `Q` cannot be
collected by any design that is a product of lists, one per prime (which is what lattices,
meets in the middle and generalised birthday merges enumerate). It is collected only by
members that are good in total without being constrained prime by prime, and for those the
bound is the Chernoff one of `Cap/Population.lean`.
-/

namespace GoldbachGaps.Cap

open Finset

/-- `(x - 1) / ln x` is nondecreasing on `(1, ∞)`, in cross-multiplied form. -/
theorem sub_one_mul_log_le {x y : ℝ} (hx : 1 ≤ x) (hxy : x ≤ y) :
    (x - 1) * Real.log y ≤ (y - 1) * Real.log x := by
  rcases eq_or_lt_of_le hxy with rfl | hlt
  · exact le_rfl
  have hy1 : 0 < y - 1 := by linarith
  -- `x` is the convex combination `(y - x)/(y - 1) · 1 + (x - 1)/(y - 1) · y`
  have hmem1 : (1 : ℝ) ∈ Set.Ioi (0 : ℝ) := by simp
  have hmemy : y ∈ Set.Ioi (0 : ℝ) := by simp; linarith
  have ha : 0 ≤ (y - x) / (y - 1) := div_nonneg (by linarith) hy1.le
  have hb : 0 ≤ (x - 1) / (y - 1) := div_nonneg (by linarith) hy1.le
  have hab : (y - x) / (y - 1) + (x - 1) / (y - 1) = 1 := by
    field_simp
    ring
  have hconc := strictConcaveOn_log_Ioi.concaveOn.2 hmem1 hmemy ha hb hab
  have hcomb : (y - x) / (y - 1) * 1 + (x - 1) / (y - 1) * y = x := by
    field_simp
    ring
  simp only [smul_eq_mul, Real.log_one, mul_zero, zero_add] at hconc
  rw [hcomb] at hconc
  have h := mul_le_mul_of_nonneg_left hconc hy1.le
  have h2 : (y - 1) * ((x - 1) / (y - 1) * Real.log y) = (x - 1) * Real.log y := by
    field_simp
  linarith

/-- **A nat of constraint on one prime buys at most `(W - μ) / ln (W / μ)` rows.**
`w a` is the number of rows killed when `N` is in the class `a`; `μ = ∑ w / s` is the average
over all `s` classes and `W` a bound for every class. For any nonempty list `L` of classes, the
average over the list exceeds `μ` by at most `(W - μ) / ln (W / μ)` times `ln (s / |L|)`, the
nats that the restriction to `L` costs. -/
theorem list_gain_le {α : Type*} [Fintype α] (w : α → ℝ) (W : ℝ) (hw0 : ∀ a, 0 ≤ w a)
    (hwW : ∀ a, w a ≤ W) (L : Finset α) (hL : L.Nonempty) (hpos : 0 < ∑ a, w a)
    (hlt : (∑ a, w a) / Fintype.card α < W) :
    (∑ a ∈ L, w a) / L.card - (∑ a, w a) / Fintype.card α ≤
      (W - (∑ a, w a) / Fintype.card α) / Real.log (W / ((∑ a, w a) / Fintype.card α)) *
        Real.log (Fintype.card α / L.card) := by
  classical
  have hl : (0 : ℝ) < L.card := by exact_mod_cast hL.card_pos
  have hls : (L.card : ℝ) ≤ Fintype.card α := by exact_mod_cast Finset.card_le_univ L
  have hs : (0 : ℝ) < Fintype.card α := lt_of_lt_of_le hl hls
  set s : ℝ := (Fintype.card α : ℝ) with hs_def
  set l : ℝ := (L.card : ℝ) with hl_def
  set T : ℝ := ∑ a, w a with hT_def
  set A : ℝ := ∑ a ∈ L, w a with hA_def
  have hμ : 0 < T / s := div_pos hpos hs
  have hAT : A ≤ T := Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ L)
    (fun a _ _ => hw0 a)
  have hAW : A ≤ l * W := by
    have h := Finset.sum_le_sum (s := L) (f := w) (g := fun _ => W) (fun a _ => hwW a)
    simpa [hl_def] using h
  have hx0 : 1 < W / (T / s) := by rw [lt_div_iff₀ hμ]; linarith
  have hlogx0 : 0 < Real.log (W / (T / s)) := Real.log_pos hx0
  have hx1 : 1 ≤ s / l := by rw [le_div_iff₀ hl]; linarith
  have hlogx : 0 ≤ Real.log (s / l) := Real.log_nonneg hx1
  clear_value s l T A
  rw [div_mul_eq_mul_div, le_div_iff₀ hlogx0]
  by_cases hcase : s / l ≤ W / (T / s)
  · -- the list is longer than the support could be: its average is at most `T / l`
    have h1 : A / l - T / s ≤ T / s * (s / l - 1) := by
      have : T / s * (s / l - 1) = T / l - T / s := by
        field_simp
      rw [this]
      have := div_le_div_of_nonneg_right hAT hl.le
      linarith
    have h2 := sub_one_mul_log_le hx1 hcase
    have h3 : (W - T / s) = T / s * (W / (T / s) - 1) := by
      field_simp
    calc (A / l - T / s) * Real.log (W / (T / s))
        ≤ T / s * (s / l - 1) * Real.log (W / (T / s)) :=
          mul_le_mul_of_nonneg_right h1 hlogx0.le
      _ = T / s * ((s / l - 1) * Real.log (W / (T / s))) := by ring
      _ ≤ T / s * ((W / (T / s) - 1) * Real.log (s / l)) :=
          mul_le_mul_of_nonneg_left h2 hμ.le
      _ = (W - T / s) * Real.log (s / l) := by rw [h3]; ring
  · -- the list is short: its average is at most `W`
    have hcase' : W / (T / s) ≤ s / l := (not_le.mp hcase).le
    have h1 : A / l - T / s ≤ W - T / s := by
      have : A / l ≤ W := by rw [div_le_iff₀ hl]; linarith
      linarith
    have h2 : Real.log (W / (T / s)) ≤ Real.log (s / l) :=
      Real.log_le_log (by linarith) hcase'
    have hWμ : 0 ≤ W - T / s := by linarith
    calc (A / l - T / s) * Real.log (W / (T / s))
        ≤ (W - T / s) * Real.log (W / (T / s)) := mul_le_mul_of_nonneg_right h1 hlogx0.le
      _ ≤ (W - T / s) * Real.log (s / l) := mul_le_mul_of_nonneg_left h2 hWμ

/-- **Above `Q` no list pays.** For a prime `s ≥ 213070` every class kills at most one row. If
at most `1609` rows are left (the best covers at the 10% target), then for every list `L` of
classes the chance that `s` kills a row, for a member uniform in the list, exceeds the
unrestricted chance `|R| / s` by at most `0.207 · ln (s / |L|)`: at most `0.207` rows for each
nat the restriction costs. -/
theorem list_gain_above_Q {α : Type*} [Fintype α] [DecidableEq α] (R L : Finset α)
    (hs : 213070 ≤ Fintype.card α) (hR : R.card ≤ 1609) (hL : L.Nonempty) :
    ((R ∩ L).card : ℝ) / L.card - (R.card : ℝ) / Fintype.card α ≤
      0.207 * Real.log (Fintype.card α / L.card) := by
  have hl : (0 : ℝ) < L.card := by exact_mod_cast hL.card_pos
  have hls : (L.card : ℝ) ≤ Fintype.card α := by exact_mod_cast Finset.card_le_univ L
  have hs' : (213070 : ℝ) ≤ Fintype.card α := by exact_mod_cast hs
  have hs0 : (0 : ℝ) < Fintype.card α := by linarith
  have hlog : 0 ≤ Real.log (Fintype.card α / L.card) :=
    Real.log_nonneg (by rw [le_div_iff₀ hl]; linarith)
  rcases Finset.eq_empty_or_nonempty R with rfl | hRne
  · simpa using mul_nonneg (by norm_num : (0 : ℝ) ≤ 0.207) hlog
  have hr : (0 : ℝ) < R.card := by exact_mod_cast hRne.card_pos
  have hr' : (R.card : ℝ) ≤ 1609 := by exact_mod_cast hR
  -- weights: the indicator of `R`
  have hsumL : ∑ a ∈ L, (if a ∈ R then (1 : ℝ) else 0) = (R ∩ L).card := by
    rw [Finset.sum_ite_mem, Finset.inter_comm]
    simp
  have hsumU : ∑ a, (if a ∈ R then (1 : ℝ) else 0) = R.card := by
    rw [Finset.sum_ite_mem]
    simp
  have hμ1 : (R.card : ℝ) / Fintype.card α < 1 := by
    rw [div_lt_one hs0]; linarith
  have h := list_gain_le (fun a => if a ∈ R then (1 : ℝ) else 0) 1
    (fun a => by positivity) (fun a => by split_ifs <;> norm_num) L hL
    (by rw [hsumU]; exact hr) (by rw [hsumU]; exact hμ1)
  rw [hsumL, hsumU] at h
  refine h.trans (mul_le_mul_of_nonneg_right ?_ hlog)
  -- `(1 - μ) / ln (1/μ) ≤ 1 / ln 128 ≤ 0.207`
  have hμ0 : 0 < (R.card : ℝ) / Fintype.card α := div_pos hr hs0
  have h128 : (128 : ℝ) ≤ 1 / ((R.card : ℝ) / Fintype.card α) := by
    rw [le_div_iff₀ hμ0, ← mul_div_assoc, div_le_one hs0]
    linarith
  have hlog128 : (4.85 : ℝ) < Real.log 128 := by
    have h2 : Real.log 128 = 7 * Real.log 2 := by
      rw [show (128 : ℝ) = 2 ^ (7 : ℕ) by norm_num, Real.log_pow]
      norm_num
    rw [h2]
    have := Real.log_two_gt_d9
    linarith
  have hlogμ : (4.85 : ℝ) < Real.log (1 / ((R.card : ℝ) / Fintype.card α)) :=
    lt_of_lt_of_le hlog128 (Real.log_le_log (by norm_num) h128)
  rw [div_le_iff₀ (by linarith)]
  have : (0.207 : ℝ) * 4.85 ≤ 0.207 * Real.log (1 / ((R.card : ℝ) / Fintype.card α)) :=
    mul_le_mul_of_nonneg_left hlogμ.le (by norm_num)
  have h1 : (1 : ℝ) ≤ 0.207 * 4.85 := by norm_num
  linarith

end GoldbachGaps.Cap
