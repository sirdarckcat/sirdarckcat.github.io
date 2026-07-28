# Goldbach Desert Records

## Prior-art check (2026-07-27)

A web literature search for published constructions of even integers
with large least Goldbach summands found none beyond the incumbents
this repo already cites and supersedes. For context: in *observed*
(exhaustive-verification) data the minimal summand stays tiny — the
largest known naturally occurring value is g = 9 781 near the
4·10^18 verification frontier (Oliveira e Silva, Herzog & Pardi,
Math. Comp. 2014; Herkommer's tables reach g = 8 443 at
2n ≈ 1.2·10^17), and a 2025 arXiv study of minimal primes in
generalised Goldbach partitions (arXiv:2510.21870) is observational
up to 10^9 only. The only constructive incumbents we are aware of
remain the source paper's 199-digit N with g = 105 667 and 237-digit
N with g = 109 621 (both re-verified in this repo before we started).
The records below are therefore "smallest/largest known to us"; if a
competing constructive literature exists it did not surface in the
search.

In-repo note: a parallel effort in `slop/goldbach/records/` (merged
from another working branch) holds a certified T(100k) bound of 179
digits (g = 101 149) and R(10^200) g = 119 419. The 150-digit record
below supersedes the 179-digit T bound; the slop R value g = 119 419
at 199 digits supersedes this directory's g = 112 249.

## New record (2026-07-26): T(100 000) at 150 digits — the GPU rung,
## 45 digits below our own 195-digit record

**N** (150 digits, `records/threshold_150digit_g104527/record.json`,
N = N0 + 62 147 038 260·M over a 68-modulus cover with M of 140 digits):

```
82666896361422214889140173486824909338317018059813
51031435344058125034274739390508125558021767403422
36249163597526688699521722930930329320505713336368
```

**g(N) = 104 527 > 100 000** with N ≈ 8.27·10^149 — the smallest known
even integer whose least Goldbach summand exceeds 100 000, taking 45
digits off the 195-digit record below (10^45× smaller). Evidence
(`evidence.json`, fully machine-checkable): all 9 977 prime offsets
q < 104 527 have N − q composite — parity (1), congruence divisor from
the cover (9 097), trial divisor < 10^5 (433), strong base-2
Miller–Rabin witness (446, unconditional). 104 527 is prime and
N − 104 527 is ECPP-certified prime (`complement_cert.gp`,
validated by `primecertisvalid`, see `check_cert.log`).

This rung was unreachable by the CPU pipeline (failure exponent
E = 24.91 at 150 digits vs 17.5 at 195 — e^7.4 ≈ 1 600× more search
per hit) and is the first result from the CUDA engine
(`gpu/engine150.py`: bit-matrix sieve + Montgomery CIOS base-2 Fermat
waves, validated bit-for-bit against Python; ~2.5M tests/s on a T4,
~8.5M tests/s on an A100 — ~430× the 4-core CPU pipeline). The k-range
[0, 7.5·10^10) was sharded across a rotating two-session Colab fleet
driven by `gpu/fleet.py` (safe_k checkpointing in git survived ~10
session culls and several container rollbacks with zero coverage
loss). The hit landed at k = 6.21·10^10, 63.8% into the round —
cumulative expectation ~0.63·0.64 ≈ 0.40 at the exact density
e^-24.91, within the central mass of the Poisson draw. The engine
found it after ~1.9·10^9 Fermat tests on this shard alone.

ROUND COMPLETE (2026-07-27): the full k-round [0, 7.5·10^10) has now
been scanned end to end (~2.1·10^12 Fermat tests across the fleet) —
exactly one hit, the record above. One draw against a Poisson mean of
0.63 is an unremarkable outcome; the density model stays unfalsified.
The next rung is 140 digits (E ≈ 28, ~22× this round's search).

## New record (2026-07-25): T(100 000) at 195 digits — 100× below the
## previous smallest desert past 100 000

**N** (195 digits, `records/threshold_195digit_g100297/record.json`,
N = N0 + 70 186·M over an 88-modulus cover with M of 190.0 digits):

```
71214124265787855971290038426160102511378229003272506217668297957
68214756376976852660013284997485991512845267319174394030269434418
51527812156074627008575588613267417336439269800778493535893423578
```

**g(N) = 100 297 > 100 000** with N ≈ 7.12·10^194 — the smallest known
even integer whose least Goldbach summand exceeds 100 000, beating the
197-digit record below by two orders of magnitude (and the paper's
199-digit incumbent by four). Evidence (`evidence.json`, fully
machine-checkable): all 9 614 prime offsets q < 100 297 have N − q
composite — parity (1), congruence divisor from the cover (8 903),
trial divisor < 10^5 (312), strong base-2 Miller–Rabin witness (398,
unconditional). 100 297 is prime and N − 100 297 is ECPP-certified
prime (`complement_cert.gp`, validated by `primecertisvalid`, see
`check_cert.log`).

Why this was reachable (see IDEAS.md for the measured ledger): the old
197-digit record came from a *dual-game* cover built at Q = 105 668; a
pure threshold cover at Q = 100 003 needs |U| = 704 instead of 752,
dropping the failure exponent from 18.2 to 17.28 (~3× cheaper), and
the new ascending-survivor test order (`search.py --sort-tests`,
measured 1.8× conditional discovery gain) plus the B = 10^6 sieve
optimum stack on top. The hit arrived after 1 590 progressions
(~1.75·10^8 sieved elements) across two 600-spec catalogs — cumulative
expectation ~1.9 at the exact density e^-17.5, so the draw landed
right at the mean. Measured Ê = 17.4 throughout, matching prediction
to 0.1.

## New record (2026-07-23): g(N) = 112 249 below 10^200

**N** (200 digits, `records/budget_1e200_200digit_g112249/record.json`,
N = N0 + 56 770·M over a 90-modulus cover with M of 194.3 digits):

```
10336361862320265637534248784107115912943733452949552173021625784255
26491232455104184949353771968786907192598875701371548940638695734951
1701812962805353232599898800895271779892845641377568833632
```

**g(N) = 112 249** — the largest least-Goldbach-summand known below
10^200, beating the best previous sub-10^200 value g = 107 719 (the
197-digit record below) and the paper's 237-digit height-game incumbent
g = 109 621 at 37 fewer digits. It misses the budget game R(10^199) by
3.4%: N = 1.0336·10^199. The find is a by-product of the R(10^199)
frontier campaign (see the 1M section below): search blocks are sieved
in full 16 384-element chunks, so ~16% of scanned candidates sit just
above the 10^199 ceiling, and the first success of the campaign landed
there (k = 56 770 vs the in-budget cap k ≤ 54 924) — at the measured
density Ê = 18.4 that is a fair draw from ~4.6·10^7 scanned elements.

Evidence (`evidence.json`, fully machine-checkable): all 10 642 prime
offsets q < 112 249 have N − q composite — parity (1), congruence
divisor from the cover (9 830), trial divisor < 10^5 (409), strong
base-2 Miller–Rabin witness (402, unconditional). 112 249 is prime and
N − 112 249 is ECPP-certified prime (`complement_cert.gp`,
validated by `primecertisvalid`, see `check_cert.log`).

## The 1M-desert-below-200-digits question (2026-07-22): measured — the
## frontier is ~1,250 digits, and 199 digits is short by a factor e^170

Target: even N < 10^200 with g(N) > 10^6, i.e. all 78,498 primes
q ≤ 10^6 have N − q composite. `exp1m.py` measures what that costs.

**Mechanism audit.** Compositeness of N − q across many q at once can
only be forced by congruence covers — r | N − q exactly when q ≡ N
(mod r), one residue class per prime r. Everything else is dead on
arrival: composite or prime-power moduli cover subsets of what their
prime factors already cover; algebraic factorizations of N − q need q of
a special polynomial shape no prime > 2 has; perfect powers in the
window [N − 10^6, N] don't exist (consecutive squares at 10^200 are
~10^100 apart); and hiding the desert inside a genuine prime gap of
10^6 needs gap merit 2,180 versus ~42 ever observed and ~460
conjecturally possible anywhere. What the cover leaves uncovered must
be composite by luck, at density e^−E with E = |U|·boost/ln N — a model
this repo has now validated at four scales (toy 26-digit: predicted
E 12.53, measured 12.51; toy 62-digit: 13.52/13.57; the 197-digit
record: 18.2/18.2; the 2,692-digit mega: 6.6/6.56).

**The E(D) frontier at Q = 10^6** (lazy-greedy digit-capped covers,
`exp1m.py frontier`; E at ln N = D·ln 10):

| digits D | moduli | |U| | E | search cost e^E |
|---|---|---|---|---|
| 199 | 91 | 8 157 | 196.7 | 10^85.4 |
| 300 | 127 | 7 311 | 124.3 | 10^54.0 |
| 400 | 161 | 6 728 | 89.3 | 10^38.8 |
| 600 | 226 | 5 865 | 54.9 | 10^23.8 |
| 800 | 288 | 5 241 | 38.2 | 10^16.6 |
| 1000 | 347 | 4 741 | 28.4 | 10^12.3 |
| 1300 | 435 | 4 100 | 19.6 | 10^8.5 |
| 1600 | 519 | 3 588 | 14.2 | 10^6.2 |
| 2400 | 736 | 2 492 | 6.9 | 10^3.0 |

D_min for a record-scale search (1.4·10^8 candidates, E ≤ 16.6):
**~1,470 digits**; heavy single-box (10^9, E ≤ 21): **~1,250**;
distributed (7·10^10, E ≤ 25): **~1,120**; a cosmological budget
(10^12/s for the age of the universe, E ≤ 68): **~520 digits**. The
2,400-digit row reproduces the mega record's regime (E 6.9 vs its 6.56)
— the model and the ladder are consistent end to end.

**The 199-digit wall** (`constructions/wall_1M_199d.json`, verified):
the best 199-digit system found — 91 moduli, residue-annealed — leaves
|U| = 8,146 residual primes, E = 196.4, success density 10^−85.3.
Annealing recovers only ~0.3% of E: the wall is structural, not an
optimization shortfall. (Structural in the sieve sense, not the
counting sense: the 91 best classes hold 148,290 slots for 78,497
targets, a 1.89× supply, so a union bound alone forbids nothing — but
prime residue classes overlap like independent sieves, coverage stops
at ~90%, and 60,000 anneal moves reclaim 11 residuals of 8,157.) Joint x/M
optimization does not help either: +25 digits of k-list entropy moves
E from 196 to ~194. Meanwhile the existence heuristic (E_random ≈ 445
for unstructured even N) predicts ~10^6.5 such N below 10^200 *exist* —
the conjectured (log N)²·log log N maximal order sits at 1.3·10^6
exactly at 200 digits — but the cheapest known path to *exhibit* one
costs 10^85 primality tests. This is a construction-versus-existence
gap of fifty-nine orders of magnitude beyond cosmological.

**The blueprint** (`constructions/blueprint_1M_1250d.json`, verified):
the cheapest practical 1M desert this machinery can specify — 420
moduli, M = 1,247 digits, |U| = 4,205, E = 20.74, i.e. ~10^9
progression elements ≈ **235 core-days** at 50 candidates/s. A
distributed campaign at mega-record throughput would find an
N ≈ 1,255 digits with g(N) > 10^6; that is the realistic version of
this target.

**The achievable 200-digit frontier** is the budget game R(10^199)
itself: at Q = 107,720 the annealer lands M = 194.3 digits, |U| = 764,
E = 18.0 (~18.3 at the 199-digit budget) — each residue-swap variant
progression holds ~47,000 sub-budget candidates, so a scan block of
several hundred variants is a ~25–35% lottery at beating g = 107,719.
The campaign run for this work scanned 1,300 distinct progressions
(500 + 800 fresh via the new `pair_pool` knob in `gen_variants.py`) —
8.5·10^7 elements at 1,850/s and measured Ê = 18.4 (predicted 18.3).
Expected hits: 0.70 in-budget + 0.14 in the 16% sieve-block overshoot
above 10^199. Observed: exactly one, in the overshoot — the
g = 112 249 record above. Poisson-fair on both counts; the strict
R(10^199) coin flip (48% per ~14 h of 4-core scan at this frontier)
landed tails this time. The incumbent 107 719 consumed ~21 h at the
same frontier; extending the catalog (deeper pair_pool, triple swaps,
or re-annealed bases) and re-running is purely a matter of core-hours.

## Joint representative/coverage optimization (2026-07-22): a 221-digit
## modulus with a sub-10^197 representative

Question: can we deliberately build a CRT system whose modulus M has far
more than 197 digits but whose least positive representative x has fewer
than 197 digits — while keeping record-class coverage of prime offsets?
Answer: **yes, by tens of digits, and the gain is exactly the entropy of
the residue search; hundreds or thousands of digits are out of reach.**

`joint.py` extends the annealer's objective log M + E to the expected-hit
objective **Phi = E − log K(x, M; B)**, where K = max(0, ⌊(B−1−x)/M⌋+1)
counts progression elements below the size budget B. It tracks the exact
representative incrementally through the CRT basis C_{r,a} =
a·(M/r)·((M/r)^{-1} mod r): a residue move shifts x by (a′−a)·C_{r,1}
mod M, so coverage counts and x anneal together. The heavy tool is a
multiple-choice modular meet-in-the-middle (`klist_solve`): split a block
of moduli into 2^d lists, enumerate the top-c residue classes of each,
and Wagner-merge with shrinking centered windows until the representative
lands in a target interval. 2^d lists of size L buy about
(d+1)·log10(L) digits of cancellation below M.

Measured on the 197-digit record's cover (88 odd moduli, M = 191
digits, |U| = 752, B = 10^197):

- **No structural small-x bias.** Over 2 000 random top-4 residue
  reassignments the deciles of x/M are (0.10, 0.25, 0.50, 0.75, 0.90) —
  uniform; the minimum matches the 1/samples order a uniform draw
  predicts. Only search entropy buys small representatives.
- **Phi reduces to the old objective while M ≪ B.** Across all x in
  [0, M), K changes by at most one (Δlog K = 7.3·10^−7): the record
  pipeline was already optimal in its regime, and E computed at the
  budget scale (18.20) reproduces the measured search density Ê = 18.2.
- **2-list MITM, moduli held fixed**: 46 solutions with x/M < 10^−8
  from 4^8 combos per side (entropy predicts ~43); the best costs
  **+8 residuals** (752 → 760) for **8.3 digits of cancellation**.

Constructions past the budget (`constructions/`, each re-verified
end-to-end: x ≡ a_r (mod r) for all 96–99 congruences, x < 10^197,
residual set recomputed from scratch):

| file | moduli | digits(M) | digits(x) | \|U\| | E at 10^197 |
|---|---|---|---|---|---|
| `m211_x196.json` | 2 + 95 | 211 | **196** | 738 | 18.09 |
| `m219_x197.json` | 2 + 98 | 219 | **< 197** | 784 | 19.33 |
| `m221_x197.json` | 2 + 98 | 221 | **< 197** | 782 | 19.32 |

The 211-digit system (4 lists × 8 moduli × top-5, 14.9 digits
cancelled) is a strictly *better* cover than the record's own (|U| 738
vs 752, E 18.09 vs 18.20) — the seven added moduli cover more residuals
than the block reassignment exposes. The 219-digit system (8 lists ×
8 moduli × top-5, 21.3 digits cancelled, 52 solutions where the
window/entropy calculus predicted ~50) shows the 4-level Wagner tree
delivering its full (d+1)·log10 L budget. The deepest run, 8 lists ×
8 moduli × top-6 over 64 block moduli, cancelled **24.3 digits**
(83 solutions, ~25 min / ~8 GB on 4 cores) for the 221-digit system —
within half a digit of its 24.9-digit entropy ceiling, and with no
coverage penalty over the top-5 run because the larger solution pool
compensates for the looser residue lists.

**Why this does not improve the bounded record games.** A sieved
progression scan generates ~1 850 candidates/s; k-list construction
generates 0.1–100 constructions/s of K = 1 candidates each, i.e.
candidates are 10^1–10^4× more expensive, while E is no lower. In Phi
terms: the record progression scores Phi = 18.20 − log 1 371 832 = 4.07,
an M > B construction scores Phi = E ≥ 18. Joint optimization is the
right tool exactly when the modulus *must* exceed the budget, and it
caps out at the search entropy: reaching 197 digits from the 2 692-digit
Game-1 cover would need ~10^2495 enumerated states (with lists of 10^6
that is 2^415 lists), so compressing that cover is impossible — matching
the uniform-representative estimate 10^(197−2692).

## Prime-gap domination record (2026-07-21): g(N) = 1 134 871

**The certified Goldbach desert exceeds the largest known prime gap with
proven endpoints** (1 113 106, between 18 662-digit primes), while the
ordinary prime gap around this N is just 8 970 — the desert is **126.5×
longer** than the local prime-free interval, so it comes entirely from
covering *prime* offsets, not from an ordinary prime gap.

N has 2 692 digits (6.9× smaller than the certified-gap endpoints); see
`records/megagap_2692digit_g1134871/record.json` (reconstructable as
N = N0 + 14·M from the stored 813-congruence cover).

| quantity | value |
|---|---|
| g(N) — least Goldbach summand | **1 134 871** (= 1.0196 × certified-gap record) |
| digits of N | 2 692 |
| prime offsets q < g proven non-summands | 88 239 |
| — by parity / congruence divisor / trial divisor | 1 / 85 476 / 895 |
| — by strong base-2 witness (unconditional) | 1 867 |
| prev/next prime around N | N−7 329 / N+1 641 (gap 8 970) |
| g(N) ÷ local prime gap | **126.5** |

The complement N − 1 134 871 is certified prime by the PARI/GP ECPP
certificate in `complement_cert.gp` (`primecertisvalid` = 1), and the
253-step certificate is additionally re-verified by the PARI-independent
projective-coordinate checker `ecpp_check.py`, which also asserts the
binding between the certificate's top-level candidate and N − g. The
local-gap endpoints N−7 329 and N+1 641 carry their own validated ECPP
certificates (`localgap_{prev,next}_cert.gp`), and every interior number
of that interval is deterministically composite, so the 8 970 local gap
is fully certified as well. Every negative witness is deterministic.
`verify_megagap.py` re-checks the entire record from the committed
artifacts in one run and writes `MANIFEST.sha256`. Search: E = 6.56
cover found the hit at k = 14. The larger the construction, the *easier*
the search — E = |U|·boost/ln N falls as N grows — so this game
optimizes at a ~2 700-digit N, unlike the digit-frugal bounded games
below.

**Remaining open targets from the challenge**: the absolute-known-gap
milestone g ≥ 16 045 849 (beating the largest PRP-endpoint gap) needs
π(16M) ≈ 1.03M covered offsets → M ≈ 20 000 digits and ~0.2 s/modexp,
i.e. a distributed campaign roughly 100–1000× this 4-core box. The
"1M-desert below 200 digits" bonus is beyond covering methods entirely:
a ≤192-digit modulus leaves ≥20 000 residual primes below 1.1M, giving
success density e^−400; note (log N)²·log log N ≈ 1.3×10⁶ at 200 digits,
so such an N sits at the extremal constant of the conjectured
Granville–van de Lune–te Riele maximal order.


Machinery and results for the two bounded record games defined in *Cute
Goldbach Gaps* (July 2026): for an even N, let g(N) be the least prime p
such that N − p is also prime (the least Goldbach summand).

- **Threshold game** T(100 000): find the *smallest* even N with
  g(N) > 100 000.
- **Budget game** R(10^199): find the *largest* g(N) attainable with
  N < 10^199 (fewer than 200 digits).

The paper's incumbents (both verified here with gmpy2/BPSW before we
started): a 199-digit N with g = 105 667 serving both games, and a
237-digit N with g = 109 621 for the unbounded height game.

## New record (2026-07-21): one integer beats both bounded games

**N** (197 digits, `records/dual_197digit_g107719/record.json`):

```
69391050047962771785886014481525499530404869626881147528776141740954715
09405658481222615550358933673643532753354708616005981520465642550488792
3382772685792448907579623625079335835156550325768132008
```

**g(N) = 107 719**, with the Goldbach partition N = 107 719 + (N − 107 719).

- Budget game: N < 10^199 and g(N) = 107 719 > 105 667 — **new best
  known R(10^199) lower bound**.
- Threshold game: N ≈ 6.94·10^196 < N_199 ≈ 5.83·10^198 with
  g(N) > 100 000 — **new best known T(100 000) upper bound**
  (~84× smaller than the incumbent).

### Proof structure (fully machine-checkable)

Every prime q < 107 719 (10 250 odd primes plus q = 2) has N − q
composite, witnessed in `evidence.json`:

| witness type | count |
|---|---|
| parity (q = 2) | 1 |
| congruence divisor r \| N − q from the 89-congruence cover | 9 471 |
| trial divisor < 10^5 | 378 |
| strong base-2 Miller–Rabin compositeness witness | 400 |

A strong-base-2 failure is an unconditional compositeness proof, so the
negative side is deterministic. The positive side: 107 719 is prime
(64-bit check) and N − 107 719 is proven prime by the PARI/GP ECPP
(Atkin–Morain) certificate in `complement_cert.gp`, validated with
`primecertisvalid` (see `check_cert.log`).

### Construction

N = N0 + k·M with k = 951 928, where M = 2·∏r over an 89-modulus
congruence cover (M has 191 digits) chosen so that every covered prime
q < 105 668 satisfies q ≡ N (mod r) for some cover modulus r | M, giving
N − q ≡ 0 (mod r). The cover was produced by a greedy set-cover pass
plus simulated annealing (`cover.py`, `anneal.py`) minimizing
digits(M)·ln 10 + E, where E = |U|·boost/ln N is the expected number of
prime complements among the |U| = 750 uncovered ("residual") primes —
the negative log of the per-k success density. The search
(`search.py`) scanned 165 independent CRT progressions (residue-swap
variants, `gen_variants.py`) with a small-prime sieve to 6·10^6 followed
by Fermat base-2 filtering, at ~1 850 progression elements/second on 4
cores; ≈1.4·10^8 elements were scanned before the hit, matching the
predicted density e^−18.2. The measured density model (calibrated at
Ê = 16.65 vs predicted 16.43 on a Q = 100 003 cover) was accurate to
~0.2 in E throughout.

### Comparison table

| record | paper incumbent | this work |
|---|---|---|
| T(100 000) upper bound | 5.83·10^198 (199 digits) | **6.94·10^196 (197 digits)** |
| R(10^199) lower bound | 105 667 | **107 719** |

## Reproduction

```
python3 verify_record.py records/dual_197digit_g107719/record.json /tmp/ev.json
gp -q  # read complement_cert.gp; primecertisvalid(...) == 1
```

`search.py` reconstructs N as N0 + k·M from `record.json` (fields N0, M,
k) and re-derives all witnesses; nothing depends on the discovery path.

## Files

- `cover.py` — greedy weighted congruence-cover builder + CRT
- `anneal.py` — simulated-annealing cover refinement
- `gen_variants.py` — independent progression variants from a base cover
- `search.py` — multiprocess sieved progression search (Fermat filter,
  exhaustive BPSW verification of successes)
- `verify_record.py` — per-offset compositeness evidence generator
- `package_record.py` — record dir: evidence + PARI ECPP certificate
- `records/` — the record integers and their proofs
