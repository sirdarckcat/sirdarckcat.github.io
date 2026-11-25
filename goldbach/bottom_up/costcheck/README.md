# A second number for the three cost-side items (research's request, 25 Nov 19:05 UTC)

These are independent checks of the uarch session's cost-side items: `goldbach/g200k/costside/RESULTS.md` on
`ccr-b8c25887-i6tn9f`, at 83b7b3e and as revised up to 99d4c1a.

Each number comes from a model written here, not from uarch's simulations or capture curves. The GPU's measured rates are
inputs that can't be checked from here, and are marked where used:
- Fermat: 24.6M tests/s;
- launch minimum t_min: 4 ms;
- gap between launches: 2.2 ms;
- pipeline speeds when both kernels run: Fermat 0.735, sieve 0.43;
- per batch: Fermat alone 1.318 s, sieve 0.434 s.

All outputs are in `costcheck.out`.

## Item 1: exact to 10^6 for every member, to 10^8 only for the emptiest share — agree (selection); cannot be checked (GPU cost)

The model is in `item1_two_stage.py`. It is a bivariate normal for the rows left at 10^6 and at 10^8 (S6, S8), built from the
Lean session's profile (94e40c5).
- **The profile:** nine ranges of primes. Range j strikes a share a_j of the rows left before it, plus an innovation e_j, and the
  innovations are uncorrelated.
- **The recursion:** with L_j the rows left after range j, L_j = (1 − a_j) L_{j−1} − e_j. So
  S8 − E S8 = (1 − a8)(1 − a9)(S6 − E S6) − (1 − a9) e8 − e9.
- **The moments this gives:**
  - Var S8 = 324.8, against 325.27 measured.
  - Var S6 = 352.1.
  - corr(S6, S8) = 0.781 (uarch measured 0.78), and corr(S7, S8) = 0.897 (uarch 0.90).
- **The hit mass** e^(−λ8 S8) tilts the pair by −λ8 (Cov, Var). The captured share is the tilted probability of the kept region.

Captured share at a final keep of 1.5%, as a fraction of the full count:

| score | this model | uarch (measured, per 32,768-block) |
|---|---|---|
| exact to 10^8 for every member | 1 (0.2032 absolute) | 1 (0.1987) |
| exact to 10^7 only | 0.820 | 0.817 |
| exact to 10^6 only | 0.642 | 0.638 |
| top 5% by the 10^6 count, then exact to 10^8 | 0.898 | – |
| top 10% by the 10^6 count, then exact to 10^8 | 0.963 (0.191 on the measured scale) | 0.959 (0.1906) |
| top 15% by the 10^6 count, then exact to 10^8 | 0.983 | – |
| top 20% by the 10^6 count, then exact to 10^8 | 0.992 (0.197) | 0.989 (0.1966) |
| top 30% by the 10^6 count, then exact to 10^8 | 0.998 | – |

- **At lower keeps the two-stage loses less.**
  - At 0.75%: 0.980 (top 10%) and 0.996 (top 20%).
  - At 0.5%: 0.986 and 0.997, against uarch's measured 0.983 and 0.995.
- **The absolute Gaussian shares are 2–3% above the measured ones** (0.2032 against 0.1987). That is the tail of a count against
  a normal. The ratios agree to 0.004.
- **The selection numbers are confirmed.**
- **The GPU design that would use them was withdrawn by its author before it was built** (4104ae5, 18:42Z). Its filter costs an L2
  lookup per large-prime mark: about 52 ms a window, against about 17 ms saved.
- The thread-block-cluster probe (c0c8ee3) looks for another way. Its rates can't be checked from here.
- **This item is not in the package below.**

## Item 2: carrying unfinished members into the next pool — agree with the waste and with +15% in its own setting; the realised gain cannot be checked from here

The model is in `item2_carry.py`, written from the round rule alone:
- each active member gets D = max(1, min(8, rows left, ⌊T / active⌋)) tests a launch;
- a member needs a geometric number of tests to reach its first probable prime;
- tests after that prime, within the same launch, are wasted.

It is an exact expected-value recursion over the active count, checked against a Monte Carlo of the same rule:
- **Waste:** both give 3.06%, on a half-pool of 503,808 members at T = 2^18.
- **Launches:** 44 by the recursion, 52 by the Monte Carlo. The difference is the deepest members.
- **Against the other models:** uarch 3.04% and 45.2 rounds; the GPU session's own model 44 rounds and 7.28M tests (7.27M here).

Gain in tests that count per second from carry-over, on a half-pool with T = 2^18. Columns 4–6 count different costs as real
(more of the tail priced to the left):

| tests a member | pool size (keep) | waste without carry-over | gaps and small launches both cost time | gaps hidden, small launches idle | gaps and small launches hidden (waste only) |
|---|---|---|---|---|---|
| geometric, mean 14 | 251,904 (0.75%) | 5.72% | +78% | +50% | +6.1% |
| geometric, mean 14 | 503,808 (1.5%) | 3.06% | +42% | +24% | +3.2% |
| geometric, mean 14 | 1,007,616 (3%) | 1.54% | +22% | +12% | +1.6% |
| geometric, mean 10 | 503,808 | 4.21% | +43% | +25% | +4.4% |
| geometric, mean 20 | 503,808 | 2.15% | +42% | +24% | +2.2% |

- **Uarch's first setting** is a full pool of 2,015,232 at T = 2^20, with gaps and t_min both costing time. There this model gives
  **+14.5%**, against uarch's +15%: agree.
- **Uarch's waste at keep 0.75%** is 5.72%. This model gives 5.72%: agree.
- **The waste scales as about 1/(pool size) and roughly as p.** Halving the keep doubles it.
- **What decides the realised gain is how much of the tail the G4 already hides.** That is a GPU measurement.
  - The GPU session's control-stream run hides the gaps.
  - Uarch's revision (99d4c1a) takes 2–6% of the batch.
  - This model's bounds, in batch time at keep 1.5%:
    - at least the waste: 3.06% of the Fermat time, about 2.5% of the batch;
    - at most the waste plus the whole tail of 0.175 s a batch: 13% of the batch, +15% hits/s.
- **Carry-over and a lower keep are complements, as uarch says.** The waste carry-over removes grows as the keep falls.

## Item 3: the keep when the objective is E[final record] with every tested member's g — disagree that 1.5% is the optimum; it is flat

The model is in `item3_keep.py`. It is the campaign model of `../campaign_table.py`, on the fleet's 170,000 cover with the rows as
run +5.5, with the keep κ left free:
- **Below the design level:** Λ(G) = M e^−E(n_G) Φ(z_κ + λ′ sd(n_G)²/sd(n_D)).
- **At and above it:** M e^−E(n_D) Φ(z_κ + λ′ sd(n_D)) e^(−λ · rows in [D, G)).
- **The budget:** M = W/cost(κ), with W calibrated at κ = 1.5%.

Three costs per member:
- **(A) additive,** the campaign model's split: 0.26 + 0.74 κ/1.5%.
- **(B) the G4 pipeline, rounds as now.**
  - The batch time is F + 0.616 S when Fermat-bound, and S + 0.776 F when sieve-bound.
  - The Fermat bulk scales with the kept members and with 1/(1 − waste(κ)), the waste taken from item 2.
  - Plus a fixed tail of 0.175 s a batch.
- **(C) the same with carry-over:** no waste and no tail.

| cost | optimum keep for E[final record] | its optimum for design hits | E at the optimum | E at 1.5% | keeps within 100 of the best E | design hits gained at the optimum |
|---|---|---|---|---|---|---|
| (A) | 0.84% | 0.84% | 175,460 | 175,252 (−208) | 0.57–1.24% | +0.045 nats |
| (B) | 1.00% | 1.00% | 175,362 | 175,252 (−110) | 0.71–1.46% | +0.024 nats |
| (C) | 1.00% | 1.00% | 176,226 | 175,910 (−316) | 0.76–1.16% | +0.070 nats |

- **Counting every tested member's g does not move the optimum.** The rows below the design level are tilted less by the
  selection, which favours a higher keep, but too little to show on a 200-point grid.
- **1.5% is not the optimum under any of the three costs.**
- **The curve is flat.** The best keep is worth +110 to +316 in E[final record].
- **Under (B) the gain is +0.024 nats at 1.0% (×1.013 at 0.75%),** against uarch's pipeline figure of ×1.049 at 0.75%. The difference
  is mostly the waste, which grows from 3.06% to 5.72% as the keep halves; uarch's linear scaling of the Fermat time leaves it out.
- **Under (C) the optimum sits where the batch turns sieve-bound** (F = 1.709 S at κ = 1.0%). Below it, a faster sieve is what would
  pay.

## The forecast on the 170,000 design with what survives (`forecast.py`)

Every tested member's g is counted, and the floor is 160,357. The keep is re-optimised for E[final record] in each row.

| configuration | keep | design hits at 170k | package (nats) | E[final record] | P(≥ 180k) | P(≥ 190k) | P(≥ 200k) |
|---|---|---|---|---|---|---|---|
| today (keep 1.5%, rounds as now) | 1.50% | 1.900 | 0 | 175,252 | 16.7% | 1.40% | 0.133% |
| keep re-optimised, rounds as now | 1.02% | 1.945 | +0.024 | 175,360 | 17.1% | 1.44% | 0.136% |
| carry-over (waste only) + keep | 0.94% | 2.002 | +0.053 | 175,495 | 17.5% | 1.48% | 0.140% |
| carry-over (waste and tail) + keep | 1.00% | 2.347 | +0.211 | 176,225 | 20.2% | 1.73% | 0.164% |
| *sensitivity:* the last with the sieve 20% faster (pass A at its integer floor; not checkable here) | 0.80% | 2.561 | +0.298 | 176,619 | 21.9% | 1.89% | 0.179% |

**My package number is +0.05 to +0.21 nats, in place of +0.35 and +0.65.**
- **The low end** is carry-over counted for its waste alone, with the gaps and small launches already hidden, plus the keep.
- **The high end** is carry-over removing the whole tail as well.
- Where the G4 falls between them is the GPU session's measurement to make: time a batch with and without `--carry-over 1`.
- **Not in the package:**
  - the two-stage count (its design was withdrawn);
  - pass A at its floor (not checkable here; it pays only once the keep is below about 1% and the batch is sieve-bound).
- **Even the high end changes the 200,000 line by 0.03 points** (0.133% → 0.164%).
