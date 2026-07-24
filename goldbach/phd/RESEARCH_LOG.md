# PhD Research Log — Extremal Least Goldbach Summands

Programme: *Extremal Least Goldbach Summands* (4-year proposal, record snapshot 2026-07-22).
Student log, year 3 — project kickoff with delegated subagent execution.

## Record board (project incumbents at kickoff, 2026-07-22)

| Game | Incumbent | Value | Status |
|---|---|---|---|
| Height H (Game 1) | 2,692-digit N (813-congruence cover, k=14) | g = 1,134,871 | **audited PASS** (2026-07-22) |
| Threshold T(100,000) (Game 2) | N₁₉₇ ≈ 6.939·10^196 (197 digits) | g = 107,719 | **audited PASS** (2026-07-22) |
| Budget R(10^199) (Game 3) | same N₁₉₇ | g = 107,719 | **audited PASS** (2026-07-22) |

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
