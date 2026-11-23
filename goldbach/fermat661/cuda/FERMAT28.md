# fermat28: a GPU base-2 Fermat kernel for numbers of up to 668 bits (24 limbs of 28 bits)

A drop-in replacement for `fermat2` of `goldbach/phd/campaign3_gpu/gpu_fermat.py`: same kernel arguments `(CQ, Mv, idx, kv, out, T)`,
same 21 x u32 limb layout for `CQ` and `Mv`, same meaning of `out` (1 iff 2^(n-1) = 1 mod n; here also 2 for an n outside
2^642 <= n < 2^668 or an even n).  **Verified on a CPU, never run on a GPU by its author: the speed is for the GPU session to measure.**

| file | what |
|---|---|
| `gen_fermat28.py` | writes `fermat28_step*.cuh`, one Montgomery squaring step as straight-line code (`python3 gen_fermat28.py 2`) |
| `fermat28_step.cuh`, `_s1`, `_s4` | the generated step with 2, 1 or 4 independent 64-bit accumulators per column (a longer dependent chain of multiply-adds against 2 more adds per column) |
| `fermat28_step_s1w.cuh`, `_w`, `_s1rw` | the same with an explicit `mul.wide.u32` for the products m_i n_j (`gen_fermat28.py ... mulw`): **600 fewer SASS instructions a step on sm_80 / 89** (see "Where the time goes") |
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

## Redundant limbs (`fermat28_step_r.cuh`, `fermat28_step_s1r.cuh`): 46-47 instructions fewer a step, about +2%

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
other files pass (3,000 residues, primes, pseudoprimes, edge values, campaign-3 numbers).  **Proved in Lean since 2026-11-23**
(the Lean session, commit 0c6933f on branch ccr-36ca7b46-8twf14, `goldbach/lean/GoldbachGaps/Gpu28/`: `Step.lean` `pre_spec`, `stepR_spec`; `Kernel.lean` `normLimbs_spec`, `fermat28r_correct`):
for limbs below 2^29 and value below 4n the step gives limbs below 2^29 and value below 4n, the FM28_REDUNDANT normalisation keeps the value, and the verdict is 1 iff 2^(n-1) = 1 mod n; their `gpu28_check/run.sh`
also runs all eight step files through the CPU build against big integers and the Lean model.  Assumed there: the set-up between n32 and the loop, and that `mul.wide.u32` and `mad.wide.u32` are the exact
32 x 32 -> 64 product and multiply-add (the PTX path itself is checked only on a GPU: the GPU session's `test28_prod.py`).  The proof of the default files (above) is unchanged.
It removes the carry chain (24 adds, 24 masks, 24 shifts, replaced by 24 shifts): 46 of 1,798 SASS instructions on sm_80 / 89, 47 of 1,151 on sm_120 ("s1 asm").  By the cost model in the
next section that is about +2% (not the +4% first guessed, not the 0% of the first retraction).  `test_gpu_fermat28.py` has the "s1r" and "s2r" rows.

## Where the time goes (SASS from `../../sieve200/cuda/sass.py`; instruction costs measured by `../../sieve200/cuda/bench_pipes.py` on the three GPU types)

The step loop (one squaring step) as the GPU runs it, from NVRTC 12.9 + `nvdisasm` for the real architecture; `ptxas -v` reports no spills in any variant:

| arch | variant | instructions a step | IMAD.WIDE | IADD3 | registers |
|---|---|---|---|---|---|
| sm_80 / sm_89 | s1 plain | 1798 | 876 | 579 (+46 IADD3.X) | 110 |
| sm_80 / sm_89 | **s1 plain + w** (`fermat28_step_s1w.cuh`) | **1198** | 876 | 49 | 96 |
| sm_80 / sm_89 | s1r plain + w (`..._s1rw.cuh`, redundant limbs too) | 1151 | 876 | 49 | 94 |
| sm_80 / sm_89 | s1 asm | 2063 | 876 | 464 + 425 IADD3.X | 92 |
| sm_120 | s1 plain | 1276 | 876 | 100 | 100 |
| sm_120 | s1 plain + w | 1197 | 876 | 28 | 96 |
| sm_120 | s1 asm | 1151 | 876 | 28 | 90 |
| sm_120 | s1r asm | 1104 | 876 | 28 | 88 |

* **Dead adds.**  LLVM hoists `(u64) n_j` out of the step loop (n does not change), so `(u64) m_i * n_j` becomes `mul.lo.s64` with one operand an opaque 64-bit register (577 of them
  in the PTX of the plain steps, one per reduction product); on sm_80 / 89 ptxas implements that as `IMAD.WIDE.U32` plus a **dead `IADD3 hi, hi, UR`** (a uniform register that is zero) and some
  extra 64-bit shifts.  The "w" steps (`python3 gen_fermat28.py 1 fermat28_step_s1w.cuh mulw`) use an explicit `mul.wide.u32` (`FM28_MADN`) for the products with n and the plain form for the others:
  **1,198 instructions instead of 1,798 on sm_80 / 89, 1,197 instead of 1,276 on sm_120.**  Same arithmetic, so the same results: `test_step28.py` and `test_fermat28.py` pass for them (6,070 exact steps, 1,500 exact residues,
  primes, pseudoprimes, real primes).
* **An explicit `mad.wide.u32` (the "asm" steps) is lowered on sm_80 / 89 to `IMAD.WIDE.U32 Rd, Ra, Rb, RZ` plus a 3-input `IADD3` / `IADD3.X` pair for two products**: 2063 instructions a step,
  worse than plain.  On sm_120 it is one instruction a product and the best of the unmodified steps.
* **Instruction costs** (`../../sieve200/cuda/bench_pipes.py` part 1, measured by the GPU session: scheduler cycles one warp instruction occupies; 4 CTAs x 256 threads an SM).  The raw rows; the two
  IMAD.WIDE rows contain the IADD3 that bumps an operand so that the product cannot be hoisted:

  | row | RTX PRO 6000 (sm_120) | A100 (sm_80) | L4 (sm_89) |
  |---|---|---|---|
  | IMAD.WIDE+acc, 1 bump | 4.35 | 6.29 | 6.65 |
  | IMAD.WIDE+acc + k IADD3 (k = 1 / 2 / 3 / 4) | 6.62 / 8.51 / 10.43 / 12.24 | 8.55 / 10.84 / 12.74 / 14.79 | 8.84 / 10.63 / 12.58 / 14.72 |
  | IMAD (32-bit) +acc | 2.02 | 2.05 | 2.04 |
  | IADD3 | 1.82 | 2.14 | 2.14 |
  | IADD3 + IADD3.X (a 64-bit add) | 2.81 | 3.13 | 3.14 |
  | SHF | 1.82 | 2.13 | 2.13 |
  | LOP3 | 0.75 | 1.07 | 1.07 |

  So **IMAD.WIDE.U32 with the addend alone costs 2.5 (RTX PRO 6000), 4.15 (A100) and 4.5 (L4) cycles** (the first row minus one IADD3), and in that benchmark every added IADD3 adds ~2 cycles.
  *Correction (2026-11-23):* until then this file listed 2.3 and 2.4 for the A100 and L4, a transcription error of mine.  It made the multiplier 45% too cheap on sm_80 / 89 and is why the "w"
  steps were predicted at +47% tests/s there (measured: +10% on the A100, +17% on the L4, +2.4% for s1r asm on the RTX PRO 6000).

* **Measured speeds** (the GPU session's `test_gpu_fermat28.py`, 128 threads a CTA, 2026-11-23 00:17Z):

  | tests/s | fermat3 (the older kernel) | s1 plain | s1 plain + w | s2 plain + w | s1r plain + w | s1 asm | s1r asm |
  |---|---|---|---|---|---|---|---|
  | A100 | 6.94M | 6.95M | 7.55M | 7.51M | 7.63M | | 6.95M |
  | L4 | 3.92M | 4.00M | 4.57M | | 4.62M | | |
  | RTX PRO 6000 | 13.08M | | | | 22.74M | 22.85M | 23.39M |

* **The cost model, refitted: `../../sieve200/cuda/costmodel.py`** (reproduces everything below from the SASS).  Cycles a step T = max(T_mul, T_alu) + rho x min(T_mul, T_alu), where T_mul = the number of IMAD.WIDE
  x the cost of one and T_alu = the sum of the benchmark costs of all other integer instructions of the loop (rho = 0: the two overlap completely; rho = 1: they simply add).
  **On the A100 one parameter, rho = 0.35 (0.3-0.4), reproduces all six timings within 1.5% (largest 2.2%) at an effective clock of 1.38 GHz (nominal 1.41), including `fermat3`, a different
  algorithm (651 multiplications and 1,677 other instructions in its loop):**

  | A100 | loop instr. | IMAD.WIDE | T_mul | T_alu | model cycles | measured cycles | tests/s measured | model |
  |---|---|---|---|---|---|---|---|---|
  | s1 plain | 1798 | 876 | 3635 | 1777 | 4257 | 4195 | 6.95M | 6.85M |
  | s1 plain + w | 1198 | 876 | 3635 | 592 | 3842 | 3862 | 7.55M | 7.59M |
  | s1r plain + w | 1151 | 876 | 3635 | 518 | 3817 | 3821 | 7.63M | 7.64M |
  | s1r asm | 2016 | 876 | 3635 | 1883 | 4294 | 4195 | 6.95M | 6.79M |
  | fermat3 | 2328 | 651 | 2702 | 3167 | 4113 | 4201 | 6.94M | 7.09M |

  (The first model of this file, "all integer instructions add up", fitted the plain steps and was wrong about the rest; so was my very first one, "multiplier pipe only".  The truth is in between: ALU
  instructions are overlapped with the multiplier pipe to about two thirds.)  The L4 fits to 5% at its observed 1.6 GHz with rho = 0.43 (1.2% at 1.75 GHz with rho = 0.63; its clock is power-capped and
  varies).
  What it says for sm_80 / sm_89:
  * **the step is bound by the multiplier pipe: 876 IMAD.WIDE x 4.15 = 3,635 of ~3,850 cycles** for the best variant; the ALU work costs only rho x T_alu = 180 cycles.  A removed dead IADD3 saves
    0.35 x 2.1 = 0.7 cycles, not 2.1 (that was the over-prediction); `s1r plain + w` is within 6% of the floor 876 x 4.15 of this algorithm.
  * only fewer multiplications could still help the A100 / L4: the model gives `fermat31` (737 IMAD.WIDE, 1,056 other instructions) 7.99M tests/s on the A100 (+4.6% over s1r plain + w), 4.52M on the L4
    (-3%), and `fermat30` +1.6% / -2%: not worth 5% of the fleet's output (the A100 is ~5%); on the RTX it is 20-25% slower.

* **The RTX PRO 6000 is not explained** (it is ~86% of the fleet's output).  Its three timings (22.74M / 22.85M / 23.39M tests/s) are 3,770-3,880 cycles a step at the nominal 2.4 GHz, while the model with the
  RTX benchmark costs (IMAD.WIDE 2.53) gives 2,540-2,610 cycles: **the measured cycles are 1.46-1.49 x the model's.**  Either the cards run at ~1.6 GHz under this load (power-limited; the A100
  and L4 sit near their nominal clocks, the L4 is power-capped at 72 W) or a multiplication costs ~3.8 cycles inside the kernel instead of 2.5.  The two are told apart by the SM clock during the
  kernel: `../../sieve200/cuda/measure_all.sh` samples it (nvidia-smi) beside `time_fermat28.py`.  If they are power-clocked, energy per test is the figure to optimise on them (fewer instructions,
  less instruction fetch), not cycles; if not, something in the 18 KB loop body (fetch, register bank conflicts) is costing 50% and the next step is a benchmark that runs the real step at several loop-body sizes.

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
