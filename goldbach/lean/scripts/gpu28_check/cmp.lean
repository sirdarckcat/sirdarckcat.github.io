import GoldbachGaps.Gpu28.Kernel
open Gpu28 Fscan.Schedule

/-! Runs the Lean model of `fermat28` on the test lines and compares with the output of the
kernel source compiled for the CPU. The third argument is `plain` (steps ending with the carry
chain, `stepF`) or `red` (redundant steps, `stepR`, and the normalisation `normLimbs`). The
model's functions are applied through arrays so that each limb is computed once;
`preLimbs_unfold` certifies that the shared form is the model. -/

def hexVal (s : String) : Nat :=
  s.foldl (fun acc ch =>
    let d := if ch.isDigit then ch.toNat - '0'.toNat else ch.toNat - 'a'.toNat + 10
    acc * 16 + d) 0

def hexPad (w v : Nat) : String :=
  let digs := Nat.toDigits 16 v
  String.ofList (List.replicate (w - digs.length) '0' ++ digs)

def fn (a : Array Nat) : Nat → Nat := fun i => a.getD i 0
def limbs28 (v : Nat) : Array Nat := (Array.range 24).map fun i => (v >>> (28 * i)) % 2 ^ 28
def words32 (v : Nat) : Array Nat := (Array.range 24).map fun i => (v >>> (32 * i)) % 2 ^ 32
def showLimbs (a : Array Nat) : String :=
  String.join ((List.range 24).reverse.map fun i => hexPad 8 (a.getD i 0))

theorem preLimbs_unfold (x n : Nat → Nat) (np : Nat) :
    preLimbs x n np 24 =
      Function.update (upper x n (lower x n np 24 24).2 24 (lower x n np 24 24).1 23).2 23
        ((upper x n (lower x n np 24 24).2 24 (lower x n np 24 24).1 23).1 % 2 ^ 32) := rfl

/-- The limbs before the shift (`preLimbs`), with the two column passes done once. -/
def preArr (x n : Array Nat) (np : Nat) : Array Nat :=
  let lo := lower (fn x) (fn n) np 24 24
  let up := upper (fn x) (fn n) lo.2 24 lo.1 23
  (Array.range 24).map (Function.update up.2 23 (up.1 % 2 ^ 32))

/-- `stepF` (carry chain) or `stepR` (`y_i << b` in 32 bits), every limb. -/
def stepArr (red : Bool) (x n : Array Nat) (np b : Nat) : Array Nat :=
  let pre := preArr x n np
  if red then pre.map fun y => (y <<< b) % 2 ^ 32 else (Array.range 24).map (chainLimb (fn pre) b)

def fermatModel (red : Bool) (nv : Nat) : Nat :=
  let bn := if nv = 0 then 0 else Nat.log2 nv + 1
  if bn < 642 ∨ bn > 668 ∨ nv % 2 = 0 then 2 else
  let t := bn - 6
  let c := cOfR 672 nv t
  let n := limbs28 nv
  let np := invNeg28 (nv % 2 ^ 32)
  let bw := BOfR 672 nv t
  let x := Id.run do
    let mut x := (Array.range 24).map (startLimbs (672 - c))
    for s in [0:t] do
      x := stepArr red x n np (bw / 2 ^ (t - (s + 1)) % 2)    -- betaR 672 nv t (s + 1)
    return x
  -- the redundant kernel normalises once: normLimbs = chainLimb · 0
  let x := if red then (Array.range 24).map (normLimbs (fn x)) else x
  -- flag: n2 = 2n, two conditional subtractions, compare with 1
  let n2 := (Array.range 24).map (chainLimb (fn n) 1)
  let x1 := (Array.range 24).map (condSub28 (fn x) (fn n2) 24)
  let x2 := (Array.range 24).map (condSub28 (fn x1) (fn n) 24)
  if isOne (fn x2) 24 then 1 else 0

def runLine (red : Bool) (line : String) : String :=
  match line.splitOn " " with
  | ["step", a, b, c] =>
    let nv := hexVal b
    "step " ++ showLimbs (stepArr red (limbs28 (hexVal a)) (limbs28 nv) (invNeg28 (nv % 2 ^ 32)) (hexVal c))
  | ["rstep", a, b, c] =>
    let nv := hexVal b
    "rstep " ++ showLimbs (stepArr red (words32 (hexVal a)) (limbs28 nv) (invNeg28 (nv % 2 ^ 32)) (hexVal c))
  | ["inv", a] => "inv " ++ hexPad 7 (invNeg28 (hexVal a))
  | ["fermat", a] => "fermat " ++ toString (fermatModel red (hexVal a))
  | _ => "?"

def main (args : List String) : IO Unit := do
  let tests ← IO.FS.lines args[0]!
  let cout ← IO.FS.lines args[1]!
  let red := args[2]! == "red"
  let mut bad := 0
  let mut n := 0
  for (t, c) in tests.toList.zip cout.toList do
    let r := runLine red t
    n := n + 1
    if r != c then
      bad := bad + 1
      if bad ≤ 5 then IO.println s!"MISMATCH on: {t}\n  lean: {r}\n  C:    {c}"
  IO.println s!"{n} tests, {bad} mismatches between the Lean model ({args[2]!}) and the kernel compiled for the CPU"
