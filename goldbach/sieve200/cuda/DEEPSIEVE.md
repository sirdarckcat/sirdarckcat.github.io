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

1. **`bench_clock.py`, `time_fermat28.py` s2r / s4r, `bench_fm28_step.py` E1-E3 (run 04:07Z; `uarch_measure/run_experiments_FGC_rtxpro6000.txt`): DONE, the Fermat step is at its multiplier floor.**  clock64 counts SM cycles (2.430 GHz;
   a dependent IMAD is 6 cycles); ticks per IMAD.WIDE 4.99 -> 4.57 from 8 to 24 limbs (not instruction fetch), flat from 2 warps a scheduler (6.72 / 4.61 / 4.55 / 4.57 at 1 / 2 / 4 / 5: not latency); s2r -3.5%, s4r -7.9%
   (more accumulators only add adds).  The 1.49x 'gap' of my cost model was a wrong benchmark number (IMAD.WIDE 2.53 on sm_120; the kernel sees 3.64, every other integer instruction 2.79, additive: five variants within
   1.1%, `costmodel.py`), and NVIDIA's table gives extended-precision multiply-add half the 32-bit rate.  Nothing left in the step; E2 (it printed only its baseline: the dummy accumulators cost registers, so fewer CTAs
   fitted and its rows were skipped) and the register-capped s1r_asm_r80 / r72 (+1-3% at best by the occupancy curve) are not worth a GPU slot.  Details: `fermat661/cuda/FERMAT28.md`.
2. **`--overlap 1` against `--overlap 0` on one RTX** (`search_gpu5_overlap.patch`; same variants, same slices: tests and PRPs must be identical, then the batch time).  Try `--fermat-cta-sm 3` and `4` with
   `--deep-tile-threads 256`.  A batch near 1.35-1.5 s: keep it, and go to 3.  About 2.1 s: the sieve and Fermat CTAs do not share the SMs (look at `--fermat-cta-sm`, `--deep-tile-threads 128`); report both times.
3. **A deeper bound B, once overlap works.**  With the sieve hidden under the Fermat rounds, the best B is the largest whose sieve still fits in them.  Marks a 2^25 window for 1,183 rows (Mertens: rows x 2^25 x ln(ln B / ln 1e6)):
   1.14e10 at B = 1e8 (the stage is ~0.4 s a window now), 1.35e10 at 2^28 (+18%), 1.48e10 at 5e8 (+30%), 1.61e10 at 1e9 (+41%).  The per-(row, prime) visits of the primes above 2^25 (at most one mark a pair)
   cost ~12 instructions a pair: 4.9e10 pairs a window at 1e9 is ~20-40 ms, small.  So the sieve of a 2^26 batch grows from ~0.8 s to ~0.95 s (2^28), ~1.05 s (5e8), ~1.15 s (1e9) against Fermat 1.24 s,
   and hit mass per test rises x1.9 -> x2.45 from 1e8 to 1e9 (the GPU session's CPU model).  `--sieve-b 268435456`, then `500000000`; the first batch builds the prime tables (numpy, measured on this container: 8.3 s and 0.5 GB of host RAM at 1e8 (5.76M primes), 92 s and 1.7 GB at 1e9 (50.8M primes);
   ~200 s and ~3.7 GB expected at 2^31 - 1; about 2.2 GB of device memory at 1e9: 28 bytes a prime in the shared tables plus 16 for the large primes).  Compare **expected hits a second** (the log's deep-sieve figure per batch), not tests a second.  Set `--p-est` for the bound: the chance that a surviving row is prime is proportional to ln B (Mertens; it
   reproduces the measured 0.0535 at B = 1e6 -> 0.0715 at 1e8, Q = 60,000 run of the research session), so 0.0715 x ln B / ln 1e8: 0.0804 at 1e9, 0.0834 at 2^31 - 1 (the ceiling: the Shoup setup is 32-bit).
   It does not change which members are selected (the emptiest by survivor count), only the expected-hits accounting.  Each decade of B has been worth less (x1.41, x1.9, x2.45 at 1e7, 1e8, 1e9: +35%, +29%, then
   perhaps +24%), so stop where the marginal sieve time (+2% of a batch from 1e9 to 2^31 - 1, for ~+6% hit mass) stops paying.
   Reading the Fermat probes (G, C): `time_fermat28.py --variant s1r_asm s2r_asm s4r_asm` (section G, ~1 minute): the cost model for a throughput-bound step says s2r -2.5%, s4r -7%; if they are FASTER the step is
   latency bound and the fix is more independent accumulators / more warps (E3 shows the occupancy curve).  E1 (body size): ticks per IMAD.WIDE rising with the loop body means the instruction cache; E2 (extra
   IADD3 / IMAD.WIDE inside the step): the marginal cost of an instruction inside the real step against bench_pipes.py's 1.8 / 2.5 ticks.
4. **`run_experiments.sh`** (A: staged large-prime kernel against the plain one, sweep, B = 2^28 and 2^30 with `bench_bigprimes.py --b 28 / 30`; B: whole batch; C-E: Fermat step experiments, only if step 1 says < 1.0).
   If the overlap hides the sieve completely, the staged kernel only shortens the contention window; if it hides it partly (step 2 between 1.5 and 2.1 s), a faster sieve is worth its percentage directly.

## The overlap trial of 23 Nov 03:10Z (RTX PRO 6000, `uarch_measure/overlap_trial_rtxpro6000.txt`) and what it says

Steady batches of 2 windows (2 x 2^25 members), near-miss driver with its 0.5 s check (a constant in every row), tests and PRPs identical in all: base 2.50 s, `--overlap 1` unchunked (ov0) 2.50, `--fermat-cta-sm 3` (ov3) 2.70,
3 with 128-thread tile CTAs 2.85, `--fermat-cta-sm 4` (ov4) 2.60, staged without overlap (st) 2.20, staged + overlap + 3 (stov3) 2.40; the staged kernel alone gave 2.10 -> 1.70 s once the 0.5 s check was fixed (now in production).

* **The sieve did not run beside Fermat at all.**  With a serialized sieve ov3 and stov3 both imply a chunked-Fermat time of 1.44-1.45 s a batch (1.24 unchunked: +17%; ov4 1.34: +8%); with the overlap they would imply 1.77 and 1.62, which
  cannot both be true.  ov0 should have saved ~0.3 s (the second window's sieve hidden under the first window's Fermat rounds) and saved nothing.  The likeliest cause: NVIDIA's list of things that stop two streams from running
  concurrently includes **a switch between L1 / shared-memory configurations**; the Fermat kernel asks for no shared memory and the sieve CTAs for 64 KB, so the SM is configured for one or the other.  Test: `FERMAT_CARVEOUT=100 DEEP_CARVEOUT=100`
  (c8b5d37), unchunked, with `--batch 4`.  Not yet run.
* **The ceiling is lower than I first wrote.**  The sieve thread is created per batch, so with `--batch 2` the first window's sieve and the last window's Fermat rounds are always exposed: S1 + max(F1, S2) + F2 saves at most S2
  (0.175 s of 1.70 staged: -10%); `--batch 4` hides 3 of 4 sieves (-16%); hiding all of them across batches would take one sieve thread for the whole campaign (not built).  Plain sieve (0.33 s a window) was worth more than staged
  (0.175), so the staged kernel has already taken most of what the overlap could give.
* **The chunked runs are an occupancy curve of the Fermat kernel** (5 CTAs / 20 warps an SM = 1.24 s; 4 = 1.34; 3 = 1.44 a batch of 2 windows; ~4% of the +8% / +17% is launch gaps and the tail of each 3-4 ms chunk): throughput 0.93 / 0.86 of
  the 5-CTA value at 4 / 3 warps a scheduler.  A saturating fit puts the half-saturation point at ~1-1.6 warps and the 5-warp kernel at ~76-82% of its many-warps throughput: a mild latency component (+10% from doubling the
  independent work a warp has, minus the extra adds), not a dependent-chain wall (that would make 3 warps 0.6 of 5).  `time_fermat28.py --variant s1r_asm s2r_asm s4r_asm` (section G) tests it directly; E3 (`bench_fm28_step.py`) draws the curve.

## The sieve-bound sweep with the staged kernel (GPU session, 23 Nov 03:58Z, RTX PRO 6000; `uarch_measure/bsweep_staged_rtxpro6000.txt`) and what my estimate missed

DEEP_STAGED=1, 6 variants x 2^25 members, 3 batches of 2 slices, f = 0.97, `--p-est` scaled by ln B / ln 1e8, tests and PRPs counted:

| B | batch | expected hits a batch | expected hits a second | tests | first batch builds tables |
|---|---|---|---|---|---|
| 1e8 | 1.70 s | 4.4595e-5 | 2.623e-5 | 84.5M | |
| 2^28 | 1.90 s | 4.8317e-5 (x1.083) | 2.543e-5 (-3%) | 80.2M (x0.95) | 12.8 s |
| 1e9 | 2.80 s | 5.0879e-5 (x1.141) | 1.817e-5 (-31%) | 75.1M (x0.89) | 43.1 s |

The selection gains are what the CPU model said (hits a test x1.28 at 1e9) but the stage cost was not: +0.20 s and +1.10 s a batch, against my +0.07 / +0.15 s.  **My estimate counted marks only (cost proportional to
marks, Mertens) and the staged kernel's cost at large B is not in the marks: it is the table.**  A CTA is (chunk of primes, `rcta` rows) and reads its chunk of the large-prime table (16 bytes a prime) in both passes, so the table
is read rows / rcta x 2 times a window: 91 MB at 1e8 (inside the 128 MB L2: free), 233 MB at 2^28 (mostly from HBM), 813 MB at 1e9 (all from HBM: ~2 TB of reads a batch at rcta = 2, ~1.4 s at 1.46 TB/s; measured +1.1 s
including the extra marks and the tests saved).  The plain kernel groups 16 rows a table read, so it would have paid 8x less of this and 3x more per mark.
* `DEEP_RCTA=8` (with `--deep-gen-threads 512`: one thread a bin, rcta x 64 bins; 41 KB of static shared memory at stage 8192, 26-30 registers, no spills; rcta 1-16 are CPU-verified: `test_gbatch_cpu.py --big` gives windows identical to the CPU feeder for rcta 8 and 16 too) divides the table traffic by 4: model +0.08 s (2^28) and +0.35 s (1e9)
  a batch instead of +0.30 / +1.41.  rcta 16 needs `DEEP_STAGE_CAP` <= ~7,000 (49,168 bytes of static shared memory at 8192: 16 bytes over the 48 KB limit) and 1,024 threads.
* With rcta = 8 and the measured selection gains: 2^28 ~ +2.6% expected hits a second (batch ~1.80 s), 1e9 ~ -2.5% (~2.0 s).  **B = 1e8 stays**; the only candidate that could pay is 2^28 with rcta 8 and the gain is inside the noise.
* The bound would only go deeper with a different design for the primes above 2^25 (at most one mark a row and window: a CTA a chunk of primes looping over ALL rows with the row offsets by recurrence,
  p(row j+1) = p(row j) - inv x (q(j+1) - q(j)) mod s, a table of inv x d for the ~100 distinct gaps d, one table read a prime a window instead of rows / rcta; marks appended to the bins with plain atomics: ~7e9 scattered
  marks at 1e9, ~0.15 s a window).  Not built: the measured selection gain (x1.14 at 1e9) does not pay for it.
* Lesson (UARCH.md): a cost model that counts the work (marks) misses the traffic that the algorithm's blocking implies (table re-reads); the second estimate of this stage that was off by a large factor (the first: 3x, the L2 request rate).

## Where the rest of a batch goes: `search_gpu5_roundprof.patch` (optional measurement, 23 Nov 2026-11-23 04:00Z)

On an RTX a 1.70 s staged batch is ~1.1-1.2 s of Fermat kernels, ~0.35 s of sieve and ~0.2-0.25 s that is neither.  Part of that is the GPU idling between Fermat rounds of `run_pool`: each round ends with a host sync (`int(bad)`), a few
more (`act.size` after a boolean-mask compaction, `rem.max()`, `total`) and some 40 small cupy launches before the next Fermat kernel can start, ~2-4 ms, in ~28 rounds a batch (target 2^20 tests a round).  The patch (applies to
d6aed28's `search_gpu5.py`; `--profile-pool 1`, off by default, results unchanged: checked on a numpy fake with identical outputs) brackets each round's `tester.test` with CUDA events and prints per pool
`[profile-pool] N members, R rounds, T tests: Fermat kernels X s on the GPU, run_pool wall Y s, gap Y-X s (..% of run_pool)` and the wall of the whole flush.  If the gap is above ~5% of the batch, the fix is to split a pool's members in
two halves on two streams (two threads) so that one half's kernel runs while the host updates the other: no kernel change, ~1-3% a batch per half-percent of gap recovered; if it is under 3%, drop the idea.
**Built already** (`search_gpu5_poolsplit.patch`, applies on top of the roundprof patch: `--pool-threads 2`, default 1): `run_pool_split` tests a pool's members as two halves in two threads on two long-lived non-blocking
streams (made once: cupy's pool is per stream, a stream per pool would strand its blocks), each half's rounds sized by half the target so that the rows a member gets per round, hence the waste, are those of one pool.  Checked on a numpy
fake: identical counted tests, PRP flags, successes and first-PRP rows for four pool shapes; computed tests equal (109,957 = 109,957), rounds doubled.  The caller's stream is synchronized before the threads start and after the
results are concatenated (the same free-list hazard as the overlap).  GPU timing: unmeasured; the profile line tells whether it is worth running.

## Where things stand, 23 Nov 2026-11-23 04:30Z (RTX PRO 6000 at Q = 170,000, 2 x 2^25 members a batch)

| step | batch | what |
|---|---|---|
| the deep sieve as first deployed (B = 1e8, plain large-prime kernel) | 2.10 s | |
| + apply vectorised, staged large-prime kernel (`DEEP_STAGED=1`) | 1.70-1.80 s | x1.24 hits/s; identical tests and PRPs |
| + `--pool-threads 2` (two halves of a pool on two streams) | 1.808 -> 1.761 s in steady state (-2.6%) | the profile said 0.08-0.10 s idle between rounds; about half is recovered, the rest is the host-bound tail rounds |
| `--overlap 1` (sieve of the next window on its own stream) | no gain (and 4 / 3 CTAs of Fermat per SM cost +8% / +17% of the Fermat time) | likely an L1 / shared-memory split switch; carve-out re-run never done; ceiling ~-10% |
| B = 2^28 / 1e9 | -3% / -31% expected hits a second | the staged kernel reads its 16-byte prime table rows / rcta x 2 times a window; B = 1e8 stays |
| the Fermat step | at its multiplier floor | 3.64 cycles x 876 IMAD.WIDE + 2.79 x 223 other instructions; `FERMAT28.md` |

Time of a 1.76 s batch: Fermat kernels ~1.27 s (72%), sieve ~0.43 s (24%: a 2^25 window at 1,262 rows is 217 ms wall = 193 ms sieve (gen + tiles) + ~24 ms count / select / finalize / rows), host work not hidden ~0.06 s.
Section H (GPU session, 04:32Z, one Q = 170,000 vector, `uarch_measure/secth_rcta_rtxpro6000.txt`): rows a CTA of the staged kernel at B = 1e8, sieve ms a window: rcta 2 193.2 (twice), rcta 4 201.9, rcta 8 with 512 gen threads 186.6:
**the table re-reads are not what limits the stage at 1e8** (rcta 8 saves 6.6 ms a window = 0.8% of a batch); production keeps rcta 2.  What is left, each worth 1-2%: rcta 4 / 8 at the
production bound (`run_experiments.sh` section H), a fused per-round update kernel for the tail rounds, the unroll-3 variant of the tile kernel, 24 doubling shifts as IADD in the Fermat step.  The estimates of the GPU session's
timing granularity (0.1 s steady batches) cannot resolve them; batch-end timestamps over hundreds of batches can.


## The overlap, again: why the first trial proved nothing, and the cross-batch pipeline (23 Nov 05:45Z)

The `--overlap 1` trial of 03:10Z could not have shown an overlap whatever the hardware does: `flush()` runs when `npool >= --pool`, the runs used `--pool 2097152`, and a deep window keeps ~1.008M members, so the pool
(2,015,232 members: the `[profile-pool]` lines show exactly one flush a batch) is only tested by the final `flush()`, after ALL the windows of the batch are sieved; the next batch's sieve (a new `overlapped()` generator)
starts after the last Fermat launch.  Nothing ever ran beside anything; the only information in that table is the cost of chunked Fermat launches.  (My overlap patch assumed a flush per window and I did not check the pool.)

What is needed, in order:
1. **The hardware question** (do the sieve CTAs and the Fermat CTAs share the SMs at all?): `bench_overlap.py` + `run_overlap_probe.sh` (4 minutes on one paused GPU): the real Fermat launch beside real sieve windows in a
   high-priority thread, in five configurations (defaults; `--carveout 100` = FERMAT_CARVEOUT / DEEP_CARVEOUT; an 80-register Fermat kernel leaving 14k registers free; the same without stream priority; chunked launches).
   A projected batch >= x1.15 prints OVERLAP WORKS.
2. **The driver**: `search_gpu5_xbatch.patch` (applies to the GPU session's driver at 45fa78c): `--flush-each-window 1` (test the pool after every window: the Fermat of window i is what the sieve of window i+1 hides
   under) and `--pipeline 1` (`overlap.Pipeline`: ONE sieve thread for the whole campaign; it plans the next batch itself, `select_batch` with a `planned` set, and runs into it while the consumer is still testing the last
   window of the current one; a semaphore bounds it to two windows alive).  Checked on stubs: `test_overlap_cpu.py` (order across batches, at most 2 alive, errors) and `test_xbatch_campaign_fake.py` (the same batches in the
   same order with and without the pipeline, every slice once, the thread 5 windows ahead of a 4-window batch).  Run: `--pipeline 1 --flush-each-window 1 --pool-threads 1|2` (+ FERMAT_CARVEOUT=100 DEEP_CARVEOUT=100 if the probe says so).
   Expected on an RTX if the hardware allows it: 1.76 s -> ~1.35 s a batch (x1.3); with a flush per window but no pipeline ~1.5 s.
3. A flush per window makes two pools a batch, each with its own tail rounds (~20 small rounds): ~+40 ms of Fermat tail, which the sieve of the next window now covers.


## The overlap on the hardware: it works (GPU session, RTX PRO 6000, 23 Nov 08:04-08:05Z, `phd/campaign3_gpu/uarch_measure/overlap_probe_rtxpro6000.txt`)

`run_overlap_probe.sh` (`bench_overlap.py`: the real Fermat launch of 2^26 tests on the default stream, real sieve windows of the production configuration in a thread on a high-priority stream; Q = 170,000 spec, 1,262 rows).
Alone: Fermat 2.832 s (23.7M tests/s), one sieve window 216 ms.

| configuration | Fermat under the sieve | sieve windows meanwhile (slowdown) | same work sequential -> overlapped | projected batch (sequential 1.76 s) |
|---|---|---|---|---|
| defaults (92-register kernel, high-priority sieve stream) | 3.127 s (x1.104) | 5 (x2.89) | 3.913 -> 3.127 s, x1.25 | **1.46 s, x1.20** |
| `--carveout 100` | 3.125 s (x1.103) | 5 (x2.89) | x1.25 | 1.46 s, x1.20 |
| 80-register kernel (`s1r_asm_r80`) + carve-out | 3.102 s (x1.077 of its own 2.880 s) | 3 (x4.80) | x1.14 | 2.12 s, x0.83 |
| the same, sieve stream without priority | 2.881 s (x1.000) | **0** | x1.00 | no overlap |
| `--carveout 100 --cta-sm 4` (chunked, 4 CTAs an SM) | 3.514 s (x1.163 of its own 3.022 s) | 8 (x2.04) | 4.741 -> 3.514 s, x1.35 | 1.64 s, x1.07 (the file's 1.54 is against the chunked launch; see below) |

What it says:
* **The hardware co-schedules the sieve beside five 92-register Fermat CTAs with the default shared-memory carve-out.**  The carve-out hint changes nothing (so an L1 / shared-memory split switch was not what blocked the 03:10Z trial; that
  trial had one flush a batch and could not show anything anyway).  1/1.104 + 1/2.89 = 1.25: while both run, the SM does 1.25 units of "alone" work a second.
* **The stream priority is what makes it work.**  Without it the sieve got NO SM time in 2.9 s: the Fermat CTAs (~1 ms each) are replaced by Fermat CTAs from the same launch before a sieve CTA is considered; with the highest
  priority the block scheduler gives a freed slot to the sieve first.  `overlap.sieve_stream` already creates the stream that way (`cudaStreamCreateWithPriority`, priority -100, clamped to the device's best).
* The 80-register kernel is WORSE for the sieve (x4.8 instead of x2.9): six Fermat CTAs an SM take more warp slots and issue slots from the sieve warps than the room they leave in the register file gives back.  Chunked launches (4 CTAs an SM)
  give the sieve more (x2.0) but cost the Fermat kernel 7% on its own (3.022 vs 2.832 s) and x1.163 on top; charged against the production kernel's one-launch 2.832 s the batch projects to 1.27 x 3.514 / 2.832 + 0.06 = 1.64 s,
  worse than the defaults.  (The probe's own projection divided by the chunked alone time, 1.54 s: fixed in 050d369, `--ref-variant`.)  **Keep the production Fermat launch as it is, with the high-priority sieve stream.**
* The balance is almost exact: a production batch needs 1.27 s of Fermat (x1.104 = 1.40 s) and 0.43 s of sieve (x2.89 = 1.24 s), so the sieve finishes ~0.16 s before the Fermat does: projected batch 1.40 + 0.06 = **1.46 s (x1.20)**.
  The sieve now has ~13% of slack (0.485 s of alone-time a batch against 0.43 s used): a slightly deeper sieve (f, B) may pay once the pipeline runs; the optimum was found in the sequential regime where every sieve second counted in full.
* Why the cross-batch pipeline and not only a flush per window: the in-batch overlap (window i + 1 under the Fermat of window i) leaves the first window's sieve (217 ms) and the last window's Fermat (0.635 s x 1.0) exposed:
  0.217 + max(0.635 x 1.104, 0.217 x 2.89) + 0.635 + 0.06 = 1.61 s (x1.09); the pipeline (`search_gpu5_xbatch.patch`) keeps the sieve thread ahead across batch boundaries and gets the 1.46 s.
* L4 / T4: the sieve is ~36% of their batch, so the same x1.25 of work would give ~x1.4-1.5 there; unmeasured (`VARIANT=s1rw MODE=fleet bash run_overlap_probe.sh`).


## The overlap inside the real driver (GPU session, 23 Nov 08:06-08:17Z; `uarch_measure/overlap_driver_rtxpro6000.txt`, `pipeline_v1_rtxpro6000.txt`)

In-batch overlap (`--overlap 1`, the sieve of window 2 under the Fermat of window 1) needs a flush per window (`--pool 1e6`), which costs +0.14 s a batch by itself (waste 5.7% against 3.1%, a second flush's tail rounds),
and it leaves window 1's sieve and window 2's Fermat exposed: even a perfect overlap gives 1.90 - 0.15 = 1.75 s = production's 1.75.  The measured 1.84 (one vector) / 1.88 (a vector a window) said little either way.

**Pipeline v1** (`search_gpu5_xbatch.patch`: `--pipeline 1 --flush-each-window 1`, one sieve thread for the whole campaign, six batches of two windows, slice lines identical to production):
production 1.752 s a batch; v1 with one Fermat thread 1.801 s; **v1 with two Fermat threads (`--pool-threads 2`) 1.647 s** (mean of batches 3-6; (x1.06) - but its last batch, with no sieve beside it, takes 1.508 s and the batches
with a sieve beside them 1.67-1.70 s, mean 1.69 s: x1.037 against production).  Reading:
* the last batch is the Fermat side alone with a flush per window: 1.508 s against production's one flush of the same members, 1.752 - 0.434 (the sieve) = 1.318 s: **a flush per window costs +0.19 s a batch**
  (the 2.6% extra waste is 0.033 s of it; the rest is two sets of tail rounds and launch gaps);
* a steady batch is 1.69 s = 1.508 + 0.18: the sieve (0.434 s alone) costs the batch only ~0.18 s, which is the Fermat slowdown beside it (x1.12 of 1.508 s; the probe said x1.10): **the sieve is hidden in the real
  driver, as the hardware probe said** - the pipeline is Fermat-bound; what is left to remove is the flush-per-window penalty and the 10-12% Fermat slowdown;
* so run the pipeline with production's pool: **`--pipeline 1 --pipeline-depth 2`** (`--flush-each-window 0`, `--pool 2097152`, `--pool-threads 2`): the consumer takes both windows of batch n, flushes once (1.318 s x1.09), and
  the thread sieves both windows of batch n + 1 under that flush (0.434 s x2.9 = 1.25 s: it fits); no extra flush, no extra waste.  Projected steady batch ~1.318 x 1.12 + 0.03 = **~1.5 s (x1.17)**.  Memory: the held pool
  (2 x 1.6 GB of int32 rows) + 2 windows waiting (2 x 0.8 GB of u16 rows); `search_gpu5_xbatch2.patch` (applies to the unpatched driver at 10210fc) adds `--pipeline-depth` and `--trace-pipeline 1` (per batch: seconds the
  consumer waited for the sieve = sieve time not hidden; seconds the sieve thread was busy / waited for the consumer; `overlap.Pipeline.take_stats`).

**A host round trip a row group (my code, found while reading why the in-batch runs hid so little).**  `BigStage.gen_group` read the bin-overflow flag `gcnt[NBINS]` with `int(...)` after EVERY row group: ~80 blocking
round trips a window (1,262 rows / rg 16), each leaving the sieve stream idle until the host relaunched and, in a driver whose main thread is busy in `run_pool`, needing the GIL back.  The probe has them too but its main
thread sleeps in one launch.  Now: `gen_group(defer=flag)` ORs the flag into a device word (one tiny kernel) and returns at once; `BatchFeeder.window` reads it ONCE after the window (which ends with host reads anyway) and, if it is
set (a bin overflowed: practically never once the capacity is right), repeats the window the old way, group by group.  The tile kernel applies NO bin of an overflowed group (`gcnt[NBINS] != 0`: the entries are incomplete and some
slots were never written, and an entry is a bit index read blindly), so nothing stale is read before the repeat.  `GBATCH_DEFER_CHECK=0` restores the per-group check.  CPU emulation (`test_gbatch_defer_cpu.py`, three geometries
incl. staged): identical windows with the deferred check, no wait in a window, a forced overflow (capacity 32) repeats the window once and gives the per-group result, and the unrepeated attempt is wrong with the flag set (the
test is not vacuous); `test_gbatch_cpu.py --big` unchanged.  NVRTC sm_120: s200g_tile 384 -> 392 instructions, 40 registers, no spills.  Expected: a few ms a window when alone (bubbles), more beside the Fermat kernel; unmeasured.


## Correction (23 Nov 08:57Z): the per-group host round trip is what makes the overlap work; what is deployed; what is next

GPU session, `uarch_measure/pipeline_v2_rtxpro6000.txt` (campaign mode, 6 batches, slice lines identical in every run): production 1.744 s; the pipeline of `search_gpu5_xbatch2.patch` with my sync-free sieve (`h`) 1.73-1.76 s
for the batches that have a sieve beside them, the sieve thread busy 0.44 s a batch (= alone) and the consumer never waiting: **no gain**; the same with the per-group overflow check (`j`) 1.55-1.60 s, the sieve busy
0.94-1.05 s a batch (x2.2) and idle 0.5-0.9 s.  The 08:20Z reading above (the in-batch overlap hides little because the main thread holds the GIL) and the sync-free window were WRONG: with the priority, a flat-out sieve's pending
CTAs take every SM slot a Fermat CTA frees (~1 ms a CTA), so the sieve runs at full speed and the Fermat rounds wait; the blocking check after each row group makes the sieve's work arrive in ~80 short bursts a window with
gaps in which the Fermat CTAs refill the SMs, which is the co-residency of the probe.  In production on the three RTX PRO 6000s since 08:40-08:42Z: the patched driver, `--pipeline 1 --pipeline-depth 2 --trace-pipeline 1
--pool-threads 2`, `GBATCH_DEFER_CHECK=0`: 1.576 / 1.587 / 1.607 s a batch against 1.76 s.  The tree now defaults to that (`GBATCH_SYNC_EVERY=1`); `GBATCH_SYNC_EVERY=0` is the deferred-only mode, N >= 2 checks every N-th
group (`test_gbatch_defer_cpu.py` covers all three).

Accounting (RTX, driver): Fermat-only flush 1.31 s (production 1.744 - sieve 0.434), pipeline batch 1.58 s: Fermat loses 0.27 s while the sieve (0.434 s of work) takes ~1.0 s of wall time, so while both run the Fermat
rounds go at 0.735 and the sieve at 0.43 of their solo speed (work rate 1.165); the probe's single big Fermat launch lost 0.12 s for the same sieve (work rate 1.25).  If the driver reached the probe's rate the batch
would be ~1.46 s (another -7%).  The loss per second of overlap is not proportional to the sieve's intensity (the driver's sieve is only 1.2x as intense as the probe's and costs 2.4x as much per second): bursts
that displace Fermat CTAs, and each Fermat round's launch queueing behind sieve CTAs of a higher priority, are the likely causes.

L4 (08:44-08:51Z): batch 10.000 s against 10.054 s with the pipeline; probe (Fermat s1rw): Fermat x2.117 beside the sieve, sieve x1.91, work rate x1.0-1.10; reverted; the T4 is not worth a slot.  (The probe's batch
projection printed 13.55 s there because it took max(Fermat x slowdown, sieve x slowdown), which is wrong when the sieve finishes first; corrected to the sieve's wall time plus the Fermat work left, which gives 10.04 s,
the measured batch.)

Two more findings while reading the driver: (1) **`BatchFeeder.tile_threads` was never used**: the tile kernel was always launched with `sieve_threads` = `nthreads` = 256, so every `--deep-tile-threads` /
`bench_batch.py --tile-threads` sweep ran the same kernel; fixed (the default stays 256); (2) the tile kernel is 40 registers x 256 threads = 10,240 registers, and 5 resident Fermat CTAs (92 registers x 128
threads = 12,288 each) leave 4,096 free: a sieve CTA can only run by taking the slot of a retiring Fermat CTA, which is why the stream priority is needed at all (without it the sieve got NO SM time).

**Next (`plt3.sh`, one script, ~5 minutes on one paused RTX; none of it is verified on hardware):** (a) throttle variants of the burst structure (a bubble after each checked group `GBATCH_GROUP_DELAY_US`, checks every 2nd /
4th group, row groups of 4 / 8 rows); (b) real 128 / 512-thread tile CTAs; (c) **a sieve that fits beside the Fermat CTAs**: `DEEP_TILE_MAXREG=32` (`__launch_bounds__(128, 16)` on the tile kernel: no spills, NVRTC sm_120; the staged
generate kernel is 26 registers) with 128-thread CTAs needs 4,096 registers a CTA = exactly what 5 Fermat CTAs leave, so it never displaces one; with the Fermat streams above the sieve's
(`FERMAT_STREAM_PRIORITY=high` + `OVERLAP_SIEVE_PRIORITY=0`, `search_gpu5_prio.patch`) the Fermat rounds would never queue behind the sieve and the sieve would take only what the Fermat CTAs leave plus the gaps and
tails; the sieve's solo speed with 128 threads is lower, so it may become the bottleneck (its slack is ~0.5 s a batch); (d) `--dmax 6` (the waste of 3.1%).


## plt3 (GPU session, 23 Nov 09:03-09:07Z, `uarch_measure/plt3_burst_rtxpro6000.txt`): shaping the sieve's bursts buys at most 1.4%; the fitted sieve is destructive

RTX PRO 6000, 6 batches of 2 windows (slice lines identical in all 15 runs), mean of the batches that have a sieve beside them: base (no pipeline) 1.755 s; j0 / j1 (production pipeline, a host check after every row group)
1.571 / 1.568; **d1** (`GBATCH_GROUP_DELAY_US=1000`: a 1 ms bubble after every group) 1.548 (sieve busy 1.35-1.48 s, idle 0.05-0.16: nearly sieve-bound); d2 (2.5 ms) 1.629 (the sieve falls behind); s2 / s4 (check every
2nd / 4th group) 1.575 / 1.580; r4 / r8 (4 / 8-row groups) 1.646 / 1.565; **tt512** (tile CTAs of 512 threads: the first time a tile-thread count was really tested) 1.553 (busy 0.83-1.10); tt128 1.639; dm6 1.581;
fA / fB / fC (the sieve in the 4,096 registers the Fermat CTAs leave: `DEEP_TILE_MAXREG=32`, 128-thread tile and gen CTAs) 1.969 / 1.736 / 1.784.  Nothing beats production by the 2% a change needs; the RTX cards keep j.

What it says about the 0.25 s a batch that the Fermat rounds lose beside the sieve (the probe's single big Fermat launch lost 0.12 s for the same sieve):
* the loss follows the sieve's WORK, not its intensity: j0 loses 0.26 s with the sieve running at x2.2 (busy 1.0 s), d1 0.24 s with it at x3.2 (busy 1.4 s): ~0.55 s of Fermat per second of sieve work (the probe: 0.28);
* **the loss is not CTA displacement**: the fitted sieve CTAs (4,096 registers, one per SM beside 5 Fermat CTAs, nothing displaced, Fermat streams at the higher priority in fA) are the WORST case: in fA the sieve finished in
  0.70 s (x1.6, flat out) and the batch took 1.97 s, longer than sequential (1.755): the Fermat rounds nearly stopped while it ran.  Whatever the sieve takes from the Fermat kernel is a resource that priorities do not
  arbitrate: the warp issue slots / pipes, or the MIO / LSU queue (the sieve's shared-memory atomics against the Fermat kernel's 88 B of local memory per thread, which is LDL / STL through the same pipe);
* so the two things that were tried to make room (register fit, stream priorities) cannot help; what is left is a gentler or cheaper sieve (d1 / tt512 / both: 1-2.5%) or finding out whether the Fermat rounds lose GPU time
  (kernels slower) or host time (the gaps between rounds longer: GIL / CPU contention with the sieve thread): `plt4.sh` (pb / pj: `--profile-pool` with and without the pipeline, a `top -H` snapshot, `nproc`).


## plt4 / plt5 (GPU session, 23 Nov 09:13-09:19Z): a2 deployed (1.527 s); the Fermat kernels slow x1.08 beside the sieve and the rest of the loss is gaps; the host is not the cause

plt4 (`uarch_measure/plt4_rtxpro6000.txt`): j0 1.576 s; **a1** (1 ms bubble after each row group + 512-thread tile CTAs) 1.518; **a2** (0.5 ms) 1.526; a4 (1 ms, 1024 threads) 1.537; a6 (512 threads alone) 1.546; a3 (1.5 ms) 1.554 (the
sieve falls behind in some batches); a5 (+ 8-row groups) 1.679 (sieve-bound).  plt5 (`plt5_cpu_rtxpro6000.txt`): the host is 48 vCPUs at load 36-40, 90% of it niced (4 drivers x 11-12 `search_c.py` at nice 5), and pausing that CPU share changes
nothing (j0 1.580 running / 1.586 paused, a2 1.529 / 1.529): **my GIL / CPU-contention explanation (and plt6.sh) is moot.**  The `--profile-pool` lines (per half-pool of 1,007,616 members, 44-45 rounds): without the pipeline the
Fermat kernels take 0.65-0.69 s on the GPU, the run_pool wall is 1.33 s (the halves' gaps are filled by each other's kernels: the GPU is ~busy), the flush 1.34 s; beside the sieve the kernels take 0.70-0.76 s (**x1.08**: GPU sharing, the
probe's x1.10), the wall 1.54 s and the flush 1.58 s (against 1.36 s in the batches with no sieve beside them): of the 0.23 s the flush loses, ~0.11 s is the slower kernels and ~0.12 s is gaps, GPU idle between the Fermat kernels
of the two halves, which is where the sieve's higher stream priority hurts the ~40 small kernels (gathers, cumsum, searchsorted, scatter_min ...) of each round.  Deployed on the three RTX PRO 6000s since 09:20-09:21Z:
`GBATCH_GROUP_DELAY_US=500 --deep-tile-threads 512` with the pipeline: **1.526-1.529 s a batch against 1.744-1.76 s at the start: x1.15.**
Next (`plt7.sh`, `search_gpu5_poolsplitn.patch`): 3 or 4 Fermat parts (`--pool-threads 3 / 4`) so a Fermat kernel is in flight more of the time; Fermat streams at the sieve's priority (`FERMAT_STREAM_PRIORITY=high`) so the small kernels
do not queue behind the sieve.


## plt7 (GPU session, 23 Nov 09:26-09:28Z, `uarch_measure/plt7_rtxpro6000.txt`): more Fermat threads and equal stream priorities are worse; a2 stays

Mean of the batches with a sieve beside them (slice lines identical): a2 (deployed) 1.554 / 1.532 s in two runs; 3 parts (`--pool-threads 3`) 1.591; 4 parts 1.671 (the sieve busy 1.23-1.41 s: it slows down as more Fermat kernels
are in flight and the batch grows with it); Fermat streams at the sieve's priority (`FERMAT_STREAM_PRIORITY=high`) 1.651 with 2 parts (the sieve busy 1.6-1.8 s, idle 0, the consumer waiting), 1.696 with 3.  Nothing beats the control,
so production stays on a2: the three RTX PRO 6000s run 1.543 s a batch over their first ~100 batches (1.76 s this morning: **x1.14**).  What would still be left on the RTX, by the accounting above: the probe says 1.45 s is
reachable if the driver lost no more than the probe does (Fermat kernels x1.08-1.10 beside the sieve, no gaps), i.e. at most ~6% more, for a re-engineering of the Fermat round (a fused per-round update kernel in place of its
~100 small cupy kernels and ~6 host syncs, so that the sieve's priority cannot delay them) and of the sieve's instruction count (the sieve taxes the Fermat kernels in proportion to its work).  Not started.


## The deep head (23 Nov 2026, 11:45Z; CPU-verified, not yet run on a GPU): the primes in (1e8, 1e9] on the first 64 rows, applied AFTER the selection

**Idea.**  A member's alive rows (no factor below B = 1e8) are tested in ascending q until the first probable prime, so the first rows carry most of the Fermat tests: a row of index i is reached with probability ~exp(-0.0228 i),
the first 64 rows take ~74% of all tests and the first ~100 rows ~86-90%.  An alive row has a prime factor in (1e8, 1e9] with probability 1 - ln B / ln B2 = 11.1% (those rows are composite and their Fermat test is wasted).
A full sieve to 1e9 would cost ~10x the present one (46.8M primes against 5.4M, 1,248 rows); sieving **only the first 64 rows by those primes, only after the count / select / finalize**, costs a visit of 46.8M x 64 pairs and
~1.3e8 marks (a prime above 2^24 marks a row at most once a window) per 2^24 window: **8.4-8.6% of the Fermat tests disappear for ~7-15 ms of GPU time a window** (headcost: 15.4 ms at rcta 8 for the two-pass
stage; the single-pass kernel here skips the counting pass: ~9 ms expected, to be measured).  Net at the vector mode's numbers (a batch = 4 windows, 1.2 s of Fermat tests in 1.575 s, a ms of sieve work costs ~0.55 ms of a batch):
**+4-6% of a batch**, ~86% of the fleet's output.

**What does NOT change.**  The count, the selection of the emptiest 3%, `alive_total`, `hm_all`, `hm_kept` stay those of the B = 1e8 sieve (the head runs after them), so the kept members are the same, every member's first-PRP
row, its success flag and its near-misses are the same as without the head (only COMPOSITE rows leave a list: a row the head removes has a prime factor and could never have been the first PRP; a success needs all rows composite,
head-removed ones included), and the members are statistically the members of the production run.  What changes: `cnt` (the list lengths) get shorter, the Window keeps the old counts as `cnt_acc`.

**Kernels** (`ghead_kernels.cuh`, `ghead.py`; `HeadStage`):
* `ghead_gen` - a thread takes HEAD_PPT = 4 primes, reads each one's table entry ONCE ({s, M^-1, Shoup constant, c0 of the window}, made by the existing `s200g_prep` for the head's primes) and visits all rows of the group
  (q values in shared memory): `a = q M^-1 mod s` by Shoup's trick, `j = a + s - c0` mod s; a mark (`j < 2^24`) is appended to the bin of (row, tile): `slot = atomicAdd(&gcnt[bin], 1)`, `bins[bin * cap + slot] = j & TILE_MASK`;
  a slot >= cap sets the overflow flag `gcnt[NBINS]` (not written: the host repeats the head with `cap` grown to the demand; marks are idempotent).  No counting pass and no staging: the marks are rare (17% of the pairs at 1e8, 1.7% at 1e9).
* `ghead_apply` - a CTA a (row, tile) reads its 64 KB tile of the bit matrix into shared memory, clears the marked bits with `atomicAnd`, and **counts a bit that was still set for its member** (`slot_of[k] >= 0`: a kept member) with
  `atomicAdd(&dcnt[slot], 1)`: the new `cnt = cnt - dcnt` (a bit cleared by two head primes counts once).  The tile is written back; the CSR offsets are recomputed with a cumsum; the `rows` kernel then writes the shortened lists.
* Memory: 46.8M primes x 40 B (s, M^-1, Shoup constant, mu, N0 mod s, a 16-byte table) = 1.87 GB of device memory, bins 1,024 x 65k x 4 B = 0.27 MB x 1000 = ~270 MB; host: a numpy sieve to 1e9 once (~1 minute, ~1 GB).
  `retarget(N0)` (a vector's N0 mod s for 46.8M primes) and `s200g_prep` (the window's c0) cost ~1 ms together a window.

**The expected-hit accounting** (the one thing the driver must change; `search_gpu5_head.patch`).  The driver estimates p^ = PRPs / tests and sums `(1 - p^)^count` over the members for "expected hits" and the near-miss
expectation.  With the head the tests on the head rows have a higher rate (a surviving head row is prime with p / (1 - c), c = the fraction of head rows removed) and the counts are shorter, so the naive estimate is wrong by 10x
(`test_head_accounting.py`: 0.09x).  The patch measures c per flush (`removed / (removed + head rows left)`) and uses p_mod = all PRPs / (tests on the head rows / (1 - c) + tests past them) with the PRE-head count `cnt_acc` as the
exponent (and `cb + (cnt_acc - cnt)` for the near-miss expectation): +0.40% hits and +0.39% near-miss against the production accounting on a 400,000-member simulation with the same random draws, where the first-PRP rows,
successes and PRP flags are identical and the tests fall 8.40%.  `p^` of the status line (`phat`) is computed from the tests past the head rows only (= P(prime | alive on the B sieve), what it is without a head).

**Tests (all CPU, `sieve200/cuda`)**: `test_ghead_cpu.py` - the head on the CPU emulation of the batch kernels against a numpy brute force (a head prime divides N0 - q + k M) for 3 geometries x 2 windows (staged / plain
large-prime stage, rcta 2 / 4, rg 3 / 4 / 8, tile 2^11 / 2^12): kept members, `alive_total`, `hm_all`, `hm_kept` identical with and without the head, `cnt_acc` = the old `cnt`, `cnt` / `offs` / `rows` = the brute-force lists, CSR
consistent, non-vacuous (removed rows > 0), a bin capacity far too small (overflow, repeat) gives the same window, a second call gives the same window; and through `DeepSieve(head_b, head_rows)` over the variants A B A C B and
`deep_feeder_for` passing the arguments through; `test_head_accounting.py` - the accounting above; `test_headcheck_cpu.py` - the GPU script `headcheck.py` itself on the CPU emulation (it must print HEADCHECK-OK for a correct head and fail for a damaged one); the earlier regression suites (`test_gbatch_cpu.py`, `test_gbatch_defer_cpu.py`, `test_gpu_sieve_cpu.py`,
`test_deep_feeder_cpu.py`) are unchanged by the hooks (ALL IDENTICAL).

**What to run on a GPU, in this order** (the gate the GPU session set: first-PRP rows, successes and near-misses identical to production on the same windows; logged expected values within ~1%):
1. `python3 headcheck.py /content/m89_8.json --rg 32 --rcta 8` (one RTX; ~1 minute of table building, then a window without and with the head on the first 200-digit k of the vector): checks (1) kept members and statistics identical,
   `cnt_acc` = the old `cnt`, the new lists are subsets of the old ones and only rows < 64 leave; (2) the fraction removed (11.1% expected) and the predicted fall of the tests (~8.4%); (3) sampled removed rows really have a
   prime factor in (1e8, 1e9] and sampled kept head rows none (Python integers); (4) the cost of the head in ms.  Prints `HEADCHECK-OK`.
2. The same fixed windows in the driver with and without the head: `search_gpu5.py ... --deep --deep-head-b 1000000000 --deep-head-rows 64 --dump-members /tmp/head` against the base run `--dump-members /tmp/base`
   (apply `search_gpu5_head.patch`; it applies together with `search_gpu5_k29.patch`, not after the persistent-kernel patch), then `python3 compare_dumps.py /tmp/base /tmp/head`: **`DUMPS-IDENTICAL`** (per member sid / k / first-PRP
   row / success) and the counted tests ~8.4% lower.  Compare the logged expected hits and the near-miss expectation (`--log-near-exp`) of the two runs: within ~1%.
3. A batch time with and without it over ~50 batches (a2 pipeline, `DEEP_RCTA=8`, `--deep-gen-threads 512` if wcost3 says so): the gain is the number that decides; below +2% it is not worth the 1.9 GB.
Not for the L4 / T4 / A100 (overlap gave nothing there; 16-24 GB cards would also pay 1.9 GB).


### First GPU results of the deep head (GPU session, gold-g4c RTX PRO 6000, 23 Nov 11:59-12:03Z, `phd/campaign3_gpu/head/headv_rtxpro6000.txt`)

`headcheck.py` (window of 2^24 from k0 = 2,137,898, 1,248 rows, 64 head rows, 45,086,079 primes in (1e8, 1e9]: tables 34 s, 1,720 MB of device memory): kept members, `alive_total`, `hm_all` and `hm_kept` identical with and without the head; **11.11% of the 9,892,086
head rows of the kept members removed (the model says 11.11%)**; predicted fall of the Fermat tests 8.43%; sampled removed rows have a factor in (1e8, 1e9], sampled kept rows none; **a window 136.1 ms without the head, 147.6 ms with it: the head costs 11.5 ms**
(my guess was 7-15; the two-pass staged prototype of headcost.sh was 15.4 ms at rcta 8).  Then the 24 test vector windows through the production driver, the base run (`--dump-members`) and the head run: production / base slice lines identical (24 / 24),
**per-member dumps identical for 12,091,392 members (`compare_dumps.py`: DUMPS-IDENTICAL) with 8.42% fewer counted tests (169,381,475 -> 155,111,986)**, logged expected hits and near-misses x0.9998.  Deployed on gold-g4c at 12:06:49Z for a production A/B
against gold-g4 / gold-g4b.  Expected: 8.42% of ~1.15 s of Fermat kernel time a batch = -97 ms, minus 4 x 11.5 ms of sieve work x ~0.55 = +25 ms: ~-4.5% a batch.


## Where the 88 ms of a vector window go, and three opt-in experiments on the tile kernel (23 Nov 2026, 12:55Z; CPU-verified, not yet timed)

**What is known.**  A 2^24 window (1,248 rows, B = 1e8) takes 88.5 ms of "sieve (gen + tiles)", 99.5 ms with count / select / finalize / rows (bench_batch, wcost2/3).  The GPU session's `bench_pipes.py` on the RTX PRO 6000 (12:26Z):
a random `ATOMS.AND` costs ~2.7 cycles a warp-op an SM (the same as a random `STS.32` / `LDS.32`), i.e. ~12 marks a clock an SM; every integer op (IADD3, LOP3, SHF, IMAD.U32) ~2 scheduler cycles a warp-op (16 lanes a clock a scheduler);
a 128-byte-run store 325-1,050 G words/s, a copy of 1 GB 1,460 GB/s.  The tile kernel makes ~1.7e10 marks a window and does ~0.8 marks a clock an SM: **15x below the atomic unit and ~15x below the integer pipes' rate** (3-10 ms each from the counts),
so neither the atomics nor the arithmetic limits it.  **`bench_split.py` (GPU session, gold-g4c, 12:34Z, `uarch_measure/bench_split_rtxpro6000.txt`) took the window apart (ms a 2^24 window, rg 32, rcta 2 / rcta 8 with 512 generate threads):**

| piece | rcta 2 | rcta 8 |
|---|---|---|
| gen (`gbig_gen_st`) | 54.5 | 49.6 |
|   pass A (visits + counting) | 22.8 | 15.6 |
|   pass B (visits again, stage, flush) | 31.8 | 34.1 |
| tile kernel | 32.9 | 33.0 |
|   small-prime marks (78,408 primes) | 14.6 | 14.6 |
|   **bin apply** | **19.9** | 19.9 |
|   init + write of the tiles | 1.7 | 1.8 |
| gen + tile | 87.4 | 82.6 |

and at rg 8 / rg 4: gen 60.8 / 69.6, tile 43.2 / 27.7, **bin apply 25.9 / 9.7**.  So **the large-prime stage (gen + apply = 74 of 87 ms) is bound by the DRAM traffic of its bins, not by arithmetic or atomics**: the 6.0e9 marks a window
(150k a (row, tile) bin, 4 bytes each) are written (24 GB) and read back (24 GB); the apply reads them at 1.2 TB/s (the DRAM rate) and takes half the time (9.7 ms) when the bins of a group are small enough to sit in the L2 (rg 4), where the generate
passes grow with the number of groups (more table re-reads and launches) and rg 32 stays cheapest.  The small-prime marks (the kernel the opt-in experiments below aim at) are 14.6 ms.  **The lever is bytes a mark: packed bins (5 marks of 19 bits in 3 words,
2.4 bytes a mark, -40%) below.**  **Three experiments, all opt-in (the default build of every kernel is byte-identical to production), all CPU-verified identical to the CPU feeder (`test_gbatch_cpu.py` with the variable set):**
* `DEEP_TILE_UNROLL=2|4` (`TILE_UNROLL` in `gbatch_kernels.cuh`): a thread sets up 2 / 4 primes at once - their 16-byte table entries loaded together, their Shoup chains computed together (independent chains instead of one) - and then runs their mark loops one
  after the other.  Same marks, same bits.  SASS (sm_120): 392 -> 416 / 496 instructions, still 40 registers.
* `DEEP_TILE_PREFETCH=N` (`TILE_PREFETCH_KB`): at kernel start every thread issues `prefetch.global.L2` (`CCTL.E.PF2`) for the first N KB of this CTA's bin, which the apply reads ~100 us later, after the marks; the DRAM read overlaps the atomics.
* `DEEP_TILE_LOG=18` (read by `DeepSieve`; `bench_split.py --tile 18`): tiles of 2^18 bits = 32 KB of shared memory: 3 tile CTAs an SM (48 warps) instead of 1 (16), twice the tiles (more table traffic and visits), bins half the size.
Decision rule: a variant is worth a deployment test if the TILE KERNEL line of `bench_split.py` falls by >= 8 ms a window (~0.5% of a batch a millisecond at the present batch of ~0.85 s: the sieve and the Fermat kernels now share the GPU almost serially).
If the large-prime stage is DRAM-bound, the next step is fewer bytes a mark (3 marks of 21 bits in a u64: -33%), not more occupancy.


## Packed bins (23 Nov 2026, 13:00Z; CPU-verified, opt-in `DEEP_BIN_PACK=1`, not yet timed on a GPU)

**Why.**  bench_split (above): the large-prime stage is bound by the DRAM traffic of its bins - 6.0e9 marks a 2^24 window, 4 bytes each, written by `gbig_gen_st` (24 GB) and read by the tile kernel's apply (24 GB, 19.9 ms = 1.2 TB/s; 9.7 ms when
the bins sit in the L2).  A mark is a 19-bit offset in a 2^19-bit tile: 4 bytes is 13 bits of waste.

**What.**  Five marks of 19 bits in three 32-bit words (95 of 96 bits, 2.4 bytes a mark, **-40% bytes**): `w0 = m0 | m1 << 19`, `w1 = m1 >> 13 | m2 << 6 | m3 << 25`, `w2 = m3 >> 7 | m4 << 12`.  `gcnt[bin]` and `cap` count WORDS
(whole groups of 3).  In `gbig_gen_st`: pass A and the scan are unchanged (marks per bin), a bin's room is `3 ceil(c / 5)` words, the flush has a lane a group of 5 marks read them from the staging buffer (sorted by bin) and write the 3 words (the last
group repeats the bin's last mark: clearing a bit twice is harmless, so no sentinel); a chunk with more marks than the staging buffer (the fallback) writes each mark as a group of five copies (3 words a mark; its room is reserved that way).
The apply (`gbig_apply_entries`, used by the tile kernel and `gbig_apply`) takes a group a step (three word loads, `GBIG_APPLY_UNROLL` groups in flight) and clears 5 bits.  The capacity is `0.6 x (marks cap) + 3 x chunks` words
(`expected_cap(..., pack=True, nchunks=...)`; bins buffer 40% smaller).  Instruction counts (sm_120): `gbig_gen_st` 488 -> 504 (28 registers), `s200g_tile` 392 -> 520 (40), `gbig_apply` 328 -> 464, no spills.  **The default build (BIN_PACK 0) of the whole
module is SASS-identical to the committed one.**

**Verification (CPU).**  `DEEP_BIN_PACK=1 python3 test_gbatch_cpu.py` (every staged geometry, 3 windows each: identical to sieve200's CPU feeder), `DEEP_BIN_PACK=1 test_gbatch_defer_cpu.py`, `DEEP_STAGED=1 DEEP_BIN_PACK=1 test_deep_feeder_cpu.py`, and `test_gbig_cpu.py`:
packed staged bins against numpy, the packed capacity retry (cap 8 -> 256), and the stage-overflow fallback with chunks made 4x too coarse (packed and unpacked).

**To run on a GPU.**  Same fixed windows with and without `DEEP_BIN_PACK=1` (and `DEEP_STAGED=1`, rcta 8, 512 generate threads as in production): the slice lines must be IDENTICAL; `bench_split.py` shows the gen / apply split
(expected: bin apply 19.9 -> ~12 ms, gen pass B 31.8 -> ~22 ms; estimate -13 ms a window, ~-6% of a batch), `bench_bigprimes.py --staged 1 --pack 1 ...` the stage alone with its bytes.
**(Measured by the GPU session, 23 Nov 13:13Z, `splitab.sh`: pass B 34.1 -> 32.9, bin apply 19.6 -> 15.9, small-prime marks 14.3 -> 16.3: -1.2 - 3.7 + 2.0 ms, against the -13 ms estimated above.  The estimate assumed pass B was bound by the bin writes; it is not: see "Where the generate kernel's issue slots go" below.)**


### The visit loops of `gbig_gen_st`, hoisted (opt-in `DEEP_GEN_HOIST=1`, `DEEP_GEN_UNROLL=2|4`; same hour; CPU-verified, not yet timed)

Pass A (22.8 ms a window at rcta 2, 15.6 at rcta 8) is largely bound by the integer pipes (bench_pipes: every integer op takes ~2 scheduler cycles a warp-op, 64 lane-ops a clock an SM): 7.1e9 visits, ~24 instructions a visit in the SASS (no mark), of which
the loop-invariant ones were not hoisted because `blockDim.x` is not known to be a multiple of RCTA: the item's row (`it & (RCTA - 1)`), its `q = U[row0 + r0 + rr]` (a global load a visit), the validity test and the table address
(`TAB + p_lo + (it >> RCTA_LOG)`: two LDCs and an IMAD.WIDE).  With `GEN_HOIST` a thread keeps its row, its q and steps a pointer into the table by blockDim.x / RCTA primes outside the loops: **24 -> 17 instructions a visit in pass A,
~26 -> 20 in pass B** (SASS, sm_120), the same (prime, row) items in the same order a thread, so the same marks.  `GEN_UNROLL = 2 | 4` additionally sets up that many primes a thread at once (their table entries loaded together, their Shoup
chains computed together, then their mark loops one after the other): 568 / 712 instructions, 34 / 40 registers, no spills.  Estimate: pass A 22.8 -> ~17 ms, pass B -2 ms if the loops stay issue-bound.
CPU: `DEEP_GEN_HOIST=1` with and without `DEEP_BIN_PACK=1`, and `DEEP_GEN_UNROLL=2 | 4`, through `test_gbig_cpu.py` and `test_gbatch_cpu.py`: identical to numpy / to the CPU feeder.  The default build of the whole module stays SASS-identical to the committed one.

`splitab.sh SPEC` runs `bench_split.py` under every opt-in variant of this tree (base, pack, hoist, pack + hoist, unroll 2 / 4, prefetch, the combinations) and prints one line each: gen (pass A / B), the tile kernel (small marks, bin apply), the window's sieve phase.


## splitab results (GPU session, gold-g4c RTX PRO 6000, 23 Nov 13:12:54-13:13:48Z, campaign paused, `uarch_measure/`), and where the generate kernel's issue slots go (13:30Z)

ms a 2^24 window (rg 32, rcta 8, 512 generate / 512 tile threads), gen (pass A / pass B), tile kernel (small-prime marks / bin apply), bench_batch's sieve phase:

| variant | gen | tile | sieve phase |
|---|---|---|---|
| base | 49.67 (15.58 / 34.09) | 32.60 (14.31 / 19.59) | 83.7 |
| `DEEP_BIN_PACK=1` | 48.53 (15.68 / 32.85) | 28.91 (16.33 / 15.89) | 78.1 |
| `DEEP_GEN_HOIST=1` | 47.27 (14.30 / 32.97) | 32.74 (14.44 / 19.74) | 81.2 |
| PACK + HOIST | 45.80 (14.34 / 31.46) | 28.90 (16.32 / 15.88) | 75.3 |
| `DEEP_TILE_UNROLL=2` | 49.70 | 29.54 (11.24 / 16.39) | 80.5 |
| `DEEP_TILE_UNROLL=4` | 49.73 | 25.98 (7.68 / 14.17) | 76.9 |
| `DEEP_TILE_PREFETCH=256` | 49.68 | 31.98 (13.69 / 18.93) | 83.9 |
| PACK + HOIST + UNROLL=4 | 45.80 (14.35 / 31.45) | 22.87 (10.28 / 11.03) | 70.3 |
| + PREFETCH=256 | 45.80 | 20.85 (8.16 / 9.02) | 69.3 |

-14.4 ms a window (-17%) with all four.  What the table says: `TILE_UNROLL=4` is the biggest single item (small-prime marks 14.3 -> 7.7, and the apply falls too: 19.6 -> 14.2); PACK and UNROLL compound on the apply (9.0 ms = 14.4 GB at 1.6 TB/s: the apply is
DRAM-bound again, at the device's rate); HOIST saves 2.4 ms of the generate kernel (of the ~3.5 the instruction counts promised); **PACK saves only 1.2 ms of pass B** although it writes 40% fewer bytes.  I had estimated -13 ms for PACK: wrong by 10x, because I
treated pass B as bound by its DRAM writes.  The generate kernel, 45.8 ms of the remaining 69, is not.

### Where the generate kernel's issue slots go (`gbig_gen_st`, hoisted, sm_120 SASS and the real prime list)

Dynamic warp instructions of one CTA (a chunk of primes x 8 rows), from the SASS loop bodies (`sass.py --loops`) and the trip counts of a simulation over the real prime list (primes in (1e6, 1e8], `make_chunks(S, 24, 768)`, random roots):
6,284 chunks x 4 row slices x 39 groups = **981k CTAs a window**; a CTA has 905 primes = 7,242 (prime, row) items = 6,139 marks; its warps run 227 visit iterations (lanes all busy) and 333 mark steps (58% of the lanes busy: the marks of a visit are 0, 1 or a few).

| phase of a CTA | instructions in the loop (SASS) | warp instructions a CTA |
|---|---|---|
| pass A: visits (table load, Shoup, 2 conditional subtracts, loop) | 20 a iteration | 4.5k |
| pass A: marks (`atomicAdd(&cnt[...])`) | 7 a step | 2.3k |
| pass B: visits | 27 a iteration | 6.1k |
| pass B: marks (`stage[atomicAdd(&cur[...])] = ...`) | 9 a step | 3.0k |
| scan (16 barriers), reservation (one global atomic a bin), zeroing | | ~1.5k |
| **flush: a warp a bin, runs of ~23 words** | **76 a bin plain, 80 packed** (64-bit address set-up, alignment peeling, ragged tail: ~8 of them move data) | **19.5k plain, 20.5k packed** |
| total | | **37k plain, 38k packed** = 36-37 G warp instructions a window |

At 188 SMs x 4 schedulers, integer ops at 1 warp instruction every 2 cycles (bench_pipes), ~2.4 GHz: 9e11 warp instructions a second, so **36 G instructions = 40 ms against the measured 45.8 ms** (packed + hoisted): the generate kernel is within 15% of the integer pipes' issue limit,
and **more than half of its instructions are the flush** (a lane a word, ~23 words a run, so lanes mostly idle).  That also explains the PACK result: the packed flush costs +1k warp instructions a CTA (+5% of the kernel) and the 40% fewer bytes were not what the kernel waited for.
(Pass A alone: 9.2 ms from the model against 14.35 measured, 64%: latency and the table's DRAM stream take the rest.)

### Two opt-in changes that follow (CPU-verified, not yet timed): `DEEP_GEN_FLUSH2=1` and `DEEP_GEN_ORDER=1`

**`GEN_FLUSH2` (flat flush).**  The staged word carries its bin: `stage[i] = (bin << TILE_LOG) | offset`, which is just `j + row * KS`, the loop variable of the item's marks (so the mark loops get SHORTER: 7 -> 6 and 9 -> 8 instructions, no `& TILE_MASK`, no
`rbt +`).  The scan leaves one word a bin, `dlt[b] = (word index of the bin's run in bins) - (its index in the staging buffer)`, and the flush is ONE flat loop, a thread a word: `bins[i + dlt[stage[i] >> TILE_LOG]] = stage[i] & TILE_MASK`
(`FLUSH_UNROLL` = 4 words a thread in flight).  Packed: each run is padded to a multiple of 5 marks IN THE STAGING BUFFER (copies of its last mark, one thread a bin after pass B), so a group of 5 never straddles two bins and a thread takes a group:
5 words in, 3 out, at `3 g + dlt[b]`.  The words of a bin, its demand `gcnt` and its padding are exactly those of the warp-a-bin flush (same capacity formula, same retry protocol, same fallback for a chunk over the buffer).  SASS (sm_120): the flush loop is
**50 instructions for 4 words a thread (12.5 a warp-iteration of 32 words) plain, 189 for 4 groups packed, a CTA's flush ~2.4k / ~3.2k instead of 19.5k / 20.5k**; a CTA's total ~18.5k (-50%); 32 / 40 registers, 37.9 KB shared memory (`dlt` adds 1 KB).

**`GEN_ORDER` (grid order).**  `gbig_gen_st`'s grid is (chunks, row slices) and every slice of a chunk reads the chunk's slice of the prime table (16 bytes a prime, 92 MB at B = 1e8): with the slice index as the slow dimension the table streams once a SLICE,
4 x 39 x 92 MB = **14.4 GB a window**, and the L2 (128 MB, with the bins streaming through it) keeps none of it until the next slice (pass A 14.35 ms = 14.4 GB at 1.0 TB/s: suspiciously close to the DRAM rate).  With the grid (slices, chunks) the 4 slices of a chunk
run together and the second to fourth read the chunk's table slice from the L2: **3.6 GB a window**.  Same marks, same bins (as sets).  Pass A shows it; if pass A does not move, it was the integer pipes after all.

**CPU.**  `test_gbig.py` (every staged geometry x {plain, hoist, hoist + unroll 2 | 4} x {flat flush, order}: bit matrix and bin demands identical to the brute-force reference, with the stage-overflow fallback and the capacity retry), `test_gbig_cpu.py` with `DEEP_GEN_FLUSH2=1` /
`DEEP_GEN_ORDER=1` / everything, plain and packed, and `test_gbatch_cpu.py` (identical to sieve200's CPU feeder) with FLUSH2 + ORDER, with PACK + HOIST + UNROLL 4 + FLUSH2 + ORDER, and with each of FLUSH2 and PACK + FLUSH2.  The default build is unchanged.

**Estimate (from the model; my last one was off by 10x, read it as an upper bound).**  Gen at ~18-20 G warp instructions instead of 36: ~22-25 ms of issue time against 45.8 measured; the DRAM floor of gen (table 14.4 GB + packed bins 14.4 GB = 24 ms at 1.2 TB/s;
15 ms with ORDER) is then the next wall, so the realistic expectation is gen 45.8 -> 25-30 ms, i.e. **-15 to -20 ms a window (-20 to -29% of the 69 ms; ~-7 to -10% of a batch)** on top of the four options already measured.
**To run:** `splitab.sh SPEC` (the new rows: `DEEP_GEN_FLUSH2=1`, `DEEP_GEN_ORDER=1`, HOIST + FLUSH2, PACK + HOIST + FLUSH2, + ORDER, ALL).  Read pass B for FLUSH2 (31.5 -> ?), pass A for ORDER (14.35 -> ?); then the driver gate as for the other options (identical slice lines
on the same windows, the known case, the batch time).


### Measured (GPU session, gold-g4c, 23 Nov 13:42-13:48Z, `uarch_measure/` / `sievepack/splitab6_rtxpro6000.txt`, `flushab.sh`): flat flush -4.9 ms, grid order -0.8 ms; the model above was wrong by 3x

ms a 2^24 window, gen (pass A / pass B), then the sieve phase of bench_batch:

| variant | gen | sieve phase |
|---|---|---|
| PACK + HOIST | 45.91 (14.31 / 31.60) | 75.1 |
| `DEEP_GEN_FLUSH2=1` alone | 45.35 (15.67 / 29.69) against base 49.67 (15.58 / 34.09) | 79.2 against 83.7 |
| HOIST + FLUSH2 | 43.07 (14.53 / 28.54) against HOIST 47.26 | 77.1 |
| PACK + HOIST + FLUSH2 | 42.34 (14.48 / 27.86) | 72.2 |
| + `DEEP_GEN_ORDER=1` | 40.32 (13.67 / 26.65) | 70.9 |
| all six + TILE_UNROLL=4 + PREFETCH=256 | 40.33 (13.76 / 26.57) | 63.5 (production's four options: 67.7) |

The driver gate (flushab.sh, 24 windows, identical slice lines, known case) on gold-g4c: batch 0.784 s against 0.811 s (x0.967), deployed 13:48Z.  **I estimated gen 45.8 -> 25-30 ms; it went to 40.3.**  The instruction count of pass B fell by 50% (28.6k -> 10.5k warp
instructions a CTA) and its time by 15%.  What that says, with the same model (981k CTAs a window, 2 CTAs an SM, integer ops 2 cycles a warp instruction, ~2.4 GHz - all assumed, not measured): before the flat flush pass B ran at ~98% of the integer pipes' issue rate (28.6k instructions x 2 CTAs
over 29k cycles = 1.97 a clock an SM, the peak is 2.0), after it at ~43%, and pass A at ~67%.  So the generate kernel was issue-bound only while the flush was in it; now **it waits**: a warp runs 14-28 visit iterations a pass (227 a CTA over 8-16 warps), each one starts with a 16-byte table load
(L2 ~300 cycles, DRAM ~600) and then ~25 instructions (~50 cycles of issue), and the SM has 4-8 warps a scheduler.  An SM sustains ~W x 50 / (50 + latency) of the issue peak with W warps a scheduler: 8 x 50 / 400 = 100%, 8 x 50 / 700 = 57%: the observed 43-67% is that.  The same reasoning
explains the tile kernel: its small-prime loop has the same load-then-compute chain per prime and `TILE_UNROLL=4` (4 loads in flight) took it from 14.3 to 7.7 ms for +27% instructions.  And it explains why `GEN_UNROLL=4` did nothing for the generate kernel: its set-up code cost +27% instructions a visit
(28 against 22: 4 x 4 dummy MOVs and 4 compares for the guarded loads), exactly what the latency hiding won back.

**Clamped loads (this commit).**  The unrolled visit loops now load `TAB[p_lo + min(pi, np - 1)]` unconditionally (an entry past the chunk is a valid address, its marks are masked by the `j = limS` select as before) instead of `if (pi < np) load else dummy`: **23-24 instructions a visit at unroll 1, 2, 4 and 8** (SASS, sm_120, FLUSH2 build: A loop 116 instructions for 4 visits and 4 mark loops,
235 for 8; registers 32 / 29 / 38 / 43, no spills).  Same marks, same bits (`test_gbig.py` now runs unroll 8 too).  **To run: `genab.sh SPEC`** (unroll 1 / 2 / 4 / 8; CTAs of 256 threads with a 6144- and 4096-word staging buffer = 3 and 4 CTAs an SM; rcta 16): one line each, gen with its passes A and B, on top of the six options in production.
What would confirm the latency reading: gen falling with the unroll depth at constant instruction count, and with the CTAs an SM.  What would refute it: no change (then the SM waits for something else: the shared-memory atomics' latency in the mark loops, the 16-barrier scan, the reservation's global atomics).

### genab (GPU session, gold-g4c, 23 Nov 14:08-14:11Z, `sievepack/genab_rtxpro6000.txt`): the latency reading was right, `DEEP_GEN_UNROLL=4` takes the generate kernel from 40.3 to 28.7 ms

ms a 2^24 window on top of production's six options (gen = pass A + pass B): unroll 1: **40.30** (13.67 + 26.64); unroll 2: 32.43 (11.68 + 20.76); **unroll 4: 28.74 (10.78 + 17.96)**; unroll 8: 30.10 (11.18 + 18.92); CTAs of 256 threads with the 8192-word buffer (2 CTAs, 8 warps): 36.27; 256 threads with 6144 / 4096 words
(3 / 4 CTAs an SM, unroll 4): 29.97 / 29.95; 256 threads, 4096 words, unroll 1: 41.08; rcta 16, unroll 4: 32.91.  Tile unroll 8 / 16 (50 / 96 registers): tile kernel 21.56 / 21.75 against 20.86 at 4 (no gain; the small-prime phase moves ~6.5 TB/s through the L2: 50 GB of table a window, so that
may be its limit now).  So **memory-level parallelism, not the instruction count or the occupancy, was what the generate kernel lacked: 4 table loads in flight a warp bought -11.6 ms a window (-29% of the kernel) at +4% instructions**, and 3-4 CTAs an SM instead of 2 buys nothing more once the loads overlap.
At unroll 4 the kernel runs at ~70% of the integer issue peak again (37k instructions a CTA pair over ~26k cycles), so instructions count again and the visit loops (54% of them) are the next thing.  (A longer window would cut the visits a member, but not here: the vectors of the campaign are short, ~2e7 members each, one 2^24 window a vector - `search_gpu5.py --vector-dir`; I proposed a 2^26 window of one vector (ksab.sh) without reading that, and withdrew it.  It would only exist for the long-vector (88-moduli) mode.)


## The pipelined tile kernel (`DEEP_TILE_PIPE=1`, 23 Nov 14:45Z; CPU-verified identical, not yet timed on a GPU)

**Why.**  After unroll 4 the tile kernel is the larger half of a window (20.9 of ~52.8 ms: small-prime marks 8.2, bin apply 9.0, init + write 3.7).  Its bin apply moves 14.4 GB at 1.6 TB/s = 9.0 ms: the apply runs at the DRAM rate while it runs, and DRAM is idle in the small-prime phase before it,
so the kernel averages 0.81 TB/s over its 20.9 ms (17 GB) and is 11.9 ms without any bin.  The L2 prefetch (`DEEP_TILE_PREFETCH=256`) bought only 1.6 ms of the ~9 it could.  One CTA an SM (the 64 KB bitmap) cannot overlap the phases itself; two CTAs would, but 2 x 64 KB do not fit.
The small primes' marks and the bin's entries are both `atomicAnd` on the same bitmap: they commute, so they can run AT THE SAME TIME.

**What.**  `s200g_tile_pipe` (a separate kernel: the plain `s200g_tile` is byte-identical): `TILE_PIPE_AT` threads (default 128 = 4 of 16 warps) have the APPLY role: they stream the bin through two shared-memory buffers of `TILE_PIPE_CH` words (default 4092 = 16 KB: a multiple of 12 so that a chunk is whole 16-byte copies
and whole groups of 3 words) with `cp.async` (straight from the memory system into shared memory: no registers, no L1), wait for a chunk (`cp.async.wait_group` + a NAMED barrier, `bar.sync 1, TILE_PIPE_AT`, among those threads only), apply it from shared memory (`gbig_apply_words`, the same
clears as `gbig_apply_entries`), and refill the buffer; the first two chunks are requested before the bitmap is initialised.  The other 12 warps run the small-prime loop of the unrolled kernel (their thread indices shifted, `TILE_UNROLL` as before) and never wait for the apply threads.  At the end the usual
`__syncthreads()` and the tile is written.  Shared memory: bitmap + 2 chunks = 98,272 B (dynamic; the host sets the attribute; `BatchFeeder.tile_smem`).  SASS (sm_120, packed, unroll 4): 720 instructions, 40 registers, 2 barriers, no spills, `LDGSTS` for the copies.
Model: the CTA takes max(compute ~45 us, DRAM 360 KB at the SM's 8 GB/s share ~45 us) + the write, instead of 38 + 42 + the write: **tile 20.9 -> ~14 ms (-7 ms a window)** if the two overlap fully; if the small-prime marks slow down with 12 warps instead of 16 (AT = 64: 14), part of that is lost.
**CPU.**  `DEEP_TILE_PIPE=1 DEEP_TILE_PIPE_AT=32 DEEP_TILE_PIPE_CH=96 test_gbatch_cpu.py` (chunks of 96 words and 32 apply threads: every bin is several chunks; named barrier = a second pthread barrier), unpacked and with the whole stack (packed, unroll 4, flat flush, order, generate unroll 4): identical to the CPU feeder.
**Risk to know about:** a named barrier whose participants do not all arrive hangs the kernel.  All 128 apply threads run the same number of chunks (nch from the bin's count, read identically by every thread, no writes to it during the launch) and the barrier is not used by anything else.
**To run:** `splitab.sh` rows `TILE_PIPE AT=128 / 64 / 192 / CH=2040` on the unroll-4 stack, the tile line (tile kernel ms; small / apply are not separable here: read the TOTAL).  Then the driver gate as usual (`DEEP_TILE_PIPE=1`, tile threads 512, the carve-out of 100 for the shared memory).


### bundle8 (GPU session, gold-g4c, 23 Nov 14:31-14:33Z, `sievepack/bundle8_rtxpro6000.txt`): the small items, measured: the tile kernel does not move

ms a 2^24 window on production's stack (reference: gen 28.74 + tile 20.78 = sieve phase 50.6-50.9):

| row | gen | tile | sieve phase |
|---|---|---|---|
| tile kernel with clamped loads | 28.79 | 20.78 | 50.6 |
| PF = 384 / 512 | 28.77 / 28.80 | 21.83 / 21.88 | 52.3 / 52.0 |
| `--split` 524288 / 700000 / 1500000 | 32.75 / 30.88 / 26.67 | 19.88 / 20.18 / 23.59 | 53.8 / 52.2 / 51.6 |
| tile 18 (PF 128 / none) | 31.58 / 31.60 | 24.44 / 20.65 | 57.2 / 53.8 |
| **pipelined tile, AT = 64** | 28.75 | **19.18** | **49.2** |
| pipelined tile, AT = 128 / 192 / (128, CH 2040) | 28.75 | 20.35 / 21.80 / 19.76 | 50.2 / 51.6 / 49.6 |

None is deployed (none reaches 1% of a batch).  **My model of the tile kernel was wrong again**: I had it as three phases in series per CTA with the apply a DRAM wave (9.0 ms = the bins at 1.6 TB/s) that streaming the bin beside the small primes would hide (-7 ms); it hid 1.6 ms.  What the table says:
the tile kernel's ~20 ms does not shrink when its phases overlap (the pipelined kernel), when its prefetch is longer (PF), when its tiles are smaller and 3 CTAs share an SM (tile 18 without PF is 20.65 against 20.78), when the table is shorter (a lower split makes the small-prime part 5.5 ms but the gen and the bins pay it back),
or when its loads are cheaper (clamped, unroll 8 / 16).  Something shared by all of them bounds it.  The candidate I cannot exclude: the small-prime table's trip through the L2 (every tile CTA reads the 1.25 MB slice of its tile: 188 SMs x 1.25 MB = 235 MB a wave, ~6 TB/s, 50 GB a window) and the bins' 14.4 GB, together
67 GB in 20 ms = 3.3 TB/s through the L2-to-SM path.  If that is the limit the way forward is fewer bytes through it - a smaller table entry (16 -> 12 or 8 bytes: the Shoup constant is 1/4 of it, and the row-dependent part q M^-1 mod s does not depend on the tile and could be a per-row table made once a vector) or two rows a CTA sharing each loaded
entry - not more overlap.  Neither is built: both are restructurings of the tile kernel and its tables for at most -2 to -3 ms a window.

### bundle9 (GPU session, gold-g4c, 14:58-14:59Z) and the LEAN gate (15:01-15:02Z): LEAN deployed (x0.9875), the pipelined tile not; my table probe was badly designed and is removed

Sieve ms a 2^24 window (reference 50.6-51.1): SCAN2 50.8, RESV_LATE 50.1 (the late reservation moves ~10 ms from "pass A" to "pass B" in the printed split: the bench's cap = 0 pass A no longer waits for the reservation), MINRED 50.4, **LEAN (all three) 49.6 (-1.5 ms)**, LEAN + pipelined tile AT = 64 48.0, the pipelined tile alone 49.4.  The driver gate (24 windows, identical
slice lines, known case 23 / 23): **LEAN x0.9875, LEAN + pipelined tile x0.994**: the pipelined tile's 96 KB of shared memory costs more beside the Fermat kernels than its 1.6 ms saves, so LEAN alone is deployed (15:02:52Z on gold-g4c, the other two cards gating).  Batch ~0.751 s.
`TILE_PROBE` (a timing-only variant that read the small-prime table from 256 sampled entries) made the tile kernel 575 ms: every thread used the same 256 entries with the same row q, so every mark landed on the same few shared-memory words and the atomics serialised.  A probe must keep the marks' addresses spread (a hash start offset a prime would have done); I removed it rather than leave a broken instrument.
Whether the table's trip through the L2 bounds the small-prime phase is therefore still untested; the best case for fixing it is -2 to -3 ms a window (-0.4% of a batch).


### The window's tail (count, select, finalize, rows): 10.6 ms of a 61 ms window, and two of the four kernels are shaped wrongly for a GPU (uarch, 23 Nov 15:50Z; CPU-verified, opt-in `DEEP_REST2=1`, NOT timed on a GPU)

**I looked at the wrong denominator in the morning.**  Task "rest phases" was closed at 385 ms a window: 11 ms of 385 is 3%.  The sieve phase is now 50 ms (generate 27.5, tile 20.8), so the same ~11 ms are **18% of the window's chain** (61 ms alone), and the window is the sieve thread's unit of work.
The GPU session's own numbers (`uarch_measure/bench_split_rtxpro6000.txt`, `measure_rtxpro6000_sections5-6_fixed.txt`, ms a 2^24 window): count 1.87, select 0.19, **finalize 2.11, rows 6.39**; `wait1` (the host reading the survivor count) 0.13-0.34.

**rows (6.4 ms for a 2.6 GB matrix that `count` reads in 1.87 ms = 1.4 TB/s).**  The SASS (`sass.py ... --kernel s200g_rows`, sm_120) is, per row of the unrolled loop: `LDG` -> `LOP3` (needs the loaded word) -> predicated `STG` -> next `LDG`.  The compiler cannot hoist the next load above the store
(`bits` and `rows` may alias) and issue is in order, so a warp waits one full memory latency for every one of the 1,248 rows with **no load in flight beside it**; 7,872 warps each keep one 256-byte request outstanding and the DRAM sees small random chunks at a 2 MB stride.  Count is at the DRAM floor because it
loads 16 rows before it adds anything.  `s200g_rows2` does the same: a thread loads `ROWS2_BATCH` = 16 words into 16 registers first (`__restrict__`), then tests and stores them in order.  SASS: 16 `LDG.E.CONSTANT` back to back, 40 registers, no spills; the lists are identical (`test_rest2_cpu.py`).
Expected: the bytes are the same, so the floor is `count`'s 1.9 ms; I expect 2.5-3.5 ms (random 256-byte chunks do not reach streaming rates), i.e. **-3 to -4 ms a window**.  A CTA a selection block that stages each row's 4 KB slab through shared memory would be closer to 2 ms; not built until the number for this one is known.

**finalize (2.1 ms: one CTA of 256 threads).**  Thread t walks a run of ~984 consecutive keys: an integer division by nkeep (~25 instructions), four loads and four stores a key at a 984-element stride across the warp (32 lines a request), then a second walk for the offsets.  Nothing about the work needs one CTA: the block's keys are contiguous.
`s200g_fin_sums` (a CTA a selection block: the sum of its kept counts, a tree reduction) and `s200g_fin_main` (a CTA a block: the sum of the blocks before it, `btot[0 .. b)`, then a Hillis-Steele scan over chunks of blockDim keys and the coalesced writes of cnt, member, k, offs; the last CTA writes offs[nsel] and total).  Same outputs, 26 registers, 2 KB of
shared memory; expected 20-40 us instead of 2.1 ms (**-2 ms a window**).  The host `wait1` and the final statistics read are unchanged.

**Together** -5 to -6 ms of the 61 (10%), -20 to -24 ms a batch alone.  The sieve thread is near the critical path, but the batch gains from latency-bound kernels have been 60-65% of the window's change (the unroll: -46 ms of sieve, -29 ms of batch), so I would expect **-1% to -2% of a batch, not measured**.  These are DRAM- and latency-bound kernels that issue few
instructions, so unlike the flat flush they should not change what the Fermat kernels pay.
**Checked on the CPU**: `test_rest2_cpu.py` (finalize == fin_sums + fin_main and rows == rows2 == numpy over 8 geometries: nU below / at / above the 16-row batch, one or several selection blocks, nkeep 1 / below / at / above the CTA size, zero counts, a block with no alive row); `DEEP_REST2=1` through
`test_gpu_sieve_cpu.py` (11 windows, every one identical to the CPU feeder; the counting wrapper shows the new kernels run), `test_gbatch_cpu.py`, `test_deep_feeder_cpu.py`, `test_ghead_cpu.py`, `test_headcheck_cpu.py`.
**To run on a GPU**: `bench_split.py` prints the four phases of a whole window (`whole window (bench_batch's phases, ms): ... count ... finalize ... rows`): run it with and without `DEEP_REST2=1` (the variable is read when the feeder is built); then the driver gate (`DEEP_REST2=1`, slice lines identical on the 24 windows, known case 23 pairs, >= 1% of a batch).


### The tail, measured (GPU session, gold-g4b, 23 Nov 15:52Z, `DEEP_REST2=1`): finalize works, rows2 is SLOWER; and what I do about it (uarch, 16:35Z)

ms a 2^24 window, the whole-window line (count / select / finalize / rows / wall): production 1.86-1.89 / 0.19 / 2.10 / 6.31-6.43 / 61.5-62.0; `DEEP_REST2=1` 1.87 / 0.19 / **0.01** / **7.83-7.84** / 61.0-61.9; + LEAN 1.87 / 0.19 / 0.01 / 7.79 / 60.9.
* **finalize: 2.10 -> 0.01 ms, as designed.**  It is now its own flag, `DEEP_FIN2=1` (the parallel finalize alone): -2.1 ms a window, ~0.6% of a batch, under the 1% bar alone.
* **rows: 6.4 -> 7.8 ms, WORSE.**  My model of `s200g_rows` (one dependent LDG -> LOP3 -> STG chain a row, a warp waiting one memory latency a row) predicted 2.5-3.5 ms for 16 loads in flight; the SASS does show 16 loads back to back; the kernel got slower.  A kernel that more memory-level parallelism makes slower is not latency-bound.  It is
  bound by HOW the matrix is read, HOW the lists are written, or both.  Two candidates, which a probe separates:
  1. **The reads.** A row is a separate 2 MB region (`KW` words), so a warp's loads walk 1,248 pages 2 MB apart (256 B at a time: a warp's 32 kept members are ~2 words apart, 8 sectors for 32 useful words), against `count`'s sequential 128-byte warp loads of the same 2.6 GB.  Page-walk and DRAM-page locality, not bytes, may be what bounds it.
  2. **The writes.** 9.3e7 two-byte stores into a 186 MB array: each 32-byte sector (16 entries of ONE member's list) is written over ~50 row iterations, which is ~0.25 ms of the kernel; with the L2 turning over every ~0.3 ms (128 MB at 0.4 TB/s) a partially written sector may be evicted and written back before it is
     full, and on a card with ECC a partial write is a read-modify-write at the DRAM: up to 9.3e7 x 64 bytes = 6 GB of extra traffic, the size of the gap.  Faster reads (rows2) would shorten the L2's turnover and make it worse, which is what was measured.
* **`bench_rows.py` (new; a synthetic window, no sieve, a minute on a card)** times the variants alone on the same inputs: `count` (the sequential reference), `rows`, `rows2`, **`rows` with its stores taken out** (a running sum; the same loads, READS ONLY), **`rows` with its loads taken out** (a hash stands in; the same scattered stores, WRITES ONLY), and the two-step lists below.
  rows vs rows-no-stores is what the stores cost, rows vs rows-no-loads what the loads cost.
* **`DEEP_ROWS3=1`: the lists in two steps** (`s200g_rowmask`, `s200g_rowlist`).  Step 1 reads the matrix once, a thread a kept member and a row group of 32 rows, into a 32-bit mask a (row group, member): grid (member chunks, row groups) with the row group the SLOW dimension, so the CTAs resident together sweep the same 32 rows (the order `count` reads
  in) and the writes are coalesced words (39 groups x 252,000 x 4 bytes = 39 MB).  Step 2 reads the masks and writes the lists (the scattered u16 stores, now with no loads of the matrix beside them).  If the reads were the problem step 1 should run near `count`'s rate; if the writes were, step 2 is where the time goes and the next version stages a CTA's contiguous
  output region in shared memory (CSR lists are contiguous across members) and flushes it with coalesced stores.  Either way the probe table says which.  Same lists (`test_rest2_cpu.py`: 10 geometries, now also rowmask + rowlist == numpy; `test_bench_rows_cpu.py`).
* Flags: `DEEP_FIN2=1` (finalize), `DEEP_ROWS3=1` (the two-step lists), `DEEP_REST2=1` (= FIN2 + rows2, kept as measured).  Not deployed, not timed beyond the above.

**Addendum, 17:10Z: a third candidate that I had missed, and the one I now like best.**  The kept members are listed in COUNT order (`keys` sorted by (count, index): the Window's documented order), so the 32 lanes of a warp in `s200g_rows` read 32 words at RANDOM places of the block's 4 KB slab of a row:
~28 distinct 32-byte sectors for 32 useful words (a sorted warp would touch 8), and the two CTAs that share a block (492 kept members, 256 a CTA) fetch the same sectors twice: ~2.7e8 sector requests a window for 8.1e7 distinct sectors.  `count` reads whole 128-byte lines.
Under this reading a deeper load queue cannot help (rows2: 16 loads in flight, each warp-load costing 28 sector misses against the L1's finite outstanding-miss capacity, was slower), which fits the data; I did not see it earlier because I had assumed consecutive kept members were neighbours in the matrix.  (My 'one memory latency a row' model came from the SASS, which is right about the dependent chain; it was wrong about the chain being the bound.)
* **`DEEP_ROWS_ORD=1`**: `s200g_order` (a CTA a selection block: a bitonic sort of (index << 13 | position) in 32 KB of shared memory, nkeep <= 8192, LLOG <= 19; ~0.05 ms for all blocks) makes the permutation that lists a block's kept members by increasing index, and `s200g_rows_ord` is the unchanged serial rows loop with thread j taking member `ord[j]`: a warp's lanes are ~2 words
  apart, a CTA reads its own half of the slab, nothing is fetched twice, and every list is written exactly where it was (`offs[ord[j]]`): the same output.  **`DEEP_ROWS_ORD=2`**: the same with 8 loads in flight a thread (`s200g_rows_ord2`): the gather is cheap enough to try it.
* `bench_rows.py` now times, on the same synthetic window: count, rows, rows2, rows without stores (READS ONLY), rows without loads (WRITES ONLY), order, rows_ord, rows_ord2, rows_ord without stores, rowmask, rowlist, rowmask + rowlist, and checks that every variant's lists equal rows'.  How to read it: **rows_ord against rows is the whole effect of the order**; rows_ord without stores against rows
  without stores is its effect on the reads alone; rows without loads is what the stores cost; if rows_ord(2) lands near count's 1.9 ms plus the write cost the gather was the problem, if it stays near 6 the stores or the pages are.
* CPU: `test_rest2_cpu.py` (10 geometries): order == argsort by index per block, rows_ord == rows_ord2 == rows == rowmask + rowlist == numpy; `DEEP_ROWS_ORD=1|2`, `DEEP_FIN2=1`, `DEEP_ROWS3=1` through `test_gpu_sieve_cpu.py` (11 windows each, identical to the CPU feeder, the intended kernels run); FIN2 + ROWS3 through `test_gbatch_cpu.py` (with pack + hoist + unroll 4 + flush2 + order) and `test_ghead_cpu.py`.
  SASS (sm_120): rows_ord 28 registers and the same serial LDG -> LOP3 -> STG chain as rows; rows_ord2 40; s200g_order 12 registers, 32 KB shared.

### Closed: the survivor-list kernel, measured (GPU session, gold-g4c, 23 Nov 16:25Z, `bench_rows.py`, synthetic window at production's f = 0.985; uarch 17:05Z)

2^24 members, 1,248 rows (2.62 GB), 251,904 kept, 97.5M alive rows.  Production tail (ms): count 1.93, select 0.18, **finalize 0.90, rows 3.85** (6.9 ms, 11% of a window).  **My "10.6 ms, 18%" and "finalize 2.1, rows 6.4" were bench_split's default f = 0.97 (504K kept members), not production's 0.985: a wrong denominator of mine, again.**

| variant | ms | GB/s of the matrix |
|---|---|---|
| count (reference) | 1.85 | 1,417 |
| rows (production, serial) | 3.88 | 675 |
| rows2 (16 loads in flight) | 3.72 | 704 |
| rows, no stores (reads only) | 2.94 | 891 |
| rows, no loads (writes only) | 1.36 | 1,926 |
| order (the permutation, once) | 0.01 | |
| rows_ord (kept members by index, serial) | 2.96 | 885 |
| **rows_ord2 (by index, 8 loads in flight)** | **2.61** | 1,002 |
| rows_ord, no stores (reads only) | 1.75 | 1,497 |
| rowmask (row-group-major grid) | 1.99 | 1,314 |
| rowlist (lists from the masks) | 1.62 | 1,614 |
| rowmask + rowlist | 3.68 | 711 |

Every variant's lists equal rows' (True).  What it says: **the order of the kept members was real** (reads only 2.94 -> 1.75 ms, count's rate), and the row-group-major grid of rowmask reaches the same read rate in COUNT order (1.99 ms); more loads in flight help a little once the gather is cheap (2.96 -> 2.61, and rows2's 3.72 is no better than rows' 3.88 on random data); what remains is the
scattered two-byte stores (writes only 1.36 ms for 186 MB, ~137 GB/s).  `DEEP_FIN2=1` (0.90 -> 0.01 ms) + `DEEP_ROWS_ORD=2` (3.88 -> 2.61) is **-2.2 ms a window, ~0.6% of a batch by the GPU session's conversion: under the 1% bar, not gated, shelved** (the flags stay as a bundle ingredient).  A fused index-ordered kernel with a shared-memory staged, contiguous write might reach ~2.0 ms (another ~0.6 ms a window, ~0.15%): not built.
(The earlier real-data DEEP_REST2 run, finalize 2.10 -> 0.01 and rows2 6.4 -> 7.8 at f = 0.97, is consistent with this: rows2 without the order is a wash or worse.)



## The one-pass generate kernel (`DEEP_GEN_ONEPASS=1`; uarch, 23 Nov 17:55Z; CPU-verified, NOT yet timed on a GPU)

**Why.**  `gbig_gen_st` visits every (prime, row) pair of its chunk **twice**: pass A to count the marks of each bin, the scan to place the bins' runs in the staging buffer, and pass B to visit the same pairs
again (the 16-byte table load, the Shoup chain, the two reductions, the mark loop) only to learn where each mark goes.  With the per-CTA accounting above (227 warp visit iterations and 333 mark steps a CTA,
real prime list) and today's SASS (unroll 4, clamped loads, flat flush, LEAN): pass A visits ~5.4k + marks ~2.0k, pass B visits ~5.4k + staging ~2.7k, flush ~3.0k, scan + reservation ~0.5k: ~19k warp
instructions a CTA, of which pass B's 5.4k of visits repeat pass A's exactly, with their table loads waited for a second time.  Measured split (genab, unroll 4): pass A 10.78 ms, pass B 17.96 ms.

**What.**  Each bin of the CTA (8 rows x 32 tiles = 256 bins) owns `SLOT_C` = 40 words of shared memory and each pair is visited ONCE: the counting atomic returns the mark's rank r in its bin, the mark goes to
`slot[b * 40 + r]` while r < 40, and to an overflow list of (word, rank) entries (`OVF_CAP` = 128) beyond that.  A bin's marks are then one contiguous run of slots, so there is **no scan**: the bins are reserved in
global memory from the counts (one atomic a bin, as before) and copied out (packed: groups of 5, the last group padded with copies of the bin's last mark when it is flushed; an overflowed mark is a group of 5
copies of itself after the bin's slot groups, at its rank).  If the list fills, the CTA writes every mark the old way (the visits again, one store a mark), like a chunk too big for the staging buffer.
The host's chunks are unchanged (3/4 of `STAGE_CAP` marks a CTA, ~24 a bin): a bin of Poisson(24) marks needs more than 40 slots with probability 9.9e-4, **0.55 overflow entries a CTA**, and the fallback
needs more than 128 of them (never in practice).  Same marks in the same bins as `gbig_gen_st`, same bit matrix, same overflow protocol (any bin over `cap`: `gcnt[NBINS] = 1`, nothing written); unpacked, the
same bin counts; the order of the marks inside a bin differs (it never was fixed: atomics).  With `DEEP_GEN_ONEPASS=0` (the default) the preprocessed source of the production kernel is byte-identical to before
(checked with `g++ -E` on the production defines).

**The visit loop**, a second change inside the new kernel: the unrolled steps whose 4 primes are all in the chunk need no clamp and no validity mask (`TAB[p_lo + min(pi, np - 1)]` and the `j = limS` select
cost ~3 instructions a visit); only the one partial step at the end is clamped, so the loads in flight a warp are the same as production's.

**SASS** (`sass.py`, sm_120, production's defines + `GEN_ONEPASS`): **44 registers** (production 40; allocated as 48, so 24,576 a CTA against 20,480; `DEEP_GEN_LB=512,3` brings it to 40 with no spills), **44,048 B** of shared memory (38,032), no spills, 2 CTAs of 512 threads an SM as before; the visit step is
46 instructions for 4 visits (**11.5 a visit**, production ~17 + pass B's again); the mark step is **13 instructions** on its common path (production: 6 in pass A + 8 in pass B; the warp-aggregated atomic of
the overflow list is off that path); the flush ~60 instructions a warp iteration over 8 group slots a bin (~5 of them used).  **Estimate a CTA: visits 227 x 13.5 = 3.1k + marks 333 x 13 = 4.3k + flush
~3.9k + reservation ~0.4k = ~11.6k warp instructions, against ~19k: -39%.**  At unroll 8: 55 registers, no spills; with 25 slots and `__launch_bounds__(512, 3)` (`DEEP_GEN_LB=512,3`): 40 registers,
28,688 B, 3 CTAs an SM.

**Expected, not measured:** if the kernel stays near its ~70% of the integer issue rate, **gen 28.7 -> ~17-21 ms a window** (the floor that does not move is the bins' DRAM writes: 14.4 GB a window, ~9 ms at
1.6 TB/s); -8 to -12 ms a window, -32 to -48 ms of a batch's alone time.  How much of that reaches the batch depends on the mix: the flat flush (instructions only: -18.1k a CTA) converted at 157% (-27 ms a batch),
the unroll (latency only) at 63%; this change is both, with 41% of the flat flush's instruction cut, so **-3% to -8% of a batch** (-20 to -60 ms), most likely near -5%.  What would refute it:
gen not falling with the instruction count (then the kernel waits on the bins' writes or on the counting atomics' latency, and pass B's visits were hiding under them).

**CPU** (the pthread emulation of the kernel source): `test_gbig.py` (`onepass_tests`: 40 slots / 20 slots / 10 slots with a 4-entry list, unroll 1 and 4, both grid orders, the min-based reduction,
unpacked and packed, the 6 staged geometries including 3x-coarse chunks and 2-row CTAs over 128 tiles, a capacity too small then large enough) against the brute-force reference: bits identical, unpacked bin
counts identical, the overflow flag set when it must be; a CPU-only counter checks that every path ran (CTAs that used the overflow list without the fallback at 40 and 20 slots, CTAs that took the fallback at a
list of 4); `onepass_wide` runs the shape of a 2^25-member window at 8 rows a CTA (64 tiles x 8 rows = 512 bins, 20 slots: 40 would not fit in 48 KB), packed and unpacked.  `test_gbig_cpu.py` with `DEEP_GEN_ONEPASS=1` at 40 and 10 slots (the cupy glue, packed and unpacked, the stage-overflow chunks, the capacity retry); `test_gbatch_cpu.py` (BatchFeeder against
sieve200's CPU feeder) on production's stack + one-pass with `--big` (8 and 16 rows a CTA), and unpacked at 7 slots: every window identical.  `run_cpu_tests.sh` has the new lines.

**To run on a GPU:** `bash onepassab.sh SPEC` (production, one-pass at 40 slots, the same at 40 registers, at unroll 8, 30 slots with 6144-word chunks, 25 slots with 4096-word chunks at 3 CTAs an SM, production again; with one pass the
printed "pass A" is all the visits and "pass B" is the flush); then the driver gate as usual with `DEEP_GEN_ONEPASS=1` added to production's environment (it needs `DEEP_GEN_HOIST=1`, which production has; slice
lines identical on the 24 windows, known case 23 / 23, >= 1% of a batch).  **2^25-member windows** (64 tiles, as on the L4): 40 slots x 8 rows a CTA is over the 48 KB of static shared memory (a static_assert says so); use `DEEP_GEN_SLOT_C=20` with 8 rows (~12 marks a bin there: overflow stays rare) or `DEEP_RCTA=4` with 40 slots.

### Measured and deployed (GPU session, 23 Nov 18:00-18:11Z, `sievepack/opab_rtxpro6000.txt`, `opgate_rtxpro6000.txt` on its branch, 2745f74)

bench_split on gold-g4b, ms a 2^24 window of m89_8, production's options (gold-g4b has no LEAN):

| row | gen (pass A / pass B) | sieve phase |
|---|---|---|
| production | 28.75 (10.79 / 17.96) | 51.2 / 52.2 |
| flag unset (the new source) | 28.75 | 50.8 |
| **ONEPASS, 40 slots** | **22.15 (13.80 / 8.35)** | **44.4** |
| ONEPASS, 40 slots, 40 registers (`DEEP_GEN_LB=512,3`) | 22.16 | 43.9 |
| ONEPASS, unroll 8 | 22.89 | |
| ONEPASS, 30 slots, stage 6144 | 23.84 | |
| ONEPASS, 25 slots, stage 4096, 3 CTAs an SM | 22.98 | 47.1 |
| ONEPASS + LEAN | 22.01 | 44.7 |
| LEAN alone | 27.52 | 50.4 |

**Generate -23%, sieve phase -14%.**  Driver gate on the 24 test vectors (deep_env_v89, f = 0.985, top placement; slice lines identical in every run, known case 23 / 23): gold-g4 x0.9735 (one-pass) /
x0.9728 (with the launch bounds), gold-g4b x0.9638 / x0.9566, gold-g4c x0.9725 / x0.9733: **-2.7% to -4.3% of a batch**, deployed 18:09:59-18:11:05Z (the bounded variant on gold-g4 and gold-g4b).
**My estimate was too optimistic:** I expected gen 17-21 ms; it is 22.15.  The single pass ("pass A" in the bench) grew 10.79 -> 13.80 ms, more than the ~2.3k instructions a CTA of slot stores I had
counted (the store waits on the counting atomic's result, a dependent shared-memory chain the old pass A did not have), and the flush alone ("pass B") is 8.35 ms, close to the ~9 ms the bins' 14.4 GB
take at the DRAM rate: that floor is now most of what is left of pass B.  The batch gain is near the low end of my -3% to -8%.

**Sizing the slots for other geometries (uarch, 18:20Z).**  A CTA's chunk holds ~3/4 of `STAGE_CAP` marks spread over `RCTA x NTILES` bins, so a bin gets ~lambda = 0.75 STAGE_CAP / (RCTA NTILES) marks a CTA
(Poisson): 24 on the RTX (8 rows x 32 tiles), but **48 on the L4** (2^25 windows: 64 tiles, `rcta 2`, stage 8192), where 40 slots would mean ~1,073 overflow entries a CTA, a full list and the slow
fallback on nearly every CTA (slower than without the flag; the static_assert does not catch it: 22.5 KB).  There use **75 slots** (0.04 entries a CTA, 40.5 KB; 70: 0.40, 37.9 KB).  `gbig.BigStage` now
computes this for its actual stage_cap / rcta / tiles and refuses to start above 32 expected entries a CTA, naming the slot count to use (`gbig.onepass_slots_for`); the RTX deployment (0.55) passes
unchanged; `DEEP_GEN_SLOT_C_ANY=1` lets the CPU tests that force overflow on purpose through.

