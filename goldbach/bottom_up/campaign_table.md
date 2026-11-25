# The 200-digit campaign: the chance of ending at or above G, by design level (25 November, evening)

The program is `campaign_table.py` (output in `campaign_table.out`), written from the cover files independently of the research
session's `cover_design.py`.

**Inputs, with today's corrections:**
- **Exponent:** averaged over members uniform in N. At 200,000 it is 36.54, against 36.46 at N = 10^200.
- **Survival through the sieve:** c, the exact product over the sieve primes to 10⁸, which is 0.336642 for the 463 family. That
  agrees with the Lean session's value.
- **Spread and tilt:** the survivors' sd is 0.9836 of independent, and the tilt is λ′·sd. That gives 20.1% captured at 200,000.
- **Rows:** the rows the fleet runs, not the best. At 170,000 that is +5.5 (G4s at 1,249–1,250 against a best of 1,245, stepping
  to 1,251). At 180,000–200,000 it is +4.5, since about ten million covers lie within +5 rows.
- **Cost per member:** 26% sieve (proportional to the rows) and 74% tests, the G4's measured split.
- **Budget:** 1.90 expected design hits at 170,000 as the fleet runs (GPU session, 16:05Z).
- **How a hit at D extends:** a design hit at D is decided beyond D by the cover's unsieved remaining rows in [D, G).
- **The record held today:** 112,249.

## No engineering package (the budget as it stands)

| design | rows run | exponent | captured | design hits | P(≥ 170k) | P(≥ 180k) | P(≥ 190k) | P(≥ 200k) | P(≥ 213,070) | E[record], hits only | E[record], all g |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 170,000 | 1,250.5 | 30.42 | 17.0% | 1.90 | 85.0% | 16.7% | 1.40% | 0.133% | 0.006% | 166,957 | 172,106 |
| 180,000 | 1,338.5 | 32.56 | 18.1% | 0.233 | – | 20.7% | 1.66% | 0.130% | 0.006% | 127,184 | 169,465 |
| 190,000 | 1,424.5 | 34.65 | 19.1% | 0.030 | – | – | 2.94% | 0.295% | 0.012% | 114,656 | 168,790 |
| 200,000 | 1,506.5 | 36.65 | 20.1% | 0.0042 | – | – | – | 0.420% | 0.018% | 112,636 | 168,361 |

## With the engineering package

+0.35 nats is uarch's +0.3 plus G4s only at +0.05. +0.65 nats is +0.45 plus +0.2.

| design | P(≥ 180k) | P(≥ 190k) | P(≥ 200k) | E[record], hits only | E[record], all g |
|---|---|---|---|---|---|
| 170,000, +0.35 | 22.9% | 1.99% | 0.188% | 173,062 | 174,669 |
| 200,000, +0.35 | – | – | 0.596% | 112,798 | 170,660 |
| 170,000, +0.65 | 29.6% | 2.67% | 0.254% | 176,681 | 176,724 |
| 200,000, +0.65 | – | – | 0.803% | 112,989 | 172,628 |

The 180,000 and 190,000 designs are in `campaign_table.out`.

## Reading it

- **The chance of 200,000 is under 1% for every design and package.** The best is 0.80%: the 200,000 design with the full package.
  The present design gives 0.13%.
- **The expected record is highest with the 170,000 design:** 167,000–177,000 according to the package.
- **"E[record], all g" assumes the tests run each kept member's survivors in increasing q.** Then the first probable prime found is
  the member's g, at no extra cost, and members that fail just below the design level also count.
  - With the 170,000 design this adds about 5,000 to the expected record without the package.
  - With a 200,000 design it turns 112,636 into 168,361, because almost all of that design's expected record then comes from
    members that fail between 160,000 and 200,000.
  - If the fleet tests survivors in another order, only the "hits only" column applies.
