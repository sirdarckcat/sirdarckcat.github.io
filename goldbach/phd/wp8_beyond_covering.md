# WP8 — Strategy reflection: 3 crazy, 3 small, 3 professor, and one path to g ≥ 200,000

Status: 2026-07-29. Written at user request after campaign 3 was stopped
(duplicative with the fleet session already attacking R(10^200) at
Q=140,009). Brief: escape the bubble — no constraint is assumed binding,
up to and including "do you need a quantum computer?". Everything below is
cross-checked against the repo's idea ledgers (IDEAS.md F1–F7, IDEAS100.md
A/B/C/S/E, SoK §5/§7, PROPOSAL_NEXT_CAMPAIGNS.md, REGISTRY.md) so that
"new" means new; scripts for the fresh computations are in `wp8/`.

## 0. New evidence produced for this memo (all runnable, `wp8/*.py`)

**(a) The rung ladder.** E(Q) at 199 digits, same 88-moduli budget
(greedy + coordinate ascent + kicks; boost 11.01):

| Q | \|U\| | E | e^E candidates | × previous rung |
|---|---|---|---|---|
| 122,000 | 867 | 20.83 | 1.1e9 | — |
| 135,000 | 1,004 | 24.12 | 3.0e10 | ×27 |
| 150,000 | 1,138 | 27.34 | 7.5e11 | ×25 |
| 175,000 | 1,335 | 32.07 | 8.5e13 | ×113 |
| 200,000 | 1,569 | 37.69 | 2.4e16 | ×280 |

At the fleet's measured 7.9e5 cand/s: 135k ≈ 11 hours, 150k ≈ 11 days,
175k ≈ 3.4 years, **200k ≈ 950 fleet-years**. The spacing is geometric, so
climbing every rung costs ~4% more than jumping to the top — and banks a
certified record at each rung. (First 200k-scale cover computed in this
repo; SoK §6's "heroic ≈ 250k" band is consistent.)

**(b) The packing probe.** Coordinate ascent + 40–60 random-restart kicks
over the class assignment: at Q=122,000 the c1 greedy cover is a **local
optimum — zero improvement** (consistent with anneal.py's plateaus,
CAMPAIGN_PLAN, and single-swap stability). At Q=200,000 it gains 33 primes
(1,602 → 1,569, −0.79 nats). Cheap local search is worth <1 nat here.

**(c) The equilibrium, not the budget, sets cover size.** At B=10^200,
adding modulus r=461 to the 88 kills ~3.5 residuals (−0.084 nats) but
multiplies every surviving residual's primality odds by 461/460
(+0.082 nats): **net +0.00**. The cover is not budget-limited (lnM = 437 of
~458 available nats); it sits at the boost-vs-kills equilibrium. This is
why the frontier is flat, why leftover budget buys nothing, and why only
(i) rounding-gap mathematics or (ii) compute moves E.

**(d) SoK §7.4 executed — and it is vacuous.** The set-cover LP relaxation
(HiGHS, 2 s) reports **fractional coverage 100.00% at both Q=122,000 and
Q=200,000**: the 88 moduli carry Σ π(Q)/(r−1) ≈ 1.86·π(Q) of kill-mass and
fractional routing covers every prime. So LP dual prices certify nothing
about integral covers. Corollary worth stating loudly:

> **The entire exponent E of the budget game is an integrality/rounding
> gap.** Naive independent rounding leaves e^−1.86 ≈ 15.6% of primes
> uncovered; adaptive greedy leaves 7.56%; the fractional optimum leaves 0.
> Every 1% (absolute) of residual removed at Q=122k is ≈ 2.7 nats ≈ 15×
> less compute. Greedy sits halfway (in halvings) between naive and perfect.

**(e) Harvest curve.** The engine already computes g(k) for every candidate
(first passing PRP, ascending q; g=112,249 was banked exactly this way).
For c1, beating the incumbent without a full-cover hit is only e^0.29 ≈
1.34× likelier than a full hit — harvesting is free telemetry, not a
shortcut.

## 1. Three crazy ideas (bubble-escape first)

**C1 — The quantum answer: no, and here is the crossover arithmetic.**
(Upgrades IDEAS100 C4 / SoK §7.10, which state the Grover exponent-halving
but not the constants.) Grover needs e^{E/2} coherent oracle calls; one
oracle call = ~|U| reversible 660-bit modexps with no early-exit — at
Gidney–Ekerå-scale resource estimates, ~10^5–10^6 s per call on a
2030s fault-tolerant machine. Classical fleet: 1.25e−6 s per candidate.
Quantum wins only when E > E* = 2·ln[(C_q/W_q)·(W_c/C_c)]:

| assumption | E* |
|---|---|
| 1 FTQC, C_q = 10^6 s | ≈ 55 |
| 1,000 FTQCs | ≈ 41 |
| 1,000 FTQCs + 1000× cheaper oracle (miracle) | ≈ 27 |

The 200k target sits at E=37.7 and sub-100 at E=44.1: with any
non-miraculous constants the crossover lands **at or above the hardest
targets we care about**, and at the crossover both approaches cost the
same (i.e., both are infeasible). You do not need a quantum computer; you
would need thousands of much better quantum computers than anyone has
projected, to tie with GPUs. Park until C_q ≈ seconds.

**C2 — GoldbachGrid: the search is a perfect volunteer-compute lottery.**
(Upgrades IDEAS100 B9 "BOINC-shaped, ready when needed" from engineering
note to strategy.) The workload is progress-free Poisson (any ticket may
win, no shared state), embarrassingly parallel, checkpoint-free per ticket,
with millisecond verification of claims — structurally identical to the
workloads on which PrimeGrid/GIMPS-scale networks (10^4–10^6 hosts) hold
essentially all records in neighboring games (Sierpiński/Riesel are
themselves covering problems). The 200k wall needs ~e^6 ≈ 400× one Colab
fleet; a modest volunteer subproject or ~300–500 spot GPUs for a quarter
delivers exactly that. This is the only lever with a historical track
record of producing e^6 in this genre. Cost: a work-unit server, a signed
verifier (exists: verify_record.py + ECPP chain), and community care.

**C3 — Desert silicon: the problem is 95% one instruction.** A candidate
costs ~17 base-2 Fermat tests of 660-bit numbers; everything else is noise.
A Montgomery-modexp ASIC in the crypto-mining mold (fixed width, fixed
base, massively replicated cores) plausibly buys 10–100× an A100 per die at
~30× better energy/test; a single rack ≈ e^5.5–e^8 over today's fleet —
enough for 200k alone, with NRE in the single-digit $M (the soft version,
IDEAS100 C10's TPU-MXU big-int, is a weekend probe; an FPGA farm is the
no-NRE middle step). If the programme ever institutionalizes, this is the
capital-for-nats trade to price.

*Honorable mentions, included to show the bubble was actually left and
promptly re-entered for cause: analytic/Chebyshev-bias steering of
complements is quantified dead (bias ~10^−70 at our sizes, IDEAS100 B5;
and P5's |Ê−E| ≤ 0.1 over 1.2e9 candidates empirically bounds ALL
exploitable structure); learned k-prioritization (C5) is bounded by the
same P5 result — the survivor count is already a sufficient statistic, and
--skip-frac is its optimal policy.*

## 2. Three obvious small optimizations (do these regardless)

**O1 — Port --skip-frac + --sort-tests to the GPU fleet.** Measured 3.0×
net discovery on CPU (hit%=27.6 at 9.2× raw rate); the fleet kernels
(fermat_t4.py wave scheduler) test exhaustively today. Expected 2–3× on
fleet = the cheapest ~1 nat in the programme. One kernel-launch reorder +
survivor-count compaction.

**O2 — Execute IDEAS100 A7/C3: product-tree (remainder-tree) batch
sieving.** Batch-gcd thousands of complements against primes to 10^9–10^10
at ~amortized-linear cost: p̂ rises ×~1.5, tests/k fall accordingly, and
the per-block kres cost (∝ π(B)·|U|) disappears into the tree. ~1.4–1.6×,
pure Bernstein-style engineering, never run here.

**O3 — Replace the fixed skip fraction with the exact marginal rule.** We
already compute the survivor histogram and exact hit-mass weights per
block; the optimal policy is a threshold on marginal hit-mass per test
(test k while w(k)/E[tests|k] ≥ λ*), not a fixed f=0.92. +5–15%, zero risk
(the accounting stays exact). Add the incremental-kres cache and BATCH=8
amortization (+~10%). Note: under skip economics, IDEAS100 B8's
variance-widening anti-covers (fatten the low-survivor tail) are worth
more than when proposed — the kept-mass share rises with σ_a; re-price it.

## 3. Three professor moves

**P1 — Never attack the top; run the certified ladder.** Formalize what the
ratchet sessions discovered empirically (199→193→186→179 dominates
grand slams): with geometric rung spacing (×25–30 in e^E), Σ rungs ≈ 1.04 ×
top rung, every rung banks a certified record, every rung is a calibration
of Ê before the next commitment, and optimal-stopping/renewal analysis
turns "when do we stop/redesign" into arithmetic instead of vibes. The
sibling fleet at Q=140,009 IS rung 1 of the 200k ladder — coordinate
(disjoint variants via a repo ledger), never duplicate. Dedicated cover per
rung (the ladder-in-one-cover alternative pays e^1.5–2 per rung; computed
and rejected).

**P2 — The rounding-gap programme (Erdős–Rankin/FGKMT transfer).** Result
(d) reframes IDEAS100 B2 from "cheap to check" to the central mathematical
question: the fractional cover is perfect; greedy rounding loses 7.6%; the
large-prime-gap literature (Rankin's layered covers; Ford–Green–Konyagin–
Maynard–Tao's semi-random covering with second-moment control and a
hypergraph-matching endgame — already cited in paper.tex for the lower
bound, never used constructively here) is precisely a technology for
rounding fractional covers of primes with quantified loss. Their loss is
o(1) in an asymptotic regime that is NOT ours (their moduli reach y/2;
ours cap at 457) — which is exactly why this is a thesis-grade open
question rather than a lookup: determine the achievable residual fraction
at π(Q) ≈ 10^4, budget θ(457). Every −1% absolute is ~15× compute;
closing even half the gap to 3.8% is e^10 ≈ 22,000×, which converts the
200k wall from "volunteer network" to "one GPU-month".

**P3 — Find the relaxation that certifies (or refutes) the gap.** The plain
LP is now proven vacuous (result d), so SoK §7.4 as posed is dead; the
honest successor question is a lower bound on min |U| over assignments:
Sherali–Adams/Lasserre lifts of the one-class-per-modulus polytope,
second-moment counting over the e^437-size assignment space, or a
Lovász-local-lemma-style obstruction. Deliverable either way: a certified
floor ("no assignment beats |U|=X, stop optimizing") or a licensed hunt
("the floor is far below greedy — fund P2"). Includes formalizing result
(c): the boost-vs-kills equilibrium as the true frontier equation
dE/d(cover) = 0, replacing budget-limited intuition at B ≥ 10^150.

## 4. The balanced idea — Operation Staircase: a costed path to g ≥ 200,000, N < 10^200

One plan combining a crazy (C2), the optimizations (O1–O3), and the
professor structure (P1–P3), with decision gates:

1. **Now (rung 140k, running):** the fleet session's Q=140,009 round
   (E=24.96, ~4.75 expected hits) — first hit expected in days. Bank it.
2. **+1 week (engine):** O1+O3 land on the fleet (×2–3); O2 prototyped.
   Rung 150k (E=27.3): ~4 fleet-days after the engine work. Bank it.
3. **+1 month:** rung 165k (E≈30.1, interpolated): ~2–3 fleet-weeks with
   the upgraded engine. In parallel, P2/P3 run as theory workpackages; any
   ≥1-nat rounding result compounds every later rung.
4. **+1 quarter (rung 175k, E=32.1):** ~1.4 fleet-years raw → 2–4 months
   with O1–O3 × modest fleet growth (5–10 GPUs). Gate: if P2 delivered
   ≥2 nats, stay in-house; else launch C2 (volunteer/spot swarm).
5. **The wall (rung 190k–200k, E=35.4–37.7):** needs ~e^5.5 beyond step 4.
   Three interchangeable closers, priced: 300–500 swarm GPUs × 1 quarter
   (C2, ~$100–300k spot or ~$0 volunteer); ASIC/FPGA rack (C3, $1–10M,
   permanent capability); or −4 nats of P2 mathematics + 10× fleet. Any
   one suffices; any two make it comfortable.
6. **Throughout:** every rung dual-verified (witnesses + PARI ECPP +
   independent checker) and banked exactly like the existing records;
   harvest-g telemetry logged (free); parallel workers claim disjoint
   variants in a committed ledger — this memo's own campaign was stopped
   for duplication, and the ladder only works if rungs are coordinated.

Expected profile: records at ~140k and ~150k within weeks, ~165k within a
month or two, 175k inside the quarter, and 200,000 in two to four quarters
— with the long pole (the last e^5.5) attackable by money, community, or
mathematics, whichever the programme can actually raise. No quantum
computer required (C1), and the mathematics that would cheapen everything
by orders of magnitude is now a named, LP-motivated open problem (P2/P3)
rather than a vibe.

## 5. Housekeeping flags

- **Game naming**: R(10^199) vs R(10^200) is inconsistent across
  RESULTS.md / SoK / directory names (g=112,249 is a 200-digit N ≥
  10^199). The ladder above targets N < 10^200; state the bound per
  record explicitly.
- Campaign 3 assets (Q=122,000, 40 variants, 380/17,200 slices banked)
  remain valid as a spare rung-0; the fleet's Q=140,009 supersedes its
  purpose while it runs.
