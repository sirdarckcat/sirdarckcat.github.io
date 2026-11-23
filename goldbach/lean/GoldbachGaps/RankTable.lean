import GoldbachGaps.RankPatterns
import GoldbachGaps.RankData

/-!
# The record holders up to `10^12` and the pairs that share a prime

`RankData.recordTable` lists the 42 even numbers up to `10^12` whose least Goldbach summand
exceeds that of every smaller even number, with the summand; `RankData.recordTable_spec` proves
each value (`N - q` composite for every prime `q < g` by an exhibited divisor, `g` and `N - g`
prime). That no smaller number does better is the scan `scripts/rank_records/lgs_scan.c`, a
computation and not a theorem here; the list agrees with terms 2 to 43 of OEIS A025018 and
A025019 (b-files).

Instances of the shift law of `RankPatterns` among the numbers that arrive in the ten largest:

* `shift_pairs`: four pairs `(N, g)`, `(N + h, g + h)` with the same prime `N - g` behind both;
* `records_42_apart`: the consecutive records `194428` and `194470`, with summands `359` and
  `383`, are `42` apart; three more arrivals lie within `126` of them (`cluster_194`).
-/

namespace GoldbachGaps

open RankData

/-- **Pairs that share a prime.** In each pair the second number is the first plus `h`, the
second least summand is the first plus `h`, and so `N - g(N)` is the same prime. -/
theorem shift_pairs :
    (IsLeastSummand 480878 337 ∧ IsLeastSummand (480878 + 30) (337 + 30)) ∧
    (IsLeastSummand 743636 367 ∧ IsLeastSummand (743636 + 30) (367 + 30)) ∧
    (IsLeastSummand 3506954 547 ∧ IsLeastSummand (3506954 + 30) (547 + 30)) ∧
    (IsLeastSummand 194344 251 ∧ IsLeastSummand (194344 + 42) (251 + 42)) :=
  ⟨⟨leastSummand_480878, leastSummand_480908⟩, ⟨leastSummand_743636, leastSummand_743666⟩,
    ⟨leastSummand_3506954, leastSummand_3506984⟩, ⟨leastSummand_194344, leastSummand_194386⟩⟩

/-- Two consecutive records `42` apart. -/
theorem records_42_apart : IsLeastSummand 194428 359 ∧ IsLeastSummand (194428 + 42) 383 :=
  ⟨leastSummand_194428, leastSummand_194470⟩

/-- Five numbers within `126` of each other, each among the ten largest least summands when it
appears: two records, and arrivals at ranks 4, 6 and 10. -/
theorem cluster_194 :
    IsLeastSummand 194344 251 ∧ IsLeastSummand 194386 293 ∧ IsLeastSummand 194428 359 ∧
      IsLeastSummand 194452 311 ∧ IsLeastSummand 194470 383 :=
  ⟨leastSummand_194344, leastSummand_194386, leastSummand_194428, leastSummand_194452,
    leastSummand_194470⟩

/-- On the 42 record holders the exact residue relation is visible: none is divisible by `3`
beyond `30`, and then `3` divides `N + g(N)`. This is `IsSummand.three_dvd_add`, checked here
on the table. -/
theorem recordTable_three_dvd :
    ∀ x ∈ recordTable, 30 < x.1 → ¬ 3 ∣ x.1 ∧ 3 ∣ x.1 + x.2 := by
  decide

end GoldbachGaps
