# PhD Research Log — Extremal Least Goldbach Summands

Programme: *Extremal Least Goldbach Summands* (4-year proposal, record snapshot 2026-07-22).
Student log, year 3 — project kickoff with delegated subagent execution.

## Record board (updated 2026-07-28 — session close)

| Game | Incumbent | Value | Status |
|---|---|---|---|
| Height H (Game 1) | 2,480-digit N (slop/goldbach/records/g1) | g = 1,157,341 | external session |
| Threshold T(100,000) (Game 2) | **150-digit** N (GPU fleet, records/threshold_150digit_g104527) | g = 104,527 | **re-verified PASS here** (witnesses + independent ECPP, 2026-07-28) |
| Budget R(10^199)/R(10^200) (Game 3) | 199-digit N (r200 round 1) | g = 119,419 | re-verified PASS here |

### 2026-07-29 — WP9 (Door 3) underway: closure theorem + falsification engine
- User directive: work Door 3 first (AlphaEvolve access offered for the
  generative tier). Delivered so far, all in `phd/wp9/`:
  **theorem draft v0.1** (scheme/certificate formalism, three lemmas with
  proof-status marks, schema language L, falsification protocol);
  **tier-0 calibration** — engine reproduces every WP7 hand number exactly
  (m²−c: c=398/113 kills; the 5.8-vs-10.5 nats/residual discrepancy
  reconciled as B=10^100 vs 10^200 context), and surfaced two refinements:
  covering endgame ≈ 1.0 nats/offset at Q=122k (2.5 was context-bound), and
  budget binds at 122k vs boost–kills equilibrium at 200k;
  **exhaustive tier: 13,661 schema instances, 0 passes** (16 first-run
  passes audited away as a baseline-family filter leak — semantics
  hardened); near-miss board topped by ExpFamily at 3.1–4.2 nats/residual
  kill (3× covering endgame, as WP7-P3 predicted);
  **Lemma 2 rigorous draft** (deterministic shared-divisor proposition +
  explicit H1 + the 1.2e9-candidate empirical bound);
  **enumeration wall measured**: quartic-product certificates cost
  height^0.50–0.74 work per certified offset (theory ½) → ~10^100
  ops/offset at B=10^200 — Lemma 1(c)'s first data.
- Later same day: §9–§10 land the mathematics — k_max cluster formula
  closes EVERY shared-variable identity family with v < d (all certify
  ≤13 offsets vs ~18,000 needed; α̂=0.761 measured vs 0.750 predicted);
  within-grammar Lemma 1 now [P] modulo value equidistribution. H2 note
  posting-ready; AlphaEvolve scorer harness ready (blocked on access).
  Remaining math: torus-action ⇒ norm-structure classification (v ≥ d).
- §11 (same day, continued): the classification item DISSOLVED — local
  isolation (all ellipsoid extents < 1 at 10^200) + orbit conservation
  (symmetry preserves value or factor; mixed words miss the window by
  10^190) close the dense frontier outright. Lemma 1 [P at draft rigor]
  on L and beyond; Door 3's mathematical core is COMPLETE at draft
  level. Next: Door 1 gate D1.0/D1.1 (does anything beat 867?).
- Door 1 turn 1 (same day): D1.0 diagnostics — 19/88 moduli tight
  (gap ≤ 1) at the greedy point; random-start ascents land 90–110 primes
  WORSE (greedy's adaptivity ≈ 2.4 nats); backbone overlap 2.4% = chance
  (fully degenerate landscape — no crossover structure). D1.1 gate after
  22 exact-LNS windows (CP-SAT, incumbent-floored): 867 never beaten,
  always matched; optimality proofs did not close within caps — gate
  OPEN, next: per-window LP certificates + provable small windows.

### 2026-07-29 — WP8: strategy reflection (3 crazy / 3 small / 3 professor / path to 200k)
- Full memo: `phd/wp8_beyond_covering.md` (scripts in `phd/wp8/`). Four new
  hard results produced for it: (1) **rung ladder** E(Q) at 199d computed to
  Q=200,000 — E=37.69, e^E=2.4e16 ≈ 950 fleet-years, geometric rung spacing
  makes climbing cost ~4% more than jumping; (2) **packing probe** — c1 is a
  local optimum (ascent+kicks gain 0 at 122k, −0.8 nats at 200k); (3)
  **boost-vs-kills equilibrium** — cover size is set by dE=0, not by the lnB
  budget (adding r=461 nets +0.00 nats), explaining the flat frontier; (4)
  **SoK §7.4 LP certificate executed and VACUOUS** — fractional coverage is
  100.00% at both Q (kill-mass 1.86·π), so the entire game exponent is an
  integrality/rounding gap: naive 15.6% → greedy 7.56% → fractional 0;
  1% absolute ≈ 2.7 nats ≈ 15× compute. Headline recommendations: quantum
  crossover computed and negative (E*≈41–55 ≥ all reachable targets);
  GPU port of skip-frac (O1, ~2–3×); Erdős–Rankin/FGKMT rounding-gap
  programme (P2) as the central open problem; Operation Staircase ladder
  140k→150k→165k→175k→200k with priced closers for the final e^5.5 wall
  (volunteer swarm / ASIC / mathematics).

### 2026-07-29 — CAMPAIGN 3 STOPPED at user request (duplicative with another worker)
- Stopped at **380/17,200 slices (3.98e8 raw candidates, hit-mass λ=0.077,
  survival 0.926)** — a clean in-model early stop; per-slice p̂/Ê/hit% steady
  throughout (p̂≈0.054, Ê≈21.08, hit%≈27.6, ~16.3k k/s). Checkpoint is
  committed; `run_campaign3.py --chunk-seconds 560` resumes losslessly.
  If any session resumes or runs a parallel budget-game campaign, coordinate
  variant/k-space assignment first — independent workers should scan
  DISJOINT variants (they compose losslessly; duplicated k-ranges are pure
  waste). Wakeup chain deleted. Next: strategy reflection memo (wp8).

### 2026-07-28 — CAMPAIGN 3 LAUNCH: budget game, target g > 119,419 under 10^199
- Target switched by user directive: largest g(N) below 200 digits. Cover: the
  ratchet session's unstarted round-2 leftover c1 (Q=122,000, 88 classes,
  M=191d, |U|=867, boost 11.01), independently re-verified here (CRT ✓,
  uncovered ≡ residual ✓); a fresh greedy re-derivation at 199d matched its E
  to 3 decimals — the frontier is flat at this Q, no better cover exists in
  this family. **Any hit gives g(N) ≥ 122,011 > 119,419 with N < 10^199.**
- 40 residue-swap variants (shared M ⇒ shared sieve-inverse cache), kmax
  4.5e8 each under the 199d ceiling ⇒ 1.8e10 raw candidates in the pool.
- **Engine: the 179d winner's selective-testing lesson, adopted exactly.**
  New `--skip-frac f` in search.py tests only the emptiest (1−f) of each
  block in survivor-count order; the sacrificed hit mass is computed exactly
  from the survivor histogram (w = (1−p̂)^a) and logged per-slice as hit%.
  p̂ stays unbiased, so Ê model validation continues to work under skipping.
- Calibration at 199d (131k-k slices): baseline 1,772 k/s (p̂=0.063,
  alive/k=337, Ê=21.24±0.06 — 0.4 nats above theory's 20.83; watching).
  Selected **f=0.92, sieve-B=1e6: 14,957 raw k/s with 29.6% hit mass kept ⇒
  ~3× net discovery rate**. Two mechanisms: test cost per candidate is
  ≈1/p̂ Fermat tests regardless of survivor count (every k dies at its first
  PRP pass), so skipping full k's is nearly pure profit; and once tests stop
  dominating, the per-block sieve-residue cost (∝ π(B)·|U|) makes the small
  sieve win. Measured hit% matched the Gaussian survivor-histogram model
  to ±0.4pp at every f tried.
- Plan: e^21.25 ≈ 1.7e9 equivalent candidates ⇒ expected first hit ≈ 3.5–4.5
  wall-days at ~85% duty. Pool capacity 1.8e10 × 0.296 ⇒ E[hits] ≈ 3.1,
  P(≥1) ≈ 96%; if exhausted hitless, mint more residue-swap variants (free)
  and continue. On hit: stop_on_success, then the standard certification
  pipeline (verify_record.py witnesses + PARI ECPP + independent checker).
- Driver: phd/campaign3/run_campaign3.py — chunked (≤560s/chunk), slices of
  1.048e6 k checkpointed in git-tracked search.log (rollback-safe),
  idempotent resume, lazy round materialization, exit 3 on hit.

### 2026-07-28 — CAMPAIGN 2 STOPPED at user request (session close)
- Stopped at **2,132/2,400 batch-1 slices (5.6e8 elements), 0 hits** — survival
  probability ≈ 0.22 under the validated model; a second consecutive unlucky-but-
  in-model draw. Per-slice statistics matched the blueprint model throughout.
- Master meanwhile certified T(100,000) = 179 digits (g=101,149; ratchet round 3)
  and closed that session with a round-4 164-digit-modulus cover built but unstarted.
- IMPORTANT: campaign 2 is NOT obsoleted by the 179d record — every attainable hit
  is ≤ 175 digits (N ≤ N0 + 1.5e6·M ≈ 1.2e174), which would still beat 179 by 4+
  digits. It is stopped, not falsified. To resume: re-run
  `python3 goldbach/phd/campaign2/run_campaign2.py --chunk-seconds 590` in chunked
  turns — the committed search.log checkpoint makes resumption lossless (268 slices
  remain in batch 1; specs_reserve.json holds 712 more variants).

### 2026-07-28 — post-mortem: evaluation of the winning 179d record (t100k round 3)
- Verified PASS here (standalone verifier). Construction: Q=99,991 cover, 80 classes,
  M=169.4 digits, |U|=728, boost 10.79 — statistically the SAME frontier point as our
  168d blueprint (167.9d, 754 res). The covers are equivalent; the outcome difference
  was search strategy and engineering, not mathematics.
- **Depth vs breadth**: they scanned ONE progression to t=758,850,385 (~7.6e8
  elements; hit after surviving λ≈2.5, P≈8% — unlucky too, but a single deep
  progression has unbounded runway, so bad luck costs digits (N grows only
  logarithmically with t) instead of terminating the campaign. Our 400×1.5e6
  breadth-first design capped every hit at ≤175 digits (better record if hit) but
  hard-exhausted at 6.3e8 elements when the dice ran cold. Ratcheting
  (199→193→186→179, banking a certified record each round) dominates our
  grand-slam-per-campaign design under fixed compute.
- **Selective testing**: their tsearch2 ranks each window's t by surviving-complement
  count and Fermat-tests only the most promising fraction — sacrificing a slice of
  hit density for a multiple of throughput. We adopted the ordering but kept
  exhaustive testing (result-preserving); their result argues the aggressive skip
  is net-positive for time-to-record.
- Left for a future session: round-4 covers (cover_t100k_d ~172d target,
  cover_r200_c1 q>122k) with search positions in their logs; our campaign 2
  checkpoint (≤175d attainable, 268+4272 slices remaining) — the two approaches
  could be merged (their engine, our smaller-N spec set).

### 2026-07-28 — evaluation of the 150-digit GPU record (post-close addendum)
- **Verified PASS here**: verify_record.py re-derives all 9,977 witnesses; ECPP chain
  (17 steps) passes the PARI-independent checker with correct binding. Dual-validated.
- Construction: 68-modulus cover, M=140 digits, k=62,147,038,260 of a full
  [0, 7.5e10) scan at E=24.91 — hit at 63.8% depth, cumulative expectation ≈0.40,
  a central Poisson draw. No luck debt this time; they simply bought enough tickets.
- **The enabler was raw throughput, not mathematics**: CUDA engine (bit-matrix sieve +
  Montgomery CIOS Fermat waves, validated bit-for-bit vs Python) at 2.5–8.5M tests/s
  ≈ 430× our 4-core pipeline. ln(430) ≈ 6.1 — exactly the E-gap (24.9 vs ~19) between
  their reachable rung and ours. The record frontier is log(compute); covers and
  strategy were already saturated at our scale.
- Other adoptable practices: full-range scan then bank the MINIMAL hit (optimal for
  the smallest-N game, vs stop-on-first-hit); git-committed safe_k checkpoints
  surviving ~10 Colab culls (our slice-checkpoint pattern, independently converged);
  bit-for-bit GPU-vs-CPU validation as certification hygiene.
- Standing record board after reconciliation: T(100k)=150d/g=104,527 (GPU session),
  R: g=119,419 @199d (slop session), Height: g=1,157,341 @2,480d.

### 2026-07-28 — RETRACTION + corrected sub-100 analysis (see wp3_small_representative_memo.md v2)
- Literature search done: GSS FOCS'00 Thm 3 obtained and verified; the recalled
  radius sqrt(L·lnB·P) is CORRECT (numerically within 0.4% of the exact finite-ℓ
  optimum). The error was mine elsewhere: v1 compared the decoding radius at
  agreement size s against an existence bound maximised over a DIFFERENT s.
  Coupling them closes the window at every pool size. **"Open window" retracted.**
- Corrected costs: conventional sub-100 optimum is 44 moduli, M=10^79, |U|=1060,
  **E = 44.1 → 1.4e19 candidates ≈ 5e4 GPU-years** (not 3e8 — earlier extrapolation
  was too pessimistic). Sub-100 is expensive, not impossible: ~10^4 A100s for a
  few years, and 120–125 digits is ~10^2 GPU-years (fundable now).
- Oversized covers would make it trivial (420 moduli, |U|=165, **E = 10.2**, ~2.7e4
  candidates) but their small representatives have design-space density e^-2630.
  Finding one = modular subset-sum with choices at **density 1.026** — the hardest
  known regime (lattice attacks need <0.94; Wagner k-tree needs 2^938 here).
- Net: the record now rests on two well-posed open problems (CRT list-recovery
  beyond the Johnson radius; density-1 subset-sum with 2^82 planted solutions),
  and WP7 algebraic mechanisms become the highest-value untested route — they are
  the only family that escapes the ln r-nats-per-offset entropy accounting.

### 2026-07-28 — (superseded by the entry above) FORWARD MEMO: the road to sub-100 digits
Brute-force frontier (validated model, Q≈10^5, dE/dD ≈ −0.10..−0.19/digit):
| D | E | candidates e^E | A100-years @8.5M tests/s |
|---|---|---|---|
| 140 | ~28 | 1.6e12 | 0.01 |
| 130 | ~32 | 1.1e14 | 0.6 |
| 120 | ~38 | 2.7e16 | ~160 |
| 110 | ~44 | 1.8e19 | ~1e5 |
| 100 | ~52 | 4.7e22 | ~3e8 |
Verdict: the covering+scan paradigm ends near D≈125 even for org-scale fleets.
Sub-100 is NOT a compute problem — it needs e^~30 of algorithmic efficiency.

Existence is not the obstacle: conjecturally max g(N) ≈ (ln N)²·ln ln N ≈ 287,000
already at 10^100 (crosses 100,000 near 10^60), so sub-100 deserts exist in
abundance heuristically. The obstacle is purely constructive.

**The breakthrough required: decouple digits(N) from digits(M)** (proposal RQ2/WP3).
Entropy accounting says it is possible in principle: a cover drawing ~150 moduli
from the 668 primes < 5,000 carries ~809 bits of design freedom (subset ~509 +
residue choices ~300), while shrinking a 10^300-mass cover's least representative
into [0,10^100) needs only ~664 bits — a surplus of ~145 bits, i.e. ~2^145 valid
systems are expected to exist with N < 10^100 and residual load E ≈ 19–26
(a trivially searchable e^19–e^26 tail). Sub-100 T(100,000) is therefore an
ALGORITHMIC SEARCH problem: find one member of an exponentially large but
exponentially sparse family — formally, an inhomogeneous modular subset-sum /
CVP-with-choices instance at density ≈ 809/997 ≈ 0.81, uncomfortably close to but
not obviously outside the lattice-reducible regime (low-density subset-sum breaks
< 0.94 for point targets; here the target is a 2^332-wide window, which helps).

Forward programme (in priority order):
1. WP3 theory memo: exact reduction of small-representative-with-choices to
   modular subset-sum; identify which relaxations (fixed subset, ±1 residue swaps
   as shift vectors δ_r) make it a clean lattice problem.
2. E4 falsifiable toy (per proposal gate): Q=1,000, pool primes<300, target a
   representative ≥30 digits below M via BKZ/fplll on the swap-shift lattice.
   Predeclared success metric; negative scaling result is publishable (RQ7).
3. If signal: ladder 10^40 → 10^60 → 10^100 targets; the found system's E≈20
   means the *search* phase runs on CPU — only certification is unchanged.
4. In parallel (cheap wins, log-compute track): merge the GPU engine with
   full-range-minimal-hit ratcheting to grind 150 → ~135 digits; D=130 costs
   only ~0.6 A100-years — reachable by a patient Colab fleet.
5. Fallback (RQ7): if lattice attacks fail at density 0.81, prove a restricted
   no-go (e.g., equivalence to average-case-hard lattice problems) — the
   "conventional model cannot reach sub-100 without solving X" barrier theorem.

### 2026-07-28 — costed menu for follow-up work (validated: model reproduces the
150d record at "6 days on 2 Colab GPUs" — the actual campaign duration)
| rung | E | candidates | A100-yr | spot-$ | 2-GPU-Colab wall |
|---|---|---|---|---|---|
| 140d | 28.1 | 1.6e12 | 0.10 | ~$1k | ~2 months |
| 135d | 29.7 | 7.7e12 | 0.49 | ~$5k | ~10 months |
| 130d | 31.2 | 3.6e13 | 2.3 | ~$24k | — |
| 125d | 32.9 | 1.9e14 | 12 | ~$125k | — |
| 120d | 34.7 | 1.2e15 | 73 | ~$770k | — |
| 100d | 44.1 | 1.4e19 | 8.9e5 | ~$9.4B | — |
(Expected values; ×1.6 for 80% confidence. Throughput engineering shifts all rows.)
Toy CRT decoder: ~zero compute, 2–4 sessions; measures practical-vs-Johnson gap.
WP7 probes: ~zero compute, ~5 bounded probes × 1–2 sessions; only unbounded-upside route.

### 2026-07-28 — master reconciliation: FRONTIER.md + SoK §7 (PRs #27/#28)
- Merged parallel sessions' work. FRONTIER.md independently measures the sub-100
  wall: realizable E = 43.66 vs our 44.1 (agreement to 0.4 nats — two independent
  implementations of the costing now concur), and its set-valued-conditioning study
  (gain saturates at H^0.35, worth 1–2.8 nats) plus enumerability theorem ("classic
  cover = unique freely-enumerable design") confirm our density-1.026 subset-sum
  barrier from the constructive side.
- CORRECTION to our memo: sub-100 cost is ~9×10^5 GPU-years, not 5×10^4 — a units
  slip (divided by test rate instead of candidate rate). Costed-menu table row was
  already correct ($9.4B at D=100); memo prose fixed. FRONTIER's fleet band also
  supersedes our Colab wall-clock estimates (140d ≈ 13 days, not ~2 months).
- SoK §7 lists 10 open angles; #2 (prime-first construction), #9 (NP-hardness of
  the existence problem) and #10 (Grover: sub-100 at ~e^22 quantum queries) are
  genuinely complementary to our WP3/WP7 program and noted in the memo.

### 2026-07-28 — toy CRT decoder + WP7 probes both executed (post-merge follow-ups)
- **Toy CRT decoder (delegated; goldbach/phd/toy_crt/)**: Howgrave-Graham/GSS lattice
  decoder implemented (FLINT LLL, cross-validated pure-Python fallback), 61-position
  pool, B=10^12, A_J=87.38, 390 decodes. Verdict: practical LLL does NOT penetrate
  below the Johnson radius — the empirical threshold is A ≈ 1.028·A_J at ℓ=30,
  approaching A_J from above like 1+c/ℓ (ℓ=45 post-hoc: cutoff ≈1.02, one failure at
  1.0041·A_J). Below threshold the failure is TOTAL: reduced bases yield zero integer
  roots, and across all 390 decodes no non-planted solution was ever found despite
  ~10^7 valid alternatives existing at ρ=0.7 — solution abundance buys nothing.
  Empirics track finite-dimension determinant bounds to ~1%: the radius is tight in
  practice for this family, closing the last "maybe practical reduction beats the
  proof" hope from the WP3 memo.
- **WP7 probes (wp7_probes.md)**: all five terminated at predeclared gates — P1
  prime-powers strictly dominated (zero new kills); P2 value-set identities 26×
  dominated on average, 2–3× at the margin, with a provable Q^(1/2) offset ceiling;
  P3 exponent families reduce to covering (search-throughput note kept); P4 norm
  forms are covering in Galois clothing; P5 hidden bias empirically ≤0.1 nats from
  1.2e9 banked candidates. Output: 3 simultaneous conditions any real mechanism must
  meet (≫√Q offsets, o(ln r) entropy each, invisible to bulk density stats).
- **Programme position, final**: sub-100 T(100,000) has exactly one live route
  (Regime-I brute force, ~5×10^4 GPU-years) and three precisely-stated mathematical
  problems that would change that. RQ7 chapter complete; 140d rung (~$1k) remains
  the cheap constructive next step.

## Programme close-out summary (2026-07-22 → 2026-07-28)
- **O1 achieved**: both kickoff incumbents independently audited PASS (dual-
  implementation ECPP validation, adversarial mutation tests); two later external
  records re-verified with the standalone verifier.
- **O2 achieved**: density model E = |U|·boost/ln N validated to ~0.1 across
  3 covers and ~1.2e9 scanned progression elements — the model is exact; both
  campaign misses were 0.22-0.30-probability draws, not model error.
- **O3/WP2 progress**: cover frontier mapped at two Q values; AlphaEvolve move-set
  audited, reward-hacking failure diagnosed (unconstrained −D fitness), E-capped
  variant built and benchmarked (blueprint within ~1 digit of frontier at E≈20);
  PR #20 blueprint audited (valid cover, inflated claims, unusable shipped kmax)
  and re-parameterized into a viable campaign.
- **O4**: no new certified record from this session's own campaigns (two honest
  negative results, fully logged); parallel sessions ratcheted all three games.
- **O6 achieved**: restart-safe chunked-compute methodology (slice checkpoints in
  git, idempotent resume, ~85% duty cycle through ~15 container restarts/rollbacks),
  sieve-inverse cache + survivor-ordered testing adopted and verified
  result-preserving; all artifacts, logs, and decisions committed to this branch.

### 2026-07-28 — compute turns (campaign 2, final stretch before stop)

Superseded (this project's kickoff incumbents, all audited PASS 2026-07-22):
height 1,134,871 @ 2,692d; dual N₁₉₇ (197d, g=107,719).

Grand-slam target: N < N₁₉₇ **and** g(N) ≥ 1,134,877 — aspirational (O5);
RESULTS.md notes covering methods leave ≥20,000 residuals under a ≤192-digit
modulus (success density e^−400), so O5 requires mechanisms beyond static covers (WP7).

## Programme status

| WP | Scope | Status |
|---|---|---|
| WP1 (E1) | Independent audit of both incumbents + adversarial mutation tests | **done — PASS** |
| WP2/WP6 (E2/E8) | Cover frontier Q=107,720; density calibration on this box | **done** — see below |
| WP8 (E10) | Incremental record campaign: g > 107,719 with N < 10^199 AND N < N₁₉₇ | **launched** |
| Certification | PARI/GP 2.15.4 installed for ECPP; ecpp_check.py as independent verifier | ready |

## Log

### 2026-07-22 — kickoff
- Surveyed inherited machinery (PR #15/#16): cover.py, anneal.py, gen_variants.py,
  search.py, verify_record.py, mega_verify.py, ecpp_check.py, package_record.py; both
  record artifact directories present.
- Environment: 4 cores, Python 3.11.15, gmpy2 2.3.1, numpy 2.4.6, sympy 1.14.0,
  PARI/GP 2.15.4 (installed today; prior campaign certificates were produced with gp).
- Delegated WP1 audit and WP2/WP6 frontier+calibration to two parallel subagents.
- Campaign design decision: one E10 campaign with Q = 107,720 (covers every prime
  ≤ 107,719) so that ANY hit strictly beats R(10^199) = 107,719; hits are ranked by N so
  a sub-N₁₉₇ hit would also take T(100,000).

### 2026-07-22 — WP1 interim
- Part A (dual 197-digit record): PASS — byte-identical N reconstruction, all bounds,
  evidence regeneration matches committed witness counts, ECPP binding verified.
- Part C (adversarial audit): PASS — all three deliberate corruptions detected.
- Part B (megagap 88,239-witness replay + 3 ECPP chains) still running.

### 2026-07-22 — WP1 final verdict: PASS (O1 achieved)
Delegated audit report (full text in agent log; scripts in scratchpad wp1/):
- **Dual 197-digit record** — N reconstructed byte-identical from (N0, M, k=951,928);
  parity/size/bound checks pass; verify_record.py re-derives all 10,250 witnesses from
  scratch and they are IDENTICAL to committed evidence.json (parity 1, congruence 9,471,
  trial 378, strong-MR 400; offsets = π(107,718) confirmed independently); g prime,
  N−g BPSW-prime; ECPP chain (26 steps) validated by the PARI-independent
  ecpp_check.py incl. binding cert[0][0] = N−g.
- **Megagap 2,692-digit record** — MANIFEST.sha256 matches all 7 artifacts;
  verify_megagap.py end-to-end on a copy: all 813 cover congruences hold, all 88,239
  prime offsets < g re-proven non-summands (85,476 congruence + 895 trial + 1,867
  strong base-2 + parity), regenerated manifest byte-identical; local gap 8,970
  fully certified; all three ECPP chains (253/267/246 steps) validated by
  ecpp_check.py with correct bindings.
- **Adversarial audit** — digit flip in N, deleted offset witness, and swapped
  certificate candidate were each loudly DETECTED (plus a colluding-expected-value
  variant also detected via chain arithmetic).
- **PARI second opinion (lead)** — after installing PARI/GP 2.15.4,
  `primecertisvalid` = 1 for all four certificates: dual complement, megagap
  complement, and both local-gap endpoints. Every ECPP certificate in the corpus is
  now validated by two independent implementations.
- One environmental note: the audit agent's Part B originally ran without PARI
  present; its ecpp_check.py validation is a superset of the missing step, and the
  lead's PARI cross-check above closes the second-implementation gap.

### 2026-07-22 — WP2/WP6 results (delegated agent)
Cover frontier at Q = 107,720 (cover.py):

| e_target | congr | digits(M) | U | E | est digits(N) | k-cap N<N₁₉₇ |
|---|---|---|---|---|---|---|
| 17.0 | 92 | 202.6 | 746 | 17.00 | 210.0 | — (M too big) |
| 17.5 | 91 | 198.4 | 750 | 17.50 | 206.0 | 0 |
| 18.0 | 89 | 194.3 | 764 | 18.00 | 202.1 | 3.8e2 |
| 18.5 | 88 | 190.6 | 770 | 18.50 | 198.6 | **1.69e6** |

- Annealing (2 seeds, ~13 min each) gave zero improvement over greedy at e_cap 18.5 —
  the greedy cover is a robust local optimum of log M + E.
- **Chosen base spec `phd_q107720_e185`**: 88 congruences (moduli 3–643), M = 190.61
  digits, |U| = 770, boost 10.99, E = 18.50. With kmax = 1.5e6 < 1.69e6 (the N₁₉₇
  k-cap), *every* hit beats both bounded games simultaneously.
- 200 variants (gen_variants.py), E ∈ [18.500, 18.546], |U| ∈ [770, 772];
  total budget 3e8 progression elements.
- Calibration (E8): 2118 k/s on 4 procs (3.8× scaling), ~17 Fermat tests/k,
  measured Ê = 18.79 vs model 18.85 → model confirmed to ~0.1 in E. Two artifacts
  documented: kmax must be a block multiple for meaningful Ê printouts, and
  sub-block kmax collapses to one worker.
- Forecast at E_eff = 18.71: e^E ≈ 1.33e8 elements → ~17.5 h expected to first hit;
  P(hit ≤ 12h) ≈ 0.50, P(≤ 24h) ≈ 0.75, P(full 39h budget) ≈ 0.90.
  Expected hit near k ≈ 6.7e5 → N ≈ 2.8e196 < N₁₉₇ (dual-game record).

### 2026-07-22 — E10 campaign launched
- `search.py phd/campaign/specs_variants.json --procs 4 --out phd/campaign/found.jsonl`
  running in background; successes append to found.jsonl and are re-verified
  exhaustively (BPSW over all primes < Q) by verify_success before being reported.
- Monitoring via hourly check-ins; on first hit: stop, certify (evidence + PARI ECPP +
  independent ecpp_check.py + manifest), package record, push.

### 2026-07-22 — check-in #1 (10:22 UTC): infrastructure hardening after two container restarts
- Finding (operational, WP1-adjacent): the remote container is reclaimed during idle
  periods between session turns, killing detached (`nohup`/`setsid`) processes. Two
  restarts (~09:47, ~10:21 UTC) each wiped in-flight scanning with zero completed-spec
  checkpoints — coarse per-variant checkpointing (12 min/unit) loses too much.
- Fix, campaign driver v2: the 200×1.5e6-k budget is now cut into 1,200 interleaved
  slices of 262,144 k (~2 min each), checkpointed per slice in search.log and resumed
  idempotently; the search runs as a harness-tracked background task instead of a
  detached process, with a log monitor armed for hit/crash signatures.
- Bonus: interleaving slices round-robin across variants makes the global scan
  breadth-first in k, so the first hit found also tends to minimise k — and hence
  N ≈ k·M — which is exactly the threshold-game (smallest N) preference.
- Progress at check-in: 0 hits, 0 completed slices survive the restarts; effective
  campaign clock restarted 10:24 UTC. Forecast unchanged (~17.5 h expected to hit,
  subject to duty-cycle losses from restarts).

### 2026-07-22 — check-in #2 (11:25–12:30 UTC): driver v3, chunked foreground compute
- Harness-tracked background tasks ALSO die on idle reclaim (measured duty cycle ~12%
  in the 10:24–11:24 window: 3 slices/54 min). Driver v3 therefore runs the search as
  timeboxed foreground chunks inside scheduled session turns: ~9.7 min per chunk,
  whole slices only, exit code 3 signals a hit for immediate certification.
- This check-in turn ran 6 chunks: 26/1200 slices complete (rounds 0 of variants
  v0–v25), 0 hits, throughput steady at ~1950 k/s, Ê ≈ 18.8 nominal.
- Cadence going forward: wakeup turns of ~6–8 chunks (~1 h compute) chained ~1 min
  apart; expected first hit around slice ~510 (Poisson, e^18.7 elements).

### 2026-07-22 — compute turns #3–#4 (12:25–14:55 UTC)
- 88/1200 slices complete (2.3e7 progression elements), 0 hits; throughput steady
  ~1870 k/s per slice incl. init overhead; chunks reliably complete 4 slices each.
  Survival to this depth has Poisson probability e^(-88/510) ≈ 0.84 — unremarkable.

### 2026-07-23 — 28-hour suspension and restart (21:30 UTC)
- The session was suspended mid-compute-turn on 2026-07-22 ~17:20 UTC (user
  interruption followed by session idle) and resumed 2026-07-23 21:28 UTC. No compute
  advanced during the gap; checkpoint state (142/1200 slices, 0 hits) survived intact
  and the chain resumed losslessly — validation of the slice-checkpoint design.
- Wakeup chain re-armed; compute turns continue at ~32 slices/turn.
- Turn #7 (21:30–22:55 UTC): 178/1200 slices (4.7e7 elements), 0 hits; slices running
  slightly faster post-restart (~530 s/chunk). Survival probability ≈ 0.70 — on-model.

### 2026-07-24 — compute turns #8–#9 (23:00–01:30 UTC)
- 242/1200 slices (6.3e7 elements, 20.2% of budget), 0 hits; survival ≈ 0.62.
  Round 0 of all 200 variants nearly complete (k < 262,144 across the ensemble);
  first hit still expected near slice ~510. Two worker restarts absorbed losslessly.

### 2026-07-24 — compute turns #10–#12 (01:32–05:25 UTC)
- 338/1200 slices (8.9e7 elements, 28.2% of budget), 0 hits; survival ≈ 0.52.
  Steady state: 32 slices/turn, ~555 s/chunk, no restarts lost work.

### 2026-07-24 — compute turns #13–#15 (05:26–09:15 UTC)
- 434/1200 slices (1.14e8 elements, 36.2% of budget), 0 hits; survival ≈ 0.43.
  Passed the model median (~slice 354 for 50%); Ê per-slice remains 18.7–18.9,
  so the deficit is ordinary Poisson variance, not model error. Worker restarts
  continue to be absorbed at zero slice loss.

### 2026-07-26 — constrained_100 benchmarked (warm-start = 168d blueprint, 6-iter schedule)
- cap E≤17.5 (as shipped): D=193.2 (85 congr, M=185.6d, |U|=723) — its own frontier
  point does NOT beat the 186-digit incumbent; the E↔D trade is steeper than the
  harness authors assumed.
- cap E≤20.0 (edited): D=179.6 — WORSE than both the blueprint (176.5) and our
  greedy-proposal anneal (175.6) at equal wall-time. The random single-move
  Metropolis walk degrades the warm start at high temperature and cannot recover;
  deterministic best-residue proposals with Boltzmann selection dominate it here.
- Conclusion: harness design is exemplary (constraint in fitness AND internal
  objective, warm start, multi-metric); the evolved *search engine* is not
  competitive with our current optimizer under warm-start conditions. No adoption
  beyond the harness pattern.

### 2026-07-26 — AlphaEvolve deep-dive part 2 (uploaded programs review)
- `evolved_program_constrained_100`: well-posed harness — warm-start cover,
  Lagrangian E≤17.5 penalty in BOTH fitness and the block's internal objective,
  secondary metrics (E, |U|, m_digits); Metropolis engine with 100k single-moves.
  Targets a cheaper/weaker frontier point (E 17.5 → expected hit ~184–185d) than
  campaign 2 (E≈19.9 → ~176.5d); noted its deeper engine for the post-hit ratchet.
- `evolved_program_super_hard_100`: reward-hacked unconstrained fitness (the
  D≈50.7 collapse lineage), but transferable engineering: Gumbel weighted move
  sampling (add small moduli ∝ r^-0.8, drop large), REPLACE move with shared
  background counts, constant-folded 4/ln²10. Anti-lesson: mod_cache keyed by
  id(targets) is a stale-cache bug pattern; our caches key by value.
- Campaign 2: 269/2,400 slices (7.1e7 elements), 0 hits; survivor-ordered testing
  active since slice ~29.

### 2026-07-25 — AlphaEvolve cover-optimizer analysis (WP2 cross-pollination)
- Reviewed evolved_program.py and evolved_program_1.py (branch
  goldbach-alphaevolve-analysis-*): SA over ADD/DROP/SWAP moves with Boltzmann
  acceptance, minimizing self-consistent D. The shipped evaluate() harness confirms
  the fitness was unconstrained −D from an empty cover — with no E cap the block
  collapses to infeasible covers (D=50.7 at E=111 observed here). With an E≤20
  penalty added, it improves the 168d blueprint by 0.9 digits (D 176.5→175.6 at
  E=20.0): the blueprint is near-locally-optimal at this E budget.
- Adopted: move-set + penalized objective as campaign2/evolved_cover_step.py
  experiment; improved cover saved (evolved_best_cover.json) for a post-hit ratchet.
  Evolved hyperparameters noted for that round: temp schedule 0.8→0.02 geometric,
  candidate moduli to 8,000.
- Campaign 2 progress: 124/2,400 slices (3.3e7 elements), 0 hits — early days
  (expected hit ≈ slice 1,700).

### 2026-07-25 — CAMPAIGN 1 RETIRED, CAMPAIGN 2 LAUNCHED (~18:30 UTC)
- Master merge brought records from parallel sessions (PRs #18/#21): height
  g=1,157,341 @ 2,480d; **T(100,000) = 186 digits (g=109,357)**; **R = 119,419 @ 199d**
  plus a stdlib-only standalone verifier. Both bounded-game incumbents re-verified
  here (verifier PASS on t100k_r2 and r200_r1; SHA warning is the self-referential
  SHA256SUMS line only).
- Campaign 1 (g>107,719, N<N₁₉₇) thereby became strictly obsolete at 1,213/2,400
  slices, 0 hits (a P≈0.30 outcome). Retired. Scientific value kept: 3.18e8 elements
  of density-model validation (Ê−E within 0.1 throughout) and the restart-safe
  chunked-compute methodology.
- PR #20 (Jules) audit: 168-digit blueprint (Q=100,003, 79 congr, M=167.9d, 754
  residuals) is mathematically VALID (CRT + cover completeness verified here), but
  its claims were inflated: honest self-consistent E=19.84 (not 20.85), expected-hit
  N ≈ 176.5 digits (not 168), and its 1,111 shipped variants had ceiling_digits=170
  ⇒ only ~120 candidates/variant (~1.3e5 total vs ~4e8 needed) — unusable as shipped.
- **Campaign 2** (user-approved adoption of PR #20 code): variants re-parameterized
  to kmax=1.5e6, ceiling 185 (strictly below the 186d incumbent). Any hit ⇒ new
  T(100,000) record. search.py sieve-inverse cache adopted + driver batches 4 slices
  per process: measured **~2,900 k/s** (+47% vs campaign 1), Ê ≈ 20.2 at k≈0 (drifts
  down with log N; effective E ≈ 19.9). Batch 1 = 400 specs (2,400 slices, capacity
  6.3e8 elements, λ≈1.5); 712 variants in reserve. Expected ~1,700 slices ≈ 2.5 days
  of chunked compute to first hit.

### 2026-07-25 — original budget EXHAUSTED, extension launched (~16:45 UTC)
- Turns #31–#39 completed the original 1,200-slice budget: **3.15e8 progression
  elements scanned across 200 variants (all k < 1.5e6), zero successes.**
- Negative-result assessment: at Ê ≈ 18.7 the expected hit count for the full budget
  was λ ≈ 2.2, so P(no hit) ≈ 0.11 — an unlucky but statistically ordinary draw.
  Per-slice p̂ (0.0588–0.0592) and alive/k (318–319) matched the calibrated model
  throughout; no evidence of implementation error or model bias. This is exactly the
  E8-validated regime: the density model is confirmed, the dice were cold.
- Contingency executed: 200 additional residue-swap variants generated from the same
  base cover (deduplicated against the first 200 by cover; E ∈ [18.546, 18.661]),
  committed as specs_variants2.json; driver now reads both spec files (2,400-slice
  extended budget). Every hit still beats both bounded games (kmax unchanged).
- Forecast for the extension: λ ≈ 2.0 → P(hit) ≈ 0.86; expected ~12 further compute
  turns to first hit.

### 2026-07-25 — compute turns #28–#30 (01:14–04:45 UTC)
- 909/1200 slices (2.38e8 elements, 76% of budget), 0 hits; survival ≈ 0.17 — an
  unlucky but unexceptional draw (a 1-in-6 outcome). Per-slice p̂ and alive/k remain
  exactly on-model, ruling out an implementation regression. Contingency (200 extra
  residue-swap variants preserving the dual-game property) locked in for rc=2.

### 2026-07-25 — compute turns #25–#27 (20:58–01:10 UTC)
- 815/1200 slices (2.14e8 elements, 68% of budget), 0 hits; survival ≈ 0.21.
  Deeper than any depth the July campaign reached (1.4e8). Contingency planning
  for possible budget exhaustion: extend the same 200 variants to kmax ≈ 2.4e8/M-cap
  under ceiling 199 digits (keeps the R(10^199) game live; drops the automatic
  sub-N₁₉₇ guarantee), OR regenerate more residue-swap variants at kmax 1.5e6 to
  retain the dual-game property. Decision due at rc=2.

### 2026-07-24 — compute turns #22–#24 (17:07–20:55 UTC)
- 719/1200 slices (1.88e8 elements, 60% of budget), 0 hits; survival ≈ 0.24.
  All variants now past k = 786,432 (round 3); remaining budget is rounds 4–5.

### 2026-07-24 — compute turns #19–#21 (13:10–16:55 UTC)
- 626/1200 slices (1.64e8 elements, 52% of budget), 0 hits; survival ≈ 0.29.
  Steady 32 slices/turn; a worker restart mid-turn-21 cost only the in-flight slice.

### 2026-07-24 — compute turns #16–#18 (09:19–13:10 UTC)
- 529/1200 slices (1.39e8 elements, 44% of budget), 0 hits; survival ≈ 0.35.
  Now past the naive expected-hit depth (1.33e8 elements). By the memoryless
  property the expected additional wait is still ~510 slices of compute; the
  full-budget hit probability from here is 1−e^−1.32 ≈ 0.73. Decision standing:
  run the full 1,200-slice budget before any redesign (per §11.4 stopping rules).
