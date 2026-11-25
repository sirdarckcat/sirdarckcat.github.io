# Two numbers of the research session, recomputed from the cover file

Asked by the research session on 25 November 2026: recompute, without its code, two answers it gave from the real
cover files, so that they stop being unverified. Input: `goldbach/fscan/cover/starts/q200000_m89.txt` (taken from
branch `ccr-d4a17dd0-7uu03r` at `2cb1bb2`, sha256 `ff0e1b7c…6d2c`; it is not on `master`). Each line is a cover:
`N = a (mod r)` for the 89 odd primes `r = 3..463`; its rows are the odd primes `q < 200,000` in none of the classes.
Everything here was written from that description; the research session's scripts were read only afterwards, to
locate the one difference.

| | claim | verdict |
|---|---|---|
| 1 | folded primes 467, 479, 487: best class holds 8, 8, 8 rows; gains +0.115, +0.118, +0.119 nats; window 2^15.5, 2^6.6, 2^−2.3 | **yes**, every number |
| 2a | the formula for Var(S) | **yes**: derivation checked, and measured by sieving 765,000 members directly |
| 2b | Var(S) = 308.8 against 333.7, sd ratio 0.9620 | **no**: 324.5 against 335.4, sd ratio **0.9836**. The 308.8 comes from replacing ∏(1 − 1/(s−1)²) by exp(−1/(463 ln 463)) |
| 2c | class counts modulo 467..997: variance/mean 0.820 | **yes** (0.8203) |
| 2d | the same ratio within 0.0002 on the other covers of the file | **yes** (all 300 lines: 0.9835 to 0.9837) |
| 2e | 0.9673 and 0.9600 at 170,000 and 213,070 | same correction: **0.9851** and **0.9831** |
| 2f | no cover differs from another in this variance | **yes**, and for a reason: see below |
| 2g | full Poisson dispersion would be worth at most 7% in hits | smaller: **3%** by the same measure |

## 1. Folded primes (`fold_check.py` → `fold_check.txt`)

The first line of the file has 89 moduli, the odd primes up to 463, and 1,502 rows, as it says.
p = 2∏r/(r−1)/(200 ln 10) = 0.02398; the cover has 10^200/(2∏r) = 21,378,977 = 2^24.35 members (16.88 nats);
its exponent is −1502 ln(1 − p) = 36.46 nats.

| s | rows before | K_max (classes reaching it) | gain, first order | gain, exact | window after |
|---|---|---|---|---|---|
| 467 | 1,502 | 8 (3) | +0.1150 | +0.1154 | 2^15.5 |
| 479 | 1,494 | 8 (3) | +0.1176 | +0.1181 | 2^6.6 |
| 487 | 1,486 | 8 (2) | +0.1194 | +0.1200 | 2^−2.3 |

"First order" is the research session's p(K_max − (rows − K_max)/(s − 1)); "exact" is the log of the ratio of the two
products of (1 − chance of a prime) over the rows. The product (1 − p)^rows that the gain is measured from is the
average member's chance to within 0.0003 nats (column `ln(average member / (1-p)^rows)`), so the gain is over the
average member. The next lines of the research session's table (491 to 521) and its table for 170,000 agree too
(`fold_check_q170000.txt`).

## 2. The variance of the rows left by the deeper sieve

S(N) = number of rows q with N − q free of prime factors in (463, B], B = 10^8. With N uniform modulo every prime
s in (463, B] independently,

    E S = n w,                w = ∏ (1 − 1/s)
    Var S = n w (1 − w) + w² Σ_{i≠j} (ρ_ij − 1),      ρ_ij = R (s0 − 1)/(s0 − 2)  or  R,
    R = ∏ (1 − 1/(s − 1)²)

where s0 is the prime factor above 463 of q_i − q_j, if it has one (it has at most one). This is the research
session's formula and it is right. Its evaluation used two shortcuts (`selection_check.py` →
`selection_q200000_line0.txt`):

| | shortcut | exact product over the 5,761,365 primes in (463, 10^8] |
|---|---|---|
| w | ln 463 / ln B = 0.333198 | 0.336642 |
| R | exp(−1/(463 ln 463)) = 0.99964817 | 0.99970483 |
| n w (1 − w) | 333.71 | 335.42 |
| pair term | −24.88 | −10.91 |
| Var S | 308.83 | **324.51** |
| sd ratio | 0.9620 | **0.9836** |

With the shortcuts my program gives the research session's numbers to the last digit, so the two programs agree and
the shortcut for R is the whole difference: Σ 1/(s−1)² over the primes above 463 is 2.952·10^−4, not
1/(463 ln 463) = 3.518·10^−4 (the integral is E₁(ln 463), 13% below its leading term, and the sum over the primes is another 4% below the
integral). The error is multiplied by n(n − 1) = 2.25 million and the result nearly cancels against the same-class
pairs (665.5 against 569.2 exactly; 793.2 against 569.1 with the shortcut). Exact R alone moves 308.8 to 323.0, exact
w the rest.

**Measured** (`members.py`, `sieve_members.c`, `combine.py` → `measured_1e6.txt`, `measured_1e8.txt`, raw output in
`runs/`): members N = N0 + kM of the first cover, each sieved by every prime up to B.

| B | members sieved | mean S, measured (n w) | Var S, measured | formula, exact constants | with the shortcuts | n w (1 − w) |
|---|---|---|---|---|---|---|
| 10^4 | 600,000 | 1010.04 (1010.03) | 294.14 ± 0.54 | 294.43 | 231.60 | 330.83 |
| 10^5 | 600,000 | 808.80 (808.77) | 345.13 ± 0.63 | 345.88 | 310.17 | 373.28 |
| 10^6 | 600,000 | 674.20 (674.16) | 351.36 ± 0.64 | 352.20 | 326.61 | 371.57 |
| 10^7 | 165,000 | 577.90 (577.87) | 344.48 ± 1.20 | 341.29 | 321.67 | 355.54 |
| 10^8 | 165,000 | 505.69 (505.64) | 326.98 ± 1.14 | 324.51 | 308.83 | 335.42 |

The formula with exact constants is inside the sampling error at 10^4 to 10^6. The 165,000 members sieved to 10^8
are a separate sample which is 2.6 high already at 10^6 (354.84, against the formula's 352.20 and the 351.36 of the
600,000), and carries that excess to 10^7 and 10^8; the shortcut value is 16 standard errors away. S is Gaussian to the eye of the third and
fourth moments (skewness +0.012, excess kurtosis +0.006 over 105,000 members).

**Other covers** (`selection_q200000_all.txt`, `selection_other_files.txt`): all 300 lines of the file have sd ratio
0.9835 to 0.9837 (0.9619 to 0.9621 with the shortcuts, the research session's "within 0.0002"); 170,000: 0.9851
(shortcuts 0.9673); 170,000 with 491: 0.9852; 180,000: 0.9847; 190,000: 0.9842; 213,070: 0.9831 (shortcuts 0.9600).
Class counts modulo the 78 primes 467..997: variance/mean 0.8203 on average over the s − 1 nonzero classes.

**Why no cover differs** (`random_cover_check.py`, `pair_density.py`). The pair term is fixed by one number, the sum
T of 1/(s0 − 2) over the pairs of rows in the same class of a prime s0 > 463, against its value T_random for rows
placed at random:

| cover on the moduli 3..463, Q = 200,000 | rows | T / T_random | pair sum / rows² | sd ratio |
|---|---|---|---|---|
| best cover of the file | 1,502 | 0.8556 | −4.27·10^−5 | 0.9836 |
| greedy cover | 1,587 | 0.8560 | −4.26·10^−5 | 0.9827 |
| five covers with random classes | 2,144 to 2,179 | 0.8559 to 0.8578 | −4.20 to −4.26·10^−5 | 0.9762 to 0.9768 |
| no classes at all (every odd prime) | 17,983 | 0.9464 | −1.59·10^−5 | 0.9246 |

The factor is arithmetic. A pair of rows (q, q + d) needs q to avoid, modulo each r ≤ 463, the classes 0, −d, a_r and
a_r − d: that leaves r − 2 classes when r divides d and (r − 2)(r − 3)/(r − 1) on average otherwise, whatever a_r is.
So a difference divisible by r carries (r − 1)/(r − 3) times the average number of pairs, and a difference with a
prime factor above 463, being s0·k with k < 429, has few small prime factors and carries fewer. Summing these local
factors alone, with no cover in hand, gives T / T_random = 0.8547; the measured value is 0.8556, and the pair counts
follow the model bin by bin to 1 or 2%. The classes of the cover enter only through which differences fall on ±a_r,
which averages out. Hence

    Var S ≈ n w (1 − w) − 4.3·10^−5 w² n²       (moduli 3..463, Q = 200,000, any classes)

and the spread of S cannot be chosen through the cover.

**What the missing spread is worth** (`measured_1e8.txt`). A row left at B is prime with chance p′ = p/w = 0.0712;
p′·sd(S) = 1.283 nats per standard deviation (the research session's 1.265 used the smaller sd); with
θ = −ln(1 − p′) = 0.0739 it is θ·sd(S) = 1.33. The hits of the average member exceed those of a member with exactly the mean S by ln E(1 − p′)^(S − ES) =
0.891 nats, measured (0.895 from the Gaussian formula θ² Var / 2). Raising the variance from 324.5 to the binomial
335.4 would add θ²·10.9/2 = **0.030 nats**; with the research session's numbers the same formula gives 0.07. For a
funnel that keeps only the best fraction f of the members the same change is worth 0.047 nats at f = 10%, 0.056 at
3%, 0.063 at 1%. In every reading it is a few hundredths of a nat, and it is not on offer.

## Files

`covlib.py` (reading a cover, its rows, p), `fold_check.py`, `selection_check.py FILE Q [B] [LINES]`,
`members.py FILE Q LINE B OUTDIR` and `sieve_members.c` (the direct sieve), `combine.py`, `random_cover_check.py`,
`pair_density.py`, and their outputs. The cover files are the research session's and are not copied here; put them in
`data/`. Needs numpy; a few minutes, except the sieve to 10^8 (17 ms per member).
