import GoldbachGaps.CoverCount
import GoldbachGaps.CoverDepthRun
import GoldbachGaps.CoverDepthGreedy
import GoldbachGaps.Cover40459

/-!
# The number of complete covers: what the certified covers say

`GoldbachGaps/CoverCount.lean` defines `g0 x Q`, the number of class vectors modulo the odd primes
up to `x` that cover every odd prime below `Q`, and proves `prod_le_g0`: if `g0 x' Q` is positive
then `g0 x Q` is at least the product of the odd primes in `(x', x]`, for every `x ≥ x'`. Every
certified cover of the package therefore gives a lower bound for `g0` on all larger sets of
moduli. In logarithms, with `θ` Chebyshev's function:

    ln g0(x, Q) ≥ θ(x) - θ(x')     for all x ≥ x',

for the pairs `(x', Q)` = `(97, 1471)`, `(199, 4909)`, `(293, 8311)`, `(463, 15907)`,
`(479, 16381)`, `(487, 16747)`, `(491, 16981)`, `(997, 40111)`, `(997, 40459)`,
`(2999, 135511)` and `(9999, 614101)` (`g0_pos_*`, `prod_le_g0_*`; in the last pair the moduli are the odd primes below
`10000`, the largest of which is `9973`). These are the first proved lower bounds for `g0` beyond
positivity. They are not the law the research session measures, `ln g0(x, Q) ≈ θ(x) - Q/ln² x`:
with the least `x'` that covers, the law at `x = x'` reads `θ(x') = Q/ln² x'`, so for larger `x`
the law's loss `Q/ln² x` is smaller than the bound `θ(x')` by the factor `ln² x / ln² x'`.

The exact depths say where the count ends: `g0_29_181`, with nine moduli `g0(29, 181) > 0` and
`g0(29, 182) = 0`. For three moduli the count itself is checked: `g0_7_19`, exactly one class
vector modulo `3, 5, 7` covers every odd prime below `19`.
-/

namespace GoldbachGaps.CoverCount

open Finset GoldbachGaps.CoverDepth

/-- A cover on the list `oddPrimesBelow (x + 1)` makes `g0 x Q` positive. -/
theorem g0_pos_of_coversBelow {x Q : ℕ} (hx : x + 1 ≤ 5929)
    (h : CoversBelow (oddPrimesBelow (x + 1)) Q) : 0 < g0 x Q :=
  (g0_pos_iff (fun _ => mem_oddPrimesBelow hx) Q).2 h

theorem g0_pos_97_1471 : 0 < g0 97 1471 := g0_pos_of_coversBelow (by norm_num) coversBelow_1471
theorem g0_pos_199_4909 : 0 < g0 199 4909 := g0_pos_of_coversBelow (by norm_num) coversBelow_4909
theorem g0_pos_293_8311 : 0 < g0 293 8311 := g0_pos_of_coversBelow (by norm_num) coversBelow_8311
theorem g0_pos_463_15907 : 0 < g0 463 15907 :=
  g0_pos_of_coversBelow (by norm_num) coversBelow_15907
theorem g0_pos_479_16381 : 0 < g0 479 16381 :=
  g0_pos_of_coversBelow (by norm_num) coversBelow_16381
theorem g0_pos_487_16747 : 0 < g0 487 16747 :=
  g0_pos_of_coversBelow (by norm_num) coversBelow_16747
theorem g0_pos_491_16981 : 0 < g0 491 16981 :=
  g0_pos_of_coversBelow (by norm_num) coversBelow_16981
theorem g0_pos_997_40111 : 0 < g0 997 40111 :=
  g0_pos_of_coversBelow (by norm_num) coversBelow_40111
theorem g0_pos_2999_135511 : 0 < g0 2999 135511 :=
  g0_pos_of_coversBelow (by norm_num) coversBelow_135511

/-- The 1,228 odd primes below `10000` (the largest is `9973`) can cover every odd prime below
`614101`. -/
theorem g0_pos_9999_614101 : 0 < g0 9999 614101 :=
  (g0_pos_iff (fun _ => mem_mods9973) 614101).2 coversBelow_614101

/-- `ln g0(x, 1471) ≥ θ(x) - θ(97)` for every `x ≥ 97`. -/
theorem prod_le_g0_1471 {x : ℕ} (hx : 97 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 98, r ≤ g0 x 1471 :=
  prod_le_g0 hx g0_pos_97_1471

/-- `ln g0(x, 4909) ≥ θ(x) - θ(199)` for every `x ≥ 199`. -/
theorem prod_le_g0_4909 {x : ℕ} (hx : 199 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 200, r ≤ g0 x 4909 :=
  prod_le_g0 hx g0_pos_199_4909

/-- `ln g0(x, 8311) ≥ θ(x) - θ(293)` for every `x ≥ 293`. -/
theorem prod_le_g0_8311 {x : ℕ} (hx : 293 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 294, r ≤ g0 x 8311 :=
  prod_le_g0 hx g0_pos_293_8311

/-- **`ln g0(x, 15907) ≥ θ(x) - θ(463)`** for every `x ≥ 463`: among the class vectors modulo
the odd primes up to `x`, at least the product of the odd primes in `(463, x]` cover every odd
prime below `15907`. -/
theorem prod_le_g0_15907 {x : ℕ} (hx : 463 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 464, r ≤ g0 x 15907 :=
  prod_le_g0 hx g0_pos_463_15907

/-- `ln g0(x, 16381) ≥ θ(x) - θ(479)` for every `x ≥ 479`. -/
theorem prod_le_g0_16381 {x : ℕ} (hx : 479 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 480, r ≤ g0 x 16381 :=
  prod_le_g0 hx g0_pos_479_16381

/-- `ln g0(x, 16747) ≥ θ(x) - θ(487)` for every `x ≥ 487`. -/
theorem prod_le_g0_16747 {x : ℕ} (hx : 487 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 488, r ≤ g0 x 16747 :=
  prod_le_g0 hx g0_pos_487_16747

/-- `ln g0(x, 16981) ≥ θ(x) - θ(491)` for every `x ≥ 491`. -/
theorem prod_le_g0_16981 {x : ℕ} (hx : 491 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 492, r ≤ g0 x 16981 :=
  prod_le_g0 hx g0_pos_491_16981

/-- `ln g0(x, 40111) ≥ θ(x) - θ(997)` for every `x ≥ 997`. -/
theorem prod_le_g0_40111 {x : ℕ} (hx : 997 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 998, r ≤ g0 x 40111 :=
  prod_le_g0 hx g0_pos_997_40111

/-- `ln g0(x, 135511) ≥ θ(x) - θ(2999)` for every `x ≥ 2999`. -/
theorem prod_le_g0_135511 {x : ℕ} (hx : 2999 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 3000, r ≤ g0 x 135511 :=
  prod_le_g0 hx g0_pos_2999_135511

/-- `ln g0(x, 614101) ≥ θ(x) - θ(9973)` for every `x ≥ 9999`. -/
theorem prod_le_g0_614101 {x : ℕ} (hx : 9999 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 10000, r ≤ g0 x 614101 :=
  prod_le_g0 hx g0_pos_9999_614101

/-- **Where the count ends, exactly, for nine moduli**: some class vector modulo
`3, 5, …, 29` covers every odd prime below `181`, and none covers `181` as well. -/
theorem g0_29_181 : 0 < g0 29 181 ∧ g0 29 182 = 0 :=
  (isDepth_iff_g0 (mods := [3, 5, 7, 11, 13, 17, 19, 23, 29]) (x := 29)
    (fun r => by
      have h : oddPrimesBelow 30 = [3, 5, 7, 11, 13, 17, 19, 23, 29] := by decide
      rw [← h]; exact mem_oddPrimesBelow (by norm_num)) 181).1 isDepth_9

/-- **The 167 odd primes up to `997` cover every odd prime below `40459`**: the best cover known
on these moduli (24 November 2026), sampled by another session from the `40111` one with the
research session's program and certified in `GoldbachGaps/Cover40459.lean`. -/
theorem coversBelow_40459 : CoversBelow (oddPrimesBelow 998) 40459 :=
  coversBelow_of_complete_cover (R := 997) (by norm_num) Cover40459.complete_cover.2.1
    Cover40459.complete_cover.2.2.1

theorem g0_pos_997_40459 : 0 < g0 997 40459 :=
  g0_pos_of_coversBelow (by norm_num) coversBelow_40459

/-- `ln g0(x, 40459) ≥ θ(x) - θ(997)` for every `x ≥ 997`. -/
theorem prod_le_g0_40459 {x : ℕ} (hx : 997 ≤ x) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow 998, r ≤ g0 x 40459 :=
  prod_le_g0 hx g0_pos_997_40459

theorem rowsBelow_8 : rowsBelow 8 = {3, 5, 7} := by decide

theorem rowsBelow_19 : rowsBelow 19 = {3, 5, 7, 11, 13, 17} := by decide

theorem rowsBelow_20 : rowsBelow 20 = {3, 5, 7, 11, 13, 17, 19} := by decide

set_option maxRecDepth 100000 in
/-- **The count itself, for three moduli.** Of the `105` class vectors modulo `3, 5, 7` exactly
one covers every odd prime below `19` (the classes `2, 3, 0` of the term `98` of A025018), and
none covers `19` as well. `scripts/cover_count/g0_exact.c` computes such counts for up to ten
moduli by going through every class vector. -/
theorem g0_7_19 : g0 7 19 = 1 ∧ g0 7 20 = 0 := by
  unfold g0
  rw [rowsBelow_8, rowsBelow_19, rowsBelow_20]
  decide +kernel

end GoldbachGaps.CoverCount
