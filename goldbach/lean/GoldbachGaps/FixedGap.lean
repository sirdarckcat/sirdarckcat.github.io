import GoldbachGaps.Gap200k_400digit_g200293
import GoldbachGaps.Gap200k_400digit_g206593
import GoldbachGaps.Gap200k_347digit_g216289
import GoldbachGaps.Gap1M_2196digit_g1001491

/-!
# The fixed-gap game: few digits for a given bound

The record game of `GoldbachGaps/Records.lean` fixes the size of `N` and asks for the largest
least Goldbach summand. This game fixes the bound and asks for the smallest `N`: an even `N`
with as few digits as possible such that `N - q` is composite for every prime `q` below the
bound, so that the least Goldbach summand of `N` is at least the bound.

Each statement below is the negative side only. For every prime `q` below the bound the kernel
checks that `N - q` is composite, by a covering modulus dividing it or by a failed base-2 Fermat
test (`GoldbachGaps/Desert.lean`, `GoldbachGaps/DesertWitness.lean`). No primality proof is
involved, so the exact least summand of `N` (a probable prime at the bound stated) is not part
of any theorem here.

| bound | digits of `N` | proved: no summand below | source |
|---|---|---|---|
| 200,000 | 400 | 200,293 | uarch session, `goldbach/records/g200k_400digit_g200293` |
| 200,000 | 400 | 206,593 | uarch session, `goldbach/records/g200k_400digit_g206593` |
| 200,000 | 347 | 216,289 | uarch session, `goldbach/records/g200k_347digit_g216289` |
| 1,000,000 | 2,196 | 1,001,491 | Opus session, `goldbach/g_million/record_2196digit` |

(The uarch session's are on branch `ccr-b8c25887-i6tn9f`, the first two at `8bbbc2d`, the third at
`05a396b`; each was recomputed from `N` alone by the research session and again here before the
certificate was generated. The Opus session's is on branch `ccr-c6e00296-3g7fp9` at `71172d4`,
checked here from `N` and the cover alone; its certificate is in the witness form, in 31 parts of
four blocks, and uses the record's divisors of `N - q` for 1,600 rows that no modulus strikes; 977
rows are left to the base-2 Fermat test.)
-/

namespace GoldbachGaps

/-- **A 400-digit even `N` with `N - q` composite for every prime `q < 200293`**: its least
Goldbach summand is at least `200293`. -/
theorem exists_400_digit_no_summand_below_200293 :
    ∃ N, 10 ^ 399 ≤ N ∧ N < 10 ^ 400 ∧ Even N ∧ ∀ q, q.Prime → q < 200293 → ¬ (N - q).Prime :=
  ⟨Gap200k_400digit_g200293.N, Gap200k_400digit_g200293.le_N, Gap200k_400digit_g200293.N_lt,
    Gap200k_400digit_g200293.N_even, Gap200k_400digit_g200293.not_prime_sub⟩

/-- **A 400-digit even `N` with `N - q` composite for every prime `q < 206593`**: its least
Goldbach summand is at least `206593`. -/
theorem exists_400_digit_no_summand_below_206593 :
    ∃ N, 10 ^ 399 ≤ N ∧ N < 10 ^ 400 ∧ Even N ∧ ∀ q, q.Prime → q < 206593 → ¬ (N - q).Prime :=
  ⟨Gap200k_400digit_g206593.N, Gap200k_400digit_g206593.le_N, Gap200k_400digit_g206593.N_lt,
    Gap200k_400digit_g206593.N_even, Gap200k_400digit_g206593.not_prime_sub⟩

/-- **A 347-digit even `N` with `N - q` composite for every prime `q < 216289`**: its least
Goldbach summand is at least `216289`. -/
theorem exists_347_digit_no_summand_below_216289 :
    ∃ N, 10 ^ 346 ≤ N ∧ N < 10 ^ 347 ∧ Even N ∧ ∀ q, q.Prime → q < 216289 → ¬ (N - q).Prime :=
  ⟨Gap200k_347digit_g216289.N, Gap200k_347digit_g216289.le_N, Gap200k_347digit_g216289.N_lt,
    Gap200k_347digit_g216289.N_even, Gap200k_347digit_g216289.not_prime_sub⟩

/-- The bound of the game at 347 digits: some even `N` below `10^347` has no Goldbach summand below
`200000`. -/
theorem exists_lt_ten_pow_347_no_summand_below_200000 :
    ∃ N < 10 ^ 347, Even N ∧ ∀ q, q.Prime → q < 200000 → ¬ (N - q).Prime :=
  ⟨Gap200k_347digit_g216289.N, Gap200k_347digit_g216289.N_lt, Gap200k_347digit_g216289.N_even,
    fun q hq hlt => Gap200k_347digit_g216289.not_prime_sub q hq (by unfold Gap200k_347digit_g216289.Q; omega)⟩

/-- **A 2,196-digit even `N` with `N - q` composite for every prime `q < 1001491`**: its least
Goldbach summand is at least `1001491`. -/
theorem exists_2196_digit_no_summand_below_1001491 :
    ∃ N, 10 ^ 2195 ≤ N ∧ N < 10 ^ 2196 ∧ Even N ∧ ∀ q, q.Prime → q < 1001491 → ¬ (N - q).Prime :=
  ⟨Gap1M_2196digit_g1001491.N, Gap1M_2196digit_g1001491.le_N, Gap1M_2196digit_g1001491.N_lt,
    Gap1M_2196digit_g1001491.N_even, Gap1M_2196digit_g1001491.not_prime_sub⟩

/-- The bound of the game at one million: some even `N` below `10^2196` has no Goldbach summand
below `1000000`. -/
theorem exists_lt_ten_pow_2196_no_summand_below_1000000 :
    ∃ N < 10 ^ 2196, Even N ∧ ∀ q, q.Prime → q < 1000000 → ¬ (N - q).Prime :=
  ⟨Gap1M_2196digit_g1001491.N, Gap1M_2196digit_g1001491.N_lt, Gap1M_2196digit_g1001491.N_even,
    fun q hq hlt => Gap1M_2196digit_g1001491.not_prime_sub q hq (by unfold Gap1M_2196digit_g1001491.Q; omega)⟩

/-- The bound of the game: some even `N` below `10^400` has no Goldbach summand below
`200000`. -/
theorem exists_lt_ten_pow_400_no_summand_below_200000 :
    ∃ N < 10 ^ 400, Even N ∧ ∀ q, q.Prime → q < 200000 → ¬ (N - q).Prime :=
  ⟨Gap200k_400digit_g200293.N, Gap200k_400digit_g200293.N_lt, Gap200k_400digit_g200293.N_even,
    fun q hq hlt => Gap200k_400digit_g200293.not_prime_sub q hq (by unfold Gap200k_400digit_g200293.Q; omega)⟩

end GoldbachGaps
