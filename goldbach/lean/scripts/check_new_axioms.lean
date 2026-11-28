-- Run from goldbach/lean with `LEAN_NUM_THREADS=1 lake env lean scripts/check_new_axioms.lean`
-- after targeted `lake build GoldbachGaps.RankinSmooth GoldbachGaps.IteratedLogBound GoldbachGaps.CoverEveryConstant GoldbachGaps.Cap.Thinning GoldbachGaps.ECPP`.
-- OOM-safe: imports ONLY the 5 targeted modules (NEVER `import GoldbachGaps`).
-- Exits non-zero if any unexpected axiom, missing target module, missing key theorem,
-- or empty theorem list is detected.
import GoldbachGaps.RankinSmooth
import GoldbachGaps.IteratedLogBound
import GoldbachGaps.CoverEveryConstant
import GoldbachGaps.Cap.Thinning
import GoldbachGaps.ECPP

open Lean Elab Command

#eval show CommandElabM Unit from do
  let env ← getEnv
  let ok : List Name := [``propext, ``Classical.choice, ``Quot.sound]
  let targets : List Name := [
    `GoldbachGaps.RankinSmooth,
    `GoldbachGaps.IteratedLogBound,
    `GoldbachGaps.CoverEveryConstant,
    `GoldbachGaps.Cap.Thinning,
    `GoldbachGaps.ECPP
  ]
  let requiredTheorems : List Name := [
    `GoldbachGaps.exists_rankin_smooth_general,
    `GoldbachGaps.exists_rankin_smooth_bound,
    `GoldbachGaps.eventually_exists_two_layer_classes,
    `GoldbachGaps.eventually_exists_even_le_rankin,
    `GoldbachGaps.exists_pos_eventually_exists_even_le_rankin,
    `GoldbachGaps.iterated_log_linear_roots_sub,
    `GoldbachGaps.iterated_log_translate_kill_survivors,
    `GoldbachGaps.iterated_log_presieve_small_survivors,
    `GoldbachGaps.iterated_log_goldbach_of_disjoint_blocks,
    `GoldbachGaps.eventually_exists_goldbach_iterated_log,
    `GoldbachGaps.eventually_exists_isLeastSummand_iterated_log
  ]
  let mut bad : Array (Name × Array Name) := #[]
  let mut missingMods : Array Name := #[]
  let mut emptyMods : Array Name := #[]
  let mut missingThms : Array Name := #[]
  let mut allUsed : NameSet := {}

  -- 1. Audit all 5 target modules explicitly (presence, theorem count, axioms)
  for t in targets do
    let mut found : Bool := false
    let mut nConst : Nat := 0
    let mut allThms : Array Name := #[]
    let mut pubThms : Array Name := #[]
    let mut modUsed : NameSet := {}
    for i in [0:env.header.moduleNames.size] do
      if env.header.moduleNames[i]! == t then
        found := true
        for ci in env.header.moduleData[i]!.constants do
          nConst := nConst + 1
          if ci.isTheorem then
            allThms := allThms.push ci.name
            if !ci.name.isInternal then
              pubThms := pubThms.push ci.name
          let axs ← liftCoreM <| Lean.collectAxioms ci.name
          for a in axs do
            modUsed := modUsed.insert a
            allUsed := allUsed.insert a
          if axs.any (fun a => !ok.contains a) then
            bad := bad.push (ci.name, axs)
    if !found then
      missingMods := missingMods.push t
    else if pubThms.size == 0 then
      emptyMods := emptyMods.push t
    IO.println s!"MODULE {t} THEOREMS={allThms.size} PUBLIC={pubThms.size} CONSTANTS={nConst} AXIOMS={modUsed.toList}"
    if t == `GoldbachGaps.RankinSmooth || t == `GoldbachGaps.IteratedLogBound then
      IO.println s!"  PUBLIC_THEOREMS {t}: {pubThms.toList}"

  -- 2. Also audit all transitively loaded GoldbachGaps.* modules for unexpected axioms
  for i in [0:env.header.moduleNames.size] do
    let mod := env.header.moduleNames[i]!
    if (`GoldbachGaps).isPrefixOf mod && !targets.contains mod then
      for ci in env.header.moduleData[i]!.constants do
        let axs ← liftCoreM <| Lean.collectAxioms ci.name
        for a in axs do allUsed := allUsed.insert a
        if axs.any (fun a => !ok.contains a) then
          bad := bad.push (ci.name, axs)

  -- 3. Verify every required headline theorem exists and is a theorem
  for nm in requiredTheorems do
    match env.find? nm with
    | some (.thmInfo _) => pure ()
    | _ => missingThms := missingThms.push nm

  IO.println s!"SUMMARY axioms_used={allUsed.toList} bad_constants={bad.size} missing_modules={missingMods.size} empty_modules={emptyMods.size} missing_theorems={missingThms.size}"
  if missingMods.size > 0 then
    throwError m!"MISSING TARGET MODULES: {missingMods.toList}"
  if emptyMods.size > 0 then
    throwError m!"MODULES WITH ZERO PUBLIC THEOREMS: {emptyMods.toList}"
  if missingThms.size > 0 then
    throwError m!"MISSING REQUIRED THEOREMS: {missingThms.toList}"
  if bad.size > 0 then
    throwError m!"UNEXPECTED AXIOMS DETECTED ({bad.size}): {bad.toList.take 10}"
  IO.println "AXIOM_CHECK_PASS"
