import GoldbachGaps.RecordWalk

/-!
The N generator of `GoldbachGaps/RecordWalk.lean`, run: it walks the even numbers below the bound
and prints those whose least Goldbach summand beats every earlier one (the terms of A025018).

    lake env lean scripts/record_gen/Walk.lean        (from goldbach/lean; a few seconds)

`walk` is the definition the theorems are about and asks its question of one `N` at a time, by
trial division; for large bounds use `ngen.c` in this directory (the same rule, 64 values of `N`
per step) or `records` (`Run.lean`).
-/

open GoldbachGaps GoldbachGaps.RecordWalk

-- the terms below 100,000
#eval walk 100000

-- the same, each with the summand that made it a term
#eval (walk 100000).map fun N => (N, lgs N)
