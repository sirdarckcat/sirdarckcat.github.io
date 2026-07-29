# Door 1, D1.1 gate — VERDICT (2026-07-29, after 3 turns)

**Question:** does exact large-neighborhood optimization beat the
greedy plateau |U| = 867 at Q = 122,000 (1 prime = 0.024 nats of E)?

**Answer: NO — and the reason is structural, not effort-bounded.**

## Evidence

1. **41 exact CP-SAT windows** over the c1 assignment (sizes 7–15,
   caps 25–300 s, warm-started, incumbent-floored; tight-set,
   tight-random and uniform-random window selection): 867 never
   beaten, matched every time.
2. **LP window certificates** (floor(LP) = incumbent coverage):
   **21 of 22 windows where computed are CERTIFIED window-optimal**,
   including tight-set windows at sizes 12 and 15. The single
   uncertified window contains the smallest moduli, where the LP shows
   its known fractional looseness (gap 16 — wp8 §0(d) in miniature).
3. **Basin probe:** a random-start coordinate-ascent solution
   (|U| = 968) is ALSO window-optimal: 20 exact windows (size 8)
   recovered 0 of its 101-prime gap to greedy. Combined with D1.0's
   backbone-at-chance-level finding, the landscape is a field of
   mutually distant, locally-exact-stable basins spanning at least
   [867, ~980].

## Interpretation

- Window-exact local search CANNOT move between basins at all — so
  "no improvement from 867" was guaranteed once c1 proved
  window-optimal; equally, nothing about local search says whether a
  deeper basin than 867 exists elsewhere.
- What IS informative: greedy's sequentially-adaptive construction
  landed ~100 primes deeper than typical local optima. The remaining
  Door-1 question is therefore about CONSTRUCTION ENSEMBLES and
  GLOBAL moves, not local exactness:
  D1.2 tempering must use basin-hopping-scale moves (10+ simultaneous
  class changes accepted uphill) or it will measure nothing;
  SP/BP-decimation and the D1.3 banded/matching constructions are the
  live routes; the annealed threshold estimate (~758, wp8 §6) remains
  the only evidence a deeper basin exists at all — it is an
  ensemble-existence heuristic, not a constructive promise.
- For P3 (certificates): per-window LP certification is cheap and
  tight away from small moduli. A global certificate would need to
  handle precisely the small-moduli looseness — consistent with wp8's
  finding that the global LP is vacuous. Lift candidates
  (Sherali–Adams on the small-moduli block only) are the natural next
  formal object.

## Recommendation

Park D1.1 (done, negative, certified). Next Door-1 investment, in
order: (a) D1.2 basin-hopping tempering with move sizes ≥ 10 classes,
budgeted a few CPU-days; (b) BP/SP-decimation implementation (also
yields the quenched-threshold estimate); (c) D1.3 banded construction
with exact b-matching endgame — the one route that mimics WHY greedy
wins (sequential adaptivity) while adding exactness where greedy is
myopic. Expected value honestly restated after this gate: the
858-to-758 annealed prize is real but unreachable by local methods;
global methods carry an unknown but nonzero share of it.

---

# D1.2 verdict addendum (BP/SP-decimation, 2026-07-29)

Method validated: sequential sum-product BP tracks exact E[U] to 0.7%
(soft regime) and BP-guided decimation finds the toy instance's EXACT
optimum (54; greedy-style 55+). On the real instance (d12_bp.py):

- **Decimation: 874 (β=1.5), 887 (β=2.5), 922 (β=3.5)** — best is 7
  primes above greedy's 867; higher β over-polarizes early freezes.
- **LNS polish of the 874 solution: stays 874** — window-optimal in
  its own basin. Third independent locally-exact basin (867 / 874 /
  968), all mutually unreachable by exact windows.
- **Naive RS/Bethe is not a threshold estimator here**: as β grows the
  Bethe E[|U|] slides toward the fractional fantasy (35 at β=4 vs LP 0,
  annealed 758, achieved 867) — mean-field shares the LP's blindness
  to integrality. A real quenched threshold needs 1RSB/SP with
  complexity (Σ) bookkeeping — noted as the remaining theory item.

**Door-1 running verdict after D1.1 + D1.2:** greedy's 867 has now
survived (i) 41 exact windows, 21/22 LP-certified; (ii) an
independent, structurally different global construction (BP
decimation) landing at 874 — closer than anything else known but not
below; (iii) basin isolation confirmed three ways. The evidence
increasingly reads: **867 is at or very near the quenched optimum for
this moduli set at Q=122,000**, and the annealed 758 likely reflects
an annealed–quenched (clustering) gap rather than reachable headroom.
Remaining unexhausted routes, in descending expected value: D1.3
banded construction with exact b-matching endgame (different ENSEMBLE,
not different search); basin-hopping tempering (brute global moves);
1RSB/SP for the honest threshold number. Each is bounded work; none is
blocking. The Door-1 prize estimate should be revised down from
"2.6 nats to the annealed threshold" to "0–2.6 nats, with the
clustering gap plausibly eating most of it."
