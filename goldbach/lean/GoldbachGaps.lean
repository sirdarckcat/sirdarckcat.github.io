import GoldbachGaps.Basic
import GoldbachGaps.Effective
import GoldbachGaps.Covering
import GoldbachGaps.Counting
import GoldbachGaps.ECPP
import GoldbachGaps.Desert
import GoldbachGaps.Record150
import GoldbachGaps.Record199
import GoldbachGaps.Record199_g125269
import GoldbachGaps.Record199_g133981
import GoldbachGaps.Record200_g146191
import GoldbachGaps.Record200_g157837
import GoldbachGaps.Records
import GoldbachGaps.Record23_g11701
import GoldbachGaps.Record23_g10729
import GoldbachGaps.Record23_g10771
import GoldbachGaps.Fscan.Fermat52
import GoldbachGaps.Fscan.Fermat26
import GoldbachGaps.Fscan.Schedule
import GoldbachGaps.Fscan.Kernel52
import GoldbachGaps.Fscan.Kernel26
import GoldbachGaps.Fscan.Fermat30
import GoldbachGaps.Fscan.Kernel30
import GoldbachGaps.Fscan.ClassStage
import GoldbachGaps.Cap.Rows
import GoldbachGaps.Cap.Budget
import GoldbachGaps.Cap.FirstMoment
import GoldbachGaps.Cap.Poly
import GoldbachGaps.Cap.Transfer
import GoldbachGaps.Cap.Layers
import GoldbachGaps.Cap.Selection
import GoldbachGaps.Cap.Brainstorm
import GoldbachGaps.Cap.Tilt
import GoldbachGaps.Cap.Radius
import GoldbachGaps.Cap.BlackBox
import GoldbachGaps.Cap.Population
import GoldbachGaps.Gpu.Limbs
import GoldbachGaps.Gpu.MontSqr
import GoldbachGaps.Gpu.Fermat
import GoldbachGaps.Gpu28.Conv
import GoldbachGaps.Gpu28.Step
import GoldbachGaps.Gpu28.Final
import GoldbachGaps.Gpu28.Kernel
import GoldbachGaps.FunctionField.Stickelberger
import GoldbachGaps.FunctionField.ParityDesert

/-!
# Least Goldbach summands in Lean

For an even `N`, the least Goldbach summand is `g(N) = min {p prime : N - p prime}`.
This library formalises the theorem-shaped parts of `goldbach/` and `slop/goldbach/`:

* `Basic`    – definitions; every odd prime is `g(N)` for arbitrarily large even `N`
               (paper Theorem `thm:dirichlet`), hence `g` is unbounded.
* `Effective` – with Linnik's theorem as a hypothesis (it is not in Mathlib), every odd prime
               `s` is `g(N)` for an even `N ≤ C · (primorial (s-1))^L + s`.
* `Covering` – the covering certificate and its unconditional realisation
               (paper Proposition `prop:cover`, Theorem `thm:coverdirichlet`).
* `Counting` – the counting bound: for large `X` some even `n` in `(X, 2X]` has no
               Goldbach summand below `log X · log log X / 48`.
* `ECPP`     – a kernel-checkable elliptic-curve primality criterion (one Atkin–Morain
               step), proved sound against Mathlib's group law.
* `Desert`   – a kernel-checkable test that no prime in a block is a Goldbach summand.
* `Record150`, `Record199` – generated certificates (see `scripts/gen_record.py`) for the
               150-digit record `g = 104527` and the 199-digit record `g = 119419`.
* `Record199_g125269`, `Record199_g133981` – generated certificates for the two records of
               2026-11-22 below `10^199` (`goldbach/records/budget_1e200_199digit_g*` on
               branch `ccr-2ce9e63a-hn0fuw`): `g = 125269` and `g = 133981`.
* `Record200_g146191`, `Record200_g157837` – generated certificates for two records below
               `10^200` (`goldbach/records/budget_1e200_200digit_g146191` and `…_g157837` on
               the same branch): 200-digit `N` with `g(N) = 146191` and, the standing record,
               `g(N) = 157837`.
* `Records`  – the bounded record games as closed theorems.
* `Record23_g11701`, `Record23_g10729`, `Record23_g10771` – generated certificates for three
               23-digit records of 2026-11-22 (`goldbach/records/threshold_23digit_*` on
               branch `ccr-2ce9e63a-hn0fuw`): `g(54284735534856910692542) = 11701`,
               `g(30625623272505310405982) = 10729`, `g(35505990484772441527442) = 10771`.
* `Fscan.*`  – correctness of the arithmetic kernels of the `goldbach/fscan` scanner (code
               at commit `a3ab69c` on branch `ccr-d4a17dd0-7uu03r`), one lane at a time:
               `Fermat52` / `Fermat26` are the Montgomery squaring steps `F52_STEP` and
               `FM_STEP` (relation, bounds, no 64-bit overflow); `Schedule` is the exponent
               schedule; `Kernel52` / `Kernel26` combine them into "the lane reports 1 iff
               `2^(n-1) ≡ 1 (mod n)`"; `ClassStage` is the division-free residue of
               `exact_stage`. `Fermat30` / `Kernel30` do the same for the 3-limb, 30-bit
               step `FM3_STEP` added at commit `1d8ab96` on branch `ccr-b8c25887-i6tn9f`.

* `Cap.*`    – the exact laws under the cost model of the capped game (largest `g(N)` for
               `N < 10^200`): `Rows` (a row `N - q` is composite iff `q ≡ N` modulo a prime
               `≤ √(N - q)`; prime moduli suffice; two rows share only divisors below `Q`),
               `Budget` (`N < X` with residues in prescribed sets `A r`: at most
               `∏ |A r| · (X / ∏ r + 1)`), `FirstMoment` (averaged over nonzero residue
               vectors exactly `|P| · ∏ (r - 2)/(r - 1)` rows are left, and the average of
               rows × boost is at least `|P| / 2` for every modulus set), `Poly` (`N = f(u)`
               makes the rows `f(c)` composite; at most `√Q + 1` of them and `√X + 1`
               members for degree `≥ 2`), `Transfer` (a prime desert gives a Goldbach gap),
               `Layers` (a fixed layer, a pigeonhole layer and a mop-up layer of moduli give
               an even `N` in an explicit window with no Goldbach summand below `Q` as soon
               as three counts allow it: the finite skeleton of lower bounds for
               `max {g(N) : N ≤ X}`, with the structure of the rows that survive a layer
               `N ≡ 1 (mod p)`), `Selection` (with independent rows, the logged hit mass
               `Σ (1 - p)^(rows left)` over any selected set of members is exactly the
               expected number of successes among them), `Brainstorm` (the statements with a
               proof among the 100 ideas of 2026-11-22: a zero class covers one row; two
               candidates that share a row value agree only on moduli of product below `g`;
               a move that keeps known factors pays for them in modulus; one exponent serves
               every row in a Fermat test; abandoning members never lowers the tests per
               success; faulty arithmetic costs false alarms, not successes; powers are
               sparse in a window; prescribed large divisors for 38 rows fix `N < 10^200`),
               `Tilt` (selection on a normal count of rows: weighting `N(μ, v)` by `e^{t x}`
               gives `e^{μ t + v t²/2} N(μ + v t, v)`, so the members with at most
               `μ - z √v` rows hold the fraction `Φ(λ - z)` of the successes,
               `λ = -√v ln(1 - p)`; a member `z` standard deviations below the mean is
               `e^(λ z - λ²/2)` times as likely to succeed as the average one, which caps what
               any search inside a progression can gain), `Radius` (lattice decoding and the
               search problem: reaching a smooth part `c` times the typical one needs
               `c² ≥ e ln K / 4`, so `c ≥ 3.88` for `K = 2^32`; in list form, a list of
               `2 ≤ ℓ ≤ r/2` classes modulo `r` carries `ln 2 - 2 ln r / r` more nats of
               information than it contributes to the lattice condition, so inside the
               Johnson radius only singleton lists, i.e. the cover, are left), `BlackBox` (a
               method that only asks members whether they are good finds one of the `g` good
               ones among `K` with `m` questions for at most the fraction `m g / K` of the
               instances), `Population` (independent rows left with probabilities `s_j`:
               `E [x^R] = ∏ (1 - s_j + s_j x)`; the members with at most `k` rows left
               contribute at most `u^(-k) ∏ (1 - s_j + s_j y u)` to `E [y^R]`; at most `μ - a`
               rows left has probability at most `exp (-a²/(2μ))`; whichever `m` members of a
               population are tested, their hit mass is at most `m y^k` plus that of the
               members with fewer than `k` rows; a merge of two lists of residue combinations
               costs at least `2 P / (K √(a b))` per member found, so the constrained primes
               can exceed the population by `F - C` nats and no more).
* `Gpu.*`    – the GPU Fermat kernel `fermat2` of `goldbach/phd/campaign3_gpu/gpu_fermat.py`
               (commit `6ef621f`, branch `ccr-8ffe9d7a-4ni11u`), one thread, for any number
               of 32-bit limbs: `Limbs` (carry chain, borrow chain, comparison loop, shift),
               `MontSqr` (`mont_sqr` is a CIOS Montgomery squaring with result below `n`;
               `dbl_mod` doubles modulo `n`), `Fermat` (the Newton inverse modulo `2^32`,
               the word and bit loop, and `fermat2_correct`: the flag is `1` iff
               `2^(n-1) ≡ 1 (mod n)`, for `n = cq + k·M` odd, `> 1`, below `2^(32 L)`,
               `k < 2^32`).
* `Gpu28.*`  – the GPU Fermat kernel `fermat28` of `goldbach/fermat661/cuda/` (commits
               `560a2cf` and `fa7d9d1`, branch `ccr-b8c25887-i6tn9f`): 24 limbs of 28 bits,
               Montgomery squaring by columns with lazy 64-bit accumulators, values kept below
               `4n`, no `R mod n`. `Conv` (the column sums of a square), `Step` (the columns
               for input limbs below `2^29`: exact accumulators, `R · Y = X² + μ N`, `Y < 2N`;
               then the plain step with its carry chain and the redundant step
               `x_i = y_i << b`, both with `R · Y' = 2^b (X² + μ N)`, `Y' < 4N`), `Final` (the
               comparison loop, the borrow chain, the two conditional subtractions and the
               test against 1), `Kernel` (the Newton inverse with seed `(3·lo) xor 2`, the
               loop, and `fermat28_correct`: the lane reports `1` iff `2^(n-1) ≡ 1 (mod n)`,
               for odd `n` of 642 to 668 bits; `fermat28r_correct`: the same for the
               redundant-limb kernel in production, with its normalisation block). The set-up
               that derives the limbs, `c` and the bits of the schedule from `n` is a
               hypothesis, and the PTX instructions `mul.wide.u32`, `mad.wide.u32` are taken
               as the exact 32 × 32 → 64 product and multiply-add; `scripts/gpu28_check`
               compares the model with every generated step file compiled for the CPU, set-up
               included.
* `FunctionField.*` – the toy setting `F_q[x]` of the research programme in
               `goldbach/sublinear/` (branch `ccr-d4a17dd0-7uu03r`), where "`N - Q` is
               reducible for every monic irreducible `Q` of small degree" replaces a Goldbach
               gap. `Stickelberger`: Stickelberger's theorem in Swan's form (Pellet's formula),
               which is not in Mathlib: over a finite field of odd characteristic,
               `χ(discr g) = (-1)^(deg g - r)` for squarefree `g` with `r` irreducible factors
               (`stickelbergerSwan`), from `discr (f g) = discr f · discr g · Res(f, g)²`
               (`discr_mul`) and the action of the Frobenius on a Vandermonde determinant.
               `ParityDesert`: over any field, if `N' = 0`, `Q` is monic of degree
               `d < n = deg N` with `d ≠ 0` in the field and every irreducible factor of `Q'`
               divides `N`, then `discr (N - Q) = ± λ^(n-d-1) d^(n-d) discr Q` (`discr_sub`) and
               `N - Q` is squarefree; hence over a finite field the parity of the number of
               irreducible factors of `N - Q` (`parity_card_factors`); over a field with a
               square number of elements and for a non-square `λ`, `N - Q` is not irreducible
               (`not_irreducible_sub_of_isSquare_card`); and `N = c · V^p` has `N - Q`
               reducible for every monic irreducible `Q` of degree at most `J + 1` when `V` is
               divisible by all irreducibles of degree at most `J` (`desert`): a desert with
               no factor exhibited and no congruence paid for the top degree.
               The condition `d ≠ 0` is not needed: with `e`, `ℓ` the degree and leading
               coefficient of `Q'`, `discr (N - Q) = ± λ^(n-2-e) ℓ^(n-d) discr Q`
               (`discr_sub_general`), and the number of irreducible factors of `N - Q` is even
               exactly when `(-1)^(d+1+e) χ(ℓ)^(n-d) = 1` (`even_card_factors_iff`), which
               decides every row, also of a degree divisible by the characteristic
               (`desert_general`). `scripts/parity_check/gen_parity.py` compares the general
               formula with full factorisations over `F_3`, `F_5`, `F_7`.

## Building

`lake exe cache get && lake build`. The record files with about 200 digits dominate: the
kernel replays the full certificates, several minutes and about 6 GB of memory for each.
No `sorry`, no `native_decide`, no extra axioms: `#print axioms` on any theorem here lists
only `propext`, `Classical.choice` and `Quot.sound`.

## Regenerating the record files

    python3 scripts/gen_record.py ../records/threshold_150digit_g104527 Record150 \
        GoldbachGaps/Record150.lean
    python3 scripts/gen_record.py ../../slop/goldbach/records/r200/record_r200_r1.json \
        Record199 GoldbachGaps/Record199.lean

## Not covered

The 2,480-digit height record (`slop/goldbach/records/g1`, `g = 1157341`). `ECPP` uses
affine coordinates with one modular inversion per group operation, recomputed inside the
kernel; that is fine at 200 digits and far too slow at 2,480. A projective-coordinate
checker would be needed for it.
-/
