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

## First GPU numbers (RTX PRO 6000, 2026-11-23; the GPU session's `uarch_measure/`) and what they changed

* **Deployed**: `--deep 1` at B = 10^8 has run on the three RTX PRO 6000s since 01:30Z: a batch of 2^26 members takes 2.10 s against 2.00 s for 1e6 and gives x1.42 expected hits: **x1.32 hits/s**.
  Two bugs the CPU emulation could not catch were found on the first run (a cupy array through `np.asarray`, `Event.elapsed_time`); fixed in f620e9b, and the fake cupy of `test_gpu_sieve_cpu.py` made faithful.
* **The stage costs 0.030 ns a mark** (2^24 .. 2^28: 0.0301 / 0.0314 / 0.0296), 2-6x my estimate: a 2^25 window at B = 1e8 is 373 ms (11.5 ns a member): tile kernel (small primes, as today) ~60,
  `gbig_gen` ~215 (pass A, the visits and counts: 3-14 ms; **pass B, the writes: 136-242 ms = 0.020 ns a mark = 49 G marks/s**), apply ~95 (62-109: **266 GB/s of the device's 1,460**).
* Why (their `bench_pipes.py` part 3): a random 4-byte store into 4 GB runs at 4.4 G/s (a DRAM read-modify-write of a 32-byte sector), into 64 MB (L2-resident) at 136 G/s, 128-byte runs at 325-1,050 G/s.
  The bins of a group are 430-790 MB, so pass B is somewhere between: ~49 G/s.  And the apply is latency bound: one CTA of 256 threads an SM (64 KB of shared memory) with one 4-byte load in flight keeps
  ~190 KB in flight, which at ~1 us is ~200 GB/s.
* Done: `gbig_apply_entries` (f5436df): 16-byte loads, four in flight a thread, all issued before the first atomic (expected ~95 -> ~35 ms a window).
* Being measured: `sweep_bigprimes.sh` (ppt = primes a thread, rg = rows a group, tile = 17 / 18 / 19, CTA size): if the bins of a group fit the 128 MB L2 (rg 2-4) or longer runs (ppt) help, pass B is
  limited by partial-sector traffic; if nothing helps it is the request rate and the next step is a staged pass B (marks sorted by bin in shared memory, flushed as runs; chunks of primes with
  equal expected marks so that a CTA's marks fit the staging buffer).  Each 100 ms a window is ~9% of a production batch.
* The cost of a mark is what limits B: every decade of B adds only ln(ln 10^(k+1) / ln 10^k) of the marks (+25% from 1e8 to 2^28), so a cheaper mark moves the optimum B up almost for free.

## Overlapping the sieve with the Fermat rounds (`overlap.py`, `search_gpu5_overlap.patch`)

A deep batch is 2.10 s = Fermat 1.24 s + sieve stage 0.75 s + 0.1 s; the stage is bound by the memory system, the Fermat kernel by the integer multiplier, so they can share the GPU.
`--overlap 1` runs the sieve of window w + 1 in a thread on a non-blocking stream of the highest priority while the caller tests the pool of window w (one window ahead, results in the same order, the
same numbers).  `git apply goldbach/sieve200/cuda/search_gpu5_overlap.patch` on `search_gpu5.py` as of f43e7f9 (after the deep patch) also adds a cache of the device `N0 - q` arrays (the same variants
come back every batch: ~48 ms of Python a 64-slice batch), `--deep-tile-threads` / `--deep-gen-threads` (CTA sizes) and syncs where an array made on the sieve stream is dropped by the caller.
Upper bound: max(1.24, 0.75) + 0.1 = 1.35 s, x1.55 over the present batch; what it really gives depends on how the two kernels share the SMs: the Fermat CTAs (5 an SM, 128 threads, 92-102 registers)
leave ~4,000 registers an SM, so a 256-thread sieve CTA cannot sit beside them (try `--deep-tile-threads 128`); the high priority lets sieve CTAs take an SM as soon as a Fermat CTA (~1 ms) retires.
`test_overlap_cpu.py` tests the helper (order, run-ahead bound, error propagation, the cache) with a stub cupy.
Memory (T4, 15 GB, ran out after three batches of two slices): the same patch converts a window's survivor rows with an in-place `+= off` (one int32 copy of ~1.5 GB, not two), releases `w.rows`
(u16, ~0.7 GB) as soon as the copies are done, and does not copy a single-window pool in `flush`.  **Order matters (fixed 2026-11-23 03:00Z, after a re-read for races): `w.rows = None` must come AFTER the
`cp.cuda.get_current_stream().synchronize()`**: cupy's pool is per stream, so a block freed while the consumer's `astype` kernel is still reading it goes back to the sieve stream's free list and the sieve
thread may be handed it (and write it) at once; the first version of the patch freed it one line early.
`--fermat-cta-sm N` (same patch) makes room for the sieve without touching the Fermat kernel: the pool's tests are launched in chunks of N CTAs an SM (N x SMs x 128 tests: 3 x 188 x 128 = 72k) instead of
one launch of 8,000+ CTAs, so each SM holds N of the 5 Fermat CTAs that fit and has registers (~28k of 64k at N = 3), threads and shared memory left for a sieve CTA; the chunks are launched back to back
in one stream (the CTAs of a chunk finish together, so the ~5 us launch gaps and the tail cost little).  Try N = 3 and 4 with `--overlap 1 --deep-tile-threads 256` (a 256-thread tile CTA needs ~5k registers).

## The staged generate kernel (`gbig_gen_st`, 2026-11-23; CPU-verified, never run on a GPU)

Pass B of `gbig_gen` is 136-242 ms of the 373 ms window: every mark is its own 4-byte store into one of 1,024 bins of 100-190k entries (430-790 MB, more than the cache): one L2 request a mark.
The staged kernel makes the same bins with whole runs:

* the host cuts the (ascending) prime list into **chunks** with about the same expected marks (a prime s makes 2^25 / s marks a row: `bigchunks.make_chunks`, 0.75 x `stage_cap` / `rcta` marks a row);
* a CTA = (chunk, `rcta` rows): pass A counts its marks by (row, tile) bin in shared memory, a Hillis-Steele scan of the counts gives each bin its place in a **staging buffer** of `stage_cap` words
  (static shared memory, < 48 KB: 8,192 = 34 KB), one global atomic a bin reserves the bin's room as before (same `gcnt` demand counts, same overflow flag and retry), pass B' recomputes the marks and
  writes them SORTED BY BIN into the buffer (a shared atomic a mark), and a warp a bin copies its run to global memory with lane i on word i: whole 128-byte lines, ~8x fewer L2 requests;
* a CTA whose chunk has more than `stage_cap` marks (a statistical outlier) writes them the old way, one store a mark: same result (tested with chunks 3x the buffer);
* the apply / tile kernel is unchanged (bins have the same layout).

SASS (NVRTC 12.9): 26-30 registers, 34.8 KB static shared memory, no spills; the mark loops are 7 (pass A) and 10 (pass B') instructions as before.  Expected: pass B 136-242 -> ~40-60 ms if the L2 request
rate and partial-sector traffic are the limit (a window 373 -> ~230 ms, ~190 with the apply change).  Costs it adds: a shared atomic and a shared store a mark, the scan and 128 global atomics a CTA
(~25k CTAs a group), and the TAB (prime table) is read once per (chunk, row pair) instead of once per 16 rows (~25 GB of L2 reads a window, ~5 ms).

Use: `bench_bigprimes.py --staged 1 --rcta 2 --stage-cap 8192` (the sweep script has a staged section), `bench_batch.py --staged 1`, and in a campaign `DEEP_STAGED=1 DEEP_RCTA=2 DEEP_STAGE_CAP=8192`
in the environment of `search_gpu5.py --deep 1` (`deep_feeder.py` reads them; no new patch).  `--deep-gen-threads` must be at least rcta x 64 and a multiple of 32; 512 threads leave two CTAs an SM busy.
`python3 test_gbig.py` (kernel vs a brute-force reference: normal chunks, chunks 3x the buffer, a partial last row pair, overflow flag), `test_gbig_cpu.py`, `test_gbatch_cpu.py`, `test_bench_batch_cpu.py` cover it.

## What to run next, in this order, and what each answer decides (written 2026-11-23 02:50Z so that it survives anyone's context)

Value first: the Fermat rounds are 1.24 s of the 2.10 s deep batch on an RTX PRO 6000 and the sieve 0.75 s, so the order is overlap (up to x1.55), then the bound B (x1.1-1.3 more once the sieve is hidden), then the rest.

1. **`bench_clock.py`** (5 s; it may run beside production on one RTX: the ticks-per-ns line does not depend on what else runs).  It decides whether every RTX "cycle" of `bench_pipes.py` / `bench_fm28_step.py` is a
   clock64 tick that runs slower than the SM clock: ratio ticks / SM clock = 0.67 explains the whole 1.49x gap of the Fermat step (the model then holds with rho 0.8 and the RTX kernel is at its multiplier floor:
   876 IMAD.WIDE of ~3.8 real cycles; nothing left to find in the step), ratio 1.0 means the gap is inside the real kernel (then `bench_fm28_step.py` E1-E3).  I now expect 1.0: ptxas encodes a stall of 4 for a
   dependent IMAD on sm_120, and a microbenchmark paper on the RTX 5080 (GB203, also sm_120; Section IV-A, Table III: `mad.lo.s32` chains timed with %clock64, "true latency ... four cycles" for INT32 and FP32 on
   both GB203 and GH100) measures exactly 4 ticks for it; the paper never says whether clock64 ticks at the SM clock, so it is consistent with both, but a real latency of 6 SM cycles would be odd.  Against 1.0: the
   RTX variants differ by 1.13-1.30 real cycles for every tick of ALU cost (rho/r > 1 if r = 1).  Five seconds settle it; `bench_fm28_step.py` now prints the same ticks-per-ns (GHz) column at production occupancy.
2. **`--overlap 1` against `--overlap 0` on one RTX** (`search_gpu5_overlap.patch`; same variants, same slices: tests and PRPs must be identical, then the batch time).  Try `--fermat-cta-sm 3` and `4` with
   `--deep-tile-threads 256`.  A batch near 1.35-1.5 s: keep it, and go to 3.  About 2.1 s: the sieve and Fermat CTAs do not share the SMs (look at `--fermat-cta-sm`, `--deep-tile-threads 128`); report both times.
3. **A deeper bound B, once overlap works.**  With the sieve hidden under the Fermat rounds, the best B is the largest whose sieve still fits in them.  Marks a 2^25 window for 1,183 rows (Mertens: rows x 2^25 x ln(ln B / ln 1e6)):
   1.14e10 at B = 1e8 (the stage is ~0.4 s a window now), 1.35e10 at 2^28 (+18%), 1.48e10 at 5e8 (+30%), 1.61e10 at 1e9 (+41%).  The per-(row, prime) visits of the primes above 2^25 (at most one mark a pair)
   cost ~12 instructions a pair: 4.9e10 pairs a window at 1e9 is ~20-40 ms, small.  So the sieve of a 2^26 batch grows from ~0.8 s to ~0.95 s (2^28), ~1.05 s (5e8), ~1.15 s (1e9) against Fermat 1.24 s,
   and hit mass per test rises x1.9 -> x2.45 from 1e8 to 1e9 (the GPU session's CPU model).  `--sieve-b 268435456`, then `500000000`; the first batch builds the prime tables (numpy: ~8 s at 1e8, ~80 s at 1e9,
   about 600 MB of device memory at 1e9).  Compare **expected hits a second** (the log's deep-sieve figure per batch), not tests a second.
4. **`run_experiments.sh`** (A: staged large-prime kernel against the plain one, sweep, B = 2^28 and 2^30 with `bench_bigprimes.py --b 28 / 30`; B: whole batch; C-E: Fermat step experiments, only if step 1 says < 1.0).
   If the overlap hides the sieve completely, the staged kernel only shortens the contention window; if it hides it partly (step 2 between 1.5 and 2.1 s), a faster sieve is worth its percentage directly.
