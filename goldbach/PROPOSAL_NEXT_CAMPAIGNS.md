# Proposal: next Goldbach-gap record campaigns (joint CPU-cover × GPU-fleet plan)

*2026-07-29 — follow-up to the merged records in `goldbach/records/` (GPU
session, PR #24) and `slop/goldbach/records/` (CPU session, PRs #21–#23).*

## Where the two pipelines stand

| capability | CPU session (`slop/goldbach`) | GPU session (`goldbach`) |
|---|---|---|
| cover/residue optimization | GRASP + SA + coordinate descent (`records/work/build_cover.py`); k=741 @ 164-digit modulus for Q=10^5 | greedy + anneal (`cover.py`, `anneal.py`) |
| progression search | numpy presieve + gmpy2 SPRP, ~6×10³ t/s on 4 cores | `gpu/engine150.py` bit-matrix sieve + Montgomery Fermat, ~2.5×10⁶ t/s on a T4; fleet sharding with git-committed `safe_k` checkpoints |
| certification | PARI ECPP + independent pure-Python cert checker + APR-CL + PARI full-scan | PARI ECPP + `ecpp_check.py` |
| current records | g=1,157,341 @ 2,480d (Game 1); g=119,419 @ 199d | **T(10^5) @ 150 digits, g=104,527** |

The 150-digit record shows the search-throughput lever dominates once the
cover is decent: their winning exponent was E≈24.9 (vs ≈20 for the CPU
ceiling), purely because the fleet can afford e^25 progressions. The cover
lever is worth ~1 digit per k-percent-improvement and the CPU annealer is
currently the stronger cover tool. Combine them.

## Campaign A — T(100,000) below 145 digits

Target: even N ≤ ~142 digits with g(N) > 100,000.

- Budget math: at L = ln N ≈ 327 nats (142 digits) with fleet range
  t ≤ 10^12 (ln ≈ 27.6), modulus budget ≈ 299 nats (130 digits),
  base primes to ~310, expected residual k ≈ 740–770 after a hard anneal
  (24 h × 4 cores, multi-seed, pool to 40,000).
  Then p₁·k ≈ 23–25 (φ between 0.60 and the plateau) → E[t] ≈
  1–7×10¹⁰ — days to one fleet-week at round-1 throughput, two at the
  unlucky tail. 145 digits is the conservative fallback (E ≈ 4×10⁹).
- Deliverable per hit: `spec*.json` (cover, N0, M) + banked k, then the
  full dual certification (below).

## Campaign B — R(10^200) above 135,000

Target: N < 10^200 with g(N) > 135,000 (current: 119,419).

- The 10^200 cap makes this *range-bound*, not compute-bound: keep the
  modulus at ≈ 434 nats so t-range ≈ 3×10¹¹, cover primes to
  Q = 135,000–140,000 (π ≈ 12,700), anneal to k ≈ 950 → p₁·k ≈ 22
  → E[t] ≈ 3–5×10⁹, E[hits in range] ≈ 60. Fleet-hours to a day.
- Any hit q > 119,419 is bankable en route (first uncovered PRP
  complement often overshoots Q by thousands).

## Campaign C (stretch) — Game 1 ladder: g(N) > 2,000,000

- Cover primes to 2×10⁶ (π = 148,933) with a ~3,300-digit modulus
  (CPU annealer scales; Game-1 greedy already handled 86,689 targets).
  p₁·k lands ≈ 9–10 even at k ≈ 5,000 because L is huge → only ~10⁴–10⁵
  progressions; but each PRP costs ~(11,000 bits)² — GPU Montgomery at
  this width is ~10⁴ tests/s, still 100× CPU. Search is hours.
- The real cost is certification: ECPP at ~3,300 digits (est. 6–12 h
  PARI) and the pure-Python re-verification (~6 h). One-time, acceptable.
- Rung ladder: 1.5M → 2M, banking each certified rung.

## Shared protocol (what made both sessions' results trustworthy)

1. **Spec handoff**: CPU annealer emits `spec.json` (Q, cover pairs,
   N0, M, k list) — same schema as `gpu/spec150.json`.
2. **Fleet discipline**: `gpu/fleet.py` HARVEST-FIRST loop; `safe_k`
   resume marks and CANDIDATE lines committed to git before anything else
   (survives Colab/container churn — proven across ~10 restarts).
3. **Dual verification, always**: every hit passes BOTH stacks
   independently — (a) `slop/goldbach/records/verify_record.py`
   (stdlib-only: CRT reconstruction, every p < q composite, ECPP chain
   re-verified from scratch) and (b) `goldbach/verify_record.py` +
   `ecpp_check.py`; plus PARI APR-CL as a second algorithm and a PARI
   `ispseudoprime` full scan as a third code path. Publish SHA-256
   manifests and both verifier logs in the record directory.
4. **Records bank**: one directory per record under `goldbach/records/`
   (newer unified layout), README table updated in the same commit.

## Resource asks & risks

- Colab GPU fleet access (as in round 1): 1–2 concurrent T4/A100
  sessions for 1–2 weeks (Campaign A is the long pole).
- This container: 4 CPU cores for annealing + certification; the
  idle-freeze issue is handled by the git-checkpoint protocol, but an
  always-on runner would roughly halve calendar time.
- Risks: Campaign A's E is within 2× of round 1's proven scan volume
  (low risk); Campaign C's ECPP size is the only untested step — mitigate
  by certifying a throwaway ~3,300-digit PRP first before burning fleet
  time.

## Suggested order

B (days, near-certain) → A (the marquee number) → C rungs as fleet
availability allows. Every intermediate improvement is banked and
certified immediately — no all-or-nothing bets.
