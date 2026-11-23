import GoldbachGaps.Record150
import GoldbachGaps.Record199
import GoldbachGaps.Record199_g125269
import GoldbachGaps.Record199_g133981
import GoldbachGaps.Record200_g146191
import GoldbachGaps.Record200_g157837
import GoldbachGaps.Record200_g158209
import GoldbachGaps.Cover15787

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

/-- Budget game, record of 2026-11-22 late (campaign at `Q = 140000`, variant
`r200_q140k_c_v77`, `k = 3101585871`): there is an `N` below `10^200` whose least Goldbach
summand is `146191`. -/
theorem exists_lt_ten_pow_200_least_summand_146191 :
    ∃ N < 10 ^ 200, IsLeastSummand N 146191 :=
  ⟨Record200_g146191.N, Record200_g146191.N_lt, Record200_g146191.isLeastSummand⟩

/-- Budget game, record of 2026-11-23 02:08 UTC (campaign at `Q = 150000`, variant
`pt_q150k_t528`, `k = 4224399187`): there is an `N` below `10^200` whose least Goldbach
summand is `157837`. -/
theorem exists_lt_ten_pow_200_least_summand_157837 :
    ∃ N < 10 ^ 200, IsLeastSummand N 157837 :=
  ⟨Record200_g157837.N, Record200_g157837.N_lt, Record200_g157837.isLeastSummand⟩

/-- Budget game, the standing record of 2026-11-23 12:48 UTC, the first on 89 covering
moduli (a near-miss of a `Q = 170000` design, vector `q170000_m89_p2c00019_v545`,
`k = 10814286`): there is an `N` below `10^200` whose least Goldbach summand is `158209`. -/
theorem exists_lt_ten_pow_200_least_summand_158209 :
    ∃ N < 10 ^ 200, IsLeastSummand N 158209 :=
  ⟨Record200_g158209.N, Record200_g158209.N_lt, Record200_g158209.isLeastSummand⟩

/-- **A bound by divisibility alone.** Some even `N < 10^200` has, for every prime `q < 15787`,
a divisor `r` of `N - q` with `2 ≤ r ≤ 463` and `r < N - q`; in particular no prime below
`15787` is a Goldbach summand of `N`. No primality or compositeness test enters the proof:
it is the complete cover on the 89 odd primes up to `463` found by the research session
(`Cover15787`). The record `157837` above needs luck on top of its cover; this is what the
cover alone certifies. -/
theorem exists_lt_ten_pow_200_complete_cover_15787 :
    ∃ N < 10 ^ 200, Even N ∧
      (∀ q < 15787, q.Prime → ∃ r, 2 ≤ r ∧ r ≤ 463 ∧ r < N - q ∧ r ∣ N - q) ∧
      ∀ q < 15787, ¬ IsSummand N q :=
  ⟨Cover15787.N, lt_trans Cover15787.N_lt (by norm_num), Cover15787.complete_cover.2.1,
    Cover15787.complete_cover.2.2.1, Cover15787.complete_cover.2.2.2⟩

/-- The same for a whole arithmetic progression: `21378977` numbers `N + t M` below `10^200`,
all even, all with every `N + t M - q` (`q < 15787` prime) divisible by some `r ≤ 463`. -/
theorem exists_progression_complete_cover_15787 :
    ∃ N M : ℕ, 0 < M ∧ ∀ t < 21378977, N + t * M < 10 ^ 200 ∧ Even (N + t * M) ∧
      (∀ q < 15787, q.Prime →
        ∃ r, 2 ≤ r ∧ r ≤ 463 ∧ r < N + t * M - q ∧ r ∣ N + t * M - q) ∧
      ∀ q < 15787, ¬ IsSummand (N + t * M) q := by
  refine ⟨Cover15787.N, Cover15787.M, ?_, fun t ht => ?_⟩
  · rw [Cover15787.M_eq]
    norm_num
  · obtain ⟨h1, h2, h3⟩ := Cover15787.complete_cover_family t
    exact ⟨Cover15787.family_lt t ht, h1, h2, h3⟩

end GoldbachGaps
