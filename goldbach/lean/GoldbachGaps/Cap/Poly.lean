import GoldbachGaps.Basic

/-!
# The capped game: algebraic families

`phd/wp7_probes.md` (probe P2) states as a mini-proposition that a polynomial identity can
make only `O(√Q)` rows composite, at the price of confining `N` to a thin family. This file
proves the exact statements behind it.

* `not_prime_eval_sub_eval` – the mechanism, for every polynomial `f` with integer
  coefficients: if `N = f(u)` and `q = f(c)`, then `u - c` divides `N - q`. So `N = f(u)`
  makes the rows `q = f(c)` composite. For `f` of degree one this is ordinary covering
  (the rows of one residue class); `f(x) = x^k - a` is the case of the note.
* `card_le_sqrt_succ` – if `f(c) ≥ c²` for all `c` (every polynomial of degree `≥ 2` with
  positive leading coefficient satisfies this from some point on), at most `√Q + 1` values of
  `c` give a row `f(c)` below `Q`, and at most `√X + 1` values of `u` give an `N = f(u)`
  below `X`.

In nats: such a family gives up half of `ln X` (115 nats at 100 digits, 230 at 200) and in
return removes at most `√Q + 1` rows (350 at `Q = 122000`), most of which a cover of the
remaining size would have removed anyway.
-/

namespace GoldbachGaps.Cap

open Polynomial

/-- **The mechanism of algebraic families.** For `f ∈ ℤ[x]` and integers `u`, `c` with
`1 < |u - c| < |f(u) - f(c)|`, the number `|f(u) - f(c)|` is not prime: it is divisible by
`|u - c|`. -/
theorem not_prime_eval_sub_eval (f : ℤ[X]) (u c : ℤ) (h1 : 1 < (u - c).natAbs)
    (h2 : (u - c).natAbs < (f.eval u - f.eval c).natAbs) :
    ¬ (f.eval u - f.eval c).natAbs.Prime :=
  Nat.not_prime_of_dvd_of_lt (Int.natAbs_dvd_natAbs.mpr (sub_dvd_eval_sub u c f)) h1 h2

/-- The same in the form used for rows: if `N = f(u)` and `q = f(c)` are natural numbers
with `q ≤ N`, and `1 < u - c < N - q`, then the row `N - q` is not prime. -/
theorem not_prime_row_of_eval (f : ℤ[X]) (u c : ℤ) {N q : ℕ} (hN : f.eval u = N)
    (hq : f.eval c = q) (hle : q ≤ N) (h1 : 1 < u - c) (h2 : u - c < (N : ℤ) - q) :
    ¬ (N - q).Prime := by
  have key := not_prime_eval_sub_eval f u c (by omega) (by rw [hN, hq]; omega)
  rw [hN, hq] at key
  have : ((N : ℤ) - q).natAbs = N - q := by omega
  rwa [this] at key

/-- **The value-set ceiling.** If `f(c) ≥ c²` for every `c` in a finite set `T` and all the
values `f(c)`, `c ∈ T`, are below `Q`, then `T` has at most `√Q + 1` elements. With `Q` the
row bound this limits the rows a family of degree `≥ 2` can remove; with `Q = X` the cap, it
limits the number of members of the family. -/
theorem card_le_sqrt_succ (f : ℕ → ℕ) (Q : ℕ) (T : Finset ℕ)
    (hT : ∀ c ∈ T, c ^ 2 ≤ f c ∧ f c < Q) : T.card ≤ Nat.sqrt Q + 1 := by
  rw [← Finset.card_range (Nat.sqrt Q + 1)]
  refine Finset.card_le_card fun c hc => ?_
  obtain ⟨h1, h2⟩ := hT c hc
  rw [Finset.mem_range, Nat.lt_succ_iff, Nat.le_sqrt']
  omega

end GoldbachGaps.Cap
