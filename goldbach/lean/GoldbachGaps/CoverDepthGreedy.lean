import GoldbachGaps.CoverDepth
import GoldbachGaps.Cover32971
import GoldbachGaps.Cover135511

/-!
# Lower bounds for the cover depth of 167 and of 429 moduli

The research session measured that the plainest rule for choosing residue classes (take the odd
primes in increasing order and give each its fullest class) reaches much further than the count
behind `CoverBound` allows for: about `0.7 · x ln² x` with the primes up to `x`
(`goldbach/sublinear/greedy_cover.txt` on branch `ccr-d4a17dd0-7uu03r`). `scripts/cover_depth/
greedy.py` recomputes that table with independent code, and one of its vectors is certified
here: the 167 odd primes up to `997` cover every odd prime below `32971`. The certificate is
`GoldbachGaps/Cover32971.lean` (divisibility only, checked by the kernel).

For comparison: `e^γ/(2 C₂) · x ln x` is `9,300` at `x = 997`, and `0.7 · x ln² x` is `33,300`.

A second vector, on the 429 odd primes up to `2999`, covers every odd prime below `135511`
(`GoldbachGaps/Cover135511.lean`); there `e^γ/(2 C₂) · x ln x` is `32,400`, a quarter of it.
-/

namespace GoldbachGaps.CoverDepth

/-- **The 167 odd primes up to `997` cover every odd prime below `32971`**: some residue vector
on them has every odd prime below `32971` in one of its classes. -/
theorem coversBelow_32971 : CoversBelow (oddPrimesBelow 998) 32971 :=
  coversBelow_of_complete_cover (R := 997) (by norm_num) Cover32971.complete_cover.2.1
    Cover32971.complete_cover.2.2.1

theorem length_oddPrimesBelow_998 : (oddPrimesBelow 998).length = 167 := by
  decide +kernel

/-- **The 429 odd primes up to `2999` cover every odd prime below `135511`.** -/
theorem coversBelow_135511 : CoversBelow (oddPrimesBelow 3000) 135511 :=
  coversBelow_of_complete_cover (R := 2999) (by norm_num) Cover135511.complete_cover.2.1
    Cover135511.complete_cover.2.2.1

set_option maxRecDepth 1000000 in
theorem length_oddPrimesBelow_3000 : (oddPrimesBelow 3000).length = 429 := by
  decide +kernel

end GoldbachGaps.CoverDepth
