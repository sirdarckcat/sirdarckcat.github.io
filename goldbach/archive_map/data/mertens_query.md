# Query from the Lean session: is Mertens' third theorem in the archive?

Answer: **no**, in neither the product form with e^(-gamma) nor the second-theorem form with the
Meissel-Mertens constant. Searched: every declaration in 175,187 modules for (a) `eulerMascheroni` together with a
prime-sum, (b) a product over primes of `(1 - 1/p)`, (c) `Real.log (Real.log _)` with prime reciprocals,
(d) names containing Mertens / Meissel / mertensThird / prod_one_sub_inv (`tools/mertens_scan.py`, 179 hits reviewed).
No statement combines gamma with a product or sum over primes of 1/p, and none states `Tendsto ... (nhds (exp (-gamma)))`.

## What exists

### 1. The identification of gamma, in von Mangoldt form (proved)
`Formalism.HermitianLattices.GL2a2.PsiZeroConst`, defined in module
`Formalism.GL3MeanSquares.PrimeCountAsymptoticInProgressions` (closure 3 files):

    def PsiZeroConst : Prop :=
      Tendsto (fun U : ℝ => ∫ u in (1 : ℝ)..U, (psumR (fun n => Λ n) u - u) / u ^ 2) atTop
        (𝓝 (-1 - Real.eulerMascheroniConstant))

with `psumR a u = ∑ n ∈ Icc 1 ⌊u⌋₊, a n` (so `psumR Λ = psi`).
Proof: `theorem psi_zero_integral_constant : GL2a2.PsiZeroConst` in module
`Formalism.GL3MeanSquares.HookFormulaTorsion.PsiZeroIntegral`, **import closure 117 files (~0.3 core-hours)**.
No `*Statement.lean` wrapper exists. The same module proves `LogDerivSeries` (sum of Lambda(n) chi(n)/n tends to
-L'/L(1,chi) for chi != 1).
By Abel summation (my derivation, not in the archive): sum_{n<=U} Lambda(n)/n = psi(U)/U + int_1^U psi/u^2, hence
int_1^U (psi-u)/u^2 = sum_{n<=U} Lambda(n)/n - psi(U)/U - log U. So PsiZeroConst together with psi(U)/U -> 1 gives
sum_{n<=U} Lambda(n)/n = log U - gamma + o(1).
I did not find psi(x) ~ x for the trivial character as a proved theorem: `PNT` in
`Development.AbelianVarietyTheory.Definitions.GlobalTwisting.LFunctionPositiveConductorFourEight` is a definition for
twisted psi0 with error C u exp(-c sqrt(log u)). The proved PNT is `pnt_progressions_relative_weak_holds`
(`PNTAPRelW`, moduli divisible by 8, `...JacobiCharacterSums.PNTFinal`, closure 209).

### 2. Proved Mertens-type inequalities (no constant identification)
| statement | module | closure |
|---|---|---:|
| `mertens_first_vonMangoldt`: `∃ CM, 0 ≤ CM ∧ ∀ y, 1 ≤ y → |∑ n ∈ Icc 1 ⌊y⌋₊, Λ n / n - Real.log y| ≤ CM` (CM = log 4 + 4) | `Development.AbelianVarietyTheory.Proofs.IwasawaDecomposition.LogFactorialEqSumVonMangoldtMulDiv` | 1 |
| `mertens_first_log_four`: `∀ x, 1 ≤ x → ∑ p ∈ (Finset.Iic ⌊x⌋₊).filter Nat.Prime, Real.log p / p ≤ Real.log x + Real.log 4` (Statement file exports `GlobalTheory.T.sum_prime_log_div_le`) | `Development.AutomorphicSpectrum.Proofs.DivisibilityProofs.SumPrimeLogDivLeStatement` | 8 |
| `mertens_upper`: `∑ n ∈ range (⌊y⌋₊+1), vonMangoldt n / n ≤ Real.log y + 2` | `Development.AutomorphicArithmetic.DedekindLFunctions.LandauTheorems.mertensUpper` | 3 |
| `MertensUpper.Statement`: `∃ C, ∀ B, 2 ≤ B → ∑ p ∈ (Iic ⌊B⌋₊).filter Nat.Prime, Real.log p / p ≤ Real.log B + C` | `GroundTheory.HeightsAndTheta.Heights.IntegralModels.PMertensUpper` | 6 |
| `sum_primes_inv_pred_le_loglog`: `∀ y, 3 ≤ y → ∑ p ∈ (range (y+1)).filter Nat.Prime, 1 / ((p:ℝ) - 1) ≤ 7 * Real.log (Real.log y) + 6` | `Development.AbelianVarietyTheory.Proofs.DivisorProofs.SumPrimesInvPredLeLoglogStatement` | 3 |
| `inv_five_log_le_sum_inv_primes_half_interval`: `∀ N, 100 ≤ N → 1 / (5 * Real.log N) ≤ ∑ p ∈ (range (N+1)).filter (fun p => p.Prime ∧ N < 2*p ∧ p+3 ≤ N), 1 / p` | `Development.AbelianVarietyTheory.Proofs.DivisorProofs.InvFiveLogLeSumInvPrimesStatement` | 2 |

### 3. Stated but, as far as I can find, not proved (only used as hypotheses)
* `MertensReciprocalBound`: `∀ y > 1, ∑ p ∈ pr y, 1 / p < Real.log (Real.log y) + 0.27 + 1 / (Real.log y) ^ 2` and
  `MertensLogLowerBound`: `∀ y > 1, Real.log y - 1.34 - 1 / (2 * Real.log y) < ∑ p ∈ pr y, Real.log p / p`
  in `Formalism.PieriBlockIdeals.MertensReciprocalElementary`.
* `MertensP`: `∃ K ≥ 1, ∀ z ≥ 3, ∑_{p≤z} 1/p ≤ log log z + K ∧ 1/(K log z) ≤ ∏_{p≤z} (1 - 1/p)` in
  `Formalism.JacobiWeightFamilies.LFunctionOnePositive`.
* `MertensUpper` (product form): `∀ z ≥ 2, ∏_{p≤z} (1 - 1/p) ≤ 1 / log z` in
  `Formalism.LandauZeroFreeBounds.LogDerivRegionChiOf`.

## Which half is missing
The constant identification exists in von Mangoldt form (item 1, needs a PNT-strength input to convert). Missing is the
passage from sum Lambda(n)/n = log U - gamma + o(1) to the prime form: remove prime powers, Abel-sum to the
1/p sum, and identify the Meissel-Mertens constant, from which the product with e^(-gamma) follows. I did not check Mathlib.
