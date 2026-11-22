import GoldbachGaps.Basic

/-!
# The capped game: the first-moment law for covers

Fix a finite set `S` of moduli (odd primes in the application) and a finite set `P` of rows,
none divisible by any modulus (in the application: the primes `q < Q` outside `S`). A
*nonzero residue vector* `b` chooses a residue `b r ∈ [1, r)` for every `r ∈ S`; the row `q`
is *left* by `b` if `q mod r ≠ b r` for all `r ∈ S` (no modulus kills it).

* `sum_card_rowsLeft` – **first-moment law**: summed over all nonzero residue vectors, the
  number of rows left is exactly `|P| · ∏ (r - 2)`. There are `∏ (r - 1)` vectors
  (`card_vectors`), so the average number of rows left is `|P| · ∏ (r - 2)/(r - 1)`, for every
  set of rows whatever.
* `exists_rowsLeft_le` – hence some vector leaves at most the average (the pigeonhole
  existence statement for covers), and `exists_le_rowsLeft` – some vector leaves at least the
  average.
* `noFreeLunch` – the rows left are prime with probability proportional to the *boost*
  `∏ r/(r - 1)`, because they are coprime to every modulus. The average of
  `rows left × boost` is `|P| · ∏ (1 - 1/(r - 1)²)`, which is at least `|P| / 2` for every
  set of moduli `≥ 3` (`prod_pred_sq_le`; the product over all odd primes is the twin prime
  constant `C₂ = 0.66…`, and `2 C₂ = 1.32` is the constant of the cost model
  `E = 1.32 · φ · π(Q) / ln N` once the factor 2 of the modulus 2 is included).

In words: averaged over residue vectors, the modulus budget cancels out of the exponent of
the search. Whatever a cover gains, it gains as the deviation of one vector from this
average; the factor `φ` of the cost model is that deviation and nothing else.
-/

namespace GoldbachGaps.Cap

open Finset

/-- The nonzero residue vectors on the moduli `S`: a residue in `[1, r)` for each `r ∈ S`. -/
def vectors (S : Finset ℕ) : Finset ((r : ℕ) → r ∈ S → ℕ) :=
  S.pi fun r => Ico 1 r

/-- The rows of `P` that the vector `b` leaves: `q mod r ≠ b r` for every `r ∈ S`. -/
def rowsLeft (S P : Finset ℕ) (b : (r : ℕ) → r ∈ S → ℕ) : Finset ℕ :=
  {q ∈ P | ∀ r (h : r ∈ S), q % r ≠ b r h}

theorem card_vectors (S : Finset ℕ) : #(vectors S) = ∏ r ∈ S, (r - 1) := by
  simp [vectors, Finset.card_pi, Nat.card_Ico]

/-- A row not divisible by any modulus is left by exactly `∏ (r - 2)` vectors. -/
theorem card_vectors_leaving (S : Finset ℕ) (hpos : ∀ r ∈ S, 0 < r) {q : ℕ}
    (hq : ∀ r ∈ S, ¬ r ∣ q) :
    #{b ∈ vectors S | ∀ r (h : r ∈ S), q % r ≠ b r h} = ∏ r ∈ S, (r - 2) := by
  have key : {b ∈ vectors S | ∀ r (h : r ∈ S), q % r ≠ b r h} =
      S.pi fun r => (Ico 1 r).erase (q % r) := by
    ext b
    simp only [vectors, mem_filter, mem_pi, mem_erase, mem_Ico]
    constructor
    · rintro ⟨h1, h2⟩ r hr
      exact ⟨fun h => h2 r hr h.symm, h1 r hr⟩
    · intro h
      exact ⟨fun r hr => (h r hr).2, fun r hr heq => (h r hr).1 heq.symm⟩
  rw [key, Finset.card_pi]
  refine Finset.prod_congr rfl fun r hr => ?_
  have hmem : q % r ∈ Ico 1 r := by
    rw [mem_Ico]
    refine ⟨?_, Nat.mod_lt _ (hpos r hr)⟩
    rcases Nat.eq_zero_or_pos (q % r) with h0 | hp
    · exact absurd (Nat.dvd_of_mod_eq_zero h0) (hq r hr)
    · exact hp
  rw [Finset.card_erase_of_mem hmem, Nat.card_Ico]
  omega

/-- **First-moment law.** Summed over all nonzero residue vectors, the number of rows left
is exactly `|P| · ∏ (r - 2)`. -/
theorem sum_card_rowsLeft (S P : Finset ℕ) (hpos : ∀ r ∈ S, 0 < r)
    (hP : ∀ q ∈ P, ∀ r ∈ S, ¬ r ∣ q) :
    ∑ b ∈ vectors S, #(rowsLeft S P b) = #P * ∏ r ∈ S, (r - 2) := by
  simp only [rowsLeft, Finset.card_filter]
  rw [Finset.sum_comm]
  have key : ∀ q ∈ P,
      (∑ b ∈ vectors S, if ∀ r (h : r ∈ S), q % r ≠ b r h then 1 else 0) =
        ∏ r ∈ S, (r - 2) := by
    intro q hq
    rw [← Finset.card_filter, card_vectors_leaving S hpos (hP q hq)]
  rw [Finset.sum_congr rfl key, Finset.sum_const, smul_eq_mul]

/-- The first-moment law in the form used by the two pigeonhole statements. -/
theorem sum_card_rowsLeft_mul (S P : Finset ℕ) (hpos : ∀ r ∈ S, 0 < r)
    (hP : ∀ q ∈ P, ∀ r ∈ S, ¬ r ∣ q) :
    ∑ b ∈ vectors S, #(rowsLeft S P b) * ∏ r ∈ S, (r - 1) =
      ∑ _b ∈ vectors S, #P * ∏ r ∈ S, (r - 2) := by
  rw [← Finset.sum_mul (vectors S) (fun b => #(rowsLeft S P b)), sum_card_rowsLeft S P hpos hP,
    Finset.sum_const, card_vectors, smul_eq_mul]
  ring

theorem vectors_nonempty (S : Finset ℕ) (hS : ∀ r ∈ S, 2 ≤ r) : (vectors S).Nonempty := by
  rw [← Finset.card_pos, card_vectors]
  exact Finset.prod_pos fun r hr => by
    have := hS r hr
    omega

/-- **Pigeonhole for covers.** Some nonzero residue vector leaves at most the average number
of rows: `rows left · ∏ (r - 1) ≤ |P| · ∏ (r - 2)`. -/
theorem exists_rowsLeft_le (S P : Finset ℕ) (hS : ∀ r ∈ S, 2 ≤ r)
    (hP : ∀ q ∈ P, ∀ r ∈ S, ¬ r ∣ q) :
    ∃ b ∈ vectors S, #(rowsLeft S P b) * ∏ r ∈ S, (r - 1) ≤ #P * ∏ r ∈ S, (r - 2) :=
  Finset.exists_le_of_sum_le (vectors_nonempty S hS)
    (f := fun b => #(rowsLeft S P b) * ∏ r ∈ S, (r - 1))
    (g := fun _ => #P * ∏ r ∈ S, (r - 2))
    (le_of_eq (sum_card_rowsLeft_mul S P (fun r hr => by
      have := hS r hr
      omega) hP))

/-- Some nonzero residue vector leaves at least the average number of rows. -/
theorem exists_le_rowsLeft (S P : Finset ℕ) (hS : ∀ r ∈ S, 2 ≤ r)
    (hP : ∀ q ∈ P, ∀ r ∈ S, ¬ r ∣ q) :
    ∃ b ∈ vectors S, #P * ∏ r ∈ S, (r - 2) ≤ #(rowsLeft S P b) * ∏ r ∈ S, (r - 1) :=
  Finset.exists_le_of_sum_le (vectors_nonempty S hS)
    (f := fun _ => #P * ∏ r ∈ S, (r - 2))
    (g := fun b => #(rowsLeft S P b) * ∏ r ∈ S, (r - 1))
    (le_of_eq (sum_card_rowsLeft_mul S P (fun r hr => by
      have := hS r hr
      omega) hP).symm)

/-- Auxiliary form of `prod_pred_sq_le`, with a telescoping bound `n` on the moduli. -/
theorem prod_pred_sq_le_aux (S : Finset ℕ) :
    (∀ r ∈ S, 3 ≤ r) → ∀ n, 2 ≤ n → (∀ r ∈ S, r ≤ n) →
      n * ∏ r ∈ S, (r - 1) ^ 2 ≤ 2 * (n - 1) * ∏ r ∈ S, (r * (r - 2)) := by
  induction S using Finset.induction_on_max with
  | empty =>
    intro _ n hn _
    simp only [Finset.prod_empty, mul_one]
    omega
  | insert a S ha ih =>
    intro h3 n hn hle
    have haS : a ∉ S := fun h => lt_irrefl a (ha a h)
    rw [Finset.prod_insert haS, Finset.prod_insert haS]
    have ha3 : 3 ≤ a := h3 a (Finset.mem_insert_self a S)
    have han : a ≤ n := hle a (Finset.mem_insert_self a S)
    have IH := ih (fun r hr => h3 r (Finset.mem_insert_of_mem hr)) (a - 1) (by omega)
      (fun r hr => by
        have := ha r hr
        omega)
    generalize (∏ r ∈ S, (r - 1) ^ 2) = A at IH ⊢
    generalize (∏ r ∈ S, (r * (r - 2))) = B at IH ⊢
    obtain ⟨d, rfl⟩ : ∃ d, a = d + 3 := ⟨a - 3, by omega⟩
    obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
    have e1 : d + 3 - 1 = d + 2 := by omega
    have e2 : d + 2 - 1 = d + 1 := by omega
    have e3 : d + 3 - 2 = d + 1 := by omega
    have e4 : m + 1 - 1 = m := by omega
    rw [e1, e2] at IH
    rw [e1, e3, e4]
    have hdm : (m + 1) * (d + 2) ≤ m * (d + 3) := by
      have h1 : (m + 1) * (d + 2) = m * d + 2 * m + d + 2 := by ring
      have h2 : m * (d + 3) = m * d + 3 * m := by ring
      omega
    calc (m + 1) * ((d + 2) ^ 2 * A) = (m + 1) * (d + 2) * ((d + 2) * A) := by ring
      _ ≤ (m + 1) * (d + 2) * (2 * (d + 1) * B) := Nat.mul_le_mul_left _ IH
      _ ≤ m * (d + 3) * (2 * (d + 1) * B) := Nat.mul_le_mul_right _ hdm
      _ = 2 * m * ((d + 3) * (d + 1) * B) := by ring

/-- For any finite set of moduli `≥ 3`: `∏ (r - 1)² ≤ 2 · ∏ r (r - 2)`, that is
`∏ (1 - 1/(r - 1)²) ≥ 1/2`. -/
theorem prod_pred_sq_le (S : Finset ℕ) (hS : ∀ r ∈ S, 3 ≤ r) :
    ∏ r ∈ S, (r - 1) ^ 2 ≤ 2 * ∏ r ∈ S, (r * (r - 2)) := by
  have h := prod_pred_sq_le_aux S hS (S.sup id + 2) (by omega) (fun r hr => by
    have : r ≤ S.sup id := Finset.le_sup (f := id) hr
    omega)
  generalize (∏ r ∈ S, (r - 1) ^ 2) = A at h ⊢
  generalize (∏ r ∈ S, (r * (r - 2))) = B at h ⊢
  generalize S.sup id = s at h
  have e : s + 2 - 1 = s + 1 := by omega
  rw [e] at h
  have h2 : 2 * (s + 1) * B ≤ (s + 2) * (2 * B) := by
    have : 2 * (s + 1) * B = (s + 1) * (2 * B) := by ring
    rw [this]
    exact Nat.mul_le_mul_right _ (by omega)
  exact Nat.le_of_mul_le_mul_left (h.trans h2) (by omega)

/-- **No free lunch.** For moduli `≥ 3` and rows not divisible by any of them, the average
over nonzero residue vectors of `rows left × ∏ r/(r - 1)` is at least `|P| / 2`:
`|P| · (number of vectors) · ∏ (r - 1) ≤ 2 · (Σ_b rows left) · ∏ r`. No choice of moduli
improves the average. -/
theorem noFreeLunch (S P : Finset ℕ) (hS : ∀ r ∈ S, 3 ≤ r)
    (hP : ∀ q ∈ P, ∀ r ∈ S, ¬ r ∣ q) :
    #P * (#(vectors S) * ∏ r ∈ S, (r - 1)) ≤
      2 * ((∑ b ∈ vectors S, #(rowsLeft S P b)) * ∏ r ∈ S, r) := by
  rw [sum_card_rowsLeft S P (fun r hr => by
    have := hS r hr
    omega) hP, card_vectors]
  have h := prod_pred_sq_le S hS
  rw [Finset.prod_pow, Finset.prod_mul_distrib] at h
  generalize (∏ r ∈ S, (r - 1)) = V at h ⊢
  generalize (∏ r ∈ S, (r - 2)) = W at h ⊢
  generalize (∏ r ∈ S, r) = R at h ⊢
  calc #P * (V * V) = #P * V ^ 2 := by ring
    _ ≤ #P * (2 * (R * W)) := Nat.mul_le_mul_left _ h
    _ = 2 * (#P * W * R) := by ring

end GoldbachGaps.Cap
