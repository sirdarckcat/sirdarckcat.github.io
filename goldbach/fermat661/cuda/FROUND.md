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


## Measured (GPU session, 23 Nov 12:26-12:35Z, RTX PRO 6000, f = 0.985, the same 24 vector windows, slice lines IDENTICAL in every run; `phd/campaign3_gpu/fround/`)

* `--fused-rounds 1` alone (frab.sh, gold-g4b): **0.869 s a batch against 0.940 s (x0.924)**; the second pair of runs 0.874 / 0.942.  `--profile-pool` (both paths print the line): a half-pool of 503,808 members, 36-41 rounds, Fermat kernels 0.34-0.41 s,
  run_pool wall 0.681-0.691 s without, 0.640-0.646 s with: the gap per pool fell from 0.33-0.35 s to 0.24-0.30 s.
* Together with `DEEP_RCTA=8` and 512 generate threads (x0.983 alone, r8f.sh): **0.846 / 0.855 / 0.847 s a batch against 0.949 / 0.948 / 0.947 s on the three RTX cards (-10%)**; both checked on each card (identity, the vector known case, >= 1% faster) and
  deployed 12:30:45-12:31:09Z.  The estimate was 0 to +6%; it was +8.2% (x0.924).
* What it means for the next items: a batch is now ~0.85 s for ~0.95 s of GPU work (Fermat kernels ~0.57 s alone, sieve ~0.38 s alone), so the two share the GPU almost serially (~12% overlap): **a millisecond of either is worth ~0.5% of a batch**.


## Control stream: the round's small kernels above the sieve's priority (opt-in, 23 Nov 15:30Z; CPU-verified, NOT run on a GPU; a hypothesis)

**What the measurement says.**  Beside the sieve a half-pool of 36-41 rounds has a gap (run_pool wall minus Fermat kernels) of **0.24-0.30 s = 6-8 ms a round** with the fused rounds (GPU session, `--profile-pool`).  The same loop alone is expected
at 0.2-0.3 ms a round (not measured for the fused rounds; the unfused loop alone measured 2.2 ms).  The sieve thread's stream has the highest priority and the pool's stream the lowest, so each of a round's ~8 small launches
(`fr_plan`, `cumsum`, `fr_info`, `fr_expand`, `fr_post`, `cumsum`, `fr_compact`, and the host read that waits for them) is queued behind the sieve's grids: a block of a lower-priority kernel starts only when no
higher-priority block is waiting for a slot, which on a GPU kept full by 0.5-0.7 ms sieve launches happens in the tails of those launches.  ~8 chances to wait ~0.7 ms is the 6 ms.  That is a model fitted to one number, not a measurement of the cause.

**The change.**  `run_pool_fused(..., ctl_stream=s)` runs the five kernels, the two scans and the host read of every round on `s`, and only `tester.test` (the Fermat kernel, unchanged) on the caller's current stream.  Events order the two:

```
ctl:  fr_plan, cumsum, fr_info, [host read], fr_expand, record(ev_x)           cur: wait(ev_x), test, record(ev_t)
ctl:  wait(ev_t), fr_post, cumsum, fr_compact                                  (next round)
start: ev_in recorded on cur, waited by ctl (the pool's arrays are complete);  end: ev_f recorded on ctl, waited by cur
```

With `s` above the sieve's priority (`FERMAT_CTL_PRIORITY=-100` = the greatest, and the sieve one level below: `OVERLAP_SIEVE_PRIORITY=-4`; with both at the greatest nothing changes) a bookkeeping block takes the next free slot instead of
waiting for a sieve launch's tail, while the long Fermat kernel stays on the pool's low-priority stream, so the sieve's share of the SMs is unchanged.  Without `ctl_stream` (the default) the code path is the old one, line for line.

**What was checked on the CPU** (`test_fround_cpu.py`, a fake device that records every launch with its stream, every event record / wait and every host read): per-member results, tests computed and rounds identical to the driver's `run_pool`
and to the one-stream mode on 5 pool shapes and a half pool; the launch order of a round is the one above; **every launch happens after the launch issued before it** (through the events and the host read: the two streams form one
chain, so nothing overlaps and no kernel reads a half-written array); the same checker flags 41 launches when the waits are left out, and each of the three essential waits (`ev_in`, `ev_x`, `ev_t`) is caught alone (the fourth, `ev_f`, is redundant:
the host read that ends the loop already follows the last bookkeeping kernel; it is kept so the caller's stream never depends on that argument); both errors raise the same messages with the current stream restored; `profile=True` works.
What it cannot check: CUDA's own semantics (a wait captures the record it was issued after; CuPy's per-stream free lists: every array is allocated on the caller's stream, used on `s` only between events that follow its last use on the caller's stream, and
freed after `ev_f`, so a block is never handed to a stream while another still uses it).

**Run it on a GPU** (the driver patch `search_gpu5_ctlprio.patch` applies after `search_gpu5_fround.patch`; `fround.py` replaced next to `gpu_fermat28.py`):

1. A = production (`--fused-rounds 1`), B = the same with `FERMAT_CTL_PRIORITY=-100 OVERLAP_SIEVE_PRIORITY=-4`, optionally C = `OVERLAP_SIEVE_PRIORITY=-4` alone (the sieve one level lower must not be what changes the batch).
   The slice lines of the 24 windows must be IDENTICAL, the known case 23 (k, q) pairs.  **Run the first window under `timeout`**: a mistake in the ordering would show as a hang or wrong lines.
2. `--profile-pool 1`: the number to read is the gap a half-pool beside the sieve (0.24-0.30 s now).  If the hypothesis is right it falls toward the alone value (tens of ms); if it does not move, the wait is not the queue behind the sieve and the change is dropped.
3. The batch time over >= 50 batches against A.  The gap is partly hidden already (the two halves and the sieve fill each other's idle time), so the batch gain is smaller than the gap: expected 0 to a few %, **not measured**; my last three estimates of this kind were off by 3x-10x.

