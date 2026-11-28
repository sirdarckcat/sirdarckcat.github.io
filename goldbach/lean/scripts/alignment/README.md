# Exact small cases of the alignment problem

The bottom-up round of 25 November 2026: the research session asked for the smallest instances, enumerated
completely. This directory holds the pieces as they come.

## 1. Where the prize sits in the miniature (`anatomy1.py`, `anatomy2.py`)

Miniature: X = 10^9, target 1,000 (167 rows), line at 23, depth 200; 157,947,020 members (the member file of
`../pprime_families/truth.c`); k1 = rows left at depth 23, a function of the class vector modulo 3..23 (the cover);
k2 = rows left at depth 200. Over all members k1 = 36.80 ± 2.86 (least 22) and k2 = 23.34 ± 3.14 (least 6). A cover
has 4.33 members (its window).

**The best members have a good cover, not the best, and the rest is position.** For the tier "k2 at most t" the
rarity ln(members / tier) splits into the information of k1 (cover nats) and the rest (luck nats):

| tier | members | rarity | cover nats | luck nats | k1 in the tier: 10% / median / 90% | cover-first quantile of the median member | share of the tier in the best 1% / 0.1% of covers |
|---|---|---|---|---|---|---|---|
| k2 ≤ 8 | 62 | 14.75 | 3.95 | 10.80 | 26 / 29 / 32 | 0.44% | 0.75 / 0.36 |
| k2 ≤ 9 | 401 | 12.88 | 3.29 | 9.59 | 27 / 29 / 32 | 0.44% | 0.60 / 0.25 |
| k2 ≤ 10 | 1,965 | 11.29 | 2.78 | 8.52 | 27 / 30 / 33 | 1.16% | 0.51 / 0.18 |
| k2 ≤ 12 | 33,598 | 8.46 | 2.13 | 6.33 | 28 / 31 / 34 | 2.64% | 0.37 / 0.11 |

Of the 1,965 best, one has a cover with 22 rows (the least there is; 14 members have one) and 18 have at most 24
(888 members). Every one of them but one is the best member of its own window, and its window siblings are
ordinary: k2 = 19.08 on average, where a member with their k1 is expected to have 18.98. So a quarter of the rarity
is the cover (a cover in the best one percent or so) and three quarters is the member's own position, which its cover
does not share with its other members.

**The position is not luck at a few primes: it is the same small tilt at every prime beyond the line.** For each
prime s from 29 to 199 in turn, let R be the rows still left and g_s the number of them in the class of N; given R,
the law of g_s for an unselected member is read off the class counts of R modulo s. For the tier k2 ≤ 10
(`anatomy2_k10.txt`):

| s | rows left before s | expected gain | mean gain in the tier | tilt θ_s | information, nats | cumulative share |
|---|---|---|---|---|---|---|
| 29 | 29.9 | 1.03 | 1.65 | 0.90 | 0.28 | 0.04 |
| 31 | 28.3 | 0.91 | 1.58 | 0.93 | 0.32 | 0.08 |
| 61 | 20.6 | 0.34 | 0.69 | 1.04 | 0.20 | 0.32 |
| 89 | 16.8 | 0.19 | 0.51 | 1.27 | 0.23 | 0.51 |
| 149 | 12.6 | 0.08 | 0.25 | 1.30 | 0.13 | 0.77 |
| 199 | 10.0 | 0.05 | 0.20 | 1.56 | 0.14 | 1.00 |

The tilt θ_s is the exponent that turns the unselected law of g_s into the tier's (one parameter per prime, maximum
likelihood): about one nat per row at every prime, rising slowly from 0.9 to 1.6 as the rows get fewer (the rise is
an effect of taking the primes in order: with the other primes held fixed the tilt is the same at every prime,
section 5). Each of the
37 primes carries 0.13 to 0.32 nats; their sum is 7.28 nats of the 8.52 of luck; half is reached only at 89, the
fifteenth of them; the first carries 4%, the first three 12%. A tier member gains above expectation at 15.8 of the 37
primes (9.1 for a member with the same cover), and its three luckiest primes give 4.7 of its 11.2 excess rows. The
tiers k2 ≤ 12 and k2 ≤ 8 show the same (`anatomy2_k12.txt`, `anatomy2_k8.txt`: half at 89 and at 97).

**None of it is visible in the classes themselves.** The class of N modulo a prime beyond the line, taken by itself,
carries 0.01 to 0.08 nats about membership of the tier: 1.40 nats for all 37 primes together (0.87 for the larger
tier, where the estimate is cleaner), against 8.52 of luck. What distinguishes the tier is where its classes fall
relative to its own cover:

| | incidences of the later classes with all rows | with the rows its cover left | distinct rows struck | repeats |
|---|---|---|---|---|
| tier k2 ≤ 10 | 80.8 | 23.8 | 20.2 | 3.6 |
| members with the same k1 | 75.4 | 13.5 | 11.0 | 2.6 |

Seven percent more incidences in all, seventy-six percent more on the rows that were still left.

So the answer to "ordinary cover and extraordinary position, or a slightly worse cover and luck at a few later
primes": neither. A cover in the best percent, and a member that is the tail of a sum of 37 small independent gains,
each prime contributing about a fifth of a nat. A family that fixes or lists the classes of j primes beyond the line
sees at most the information those j primes carry, about 0.2 to 0.3 nats each even when the lists may depend on the
cover, and a few hundredths when they may not; it cannot hold the tier at a density better than that allows. The only
family that holds it at measurable density is "the best few percent of the covers, every member scored".

## 2. Small instances, enumerated completely (`tiny.c`, `grid.py`, `smallest.py`, `optima.py`)

An instance: rows = the odd primes below Q; moduli = the first k odd primes; candidates = every even N below X.
score_j(N) = rows q with N − q divisible by none of the first j moduli. The line is the largest l with
2·p_1···p_l ≤ X; a cell is a class modulo M = 2·p_1···p_l (a vector of classes of the first l moduli; every vector
occurs below X), its design value is score_l, and its X/M members are its window. For each depth j beyond the line:

- **OPT**: the least score_j over all candidates (the true optimum);
- **D**: the least score_j over all class vectors of the first j moduli, no bound on N (what a cover on j primes
  would do if X allowed it);
- **scan**: the least score_j over the members of the best cells (pinning, then a full scan of the windows);
- **mean**: the mean score_j over those members (pinning, no choice inside the window).

**The grid** (`grid.txt`: Q = 200, 300, 500, 1000; line after 11, 13, 17, 19 or 23; windows 2, 4, 8 and the largest
possible; 76 instances), by the number of primes beyond the line:

| primes beyond the line | scan = OPT in | mean of scan − OPT, rows | largest | mean of (mean − scan) | mean of OPT − D |
|---|---|---|---|---|---|
| 1 | 66 of 76 | 0.13 | 1 | 1.25 | 0.41 (64 instances) |
| 2 | 46 | 0.45 | 3 | 1.66 | 1.59 (32 instances) |
| 3 | 39 | 0.67 | 3 | 1.89 | not enumerated |
| 4 | 30 | 0.88 | 3 | 2.04 | not enumerated |

For the 19 instances with Q = 1000 alone: scan − OPT = 0.32, 0.89, 1.16, 1.63 rows. So the window scan is worth one to
two rows over pinning alone and that grows slowly; what the scan of the best cells still misses grows by about a
quarter to a half of a row for each further prime; and already one prime beyond the line a cover on the same primes
with no bound on N would do 0.4 rows better than anything below X.

**The miniature to full depth** (`miniature_full.txt`: Q = 1000, X = 10^9, line after 23, all 5·10^8 even N; the best
cells have 22 rows left and 15 members):

| primes beyond the line (depth) | OPT | scan of the best cells | mean | design value of the best cell holding an optimum | cells at least that good |
|---|---|---|---|---|---|
| 1 (29) | 20 | 20 | 21.4 | 22 | 3 |
| 2 (31) | 18 | 19 | 21.1 | 24 | 205 |
| 4 (41) | 16 | 18 | 19.9 | 23 | 32 |
| 6 (47) | 14 | 16 | 19.0 | 24 | 205 |
| 9 (61) | 13 | 16 | 18.1 | 27 | 23,751 |
| 12 (73) | 11 | 15 | 17.4 | 26 | 5,708 |
| 17 (101) | 10 | 14 | 16.4 | 26 | 5,708 |
| 20 (109) | 9 | 14 | 16.1 | 33 | 5,003,554 |
| 23 (131) | 8 | 13 | 15.8 | 28 | 82,812 |
| 28 (157) | 7 | 13 | 15.3 | 27 | 23,751 |
| 37 (199) | 6 | 10 | 14.6 | 26 | 5,708 |

The gap between the scan of the best cells and the optimum is 0, 1, 0, 2 rows for the first four primes, 2 to 4 from
the fifth to the nineteenth and 4 to 6 after; the optimum's own cell is 0 to 6 rows worse than the best, which puts
it between the 3rd and the 83,000th cell of 36.5 million in cover-first order (once, at the twentieth prime, where
the optimum is a single number, 11 rows worse: the 5 millionth cell).

**The smallest instance** in which pinning cannot reach the optimum (`smallest.py`, `smallest_instance.txt`; searched
with candidates above the rows, X at least 5Q, every pinnable set allowed, a set being pinnable when twice its
product is at most X and maximal when no further modulus fits): rows the 36 odd primes below 160, moduli
3, 5, 7, 11, 13, X = 840 (the least X is 800). The optimum is 6 rows left, at N = 578 only (classes 2, 3, 4, 6, 6;
rows left 7, 31, 37, 79, 139, 157). The seven maximal pinnable sets:

| pinned set | window | design value | full scores of the members of its best cells | design value of the cell of 578 |
|---|---|---|---|---|
| 3, 5, 7 | 4.0 | 9 | 7, 7, 7, 8, 8, 9 | 10 |
| 3, 5, 11 | 2.5 | 10 | 7 ×5, 9, 9, 10 | 11 |
| 3, 5, 13 | 2.2 | 10 | 7, 8, 9, 9 | 11 |
| 3, 7, 11 | 1.8 | 12 | 7, 7, 8 ×7, 9 ×5, 10 ×3, 11, 11 | 13 |
| 3, 7, 13 | 1.5 | 12 | 7, 7, 11, 12 | 13 |
| 5, 7, 11 | 1.1 | 17 | 11, 15 | 18 |
| 11, 13 | 2.9 | 27 | 8, 10, 17 | 28 |

In every design the optimum's cell is exactly one row short of the best, and it is the best number below X. This is
in the kernel (`Cap.Example840`: `optimum`, `pinning_misses`, `optimum_second_best`, `pinnable_iff`). For Q = 100 to
200 in steps of 20 and the moduli 3..13, Q = 160 is the only target with such an instance below 2,310.

**What the best members share** (`optima_k10.txt`, the 1,965 best members of the miniature).
The classes of the smallest primes, and less and less of them: 95% are in the best class of 3 (half would be by
chance), 73% in the best class of 5 (a quarter), then 30% in one class of 7 (a sixth), 21% at 11, 17% at 13, 12% at
17, 13% at 19, 9% at 23 and 6.5% at 29, each about twice the uniform share, the favoured class being the best or
nearly the best of its prime. Nothing beyond that: two best members share a class at 0.497 of the 37 later primes on
average (0.451 for uniform classes), the number of later primes shared follows the law of independent primes, and
the classes modulo 29 and 31 as points of the 29 × 31 grid are independent (χ² = 759 on 810 degrees of freedom). The
rows still left are not particular rows: the rows outside the favoured classes of 3 and 5, each left in about 15% of
the best members. One pattern is real and known: eight pairs of best members lie within 90 of each other
(differences 24, 30, 30, 30, 60, 60, 60, 90) where 0.4 is expected, the inheritance between neighbours at a multiple
of 30 that the research session has already priced.

**More strikes, or fewer repeated strikes?** (`repeats.py`, `repeats_small.py`; asked by the research session.)
For a member let L be the rows its cover left, K_s the number of them in its class modulo the later prime s, I the sum
of the K_s (strikes), U the distinct rows struck, I − U the repeats. If the K_s strikes of each prime fell on a random
K_s-subset of the L rows, independently for different primes, U would be U0 = L(1 − ∏(1 − K_s/L)) on average. For
ordinary members this is exact (U − U0 = 0.00 to 0.01 rows in every control set). For the best members of the miniature:

| tier | rows left by the cover | strikes I (same cover: ) | distinct U | repeats | repeats expected by chance for these strikes | advantage in rows = more strikes + fewer repeats |
|---|---|---|---|---|---|---|
| the optimum (k2 = 6) | 26 | 21 (11.7) | 20 | 1 | 6.3 | 10.5 = 5.2 + 5.3 |
| k2 ≤ 8 (62) | 28.8 | 24.8 (13.1) | 21.0 | 3.8 | 8.0 | 10.4 = 6.3 + 4.1 |
| k2 ≤ 10 (1,965) | 29.9 | 23.8 (13.5) | 20.2 | 3.6 | 7.1 | 9.2 = 5.7 + 3.5 |
| k2 ≤ 12 (33,598) | 30.8 | 22.6 (13.9) | 19.1 | 3.5 | 6.4 | 7.8 = 5.0 + 2.9 |

Both, and the second is not small: the best members have nearly twice the strikes of a member with the same cover, and
half the repeats that chance would give for that many strikes; fewer repeats is 36 to 50% of their advantage. In the
small instances (27 of them, true optima against candidates with the same design value) the share is 19% at four
primes beyond the line and 39% at eight, and the optimum often has no repeat at all (19 strikes on 19 rows for target
1,000 with the line after 11). The later primes of an optimum avoid each other's rows.

## 3. Statements (`GoldbachGaps/Cap/SoftLists.lean`, `GoldbachGaps/Cap/PairVariance.lean`)

- **Lists below a bound.** The number of N < X in a product of lists is at most
  (∏_{r∈S′} |A_r|)·(X/∏_{r∈S′} r + 1) for every subfamily S′ of the moduli (`card_residues_in_le_sub`), so the least
  over subfamilies. A modulus r ≥ X caps it at |A_r| alone (`card_residues_in_le_of_le`), and any ℓ numbers lie in
  lists of ℓ classes (`exists_lists_holding`): when every listed prime exceeds the window, the most a product of lists
  can hold is exactly the length of its shortest list, however many primes are listed.
- **Families and information** (`binary_kl_le`, `family_rarity_le`, `family_enrichment_le`,
  `exp_neg_kl_le_of_holds_all`). If p is the law of the best members and q the law of all members on whatever a family
  may read, then for a family F the two-point divergence between p(F) and q(F) is at most KL(p‖q); hence
  p(F)·ln(1/q(F)) ≤ KL(p‖q) + ln 2; a family holding the share c of the best members is at most
  exp((KL + ln 2)/c) times denser in them than the population; and a family holding all of them at most exp(KL)
  times. With section 1: to hold half of
  the 1,965 best members at an enrichment of e^8.5 a family must read at least 3.9 nats, which is 13 to 20 of the 37
  later primes when its lists may depend on the cover, and is not available at all from the classes alone (1.4 nats in
  the 37 primes together).
- **Two and three primes beyond the line.** There is no formula better than the enumeration: inside a cell the class
  vectors available at the later primes are the w points N0 + kM (k < w) of a line in the product of the residue
  rings, direction (M mod s_1, M mod s_2, …), and the best of them is what the tables above list. The exact statements
  are the two bounds OPT ≥ D (a cover on the same primes with no bound on N) and OPT ≤ scan, and the grid shows both
  strict from the first prime on.

## 4. The same anatomy on a real cover at 200 digits (`sieve_profile.c`, `profile_analysis.py`)

The first cover of `q200000_m89.txt` (1,502 rows; its members are 200-digit numbers), 240,000 members N0 + kM sieved
by every prime up to 10^8 (`../selection_check/members.py` writes the residues), recording for each member the rows
newly struck in nine ranges of primes. Rows left at 10^8: 505.62 on average, variance 325.27 (the formula of
`../selection_check` gives 324.5). The tier is the best 1.1% (rows left ≤ 464; 4.50 nats) or the best 0.1%
(≤ 450; 6.87 nats).

The rows a range strikes depend on how many were left before it, so the quantity that separates is the innovation:
the gain of the range minus the share of the rows left that the range strikes on average. The nine innovations are
uncorrelated (largest correlation 0.005), and their informations (mean² / (2 variance)) add up to
(mean excess)² / (2 Var S) exactly, 3.42 nats for the larger tier:

| primes | number of primes | share of the rows left that the range strikes | mean innovation in the tier, in standard deviations | information, nats | per prime | cumulative share |
|---|---|---|---|---|---|---|
| 463 to 10^3 | 78 | 0.106 | +0.59 | 0.17 | 2·10^−3 | 0.05 |
| 10^3 to 3·10^3 | 262 | 0.136 | +0.74 | 0.28 | 1·10^−3 | 0.13 |
| 3·10^3 to 10^4 | 799 | 0.130 | +0.79 | 0.31 | 4·10^−4 | 0.22 |
| 10^4 to 3·10^4 | 2,016 | 0.106 | +0.83 | 0.35 | 2·10^−4 | 0.32 |
| 3·10^4 to 10^5 | 6,347 | 0.105 | +0.79 | 0.31 | 5·10^−5 | 0.41 |
| 10^5 to 2·10^5 | 8,392 | 0.057 | +0.65 | 0.21 | 3·10^−5 | 0.48 |
| 2·10^5 to 10^6 | 60,514 | 0.116 | +0.96 | 0.46 | 8·10^−6 | 0.61 |
| 10^6 to 10^7 | 586,081 | 0.143 | +1.18 | 0.70 | 1·10^−6 | 0.81 |
| 10^7 to 10^8 | 5,096,876 | 0.125 | +1.13 | 0.64 | 1·10^−7 | 1.00 |

Half of what distinguishes the best members is carried by the primes above 200,000, each of which can strike one row
at most, and two fifths by the primes above a million; the later a range, the more it counts, because a row struck
early would often have been struck later anyway. The smaller tier gives the same shares (0.06, 0.15, 0.21, 0.32, 0.41,
0.48, 0.61, 0.81, 1). No prime carries more than a few thousandths of a nat.

Strikes and repeats, as in section 2: over all members 1,635 strikes on the 1,502 rows, 996 distinct rows struck, 639
repeats, exactly what strikes on random rows give. The best 1.1% have 1,711 strikes, 1,044 distinct and 667 repeats
where chance would give 689 for that many strikes: an advantage of 47.1 rows = 24.9 from more strikes + 22.3 from
fewer repeats. The best 0.1%: 59.9 = 30.4 + 29.5. Half and half, as in the miniature.

## 5. Does the prize extrapolate? Three exact miniatures against the count over class vectors (`truth2.c`, `ensemble.c`, `fair_sample.py`, `depth_series.py`, `anatomy4.py`, `tilt_prize.py`)

The research session's Result 3 gives the prize at 200 digits from a count of class vectors by rows left, with no N
in it. It rests on two things that had been checked on one exact instance: that the N below the bound are a fair
sample of the class vectors, in the far tail where the prize sits; and that the gain of a later prime s is (rows / s)
times a price. Two more instances enumerated completely, one of them at five depths, against 6.4·10^9 class vectors
drawn uniformly at random for each (`ensemble.c`; nonzero classes up to the prime after the line, as for members):

| | X | target (rows) | line | members | successes | rows left at the line | at depth 200 | correlation r |
|---|---|---|---|---|---|---|---|---|
| M1 | 10^9 | 1,000 (167) | 23 | 157,947,020 | 256 | 36.80 ± 2.86 | 23.34 ± 3.14 | 0.579 |
| M2 | 10^10 | 1,000 (167) | 29 | 1,528,521,322 | 12,283 | 35.50 ± 2.89 | 23.33 ± 3.14 | 0.604 |
| M3 | 10^9 | 2,000 (302) | 23 | 157,946,861 | 0 | 66.22 ± 3.27 | 41.99 ± 3.93 | 0.528 |

**(a) Fair sample, in the tail too** (`fair_sample_M1.txt`, `_M2`, `_M3`). Members with at most k rows left at depth
200, exact count against the count for random class vectors scaled to the same number of members:

| rarity of the level, nats | M1: exact / ensemble | M2 | M3 |
|---|---|---|---|
| about 16.5 | 13 / 9.0 | 90 / 91.5 = 0.98 | 8 / 7.6 |
| about 14.7 | 62 / 64.3 = 0.96 | 592 / 622.6 = 0.95 | 115 / 125.6 = 0.92 |
| about 12.9 | 401 / 376.8 = 1.06 | 3,739 / 3,737 = 1.000 | 411 / 460.1 = 0.89 |
| about 11.3 | 1,965 / 1,930 = 1.018 | 18,965 / 19,093 = 0.993 | 1,558 / 1,567 = 0.994 |
| about 8.4 | 33,598 / 33,092 = 1.015 | 324,523 / 324,297 = 1.001 | 40,895 / 40,256 = 1.016 |
| about 6.1 | 343,538 / 340,108 = 1.010 | 3,333,965 / 3,332,755 = 1.000 | 250,902 / 247,782 = 1.013 |
| about 4.2 | 2,235,494 / 2,217,292 = 1.008 | 21,705,777 / 21,702,591 = 1.000 | 2,351,456 / 2,323,224 = 1.012 |

At X = 10^10 the two agree within the sampling error at every level. At X = 10^9 the true members have one to two
percent more in every level of the tail, and it is one effect, a shift of the mean that depends only on how long the
interval is against the depth z of the sieve:

| | X as a power of z | mean rows left, true members − class vectors | relative |
|---|---|---|---|
| M2 at depth 50, 100, 200 | z^5.89, z^5.00, z^4.35 | −0.0001, +0.0001, −0.0001 (± 0.0001) | below 4·10^−6 |
| M1, depth 200 | z^3.91 | −0.0095 ± 0.0003 | −4.1·10^−4 |
| M3, depth 200 | z^3.91 | −0.0171 ± 0.0003 | −4.1·10^−4 |
| M2 at depth 400 | z^3.84 | −0.0105 ± 0.0001 | −5.0·10^−4 |
| M2 at depth 700 | z^3.51 | −0.0056 ± 0.0001 | −2.9·10^−4 |

Nothing above the fourth power; below it (where products of four sieving primes start to exceed X) a few parts in
ten thousand, not monotone, as the error term of a sieve is, and the same for 167 rows and for 302. At 200 digits and
depth 50,000 the interval is z^42.6. The split of the tier between cover and position is the same too (cover nats of
the tier k2 ≤ 10 of M2: 3.00 exact, 3.03 in the ensemble; mean rows left by the cover 28.32 and 28.28).

**(b) The prize computed from class vectors is the prize, at every depth** (`depth_series.py` → `depth_series_M2.txt`;
M2 enumerated again at depths 50, 100, 400 and 700, with 1.6·10^9 class vectors for each). Prize = ln of (members
examined by cover first / by the ideal order at that depth) for the same number of successes, three ways: with the
true successes; with the exact histogram and the chance (1 − p)^k for a member with k rows left, p fitted to the
successes by level; with the histogram of random class vectors and the same chance.

| depth | primes beyond the line | rows left | r | p | prize at 100 successes: true / exact histogram / class vectors | at 1,000 | at 3,000 |
|---|---|---|---|---|---|---|---|
| 50 | 5 | 31.14 ± 2.99 | 0.847 | 0.330 | 0.79 / 0.75 / 0.75 | 0.49 / 0.52 / 0.52 | 0.41 / 0.40 / 0.40 |
| 100 | 15 | 27.02 ± 3.09 | 0.711 | 0.378 | 1.79 / 1.68 / 1.68 | 1.17 / 1.24 / 1.24 | 0.97 / 0.98 / 0.98 |
| 200 | 36 | 23.33 ± 3.14 | 0.604 | 0.435 | 2.83 / 2.76 / 2.76 | 2.11 / 2.15 / 2.15 | 1.66 / 1.71 / 1.71 |
| 400 | 68 | 20.89 ± 3.15 | 0.539 | 0.485 | 3.92 / 3.67 / 3.67 | 2.94 / 2.97 / 2.96 | 2.39 / 2.42 / 2.41 |
| 700 | 115 | 19.13 ± 3.14 | 0.495 | 0.528 | 4.65 / 4.48 / 4.51 | 3.71 / 3.72 / 3.72 | 3.05 / 3.04 / 3.04 |

The prize grows with the depth, from 0.4 to 3.0 nats at 3,000 successes, and the count over class vectors gives the
exact histogram's prize to 0.03 nats at every depth; the true successes follow within their own noise (0.1 to 0.25
nats at 100 successes, a few hundredths at 3,000). In M1: 3.86, 3.57, 3.04, 2.70, 1.93 nats at 1, 3, 10, 30, 100
successes from class vectors, 3.85, 3.57, 3.06, 2.70, 1.93 from the exact histogram (the true successes give 5.44,
5.06, 3.15, 2.79, 1.94: the first of them came early in the ideal order, after 13 members where 305 are expected).

**(c) One price at every prime** (`anatomy4.py`, `ensemble_tier.c`). For a member and a later prime s let others_s
be the rows left by every prime except s, and only_s the number of them in the member's class modulo s. In a
population weighted by exp(−β·rows left), the class modulo s given all the other classes has the law
exp(β·only_s) exactly, with the same β at every prime. So the claim is that the best members show one tilt in
only_s, whose unselected mean is others_s / s. M2, the 18,965 members with at most 10 rows left, against the 79,301
random class vectors with at most 10 (`anatomy4_M2.txt`):

| s | rows left by the other primes | unselected mean of only_s | mean in the tier | tilt β_s | same mean in the ensemble tier |
|---|---|---|---|---|---|
| 31 | 10.93 | 0.359 | 1.160 | 1.595 | 1.162 |
| 41 | 10.64 | 0.260 | 0.878 | 1.587 | 0.864 |
| 61 | 10.36 | 0.170 | 0.593 | 1.609 | 0.582 |
| 97 | 10.18 | 0.105 | 0.412 | 1.575 | 0.416 |
| 149 | 10.03 | 0.067 | 0.263 | 1.588 | 0.263 |
| 199 | 9.97 | 0.050 | 0.206 | 1.590 | 0.206 |

| | tier | β fitted to each prime: least to largest (sd over the primes) | one β for all primes | largest error of that one β at a prime | slope of ln(members) by level at the tier | exact tier / ensemble tier, prime by prime |
|---|---|---|---|---|---|---|
| M1 | k2 ≤ 10 (1,965) | 1.47 to 1.68 (0.05) | 1.584 | 10% | 1.60 | 0.92 to 1.08, mean 1.000 |
| M2 | k2 ≤ 10 (18,965) | 1.54 to 1.61 (0.016) | 1.579 | 3% | 1.60 | 0.96 to 1.02, mean 1.001 |
| M3 | k2 ≤ 25 (1,558) | 1.12 to 1.27 (0.04) | 1.198 | 6% | 1.20 | 0.94 to 1.05, mean 0.999 |

The scatter of β_s over the primes is the sampling error of the tier (1% with 19,000 members). So: yes. The gain of a
later prime is (rows left by the other primes / s) times a factor fixed by one price β (3.2 at the prime 31 to 4.1 at
199 in M2, the mean of the class counts under the weight e^(β·count); e^β = 4.85 is its value for Poisson counts);
β is the slope of the logarithm of the number of members by level (the slope column, from the ensemble's counts at
the top level of the tier), 1.58 nats per row at the tier of rarity 11.3 with 167 rows and 1.20 with 302; and the
true members carry it prime by prime as the class vectors do. The tilt of section 1, rising from 0.9 to 1.6
along the primes, was this one price seen through the order of the primes: a row struck at an early prime would often
have been struck by a later one.

**(d) A closed form, good for the miniatures only** (`tilt_prize.py`; `Cap.selection_fraction_two`). If the two
counts were jointly normal with correlation r, and λ = −ln(1 − p)·sd(rows left at depth), then to collect the share
f of the successes the ideal order examines the share Φ(Φ⁻¹(f) − λ) of the members and cover first the share
Φ(Φ⁻¹(f) − rλ), so prize(f) = ln Φ(Φ⁻¹(f) − rλ) − ln Φ(Φ⁻¹(f) − λ). For M2 at depth 200 (r = 0.604, λ = 1.791):
3.82, 3.63, 3.40, 3.17, 2.89, 2.60, 2.22, 1.77 nats at 1 to 3,000 successes, against 3.62, 3.46, 3.22, 3.03, 2.76,
2.49, 2.15, 1.71 from the histogram: 0.06 to 0.2 too large, more in the tail. It shows what the prize depends on (how
weakly the cover predicts the later count, and how many standard deviations the price buys), and it cannot be carried
to 200 digits: there the best covers are 27 standard deviations below the mean cover, where no normal law holds. The
count over class vectors is the tool at that distance, and (a) to (c) are the check of its two assumptions.

## 6. The inspection game: how many windows must be looked at (`strategy.py`, `mustlook.py`, `chance_first.py`, `smallest_cells.py`; `GoldbachGaps/Cap/Inspection.lean`)

The research session's question: on instances small enough to be exact, what is the cheapest procedure that finds
the optimum, counting the candidates whose full score it computes, if it may read residues for free? Read literally
this is empty, since a score is a function of residues. It is a game once something is hidden, and the choice made
here is the one the search itself makes: **free** is whatever depends on the cover alone (for each cell c the set
R_c of rows its classes leave, hence the least score LB(c) that any classes of the later primes could give it, its
free bound, and the chance P_c(v) that a member with uniform later classes scores at most v); **hidden**, until the
cell is looked at, are the classes of its members modulo the later primes.

**Proving the optimum: the game is solved** (`mem_of_certifies`, `certifies_of`, `card_le_of_certifies`,
`exists_certifies_card_le`). A set of cells proves the optimum v exactly when it contains every cell with LB(c) < v
and one cell that attains v. So the least number of cells is #{c : LB(c) < OPT}, plus one if none of those holds an
optimum; no adaptive procedure does better, and "increasing free bound, stop when the best score seen is at most the
next bound" attains it up to the ties at LB = OPT.

**The smallest instance** (rows below 160, cells the 105 even classes modulo 210, later primes 11 and 13;
`smallest_cells.txt`; in the kernel: `Example840.cells_below_optimum`, `cells_at_optimum`). Three cells have free
bound 5 (their candidates score 7 to 11); seven have 6, the optimum's own among them, so 578 has the best classes
modulo 11 and 13 that its cover allows; the other 95 have 7 or more. Value of the game: 4 cells, 16 of the 420
candidates. Bound first looks at 4 to 10 cells.

*All seven designs at once* (`smallest_designs.py`; `free_bounds_optimum`, `free_bounds_all_but_two`, `tie_152`). A candidate lies in one
cell of each maximal pinnable design, and each has its free bound. Taken together they exclude everything: every
candidate is in some cell none of whose numbers could be left with fewer than 6 rows, and every candidate but 152 and
578 in one none of whose numbers could be left with fewer than 7 (578 has bound 6 in all seven designs, 152 in five;
for 91 of the 420 candidates the best of the seven bounds is the score itself, for 243 it is within one row).
One full score, of 578, then proves the optimum, where the single design needs 16. This is the one place where a
procedure does markedly better than "every candidate in the cells that could contain it", and it does not travel:
the seven bounds are 1,497 cells' worth of work for 420 candidates, and a free bound is strong only while two or three
moduli lie outside the design (next table).

**The grid** (`strategy.txt`, 25 instances: targets 160 to 1,000, 105 to 15,015 cells, windows 2 to 8):

| primes beyond the line | cells with LB < OPT, mean | share of the cells: mean (largest) | cells looked at before the first optimum: cover first | bound first | chance first |
|---|---|---|---|---|---|
| 1 | 1.9 | 0.06% (0.3%) | 3.7 | 5.4 | 1.4 |
| 2 | 6.8 | 0.6% (2.9%) | 4.6 | 7.8 | 5.6 |
| 3 | 64.6 | 1.4% (6.1%) | 9.2 | 6.5 | 4.8 |

(Ties broken at the midpoint; "chance first" is the decreasing order of P_c(OPT), which uses the value of the
optimum.) Under uniform later classes the cells are expected to hold 56.6 members at least as good as the optimum,
over the 25 instances; they hold 56: the instances are what the game's model says.

**The miniature, to full depth** (`mustlook.txt`: Q = 1,000, line 23, 200,000 random cells; the free bound is
bracketed, from above by the greedy choice of one class per later prime, from below by letting each prime take its
fullest class with overlaps ignored). Share of the cells that no free bound excludes:

| primes beyond the line | OPT | at least | at most |
|---|---|---|---|
| 1 to 5 | 20 to 15 | 0.00% | 0.01% |
| 6 | 14 | 0.01% | 0.09% |
| 8 | 14 | 1.2% | 4.9% |
| 10 | 12 | 3.5% | 16% |
| 12 | 11 | 11% | 38% |
| 15 | 11 | 40% | 60% |
| 20 | 9 | 58% | 78% |
| 30 | 7 | 78% | 99.4% |
| 37 | 6 | 93% | 99.99% |

The exact free bound of a cell with many later primes is a covering problem of its own (one class per prime, most
rows covered); it was not solved, and the bracket is where the exact answer stops. It does not need to be: a free
bound lets every later prime take its best class, each later prime strikes at least one row of its choice, and the
bound is gone once the later primes outnumber the rows left. At 200 digits it is zero for every cover that matters:
the best cover leaves 1,502 rows, and there are 17,894 primes between 463 and the target alone.

**Finding rather than proving** (`searchCost_le_of_perm`; `chance_first.py`). To find a member at least as good as a
target, with independent cells, what is seen in one cell says nothing about another, every procedure is an order,
and the decreasing order of the chances P_c is the best one. On the grid it reaches the optimum earlier than cover
first in 18 instances of 25 and later in 3 (4.0 cells against 5.8 on average). In the miniatures the chance of a
cover is its number of rows left and the spread of the later count given the cover, and the spread hardly varies:
its standard deviation is 2.56 on average and differs by 1% between covers with the same number of rows. Ordering the
true members by the two-moment chance instead of the rows left collects the best tier 0.03 nats sooner (member by
member +0.031 ± 0.009 in M1 and +0.034 ± 0.003 in M2, where it is positive at every share collected). At 200 digits
the spread is the same to 0.01% for the 300 covers of the search file (`../selection_check`: 0.9835 to 0.9837 of the
binomial value), and the two orders coincide.

**So**: in the game the cheapest proof looks at every cell whose free bound is below the optimum, and nothing else
helps; near the line that is a handful of cells, and with every further prime it is more, up to all of them. The
cheapest search is by chance, which is cover first to 0.03 nats in the miniature and to nothing measurable at 200
digits. What the
game leaves out is any link between the later classes of different cells, which are one arithmetic progression's
worth of points and not independent draws. Every use of that link tried so far is a family of
`../pprime_families` (lattice decoding, merging, trees, buckets), each negative on the miniature; the game is the
statement that without such a link nothing beats looking.

**What the link can give** (asked by the research session after this section; `card_good_sharing_le`,
`card_good_sharing_le_card`, `add_mul_prod_mod`). Moving by a multiple of the product P of a set U of later primes
changes no class on U, so the numbers that share a member's classes on U are the points N + tP of one progression,
each in a different cell while there are fewer than M of them. How many of them lie in good cells? The room count
again: at most X/P + 1 in all, and at most (number of good cells)·(X/(MP) + 1), which is one for each good cell at
most once P exceeds the window. It is `card_residues_in_le_sub` with the cover modulus as a single modulus carrying
the list of good cells and one class on each prime of U. On average over the classes on U the number is exactly
(members of good cells)/P. The progression is the pinnable design "U and whichever cover primes still fit below X",
so the link is the freedom to choose what to pin, already counted in section 2, and nothing more.

To reproduce: `gcc -O3 -march=native -o truth2 truth2.c` and the same for `ensemble.c`, `ensemble_tier.c`;
`./truth2 1000 29 31 200 A B 11 OUT` over slices [A, B) of [0, 10^10) for M2 (a few minutes on four cores; the
lists `OUT.top` of the best members are in `runs/top/`: `check_1e9.top` for M1, `m2a_0..3.top` and `m2b.top` for M2,
`depth_z*_*.top` for the depth series), `./ensemble 1000 29 31 200 1600000000 SEED OUT`; the merged
histograms are in `runs/`. Then `python fair_sample.py M2 runs/M2 -- runs/M2_ensemble`,
`python depth_series.py 29 50:runs/M2_z50:runs/M2_z50_ensemble ...`,
`python anatomy4.py 1000 29 31 200 10 runs/M2_ensemble.tier OUT_*.top`, `python strategy.py`, `python mustlook.py`,
`python chance_first.py 1000 29 31 200 1e10 10 2000000 OUT_*.top`.
