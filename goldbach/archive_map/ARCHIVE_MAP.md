# Map of the "remark.pdf" Lean archive (static analysis, nothing executed)

Status: 2026-11-23. Author: the coordinating session that was asked to build this map and test whether
it helps the Goldbach-gap team. **Nothing in the archive was compiled or run here.** Everything below
comes from reading text. Labels: **[V]** verified here by direct count/read, **[D]** derived from
names/structure, **[I]** inference or judgement (may be wrong).

## 0. Bottom line (read this first)

1. **[V]** The archive is a 17.5M-line, 175,187-module Lean 4 / Mathlib project whose only exported
   claims are `riemannHypothesis : RiemannHypothesis` and four siblings about Dirichlet L-functions.
   Its machinery is automorphic forms, theta lifts, abelian varieties and arithmetic geometry; analytic
   number theory appears only as supporting infrastructure (zero-free regions, Siegel-Walfisz,
   PNT in progressions, Linnik, large sieve, Mertens-type bounds).
2. **[V/I]** I found **no technique aimed at our three barriers** (Door 1 covering CSP; the integer
   "parity" gap behind Door 3; the WP3 decoding/modulus barrier). Evidence in section 6. The
   "multiplicity" in the archive is representation-theoretic (Harish-Chandra / Bessel multiplicity one,
   theta-lift chain length), not interpolation-with-multiplicity; the string "Stepanov" occurs in **zero**
   identifiers; there is **no** list decoding / Reed-Solomon / Coppersmith / LLL / covering-system content.
3. **[V]** It does contain **reusable, kernel-checked analytic-number-theory components** with small
   build closures (2 to 500 files, minutes to ~1.4 core-hours): see section 5. These help the *theory
   track* (rigorous statements around max g(N)), not the search.
4. **[I]** It is also a worked example of how to organise a very large agent-built formalisation
   (section 7); some of that is directly reusable for our own Lean library.
5. **[V]** The claim itself is **unverified**: only 0.76% was compiled by the Lean session plus the
   517-file Linnik closure. A full build is ~470 CPU-hours.

## 1. Provenance and integrity

| item | value |
|---|---|
| note | `https://alpo.ge/remark.pdf`, 4 pages, anonymous, claims an RH/GRH proof "found working with Claude" |
| archive | `https://alpo.ge/lean.tar.gz.part01 ... part14` (14 parts, 239.3 MB) |
| SHA-256 of concatenation | `9631b4f020199e580ba86178cb56c6e9b09f690c2369a80dc4334aa93f49c7fc` (matches the Lean session's hash) |
| tar contents | 175,190 entries, **all regular files** (no links/devices/absolute or `..` paths), 1,030,536,719 bytes |
| toolchain | Lean `v4.33.1`, Mathlib rev `0df444a360eaa60ab8c11dca51a86af692955474`; package name `tree` |
| size | 175,187 `.lean` modules, 17,549,402 lines (about 10x Mathlib) |

My import-graph tooling reproduces the Lean session's independent number: the import closure of
`...ThetaCorrespondence.Linnik` is **517 files** (their build count). **[V]**

## 2. What the note says, and how the archive lines up

The note (4 pages) contains no proof, only a narrative and a 20-item timeline (10/6/26 to 11/16/26).
Its self-described method **[V, as the note's own claim]**: a Stepanov-style auxiliary determinant,
with the missing "multiplicity" supplied over the integers by *iterated theta lifts* between
totally definite unitary groups (chain length ~ sqrt(X) for a von Mangoldt sum of length X); a Weil/
Guinand explicit-formula positivity argument with a "sign-only" proof (`qN = M^k + R`); an Iwasawa-
tower/pigeonhole analogue of the F_{q^n}/F_q situation; Bost's slope inequality; a relative trace
formula; a Behrend-set choice of the tower; ending with GRH on 11/16.

Where each ingredient shows up in the archive (name-based, **[D]**, confidence medium):

| note step | archive evidence |
|---|---|
| Stepanov determinant, Bost slopes (1,4,13) | `Formalism.{HarderNarasimhan,LatticeSlopes,SuccessiveMinima,MeanHeightDescent}`, `ReciprocityTheory.GeometryOfNumbers`; "Stepanov" appears in 0 names |
| CM curve, invariant derivation, p inert (2) | `Formalism.EllipticTorsion` (Deuring, Frobenius expansion, Velu), `FormalGroupWitt`, `TorsionNormIteration` (Lubin-Tate), `GroundTheory.PAdicHodge` |
| thetas, periods, `qN = M^k + R`, trace formula (3,16) | `Formalism.PeriodIntegrals` (~3,600 Siegel-Weil/mass-formula modules), `GroundTheory.HeightsAndTheta`, `Formalism.HermitianCurvature`; ~700 trace-formula modules |
| Guinand-Weil positivity, von Mangoldt sums (5,6) | `Formalism.PeriodIntegrals` (48 positivity/explicit-formula names), `Formalism.{LandauZeroFreeBounds,ZeroFreeRegion}`, `UpperTheory.Top.VWin` |
| GGP periods, seesaw, Bessel periods (7,12) | `CompanionTheory.AutomorphicTheory.LocalBesselUniqueness`, `HarishChandraModules`, `Formalism.MirabolicMackeyTheory` |
| iterated theta lifts, Chowla-Selberg, Siegel mass, divisibility (8-10) | `Development.AutomorphicArithmetic.ThetaCorrespondence` (~4,500 theta-lift modules), `Formalism.{GradedWeylDivisibility,PieriBlockIdeals}`, `SharpRestriction.Divisibility` |
| Iwasawa tower, pigeonhole, Behrend (11,19) | `Formalism.{TameInertiaTowers,CyclotomicNorms (GTPigeonhole),BehrendSets}` |
| H^1(O_E[1/l], Q_l/Z_l(-e)), Vandiver, K-groups (17) | `GroundTheory.{ProfiniteCohomology (Poitou-Tate),TateCohomology}`, `Formalism.CoboundaryTransfers` |
| L2 estimates (16) | `ReciprocityTheory.L2DbarEstimates` (227 modules) |
| GRH (20) | `Formalism.GammaFactorNonvanishing.CritLine`, `Statements`, `Main` |

## 3. Architecture **[V]**

Libraries (from `lakefile.toml`), with sizes:

| library | modules | lines | role **[D]** |
|---|---:|---:|---|
| `Development` | 141,928 | 12.23M | bulk development; `AbelianVarietyTheory` alone is 99,187 modules / 8.2M lines, with `Definitions`, `Proofs`, `PublishedTheorems`, `BlockTheory`, `Counterexamples`, `Statements`; also `AutomorphicArithmetic` (18k), `AutomorphicSpectrum` (15k), `WeilBound` (7k) |
| `Formalism` | 18,254 | 3.20M | ~150 small topical libraries (LocalToGlobal, PeriodIntegrals, SharpRestriction, HermitianCurvature, LandauZeroFreeBounds, GL3MeanSquares, BehrendSets, ...) |
| `GroundTheory` | 8,507 | 1.12M | foundations: function fields, global/local fields, Brauer, cohomology, heights and theta |
| `ReciprocityTheory` | 3,845 | 0.56M | reductive groups, class field theory, Chebotarev, geometry of numbers |
| `CompanionTheory` | 2,027 | 0.19M | spectral geometry, Harish-Chandra modules, Bessel models |
| `PositivityTheory` | 449 | 55k | automorphic forms; "published inputs" |
| `Lemmata`, `Supplements`, `BuildAid`, `Statements`, `Main` | 167+3+5+2 | ~10k | glue; `BuildAid` = 5 files that add names to a library-suggestions deny list (`run_cmd`, benign) |

**Proof spine.** `Main` -> `Supplements.Kernels.MainTheorems`:
`allChi : UpperTheory.EveryCharacter` (= "L(s,chi) != 0 for Re s > 1/2 for every Dirichlet character",
i.e. GRH's non-vanishing form), `rhOfAll := Formalism.VW.rh_of_every allChi` (functional equation step in
`Formalism.GammaFactorNonvanishing.CritLine`). `everyCharacter` is in
`Development.AutomorphicArithmetic.CharacterBoxes.MainConclusion`:
`everyCharacter_of_row (h : Row0b ...) := every_character_of_literature_of_vWin ⟨h, recTExists, h⟩ (vwin_of_row h)`, discharged by
`Gal.Int.galoisLocalGlobalStrong_recParameter`. Three inputs:

* `Row0b`: Galois representations for regular algebraic polarised cuspidal representations of GL_a
  over CM fields (existence plus Hodge-Tate data);
* `recTExists`: existence of a local Langlands-type reciprocity parameter at every finite place;
* **`VWin`** (the new analytic claim; `VWinAt psi 401`): for every character `psi` and `eps < 1/52`,
  there are `J, X0` such that for all `X ≥ X0` and **every** "window pair" of primes `(q,d)`
  (`WinPair`: `q ≡ 3 mod 8`, `d ≡ 7 mod 16`, `log q, log d` in explicit windows, `q | d+1`, and
  **every odd prime `p ≤ Y^(eps/5)` divides `d+1`**) there is `Y` with `X^(1/J) ≤ Y ≤ sqrt X` such that
  for all `x ∈ [Y, Y^2]` and every number field `E` cut out by `(psi,q,d,2^(e+2))` (`IsChiField`) the
  Galois-cohomology length bound `VVle E ⌊x^401⌋ (sqrt(exp(x^eps)))` holds, i.e.
  `Σ_{l∈S} log l · Σ_{1≤e<t} shaLen(l,e) ≤ B` for every finite set `S` of primes (and `shaLen` finite).
  Existence of the window pairs is a *separate* statement (`ExistsSplitGoodPrimePair`, below).

The prime pairs come from `ExistsSplitGoodPrimePair`, derived from an explicit **PNT in progressions
with possible exceptional zero** (`PNTAPRelW`, proved in `Formalism/GL3MeanSquares/.../PNTFinal.lean`)
and a numerical zero-density bound (`NumericalZeroDensityBound.lean`, `zero_density_of_hypothesis`).

**Import graph.** 753,569 internal edges; **every module is reachable from `Main`** (100%); longest chain
**203** modules; hubs are mostly `Development.AbelianVarietyTheory.{Definitions,PublishedTheorems}`
(`CTSmallCone` is imported by 3,088 modules). Heaviest cross-library flows:
`Development->Formalism` (41,859), `Development->ReciprocityTheory` (38,051), `Development->GroundTheory` (7,532).

**Logical (name-level) cone.** Following only *explicitly named* references from `riemannHypothesis`
reaches **665,142 declarations in 139,002 modules (79.3%)**; the share is ~uniform across Statement,
Proof, Definition and PublishedTheorems modules. This is a *lower bound* (implicit instances and
simp lemmas are not followed; name resolution is approximate), so the proof does **not** have a small
logical core you can read instead of the whole; reading must be interface-first (section 7).
(`MumfordConstruction`, a deep published statement, is defined once, imported ~500 times and
never referenced by name: imports overstate dependencies.)

## 4. Trust-surface scan **[V as text scan; this is not a verification]**

Over all 175,187 files: **0** `sorry`, **0** `axiom` lines, **0** `native_decide`, **0** `unsafe`,
**0** `@[implemented_by]/@[extern]`, **0** `initialize`, **0** uses of Lean's `IO` process/file/env/print
functions (43 files contain the token `IO.`, but it is a *mathematical* namespace
`...IntegralLatticeDensity.IO` with names like `IO.cf`, `IO.HfInt`), **0** `skipKernelTC`-style options.
Elaboration-time code: 5 `run_cmd` (the `BuildAid` deny-list lines), 22 files with `macro`/`elab`
(tactic macros for simp/omega patterns, plus three metaprograms: `kexactB` assigns a term without
elaborator type-checking, `kcopy` rewrites a term to a target structure type, `cpt_copy_thms` re-adds
copied declarations through `addDecl`; all outputs still go to the kernel). 88,137 `set_option`
uses (mostly `maxHeartbeats`). **What this does not establish**: that the formal statements mean
what their names say, or that the whole thing compiles; only a full build and `#print axioms` do.

## 5. Reusable assets (build closure = files that must compile)

Full table: `data/assets.tsv` (closure sizes computed from the import graph; hours at the Lean
session's measured 9.6 s/file, single core).

| asset | module (short) | closure files | ~core-h |
|---|---|---:|---:|
| Linnik: least prime in a class `<= C q^L` (**existential** `C,L`) | `ThetaCorrespondence.Linnik` | 517 | 1.4 |
| Arithmetic large sieve, one class per prime | `GlobalInterpolation.ArithmeticLargeSieveOneResidueClassPerPrimeStatement` | 106 | 0.3 |
| Multiplicative large sieve (primitive chars) | `...MultiplicativeLargeSieveStatement` | 105 | 0.3 |
| Brun-Titchmarsh (existential const) | `...BrunTitchmarshExistsConstStatement` | 112 | 0.3 |
| Siegel-Walfisz | `Formalism.LandauZeroFreeBounds.SiegelWalfiszAPOfSiegelLower` | 114 | 0.3 |
| PNT in progressions + exceptional zero (`PNTAPRelW`) | `...JacobiCharacterSums.PNTFinal` | 209 | 0.6 |
| log-free zero-density | `...LogFreeZeroDensityDirichletOneModulusStatement` | 426 | 1.1 |
| Deuring-Heilbronn repulsion | `...RepulsionStatement` | 16 | 0.04 |
| Mertens-type sums (`sum log p/p <= log x + log 4`, `sum 1/(p-1) <= 7 loglog y + 6`, `sum_{N/2<p<=N-3} 1/p >= 1/(5 log N)`) | `...DivisibilityProofs.SumPrimeLogDivLeStatement` etc. | 2 to 8 | ~0 |
| Behrend-type random-subset toolkit (`Select`, `TopsBad`, `BadOrbit`, `BadMean`, `BehrendBound`) | `Formalism.BehrendSets.FinalE` | 13 | 0.03 |

Caveats **[V]**: Linnik and Brun-Titchmarsh are *stated* with existential constants (`∃ C L`, `∃ C`),
so no numeric exponent can be read off the statements (the Lean session reported an explicit 48 inside
the Brun-Titchmarsh proof); the large sieve is the "one class per prime / `ω=1`" form only
(no general `ω(p)`, hence **no prime-pair `ω=2` upper-bound sieve** here); the `Statement` modules are
standalone restatements in Mathlib-only vocabulary, ideal import targets.
`data/nt_statements.tsv` lists 38 elementary number-theory statements (Mathlib vocabulary only).

## 6. Relevance triage against our barriers **[V where measured, I otherwise]**

* **Door 1 (covering CSP: odd-prime moduli 3..457 (87 of them; the WP9 plan says 88), one class each,
  minimise uncovered primes).**
  No covering/set-cover/CP-SAT/LP/annealing/belief-propagation content. The only sieve is the large
  sieve, which bounds `|U|` from **above**; for the Door-1 instance (`Q=457`, `N=122,000`) the formal
  bound gives `|U| <= 318,514`, vacuous against a universe of 11,474 odd primes and 400x the known
  optimum region (~760-870). It cannot certify a floor. `BehrendSets` provides formal *existence*
  templates (size-concentrated random subsets with bad-window first-moment bounds), similar in spirit to
  the D1.3(i) "second-moment control", but it supplies no search method.
* **Parity / Door 3 closure theorem.** No parity-of-prime-factor-count machinery for integers, no
  class-group computation. "Frobenius-Stickelberger" names refer to a theta-function determinant, not the
  Stickelberger-Swan discriminant parity used in the function-field filter; `sign_perm` lemmas are
  generic. Consistent with the team's (H2) "no sub-modexp compositeness detector".
* **WP3 decoding / 460-nat modulus budget.** No identifiers on list decoding, Reed-Solomon, Coppersmith,
  LLL/BKZ (a case-insensitive "lll" matches words like "FullLattice"). Lattice material is Minkowski /
  successive minima / covolume / shortest-vector lemmas for Hermitian lattices over number fields, plus one
  genuine 2-D reduction step (`plane_lattice_reduction_step`); "lattice reduction" elsewhere means reduction
  mod a prime. The multiplicity is representation-theoretic.
* **Direction of the analytic tools.** Linnik, Siegel-Walfisz, PNT-AP and zero-density *produce primes in
  classes*; our search needs *composites* (absence) at moduli ~q^1.05, outside GRH's range anyway.
* **What would change this assessment**: the claimed core (`VWin`, `VVle`, `IsChiField`, `WinPair`)
  was read only at statement level, and ~170,000 modules were classified by name only. A technique
  hiding under unfamiliar names cannot be excluded; nothing in the statement catalogue points to one.

## 7. Conventions worth stealing (methodology) **[V counts, I value]**

1. **Statement files.** 46,610 `...Statement.lean` files restate a result in Mathlib-only vocabulary with a
   `first | exact ...` proof; an auditable API without reading proofs.
2. **Named-Prop hypotheses.** 89,053 `def X : Prop := ...` statements plus implications such as
   `PNTAPRelW → ...`, discharged once at the end (`pnt_progressions_relative_weak_holds`).
3. **Closure-first builds.** Each result's import closure is small, so sub-libraries can be built and
   checked independently (how the Lean session verified Linnik).
4. **Counterexample certificates.** Refuted lemmas are kept as `def Foo : Prop := ¬ ...` with explicit
   witnesses (192 `Counterexamples` modules; e.g. `RankGapBounds.CloudMinFalse`, witness `![114,...,0]`).
5. **Kernel-first proof engineering.** repeated-pattern tactic macros, term assignment without
   elaborator checks, declaration copying; lakefile `maxHeartbeats 4000000`, `--tstack=400000`,
   `autoImplicit=false`; no module docstrings at all (0%), long descriptive module names instead.

## 8. How to query (tools are in `tools/`; all read text only; run with `python3 -I`)

```
python3 -I tools/index.py  <src_dir> <out_dir>      # parse all .lean -> out/index.jsonl (43 s, 4 cores)
python3 -I tools/analyze.py <out_dir>               # structure, hubs, depth, reachability
python3 -I tools/q.py <out_dir> props|decls|mods|imps <regex> [limit]
python3 -I tools/closure.py <out_dir> <module> ...  # import closure + build-cost estimate
python3 -I tools/stmts.py  <src_dir> <out_dir>      # extract Statement-file theorems -> statements.json
python3 -I tools/cone.py   <src_dir> <out_dir> <fullname>   # approximate name-level cone
```
Re-download: parts `01..14` from the URLs above; check the SHA-256 before extracting; extract into an
empty directory; list the tar first (`tar -tvzf`) to reject non-regular files.

## 9. Limits

Name-based area descriptions are guesses for most of the ~170 small areas; the keyword scan is noisy
(e.g. "psiEven" matches "sieve" case-insensitively); the cone is approximate; nothing was built.
Next useful steps, in order of value: (a) the Lean session builds the 100-file closures in section 5 and
states reusable lemmas against them; (b) a reader goes through `Formalism.GL3MeanSquares` (PNT-AP and
zero-density) and `Formalism.LandauZeroFreeBounds` statement-by-statement; (c) only if someone wants the
claim itself checked: the ~470 core-hour full build on an isolated machine, then `#print axioms riemannHypothesis`.
