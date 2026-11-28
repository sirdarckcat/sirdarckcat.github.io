# Handover: what this session did, what came of it, and what is unfinished

This session worked from 23 to 26 November 2026, mostly on requests from the research session. Everything below is in this branch
under `goldbach/`. All jobs were stopped on 26 November at 08:37 UTC, when the user decided to wind the work down.

## The problem in brief

Take an even number N. Its *least Goldbach summand*, g(N), is the smallest prime p for which N − p is also prime. The game is to
find N for which g(N) is unusually large. The main goal was an N with at most 200 digits. The record there is g = 160,357, found by
the GPU search that the other sessions ran.

For g(N) to be large, N − q must be composite for every prime q below the target. The searches arrange most of this on purpose.

- **The cover.** A *cover* fixes the remainders of N on division by the first 89 odd primes. When N leaves the same remainder as q,
  that small prime divides N − q.
- **The rows.** A good cover deals with all but about 1,200 to 1,500 of the primes q. Those leftovers are called *rows*, and they
  are left to luck.
- **The window.** The numbers below 10^200 that share a cover's remainders form a *window* of 16 to 21 million candidates.
- **The sieve.** A *sieve* by further small primes discards the candidates whose rows are most likely to hold a prime.
- **The tests.** The remaining candidates get *Fermat tests*, a quick test that proves a number composite when it fails.

A *nat* is a factor of e, about 2.7, so five nats is a factor of about 150.

Each result is marked with one of these:
- **proved**: on paper, sometimes within a stated model;
- **machine-checked**: also verified by the Lean proof assistant, in the Lean session;
- **computed twice**: by two independent programs or sessions;
- **computed once**;
- **opinion**.

## The million-gap records (`../g_million/`)

Here the question is turned round: how few digits does an N with no summand below 1,000,000 need? The record before this work had
2,480 digits.

| digits | g(N) | directory |
|---|---|---|
| 2,196 | 1,001,491 | `record_2196digit/` |
| 1,997 | 1,008,589 | `record_1997digit/` |
| 1,797 | 1,021,897 | `record_1797digit/` |

- **No summand below g.** Every N − q below g is shown composite, with one reason for each prime q. This is computed twice (here,
  and from N alone by another session) and machine-checked.
- **g is a summand.** That rests on a strong probable-prime test of N − g, as is usual at this size.
- **Unfinished.** A 1,700-digit step was prepared: a cover on 547 primes, the sieve, and 300,000 selected candidates. 1,184 of them
  were tested (`tested_d1700.jsonl`) before the step was paused. The cost model puts a hit at about 35 CPU-hours.

## The 200-digit campaign: forecast and design

- **The campaign table** (`campaign_table.md`). This gives the chance that the GPU search ends at or above each level, for each
  target the search could be built for. It counts every tested candidate, since one that fails just above the record still sets a
  new one.
  - On the design in use (built for 170,000), the chance of passing 170,000 was 85% and of reaching 200,000 about 0.14%. The
    expected final record was about 175,000.
  - Computed twice: the research session's own program agrees.
- **The two-stage design** (`../two_stage/b_answer.md`). This decides how many candidates to test.
  - Proved, within the model that rows are independent: testing the candidates with the fewest surviving rows is the best rule.
  - Proved in the same model: keeping the emptiest 1.5% is best when sieving a candidate costs about a sixth of a Fermat test, and
    loses less than 0.1 nat over a wide range around that.
  - The GPU cards' measured costs fall in that range.
- **The cost check** (`costcheck/`). An independent model of three cost questions the uarch session had measured agrees with its
  figures. Computed twice.
- **The CPU side scan** (`cpu_scan/`). 2,589 covers (42 billion candidates, 50 core-hours) were scanned at a target just above the
  record, and nothing beat it. Computed once.

## Can a smarter search find the best candidates without scoring them one by one?

That is where the user's "better maths" led. Every route examined fails, and these notes say where and why.

- **Methods that only look at candidates, or fix extra remainders** (`query_bound.md`). Proved: neither kind beats scoring every
  candidate by more than a small factor.
- **Combining half-solutions** ("meet in the middle", `statement_c/`). These never beat the plain method on a small problem built
  from the real tables. Computed once.
- **Soft decoding** (`../two_stage/d_answer.md`). The strongest known method for finding numbers whose remainders fall in given
  weighted lists cannot reach the best candidates. Proved, given that method's known guarantee.
- **A check cheaper than a Fermat test** (`../H2_one_page.md`).
  - Even a free one would be worth at most about 3 nats here. Proved, given the measured split of costs.
  - Every known check costs about as much as a Fermat test. That is from the literature, partly re-checked.
  - The cheaper screens the uarch session tried fell about 120 times short of paying for themselves.
- **Other kinds of N** (`README.md`). Neighbours that share rows, numbers next to a highly divisible number, and covers shared by
  pairs of numbers all lose against a plain cover. Computed once.
- **Opinion.** This is the same task as the "smooth number" search inside the fastest known factoring method, the number field
  sieve. Decades of work there have found nothing faster than sieving.

## Toy worlds (`worlds/`)

At the user's suggestion, the research session set up simplified settings in which the same question can be settled completely.
This session took two of them.

- **World 4: random tables** (`world4.md`). All of the following are proved.
  - On a random window, no method beats scoring by more than a small factor.
  - A method that is exact to the sieve's depth must read 300 to 440 table entries per candidate, close to what the sieve does.
  - For arbitrary tables (encoded by their two allowed residues), deciding whether a window holds even one qualifying candidate is
    NP-complete under an expected-polynomial-time randomized reduction for distinct prime moduli (so a fast solver implies
    NP ⊆ ZPP / RP), and deterministically NP-complete if prime-power/composite moduli are allowed or the primes are supplied. That
    means it is as hard as a large family of problems believed to have no fast solution.
- **World 2: candidates that form an error-correcting code** (`world2.md`). Proved: decoding methods of this kind are never cheaper
  than scanning at our sizes. Folding several remainders into one symbol, or counting one several times, gains nothing. One
  statement was corrected after the research session's checker read it.
- The results written on 26 November (W4.4, W4.5 and W2.1b) have not yet been checked by another session (W4.5's reduction was
  qualified as randomized following PR #34 review).

## Smaller pieces

- **Archipelagos** (`../archipelagos/`). g(N) was computed exactly for 20 million consecutive even numbers near 10^12, 10^15 and
  10^18.
  - The probability model behind every forecast holds to about 1%.
  - Large values cluster because neighbours share rows, a mechanism the Lean session proved.
  - Machine learning does no better than the count of rows.
  - Computed once.
- **Complete covers** (`../tempering_covers/`). These are remainder choices that make every N − q composite with no luck at all:
  up to 41,659 on 167 primes, 70,111 on 238 and 98,731 on 302. The first is machine-checked, and any cover can be re-checked from
  its list of remainders.
- **Closeness records** (`../closeness25/records/`). Two numbers at a quarter of the largest g expected for their size: 47 digits
  with g = 21,031, and 48 digits with g = 23,227. Each has a certificate and a check from N alone. Computed once.
- **Balls in boxes** (`../balls_in_boxes/`). Measurements for one step of the research session's proof outline. Computed once.

## Still open

- **The central question** (the research session's Problem P′). Find numbers below 10^200 that have few surviving rows at a deeper
  sieve level, without scoring candidates one by one. It would be worth 3 to 11 nats, enough to make 200,000 likely. No route to it
  is known.
- **Unscanned covers.** 411 of the first 3,000 covers in the 613 family were never scanned, nor the 2,727 free covers of the 479
  family, nor covers 3,000 to 5,999 of the 613 family. The ledger in `cpu_scan/` says how their specifications are made.
- **The 1,700-digit step** of the million-gap search.
- **Outside checks** of W4.4, W4.5 (since qualified as a randomized reduction following PR #34 review) and W2.1b.
