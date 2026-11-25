# Seven mechanisms scored on the exact miniature

Helper session, requested by Research at 13:34 UTC on the lead's instruction: "Five with numbers beat twenty with arguments. If one gains more than a nat at equal work, stop and tell me at once." Scored here: seven mechanisms (M4 in two variants) outside the grammar L of the July closure theorem (or, for calibration, inside it), each with its number, each tested out of sample, negative results included. One of them clears a nat under the lead's accounting and does not clear it under the accounting that prices verification. That gap is the main finding. Read section 1 before the table.

All scripts and logs are under `goldbach/gaps_map/data/mechanisms/`. Nothing here has been refereed.

## 0. Setup

The miniature is Research's (`goldbach/sublinear/README.md`, "The same thing in miniature"): the members are even N < X with no prime factor in 3..29, there are 167 rows (odd primes below Q = 1000), and N is a *success* when no N − q is prime. I rebuilt it from scratch (`mini.c`: every member, its rows alive after the odd primes up to 23, 31, 43, 61, 97 and 199, and the exact success flag) and reproduced Research's cover-first and ideal numbers on A to the digit.

| miniature | X | Q | members | successes |
|---|---|---|---|---|
| A (Research's) | 1·10⁹ | 1000 | 157,947,020 | 256 |
| B (second X) | 2·10⁹ | 1000 | 315,894,246 | 826 |
| C (second Q) | 1·10⁹ | 900 | 157,947,037 | 662 |

Cover first (order by rows alive at depth 23, ties random), expected cost in members to reach k successes, with Research's interpolation convention:

| | k=1 | k=3 | k=10 | k=30 | k=100 |
|---|---|---|---|---|---|
| A | 2,982 | 63,350 | 253,380 | 1,205,425 | 12,004,497 |
| B | 3,888 | 8,058 | 204,319 | 624,238 | 2,971,037 |
| C | 3,529 | 28,851 | 77,278 | 422,635 | 2,860,330 |

(Ideal order by rows alive at depth 199, for context: A 13 / 401 / 10,811 / 73,849 / 1,720,522.)

**Gain** = ln(E_cover(k) / E_mechanism(k)), in nats, at equal work. **Noise**: with 256 successes the numbers at k = 1 and 3 are dominated by where one or two successes land. Every gain below carries a bootstrap standard deviation over resampled success sets (paired, so the baseline and the mechanism see the same resample), and I trust k ≥ 10 more than k ≤ 3. **Out of sample**: anything fitted (a model, a threshold, a prefix) is fitted on one miniature and scored on the other two; the fits never see the test successes.

## 1. Two accountings, and why they matter here

**(A) The lead's unit.** One member scored at depth 200 costs one unit (36 modular operations: the 36 odd primes 31..199; the first 9 are free from the class). Checking whether the member is a success is free. This is how Research's tables and the lead's rule are written, and it is what every number in the column "(A)" below uses.

**(V) Verification priced.** A real run must also find, for every member it does not reject by sieving, a prime row (about 2.2 modexps when each alive row is prime with probability about 0.45). One modexp is about 139 units (5,000 modular operations at 200 digits). Under (V) a member costs about 306 units to reject and the sieve is a rounding error.

Most mechanisms are unchanged by the choice. Two are not: the early-abort funnel and the neighbour search. The neighbour search needs the *exact* prime rows of its seeds, and that is exactly the quantity (A) hands over for free.

## 2. The table

Gains in nats against cover first, accounting (A). "o.o.s." = out of sample. Standard deviations are bootstrap; ± is one s.d.

| # | mechanism | in L? | k=1 | k=3 | k=10 | k=30 | k=100 | verdict |
|---|---|---|---|---|---|---|---|---|
| M1 | size of N inside the range (logit on k1, 1/ln N, k1/ln N) | outside | +0.4…+0.9 (±0.4–0.9) | −0.4…+0.4 (±0.3–0.9) | +0.2…+0.6 (±0.15–0.5) | +0.05…+0.26 (±0.14–0.2) | +0.14…+0.27 (±0.06–0.09) | small, real, vanishes at 200 digits (≈0.1) |
| M2 | any function of N mod 3..23 (Bayes-optimal shallow statistic: S₂ clumping, row weights, learned scores) | Congruence information | ≤ +0.12 | ≤ +0.13 | ≤ +0.11 | ≤ +0.08 | n/a | bounded by ≈0.1; any such statistic costs more than scoring |
| M3 | early-abort funnel (sieve deeper, abort when rows alive exceed a threshold) | schedule, not information | 0.00 | 0.00…0.02 | 0.02…0.04 | 0.05…0.14 | 0.10…0.39 | under (A) ≈0; under (V) +0.14…+0.23 (k=10), +0.23…+0.41 (k=30), +0.39…+0.95 (k=100) |
| M4a | neighbours N±h of found successes (Research's scoring, reproduced) | outside (per-instance) | −0.17…−0.10 | −0.14…−0.02 | −0.04…+0.04 | −0.02…+0.06 | 0.00…+0.02 | 2–8 success pairs per miniature; ≈0.02 extra successes per success |
| **M4b** | **neighbours of NEAR-successes, clean shifts only** | outside (per-instance) | — | 0.00 | +0.08 | +0.8…+0.9 | **+1.4…+1.65 (k=78…127)** | **clears a nat from k≈40 under (A); between −0.8 and +0.2 under (V)** |
| M5 | integers within Q of a perfect square (PolyImage degree 2; for calibration) | **in L** | −0.95 | −1.11 | −1.73 | n/a | n/a | forced rows give +0.07 for 2.8 nats of density |
| M6 | coherent block: order by "same residue t at many primes", and the block family | Congruence class; the order is outside | +0.3…+0.7 (±0.3) | −0.1…+0.4 (±0.3) | −0.05…+0.08 (±0.1) | −0.02…+0.05 | −0.01…+0.07 | null: successes' mean index 3.63 vs 3.62 |
| M7 | N/2 prime (N has no odd prime factor at all) | Congruence avoidance; the order needs a primality test | −0.23…0.00 | −0.36…+0.71 (±0.4) | −0.06…0.00 | +0.02…+0.05 | 0.00…+0.04 | rate +0.07…+0.16 nats, family costs 1.8 nats |

The sections below give the definition, the number, the transfer to 200 digits and the files for each row.

## 3. Mechanism by mechanism

### 3.1 M1. Size of N (non-residue information about N)

*Idea (the lead's first item).* Successes lean to large N because the chance that N − q is prime falls like 1/ln N. Rank members by a logit fitted on (k1, 1/ln N, k1/ln N) instead of k1 alone.

*Number.* Fitted on each miniature, scored on the other two (24 size bins per k1 level; `m1_size.py`, log `m1_size_ABC.log`). Out-of-sample gains at k = 100: +0.14 to +0.28, with bootstrap s.d. 0.06–0.09 and the same sign in all six pairs. At k = 30: +0.05 to +0.29 (s.d. 0.14–0.2). At k = 10: +0.17 to +0.57 (s.d. 0.15–0.5). At k = 1 and 3 the point values range from −0.4 to +0.95 and the s.d. is 0.3–0.9, so there is nothing to read there.

*At 200 digits.* The tilt is a function of ln N, which varies by about 10 % across the miniature's range and by 0.5 % across the top decade at 200 digits. With about 33 nats of exponent the best case is 33 × 0.005 ≈ 0.17 nats for taking only the top of the range, and about 0.1 for the natural distribution. So: real in the miniature, ≈0.1 nats at the target.

*Cost.* None: N is known.

### 3.2 M2. The best possible statistic of the shallow cover (orderings "learned from the exact data")

*Idea (the lead's third item).* Fit any cheap statistic to the successes and test it out of sample. Rather than try statistics one by one, I computed the *ceiling*: the Bayes-optimal statistic of N mod 3..23. For each member in the best cover levels (k1 ≤ 34: 33.2M members on A, 66.4M on B), with R the set of rows alive after the primes up to 23, I estimated by Monte Carlo (256 samples)

L(R) = ln E_c [ (1−ρ)^{k(R,c)} ],

where c is a uniformly random residue vector at the primes 29..199, k(R,c) is the number of rows still alive at depth 199 and (1−ρ) = 0.5 is the calibrated per-row chance of being composite. L is the best estimate of ln P(success) that can be made from the shallow class under the independence hypothesis H1, so *any* function of N mod 3..23 (pair clumping S₂, learned row weights, quadratic or higher characters of N at those primes, anything fitted to the 256 successes) is dominated by ordering on L. The model itself passes its own test: the calibrated success mass per k1 level matches the observed count within noise (predicted / observed at k1 = 28, 30, 32, 34, 36: 7.2/10, 19.9/19, 31.4/30, 32.5/34, 22.4/21).

*Number.* Within a k1 level L has a standard deviation of 0.20–0.24 nats (this includes Monte Carlo noise, not separately measured), so ordering by L inside levels can only buy a fraction of that. Gains over cover first:

| | k=1 | k=3 | k=10 | k=30 |
|---|---|---|---|---|
| A, observed successes (lower bound: the Monte Carlo noise only hurts) | +1.04 ± 0.40 | +0.79 ± 0.55 | −0.01 ± 0.17 | −0.03 ± 0.09 |
| B, observed successes (o.o.s.; the model is not refit) | +0.23 ± 0.32 | +0.13 ± 0.31 | +0.16 ± 0.21 | +0.00 ± 0.09 |
| model-predicted gain, A / B (an upper estimate: it includes the winner's curse of the Monte Carlo noise) | +0.12 / +0.12 | +0.12 / +0.13 | +0.07 / +0.11 | +0.08 / +0.08 |

The A values at k = 1 and 3 are two successes landing in good bins. B, with three times as many successes and the same model, gives +0.23 and +0.13.

*Conclusion.* Everything computable from the residues mod 3..23 is worth at most about 0.1 nats beyond k1. That includes the "pair clumping", "row weights" and "characters" ideas, which are functions of those residues. *Cost*: the statistic needs the alive set and a pass over the primes 29..199; scoring the member exactly at those primes costs one operation per prime, so any predictor that costs more than about one unit is dominated by simply scoring. A statistic that costs 100 units to gain 0.1 nats loses 4.5 nats at equal work.

*Files.* `bayes.c`, `bayes_an.py`, logs `bayes_bound_A.log`, `bayes_bound_B.log`.

### 3.3 M3. Early-abort funnel (the sieve schedule)

*Idea.* Score a member in stages at depths 31, 43, 61, 97 and 199 and abort as soon as the rows alive exceed a threshold, so most members cost a fraction of a unit. This is the mechanism that could most easily fake a gain, so it is scored on its own. It adds no information: the baseline could do it too.

*Number, accounting (A)* (cost per stage = the primes in that stage / 36; thresholds fitted by coordinate descent on A for the objective Σ ln E(k), k = 10, 30, 100; fit `funnel_fit_A.log`): thresholds on rows alive (30, 27, 25, 23) at depths (31, 43, 61, 97). The funnel costs 0.137 units per member on average and keeps 103 of 225 successes.

| | k=1 | k=3 | k=10 | k=30 | k=100 |
|---|---|---|---|---|---|
| A (in-sample) | 0.00 | +0.02 | +0.04 | +0.14 | +0.39 |
| B (o.o.s.) | 0.00 | 0.00 | +0.02 | +0.05 | +0.10 |
| C (o.o.s.; thresholds scaled by 153/167) | 0.00 | +0.02 | +0.03 | +0.08 | +0.21 |

The savings are real where the stream is long (k = 100) and absent where successes live: the best-cover members, where almost every member passes every threshold. Under (A) the funnel is worth ≤ 0.1 nats at k ≤ 30.

*Number, accounting (V)* (a member that survives the thresholds costs 306 units to verify, the baseline verifies every member; thresholds refit on A for the same objective: rows alive ≤ (30, 27, 25, 23, 19) at depths (31, 43, 61, 97, 199); mean cost 20.8 units per member against 306, and it keeps 102 of 225 successes; `funnel_b.py`, `funnel_b_eval.py`):

| | k=1 | k=3 | k=10 | k=30 | k=100 |
|---|---|---|---|---|---|
| A (in-sample) | +0.03 | +0.13 | +0.22 | +0.41 | +0.95 |
| B (o.o.s.) | +0.03 | +0.04 | +0.14 | +0.23 | +0.39 |
| C (o.o.s.; thresholds (27, 25, 23, 21, 17)) | +0.07 | +0.17 | +0.23 | +0.39 | +0.66 |

So "sieve before you verify" is worth 0.1–0.4 nats at k = 10–30 and 0.4–0.95 at k = 100 once verification is priced. It is not a mechanism (any real run does it), but it is the baseline a mechanism should be compared with under (V), and it is larger than every gain in the table except M4b's (A) number.

### 3.4 M4a. Neighbours of found successes (Research's scoring, reproduced)

*Idea.* If N is a success, N + h inherits the rows q' with q' − h prime (the same integers N − q), so N + h starts with part of its cover paid. Scan the allowed neighbours of every success found.

*Number.* On A, 2 pairs of successes lie within |h| ≤ 1000 (independence predicts 0.065), on B 8 pairs among 826 and on C 8 among 662. Each success costs about 315 neighbour scans (284 on C) and yields about 0.01–0.02 extra successes. Gain of the whole policy over cover first, k = 1/3/10/30/100: A −0.15/−0.02/+0.04/+0.06/+0.02, B −0.10/−0.14/−0.02/+0.01/+0.01, C −0.17/−0.03/−0.04/−0.02/0.00. Restricting to the 30 shifts with most inherited rows (30 scans per success) removes the loss at k ≤ 3 and leaves ≤ +0.07. This confirms Research's 0.02: *success* seeds are far too rare to matter.

### 3.5 M4b. Neighbours of near-successes with clean shifts — the one that clears a nat under (A)

*Idea (the lead's "turn the inheritance structure into a search").* A seed does not need to be a success. It needs only that the rows its neighbour inherits are composite. A stream member with j ≤ J prime rows (with J = 5, 6.7 % of the stream members are seeds on A) passes its composite rows to N + s for every shift s whose inherited rows avoid the seed's prime rows. Shift s is *usable* if at least c_min of the rows of N + s are rows of N (q' prime and q' − s prime); on A the best shifts share 97 of 167 rows and 126 shifts share at least 50. A shift is *clean* for a seed if no prime row q₀ of the seed lands on a prime row q₀ + s of N + s. Then every inherited row of the neighbour is composite for free and only the fresh rows are left to chance.

*Procedure scored.* Stream = cover-first prefix k1 ≤ kmax. Seeds = stream members with ≤ J prime rows (exact, from the table: verification is free in (A)). For each seed, every clean usable shift with |s| ≤ 1000; skip neighbours already in the stream (they are scored there); score each distinct neighbour once (one unit each). Cost = stream members + distinct neighbour scans. Compare with the cover-first cost of the same number of distinct successes.

*A, J ≤ 5, c_min = 50* (`nbr4.c`, `nbr4_drive.py`; all 80 neighbour successes at kmax = 30 were checked against the exact success list: 80 distinct, all in the 256, all with k1 = 31…38, i.e. members cover first reaches only later):

| stream prefix | stream members | neighbour scans | units | successes (stream + neighbours) | cover-first units for that many | gain |
|---|---|---|---|---|---|---|
| k1 ≤ 26 | 24,590 | 39,000 | 63,590 | 2 + 1 = 3 | 63,350 | 0.00 |
| k1 ≤ 27 | 102,109 | 131,289 | 233,398 | 4 + 6 = 10 | 253,380 | +0.08 |
| k1 ≤ 28 | 354,228 | 367,615 | 721,843 | 14 + 24 = 38 | 1,867,799 | +0.95 |
| k1 ≤ 29 | 1,039,832 | 864,039 | 1,903,871 | 28 + 50 = 78 | 7,779,758 | +1.41 |
| k1 ≤ 30 | 2,612,970 | 1,700,423 | 4,313,393 | 47 + 80 = 127 | 18,349,530 | **+1.45** |
| k1 ≤ 31 | 5,742,016 | 2,862,569 | 8,604,585 | 67 + 95 = 162 | 30,518,531 | +1.27 |
| k1 ≤ 32 | 11,299,493 | 4,182,383 | 15,481,876 | 97 + 95 = 192 | 44,349,824 | +1.05 |

*Out of sample* (J ≤ 5 and the shared-row threshold fixed from A, scaled to 46 for C; the prefix is the only free choice): B +0.90 (119 successes), +1.43 (257), +1.56 (425), +1.37 (545); C +0.70 (35), +1.12 (100), +1.16 (200), +1.36 (334), +1.25 (458). So the gain is about zero at k ≤ 10, about +0.8 at k = 30 and +1.1…+1.6 for k ≥ 80.

*Does it decay as Q grows?* Same recipe on X = 2·10⁹ with Q = 700, 800, 900, 1100 (successes 21,820 / 6,885 / 2,190 / 208; `qscale.py`, `qscale_Q700-1100.log`; Q = 1200 did not run because `mini.c` is built for 192 rows):

| Q | rows | prefix 1 (k) | gain | prefix 2 (k) | gain |
|---|---|---|---|---|---|
| 700 | 124 | 13,847 | +0.99 | 17,128 | +0.82 |
| 800 | 138 | 3,724 | +1.23 | 6,229 | +1.08 |
| 900 | 153 | 1,130 | +1.41 | 1,535 | +1.30 |
| 1000 (B) | 167 | 257 | +1.43 | 425 | +1.56 |
| 1100 | 183 | 86 | +1.52 | 161 | +1.26 |

No decay over a 1.5-fold increase in λ (here the negative log of the population success rate, which rises from 9.6 at Q = 700 to 14.3 at Q = 1100).

*Why it is not a result yet.*

1. **Accounting (V) removes it.** To know that a stream member has at most J prime rows, you must test its alive rows until J + 1 primes turn up: about (J + 1)/0.5 modexps for a member that is not a seed (8, 12, 16 for J = 3, 5, 7), against 2.2 for plain rejection. (A) charges nothing for this, because the miniature's prime table is free. Pricing it (stream members × (J + 1)/0.5 + neighbour scans × 2.2, against cover first × 2.2) turns the 15 cells I ran (prefix k1 ≤ 28, 30, 32; J ≤ 3, 5, 7; c_min = 50, 70) from +0.45…+1.65 under (A) into **−0.82…+0.23 under (V)**. The quoted cell (kmax = 30, J ≤ 5, c_min = 50) is +1.45 under (A) and +0.14 under (V); the best (V) cell (kmax = 30, J ≤ 7, c_min = 50) is +1.50 and +0.23; at k = 30 (kmax = 28, J ≤ 7, c_min = 70: 30 successes for 485,807 units against 1,205,425) it is +0.91 under (A) and −0.81 under (V). What (A) measures is the value of *exact primality knowledge about the rows of the stream*, not the value of a method that gets it for less than the work it saves.
2. **Not shown to scale to 200 digits.** With λ the mean number of prime rows in a best-cover member and f the fraction of rows a neighbour shares, a back-of-envelope yield ratio is R ≈ (λ^J / J!) · m_clean · e^(−λ(1−f)). At λ ≈ 33 and f ≈ 0.45 (the best a shift can do at Q = 10⁵) and J = 5 this is well below 1, and J = 10 needs eleven primes' worth of verification per stream member. The miniature sweep above does not show the decay this predicts over its range, and it cannot reach λ = 33. This is an open question, not a result either way.
3. **In-sample selection.** On A, about 30 cells (prefix × J × threshold) were run before choosing the one quoted; the B and C numbers and the sweep are out of sample in J and c_min, not in the idea.

*What it does say.* Exact knowledge of which integers near N are prime is worth about 1.4 nats at k ≈ 100 on these miniatures; nothing in residues does. The miniature's free verification therefore *overstates* any mechanism that spends it, and the right comparison for such mechanisms is against a baseline that also owns that knowledge (sieve everything, verify only the best), not against cover first with free verification.

### 3.6 M5. The neighbourhood of perfect squares (calibration of the closure theorem's accounting; inside L)

*Idea.* Take N = m² + c with c < Q (or (m+1)² − c): then N − q = (m − a)(m + a) whenever q − c = a², a composite for free whatever the small primes do. Value set: N within Q of a square.

*Number* (`fam_gen.py`, `evalN.c`, `sq_family.py`; 9,828,167 members on A, density 6.2 %):
- forced rows: 0.22 per member alive at depth 23, 0.095 alive at depth 199 (a forced row is a product of two numbers near √N, and both must avoid every prime up to 199 for it to be alive: most are struck anyway);
- the k1-matched rate ratio: 1.014 without credit for the forced rows, 1.088 with it, i.e. forcing gains 0.07 nats and membership 0.01;
- cover first inside the family against cover first on everything (predicted success mass, calibrated): −0.95 / −1.11 / −1.73 nats at k = 1 / 3 / 10 (not enough successes in the family for k ≥ 30);
- cost: 2.78 nats of density for 0.095 kills = **29 nats per kill**, against about 1 nat per kill for covering and 3.1–4.2 for the closure theorem's near-miss ExpFamily.

*At 200 digits.* The density cost becomes ln(√N/Q) ≈ 220 nats for the same ≤ 0.1 of a kill per member. This reproduces the theorem's balanced-representation accounting with a measured constant.

### 3.7 M6. The common-integer block turned into an order (the lead's fourth item)

*Idea.* The block uses one small integer t for every prime in the block (N ≡ t mod p for all p ∈ B, t ∈ (Q, 2Q]), so that the rows struck are those q with p | t − q and nothing overlaps. Two readings:

1. *An order by coherence.* For each member, the largest number of primes in 31..199 that divide N − t for a common t ∈ (Q, 2Q]. `evalN.c` computes it. The distribution is nearly identical for successes and for members matched on k1: mean coherence index **3.628 vs 3.621 (A), 3.628 vs 3.620 (B), 3.600 vs 3.581 (C)**. Ordering by (k1, coherence): A +0.31 / −0.13 / +0.08 / −0.02 / 0.00 at k = 1 / 3 / 10 / 30 / 100, B +0.66 / +0.44 / 0.00 / +0.01 / −0.01, C +0.48 / −0.05 / −0.05 / +0.05 / +0.07 (bootstrap s.d. 0.3 at k = 1 and 3, ≤ 0.1 at k ≥ 10). Null at every k ≥ 10.
2. *A restricted family.* Members with N mod ∏B ∈ (Q, 2Q] for B = {31, 37, 41}, {31, 37, 41, 43}, {31, 37, 41, 43, 47}: density 2.1 %, 0.05 %, 0.0017 % (cost 3.85, 7.6, 11.4 nats); rate ratio at equal k1 +0.013, +0.045, −0.045 nats. On B and C the three-prime family gives +0.003 and +0.012. (A shows 11 successes in the family against 5.5 predicted, B 22 against 17.6, C 22 against 12.8; B contains A, and its half N > 10⁹ shows 11 against 12.1, so I read the excess on A as chance: Poisson p ≈ 0.03 among about ten comparisons.)

*Why.* A coherent class does strike more rows than independent classes: if all 36 primes 31..199 could share one t the alive fraction of rows would be 0.59 against 0.66 (about 10 % fewer alive rows, worth about a nat on paper). A random member, however, shares t at only 3–5 primes (index mean 3.6) and the successes are not different; pinning more than that costs the CRT overhead (about 10⁷² vectors per member at depth 200 in Research's table). At the shared-prime counts the miniature offers, the saving is below the noise. Its advantage is asymptotic (Rankin's trick) and is not visible at this size.

### 3.8 M7. N/2 prime (a non-residue, per-member fact)

*Idea.* N = 2r with r prime means N is divisible by no odd prime, which avoids the zero class at every deeper prime (the worst class: it kills one row). That is information about N beyond the residues the order uses.

*Number* (`half_prime.py`): density among allowed members 16.1–16.7 %; the number of successes with N/2 prime against the expected number at the same k1 mix: A 48 vs 42.7, B 142 vs 133.0, C 130 vs 110.5, i.e. a rate gain of +0.12, +0.07, +0.16 nats. Ordering within k1 by "N/2 prime first": −0.11…+0.05 at k ≥ 10 (A −0.03 / +0.05 / +0.01 at k = 10 / 30 / 100; B 0.00 / +0.02 / +0.04; C −0.06 / +0.03 / 0.00). Restricting to the family costs ln(1/0.167) = 1.8 nats and yields worse cover-first costs than the full set (A at k = 10: 435,939 against 253,380). Small and requires a primality test per member.

## 4. Considered, not scored (and why)

- **Quadratic or higher characters of N (the lead's first item).** At primes ≤ 23 they are functions of the residues M2 already bounds. At larger primes they are residues the order cannot pin (CRT line). Characters of N − q at large moduli carry no information about primality beyond divisibility.
- **Fluctuations of the local prime density (explicit-formula terms).** Relative size N^(−1/2) times a (ln T)² sum over zeros up to height N/Q: of order 10⁻⁴ at 10⁹ (rough estimate) and smaller at 200 digits, and not computable without the zeros.
- **Linear recurrences and Lucas sequences.** A family with V members costs ln(X/V) nats of density, and the miniature has about ln X ≈ 20 terms. The closure theorem's accounting (3.1–4.2 nats per kill) applies, and M5 is the measured version of it for a denser family.
- **Cubes, x³ + y³, higher-degree polynomial families.** Outside L's degree bounds, but the density cost grows and the forced rows are products of balanced factors, as in M5.
- **Partial verification by sampling rows.** That is the verification schedule discussed under (V), not a new source of information.
- **Algorithms on the same miniature (lattice decoding with lists, meet in the middle, generalised birthday, hashing).** Lean is running these; not duplicated.

## 5. What this says about "prove nothing better exists, or find it"

1. **Anything computed from the residues of N at the small primes** is bounded by about 0.1 nats beyond cover first (M2), with a measured ceiling and an out-of-sample check. The "learned ordering" family is closed on the miniature.
2. **Non-residue facts about N** (size, N/2 prime, algebraic neighbourhoods, coherence) gave +0.1…+0.3 (size, vanishing at scale), +0.1 (N/2 prime, at 1.8 nats of density), 0 (coherence) and −1…−2 (squares). None approaches a nat.
3. **Schedules** (early abort) give ≤ 0.1 nats at k ≤ 30 under (A) and 0.1–0.4 under (V), 0.4–0.95 at k = 100 (§3.3). Under (V) this is the baseline to beat, and against it M4b's (V) numbers are lower still.
4. **The only thing that moved a number past a nat is exact primality knowledge of nearby integers** (M4b), worth about 1.4 nats at k ≈ 100 when the knowledge is free and between −0.8 and +0.2 when it is paid for. The miniature's free verification is the reason the lead's accounting rewards it. Before the lead builds on any mechanism that consults the table of primes near N, the comparison should be redone under (V), against a baseline that sieves deeper before it verifies.
5. **No mechanism here tests the claim at 200 digits.** The sweep to λ ≈ 14 shows no decay for M4b; the back-of-envelope scaling says there should be one. That is the open question the miniature cannot close.

## 6. Not tested

- (V) accounting for M1, M2, M6, M7 (their gains are ≤ 0.3 in (A) and the verification cost does not help them).
- Scale: Q ≥ 1200 (the miniature code is built for 192 rows), X > 2·10⁹, and any λ above 15.
- Seeds identified by sampling rather than full verification (a cheaper identification that keeps most of the gain would change §3.5).
- M4b with stream orders other than cover first, with shifts beyond |s| ≤ 1000, or with the stream chosen to *maximise* seeds.
- A success-mass model to extrapolate M4b to Q = 1500 (X = 2·10⁹): fitted at Q = 1000 it underpredicts the stream's successes there by about 8× (0.6 predicted, 5 observed at kmax = 48), so I dropped it (`nbr5.c`, `scale_drive.py` are kept for the record; nothing quoted depends on them).
- Combination of the funnel and M4b (the funnel changes which stream members are scored; the seeds need exact rows, so they do not combine for free).

## 7. Files

`goldbach/gaps_map/data/mechanisms/`: `README.md` (how to rerun), C programs `mini.c` (the miniature), `evalN.c` (member lists: coherence index, forced rows), `bayes.c` (Bayes-optimal shallow statistic), `nbr2.c`, `nbr3.c`, `nbr4.c`, `nbr5.c` (neighbour search variants; `nbr4.c` is the deduplicated one quoted), Python `lib.py`, `ev.py` (evaluation and bootstrap), `m1_size.py`, `bayes_an.py`, `funnel.py`, `funnel_eval.py`, `funnel_b.py`, `nbr.py`, `nbr3_drive.py`, `nbr4_drive.py`, `qscale.py`, `scale_drive.py`, `fam.py`, `fam_gen.py`, `fam_blk.py`, `fam_blk2.py`, `sq_family.py`, `coh_run.py`, `half_prime.py`, `make_logs.sh`, and `logs/` with every output quoted above.

The per-member data (several GB) is not committed; `mini.c` regenerates it in about 15 s for A.
