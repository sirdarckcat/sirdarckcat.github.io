import GoldbachGaps.RecordGen

/-!
# The generator for A025018, run by the kernel

`RecordGen.records X` is proved to list the terms of A025018 / A025019 below `X`
(`RecordGen.mem_records`). Here the kernel itself evaluates `records (2^20)`, so the first 21
terms are a theorem obtained by running the generator, with no input from any scan.

Larger bounds are a matter of time and memory only: the kernel keeps every intermediate number
of the prime sieve, about `0.6` GB at `2^20` and several times that at `2^22`. For more terms
evaluate `records X` outside the kernel (`scripts/record_gen/Run.lean`), or use
`RankSieve.isRecordHolder_iff`, which proves the table below `2^25` from certificates.
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

end GoldbachGaps.RecordGen
