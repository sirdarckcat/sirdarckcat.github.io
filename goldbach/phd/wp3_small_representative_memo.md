# WP3 memo — Sub-100 Goldbach deserts: reduction to modular subset-sum at density ≈ 1

Status: v2, 2026-07-28. **v1 of this memo claimed an "open window" for a
polynomial-time CRT-decoding attack. That claim was WRONG and is retracted
below** — the error is documented in §6 because it is instructive. All
computations here are reproducible from this repo; the one literature bound
is now verified against the source rather than recalled.

## 1. The target

Find even N < B = 10^100 with g(N) > 100,000: every prime q < 10^5 must have
N − q composite. Covering paradigm: impose N ≡ a_r (mod r) so that r | N − q
for all q ≡ a_r (mod r); the uncovered ("residual") primes must all fail an
independent primality lottery with exponent E = |U|·boost/ln N, where
boost = 2·Π_{r ∈ cover} r/(r−1).

**Sub-100 deserts exist in abundance.** With no cover, E_random ≈ 110, so the
density of qualifying N near 10^100 is ≈ e^−110 and the expected count below
10^100 is ≈ 10^100·e^−110 ≈ **10^52**. Nothing in this memo is an existence
obstruction; the entire difficulty is constructive.

## 2. Verified literature bound (replaces v1's recalled form)

Guruswami–Sahai–Sudan, *"Soft-decision" decoding of Chinese Remainder Codes*,
FOCS 2000, Theorem 3: for a CRT code with moduli p_i, message bound K, any
non-negative integers ℓ and z_i, one finds in time poly(n, log N, ℓ, Σz_i) all
codewords m with

  Σ_i a_i z_i log p_i > log(ℓ+1) + (ℓ/2)·log(K/2)
                        + (1/(ℓ+1))·Σ_i C(z_i+1, 2)·log p_i,

(a_i = 1 iff m ≡ r_i mod p_i). Optimising z, ℓ under uniform weights, with
L allowed classes per position (each (i,a) pair paying the cost term), the
agreement-mass radius is

  **A > sqrt(L · ln B · P)**,  P = Σ_{pool} ln p_i.

[V] Numerically confirmed against the exact finite-ℓ optimum: ratio
1.001–1.004 across pools 5·10^3–10^5 and L ∈ {1,2}. My recalled amplitude was
correct; the error in v1 was elsewhere.

## 3. The two regimes, honestly costed

Let A = cover mass (nats), lnB = 230.

**Regime I — A ≤ lnB (modulus fits under the bound).** The CRT progression
N = N₀ + kM itself supplies e^(lnB − A) candidates; cost = e^E.
[V] Optimum at Q = 10^5, B = 10^100: **44 moduli, M = 10^79, |U| = 1060,
boost 9.6, E = 44.1 → 1.4×10^19 candidates ≈ 9×10^5 GPU-years** at the
record engine's ~5×10^5 candidates/s (a candidate costs ~17 Fermat tests;
an earlier revision of this paragraph divided by the 8.5M tests/s TEST rate
and reported 5×10^4 GPU-years — a units error, corrected 2026-07-28).
Independent confirmation: goldbach/FRONTIER.md (parallel session, PR #28)
measures realizable E = 43.66 at 100 digits — 0.4 nats from this memo's
44.1 — and quotes 1.9×10^5 GPU-years at an optimistic 1.5M cand/s; at equal
throughput conventions the two studies agree. Sub-100 is ~7 orders of
magnitude beyond plausible compute; the fundable frontier is 130–140 digits
(FRONTIER.md's measured fleet band: 140d ≈ 13 days, 130d ≈ 5 months on the
existing 2-GPU engine — superseding this memo's cruder Colab estimates).

**Regime II — A > lnB (oversized cover).** Coverage is then excellent —
[V] all 9,592 primes q < 10^5 are covered by 355 moduli of mass 1,019 digits,
and 420 moduli with L = 16 gives |U| = 165, **E = 10.2: only ~27,000
candidates**. Solutions exist: the design space (which moduli, which classes)
carries ~2,698 nats of entropy against ln(M/B) = 2,630 nats, leaving a
surplus of ~+57 nats ⇒ ~e^57 valid (design, N) pairs below 10^100.
But the *density* of designs whose CRT representative lands below B is
**e^−2630**. Enumeration is out by ~1,100 orders of magnitude.

Regime II is where sub-100 becomes easy *if and only if* small
representatives can be found directly. That is the whole problem.

## 4. What the small-representative problem actually is

CRT reconstruction is additive: N ≡ Σ_{r∈S} a_r·(M/r)·((M/r)^{-1} mod r)
(mod M). So "find a design whose representative is < B" is exactly

  **minimise |Σ_r c_r mod M| over c_r ∈ C_r (|C_r| = L), target window [0,B)**

— an inhomogeneous **modular subset-sum with per-position choices**, with
[V] density d = (design entropy)/(ln(M/B)) = 2698/2630 ≈ **1.026**.

This is the worst possible density. Low-density instances (d < 0.94) fall to
lattice reduction (Lagarias–Odlyzko / Coster et al.); very high density
instances fall to birthday/k-tree methods (Wagner). Density ≈ 1 is the
regime where neither works and where subset-sum's presumed hardness is
concentrated. Concretely: the solution set is ~2^82 inside a design space of
~2^3893; meet-in-the-middle gives 2^1897, Wagner's k-tree with our list sizes
(16^40 per group) still needs 2^938 — both astronomically short.

## 5. Why the CRT-decoder shortcut fails (the retraction)

The decoder would bypass §4 entirely — but its radius is out of reach:
[V] at pool < 60,000, L = 16, radius = 14,845 nats vs our cover mass 2,860
nats — **short by 5.2×** (radius scales as sqrt(L·lnB·P), and P is the mass
of the *whole pool*, which must be far larger than the cover to supply
subset entropy). Shrinking the pool to lower the radius destroys the subset
entropy that makes solutions exist. That trade-off is the barrier:

  decodable ⇒ pool small ⇒ subset entropy small ⇒ no representative exists;
  representative exists ⇒ pool large ⇒ radius ≫ cover mass ⇒ not decodable.

**Barrier statement (heuristic, first-moment).** For CRT-cover constructions
of even N < B with g(N) > Q, no parameter choice simultaneously satisfies
(a) A < lnB + lnC(n,s) + s·lnL [representatives exist] and
(b) A > sqrt(L·lnB·P) [GSS-decodable]. Sub-100 via oversized covers therefore
requires list-recovery of CRT codes **beyond the Johnson-type radius** — an
open problem in coding theory — or a subset-sum algorithm at density ≈ 1.

## 6. The v1 error, recorded

v1 compared a decoding radius computed at agreement size s against an
existence bound *maximised over a different s* (≈ 2n/3). Requiring both
conditions at the **same** s closes the window at every pool size. Lesson for
the thesis: feasibility windows built from two separately-optimised bounds
are worthless; couple the parameters first. The published table in v1
("OPEN at R ≥ 60,000") is withdrawn.

## 7. Where this leaves the programme

1. **Regime I is the only currently viable route to sub-100** and it is out
   of reach: ~9×10^5 GPU-years (corrected; see §3), ~7 orders of magnitude
   beyond plausible compute — FRONTIER.md concurs independently. Realistic
   near-term targets: 140 digits (~13 fleet-days) to 130 (~5 fleet-months);
   120–125 digits (~10^2 GPU-years) is the institutional-scale edge.
2. **Two well-posed open problems** now sit under the record, either of which
   would collapse it: (i) CRT list-recovery beyond the Johnson radius for
   *structured, solution-abundant* instances; (ii) modular subset-sum with
   choices at density ≈ 1 where 2^82 solutions exist. Both are of independent
   interest — which is the right way for a thesis to end up.
2b. **Cross-validation with FRONTIER.md (merged from master 2026-07-28):** the
   parallel session's "set-valued conditioning" study measures the L>1
   relaxation this memo treats combinatorially: the sqrt extreme-value gain
   saturates at ~H^0.35 (overlap + Poisson discreteness), worth only 1–2.8
   nats of E — and its enumerability analysis states the structural theorem
   cleanly: *the classic cover is the unique design whose admissible set is
   an arithmetic progression (free to enumerate); every relaxation that buys
   coverage destroys enumerability and vice versa.* That is the constructive-
   side statement of this memo's density-1.026 barrier; the two analyses
   confirm each other from opposite directions. SoK §7's open angles #2
   (prime-first two-sided construction), #9 (complexity-theoretic placement
   of ∃N<B: g(N)>Q) and #10 (Grover halves the exponent: sub-100 at ~e^22
   quantum queries) are complementary directions not covered here.
3. **WP7 (algebraic mechanisms) is now the highest-value untested route**:
   every analysis here assumes compositeness is certified by *congruence
   divisors*. A mechanism certifying many N − q composite for algebraic
   reasons (norm forms, cyclotomic identities, Sierpiński/Riesel-style
   exponent families) escapes the entropy accounting entirely, because it
   does not spend ln r nats per excluded offset. That is the one place where
   the barrier of §5 does not apply.
