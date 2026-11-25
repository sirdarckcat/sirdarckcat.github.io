# (b): the best two-stage design at 200 digits, against the present single cut

**Setting.** The cover keeps 1,502 rows at p = 0.02398, with 89 moduli up to 463. The present design sieves to B = 10⁸ with a
window W = 2²⁴ and keeps the emptiest 1.5% (f = 0.985). `design_b.py` does the computations.

**Marks.** **[P]** proved, under the model stated in `design_b.py` (the H1 independence of survivors, S normal). **[M]** computed.
**[O]** opinion.

1. **A hard cut on S is optimal [P].**
   - P(hit | S) = (1 − p′)^S is strictly decreasing in S.
   - A kept member costs (1 − (1 − p′)^S)/p′ tests, which is 1/p′ to within e^(−36).
   - So for any test budget, the selection with the most hits is the threshold on S: the knapsack has equal weights and values
     that decrease in S.
   - Under H1 every survivor has the same p′, so S is sufficient. No other statistic of the survivor set can help.
2. **The tilt is λσ, not p′σ [P].**
   - The hit-weighted law of S is the normal law shifted down by λσ², with λ = −ln(1 − p′).
   - So δ = λσ = 1.311 sd, against p′σ = 1.263, using σ = 0.962·√(Rc(1 − c)) = 17.58.
   - The hit mass captured at a keep of 1.5% is Φ(−2.170 + 1.311) = **19.5%**, not 18%.
3. **When the present cut is optimal [P].**
   - Write ρ = (sieve cost per member)/(test cost per kept member), where a kept member costs 1/p′ = 13.9 Fermat tests.
   - The optimal z solves e^(−zδ − δ²/2)·(ρ + Φ(z)) = Φ(z + δ).
   - So keeping 1.5% is optimal exactly when **ρ = 0.0118**, that is, when sieving a member costs 0.16 of a Fermat test.
4. **Loss of the present cut against the best keep fraction, with B and W as now [M]:**

   | ρ | 0.001 | 0.003 | 0.01 | 0.0118 | 0.02 | 0.03 | 0.05 | 0.1 | 0.3 | 1 |
   |---|---|---|---|---|---|---|---|---|---|---|
   | best keep | 0.17% | 0.46% | 1.30% | 1.50% | 2.34% | 3.27% | 4.93% | 8.45% | about 20% | 39% |
   | gain (nats) | 0.47 | 0.17 | 0.003 | 0 | 0.03 | 0.09 | 0.21 | 0.42 | about 0.8 | 1.16 |

   **The present cut is within 0.1 nat of its optimum for 0.004 ≤ ρ ≤ 0.03.**
5. **Depth and keep re-optimized together, with W = 2²⁴ [M].** φ is the share of the sieve's cost spent on start positions.
   - For φ ≤ 0.5: the gain is 0.003–0.05 nat at ρ = 0.01 and 0.09–0.18 nat at ρ = 0.03.
   - Only a set-up share of φ = 0.8 moves the best depth down to about 2·10⁷, for a gain of 0.2–0.4 nat.
   - This confirms that the set-up cost (R·π(B) start positions per vector) holds the depth near the window length.
6. **A staged sieve (funnel) gains nothing [P under the cost model].**
   - In a window sieve the start positions are per (row, prime) and the marks are per progression, so abandoned members cannot be
     skipped.
   - Continuing one member by itself costs a reduction per prime, which is τ ≈ 10⁻⁴ of a Fermat test (by word counts).
   - Continuation beats testing the member at B₁ only over fewer than (1/p′)/τ ≈ 1.4–1.9·10⁵ primes. From B₁ ≥ 10⁷ that changes c
     by under 1.4%.
   - This agrees with the research session's threshold: keep fractions near 3·10⁻⁴, where the shallow statistic has already
     discarded about 99% of the hit mass.
7. **The one lever left is the window [M].**
   - W is already the whole cover, 2^24.3 members at 89 moduli. Without the largest modulus, 463, a cover has 2^33.2.
   - At ρ = 0.0118 and φ = 0.5, re-optimizing B and the keep for W = 2²⁶, 2²⁸ and 2³⁰ gains +0.20, +0.34 and +0.47 nat, against
     +0.05 at 2²⁴.
   - The price is Δ·0.0243 − 0.08 nat, where Δ is the number of rows only 463 covers and the 0.08 is because p falls by a factor
     462/463. So it pays when Δ < 20, if the fleet's sieve can hold 2³⁰ members per vector.
   - It also needs 462 times fewer distinct covers per hit: about 7·10⁵ instead of 3·10⁸. That matters if covers within a row or
     two of the best are scarce.

**Verdict.**
- If the fleet's constants give 0.004 ≤ ρ ≤ 0.03 with set-up share φ ≤ 0.5, the present single cut is within 0.1 nat (keep alone)
  to 0.2 nat (with depth) of the optimum for W = 2²⁴. That closes (b) with a negative answer: the design is not where the 5.4 nats
  are.
- The only gain over 0.2 nat is the bigger window above (+0.3 to 0.4 nat net), and it depends on Δ and on whether the sieve can
  hold 2³⁰ members per vector. **[O]**
- The numbers needed to settle it are ρ and φ from the fleet: ns per mark, ns per start position, ns per Fermat test, all per card.

## Addendum: the fleet's constants (GPU session, 16:05Z, relayed by the research session)

Here ρ = sieve cost per member / (tests per kept member × ns per test). It is 0.0054 on the G4, 0.0079 on the L4 and 0.0093 on the T4.
δ = 1.213 comes from the L4's own capture shares (25.2% at 3%, 16.8% at 1.5%). **[M]**

- **G4: best keep 0.85%, +0.04 nat over 1.5% and +0.19 over 3%.**
  - If its sieve (51 ms) runs beside the Fermat stage and the other 35 ms of a window are fixed, the wall time is
    max(51, 148·keep/1.5%) + 35 ms. The best keep is then 0.6%, +0.11 nat (keep 0.75% gives +0.10).
  - With the 1,502-row cover's δ = 1.311: best keep 0.77%, +0.06 nat.
- **L4 and T4:** at 1.19% and 1.36% the gain over 1.5% is under 0.01 nat. Over their 3% it is +0.11 and +0.08.
- **The window-for-modulus trade is closed on the G4.**
  - A bigger window can save only the fixed 24 ms a window, 1.43 ns of 11.59 ns a member (+0.13 nat). Its price is 9 rows:
    9·0.0243 − 0.08 = +0.14 nat. So it gains nothing.
  - Sieving to 10⁹ costs 147 marks at 0.13 ns, plus (prime, row) visits. It loses 1.2 nat at W = 2²⁴ and 0.8 nat at W = 2³⁰,
    even though it captures 19.8% instead of 16.9%.
- **Why the L4 A/B disagreed with the model (+8% predicted, −1.35% measured).**
  - The A/B implies an effective ρ = 0.0163. The L4's sieve and other costs give 0.0090. So about 22 ns a member, 0.75 s of the
    4.01 s window, does not shrink with the keep.
  - Equivalently, at 1.5% the Fermat stage took about 1.79 s, not half of 3.09 s. Its fixed part is about 0.49 s a window.
  - With that fixed part counted, the model gives the best keep at 2.2%, with 1.5% and 3% within 0.02 nat of each other. That is
    what the A/B found.
  - The likely cause **[O]**: the tail of the test stage. A kept member dies at a geometric number of tests, so a window needs
    about ln(n_kept)/λ rounds whatever n_kept is. The last rounds run with the GPU underfilled, and each round pays its launch
    and synchronization.
  - Two fixes. Fit the wall time per window at three or more keeps, as wall = a + b·keep, and optimize H(keep)/wall(keep).
    Or carry each window's unfinished members into the next window's test batches, which removes most of a; the linear model's
    optimum then holds.
  - The G4's production Fermat rate (19.9M a second, against 24.6M in the benchmark) suggests a similar loss there. An A/B at
    keep 0.75% on the G4 would settle whether its +0.04 to +0.11 nat is real.
