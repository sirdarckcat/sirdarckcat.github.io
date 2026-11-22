import GoldbachGaps.Record150
import GoldbachGaps.Record199

/-!
# The two bounded record games, as kernel-checked theorems

These restate the certified records of `goldbach/SOK_GOLDBACH_GAPS.md` (threshold game
`T(100000)` and budget game `R(10^199)`) as closed statements about natural numbers.
Each is an upper or lower bound that a construction witnesses. Neither says the bound is
optimal.
-/

namespace GoldbachGaps

/-- Threshold game: there is an `N` below `10^150` whose least Goldbach summand exceeds
`100000`. (Witness: the 150-digit record, with least summand `104527`.) -/
theorem exists_lt_ten_pow_150_least_summand_gt :
    ∃ N < 10 ^ 150, ∃ g, IsLeastSummand N g ∧ 100000 < g :=
  ⟨Record150.N, Record150.N_lt, Record150.g, Record150.isLeastSummand, by decide⟩

/-- Budget game: there is an `N` below `10^199` whose least Goldbach summand is `119419`. -/
theorem exists_lt_ten_pow_199_least_summand_eq :
    ∃ N < 10 ^ 199, IsLeastSummand N 119419 :=
  ⟨Record199.N, Record199.N_lt, Record199.isLeastSummand⟩

end GoldbachGaps
