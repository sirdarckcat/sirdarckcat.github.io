# Headroom: where could the search be 2x-5x faster? (uarch session, 23 Nov 2026, 05:30Z)

Question asked: find further performance improvements on GPU, CPU or anything else, aiming for 2x-5x.  This file is the audit.  Short answer: **on the GPUs the fleet has, kernel and
algorithm work can still give about x1.3-1.4 in total (one lever, hiding the sieve under the Fermat kernel, is worth most of it: measured on an RTX PRO 6000 at 08:04Z, projected x1.20 there, being deployed); a real 2x-5x needs more GPUs, which is a
money question, not an engineering one; and a 2x-5x of compute buys only +3,300 to +7,700 on the final record, because the return is logarithmic.**

## 1. Where an RTX PRO 6000 batch goes (2 x 2^25 members, Q = 170,000, 1.76 s)

| part | time | what bounds it | floor / what was tried |
|---|---|---|---|
| Fermat kernels (28M tests) | 1.27 s (72%) | the integer multiplier: 876 IMAD.WIDE x 3.64 + 223 other instructions x 2.79 cycles a warp-step, 4,000 cycles x 655 steps a test (43 ns), measured within 1.1% by an additive model (`fermat661/cuda/FERMAT28.md`) | no fewer multiplications fits the registers (Karatsuba needs the whole 47-column product live: 140+ registers); fermat31 / 30 -33% / -24%; 2 / 4 accumulators -3.5% / -7.9%; more warps +1-3% at best; trimming the 223 other instructions ~+3% of the step |
| sieve (2 windows of 217 ms) | 0.43 s (24%) | tile kernel (primes <= 1e6, ~3.2e10 marks a window, ~3 ps a mark: the shared-memory atomic rate) and the staged large-prime stage (1.1e10 marks, ~9 ps a mark, 91 MB table read from the L2) | deeper bounds lose (B = 2^28 / 1e9: -3% / -31%: marks grow with ln ln B and the table traffic with the number of primes); f = 0.97 is a flat optimum; rcta 8 saves 0.8% |
| host work not hidden | ~0.06 s | the tail rounds of `run_pool`, ~40 cupy launches and 3 syncs each | `--pool-threads 2` recovered half of a 0.10 s gap (+2.7%) |

Time per kept member: 0.87 us = 14 Fermat tests (0.6 us) to find one prime among its ~390 alive rows + 0.2 us of sieve (6.5 ns x 33 members sieved for each one kept).

## 2. What was examined and why it is not a multiple (numbers, not opinions)

* **A cheaper primality test.**  A base-2 Fermat test is 660 modular squarings of 661 bits whatever the shortcut; the first 6 are already free (start value 2^(672-c)); 9-10 are possible (+0.6%).
  The 40 rows of a member are N - q with the same top 640 exponent bits, but the squarings are modulo different numbers: nothing is shared (a product modulus costs 8x more).  No early exit exists for composites.
* **Tensor cores.**  Even at 100% utilisation, INT8 dense (~1 POPS) gives ~3.7e7 tests/s against 2.3e7 now (x1.6), and the recombination of 7-bit pieces into 28-bit limbs costs the ALU work saved.
  The multiplicand of the reduction is the modulus, which is the same for the rows of one member, so a GEMM exists, but its packing / unpacking dominates.  FP32 FMA shares the lanes with INT32 ("unified cores").
* **Tests per hit.**  ~14 tests kill a kept member (1/p with p = 7.15% a surviving row).  Rows are equally likely prime, so no order helps; a cheaper first-pass detector would have to detect >50%
  of the composites for <30% of a test: trial division to 1e9-1e12 costs 3-4 orders of magnitude more (4e8-4e10 primes a row).
* **Deeper sieve.**  The sweep with the staged kernel (GPU session, 03:58Z): hits a second -3% at 2^28 and -31% at 1e9 even though hits per test rise x1.28 at 1e9; pair visits of the primes above 2^25
  (primes x rows) and marks (ln ln B) outgrow the saving.  A lattice enumeration of the marks wins only for primes above ~4.5e9 and there are 2e8-4e10 of them.
* **A deeper sieve for the first rows only** (the rows tested first, by ascending q, carry most of the tests: P(row r is tested) ~ e^(-0.024 r)): B = 1e9 for the lowest ~60 uncovered rows saves ~8% of the tests
  for ~18 ms a window: ~+3.5%.  Not built.
* **Selection.**  Pruning members after the cheap small-prime stage (90% of the final best 3% are in the best 15% after primes <= 1e6) saves only the apply part of the large stage: ~+3%.
* **The cover.**  Each uncovered row removed multiplies the hit probability by 1.024; the 88 moduli use 438 of the 460 nats of 10^200 and the window of 2^25 members needs 17: one more modulus (+7 rows,
  x1.18) at best.  The research session's entropy argument says the 88-modulus plateau is the optimum.
* **CPU.**  A Sapphire Rapids core does ~1e5 Fermat tests/s: 230 cores equal one RTX PRO 6000.  The Colab hosts have ~10 vCPUs: +2-4% per runtime at best.  The CPU pipeline of the contractor session
  (150k members/s) is 0.4% of one RTX.
* **Other GPUs.**  The RTX PRO 6000 is the fastest integer-multiply GPU on offer (188 SMs x 2.43 GHz; H100 0.57x, B200 0.62x, A100 0.33x, L4 0.2x, RTX 5090 0.9x, 4090 0.7x).

## 3. What does give a multiple

1. **Hide the sieve under the Fermat kernel: MEASURED on the RTX PRO 6000 (GPU session, 23 Nov 08:04Z): the sieve runs beside the Fermat kernel (x1.104 on the Fermat kernel, x2.89 on the sieve, x1.25 more work a second) when its stream has the highest
   priority; projected batch 1.76 -> 1.46 s = x1.20; the carve-out, an 80-register kernel and chunked launches do not help (`sieve200/cuda/DEEPSIEVE.md`, last section).**  Inside the real driver (GPU session, 08:16Z, `search_gpu5_xbatch.patch` v1, a flush per window): 1.752 -> 1.647 s a batch (x1.06) with the sieve almost completely hidden (the batch is Fermat-bound: 1.508 s without a sieve
   beside it, +0.14 s with it) but the flush per window costs +0.19 s itself; with production's single flush and the sieve thread a whole batch ahead (`search_gpu5_xbatch2.patch`, `--pipeline 1 --pipeline-depth 2`) the
   projection is ~1.47 s (x1.19), untested.  Not yet a production number: the driver needs the cross-batch sieve thread, because a batch of 2 windows exposes the first sieve and the last Fermat.  The L4 / T4 (sieve ~36% of their batch) should gain more, ~x1.4-1.5
   (`run_overlap_probe.sh` with `VARIANT=s1rw MODE=fleet`); the fleet in all ~ +22-26% (3 RTX x1.20 + 0.7 RTX-equivalents of L4 / T4 x ~1.4).  Before the measurement this was a guess (x1.3 / +33%); the 03:10Z trial
   that seemed to say it does not work had one flush a batch and could not have shown anything.
2. **More GPUs.**  The fleet is ~3.7 RTX-PRO-6000 equivalents of Fermat throughput (3 RTX + 3 L4 at 0.20 + a T4 at 0.11).  An RTX 5090 is 0.9 of one.  Marketplace prices of November 2026: a 5090
   $0.49-1.12 an hour (median ~$0.75), RunPod $0.69-1.19, market median $0.72 over 18 providers; Colab's G4 (the RTX PRO 6000) ~8.7 compute units an hour, ~$0.87.  So an RTX-equivalent costs ~$0.8-0.9
   an hour, ~$20 a day: **x2 = +3.7 of them = ~$75 a day, x3 ~$150, x5 ~$300** (2.4 days of campaign: ~$180 / ~$360 / ~$720).  Consumer cards are the cheapest integer multipliers there are.  The software
   runs unchanged on any sm_75 / 80 / 86 / 89 / 120 card (NVRTC builds for the device); what a rented box needs is the staging the GPU session already does for Colab.
3. **The return on compute is logarithmic**: raising the target by 1,000 costs 0.21 nats (8.7 more uncovered rows), so x2 compute = +0.69 nats = +3,300 on the expected final record (172,300 -> ~175,600), x5 = +7,700
   (~180,000).  Speed is worth having; it does not change the order of magnitude of the answer.

## 4. Everything else (each 1-4%, none worth a GPU slot alone)

fused per-round update kernel for the tail rounds (+1%), the unroll-3 variant of the tile kernel (+2%), the 24 doubling shifts as IADD in the Fermat step (+1%), pruned apply (+3%), a deeper sieve for the
first 60 rows (+3.5%), exponent prefix of 9-10 bits instead of 6 (+0.6%), per-GPU-type (B, f) for the L4 / T4 (+1-2% of the fleet).  Together ~x1.12 if all were done; the first two measurements of this audit
(`--pool-threads 2`: +2.7%; rcta 8: +0.8%) agree with the sizes quoted.
