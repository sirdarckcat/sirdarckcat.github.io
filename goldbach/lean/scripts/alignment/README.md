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
likelihood): about one nat per row at every prime, rising slowly from 0.9 to 1.6 as the rows get fewer. Each of the
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
