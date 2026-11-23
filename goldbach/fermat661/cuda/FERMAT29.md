# fermat29: 23 limbs of 29 bits with a 31-bit top Montgomery digit (R = 2^669, n < 2^665): 805 + 23 multiplications a step instead of 876 + 24

Same job, same kernel (`fermat28_kernel.cuh`), same interface as `fermat28`: a base-2 Fermat test of n = cq[i] + k M, flag 1 / 0, flag 2 outside the range.  Only the generated step file differs
(`fermat29_step_s1.cuh` for the RTX PRO 6000's PTX `mad.wide` build, `fermat29_step_s1w.cuh` with `mul.wide` for the m * n products on sm_80 / 89 / 75), made by
`python3 -c "import gen_fermat28 as G; open('fermat29_step_s1.cuh', 'w').write(G.generate(23, 1, False, False, W=29, RB=669)); open('fermat29_step_s1w.cuh', 'w').write(G.generate(23, 1, False, True, W=29, RB=669))"`.
**CPU-verified, not yet run on a GPU.**  Measured on a GPU by the GPU session (`uarch_measure/e4_radix_rtx_l4.txt`, a step with the same multiplications and a chain of the same size, R = 2^667):
**0.926 of the production step on the RTX PRO 6000 (+8% tests/s), 0.951 on the L4**; the real step has the same IMAD count (828 + 2) and a funnel-shift pass in place of the carry chain.

## Why 29 bits, and why the top digit has 31

* **29 bits is the widest limb that needs no carry groups.**  With limbs below 2^29 a column sum (11 cross products d_i x_j < 2^59, the diagonal, 22 reduction products m_i n_j < 2^58, the wide top term, the carry) is below
  49 x 2^58 = 2^63.6 < 2^64, so one 64-bit accumulator a column still works (`fermat30`, `fermat31` need 96-bit column sums and lose; see FERMAT31.md).  23 limbs hold 667 bits.
* **But 23 x 29 = 667 bits is not enough room.**  The lazy step keeps X < 4n and needs 16 n < R (b = 1 doubles the value every step: Y < 2 (n + X^2 / R)); R = 2^667 allows n < 2^663, and the campaign's numbers run to
  N < 10^200 = 2^664.4 (the 89-moduli windows to 8.85e199 = 2^664.2, the 88-moduli k range to 7.9e199 = 2^664.05; GPU session's check, 10:55Z).
* **The fix: R = 2^669 = 2^(29 x 22 + 31).**  The LAST Montgomery digit m_22 has 31 bits instead of 29, so T = X^2 + mu n is divisible by 2^669 with mu < 2^669, 16 n < R holds for n < 2^665, and no multiplication is added.
  Two things change:
  1. **Bits 667-668 of T come from column 23**, so m_22 must see them.  The part of column 23 that does not depend on m_22 (the squaring cross products with i + j = 23 and m_i n_(23-i) for i <= 21) is summed first
     (`b0`, before column 22 is finished; the multiplications are the same ones, only done earlier), and m_22 = ((acc_22 + 2^29 b0) n') mod 2^31 with n' = -n^-1 mod **2^32** (the full inverse of the low word: the kernel
     computes it with `fm28_inv_neg32`; the lower digits just mask it to 29 bits).  Then acc_22 += m_22 n_0, and column 23 starts from carry + b0 + m_22 n_1.
     Check: acc_22 + m_22 n_0 + 2^29 (b0 + m_22 n_1) = acc_22 + 2^29 b0 + m_22 (n_0 + 2^29 n_1) = 0 mod 2^31 because n mod 2^31 = n_0 + 2^29 n_1 mod 2^31, so T = 0 mod 2^(29 x 22 + 31) = 2^669.
  2. **The normal carry chain of the upper columns then gives Z = T / 2^667 = 4 Q** (Q = T / 2^669 the Montgomery quotient, Z divisible by 4 because T is divisible by 2^669), and the output is 2^b Q = Z >> (2 - b):
     one funnel of two limbs a limb, `x[i] = ((y_i >> sh) | (y_(i+1) << (29 - sh))) & MASK29` with sh = 2 - b, the top limb `y_22 >> sh`.  It replaces the 28-bit step's carry chain `(y << b) + carry` (and costs the same).
* Range, as before with R: Y < n + X^2 / R < 2n for 16 n <= R, so Y < 4n and the step maps {X < 4n} to itself; X < 4n < 2^667 fits 23 limbs of 29 bits.  The kernel flags n >= 2^665 with 2 (`FM_NMAX` 665).
  Setup differences in `fermat28_kernel.cuh` (macros `FM_W` 29, `FM_NL` 23, `FM_RB` 669, `FM_NMAX` 665, `FM_TOPX` 2, all defaulting to the 28-bit values: the SASS of every existing configuration, sm_120 / sm_89, s1r / s1rw, is
  byte-identical to before): E = n + 668, start value 2^(669 - c), the exponent buffer is aligned to the top of its 21 words (`sh = 32 L32 - t`, was `RB - t`: the same number for R = 2^672).

## Verified on the CPU (g++, the same source text)

* `FM28_STEP=fermat29_step_s1.cuh python3 test_step28.py` (and `_s1w`): the step alone against big-integer arithmetic, 6,070 inputs (random, X near 4n, limbs all ones, n near 2^665 and 2^642, even limbs): wrong 0, largest Y/n 3.9366,
  every output limb below 2^29, Y = 2^b X^2 R^-1 mod n for R = 2^669.
* `FM28_STEP=fermat29_step_s1.cuh python3 test_fermat28.py --count 300` (and `_s1w`): the final residue 2^(1-n) mod n of 3,000 random n of 642..665 bits, the verdict of random n of 666 (flag 2) down to 642 bits, 100 primes, 12 base-2
  pseudoprimes, edge values, **n = N0 - q + kM of the 88-moduli campaign with k in [2^31, 2^32) (n up to 2^664.05) and of the 89-moduli vector windows (k in [k_lo, k_lo + 2^24), n up to 2^664.2; `vector89_spec.json`)**, 40 real
  primes of each form: ALL OK.  The 28-bit steps pass the same tests unchanged.
* `FM28_STEP=fermat29_step_s1.cuh python3 test_fermat28_persist.py`: the persistent pool kernel with the 29-bit step (real threads): ALL OK.

## Compiled (NVRTC + ptxas 12.9, `sieve200/cuda/sass.py`, no GPU)

| kernel | step loop instr. | IMAD | registers | spills |
|---|---|---|---|---|
| sm_120 production s1r asm (24 x 28, redundant) | 1,104 | 900 | 88 (92 in cupy) | 0 |
| **sm_120 fermat29 s1 asm** | **1,072** | **830** | **91** | 0 |
| sm_89 production s1rw | 1,151 | 926 | 94 | 0 |
| **sm_89 fermat29 s1w** | **1,116** | **854** | **110** (96: 36 B spill; 104: 36 B) | 0 |

On the RTX both allocate 96 registers a thread: 5 CTAs of 128 threads an SM as now.  On sm_89 / 75 the uncapped kernel needs 110 (4 CTAs an SM; the step is flat from 2 warps a scheduler); `maxreg` 96 / 104 give 5 CTAs with 9 spilled words.

## To run on a GPU (GPU session)

```
cd goldbach/fermat661/cuda
python3 time_fermat28.py <spec.json> --variant s1r_asm s29_asm --check --seconds 20          # RTX PRO 6000: correctness against gmpy2 on 2,000 candidates + tests/s
python3 time_fermat28.py <spec.json> --variant s1rw s29w s29w_r96 s29w_r104 --check          # L4 / A100 / T4 (--k28-asm 0)
python3 time_fermat28.py /content/m89_8.json --kmin 2137898 --kmax 18915114 --variant s1r_asm s29_asm --check     # a vector window
python3 test_gpu_fermat28.py specs_variants.json                                              # every variant against gmpy2, registers, local bytes
python3 bench_persist.py --variant s29_asm                                                    # the persistent kernel with the 29-bit step
```
Driver: `--k28-step fermat29_step_s1.cuh --k28-asm 1` (RTX) or `fermat29_step_s1w.cuh --k28-asm 0` (L4 / A100 / T4), with `search_gpu5_k29.patch` (the driver's n-range assertion follows the step file: `gpu_fermat28.step_nmax`).
The kernel returns flag 2 for n >= 2^665 and the driver raises ("kernel 28 flagged an n outside its range"): nothing can silently go wrong at the edge; the 89-moduli windows end at 2^664.2 and the 88-moduli scan at k = 2^32 - 1 at 2^664.05.


## Measured on the GPUs (GPU session, 23 Nov 11:25-12:00Z; `phd/campaign3_gpu/k29/` on its branch)

* **RTX PRO 6000** (gold-g4c, `time_fermat28.py --check`, 2,000 candidates against gmpy2, 20 s a variant): **s1r_asm 23.29M tests/s (92 registers), s29_asm 24.62M (91 registers): +5.7%**; 0 mismatches (36 / 45 PRPs on the 88-moduli spec, 50 / 61 on
  an 89-moduli vector window).  The step-level E4 benchmark had promised +8% (ratio 0.926); the kernel's 0.946 is what the additive cost model gives (-72 IMAD.WIDE x 4.2 cycles, +40 other instructions for the funnel-shift output x ~1.2).
* **L4** (gold-l4b): s1rw 4.472M -> s29w 4.729M tests/s (+5.7%, 110 registers); capping the step at 96 / 104 registers (s29w_r96 / _r104) is not better (4.665M / 4.625M medians).
* **In the driver** (vector mode, 24 test windows, batches of 4): slice lines identical to production on every card, the known case's 23 (k, q) found as the CPU brute force found them; batch **1.564-1.582 -> 1.501-1.516 s on the three RTX cards (-3.7 to
  -4.3%)**, -3.7% on the L4 (9.705 s against 10.057-10.103 s), -3.0 to -3.6% on the other L4 and the T4.  Deployed on all seven GPUs under the lead's standing rule.
