import GoldbachGaps.Cap.Rows
import GoldbachGaps.Cap.Budget

/-!
# The brainstorm of 2026-11-22: the parts a kernel can decide

The research session sent 100 ideas for raising the largest known `g(N)` with `N < 10^200`
(standing: `g = 133981`, 6.3% of the heuristic ceiling `2130704`), with the request to try to
prove each of them wrong. Most of the list is engineering, measurement or heuristic counting
and has no theorem in it. This file holds the statements that do, numbered as in that list.

* idea 4 (zero classes)            – `zero_class_row`, `card_zero_class_rows_le_one`
* ideas 26, 53 (shared row values)  – `prod_le_sub_of_modEq`, `shared_row_value`,
                                     `no_shared_row_value_of_six`
* idea 46 (moves under the cap)    – `move_budget`, `move_keeps_at_most_three`
* idea 28 (one exponent, all rows) – `fermat_common_exponent`, `fermat_from_product`
* ideas 34, 57 (stopping rules)    – `never_abandon`, `cost_per_hit_le`
* idea 96 (which row first)        – `test_order`
* ideas 35, 74 (faulty arithmetic) – `faulty_scan_reports_hits`
* ideas 12, 14, 15, 20 (sparse algebraic values) – `pow_succ_ge`, `pow_window`,
                                     `doubling_window`
* idea 24 (parity)                 – `odd_N_trivial`, `two_pow_not_dvd_row`
* idea 44 (linear combinations)    – `affine_combination`
* ideas 43, 73, 97 (recombination, special forms) – `card_prescribed_le`
* idea 100 (a third mechanism)     – `large_divisor_budget`, `large_divisors_unique`
* idea 70 (unions of families)     – `union_density`

Already in the library and used for other numbers of the list: `Cap.lt_of_dvd_two_rows`
(a divisor of two rows is below `Q`), `Cap.card_residues_in_le` (the budget law),
`Cap.sum_card_rowsLeft` (the first moment), `Cap.card_le_sqrt_succ` (polynomial families),
`Cap.not_isSummand_of_desert` (a prime-free run gives rows, never the other way round).
-/

namespace GoldbachGaps.Brainstorm

open Finset

/-! ### Idea 4: zero classes -/

/-- **Idea 4.** If the modulus `r` divides `N` (a zero class), the only prime row it covers
is `q = r`. -/
theorem zero_class_row {N q r : ℕ} (hr : r.Prime) (hq : q.Prime) (hqN : q ≤ N) (hN : r ∣ N)
    (h : r ∣ N - q) : q = r := by
  have h1 : r ∣ N - (N - q) := Nat.dvd_sub hN h
  rw [Nat.sub_sub_self hqN] at h1
  exact ((Nat.prime_dvd_prime_iff_eq hr hq).mp h1).symm

/-- A zero class covers at most one row, against about `|P| / (r - 1)` for a nonzero class
(`Cap.sum_card_rowsLeft`). -/
theorem card_zero_class_rows_le_one {N r : ℕ} (hr : r.Prime) (hN : r ∣ N) (P : Finset ℕ)
    (hP : ∀ q ∈ P, q.Prime ∧ q ≤ N) : #{q ∈ P | r ∣ N - q} ≤ 1 := by
  refine Finset.card_le_one.mpr fun a ha b hb => ?_
  rw [Finset.mem_filter] at ha hb
  rw [zero_class_row hr (hP a ha.1).1 (hP a ha.1).2 hN ha.2,
    zero_class_row hr (hP b hb.1).1 (hP b hb.1).2 hN hb.2]

/-! ### Ideas 26, 46, 53: what two candidates can have in common -/

/-- Two different numbers with the same residues modulo pairwise coprime moduli are at least
the product of the moduli apart. -/
theorem prod_le_sub_of_modEq {S : Finset ℕ} (hcop : (S : Set ℕ).Pairwise Nat.Coprime)
    {N N' : ℕ} (hlt : N < N') (h : ∀ r ∈ S, N ≡ N' [MOD r]) : ∏ r ∈ S, r ≤ N' - N := by
  have hdvd : (∏ r ∈ S, r) ∣ N' - N :=
    (Nat.modEq_iff_dvd' hlt.le).mp (Cap.modEq_prod_of_forall hcop h)
  exact Nat.le_of_dvd (by omega) hdvd

/-- **Ideas 26 and 53 (windows, neighbours of a hit).** If two candidates `N < N'` share a
row value, `N - q = N' - q'` with `q' < g`, then the moduli on which they have the same
residue multiply to less than `g`: sharing work between candidates and sharing a deep cover
exclude each other. -/
theorem shared_row_value {S : Finset ℕ} (hcop : (S : Set ℕ).Pairwise Nat.Coprime)
    {N N' q q' g : ℕ} (hlt : N < N') (hq : q ≤ N) (hq' : q' ≤ N') (hg : q' < g)
    (hval : N - q = N' - q') (h : ∀ r ∈ S, N ≡ N' [MOD r]) : ∏ r ∈ S, r < g := by
  have := prod_le_sub_of_modEq hcop hlt h
  omega

/-- For rows below `255255 = 3·5·7·11·13·17` (the 10% target is `213070`): two candidates
that share a row value cannot have the same residues modulo all of 3, 5, 7, 11, 13, 17. -/
theorem no_shared_row_value_of_six {N N' q q' : ℕ} (hlt : N < N') (hq : q ≤ N)
    (hq' : q' ≤ N') (hg : q' < 255255) (hval : N - q = N' - q')
    (h : ∀ r ∈ ({3, 5, 7, 11, 13, 17} : Finset ℕ), N ≡ N' [MOD r]) : False := by
  have hcop : (({3, 5, 7, 11, 13, 17} : Finset ℕ) : Set ℕ).Pairwise Nat.Coprime := by
    intro a ha b hb hab
    simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff] at ha hb
    rcases ha with rfl | rfl | rfl | rfl | rfl | rfl <;>
      rcases hb with rfl | rfl | rfl | rfl | rfl | rfl <;>
      first
        | exact absurd rfl hab
        | decide
  have := shared_row_value hcop hlt hq hq' hg hval h
  simp at this

/-- **Idea 46 (local moves under the cap).** Two different numbers below `X` in the same
class modulo the cover modulus `M` and modulo every sieve prime of `T`: then `M · ∏ T < X`.
The reasons a move can keep are bought with the modulus that is left. -/
theorem move_budget {T : Finset ℕ} (hcop : (T : Set ℕ).Pairwise Nat.Coprime) {M : ℕ}
    (hM : ∀ s ∈ T, M.Coprime s) {N N' X : ℕ} (hlt : N < N') (hX : N' < X)
    (hmodM : N ≡ N' [MOD M]) (h : ∀ s ∈ T, N ≡ N' [MOD s]) : M * ∏ s ∈ T, s < X := by
  have h1 := Cap.modEq_prod_of_forall hcop h
  have hc : M.Coprime (∏ s ∈ T, s) := Nat.coprime_prod_right_iff.mpr hM
  have h2 : N ≡ N' [MOD M * ∏ s ∈ T, s] :=
    (Nat.modEq_and_modEq_iff_modEq_mul hc).mp ⟨hmodM, h1⟩
  have := Nat.le_of_dvd (by omega) ((Nat.modEq_iff_dvd' hlt.le).mp h2)
  omega

/-- With the campaign's numbers (`X / M < 463 ^ 4`, the spare room is 22.4 nats and four
sieve primes need 24.6): a move keeps the reasons of at most three sieve primes. -/
theorem move_keeps_at_most_three {T : Finset ℕ} (hbig : ∀ s ∈ T, 463 ≤ s) {M X : ℕ}
    (hprod : M * ∏ s ∈ T, s < X) (hX : X ≤ M * 463 ^ 4) : T.card ≤ 3 := by
  by_contra hcon
  have h4 : 4 ≤ T.card := by omega
  have h1 : 463 ^ T.card ≤ ∏ s ∈ T, s := by
    rw [← Finset.prod_const]
    exact Finset.prod_le_prod hbig
  have h2 : 463 ^ 4 ≤ 463 ^ T.card := Nat.pow_le_pow_right (by norm_num) h4
  have := Nat.mul_le_mul_left M (h2.trans h1)
  omega

/-! ### Idea 28: one exponent for all rows -/

/-- **Idea 28.** The row `N - q` (odd) passes the base-2 Fermat test iff
`2^(N-1) ≡ 2^q` modulo it: the exponent `N - 1` serves every row of `N`. -/
theorem fermat_common_exponent {N q : ℕ} (hq : q < N) (hodd : (N - q) % 2 = 1) :
    2 ^ (N - 1) ≡ 2 ^ q [MOD N - q] ↔ 2 ^ (N - q - 1) ≡ 1 [MOD N - q] := by
  have he : N - 1 = (N - q - 1) + q := by omega
  have h2 : Nat.Coprime (N - q) 2 := by
    rw [Nat.coprime_comm, Nat.Prime.coprime_iff_not_dvd Nat.prime_two]
    omega
  have hc : Nat.Coprime (N - q) (2 ^ q) := Nat.Coprime.pow_right q h2
  rw [he, pow_add]
  constructor
  · intro h
    have h' : 2 ^ (N - q - 1) * 2 ^ q ≡ 1 * 2 ^ q [MOD N - q] := by simpa using h
    exact Nat.ModEq.cancel_right_of_coprime hc h'
  · intro h
    simpa using h.mul_right (2 ^ q)

/-- The same read off one exponentiation modulo any multiple `P` of the row, for instance
the product of all rows of `N`. -/
theorem fermat_from_product {N q P : ℕ} (hq : q < N) (hodd : (N - q) % 2 = 1)
    (hP : N - q ∣ P) :
    (2 ^ (N - 1) % P) % (N - q) = 2 ^ q % (N - q) ↔ 2 ^ (N - q - 1) ≡ 1 [MOD N - q] := by
  rw [Nat.mod_mod_of_dvd _ hP]
  exact fermat_common_exponent hq hodd

/-! ### Ideas 34, 57, 96: stopping rules and the order of the tests -/

/-- **Ideas 34 and 57.** `s j` is the probability that a member is still alive before its
`(j+1)`-st test, `A j` the probability that the policy has not abandoned it by then (so `A`
does not increase). Tests spent per member: `Σ s j · A j`. Chance of a completed success:
`s k · A k`. Then `A k · Σ s j ≤ Σ s j · A j`: no policy of abandoning members spends fewer
tests per success than never abandoning. -/
theorem never_abandon (k : ℕ) (s A : ℕ → ℝ) (hs : ∀ j < k, 0 ≤ s j)
    (hA : ∀ j < k, A k ≤ A j) : A k * ∑ j ∈ range k, s j ≤ ∑ j ∈ range k, s j * A j := by
  rw [Finset.mul_sum]
  refine Finset.sum_le_sum fun j hj => ?_
  have hj' := Finset.mem_range.mp hj
  nlinarith [hs j hj', hA j hj']

/-- The same as a cost per success: `(Σ s j) / S ≤ (Σ s j A j) / (S · A k)`. -/
theorem cost_per_hit_le (k : ℕ) (s A : ℕ → ℝ) (S : ℝ) (hs : ∀ j < k, 0 ≤ s j) (hS : 0 < S)
    (hA : ∀ j < k, A k ≤ A j) (hAk : 0 < A k) :
    (∑ j ∈ range k, s j) / S ≤ (∑ j ∈ range k, s j * A j) / (S * A k) := by
  rw [div_le_div_iff₀ hS (mul_pos hS hAk)]
  have := mul_le_mul_of_nonneg_left (never_abandon k s A hs hA) hS.le
  nlinarith [this]

/-- **Idea 96.** Two rows with test costs `c₁, c₂` and prime probabilities `p₁, p₂`: testing
row 1 first is cheaper in expectation iff `p₂ c₁ ≤ p₁ c₂`. With equal `p` and `c` the order
does not matter. -/
theorem test_order (c₁ c₂ p₁ p₂ : ℝ) :
    c₁ + (1 - p₁) * c₂ ≤ c₂ + (1 - p₂) * c₁ ↔ p₂ * c₁ ≤ p₁ * c₂ := by
  constructor <;> intro h <;> nlinarith [h]

/-! ### Ideas 35, 74: arithmetic that may be wrong -/

/-- **Ideas 35 and 74.** `ρ i` is the residue a possibly faulty kernel reports for row `i`.
If every fault either leaves the true residue or produces something other than `1`, every
true success (no row with Fermat residue `1`) is still reported as a success. Faults cost
false alarms, never successes. -/
theorem faulty_scan_reports_hits {ι : Type*} (rows : Finset ι) (n ρ : ι → ℕ)
    (hit : ∀ i ∈ rows, 2 ^ (n i - 1) % n i ≠ 1)
    (fault : ∀ i ∈ rows, ρ i = 2 ^ (n i - 1) % n i ∨ ρ i ≠ 1) : ∀ i ∈ rows, ρ i ≠ 1 := by
  intro i hi
  rcases fault i hi with h | h
  · rw [h]
    exact hit i hi
  · exact h

/-! ### Ideas 12, 14, 15, 20: values of algebraic families are sparse in a window -/

/-- Bernoulli's inequality in `ℕ`. -/
theorem pow_succ_ge (a k : ℕ) : a ^ (k + 1) + (k + 1) * a ^ k ≤ (a + 1) ^ (k + 1) := by
  induction k with
  | zero => simp
  | succ k ih =>
    have h := Nat.mul_le_mul_right (a + 1) ih
    have e1 : (a + 1) ^ (k + 1 + 1) = (a + 1) ^ (k + 1) * (a + 1) := pow_succ _ _
    have e2 : (a ^ (k + 1) + (k + 1) * a ^ k) * (a + 1) =
        a ^ (k + 1 + 1) + (k + 1 + 1) * a ^ (k + 1) + (k + 1) * a ^ k := by ring
    rw [e1]
    rw [e2] at h
    exact le_trans (Nat.le_add_right _ _) h

/-- **Ideas 12, 14, 15, 20.** Two different `(k+1)`-st powers in a window of length `Q`:
then `(k + 1) · a^k ≤ Q` for the smaller base `a`. Above that size a window holds at most
one of them, so a row cannot be written as such a power in two ways and the rows of this
shape are counted by the bases. -/
theorem pow_window {a b k Q : ℕ} (hab : a < b) (h : b ^ (k + 1) ≤ a ^ (k + 1) + Q) :
    (k + 1) * a ^ k ≤ Q := by
  have h1 : (a + 1) ^ (k + 1) ≤ b ^ (k + 1) := Nat.pow_le_pow_left hab _
  have h2 := pow_succ_ge a k
  linarith

/-- **Idea 15.** Two terms `u < v` of a sequence that at least doubles, in a window of length
`Q`: then `u ≤ Q`. Above `Q` a window holds at most one term of a Lucas sequence. -/
theorem doubling_window {u v Q : ℕ} (h2 : 2 * u ≤ v) (hw : v ≤ u + Q) : u ≤ Q := by omega

/-! ### Idea 24: parity -/

/-- **Idea 24.** For odd `N` every odd row is even, hence composite when it exceeds 2: the
game is trivial for odd `N`. -/
theorem odd_N_trivial {N q : ℕ} (hN : Odd N) (hq : Odd q) (h : 2 < N - q) :
    ¬ (N - q).Prime := by
  intro hp
  have he : Even (N - q) := Nat.Odd.sub_odd hN hq
  have := (Nat.Prime.even_iff hp).mp he
  omega

/-- For even `N` no power of two divides an odd row: nothing survives of parity modulo 4, 8,
… . -/
theorem two_pow_not_dvd_row {N q j : ℕ} (hN : Even N) (hq : Odd q) (hqN : q ≤ N)
    (hj : 0 < j) : ¬ 2 ^ j ∣ N - q := by
  intro h
  have h2 : 2 ∣ N - q := (dvd_pow_self 2 hj.ne').trans h
  have h3 := Nat.Even.sub_odd hqN hN hq
  rw [Nat.odd_iff] at h3
  omega

/-! ### Idea 44: linear combinations of members -/

/-- **Idea 44.** A combination `a N₁ + c N₂` of two numbers in the class `b` modulo `r`
stays in that class when `a + c ≡ 1`. Over all moduli of a cover this says the combination
is another member of the same progression, nothing new. -/
theorem affine_combination {N₁ N₂ b a c r : ℕ} (h1 : N₁ ≡ b [MOD r]) (h2 : N₂ ≡ b [MOD r])
    (hac : a + c ≡ 1 [MOD r]) : a * N₁ + c * N₂ ≡ b [MOD r] := by
  have h3 := (Nat.ModEq.mul_left a h1).add (Nat.ModEq.mul_left c h2)
  have h4 : a * b + c * b ≡ 1 * b [MOD r] := by
    rw [← add_mul]
    exact hac.mul_right b
  simpa using h3.trans h4

/-! ### Ideas 43, 73, 97, 100: prescribing residues -/

/-- **Ideas 43, 73 and 97.** Below `X`, at most `X / ∏ S + 1` numbers have prescribed
residues on pairwise coprime moduli `S`. Merging two covers multiplies the moduli; a special
form such as `2^664 - δ` with small `δ` meets a deep cover in at most one number. -/
theorem card_prescribed_le (S : Finset ℕ) (b : ℕ → ℕ) (X : ℕ) (hpos : ∀ r ∈ S, 0 < r)
    (hcop : (S : Set ℕ).Pairwise Nat.Coprime) :
    #{N ∈ range X | ∀ r ∈ S, N % r = b r} ≤ X / (∏ r ∈ S, r) + 1 := by
  have := Cap.card_residues_in_le S (fun r => {b r}) X hpos hcop
  simpa using this

/-- **Idea 100.** Whatever the mechanism, a divisor that serves two rows is below `Q`
(`Cap.lt_of_dvd_two_rows`), so divisors `≥ Q` serve one row each. Prescribing such divisors
for `|S|` rows leaves at most `X / Q^|S| + 1` numbers below `X`. -/
theorem large_divisor_budget (S : Finset ℕ) (b : ℕ → ℕ) (X Q : ℕ) (hQ : 0 < Q)
    (hbig : ∀ r ∈ S, Q ≤ r) (hcop : (S : Set ℕ).Pairwise Nat.Coprime) :
    #{N ∈ range X | ∀ r ∈ S, N % r = b r} ≤ X / Q ^ S.card + 1 := by
  have h1 := card_prescribed_le S b X (fun r hr => lt_of_lt_of_le hQ (hbig r hr)) hcop
  have h2 : Q ^ S.card ≤ ∏ r ∈ S, r := by
    rw [← Finset.prod_const]
    exact Finset.prod_le_prod hbig
  have h3 : X / (∏ r ∈ S, r) ≤ X / Q ^ S.card :=
    Nat.div_le_div_left h2 (Nat.pos_of_ne_zero (pow_ne_zero _ hQ.ne'))
  omega

/-- With the numbers of the 10% target: 38 pairwise coprime divisors `≥ 213070`, one for each
of 38 rows, already determine `N < 10^200`. A mechanism made of large divisors has to make
them dependent on each other, as a polynomial identity does (`Cap.card_le_sqrt_succ`). -/
theorem large_divisors_unique (S : Finset ℕ) (b : ℕ → ℕ) (hbig : ∀ r ∈ S, 213070 ≤ r)
    (hcop : (S : Set ℕ).Pairwise Nat.Coprime) (hcard : 38 ≤ S.card) :
    #{N ∈ range (10 ^ 200) | ∀ r ∈ S, N % r = b r} ≤ 1 := by
  have h1 := large_divisor_budget S b (10 ^ 200) 213070 (by norm_num) hbig hcop
  have h2 : (213070 : ℕ) ^ 38 ≤ 213070 ^ S.card := Nat.pow_le_pow_right (by norm_num) hcard
  have h3 : (10 : ℕ) ^ 200 < 213070 ^ 38 := by norm_num
  have h4 : 10 ^ 200 / 213070 ^ S.card = 0 := Nat.div_eq_of_lt (lt_of_lt_of_le h3 h2)
  omega

/-! ### Idea 70: unions of families -/

/-- **Idea 70.** A family that is a union of parts (progressions with a common modulus, say)
has at most the success density of its best part. A set cut out by residue conditions on
moduli of product at most `X` cannot beat the best single progression. -/
theorem union_density {ι : Type*} (parts : Finset ι) (size hits : ι → ℝ) (ρ : ℝ)
    (h : ∀ i ∈ parts, hits i ≤ ρ * size i) :
    ∑ i ∈ parts, hits i ≤ ρ * ∑ i ∈ parts, size i := by
  rw [Finset.mul_sum]
  exact Finset.sum_le_sum h

end GoldbachGaps.Brainstorm
