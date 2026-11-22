import GoldbachGaps.Gpu.MontSqr

/-!
# The GPU Fermat kernel `fermat2`, one thread

`fermat2` of `goldbach/phd/campaign3_gpu/gpu_fermat.py` (commit `6ef621f`, branch
`ccr-8ffe9d7a-4ni11u`) tests `n = cq + k·M` with `LIMBS` 32-bit words:

    n     = cq + k * M                          (one carry chain)
    inv   = n[0]; 5 times: inv *= 2 - n[0]*inv; ninv = -inv
    one   = 2^(32 L) mod n                      (32 L doublings of 1)
    x     = dbl_mod(one)                        (the top bit of n - 1)
    for the lower bits of n - 1, most significant first: x = mont_sqr(x); if bit: x = dbl_mod(x)
    out   = (x == one)

`fermat2_correct`: for limb arrays `cq`, `M` of the same positive length, `k < 2^32`, and
`n = cq + k·M` odd, greater than 1 and below `2^(32 L)`, the thread reports `1` exactly when
`2^(n-1) ≡ 1 (mod n)`.

Modelled with the machine's wrapping arithmetic: every 64-bit sum and product, the 32-bit
truncations, the borrow chain, the comparison loop, the Newton iteration, the masking
`word &= ~1`, and the loop structure over words and bits. Not modelled: memory, the thread
index arithmetic, and `__clz` (taken as `31 - clz(v) = ⌊log₂ v⌋` for `v ≠ 0`).
-/

namespace Gpu

local notation "B" => (2 ^ 32 : ℕ)

/-! ### The inverse modulo `2^32` -/

/-- `inv *= 2u - n0 * inv` in 32-bit arithmetic. -/
def invStep (n0 inv : ℕ) : ℕ := (inv * ((2 + (B - (n0 * inv) % B)) % B)) % B

/-- `ninv = 0u - inv` after five steps from `inv = n0`. -/
def ninvOf (n0 : ℕ) : ℕ := (B - (invStep n0)^[5] n0 % B) % B

theorem invStep_cast (n0 inv : ℕ) :
    ((invStep n0 inv : ℕ) : ZMod B) = (inv : ZMod B) * (2 - (n0 : ZMod B) * inv) := by
  unfold invStep
  have hp : (n0 * inv) % B ≤ B := (Nat.mod_lt _ (by norm_num)).le
  rw [ZMod.natCast_mod, Nat.cast_mul, ZMod.natCast_mod, Nat.cast_add, Nat.cast_sub hp,
    ZMod.natCast_mod, Nat.cast_mul, ZMod.natCast_self]
  push_cast
  ring

theorem one_sub_iterate (n0 : ℕ) : ∀ (j : ℕ) (inv : ℕ),
    1 - (n0 : ZMod B) * (((invStep n0)^[j] inv : ℕ) : ZMod B) =
      (1 - (n0 : ZMod B) * (inv : ZMod B)) ^ 2 ^ j
  | 0, inv => by simp
  | j + 1, inv => by
    rw [Function.iterate_succ_apply', invStep_cast, show (2 : ℕ) ^ (j + 1) = 2 ^ j * 2 from pow_succ 2 j,
      pow_mul, ← one_sub_iterate n0 j inv]
    ring

/-- **The Newton iteration gives `n0 · ninv ≡ -1 (mod 2^32)`** for every odd `n0`. -/
theorem ninvOf_spec {n0 : ℕ} (hodd : n0 % 2 = 1) : (n0 * ninvOf n0 + 1) % B = 0 := by
  -- n0² = 8 t + 1
  obtain ⟨t, ht⟩ : ∃ t, n0 * n0 = 8 * t + 1 := by
    have h8 : n0 * n0 % 8 = 1 := by
      have hr : n0 % 8 < 8 := Nat.mod_lt _ (by norm_num)
      have ho : n0 % 8 % 2 = 1 := by omega
      rw [Nat.mul_mod]
      generalize n0 % 8 = r at hr ho
      interval_cases r <;> simp_all
    exact ⟨n0 * n0 / 8, by omega⟩
  have h2 : ((2 : ZMod B)) ^ 32 = 0 := by
    have := ZMod.natCast_self B
    push_cast at this
    exact this
  have hsq : (1 - (n0 : ZMod B) * (n0 : ZMod B)) ^ 2 ^ 5 = 0 := by
    have e : (n0 : ZMod B) * (n0 : ZMod B) = 8 * (t : ZMod B) + 1 := by
      have := congrArg (Nat.cast : ℕ → ZMod B) ht
      push_cast at this
      exact this
    rw [e]
    have : (1 - (8 * (t : ZMod B) + 1)) ^ 2 ^ 5 = ((2 : ZMod B) ^ 32) ^ 3 * (t : ZMod B) ^ 32 := by
      ring
    rw [this, h2]
    ring
  have key := one_sub_iterate n0 5 n0
  rw [hsq] at key
  -- cast of ninv
  have hlt : (invStep n0)^[5] n0 % B ≤ B := (Nat.mod_lt _ (by norm_num)).le
  have hc : ((ninvOf n0 : ℕ) : ZMod B) = -(((invStep n0)^[5] n0 : ℕ) : ZMod B) := by
    unfold ninvOf
    rw [ZMod.natCast_mod, Nat.cast_sub hlt, ZMod.natCast_mod, ZMod.natCast_self]
    ring
  have hz : ((n0 * ninvOf n0 + 1 : ℕ) : ZMod B) = 0 := by
    push_cast
    rw [hc]
    linear_combination key
  exact Nat.mod_eq_zero_of_dvd ((ZMod.natCast_eq_zero_iff _ _).mp hz)

/-! ### Montgomery forms of powers of two -/

/-- `x` is the limb array of `2^a · R mod n`, `R = 2^(32 L)`. -/
def IsMont (n : List ℕ) (a : ℕ) (x : List ℕ) : Prop :=
  Limbs x ∧ x.length = n.length ∧ val x = (2 ^ a * B ^ n.length) % val n

section loop

variable {n : List ℕ} {ninv : ℕ} (hn : Limbs n) (hL : 0 < n.length)
  (hinv : (n.headD 0 * ninv + 1) % B = 0) (hodd : val n % 2 = 1) (hgt : 1 < val n)

include hgt in
theorem IsMont.lt {a : ℕ} {x : List ℕ} (h : IsMont n a x) : val x < val n := by
  rw [h.2.2]
  exact Nat.mod_lt _ (by omega)

include hodd in
theorem coprime_R : Nat.Coprime (B ^ n.length) (val n) := by
  have h2 : Nat.Coprime 2 (val n) :=
    (Nat.Prime.coprime_iff_not_dvd Nat.prime_two).mpr (by omega)
  exact (h2.pow_left 32).pow_left _

include hn hL hinv hodd hgt in
theorem IsMont.sqr {a : ℕ} {x : List ℕ} (h : IsMont n a x) :
    IsMont n (2 * a) (montSqr x n ninv) := by
  obtain ⟨m1, m2, m3, m4⟩ := montSqr_spec h.1 hn h.2.1 hL hinv (h.lt hgt)
  refine ⟨m1, m2, ?_⟩
  have e : (val x * val x) % val n = (B ^ n.length * (2 ^ (2 * a) * B ^ n.length)) % val n := by
    rw [h.2.2, ← Nat.mul_mod]
    congr 1
    rw [two_mul, pow_add]
    ring
  have hmod : B ^ n.length * val (montSqr x n ninv) ≡
      B ^ n.length * (2 ^ (2 * a) * B ^ n.length) [MOD val n] := m4.trans e
  have hc : Nat.gcd (val n) (B ^ n.length) = 1 := (coprime_R hodd).symm
  have := Nat.ModEq.cancel_left_of_coprime hc hmod
  exact (Nat.mod_eq_of_lt m3).symm.trans this

include hn hgt in
theorem IsMont.dbl {a : ℕ} {x : List ℕ} (h : IsMont n a x) : IsMont n (a + 1) (dblMod x n) := by
  obtain ⟨d1, d2, d3⟩ := dblMod_spec h.1 hn h.2.1 (h.lt hgt)
  refine ⟨d1, d2, ?_⟩
  rw [d3, h.2.2, Nat.mul_mod, Nat.mod_mod, ← Nat.mul_mod]
  congr 1
  rw [pow_succ]
  ring

/-- The inner loop over the bits `cnt - 1, …, 0` of one word:
`mont_sqr(x); if ((word >> i) & 1) dbl_mod(x)`. -/
def bitLoop (n : List ℕ) (ninv : ℕ) (word : ℕ) : ℕ → List ℕ → List ℕ
  | 0, x => x
  | i + 1, x =>
      bitLoop n ninv word i
        (if (word >>> i) &&& 1 = 1 then dblMod (montSqr x n ninv) n else montSqr x n ninv)

include hn hL hinv hodd hgt in
/-- Processing `cnt` bits of `word` turns the exponent `a` into `a · 2^cnt + word mod 2^cnt`. -/
theorem bitLoop_spec (word : ℕ) : ∀ (cnt a : ℕ) (x : List ℕ), IsMont n a x →
    IsMont n (a * 2 ^ cnt + word % 2 ^ cnt) (bitLoop n ninv word cnt x)
  | 0, a, x, h => by simpa [bitLoop, Nat.mod_one] using h
  | i + 1, a, x, h => by
    have hs := h.sqr hn hL hinv hodd hgt (ninv := ninv)
    have hbit : ((word >>> i) &&& 1 = 1) ↔ word / 2 ^ i % 2 = 1 := by
      rw [Nat.and_one_is_mod, Nat.shiftRight_eq_div_pow]
    have hsplit : word % 2 ^ (i + 1) = word % 2 ^ i + 2 ^ i * (word / 2 ^ i % 2) :=
      Nat.mod_pow_succ
    unfold bitLoop
    by_cases hb : word / 2 ^ i % 2 = 1
    · simp only [hbit.mpr hb, ↓reduceIte]
      have := bitLoop_spec word i (2 * a + 1) _ (hs.dbl hn hgt)
      have e : (2 * a + 1) * 2 ^ i + word % 2 ^ i = a * 2 ^ (i + 1) + word % 2 ^ (i + 1) := by
        rw [hsplit, hb, pow_succ]
        ring
      rwa [e] at this
    · have hnb : ¬ ((word >>> i) &&& 1 = 1) := fun h => hb (hbit.mp h)
      simp only [hnb, ↓reduceIte]
      have hb0 : word / 2 ^ i % 2 = 0 := by omega
      have := bitLoop_spec word i (2 * a) _ hs
      have e : 2 * a * 2 ^ i + word % 2 ^ i = a * 2 ^ (i + 1) + word % 2 ^ (i + 1) := by
        rw [hsplit, hb0, pow_succ]
        ring
      rwa [e] at this

/-! ### The loop over the words of `n - 1` -/

/-- `word &= ~1u` clears bit 0. -/
theorem and_not_one {w : ℕ} (hw : w < B) : w &&& 4294967294 = w - w % 2 := by
  have h1 : (w &&& 4294967294) / 2 = w / 2 := by
    rw [Nat.and_div_two, show (4294967294 : ℕ) / 2 = 2 ^ 31 - 1 by norm_num,
      Nat.and_two_pow_sub_one_eq_mod]
    omega
  have h2 : (w &&& 4294967294) % 2 = 0 := by
    have := Nat.and_mod_two_pow (a := w) (b := 4294967294) (n := 1)
    rw [pow_one] at this
    rw [this, show (4294967294 : ℕ) % 2 = 0 by norm_num, Nat.and_zero]
  omega

/-- `while (top > 0 && n[top] == 0) top--`, on the words listed from the most significant:
drop leading zero words, but keep the last word. -/
def dropZeros : List ℕ → List ℕ
  | a :: b :: l => if a = 0 then dropZeros (b :: l) else a :: b :: l
  | [a] => [a]
  | [] => []

theorem valBE_dropZeros : ∀ l : List ℕ, valBE (dropZeros l) = valBE l
  | [] => rfl
  | [_] => rfl
  | a :: b :: l => by
    rw [dropZeros]
    split_ifs with h
    · rw [valBE_dropZeros (b :: l), h]
      simp [valBE]
    · rfl

theorem Limbs_dropZeros : ∀ {l : List ℕ}, Limbs l → Limbs (dropZeros l)
  | [], h => h
  | [_], h => h
  | a :: b :: l, h => by
    rw [dropZeros]
    split_ifs with h0
    · exact Limbs_dropZeros h.tail
    · exact h

theorem dropZeros_head_ne_zero : ∀ {l : List ℕ} {a b : ℕ} {m : List ℕ},
    dropZeros l = a :: b :: m → a ≠ 0
  | [], _, _, _, h => by simp [dropZeros] at h
  | [_], _, _, _, h => by simp [dropZeros] at h
  | c :: d :: l, a, b, m, h => by
    rw [dropZeros] at h
    split_ifs at h with h0
    · exact dropZeros_head_ne_zero h
    · have := (List.cons.inj h).1
      omega

/-- The words below the top one, most significant first, 32 bits each; the last one (word 0)
is masked with `~1`. -/
def restLoop (n : List ℕ) (ninv : ℕ) : List ℕ → List ℕ → List ℕ
  | [], x => x
  | [w0], x => bitLoop n ninv (w0 &&& 4294967294) 32 x
  | w :: w' :: ws, x => restLoop n ninv (w' :: ws) (bitLoop n ninv w 32 x)

/-- The exponent loop of `fermat2`, after the first `dbl_mod`: the top word from its highest
set bit minus one down, then the lower words. -/
def expLoop (n : List ℕ) (ninv : ℕ) (x : List ℕ) : List ℕ :=
  match dropZeros n.reverse with
  | [] => x
  | [w0] => bitLoop n ninv (w0 &&& 4294967294) (Nat.log2 w0) x
  | w :: w' :: ws => restLoop n ninv (w' :: ws) (bitLoop n ninv w (Nat.log2 w) x)

theorem two_dvd_pow_length {l : List ℕ} (h : l ≠ []) : ∃ P, B ^ l.length = P * 2 := by
  cases l with
  | nil => exact absurd rfl h
  | cons a l =>
    refine ⟨B ^ l.length * 2 ^ 31, ?_⟩
    rw [List.length_cons, pow_succ (2 ^ 32) l.length]
    ring

include hn hL hinv hodd hgt in
theorem restLoop_spec : ∀ (ws : List ℕ) (a : ℕ) (x : List ℕ), ws ≠ [] → Limbs ws →
    IsMont n a x →
    IsMont n (a * B ^ ws.length + (valBE ws - valBE ws % 2)) (restLoop n ninv ws x)
  | [], _, _, h, _, _ => absurd rfl h
  | [w0], a, x, _, hl, hx => by
    have hw := hl.head
    have h := bitLoop_spec hn hL hinv hodd hgt (w0 &&& 4294967294) 32 a x hx
    have e : a * 2 ^ 32 + (w0 &&& 4294967294) % 2 ^ 32 =
        a * B ^ [w0].length + (valBE [w0] - valBE [w0] % 2) := by
      rw [and_not_one hw, Nat.mod_eq_of_lt (by omega)]
      simp [valBE]
    rw [e] at h
    exact h
  | w :: w' :: ws, a, x, _, hl, hx => by
    have hw := hl.head
    have h1 := bitLoop_spec hn hL hinv hodd hgt w 32 a x hx
    rw [Nat.mod_eq_of_lt hw] at h1
    have h2 := restLoop_spec (w' :: ws) _ _ (by simp) hl.tail h1
    obtain ⟨P, hP⟩ := two_dvd_pow_length (l := w' :: ws) (by simp)
    have e : (a * 2 ^ 32 + w) * B ^ (w' :: ws).length +
        (valBE (w' :: ws) - valBE (w' :: ws) % 2) =
        a * B ^ (w :: w' :: ws).length +
          (valBE (w :: w' :: ws) - valBE (w :: w' :: ws) % 2) := by
      have hv : valBE (w :: w' :: ws) = w * B ^ (w' :: ws).length + valBE (w' :: ws) := rfl
      have hpow : B ^ (w :: w' :: ws).length = B ^ (w' :: ws).length * B := by
        rw [List.length_cons, pow_succ (2 ^ 32) (w' :: ws).length]
      rw [hv, hpow, hP]
      generalize valBE (w' :: ws) = V
      have e1 : (w * (P * 2) + V) % 2 = V % 2 := by
        have : w * (P * 2) = (w * P) * 2 := by ring
        rw [this]
        omega
      rw [e1]
      have e2 : V % 2 ≤ V := Nat.mod_le _ _
      have e3 : (a * 2 ^ 32 + w) * (P * 2) = a * (P * 2 * 2 ^ 32) + w * (P * 2) := by ring
      rw [e3]
      generalize a * (P * 2 * 2 ^ 32) = Z1
      generalize w * (P * 2) = Z2
      omega
    rw [e] at h2
    simpa [restLoop] using h2

include hn hL hinv hodd hgt in
/-- **The exponent loop**: from the Montgomery form of `2^1` to that of `2^(n-1)`. -/
theorem expLoop_spec {x : List ℕ} (hx : IsMont n 1 x) :
    IsMont n (val n - 1) (expLoop n ninv x) := by
  have hval : valBE (dropZeros n.reverse) = val n := by
    rw [valBE_dropZeros, valBE_reverse]
  have hlim : Limbs (dropZeros n.reverse) :=
    Limbs_dropZeros fun a ha => hn a (List.mem_reverse.mp ha)
  unfold expLoop
  -- facts about ⌊log₂ w⌋ used for the top word
  have top : ∀ w : ℕ, w ≠ 0 → 2 ^ Nat.log2 w + w % 2 ^ Nat.log2 w = w := by
    intro w hw
    have h1 := Nat.log2_self_le hw
    have h2 := Nat.lt_log2_self (n := w)
    rw [pow_succ] at h2
    rw [Nat.mod_eq_sub_mod h1, Nat.mod_eq_of_lt (by omega)]
    omega
  generalize hd : dropZeros n.reverse = l at hval hlim
  match l, hd with
  | [], _ =>
    simp only [valBE] at hval
    omega
  | [w0], _ =>
    simp only [valBE, List.length_nil, pow_zero, mul_one, add_zero] at hval
    have hw := hlim.head
    have hw0 : w0 ≠ 0 := by omega
    have h := bitLoop_spec hn hL hinv hodd hgt (w0 &&& 4294967294) (Nat.log2 w0) 1 x hx
    have h1 := Nat.log2_self_le hw0
    have h2 := Nat.lt_log2_self (n := w0)
    rw [pow_succ] at h2
    -- the logarithm is positive because w0 is odd and greater than 1
    have hpos : Nat.log2 w0 ≠ 0 := by
      intro h0
      rw [h0] at h2
      omega
    obtain ⟨j, hj⟩ := Nat.exists_eq_succ_of_ne_zero hpos
    have heven : 2 ^ Nat.log2 w0 % 2 = 0 := by
      rw [hj, Nat.succ_eq_add_one, pow_succ]
      omega
    have e : 1 * 2 ^ Nat.log2 w0 + (w0 &&& 4294967294) % 2 ^ Nat.log2 w0 = val n - 1 := by
      rw [and_not_one hw, ← hval]
      have hle : 2 ^ Nat.log2 w0 ≤ w0 - w0 % 2 := by omega
      rw [Nat.mod_eq_sub_mod hle, Nat.mod_eq_of_lt (by omega)]
      omega
    rw [e] at h
    exact h
  | w :: w' :: ws, hd' =>
    have hw := hlim.head
    have hw0 : w ≠ 0 := dropZeros_head_ne_zero hd'
    have h := bitLoop_spec hn hL hinv hodd hgt w (Nat.log2 w) 1 x hx
    rw [one_mul, top w hw0] at h
    have h2 := restLoop_spec hn hL hinv hodd hgt (w' :: ws) w _ (by simp) hlim.tail h
    obtain ⟨P, hP⟩ := two_dvd_pow_length (l := w' :: ws) (by simp)
    have e : w * B ^ (w' :: ws).length + (valBE (w' :: ws) - valBE (w' :: ws) % 2) =
        val n - 1 := by
      have hv : valBE (w :: w' :: ws) = w * B ^ (w' :: ws).length + valBE (w' :: ws) := rfl
      rw [hv, hP] at hval
      rw [hP]
      generalize valBE (w' :: ws) = V at hval ⊢
      have : w * (P * 2) = (w * P) * 2 := by ring
      rw [this] at hval ⊢
      generalize w * P = Z at hval ⊢
      omega
    rw [e] at h2
    exact h2

end loop

/-! ### The whole thread -/

/-- `one = 2^(32 L) mod n` by `32 L` doublings of `1`. -/
def oneOf (n : List ℕ) : List ℕ :=
  (fun x => dblMod x n)^[32 * n.length] (1 :: List.replicate (n.length - 1) 0)

/-- One thread of `fermat2`: the flag it writes for the inputs `cq`, `M`, `k`. -/
def fermat2 (cq Mv : List ℕ) (k : ℕ) : Bool :=
  decide (expLoop (row k Mv cq 0).1 (ninvOf ((row k Mv cq 0).1.headD 0))
    (dblMod (oneOf (row k Mv cq 0).1) (row k Mv cq 0).1) = oneOf (row k Mv cq 0).1)

theorem dbl_iterate {n : List ℕ} (hn : Limbs n) (hgt : 1 < val n) : ∀ (j : ℕ) (x : List ℕ),
    Limbs x → x.length = n.length → val x < val n →
    Limbs ((fun x => dblMod x n)^[j] x) ∧ ((fun x => dblMod x n)^[j] x).length = n.length ∧
      val ((fun x => dblMod x n)^[j] x) = (2 ^ j * val x) % val n
  | 0, x, h1, h2, h3 => by
    refine ⟨h1, h2, ?_⟩
    simp only [Function.iterate_zero, id_eq, pow_zero, one_mul]
    exact (Nat.mod_eq_of_lt h3).symm
  | j + 1, x, h1, h2, h3 => by
    obtain ⟨i1, i2, i3⟩ := dbl_iterate hn hgt j x h1 h2 h3
    have hlt : val ((fun x => dblMod x n)^[j] x) < val n := by
      rw [i3]
      exact Nat.mod_lt _ (by omega)
    obtain ⟨d1, d2, d3⟩ := dblMod_spec i1 hn i2 hlt
    rw [Function.iterate_succ_apply']
    refine ⟨d1, d2, ?_⟩
    rw [d3, i3, Nat.mul_mod, Nat.mod_mod, ← Nat.mul_mod]
    congr 1
    rw [pow_succ]
    ring

theorem oneOf_isMont {n : List ℕ} (hn : Limbs n) (hL : 0 < n.length) (hgt : 1 < val n) :
    IsMont n 0 (oneOf n) := by
  have hx0 : Limbs (1 :: List.replicate (n.length - 1) 0) :=
    Limbs.cons (by norm_num) (Limbs_replicate_zero _)
  have hl0 : (1 :: List.replicate (n.length - 1) 0).length = n.length := by
    simp only [List.length_cons, List.length_replicate]
    omega
  have hv0 : val (1 :: List.replicate (n.length - 1) 0) = 1 := by
    simp only [val, val_replicate_zero, mul_zero, add_zero]
  obtain ⟨i1, i2, i3⟩ := dbl_iterate hn hgt (32 * n.length) _ hx0 hl0 (by rw [hv0]; exact hgt)
  refine ⟨i1, i2, ?_⟩
  show val ((fun x => dblMod x n)^[32 * n.length] (1 :: List.replicate (n.length - 1) 0)) = _
  rw [i3, hv0, mul_one, pow_zero, one_mul, pow_mul]

/-- **One thread of the GPU kernel is a base-2 Fermat test.** Let `cq` and `M` be arrays of
`L ≥ 1` limbs below `2^32`, `k < 2^32`, and suppose `n = cq + k·M` is odd, greater than 1 and
below `2^(32 L)`. Then the flag written by `fermat2` is `1` if and only if
`2^(n-1) mod n = 1`. -/
theorem fermat2_correct {cq Mv : List ℕ} {k : ℕ} (hcq : Limbs cq) (hM : Limbs Mv)
    (hlen : Mv.length = cq.length) (hL : 0 < cq.length) (hk : k < B)
    (hfit : val cq + k * val Mv < B ^ cq.length) (hodd : (val cq + k * val Mv) % 2 = 1)
    (hgt : 1 < val cq + k * val Mv) :
    fermat2 cq Mv k = true ↔ 2 ^ (val cq + k * val Mv - 1) % (val cq + k * val Mv) = 1 := by
  -- the limbs of n
  obtain ⟨r1, r2, r3, r4⟩ := row_spec hk Mv cq 0 hM hcq hlen (by norm_num)
  have hnl : (row k Mv cq 0).1.length = cq.length := r2.trans hlen
  have hnv : val (row k Mv cq 0).1 = val cq + k * val Mv := by
    have hlt := val_lt r1
    rw [hnl] at hlt
    rw [hlen, add_zero] at r4
    have hc : (row k Mv cq 0).2 = 0 := by
      by_contra hne
      have := Nat.le_mul_of_pos_right (B ^ cq.length) (Nat.pos_of_ne_zero hne)
      omega
    rw [hc, mul_zero, add_zero] at r4
    exact r4
  unfold fermat2
  generalize hnn : (row k Mv cq 0).1 = n at r1 hnl hnv ⊢
  rw [← hnv] at hodd hgt ⊢
  have hL' : 0 < n.length := by omega
  have hhead : n.headD 0 % 2 = 1 := by
    have := val_headD_tail n
    omega
  have hinv := ninvOf_spec hhead
  have hone := oneOf_isMont r1 hL' hgt
  have hx1 : IsMont n 1 (dblMod (oneOf n) n) := hone.dbl r1 hgt
  have hfin := expLoop_spec r1 hL' hinv hodd hgt hx1
  have hcop := coprime_R (n := n) hodd
  have hpos : 0 < val n := by omega
  rw [decide_eq_true_eq]
  constructor
  · intro heq
    have hv : (2 ^ (val n - 1) * B ^ n.length) % val n = (2 ^ 0 * B ^ n.length) % val n := by
      rw [← hfin.2.2, ← hone.2.2, heq]
    rw [pow_zero] at hv
    have hmod : B ^ n.length * 2 ^ (val n - 1) ≡ B ^ n.length * 1 [MOD val n] := by
      show (B ^ n.length * 2 ^ (val n - 1)) % val n = (B ^ n.length * 1) % val n
      rw [mul_comm, hv, mul_comm]
    have := Nat.ModEq.cancel_left_of_coprime hcop.symm hmod
    exact (show 2 ^ (val n - 1) % val n = 1 % val n from this).trans (Nat.mod_eq_of_lt hgt)
  · intro h
    apply val_injective hfin.1 hone.1 (hfin.2.1.trans hone.2.1.symm)
    rw [hfin.2.2, hone.2.2, pow_zero, Nat.mul_mod, h, one_mul, one_mul, Nat.mod_mod]

end Gpu
