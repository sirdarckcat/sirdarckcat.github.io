# The sub-100-digit ledger: 50 ideas toward T(100,000) < 10^100

Ground truth measured first (`exp1m.py frontier --Q 100003`, greedy
digit-capped covers, E at ln N = D·ln 10):

| D | moduli | |U| | E | candidates e^E |
|---|---|---|---|---|
| 100 | 52 | 973 | 41.3 | 10^17.9 |
| 120 | 60 | 899 | 32.8 | 10^14.2 |
| 130 | 64 | 862 | 29.5 | 10^12.8 |
| 140 | 68 | 830 | 26.8 | 10^11.6 |
| 150 | 72 | 802 | 24.4 | 10^10.6 |
| 160 | 76 | 773 | 22.3 | 10^9.7 |
| 170 | 79 | 754 | 20.6 | 10^8.9 |
| 195 | 89 | 692 | 16.8 | 10^7.3 |

Existence is NOT the obstacle: at 100 digits the random-N heuristic
gives 10^100·e^-108 ≈ **10^53 qualifying integers** — the true
T(100,000) likely sits near 65–70 digits. The obstacle is search:
e^41.3 candidates ≈ 9,000 GPU-years at 3·10^6 k/s. GPU-feasible now:
147 digits ≈ 7 h (one T4), 133 ≈ 5 T4-days, 120 ≈ 10 A100-months.
The gap from 120 → 100 digits is ~9 nats = the prize the crazy ideas
must chase. Every idea below carries its small-number test status.

## A. Ten obvious small optimizations (of our current stack)

- **A1. GPU Montgomery-Fermat kernel** — batched 500-bit-class modexp,
  one thread/candidate, 32-bit limbs, CuPy RawKernel. Expect
  10^6–10^7 tests/s vs CPU's 3.1·10^4. THE enabler. Test: exact
  agreement with gmpy2 on 10^5 random cases, then throughput curve.
- **A2. GPU sieve** — per-(residual, k) bitmask is embarrassingly
  parallel; must move with A1 or it becomes the bottleneck (CPU sieve
  feeds only ~5k k/s/core). Test: bit-identical alive masks vs CPU.
- **A3. Sieve-depth re-sweep on GPU** — optimal B shifts when tests
  get 100× cheaper relative to sieving. Rerun the F5 sweep on-device.
- **A4. Zero-penalty variant catalogs (F4, measured)** — 26 singles /
  325 pairs / ~2,600 triples at exactly base |U|; mandatory at low D
  where per-variant k-room shrinks (k ≤ 10^4-10^5).
- **A5. Global ascending-a testing (F2, measured 1.8× conditional)** —
  trivial on GPU: sort the whole catalog's k by survivor count.
- **A6. Montgomery-constant amortization** — per-residual R², n', M
  mod n precomputation reused across k; pure kernel engineering.
- **A7. Product-tree batch trial division** (Bernstein) — replace the
  first Fermat rounds with batched gcd against deep prime products;
  2–3× fewer modexps. Test on CPU first at toy scale.
- **A8. Catalog-level init amortization** — shared sieve arrays across
  same-M specs (F5 leftover), ~free.
- **A9. Pair/triple-swap annealing + parallel tempering (F3 open)** —
  the greedy covers above are un-annealed; the 195-row annealed
  equivalent gained ~2% of |U|. Worth ~0.3-0.5 nats at low D.
- **A10. k-room-aware cover sizing** — at D digits the modulus must
  stop at ~D−6 digits for k-room; re-run the frontier with M = D−6
  and let the annealer trade last-modulus vs variant count optimally.

## B. Ten things other mathematicians would reach for

- **B1. Primorial shift N = q0 + k·P#** (the classic). TESTED and
  dead: at a 161-digit modulus it leaves |U| = 1,468 (best q0 = 11)
  vs greedy's ~770 — costs ~+8 nats. Covering wins because it picks
  the best class per prime instead of one global shift.
- **B2. Erdős–Rankin layered covers** (smooth-kill middle layer, large
  primes pick off survivors — the prime-gap-record construction).
  Test: does the layered heuristic beat greedy set-cover on
  prime-only targets at equal digit budget? (Suspect no — greedy
  already discovers the layer structure — but cheap to check.)
- **B3. Exact residue assignment via CP-SAT/ILP** at fixed modulus set
  — the proper F3 tool; bounds the annealer's optimality gap. Test at
  Q = 10^4 where exact is feasible.
- **B4. Maier-matrix positioning** — choosing N's class mod a
  primorial to sit in a low-density row IS residue choice; already
  subsumed by the cover. No extra freedom. (Understood, not dismissed:
  measured Ê matches the model to 2%, leaving no room for hidden bias.)
- **B5. Chebyshev-bias exploitation** — prime races give O(x^-1/2 log)
  density bias in APs: ~10^-70 at our sizes. Quantified, negligible.
- **B6. Admissible-tuple obstructions** — designing {N−q} to contain
  an inadmissible constellation = covering congruences again (any
  inadmissibility is a mod-p obstruction). Equivalent, not new.
- **B7. Selberg-weighted residual selection** — leave uncovered the
  targets cheapest to kill by sieve luck; at fixed N-size all
  residual complements are exchangeable, so the freedom is only in
  |U|. Subsumed.
- **B8. Variance-aware objective** — minimize −ln E[(1−p)^a] (the
  exact density) instead of |U|: rewards covers whose residual sieve
  positions correlate (fat low-a tail). We measured the lognormal
  bonus exists (σ_a ≈ 13-14, worth e^{p²σ²/2} ≈ 0.3 nats for free);
  can cover design fatten it? Test: σ_a across random equal-|U|
  assignments at toy scale.
- **B9. Distributed work units** (the Oliveira e Silva model) — the
  catalog is embarrassingly parallel; BOINC-shaped if we ever go to
  a fleet. Engineering, ready when needed.
- **B10. Proof-side batching** — ECPP certificates for records via
  parallel Primo/PARI; irrelevant to search cost, required for polish.

## C. Ten crazy ideas

- **C1. BKZ/CVP residue assignment** — "pick classes to make x small
  AND coverage high" is an inhomogeneous CVP in the CRT lattice;
  lattice reduction could beat the 2-list MITM entropy bound that
  capped the joint-optimization work at ~25 digits of cancellation.
  Test: compare BKZ-20 vs MITM on a 30-modulus toy.
- **C2. SMT/Z3 block repair** — exact bounded-width encoding of
  "x < 10^D ∧ coverage ≥ c"; use as a block polisher, not a global
  solver (from the July analysis). Test on 16-modulus blocks.
- **C3. Remainder-tree mega-sieve** — batch-smoothness (product trees
  over 10^9 complements) pushes effective sieve depth to 10^10+ where
  per-prime sieving can't go; cuts Fermat load 2-3× (density
  invariant — pure throughput). CPU prototype first.
- **C4. Grover** — e^41.3 → e^20.7 oracle calls quadratically; needs
  ~10^3 logical qubits running 700-bit modexp oracles. Honest date:
  2040s. Parked with numbers.
- **C5. Learned k-prioritization** — train on (sieve-pattern → hit)
  from toy scans: is there signal beyond the survivor count a_k?
  If residual kill-position correlations matter (see C8), a model
  finds them. Test: AUC vs a_k-only baseline on the Q=6000 toy where
  hits are plentiful.
- **C6. FFT-shared catalog sieve** — the union-of-APs structure across
  thousands of same-M variants admits one convolution-style pass
  instead of per-variant sieves; near-zero marginal sieve per variant.
- **C7. Incremental/shared modexp across k** — dead on arrival: the
  modulus N−q changes with k, so no chain sharing survives; recorded
  so nobody re-derives it.
- **C8. Anti-cover design (variance maximization)** — choose residues
  so residual kill-positions ALIGN, concentrating alive-mass into a
  fat low-a tail that A5 then exploits; the exact-density objective
  B8 taken to its adversarial extreme. Small-scale testable now.
- **C9. Additive meet-in-the-middle on N** — split-and-recombine
  compositeness constraints; dead (compositeness is not additive over
  N = A+B), recorded with reasoning.
- **C10. TPU big-int via MXU matmuls** — 700-bit modmul as int8/int32
  matrix products on v5e/v6e systolic arrays; research-grade, but
  Colab gives TPUs away and nobody has pointed one at a Goldbach
  desert. Feasibility spike: one modmul kernel, measured against T4.

## D. Ten scale-and-infrastructure ideas

- **S1. `colab run` fleet** — N concurrent sessions, each a shard of
  the catalog; the CLI supports named sessions. Session-count limits
  set the fan-out; measure the cap empirically.
- **S2. A100/H100 tier** — 4-8× T4 on this workload class; reserve for
  the record runs, develop on T4.
- **S3. Checkpointed shards** — work units = (spec range, k range)
  with resumable JSON state; survives Colab preemption (we already
  survived five container kills this week — same discipline).
- **S4. On-VM auto-verification** — hits re-verified with sympy/gmpy2
  on the VM before returning, so a lost session can't lose a record.
- **S5. Local+remote hybrid** — CPU box does covers/annealing/variant
  generation (cheap, latency-tolerant); GPUs only scan. Already the
  architecture; formalize the spec-shipping interface.
- **S6. Throughput telemetry** — per-kernel counters (sieve occupancy,
  tests/k, Ê) streamed back; the E-model must keep validating at
  every scale jump, as it did at five scales so far.
- **S7. Autotuned launch configs** — block sizes, limb counts, batch
  shapes per GPU model; one-off sweep cached per accelerator.
- **S8. Mixed CPU-GPU pipelining** — sieve on GPU stream 1, Fermat on
  stream 2, verification on host threads; hide all transfer latency.
- **S9. Colab 24h-session cron rotation** — sessions expire; a
  send_later-driven rotation keeps a standing fleet alive unattended.
- **S10. Budget accounting** — compute-unit burn per nat of E, so
  digit targets are priced before launch (T4 ≈ free-tier friendly;
  A100 burns ~8× faster).

## E. Ten combinations that deliver the run

- **E1. Kernel MVP** = A1+A2+A6: validated GPU scanner, target ≥10^6
  k/s on T4. Gate: reproduce the 26-digit and 62-digit toy deserts
  bit-for-bit, then reproduce the 195-digit record's measured Ê=17.4.
- **E2. Full engine** = E1+A3+A5+A7+A8+S8: target 3·10^6 k/s.
- **E3. Smart catalogs** = A4+A9+A10+B3+B8: k-room-aware annealed
  covers with zero-penalty variants and exact-density objective;
  worth ~1 nat ≈ half a digit at low D.
- **E4. First strike: 168 digits** (E ≈ 21): minutes on T4 once E2
  works — the validation record.
- **E5. Milestone: 150 digits** (E ≈ 24.4+k-room ≈ 25.5): ~7-20 h
  on one T4 — a 45-digit leap over our own 3-day-old record.
  **WON (2026-07-26)**: records/threshold_150digit_g104527 —
  N ≈ 8.27·10^149, g = 104 527. True E at 150d was 24.91; the hit
  landed at k = 6.21·10^10, 63.8% into the [0, 7.5·10^10) round
  (cumulative expectation 0.40), on the A100 shard of the two-session
  fleet after ~26 wall-clock hours of supervised rotation (~10 session
  culls, zero coverage loss via git-committed safe_k marks). The T4/
  A100 split ran at 185k/604k k/s = 2.5M/8.5M tests/s. Next rung: E6
  at 140 digits (E ≈ 28, ~22× this round's search — needs either
  patience or the E3 cover nats).
- **E6. Flagship: 140 digits** (E ≈ 26.8+1 ≈ 28): ~2 days A100 or
  ~1 week T4, P(hit) per pass ~0.6.
- **E7. Stretch: 130 digits** (E ≈ 30.5): ~3-4 weeks single-A100 or
  S1 fleet × days. Decision point on compute-unit budget.
- **E8. Moonshot line: 120 digits** (E ≈ 33.8): needs the fleet plus
  C6/C3 throughput ideas plus E3 nats — plausible ceiling of this
  program on Colab.
- **E9. The 100-digit ledger entry**: e^41.3 at 10^7 k/s = ~900
  A100-years, minus whatever C1/C8/C5 deliver in nats — each nat is
  37% off the bill. The program: measure those three on toys; if
  together they exceed ~5 nats, 105-110 digits enters fleet range;
  100 needs either ~10^3 GPUs or genuinely new mathematics. Honest
  status: OPEN, not impossible — 10^53 qualifying integers exist.
- **E10. The committed sequence**: E1 → E4 → E5 → E6, packaging each
  record with full evidence as before; E7+ by explicit go/no-go on
  budget. Every stage revalidates the density model before scaling.
