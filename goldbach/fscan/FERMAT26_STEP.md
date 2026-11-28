# The 3-limb Montgomery step of `fermat26.h`, stated for a proof

`fm3_run` / `FM3_STEP` in `fermat26.h` (3 limbs of 30 bits, used when the largest number of a batch has
at most 86 bits).  `model3.py` is an executable exact-integer copy of the same operations; the bounds
below are computed with exact integers and agree with its largest intermediate value (2^61.89 over
millions of random and adversarial steps; the analytic bound is 2^62).

## Notation and hypotheses

* `B = 2^30`, `R = B^3 = 2^90`, `X = B - 1`.
* `n` odd with `2^40 < n < 2^86` (so `16 n < R`).  Limbs `n = n0 + n1 B + n2 B^2`:
  `n0, n1 <= X`, `n2 <= 2^26 - 1` (because `n < 2^86`).
* `np = (-n^-1) mod B`, from `fm_inv_neg(n mod 2^64, 3) & (B-1)`: three Newton steps from the 5-bit seed
  `(3 lo) ^ 2` give 40 >= 30 correct bits.  So `n0 * np = -1 mod B`.
* State of one lane: `a = (a0, a1, a2)`, value `A = a0 + a1 B + a2 B^2`.
  **H(A)**: `A < 4 n`, `a0, a1 <= X`, `a2 <= 2^28 - 1 =: Y2` (the last follows from `A < 4n < 2^88`).
* `vpmuludq(x, y) = (x mod 2^32) * (y mod 2^32)` as an exact 64-bit product; `+`, `<<` are the 64-bit lane
  operations.  Every operand of a multiply below is `< 2^32` or only its low 30 bits matter (see C4).
* `b` is 0 or 1 per lane (the next bit of the exponent; the driver is the one of the 26-bit kernel, see the end).

## The step (program order of `FM3_STEP`; `*` is `vpmuludq`, `&M` is `& (B-1)`)

```
d1 = a1 + a1          d2 = a2 + a2
z0 = a0*a0            z1 = a0*d1            z2 = a0*d2 + a1*a1        z3 = a1*d2        z4 = a2*a2

m  = ((z0*np) & M)                          # round 0
z0 = z0 + m*n0        z1 = z1 + m*n1        z2 = z2 + m*n2
z1 = z1 + (z0 >> 30)
m  = ((z1*np) & M)                          # round 1
z1 = z1 + m*n0        z2 = z2 + m*n1        z3 = z3 + m*n2
z2 = z2 + (z1 >> 30)
m  = ((z2*np) & M)                          # round 2
z2 = z2 + m*n0        z3 = z3 + m*n1        z4 = z4 + m*n2
z3 = z3 + (z2 >> 30)

z3 = z3 << b          z4 = z4 << b
z4 = z4 + (z3 >> 30)
a0' = z3 & M          a1' = z4 & M          a2' = z4 >> 30
```

## Claims

**C1 (exactness).**  Writing `m_0, m_1, m_2` for the three values of `m` and `mu = m_0 + m_1 B + m_2 B^2`
(`0 <= mu < R`): after round `i` the low 30 bits of `z_i` are 0 (so `z_i >> 30` is the exact carry), and
`Y := a0' + a1' B + a2' B^2 = 2^b * (A^2 + mu * n) / R`, with `A^2 + mu*n = 0 mod R`.  Hence
`Y = 2^b * A^2 * R^-1 (mod n)`.  (The columns `z0..z4` hold `A^2` with the cross terms doubled through
`d1, d2`; `m_i = z_i * np mod B` makes `z_i + m_i n0 = 0 mod B` because `n0 * np = -1 mod B`.)

**C2 (range).**  H(A) and `16 n <= R` give `0 <= (A^2 + mu n)/R < 16 n^2/R + n <= 2n`, so `Y < 4n`, and
therefore `H(Y)` holds again: `a0', a1' < B`, `a2' < 2^28`.  The step maps H to H.

**C3 (no overflow).**  Every intermediate value is `< 2^62`, so no 64-bit lane wraps.  With
`P = X^2 < 2^60`, `Q = X (2^26-1) < 2^56`, `S = X * Y2 < 2^58`, `Y2^2 < 2^56`:

| after the operation | bound | log2 |
|---|---|---|
| `z0 = a0*a0` | X^2 | 60.000 |
| `z1 = a0*d1` | 2X^2 | 61.000 |
| `z2 = a0*d2 + a1*a1` | 2XY2 + X^2 | 60.585 |
| `z3 = a1*d2` | 2XY2 | 59.000 |
| `z4 = a2*a2` | Y2^2 | 56.000 |
| `z0 += m*n0` (round 0) | 2X^2 | 61.000 |
| `z1 += m*n1` (round 0) | 3X^2 | 61.585 |
| `z2 += m*n2` (round 0) | 2XY2 + X^2 + X*N2 | 60.644 |
| `z1 += z0 >> 30` | 3X^2 + 2^31 | 61.585 |
| `z1 += m*n0` (round 1) | 4X^2 + 2^31 | 62.000 (strictly below: 2^62 - 2^33 + 2^31 + 4) |
| `z2 += m*n1` (round 1) | 2XY2 + 2X^2 + X*N2 | 61.358 |
| `z3 += m*n2` (round 1) | 2XY2 + X*N2 | 59.170 |
| `z2 += z1 >> 30` | ... + 2^32 | 61.358 |
| `z2 += m*n0` (round 2) | 2XY2 + 3X^2 + X*N2 + 2^32 | 61.833 |
| `z3 += m*n1` (round 2) | 2XY2 + X^2 + X*N2 | 60.644 |
| `z4 += m*n2` (round 2) | Y2^2 + X*N2 | 57.000 |
| `z3 += z2 >> 30` | ... + 2^32 | 60.644 |
| `z3 <<= b` (b = 1) | 2 * z3 | 61.644 |
| `z4 <<= b` (b = 1) | 2 * z4 | 58.000 |
| `z4 += z3 >> 30` | 2 * z4 + 2^33 | 58.000 |

(`N2 = 2^26 - 1`; the carries are `z0 >> 30 < 2^31` and `z1 >> 30, z2 >> 30, z3 >> 30 < 2^32`.)

**C4 (multiplier operands).**  `vpmuludq` ignores the bits above 31 of its operands, so all multiplicands
must be `< 2^32`: `a0, a1 <= X`; `d1 = 2 a1 <= 2X < 2^31`; `d2 = 2 a2 < 2^29`; `a2 < 2^28`; `np, m <= X`;
`n0, n1 <= X`, `n2 < 2^26`.  The only operand that exceeds 32 bits is the `z_i` in `z_i * np`; the product
uses `z_i mod 2^32`, and `((z_i mod 2^32) * np) & M = (z_i * np) mod B` because `B = 2^30` divides `2^32`.
(The product `(z_i mod 2^32) * np < 2^62` is itself exact in 64 bits.)

## What surrounds the step (same as `fermat52.h` and the 4-limb kernel, only `Rb` changes from 104 to 90)

(Proved in `goldbach/lean/GoldbachGaps/Fscan/` on the Lean branch for the step, C1 to C4, and for a whole lane,
`Fscan.F30.lane_correct`; the points the Lean session lists as assumed are marked below.)

* Setup per lane (`fm3_setup`; the exponent words come from `fm_exp_words` in `fm_common.h` since 9f631b4, before
  that from u128 shifts with the same values, `test_fm_common.c` compares the two on 106 million cases):
  `E = n + Rb - 1`, `c = ceil(E / 2^t)`, `B_t = c 2^t - E` (`0 <= B_t < 2^t`, equal to `(-E) mod 2^t`), exponent
  bits = the `t` bits of `B_t`, most significant first, top-aligned in 128 bits as `(bh, bl)` (the step `i` takes
  bit 63 of `bh << i`, i.e. bit `t-1-i` of `B_t`, then from `bl` after 64 steps: ASSUMED, not proved),
  `t = bits(max n of the batch) - 6` (`t <= 80` selects this kernel).
  `1 <= c <= 65` for every lane (Lean: `c_boundsR`).  For a lane whose n has the bit length of the batch maximum,
  which is every lane of fscan's batches (all close to N), `33 <= c`, hence the start value `y = 2^(Rb - c)` is
  `< 2^58`; a lane much smaller than the maximum has a smaller c (down to 1) and `y` up to `2^89`.  The start value
  is `y = 2^e` with `e = Rb - c` if `e <= bits(n)` (then `y < 2n`), otherwise `2^e` reduced mod n if `2^e >= 4n`
  (a u128 remainder) -- the same as `startVal` in the Lean model.  It never needs the reduction for n of 62 bits or
  more with the 3-limb kernel (`e <= 57`).  Limbs `a_j = (y >> 30 j) & M` (`a2 = y >> 60`).
* `np = fm_inv_neg(n mod 2^64, 3) & M`: the seed `(3 lo) ^ 2` is the inverse of `lo` modulo 32 for odd `lo`, and
  each step `x *= 2 - lo*x` doubles the number of correct bits, so 3 steps give 40 >= 30 bits and `n0 * np = -1 mod B`
  (a hypothesis of the Lean theorems; ASSUMED, not proved).
* Invariant: with `y_i = 2^(u_i) mod n` and `v_i = u_i - Rb`, a step takes `v` to `2v + b`.  After `t` steps
  `v = -c 2^t + B_t = -E = -(n + Rb - 1)`, i.e. `u = 1 - n`: the final `y` is `2^(1-n) mod n`.
* Finish (`fm3_run`, per lane, `u128`): `y = a0 + a1 2^30 + a2 2^60` (`y < 4n` by C2), two conditional
  subtractions of `2n` then `n`, the verdict is `y == 1`, i.e. `2^(n-1) = 1 mod n`.

## Evidence besides the proof obligation

`python3 model3.py 30 86 20` (exact integers, mirrors every operation and asserts C3, the value bound of C2
after every step, and that the low 30 bits cancel); `python3 test_fermat.py` and `python3 stress_fermat.py`
(about 1.5 million numbers of 41 to 100 bits, structured and Carmichael cases included, against
`pow(2, n-1, n)`), and `./check_record.sh` (the record N = 83668534093338795647672: all 111 rows left by the
primes <= 383 are reported composite).
