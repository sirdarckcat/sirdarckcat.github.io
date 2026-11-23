# Fused Fermat rounds: the bookkeeping of `run_pool` on the device (23 Nov 2026, 12:15Z; CPU-verified, not yet run on a GPU)

## The loss it targets

`search_gpu5.run_pool` tests a pool of members in rounds: each round picks D rows of every still-active member (D = clamp(target / active, 1, dmax)), runs the Fermat kernel on that flat list of (row, k) pairs,
then updates the members (tests counted, first PRP, success, who stays active).  Everything around the one Fermat kernel is ~100 small cupy kernels (gathers, `cumsum`, `searchsorted`, `scatter_min`, boolean-mask
indexing ...) and ~6 host syncs.  What the GPU session measured of it (`uarch_measure/profile_pool_rtxpro6000.txt`, `plt5_cpu_rtxpro6000.txt`):

* alone on the GPU, one stream: 44 rounds, Fermat kernels 1.277 s, `run_pool` wall 1.375 s: **0.098 s of gap = 2.2 ms a round** (7.1% of the pool);
* two halves in two threads (`--pool-threads 2`) fill each other's gaps: no sieve beside them the flush is 1.358 s for 0.646 + 0.697 = 1.343 s of kernels (0.015 s of gap);
* with the sieve beside them (the a2 pipeline) the flush is 1.583 s for 0.743 + 0.695 = 1.438 s of kernels: **0.145 s of gap, ~0.13 s a batch more than without the sieve (8% of a batch)**: the sieve's grids have the higher stream
  priority, a small kernel of the round queues behind a burst of sieve CTAs, and ~40 dependent small kernels a round are 40 chances to wait.

## What a round is now (`fround_kernels.cuh`, `fround.py`)

`fr_plan` (take = min(remaining, D) a member) -> `cumsum` -> `fr_info` -> **one host read** of 3 ints (active members, error flags, tests) -> `fr_expand` (the Fermat kernel's inputs: a binary search of every test
in the scan gives its member, row and k) -> the Fermat kernel, **unchanged** -> `fr_post` (a thread a member scans its block of flags: ascending-rows check, range check, first PRP, tests counted, first-PRP row, success,
keep) -> `cumsum` -> `fr_compact` (order-preserving).  ~10 launches and one host read a round instead of ~100 and ~6; the arrays are allocated once a pool.

The test lists of every round are those of `run_pool` (D without `rem.max()`: it only caps D when every remaining list is shorter, where `take = min(rem, D)` is the same), so the per-member results, the computed tests and
the number of rounds are identical: `test_fround_cpu.py` runs the driver's `run_pool` VERBATIM (copied from `origin/ccr-8ffe9d7a-4ni11u` @123d93c) and `run_pool_fused` on random pools (6 pool shapes x 5 (target, dmax) settings,
PRP probability 0 to 1, empty and one-row lists, the two halves of a split pool, both errors, a flag above 1 with and without the kernel-28 range check) with the kernels compiled from the same `.cuh` by g++: **ALL IDENTICAL**
(tests counted, PRP flags, successes, first-PRP rows, tests computed, rounds, error messages).  NVRTC compiles the kernels for sm_80 / 89 / 120 (8-40 registers, no spills).

## Run on a GPU

1. Stage `fround.py` and `fround_kernels.cuh` next to `gpu_fermat28.py` (FERMAT28_DIR, /content/f28), apply `search_gpu5_fround.patch` (it applies after `search_gpu5_k29.patch` and `search_gpu5_head.patch` in any order).
2. The same fixed windows with `--fused-rounds 0` and `1`: the slice lines must be IDENTICAL (they are, by construction; this is the check that cupy's `cumsum(out=...)` and the launches behave).
3. `--profile-pool 1` prints the `[profile-pool]` line for both (`[fused rounds]` in the second): the gap per round is the number (2.2 ms alone, expected ~0.2-0.3 ms); then the batch time over >= 50 batches with the a2 pipeline.
   What it can and cannot do: it removes the host time and the exposure of ~90 small kernels a round to the sieve's priority; it does not change the Fermat kernel, so the x1.08 slowdown of the kernels beside the sieve stays.
   Expected: 0 to +6% on the RTX cards (the 0.13 s of sieve-induced gap is the ceiling), ~+2% on L4 / T4 (7% gaps, 5x longer rounds); not measured.
