# A deeper sieve bound on the GPU: what it would cost, what is built, what is still to be measured

The question (from the research session): the sieve bound is B = 1e6 (2^20). The model of the search says a bound of 2^24 .. 2^28 is worth +30% .. 2x in members a second
**if one mark by a prime above the 2^19-bit tile costs less than ~0.03 ns** (about 0.01 ns: 1.3x at 2^24, 1.6x at 2^28 over the re-tuned 2^20; dead above ~0.05 ns).
The marks per member by primes above 2^20 are k ln(log2 B / 20): 199 at 2^24, 370 at 2^28 for k = 1,093 rows.

## Why the present kernel cannot just be given more primes

`s200g_sieve_sh` visits every (row, prime) pair for every 2^19-member window: pi(B) k / 2^19 visits a member (163 at 1e6, 2,245 at 2^24), each 35 SASS
instructions a warp, 0.005-0.008 ns in the current kernel.  Above the window a pair has a mark in a given window with probability 2^19 / s, so at 2^24 there are 32 visits a mark.

## Layouts

| layout | what a mark costs | verdict |
|---|---|---|
| (a) naive: `atomicAnd` into a global bit matrix of a batch (2^25 members x 1,093 rows = 4.6 GB) | a random 32-byte sector read-modify-write in DRAM: ~0.04-0.08 ns on HBM / GDDR7 cards, ~0.2 on an L4 (`bench_pipes.py` part 3 measures it) | dead |
| (b) bucketed (multi-split by (row, tile)), built here: `gbig_kernels.cuh` | ~38 SASS instructions a mark in total (pass A 7, pass B 10, pair set-up, apply ~15): 0.002 / 0.006 / 0.008 ns at full issue on RTX PRO 6000 / A100 / L4, bin traffic 8 B a mark: 0.005 ns at 1.5-1.8 TB/s, 0.027 on an L4 | estimate 0.005-0.015 ns on the big cards; **measurement pending** (`bench_bigprimes.py`) |
| (c) sorted roots or per-pair next-hit state | one entry a (row, prime): 4.7 GB at 2^24, 63 GB at 2^28 | only for bounds above 2^28 |

Pair visits at batch scale (K = 2^25, one pair visit per batch): rows x pi(B) = 128 a member at 2^26, 475 at 2^28 (0.2-1 ns a member): affordable up to 2^28.

## What is built (all CPU-verified, none of it in production)

* `gbig_kernels.cuh`: `gbig_gen` (a CTA takes PPT x blockDim primes and RG rows; pass A counts the marks of every (row, tile) bin in a shared histogram; one global `atomicAdd` a bin
  reserves room; the capacity is checked once a CTA and, on overflow, the CTA writes nothing and the demand sizes the retry; pass B writes the 19-bit offsets with one shared atomic a
  mark) and `gbig_apply` (a CTA a bin: ones, every entry clears its bit, the tile is written).  `gbig.py`: `BigStage` (capacity retry, events), `make_table`, `primes_between`.
* `test_gbig.py`: identical to a brute-force reference (3 geometries, row groups, the overflow flag); `test_gbig_cpu.py`: the cupy glue and the retry path with cupy replaced by numpy + the emulation.
* `bench_bigprimes.py`: ns a mark for the whole stage with the pass A / pass B / apply split and GB/s: **the number the question needs**.

* `gbatch_kernels.cuh`, `gbatch_cpu.cpp`, `gbatch.py`, `test_gbatch_cpu.py`: the rest of the batch pipeline, **built and CPU-verified end to end**: `s200g_prep_tiles` (a table per tile),
  `s200g_tile` (CTA (row, tile): the small-prime marks, then the (row, tile) bin applied to the same shared bitmap, then the tile written into the batch matrix), and `BatchFeeder`
  (a `GpuFeeder` whose window is a batch of 2^ks_log members: per group of rg rows `gbig_gen` then the tile kernel; count, select, finalize and rows are the GpuFeeder's).  Identical to
  sieve200's CPU Feeder (counts, selected members, rows, statistics) on four geometries: all primes large, none large, mixed, row groups that do not divide the row count, f from 0 to 0.9.

## What would still be needed if the measurement says go

1. Measure it end to end on the three cards (`bench_batch.py`: the whole pipeline at production size, per-phase times) and at the keep fraction the model wants (~1%, not 3%).
2. count over the batch matrix (KLOG = 25: 4,096 CTAs, 64 MB of counts) and select over 1,024 blocks of 2^15 (a 64x better filled GPU than today's 16 CTAs) work unchanged; finalize
   scans ~1M keys in one CTA and rows extraction handles ~1M kept members: the present rows kernel gathers one bit a row at a 64 KB stride (550 MB of L2 traffic per 2^19 members;
   order the kept members by index first, ~6x less), so these two may need work once they are measured at batch scale.
3. The caller (search_gpu5) works on batches instead of 2^19-member windows; overlapping the sieve of batch b+1 with the Fermat rounds of batch b matters more here than today (at ~1% kept the
   sieve is a large share of a batch).
4. An L4 stays at 1e6 (its DRAM is 300 GB/s: the bins would cost ~0.03 ns a mark).

Exactness is not at risk: a deeper sieve only removes rows that have a prime factor, and the same identical-to-CPU tests (`test_gsieve.py` style, B up to 2^15 on small geometries) apply.

## Integration with search_gpu5 (built 2026-11-23, CPU-tested; not run on a GPU)

The GPU session measured (CPU model and `search_gpu5.py --sieve-b` on an RTX PRO 6000) that a deeper bound B is worth a hit mass per Fermat test of x1.41 at 10^7, x1.9 at 10^8, x2.45 at 10^9, but that
`GpuFeeder` charges ~0.08 ns per (prime, row, 2^19-window) pair, so it is a loss today; they put the break-even of a large-prime path at ~1.6 ps a pair-step (primes above 10^6 x rows x windows of 2^19)
and a +40% gain at B = 10^8 at ~0.5 ps.  The bucketed layout above is that path.  My estimate per batch of 2^25 members (64 windows) at B = 10^8, 1,093 rows, RTX PRO 6000 (**unmeasured**):
1.0e10 marks by primes in (10^6, 10^8] (3.7e10 x sum of 1/s) at ~38 SASS instructions (~0.1 s), ~83 GB of bin traffic (~0.1 s), 6e9 pair visits (~5 ms): 0.2-0.4 s, i.e. 0.25-0.5 ps a pair-step
(7.9e11 pair-steps), plus the rows kernel at batch scale (a bit matrix of 4.4 GB read at ~1M kept members x 1,093 rows: ~50 ms if the gather is the sector-bound kind).

What is there:

| file | what |
|---|---|
| `deep_feeder.py` | `DeepSieve(M, cover, B, ks_log=25, ...)`: the prime list and M^-1 mod s of all primes below B made once per M with numpy (5.7M primes at B = 10^8: a few seconds; `search.init_spec` loops in Python and would take minutes), one `BatchFeeder`, one bit matrix for `max_rows` rows; `.feeder(N0, rows)` retargets the feeder at a variant (N0 mod s computed on the GPU); `deep_feeder_for(state, spec, ...)` is search_gpu5's `feeder_for` for it |
| `gpu_sieve.py` | `GpuFeeder(max_rows=)` allocates the bit matrix once for the largest variant; `retarget(N0, U)` points the same feeder at another variant of the same M; `BatchFeeder` inherits both |
| `search_gpu5_deep.patch` | `git apply goldbach/sieve200/cuda/search_gpu5_deep.patch` on `goldbach/phd/campaign3_gpu/search_gpu5.py` (as of 990b23e): options `--deep 1 --deep-split 1000000 --deep-rg 16 --deep-max-rows 1100`; `run_batch`, `run_pool` and the accounting are untouched, because the Window is the same object |
| `test_deep_feeder_cpu.py` | CPU: the numpy tables equal `search.init_spec`'s S and M^-1 mod s; one retargeted feeder over variants A B A C B (different N0 and numbers of rows) is identical to sieve200's CPU Feeder in every window; one DeepSieve per M; a new M (x7) builds a new one; too many rows are refused |

How to run it (all of it needs a GPU run first: `measure_all.sh`, sections 3, 4, 6):

    python3 search_gpu5.py --campaign DIR --deep 1 --klog 25 --slice 33554432 --batch 2 --sieve-b 100000000 --skip-frac F --p-est P --kernel 28 ...

* a window is now 2^25 members, so a slice must be a multiple of 2^25 (`--slice 33554432`, `--klo` and `--kmax` multiples of it) and a batch of two slices is the same 2^26 members as today's 64 slices of 2^20; the pool is
  flushed once a window (about 1M kept members at f = 0.97), so the sieve of a window and its Fermat rounds are serial as they are today.
* `--p-est` only changes the hit-mass statistics, not the selection (the emptiest members of each block of 2^15 are kept by their survivor counts): use the GPU session's calibrated p_B (0.0625 at 10^7, 0.0715 at 10^8).
* GPU memory at B = 10^8, 1,100 rows: bit matrix 4.4 GB, bins ~0.7 GB (`expected_cap`; a bin that overflows makes the stage repeat with the capacity it needs), prime tables ~0.4 GB, counts 64 MB: about 6 GB.  An L4 (24 GB) fits it too,
  though its bin traffic (300 GB/s) makes a gain there unlikely: keep it at B = 10^6 until measured.
* if `window()` fails to allocate, lower `--deep-max-rows` to the largest row count of the campaign.

Not done: the sieve of window w+1 on a second stream beside the Fermat rounds of window w (the same idea as for the 2^19 windows); selection of f and B (the research session's model); the rows kernel's index ordering if
`bench_batch.py` shows the rows phase above ~5% of the window.
