# The bottom-up round, helper session: the accounting of the 460 nats, the reformulations, the computational literature, and a calibration on the published records

For the research session and the lead (requests of 17:31 and 17:51 UTC 25 Nov). Everything below was computed here unless marked "literature" or "not read". Scripts and logs: `goldbach/gaps_map/data/bottomup/` (README there). Rule used: nats at 200 digits (Q = 200,000, the 89 odd moduli 3 to 463, n = 1,502 rows on the campaign's cover, 1,524 on mine, kappa = -ln(1 - 0.02398) = 0.02428 nats per row), a number before every claim, negative results kept.

## 0. The result in fifteen lines

1. **Nothing in this round lowers the 36.46 nats**, and I could not find a place where the 5.4 are hiding. What the round adds is an accounting that says why, and three measurements that close open items.
2. **The one entropy is ln 10^200 = 460.5 nats.** The exponent goes 78.3 (the mean number of representations of an even N by a prime below Q and a prime) to 52.2 (N not divisible by any odd r up to 463, random classes: 1.7 nats of entropy) to 36.46 (classes optimised: 443 nats of pins, 15.8 nats of exponent, 0.036 per nat). 16.9 nats are left: the window of 2.2*10^7 members.
3. **Every free source of information here is a Gaussian-tail selection**: tilt about rate * sqrt(2 S). The cover has rate 0.58 nats per sd (sd 24.0 rows over random covers, skew -0.04), so the random-energy bound is 17.3 nats and the best cover has taken 15.8 (91%). The window has 1.33 nats per sd; a whole window of 2*10^7 members simulated reaches +5.41 sd (Gaussian 5.34).
4. **The marginal price is the same everywhere**: one more pin beyond 463, at its best class, pays 0.035 nats per nat of entropy at 467, 0.016 at 2,003, 0.002 at 200,003; the cover as a whole pays 0.036. Nothing is left unspent at a better price, and the 16.9 nats are the window the sieve needs.
5. **Research's three points** (section 1): no known method beats the progression sieve (Bernstein's batch smooth part costs 2,900 to 8,700 Fermat tests per member in wall-clock, not 2 to 5); no integer analogue of the Joux/Swan relations exists, for a structural reason; no way to bias roots modulo medium primes without paying their logarithm, and the root sieve of the number field sieve is a scan.
6. **Cover supply** (section 2): 3.6*10^8 covers are needed per hit; there are e^21 within 8 rows of the best (my independent-move count, checked), which costs 0.12 to 0.19 nats; Research's thermodynamic integration gives the same within a factor 1.5.
7. **Additive structure** (section 3): none beyond shared pins. In a simulated window the top 1% have pair-count ratios 0.993 (lags with no band prime), 1.015 (one), 1.050 (two); additive energy 1.0000 of the independent value.
8. **Dual and geometry** (section 3): the expected overlap is n * pi = 36.6 whatever the window's prime count; a prime-poor window is worth nothing by itself; every pin costs its volume.
9. **Literature** (section 4): nothing below the Johnson-type threshold is known for random lists; hardness is worst-case or conditional; the same regime is a cryptographic assumption (Polynomial Reconstruction).
10. **Calibration on the 69 published records of the least Goldbach summand** (section 5, new): the success model reproduces them with an excess of +0.06 +- 0.34 nats (hit rate predicted too high by e^0.06) for N from 8*10^13 to 9*10^17, where the exponent is 36 to 41, the fleet's range; 0.6 to 0.9 nats optimistic below 5*10^13 (pi 0.25 to 0.3, shallow truncation).
11. **Corrections to my earlier notes** (section 7): the lone-N sieve cost in cycles is 1.2 to 7 tests, not 0.25 to 0.65, so the lone-N loss is 1.9 to 3.4 nats, not 1.2 to 1.6; the window sieve costs 0.075 to 0.13 tests per member, not 0.005 to 0.012.
12. **What would count as progress** (section 6): a list with the number each item needs.
13. **Follow-up to Research's message of 18:40 UTC** (section 8): the fleet's own tally agrees with its model (-0.15 +- 0.30 nats, 11 found against 12.8 expected); the overshoot law beyond the design level, on which the chance of 200,000 depends (0.13% at theta = 1, 0.59% at 1.26, 1.9% at 1.58), is exact on the miniature (0.98 +- 0.07, 303 hits), 0.975 +- 0.040 on Research's 666 pipeline hits at 100 and 150 digits (0.99 +- 0.03 pooled) and not lengthened by the selection (block correlation -0.023); `--near-miss 140000` would measure it to +-0.2 in a day and a half; and no family outside the grammar exists in the literature, because the 18 nats of divergence still to supply cannot be bought by pins (0.63 nats) or sampled.
14. **The idle-core CPU scan at 200 digits** (section 8.4, new): 273 covers at the record target 160,367 (6.4 core-hours), 0.0003 successes expected, none found (one success costs 23,100 core-hours); a calibration at target 80,000 on 114 covers finds 42 against 46.7 expected (-0.11 +- 0.15 nats at an exponent of 15), every find recomputed from its N, and an overshoot of 0.83 +- 0.16 of the model's (pooled with the rest, 0.98 +- 0.03: theta = 1 stands).
15. **The overshoot law does not decide the design level** (section 8.5, new): on the Opus model with the same work for every design, the 170,000 design has the highest expected record for every theta from 0.8 to 2 at today's work (margin 1,200 to 6,500), and a higher design level wins only with 1.9 to 20 times the work and a theta of 1 or less; so the 24-hour calibration of theta changes the forecast, not the decision.

## 1. Research's three points (17:51)

### 1.1 Is anything better than sieving known for polynomial values with many small prime factors?

Calibration on this machine (libgmp through ctypes, `gmp_cal.py`): a base-2 Fermat test at 665 bits 77.6 us; `mpz_mul` of two 10^8-bit numbers 0.50 s (6,400 tests), of two 3*10^8-bit numbers 1.9 s (24,700 tests); a 1.44*10^8-bit number reduced modulo a 10^6-bit one 0.57 s (7,300 tests).

| per member (1,502 rows), in Fermat tests | B = 10^6 | B = 10^7 | B = 10^8 |
|---|---|---|---|
| Bernstein's batch smooth part, rows as unrelated numbers (batch K = bits(z)/665, c * log2 K levels, c = 1 to 3, `mpz_mul` timings) | 1,000 to 3,100 | 1,700 to 5,200 | **2,900 to 8,700** |
| z mod F(N) once per member (F = product of the rows, 10^6 bits) | 56 | 560 | 5,600 |
| **per-N root lookup** (one reduction of N per prime, 4 to 25 cycles with the table lookup; a test is 2.7*10^5 cycles) | 1.2 to 7.2 | 10 to 61 | **85 to 530** |
| window sieve of the fleet (rho * 13.9 tests: G4 0.075, L4 0.11, T4 0.13 per member) | | | 0.075 to 0.13 |

- **Your 2 to 5 tests per member is what bit-operation counting gives**: |z| = 1.44*10^8 bits, L = 2.9*10^8, K = 2.2*10^5 rows per batch, 17.7 levels at L log2 L bit-operations, 6.5*10^5 per row, 1.0*10^9 per member, against 665 * 665^2 * 1.5 = 4.4*10^8 per test: 2 to 3 tests. In wall-clock it is 3,000 times that, because the schoolbook test does a 64-bit multiply (4,096 bit-operations) per cycle and the FFT does not: at this size bit-operations and seconds differ by a factor of about 750. On a G4-class card (weak FP64) the FFT side is worse still.
- **The right comparator for a scattered number is not row-wise trial division.** F(N) is a product of known linear forms, so each prime costs one reduction of N and one lookup, independent of n. Bernstein on 1,502 unrelated 665-bit numbers throws that structure away.
- **Floor of the window sieve**: the strike events, n * sum over 463 < s < J of 1/s = 1,513 per member at J = 2*10^7, each touched once. A faster evaluation of all members cannot beat that by more than the constant of the marks (bit-sliced tables for groups of primes below 10^4 save about 20%).
- **Stake of a cheaper sieve** (my cost function reproduces the Opus table to 0.01 nat: best keep 1.51% at rho = 0.0118, gains over the 1.5% keep 0.48 / 0.18 / 0.03 / 0.20 / 0.40 at rho = 0.001 / 0.003 / 0.02 / 0.05 / 0.1; theirs 0.47 / 0.17 / 0.03 / 0.21 / 0.42; `q1_stake.py`). From the G4's rho = 0.0054: 0.0027 gives +0.28 nats, 0.001 gives +0.66, 0.0003 gives +1.09, a free sieve +2.72 (no pool limit). About 0.3 nats per halving.
- **The lone number** (`q1_cost.py` part c): own sieve to 10^6 and a 3% cut, 1,116 rows alive at depth 2,000. The loss against the fleet's 1.5 is a function of the sieve cost per N:

  | sieve cost per N in tests | 0.25 | 0.65 | 1.2 | 2.5 | 5 | 7.3 | none (test as it comes) |
  |---|---|---|---|---|---|---|---|
  | loss, nats | 1.18 | 1.56 | 1.91 | 2.45 | 3.04 | 3.38 | 3.12 |

  In cycles on a CPU the per-N sieve to 10^6 is 1.2 to 7 tests, so a lone ideal N costs **1.9 to 3.4 nats**, and an enumerator has to gain at least that before it pays. The card's own per-N sieve cost is the number to take from the GPU session.

### 1.2 Systematic relations in the integers?

No, and I think the reason is structural, not a lack of imagination.

- Joux (2013) and Barbulescu-Gaudry-Joux-Thome get relations free from x^q - x = prod over a in F_q of (x - a) **and** the group PGL_2(F_q), which acts transitively on the complete row set P^1(F_q): every Moebius image of the one identity is a new relation. Result 1 of your README (Swan's parity in F_3[x]) is the same phenomenon: the discriminant is a square or not.
- In Z the only complete row sets are residue systems: prod over a mod s of (N - a) = N^s - N = 0 mod s, so every run of s consecutive integers is divisible by s. For our rows (primes below Q alive after the cover: 0.75% of the integers below Q) this holds for no prime above about n / ln n, and for the smaller ones it is the cover's own mechanism (a pinned class is an empty class). There is no group acting on a sparse row set: translation maps rows to non-rows. One identity gives one relation.
- Kummer: for a run of consecutive rows prod over q < k of (N - q) = k! * C(N, k), with the valuations forced by carries. Our rows are primes, not runs.
- Algebraic reducibility of N - q (x^2 - y^2, x^4 + 4y^4, cyclotomic): only for q in a sparse set (at most 155 rows below Q for degree 2: ROWS_AND_GAPS row 1, net -6.6 nats).
- Quadratic reciprocity gives the Jacobi symbol (N / (N - q)) from N mod q: one free bit per row at one reduction. For a prime N - q it is the Legendre symbol; for a composite it is +-1 with no relation to the number of prime factors; comparing it with q^((N-q-1)/2) is a Fermat test.
- **Why the grammar is closed (heuristic, not a theorem).** A systematic relation along a one-parameter family N = f(t) is a bias, uniform in t, in the divisibility or primality of f(t) - q. Bateman-Horn and Schinzel's Hypothesis H fix the density of prime values of polynomial families by local factors and algebraic factorisation alone; the Chowla and Sarnak conjectures say the Liouville function has no bias along zero-entropy sequences (known for progressions by the prime number theorem, for nilsequences by Green and Tao). The exceptions allowed are exactly the congruences (pins) and the identically reducible forms, which is the grammar L of the closure theorem. A family outside it would be a counterexample to Hypothesis H for that family, and a cheap parity predictor in Z would contradict Chowla.

### 1.3 Roots modulo medium primes without paying their logarithm?

Not that I know of, and the structure argues against it.

- The number field sieve pins the small primes (Kleinjung 2006 makes the leading coefficient divisible by small primes; Murphy's alpha is a sum of per-prime root terms) and treats the medium primes by a root sieve over the (u, v) family (Kleinjung 2006; Bai, Bouvier, Kruppa and Zimmermann 2016: not read, from memory): a scan of the family at a few operations per member, keeping the extreme. That is soft by the Gaussian maximum (z = sqrt(2 ln |family|)) and linear in the family: our window sieve, not a sublinear method.
- Our family has rank 1: the integers preserving N mod r for all r <= 463 are MZ. The only multi-parameter structure is the near-optimal covers times the window, N = sum of c_r e_r + M k with c_r in a small set C_r, where N mod s is **linear in the coordinates**. A special-q (pin one prime s_0 > 463 at its best class) is an index-s_0 sublattice of that box: it costs ln s_0 nats of family entropy and pays 0.024 w nats.
- The exchange rate on my cover (`a12_numbers.py`; w = rows of the best class mod s among the alive rows):

  | s | 467 | 479 | 503 | 541 | 701 | 1,009 | 2,003 | 5,003 | 20,011 | 100,003 | 200,003 |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | w | 9 | 9 | 8 | 7 | 7 | 5 | 5 | 3 | 2 | 1 | 1 |
  | nats of exponent per nat of entropy | 0.035 | 0.035 | 0.031 | 0.027 | 0.026 | 0.017 | 0.016 | 0.008 | 0.005 | 0.002 | 0.002 |

  The cover itself pays 0.036 per nat. Whether a pin beyond 463 gains anything depends on the price of a nat of family entropy in rows of cover quality (section 2: about 0.5 row, 0.012 nats) **and** on the window: the sieve's set-up (R * pi(B) start positions per vector) is amortised over the window, which holds the depth near the window length (Opus, `b_answer.md`, items 5 and 7), and the 16.9 nats are that window. A pin beyond 463 would have to be paid by dropping a smaller one, which kills about as many rows. Opus's window-for-modulus trade is the same exchange and found +0.14 nats against fixed costs.
- Your ratchet result (both end at 18 rows) fits the accounting: pins, cover family and window are paid from the same 460 nats.

## 2. The accounting, and the supply of covers

**Where the exponent goes** (`a12_numbers.py`, `cover_rem.py`; exponent = rows * kappa, kappa = 0.02428):

| step | entropy used | rows | exponent | per nat |
|---|---|---|---|---|
| all 17,983 odd primes below Q, N even (row prime with chance 2/ln N): the mean number of representations, a first-moment exponent | 0.7 | 17,983 | 78.3 | |
| N not divisible by any odd r <= 463, random nonzero classes | 1.7 | 2,150.9 | 52.2 | 15.5 |
| classes optimised: campaign / mine | 443 | 1,502 / 1,524 | 36.46 / 37.00 | 0.036 |
| window: the members of one class vector | 16.9 | | -6.6 ideal at the pool 2*10^7; -2.4 realised | |

- **Rate of the cover.** Random nonzero classes leave a mean of 2,150.9 rows with sd 23.98 (4,000 samples, skew -0.04, excess kurtosis 0.02), so one sd is 0.58 nats. A Gaussian random-energy model with ln(number of covers) = 441 has its optimum at z = 29.7, 1,438 rows, 17.3 nats below the mean; the best known takes 15.8. At Q = 170,000 the same estimate reads mean 1,853.4 (Research quotes 1,853), sd 22.86, floor 1,174, against Research's thermodynamic-integration floor 1,214 and best cover 1,248: the Gaussian model is a loose lower bound (40 rows low there), and Research's floor is the one to use. The cover is at its optimum to within a few rows; there is no headroom in the optimiser.
- **Rate of the window.** Survivors at depth B are binomial with sd 18.0 at B = 10^8; a survivor is prime with chance p' = 0.0712, so the hit-mass tilt per sd is kappa' * sd = 1.33. The selection ceiling for a pool J is about 1.33 * z_max(J) - 0.9: 6.3 nats at 2*10^7 (ROWS_AND_GAPS row 6 has 6.6 at B = 2*10^7).
- **The price of a pin beyond 463** is in section 1.3: 0.035 per nat at the first, already at the cover's own average (0.036), and below half of it from about s = 1,000.
- **Digits.** The exponent scales as 1/ln N (0.18 nats per digit) and the pins add about 0.05 to 0.08 per digit: the 5.4 nats are about 22 digits.

**Supply of covers** (`dos_gf.py`, `dos_check.py`). A hit needs about 3.6*10^8 = e^19.7 covers (one window per cover, 2.2*10^7 members each). Counting covers from single-prime moves of my best cover, with costs additive across primes (cost of moving the pin at r to class c' = unique kills of r minus the rows alive without r that lie in c'), the number of covers within Delta rows of the best is

| Delta (rows) | 0 | 1 | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|
| S = ln(count), nats | 0.7 | 4.4 | 7.4 | 10.1 | 14.8 | 21.0 | 24.8 | 33.5 | 41.5 | 55.9 |

with a slope of 2.8 nats per row at the optimum and 1.8 at Delta = 8. The additive-move assumption was checked by applying random sets of 2 to 8 moves: true minus predicted alive rows has mean 0.00, -0.03, 0.02, 0.01, -0.18 and sd 0.33, 0.60, 0.73, 1.10, 1.69 for 2, 3, 4, 6, 8 moves. So the supply costs 8 rows (0.19 nats) by this count, an upper bound since other basins add covers; Research's table at Q = 170,000 (e^4 covers at the best level, then x50, x22 falling to x11 per row) gives about 5 rows (0.12 nats). **The price of a nat of family entropy is 0.4 to 0.55 row, 0.010 to 0.013 nats.**

## 3. The three reformulations

### 3.1 The dual

g(N) >= Q says every prime P in the window (N - Q, N) has N - P composite. Numbers on my cover (`a12_numbers.py`): the window length is (ln N)^1.990; it holds Q / ln N = 434 primes in expectation; 17,893 positions (8.9%) are odd and outside the pinned classes ("rough"); 1,524 of them (8.5%) have a prime offset N - x, the forbidden positions; each rough position is prime with chance pi = 0.02398.

- The success event is "no prime at a forbidden position": expected overlap n * pi = 36.6 = the exponent. It does **not** depend on how many primes the window holds, because the prime chance of a rough position does not depend on the others. A prime-poor window (Maier's matrix method works at lambda > 1, here 1.99) is worth nothing by itself: depleting positions that are not forbidden changes R, not n * pi. The only handle is a kill at a forbidden position, which is the row count. The same event for "no prime in the whole window" would be e^-434 against e^-36.6: Goldbach gaps are cheap compared with prime gaps because only 8.5% of the rough positions matter.
- Each pin kills forbidden positions by one divisibility; the dual adds nothing computable more cheaply than the rows: the window primes themselves would have to be located (18,000 tests) where the rows need about 33.

### 3.2 The geometry

For s above Q a kill is "N mod s lies in [0, Q) and is an alive row": all arcs sit in [0, Q/s] and are 0.75% filled; for s below Q they wrap and fill n/s of the classes. Simultaneous inhomogeneous approximation obeys the volume bound: k pins at primes s_i have a solution below X only if the product of the s_i is below about X. So a kill by a large prime costs ln s >= 12.2 nats for 0.024 nats (0.002 per nat), and the arcs have no structure to exploit because the rows (primes) are random modulo s. The table in 1.3 is the geometry in numbers. **The image of the rows is dense in an interval for no prime and no multiplier**: q * u mod s maps the primes to random classes.

### 3.3 Additive structure of the ideal set

Model: the window N(k) = c + M k, so N(k + d) mod s = N(k) + M d mod s and the strikes are shared exactly when s divides d. A whole window of 2*10^7 members was simulated (`a3_pairs.py`: my 1,524 rows, 460 primes in (463, 4,000], strike count F(k) = rows struck, mean 445.3, sd 19.4 = the model's). The top set T is the best 1% (215,257 members, threshold +2.35 sd); A(d) = number of pairs k, k + d in T by FFT, against the independent value (J - d) (|T|/J)^2 and the Gaussian shared-variance prediction rho(d) = sum over s | d of var_s / var_total:

| lags d <= 2*10^6 | number | top 1%: measured (Gaussian) | top 0.1% (23,149 members, +3.12 sd): measured (Gaussian) |
|---|---|---|---|
| no band prime divides d | 1,454,759 | 0.993 (1.000) | 0.989 (1.000) |
| exactly one band prime | 506,317 | 1.015 (1.025) | 1.023 (1.038) |
| exactly two | 38,924 | 1.050 (1.061) | 1.079 (1.097) |

by the prime (top 1%): s in 463 to 600: 1.038 (1.048); 600 to 900: 1.026 (1.036); 900 to 1,500: 1.014 (1.023); 1,500 to 2,500: 1.006 (1.015); 2,500 to 4,000: 1.001 (1.010); top 0.1%: 1.061, 1.041, 1.022, 1.010, 1.002. **The sum of A(d)^2 over d <= 2*10^6 is 1.0000 (top 1%) and 0.9997 (top 0.1%) of the independent value.** So the good members are additively unstructured beyond the correlation of shared pins (a few percent at multiples of one or two band primes, 1 to 2 points below the Gaussian prediction); no map sends good N to good N, which is Research's neighbour identity seen from the other side (0.036 at the campaign's cover). The set of good class vectors is not a coset structure either: the annealing landscape is rugged (plateau at 1,524 for two seeds over 70M steps).

## 4. The computational literature (point B)

The bare problem: primes s_1 .. s_m, a weight w_s(a) per class (here row counts, essentially independent Poisson noise), find N < X maximising the sum of w_s(N mod s), X far below the product of the primes. This is list recovery of the CRT code with dense lists and partial agreement; the message is 16.9 nats against 460 primes, rate about 0.4% ("k" is 2 or 3 moduli).

- **Algorithms (literature)**: Goldreich-Ron-Sudan, "Chinese remaindering with errors" (STOC 1999, IEEE Trans. IT 2000, ECCC TR98-062): all integers agreeing with at least t of n residues when t is of order sqrt(k n log p_n / log p_1); Boneh (STOC 2000, JCSS 2002); Guruswami-Sahai-Sudan (FOCS 2000); Howgrave-Graham (2001); Cohn and Heninger, "Ideal forms of Coppersmith's theorem and Guruswami-Sudan list decoding" (arXiv 1008.1284) and "An algorithm for list decoding number field codes" (arXiv 1107.2321). All are Johnson-type. For this instance my LATTICE_CHECK gives a ratio of 0.36 of the needed agreement at best (closed form ratio^2 <= ln(1 + n/x)/ln K = 0.086).
- **Bleichenbacher and Nguyen, "Noisy polynomial interpolation and noisy Chinese remaindering" (Eurocrypt 2000)**: not read beyond the abstract (the full text is on an ftp link and behind a login); the abstract says the problem reduces to the shortest vector problem when the parameters satisfy a condition the paper makes explicit, and that lattice reduction solves most practical instances. My derivation of the regime, **not a quote**: with the true residue among m candidates at *every* modulus, the candidate polynomials combine by the Chinese remainder theorem into one polynomial G of degree m with G(x) = 0 mod P, and Coppersmith finds every root x < P^(1/m). Our instance is the other regime (agreement at a fraction n/s of the primes, lists of 25 to 100% of the classes), where solutions exist but are not findable that way.
- **Existence beyond the Johnson bound (literature)**: randomly punctured codes with good distance are list recoverable beyond the Johnson bound, hence some Reed-Solomon codes (Goldberg-Shangguan-Tamo, arXiv 2005.02478); random Reed-Solomon codes reach the generalised Singleton bound (Brakensiek-Gopi-Makam). The 2026 ECCC report TR26-164, as quoted by the search tool, says that for random evaluation points "no efficient algorithm is known to attain their beyond-Johnson decoding radius".
- **Hardness (literature)**: maximum-likelihood decoding of Reed-Solomon codes is NP-hard in the worst case (Guruswami-Vardy 2005, from memory); Gandikota-Ghazi-Grigorescu (arXiv 1611.03069): bounded-distance decoding is NP-hard beyond N - K - c log N / log log N errors, with field size exponential in the block length; Cheng-Wan (arXiv math/0405082): list decoding of Reed-Solomon codes beyond the Johnson radius is infeasible unless discrete logarithms are easy in a related field. A "fuzzy simultaneous congruences" problem is NP-hard (a Kiel University paper found by search, not read). **None of these is an average-case result for random lists.**
- **The same regime is a cryptographic assumption**: the Polynomial Reconstruction problem with agreement below sqrt(kn) (Naor-Pinkas 1999; Kiayias-Yung, ICALP 2002 and ePrint 2007/153, with parameter choices "where decoding is not known to be efficiently solvable"); the sparse-list full-agreement regime was broken by Bleichenbacher-Nguyen; Kiayias-Yung cryptanalysed a Polynomial-Reconstruction public-key scheme (Asiacrypt 2004). I found no break of the partial-agreement regime in the literature I read.
- **Not found**: a low-degree, statistical-query or sum-of-squares lower bound for Reed-Solomon or CRT list recovery; any algorithm for the planted weighted-CRT problem with a deficit exponent below the trivial one; a sub-exponential method. So "an algorithm with an exponent below 1/2 in the deficit would be news" stands, and so would a hardness proof for a model that contains our pipeline.
- **A remark of mine** (not in the literature I read): the window problem is a maximum-likelihood decoding of a low-rate code in the noise-dominated regime; for random linear codes at low rate the best known method is enumeration of the codewords (information-set decoding only helps at high rate), here e^16.9 members. The best member of a window is spread over all primes (each contributes about +0.2 of its own sd), so no information set concentrates it.

## 5. Calibration of the success model on the published records

Data: the OEIS record tables A025018 (first even N where the least prime in the Goldbach partition increases) and A025019 (that prime), Oliveira e Silva's computation: 69 records up to N = 3,325,581,707,333,960,528; the prime is listed for the first 67 (to p = 9,341 at N = 9.06*10^17). The page with the last two (sweet.ua.pt) could not be fetched; my memory of p = 9,781 for the last is unconfirmed and not used. `records.txt` holds the table.

Model (`rec_mc.py`, `rec_rescale.py`): for even N and level P (all odd primes below P fail), a cover is the class vector (N mod r, r <= R) with R the largest prime such that the product of the odd primes up to R is at most N/30; k = number of odd primes p < P with N - p coprime to all r <= R, sampled over uniform classes (2*10^5 covers, effective sample sizes 10^4 to 3*10^4); a cover with k alive rows succeeds with probability (1 - pi)^k, pi = 2 prod r/(r - 1) / ln N. No Gaussian approximation (my first attempt used one and was wrong: at these N the tilt beta * var exceeds the mean, the distribution of k is far from Gaussian).

**Time rescaling** (exact under a Poisson model of hits): after record k - 1 the next record is the first N with g(N) > p_(k-1); the integral W_k of the predicted hit intensity between records is Exp(1) and independent across k, and the level of the new record has a survival function S whose value U_k at the observed level is uniform.

| records | N | mean ln W (Exp(1): -0.58) | excess, nats | mean U (0.5) |
|---|---|---|---|---|
| k = 28 to 39 (12) | 4*10^7 to 2*10^10 | +0.06 +- 0.37 | +0.64 | 0.50 |
| k = 40 to 53 (14) | 4*10^10 to 5*10^13 | +0.28 +- 0.34 | +0.86 | 0.50 |
| **k = 54 to 67 (14)** | **8*10^13 to 9*10^17** | **-0.51 +- 0.34** | **+0.06** | 0.35 +- 0.08 |
| all 40 | | -0.06 +- 0.20 (KS against Exp(1): p = 0.009) | +0.52 | 0.45 +- 0.05 (KS p = 0.38) |

With the truncation prime R larger (N * 10^3 in the rule) the last bin reads -0.57 (excess 0.00) and the middle one -0.21 (0.78); smaller R: -0.43 (0.14) and +0.40 (0.97). A grid test of Lambda(N, F(N)+) at ten decades gives mean ln Lambda -0.12 (Exp(1) -0.58), the same excess. The cover-level check of each record holder (33 holders, p >= 1,000): weighted CDF of its own alive-row count under the tilted measure, mean 0.41 +- 0.05 (KS p = 0.053): holders have about a quarter of a sd fewer alive rows than the model's tilted mean, 1 to 2 rows.

**Reading.** Where the exponent is the fleet's (30 to 40 nats at the record holders with N >= 8*10^13), the model predicts the observed inter-record times with no excess (+0.06 +- 0.34 nats; 0.00 with deeper conditioning); below 5*10^13, where a row is prime with chance 0.25 to 0.3 and the truncation is shallow, it over-predicts hits by 0.6 to 0.9 nats, and the excess shrinks with N and with R. The effective prime chance among alive rows that would explain 0.5 nats at k = 200 is a 1% excess in pi, so the data constrain pi to about 1% (one sd) over 10^8 to 10^18. The fleet's own checks at 300 and 400 digits (per-member exponent e^-20.86 against e^-20.90; 329 hits against 355 expected, 6 against 6.0, 10 against 9.0) say the same at its scale. The level statistic is uniform overall and mildly low (0.35 +- 0.08, 1.9 sd) at the top: levels jump slightly higher than the model's conditional law, which if real would make the exponent grow more slowly with Q than modelled; not significant. **The budget's 36.46 is not contradicted by 69 real records; if anything the model is 0 to 0.1 nats optimistic at the right scale and 0.5 to 0.9 below 10^14.**

## 6. What would count as progress, with the number each item needs

| item | what it must do | worth |
|---|---|---|
| a cheaper window sieve | rho from 0.0054 to 0.0027 / 0.001 / 0.0003 | +0.28 / +0.66 / +1.09 nats |
| per-N sieve on the card | cost per lone N below 1 test, with an enumerator that outputs ideal members at depth 1,500 to 2,000 | the loss of a lone N is 1.2 (0.25 test) to 3.4 (7 tests) nats |
| a sublinear finder of the extreme members of a window | list at least 100 of the top 10^-4 of 2.2*10^7 members at under 10^-2 of the window's sieve cost | up to 2.7 nats (free oracle, best keep 10^-5); lattice decoders reach 0.36 of the needed agreement, so a new idea is required |
| a cheap statistic of primality beyond the sieve | find, among about 500 survivors, a subset of at least 15 rows whose prime chance is 0.19 instead of 0.071 (first prime in about 5 tests instead of 13.9) at under 0.018 test per surviving row | 1 nat; none known (Jacobi symbols carry no information on primality) |
| a family outside the grammar L | force 15 rows at V >= N^0.98 members, or unpin at most 2.6 primes (ROWS_AND_GAPS) | 0.36+ nats; would contradict Hypothesis H for the family |
| a better cover | 1,502 to 1,490 | 0.3 nats; the thermodynamic floor says a row or two at most |
| more digits | 22 more digits at the same method | 5.4 nats |

## 7. Corrections to my earlier notes

- `LATTICE_CHECK.md` section 5 and `iso_check.py`: the isolated-N sieve to 10^6 was taken at 0.25 to 0.65 tests per N (instruction counts). In cycles on this CPU (a test is 2.7*10^5 cycles, a reduction plus lookup 4 to 25) it is 1.2 to 7.2 tests; the lone-N loss is 1.9 to 3.4 nats, not 1.2 to 1.6, and testing as it comes (3.1) is within the range. The fleet's own per-N cost on the card replaces mine.
- `iso_check.py` part (1) printed the Opus rho (sieve cost per member over the 13.9 tests of a kept member) as a cost per member in tests: the labels were wrong by the factor 13.9; the 1.48 to 1.50 at a 3% keep does not depend on it (1.5 reproduced). `q1_stake.py` redoes it with the right units and reproduces the Opus table.
- My message of 18:05 UTC gave the window sieve as 0.005 to 0.08 tests per member; it is rho * 13.9 = 0.075 (G4), 0.11 (L4), 0.13 (T4).
- `rec_ktest.py` (a Gaussian version of the record test) was removed: its z of 15 was an artefact of the Gaussian cumulants at these N.
- The alive rows of an event were counted with the odd primes up to 463 as the cover's moduli in `fleet_ovs.py`, `scan_tally.py` and the first version of `nearmiss_rescale.py`. The GPU session's correction (23:18Z 25 Nov): the 491 family (vector names `q170000_m89r491_...`) has the first 88 odd primes (3 to 461) and 491, not 463 (its residual list below 170,000 has 1,250 rows; the 463 set gives 1,257), and the 479 family of the CPU scan has the first 88 odd primes and 479. The three scripts now take the moduli from the vector name (`m89r491`, `m89`) or the family, and `nearmiss_rescale.py` uses the card's own row counts when the event carries them (`rows`). Effect on every number reported: none at the precision shown (the fleet's 11 events 596 rows against 446.8, 1.33 +- 0.31 unchanged; the scan's 42 finds 1,410 against 1,705.5, 0.83 +- 0.16 unchanged; the first calibration event 131 alive rows past 140,000 becomes 130, the card's count); only the 9 older events of the fleet (vectors `r200b_q122k`, `r200_q122k_k850`, `r200_q140k`, `pt_q150k`) still use the odd primes up to 463, because their covers are not at hand, and a modulus set that differs by one prime moves a count by one row in 40 (R = 463 against 491: 1.33 against 1.34).

## 8. Follow-up to Research's message of 18:40 UTC: the fleet's own record sequence, the overshoot law, and families outside the grammar

### 8.1 The fleet's expected against found, from its own tally

Source: `goldbach/phd/campaign3_gpu/TALLY.md` on `ccr-8ffe9d7a-4ni11u` (regenerated 10:25 UTC from the cards' logs). "Expected" is the sum of (1 - p^)^c over the tested members, p^ the batch's measured prime rate, or for the slices before 22 Nov 20:50 UTC members * hit% * exp(-1.0275 E^ + 0.33).

| campaign | exponent E^ | expected | found |
|---|---|---|---|
| Q = 122,000, 867-872 rows | 20.9 | 2.089 | 3 |
| Q = 122,000, 850 rows (Lean cover) | 20.4 | 5.028 | 4 |
| Q = 122,000, full mass | 21.0 | 0.110 | 0 |
| Q = 140,000 | 24.15 | 1.274 | 1 |
| Q = 150,000 | 26.2 | 1.282 | 1 |
| Q = 170,000, design hits | 30.0 to 30.2 | 0.598 | 0 |
| Q = 170,000, near-misses at the record of the time (where logged) | 28 to 29 | 2.431 | 2 |
| all | | 12.81 | 11 |

The excess ln(found/expected) is **-0.15 +- 0.30 nats** (Poisson); at exponents of 24 and above 5.59 expected against 4 found, **-0.33 +- 0.50**; at 20 to 21, 7.23 against 7, -0.03 +- 0.38. (Updated at 20:25 UTC with the final snapshots of gold-g4g, gold-g4h, gold-l4g, gold-l4i and gold-xt4c, 19:00 to 19:44Z: expected design hits +0.070, expected near-misses at 160,357 +0.226, nothing found; the 10:25 figures were 12.52 and -0.13. gold-l4j's snapshot is not counted, its directory repeats gold-l4g's lineage: at most +0.02.) So the fleet's own record sequence agrees with its model within the error, which is too large for "a few tenths"; and the oldest rows use a formula with a fitted constant, so this tests the fleet's accounting, not the a priori model. (Against the 69 published records the a priori model has +0.06 +- 0.34 at the same exponents, section 5; the two checks are independent.)

What reaches +-0.2 nats at exponents 25 to 31 is the all-g log. Events per day with g >= T, from the Opus session's `campaign_table.py` on its 491-family 170,000 cover (1,250.5 rows run) at today's 0.19 design hits a day (`fleet_rates.py`; the same model gives 3.9 times the design-hit rate at >= 160,357 where the fleet's tally gives 3.2, so read the rates as +-25%):

| T | 135,000 | 140,000 | 145,000 | 150,000 | 155,000 | 160,357 | 165,000 |
|---|---|---|---|---|---|---|---|
| exponent at T | 24.7 | 25.7 | 26.6 | 27.5 | 28.2 | 29.0 | 29.6 |
| events a day | 40 | 16 | 7.1 | 3.0 | 1.6 | 0.74 | 0.41 |
| days for 25 events (+-0.2 nats) | 0.6 | 1.5 | 3.5 | 8.4 | 16 | 34 | 62 |

The flag exists (`--near-miss 140000`, tested in `check_nearmiss.sh`); it is the GPU session's and Research's to set.

### 8.2 The overshoot law is the lever on the 200,000 forecast

A hit at the design level D is decided beyond D by the cover's alive rows in [D, G), each composite with probability 1 - p, so the overshoot (alive rows before the first prime) is geometric with mean (1 - p)/p = 41. There are 299 alive rows between 170,000 and 200,000, so the model suppresses a hit at 200,000 by e^-7.27, and a per-row prime chance beyond D that is 1/theta of the model's moves the forecast by e^(7.27 (1 - 1/theta)). With the Opus session's table as the base (`fleet_sens.py`; theta = 1 reproduces its 46.2, 16.7, 5.65, 1.40, 0.45, 0.13%):

| theta (mean overshoot / model) | P(final >= 175,000) | 180,000 | 185,000 | 190,000 | 195,000 | 200,000 |
|---|---|---|---|---|---|---|
| 0.80 | 37.4% | 9.7% | 2.4% | 0.41% | 0.10% | 0.02% |
| 1.00 | 46.2% | 16.7% | 5.65% | 1.40% | 0.45% | 0.13% |
| 1.26 | 54.2% | 25.7% | 11.3% | 3.8% | 1.55% | 0.59% |
| 1.50 | 59.3% | 32.9% | 17.0% | 7.0% | 3.3% | 1.49% |
| 1.58 | 60.7% | 35.1% | 18.9% | 8.2% | 4.05% | 1.90% |

Evidence on theta (`ovs.c`, `ovs_test.py`, `rec_ovs.py`):

| data | hits | observed / model overshoot | mid-PIT mean (0.5) |
|---|---|---|---|
| the exact miniature, N < 10^9, Q = 1,000, every hit by brute force (R = 23, 47, 97, 199) | 303 | 0.97, 0.98, 0.98, 1.01 +- 0.07 | 0.505 to 0.518 (se 0.017) |
| the published record holders, exact (N >= 10^6; R = 23, 47, 97) | 46 | 1.24, 1.27, 1.27 +- 0.18 | 0.42 to 0.43 (se 0.043) |
| the fleet's 11 events from their N alone (`fleet_ovs.py`: the 9 design hits of TALLY.md's overshoot table and its 2 near-misses; the odd primes to 463 for the 9 older vectors, the vector's own moduli for the 2 newest) | 11 | 1.33 +- 0.31 (596 rows against 447; TALLY's own count for the 9 hits alone is 579 against 367, 1.58 +- 0.34) | 0.40 (se 0.087) |
| the uarch session's calibration ladders at 100 and 150 digits, real pipeline hits (Research, `sublinear/frontier_overshoot.py`, commit 5a4da41 on `ccr-d4a17dd0-7uu03r`; rows above the target not sieved) | 666 | 0.975 +- 0.040 (14,940 rows against 15,329) | 0.491 (se 0.011) |
| the 200-digit CPU scan of section 8.4 (the 479 family, Q = 80,000: the pipeline's 42 finds, each recomputed from its N; rows above the target not sieved) | 42 | 0.83 +- 0.16 (1,410 rows against 1,705) | 0.554 (se 0.045) |
| pooled by inverse variance (Research's three-sample pooling 0.99 +- 0.03 with the 1,026 hits above, then the scan) | 1,068 | 0.98 +- 0.03 | |

**No evidence for a heavier tail, and Research's 666 real pipeline hits settle it (0.975 +- 0.040): theta = 1 stands at 100 and 150 digits and the forecast's tail with it.** The exact miniature fixes the law to 7% (at a row prime chance of 0.3 to 0.5), the records are 1.4 sd high and the fleet's 11 events 1.1 sd high (1.7 sd for TALLY's 9 hits alone: the two near-misses survived only 4 and 16 rows). But the number that matters sits at 200 digits and rests on 11 fleet events with +-31% and the scan's 42 finds at Q = 80,000 with +-19% (0.83 +- 0.16, section 8.4), and the forecast of the 200,000 chance moves by a factor 4.5 for theta = 1.26. By construction theta = 1: p = p' c with p' measured by the fleet's own tests (1 prime in 14, billions of tests) and c the exact sieve survival. The one mechanism that could lengthen the overshoot is a correlation between the survivors below the design level, where the members are selected, and those beyond it. Whole simulated window (`block_corr.py`: my cover split at 170,000, 1,310 and 214 alive rows, strikes by the 460 primes in (463, 4,000], the same residues for both blocks): The correlation of the two blocks' strike counts over the window is -0.0226 (the exact covariance gives -0.0226; -0.0176 with sieve primes to 10^5 and -0.0130 to 2*10^6, `block_cov_theory.py`), and the best 1%, 0.1% and 0.01% of block 1 (+2.7, +3.4, +4.0 sd) have 0.06, 0.07 and 0.08 sd FEWER strikes beyond the design level (0.5 to 0.6 of 62.5), i.e. 0.7 to 1% more survivors there. If anything the overshoot of the selected members is marginally shorter (theta about 0.995), so selection cannot explain a heavier tail; a covariance of this size is zero within the pair fluctuations of this row set (sd about 10 against -3.1).

Two direct measurements settle it: (a) sieve the alive rows in [170,000, 200,000) of the kept members and of unselected members and compare the mean survivors (equal means theta = 1 exactly, fewer for the kept means theta > 1); (b) every logged member with g >= T is a geometric overshoot sample beyond T (mean 41 alive rows), so 25 events at T = 140,000 give theta +- 0.2. (b) was run on the CPU scan at T = 80,000: 42 events, 0.83 +- 0.16 (section 8.4).

### 8.3 Families outside the grammar, with local densities biased at the medium primes

Research's question: any construction of integers with prescribed local behaviour at many primes, whose members are not sub-progressions, with biased densities at the medium primes? **No example, and the reason is a counting argument, not a gap in my reading.**

What the members are, construction by construction:

| construction | its members | bias at the primes | price |
|---|---|---|---|
| Erdos 1935 / Rankin 1938 | one progression: a class for each prime up to y | one class per prime, chosen greedily | ln p per prime |
| Maier's matrix method (Michigan Math. J. 1985) and its adaptations (Hildebrand-Maier; Friedlander-Granville progressions with more or fewer primes than usual) | rows are short intervals, columns are progressions modulo a primorial: sub-progressions with class 0 at every prime up to y | uniform: it changes the count R of rough positions in the window | ln p per prime; here R is irrelevant (section 3.1): 0 nats |
| Ford-Green-Konyagin-Maynard-Tao (JAMS 2018) | the Chinese remainder of one class per prime, the classes of the large primes chosen by a random hypergraph covering (Rodl nibble, generalising Pippenger-Spencer) so as to cover the leftovers | biased at the LARGE primes | ln p per prime (about x nats for a gap built from primes up to x); the smallness hypothesis needs ln x >= 10^5 against 6.1 at x = 463 (ROWS_AND_GAPS) |
| Maynard-Tao / GPY weights | not integers: weights on all n of a progression modulo W, tilting the divisibility by every prime up to the sieve level | toward ROUGHNESS of the shifts, the wrong sign for an all-composite event; for that event the rows left S are sufficient under independence (Opus, `b_answer.md`), so no weights beat S | a sample from the weights is rejection from the uniform: e^KL |
| Sierpinski/Riesel covering sets (Selfridge: 78,557, covering set 3, 5, 7, 13, 19, 37, 73) | k in one progression modulo the product of the covering primes (18.1 nats) | kills every row k 2^n + 1, because divisibility by p is periodic in n with the tiny period ord_p(2) | 18.1 nats for infinitely many rows; the rows here are primes, equidistributed modulo p, so a pin kills only 1/(p-1) of them (443 nats for 15,500) |
| Granville-Soundararajan, "An uncertainty principle for arithmetic sequences" (Annals 2007; the ICM 1994 survey "Unexpected irregularities in the distribution of prime numbers" is Granville's alone) | a theorem: no sequence is equidistributed in all progressions | | non-constructive |

**The counting.** For a product measure the exchange is exact: biasing the classes of a set of primes with total divergence S from uniform shifts the strike count by sqrt(2 S V), V the variance of the weights (the Gaussian-tail law of section 2). The fleet's keep of 0.85% is z = 2.4, S = -ln f = 4.8 nats of selection; with a free sieve, closing the 5.4 nats (1.34 tests per unit of mass down to 0.0061) needs the top 1.3*10^-10 of the members, z = 6.3, S = 22.7, so **18 nats of divergence more, delivered at the price of a test**, not of a sieve at 0.075 test per member. Two ways to pay it:
- **pins**: 18 nats at the best price beyond 463 (0.035 nats of exponent per nat of entropy, section 1.3) buy 0.63 nats, not 5.4, and the room is 16.9 nats, all of it the window;
- **a soft bias at the 460 medium primes as a product measure**: this is the cheap way (18 nats for +6.0 sd of the strike count) but it needs N to carry the product of those primes, the sum of ln s over those 460 primes, 3,468 nats, against 16.9 nats of room: 205 times too little. Within 10^200 every such bias is a selection out of the 2.2*10^7 members of a window, i.e. a sampler for the Gibbs measure of the strike count on 2.2*10^7 integers cheaper than rejection (e^KL). The strike field has no structure to sample by (additive energy 1.0000, section 3.3), the only method known is rejection, and lattice decoders reach 0.36 of the agreement they need (LATTICE_CHECK.md).

So the family sought would have to be a fast sampler of the window's Gibbs measure; every construction in the literature above either pins classes (a sub-progression, priced at ln p) or is an existence argument with weights that cannot be sampled. That none of them is constructive at 200 digits is the same statement as the open problem of section 4.

### 8.4 The idle-core CPU scan at 200 digits: the record target, and a calibration of the pipeline's accounting and of the overshoot law

The lead's ruling of 19:52Z put idle session cores on 200-digit covers the fleet does not use. I ran four cores (nice 10) of the uarch session's pipeline (`sieve200/search_c.py`, fm13 Fermat) on the 479 family (the first 88 odd primes and 479; 2.06*10^7 members per cover): three at the record target 160,367, one at target 80,000 as a calibration, where events are frequent enough to test the pipeline's expectation (K * hit% * e^-E^ per cover) and the overshoot of every find from its N (`scan_tally.py`). Ledger, logs, finds and scripts: `data/bottomup/scan479/`.

| | record target 160,367 | calibration, target 80,000 |
|---|---|---|
| covers (2.06*10^7 members each) | 273 | 114 |
| core-hours; Fermat tests | 6.36; 1.36*10^9 | 2.09; 5.7*10^8 |
| mean E^ (the pipeline's exponent, nats) | 28.64 | 15.23 |
| expected successes | 0.000275 | 46.74 |
| found | 0 | 42 |
| ln(found / expected) | | -0.11 +- 0.15 |
| overshoot (rows survived beyond the target, from N alone, the moduli of the 479 family: the first 88 odd primes and 479) | | 1,410 against 1,705 expected: 0.83 +- 0.16 (mid-PIT 0.554, se 0.045) |

- **The pipeline's accounting is right at E^ = 15**: 42 found against 46.7 expected, -0.11 +- 0.15 nats, the same size as the fleet's -0.15 +- 0.30 at exponents 25 to 31 (section 8.1, the other pipeline). It says nothing on the slope: the fleet's exponents are 25 to 31, the calibration is at 15; 90 finds would give +-0.10 for 2.3 more core-hours.
- **The overshoot law at 200 digits**: 0.83 +- 0.16, 1.1 sd below theta = 1; pooled with the 1,026 earlier hits it is 0.98 +- 0.03 (section 8.2), so theta = 1 stands.
- **Every find was recomputed from N alone** (`verify_g.py`, `logs/verify_g.log`): g is the reported value for all 42; all N are below 10^200 (6 have 199 digits); compositeness of every N - p with p < g is certified by a small factor or a failed Fermat base-2 test (30,224 tests, 25 s).
- **The record target is out of reach of four cores**: 83.8 s per cover (246,000 members/s per core, 4.96*10^6 Fermat tests per cover); one expected success at 160,367 costs 23,100 core-hours = 4.9*10^12 Fermat tests (e^29.2), i.e. 5,800 hours on four cores. 273 covers are 0.03% of one success and none was found. The idle cores are not a contribution to the record; the calibration is what this scan was worth.
- **The sandbox**: `nohup` processes died when the container was recycled while the session was idle (about 20:20Z); the same workers as harness-tracked background commands, resumed from their logs, ran the full 2 hours (the maximum timeout, 7,200,000 ms) through the idle period with the container up throughout, and were stopped by the harness at the limit. They were not restarted.

### 8.5 Does the calibration change the decision? The design level against the overshoot law

The 24-hour calibration measures theta (section 8.2). If theta were far from 1, would another design level than 170,000 (the Opus session's 180,000, 190,000 and 200,000 designs on their own covers, at the same work) give a higher expected final record? `design_theta.py` re-runs the Opus model (`campaign_table.py`; theta = 1 reproduces its E[record] = 175,252 at today's budget) with the design hits' suppression exp(-extra * kappa) replaced by exp(-extra * kappa / theta), the same work for every design (1.90 design hits at 170,000 as the fleet runs, times e^package, package in nats), and the g of every tested member counted (`logs/design_theta.log` has every table):

| design with the highest E[record] (margin over the next design) | theta 0.8 | 1.0 | 1.26 | 1.5 | 2.0 |
|---|---|---|---|---|---|
| work as today (package 0) | 170,000 (+1,176) | 170,000 (+2,098) | 170,000 (+3,264) | 170,000 (+4,318) | 170,000 (+6,478) |
| package +0.65 nats (the largest package of the Opus table, which lists 0, 0.35 and 0.65) | 180,000 (+395) | 170,000 (+877) | 170,000 (+2,480) | 170,000 (+3,928) | 170,000 (+6,907) |
| package +1.5 (4.5 times the work) | 180,000 (+1,306) | 180,000 (+178) | 170,000 (+1,818) | 170,000 (+3,631) | 170,000 (+7,418) |
| package +3.0 (20 times) | 190,000 (+1,174) | 190,000 (+846) | 170,000 (+1,582) | 170,000 (+3,626) | 170,000 (+7,936) |

- **At today's work the 170,000 design is the best for every theta from 0.8 to 2**, by 1,200 to 6,500 in the expected record. So the calibration changes the forecast (P(final >= 175,000) 37% to 59% and P(final >= 200,000) 0.02% to 1.5% for theta 0.8 to 1.5, section 8.2), **not the decision**.
- The best design level moves up only with more work together with a thin overshoot: 180,000 wins at theta = 0.8 from a package of +0.65 (by 395) and at theta = 1 from +1.5 (by 178); 190,000 needs +3 nats; for theta >= 1.26 the 170,000 design stays best up to +3 nats.
- **A lottery on 200,000 costs more than it gives**: at theta = 1 and today's work the 200,000 design raises P(final >= 200,000) from 0.133% to 0.42%, and lowers P(final >= 175,000) from 46% to 20% and E[record] from 175,252 to 168,739.

## 9. Files

`goldbach/gaps_map/data/bottomup/` (README there): `gmp_cal.py` (GMP calibration), `q1_cost.py`, `q1_stake.py` (Q1), `dos_gf.py`, `dos_check.py` (cover supply), `cover_rem.py`, `cover_rem170.py` (rate of the cover), `a12_numbers.py` (dual and geometry), `a3_pairs.py` (additive structure), `rec_mc.py`, `rec_rescale.py`, `rec_rescale_R.py`, `records.txt` (calibration), `ovs.c`, `ovs_test.py`, `rec_ovs.py`, `hits_1e9_1000.txt`, `fleet_ovs.py`, `fleet_hits.jsonl` (overshoot law), `block_corr.py`, `block_cov_theory.py` (selection and overshoot), `fleet_rates.py`, `fleet_sens.py` (event rates and forecast sensitivity; they need the Opus session's `campaign_table.py` and `covers/`), `scan_tally.py`, `verify_g.py`, `scan479/` (the CPU scan: ledger, logs, the 42 finds, scripts), `nearmiss_rescale.py` (the 24-hour calibration of the fleet's near-miss log), `design_theta.py` (design level against the overshoot law; needs `campaign_table.py` and `covers/` of the Opus session), `logs/`.
