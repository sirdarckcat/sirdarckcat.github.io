# Approach registry & Pareto frontier — Goldbach gap records session 2026-07-21

## Approach families

| id | family | status | notes |
|----|--------|--------|-------|
| A1 | Transfer from verified ordinary prime gaps | **blocked (resource-strength)** | Needing gap ≥ 1,113,139 puts endpoints at ~18k-digit PRPs with no feasible primality certificates, plus ~10^6 compositeness proofs of 18k-digit numbers. Strictly dominated by A3 for every game here. Reopen only with a fully-verified gap of length > 1.11M at ≤3k digits (none exists). |
| A2 | Complete prime-offset congruence cover (prior paper's method) | dominated | Full cover for Q=10^5 cost 1,020 digits (repo paper); incumbent N* shows partial cover + search reaches 199 digits. Kept as correctness baseline. |
| A3 | Partial cover + CRT progression search (residuals PRP-tested per t) | **active, primary** | Greedy weighted set cover (cost ln r) + GRASP/SA + coordinate descent; then windowed t-search with numpy presieve, fail-fast SPRP, survivor-count ordering. |
| A4 | Weighted set cover via CP-SAT / ILP exact optimization | not started | Escalation path if GRASP stalls above required k. |
| A5 | Lattice / small-CRT-representative search | not needed so far | Would matter for pushing Game 2 far below 199 digits. |
| A6 | GPU/SIMD Montgomery progression search | unavailable | No GPU in container; 4 cores only. |

## Benchmarks measured (this container)

- SPRP (gmpy2): 0.11 ms @199 digits; 16 ms @1200d; 89 ms @2500d.
- PARI primecert (ECPP): 223 s @1200 digits (cert validated); 2400d in progress.
- Cover build (numpy greedy): Q=105,667 → k=743 @ 437.7 nats (88 moduli) in 5 min.
  Q=1,113,137 → k=2,915 @ 5,700 nats (759 moduli) in ~8 min.

## Pareto frontier (target q / #congr / log10 M / residual k / E[t] / status)

| game | target q > | #congr | log10 M | k | p1·k | E[t to hit] | fits range? |
|------|-----------|--------|---------|---|------|-------------|-------------|
| G2/3 | 105,667 | 88+1 | 190.3 | 729 | 17.53 | 4.1e7 | HIT t=299,581,384 q=110,917 CERTIFIED ✓ |
| G1 | 1,113,137 | 759+1 | 2,474.6 | 2,844 | 7.68 | ~2.2e3 | searching (4 workers, ~29 s/tested t) |

## Key design decisions

- Compositeness witnesses: class divisor r (covered p) or failed base-2 strong PRP
  (residual p) — both one-sided proofs; verifier recomputes both deterministically.
- Primality: q by trial division (<2^64); N−q by PARI ECPP certificate,
  re-verified by an independent pure-Python checker (ecpp_verify.py), plus PARI
  APR-CL (isprime flag 2) as an algorithmically distinct second proof.
- Games 2/3 modulus budget 440 nats fixed by: E[hits in t-range to N*] ≥ ~4
  with p1·k ≈ 18; adding/removing one modulus strictly loses (checked both directions).

## Blockers log

- SA without move diversity stalls immediately (k frozen at greedy value) → fixed by
  GRASP-randomized refill + residue kicks (2026-07-21).
- build_cover killed runs lost state → checkpointing added.

## Certified results

- **Games 2+3 (2026-07-22)**: N = 58265...638 (199 digits) < N_*, g(N) = 110,917.
  Package records/g23/record_g23.json (sha256 1b1113...ad65). Verified by:
  standalone verifier (gmpy2 + stdlib modes), PARI full-scan crosscheck
  (10,526 primes, 0 violations), ECPP 30 steps + python re-verify + APR-CL.
  Search cost: 1.66e7 tested t of 3.0e8 range (hit at 99.9% of range).
