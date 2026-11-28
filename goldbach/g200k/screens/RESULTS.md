# Cheaper-than-Fermat compositeness at 200 digits, and the CPU pipeline's rate (research's (c) and (f), 25 Nov)

Cover: research's `fscan/cover/starts/q200000_m89.txt` (first line: 89 moduli, 1,502 rows at Q = 200,000; copied here), N < 10^200
(665 bits), one window of 2^22 members in the middle of the cover's k range.  Sapphire Rapids core, the other three cores busy
at nice 19.  Costs are in Fermat tests: 664 modular squarings (the test of a 665-bit n).

## The CPU pipeline at 200 digits, a core (`rate200.py q200000_m89.txt 200000 B 22 0.015`)

| B | sieve | select + rows | Fermat | members/s a core | tests a kept member | p^ | expected hits a core-second |
|---|---|---|---|---|---|---|---|
| 10^7 | 2.01 us | 0.12 us | 2.80 us | 202,800 | 16.0 | 0.0626 | 4.1e-12 |
| 3 10^7 | 3.36 us | 0.12 us | 2.76 us | 160,500 | 15.0 | 0.0667 | 3.8e-12 |
| 10^8 | 7.50 us | 0.11 us | 2.53 us | 98,700 | 14.0 | 0.0716 | 2.3e-12 |

(the emptiest 1.5% of each 32,768-block; fm13 until the first probable prime, ~12 us a test with the box loaded).  The CPU sieve
at 10^8 is bound by the per-prime work of the 5.76M primes on 1,502 rows a window, so B = 10^7 is this pipeline's best point.

## Real survivors (`survivors.py 30`)

The 30 emptiest kept members of the window's first block, their alive rows N - q (no prime factor below 10^8): 13,406 numbers,
447 a member, 951 base-2 probable primes (7.09%), 12,455 composite.

## (c)1 Batching the Fermat condition (`batch.py`)

2^(N-1) mod prod (N - q_i), a remainder tree, the check 2^(N-1) = 2^(q_i) mod (N - q_i), against k separate powmods (GMP,
gmpy2; one powmod at 664 bits: 175 us on this box, fm13 is 15-35x faster): k = 2: 0.98x, 4: 1.65x, 8: 2.96x, 13: 7.0x,
16: 7.5x, 32: 6.1x, 64: 10.7x the cost of the separate powmods.  An exponentiation modulo the product costs log N M(k n) with M
superlinear at these sizes, so no k gains; against the IFMA kernel every k loses by more than 15x.

## (c)2 p-1 and ECM stage 1 as screens (`pm1.py`, `ecm1.py`; the 12,455 composite survivors)

Break-even (research's formula, below): c / e >= 1 / 0.925 = 1.08 (c = the fraction of the composite rows a screen proves
composite, e = its cost in tests).

| screen | cost e (tests) | killed | c | c / e |
|---|---|---|---|---|
| p-1 stage 1, B1 = 100 | 0.205 | 3 | 0.0002 | 0.0012 |
| B1 = 300 | 0.651 | 58 | 0.0047 | 0.0072 |
| B1 = 1,000 | 2.17 | 240 | 0.0193 | 0.0089 |
| B1 = 3,000 | 6.52 | 539 | 0.0433 | 0.0066 |
| B1 = 10,000 | 21.8 | 1,025 | 0.0823 | 0.0038 |
| B1 = 30,000 | 65.1 | 1,561 | 0.125 | 0.0019 |
| p-1, B1 = 100, B2 = 10^4 | 3.83 | 169 | 0.0136 | 0.0035 |
| p-1, B1 = 1,000, B2 = 10^5 | 30.6 | 1,333 | 0.107 | 0.0035 |
| ECM, one curve, B1 = 1,000 (4,000 composites) | 23.6 | 123 | 0.0307 | 0.0013 |

The best is 120x short of break-even.  (ECM checked on n = p q, p ~ 10^5: 14 of 20 curves at B1 = 1,000 find p.)

## (c)3 What a screen is worth

With rows tested in order until the first probable prime and a screen of cost e applied to each row before its test, killing a
fraction c of the composite rows, a rejected member costs (e + 1 - c (1 - p')) / p' tests instead of 1 / p': the primes are never
killed, so the number of rows looked at is the same 1 / p', and each costs e plus a test unless it was killed.  Research's
(e + 1 - 0.925 c) / p' is this with p' = 0.075.  So a screen pays only if e < 0.925 c, i.e. it must cost less than 0.925 tests
even if it killed every composite.  The only screens that pass are sieve-like, whose work is shared by the members of a residue
class (a prime marks every s-th member of a window at once): the deep head (primes in (10^8, 10^9] on the first 64 rows after the
selection) removes 11.1% of the alive rows (c ~ 0.12) for a few ms of GPU time a window, an estimated +4-6% of a batch.
A screen applied before the selection would also sharpen the selection; that is exactly a deeper sieve bound B.
