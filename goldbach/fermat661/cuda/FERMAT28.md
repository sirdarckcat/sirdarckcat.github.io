# fermat28: a GPU base-2 Fermat kernel for numbers of up to 668 bits (24 limbs of 28 bits)

A drop-in replacement for `fermat2` of `goldbach/phd/campaign3_gpu/gpu_fermat.py`: same kernel arguments `(CQ, Mv, idx, kv, out, T)`,
same 21 x u32 limb layout for `CQ` and `Mv`, same meaning of `out` (1 iff 2^(n-1) = 1 mod n; here also 2 for an n outside
2^642 <= n < 2^668 or an even n).  **Verified on a CPU, never run on a GPU by its author: the speed is for the GPU session to measure.**

| file | what |
|---|---|
| `gen_fermat28.py` | writes `fermat28_step*.cuh`, one Montgomery squaring step as straight-line code (`python3 gen_fermat28.py 2`) |
| `fermat28_step.cuh`, `_s1`, `_s4` | the generated step with 2, 1 or 4 independent 64-bit accumulators per column (a longer dependent chain of multiply-adds against 2 more adds per column) |
| `fermat28_kernel.cuh` | the kernel: n = cq + M k, setup, the step loop, the final test |
| `gpu_fermat28.py` | `kernel(limbs, step_file=..., asm_mad=...)`, `Tester`, `MultiTester` (checks the range of the whole pool), `to_limbs` |
| `test_gpu_fermat28.py` | on a GPU: mismatches against gmpy2, registers and local memory of every variant, tests/s of every variant against `fermat2` |
| `fermat28_cpu.cpp`, `test_fermat28.py`, `test_step28.py` | the same source compiled with g++ and tested on the CPU against Python `pow` and big-integer arithmetic |

## What is different from `fermat2`, and why it should be faster

1. **Reduced radix.** Limbs of 28 bits, so a 32x32 -> 64 product is below 2^56 and a whole column of up to 49 of them, plus the
   carry, stays below 2^62: every product is one 64-bit multiply-add into a register (`IMAD.WIDE.U32`), with no carry chain and no
   carry extraction per product.  The carry between columns is one shift of the column's accumulator.  `fermat2` does a 64-bit
   `t[j] + a x[j] + c` with two further adds per product.
2. **Dedicated squaring.** The off-diagonal products x_i x_j (i < j) once, with x_i doubled in advance (`d_i = 2 x_i`, 29 bits), plus the
   diagonal: 300 products, then the reduction 576: 876 multiply-adds a step, against 882 products in `fermat2` of which 441 are the
   product row and 441 the reduction, each with its adds.
3. **No local memory in the loop.** In `fermat2` the arrays `x` and `n` are indexed with runtime loop variables, so the compiler keeps
   them in local memory: compiling it with clang for sm_80 (`clang++ -x cuda --cuda-device-only`) gives a 168-byte stack frame with 190
   `ld.local` and 188 `st.local` in the code, roughly one local load per multiply-add.  Here all indices are static (the step is
   generated, fully unrolled); the only local array is the 84-byte exponent `bt`, read once every 32 steps (1 `ld.local`).  Check with
   `kernel(21).attributes['local_size_bytes']` for both.
4. **No per-step compare and subtract.** Values stay below 4n (R = 2^672 > 16 n for n < 2^668): the step returns a value below 4n for an input below 4n.
5. **The exponent bit is a shift in the step** (`(y << b) + carry` in the final carry chain), so there is no divergent branch and no
   separate doubling routine.
6. **No R mod n.** `fermat2` does 672 doublings modulo n (about 100,000 instructions, ~5% of a test) to get Montgomery 1.  Here, as in
   `goldbach/fscan/fm_common.h`, the residue is kept as a power of two: the start value is 2^(672-c) and the exponent bits are those of
   c 2^t - (n + 671), with t = bits(n) - 6 steps and c = ceil((n + 671) / 2^t); after the t steps y = 2^(1-n) mod n, which is 1 iff
   n is a base-2 probable prime.  6 squarings fewer, and the setup is a few dozen limb operations.

## The step (`fm28_step`), for a proof

Notation: B = 2^28, R = B^24 = 2^672, n odd with 2^642 <= n < 2^668, n' = -n^-1 mod B (three Newton steps from the 5-bit seed
(3 n_0) xor 2 give 40 correct bits), X = sum x_i B^i with x_i < B and X < 4n.

* column k (0 <= k <= 23): acc += sum_{i < k-i} (2 x_i) x_(k-i) + [k even] x_(k/2)^2 + sum_{i < k} m_i n_(k-i);
  m_k = ((acc mod 2^32) n') mod B; acc += m_k n_0; acc >>= 28.
* column k (24 <= k <= 46): the same sums with i and k-i <= 23, no m_k; limb y_(k-24) = acc mod B; acc >>= 28.
* y_23 = acc; then Y = 2^b sum y_i B^i by one carry chain (b in {0, 1}).

(C1) exactness: after the products and m_k n_0 the low 28 bits of acc are zero (n_0 n' = -1 mod B), so `>> 28` is the exact carry, and
sum_k (column k) B^k = X^2 + mu n with mu = sum m_i B^i < R, divisible by R: Y_pre = (X^2 + mu n) / R, and Y = 2^b X^2 R^-1 mod n.
(C2) range: Y_pre < (X^2 + R n) / R = n + X^2 / R < n + 16 n^2 / R < 2n because 16 n < R, so Y < 4n; Y < 2^670 < R, so the final
carry is 0 and every limb is below B.  The step maps {X < 4n} to itself.
(C3) no overflow: a product d_i x_j < 2^57, x_i x_j and m_i n_j < 2^56; a column holds at most 12 of the first kind, 1 diagonal,
24 reduction products and the carry (< 2^35): below 49 * 2^56 < 2^62.
(C4) the start value 2^(672-c) with 32 <= c <= 65 (c = ceil((n + 671) / 2^(bits(n) - 6))) is below n/2, and with v = log2(y) - 672 a step is
v -> 2v + b, so after t steps v = -c 2^t + B_t = -(n + 671), y = 2^(1-n) (mod n).  `test_step28.py` checks C1/C2 on 6,070 random and
adversarial inputs (limbs all ones, X near 4n, n near 2^668: the largest Y/n seen is 3.857).

## Verified on the CPU (the same source text, `fermat28_cpu.cpp`)

`python3 test_fermat28.py`: the final residue 2^(1-n) mod n of 3,000 random n of 642 to 668 bits equals Python's `pow(2, 1-n, n)` (this
catches a wrong carry that a verdict, which is 0 for nearly every random number, would hide); the verdict on random odd n of 668
down to 642 bits, 100 primes, 12 base-2 pseudoprimes, edge values (2^664 +- 1, 2^668 - 1, 2^642 + 1 ...), out-of-range and even n (flag 2);
n = N0 - q + k M of campaign 3 with k in [2^31, 2^32), [2^28, 2^31) and small k, and 40 real primes of that form (all pass).
`python3 test_step28.py`: the step alone.  Both pass for 1, 2 and 4 accumulators per column.

## Not verified here

Compilation by NVRTC (clang compiles the same source to PTX for sm_80 without errors, both with `asm_mad` and without), anything about speed, register count and occupancy
(my estimate is about 125 registers a thread), and whether a 17 KB straight-line step hurts the instruction cache.  If it does, the generator
can be changed to roll the reduction loop.  Things to try, in this order: `python3 test_gpu_fermat28.py specs_variants.json` (prints every
variant's registers, local bytes and tests/s next to `fermat2`); 64 / 128 / 256 threads per block; `asm_mad=True`; 1 / 2 / 4 accumulators.
