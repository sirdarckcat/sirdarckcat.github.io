import GoldbachGaps.CoverDepth
import GoldbachGaps.Cover1471
import GoldbachGaps.Cover4909
import GoldbachGaps.Cover8311
import GoldbachGaps.Cover32971
import GoldbachGaps.Cover40111
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

On the 167 moduli the research session's sampler does better than the greedy rule: its vector
covers every odd prime below `40111` (`GoldbachGaps/Cover40111.lean`, `coversBelow_40111`).
Three more of its vectors are certified the same way: the odd primes up to `97`, `199` and
`293` (24, 45 and 61 moduli) cover every odd prime below `1471`, `4909` and `8311`.
-/

namespace GoldbachGaps.CoverDepth

/-- A complete cover in the sense of `GoldbachGaps/CompleteCover.lean`, read as a cover by its
odd moduli: the classes are those of `N` itself. -/
theorem coversBelow_of_coveredIn {N Q : ℕ} {mods : List ℕ} (hE : Even N) (hQ : Q ≤ N)
    (h : CoveredIn N mods 0 Q) : CoversBelow (mods.filter fun r => r != 2) Q := by
  refine ⟨fun _ => N, fun q hq h2 hlt => ?_⟩
  obtain ⟨r, hr, hdvd⟩ := h q (Nat.zero_le q) hlt hq
  have hr2 : r ≠ 2 := by
    rintro rfl
    have hqodd := hq.eq_two_or_odd.resolve_left h2
    obtain ⟨k, hk⟩ := hE
    omega
  exact ⟨r, List.mem_filter.mpr ⟨hr, by simpa using hr2⟩,
    (Nat.modEq_iff_dvd' (show q ≤ N by omega)).mpr hdvd⟩

/-- The 24 odd primes up to `97` cover every odd prime below `1471` (the research session's
vector). -/
theorem coversBelow_1471 : CoversBelow (oddPrimesBelow 98) 1471 :=
  coversBelow_of_complete_cover (R := 97) (by norm_num) Cover1471.complete_cover.2.1
    Cover1471.complete_cover.2.2.1

/-- The 45 odd primes up to `199` cover every odd prime below `4909` (the research session's
vector). -/
theorem coversBelow_4909 : CoversBelow (oddPrimesBelow 200) 4909 :=
  coversBelow_of_complete_cover (R := 199) (by norm_num) Cover4909.complete_cover.2.1
    Cover4909.complete_cover.2.2.1

/-- The 61 odd primes up to `293` cover every odd prime below `8311` (the research session's
vector). -/
theorem coversBelow_8311 : CoversBelow (oddPrimesBelow 294) 8311 :=
  coversBelow_of_complete_cover (R := 293) (by norm_num) Cover8311.complete_cover.2.1
    Cover8311.complete_cover.2.2.1

theorem length_oddPrimesBelow_98 : (oddPrimesBelow 98).length = 24 := by
  decide +kernel

theorem length_oddPrimesBelow_200 : (oddPrimesBelow 200).length = 45 := by
  decide +kernel

theorem length_oddPrimesBelow_294 : (oddPrimesBelow 294).length = 61 := by
  decide +kernel

/-- **The 167 odd primes up to `997` cover every odd prime below `32971`**: some residue vector
on them has every odd prime below `32971` in one of its classes. -/
theorem coversBelow_32971 : CoversBelow (oddPrimesBelow 998) 32971 :=
  coversBelow_of_complete_cover (R := 997) (by norm_num) Cover32971.complete_cover.2.1
    Cover32971.complete_cover.2.2.1

theorem length_oddPrimesBelow_998 : (oddPrimesBelow 998).length = 167 := by
  decide +kernel

/-- **The 167 odd primes up to `997` cover every odd prime below `40111`** (the research
session's vector). -/
theorem coversBelow_40111 : CoversBelow (oddPrimesBelow 998) 40111 :=
  coversBelow_of_complete_cover (R := 997) (by norm_num) Cover40111.complete_cover.2.1
    Cover40111.complete_cover.2.2.1

/-- **The 429 odd primes up to `2999` cover every odd prime below `135511`.** -/
theorem coversBelow_135511 : CoversBelow (oddPrimesBelow 3000) 135511 :=
  coversBelow_of_complete_cover (R := 2999) (by norm_num) Cover135511.complete_cover.2.1
    Cover135511.complete_cover.2.2.1

set_option maxRecDepth 1000000 in
theorem length_oddPrimesBelow_3000 : (oddPrimesBelow 3000).length = 429 := by
  decide +kernel

end GoldbachGaps.CoverDepth
