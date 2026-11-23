# fermat31: a GPU base-2 Fermat kernel with 22 limbs of 31 bits (737 wide multiplications a step instead of 876): correct, and predicted NOT faster

Same job and same interface as `fermat28` (`kernel(limbs, step_file=...)`, `Tester`, `MultiTester`, `to_limbs` in `gpu_fermat31.py`; the kernel arguments, the
21 x u32 input limbs and the flags `out[t]` = 1 / 0 / 2 are fermat28's; valid for odd n with 2^642 <= n < 2^668).  **Verified on a CPU, never run on a GPU.**

**Result so far: a negative one, kept because the reason is useful.**  It was written on the belief that the multiplier pipe is the bottleneck (so that carry-handling ALU instructions are free);
a first reading of `bench_pipes.py` seemed to refute that (ALU instructions *add* to the multiplications) and put the prediction at +0% / +34% slower; **the refitted model of `FERMAT28.md` (2026-11-23:
IMAD.WIDE costs 4.15 / 4.5 / 2.5 cycles on the A100 / L4 / RTX PRO 6000, not 2.3 / 2.4 / 2.5; ALU work overlaps the multiplier pipe to about two thirds, and it reproduces six measured A100 timings within
1.5%) predicts fermat31 at +4.6% tests/s on an A100 against the best fermat28 (s1r plain + w), -3% on an L4 and ~33% slower on an RTX PRO 6000 (the additive refit of 2026-11-23 04:07Z; ~20% in the first fit)** (fermat30: +1.6% / -2% / -24%).  Same verdict, a
different reason: the ~1,000 ALU instructions its carries need do not hide under the 139 multiplications they save.  It is there to be timed if someone wants to test the model
(`test_gpu_fermat31.py` times it beside fermat28 in the same run); it should not go into production.

## Why it was tried

fermat28 needs 876 wide multiplications a step (24 limbs of 28 bits: 300 for the squaring, 576 for the Montgomery reduction).  With 22 limbs of 31 bits it is 253 + 484 = 737 (-15.9%), with 23 limbs of 30 bits
276 + 529 = 805 (-8.1%).  The price is carries: a product of two 31-bit limbs is below 2^62, so a 64-bit register holds 4 of them, not 49, and the products are summed in groups through a 96-bit column sum.
A multiplication saved costs 4.15 cycles on an A100 (2.5 on an RTX PRO 6000), an ALU instruction added about 2.1 of which a third shows (the rest hides under the multiplier pipe), and the carries add 1.4 of them per multiplication saved: a gain of a few % on an A100, a loss elsewhere.

## The step (`gen_fermat31.py`, `fm31_step`)

Notation: B = 2^31, NL = 22, R = B^22 = 2^682, n odd, 2^642 <= n < 2^668 (so 16 n < R with room to spare), n' = -n^-1 mod 2^32, X = sum x_i B^i, x_i < B, X < 4n.

* column k (0 <= k <= 21): s = carry_in + 2 sum_{i<j, i+j=k} x_i x_j + x_(k/2)^2 + sum_{i<k} m_i n_(k-i); m_k = ((s mod 2^32) n') mod B; s += m_k n_0; carry = s >> 31.
* column k (22 <= k <= 42): the same with i, j <= 21 and no m_k; the output limb k-22 is s mod B; carry = s >> 31.  The last output limb is the carry.
* then Y = 2^b sum y_i B^i by one carry chain (y_i 2^b < 2^32: no overflow).
* **products** are added in groups of 4 through one 64-bit register (`g = a*b; g += c*d; ...`: one `IMAD.WIDE.U32` each with the group as the addend; 4 (2^31 - 1)^2 < 2^64),
  and each group is added to a **96-bit column sum** (three u32, a PTX `add.cc / addc.cc / addc` chain: `IADD3`, `IADD3.X`, `IADD3.X`).  The cross terms are summed first, the sum is doubled
  (three funnel shifts), then the diagonal, the carry and the reduction products are added.  A column sum is below 2 * 11 * 2^62 + 2^62 + 22 * 2^62 + 2^38 < 2^68, so 96 bits are plenty.
* (C1) exactness: after m_k n_0 the low 31 bits of the column sum are zero (n_0 n' = -1 mod 2^31), so the shift is the exact carry and sum_k (column k) B^k = X^2 + mu n with
  mu = sum m_i B^i < R: Y_pre = (X^2 + mu n) / R and Y = 2^b X^2 R^-1 mod n.  (C2) range: Y_pre < n + X^2 / R < n + 16 n^2 / R <= n (1 + 2^-10), so Y < 2.01 n: values stay below 4n
  (the test's largest Y/n is 2.0005).  (C3) limbs: every output limb is below 2^31 before the doubling; the carry chain brings y_i 2^b back below 2^31.
* R = 2^682 is larger than fermat28's 2^672, which changes the start of the exponentiation: t = bits(n) - 7 squarings (one fewer than fermat28's bits - 6), the start value is
  2^(682 - c) with c = ceil((n + 681) / 2^t) in [64, 130] (fermat28: c in [32, 65]; with R = 2^682 and c = 32 the start value would exceed 4n for the smallest n), and the exponent bits
  c 2^t - (n + 681) sit in a 22-word buffer (704 bits) with bit t-1 at bit 703.

`fermat30_step.cuh` is the same with 23 limbs of 30 bits (R = 2^690): operands are doubled in advance (d_i = 2 x_i < 2^31, d_i x_j < 2^61), groups of 8 cross / 16 other products.

## Details that cost something to find (SASS, `../../sieve200/cuda/sass.py`)

* LLVM hoists `(u64) n_j` out of the step loop (n does not change), so `(u64) m_i * n_j` becomes `mul.lo.s64` with one operand an opaque 64-bit register; on sm_80 / 89 ptxas
  implements that as `IMAD.WIDE.U32` plus a **dead `IADD3 hi, hi, UR`** (a uniform register that is zero): one useless ALU instruction a reduction product (484 here, 576 in fermat28's plain
  variants; the 31-bit step went from 2,288 to 1,773 instructions without them).  The step file uses an explicit `mul.wide.u32` (`FM31_MULW`) for the products with n.
* Group of 4 compiles as `IMAD.WIDE.U32 g, a, b, RZ` then `IMAD.WIDE.U32 g, c, d, g` ...: one instruction a product, as wanted.

## Numbers from the compiler (not from a GPU)

Step loop of the whole kernel, `ptxas -v` registers (no spills; a 176-byte stack frame holds the exponent words and is read once per 32 steps), and the cost model of `FERMAT28.md`:

| arch | kernel | instructions a step | IMAD.WIDE | model cycles a step (refitted, `costmodel.py`) | predicted tests/s | registers |
|---|---|---|---|---|---|---|
| sm_80 | fermat28 s1r plain + w (the A100's production kernel) | 1151 | 876 | 3817 | 7.64M (measured 7.63M) | 94 |
| sm_80 | fermat31 | 1793 | 737 | 3651 | 7.99M (+4.6%) | 96 |
| sm_80 | fermat30 | 1549 | 805 | 3755 | 7.76M (+1.6%) | 94 |
| sm_89 | fermat28 s1r plain + w (the L4's) | 1151 | 876 | 4268 | 4.65M (measured 4.62M) | 94 |
| sm_89 | fermat31 / fermat30 | 1793 / 1549 | 737 / 805 | 4383 / 4369 | 4.52M / 4.54M (-3% / -2%) | 96 / 94 |
| sm_120 | fermat28 s1r asm (the RTX PRO 6000s' kernel) | 1104 | 876 | 3811 (additive fit, `costmodel.py`) | 23.4M (measured 23.29M) | 88 |
| sm_120 | fermat31 | 1831 | 737 | 5717 | 15.6M (-33%) | 128 |
| sm_120 | fermat30 | 1548 | 805 | 2941 | 20.15M (-14%) | 94 |

(The sm_120 rows were rewritten 2026-11-23 04:07Z: the clock is not a fit (clock64 counts SM cycles at 2.43 GHz) and the model is the additive 3.64 x IMAD.WIDE + 2.79 x other, see `FERMAT28.md`; the A100 and L4 rows are predictions for kernels nobody has timed.)

## Verified on the CPU (`fermat31_cpu.cpp`: the same step and kernel text; the PTX carry chain and `mul.wide` are replaced there by portable C)

* `python3 test_step31.py` (and `FM31_W=30 python3 test_step31.py`): the step alone against big-integer arithmetic on 6,076 random and adversarial inputs (limbs all ones, X near 4n,
  n near 2^668): output below 4n, limbs below 2^31 (2^30), congruent to 2^b X^2 R^-1 mod n.  Wrong 0, largest Y/n 2.0005.
* `python3 test_fermat31.py [--count N]` (and `FM31_W=30`): the final residue 2^(1-n) mod n of 6,000 random n of 642..668 bits equals Python's `pow(2, 1-n, n)`; the verdict on random odd
  n of every bit length, 50 primes, 12 base-2 pseudoprimes, edge values, out-of-range and even n (flag 2), campaign-3 numbers N0 - q + kM with k in [2^28, 2^32) and 40 real primes.  All pass.
* the full kernel compiles with NVRTC 12.9 for sm_80, sm_89 and sm_120 (`sass.py`, with `-D` nothing needed); `ptxas -v`: no spills.

## Not verified here

* Anything about speed (the prediction above is a model fitted to the benchmark; a run of `test_gpu_fermat31.py` would test it: it predicts fermat31 at about 0.67x fermat28 s1r asm on an RTX PRO 6000 and +4.6% against s1r plain + w on an A100).
* The two PTX snippets: `FM31_ADD96` (`add.cc.u32 / addc.cc.u32 / addc.u32`) and `fm31_mulw` (`mul.wide.u32`).  The compiler's SASS for them is the expected `IADD3` / `IADD3.X` / `IADD3.X`
  and `IMAD.WIDE.U32`, but only a GPU run checks the carries: `python3 test_gpu_fermat31.py specs_variants.json` compares with gmpy2 (it must print `mismatches 0`) and times every variant
  against fermat28 (s1 plain / asm, s2), fermat3 and fermat2 for 64 / 128 / 256 threads a block, with the register caps 72 and 96 as variants.
