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

## Use

    fd = GpuFeeder.from_search_G(search.G, klog=18, llog=15, f=0.97, p_est=0.055)   # after search.init_spec(spec, B, block)
    w = fd.window(k0)       # w.k, w.cnt, w.offs, w.rows, w.block (device), w.alive_total, w.hm_all, w.hm_kept (numpy, per block)

`fd.with_variant(n0m, U)` makes the feeder of another variant (same M: the tables of primes, M^-1 mod s and mu are shared).  The caller adds
the variant's row offset to `w.rows` as it does for `nonzero`'s columns.  Run `python3 test_gpu_sieve.py spec.json --B 1000000` on the GPU host
(needs gcc for the CPU feeder it compares with, cupy, gmpy2, numpy, goldbach/search.py).

## Tests on the CPU

    python3 test_gsieve.py        # bits, counts, selection (nkeep from 1 to L), statistics and rows equal sieve200's / numpy's
