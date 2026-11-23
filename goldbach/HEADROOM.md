# Headroom: where could the search be 2x-5x faster? (uarch session, 23 Nov 2026, 05:30Z)

Question asked: find further performance improvements on GPU, CPU or anything else, aiming for 2x-5x.  This file is the audit.  Short answer: **kernel and algorithm work on the GPUs the fleet has gave
one lever worth having and it is deployed: hiding the sieve beside the Fermat kernel (cross-batch sieve thread + a tuned burst shape), measured on the three RTX PRO 6000s at 1.76 -> 1.543 s a batch (x1.14, over their first ~100 batches; those
cards are ~81% of the fleet's Fermat throughput; the L4s and the T4 gain nothing), about +11% for the fleet; the remaining kernel / algorithm items are 1-4% each (section 4), and at most ~6% more on the RTX cards from re-engineering the Fermat round (more Fermat threads and equal
stream priorities were tried and are worse: plt7).  A real 2x-5x needs more GPUs, which is a money question, not an engineering one; and a 2x-5x of compute buys only +3,300 to +7,700 on the final record,
because the return is logarithmic.**

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

1. **Hide the sieve beside the Fermat kernel: DONE on the RTX PRO 6000s, x1.14 measured in production (1.76 -> 1.543 s a batch), nothing on the L4 / T4.**  Probe (GPU session, 08:04Z): the sieve runs beside the Fermat kernel when its stream has
   the highest priority (Fermat x1.104, sieve x2.89, work rate x1.25; projected batch 1.76 -> 1.45 s); without the priority it gets no SM time.  In the real driver the cross-batch sieve thread (`overlap.Pipeline`,
   `search_gpu5_xbatch2.patch`: `--pipeline 1 --pipeline-depth 2`, production's pool, one flush a batch) gives batches of 1.576 / 1.587 / 1.607 s on gold-g4 / g4b / g4c against 1.76 s, with identical slice lines and
   near-misses, since 08:40-08:42Z.  Two things I got wrong on the way, both found by the GPU session's measurements: (a) a flush per window (v1) costs +0.19 s a batch and leaves little (1.69 s); (b) my "sync-free
   sieve" (no host round trip a row group, thought to free the sieve thread from the GIL) made the overlap WORSE (1.73-1.76 s = none): a flat-out sieve on the highest-priority stream takes the SMs at full speed and the
   Fermat rounds wait, while the old per-group host check makes the sieve arrive in short bursts that the Fermat CTAs fill in between (sieve x2.2, hidden); the production tree keeps the per-group check
   (`GBATCH_SYNC_EVERY=1`, the default again).  Tuning of the sieve's bursts (plt3 / plt4 / plt5, GPU session): a 0.5-1 ms bubble after each row group (`GBATCH_GROUP_DELAY_US`) with 512-thread tile CTAs (`--deep-tile-threads 512`; the
   tile-thread setting had never had any effect before 4f8edff) takes the batch from 1.575 to 1.527 s (-3%), in production since 09:21Z ("a2"); the host's niced CPU share costs nothing (plt5: paused or running, same batch).  In the driver the work rate beside the sieve is x1.165 (Fermat x1.36 / sieve x2.2 while both run, the sieve busy 1.0 s of a 1.58 s batch) against the probe's x1.25: the
   Fermat rounds (many launches, host gaps) lose more than one big launch does; `plt3.sh` tries gentler / shorter / smaller-footprint sieve bursts.  L4 (GPU session, 08:44-08:51Z): batch 10.000 s against 10.054 s; the
   probe's work rate beside the sieve is x1.0-1.10 (Fermat x2.1, sieve x1.9: the two just share the 58 SMs), so the L4s and the T4 stay as they were.  Beside the sieve the Fermat KERNELS slow only x1.08 (plt5 `--profile-pool`: 0.65-0.69 -> 0.70-0.76 s a half-pool, the probe's x1.10); the rest of the loss is gaps between the Fermat kernels of the two halves.  Fleet: +11% (3 RTX x1.14 of ~3.0 of 3.7 RTX-equivalents).  Tried and worse (plt7): 3 / 4 Fermat parts, Fermat streams at the sieve's priority.
2. **More GPUs.**  The fleet is ~3.7 RTX-PRO-6000 equivalents of Fermat throughput (3 RTX + 3 L4 at 0.20 + a T4 at 0.11).  An RTX 5090 is ~0.9 of one, an RTX 4090 ~0.55-0.7 (an estimate from the L4's measured 0.20,
   SM count x clock).  Prices are third-party aggregator figures of Oct-Nov 2026 (live prices move by the hour): RTX 5090 on Vast.ai median ~$0.78 an hour, range $0.49-1.12
   ([ThunderCompute](https://www.thundercompute.com/blog/nvidia-rtx-5090-pricing)); market median $0.72 over 18 providers ([Getdeploying](https://getdeploying.com/reference/cloud-gpu/nvidia-rtx-5090)), $0.50-1.25 with median $0.72
   ([AmCompute](https://www.amcompute.com/gpu-cloud-prices/rtx-5090)); [RunPod](https://www.runpod.io/gpu-models/rtx-5090) $0.69-1.19.  RTX 4090: median on-demand ~$0.48-0.49
   ([Getdeploying](https://getdeploying.com/reference/cloud-gpu/nvidia-rtx-4090), [AmCompute](https://www.amcompute.com/gpu-cloud-prices/rtx-4090)).  Colab's G4 (the RTX PRO 6000): ~8.7 compute units an hour, ~$0.87 - a third-party
   figure ([ThunderCompute](https://thundercompute.com/blog/colab-alternatives-for-cheap-deep-learning-in-2025)); Google's own pricing page did not come up.  So an RTX-equivalent costs ~$0.7-0.9 an hour whichever card is
   rented (the 4090's lower price buys proportionally less multiplier), ~$20 a day: **x2 = +3.7 of them = ~$75 a day, x3 ~$150, x5 ~$300** (2.4 days of campaign: ~$180 / ~$360 / ~$720).  The software
   runs unchanged on any sm_75 / 80 / 86 / 89 / 120 card (NVRTC builds for the device); what a rented box needs is the staging the GPU session already does for Colab.
3. **The return on compute is logarithmic**: raising the target by 1,000 costs 0.21 nats (8.7 more uncovered rows), so x2 compute = +0.69 nats = +3,300 on the expected final record (172,300 -> ~175,600), x5 = +7,700
   (~180,000).  Speed is worth having; it does not change the order of magnitude of the answer.

## 4. Everything else (each 1-4%, none worth a GPU slot alone)

Sizes as of 09:30Z, after the pipeline: the sieve is now hidden, but it still taxes the Fermat rounds (~0.55 s of Fermat per second of sieve WORK, plt3), so a percent of sieve work removed is worth ~0.55% of a batch and a
percent of Fermat work removed is worth 1%.  Fermat side: fused per-round update kernel for the tail rounds (+1%), the 24 doubling shifts as IADD in the Fermat step (+1%), exponent prefix of 9-10 bits instead of
6 (+0.6%), a smaller waste than 3.1% (`--dmax 6` gave nothing: 1.581 against 1.571 s).  Sieve side (each % of its work x 0.55): the unroll-3 variant of the tile kernel (~-22% of its integer instructions: ~+2%), pruned
apply (+1.5%), a deeper sieve for the first 60 rows (it adds sieve work: ~+2% net).  Sieve bursts (plt3): a 1 ms bubble after each row group +1.4%, 512-thread tile CTAs +1.1% (not applied: under the 2% a change needs;
plt4 tries the two together).  L4 / T4: per-GPU-type (B, f) (+1-2% of the fleet's 19%).  Together at most ~x1.08 if all were done; measured so far: `--pool-threads 2` +2.7%, the pipeline + burst shape +14% on the RTX cards.

The Fermat kernel itself has no hot local memory (its 88 B of local memory is the 84-byte exponent array, one load per 32 steps), no shared memory, and is bound by one shared integer pipe (the additive cost model);
anything the sieve issues on that pipe is paid by the Fermat kernel, which is why neither stream priorities nor a sieve that fits in the leftover registers help.
