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

## 2. The cost model (validated across 8 certified records)

Let L = ln N, let the cover use moduli set R with residual count k, and
let p₁ ≈ e^γ·ln(max contiguous prime)·(1/L) be the per-residual
probability that a complement is prime. Then:

- **Search exponent**: E[t to success] ≈ e^{p₁k}. This single number
  decided every campaign. Observed hits landed at 0.25×–7× of E
  (n=8; the exponential clock is merciless about variance — plan for 3×).
- **Digit budget split**: ln N = (modulus nats) + (search nats). Search
  nats are nearly free if you have throughput (ln t ≈ 25 for a GPU
  fleet vs ≈ 18 for 4 CPU cores) — this is why the GPU record jumped
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
  validated the e^{p₁k} model (hit at 99.9% of a range sized E[hits]≈4
  — the 7× outlier that taught us to respect variance).
- **193 → 186 → 179-digit ladder**: the digit-walk works; each ~7-digit
  rung cost ~2.5× the previous search — measured, not theorized.
- **2,480-digit g=1,157,341** (Game 1): at huge L the exponent
  collapses (p₁k ≈ 7.7 → hit #443); big-g records are *search-trivial,
  certification-bound*. Beat the 1,113,137 prime-gap benchmark with a
  number 7× shorter than the gap's own endpoints.
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
manifests. Cost: minutes per record. Records that skip any leg have
been wrong twice in this repo's history; records that pass all legs
have never been overturned.

## 5. Open problems (ranked by expected digits-per-effort)

1. **Cover optimization beyond GRASP** — exact/hybrid set-cover (CP-SAT
   on the residue-selection LP) targeting k ≈ 0.5·k₀; worth ~5–8 digits
   on T(10⁵) at zero search cost.
2. **Throughput** — wider Montgomery kernels (Game-1 widths) and more
   fleet; each 10× is worth ~+2.3 nats of exponent ≈ 4 digits.
3. **Small-CRT-representative / lattice methods** — never attempted;
   the only known route that could break the "modulus digits are the
   floor" barrier.
4. **The gap to truth** — heuristically T(10⁵) lives near 10²⁵; our
   constructive 150 digits is ~6× the *logarithm* of the likely truth.
   Closing that is not an engineering problem; it is the
   Granville–van de Lune–te Riele regime, and nothing here touches it.
5. **Game-1 ceiling** — g > 10⁷ needs ~30k-digit moduli and ECPP far
   beyond practice; APR-CL-free certification ideas (Pocklington-
   friendly N−q by construction?) are the only visible door.

## 6. One-paragraph takeaway

A large least Goldbach summand is bought with three currencies —
modulus digits, search throughput, and certification compute — trading
at exchange rates that are now measured, not guessed: ~2.5× search per
7 digits, ~1 digit per percent of cover quality, exponent e^{p₁k} for
everything. Full covers were the gold standard and are now obsolete;
partial covers plus brute progression scanning, checkpointed in git and
certified twice by independent code, are the entire present frontier.
The truth (T(10⁵) ≈ 10²⁵?) remains ~120 digits below anything any of
these methods can reach — a fact worth stating in every future README
so the records stay honest about what they are: upper bounds,
manufactured, and falling.
