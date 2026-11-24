import GoldbachGaps.RecordGen

/-!
# The generator for A025018, run by the kernel

`RecordGen.records X` is proved to list the terms of A025018 / A025019 below `X`
(`RecordGen.mem_records`). Here the kernel itself evaluates `records (2^20)`, so the first 21
terms are a theorem obtained by running the generator, with no input from any scan.

Larger bounds are a matter of time and memory only: the kernel keeps every intermediate number
of the prime sieve, about `0.5` GB at `2^20` and `2.3` GB at `2^22` (where the same statement
with 24 terms checks in 6 s). For more terms evaluate `records X` outside the kernel
(`scripts/record_gen/Run.lean`), or use `RankSieve.isRecordHolder_iff`, which proves the table
below `2^25` from certificates.
-/

namespace GoldbachGaps.RecordGen

/-- The first 21 terms of A025018 with their least summands (A025019). -/
def terms20 : List (ℕ × ℕ) :=
  [(4, 2), (6, 3), (12, 5), (30, 7), (98, 19), (220, 23), (308, 31), (556, 47), (992, 73),
   (2642, 103), (5372, 139), (7426, 173), (43532, 211), (54244, 233), (63274, 293),
   (113672, 313), (128168, 331), (194428, 359), (194470, 383), (413572, 389), (503222, 523)]

set_option maxRecDepth 1000000 in
/-- **The generator, run by the kernel up to `2^20`.** -/
theorem records_two_pow_20 : records (2 ^ 20) = terms20 := by decide +kernel

/-- **A025018 / A025019 below `2^20`.** `(N, g)` is a term with `N < 2^20` exactly when it is
one of the 21 pairs of `terms20`. -/
theorem isRecord_iff_mem_terms20 {N g : ℕ} (hN : N < 2 ^ 20) :
    IsRecord N g ↔ (N, g) ∈ terms20 := by
  rw [← records_two_pow_20, mem_records]
  exact ⟨fun h => ⟨hN, h⟩, fun h => h.2⟩

/-! ### The simpler rules are wrong, provably

`scripts/record_gen/ladder.py` generates the first terms by four simpler rules; each is right
for one term more than the previous and then leaves the sequence. What each of them produces
at that point is not a term. -/

/-- Rule 1 (the next even number) is right for 2 terms and then says `8`. -/
theorem not_isRecord_8 (g : ℕ) : ¬ IsRecord 8 g := by
  intro h
  rw [isRecord_iff_mem_terms20 (by norm_num)] at h
  simp [terms20] at h

/-- Rule 2 (the next even `N` with `N - (last value)` composite) is right for 3 terms and then
says `14`. -/
theorem not_isRecord_14 (g : ℕ) : ¬ IsRecord 14 g := by
  intro h
  rw [isRecord_iff_mem_terms20 (by norm_num)] at h
  simp [terms20] at h

/-- Rule 3 (dodge every earlier value; the value is the next prime) is right for 4 terms, finds
`98`, and says its value is `11`. It is `19`: the strikers `11`, `13`, `17` miss. -/
theorem isRecord_98 : IsRecord 98 19 ∧ ¬ IsRecord 98 11 := by
  constructor
  · rw [isRecord_iff_mem_terms20 (by norm_num)]
    decide
  · intro h
    rw [isRecord_iff_mem_terms20 (by norm_num)] at h
    simp [terms20] at h

/-- Rule 4 (as rule 3 with the right value, but only the earlier values strike) is right for 5
terms and then says `124`: the strikers that missed `98` must keep striking, and `11` hits
`124`. The sixth term is `220`. -/
theorem not_isRecord_124 (g : ℕ) : ¬ IsRecord 124 g := by
  intro h
  rw [isRecord_iff_mem_terms20 (by norm_num)] at h
  simp [terms20] at h

end GoldbachGaps.RecordGen
