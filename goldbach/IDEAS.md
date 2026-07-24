# Ideas ledger: order-of-magnitude improvements

Each nat of E-efficiency or search-throughput is worth e× less work;
2.3 nats = one digit of threshold-game progress. Fronts stay open until
an experiment kills them; nothing dismissed on intuition alone.

## F1 — The threshold game is soft (ACTIVE)

The 197-digit T(100,000) record came from a *dual-game* cover built at
Q = 105,668 (it had to beat the budget game too). A pure threshold
cover only needs Q = 100,003: ~8% fewer targets → |U| ≈ 700 →
E ≈ 17.2 at 195 digits (~3× less search than the record's 18.2), with
one digit of N-size improvement per ~2.3 nats. Plan: verify with a
real cover, then campaign 195 → 194 → 193 digits.
Status: cover built at Q=100,003 (see below); campaign pending.

## F2 — Order-statistics search: test emptiest k first (ACTIVE)

After sieving, k-values differ in surviving residual count a_k
(mean ~316, sd ~14 for the R-campaign cover). Success probability per
k is (1-p)^{a_k} — hits concentrate exponentially (tilt e^{-p a}) in
the low-a tail, but the scanner tests k in index order. Two-phase
search (sieve everything, then Fermat-test globally in ascending-a
order with stop-at-first-success) should cut discovery cost by the
tilt factor. Predicted gain ~1.5-3.5×; measure the hit-vs-a
distribution on toys first.
Status: toy measurement running.

## F3 — Cover optimality gap (OPEN)

Three anneal seeds converged to identical |U| — plateau or optimum?
Measure the gap vs exact/ILP at small Q where exhaustive residue
choice is feasible; if the gap is real at scale, parallel tempering /
LP-rounding at Q = 100,003 buys direct E. Each −0.1 in E = 10% less
search.
Status: not started.

## F4 — Zero-penalty variant catalogs (OPEN)

gen_variants pays +0..12 residuals per variant (catalog-average E
+0.1..0.3 over base). The annealer plateau implies many *equal*-|U|
assignments exist; enumerate them (tabu walks at T=0, or k-list
assignment enumeration filtered to d|U| = 0) for catalogs whose E
equals the base everywhere.
Status: not started.

## F5 — Throughput engineering (OPEN)

- All variants share M, but init_spec recomputes pi(3e6) sieve
  inverses per spec (~0.4 s × catalog size): cache (S, inv) keyed on M.
- Sieve-depth sweep: deeper B cuts Fermat tests/k ~ 1/ln B but sieve
  cost rises; optimum depends on kmax per spec. Measure the curve.
- Fermat batching / lower per-test overhead (gmpy2 call overhead is
  ~30% at 660 bits).
Target ≥1.5× combined.
Status: not started.

## F6 — R(10^200) follow-up lottery (OPEN)

Q = 112,250 catalogs with ceiling 200: 10× the k-range per variant vs
the 10^199 game, chasing our own g = 112,249. Secondary to F1 on
shared CPU.
Status: not started.

## F7 — Understood dead ends (kept honest, with the numbers)

- *Planting composites via k-congruences*: forcing s | N-q costs
  density 1/s (ln s ≥ 6.1 nats for s coprime to M) to save p ≈ 0.06
  nats — the sieve already harvests this optimally for free.
- *Composite/prime-power moduli*: their classes are subsets of their
  prime factors' classes.
- *Alive-variance-maximizing covers*: couples to F2 — if the low-a
  tail is where hits live, cover choices that fatten that tail
  (correlated residual sieve positions) could compound the F2 gain.
  Speculative; revisit after F2 measurements.
