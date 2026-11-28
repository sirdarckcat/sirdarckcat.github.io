import GoldbachGaps.RankPatterns

/-!
# A prime sieve on bitmasks, for the kernel

To prove a statement about *every* even `N` below a few million ("each has a Goldbach summand
at most `G`") the kernel has to see the primes of a whole interval. Testing the numbers one by
one is too slow; this file does it with a few thousand operations on big natural numbers, which
the kernel evaluates with multi-precision arithmetic.

* `multMask d i`: the number whose binary digits are `1` exactly at the multiples of `d` below
  `d · 2^i` (built by doubling); `classMask a d i`: the same shifted, so that the digit `j` is
  `1` iff `d ∣ a + j`.
* `segSieve a L ds`: start from `L` ones and clear, for each `d` of the list, the digits `j`
  with `d ∣ a + j`. If the list holds every prime below `D` and `a + L ≤ D²`, a digit `j` that
  is still `1` means that `a + j` is prime (`prime_of_testBit_segSieve`). Nothing is claimed in
  the other direction, and nothing is needed.
* `unionShift S qs`: the union of the masks `S <<< q`. Its digit `j` is `1` only if `a + j - q`
  is prime for some `q` of the list.
* `specCheck`, `segCheck`: the Boolean test that every `N` of `[A, B)` divisible by `m` has its
  digit set in the union for the `q ≤ G`, and `holds_of_segCheck`: then every such `N` has a
  Goldbach summand `q ≤ G` (`Holds (A, B, m, G)`).
* `tinyCheck`, `holds_of_tinyCheck`: the same below `4096` by trial division.
* `sievePrimesBelow D`: the primes below `D ≤ 5929` by trial division, with
  `mem_sievePrimesBelow`.
* `isChain`, `exists_mem_of_isChain`, `summand_of_chain`: consecutive intervals cover their
  union.
* `NotAmongTen`, `notAmongTen_of_chain`: no multiple of `m` in the range of a chain enters the
  ten largest least summands, as soon as each interval of the chain has ten certified numbers
  below it whose least summand is at least its bound.
* `IsRecordHolder`, `isRecordHolder_of_mem`, `mem_of_isRecordHolder`: a table of numbers with
  their least summands is the complete list of record holders below `X` as soon as a chain of
  proved statements "every even `N` of `[A, B)` has a summand at most `G`" carries, on each
  interval, the value of the last table entry.

`GoldbachGaps/RankSieveData.lean` (generated) applies this to `[6, 2^25)`.
-/

namespace GoldbachGaps.BitSieve

/-- Binary digits `1` exactly at the multiples `0, d, 2d, …` of `d` below `d · 2^i`. -/
def multMask (d : ℕ) : ℕ → ℕ
  | 0 => 1
  | i + 1 => multMask d i ||| (multMask d i <<< (d * 2 ^ i))

theorem testBit_multMask {d : ℕ} (hd : 0 < d) :
    ∀ i j : ℕ, (multMask d i).testBit j = decide (d ∣ j ∧ j < d * 2 ^ i)
  | 0, j => by
    have h1 : (1 : ℕ) = 2 ^ 0 := rfl
    rw [multMask, h1, Nat.testBit_two_pow, pow_zero, mul_one]
    apply Bool.eq_iff_iff.mpr
    simp only [decide_eq_true_eq]
    constructor
    · rintro rfl
      exact ⟨dvd_zero d, hd⟩
    · rintro ⟨h, hlt⟩
      exact (Nat.eq_zero_of_dvd_of_lt h hlt).symm
  | i + 1, j => by
    rw [multMask, Nat.testBit_or, Nat.testBit_shiftLeft, testBit_multMask hd i j,
      testBit_multMask hd i (j - d * 2 ^ i)]
    have hS : d ∣ d * 2 ^ i := Dvd.intro _ rfl
    have h2 : d * 2 ^ (i + 1) = 2 * (d * 2 ^ i) := by ring
    rw [h2]
    generalize d * 2 ^ i = S at hS ⊢
    apply Bool.eq_iff_iff.mpr
    simp only [Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq, ge_iff_le]
    constructor
    · rintro (⟨h, hlt⟩ | ⟨hle, h, hlt⟩)
      · exact ⟨h, by omega⟩
      · refine ⟨?_, by omega⟩
        have := Dvd.dvd.add h hS
        rwa [Nat.sub_add_cancel hle] at this
    · rintro ⟨h, hlt⟩
      rcases Nat.lt_or_ge j S with hj | hj
      · exact Or.inl ⟨h, hj⟩
      · exact Or.inr ⟨hj, Nat.dvd_sub h hS, by omega⟩

/-- Binary digit `j` is `1` iff `d ∣ a + j`, for the `j` below `d · 2^i` (at least). -/
def classMask (a d i : ℕ) : ℕ := multMask d i <<< ((d - a % d) % d)

theorem dvd_add_classShift (a : ℕ) {d : ℕ} (hd : 0 < d) : d ∣ a + (d - a % d) % d := by
  rcases Nat.eq_zero_or_pos (a % d) with h | h
  · rw [h, Nat.sub_zero, Nat.mod_self, Nat.add_zero]
    exact Nat.dvd_of_mod_eq_zero h
  · have hlt : a % d < d := Nat.mod_lt _ hd
    rw [Nat.mod_eq_of_lt (by omega)]
    have hdm := Nat.div_add_mod a d
    refine ⟨a / d + 1, ?_⟩
    rw [Nat.mul_add, Nat.mul_one]
    omega

theorem testBit_classMask {a d i j : ℕ} (hd : 0 < d) (hj : j < d * 2 ^ i) :
    (classMask a d i).testBit j = decide (d ∣ a + j) := by
  have hr_lt : (d - a % d) % d < d := Nat.mod_lt _ hd
  have hdvd : d ∣ a + (d - a % d) % d := dvd_add_classShift a hd
  rw [classMask, Nat.testBit_shiftLeft, testBit_multMask hd]
  generalize (d - a % d) % d = r at hr_lt hdvd ⊢
  apply Bool.eq_iff_iff.mpr
  simp only [Bool.and_eq_true, decide_eq_true_eq, ge_iff_le]
  constructor
  · rintro ⟨hrj, hdj, _⟩
    have h : a + j = (a + r) + (j - r) := by omega
    rw [h]
    exact Dvd.dvd.add hdvd hdj
  · intro h
    have hrj : r ≤ j := by
      by_contra hlt
      have h1 : d ∣ (a + r) - (a + j) := Nat.dvd_sub hdvd h
      have h2 : (a + r) - (a + j) = r - j := by omega
      rw [h2] at h1
      have := Nat.le_of_dvd (by omega) h1
      omega
    refine ⟨hrj, ?_, by omega⟩
    have h1 : d ∣ (a + j) - (a + r) := Nat.dvd_sub h hdvd
    have h2 : (a + j) - (a + r) = j - r := by omega
    rwa [h2] at h1

/-- The number of doublings after which the mask of `d` reaches `L` digits: `d · 2^(lvl L d)`
is at least `L` (and below `2 L` when `d < L`); checked where it is used, not proved. -/
def lvl (L d : ℕ) : ℕ := Nat.log2 ((L - 1) / d) + 1

/-- One pass of the sieve of the segment `[a, a + L)`: clear the digits `j` with `d ∣ a + j`. -/
def segPass (a L : ℕ) (P d : ℕ) : ℕ := P ^^^ (P &&& classMask a d (lvl L d))

theorem testBit_segPass (a L P d j : ℕ) :
    (segPass a L P d).testBit j = (P.testBit j && !(classMask a d (lvl L d)).testBit j) := by
  simp only [segPass, Nat.testBit_xor, Nat.testBit_and]
  cases P.testBit j <;> cases (classMask a d (lvl L d)).testBit j <;> rfl

/-- The sieve of the segment `[a, a + L)` by the numbers of the list. -/
def segSieve (a L : ℕ) (ds : List ℕ) : ℕ := ds.foldl (segPass a L) (2 ^ L - 1)

theorem testBit_foldl_segPass {a L j : ℕ} : ∀ (ds : List ℕ) (P : ℕ),
    (ds.foldl (segPass a L) P).testBit j = true →
      P.testBit j = true ∧ ∀ d ∈ ds, (classMask a d (lvl L d)).testBit j = false
  | [], P, h => ⟨h, by simp⟩
  | d :: ds, P, h => by
    rw [List.foldl_cons] at h
    obtain ⟨h1, h2⟩ := testBit_foldl_segPass ds _ h
    rw [testBit_segPass, Bool.and_eq_true, Bool.not_eq_true'] at h1
    refine ⟨h1.1, fun d' hd' => ?_⟩
    rcases List.mem_cons.mp hd' with rfl | hd'
    · exact h1.2
    · exact h2 d' hd'

/-- Each mask of a pass reaches the end of the segment. -/
def reachOK (L : ℕ) (ds : List ℕ) : Bool :=
  ds.all fun d => decide (0 < d) && decide (L ≤ d * 2 ^ lvl L d)

theorem not_dvd_of_testBit_segSieve {a L j : ℕ} {ds : List ℕ} (hr : reachOK L ds = true)
    (h : (segSieve a L ds).testBit j = true) : j < L ∧ ∀ d ∈ ds, ¬ d ∣ a + j := by
  obtain ⟨h1, h2⟩ := testBit_foldl_segPass ds _ h
  rw [Nat.testBit_two_pow_sub_one, decide_eq_true_eq] at h1
  refine ⟨h1, fun d hd hdvd => ?_⟩
  have hc := List.all_eq_true.mp hr d hd
  rw [Bool.and_eq_true, decide_eq_true_eq, decide_eq_true_eq] at hc
  have h3 := h2 d hd
  rw [testBit_classMask hc.1 (lt_of_lt_of_le h1 hc.2), decide_eq_false_iff_not] at h3
  exact h3 hdvd

/-- **A digit left by the sieve is a prime.** If the list holds every prime below `D` and the
segment `[a, a + L)` ends at or below `D²`, then a digit `j` equal to `1` in `segSieve` means
that `a + j` is prime. -/
theorem prime_of_testBit_segSieve {a L j D : ℕ} {ds : List ℕ} (hr : reachOK L ds = true)
    (hds : ∀ p, p.Prime → p < D → p ∈ ds) (hD : a + L ≤ D * D) (ha : 2 ≤ a)
    (h : (segSieve a L ds).testBit j = true) : (a + j).Prime := by
  obtain ⟨hj, hnd⟩ := not_dvd_of_testBit_segSieve hr h
  by_contra hnp
  have hp : (a + j).minFac.Prime := Nat.minFac_prime (by omega)
  have hsq : (a + j).minFac ^ 2 ≤ a + j := Nat.minFac_sq_le_self (by omega) hnp
  have hlt : (a + j).minFac < D := by
    by_contra hge
    have hge : D ≤ (a + j).minFac := Nat.le_of_not_lt hge
    have : D * D ≤ (a + j).minFac ^ 2 := by
      rw [sq]
      exact Nat.mul_le_mul hge hge
    omega
  exact hnd _ (hds _ hp hlt) (Nat.minFac_dvd _)

/-- The union of the masks `S <<< q`, `q` in the list. -/
def unionShift (S : ℕ) (qs : List ℕ) : ℕ := qs.foldl (fun U q => U ||| (S <<< q)) 0

theorem testBit_foldl_unionShift {S j : ℕ} : ∀ (qs : List ℕ) (U : ℕ),
    (qs.foldl (fun U q => U ||| (S <<< q)) U).testBit j = true →
      U.testBit j = true ∨ ∃ q ∈ qs, q ≤ j ∧ S.testBit (j - q) = true
  | [], U, h => Or.inl h
  | q :: qs, U, h => by
    rw [List.foldl_cons] at h
    rcases testBit_foldl_unionShift qs _ h with h | ⟨q', hq', h⟩
    · rw [Nat.testBit_or, Bool.or_eq_true, Nat.testBit_shiftLeft, Bool.and_eq_true,
        decide_eq_true_eq] at h
      rcases h with h | ⟨h1, h2⟩
      · exact Or.inl h
      · exact Or.inr ⟨q, List.mem_cons_self, h1, h2⟩
    · exact Or.inr ⟨q', List.mem_cons_of_mem _ hq', h⟩

theorem testBit_unionShift {S j : ℕ} {qs : List ℕ} (h : (unionShift S qs).testBit j = true) :
    ∃ q ∈ qs, q ≤ j ∧ S.testBit (j - q) = true := by
  rcases testBit_foldl_unionShift qs 0 h with h | h
  · rw [Nat.zero_testBit] at h
    exact absurd h (by decide)
  · exact h

/-- The digits `j` with `A ≤ a + j < B` and `m ∣ a + j`. -/
def specMask (a L A B m : ℕ) : ℕ :=
  classMask a m (lvl L m) &&& ((2 ^ (B - A) - 1) <<< (A - a))

/-- A statement `(A, B, m, G)`: every `N` of `[A, B)` divisible by `m` has a Goldbach summand
at most `G`. -/
def Holds (s : ℕ × ℕ × ℕ × ℕ) : Prop :=
  ∀ N, s.1 ≤ N → N < s.2.1 → s.2.2.1 ∣ N → ∃ q, q ≤ s.2.2.2 ∧ IsSummand N q

/-- The test of one statement `(A, B, m, G)` on the prime mask `S` of the segment
`[a, a + L)`: every digit of `specMask` is in the union of the `S <<< q`, `q ≤ G`. -/
def specCheck (a L S : ℕ) (qs : List ℕ) (s : ℕ × ℕ × ℕ × ℕ) : Bool :=
  decide (a ≤ s.1) && decide (s.2.1 ≤ a + L) && decide (0 < s.2.2.1) &&
    decide (L ≤ s.2.2.1 * 2 ^ lvl L s.2.2.1) &&
    decide (specMask a L s.1 s.2.1 s.2.2.1 &&& unionShift S (qs.filter (· ≤ s.2.2.2)) =
      specMask a L s.1 s.2.1 s.2.2.1)

theorem specCheck_sound {a L S : ℕ} {qs : List ℕ} {s : ℕ × ℕ × ℕ × ℕ}
    (h : specCheck a L S qs s = true) {N : ℕ} (hA : s.1 ≤ N) (hB : N < s.2.1)
    (hm : s.2.2.1 ∣ N) :
    ∃ q ∈ qs, q ≤ s.2.2.2 ∧ q ≤ N - a ∧ S.testBit (N - a - q) = true := by
  simp only [specCheck, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩ := h
  have hK : (specMask a L s.1 s.2.1 s.2.2.1).testBit (N - a) = true := by
    rw [specMask, Nat.testBit_and, testBit_classMask h3 (by omega), Nat.testBit_shiftLeft,
      Nat.testBit_two_pow_sub_one]
    have h6 : a + (N - a) = N := by omega
    rw [h6]
    simp only [Bool.and_eq_true, decide_eq_true_eq, ge_iff_le]
    exact ⟨hm, by omega, by omega⟩
  have hU := congrArg (fun x => x.testBit (N - a)) h5
  simp only [Nat.testBit_and, hK, Bool.true_and] at hU
  obtain ⟨q, hq, hqj, hS⟩ := testBit_unionShift hU
  rw [List.mem_filter, decide_eq_true_eq] at hq
  exact ⟨q, hq.1, hq.2, hqj, hS⟩

/-- The test of a segment: sieve `[a, a + L)` by `ds` and test every statement of the list. -/
def segCheck (a L D : ℕ) (ds qs : List ℕ) (specs : List (ℕ × ℕ × ℕ × ℕ)) : Bool :=
  decide (2 ≤ a) && decide (a + L ≤ D * D) && reachOK L ds &&
    specs.all (specCheck a L (segSieve a L ds) qs)

/-- **Soundness of the segment test.** If `ds` holds every prime below `D` and the `qs` are
prime, a successful test proves every statement of the list. -/
theorem holds_of_segCheck {a L D : ℕ} {ds qs : List ℕ} {specs : List (ℕ × ℕ × ℕ × ℕ)}
    (hds : ∀ p, p.Prime → p < D → p ∈ ds) (hqs : ∀ q ∈ qs, q.Prime)
    (h : segCheck a L D ds qs specs = true) : ∀ s ∈ specs, Holds s := by
  simp only [segCheck, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨ha, hD⟩, hr⟩, hall⟩ := h
  intro s hs N hA hB hm
  have hs' := List.all_eq_true.mp hall s hs
  obtain ⟨q, hq, hqG, hqj, hS⟩ := specCheck_sound hs' hA hB hm
  have hprime := prime_of_testBit_segSieve hr hds hD ha hS
  have ha1 : a ≤ s.1 := by
    simp only [specCheck, Bool.and_eq_true, decide_eq_true_eq] at hs'
    exact hs'.1.1.1.1
  have h6 : a + (N - a - q) = N - q := by omega
  rw [h6] at hprime
  exact ⟨q, hqG, hqs q hq, hprime⟩

/-- The same test below `4096`, by trial division. -/
def tinyCheck (qs : List ℕ) (s : ℕ × ℕ × ℕ × ℕ) : Bool :=
  decide (s.2.1 ≤ 4096) && (List.range' s.1 (s.2.1 - s.1)).all fun N =>
    decide (N % s.2.2.1 ≠ 0) ||
      (qs.filter (· ≤ s.2.2.2)).any fun q => decide (q ≤ N) && isPrimeBelow4096 (N - q)

theorem holds_of_tinyCheck {qs : List ℕ} {s : ℕ × ℕ × ℕ × ℕ} (hqs : ∀ q ∈ qs, q.Prime)
    (h : tinyCheck qs s = true) : Holds s := by
  simp only [tinyCheck, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨hB4, hall⟩ := h
  intro N hA hB hm
  have hN : N ∈ List.range' s.1 (s.2.1 - s.1) := by
    rw [List.mem_range'_1]
    omega
  have h1 := List.all_eq_true.mp hall N hN
  rw [Bool.or_eq_true, decide_eq_true_eq] at h1
  rcases h1 with h1 | h1
  · exact absurd (Nat.mod_eq_zero_of_dvd hm) h1
  · obtain ⟨q, hq, h2⟩ := List.any_eq_true.mp h1
    rw [List.mem_filter, decide_eq_true_eq] at hq
    rw [Bool.and_eq_true, decide_eq_true_eq] at h2
    exact ⟨q, hq.2, hqs q hq.1, (prime_iff_isPrimeBelow4096 (by omega)).mpr h2.2⟩

/-- The primes below `D` (for `D ≤ 5929 = 77²`), by trial division by `2, …, 76`. -/
def sievePrimesBelow (D : ℕ) : List ℕ :=
  (List.range D).filter fun d =>
    decide (2 ≤ d) && (List.range' 2 75).all fun t => !(decide (t < d) && d % t == 0)

theorem mem_sievePrimesBelow {D : ℕ} (hD : D ≤ 5929) {p : ℕ} :
    p ∈ sievePrimesBelow D ↔ p.Prime ∧ p < D := by
  simp only [sievePrimesBelow, List.mem_filter, List.mem_range, Bool.and_eq_true,
    decide_eq_true_eq, List.all_eq_true, List.mem_range'_1, Bool.not_eq_true',
    Bool.and_eq_false_iff, decide_eq_false_iff_not, beq_eq_false_iff_ne, ne_eq]
  constructor
  · rintro ⟨hlt, h2, hall⟩
    refine ⟨?_, hlt⟩
    by_contra hnp
    have hp : p.minFac.Prime := Nat.minFac_prime (by omega)
    have hsq : p.minFac ^ 2 ≤ p := Nat.minFac_sq_le_self (by omega) hnp
    have h77 : p.minFac < 77 := by
      by_contra hge
      have hge : 77 ≤ p.minFac := Nat.le_of_not_lt hge
      have : 77 * 77 ≤ p.minFac ^ 2 := by
        rw [sq]
        exact Nat.mul_le_mul hge hge
      omega
    have hltp : p.minFac < p := by
      have h2' := hp.two_le
      have : p.minFac * 2 ≤ p.minFac ^ 2 := by
        rw [sq]
        exact Nat.mul_le_mul_left _ h2'
      omega
    rcases hall p.minFac ⟨hp.two_le, by omega⟩ with h | h
    · exact h hltp
    · exact h (Nat.mod_eq_zero_of_dvd (Nat.minFac_dvd p))
  · rintro ⟨hp, hlt⟩
    refine ⟨hlt, hp.two_le, fun t ht => ?_⟩
    by_cases htp : t < p
    · refine Or.inr fun h0 => ?_
      rcases (Nat.dvd_prime hp).mp (Nat.dvd_of_mod_eq_zero h0) with h | h <;> omega
    · exact Or.inl htp

/-- Consecutive statements: the first starts at or below `lo`, each next one where the
previous ends, and the last ends at or beyond `hi`. -/
def isChain : ℕ → ℕ → List (ℕ × ℕ × ℕ × ℕ) → Bool
  | lo, hi, [] => decide (hi ≤ lo)
  | lo, hi, s :: t => decide (s.1 ≤ lo) && isChain s.2.1 hi t

theorem exists_mem_of_isChain : ∀ (l : List (ℕ × ℕ × ℕ × ℕ)) (lo hi : ℕ),
    isChain lo hi l = true → ∀ N, lo ≤ N → N < hi → ∃ s ∈ l, s.1 ≤ N ∧ N < s.2.1
  | [], lo, hi, h, N, h1, h2 => by
    rw [isChain, decide_eq_true_eq] at h
    omega
  | s :: t, lo, hi, h, N, h1, h2 => by
    rw [isChain, Bool.and_eq_true, decide_eq_true_eq] at h
    rcases Nat.lt_or_ge N s.2.1 with hN | hN
    · exact ⟨s, List.mem_cons_self, by omega, hN⟩
    · obtain ⟨s', hs', h3⟩ := exists_mem_of_isChain t s.2.1 hi h.2 N hN h2
      exact ⟨s', List.mem_cons_of_mem _ hs', h3⟩

/-- Every statement of the list has modulus `m` and bound at most `G`. -/
def shapeOK (m G : ℕ) (l : List (ℕ × ℕ × ℕ × ℕ)) : Bool :=
  l.all fun s => decide (s.2.2.1 = m) && decide (s.2.2.2 ≤ G)

/-- A chain of proved statements with modulus `m` and bounds at most `G` gives the bound `G`
on the whole interval. -/
theorem summand_of_chain {l : List (ℕ × ℕ × ℕ × ℕ)} {lo hi m G : ℕ}
    (hc : isChain lo hi l = true) (hl : ∀ s ∈ l, Holds s) (hshape : shapeOK m G l = true)
    {N : ℕ} (h1 : lo ≤ N) (h2 : N < hi) (hm : m ∣ N) : ∃ q, q ≤ G ∧ IsSummand N q := by
  obtain ⟨s, hs, hA, hB⟩ := exists_mem_of_isChain l lo hi hc N h1 h2
  have h := List.all_eq_true.mp hshape s hs
  rw [Bool.and_eq_true, decide_eq_true_eq, decide_eq_true_eq] at h
  obtain ⟨q, hq, hsum⟩ := hl s hs N hA hB (h.1 ▸ hm)
  exact ⟨q, le_trans hq h.2, hsum⟩

end GoldbachGaps.BitSieve

namespace GoldbachGaps

open BitSieve

/-- `N` is a *record holder*: its least Goldbach summand is larger than that of every smaller
even number from `6` on. -/
def IsRecordHolder (N : ℕ) : Prop :=
  ∃ g, IsLeastSummand N g ∧ ∀ M, Even M → 6 ≤ M → M < N → ∃ q, q < g ∧ IsSummand M q

/-- The least Goldbach summand of `N` is at most that of `M` (said without naming either). -/
def LeastSummandLE (N M : ℕ) : Prop := ∀ q, IsSummand M q → ∃ q', q' ≤ q ∧ IsSummand N q'

/-- `N` does not enter the ten largest least Goldbach summands when it appears: ten smaller
even numbers (from `6` on) have a least summand at least as large as that of `N`. -/
def NotAmongTen (N : ℕ) : Prop :=
  ∃ l : List ℕ, l.Nodup ∧ l.length = 10 ∧
    ∀ M ∈ l, Even M ∧ 6 ≤ M ∧ M < N ∧ LeastSummandLE N M

namespace BitSieve

/-- The table has distinct even numbers from `6` on, and for every statement of the chain ten
of them lie below its start with a value at least its bound. -/
def tenOK (l : List (ℕ × ℕ × ℕ × ℕ)) (T : List (ℕ × ℕ)) : Bool :=
  decide (T.map Prod.fst).Nodup && (T.all fun x => decide (x.1 % 2 = 0) && decide (6 ≤ x.1)) &&
    l.all fun s =>
      decide (10 ≤ (T.filter fun x => decide (x.1 < s.1) && decide (s.2.2.2 ≤ x.2)).length)

/-- **Never among the ten largest.** If on each interval of a chain the multiples of `m` have
a summand at most `c`, and ten certified numbers below the interval have least summand at least
`c`, then no multiple of `m` in the range of the chain enters the ten largest. -/
theorem notAmongTen_of_chain {l : List (ℕ × ℕ × ℕ × ℕ)} {T : List (ℕ × ℕ)} {lo hi m G : ℕ}
    (hc : isChain lo hi l = true) (hl : ∀ s ∈ l, Holds s) (hshape : shapeOK m G l = true)
    (hT : ∀ x ∈ T, IsLeastSummand x.1 x.2) (hok : tenOK l T = true) {N : ℕ} (h1 : lo ≤ N)
    (h2 : N < hi) (hm : m ∣ N) : NotAmongTen N := by
  obtain ⟨s, hs, hA, hB⟩ := exists_mem_of_isChain l lo hi hc N h1 h2
  have hsh := List.all_eq_true.mp hshape s hs
  rw [Bool.and_eq_true, decide_eq_true_eq, decide_eq_true_eq] at hsh
  simp only [tenOK, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hok
  obtain ⟨⟨hnd, hT2⟩, hten⟩ := hok
  have hlen := hten s hs
  obtain ⟨q', hq', hsum'⟩ := hl s hs N hA hB (hsh.1 ▸ hm)
  refine ⟨((T.filter fun x => decide (x.1 < s.1) && decide (s.2.2.2 ≤ x.2)).take 10).map
    Prod.fst, ?_, ?_, ?_⟩
  · exact hnd.sublist (((List.take_sublist 10 _).trans List.filter_sublist).map Prod.fst)
  · rw [List.length_map, List.length_take]
    omega
  · intro M hM
    obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hM
    have hxF := List.mem_of_mem_take hx
    rw [List.mem_filter, Bool.and_eq_true, decide_eq_true_eq, decide_eq_true_eq] at hxF
    obtain ⟨hxT, hxlt, hxG⟩ := hxF
    have h3 := hT2 x hxT
    refine ⟨Nat.even_iff.mpr h3.1, h3.2, by omega, fun q hq => ?_⟩
    have := (hT x hxT).2 q hq
    exact ⟨q', by omega, hsum'⟩

/-- Every statement of the chain is about the even numbers and carries the value of a table
entry at or before its start. -/
def recLinkOK (l : List (ℕ × ℕ × ℕ × ℕ)) (T : List (ℕ × ℕ)) : Bool :=
  l.all fun s => decide (s.2.2.1 = 2) &&
    T.any fun x => decide (x.1 ≤ s.1) && decide (x.2 = s.2.2.2)

/-- Every table entry is an even number in `[6, X]`, and every statement of the chain that
starts before it has a smaller bound. -/
def recTableOK (X : ℕ) (l : List (ℕ × ℕ × ℕ × ℕ)) (T : List (ℕ × ℕ)) : Bool :=
  T.all fun x => decide (x.1 ≤ X) && decide (x.1 % 2 = 0) && decide (6 ≤ x.1) &&
    l.all fun s => !decide (s.1 < x.1) || decide (s.2.2.2 < x.2)

/-- The entries of the table are record holders. -/
theorem isRecordHolder_of_mem {l : List (ℕ × ℕ × ℕ × ℕ)} {T : List (ℕ × ℕ)} {X : ℕ}
    (hc : isChain 6 X l = true) (hl : ∀ s ∈ l, Holds s) (hlink : recLinkOK l T = true)
    (hT : ∀ x ∈ T, IsLeastSummand x.1 x.2) (hok : recTableOK X l T = true) :
    ∀ x ∈ T, IsRecordHolder x.1 := by
  intro x hx
  have hx' := List.all_eq_true.mp hok x hx
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, Bool.or_eq_true,
    Bool.not_eq_true', decide_eq_false_iff_not] at hx'
  obtain ⟨⟨⟨hxX, _⟩, _⟩, hlt⟩ := hx'
  refine ⟨x.2, hT x hx, fun M hE h6 hM => ?_⟩
  obtain ⟨s, hs, hA, hB⟩ := exists_mem_of_isChain l 6 X hc M h6 (by omega)
  have hs' := List.all_eq_true.mp hlink s hs
  rw [Bool.and_eq_true, decide_eq_true_eq] at hs'
  obtain ⟨q, hq, hsum⟩ := hl s hs M hA hB (hs'.1 ▸ hE.two_dvd)
  rcases hlt s hs with h | h
  · exact absurd (by omega : s.1 < x.1) h
  · exact ⟨q, by omega, hsum⟩

/-- A record holder below `X` is an entry of the table. -/
theorem mem_of_isRecordHolder {l : List (ℕ × ℕ × ℕ × ℕ)} {T : List (ℕ × ℕ)} {X : ℕ}
    (hc : isChain 6 X l = true) (hl : ∀ s ∈ l, Holds s) (hlink : recLinkOK l T = true)
    (hT : ∀ x ∈ T, IsLeastSummand x.1 x.2) (hok : recTableOK X l T = true) {N : ℕ}
    (hE : Even N) (h6 : 6 ≤ N) (hX : N < X) (h : IsRecordHolder N) : N ∈ T.map Prod.fst := by
  obtain ⟨g, hg, hall⟩ := h
  obtain ⟨s, hs, hA, hB⟩ := exists_mem_of_isChain l 6 X hc N h6 hX
  have hs' := List.all_eq_true.mp hlink s hs
  rw [Bool.and_eq_true, decide_eq_true_eq] at hs'
  obtain ⟨x, hx, hx2⟩ := List.any_eq_true.mp hs'.2
  rw [Bool.and_eq_true, decide_eq_true_eq, decide_eq_true_eq] at hx2
  obtain ⟨q, hq, hsum⟩ := hl s hs N hA hB (hs'.1 ▸ hE.two_dvd)
  have hgq : g ≤ q := hg.2 q hsum
  by_contra hnot
  have hne : x.1 ≠ N := fun h => hnot (List.mem_map.mpr ⟨x, hx, h⟩)
  have hx' := List.all_eq_true.mp hok x hx
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hx'
  obtain ⟨⟨⟨_, hx2'⟩, hx6⟩, _⟩ := hx'
  obtain ⟨q', hq', hsum'⟩ := hall x.1 (Nat.even_iff.mpr hx2') hx6 (by omega)
  have := (hT x hx).2 q' hsum'
  omega

end BitSieve

end GoldbachGaps
