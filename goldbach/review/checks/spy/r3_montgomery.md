# r3_montgomery: working notes (spy rank 3, "Montgomery squaring bundle")

Verdict: ALREADY DONE (all four sub-ideas are in the deployed kernel or were superseded by something measured faster). Residual gain of the bundle: 0.

Branches read: uarch origin/ccr-b8c25887-i6tn9f, fleet origin/ccr-8ffe9d7a-4ni11u, Lean origin/ccr-36ca7b46-8twf14.

## What is deployed (primary sources)

- Production env of 24 Nov, fleet branch `goldbach/phd/campaign3_gpu/runlogs/2026-11-24/<host>/next_campaign_env`:
  gold-g4d / g4e: `KERNEL=28 K28_STEP=fermat29_step_s1.cuh K28_ASM=1`; gold-l4d / gold-xt4b: `KERNEL=28 K28_STEP=fermat29_step_s1w.cuh K28_ASM=0`.
- `goldbach/fermat661/cuda/fermat29_step_s1.cuh` (uarch): `FM_W 29, FM_NL 23, FM_RB 669, FM_NMAX 665`. Counted by grep:
  253 cross products (d_i x_j, d_i = 2 x_i) + 23 diagonal + 529 reduction (m_i n_j) = 805 wide multiply-adds, plus 23 32-bit multiplies for m_k.
  No compare / subtract / branch inside the step; exponent bit applied by the output funnel shift `sh = 2 - b`.
- `goldbach/fermat661/cuda/fermat28_kernel.cuh`: line 9 "No Montgomery conversion, no R mod n. All values stay below 4n ... a step needs no compare and subtract";
  line 75 `t = bn - 6`; lines 128-134 start value `2^(RB - c)` (one limb set); lines 136-144 the loop is only `fm28_step(x, n, np, b)`;
  lines 155-163 two conditional subtractions (2n, n) AFTER the loop; lines 164-167 compare with 1.
- Lean `GoldbachGaps/Gpu28/Step.lean` + `Kernel.lean`: prove the 24 x 28-bit step (limbs < 2^29, X < 4N, 16N < R -> Y < 4N, no accumulator wraps) and the lane. No statement for the 23 x 29-bit / R = 2^669 step found (grep fermat29 / 669 in Gpu28: empty) - that one rests on CPU tests and gmpy2 comparisons.

## The four sub-ideas

1. Dedicated squaring: DEPLOYED. Since kernel 3 (22 Nov 21:25Z, `gpu_fermat3.py` lines 8-9: 231 products instead of 441), kept in kernel 28 (FERMAT28.md:24) and the 29-bit step (276 of 805).
2. No in-chain subtraction (Walter-type bound): DEPLOYED. Invariant X < 4n with 16n <= R (the doubling for base 2 is folded in, hence 4n / 16n instead of 2n / 4n). FERMAT28.md:32, FERMAT29.md "Range", kernel lines 9, 155-163.
3. "Exact 21 limbs" (21 x 32 bits, 231 + 441 = 672 MACs): MEASURED AND SUPERSEDED. That design is exactly `fermat3`. Same-harness timings (FERMAT28.md:134-138, fleet README:185-190, uarch_measure/t4_test28.txt):
   RTX PRO 6000 fermat3 13.08M tests/s vs 23.39M (24 x 28) vs 24.62M (23 x 29, k29/first_light_rtxpro6000.txt); L4 3.92M vs 4.62M vs 4.73M; T4 2.09-2.12M vs 2.51M (s1rw).
   Reason (UARCH.md:30-32): a 32-bit-limb product needs ~3.5 instructions (carry per product); 28/29-bit limbs make each product ONE IMAD.WIDE into a 64-bit column accumulator.
   Wider reduced radices: 22 x 31 (737) and 23 x 30 (805) built and CPU-verified, need 96-bit column sums; model predicts -33% / -14..-24% on the RTX (FERMAT31.md:1-9, :57) - NEVER TIMED ON A GPU.
4. Cheaper R mod n: DEPLOYED, and stronger: R mod n does not exist any more. FERMAT28.md:35-38: fermat2/3 did 672 modular doublings (~100,000 instructions, ~5% of a test); now start value 2^(R_bits - c), which also makes the first 6 squarings free.

## Recomputing the spy's number

- 903 = 441 + 441 + 21 is `fermat2` (CIOS, per-step compare/subtract, `gpu_fermat.py`), not production since 22 Nov 21:25Z.
- 672 = 231 + 441 is `fermat3`. The step 903 -> 672 was taken and gave x1.48 on the RTX (8.86M -> 13.08M), x1.87 on the L4 (2.18M -> 4.07M), x1.82 on the T4 (1.15M -> 2.09M): more than the spy's x1.15-1.25.
- Then reduced radix: x1.79 more on the RTX (-> 23.39M), then 29-bit limbs x1.057 (-> 24.62M). Deployed kernel / spy's target design = 24.62 / 13.08 = x1.88 (RTX), 4.73 / 3.92 = x1.21 (L4).
- Per test today: RTX PRO 6000 40.6 ns (24.62M/s), L4 211 ns (4.73M/s); T4 ~0.4 us (2.51M/s with the 28-bit s1rw; 29-bit kernel-only not timed there, batch -3.6%).
- Floor: 24.62M tests/s x ~658 steps / 32 lanes / (188 SMs x 4 schedulers) -> ~3,600 cycles a warp-step at 2.426 GHz; 805 x 3.64 = 2,930 (81%) is the wide multiplier. Even deleting every non-multiply instruction gives only x1.23.
- E5 (uarch_measure/e5_ffma_rtxpro6000.txt): an added IMAD.WIDE costs 3.95-4.17 ticks, an IADD3 1.1-1.6, an FFMA 1.16-1.24.

## What the authors list as left in the kernel (HEADROOM.md)

- :52 "no fewer multiplications fits the registers (Karatsuba ... 140+ registers); fermat31 / 30 -33% / -24%; 2 / 4 accumulators -3.5% / -7.9%; more warps +1-3% at best; trimming the 223 other instructions ~+3% of the step".
- :60 exponent prefix of 9-10 bits instead of 6: +0.6% (not done: kernel line 75 still `bn - 6`).
- :121-122 Karatsuba: saves 66-138 IMAD.WIDE, costs 140-280 IADD3-class instructions: a loss (model, not measured).
- :147 the doubling shifts as IADD: +1% (not tried).
- FERMAT28.md:171 "Nothing is left to find in the kernel itself".
- 3b: persistent kernel is -3.4% alone, worse beside the sieve on the RTX; available untested on L4 / T4 (~+0.6% of the fleet).
- Sum of the open items: about +1.5-4% of Fermat kernel time, x ~0.65-0.7 Fermat share of a batch = +1-3% throughput = 0.01-0.03 nats. None of it is the spy's bundle.

## Soft spots in the team's own evidence (not the spy's ideas)

- fermat31 / fermat30 and Karatsuba were rejected by a cost model, not a timing. The same model under-predicted the 29-bit gain (predicted -4.2% cycles, step measured -7.4%, kernel -5.4%) because it over-charges LOP3 / LEA-class instructions. The fermat31 extras are IADD3 / IADD3.X carry chains (the expensive class, 1.1-1.6 ticks measured in E5), so the sign is very likely right: bound = 68 fewer IMAD.WIDE x 4.1 = -280 ticks against +760 instructions x (0.17 .. 1.5) = +130 .. +1,140 ticks -> between +4% and -24% on the kernel.
- `test_gpu_fermat31.py` exists and would settle it in ~1-2 minutes of one paused G4 (~0.3 CU).
- FP64 (DFMA, 52-bit limbs, Emmart-style) does not appear in HEADROOM / UARCH / FERMAT*.md / bench_pipes.py (grep empty); only FP32 was measured. Unknown, not claimed.
