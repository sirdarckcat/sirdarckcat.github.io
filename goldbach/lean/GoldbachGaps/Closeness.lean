import GoldbachGaps.Record27_g11467
import GoldbachGaps.Record26_g10303
import GoldbachGaps.Record26_g10159
import GoldbachGaps.Record25_g10357

/-!
# The closeness game: least Goldbach summands certified exactly, both sides

The game set by the lead on 25 November 2026 asks for the largest number of digits at which a
certified `N` has `g(N)` at least a given share (10%, 25%, 50%) of the ceiling of its own size.
The ceiling and the share are a model and are not part of any statement here. What is proved, for
each number below, is the exact value of its least Goldbach summand:

* `N` is even and has exactly the stated number of digits;
* `N - g` is prime: a Lucas certificate (a primitive root and the complete factorisation of
  `n - 1` for every prime `n` of the Pratt tree), from which Mathlib's `primality` tactic builds a
  proof that the kernel checks;
* `N - p` is not prime for any prime `p < g`: one of the moduli `3, …, 43` divides it, or it
  fails the base-2 Fermat test (`GoldbachGaps/Desert.lean`).

| digits | `N` | `g(N)` |
|---|---|---|
| 27 | `111308182437581302718351168` | 11,467 |
| 26 | `10492156463590001369800256` | 10,303 |
| 26 | `10621579671744600348710546` | 10,159 |
| 25 | `5471513744131872011405456` | 10,357 |

The numbers are the research session's (`goldbach/sublinear/` on branch `ccr-d4a17dd0-7uu03r`,
Pratt trees in `frontier_pratt.json` at `94b5ea8`). Each was rechecked here from `N` alone, and
each tree node by node, before the certificate was generated (`scripts/gen_record.py --lucas`);
none of that is trusted by Lean.
-/

namespace GoldbachGaps

/-- The least Goldbach summand from its parts: `g` is the least Goldbach summand of `N` exactly
when `g` and `N - g` are prime and `N - p` is not prime for any prime `p < g`. -/
theorem isLeastSummand_iff {N g : ℕ} :
    IsLeastSummand N g ↔ g.Prime ∧ (N - g).Prime ∧ ∀ p, p.Prime → p < g → ¬ (N - p).Prime :=
  ⟨fun h => ⟨h.1.1, h.1.2, fun p hp hlt hq => absurd (h.2 p ⟨hp, hq⟩) (not_le.mpr hlt)⟩,
   fun ⟨hg, hc, hno⟩ => ⟨⟨hg, hc⟩, fun p hp => not_lt.mp fun hlt => hno p hp.1 hlt hp.2⟩⟩

/-- The least Goldbach summand is unique, so `IsLeastSummand N g` says `g(N) = g`. -/
theorem IsLeastSummand.unique {N a b : ℕ} (ha : IsLeastSummand N a) (hb : IsLeastSummand N b) :
    a = b :=
  le_antisymm (ha.2 b hb.1) (hb.2 a ha.1)

/-- **`g(111308182437581302718351168) = 11467`**: the least Goldbach summand of this 27-digit number
is exactly `11467`. -/
theorem isLeastSummand_27digit_11467 : IsLeastSummand 111308182437581302718351168 11467 :=
  Record27_g11467.isLeastSummand

/-- The same in full: `N` is even, has exactly 27 digits, `N - 11467` is prime, and `N - p` is not
prime for any prime `p < 11467`. -/
theorem closeness_27digit_11467 :
    Even 111308182437581302718351168 ∧ 10 ^ 26 ≤ 111308182437581302718351168 ∧
      111308182437581302718351168 < 10 ^ 27 ∧ (111308182437581302718351168 - 11467).Prime ∧
      ∀ p : ℕ, p.Prime → p < 11467 → ¬ (111308182437581302718351168 - p).Prime :=
  ⟨Record27_g11467.N_even, Record27_g11467.le_N, Record27_g11467.N_lt, Record27_g11467.prime_complement,
    Record27_g11467.not_prime_sub⟩

/-- Some even number with exactly 27 digits has least Goldbach summand exactly `11467`. -/
theorem exists_27_digit_isLeastSummand_11467 :
    ∃ N, 10 ^ 26 ≤ N ∧ N < 10 ^ 27 ∧ Even N ∧ IsLeastSummand N 11467 :=
  ⟨Record27_g11467.N, Record27_g11467.le_N, Record27_g11467.N_lt, Record27_g11467.N_even, Record27_g11467.isLeastSummand⟩

/-- **`g(10492156463590001369800256) = 10303`**: the least Goldbach summand of this 26-digit number
is exactly `10303`. -/
theorem isLeastSummand_26digit_10303 : IsLeastSummand 10492156463590001369800256 10303 :=
  Record26_g10303.isLeastSummand

/-- The same in full: `N` is even, has exactly 26 digits, `N - 10303` is prime, and `N - p` is not
prime for any prime `p < 10303`. -/
theorem closeness_26digit_10303 :
    Even 10492156463590001369800256 ∧ 10 ^ 25 ≤ 10492156463590001369800256 ∧
      10492156463590001369800256 < 10 ^ 26 ∧ (10492156463590001369800256 - 10303).Prime ∧
      ∀ p : ℕ, p.Prime → p < 10303 → ¬ (10492156463590001369800256 - p).Prime :=
  ⟨Record26_g10303.N_even, Record26_g10303.le_N, Record26_g10303.N_lt, Record26_g10303.prime_complement,
    Record26_g10303.not_prime_sub⟩

/-- Some even number with exactly 26 digits has least Goldbach summand exactly `10303`. -/
theorem exists_26_digit_isLeastSummand_10303 :
    ∃ N, 10 ^ 25 ≤ N ∧ N < 10 ^ 26 ∧ Even N ∧ IsLeastSummand N 10303 :=
  ⟨Record26_g10303.N, Record26_g10303.le_N, Record26_g10303.N_lt, Record26_g10303.N_even, Record26_g10303.isLeastSummand⟩

/-- **`g(10621579671744600348710546) = 10159`**: the least Goldbach summand of this 26-digit number
is exactly `10159`. -/
theorem isLeastSummand_26digit_10159 : IsLeastSummand 10621579671744600348710546 10159 :=
  Record26_g10159.isLeastSummand

/-- The same in full: `N` is even, has exactly 26 digits, `N - 10159` is prime, and `N - p` is not
prime for any prime `p < 10159`. -/
theorem closeness_26digit_10159 :
    Even 10621579671744600348710546 ∧ 10 ^ 25 ≤ 10621579671744600348710546 ∧
      10621579671744600348710546 < 10 ^ 26 ∧ (10621579671744600348710546 - 10159).Prime ∧
      ∀ p : ℕ, p.Prime → p < 10159 → ¬ (10621579671744600348710546 - p).Prime :=
  ⟨Record26_g10159.N_even, Record26_g10159.le_N, Record26_g10159.N_lt, Record26_g10159.prime_complement,
    Record26_g10159.not_prime_sub⟩

/-- Some even number with exactly 26 digits has least Goldbach summand exactly `10159`. -/
theorem exists_26_digit_isLeastSummand_10159 :
    ∃ N, 10 ^ 25 ≤ N ∧ N < 10 ^ 26 ∧ Even N ∧ IsLeastSummand N 10159 :=
  ⟨Record26_g10159.N, Record26_g10159.le_N, Record26_g10159.N_lt, Record26_g10159.N_even, Record26_g10159.isLeastSummand⟩

/-- **`g(5471513744131872011405456) = 10357`**: the least Goldbach summand of this 25-digit number
is exactly `10357`. -/
theorem isLeastSummand_25digit_10357 : IsLeastSummand 5471513744131872011405456 10357 :=
  Record25_g10357.isLeastSummand

/-- The same in full: `N` is even, has exactly 25 digits, `N - 10357` is prime, and `N - p` is not
prime for any prime `p < 10357`. -/
theorem closeness_25digit_10357 :
    Even 5471513744131872011405456 ∧ 10 ^ 24 ≤ 5471513744131872011405456 ∧
      5471513744131872011405456 < 10 ^ 25 ∧ (5471513744131872011405456 - 10357).Prime ∧
      ∀ p : ℕ, p.Prime → p < 10357 → ¬ (5471513744131872011405456 - p).Prime :=
  ⟨Record25_g10357.N_even, Record25_g10357.le_N, Record25_g10357.N_lt, Record25_g10357.prime_complement,
    Record25_g10357.not_prime_sub⟩

/-- Some even number with exactly 25 digits has least Goldbach summand exactly `10357`. -/
theorem exists_25_digit_isLeastSummand_10357 :
    ∃ N, 10 ^ 24 ≤ N ∧ N < 10 ^ 25 ∧ Even N ∧ IsLeastSummand N 10357 :=
  ⟨Record25_g10357.N, Record25_g10357.le_N, Record25_g10357.N_lt, Record25_g10357.N_even, Record25_g10357.isLeastSummand⟩

end GoldbachGaps
