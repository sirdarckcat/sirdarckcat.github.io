# Goldbach Desert Records

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
