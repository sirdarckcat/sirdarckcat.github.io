# Goldbach Desert Records

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
