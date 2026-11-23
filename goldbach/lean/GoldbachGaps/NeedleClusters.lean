import GoldbachGaps.NeedlePairs

/-!
# Needles are not independent: four close pairs in the miniature

In the exhaustive miniature (`X = 10^9`, level `Q = 1000`) there are 303 needles: even numbers
`N` in `[1200, 10^9)` with `N - q` composite for every prime `q < 1000` (enumeration by
`scripts/mini_check/needles.c`; that there are no others is a computation, not a theorem here).
Independent uniform positions would give `303² / 2 · 2000 / 10^9 = 0.09` pairs closer than
`1000`. There are four, at distances 30, 30, 126 and 210, and they are theorems:
`needle_pairs_lt_1000`.

The reason is `IsNeedle.add_of_forall`: `N + 30` inherits 97 of its 168 rows from `N`
(`card_inherited_rows_30`), `N + 126` inherits 73 and `N + 210` inherits 87, so given that `N`
is a needle the neighbour has less than half of its rows left to pass. Counting the inherited
rows as certain, the same model that gives 0.09 gives 2.7 expected close pairs
(`scripts/mini_check/needle_pairs.txt`).
-/

namespace GoldbachGaps

open NeedlePairs

/-- **Four pairs of needles closer than `Q`.** Each of the eight numbers has `N - q` composite
for every prime `q < 1000`, by exhibited divisors. -/
theorem needle_pairs_lt_1000 :
    (IsNeedle 723090434 1000 ∧ IsNeedle (723090434 + 30) 1000) ∧
    (IsNeedle 792038384 1000 ∧ IsNeedle (792038384 + 30) 1000) ∧
    (IsNeedle 821176592 1000 ∧ IsNeedle (821176592 + 126) 1000) ∧
    (IsNeedle 793940696 1000 ∧ IsNeedle (793940696 + 210) 1000) :=
  ⟨⟨needle_723090434, needle_723090464⟩, ⟨needle_792038384, needle_792038414⟩,
    ⟨needle_821176592, needle_821176718⟩, ⟨needle_793940696, needle_793940906⟩⟩

/-- There are two needles at level `1000` below `10^9` at distance `30`. -/
theorem exists_needle_pair_30 :
    ∃ N : ℕ, N + 30 < 10 ^ 9 ∧ IsNeedle N 1000 ∧ IsNeedle (N + 30) 1000 :=
  ⟨792038384, by norm_num, needle_792038384, needle_792038414⟩

end GoldbachGaps
