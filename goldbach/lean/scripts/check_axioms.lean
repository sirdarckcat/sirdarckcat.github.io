-- Run from goldbach/lean with `lake env lean scripts/check_axioms.lean` after `lake build`.
-- Prints the number of modules, constants and theorems of the package and every axiom any of them uses.
import GoldbachGaps
open Lean Elab Command

-- Every constant declared in a module of the package, with the axioms it depends on.
#eval show CommandElabM Unit from do
  let env ← getEnv
  let ok : List Name := [``propext, ``Classical.choice, ``Quot.sound]
  let mut nThm : Nat := 0
  let mut nAll : Nat := 0
  let mut nMod : Nat := 0
  let mut used : NameSet := {}
  let mut bad : Array (Name × Array Name) := #[]
  for i in [0:env.header.moduleNames.size] do
    let mod := env.header.moduleNames[i]!
    unless (`GoldbachGaps).isPrefixOf mod do continue
    nMod := nMod + 1
    let md := env.header.moduleData[i]!
    for ci in md.constants do
      nAll := nAll + 1
      if ci.isTheorem then nThm := nThm + 1
      let axs ← liftCoreM <| Lean.collectAxioms ci.name
      for a in axs do used := used.insert a
      if axs.any (fun a => !ok.contains a) then bad := bad.push (ci.name, axs)
  logInfo m!"modules: {nMod}; constants: {nAll}; theorems: {nThm}; axioms used by any of them: {used.toList}; constants using any other axiom: {bad.size} {bad.toList.take 10}"
