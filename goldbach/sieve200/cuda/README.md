# GPU sieve, counts, selection and survivor rows (for search_gpu3.py)

Replaces, per window of K members, `sieve_block` (sieve3: one thread per (row, prime), a 64-bit `%`, byte stores into a 28 MB
matrix), `alive.sum(axis=0)`, `cp.lexsort`, `alive[:, order].T` and `cp.nonzero` of `search_gpu3.py`.  **Verified on the CPU
(the same source text run by pthreads with real barriers and atomics: `test_gsieve.py`); never run on a GPU by its author.**

| file | what |
|---|---|
| `gsieve_kernels.cuh` | the four kernels (CUDA C++, also built as plain C++ by `gsieve_cpu.cpp`) |
| `gpu_sieve.py` | `GpuFeeder` (cupy): `window(k0)` returns the selected members' k, counts, CSR rows and the per-block statistics |
| `test_gpu_sieve.py` | on a GPU: identity with sieve200's CPU `Feeder` (itself identical to numpy and to `search.run_block`) and per-phase times |
| `gsieve_cpu.cpp`, `test_gsieve.py` | the CPU emulation and its test against sieve200 and numpy |

## The kernels

* `s200g_sieve`: one CTA per row; the K-bit alive map of the row (K = 2^klog, 32 KB for 2^18) in dynamic shared memory; each thread takes
  primes p, p + blockDim, ...: the first offset j = ((q - N0 mod s) M^-1 - k0) mod s with `q % s` only when q >= s and a Barrett
  reduction for the product (mu = floor((2^64-1)/s), `__umul64hi`, one conditional subtract), then `atomicAnd` on the shared word for
  j, j + s, ... < K.  The map goes to `bits[row][K/32]` once.  Per prime the global loads are S, M^-1 mod s, mu, N0 mod s, k0 mod s.
* `s200g_count`: a thread per 32 members, the rows added by a carry-save tree over 16 rows into a bit-sliced counter of 12 planes (up
  to 4095 rows), counts u16[K].
* `s200g_select`: a CTA per block of L = 2^llog members: histogram of the counts in shared memory, the threshold count and the number
  of members to take at it (hist scan), the kept members in index order by a block scan (all below the threshold, then the first
  `need` at it), a bitonic sort of the keys `count << 20 | index` (up to 8192 kept members; beyond that the caller sorts), and the
  statistics alive_total, hm_all, hm_kept.  The result is exactly `np.argsort(counts, kind="stable")[:ceil(L (1-f))]`.
* `s200g_rows`: a thread per kept member: its alive rows ascending, read from the bit matrix, written to `rows[offs[i]...]`.
* `s200g_km` (k0 mod s per prime), `s200g_finalize` (k, counts, member index and the CSR offsets by one scan, in a CTA), `s200g_n0m` (N0 mod s per prime,
  for `GpuFeeder.with_N0`): the glue that was a dozen small cupy launches.  A window is six launches and two small waits.

## Use

    fd = GpuFeeder.from_search_G(search.G, klog=18, llog=15, f=0.97, p_est=0.055)   # after search.init_spec(spec, B, block)
    w = fd.window(k0)       # w.k, w.cnt, w.offs, w.rows, w.block (device), w.alive_total, w.hm_all, w.hm_kept (numpy, per block)

Options of `GpuFeeder` (all give identical output; `test_gpu_sieve.py` sweeps them and checks that):

* `sieve_threads=1024`: the CTA size of the sieve kernel, separate from `nthreads` (select, rows, count, finalize: their time grows with the CTA size, keep 256).  On an A100 and an L4
  the sieve kernel got 1.5-1.8x faster from 256 to 1024 threads (more warps hide its latency); on an RTX PRO 6000 keep 256.
* `shoup=True` (default): the 32-bit setup.  The original kernel spends ~85 SASS instructions a prime on `q % s`, a 64-bit Barrett and the loop; the Shoup kernel (`s200g_prep`
  builds `TAB[p] = {s, M^-1, floor(M^-1 2^32 / s), c0 = (N0 M^-1 + k0) mod s}` once a window, `s200g_sieve_sh` takes `q M^-1 mod s = q M^-1 - mulhi(q, invp) s` minus s if >= s, then
  `(. - c0) mod s`) spends 35, 20 registers instead of 31 on sm_80 / 89 (`sass.py`).  Same bits (`test_gsieve.py`, also for q up to 2^32 - 1).  `shoup=False` is the original, for A/B.
* `unroll=1` (default), 2 or 3: marks a trip of the Shoup kernel's loop (3 sends the out-of-range second mark to a dummy shared word, no branch).  Fewer instructions a mark only on paper (8, 8.5, 7.5):
  a variant to time, not an expected win.
* `window(k0, timings=True)`: `w.timings` in ms: prep, sieve, count, select, finalize, `wait1` (the GPU's idle gap while the host reads the survivor-row count and allocates), rows, `wait2`
  (host time reading the statistics), `wall`, `host` = wall minus the GPU parts (launch and Python overhead).

`fd.with_variant(n0m, U)` makes the feeder of another variant (same M: the tables of primes, M^-1 mod s and mu are shared).  The caller adds
the variant's row offset to `w.rows` as it does for `nonzero`'s columns.  Run `python3 test_gpu_sieve.py spec.json --B 1000000` on the GPU host
(needs gcc for the CPU feeder it compares with, cupy, gmpy2, numpy, goldbach/search.py).

## Tests on the CPU

    python3 test_gsieve.py        # bits, counts, selection (nkeep from 1 to L), statistics and rows equal sieve200's / numpy's; the Shoup table, the Shoup kernel
                              # (CTA sizes 32 / 96 / 160 / compiled, unroll 1 / 2 / 3, q up to 2^32 - 1)
    python3 test_gpu_sieve_cpu.py # gpu_sieve.py's Python glue with the options, with cupy replaced by numpy + the emulation

## Looking at what a GPU would run, without a GPU

    python3 sass.py gsieve_kernels.cuh --arch sm_80 --kernel s200g_sieve -D KLOG=19 -D LLOG=15 -D NTHREADS=256 \
            -D 'S200G_DYNSHARED(type,name)=extern __shared__ type name[]' --loops

`sass.py` compiles a source with NVRTC for a real architecture (sm_80 A100, sm_89 L4, sm_120 RTX PRO 6000), disassembles the cubin with `nvdisasm` and prints the
instruction counts of every kernel and of every loop, with the registers and spills `ptxas -v` reports (the docstring says where the three tools come from:
two PyPI wheels and one NVIDIA redistributable, all downloadable on a CPU box).  What it showed so far:

* `s200g_sieve` is 31-33 registers, no spills, so shared memory (64 KB a CTA at klog 19) sets its occupancy: 2 CTAs an SM on an A100, 1 on an L4 and an RTX PRO 6000.
  A prime costs about 85 instructions (the `q % s` division, a 64-bit Barrett with 7 IMAD.WIDE) and a mark 8 (shift, mask, rotate, `ATOMS.AND`, add, compare, branch).
* the Fermat step loops of `fermat28`, `fermat3`: see `../../fermat661/cuda/FERMAT28.md`, "Where the time goes".

`bench_pipes.py` measures, on a GPU, how many cycles a warp-level `IMAD.WIDE.U32`, `IMAD`, `IADD3`, `IADD3.X`, `LOP3`, `SHF` occupy a scheduler for, how many adds fit beside one
`IMAD.WIDE` for free, and what `ATOMS.AND`, `STS.32`, `STS.U8`, `LDS` and a plain read-modify-write cost with random and with conflict-free addresses at the shared-memory
sizes of klog 17, 18 and 19.  `python3 bench_pipes.py --check sm_80` (no GPU) prints the SASS loop of every kernel, to see that it measures what it names.

## A deeper sieve bound (prototype, not in production): see DEEPSIEVE.md

| file | what |
|---|---|
| `gbig_kernels.cuh`, `gbig.py` | the large-prime stage: each (row, prime above the tile) pair visited once per 2^25-member batch, marks counted and written into (row, tile) bins; `gbig_apply` applies a bin to a shared bitmap |
| `gbatch_kernels.cuh`, `gbatch.py` | `s200g_tile` (small-prime marks + the bin of the same (row, tile) on one shared bitmap, tile written into the batch matrix) and `BatchFeeder` (a `GpuFeeder` whose window is a batch) |
| `bench_bigprimes.py` | **ns a mark** of the large-prime stage with the pass A / pass B / apply split (the number the question "does a deep bound pay?" needs) |
| `bench_batch.py` | the whole batch pipeline at production size, per-phase times, check against the CPU feeder, `--sweep` of row-group and CTA sizes |
| `bench_pipes.py` part 3 | the memory-system rates behind it: scattered atomicAnd / store / load in 64 MB .. 4 GB, 128-byte runs, copy bandwidth |
| `test_gbig.py`, `test_gbig_cpu.py`, `test_gbatch_cpu.py`, `test_bench_batch_cpu.py` | on a CPU: identical to a brute-force reference and to sieve200's CPU Feeder (several geometries, row groups, overflow and retry), glue under a fake cupy |
