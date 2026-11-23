# The least Goldbach summand by other means

`GoldbachGaps/RecordGen.lean` generates A025018 exactly, and it does so by Goldbach calculations:
every step asks whether `front − q` is prime. This directory asks the other question: how much of
the sequence, and of the least Goldbach summand (LGS) in general, can be obtained *without* testing
any `N − q` for primality.

Answer: the statistics, almost completely; the individual terms, not at all. Four experiments.

## 1. A model with no primes in it (`model.py` → `model.txt`)

In the generator a striker `q` hits a number `N` when `N − q` is prime. The model replaces that by
a probability taken from the Hardy–Littlewood density,

    h(N) = 2 C₂ S(N) / ln N,      S(N) = ∏ over odd primes p | N of (p − 1)/(p − 2),

and one correction for the dependence between the summands of one `N`: the chance that `N` is
unstruck by the first `m` odd primes is

    u(N, m) = (1 − h)^m · exp(−c · A_m · m · h²),     A_m = Σ over the m strikers p of 1/(p − 2).

`c = 0` would be independent strikers. They are not independent: a prime `p ∤ N` kills the
strikers of one class modulo `p` together and leaves the others with a higher chance, so the number
of summands among the first `m` primes is less dispersed than a Poisson variable (to second order
its factorial cumulant is `−m h² (1 + A_m)`, counting one prime at a time; for the primes above
the strikers this is the inequality proved in `GoldbachGaps/Cap/Thinning.lean`). `c` is the only fitted number: `c = 0.92`,
fitted on the count of the scan up to 10^12.

| test | independent (c = 0) | with dependence (c = 0.92) |
|---|---|---|
| number of N ≤ 10^12 with LGS ≥ the m-th odd prime, m = 2 … 360 (4.6·10^11 down to 234 numbers) | too many, by a factor up to e^2.2 | within 10% (fitted here) |
| the same up to 10^11, **not used in the fit** | too many, up to e^2.5 | within 5% up to m = 240; +18%, −5%, −8% at the last three counts (353, 36 and 3 numbers) |
| wait of a front for its hit, 58 terms from 10^3 to 10^18: mean of h × (strikers faced), 1 expected | 1.03 ± 0.13 | (same law) |
| jump from one front to the next, 57 jumps up to 10^18, **not used in the fit**: expected unstruck numbers in between, 1 expected | 11.6 | 1.00 ± 0.13 (median 0.76; 0.69 expected) |
| record value at 10^8 / 10^12 / 10^18 (actual 1093 / 3457 / 9341) | 1319 / 3671 / 9697 | 1097 / 3229 / 8861 |
| ln #{even N < 10^200 : LGS ≥ Q} for Q = 213,070 / 245,000 / 300,000 / 350,000 / 500,000 (research session's sampler: 403.3 / 395.7 / 383.1 / 371.5 / 338.0) | 403.7 / 396.2 / 383.7 / 372.2 / 338.9 | 403.2 / 395.7 / 383.0 / 371.5 / 337.9 |
| the value with one expected N below 10^200 (the campaign's ceiling: 2,130,704) | 2,154,007 | 2,133,689 |

So the campaign's cost-model figures follow from a formula that fits on a line, with one constant
measured on numbers below 10^12; neither the sampler nor any 200-digit computation enters. The
two routes agree within 0.1 nats at all five targets, which checks both. The ceiling moves by
about 0.4% when `c` goes from 0.5 to 1.3, so it is known to that accuracy and no better.

The second-order value of `c` counts one prime at a time and gives `1/2`; pairs of primes whose
product is below `m` add to it, and the fit absorbs them.

## 2. A generator that never sees a large prime (`simulate.py` → `simulate.txt`)

From a term `(N, g)`: the next front is the first point of a Poisson process with the model's
density of unstruck numbers; its value is the prime at which the first hit occurs, each striker
hitting with probability `h`. The output is random, so it is not A025018; the question is whether
A025018 looks like a typical output. It does. 400 synthetic sequences from the term 2642 to the
67th term (9.06·10^17), against the real one:

| | synthetic (median or mean, 5% to 95%) | real |
|---|---|---|
| number of terms in that range | 57.7 (46 to 69) | 57 |
| largest value at 10^6 | 532 (457 to 683) | 523 |
| at 10^9 | 1567 (1439 to 1871) | 1789 |
| at 10^12 | 3319 (3067 to 3701) | 3457 |
| at 10^15 | 5779 (5476 to 6353) | 5569 |
| at the end | 8933 (8572 to 9677) | 9341 |

## 3. Residues only (`cover_rank.c` → `cover_rank.txt`)

Between two consecutive terms, give every even `N` the score "number of strikers `q` for which
`N − q` has no prime factor ≤ z": what the residues of `N` modulo the primes up to `z` leave open.
A search that tries candidates in order of this score reaches the next term after examining, on
average (17 terms from 54,244 to 113,632,822),

| z | 3 | 7 | 13 | 31 | 101 | 1009 |
|---|---|---|---|---|---|---|
| one candidate in | 4 | 10 | 16 | 48 | 408 | 36,880 |

At `z = 101` the term 113,632,822 has 19 of its 182 strikers left open, against 43 for a typical
number of its interval: a term is a good cover *and* lucky on what the cover leaves. This is the
"cover and luck" of the 200-digit search, measured on the exact sequence.

## 4. When is the next term? (`forecast.py` → `forecast.txt`)

The N generator (`GoldbachGaps/RecordWalk.lean`, `scripts/record_gen/ngen.c`) walks the even
numbers and announces `N` when no striker up to the current record `G` hits it. The model gives
each `N` a chance `u(N, m)` of that, `m` the number of odd primes up to `G`, so after a term the
expected number of announcements among the next numbers up to `x` is the sum `E(x)` of those
chances, and the next term is the first ring of a clock of that rate. `forecast.py` inverts
`E`: from each term alone it gives the points below which the next term falls with probability
5%, 50% and 95%. This is the front law of section 1 read on the `N` axis; nothing is fitted.

| after the term (value) | 5% | 50% | 95% | the next term really was |
|---|---|---|---|---|
| 721013438 (1789) | × 1.69 | × 4.84 | × 9.74 | × 2.56 |
| 599533546358 (3457) | × 1.28 | × 3.03 | × 5.96 | × 5.22 |
| 3132059294006 (3463) | × 1.012 | × 1.15 | × 1.55 | × 1.16 |
| 1047610575836828 (6469) | × 1.90 | × 5.77 | × 11.7 | × 5.97 |
| 906030579562279642 (9341) | × 1.18 | × 2.47 | × 4.77 | × 3.09 |
| 2795935116574469638 (9629) | × 1.06 | × 1.62 | × 2.82 | × 1.19 |

Over the 59 terms from 2642 to the 68th: 53 next terms inside the 5%–95% band (53.1 expected),
4 before it and 2 after it (3 and 3 expected); the mean of P(next ≤ real) is 0.489 (0.5 ± 0.038
expected). Terms 68 and 69 (`terms_68_69.txt`) entered no earlier test.

So the model knows *about when*: the band is a factor of 3 wide in the median, and narrow after
a small step (after 3463, a value only 6 above the previous one, the next term was due within
15% at even odds, and came at 16%), wide after a large one. It cannot know *which* `N`: inside
the band every candidate looks alike to it.

The first term nobody has computed is the one after 3325581707333960528 (value 9781, the last
of the b-file; the verification of Oliveira e Silva, Herzog and Pardi ends at 4·10^18 with no
further term). Given that, the forecast is: 5% below 4.2·10^18, even odds below 6.2·10^18, 95%
below 1.06·10^19.

## What this is and is not

* It is not a proof and cannot become one with present methods: `h(N)` is the Hardy–Littlewood
  conjecture, and the model treats the residues of `N` as random.
* It does not produce the terms. Which `N` is the next front depends on the primes near `N`; the
  model only says how far away it is likely to be (section 4) and how large its value is likely
  to be. An exact generator has to show, for every smaller even number, a summand below the
  record, and that is a Goldbach calculation for each of them (`GoldbachGaps/RecordGen.lean`;
  with `N` as the loop variable, `GoldbachGaps/RecordWalk.lean`).
* It found no hidden pattern beyond two effects: the singular series (a term avoids small odd prime
  factors, because each one multiplies the hit chance) and the dependence between summands. With
  these two, the real sequence passes every test above as a typical random outcome.

    python3 -I model.py terms.txt ../rank_records/hist_1e12.txt 1000000000000 ../rank_records/hist_1e11.txt 100000000000 > model.txt
    python3 -I simulate.py terms.txt 400 0.92 > simulate.txt          (from this directory; about 15 minutes)
    python3 -I forecast.py terms.txt 0.92 terms_68_69.txt > forecast.txt      (about 4 minutes)
    gcc -O2 -o cover_rank cover_rank.c -lm && ./cover_rank terms.txt 120000000 3 7 13 31 101 1009 > cover_rank.txt
