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
Status: **WON** (2026-07-25) — records/threshold_195digit_g100297:
N ≈ 7.12·10^194 (195 digits) with g = 100,297, a 100× improvement on
the 197-digit incumbent. Round 1 (600 specs) came up empty (P(0) ≈
25%); the hit landed in round 2 at spec v990, k = 70,186 — 1,590
progressions ≈ 1.75·10^8 sieved elements total, cumulative
expectation ~1.9 at exact density e^-17.5: the draw landed at the
mean. Measured Ê = 17.4 throughout (predicted 17.28 naive / 17.51
exact). The F1+F2+F5 stack (pure-threshold cover 3×, sorted testing
1.8× conditional, sieve tuning 1.1×) delivered the two-digit record
on a 4-core box in ~30 h of scan. Next rungs: finish round 2's
remaining 209 specs for a possibly smaller N, then 194 digits via
the F4 zero-penalty catalog (needs ~3,000 variants at K = 10^4).
Round-2 tail addendum: a second independent hit at v1088, k = 76,862
(N ≈ 7.80·10^194, g = 101,611) — larger than the record N, so the
record stands, but the tally is now 2 hits in ~1,780 progressions
vs cumulative expectation ~2.1: the density model is exact.

## F2 — Order-statistics search: test emptiest k first (ACTIVE)

After sieving, k-values differ in surviving residual count a_k
(mean ~316, sd ~14 for the R-campaign cover). Success probability per
k is (1-p)^{a_k} — hits concentrate exponentially (tilt e^{-p a}) in
the low-a tail, but the scanner tests k in index order. Two-phase
search (sieve everything, then Fermat-test globally in ascending-a
order with stop-at-first-success) should cut discovery cost by the
tilt factor. Predicted gain ~1.5-3.5×; measure the hit-vs-a
distribution on toys first.
Status: MEASURED and DEPLOYED. Toy (p = 0.305): hit-mean shift −5.7
vs −p·σ² = −5.2 predicted; 53% of hits in the bottom a-decile; 12×
tests-to-first-hit gain. Campaign scale (p = 0.059, exact
computation over the real T-cover's sieved a-distribution): 1.83×
conditional discovery gain, median first hit 15% into the sorted
catalog. For full-sweep *expectation* the sieve phase dominates and
the gain is only ~8%, so the deployed form is per-block sorted
testing + stop-on-success (`search.py --sort-tests`): bank the
record early, then descend a digit. Corollary measured: the exact
density is e^{-a·ln(1-p)} averaged over a — E_eff 17.51 vs naive
17.28 at 195d; the naive formula undercounts by ~0.2 nats.

## F3 — Cover optimality gap (OPEN)

Three anneal seeds converged to identical |U| — plateau or optimum?
Measure the gap vs exact/ILP at small Q where exhaustive residue
choice is feasible; if the gap is real at scale, parallel tempering /
LP-rounding at Q = 100,003 buys direct E. Each −0.1 in E = 10% less
search.
Status: CORRECTED — the apparent E 17.07 < 17.28 in the catalog was a
convention mismatch (self-consistent-D vs fixed-195d evaluation), not
better covers; those variants have exactly |U| = 704. Steepest descent
(all moduli × top-8 residues, first-improvement, to fixpoint) from 5
starts finds zero improving single swaps: the annealed cover is
single-swap-stable. The optimality gap question stays open — needs
pair/triple moves, basin hopping, or ILP at small Q.

## F4 — Zero-penalty variant catalogs (OPEN)

gen_variants pays +0..12 residuals per variant (catalog-average E
+0.1..0.3 over base). The annealer plateau implies many *equal*-|U|
assignments exist; enumerate them (tabu walks at T=0, or k-list
assignment enumeration filtered to d|U| = 0) for catalogs whose E
equals the base everywhere.
Status: MEASURED on the Q=100,003 T-cover: 26 zero-penalty single
swaps (e.g. r=401 has 4 equal-coverage alternatives) → 325 pairs →
~2,600 triples: a ~3,000-progression catalog at exactly base E —
just what the 194-digit round needs (K = 10^4 per variant there).
The current 195d catalog's early variants are already zero-penalty.

## F5 — Throughput engineering (OPEN)

- All variants share M, but init_spec recomputes pi(3e6) sieve
  inverses per spec (~0.4 s × catalog size): cache (S, inv) keyed on M.
- Sieve-depth sweep: deeper B cuts Fermat tests/k ~ 1/ln B but sieve
  cost rises; optimum depends on kmax per spec. Measure the curve.
- Fermat batching / lower per-test overhead (gmpy2 call overhead is
  ~30% at 660 bits).
Target ≥1.5× combined.
Status: sweep DONE on the T-cover (30k k, B ∈ {3e5, 1e6, 3e6, 1e7}):
B = 1e6 optimal (901 k/s vs 816 at the old 3e6 default; measured
density invariant across depths as required). Campaign runs at 1e6.
Sieve-inverse caching across same-M specs: worth ~2 min per 600-spec
catalog; skipped for now. Fermat batching: open.

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
