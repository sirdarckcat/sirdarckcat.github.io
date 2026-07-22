# Goldbach Desert Records

## Joint representative/coverage optimization (2026-07-22): a 219-digit
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

The 211-digit system (4 lists × 8 moduli × top-5, 14.9 digits
cancelled) is a strictly *better* cover than the record's own (|U| 738
vs 752, E 18.09 vs 18.20) — the seven added moduli cover more residuals
than the block reassignment exposes. The 219-digit system (8 lists ×
8 moduli × top-5, 21.3 digits cancelled, 52 solutions where the
window/entropy calculus predicted ~50) shows the 4-level Wagner tree
delivering its full (d+1)·log10 L budget.

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
certificate in `complement_cert.gp` (`primecertisvalid` = 1); every
negative witness is deterministic. Search: E = 6.56 cover found the hit
at k = 14. The larger the construction, the *easier* the search — E =
|U|·boost/ln N falls as N grows — so this game optimizes at a ~2 700-digit
N, unlike the digit-frugal bounded games below.

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
