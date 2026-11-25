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
- **The record held today:** 160,357, the floor of every expected record (the fleet found it on the 24th; corrected at the research session's note, 18:24Z).

## No engineering package (the budget as it stands)

| design | rows run | exponent | captured | design hits | P(≥ 170k) | P(≥ 180k) | P(≥ 190k) | P(≥ 200k) | P(≥ 213,070) | E[record], hits only | E[record], all g |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 170,000 | 1,250.5 | 30.42 | 17.0% | 1.90 | 85.0% | 16.7% | 1.40% | 0.133% | 0.006% | 174,158 | 175,252 |
| 180,000 | 1,338.5 | 32.56 | 18.1% | 0.233 | – | 20.7% | 1.66% | 0.130% | 0.006% | 165,310 | 173,154 |
| 190,000 | 1,424.5 | 34.65 | 19.1% | 0.030 | – | – | 2.94% | 0.295% | 0.012% | 161,348 | 170,213 |
| 200,000 | 1,506.5 | 36.65 | 20.1% | 0.0042 | – | – | – | 0.420% | 0.018% | 160,542 | 168,739 |

213,070 is 10% of the ceiling at 10^200.

## The distribution of the final record, with every tested member's g counted (floor 160,357)

P(final ≥ x), without the engineering package:

| design | 165,000 | 170,000 | 175,000 | 180,000 | 185,000 | 190,000 | 195,000 | 200,000 |
|---|---|---|---|---|---|---|---|---|
| 170,000 | 98.3% | 85.0% | 46.2% | 16.7% | 5.65% | 1.40% | 0.45% | 0.13% |
| 180,000 | 81.4% | 61.2% | 39.9% | 20.7% | 5.91% | 1.66% | 0.48% | 0.13% |
| 190,000 | 65.5% | 40.6% | 27.0% | 12.0% | 6.48% | 2.94% | 0.82% | 0.30% |
| 200,000 | 59.0% | 34.8% | 19.7% | 9.10% | 4.36% | 1.88% | 0.84% | 0.42% |

With +0.35 nats and +0.65 nats, see `campaign_table.out`. At +0.65 the 200,000 design reaches 0.80% at 200,000, and the 170,000
design reaches 99.96% at 165,000 and 29.6% at 180,000.

## Reading it

- **The chance of 200,000 is under 1% for every design and package.** The best is 0.80%: the 200,000 design with the full package.
  The present design gives 0.13%.
- **The design to pick depends on what is wanted.**
  - The 170,000 design gives the highest expected record: 175,000 without the package, 177,000 with the full one.
  - It is also best for every x up to 180,000.
  - The 190,000 design is best at 185,000–195,000 (2.94% against 1.40% at 190,000).
  - The 200,000 design is best only at 200,000 and above.
- **"All g" assumes the tests run each kept member's survivors in increasing q.** Then the first probable prime found is the member's
  g, at no extra cost, and members that fail just below the design level count. The research session is asking the GPU session
  whether the fleet does this. The records below the design level (160,357 and 158,209) suggest it reads something of the kind.
- **A correction to the first version of this table (6683f3e).** Its "all g" column for the 170,000–190,000 designs used the
  200,000 cover's rows below the design level, because of a late-binding bug in `campaign_table.py`. The P(≥ G) columns at or above
  the design level, and the 200,000 design's row, were not affected. The numbers above are after the fix.
