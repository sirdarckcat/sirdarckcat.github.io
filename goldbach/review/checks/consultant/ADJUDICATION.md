# Adjudication of the six referee reports on the consultant's map (25 Nov 2026)

An adjudicating agent read the six reports in this directory, went to the sources where two referees disagreed, and wrote the following. It is reproduced as returned.


## Status of the theorem

Proved at paper level. I read section 2 of COHERENT_BLOCK.md line by line myself and agree with both proof referees: every step holds, and the bound D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)² follows, as does "beats every constant times r·ln r".

What it rests on: Chebyshev, Mertens, π(x) − π(x/4) ≥ 0.7·x/ln x, and Rankin's trick. Brun–Titchmarsh (F2) is not needed, because the inner count in Step 1 (ii) is of primes q < Q and is at most π(Q).

Repairs, each one line, none needing a new idea:
- **Realisation by an integer:** take the even solution N in [2P, 4P), P the product of the odd primes up to x. As written ("N < 2∏t ... t < N − q") neither N − q > t nor ln N = (1 + o(1))x is shown, and q = 2 is not mentioned.
- **Quantifiers:** state that C₁ depends only on C₀, for every fixed c ≤ 1/8 and x ≥ x₀(c), before choosing c = 1/(8·C₁C₂).
- **Step 1 (i):** the "(ln x)^(3−o(1))" hides an o(1) of size 3·ln₄x/ln₃x. Referee A's uniform inequality u₀·ln u₀ − u₀ ≥ 2·ln₂x removes it; I checked it by hand (L − 3 ln L + 3 ln 3 − 3 ≥ 0, minimum 0 at L = 3).
- **(F4) remark:** the condition "z ≥ (ln X)^(1+ε)" is not what the derivation uses; it uses ln u/ln z → 0 and u/ln z → 0.

Limits of this verdict: no constant is computed, the threshold x₀ is unknown, and the result says nothing below 10^200. The only kernel-checked statement is the weaker every-constant form (CoverEveryConstant.lean, commit 1f1b090); I confirmed the file has no sorry, admit or axiom string, but nobody compiled it.

## Novelty

Likely new, and not deep. The search found one prior lower bound: W. Shi, arXiv:2605.21529, Theorem 6.22(iii), max p(n) ≥ (1/2 + o(1))·log X·log log X by counting. Shi's Remark 6.24 poses the covering improvement as open. I checked both quotes in the downloaded text, and the Granville–van de Lune–te Riele conjecture p(n) ≪ log² n·log log n (an upper-bound conjecture with no constant).

- **Lean theorem (every constant, earlier 1.349):** improves Shi's constant; modest.
- **Consultant's theorem:** improves the order by ln₂N·ln₄N/(ln₃N)², the exact Erdős–Rankin analogue. It answers Remark 6.24 and shows smooth numbers plus an average over the common integer suffice, without Ford–Green–Konyagin–Maynard–Tao machinery.

Caveats: this is absence of evidence. MathSciNet, zbMATH and the Russian literature were not searched, the adaptation is easy enough to exist as folklore, and Shi's preprint is unrefereed. The idea is credited in the note to the Lean session; the consultant's contribution is the averaging over N₁ and the write-up.

## The measured numbers

All 13 recorded outputs in data/limit_check reproduce byte-identically (numbers referee), and LIMIT_CHECK.md and COHERENT_BLOCK.md quote them without transcription error. Referee B reproduced the section 3.1 table from an independent script, and so did I at x = 10⁴.

My run (x = 10⁴, Q = 610,000, z = 80): minimum over N₁ = Q..Q+49 is 0.5192 at N₁ = 610031, mean 0.5597, maximum 0.6076; odd N₁ mean 0.5389, even 0.5805. Over 300 random N₁ in (Q, 2Q] the mean is 0.5815, which is 1.013 of the exact random product 0.5740.

What the numbers mean:
- **Block ratios 0.93 / 0.86 / 0.72 / 0.57:** these are best-of-50 N₁ and best-of-9 z against the Mertens approximation ln z/ln w. Against the exact product they are 0.904 / 0.854 / 0.708 / 0.567. The mean over the 50 N₁ is about 0.975 / 0.94 / 0.84 / 0.71, and over the whole (Q, 2Q], which is what the proof averages, 1.01 at 10⁴ and 0.99 at 10⁵. At x = 10⁴ the gain is the choice of N₁ only; the trend with x holds for the mean from about 10⁵.
- **Greedy plateau 0.72:** robust for x ≥ 10⁴. At x ≤ 2,000 greedy completion is not monotone in Q, so the bisected values carry about 3%.
- **"No complete cover for y = 3x/4":** means none at 0.30·x·ln² x or above, the bisection's starting point.
- **"Accurate to about 10%" and "12 to 18% weaker":** two different comparisons; the second is the end-to-end one.

Not recomputed by anyone: the Lean session's asymptotic table (0.98 down to 0.07) and the Poisson model's validity.

## How far the map can be trusted

Reliable as a transcription of the 200-digit campaign's limits; not reliable for the fixed-gap game, the fleet tally, or the status of anything written on 25 Nov.

- **Campaign limits (trust):** the floors 1,214 and 1,554–1,596, the certified 777, the ceiling 2,130,704, the prizes, the design menu and the price list all match their sources with correct labels (fidelity referee, 27 boxes audited by text).
- **Fixed-gap game (do not use):** I confirmed that e_dual carries the chips "prediction", "untested" and e_dualcpu "costed, not run", and that 200,293, 206,593 and 216,289 occur in no box. The research README has had these three records since 09:37–11:46, two of them Lean-certified, with pricing corrected by a factor of 2 to 4.
- **Fleet:** the map says 0.41 expected design hits (P(0) = 66%); TALLY.md of 10:25 says 0.53 and 0.59.
- **Limit of D(n):** m_thm1 still says "the research session conjectures D(n) ≈ 1.1275 · r ln² r"; m_lower, m_errata and one edge carry the second withdrawn order.
- **Status labels:** d_limit says "The proved window"; both ends are paper or draft proofs. The header says the snapshot is of 09:00 at research commit 48c73de while the commit message claims 921555c, so a reader cannot tell which boxes are current.
- **Planning figures:** 175,000–176,000 and "below 0.01%" are seven-GPU figures from a model nobody has rerun; the fleet runs five.

The pattern: on 25 Nov the consultant updated the boxes tied to its own new mathematics and left the rest at the morning snapshot. The QA pass checks boxes against ledgers at one commit, so it cannot catch staleness. The structure counts I recomputed match the structure referee (72 boxes depend on H1; m_ceiling's ancestry is four boxes).

## What the structure of the map shows

- One model prices everything. Every forecast box (ceiling, price list, portfolio, design menu, rows above the design level) descends from m_density on H1; I recomputed 72 dependents of H1 and 55 of m_density. No box on the map can disagree with the 0.01% verdict, because all of them inherit the same formula.
- Evidence and present facts are not premises. The tests of H1 (t_calib, t_joint, t_tail), the standing record and the fleet's state (e_fleetnow) are drawn as sinks pointing at the claims. The forecasts do not depend on the current budget, rate or observed hit counts.
- One edge type. Tests, contradictions ("3.7x faster than priced"), supersessions and provenance are all drawn as "relies on". The evidence lens colours a box by its own kind, not by its weakest premise, so the 0.01% figure has the colour of a measurement.
- No box for the goal or the choices. "Goal", "decision", "recommend", "priority", "why 200" occur in no box. Nothing records who chose 200 digits or 10% of a modelled ceiling, the stopping rule, or the budget as an object. The question "is this the right game" cannot be put to the map.
- The work that is producing results is thinnest. The last two records were near-misses of a 170,000 design; that mechanism has one box with two dependants. The fixed-gap game produced the only new records of 25 Nov and sits as a stale leaf feeding nothing.
- The newest effort is where the record does not depend on it. 31 of 51 new boxes are cover-depth theory, 15 of those have no path to or from any record or forecast box, and all of the consultant's 25 Nov mathematics is among them. Only 20 boxes are labelled "aside" where 70 are disconnected.
- The typical-versus-existence lesson is not applied to door 1. The consultant wrote that a count of typical covers and the existence threshold differ once structured families exist. The measured floor (1,214) is exactly a count of typical covers, and the map does not carry the lesson over to it.
- Low hit counts at the top targets have no box. The research README reports 2 found against 6.8 expected at 400 digits and 0 against 1.75 on the first 350-digit progression; the fleet has 0 against 0.53. Smaller targets on the same cover match (329 of 355, 6 of 6.0, 10 of 9.0). I did not test this; if real, it makes the forecast more negative.

## Corrections for the consultant

- COHERENT_BLOCK.md section 2, closing paragraph ("N < 2∏t, ln N = (1 + o(1))x ... t < N − q"): take the even solution N in [2P, 4P), P the product of the odd primes up to x, and add that N − 2 is even and above 2. As written N − q > t is not shown.
- COHERENT_BLOCK.md Step 1 (ii) and section 4 ("it needs the smooth-number estimate and Brun–Titchmarsh"): drop (F2). The inner count is at most π(Q) by (F1), so the proof is elementary and the Lean obstacle is overstated.
- COHERENT_BLOCK.md section 2 ("c fixed at the end", "c = 1/(8·C₁C₂)"): state that C₁ depends only on C₀, for every c ≤ 1/8 and x ≥ x₀(c). Replace the checks-paragraph remark on "z ≥ (ln X)^(1+ε)" by the conditions actually used (ln u/ln z → 0, u/ln z → 0).
- COHERENT_BLOCK.md section 3.1 table: report mean and minimum over N₁ separately, by parity, and over (Q, 2Q]; use the exact product ∏(1 − 1/(t − 1)) (0.574, 0.507, 0.413, 0.3735) as the random column. Say that at x = 10⁴ the gain is the choice of N₁ (odd, no small prime factor, near Q).
- GAPS_MAP.md section 10 ("I checked it on real primes (0.93, 0.86, 0.72, 0.57 of the random count ...)") and LIMIT_CHECK.md line 23: add "best of 50 N₁"; a typical N₁ shows no gain at x = 10⁴.
- COHERENT_BLOCK.md section 3.2 ("no complete cover for y = 3x/4 at any z tried"): write "none at 0.30·x·ln² x or above". LIMIT_CHECK.md 3.1 ("bisection to 1%"): add that completion is not monotone in Q, about 3% at x ≤ 2,000.
- COHERENT_BLOCK.md: add a prior-work paragraph (Shi arXiv:2605.21529 Theorem 6.22 and Remark 6.24; Granville–van de Lune–te Riele 1989; Rankin 1938 and the later gap papers). Shi is cited in the map's ledgers but not next to the theorem.
- ledger_thesis.md, entries lower_bound_thm and sandwich_open: mark superseded. The bound log N·log₂N·log₄N/log₃N they record as the rigorous frontier is below Shi's counting bound.
- Boxes e_dual, e_dualcpu, the news line and GAPS_MAP.md lines 213–214: rewrite from research README lines 2348–2485. Add the records 200,293 and 206,593 (400 digits, Lean-certified) and 216,289 (347 digits), the factor 2 to 4, the binomial cut, 1,340 and 4,900 digits, and "230 digits" for the cost parity.
- Box e_fleetnow: 0.53 expected design hits and P(none) = 0.59 (TALLY.md, 10:25 UTC); near-misses 2.21 expected against 2 found.
- Boxes m_thm1, m_lower, m_errata and edge d_limit>m_thm1: remove the present-tense 1.1275 conjecture and the second withdrawn order; write "both withdrawn, order open".
- Box d_limit and GAPS_MAP.md section 10 ("The proved window", "a rigorous depth"): write "on paper" for the lower end and cite WP12 Theorem 2 (phd/wp12_prime_covering_grh_ledger.md, research README lines 1222–1229) for the upper end, which the research README itself calls "not written out here".
- Box d_block (chip "unformalised"): the every-constant corollary is Lean-proved since 1f1b090; the full order is paper only.
- Boxes m_portfolio, m_designmenu and GAPS_MAP.md: label 175,000–176,000 and "below 0.01%" as seven-GPU figures not recomputed for five; give one figure for the cost of 213,070 (50,749 fleet-days and 400,099 card-days come from different tables).
- Box m_floorpred: add that the recursion's floor is 4 to 14% low near the end of complete covers and 4 to 7% low at fixed-gap sizes. Box e_t5: update to 2,829 and 2,563 rows.
- GAPS_MAP.md header: the snapshot line says 09:00 at 48c73de while the commits claim 921555c. Stamp each box with the commit it was read at, or say which group is current.
- Map structure: type the edges (assumes, tested by, contradicts, supersedes, data from) and add an inherited-evidence lens, so that model outputs resting on H1 are not coloured as measurements.

## What the map implies for the goal

- The new theorem does not move the 200-digit game in either direction. It is asymptotic, it starts to pay only for moduli far beyond 10⁶ (the Lean session's table puts half the rows near 10²⁵), and block covers at x = 10⁴ reach 0.39–0.48·x·ln² x against 0.71 for greedy. It is a publishable by-product, not a way out.
- The negative verdict is a statement about one method: scoring members of covers one by one under the cost model. It reads "expected final record 175,000–176,000, chance of 213,070 below 0.01%, 5,600 times the budget". It is not a statement that the target numbers are rare; the map says about 10¹⁷⁵ of them exist and that the difficulty is entirely location.
- Premise 1, H1 and the cost model: firm. Tested within about 1% on exhaustive data near 10¹² to 10¹⁸, by hit counts at 400 digits (329 of 355, 6 of 6.0, 10 of 9.0) and consistent with the fleet tally. The one loose end is that counts at the highest targets run low; that would make the verdict harsher.
- Premise 2, the cover floor (door 1): medium. Two independent methods agree (tempering 1,214 and 1,554–1,596; the recursion 1,221 and 1,584), so typical covers are near their best. The rigorous backstop is 777 rows, which the map says "still allows about 11 nats"; the target is short by ln 5,600 = 8.6 nats. So the closure is a measurement of typical covers, and the 25 Nov episode is a worked example of structured covers that such a count does not see. Against that, exact D(n) to n = 35 matches the count, and no structured cover is competitive at these sizes.
- Premise 3, budget and rate: soft and stale. Seven-GPU figures, horizons that differ between tables, a price list the fleet beat by 3.7 times, and a fleet now at five cards. The errors run both ways and nobody has recomputed; the order of magnitude of the shortfall (thousands) is not at risk from this.
- Premise 4, no way to locate good N faster than scoring (H2 and the sublinear verdict): open, by the map's own label "none known, none ruled out". This is where the largest prize sits: an ideal search to depth 5,000 would reach 214,000 within the remaining budget. Several routes are ruled out with numbers; no lower bound exists.
- Premise 5, the framing: a choice, not a finding. The 10% target is a fraction of a heuristic median, and the 200-digit cap and the definition of success appear in no box. The fixed-gap game shows what a change of framing buys: g above 200,000 at 400 digits in under two CPU-hours, kernel-certified, the same day. The research README also notes that closeness to the ceiling is cheaper at smaller sizes.
- What a reader should conclude: within the current method the map's verdict is sound to the order of magnitude and more effort on cover depth will not change it. The verdict would change only through premise 4 (a way to locate), premise 2 (a structured cover far below the measured floor at 89 moduli), or premise 5 (a different question). The map shows nobody working on the first two, and the third is not represented.

## Where the referees disagreed

- Proof referees A and B: no disagreement on substance. Both say proved; both find the same four repairs. They differ on labels (A calls the Brun–Titchmarsh step and the CRT paragraph minor, B calls the first cosmetic) and on a detail of (F4): A says exp(−u ln u + u) is right as written, B says (1 + o(1))·u. A is right here, since the error is O(u/ln z) = o(1) in the exponent; B's version is also true. I side with both on the verdict after my own read.
- Severity of the best-of-50 selection in the 3.1 table: the numbers referee says major, referee B says minor. I ran it (x = 10⁴: best 0.519, mean near Q 0.560, mean over (Q, 2Q] 0.5815 against exact random 0.574). Decision: minor for the table, whose caption says "the best of 50", and it affects no decision. It should be corrected where the qualifier is dropped (GAPS_MAP.md section 10, LIMIT_CHECK.md line 23), because there it reads as a check of the mechanism, and at x = 10⁴ it is not one.
- Fidelity referee against the source on the upper window: the referee says r^(4+ε) "has no source outside COHERENT_BLOCK.md". That is wrong. It is WP12 Theorem 2 (ledger_phd.md wp12-thm2, pointing to phd/wp12_prime_covering_grh_ledger.md section 2) and research README lines 1222–1229. The referee's underlying point stands in weaker form: the README says the argument is "standard sieve theory, not written out here", so "proved window" overstates the status at both ends.
- Fidelity referee against the proof referees on d_limit's "rigorous": no real conflict. The fidelity referee objects to the label on a same-hour, single-author proof; three referees and I have now read the proof and found it correct. The label should be "proved on paper, read by outside referees on 25 Nov", not "unrefereed" and not "proved" without qualification.
- Whether the bound can be pushed (referee A against referee B and the literature referee): A lists the Ford–Green–Konyagin–Maynard–Tao gain of ln₂x as unexamined; the literature referee names it as the natural next step; B argues there is no unconditional route, because the survivors are pairs (q prime, (N₁ − q)/a prime) and the sieve weights give O(1) per top prime after averaging over N₁. None of this is worked out. I find B's obstacle specific and credible, and leave it open; it has no bearing on the 200-digit goal.
- Literature referee against referees A and B on the inputs: the literature referee's summary lists Brun–Titchmarsh among the proof's inputs, following the note. A and B show it is unnecessary; I checked and agree.
