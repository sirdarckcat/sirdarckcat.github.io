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
  - It is also best for every x up to 175,000. At 180,000 the 180,000 design is ahead (20.7% against 16.7%).
  - The 190,000 design is best at 185,000–190,000 (2.94% against 1.40% at 190,000).
  - The 200,000 design is best from 195,000, where it only just leads the 190,000 design (0.84% against 0.82%).
  - (Corrected after bc7316f, which said "up to 180,000" and "185,000–195,000". The same holds with both packages.)
- **"All g" assumes the tests run each kept member's survivors in increasing q.** Then the first probable prime found is the member's
  g, at no extra cost, and members that fail just below the design level count. The research session is asking the GPU session
  whether the fleet does this. The records below the design level (160,357 and 158,209) suggest it reads something of the kind.
- **A correction to the first version of this table (6683f3e).** Its "all g" column for the 170,000–190,000 designs used the
  200,000 cover's rows below the design level, because of a late-binding bug in `campaign_table.py`. The P(≥ G) columns at or above
  the design level, and the 200,000 design's row, were not affected. The numbers above are after the fix.

## (b) Covers for a weighted target — `weighted_eval.py`, `weighted_eval.out`, `../g_million/heatbath_w.c`

- **The target:** rows below 170,000 weigh 1, and rows in [170,000, 200,000) weigh w.
- **The covers:** tempered with `heatbath_w`, which is `heatbath2`'s exact heat-bath move with a weight per row. Each run is 20,000
  sweeps with β from 1.8 to 10, over several seeds, and the best is kept. Both modulus families were run: the fleet's 491 family,
  started from its 170,000 cover, and the 463 family, started from the 170,000 and 200,000 covers.
- **At w = 0.25 the 491 family found nothing better than the fleet's cover:** the file `qw025_m89r491` is that cover, class for
  class.
- **The evaluation** is the same model as above:
  - the budget is calibrated on the fleet's 170,000 cover;
  - every tested member's g is counted;
  - the floor is 160,357;
  - the rows as run are the best plus 5.5 (491 family) or plus 4.5 (463 family).

### With the cut at 170,000 (the sieve and the 1.5% selection on the rows below 170,000), no package

| cover | rows < 170k / < 200k (run) | E[record] | P(≥ 165k) | P(≥ 170k) | P(≥ 175k) | P(≥ 180k) | P(≥ 185k) | P(≥ 190k) | P(≥ 195k) | P(≥ 200k) |
|---|---|---|---|---|---|---|---|---|---|---|
| the fleet's 170,000 cover (= w 0.25, 491) | 1,251 / 1,550 | 175,252 | 98.3% | 85.0% | 46.2% | 16.7% | 5.65% | 1.40% | 0.45% | 0.13% |
| w = 0.25 (463) | 1,254 / 1,546 | 174,942 | 97.2% | 82.8% | 43.7% | 16.7% | 5.65% | 1.44% | 0.48% | 0.15% |
| w = 0.5 (491) | 1,258 / 1,535 | 174,664 | 96.2% | 79.2% | 43.9% | 16.4% | 6.24% | 1.75% | 0.57% | 0.19% |
| w = 0.5 (463) | 1,261 / 1,527 | 174,291 | 95.2% | 76.7% | 40.8% | 15.7% | 6.39% | 1.98% | 0.63% | 0.23% |
| w = 0.75 (491) | 1,284 / 1,519 | 171,801 | 82.9% | 57.1% | 28.5% | 10.8% | 4.13% | 1.62% | 0.63% | 0.29% |
| w = 0.75 (463) | 1,288 / 1,509 | 171,565 | 76.7% | 54.4% | 28.4% | 12.7% | 6.18% | 2.32% | 0.88% | 0.36% |
| *for comparison, from the table above:* | | | | | | | | | | |
| 180,000 design (cut 180,000) | 1,339 below 180k | 173,154 | 81.4% | 61.2% | 39.9% | 20.7% | 5.91% | 1.66% | 0.48% | 0.13% |
| 190,000 design (cut 190,000) | 1,425 below 190k | 170,213 | 65.5% | 40.6% | 27.0% | 12.0% | 6.48% | 2.94% | 0.82% | 0.30% |
| 200,000 design (cut 200,000) | 1,306 / 1,506 | 168,739 | 59.0% | 34.8% | 19.7% | 9.10% | 4.36% | 1.88% | 0.84% | 0.42% |

### Every cover with the cut at 170,000–200,000 (`--cuts`): the best (cover, cut) for each x

| x | no package | +0.65 nats |
|---|---|---|
| 165,000–170,000 | the fleet's cover, cut 170,000: 98.3%, 85.0% | the same: 99.96%, 97.4% |
| 175,000 | the fleet's cover, cut 175,000: 47.0% | the same: 70.4% |
| 180,000 | the 180,000 design: 20.7% | the same: 35.9% |
| 185,000 | w = 0.5 (463), cut 185,000: 6.81% (the 190,000 design: 6.48%) | the same: 12.6% (12.1%) |
| 190,000 | the 190,000 design: 2.94% (w = 0.75 (463), cut 190,000: 2.50%) | the same: 5.56% |
| 195,000 | w = 0.75 (463), cut 195,000: 0.97% (the 200,000 design: 0.84%) | the same: 1.84% (1.60%) |
| 200,000 | the 200,000 design: 0.42% (w = 0.75 (463), cut 200,000: 0.40%) | the same: 0.80% |
| E[record] | the fleet's cover, cut 175,000: 175,259 (cut 170,000: 175,252) | the same: 178,246 (178,174) |

### Reading it

- **The weighted covers fill in the frontier between the designs, but they do not move the tail.**
  - They win only at 185,000 and at 195,000. Against the best other (cover, cut) pair, the margins are +0.15 points (6.81% against
    6.66%, the 190,000 design cut at 185,000) and +0.11 points (0.97% against 0.86%, the 200,000 design cut at 195,000).
  - With the full package those margins are +0.28 and +0.20.
  - At 200,000, w = 0.75 comes within 0.02 points of the 200,000 design.
- **The 180,000 design is beaten everywhere except at 180,000.** Both w = 0.5 covers have a higher expected record (174,300–174,700
  against 173,154) and a higher P(≥ x) for every x except 180,000. At 180,000 the 180,000 design leads, 20.7% against 16.4%.
- **The cut level matters little.**
  - Over cuts from 170,000 to 200,000, any one cover's expected record moves by at most 1,161, and its P(≥ 200,000) by at most
    +0.04 points (+0.08 with the package).
  - A higher cut buys probability near the new cut and pays for it below.
  - Raising the fleet's cut from 170,000 to 175,000 is neutral: +7 on the expected record. It trades 1.1 points at 170,000
    (85.0% → 84.0%) for 0.9 at 175,000 and 0.4 at 180,000.
- **The 463 family's weighted covers have heavier tails than the 491 family's at the same w** (w = 0.75: 0.36% against 0.29% at
  200,000). This is from one campaign each, and it may only reflect how far each one tempered.
- **The model ranks the designs. It does not change how small the tail is.** No cover and no cut reaches 1% at 200,000. The best
  is 0.42% without the package and 0.80% with the full package, the same as the 200,000 design in the table above.
