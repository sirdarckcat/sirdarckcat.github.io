# Outside review, 25 November 2026: the consultant's map, the spy's list, and the ways out

Written by a reviewer session with no part in the campaign, at the user's request: check the consultant's map, check the
spy session's recommendations, and find a way out of the "local minimum". Everything here was read from the team's
branches and transcripts on 25 Nov between 11:50 and 14:00 UTC and recomputed where a number carries weight. Working
notes and scripts of the checks are listed in section 9. Nothing in any other branch was changed.

How it was checked: 22 reader agents mapped every branch and four session transcripts; each spy recommendation was
verified against the production code and logs, and every "gain still available" verdict was attacked by a second agent;
the consultant's proof had three independent referees and an adjudicator; the barrier was audited from four lenses, each
followed by a skeptic. Figures marked (mine) I computed myself.

## 1. The verdict

1. **It is not a local minimum.** The team is at the optimum of its method, and the method has a ceiling. Nothing found
   in four independent audits moves the 200-digit record by more than a few tenths of a nat without new mathematics.
2. **The 10% target at 200 digits is 7.8 nats away** (a factor 2,340 in work on the 7,000 units left). Every exit that
   exists inside known mathematics is priced in section 6; the largest is compute, at one nat per factor e.
3. **"10% to 50%" is reachable today, at other sizes.** With the units that remain the method reaches 10% up to about
   165 digits, 25% up to about 71 and 50% up to about 36. The scoreboard has those lines at 63, 46 and 25 digits. The
   stretch from 63 to 150 digits is empty and cheap.
4. **10% of the ceiling is (ln N)².** 213,070 / (ln 10^200)² = 1.005 (mine), and the largest cover prime, 463, is ln N.
   The target is "a desert longer than (ln N)²", which the method has crossed up to 63 digits and can cross up to about
   160 now.
5. **The new mathematics the user asked for exists, in a place the 200-digit scoreboard cannot see.** The consultant's
   lower bound for the cover depth is correct, elementary and apparently new (section 3).
6. **The spy's engineering list is almost entirely already done.** It read the lead's transcript and never the
   repository. Its three top items were deployed or measured and rejected days ago (section 4).

## 2. What the user asked for, and what the team is doing

The user's own words, from the lead's transcript (times UTC):

| when | words |
|---|---|
| before 22 Nov | "goal: maximize g(N) within N<1e200 (maximize closeness % within that class). That's the primary game now." |
| before 22 Nov | "The research delegate should focus more on ideating a stronger theoretical approach ... Discover new math. Find unexpected paths to the solution." |
| 22 Nov 21:44 | "CPUs can go to 21 digits if necessary to obtain empirical data to reach 10%-50% on 200 digits. Goal is significantly higher progress on the 200 digits domain, no baby steps. GIANT steps." |
| 23 Nov 09:40 | "No volunteer bs. We will discover new math. Let's see how far we can get with the current colab resources." (a reply to a message that priced scale at one to two million dollars) |
| to research | "prove nothing better exists, or find it" (as research quotes it); a standing goal "reach 10%" |
| 25 Nov 08:07 | "... what if we try to reach the problem from the other direction as well as minimize N for a given g(N)? Is the algorithm different?" |
| 25 Nov 10:48, to the spy | "... brainstorming new ideas that can help us get out of our local minima." |

Against that: the fleet's forecast is 7.5% → about 8.2% (a baby step by the user's definition); the research session's
README says no method was found and "Nothing here proves that no algorithm exists"; since 24 Nov the theory effort went
into the limit of D(n), where four successive claims were relayed to the user and withdrawn within 18 hours; and the
lead ended nearly every relay with "nothing changes at 200 digits". The lead never heard "10%" from the user (it came
through the research session), and it offered the long shot three times without an answer.

## 3. The consultant's map

**The proof (COHERENT_BLOCK.md): correct.** D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)², hence infinitely many even N with
g(N) ≥ c·ln N·(ln₂N)²·ln₄N/(ln₃N)².

- Two referees and I checked every step; one wrote the proof blind from the statement and reached the same order by the
  same route; one built the construction from the text and verified a complete cover by brute force at x = 2,000 and
  10,000.
- It is more elementary than it says: Brun–Titchmarsh is not needed (the inner count is of primes q < Q, at most π(Q)).
  The inputs are Chebyshev, Mertens, Rankin's trick and π(x) − π(x/4) ≫ x/ln x.
- Four one-line repairs: take the even solution N in [2P, 4P) (as written neither N − q > t nor ln N = (1 + o(1))x is
  shown); state that C₁ depends only on C₀ before c is fixed; replace "(ln x)^(3−o(1))" by the uniform inequality
  u₀ ln u₀ − u₀ ≥ 2 ln₂x; drop the remark that z ≥ (ln X)^(1+ε) is needed.
- Novelty: likely new, not deep. The one earlier lower bound found is W. Shi, arXiv:2605.21529, Theorem 6.22(iii),
  (1/2 + o(1))·log X·log log X by counting; Shi's Remark 6.24 poses the covering improvement as open. This answers it.
  MathSciNet and zbMATH were not searched.
- It says nothing below 10^200, as the note itself states.

**The numbers: they reproduce, with one caveat.** All 13 recorded outputs of `data/limit_check` reproduce byte for byte.
The block ratios 0.93 / 0.86 / 0.72 / 0.57 are the best of 50 common integers and the best z. Averaged over the common
integer in (Q, 2Q], which is what the proof uses, the block shows no gain at x = 10⁴ (1.01) or 10⁵ (0.99). GAPS_MAP.md
quotes the ratios without "best of 50".

**Fidelity: reliable on the 200-digit limits, stale elsewhere.** 27 boxes audited against primary sources. Floors,
ceiling, prizes, design menu and price list all match. Stale on 25 Nov: the two fixed-gap boxes still say "untested" and
hold none of 200,293, 206,593 or 216,289; the fleet box says 0.41 expected design hits where TALLY.md says 0.53; three
boxes still carry 1.1275 in the present tense; the header names a snapshot the commits contradict.

**Structure: what the map cannot ask.**

- One model prices everything: 72 of 187 boxes depend on H1 through one box, so no box can disagree with the 0.01%
  verdict.
- 70 boxes have no path to or from any record or forecast box, among them all of 25 Nov's new mathematics.
- There is no box for the goal, the budget or any decision. "Is this the right game" cannot be put to the map.
- The fixed-gap game, the only source of new records on 25 Nov, is a stale leaf that feeds nothing.
- The consultant's own lesson of 25 Nov (a count of typical covers is not the existence threshold once structured
  families exist) is not applied to the floor under every cover, which is exactly a count of typical covers.

## 4. The spy's recommendations

The spy read only the lead's transcript. Verified against code and logs:

| rank | recommendation | verdict | what is left (nats) |
|---|---|---|---|
| 1 | deepen the selection score | already done: the deep score has been production since 23 Nov 01:30; the ×1.97 it predicts is the gain banked that night | 0 to 0.08 |
| 2 | remove the +3.17 units/h premium | the discrepancy is real and was the fleet's own caveat; the "runtime shape" guess is contradicted by the scripts; a Colab-side repricing fits as well | 0 to 0.12 |
| 3 | Montgomery squaring bundle | already done: three of four parts are in the deployed kernel, the fourth is an older kernel measured 1.2 to 1.9 times slower | 0.01 to 0.03 |
| 4 | method-ceiling statement, restated objective | the analysis exists (README lines 1346–1356) with more precision than the spy's; what is missing is the sentence in the user-facing documents and the question to the user | 0 (a decision) |
| 5 | more modulus swaps | the one-slot version is deployed (491); this review ran the multi-slot version and it is flat; all six of the spy's sets are too short for the deployed loader | 0 to 0.015 |
| 6 | persistent work-queue kernel | built and A/B-tested three times on 23 Nov, 5 to 19% slower on the large cards | 0 to 0.007 |
| 7, 8 | cover supply; pair-correlation ranking | see section 9 (check finishing as this was written) | small |
| 9 | calibrate on small sizes | already done at least eight ways on five branches, to about 1% | 0 |

Total: at most about 0.2 to 0.3 nats, against the spy's own "×1.3 to ×2.4". The spy's bottom line survives and is the
part worth keeping: nothing on its list approaches 10%, and the scope question belongs to the user. Its figure "11% at
150 digits and 17% at 100 with the remaining units" checks (11.1% and 17.3% in the price list of section 6).

## 5. Why there is no way out inside the method

**Where every nat comes from (mine, on real primes).** Random nonzero classes on the 89 primes up to 463 leave 2,278 of
the 19,050 rows below 213,070: 54.6 expected prime rows, exactly the Hardy–Littlewood average 2·C₂·π(Q)/ln N. The best
cover leaves 1,609: 38.6. So all of covering is worth 16.0 nats, selection about 2, the budget about 31.3.

**The exchange rates.** A cover prime beyond 463 costs about 6.2 nats of N for 0.03 to 0.14 nats of luck. A factor e of
compute buys one nat. Nothing else in the project buys luck at all.

**Four audits, four skeptics, no loophole.**

| door | what the audit found | worth at most |
|---|---|---|
| better covers | measured floor 1,554 against 1,609 at 213,070 (two methods agree); certified floor 777 | 1.3 nats measured |
| engineering (sieve depth, keep fraction, kernel) | the deployed point is within 1% of the optimum of its own cost model | 0.3 |
| a cheaper compositeness test (H2 false) | even a free, perfect test leaves the sieve as the floor | 2.5 |
| locating good N beyond the Chinese-remainder line (P′) | every pair-merging method pays its constraint out of the same 460.5 nats; and what it outputs are isolated N, which lose the amortised sieve and the selection, 4 to 7 nats per candidate. So (P′) as posed (depth 1,000, prize 3.5 nats) would not pay even if solved; the depth that pays is nearer 20,000 | 0 net today |
| algebraic families (S-units, Lucas, common integer, sparse N, shared stretches) | all negative; a common integer leaves 2,129 rows at best, 1,954 after re-optimising 20 primes | negative |
| compute | one nat per factor e | 2.3 per ×10 |

10% needs 7.8. The first four doors together do not reach it even if every one opened, and two of them are open
problems. The record prime-gap community, with the same cover-sieve-luck method and twenty years, sits near 8% of its
own ceiling at 200 digits (research's note of 22 Nov; I did not verify the figure).

One refinement the audit adds to the research README: its prize table counts each ideal candidate as a full-weight
member with the deep sieve behind it. Candidates selected on primes beyond the line cannot share those residues across a
progression, so the table should be read net of 4 to 7 nats.

## 6. The ways out, with prices

All figures from the team's own models, re-implemented and checked against the team's numbers (forecast 176,200 against
the team's 175,000–176,000; 11.1% and 17.3% against "11%" and "17%"; CPU-hours per hit at 300 / 350 / 400 digits 83 /
2.6 / 0.23 against 78 / 2.7 / 0.24).

**A. Keep 200 digits, keep the method.**

| compute | expected record | closeness |
|---|---|---|
| the 7,000 units left | 176,200 | 8.3% |
| ×10 (about $7,000 at list price) | 187,400 | 8.8% |
| ×100 | 198,900 | 9.3% |
| ×1,000 | 210,700 | 9.9% |
| ×2,340 (about $1.7 million) | 213,070 | 10% |

25% costs ×10^32 and 50% costs ×10^78. Even a perfect search over everything the fleet's sieve sees ends near 16%.

**B. Keep the closeness, move the size.** With 7,000 units, one expected success:

| line | reachable now | on the scoreboard | cost of the first step |
|---|---|---|---|
| closeness ≥ 10% | 165 digits | 63 digits | 150 digits: about 190 units, 2.7% of the budget; 100 digits: minutes of one card or about a CPU-day |
| g > (ln N)² | 160 digits | 63 digits | 150 digits: about 900 units |
| closeness ≥ 25% | 71 digits | 46 digits | |
| closeness ≥ 50% | 36 digits | 25 digits | |

At a fixed budget, closeness × digits is nearly constant (about 16 to 18), so the user's band of 10% to 50% lives
between 36 and 165 digits. One more digit of N at 10% costs a factor 1.25.

*Tried, to see whether the table is real.* With the team's own tools (uarch's CPU scanner, a tempering cover on 49
moduli, 407 rows) on three cores of the reviewer's container:

| digits | g(N) | closeness | g / (ln N)² | members sieved | time |
|---|---|---|---|---|---|
| 100 | 47,881 | 10.3% | 0.90 | 432 million | 12 minutes, 18 CPU-minutes |

N = 8223574663857043817842483455238569126110624927813137471170822278151226773853347935411335888798540538. Checked
from N alone twice (the agent's script and mine, `demo/verify_g.py`): N − q fails a base-2 Fermat test for every odd
prime q < 47,881, and N − 47,881 is a strong probable prime to 16 bases (not a proved prime). It is a demonstration
point, not an entry on the team's scoreboard: the largest N there with closeness of 10% or more has 63 digits.

**C. Keep the gap, move the size (the user's other direction).** A gap of 200,000 needs about 230 digits on the 7,000
units, 244 on one fleet-day, 300 on four cores for a day; 213,070 needs 244 on the 7,000 units. This is the same curve
as A and B read along another axis.

**D. New mathematics for 200 digits.** Three named problems, none with a known approach: a decoder for noisy Chinese
remaindering with dense lists that outputs progressions, to depth 20,000 or beyond; a compositeness test cheaper than
one exponentiation (capped at 2.5 nats); a certificate of compositeness that is neither a small factor nor luck (the
integer counterpart of the function-field parity theorem). The miniature (X = 10⁹, Q = 1,000, ideal order wins by 229)
is the test bench for the first.

**E. New mathematics that is already in hand.** The Erdős–Rankin bound for the least Goldbach prime, with its Lean
corollary; D(n) exact to n = 35 (not in OEIS); the counting law for covers derived from Hardy–Littlewood with nothing
fitted; Stickelberger–Swan in Lean. The natural next theorem is the Ford–Green–Konyagin–Maynard–Tao analogue; one
referee sees a specific obstacle (the survivors are pairs of primes), so it is a research question, not a write-up.

A, B and C are decisions for the user. D is a bet with no odds. E is finished work waiting to be claimed.

## 7. Things to watch

- **Design-level hits arrive late in the fixed-gap runs.** From the survivor counts: 400 digits, 2 found against 6.8
  expected (first after about 6.5); 350 digits, 0 against 1.75; 347 digits, 1 at 0.37; 2,196 digits, 1 where 3.2 were
  expected. Four hits against about 12 expected is a 0.7% event (mine, rough). Lower targets on the same covers match
  (329 of 355, 6 of 6.0, 10 of 9.0), and the 200-digit tally matches (9 against 10.3). Each case was booked as luck.
  Pooling the exposure of the 319- and 300-digit runs would settle it.
- **Context.** Research, Lean, uarch, the consultant and the Opus session were at 75 to 83% of their windows this
  morning; one showed "disconnected" and one "safety-stopped" while receiving work. There is no single page with the
  goal, the decisions taken and the units ledger; I rebuilt the goal from two of the lead's compaction summaries.
- **Budget convention.** 7,000 units at the fleet's logged rate are e^31.3 full-weight members; the README's e^30.75 is
  about 4,100 units. Its two forecasts (172,000 and 175,000–176,000) differ for that reason only.

## 8. Questions put to the lead, and its reply

Twelve questions at 12:27 UTC and two more at 12:50, questions only. In short: which of "GIANT step" and "baby step" is
7.5% → 8.2%; where the 10% came from; what else "let's see how far we can get with the current colab resources" could
mean; what the "nothing changes" relays tell the user; who is working on (P′), H2 or the miniature today; what the new
mathematics has to be in one sentence; why the other direction paid in hours; what the prime-gap wall does to the
prior; what the surviving claims had in common; what survives a compaction; and what the smallest check of a relayed
number would be.

The lead's reply (12:31 UTC): it will put to the user, in one message, that the forecast is a baby step by the user's
own words, and ask which objective the remaining units should serve; a claim will reach the user only with a kernel
proof or an independent recomputation, or else labelled unverified in its first words; the "nothing changes" relays
stop; it will ask research who is on (P′), H2 and the miniature; it will not reinterpret the user's ruling on outside
hardware on its own; it will offer the user a one-page state file.

## 9. Sources of this review

Beside this file:

- `checks/consultant/`: the two proof referees, the literature search, the rerun of the scripts, the fidelity audit, the
  graph analysis, and `ADJUDICATION.md`.
- `checks/spy/`: one note per recommendation, with the lines of code and logs that decide it.
- `checks/barrier/`: the algorithmic audit and its skeptic, the families audit, the cost-floor audit, and
  `price_list.md` (every table of section 6, with its derivation and its checks against the team's figures).
- `demo/`: the demonstration points of section 6 B, each with N, a record file and a check from N alone;
  `verify_g.py` is the reviewer's own check in plain Python.

The 22 source maps (one per branch or transcript) and the scripts of the checks stayed in the reviewer's scratchpad.
The agents' notes are reproduced as written; where they cite scratchpad paths, those files are not in the repository.
