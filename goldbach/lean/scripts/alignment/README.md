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
