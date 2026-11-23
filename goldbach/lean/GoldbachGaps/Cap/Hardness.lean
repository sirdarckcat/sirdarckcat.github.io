import GoldbachGaps.CoverDepth
import Mathlib.Data.Nat.ChineseRemainder
import Mathlib.NumberTheory.Bertrand

/-!
# Finding a covering residue vector is as hard as satisfiability

The cover stage of the search asks: given moduli and rows, choose one residue class per modulus
so that every row lies in the chosen class of some modulus (`CoverDepth.CoversList`), or as many
rows as possible. Equivalently: find a number `N` such that every row `q` has `N - q` divisible
by one of the moduli.

This file proves that, **for arbitrary rows, this question contains the satisfiability of
Boolean formulas.** From a formula in conjunctive normal form with `n` variables and `m`
clauses it builds `n` prime moduli and `m (n + 1)` rows, of size polynomial in the formula, such
that

  the formula is satisfiable  ↔  some residue vector covers every row  ↔  some `N` does

(`sat_iff_coversList`, `sat_iff_exists_number`), and the depth-first search of
`GoldbachGaps/CoverDepth.lean`, run on these rows, decides the formula (`sat_iff_search`).

Construction. Variable `i` gets a prime `p_i` larger than every residue used. Clause `j` gets
`n + 1` rows; each shows to `p_i` the residue `1` if the clause contains the variable `i`, `0`
if it contains its negation, and otherwise a dummy value that belongs to this row alone. A
satisfying assignment is the vector with classes `0` and `1`. Conversely a covering vector may
spend the class of a variable on one dummy value, but a clause has `n + 1` rows with different
dummy values and there are only `n` variables, so one of its rows is covered through a literal.

What this says about the search, and what it does not. A method that finds covering vectors
(or the best vector, or the best `N`) for *arbitrary* lists of rows would decide satisfiability,
so no method that treats the rows as arbitrary data can be fast in general, unless every
problem in NP is easy. Together with `Cap/BlackBox.lean` (a method that only asks "how good is
this member?" cannot beat enumeration) this leaves one kind of method that could do better than
the present search: one that uses the fact that the rows are the *primes* below the target.
For that special case nothing is proved here, and nothing of the kind is known.
-/

namespace GoldbachGaps.Cap.Hardness

open GoldbachGaps.CoverDepth

/-- A literal: a variable and a sign (`true` for the variable, `false` for its negation). -/
abbrev Literal := ℕ × Bool

/-- An assignment satisfies a formula in conjunctive normal form (a list of clauses, each a list
of literals) when every clause contains a literal that it makes true. -/
def Satisfies (τ : ℕ → Bool) (φ : List (List Literal)) : Prop :=
  ∀ C ∈ φ, ∃ l ∈ C, τ l.1 = l.2

/-- The `i`-th prime above `B`. -/
def bigPrime (B : ℕ) : ℕ → ℕ
  | 0 => Nat.find (Nat.exists_infinite_primes (B + 1))
  | i + 1 => Nat.find (Nat.exists_infinite_primes (bigPrime B i + 1))

theorem bigPrime_prime (B : ℕ) : ∀ i, (bigPrime B i).Prime
  | 0 => (Nat.find_spec (Nat.exists_infinite_primes (B + 1))).2
  | i + 1 => (Nat.find_spec (Nat.exists_infinite_primes (bigPrime B i + 1))).2

theorem bigPrime_lt_succ (B i : ℕ) : bigPrime B i < bigPrime B (i + 1) :=
  (Nat.find_spec (Nat.exists_infinite_primes (bigPrime B i + 1))).1

theorem bigPrime_strictMono (B : ℕ) : StrictMono (bigPrime B) :=
  strictMono_nat_of_lt_succ (bigPrime_lt_succ B)

theorem lt_bigPrime (B : ℕ) : ∀ i, B < bigPrime B i
  | 0 => (Nat.find_spec (Nat.exists_infinite_primes (B + 1))).1
  | i + 1 => lt_trans (lt_bigPrime B i) (bigPrime_lt_succ B i)

/-- The moduli are small: the `i`-th is at most `2^(i+1) (B + 1)` (Bertrand's postulate). -/
theorem bigPrime_le (B : ℕ) : ∀ i, bigPrime B i ≤ 2 ^ (i + 1) * (B + 1)
  | 0 => by
    obtain ⟨p, hp, hlt, hle⟩ := Nat.exists_prime_lt_and_le_two_mul (B + 1) (by omega)
    have h := Nat.find_min' (Nat.exists_infinite_primes (B + 1)) ⟨hlt.le, hp⟩
    have e : bigPrime B 0 = Nat.find (Nat.exists_infinite_primes (B + 1)) := rfl
    rw [e]
    omega
  | i + 1 => by
    have ih := bigPrime_le B i
    obtain ⟨p, hp, hlt, hle⟩ :=
      Nat.exists_prime_lt_and_le_two_mul (bigPrime B i) (bigPrime_prime B i).pos.ne'
    have h := Nat.find_min' (Nat.exists_infinite_primes (bigPrime B i + 1)) ⟨hlt, hp⟩
    have e : bigPrime B (i + 1) = Nat.find (Nat.exists_infinite_primes (bigPrime B i + 1)) := rfl
    rw [e]
    calc Nat.find (Nat.exists_infinite_primes (bigPrime B i + 1)) ≤ p := h
      _ ≤ 2 * bigPrime B i := hle
      _ ≤ 2 * (2 ^ (i + 1) * (B + 1)) := Nat.mul_le_mul_left 2 ih
      _ = 2 ^ (i + 1 + 1) * (B + 1) := by ring

theorem coprime_bigPrime (B n : ℕ) :
    (List.range n).Pairwise (Function.onFun Nat.Coprime (bigPrime B)) := by
  refine List.pairwise_lt_range.imp ?_
  intro i j hij
  exact (Nat.coprime_primes (bigPrime_prime B i) (bigPrime_prime B j)).mpr
    (bigPrime_strictMono B hij).ne

/-- The residue that a row of the clause `C` shows to variable `i`: `1` if `C` contains the
variable, `0` if it contains its negation, and the dummy value `d` otherwise. -/
def res (C : List Literal) (d i : ℕ) : ℕ :=
  if (i, true) ∈ C then 1 else if (i, false) ∈ C then 0 else d

theorem res_lt {C : List Literal} {d i B : ℕ} (hd : d < B) (hB : 2 ≤ B) : res C d i < B := by
  unfold res
  split_ifs <;> omega

/-- A row of a clause: the number with residue `res C d i` modulo the `i`-th prime. -/
def row (B n : ℕ) (C : List Literal) (d : ℕ) : ℕ :=
  (Nat.chineseRemainderOfList (res C d) (bigPrime B) (List.range n) (coprime_bigPrime B n) : ℕ)

theorem row_modEq (B n : ℕ) (C : List Literal) (d : ℕ) {i : ℕ} (hi : i < n) :
    row B n C d ≡ res C d i [MOD bigPrime B i] :=
  (Nat.chineseRemainderOfList (res C d) (bigPrime B) (List.range n) (coprime_bigPrime B n)).2 i
    (List.mem_range.mpr hi)

/-- Every residue used is below this bound. -/
def bound (φ : List (List Literal)) (n : ℕ) : ℕ := 2 + φ.length * (n + 1)

/-- The moduli: one prime above the bound for each of the `n` variables. -/
def mods (φ : List (List Literal)) (n : ℕ) : List ℕ :=
  (List.range n).map (bigPrime (bound φ n))

/-- The rows: `n + 1` for each clause, with different dummy values. -/
def rows (φ : List (List Literal)) (n : ℕ) : List ℕ :=
  (List.range φ.length).flatMap fun j =>
    (List.range (n + 1)).map fun c => row (bound φ n) n (φ.getD j []) (2 + j * (n + 1) + c)

theorem length_mods (φ : List (List Literal)) (n : ℕ) : (mods φ n).length = n := by
  simp [mods]

theorem prime_of_mem_mods (φ : List (List Literal)) (n : ℕ) {r : ℕ} (hr : r ∈ mods φ n) :
    r.Prime := by
  obtain ⟨i, -, rfl⟩ := List.mem_map.mp hr
  exact bigPrime_prime _ i

theorem nodup_mods (φ : List (List Literal)) (n : ℕ) : (mods φ n).Nodup :=
  List.Nodup.map (bigPrime_strictMono _).injective List.nodup_range

theorem mem_rows {φ : List (List Literal)} {n q : ℕ} :
    q ∈ rows φ n ↔ ∃ j < φ.length, ∃ c < n + 1,
      row (bound φ n) n (φ.getD j []) (2 + j * (n + 1) + c) = q := by
  simp only [rows, List.mem_flatMap, List.mem_range, List.mem_map]

theorem dummy_lt {φ : List (List Literal)} {n j c : ℕ} (hj : j < φ.length) (hc : c < n + 1) :
    2 + j * (n + 1) + c < bound φ n := by
  unfold bound
  have h : (j + 1) * (n + 1) ≤ φ.length * (n + 1) := Nat.mul_le_mul_right _ hj
  have e : (j + 1) * (n + 1) = j * (n + 1) + (n + 1) := by ring
  omega

/-- **Satisfiability reduces to covering.** A formula in conjunctive normal form over the
variables `0, …, n - 1` (no clause containing a variable together with its negation) is
satisfiable exactly when some residue vector on the moduli `mods φ n` covers every row of
`rows φ n`. -/
theorem sat_iff_coversList (φ : List (List Literal)) (n : ℕ)
    (hvars : ∀ C ∈ φ, ∀ l ∈ C, l.1 < n)
    (hcons : ∀ C ∈ φ, ∀ i, ¬ ((i, true) ∈ C ∧ (i, false) ∈ C)) :
    (∃ τ, Satisfies τ φ) ↔ CoversList (mods φ n) (rows φ n) := by
  classical
  constructor
  · rintro ⟨τ, hτ⟩
    refine ⟨fun r => if ∃ i, i < n ∧ bigPrime (bound φ n) i = r ∧ τ i = true then 1 else 0,
      fun q hq => ?_⟩
    obtain ⟨j, hj, c, -, rfl⟩ := mem_rows.mp hq
    have hCmem : φ.getD j [] ∈ φ := by
      rw [List.getD_eq_getElem _ _ hj]
      exact List.getElem_mem hj
    generalize φ.getD j [] = C at hCmem ⊢
    obtain ⟨⟨i, b⟩, hl, hτl⟩ := hτ _ hCmem
    have hi : i < n := hvars _ hCmem _ hl
    refine ⟨bigPrime (bound φ n) i, List.mem_map.mpr ⟨i, List.mem_range.mpr hi, rfl⟩, ?_⟩
    refine (row_modEq (bound φ n) n _ _ hi).trans ?_
    have hτi : τ i = b := hτl
    cases b with
    | true =>
      have h1 : res C (2 + j * (n + 1) + c) i = 1 := by
        unfold res
        simp only [hl, ↓reduceIte]
      have h2 : ∃ i', i' < n ∧ bigPrime (bound φ n) i' = bigPrime (bound φ n) i ∧ τ i' = true :=
        ⟨i, hi, rfl, hτi⟩
      simp only [h1, h2, ↓reduceIte]
      exact Nat.ModEq.refl _
    | false =>
      have hnt : (i, true) ∉ C := fun h => hcons _ hCmem i ⟨h, hl⟩
      have h1 : res C (2 + j * (n + 1) + c) i = 0 := by
        unfold res
        simp only [hnt, hl, ↓reduceIte]
      have h2 : ¬ ∃ i', i' < n ∧ bigPrime (bound φ n) i' = bigPrime (bound φ n) i ∧
          τ i' = true := by
        rintro ⟨i', -, he, ht⟩
        have e := (bigPrime_strictMono (bound φ n)).injective he
        rw [e, hτi] at ht
        exact absurd ht (by simp)
      simp only [h1, h2, ↓reduceIte]
      exact Nat.ModEq.refl _
  · rintro ⟨a, ha⟩
    refine ⟨fun i => decide (a (bigPrime (bound φ n) i) % bigPrime (bound φ n) i = 1),
      fun C hC => ?_⟩
    by_contra hno
    have hno' : ∀ l ∈ C,
        decide (a (bigPrime (bound φ n) l.1) % bigPrime (bound φ n) l.1 = 1) ≠ l.2 :=
      fun l hl h => hno ⟨l, hl, h⟩
    obtain ⟨j, hj, hjC⟩ := List.getElem_of_mem hC
    have hget : φ.getD j [] = C := by rw [List.getD_eq_getElem _ _ hj, hjC]
    -- every one of the `n + 1` rows of the clause is covered through a dummy value
    have key : ∀ c : Fin (n + 1), ∃ i : Fin n,
        a (bigPrime (bound φ n) i) % bigPrime (bound φ n) i = 2 + j * (n + 1) + c := by
      intro c
      have hmem : row (bound φ n) n C (2 + j * (n + 1) + c) ∈ rows φ n :=
        mem_rows.mpr ⟨j, hj, c, c.2, by rw [hget]⟩
      obtain ⟨r, hr, hmod⟩ := ha _ hmem
      obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hr
      have hi' : i < n := List.mem_range.mp hi
      have h1 : res C (2 + j * (n + 1) + c) i ≡ a (bigPrime (bound φ n) i)
          [MOD bigPrime (bound φ n) i] :=
        (row_modEq (bound φ n) n C _ hi').symm.trans hmod
      have hlt : res C (2 + j * (n + 1) + c) i < bigPrime (bound φ n) i :=
        lt_trans (res_lt (dummy_lt hj c.2) (by unfold bound; omega)) (lt_bigPrime _ i)
      have h2 : a (bigPrime (bound φ n) i) % bigPrime (bound φ n) i =
          res C (2 + j * (n + 1) + c) i := by
        have h3 : res C (2 + j * (n + 1) + c) i % bigPrime (bound φ n) i =
            a (bigPrime (bound φ n) i) % bigPrime (bound φ n) i := h1
        rw [Nat.mod_eq_of_lt hlt] at h3
        exact h3.symm
      by_cases ht : (i, true) ∈ C
      · exfalso
        have e : a (bigPrime (bound φ n) i) % bigPrime (bound φ n) i = 1 := by
          rw [h2]
          unfold res
          simp only [ht, ↓reduceIte]
        exact hno' (i, true) ht (decide_eq_true e)
      by_cases hf : (i, false) ∈ C
      · exfalso
        have e : a (bigPrime (bound φ n) i) % bigPrime (bound φ n) i = 0 := by
          rw [h2]
          unfold res
          simp only [ht, hf, ↓reduceIte]
        refine hno' (i, false) hf ?_
        show decide (a (bigPrime (bound φ n) i) % bigPrime (bound φ n) i = 1) = false
        rw [e]
        rfl
      · refine ⟨⟨i, hi'⟩, ?_⟩
        show a (bigPrime (bound φ n) i) % bigPrime (bound φ n) i = 2 + j * (n + 1) + c
        rw [h2]
        unfold res
        simp only [ht, hf, ↓reduceIte]
    choose f hf using key
    obtain ⟨c, c', hne, hfc⟩ := Fintype.exists_ne_map_eq_of_card_lt f (by simp)
    have h1 := hf c
    have h2 := hf c'
    rw [hfc] at h1
    have e : (c : ℕ) = c' := by omega
    exact hne (Fin.ext e)

/-- The same with a number in place of the residue vector: the formula is satisfiable exactly
when some `N` is congruent to every row modulo one of the moduli (every `N - q` has one of the
moduli as a factor). -/
theorem sat_iff_exists_number (φ : List (List Literal)) (n : ℕ)
    (hvars : ∀ C ∈ φ, ∀ l ∈ C, l.1 < n)
    (hcons : ∀ C ∈ φ, ∀ i, ¬ ((i, true) ∈ C ∧ (i, false) ∈ C)) :
    (∃ τ, Satisfies τ φ) ↔ ∃ N, ∀ q ∈ rows φ n, ∃ r ∈ mods φ n, q ≡ N [MOD r] := by
  rw [sat_iff_coversList φ n hvars hcons]
  constructor
  · rintro ⟨a, ha⟩
    obtain ⟨N, hN⟩ := Nat.chineseRemainderOfList (fun i => a (bigPrime (bound φ n) i))
      (bigPrime (bound φ n)) (List.range n) (coprime_bigPrime _ n)
    refine ⟨N, fun q hq => ?_⟩
    obtain ⟨r, hr, hmod⟩ := ha q hq
    obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hr
    exact ⟨_, hr, hmod.trans (hN i hi).symm⟩
  · rintro ⟨N, hN⟩
    exact ⟨fun _ => N, hN⟩

/-- **The depth-first search of `CoverDepth` decides satisfiability** on the rows of the
formula. -/
theorem sat_iff_search (φ : List (List Literal)) (n : ℕ)
    (hvars : ∀ C ∈ φ, ∀ l ∈ C, l.1 < n)
    (hcons : ∀ C ∈ φ, ∀ i, ¬ ((i, true) ∈ C ∧ (i, false) ∈ C)) :
    (∃ τ, Satisfies τ φ) ↔ search n (mods φ n) (rows φ n) = true := by
  rw [sat_iff_coversList φ n hvars hcons,
    search_iff n _ _ (nodup_mods φ n) (length_mods φ n).le]

/-! ### The instance is of polynomial size -/

theorem length_rows (φ : List (List Literal)) (n : ℕ) :
    (rows φ n).length = φ.length * (n + 1) := by
  simp [rows, List.length_flatMap]

/-- Every modulus is at most `2^n (3 + m (n + 1))`, `m` the number of clauses: it has at most
`n` binary digits more than the number of rows. -/
theorem mods_le (φ : List (List Literal)) (n : ℕ) {r : ℕ} (hr : r ∈ mods φ n) :
    r ≤ 2 ^ n * (3 + φ.length * (n + 1)) := by
  obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hr
  have hi' : i + 1 ≤ n := List.mem_range.mp hi
  calc bigPrime (bound φ n) i ≤ 2 ^ (i + 1) * (bound φ n + 1) := bigPrime_le _ i
    _ ≤ 2 ^ n * (bound φ n + 1) :=
        Nat.mul_le_mul_right _ (Nat.pow_le_pow_right (by norm_num) hi')
    _ = 2 ^ n * (3 + φ.length * (n + 1)) := by unfold bound; ring

/-- Every row is below the product of the moduli. -/
theorem rows_lt (φ : List (List Literal)) (n : ℕ) {q : ℕ} (hq : q ∈ rows φ n) :
    q < (mods φ n).prod := by
  obtain ⟨j, -, c, -, rfl⟩ := mem_rows.mp hq
  exact Nat.chineseRemainderOfList_lt_prod _ _ _ _ fun i _ => (bigPrime_prime _ i).pos.ne'

end GoldbachGaps.Cap.Hardness
