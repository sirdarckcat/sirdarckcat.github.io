import GoldbachGaps.Record150
import GoldbachGaps.Record199
import GoldbachGaps.Record199_g125269
import GoldbachGaps.Record199_g133981
import GoldbachGaps.Record200_g146191
import GoldbachGaps.Record200_g157837
import GoldbachGaps.Record200_g158209
import GoldbachGaps.Cover15907
import GoldbachGaps.Cover16381
import GoldbachGaps.Cover16747
import GoldbachGaps.Cover16981

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

/-- **A bound by divisibility alone.** Some even `N < 10^200` has, for every prime `q < 15907`,
a divisor `r` of `N - q` with `2 ≤ r ≤ 463` and `r < N - q`; in particular no prime below
`15907` is a Goldbach summand of `N`. No primality or compositeness test enters the proof:
it is the complete cover on the 89 odd primes up to `463` found by the research session
(`Cover15907`, the best of its three covers of 2026-11-23, after `15787` and `15877`). The
records above need luck on top of their covers; this is what a cover alone certifies. -/
theorem exists_lt_ten_pow_200_complete_cover_15907 :
    ∃ N < 10 ^ 200, Even N ∧
      (∀ q < 15907, q.Prime → ∃ r, 2 ≤ r ∧ r ≤ 463 ∧ r < N - q ∧ r ∣ N - q) ∧
      ∀ q < 15907, ¬ IsSummand N q :=
  ⟨Cover15907.N, lt_trans Cover15907.N_lt (by norm_num), Cover15907.complete_cover.2.1,
    Cover15907.complete_cover.2.2.1, Cover15907.complete_cover.2.2.2⟩

/-- The same for a whole arithmetic progression: `21378978` numbers `N + t M` below `10^200`,
all even, all with every `N + t M - q` (`q < 15907` prime) divisible by some `r ≤ 463`. -/
theorem exists_progression_complete_cover_15907 :
    ∃ N M : ℕ, 0 < M ∧ ∀ t < 21378978, N + t * M < 10 ^ 200 ∧ Even (N + t * M) ∧
      (∀ q < 15907, q.Prime →
        ∃ r, 2 ≤ r ∧ r ≤ 463 ∧ r < N + t * M - q ∧ r ∣ N + t * M - q) ∧
      ∀ q < 15907, ¬ IsSummand (N + t * M) q := by
  refine ⟨Cover15907.N, Cover15907.M, ?_, fun t ht => ?_⟩
  · rw [Cover15907.M_eq]
    norm_num
  · obtain ⟨h1, h2, h3⟩ := Cover15907.complete_cover_family t
    exact ⟨Cover15907.family_lt t ht, h1, h2, h3⟩

/-! The bounds `15787` and `15877` of the two earlier covers, under the names they were
announced with. They are consequences of the cover to `15907` (the witness is that cover's
`N`, not the earlier ones). -/

theorem exists_lt_ten_pow_200_complete_cover_15877 :
    ∃ N < 10 ^ 200, Even N ∧
      (∀ q < 15877, q.Prime → ∃ r, 2 ≤ r ∧ r ≤ 463 ∧ r < N - q ∧ r ∣ N - q) ∧
      ∀ q < 15877, ¬ IsSummand N q := by
  obtain ⟨N, hN, he, h1, h2⟩ := exists_lt_ten_pow_200_complete_cover_15907
  exact ⟨N, hN, he, fun q hq => h1 q (by omega), fun q hq => h2 q (by omega)⟩

theorem exists_lt_ten_pow_200_complete_cover_15787 :
    ∃ N < 10 ^ 200, Even N ∧
      (∀ q < 15787, q.Prime → ∃ r, 2 ≤ r ∧ r ≤ 463 ∧ r < N - q ∧ r ∣ N - q) ∧
      ∀ q < 15787, ¬ IsSummand N q := by
  obtain ⟨N, hN, he, h1, h2⟩ := exists_lt_ten_pow_200_complete_cover_15907
  exact ⟨N, hN, he, fun q hq => h1 q (by omega), fun q hq => h2 q (by omega)⟩

theorem exists_progression_complete_cover_15877 :
    ∃ N M : ℕ, 0 < M ∧ ∀ t < 21378978, N + t * M < 10 ^ 200 ∧ Even (N + t * M) ∧
      (∀ q < 15877, q.Prime →
        ∃ r, 2 ≤ r ∧ r ≤ 463 ∧ r < N + t * M - q ∧ r ∣ N + t * M - q) ∧
      ∀ q < 15877, ¬ IsSummand (N + t * M) q := by
  obtain ⟨N, M, hM, h⟩ := exists_progression_complete_cover_15907
  refine ⟨N, M, hM, fun t ht => ?_⟩
  obtain ⟨h0, he, h1, h2⟩ := h t ht
  exact ⟨h0, he, fun q hq => h1 q (by omega), fun q hq => h2 q (by omega)⟩

theorem exists_progression_complete_cover_15787 :
    ∃ N M : ℕ, 0 < M ∧ ∀ t < 21378977, N + t * M < 10 ^ 200 ∧ Even (N + t * M) ∧
      (∀ q < 15787, q.Prime →
        ∃ r, 2 ≤ r ∧ r ≤ 463 ∧ r < N + t * M - q ∧ r ∣ N + t * M - q) ∧
      ∀ q < 15787, ¬ IsSummand (N + t * M) q := by
  obtain ⟨N, M, hM, h⟩ := exists_progression_complete_cover_15907
  refine ⟨N, M, hM, fun t ht => ?_⟩
  obtain ⟨h0, he, h1, h2⟩ := h t (by omega)
  exact ⟨h0, he, fun q hq => h1 q (by omega), fun q hq => h2 q (by omega)⟩

/-! ### Covers on more primes

Each prime added to the covering set multiplies the modulus by more than `463`, so beyond 89
primes the progression of a cover has few members below `10^200` (95 on 91 primes) or, from
92 primes on, less than one on average: a cover below `10^200` then exists only for a
fraction of the choices of residues, and the research session finds one by enumerating them
(`goldbach/sublinear/complete_cover_16381_91primes.txt`, `…_16747_92primes.txt` and
`…_16981_93primes.txt`, branch `ccr-d4a17dd0-7uu03r`, commit `10648a4`). The bound proved
by divisibility alone grows with the set: `15907` on the odd primes up to `463`, `16381` up
to `479`, `16747` up to `487`, `16981` up to `491`. -/

/-- **The bound by divisibility alone, on 93 primes.** Some even `N < 10^200` has, for every
prime `q < 16981`, a divisor `r` of `N - q` with `2 ≤ r ≤ 491` and `r < N - q`; in particular
no prime below `16981` is a Goldbach summand of `N`. Its progression has no other member below
`10^200` (`Cover16981.family_ge`). -/
theorem exists_lt_ten_pow_200_complete_cover_16981 :
    ∃ N < 10 ^ 200, Even N ∧
      (∀ q < 16981, q.Prime → ∃ r, 2 ≤ r ∧ r ≤ 491 ∧ r < N - q ∧ r ∣ N - q) ∧
      ∀ q < 16981, ¬ IsSummand N q :=
  ⟨Cover16981.N, Cover16981.N_lt, Cover16981.complete_cover.2.1,
    Cover16981.complete_cover.2.2.1, Cover16981.complete_cover.2.2.2⟩

/-- The same on 92 primes: every `N - q` with `q < 16747` prime is divisible by some
`r ≤ 487`. -/
theorem exists_lt_ten_pow_200_complete_cover_16747 :
    ∃ N < 10 ^ 200, Even N ∧
      (∀ q < 16747, q.Prime → ∃ r, 2 ≤ r ∧ r ≤ 487 ∧ r < N - q ∧ r ∣ N - q) ∧
      ∀ q < 16747, ¬ IsSummand N q :=
  ⟨Cover16747.N, Cover16747.N_lt, Cover16747.complete_cover.2.1,
    Cover16747.complete_cover.2.2.1, Cover16747.complete_cover.2.2.2⟩

/-- The same on 91 primes: every `N - q` with `q < 16381` prime is divisible by some
`r ≤ 479`. -/
theorem exists_lt_ten_pow_200_complete_cover_16381 :
    ∃ N < 10 ^ 200, Even N ∧
      (∀ q < 16381, q.Prime → ∃ r, 2 ≤ r ∧ r ≤ 479 ∧ r < N - q ∧ r ∣ N - q) ∧
      ∀ q < 16381, ¬ IsSummand N q :=
  ⟨Cover16381.N, lt_trans Cover16381.N_lt (by norm_num), Cover16381.complete_cover.2.1,
    Cover16381.complete_cover.2.2.1, Cover16381.complete_cover.2.2.2⟩

/-- On 91 primes the cover is still a progression with several members below `10^200`:
`95` numbers `N + t M`, all even, all with every `N + t M - q` (`q < 16381` prime) divisible
by some `r ≤ 479`. The next member is not below `10^200` (`Cover16381.family_ge`). -/
theorem exists_progression_complete_cover_16381 :
    ∃ N M : ℕ, 0 < M ∧ ∀ t < 95, N + t * M < 10 ^ 200 ∧ Even (N + t * M) ∧
      (∀ q < 16381, q.Prime →
        ∃ r, 2 ≤ r ∧ r ≤ 479 ∧ r < N + t * M - q ∧ r ∣ N + t * M - q) ∧
      ∀ q < 16381, ¬ IsSummand (N + t * M) q := by
  refine ⟨Cover16381.N, Cover16381.M, ?_, fun t ht => ?_⟩
  · rw [Cover16381.M_eq]
    norm_num
  · obtain ⟨h1, h2, h3⟩ := Cover16381.complete_cover_family t
    exact ⟨Cover16381.family_lt t ht, h1, h2, h3⟩

end GoldbachGaps
