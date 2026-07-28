# SoK: Engineering Large Least Goldbach Summands

*Systematization of knowledge from every certified record in this repo:
the covering-systems paper (`slop/goldbach/paper.tex`), the CPU-session
records (`slop/goldbach/records/`, PRs #21–#23), and the GPU-session
records (`goldbach/records/`, PR #24). 2026-07-29.*

For even N, g(N) = min{p prime : N−p prime}. Nature keeps g tiny —
g ≤ 9,781 for all even N ≤ 4×10¹⁸ — so every large value below was
*manufactured*. This document systematizes how, what it costs, and what
we now know that we did not know at the start.

## 1. Taxonomy of constructions (weakest → strongest)

| family | mechanism | measured cost | verdict |
|---|---|---|---|
| Factorial/Wilson (`27!+28`) | divisibility accident | g=71 at 29 digits | pedagogy only |
| Primorial + Dirichlet | force p ∤ N−p for all small p | g=nextprime(P) at θ(P) digits (exponential) | proves unboundedness, unusable for records |
| **Full covering system** (paper, 2025) | every prime p<Q hit by a class p ≡ N (mod r) | Q=10⁵ at 1,020 digits; Q=10⁸ at 327,455 digits (no partition) | first real records; pays for *certainty* it doesn't need |
| **Partial cover + progression search** (all 2026 records) | cover most primes; PRP-test the k residuals per candidate N = N₀+tM | Q=10⁵ at **150 digits**; g=1,157,341 at 2,480 digits | the frontier; everything below is about its economics |
| Prime-gap transfer | park all N−p inside a known gap | needs a *fully verified* gap > 1.1M: endpoints are ~18k-digit PRPs | blocked (resource-strength); dominated by covers — a Goldbach gap needs only the sparse set {N−p} composite, not an interval |

The last row is the theoretical point the whole project demonstrates:
**Goldbach gaps are strictly cheaper than prime gaps.** A 2,480-digit N
carries a Goldbach desert of 1.16M, while an *ordinary* prime-free
interval of that length needs numbers of ~18,000 digits (and still has
no proven endpoints). The sparse-cover advantage is ~7× in digits today
and widens with the target.

## 2. The cost model (12 certified records; hit statistics from the n=7 fully-logged searches)

Let L = ln N, let the cover use moduli set R with residual count k, and
let p₁ ≈ e^γ·ln(max contiguous prime)·(1/L) be the per-residual
probability that a complement is prime. Then:

- **Search exponent**: E[t to success] ≈ e^{p₁k}. This single number
  decided every campaign. On a consistent consumed-t basis the n=7
  fully-logged hits landed at 0.25×–3.0× of E (median 0.5×; the
  exponential clock is merciless about variance — plan for 3×).
- **Digit budget split**: ln N = (modulus nats) + (search nats). Search
  nats are nearly free if you have throughput (ln t ≈ 25 for a GPU
  fleet vs ≈ 20 demonstrated on 4 CPU cores) — this is why the GPU record jumped
  29 digits in one step: it moved ~7 nats of cost from the modulus to
  the scan.
- **Cover quality**: random residues leave k₀ ≈ 0.74·π(Q)/ln y;
  greedy+GRASP/SA reliably reaches ≈ 0.60·k₀ and then plateaus hard.
  Every further 1% of k is worth e^{0.01·p₁k₀} of search time — at the
  frontier that's the whole game, and it is the *least* solved part
  (CP-SAT/ILP never got tried seriously; registered as the open lever).
- **Range-bound vs compute-bound**: under a size cap (N < 10^199,
  N < N*, N < 10^200) the binding constraint flips from CPU to
  t-range = cap/M; the optimum then *shrinks* M below the naive value
  (counterintuitive but derived and confirmed twice: each nat removed
  from M buys a full nat of range but costs only ~0.2 nats of exponent).
- **Certification wall**: ECPP+verification is minutes to 200 digits,
  ~2h (+2h python re-verify, +2h APR-CL) at 2,480 digits, and scales
  ~quartically — it caps Game-1-style ladders near ~4,000 digits with
  present tools, long before search does.

## 3. What each record contributed

- **1,020-digit g=100,747** (paper): full covers work but overpay ~7×;
  established ECPP-certified partitions as the proof standard.
- **199-digit g=110,917 / N < N\***: first partial-cover record here;
  validated the e^{p₁k} model the hard way: hit at 99.9% of the range,
  3.0× the selection-adjusted expectation — the outlier that taught us
  to respect variance.
- **193 → 186 → 179-digit ladder**: the digit-walk works; each ~7-digit
  rung cost ~2.5× the previous search — measured, not theorized.
- **2,480-digit g=1,157,341** (Game 1): at huge L the exponent
  collapses (p₁k ≈ 7.7 → hit #443); big-g records are *search-trivial,
  certification-bound*. Beat the 1,113,137 prime-gap benchmark with a
  number 7× shorter than the gap's own endpoints.
- **2,692-digit g=1,134,871** (GPU megagap): independent confirmation
  of the certification-bound regime by the second pipeline.
- **150-digit g=104,527** (GPU): throughput converts directly into
  digits (e^{25} affordable ⇒ −29 digits); also proved the
  git-checkpointed fleet protocol across ~10 preemptions.
- **200-digit g=112,249 attempt** (GPU): negative result worth keeping:
  raw throughput without re-optimizing the cover for the range-bound
  regime does *not* beat a tuned CPU cover (119,419 stood).

## 4. Soundness: what it takes to not fool ourselves

All of these actually occurred in-session and were caught by process:

1. A "PASS" from a vacuously-parsed GP script (multi-line loop silently
   skipped) — caught because the checker asserts the *count* of scanned
   primes against an independently computed π(q).
2. PARI thread-stack overflows mid-`primecert` leaving a 2-byte junk
   "certificate" — caught by type-checking the cert and re-verifying it
   in a from-scratch Python implementation before accepting.
3. Self-matching pkill/pgrep and cwd resets silently killing or
   misplacing multi-day jobs — solved by git-committed resume marks
   (`safe_k` / logged t~), which turned ~10 container losses into
   wall-time-only losses.
4. An adversarial code audit (independent agent, executable tests)
   found zero false-accept paths but three false-*reject* bugs — the
   asymmetry (one-sided SPRP witnesses, gcd-surfacing EC arithmetic)
   is what makes the verifier trustworthy.

The resulting standard, now uniform across both pipelines: CRT
reconstruction from published data; every p < q composited by proper
divisor or failed strong-PRP (both re-derived, never trusted from
logs); ECPP re-verified by an independent implementation; APR-CL as a
second algorithm; a PARI full scan as a third code path; SHA-256
manifests. Cost: minutes per record. Twice in this repo's history a
check that skipped one of these legs returned a false PASS (the
vacuous scan, the junk certificate) and was caught by the remaining
legs before anything was recorded; no record that passed all legs has
ever been overturned.

## 5. Open problems (ranked by expected digits-per-effort)

1. **Cover optimization beyond GRASP** — exact/hybrid set-cover (CP-SAT
   on the residue-selection LP) targeting k ≈ 0.5·k₀; worth ~5–8 digits
   on T(10⁵) at zero search cost.
2. **Throughput** — wider Montgomery kernels (Game-1 widths) and more
   fleet; each 10× is worth ~+2.3 nats of exponent ≈ 4 digits.
3. **Small-CRT-representative / lattice methods** — never attempted;
   the only known route that could break the "modulus digits are the
   floor" barrier.
4. **The gap to truth** — calibrating the Granville–van de Lune–te
   Riele law against the exhaustive data (g ≤ 9,781 up to 4×10¹⁸ gives
   C ≈ 1.4 in g_max(X) ≈ C·ln²X·ln ln X) puts the true T(10⁵) near
   **10⁵³**; our constructive 150 digits is ~2.9× the logarithm of the
   likely truth. See §6, THE WALL, for how much of that gap is closable.
5. **Game-1 ceiling** — g > 10⁷ needs ~30k-digit moduli and ECPP far
   beyond practice; APR-CL-free certification ideas (Pocklington-
   friendly N−q by construction?) are the only visible door.


## 6. THE WALL — predicted limits, per game

Calibration used throughout: the exhaustive record (g ≤ 9,781 for all
even N ≤ 4×10¹⁸) fixes the constant in the GLvdtR law at C ≈ 1.4
(g_max(X) ≈ C·ln²X·ln ln X); the measured cost identity for our
constructions is p₁·k ≈ 1.32·φ·π(Q)/ln N with cover-quality factor
φ ≈ 0.60 today (GRASP/SA), where ln(compute) = ln C is the affordable
search exponent (≈ 25 for today's fleet, ≈ 35 for a "heroic"
nation-scale scan, ≈ 45 as a generous ceiling for anything classical).
A useful collapse: the modulus budget cancels out of the exponent, so
every threshold game obeys

    digits(N) ≳ 0.57·φ·π(Q) / ln(compute)      (compute-bound wall)
    digits(N) ≳ sqrt(c·π(Q)) / 2.3, c∈[0.8,1.3] (absolute floor)

and at the absolute floor the "construction" has degenerated into
nature's own ensemble scan — which is why the floor and the truth
nearly coincide.

### Game T(100,000) — smallest N with g > 10⁵  (now: 150 digits)

- **Actual maximum (truth)**: T(10⁵) ≈ 10⁵³ (±5 in the exponent from
  the unknown constant and residue-luck tails). Not computable by any
  imaginable exhaustive verification — it would require ~10⁵² scans.
- **Best our current algorithms can do**: ~132 digits with today's
  fleet (ln C ≈ 25); ~95 digits if someone burns absurd compute
  (ln C ≈ 35). Each digit below 150 costs ×1.3–1.5 in scan time — the
  ladder gets exponentially steep but has no cliff until ~130.
- **Best likely-discoverable algorithms**: cover quality is a linear
  divisor of the wall — exact/ILP covers reaching φ ≈ 0.45 give
  ~91 digits at today's compute, ~60–65 digits at ln C ≈ 40. The
  absolute floor for *any* cover-and-scan method is 38–49 digits
  (c ∈ [0.8, 1.32]), essentially the truth (~53 digits). Verdict: the
  truth is approachable in *order of magnitude* but the last factor ~2
  in digits is protected by an e^{100}-scale search — permanently out
  of reach. Prediction: the record stalls in the **90–130 digit** band
  for the foreseeable future.

### Game R(10^200) — largest g with N < 10²⁰⁰  (now: 119,419)

- **Actual maximum (truth)**: R(10²⁰⁰) ≈ C·(460.5)²·ln(460.5) ≈
  **1.8 million** (same ±: order 10⁶, not 10⁵). Unverifiable exactly,
  but this game's truth is *much* closer to reach than T's.
- **Best our current algorithms can do**: the 10²⁰⁰ cap makes the game
  range-bound: π(Q) ≤ ln N·ln C/(1.32·φ). Today: Q ≈ 170,000.
  Heroic compute: Q ≈ 250,000.
- **Best likely-discoverable algorithms**: φ → 0.45 plus ln C ≈ 45
  gives Q ≈ 450,000; fully saturating the range (scan everything below
  10²⁰⁰ coprime to a cover — impossible, e^{450} candidates) would
  reach the truth. Verdict: **~25% of the true maximum** (≈ 400–500k
  of ≈ 1.8M) is the realistic ceiling; the remaining factor ~4 is
  again search-entropy-protected. This is the game where algorithms
  matter most per unit compute. Our 119,419 stands at ~70% of today's
  ~170k ceiling; Campaign B's 135k target consumes most of the
  remaining headroom, after which every gain awaits better covers or
  more compute.

### Game 1 — largest g, N unbounded  (now: 1,157,341)

- **Actual maximum (truth)**: none. g(N) is unbounded (proved
  unconditionally in the 2025 paper via covering systems + Dirichlet).
  This game has no mathematical wall at all.
- **Best our current algorithms can do**: the search is nearly free at
  large N (our hit came at attempt #443); the binding constraint is
  *certifying* N−q. With ECPP practical to ~4,000 digits in days:
  **g ≈ 2.5 million**. That is Campaign C's territory and little more.
- **Best likely-discoverable algorithms**: the wall moves in lockstep
  with primality-proving technology and nothing else. fastECPP-class
  distributed certification (~50,000-digit proofs, months on a
  cluster): g ≈ 5×10⁷. A future certification breakthrough to
  10⁶-digit proofs: g ≈ 1.5×10⁹. A *construction* breakthrough —
  arranging N−q to have Pocklington-friendly form (N−1-style factored
  structure) while satisfying the cover congruences — would blow the
  wall off entirely, since such proofs scale to millions of digits
  today; nobody knows how to intersect the two constraint systems, and
  we flag it as the single most valuable open trick in this problem
  family. Verdict: Game 1's record is an index of certification
  technology, not of number theory: expect it to track the largest
  general-form proven primes at a fixed ratio (g ≈ π-count of ~2·10⁻⁴
  × certifiable digits²... in practice: whatever can be ECPP'd, times
  ~600 in q per 1,000 digits).

### Summary table

| game | truth | current algos, today's compute | current algos, heroic compute | likely-future algorithms | protected by |
|---|---|---|---|---|---|
| T(10⁵) smallest N | ~10⁵³ (53 digits) | ~132 digits | ~95 digits | ~60–90 digits; floor 38–49 | search entropy e^{L} |
| R(10²⁰⁰) largest g | ~1.8M | ~170k | ~250k | ~450k | range entropy under the cap |
| Game 1 largest g | unbounded | ~2.5M | ~5×10⁷ (fastECPP) | ~10⁹+; unbounded via Pocklington-form trick if found | certification cost only |

## 7. One-paragraph takeaway

A large least Goldbach summand is bought with three currencies —
modulus digits, search throughput, and certification compute — trading
at exchange rates that are now measured, not guessed: ~2.5× search per
7 digits, ~1 digit per percent of cover quality, exponent e^{p₁k} for
everything. Full covers were the gold standard and are now obsolete;
partial covers plus brute progression scanning, checkpointed in git and
certified twice by independent code, are the entire present frontier.
The truth (T(10⁵) ≈ 10⁵³) sits a factor ~3 below our records in log
scale, and §6's wall analysis says roughly half of that gap will fall
to compute and cover quality while the last factor ~2 is
entropy-protected forever — a fact worth stating in every future README
so the records stay honest about what they are: upper bounds,
manufactured, and falling toward a floor they will never touch.
