# fermat28: a GPU base-2 Fermat kernel for numbers of up to 668 bits (24 limbs of 28 bits)

A drop-in replacement for `fermat2` of `goldbach/phd/campaign3_gpu/gpu_fermat.py`: same kernel arguments `(CQ, Mv, idx, kv, out, T)`,
same 21 x u32 limb layout for `CQ` and `Mv`, same meaning of `out` (1 iff 2^(n-1) = 1 mod n; here also 2 for an n outside
2^642 <= n < 2^668 or an even n).  **Verified on a CPU, never run on a GPU by its author: the speed is for the GPU session to measure.**

| file | what |
|---|---|
| `gen_fermat28.py` | writes `fermat28_step*.cuh`, one Montgomery squaring step as straight-line code (`python3 gen_fermat28.py 2`) |
| `fermat28_step.cuh`, `_s1`, `_s4` | the generated step with 2, 1 or 4 independent 64-bit accumulators per column (a longer dependent chain of multiply-adds against 2 more adds per column) |
| `fermat28_step_r.cuh`, `_s1r` | the same with **redundant limbs** (2 and 1 accumulators): no carry chain after the doubling, limbs left below 2^29, one normalising chain in the kernel after the last step (`#define FM28_REDUNDANT`, set by the step file); 70 of the 1,169 PTX instructions of a step less (`python3 gen_fermat28.py 2 fermat28_step_r.cuh redundant`) |
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

## Redundant limbs (`fermat28_step_r.cuh`, `fermat28_step_s1r.cuh`): fewer instructions, but no speed-up expected

The last thing the step does is the carry chain `x[i] = ((y_i << b) + carry) & MASK28` (24 x add, and, shift, about 70 instructions of the
1,169 in a step).  It is not needed to keep the numbers in range: **leave `x_i = y_i << b`**, which is below 2^29 and has the value 2^b Y exactly.
The next step only needs the limbs small enough that no 64-bit column overflows, so the change to the proof of the step is:

* (C1) and (C2) are unchanged: they use only the value X < 4n (here X = sum x_i B^i = 2^b Y < 4n) and the exact division by R.
* (C3') no overflow with limbs below 2^29: a doubled product d_i x_j = 2 x_i x_j < 2^30 * 2^29 = 2^59 (at most 12 per column), the diagonal
  x_i^2 < 2^58, a reduction product m_i n_j < 2^56 (m, n have limbs below 2^28; at most 24 per column), the carry < 2^36:
  12 * 2^59 + 2^58 + 24 * 2^56 + 2^36 < 15.5 * 2^59 + 2^36 < 2^63 (about 2^62.96).  The 32-bit value `acc mod 2^32` that feeds m_k is still exact.
* The output limbs are y_i << b < 2^29 (y_i = acc mod B < 2^28, and y_23 = acc < B because Y_pre < 2n < R), so the invariant of the loop is
  "limbs < 2^29, value < 4n" instead of "limbs < 2^28, value < 4n".  The start value 2^(672-c) has one nonzero limb below 2^28.
* After the last step the kernel runs one carry chain (`#ifdef FM28_REDUNDANT` in `fermat28_kernel.cuh`), which brings the limbs below 2^28 for the final
  reduction and comparison; the value is unchanged, so the verdict and the residue are the same bit for bit.

`FM28_STEP=fermat28_step_s1r.cuh python3 test_step28.py` checks C1/C2/C3' on 12,088 steps: the 6,070 of the default files, and 6,000 inputs whose
carries are partly left in the limbs (limbs up to 2^29 - 1), among them the extremes of C3' (limbs 0..22 all at 2^29 - 1 and the top limb as large
as X < 4n allows): wrong 0, largest Y/n 3.959 (< 4).
`FM28_STEP=fermat28_step_s1r.cuh python3 test_fermat28.py` and `FM28_STEP=fermat28_step_r.cuh python3 test_fermat28.py` pass everything the
other files pass (3,000 residues, primes, pseudoprimes, edge values, campaign-3 numbers).  **The proof in the section above is for the
default files (limbs < 2^28); the redundant ones change the invariant and the bound C3, so they need the paragraph above to be checked too.**
**Do not expect it to be faster**: the SASS says why (next section).  It removes ALU instructions (the carry chain), and the step is limited by the
wide multiplier, not by the ALU; the 876 multiply-adds are unchanged.  `test_gpu_fermat28.py` has "s1r" and "s2r" rows if someone wants to see it.

## Where the time goes (SASS, from `../../sieve200/cuda/sass.py`: NVRTC 12.9 for the real architecture, then `nvdisasm`; no GPU needed)

The step loop (one squaring step, the loop with the largest body) as the GPU runs it, and the registers `ptxas -v` reports (no spills in any):

| arch | variant | instructions a step | IMAD.WIDE | other IMAD | IADD3 / IADD | registers |
|---|---|---|---|---|---|---|
| sm_80 / sm_89 | s1 plain | 1798 | 876 | 52 | 579 | 110 |
| sm_80 / sm_89 | s1 asm | 2063 | 876 | 75 | 464 + 425 IADD3.X-class | 92 |
| sm_80 / sm_89 | s1r plain / asm (redundant limbs) | 1752 / 2016 | 876 | 53 / 76 | | 112 / 96 |
| sm_120 | s1 plain | 1276 | 876 | 24 | 100 | 100 |
| sm_120 | s1 asm | 1151 | 876 | 24 | 28 | 90 |
| sm_120 | s1r asm | 1104 | 876 | 24 | 28 | 88 |
| sm_80 / sm_89 | fermat3 (`gpu_fermat3.py`) | 2328 | 651 | 579 (435 of them IMAD.X) | 751 | 128 |
| sm_120 | fermat3 | 3196 | 651 | 43 | 5 (+ 2,497 MOV / IADD / HFMA2) | 144 |

* On sm_80 / sm_89 an explicit `mad.wide.u32` (the "asm" variants) is lowered by ptxas to `IMAD.WIDE.U32 Rd, Ra, Rb, RZ` plus a 3-input `IADD3` / `IADD3.X` pair
  for two products: about 2 instructions a product, 2063 a step.  The plain C form `acc += (u64) a * b` becomes one `IMAD.WIDE.U32 Rd, Ra, Rb, Rd` (the
  accumulator is the addend): 1798 a step.  On sm_120 both are one instruction per product.  So on A100 and L4 use the plain variants, not "asm".
* **A model that fits six measurements** (A100, L4, RTX PRO 6000 x fermat3, fermat28; the speeds are the GPU session's): a warp-level `IMAD.WIDE` occupies the
  multiplier pipe of a scheduler for about 4 cycles, any other IMAD flavour (IMAD.X, IMAD.MOV, IMAD.SHL) for 2, and the ALU instructions (IADD3, SHF, LOP3,
  ISETP ...) use a separate pipe at 2 cycles each.  A step then costs 4 x IMAD.WIDE + 2 x other IMAD cycles on the busier pipe: fermat28 3,552-3,608, fermat3
  3,762 on sm_80 / 89.  With 655 steps a test and SMs x 4 schedulers x clock, that predicts 8.2M tests/s on the A100 (measured 6.95M for fermat28, 6.94M for
  fermat3, which the model also predicts to be a tie), 24.8M on the RTX PRO 6000 for fermat28 (measured 22.86M), 6.4M on an L4 at its nominal clock (measured
  4.0M, power-limited).  It does not fit fermat3 on sm_120 (the ALU and move instructions bind there).
* If the model is right: **cutting multiplications is the only thing that makes this kernel faster; cutting ALU instructions does nothing** (hence the redundant limbs
  do nothing), and ALU work up to about 2 instructions per multiplication removed is free.  `bench_pipes.py` (in `../../sieve200/cuda`) measures the pipe rates
  directly; run it before building anything on the model.

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
