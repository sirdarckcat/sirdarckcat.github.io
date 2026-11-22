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

## What would still have to be built if the measurement says go

1. The small-prime kernel as a tile kernel of a batch: CTA (row, tile), the Shoup marks of the tile (a table per tile: c0 = (N0 M^-1 + k0 + tile 2^19) mod s, 64 x 1.25 MB), then the bin of
   (row, tile) applied to the same shared bitmap, then the tile written into the batch matrix `bits[row][2^25 / 32]` (4.6 GB for 1,093 rows; fits an RTX PRO 6000, A100 and L4).
2. count over the batch matrix (KLOG = 25: 4,096 CTAs, 64 MB of counts), select over 1,024 blocks of 2^15 (a 64x better filled GPU than today's 16 CTAs), finalize with a scan over ~1M keys,
   rows extraction for ~1M kept members (the present rows kernel gathers one bit a row at a 64 KB stride: 550 MB of L2 traffic per 2^19 members; order the kept members by index first, ~6x less).
3. The caller (search_gpu5) works on batches instead of 2^19-member windows.
4. An L4 stays at 1e6 (its DRAM is 300 GB/s: the bins would cost ~0.03 ns a mark).

Exactness is not at risk: a deeper sieve only removes rows that have a prime factor, and the same identical-to-CPU tests (`test_gsieve.py` style, B up to 2^15 on small geometries) apply.
