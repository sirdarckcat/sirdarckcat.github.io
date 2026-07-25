# Certified Goldbach-gap records — session 2026-07-21/22

For an even N, the least Goldbach summand is
g(N) = min { p prime : N − p prime }. Proving g(N) = q requires
(A) N − p composite for **every** prime p < q, (B) q prime and N − q prime,
(C) exact record inequalities. All three are machine-verified here.

## Game 1 — prime-gap domination: g(N) > 1,113,137   **[SOLVED]**

- **N**: 2,480 digits, `g1/record_g1.json` field `N` (full decimal), also `g1/N_g1.txt`
- **g(N) = q = 1,157,341** (> 1,113,137 benchmark)
- Construction: 760 congruence classes N ≡ b_r (mod r) over prime moduli
  (plus N ≡ 0 mod 2), CRT + progression index t = 14,544.
  Modulus M ≈ 10^2474.6; classes force a proper divisor r | N − p for
  86,689 − 2,844 of the primes p ≤ 1,113,137; the 2,844 residual primes and
  all uncovered primes up to q have complements proven composite by failed
  strong probable-prime tests (one-sided compositeness proofs, reproduced
  deterministically by the verifier).
- q prime: trial division (q < 2^64). N − q prime: PARI/GP `primecert`
  Atkin–Morain ECPP certificate (`g1/record_g1.json` field `ecpp_cert`),
  re-verified by the independent pure-Python checker `ecpp_verify.py`
  (affine EC arithmetic with explicit gcd surfacing, exact
  q > (N^{1/4}+1)^2 bound, chain to < 2^64 closed by deterministic
  Miller–Rabin on the verified base set), **plus** PARI APR-CL
  (`isprime(P, 2)`) as an algorithmically distinct second proof.
- Independent full-scan crosscheck (PARI, separate code path from the
  verifier): all 89,841 primes p ≤ q scanned; 0 violations (27.4 min).

### Game 1 verification status
Standalone verifier: **PASS** (exit 0) — 89,840 primes below q all proven
composite (86,714 by covering divisor, 3,126 by failed SPRP), ECPP chain of
245 steps re-verified from scratch, APR-CL concurs (isprime(P,2)=1, 7,409 s),
PARI independent full scan of all 89,841 primes ≤ q: 0 violations.

## Games 2+3 — threshold-size and digit-budget records   **[SOLVED]**

- **N** (199 digits) =
  `5826514888096346710424101028998025020075881503887142804363529668935257470431091522030267318246838585230530561188277028297971745097373095670026256472852062861864834445540663306089431682760572685412638`
- **N < N_*** (the 199-digit incumbent) and **g(N) = 110,917 > 105,667**,
  improving Game 2 (threshold-size, q > 100,000 at smaller N) and
  Game 3 (digit-budget, R(10^199) ≥ 110,917) simultaneously.
- Construction: 88 congruence classes + parity, t = 299,581,384,
  M ≈ 10^190.3; 795 residual primes below q; same proof standard as Game 1
  (ECPP 30 steps + python re-verification + APR-CL; PARI full scan of all
  10,526 primes ≤ q, 0 violations).

## Reproducing / verifying

Each record is one JSON package. The independent verifier is
`verify_record.py` (Python 3 **stdlib only**; uses gmpy2 only to speed up
if present — same proof path either way):

    python3 verify_record.py g1/record_g1.json
    python3 verify_record.py g23/record_g23.json

It (1) reconstructs N by CRT from the published congruences and t and
compares with the published decimal, (2) enumerates every prime p < q with
its own sieve and proves each complement composite (covering divisor —
checked as a proper divisor — or failed SPRP base 2/3), (3) proves q prime
by trial division, (4) re-verifies the ECPP certificate from scratch and
checks its top integer equals N − q, (5) checks the record inequalities
exactly. Exit code 0 = all checks pass.

Cross-checks (optional, need PARI/GP): `g1/crosscheck_g1.gp`,
`g23/crosscheck_g23.gp` — brute-force scans of every p ≤ q with
`ispseudoprime`, independent of the covering data.

SHA-256 hashes: `g1/SHA256SUMS`, `g23/SHA256SUMS`.

## How the numbers were found

1. **Cover optimization** (`work/build_cover.py`): weighted set cover —
   choose prime moduli r (cost ln r) and residues b_r maximizing the number
   of target primes p ≡ b_r (mod r); lazy greedy by gain/cost, then
   GRASP-randomized ruin-and-recreate with simulated-annealing acceptance,
   coordinate descent on residues, and checkpointing.
2. **Progression search** (`work/tsearch2.py`): N = N0 + t·M; windowed
   numpy presieve over (residual, prime) pairs with incremental int32
   offsets; per window, t values ranked by surviving-complement count and
   only the most promising fraction tested (fail-fast SPRP base 2); on an
   all-composite t, ascending scan of uncovered q > Q for the first
   probable-prime complement.
3. **Certification** (`work/make_cert.py`): PARI ECPP + immediate
   independent re-verification + APR-CL, then package assembly.

Environment: 4-core Linux container, Python 3 + numpy + gmpy2,
PARI/GP 2.15.4. Measured costs: SPRP 0.11 ms @ 199 digits, 89 ms @ 2,480
digits; ECPP 223 s @ 1,200 digits; Game 1 search hit after 443 tested
progressions (expectation ≈ 1,800).

## Honest accounting of proof obligations

- Compositeness of every N − p, p < q: **unconditional** (divisor or SPRP
  failure; both re-derived by the verifier, not trusted from search logs).
- Primality of q: **unconditional** (trial division in verifier).
- Primality of N − q: **unconditional** given the ECPP certificate, which
  is verified end-to-end here by two independent implementations and
  additionally confirmed by APR-CL.
- Goldbach partition exhibited: N = q + (N − q) with both parts proven
  prime — so g(N) is exactly q, not merely ≥ q.

## Ratchet rounds (post-solve improvements)

- **T(100,000) upper bound, round 1**: 193-digit N = 21748...708 with
  g(N) = 102,337 (package `t100k/record_t100k_r1.json`) — verifier PASS,
  ECPP 24 steps + APR-CL, PARI scan 9,802 primes clean.
- **T(100,000) upper bound, round 2**: **186-digit** N = 12868...018 with
  g(N) = 109,357 (package `t100k/record_t100k_r2.json`) — verifier PASS,
  ECPP + python re-verify + APR-CL, PARI scan 10,395 primes clean.
  Round 3 (targeting ~179 digits) in progress.
- **R(10^200) lower bound**: round 1 in progress (Q = 114,000 cover).
