import GoldbachGaps.RecordGen

/-!
Run the generator for A025018 / A025019 outside the kernel:

    lake env lean scripts/record_gen/Run.lean

`RecordGen.mem_records` proves that `records X` is exactly the list of terms below `X`, for
every `X`; this file only evaluates it. Change the exponent for more terms (2^25: 27 terms in
about 22 s; 2^27: 30 terms in 3 min 12 s; the time grows like X^1.5, the prime sieve being the
slow part).
-/

open GoldbachGaps.RecordGen

#eval records (2 ^ 25)
