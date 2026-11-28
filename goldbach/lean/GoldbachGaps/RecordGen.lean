import GoldbachGaps.BitSieve

/-!
# A generator for OEIS A025018, and the proof that it is correct

A025018: the even numbers `N ≥ 4` whose least Goldbach summand (least prime `q` with `N - q`
prime) is larger than that of every smaller even number; A025019 lists those summands.
`4, 6, 12, 30, 98, 220, 308, 556, 992, 2642, …` with `2, 3, 5, 7, 19, 23, 31, 47, 73, 103, …`.

`IsRecord N g` is that definition. `records X` is a program that builds the terms below `X`,
and `mem_records` proves, for every `X`,

  `(N, g) ∈ records X ↔ N < X ∧ IsRecord N g`,

with `records_sorted` saying that it lists them in increasing order. So `records X` *is* the
sequence below `X`, by a theorem about the program and not by a check of its output.

## The generator: a sieve of translates of the primes

Take the primes `q = 2, 3, 5, …` in order as *strikers*. The striker `q` strikes the numbers
`q + p`, `p` prime. The *front* is the smallest even number `≥ 4` that no striker has struck
yet. Then:

* if the next striker `q` hits the front `m` (`m - q` is prime), `m` is a term and `q` is its
  value, and the front moves to the next unstruck even number;
* if it misses (`m - q` is composite), nothing happens: the front waits for a later striker.
  That is why A025019 skips primes (`7` is followed by `19`: the strikers `11, 13, 17` miss
  the front `98`), and why every prime, also the skipped ones, must keep striking.

Trying to generate the first 2, 3, 4, 5, 6 terms by simpler rules fails each time at the next
term, and the failures are exactly these points (`scripts/record_gen/ladder.py`).

`isRecord_iff_front` is this principle as a statement: a term is a front that its striker
hits. The front depends on the striker alone (`IsFront.unique`), so the whole state of the
generator is one prime; the mask of struck numbers that the program carries is a cache.

## The program

Everything is done on bitmasks, i.e. on natural numbers read in binary, so that the kernel as
well as the compiler can run it:

* `primeMask X`: digit `j` is `1` iff `j` is a prime below `X` (`testBit_primeMask`; a sieve of
  Eratosthenes whose passes are `P xor (P and multiples)`, by the primes below a bound that it
  computes with itself, recursively);
* the struck numbers after the striker `q` are `U ||| (P <<< q)`;
* `nextFree` finds the next unstruck even number: a guess by binary search on the digits
  (`lowestZero`), which is then checked (`checkGuess`), with a plain search as fallback if the
  check should ever fail (it does not, but the proof does not need to know that).

`GoldbachGaps/RecordGenRun.lean` has the kernel run the generator up to `2^20` (21 terms);
`scripts/record_gen/Run.lean` evaluates it further (27 terms below `2^25` in 22 s).
-/

namespace GoldbachGaps

/-- **The record sequence.** `(N, g)` is a term of A025018 / A025019: `N ≥ 4` is even, `g` is
its least Goldbach summand, and every smaller even number from `4` on has a smaller one. -/
def IsRecord (N g : ℕ) : Prop :=
  Even N ∧ 4 ≤ N ∧ IsLeastSummand N g ∧
    ∀ M, Even M → 4 ≤ M → M < N → ∃ q, q < g ∧ IsSummand M q

/-- `N` is the *front* when the striker `g` arrives: the smallest even number `≥ 4` that no
prime below `g` has struck (`N - q` is not prime for the primes `q < g`). -/
def IsFront (g N : ℕ) : Prop :=
  Even N ∧ 4 ≤ N ∧ (∀ q < g, ¬ IsSummand N q) ∧
    ∀ M, Even M → 4 ≤ M → M < N → ∃ q, q < g ∧ IsSummand M q

/-- **The principle of the generator.** A term is a front that its striker hits: `(N, g)` is a
term of A025018 / A025019 iff `N` is the front when `g` arrives and `N - g` is prime. -/
theorem isRecord_iff_front {N g : ℕ} : IsRecord N g ↔ IsFront g N ∧ IsSummand N g := by
  constructor
  · rintro ⟨hE, h4, hl, hall⟩
    exact ⟨⟨hE, h4, fun q hq hs => by have := hl.2 q hs; omega, hall⟩, hl.1⟩
  · rintro ⟨⟨hE, h4, hfree, hall⟩, hs⟩
    exact ⟨hE, h4, ⟨hs, fun p hp => by
      by_contra hlt
      exact hfree p (by omega) hp⟩, hall⟩

/-- The front is determined by the striker alone: the state of the generator is one prime. -/
theorem IsFront.unique {g N N' : ℕ} (h : IsFront g N) (h' : IsFront g N') : N = N' := by
  obtain ⟨hE, h4, hfree, hall⟩ := h
  obtain ⟨hE', h4', hfree', hall'⟩ := h'
  rcases Nat.lt_trichotomy N N' with hlt | heq | hgt
  · obtain ⟨q, hq, hs⟩ := hall' N hE h4 hlt
    exact absurd hs (hfree q hq)
  · exact heq
  · obtain ⟨q, hq, hs⟩ := hall N' hE' h4' hgt
    exact absurd hs (hfree' q hq)

namespace RecordGen

open BitSieve

/-! ### The primes below `X` as a bitmask, exactly -/

theorem le_mul_two_pow_lvl (X : ℕ) {d : ℕ} (hd : 0 < d) : X ≤ d * 2 ^ lvl X d := by
  unfold lvl
  have h1 : (X - 1) / d < 2 ^ (((X - 1) / d).log2 + 1) := Nat.lt_log2_self
  have h2 := Nat.div_add_mod (X - 1) d
  have h3 : (X - 1) % d < d := Nat.mod_lt _ hd
  have h4 : d * ((X - 1) / d + 1) ≤ d * 2 ^ (((X - 1) / d).log2 + 1) :=
    Nat.mul_le_mul_left d h1
  rw [Nat.mul_add, Nat.mul_one] at h4
  omega

/-- One pass of the sieve of `[0, X)`: clear the multiples `2d, 3d, …` of `d`. -/
def pass (X P d : ℕ) : ℕ := P ^^^ (P &&& (multMask d (lvl X d) <<< (2 * d)))

theorem testBit_pass_of_false (X d : ℕ) {P j : ℕ} (h : P.testBit j = false) :
    (pass X P d).testBit j = false := by
  rw [pass, Nat.testBit_xor, Nat.testBit_and, h]
  rfl

theorem testBit_pass {X d : ℕ} (hd : 0 < d) (P : ℕ) {j : ℕ} (hj : j < X) :
    (pass X P d).testBit j = (P.testBit j && !decide (d ∣ j ∧ 2 * d ≤ j)) := by
  have hreach := le_mul_two_pow_lvl X hd
  have h2d : d ∣ 2 * d := Dvd.intro_left 2 rfl
  have hiff : (decide (j ≥ 2 * d) &&
      decide (d ∣ j - 2 * d ∧ j - 2 * d < d * 2 ^ lvl X d)) = decide (d ∣ j ∧ 2 * d ≤ j) := by
    apply Bool.eq_iff_iff.mpr
    simp only [Bool.and_eq_true, decide_eq_true_eq, ge_iff_le]
    constructor
    · rintro ⟨h2, h, _⟩
      refine ⟨?_, h2⟩
      have := Dvd.dvd.add h h2d
      rwa [Nat.sub_add_cancel h2] at this
    · rintro ⟨h, h2⟩
      exact ⟨h2, Nat.dvd_sub h h2d, by omega⟩
  rw [pass, Nat.testBit_xor, Nat.testBit_and, Nat.testBit_shiftLeft, testBit_multMask hd, hiff]
  cases P.testBit j <;> cases decide (d ∣ j ∧ 2 * d ≤ j) <;> rfl

theorem testBit_foldl_pass_of_false {X : ℕ} : ∀ (ds : List ℕ) (P j : ℕ),
    P.testBit j = false → (ds.foldl (pass X) P).testBit j = false
  | [], _, _, h => h
  | d :: ds, P, j, h => by
    rw [List.foldl_cons]
    exact testBit_foldl_pass_of_false ds _ j (testBit_pass_of_false X d h)

theorem testBit_foldl_pass {X : ℕ} : ∀ (ds : List ℕ) (P j : ℕ), (∀ d ∈ ds, 0 < d) → j < X →
    (ds.foldl (pass X) P).testBit j =
      (P.testBit j && ds.all fun d => !decide (d ∣ j ∧ 2 * d ≤ j))
  | [], P, j, _, _ => by simp
  | d :: ds, P, j, hds, hj => by
    rw [List.foldl_cons, testBit_foldl_pass ds _ j
      (fun d' hd' => hds d' (List.mem_cons_of_mem _ hd')) hj,
      testBit_pass (hds d List.mem_cons_self) P hj, List.all_cons, Bool.and_assoc]

/-- The sieve of `[0, X)` by the numbers of the list. -/
def sieveBy (X : ℕ) (ds : List ℕ) : ℕ := ds.foldl (pass X) ((2 ^ (X - 2) - 1) <<< 2)

theorem testBit_init (X j : ℕ) :
    ((2 ^ (X - 2) - 1) <<< 2).testBit j = decide (2 ≤ j ∧ j < X) := by
  rw [Nat.testBit_shiftLeft, Nat.testBit_two_pow_sub_one]
  apply Bool.eq_iff_iff.mpr
  simp only [Bool.and_eq_true, decide_eq_true_eq, ge_iff_le]
  omega

/-- **The sieve is exact.** If the list consists of numbers `≥ 2` and holds every prime `p`
with `p² < X`, the digit `j` of `sieveBy X ds` is `1` iff `j` is a prime below `X`. -/
theorem testBit_sieveBy {X : ℕ} {ds : List ℕ} (hds : ∀ d ∈ ds, 2 ≤ d)
    (hc : ∀ p, p.Prime → p * p < X → p ∈ ds) (j : ℕ) :
    (sieveBy X ds).testBit j = decide (j.Prime ∧ j < X) := by
  by_cases hj : 2 ≤ j ∧ j < X
  · rw [sieveBy, testBit_foldl_pass ds _ j (fun d hd => by have := hds d hd; omega) hj.2,
      testBit_init]
    apply Bool.eq_iff_iff.mpr
    simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, Bool.not_eq_true',
      decide_eq_false_iff_not]
    constructor
    · rintro ⟨_, hall⟩
      refine ⟨?_, hj.2⟩
      by_contra hnp
      have hp : j.minFac.Prime := Nat.minFac_prime (by omega)
      have hsq : j.minFac ^ 2 ≤ j := Nat.minFac_sq_le_self (by omega) hnp
      rw [sq] at hsq
      have hmem := hc _ hp (by omega)
      have h2 := hp.two_le
      have h3 : 2 * j.minFac ≤ j.minFac * j.minFac := Nat.mul_le_mul_right _ h2
      exact hall _ hmem ⟨Nat.minFac_dvd j, by omega⟩
    · rintro ⟨hp, _⟩
      refine ⟨hj, fun d hd hdj => ?_⟩
      have h2 := hds d hd
      rcases (Nat.dvd_prime hp).mp hdj.1 with h | h <;> omega
  · have hfalse : ((2 ^ (X - 2) - 1) <<< 2).testBit j = false := by
      rw [testBit_init, decide_eq_false_iff_not]
      exact hj
    rw [sieveBy, testBit_foldl_pass_of_false ds _ j hfalse]
    symm
    rw [decide_eq_false_iff_not]
    rintro ⟨hp, hlt⟩
    exact hj ⟨hp.two_le, hlt⟩

/-- Newton steps for `√X`. Only a guess: `sqrtBound` checks what it gets. -/
def newtonSqrt (X : ℕ) : ℕ → ℕ → ℕ
  | 0, s => s
  | f + 1, s => newtonSqrt X f ((s + X / s) / 2)

/-- A number `D ≥ 2` with `X < D²`: one more than the Newton guess for `√X` if that passes the
test, and a power of two otherwise. -/
def sqrtBound (X : ℕ) : ℕ :=
  if 2 ≤ newtonSqrt X 40 (2 ^ (X.log2 / 2 + 1)) + 1 ∧
      X < (newtonSqrt X 40 (2 ^ (X.log2 / 2 + 1)) + 1) *
        (newtonSqrt X 40 (2 ^ (X.log2 / 2 + 1)) + 1) then
    newtonSqrt X 40 (2 ^ (X.log2 / 2 + 1)) + 1
  else 2 ^ (X.log2 / 2 + 1)

theorem lt_sqrtBound_sq (X : ℕ) : X < sqrtBound X * sqrtBound X := by
  unfold sqrtBound
  split_ifs with h
  · exact h.2
  · have h1 : X < 2 ^ (X.log2 + 1) := Nat.lt_log2_self
    have h2 : 2 ^ (X.log2 + 1) ≤ 2 ^ (X.log2 / 2 + 1 + (X.log2 / 2 + 1)) :=
      Nat.pow_le_pow_right (by norm_num) (by omega)
    rw [← Nat.pow_add]
    exact lt_of_lt_of_le h1 h2

theorem two_le_sqrtBound (X : ℕ) : 2 ≤ sqrtBound X := by
  unfold sqrtBound
  split_ifs with h
  · exact h.1
  · calc 2 = 2 ^ 1 := rfl
      _ ≤ 2 ^ (X.log2 / 2 + 1) := Nat.pow_le_pow_right (by norm_num) (by omega)

/-- The primes below `X` as a bitmask. With fuel `f + 1` the sieving numbers are the primes
below `sqrtBound X`, taken from the same function with fuel `f`; with fuel `0` they are all
the numbers from `2` to `sqrtBound X`. The result does not depend on the fuel. -/
def primeMaskAux : ℕ → ℕ → ℕ
  | 0, X => sieveBy X (List.range' 2 (sqrtBound X - 2))
  | f + 1, X =>
    let S := primeMaskAux f (sqrtBound X)
    sieveBy X ((List.range' 2 (sqrtBound X - 2)).filter fun d => S.testBit d)

theorem testBit_primeMaskAux : ∀ f X j : ℕ,
    (primeMaskAux f X).testBit j = decide (j.Prime ∧ j < X)
  | 0, X, j => by
    refine testBit_sieveBy (fun d hd => (List.mem_range'_1.mp hd).1) (fun p hp hlt => ?_) j
    have h1 := lt_sqrtBound_sq X
    have h2 := two_le_sqrtBound X
    have hlt' : p < sqrtBound X := by
      by_contra hge
      have hge : sqrtBound X ≤ p := Nat.le_of_not_lt hge
      have := Nat.mul_le_mul hge hge
      omega
    rw [List.mem_range'_1]
    exact ⟨hp.two_le, by omega⟩
  | f + 1, X, j => by
    simp only [primeMaskAux]
    refine testBit_sieveBy (fun d hd => (List.mem_range'_1.mp (List.mem_of_mem_filter hd)).1)
      (fun p hp hlt => ?_) j
    have h1 := lt_sqrtBound_sq X
    have h2 := two_le_sqrtBound X
    have hlt' : p < sqrtBound X := by
      by_contra hge
      have hge : sqrtBound X ≤ p := Nat.le_of_not_lt hge
      have := Nat.mul_le_mul hge hge
      omega
    rw [List.mem_filter, testBit_primeMaskAux f, decide_eq_true_eq, List.mem_range'_1]
    exact ⟨⟨hp.two_le, by omega⟩, hp, hlt'⟩

/-- The primes below `X` as a bitmask. -/
def primeMask (X : ℕ) : ℕ := primeMaskAux 4 X

/-- **Digit `j` of `primeMask X` is `1` iff `j` is a prime below `X`.** -/
theorem testBit_primeMask (X j : ℕ) : (primeMask X).testBit j = decide (j.Prime ∧ j < X) :=
  testBit_primeMaskAux 4 X j

/-! ### The next unstruck even number -/

/-- The plain search: from `N` in steps of `2`, the first number that is `≥ X` or whose digit
in `U` is `0`. -/
def slowNext (X U : ℕ) : ℕ → ℕ → ℕ
  | 0, N => N
  | f + 1, N => if X ≤ N then N else if U.testBit N then slowNext X U f (N + 2) else N

theorem slowNext_spec (X U : ℕ) : ∀ f N : ℕ, X ≤ N + 2 * f →
    (∃ k, slowNext X U f N = N + 2 * k) ∧
      (slowNext X U f N < X → U.testBit (slowNext X U f N) = false) ∧
      ∀ k, N + 2 * k < slowNext X U f N → U.testBit (N + 2 * k) = true
  | 0, N, h => by
    simp only [slowNext]
    exact ⟨⟨0, rfl⟩, fun hlt => by omega, fun k hk => by omega⟩
  | f + 1, N, h => by
    simp only [slowNext]
    split_ifs with h1 h2
    · exact ⟨⟨0, rfl⟩, fun hlt => by omega, fun k hk => by omega⟩
    · obtain ⟨⟨k0, hk0⟩, h3, h4⟩ := slowNext_spec X U f (N + 2) (by omega)
      refine ⟨⟨k0 + 1, by omega⟩, h3, fun k hk => ?_⟩
      rcases Nat.eq_zero_or_pos k with rfl | hpos
      · simpa using h2
      · have := h4 (k - 1) (by omega)
        have e : N + 2 + 2 * (k - 1) = N + 2 * k := by omega
        rwa [e] at this
    · exact ⟨⟨0, rfl⟩, fun _ => by simpa using h2, fun k hk => by omega⟩

/-- Binary digits `1` at the odd positions (below `X`, at least). -/
def oddMask (X : ℕ) : ℕ := multMask 2 (lvl X 2) <<< 1

theorem odd_of_testBit_oddMask {X j : ℕ} (h : (oddMask X).testBit j = true) : ¬ Even j := by
  rw [oddMask, Nat.testBit_shiftLeft, testBit_multMask (by norm_num), Bool.and_eq_true,
    decide_eq_true_eq, decide_eq_true_eq] at h
  obtain ⟨h1, ⟨k, hk⟩, _⟩ := h
  rw [Nat.even_iff]
  omega

/-- The struck numbers, the odd numbers and everything up to `m`, in one mask: its lowest `0`
digit is the next unstruck even number after `m`. -/
def freeMask (X U m : ℕ) : ℕ := U ||| oddMask X ||| (2 ^ (m + 1) - 1)

/-- Binary search for the number of trailing `1` digits of `A`: starting from `lo` (below which
all digits are `1`), try to advance by `2^(k-1)`, `2^(k-2)`, …, `1`. -/
def trailingOnes (A : ℕ) : ℕ → ℕ → ℕ
  | 0, lo => lo
  | k + 1, lo =>
    if A % 2 ^ (lo + 2 ^ k) = 2 ^ (lo + 2 ^ k) - 1 then trailingOnes A k (lo + 2 ^ k)
    else trailingOnes A k lo

/-- The position of the lowest `0` digit of `A` (if it is below `2^(log₂ X + 1)`), as a guess:
nothing is proved about it, `checkGuess` verifies what it returns. -/
def lowestZero (X A : ℕ) : ℕ := trailingOnes A (X.log2 + 1) 0

/-- Use the guess `t` for the lowest `0` of `A` if it checks out: either the digits of `A` below
`X` are all `1` (nothing unstruck below `X`: answer some even number `≥ X`), or `t` is even,
beyond `m`, the digit `t` is `0` and all digits below `t` are `1`. Otherwise search. -/
def checkGuess (X U m A t : ℕ) : ℕ :=
  if decide (X ≤ t) && decide (A % 2 ^ X = 2 ^ X - 1) then 2 * (X + m + 1)
  else if decide (m < t) && decide (t % 2 = 0) && !A.testBit t &&
      decide (A % 2 ^ t = 2 ^ t - 1) then t
  else slowNext X U X (m + 2)

/-- **The next unstruck even number** after the even number `m`: the least even `N > m` below
`X` whose digit in `U` is `0`, or some even number `≥ X` if there is none. -/
def nextFree (X U m : ℕ) : ℕ :=
  checkGuess X U m (freeMask X U m) (lowestZero X (freeMask X U m))

/-- If the digits of `freeMask X U m` below `t` are all `1`, every even number between `m` and
`t` has its digit set in `U`. -/
theorem testBit_of_mod_eq {X U m t : ℕ} (h : freeMask X U m % 2 ^ t = 2 ^ t - 1) {N : ℕ}
    (hE : Even N) (hm : m < N) (ht : N < t) : U.testBit N = true := by
  have h1 := congrArg (fun x => x.testBit N) h
  simp only [freeMask, Nat.testBit_mod_two_pow, Nat.testBit_two_pow_sub_one, Nat.testBit_or, ht,
    decide_true, Bool.true_and] at h1
  have h2 : (oddMask X).testBit N = false := by
    by_contra hne
    exact odd_of_testBit_oddMask (by simpa using hne) hE
  have h3 : decide (N < m + 1) = false := by
    rw [decide_eq_false_iff_not]
    omega
  rw [h2, h3] at h1
  simpa using h1

/-- Whatever the guess `t`, the answer is right. -/
theorem checkGuess_spec {X U m : ℕ} (hm : Even m) (t : ℕ) :
    Even (checkGuess X U m (freeMask X U m) t) ∧ m < checkGuess X U m (freeMask X U m) t ∧
      (checkGuess X U m (freeMask X U m) t < X →
        U.testBit (checkGuess X U m (freeMask X U m) t) = false) ∧
      ∀ N, Even N → m < N → N < checkGuess X U m (freeMask X U m) t → N < X →
        U.testBit N = true := by
  unfold checkGuess
  split_ifs with h1 h2
  · rw [Bool.and_eq_true, decide_eq_true_eq, decide_eq_true_eq] at h1
    refine ⟨even_two_mul _, by omega, fun hlt => by omega, fun N hE hmN _ hNX => ?_⟩
    exact testBit_of_mod_eq h1.2 hE hmN hNX
  · simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.not_eq_true'] at h2
    obtain ⟨⟨⟨hmt, hpar⟩, hbit⟩, hmod⟩ := h2
    refine ⟨Nat.even_iff.mpr hpar, hmt, fun _ => ?_, fun N hE hmN hNt _ => ?_⟩
    · rw [freeMask, Nat.testBit_or, Nat.testBit_or, Bool.or_eq_false_iff,
        Bool.or_eq_false_iff] at hbit
      exact hbit.1.1
    · exact testBit_of_mod_eq hmod hE hmN hNt
  · obtain ⟨⟨k0, hk0⟩, h3, h4⟩ := slowNext_spec X U X (m + 2) (by omega)
    obtain ⟨c, hc⟩ := hm
    refine ⟨?_, by omega, h3, fun N hE hmN hNt _ => ?_⟩
    · rw [hk0, Nat.even_iff]
      omega
    · obtain ⟨b, hb⟩ := hE
      have := h4 (b - c - 1) (by omega)
      have e : m + 2 + 2 * (b - c - 1) = N := by omega
      rwa [e] at this

theorem nextFree_spec {X U m : ℕ} (hm : Even m) :
    Even (nextFree X U m) ∧ m < nextFree X U m ∧
      (nextFree X U m < X → U.testBit (nextFree X U m) = false) ∧
      ∀ N, Even N → m < N → N < nextFree X U m → N < X → U.testBit N = true :=
  checkGuess_spec hm _

/-! ### The generator -/

/-- The sieve of translates. State: the next striker candidate `q`, the front `m`, the mask `U`
of the numbers struck by the primes below `q`, and the terms found so far (latest first). -/
def loop (X P : ℕ) : ℕ → ℕ → ℕ → ℕ → List (ℕ × ℕ) → List (ℕ × ℕ)
  | 0, _, _, _, acc => acc.reverse
  | fuel + 1, q, m, U, acc =>
    if X ≤ m then acc.reverse
    else if P.testBit q then
      if decide (q ≤ m) && P.testBit (m - q) then
        loop X P fuel (q + 1) (nextFree X (U ||| (P <<< q)) m) (U ||| (P <<< q)) ((m, q) :: acc)
      else loop X P fuel (q + 1) m (U ||| (P <<< q)) acc
    else loop X P fuel (q + 1) m U acc

/-- **The generator.** The terms `(N, g)` of A025018 / A025019 with `N < X`, in order. -/
def records (X : ℕ) : List (ℕ × ℕ) := loop X (primeMask X) X 2 4 0 []

/-- What the state means, before the striker `q`. -/
structure Inv (X q m U : ℕ) (acc : List (ℕ × ℕ)) : Prop where
  struck : ∀ N < X, U.testBit N = true ↔ ∃ q' < q, IsSummand N q'
  even : Even m
  four : 4 ≤ m
  free : m < X → ∀ q' < q, ¬ IsSummand m q'
  least : ∀ N, Even N → 4 ≤ N → N < m → N < X → ∃ q' < q, IsSummand N q'
  acc_iff : ∀ N g, (N, g) ∈ acc ↔ N < X ∧ IsRecord N g ∧ g < q
  acc_lt : ∀ a ∈ acc, a.1 < m ∧ a.2 < q
  acc_sorted : acc.Pairwise fun a b => b.1 < a.1 ∧ b.2 < a.2

theorem lt_of_isSummand {N q : ℕ} (h : IsSummand N q) : q < N := by
  have := h.2.two_le
  omega

/-- A term whose value is the current striker is the front. -/
theorem eq_front {X q m U : ℕ} {acc : List (ℕ × ℕ)} (I : Inv X q m U acc) (hm : m < X)
    {N : ℕ} (hN : N < X) (h : IsRecord N q) : N = m := by
  obtain ⟨hE, h4, hl, hall⟩ := h
  have h1 : m ≤ N := by
    by_contra hlt
    obtain ⟨q', hq', hs⟩ := I.least N hE h4 (by omega) hN
    have := hl.2 q' hs
    omega
  have h2 : N ≤ m := by
    by_contra hlt
    obtain ⟨q', hq', hs⟩ := hall m I.even I.four (by omega)
    exact I.free hm q' hq' hs
  omega

/-- A striker that hits the front makes it a term. -/
theorem isRecord_front {X q m U : ℕ} {acc : List (ℕ × ℕ)} (I : Inv X q m U acc) (hm : m < X)
    (h : IsSummand m q) : IsRecord m q :=
  ⟨I.even, I.four, ⟨h, fun p hp => by
    by_contra hlt
    exact I.free hm p (by omega) hp⟩, fun M hE h4 hM => I.least M hE h4 hM (by omega)⟩

theorem loop_spec {X P : ℕ} (hP : ∀ j, P.testBit j = decide (j.Prime ∧ j < X)) :
    ∀ (fuel q m U : ℕ) (acc : List (ℕ × ℕ)), Inv X q m U acc → X ≤ q + fuel →
      (∀ N g, (N, g) ∈ loop X P fuel q m U acc ↔ N < X ∧ IsRecord N g) ∧
        (loop X P fuel q m U acc).Pairwise fun a b => a.1 < b.1 ∧ a.2 < b.2 := by
  intro fuel
  induction fuel with
  | zero =>
    intro q m U acc I hq
    simp only [loop]
    refine ⟨fun N g => ?_, List.pairwise_reverse.mpr I.acc_sorted⟩
    rw [List.mem_reverse, I.acc_iff]
    exact ⟨fun h => ⟨h.1, h.2.1⟩, fun h => ⟨h.1, h.2, by
      have := lt_of_isSummand h.2.2.2.1.1
      omega⟩⟩
  | succ fuel ih =>
    intro q m U acc I hq
    simp only [loop]
    split_ifs with hXm hprime hhit
    · -- the front has left the range: nothing more below `X`
      refine ⟨fun N g => ?_, List.pairwise_reverse.mpr I.acc_sorted⟩
      rw [List.mem_reverse, I.acc_iff]
      refine ⟨fun h => ⟨h.1, h.2.1⟩, fun h => ⟨h.1, h.2, ?_⟩⟩
      by_contra hge
      obtain ⟨hE, h4, hl, _⟩ := h.2
      obtain ⟨q', hq', hs⟩ := I.least N hE h4 (by omega) h.1
      have := hl.2 q' hs
      omega
    · -- `q` is a prime below `X` and hits the front
      have hmX : m < X := by omega
      rw [hP, decide_eq_true_eq] at hprime
      rw [Bool.and_eq_true, decide_eq_true_eq, hP, decide_eq_true_eq] at hhit
      have hsum : IsSummand m q := ⟨hprime.1, hhit.2.1⟩
      have hstruck : ∀ N < X, (U ||| (P <<< q)).testBit N = true ↔
          ∃ q' < q + 1, IsSummand N q' := by
        intro N hN
        rw [Nat.testBit_or, Bool.or_eq_true, I.struck N hN, Nat.testBit_shiftLeft,
          Bool.and_eq_true, decide_eq_true_eq, hP, decide_eq_true_eq]
        constructor
        · rintro (⟨q', hq', hs⟩ | ⟨_, hp, _⟩)
          · exact ⟨q', by omega, hs⟩
          · exact ⟨q, by omega, hprime.1, hp⟩
        · rintro ⟨q', hq', hs⟩
          rcases Nat.lt_or_ge q' q with h | h
          · exact Or.inl ⟨q', h, hs⟩
          · have e : q' = q := by omega
            subst e
            have := lt_of_isSummand hs
            exact Or.inr ⟨by omega, hs.2, by omega⟩
      obtain ⟨hnE, hnm, hnfree, hnall⟩ := nextFree_spec (X := X) (U := U ||| (P <<< q)) I.even
      have hrec := isRecord_front I hmX hsum
      refine ih (q + 1) _ _ _ ⟨hstruck, hnE, by have := I.four; omega, ?_, ?_, ?_, ?_, ?_⟩
        (by omega)
      · intro hlt q' hq' hs
        have h1 := hnfree hlt
        have h2 := (hstruck _ hlt).mpr ⟨q', hq', hs⟩
        rw [h1] at h2
        exact absurd h2 (by decide)
      · intro N hE h4 hNn hNX
        rcases Nat.lt_trichotomy N m with h | h | h
        · obtain ⟨q', hq', hs⟩ := I.least N hE h4 h hNX
          exact ⟨q', by omega, hs⟩
        · subst h
          exact ⟨q, by omega, hsum⟩
        · exact (hstruck N hNX).mp (hnall N hE h hNn hNX)
      · intro N g
        rw [List.mem_cons, I.acc_iff]
        constructor
        · rintro (h | h)
          · obtain ⟨rfl, rfl⟩ := Prod.mk.inj h
            exact ⟨hmX, hrec, by omega⟩
          · exact ⟨h.1, h.2.1, by omega⟩
        · rintro ⟨hN, hr, hg⟩
          rcases Nat.lt_or_ge g q with h | h
          · exact Or.inr ⟨hN, hr, h⟩
          · have e : g = q := by omega
            subst e
            exact Or.inl (by rw [eq_front I hmX hN hr])
      · intro a ha
        rcases List.mem_cons.mp ha with rfl | ha
        · exact ⟨hnm, by omega⟩
        · have := I.acc_lt a ha
          exact ⟨by omega, by omega⟩
      · exact List.pairwise_cons.mpr ⟨fun b hb => I.acc_lt b hb, I.acc_sorted⟩
    · -- `q` is a prime below `X` and misses the front
      have hmX : m < X := by omega
      rw [hP, decide_eq_true_eq] at hprime
      have hmiss : ¬ IsSummand m q := by
        intro hs
        apply hhit
        rw [Bool.and_eq_true, decide_eq_true_eq, hP, decide_eq_true_eq]
        have := lt_of_isSummand hs
        exact ⟨by omega, hs.2, by omega⟩
      have hstruck : ∀ N < X, (U ||| (P <<< q)).testBit N = true ↔
          ∃ q' < q + 1, IsSummand N q' := by
        intro N hN
        rw [Nat.testBit_or, Bool.or_eq_true, I.struck N hN, Nat.testBit_shiftLeft,
          Bool.and_eq_true, decide_eq_true_eq, hP, decide_eq_true_eq]
        constructor
        · rintro (⟨q', hq', hs⟩ | ⟨_, hp, _⟩)
          · exact ⟨q', by omega, hs⟩
          · exact ⟨q, by omega, hprime.1, hp⟩
        · rintro ⟨q', hq', hs⟩
          rcases Nat.lt_or_ge q' q with h | h
          · exact Or.inl ⟨q', h, hs⟩
          · have e : q' = q := by omega
            subst e
            have := lt_of_isSummand hs
            exact Or.inr ⟨by omega, hs.2, by omega⟩
      refine ih (q + 1) _ _ _ ⟨hstruck, I.even, I.four, ?_, ?_, ?_, ?_, I.acc_sorted⟩ (by omega)
      · intro hlt q' hq' hs
        rcases Nat.lt_or_ge q' q with h | h
        · exact I.free hlt q' h hs
        · have e : q' = q := by omega
          subst e
          exact hmiss hs
      · intro N hE h4 hNm hNX
        obtain ⟨q', hq', hs⟩ := I.least N hE h4 hNm hNX
        exact ⟨q', by omega, hs⟩
      · intro N g
        rw [I.acc_iff]
        constructor
        · rintro ⟨hN, hr, hg⟩
          exact ⟨hN, hr, by omega⟩
        · rintro ⟨hN, hr, hg⟩
          refine ⟨hN, hr, ?_⟩
          by_contra hge
          have e : g = q := by omega
          subst e
          have := eq_front I hmX hN hr
          subst this
          exact hmiss hr.2.2.1.1
      · intro a ha
        have := I.acc_lt a ha
        exact ⟨this.1, by omega⟩
    · -- `q` is not a prime below `X`: it strikes nothing below `X`
      have hno : ∀ N < X, ¬ IsSummand N q := by
        intro N hN hs
        apply hprime
        rw [hP, decide_eq_true_eq]
        have := lt_of_isSummand hs
        exact ⟨hs.1, by omega⟩
      refine ih (q + 1) _ _ _ ⟨?_, I.even, I.four, ?_, ?_, ?_, ?_, I.acc_sorted⟩ (by omega)
      · intro N hN
        rw [I.struck N hN]
        constructor
        · rintro ⟨q', hq', hs⟩
          exact ⟨q', by omega, hs⟩
        · rintro ⟨q', hq', hs⟩
          rcases Nat.lt_or_ge q' q with h | h
          · exact ⟨q', h, hs⟩
          · have e : q' = q := by omega
            subst e
            exact absurd hs (hno N hN)
      · intro hlt q' hq' hs
        rcases Nat.lt_or_ge q' q with h | h
        · exact I.free hlt q' h hs
        · have e : q' = q := by omega
          subst e
          exact hno m hlt hs
      · intro N hE h4 hNm hNX
        obtain ⟨q', hq', hs⟩ := I.least N hE h4 hNm hNX
        exact ⟨q', by omega, hs⟩
      · intro N g
        rw [I.acc_iff]
        constructor
        · rintro ⟨hN, hr, hg⟩
          exact ⟨hN, hr, by omega⟩
        · rintro ⟨hN, hr, hg⟩
          refine ⟨hN, hr, ?_⟩
          by_contra hge
          have e : g = q := by omega
          subst e
          exact hno N hN hr.2.2.1.1
      · intro a ha
        have := I.acc_lt a ha
        exact ⟨this.1, by omega⟩

/-- The state before the first striker. -/
theorem inv_init (X : ℕ) : Inv X 2 4 0 [] where
  struck := fun N _ => by
    rw [Nat.zero_testBit]
    constructor
    · intro h
      exact absurd h (by decide)
    · rintro ⟨q', hq', hs⟩
      have := hs.1.two_le
      omega
  even := ⟨2, rfl⟩
  four := le_rfl
  free := fun _ q' hq' hs => by
    have := hs.1.two_le
    omega
  least := fun N _ h4 hN _ => by omega
  acc_iff := fun N g => by
    constructor
    · intro h
      exact absurd h (by simp)
    · rintro ⟨_, hr, hg⟩
      have := hr.2.2.1.1.1.two_le
      omega
  acc_lt := fun a ha => absurd ha (by simp)
  acc_sorted := List.Pairwise.nil

/-- **The generator is correct.** For every bound `X`, the list `records X` consists exactly of
the terms of A025018 below `X`, each with its least Goldbach summand (A025019). -/
theorem mem_records {X N g : ℕ} : (N, g) ∈ records X ↔ N < X ∧ IsRecord N g :=
  (loop_spec (testBit_primeMask X) X 2 4 0 [] (inv_init X) (by omega)).1 N g

/-- **… and lists them in order:** both the numbers and their summands increase along
`records X`. In particular there are no repetitions. -/
theorem records_sorted (X : ℕ) : (records X).Pairwise fun a b => a.1 < b.1 ∧ a.2 < b.2 :=
  (loop_spec (testBit_primeMask X) X 2 4 0 [] (inv_init X) (by omega)).2

/-- A025018 below `X`: the numbers. -/
theorem mem_map_fst_records {X N : ℕ} :
    N ∈ (records X).map Prod.fst ↔ N < X ∧ ∃ g, IsRecord N g := by
  rw [List.mem_map]
  constructor
  · rintro ⟨⟨N', g⟩, h, rfl⟩
    exact ⟨(mem_records.mp h).1, g, (mem_records.mp h).2⟩
  · rintro ⟨hN, g, hr⟩
    exact ⟨(N, g), mem_records.mpr ⟨hN, hr⟩, rfl⟩

/-- The record holders of `GoldbachGaps/BitSieve.lean` (smaller numbers counted from `6`) are
the terms from `6` on. -/
theorem isRecordHolder_iff_exists_isRecord {N : ℕ} (hE : Even N) (h6 : 6 ≤ N) :
    IsRecordHolder N ↔ ∃ g, IsRecord N g := by
  constructor
  · rintro ⟨g, hg, hall⟩
    refine ⟨g, hE, by omega, hg, fun M hM h4 hlt => ?_⟩
    rcases Nat.lt_or_ge M 6 with h | h
    · have hM4 : M = 4 := by
        obtain ⟨c, hc⟩ := hM
        omega
      subst hM4
      have hg2 : g ≠ 2 := by
        rintro rfl
        have h1 := hg.1.2
        have h2 : Even (N - 2) := (Nat.even_sub (by omega)).mpr ⟨fun _ => even_two, fun _ => hE⟩
        have h3 := (Nat.Prime.even_iff h1).mp h2
        omega
      have := hg.1.1.two_le
      exact ⟨2, by omega, Nat.prime_two, by norm_num⟩
    · exact hall M hM h hlt
  · rintro ⟨g, _, _, hg, hall⟩
    exact ⟨g, hg, fun M hM h6' hlt => hall M hM (by omega) hlt⟩

end RecordGen

end GoldbachGaps
