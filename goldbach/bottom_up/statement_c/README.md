# Statement C on a toy that can be solved exactly (research's request, 25 Nov)

**The question.** Statement C of `../query_bound.md` concerns additive algorithms, the ones that add partial solutions. Can one
of them beat pinning plus scanning? Here the question is measured on a toy built from the real data rather than argued.

**Answer (measured).** On this toy the additive class never beats pinning plus scanning, at any depth or harvest.
- **Closest case:** a factor of 2.3 (m = 6, window 2^24, the second-deepest level, harvesting every output).
- **Usual gap:** factors of 10 to 10^8.
- **Against plain scanning,** the additive class wins only for m = 6:
  - in a 2^24 window, from about κ = 6.5 when it harvests part of the outputs, and from about κ = 13.5 when it harvests all of them;
  - in a 2^20 window, only at the window's maximum.

  For m ≥ 8 it loses even to scanning.
- **The representation technique** has a single separable representation per solution here, so it reduces to the
  meet-in-the-middle that was measured.

## The toy (`toy.py`)

- **The cover:** `../covers/q200000_m89.txt` (89 moduli, the 1,502 rows below 200,000 that the cover leaves).
- **The members:** N = N0 + kM, with N0 in the middle of the cover's k range.
- **The later primes:** the first m primes after the moduli, s_1 … s_m = 467, 479, 487, …, for m = 6, 8 and 10.
- **The weight tables:** w_i(a) = #{rows q : N0 + aM ≡ q (mod s_i)}, the real tables. They have mean about 3, variance 2.2–2.7
  and maximum 7–9.
- **The score** is the knapsack form, with repeated strikes counted: S(k) = Σ_i w_i(k mod s_i).
- **The window:** k < K, for K = 2^20 and 2^24.
- **The depth t:** the outputs are the n(t) members of the window with S ≥ t, and κ = ln(K / n(t)).

## The classes and what each one touches (`measure.py`)

| class | what it does | touched |
|---|---|---|
| scan | every member of the window | K |
| pin (Theorem B, P_I ≤ K) | lists in full every sub-progression k ≡ a_I (mod P_I) whose pinned score S_I(a_I) ≥ τ | its members |
| tries (Theorem B, P_I > K) | tries every class vector a_I with S_I ≥ τ and evaluates the members that land in the window | 1 per try plus 1 per member landed |
| MITM (additive) | splits the primes A \| B with P_A, P_B > K; generates L_A = {x_A : S_A ≥ t_A} and L_B = {x_B : S_B ≥ t_B}; matches k = u_A + u_B (mod P) < K by a sort and range queries; evaluates every match | 1 per list entry plus 1 per match |
| pin+list (additive) | the same with one side small (P_A ≤ K): each pinned sub-progression is matched against L_B by a range query, j = (v_B − v_A) mod P_B < K / P_A, instead of being scanned | the same |

- **Parameters:** each class is optimised over its sets, its splits (prefixes of the later primes, which are alike) and its
  thresholds.
- **Harvest levels:** the best cost per output is reported at four levels: at least 1 output, at least 10%, at least 50%, and
  all n(t).
- **The counts are exact:**
  - list sizes and tries come from the convolution of the per-prime weight histograms;
  - members, matches and outputs come from the joint histogram of (S_A, S_B) over the window's exact scan.
- **The matching was run for real** (`mitm_run.py`, `mitm_run.out`) on m = 6 at 2^24 with thresholds (18, 18) and (20, 17):
  - the lists were 284,619 + 197,145 and 28,811 + 572,818 entries, equal to the convolution counts;
  - the 62 and 22 matches are exactly the window's members with S_A ≥ t_A and S_B ≥ t_B;
  - each run took 0.3 s.

## Results (`measure.out`)

Members touched per member output, for each class at its best:

| m | K | ln(4P/K²) | depth t | n(t) | κ | harvest | scan | best pin / tries | best additive | additive ÷ best enumerative |
|---|---|---|---|---|---|---|---|---|---|---|
| 6 | 2^20 | 10.80 | 31 | 1,520 | 6.54 | ≥ 1 | 690 | 5 | 10,086 | ×1,870 |
| 6 | 2^20 | 10.80 | 34 | 112 | 9.14 | all | 9,362 | 1,562 | 245,681 | ×157 |
| 6 | 2^20 | 10.80 | 38 | 1 | 13.86 | all | 1,048,576 | 16,139 | 225,957 | ×14 |
| 6 | 2^24 | 5.25 | 31 | 24,357 | 6.53 | all | 689 | 624 | 6,659 | ×10.7 |
| 6 | 2^24 | 5.25 | 34 | 1,810 | 9.13 | ≥ 1 | 9,269 | 13 | 2,468 | ×185 |
| 6 | 2^24 | 5.25 | 36 | 227 | 11.21 | all | 73,908 | 21,605 | 165,119 | ×7.64 |
| 6 | 2^24 | 5.25 | 38 | 24 | 13.46 | all | 699,051 | 59,398 | 136,775 | **×2.3** |
| 6 | 2^24 | 5.25 | 41 | 1 | 16.64 | all | 16,777,216 | 900 | 32,081 | ×35.6 |
| 8 | 2^24 | 17.74 | 42 | 1,695 | 9.20 | all | 9,898 | 8,962 | 27,397,046 | ×3,060 |
| 8 | 2^24 | 17.74 | 49 | 3 | 15.54 | all | 5,592,405 | 214,277 | 138,138,580 | ×645 |
| 10 | 2^24 | 30.29 | 50 | 1,233 | 9.52 | all | 13,607 | 13,166 | 16,460,383,205 | ×1.25·10^6 |
| 10 | 2^24 | 30.29 | 58 | 1 | 16.64 | all | 16,777,216 | 1,077,764 | 25,654,357,843 | ×23,800 |

- `measure.out` has every depth from the top 1% down to the window's maximum, at all four harvest levels, for all six cases.
- **The best additive algorithm** is always the both-sides MITM, except one case, where pin+list is marginally ahead (m = 6, 2^24,
  t = 38, harvest ≥ 1: 25,217 against 25,844).
- **In no row is the additive class below the best of scan, pin and tries.**

## The reason, with a number

**The additive bound.**
- In a split A | B, the CRT makes the window's members uniform over Z/P_A × Z/P_B, at density K/P.
- So lists of sizes P_A π_A and P_B π_B produce K π_A π_B matches.
- The cost per output is therefore at least (P_A π_A + P_B π_B) / (K π_A π_B) ≥ 2 √(P/K²) e^(κ_AB / 2), where
  κ_AB = −ln(π_A π_B) is the depth of the matched set.
- Scanning the same members costs e^(κ_AB). So the additive class beats scanning only when κ_AB > ln(4P/K²).

**The measured thresholds against the room in the window:**

| m | ln(4P/K²) at 2^20 | at 2^24 |
|---|---|---|
| 6 | 10.8 | 5.25 |
| 8 | 23.3 | 17.7 |
| 10 | 35.8 | 30.3 |

- A window has no depth beyond ln K: 13.9 at 2^20, 16.6 at 2^24.
- So m = 6 is the only case with room. The crossover against scanning is where the table shows it: at 2^24, about κ = 6.5 for a
  partial harvest and about 13.5 for a full one.

**Why pins do better.**
- A pin with P_I ≤ K pays no √(P/K²) factor: its outputs cost 1/π(I, a).
- The best classes of the pinned primes come at no cost. In the toy a class averages about 3 strikes and the first two primes
  reach 8. Two pinned primes at their best classes bring about +10 of a depth that needs +15 to +20.

**At the real parameters.**
- The score uses every prime to 10^8, so ln P ≈ 10^8.
- The primes in (463, 2,000] alone give ln P ≈ 1,500 nats: the "deficit of 900–1,500 nats" of `../batching.md`.
- No window of e^16.6 comes near it.

**The representation technique.**
- In subset-sum it gains because a solution has many representations as a sum of two half-weight vectors. A constraint mod R can
  then filter the lists and still keep one representation.
- Here the score Σ w_i(x_i) has arbitrary per-coordinate tables. A representation x_i = y_i + z_i (mod s_i) does not split w_i,
  so a partial vector that is not supported on its own coordinates cannot be scored or pruned.
- The only representations that keep the score separable are the coordinate splits, one per solution. With one representation,
  a filter mod R keeps a share 1/R of the solutions, so there is nothing to gain and the technique is the MITM measured above.
- A gain would need weight tables with additive structure (w_i(y + z) bounded by functions of y and z). The real tables are counts
  of rows in classes, with no such structure (§8 of `../README.md`).

## Files

- `toy.py`: the weight tables and the scan.
- `measure.py` → `measure.out`: the four classes, exact counts.
- `mitm_run.py` → `mitm_run.out`: the matching run for real and checked.
