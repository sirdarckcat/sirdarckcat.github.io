import GoldbachGaps.Basic

/-!
# The capped game: what can make a row composite

In the game "largest `g(N)` for `N` below a cap" every prime `q < Q` gives a *row*, the
number `N - q`, and `g(N) ≥ Q` means that every row is composite. This file records the exact
facts about what can make rows composite. They are elementary; they are stated here because
the cost model of `goldbach/SOK_GOLDBACH_GAPS.md` and several entries of the ideas ledgers
(`IDEAS.md` F7, `phd/wp7_probes.md` P1) rest on them.

* `not_prime_sub_iff` – a row is composite exactly when `q ≡ N` modulo some prime `r` with
  `r² ≤ N - q`. So the only thing one can design about `N` is its residues modulo primes.
* `dvd_sub_iff` – a prime kills exactly one residue class of rows.
* `prime_moduli_suffice` – a system of congruences with arbitrary moduli (composite, prime
  powers, not coprime) kills nothing that the system of one prime factor per modulus does not
  kill, and every `N` satisfying the first satisfies the second.
* `dvd_sub_rows`, `lt_of_dvd_two_rows`, `row_unique_of_le` – a number dividing two rows
  divides the difference of their `q`; so a prime `r ≥ Q` divides at most one row below `Q`.
  Whatever dependence there is between rows passes through primes below `Q`.
-/

namespace GoldbachGaps.Cap

/-- One class per modulus: the rows of `N` divisible by `r` are those with `q ≡ N (mod r)`. -/
theorem dvd_sub_iff {N q r : ℕ} (h : q ≤ N) : r ∣ N - q ↔ q ≡ N [MOD r] :=
  (Nat.modEq_iff_dvd' h).symm

/-- **Kills are residues.** For `q + 2 ≤ N`, the row `N - q` is composite exactly when
`q ≡ N` modulo some prime `r` with `r² ≤ N - q`. -/
theorem not_prime_sub_iff {N q : ℕ} (h : q + 2 ≤ N) :
    ¬ (N - q).Prime ↔ ∃ r, r.Prime ∧ r * r ≤ N - q ∧ q ≡ N [MOD r] := by
  have hle : q ≤ N := by omega
  constructor
  · intro hnp
    refine ⟨(N - q).minFac, Nat.minFac_prime (by omega), ?_, ?_⟩
    · have := Nat.minFac_sq_le_self (by omega : 0 < N - q) hnp
      rwa [sq] at this
    · exact (dvd_sub_iff hle).mp (Nat.minFac_dvd _)
  · rintro ⟨r, hr, hsq, hmod⟩ hp
    have hdvd : r ∣ N - q := (dvd_sub_iff hle).mpr hmod
    have hreq : r = N - q := (Nat.prime_dvd_prime_iff_eq hr hp).mp hdvd
    have h2 := hr.two_le
    rw [← hreq] at hsq
    have : r * 2 ≤ r * r := Nat.mul_le_mul_left r h2
    omega

/-- **Prime moduli suffice.** Given any family of congruence conditions `x ≡ a i (mod m i)`
with moduli `m i ≥ 2` (composite, prime powers, with common factors: anything), there are
primes `r i ∣ m i` such that every `N` in all the classes modulo the `m i` is in all the
classes modulo the `r i`, and every row killed through `m i` is killed through `r i`. -/
theorem prime_moduli_suffice {ι : Type*} (m a : ι → ℕ) (hm : ∀ i, 2 ≤ m i) :
    ∃ r : ι → ℕ, (∀ i, (r i).Prime ∧ r i ∣ m i) ∧
      (∀ N, (∀ i, N ≡ a i [MOD m i]) → ∀ i, N ≡ a i [MOD r i]) ∧
      ∀ q i, q ≡ a i [MOD m i] → q ≡ a i [MOD r i] := by
  refine ⟨fun i => (m i).minFac, fun i => ⟨Nat.minFac_prime ?_, Nat.minFac_dvd _⟩, ?_, ?_⟩
  · have := hm i
    omega
  · intro N hN i
    exact (hN i).of_dvd (Nat.minFac_dvd _)
  · intro q i h
    exact h.of_dvd (Nat.minFac_dvd _)

/-- A number dividing two rows divides the difference of their `q`. -/
theorem dvd_sub_rows {N q q' r : ℕ} (hq' : q' ≤ N) (hlt : q < q')
    (h : r ∣ N - q) (h' : r ∣ N - q') : r ∣ q' - q := by
  have : q' - q = (N - q) - (N - q') := by omega
  rw [this]
  exact Nat.dvd_sub h h'

/-- **Two rows share only small divisors**: a common divisor of two different rows below `Q`
is itself below `Q`. -/
theorem lt_of_dvd_two_rows {N q q' r Q : ℕ} (hq' : q' ≤ N) (hlt : q < q') (hQ : q' < Q)
    (h : r ∣ N - q) (h' : r ∣ N - q') : r < Q := by
  have hd := dvd_sub_rows hq' hlt h h'
  have := Nat.le_of_dvd (by omega) hd
  omega

/-- A number `r ≥ Q` divides at most one row below `Q`. -/
theorem row_unique_of_le {N q q' r Q : ℕ} (hr : Q ≤ r) (hqN : q ≤ N) (hq'N : q' ≤ N)
    (hq : q < Q) (hq' : q' < Q) (h : r ∣ N - q) (h' : r ∣ N - q') : q = q' := by
  rcases lt_trichotomy q q' with hlt | heq | hgt
  · have := lt_of_dvd_two_rows hq'N hlt hq' h h'
    omega
  · exact heq
  · have := lt_of_dvd_two_rows hqN hgt hq h' h
    omega

end GoldbachGaps.Cap
