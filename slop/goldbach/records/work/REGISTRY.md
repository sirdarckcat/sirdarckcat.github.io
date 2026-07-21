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
| G2/3 | 105,667 | 88+1 | 190.4 | 743 | 17.86 | 5.7e7 | E[hits<N*]=3.98 ✓ |
| G1 | 1,113,137 | 759+1 | ~2,476 | 2,915 | ~8.0 | ~3e3 | unbounded ✓ |

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
