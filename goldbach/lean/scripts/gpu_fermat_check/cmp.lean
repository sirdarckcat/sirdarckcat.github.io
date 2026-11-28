import GoldbachGaps.Gpu.Fermat
open Gpu

def hexVal (s : String) : Nat :=
  s.foldl (fun acc ch =>
    let d := if ch.isDigit then ch.toNat - '0'.toNat else ch.toNat - 'a'.toNat + 10
    acc * 16 + d) 0

def toLimbs (x : Nat) : Nat → List Nat
  | 0 => []
  | k + 1 => x % 2 ^ 32 :: toLimbs (x / 2 ^ 32) k

def hexOf (L : Nat) (l : List Nat) : String :=
  let v := val l
  let digs := (Nat.toDigits 16 v)
  String.ofList (List.replicate (8 * L - digs.length) '0' ++ digs)

def runLine (L : Nat) (line : String) : String :=
  match line.splitOn " " with
  | ["fermat", a, b, c] =>
    "fermat " ++ (if fermat2 (toLimbs (hexVal a) L) (toLimbs (hexVal b) L) (hexVal c) then "1" else "0")
  | ["sqr", a, b, c] =>
    "sqr " ++ hexOf L (montSqr (toLimbs (hexVal a) L) (toLimbs (hexVal b) L) (hexVal c))
  | ["dbl", a, b, _] =>
    "dbl " ++ hexOf L (dblMod (toLimbs (hexVal a) L) (toLimbs (hexVal b) L))
  | _ => "?"

def main (args : List String) : IO Unit := do
  let tests ← IO.FS.lines args[0]!
  let cout ← IO.FS.lines args[1]!
  let mut bad := 0
  let mut n := 0
  for (t, c) in tests.toList.zip cout.toList do
    let r := runLine 21 t
    n := n + 1
    if r != c then
      bad := bad + 1
      if bad ≤ 5 then IO.println s!"MISMATCH on: {t}\n  lean: {r}\n  C:    {c}"
  IO.println s!"{n} tests, {bad} mismatches between the Lean model and the kernel compiled for the CPU"
