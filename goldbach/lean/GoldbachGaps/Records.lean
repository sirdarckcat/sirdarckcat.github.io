import GoldbachGaps.Record150
import GoldbachGaps.Record199
import GoldbachGaps.Record199_g125269
import GoldbachGaps.Record199_g133981
import GoldbachGaps.Record200_g146191

/-!
# The bounded record games, as kernel-checked theorems

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

/-- Budget game, record of 2026-11-22 (campaign 3 on a GPU, variant `r200b_q122k_v367`):
there is an `N` below `10^199` whose least Goldbach summand is `125269`. -/
theorem exists_lt_ten_pow_199_least_summand_125269 :
    ∃ N < 10 ^ 199, IsLeastSummand N 125269 :=
  ⟨Record199_g125269.N, Record199_g125269.N_lt, Record199_g125269.isLeastSummand⟩

/-- Budget game, the standing record of 2026-11-22 (variant `r200b_q122k_w175`): there is an
`N` below `10^199` whose least Goldbach summand is `133981`. -/
theorem exists_lt_ten_pow_199_least_summand_133981 :
    ∃ N < 10 ^ 199, IsLeastSummand N 133981 :=
  ⟨Record199_g133981.N, Record199_g133981.N_lt, Record199_g133981.isLeastSummand⟩

/-- Budget game, the standing record of 2026-11-22 late (campaign at `Q = 140000`, variant
`r200_q140k_c_v77`, `k = 3101585871`): there is an `N` below `10^200` whose least Goldbach
summand is `146191`. -/
theorem exists_lt_ten_pow_200_least_summand_146191 :
    ∃ N < 10 ^ 200, IsLeastSummand N 146191 :=
  ⟨Record200_g146191.N, Record200_g146191.N_lt, Record200_g146191.isLeastSummand⟩

end GoldbachGaps
