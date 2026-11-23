# Micro-optimizations of the search engines: index, numbers, how to test

Everything here was measured, and every replacement is tested against the code it replaces before it was offered.  Speeds are one
core of a 4-core Sapphire Rapids container (AVX-512 with IFMA, about 3.6 GHz under 512-bit load) unless a GPU is named.  GPU code
was written and verified on a CPU (the same source compiled as C++), then timed by the GPU session on its GPUs.

| directory | what it replaces | result | test |
|---|---|---|---|
| `fscan/` | `fscan.c`'s score loop, exact stage, Fermat kernels (IFMA 52-bit, AVX2 3 x 30-bit) | 27-31% fewer cycles a member (Intel and Zen 2), same members found; `FERMAT26_STEP.md` states the 3-limb step for a proof | `selftest_ab.sh`, `test_fermat.py`, `stress_fermat.py`, `check_record.sh` |
| `sieve200/` | numpy sieve of `search.run_block` (campaign 3, 867-1,094 rows, 661-bit members) | 0.64 us a member at B=1e6 against 52 us (K=2^20, 867 rows); identical alive matrices, counts, tests, prps, successes; the feeder (counts, selection, CSR survivor rows) gives a GPU tester exactly what it needs | `test_sieve200.py`, `test_dropin.py`, `test_feeder.py` |
| `fermat661/` | `gmpy2.powmod(2, n-1, n)` on 661-bit numbers | 10-11 us a test against 110-129 us on IFMA CPUs (13 limbs of 52 bits, 8 lanes); `search_c.py` uses it: a whole block 8.3 s -> 0.61 s | `test_fm13.py`, `test_dropin.py` |
| `fermat661/cuda/` | `gpu_fermat.py`'s `fermat2` and `fermat3` | 22.9M tests/s on an RTX PRO 6000 against 13.1M (`fermat3`) and 8.9M (`fermat2`): 24 limbs of 28 bits, every product one 64-bit multiply-add, dedicated squaring, generated step with static indices, lazy reduction, start value 2^(672-c); ties `fermat3` on sm_80/89; redundant-limb steps (`_r`, `_s1r`: no carry chain after the doubling, limbs < 2^29) are correct and 46-47 instructions shorter: measured +2.4% on an RTX PRO 6000 (s1r asm 23.39M against s1 asm 22.85M), +1% on the A100; in production since 2026-11-22 23:50Z | `test_fermat28.py`, `test_step28.py` (CPU), `test_gpu_fermat28.py` (GPU) |
| `fermat661/cuda/` (`fermat28` "w" steps) | `fermat28` plain | explicit `mul.wide.u32` for the products m_i n_j: no dead IADD3 a product; **1,198 SASS instructions a step instead of 1,798 on sm_80 / 89**; CPU-verified (same results); **measured by the GPU session: +8.6% on an A100 (6.95M -> 7.55M tests/s; 7.63M with redundant limbs), +14-15% on an L4, ~0 on an RTX PRO 6000; in production since 2026-11-22 23:50Z (A100 +13.5% and L4 +14% over the old kernel 3, fleet +4.4%).** I had predicted +47% on the A100 and L4: wrong, because my table said IMAD.WIDE costs 2.3 cycles there and it costs 4.15 (see lesson below) | `test_step28.py`, `test_fermat28.py` with `FM28_STEP=fermat28_step_s1w.cuh` |
| `fermat661/cuda/` (`fermat31`) | `fermat28` | 22 limbs of 31 bits, 737 IMAD.WIDE a step instead of 876: correct (CPU-verified); the refitted model (`costmodel.py`) predicts +4.6% on an A100, -3% on an L4 and 21% slower on an RTX PRO 6000: not worth deploying; negative result | `test_step31.py`, `test_fermat31.py` |
| `sieve200/cuda/` | `search_gpu3.py`'s sieve3, `alive.sum`, `lexsort`, gather, `nonzero` | in production on 5 GPUs (2.3 ns a member on an RTX PRO 6000, 10-15 on an A100, 15-22 on an L4); next version: 32-bit Shoup setup (35 instead of 85 SASS instructions a prime, 20 registers), separate sieve CTA size, per-phase timings | `test_gsieve.py`, `test_gpu_sieve_cpu.py` (CPU), `test_gpu_sieve.py` (GPU) |

| `sieve200/cuda/` (deep sieve: `gbig`, `gbatch`, `deep_feeder.py`) | `GpuFeeder` at a deeper bound B | a bound of 1e7 .. 1e9 is worth x1.4 .. x2.45 hit mass per Fermat test (the GPU session's measurement) but `GpuFeeder` charges every (prime, row, 2^19-window) pair: a loss.  The bucketed large-prime stage visits each (row, prime) pair once per 2^25-member batch (64x fewer visits), bins the marks by (row, tile) and applies them to the tile's shared bitmap.  **A new 200-digit record, g = 157,837 (+8% over 146,191; certified, 7a7c728 on the GPU session's branch), was found by `search_gpu5.py --deep 1` (B = 1e8) 54 minutes after a G4 host switched to it.**  **Measured by the GPU session: 0.030 ns a mark on an RTX PRO 6000 (my estimate was 0.005-0.015), 0.10 ns on an L4; a 2^25 window at B = 1e8 takes 373 ms (11.5 ns a member) on an RTX PRO 6000; in production at B = 1e8 since 2026-11-23 01:14-01:26Z on 3 RTX PRO 6000 and 3 L4: x1.37 / x1.40 hits/s** (batch 2.10 s against 2.00 s for x1.42 expected hits).  Two bugs the CPU emulation could not catch (a cupy array through `np.asarray`, `Event.elapsed_time`) were found by its first GPU run.  Next: the apply kernel with 16-byte loads (f5436df; 266 of 1,460 GB/s was latency), a staged generate kernel (9153752: marks sorted by bin in shared memory, whole runs written; pass B is 136-242 ms of the 373), the sieve overlapped with the Fermat rounds on a second stream (`overlap.py`) | `test_gbig.py`, `test_gbatch_cpu.py`, `test_deep_feeder_cpu.py` (CPU); `bench_bigprimes.py`, `bench_batch.py`, `sweep_bigprimes.sh` via `measure_all.sh` (GPU) |
| `sieve200/cuda/` (tools) | guesses about instruction costs | `sass.py` (NVRTC + nvdisasm: the SASS a GPU runs, no GPU), `bench_pipes.py` (instruction and memory costs on a GPU), `costmodel.py` (cycles a step from SASS and those costs: six A100 timings within 1.5% with one parameter), `measure_all.sh` (everything that needs a GPU, one command a GPU type) | `python3 costmodel.py` |

`sieve200/balance.py` answers "which sieve bound B": with a CPU feeder and a GPU tester of a few tens of million tests a second the best
B is 1e6 to 3e6 (deeper loses 5-15% to the CPU sieve), so `--sieve-b 1000000` stays *for a CPU feeder*; for the GPU feeder a deeper bound is worth x1.4 (1e7) to x1.9 (1e8) hit mass per test and the question is the cost of the primes above 1e6: `sieve200/cuda/DEEPSIEVE.md`.

## What was learned (and what it cost to find out)

* **Count first, then optimize.**  `search.run_block` spent 26% in the numpy sieve and 73% in gmpy2 tests, so the sieve drop-in alone gave
  1.3x, not the 2.4x that had been hoped for; the test kernel gave the next 10x.
* **Arrays indexed by a loop variable live in local memory on a GPU.**  `fermat2` kept `x` and `n` there: 190 `ld.local` for
  882 multiply-adds a step (found by compiling to PTX with clang for sm_80, no GPU needed).  A generated, fully unrolled step has none.
* **Reduced radix beats carry chains where a multiply-add into a 64-bit register is one instruction**: 28-bit limbs, 876 multiply-adds
  and no carry per product, against about 3.5 instructions a product for 32-bit limbs.  It only ties on sm_80/89, where the wide multiply
  appears to be half rate.
* **The sieve's cost is in the marks and the per-prime loop exits, not in the arithmetic.**  A constant trip count made the mark loop
  66% busier yet 23% faster (branch mispredictions at the exits); marks of the small primes done a 16 KB tile at a time and a
  7-instruction BMI2 loop gave a further 17-22%.  Per-(row, prime) set-up is vectorized (64 primes at a time, double reciprocal).
* **Measure interleaved.**  Timings on this VM drift by 20% over minutes; A/B/A/B rounds with the minimum are the only comparison that held up.
  A first-touch page fault in a VM costs far more than a cache miss: warm up before timing.
* **Count the loop body, not the file.**  Moving a carry chain from the end of the step to after the loop leaves the static instruction count of the whole
  kernel unchanged (my first comparison said "identical"); the inner loop went from 1,169 to 1,099 PTX instructions.  LLVM's NVPTX output puts
  `// =>This Inner Loop Header` after a label, so a parser that tests `line.endswith(':')` finds no loops: strip the comments first.
* **Compile for the real architecture and read the SASS** (`sieve200/cuda/sass.py`: NVRTC + nvdisasm, no GPU needed).  It showed that an explicit `mad.wide.u32` is two instructions a product on sm_80 / 89
  and one on sm_120; that LLVM hoists a loop-invariant `(u64) n_j` and turns `(u64) m * n_j` into `mul.lo.s64`, which ptxas answers with a dead `IADD3` a product (576 a step in fermat28);
  and that a micro-benchmark written in asm had its product hoisted out of the loop and measured nothing.  Check the SASS of a benchmark before running it.
* **A CPU emulation of a GPU program is only as honest as its fake of the library.**  My fake cupy had an `Event.elapsed_time` that real cupy does not have, and numpy lets `np.asarray` take a device
  array that cupy refuses: two bugs that every CPU test passed and the first GPU run found in a minute.  Look the API names up (a wheel of the real library is enough: `strings` on its modules)
  and make the fake raise where the real one raises.
* **Ask for the measurement in one command per GPU type** (`sieve200/cuda/measure_all.sh`: clocks and power during the kernel, memory rates, the new kernels with a correctness check, per-phase
  times): it returned in minutes what a dozen separate requests had not, and it found that the RTX PRO 6000 is NOT power-clocked (2,422 MHz, 418 W of 600), which closed one explanation and opened the real one.
* **An estimate from instruction counts and bandwidth is a lower bound on cost.**  I estimated the large-prime stage at 0.005-0.015 ns a mark; it measured 0.030 (pass B, the scattered 4-byte stores
  into bins larger than the L2 cache, and the apply kernel's one load in flight a thread, each ~3x off).  The estimate decided what to build; the measurement decided what to fix next.
* **Read a benchmark's raw rows, subtract what the benchmark itself adds, and test a model on data it was not tuned on.**  I modelled the Fermat step as bound by a multiplier pipe (too pessimistic about the ALU
  work), retracted a variant that removed ALU instructions, built a 31-bit-limb kernel with fewer multiplications, then read `bench_pipes.py` as "integer instructions add up, IMAD.WIDE ~2.4 cycles" (wrong the other
  way: its IMAD.WIDE rows contain the operand-bump IADD3, so the multiplier costs 4.15 / 4.5 cycles on sm_80 / 89, and ALU instructions overlap the multiplier pipe to about two thirds) and predicted +47% from removing
  600 dead adds a step on an A100 / L4; the GPU session measured +9-14%.  The refitted model T = max(T_mul, T_alu) + rho min(T_mul, T_alu) with the benchmark's costs and one parameter (rho = 0.35) reproduces six A100
  timings within 1.5% (`sieve200/cuda/costmodel.py`, `fermat661/cuda/FERMAT28.md`), including the older `fermat3`, a different algorithm.  It does not explain the RTX PRO 6000 (measured cycles 1.5x the model's at the
  nominal clock: the clock under load or something in the kernel; `measure_all.sh` samples the clock).
* **Mistakes that were caught by tests, not by reading**: a 10-plane vertical counter overflows above 1,023 rows (Q = 150,000 has 1,093);
  `fermat28`'s lazy reduction needs 16n < R, so n < 2^668 (669-bit inputs gave a wrong residue in 0.3% of cases, invisible in verdicts,
  which are 0 for almost every random number: the final residue 2^(1-n) mod n is what to compare).
