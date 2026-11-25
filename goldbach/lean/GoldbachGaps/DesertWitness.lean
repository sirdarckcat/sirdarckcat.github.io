import GoldbachGaps.Desert

/-!
# A witness for every row: a faster check that `N` has no small Goldbach summand

`GoldbachGaps/Desert.lean` certifies "no `q` in a block is a Goldbach summand of `N`" by letting
the kernel find, for every `q`, a small prime factor of `q` or a covering modulus dividing
`N - q`. The search is most of the cost. Here the certificate carries the answer: one number
`d` for every `q`, and the kernel does one division per row.

* `rowCheck N q d`: the witness `d` settles the row `q`. Either `q < 2`; or `d ≤ 1` and `N - q`
  fails the base-2 Fermat test; or `d` is a proper divisor of `q`; or `d` is a proper divisor
  of `N - q`.
* `not_isSummand_of_rowCheck`: then `q` is not a Goldbach summand of `N`.
* `witnessCheck N lo ws`, `noSummandIn_of_witnessCheck`: the rows `lo, lo + 1, …` against the
  list `ws` of witnesses.

`scripts/gen_desert.py --witness` writes certificates in this form.
-/

namespace GoldbachGaps

open Mathlib.Tactic.Primality (powMod)

/-- The witness `d` settles the row `q`: `q < 2`, or `N - q` fails the base-2 Fermat test
(`d ≤ 1`), or `d` is a proper divisor of `q`, or `d` is a proper divisor of `N - q`. -/
def rowCheck (N q d : ℕ) : Bool :=
  decide (q < 2) ||
    if d ≤ 1 then decide (q + 2 < N) && powMod 2 (N - q - 1) (N - q) != 1
    else (decide (d < q) && q % d == 0) || (decide (d + q < N) && (N - q) % d == 0)

theorem not_isSummand_of_rowCheck {N q d : ℕ} (h : rowCheck N q d = true) : ¬ IsSummand N q := by
  rintro ⟨hq, hNq⟩
  have hq2 := hq.two_le
  unfold rowCheck at h
  rw [Bool.or_eq_true, decide_eq_true_eq] at h
  rcases h with h | h
  · omega
  · split_ifs at h with hd
    · rw [Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne] at h
      exact not_prime_of_powMod_ne_one (by omega) h.2 hNq
    · simp only [Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
      rcases h with ⟨hlt, hmod⟩ | ⟨hlt, hmod⟩
      · rcases (Nat.dvd_prime hq).1 (Nat.dvd_of_mod_eq_zero hmod) with h1 | h1 <;> omega
      · rcases (Nat.dvd_prime hNq).1 (Nat.dvd_of_mod_eq_zero hmod) with h1 | h1 <;> omega

/-- The rows `q, q + 1, …` against the witnesses `ws`, one each. -/
def witnessCheck (N : ℕ) : ℕ → List ℕ → Bool
  | _, [] => true
  | q, d :: ws => rowCheck N q d && witnessCheck N (q + 1) ws

/-- Soundness of `witnessCheck`. -/
theorem noSummandIn_of_witnessCheck {N : ℕ} :
    ∀ (ws : List ℕ) (lo : ℕ), witnessCheck N lo ws = true → NoSummandIn N lo (lo + ws.length)
  | [], lo, _ => fun q h1 h2 => by
    simp only [List.length_nil, Nat.add_zero] at h2
    omega
  | d :: ws, lo, h => by
    rw [witnessCheck, Bool.and_eq_true] at h
    intro q h1 h2
    rw [List.length_cons] at h2
    rcases Nat.eq_or_lt_of_le h1 with rfl | hlt
    · exact not_isSummand_of_rowCheck h.1
    · exact noSummandIn_of_witnessCheck ws (lo + 1) h.2 q (by omega) (by omega)

/-- The form the generated files use: the block `[lo, hi)` from a list of `hi - lo` witnesses. -/
theorem noSummandIn_of_witnessCheck' {N lo hi : ℕ} (ws : List ℕ)
    (h : witnessCheck N lo ws = true) (hlen : lo + ws.length = hi) : NoSummandIn N lo hi :=
  hlen ▸ noSummandIn_of_witnessCheck ws lo h

end GoldbachGaps
