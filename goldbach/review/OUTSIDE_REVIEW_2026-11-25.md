# Outside review of the Goldbach desert work, 25 and 26 November 2026

I was brought in from outside on 25 November, while the search was running, with three tasks from the user: check the
map of all the team's results that the consultant session had drawn, check the list of suggestions written by the
"spy" session, and help the team out of what the user called a local minimum. I could also put questions to the lead
session, as long as they were questions and feedback rather than instructions.

Part 1 tells the story in plain language, for a reader without a mathematics degree. Part 2 is the review as I wrote
it for the team on 25 November between 11:50 and 14:00 UTC, with its numbers, plus a last section (10) on what
happened afterwards, added on the morning of the 26th. The notes of every check are in `checks/` next to this file.
I changed nothing on any other branch.

---

# Part 1. In plain words

## The problem

Take an even number, say 100, and look for the smallest prime p such that 100 − p is also prime. 100 − 2 = 98 is not
prime, 100 − 3 = 97 is, so the answer for 100 is 3. Write g(N) for that answer. Goldbach's famous conjecture, which
nobody has proved, says that there is always an answer. For almost every even number the answer is small, but now and
then an even number has to go a long way before it finds a prime p with N − p also prime. The team calls such a number
a desert. The question was: among the even numbers below 10^200 (numbers with up to 200 digits), how large can g(N)
be made?

Nobody knows the true maximum. A probability model, which the team tested against every even number up to 10^12 and
against hundreds of millions of samples near 10^18, says the largest g below 10^200 should be about 2.13 million. The
team measures its records against that "ceiling". When I arrived the record was g = 160,357, which is 7.5% of the
ceiling. The user had asked for 10% and more, and later put it this way: a dream of 2 million, a hope of 1 million,
an expectation of 200,000.

## How the search works

Nobody can try 10^200 numbers, so the team builds its candidates in two steps.

The first step is called a cover. For each of the first 89 small primes (3, 5, 7 and so on, up to about 490) the team
chooses the remainder that N should leave when divided by that prime. The choices are made so that, for most primes q
below the target, N − q is automatically divisible by one of those 89 primes and therefore cannot be prime. For a
target of 170,000 there are about 15,500 primes q to deal with, and a good cover takes care of all but about 1,250 of
them. Fixing those 89 remainders uses up almost the whole 200-digit budget: the product of the 89 primes has about 193
digits, so each cover leaves only about 20 million numbers below 10^200 to choose from.

The second step is luck. Each of the roughly 1,250 numbers N − q that the cover did not handle has to turn out to be
composite on its own. Each of them is prime with a chance of about 2.4%, so the chance that all 1,250 are composite is
about one in 15 trillion. The team's GPUs filter the candidates cheaply, throw away those with poor prospects, and test
the promising ones properly. By 25 November they had looked at about 48 trillion candidates for the 170,000 target.

The difficulty is that every step up costs a fixed multiple. Raising the target by 1,000 adds a few more numbers that
must be composite by luck, which makes the search about 22% more expensive. That compounds quickly. Going from the
expected final result of about 176,000 to the user's expectation of 200,000 multiplies the work by roughly 130 to 190,
and reaching 10% of the ceiling (213,070) multiplies it by roughly 2,400 to 3,400. The team had about 7,000 Colab
compute units left, about ten days of its five GPUs.

## What I found

**The consultant's map is accurate where it matters.** Its numbers on the limits of the 200-digit search match the
team's own primary sources. Some boxes were out of date by the afternoon of the 25th, and the map has no place for the
goal or for the decisions being taken, so it cannot help anyone ask whether the team is playing the right game. The
consultant also wrote a new mathematical proof that day: a lower bound on how long these deserts must get, for
infinitely many even numbers. Three independent checkers and I went through it line by line. It is correct, it needs
less than its author thought, and as far as we could find it is new. It does not help the 200-digit search, because
it only starts to matter for numbers far beyond 10^200.

**The spy's suggestions were mostly done already.** The spy had read only the lead's conversation, never the code. Its
three best ideas (a sharper filter, a cheaper way to square large numbers, a way to keep the GPUs fuller) were already
running in production, or had been built, measured and dropped days earlier. Everything left on its list adds up to a
few percent at best, against a need of hundreds or thousands of times.

**There was no hidden way out.** In my reading the team was not stuck in a local minimum in the usual sense. It sat at
the best point of its method, and the method has a ceiling. Four independent audits looked for a loophole from four
directions (cleverer search algorithms, other kinds of constructions, cheaper primality tests, and the price of every
exit), and each was followed by a sceptic whose job was to knock down whatever the first one claimed. None found a
way to the target. The reason is easy to state. The 200 digits are a fixed budget, the cover already spends almost all
of it in the most efficient way anyone knows, and everything else has to come from luck, which costs the same however
it is organised. According to the research session, the people who hunt record gaps between primes, using the same
cover-and-luck method for twenty years on a closely related problem, also stop near 8% of their own ceiling at 200
digits.

So the honest ways out were much more computing, a different question, or genuinely new mathematics, for which nobody
had a lead. I put the price of each in front of the lead and sent it fourteen questions instead of instructions. The
lead changed how it worked: it put the choice of objective to the user directly, it recomputed numbers before passing
them on, and it labelled anything unchecked as unchecked.

One of the different questions turned out to be cheap: the same 10% closeness at a smaller size. To make sure that was
real and not only a model, I ran the team's own CPU tools for an hour. They found a 100-digit number with g = 47,881,
which is 10.3% of the ceiling for numbers of that size. Until then the largest number known at 10% or more had 63
digits.

## What the user decided, and what happened next

At 15:25 UTC on the 25th the user settled the question of scope: "My ultimate goal is to get the largest least goldbach
summand under 200 digits. A dream? 2 million. A hope? 1 million. My expectation? 200k." Eight minutes later: "Your only
shot is better maths. Do better maths then." So the cheaper sizes became side results, run only on idle CPU cores.

That evening and night the team did what the questions had pointed at. Ideas that had been ruled out on paper were
run for real on a small exact model (every even number below 10^9, where the full truth is known): eleven approaches
in all, four older ones such as meet-in-the-middle searches, list merges and lattice decoding, and seven new ones from
outside the team's usual framework. According to the sessions that ran them, none did better than plain cover and luck
for the same amount of work. The research session then started a programme the user suggested at 22:20 UTC: build a
library of ideas on toy versions of the problem (polynomials over finite fields, groups) and try to carry over what
works to whole numbers. By 04:00 UTC on the 26th at least six of its nine lines of attack had reported, none with a
substitute for cover and luck, and several earlier claims had been corrected on the way.

Meanwhile the probability model held up wherever it could be tested with enough hits: 173 hits found against 175
expected at 100 and 150 digits, and overnight, on the two large GPUs at 200 digits, 5 near-records above 140,000
against about 6.3 expected. The 200-digit record stayed at 160,357. The cheap side lines moved: numbers at 10% of their
own ceiling now reach 110 digits, at 25% 48 digits, and at 50% 27 digits. I rechecked those three numbers myself from
scratch.

On the morning of 26 November the user stopped all sessions and asked for the work to be submitted.

## Is this a theoretical limit?

At 22:15 UTC on the 25th the user asked whether the team was getting close to a theoretical limit. Two arguments had
been put to the user. One: finding these numbers faster than by sieving is like finding values of a polynomial with
unusually many small prime factors faster than by sieving, which is the step of the best factoring algorithm (the
number field sieve) where forty years of work have produced better sieves and nothing fundamentally cheaper. Two: a
family of numbers that forced N − q to be composite by anything other than divisibility would contradict a standard
conjecture about primes in polynomial families (the Bateman–Horn conjecture).

My answer, from outside: partly. Both arguments are good evidence and they agree with everything the audits found, but
neither is a proof. The first compares two problems; nobody has shown that a fast method for one would give a fast
method for the other. The second is about families of numbers given by a formula, and about what happens for all
members of such a family, while a search needs only one lucky number. What has actually been proved, partly with a
computer proof checker, is a set of limits on particular kinds of method: methods that only test candidates one at a
time, methods built from lists of allowed remainders, and lattice methods within their known range. Overnight the
research session added that, in a simplified random model of the problem, a whole class of simple statistical tests
cannot tell a planted good candidate from noise. That is the kind of evidence people use for hard problems in
cryptography, but it is still about a model. What would settle the question is a proof that no method at all can do
much better than sieving here, and no one knows how to prove statements like that; they are not known even for
factoring. So the fair summary is that the team reached the edge of what known mathematics can do, and that the
problem looks as hard as problems people have worked on for decades, but nobody has shown it must stay that way.

## What is worth keeping

- The 200-digit record, g = 160,357, with a computer-checked proof.
- Records the other way round, the fewest digits for a given gap: for example a 347-digit number with g = 216,289, and
  a 1,797-digit number with no Goldbach partner below 1,021,897 (both computer-checked).
- New theorems. The lower bound above is proved on paper; the Lean session has a computer-checked version that is only
  slightly weaker: infinitely many even N whose smallest Goldbach prime exceeds about ln N·(ln ln N)², divided by a
  slowly growing correction. The only earlier bound we found grows like ln N·ln ln N.
- A cost model that predicts the search within a few percent wherever it has been tested.
- A careful record of what does not work and why (`checks/maps/RULED_OUT.md`), so that whoever picks this up does not
  repeat it.

## Some words used in Part 2

- **g(N)**: the smallest prime p for which N − p is prime.
- **ceiling**: the largest g the probability model expects among all numbers of a given size (about 2.13 million below
  10^200). **Closeness** is g divided by the ceiling at N's size.
- **cover** and **moduli**: the cover is the choice of remainders of N for the first small primes; the moduli are those
  primes.
- **rows**: the primes q below the target. A row is covered when N − q is divisible by a modulus; the others have to
  be composite by luck.
- **nat**: a unit of difficulty. One nat is a factor e ≈ 2.7 in the amount of work; 2.3 nats is a factor of 10, and
  7.8 nats a factor of about 2,400.
- **design hit, near-miss**: a candidate that reaches the target the search was designed for, or one that beats the
  record without reaching the target.
- **units**: Colab compute units, the money the GPUs were paid in.
- **the miniature**: the small exact model, every even number below 10^9 with a target of 1,000, where any idea can be
  checked against the whole truth in seconds.
- **H1, H2, P′**: H1 is the assumption that the rows left to luck behave independently (checked to about 1%); H2 the
  assumption that no compositeness test is much cheaper than one modular exponentiation (open); P′ the open problem of
  finding good candidates without scoring them one by one.
- **Lean, kernel**: Lean is a proof assistant; a kernel-checked statement has a proof that the computer has verified
  step by step.

---

# Part 2. The review in detail

Written for the team on 25 Nov between 11:50 and 14:00 UTC and updated on the morning of 26 Nov. Everything was read
from the team's branches and transcripts and recomputed where a number carries weight. How it was checked: 22 reader
agents mapped every branch and four session transcripts; each spy recommendation was verified against the production
code and logs, and every "gain still available" verdict was attacked by a second agent; the consultant's proof had
three independent referees and an adjudicator; the barrier was audited from four lenses, each followed by a sceptic.
Figures marked (mine) I computed myself.

## 1. The verdict

1. **It is not a local minimum.** The team is at the optimum of its method, and the method has a ceiling. Nothing found
   in four independent audits moves the 200-digit record by more than a few tenths of a nat without new mathematics.
2. **The 10% target at 200 digits is about 8 nats away** (7.8 to 8.1: a factor 2,400 to 3,400 in work on the 7,000
   units left, for a 63% chance). Every exit that exists inside known mathematics is priced in section 6; the largest
   is compute, at one nat per factor e.
3. **"10% to 50%" is reachable today, at other sizes.** With the units that remain the method reaches 10% up to about
   165 digits, 25% up to about 71 and 50% up to about 36. The scoreboard had those lines at 63, 46 and 25 digits. The
   stretch from 63 to 150 digits was empty and cheap. (At 15:25 on 25 Nov the user ruled this out as the goal; see
   section 10.)
4. **10% of the ceiling is (ln N)².** 213,070 / (ln 10^200)² = 1.005 (mine), and the largest cover prime, 463, is ln N.
   The target is "a desert longer than (ln N)²", which the method had crossed up to 63 digits and can cross up to about
   160 now.
5. **The new mathematics the user asked for exists, in a place the 200-digit scoreboard cannot see.** The consultant's
   lower bound for the cover depth is correct, elementary and apparently new (section 3).
6. **The spy's engineering list is almost entirely already done.** It read the lead's transcript and never the
   repository. Its three top items were deployed or measured and rejected days ago (section 4).

## 2. What the user asked for, and what the team was doing

The user's own words, from the lead's transcript (times UTC):

| when | words |
|---|---|
| before 22 Nov | "goal: maximize g(N) within N<1e200 (maximize closeness % within that class). That's the primary game now." |
| before 22 Nov | "The research delegate should focus more on ideating a stronger theoretical approach ... Discover new math. Find unexpected paths to the solution." |
| 22 Nov, to research | "... BRAINSTORM IDEAS WITH THE LEAN SESSION TO GET TO 10% AT LEAST AND THEN HILL CLIMB TO 20, 30, 40 AND 50%. I know you are stuck with your current way of thinking about the problem ..." |
| 22 Nov 21:44 | "CPUs can go to 21 digits if necessary to obtain empirical data to reach 10%-50% on 200 digits. Goal is significantly higher progress on the 200 digits domain, no baby steps. GIANT steps." |
| 23 Nov 09:40 | "No volunteer bs. We will discover new math. Let's see how far we can get with the current colab resources." (a reply to a message that priced scale at one to two million dollars) |
| to research | "prove nothing better exists, or find it" (as research quotes it); a standing goal "reach 10%" |
| 25 Nov 08:07 | "... what if we try to reach the problem from the other direction as well as minimize N for a given g(N)? Is the algorithm different?" |
| 25 Nov 10:48, to the spy | "... brainstorming new ideas that can help us get out of our local minima." |
| 25 Nov 15:25 (after this review) | "My ultimate goal is to get the largest least goldbach summand under 200 digits. A dream? 2 million. A hope? 1 million. My expectation? 200k. Approach this problem whatever way works. All my prompts have been to guide you towards that goal." |
| 25 Nov 15:33 | "Your only shot is better maths. Do better maths then." |
| 25 Nov 22:15 | (on two arguments relayed to the user, see Part 1) "Sounds like we are getting closer to a theoretical limit and equivalence of the problem to other harder problems. Is that so" |
| 25 Nov 22:20 | "could we start with a proof on smaller toy examples (like in groups or similar) which we know can't be transfered to integers but at least give us a library of tools and ideas, and then attempt to transfer what we can to integers and what we can't try to replace somehow with other fields" |
| 26 Nov 08:34 | stop all sessions and submit on PR #34, with documentation "readable for a person without a math degree" |

Against that, at the time of the review: the fleet's forecast was 7.5% → about 8.2% (a baby step by the user's
definition); the research session's README said no method was found and "Nothing here proves that no algorithm
exists"; since 24 Nov the theory effort had gone into the limit of D(n), where four successive claims were relayed to
the user and withdrawn within 18 hours; and the lead ended nearly every relay with "nothing changes at 200 digits".
The 10% is the user's own first milestone, said to the research session and set there as a standing goal; the lead
knew it only second-hand, and it had offered the long shot three times without an answer. Several "rules" the sessions
worked under were their own readings of short sentences: "never mention rental" (the user named volunteers), "small N
is closed" (the user allowed 21-digit experiments), "units, not a date".

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
- Since then (Lean branch, `CoverEveryConstant.lean` and `CoverCountAsymptotic.lean`): the Lean session proved in the
  kernel the same order short of the factor ln₄: for all large X some even N ≤ X has no Goldbach summand below
  ln X·(ln₂X)²/(150,000·(ln₃X)²), equivalently D(n) ≥ r·ln² r/(9,000·(ln₂ r)²). The files contain no `sorry`; I did
  not rebuild them.

**The numbers: they reproduce, with one caveat.** All 13 recorded outputs of `data/limit_check` reproduce byte for byte.
The block ratios 0.93 / 0.86 / 0.72 / 0.57 are the best of 50 common integers and the best z. Averaged over the common
integer in (Q, 2Q], which is what the proof uses, the block shows no gain at x = 10⁴ (1.01) or 10⁵ (0.99). GAPS_MAP.md
quotes the ratios without "best of 50".

**Fidelity: reliable on the 200-digit limits, stale elsewhere.** 27 boxes audited against primary sources. Floors,
ceiling, prizes, design menu and price list all match. Stale on 25 Nov: the two fixed-gap boxes still said "untested"
and held none of 200,293, 206,593 or 216,289; the fleet box said 0.41 expected design hits where TALLY.md said 0.53;
three boxes still carried 1.1275 in the present tense; the header named a snapshot the commits contradict.

**Structure: what the map cannot ask.**

- One model prices everything: 72 of 187 boxes depend on H1 through one box, so no box can disagree with the 0.01%
  verdict.
- 70 boxes have no path to or from any record or forecast box, among them all of 25 Nov's new mathematics.
- There is no box for the goal, the budget or any decision. "Is this the right game" cannot be put to the map.
- The fixed-gap game, the only source of new records on 25 Nov, was a stale leaf that fed nothing.
- The consultant's own lesson of 25 Nov (a count of typical covers is not the existence threshold once structured
  families exist) is not applied to the floor under every cover, which is exactly a count of typical covers.

## 4. The spy's recommendations

The spy read only the lead's transcript. Verified against code and logs:

| rank | recommendation | verdict | what is left (nats) |
|---|---|---|---|
| 1 | deepen the selection score | already done: the deep score has been production since 23 Nov 01:30; the ×1.97 it predicts is the gain banked that night | 0 to 0.08 |
| 2 | remove the +3.17 units/h premium | the discrepancy is real (28.3 against 25.1 units an hour) and was the fleet's own caveat, but there is nothing to remove: every runtime was created with the cheapest shape, and the premium arrived the evening Colab cut the caps. A Colab-side price change is the likeliest reading | 0 to 0.03 |
| 3 | Montgomery squaring bundle | already done: three of four parts are in the deployed kernel, the fourth is an older kernel measured 1.2 to 1.9 times slower | 0.01 to 0.03 |
| 4 | method-ceiling statement, restated objective | the analysis exists (README lines 1346–1356) with more precision than the spy's; what was missing was the sentence in the user-facing documents and the question to the user | 0 (a decision) |
| 5 | more modulus swaps | the one-slot version is deployed (491); this review ran the multi-slot version and it is flat; all six of the spy's sets are too short for the deployed loader | 0 to 0.015 |
| 6 | persistent work-queue kernel | built and A/B-tested three times on 23 Nov, 5 to 19% slower on the large cards | 0 to 0.007 |
| 7 | surrogate-guided cover supply | the supply "running out" is a counting fact the team had measured (about 30,000 covers at the first usable level, 12 times more per row), and the generator already enumerates each level best-first | 0 to 0.002 |
| 8 | rank vectors by the pair-correlation term | priced on 22 Nov by the two-session brainstorm at 0.0002 nats between covers of equal rows | 0 |
| 9 | calibrate on small sizes | already done at least eight ways on five branches, to about 1% | 0 |

Total: at most about 0.17 nats, against the spy's own "×1.3 to ×2.4" (0.3 to 0.9). The largest single item still open
was the team's own pending decision on the card mix (0.06 to 0.2 nats), which is not on the spy's list. One
neighbouring lever turned up in the check of rank 7: ordering the vector supply by research's weighted rows was 0.4 to
0.9 weighted rows better at equal supply in a test at 5,000 to 35,000 covers, where the cover README says it gives
nothing; at most 0.02 nats, and unconfirmed at the 3.7 million covers the fleet draws from. The spy's bottom line
survives and is the part worth keeping: nothing on its list approaches 10%, and the scope question belongs to the user.
Its figure "11% at 150 digits and 17% at 100 with the remaining units" checks (11.1% and 17.3% in the price list of
section 6).

## 5. Why there is no way out inside the method

**Where every nat comes from (mine, on real primes).** Random nonzero classes on the 89 primes up to 463 leave 2,278 of
the 19,050 rows below 213,070: 54.6 expected prime rows, exactly the Hardy–Littlewood average 2·C₂·π(Q)/ln N. The best
cover leaves 1,609: 38.6. So all of covering is worth 16.0 nats, selection about 2, the budget about 31.3.

**The exchange rates.** A cover prime beyond 463 costs about 6.2 nats of N for 0.03 to 0.14 nats of luck. A factor e of
compute buys one nat. Nothing else in the project buys luck at all.

**Four audits, four sceptics, no loophole.**

| door | what the audit found | worth at most |
|---|---|---|
| better covers | measured floor 1,554 against 1,609 at 213,070 (two methods agree); certified floor 777 | 1.3 nats measured |
| engineering (sieve depth, keep fraction, kernel) | the deployed point is within 1% of the optimum of its own cost model (two independent models). Unpriced: 88 moduli with long vectors and a deeper sieve, between −0.1 and +0.2 | 0.3 |
| a cheaper compositeness test (H2 false) | a test K times cheaper is worth 0.4 nats at K = 2, 1.2 at K = 10, 2.4 at K = 100. The deployed point costs 57 ns per full-weight member and 10% needs 0.026 ns, under half of one modular squaring | 2.4 at K = 100 |
| locating good N beyond the Chinese-remainder line (P′) | every pair-merging method pays its constraint out of the same 460.5 nats; and what it outputs are isolated N, which lose the amortised sieve and the selection, an estimated 4 to 7 nats per candidate (not measured). So (P′) as posed (depth 1,000, prize 3.5 nats) would not pay even if solved; the depth that pays is nearer 20,000 | 0 net today |
| algebraic families (S-units, Lucas, common integer, sparse N, shared stretches) | all negative; a common integer leaves 2,129 rows at best, 1,954 after re-optimising 20 primes | negative |
| covers on 90 or more primes | 0.135 nats a prime once the higher chance per row is charged; the lost sieve costs more (the team had already closed this) | 0 net |
| compute | one nat per factor e | 2.3 per ×10 |

10% needs about 8. Covers and engineering together hold at most 1.6. The test door closes the gap alone only with a
detector some 60,000 times cheaper than an exponentiation. The location door is negative at the depth the team posed
and has no known method at any depth. The record prime-gap community, with the same cover-sieve-luck method and twenty
years, sits near 8% of its own ceiling at 200 digits (research's note of 22 Nov; I did not verify the figure).

**No loophole found is not the same as closed.** The merged catalogue of everything the team has ruled out
(`checks/maps/RULED_OUT.md`, 100-odd entries, each with the strength of its ruling and its scope) showed which verdicts
rested on argument or cost arithmetic and had never been run:

- the cover floor is measured, not proved (certified 777 rows against 1,248); 13 of 92,160 frames were taken to the
  bottom; an exact method (integer programming on the last moduli) was called feasible and never done;
- lattice decoding, meet in the middle, the k-tree and hashing had been ruled out by arithmetic only. They were run as
  algorithms on the miniature that afternoon, after the questions of section 8: in 179 configurations none did better
  than cover-first for equal work (the Lean session's runs; not rerun by me);
- seven mechanisms outside the closure grammar were scored the same afternoon under a stricter rule the lead adopted
  (work counted in exponentiations, the sieve-then-test funnel as the baseline, an at-scale bound before anything is
  called a gain); all came out negative, the best at most +0.035 nats at 200 digits (the consultant's table);
- structured covers at 89 moduli were first measured on 25 Nov at 13:33 (1,342 to 1,449 rows against 1,248: worse);
- of the ways to share work between tests only one is disproved; two brainstorm ideas (Fermat along a progression, a
  group test for primality) were left unruled;
- two-stage selection was argued, not measured.

My audits priced most of these and found nothing; the catalogue is the list to work down if anyone wants each door
shut by measurement. `checks/maps/PREMISES.md` is the matching ledger of what the plan assumes.

One refinement the audit adds to the research README: its prize table counts each ideal candidate as a full-weight
member with the deep sieve behind it. Candidates selected on primes beyond the line cannot share those residues across a
progression, so the table should be read net of 4 to 7 nats.

## 6. The ways out, with prices

All figures from the team's own models, re-implemented and checked against the team's numbers (forecast 176,200 against
the team's 175,000–176,000; 11.1% and 17.3% against "11%" and "17%"; CPU-hours per hit at 300 / 350 / 400 digits 83 /
2.6 / 0.23 against 78 / 2.7 / 0.24).

**A. Keep 200 digits, keep the method.** This is the frame the user chose at 15:25 on 25 Nov.

| compute | expected record | closeness |
|---|---|---|
| the 7,000 units left | 176,200 | 8.3% |
| ×10 (about $7,000 at list price) | 187,400 | 8.8% |
| ×100 | 198,900 | 9.3% |
| ×130 to ×190 | 200,000 (the user's stated expectation) | 9.4% |
| ×1,000 | 210,700 | 9.9% |
| ×2,400 to ×3,400 (about $1.7 to 2.4 million) | 213,070 | 10%, a 63% chance |

25% costs about ×10^32 and 50% about ×10^78 (orders of magnitude: the hit model was then validated only up to the
170,000 level, 9 found against 10.3 expected). Even a perfect search over everything the fleet's sieve sees ends near
16%. Rented cards are cheaper than Colab's list price by a factor 1.3 at the median and 2 to 4 on interruptible
capacity; the user declined outside hardware on 23 Nov, and it would close at most one of the eight nats per factor e
of money. For 200,000 the research session gives the chance with all remaining units as 0.4%.

**B. Keep the closeness, move the size.** With 7,000 units, one expected success. Declined by the user as the goal; run
afterwards on idle CPU cores only (the last column, section 10).

| line | reachable now | on the scoreboard, 25 Nov morning | cost of the first step | held on 26 Nov |
|---|---|---|---|---|
| closeness ≥ 10% | 165 digits | 63 digits | 150 digits: about 190 units, 2.7% of the budget; 100 digits: minutes of one card or about a CPU-day | 110 digits |
| g > (ln N)² | 160 digits | 63 digits | 150 digits: about 900 units | 63 digits |
| closeness ≥ 25% | 71 digits | 46 digits | | 48 digits |
| closeness ≥ 50% | 36 digits | 25 digits | | 27 digits |

At a fixed budget, closeness × digits is nearly constant (about 16 to 18), so the user's band of 10% to 50% lives
between 36 and 165 digits. One more digit of N at 10% costs a factor 1.25.

*Tried, to see whether the table is real.* With the team's own tools (uarch's CPU scanner, a tempering cover on 49
moduli, 407 rows) on three cores of the reviewer's container:

| digits | g(N) | closeness | g / (ln N)² | members sieved | time |
|---|---|---|---|---|---|
| 100 | 47,881 | 10.3% | 0.90 | 432 million | 12 minutes, 18 CPU-minutes |

The scan found it after 1.7 times the model's expected number of members; the quantities that do not depend on luck
(rows alive after the sieve, the rate of probable primes, the hit mass kept by the cut, the cost per member) agree with
the model within 1 to 5%. A 110-digit scan (53 moduli, 494 rows, 2.46 billion members, 2 CPU-hours) ended at the
time limit with no hit where the model expected 1.21, a 30% event; both scans together are 1 found against 2.9
expected. 120 and 130 digits were priced, not run, at about 10 to 15 and 100 to 170 CPU-hours a hit
(`demo/SUMMARY.md`).

N = 8223574663857043817842483455238569126110624927813137471170822278151226773853347935411335888798540538. Checked
from N alone twice (the agent's script and mine, `demo/verify_g.py`): N − q fails a base-2 Fermat test for every odd
prime q < 47,881, and N − 47,881 is a strong probable prime to 16 bases (not a proved prime). It was a demonstration
point, not an entry on the team's scoreboard; the team later listed it as the first holder of the 10% line.

**C. Keep the gap, move the size (the user's other direction).** A gap of 200,000 needs about 230 digits on the 7,000
units, 244 on one fleet-day, 300 on four cores for a day; 213,070 needs 244 on the 7,000 units. This is the same curve
as A and B read along another axis.

**D. New mathematics for 200 digits.** Three named problems, none with a known approach: a decoder for noisy Chinese
remaindering with dense lists that outputs progressions, to depth 20,000 or beyond; a compositeness test far cheaper
than one exponentiation (1.2 nats at ten times cheaper, 2.4 at a hundred); a certificate of compositeness that is
neither a small factor nor luck (the integer counterpart of the function-field parity theorem). The miniature
(X = 10⁹, Q = 1,000, ideal order wins by 229) is the test bench for the first.

**E. New mathematics that is already in hand.** The Erdős–Rankin bound for the least Goldbach prime, with its Lean
version; D(n) exact to n = 35 (not in OEIS); the counting law for covers derived from Hardy–Littlewood with nothing
fitted; Stickelberger–Swan in Lean. The natural next theorem is the Ford–Green–Konyagin–Maynard–Tao analogue; one
referee sees a specific obstacle (the survivors are pairs of primes), so it is a research question, not a write-up.

A, B and C were decisions for the user. D is a bet with no odds. E is finished work waiting to be claimed. The user
chose A, with D as the only accepted way beyond it ("Your only shot is better maths").

## 7. Things to watch

- **Design-level hits arrived late in the fixed-gap runs.** From the survivor counts: 400 digits, 2 found against 6.8
  expected (first after about 6.5); 350 digits, 0 against 1.75; 347 digits, 1 at 0.37; 2,196 digits, 1 where 3.2 were
  expected; then 319 digits, 1 at about 0.2. Five hits against about 12 expected was about a 2% event by the research
  session's count. It has since been tested where counts are large, and the model holds: the calibration ladder at 100
  and 150 digits found 173 against 175.0 expected with no trend up to an exponent of 16 nats; the 10% line at 101 to
  120 digits found 17 against 19.9; and overnight the two large cards, logging near-records above 140,000 at 200
  digits, found 5 against about 6.3 expected (my sum of the fleet's hourly log, `calib_hourly.jsonl`). No correction
  to the model is needed.
- **Context.** Research, Lean, uarch, the consultant and the Opus session were at 75 to 83% of their windows on the
  morning of the 25th (research near 88% by the afternoon, after two compactions; it lost its own 22 Nov Erdős–Rankin
  proposal in a README rewrite). The spy saw one session "disconnected" and one "safety-stopped" at 09:15; both were
  answering again from 10:26. There was no single page with the goal, the decisions taken and the units ledger; the
  goal had to be rebuilt from compaction summaries of two sessions.
- **Budget convention.** 7,000 units at the fleet's logged rate are e^31.3 full-weight members; the README's e^30.75 is
  the 23 Nov figure (about 4,100 units at today's rate). Its two forecasts (172,000 and 175,000–176,000) differ for
  that reason only.

## 8. Questions put to the lead, and its reply

Twelve questions at 12:27 UTC and two more at 12:50, questions only. In short: which of "GIANT step" and "baby step" is
7.5% → 8.2%; where the 10% came from; what else "let's see how far we can get with the current colab resources" could
mean; what the "nothing changes" relays tell the user; who is working on (P′), H2 or the miniature today; what the new
mathematics has to be in one sentence; why the other direction paid in hours; what the prime-gap wall does to the
prior; what the surviving claims had in common; what survives a compaction; what the smallest check of a relayed
number would be; whether the lesson about typical covers applies to the cover floor; and whether the late fixed-gap
hits were luck or a model error.

The lead's reply (12:31 UTC): it would put to the user, in one message, that the forecast is a baby step by the user's
own words, and ask which objective the remaining units should serve; a claim would reach the user only with a kernel
proof or an independent recomputation, or else labelled unverified in its first words; the "nothing changes" relays
would stop; it would ask research who is on (P′), H2 and the miniature; it would not reinterpret the user's ruling on
outside hardware on its own; it would offer the user a one-page state file.

At 12:54 the lead asked research for a calibration ladder at 100 and 150 digits (uarch), for the four families ruled out
by arithmetic to be run as algorithms on the miniature (Lean), for at least five mechanisms outside the closure grammar
to be scored on the miniature (the consultant), and for a one-page note on H2 (delivered 13:37). Research ran the
block-cover test at 89 moduli that it had set aside at 11:50. Research's own words at that point: "Today no session I
work with has spent time on problem P′ ..., on H2 ..., or on a mechanism outside the grammar". Questions 7 (what the new
mathematics has to be, in one sentence) and 9 (the prime-gap wall) were not answered.

## 9. Sources of this review

Beside this file:

- `checks/consultant/`: the two proof referees, the literature search, the rerun of the scripts, the fidelity audit, the
  graph analysis, and `ADJUDICATION.md`.
- `checks/spy/`: one note per recommendation, with the lines of code and logs that decide it.
- `checks/barrier/`: the algorithmic audit and its sceptic, the families audit, the cost-floor audit, and
  `price_list.md` (every table of section 6, with its derivation and its checks against the team's figures).
- `checks/maps/`: `RULED_OUT.md` and `PREMISES.md`, the two technical syntheses of the 22 source maps.
- `demo/`: the demonstration point of section 6 B, with N, a record file and a check from N alone; `verify_g.py` is the
  reviewer's own check in plain Python, and `frontier_rechecks.txt` its output on the frontier numbers of section 10.

The source maps themselves (one per branch or transcript), a dossier of the user's statements and the scripts of the
checks stayed in the reviewer's scratchpad. The agents' notes are reproduced as written; where they cite scratchpad
paths, those files are not in the repository. Section 10 is taken from the lead's and research session's transcripts
and from the team's branches as of 26 Nov 08:45 UTC; the figures I checked myself are marked.

## 10. After the review: 25 Nov 14:00 to 26 Nov 08:40 UTC

- **The objective.** At 14:17 the lead set up a "closeness frontier" (the most digits at 10%, 25% and 50% of the
  ceiling) and put to the user the choice between the 200-digit record and closeness at about 150 digits. The user's
  answer at 15:25 and 15:33 is in section 2. The frontier lines then ran at the lowest priority on idle cores.
- **Prove or find.** By 14:57 eleven methods had been scored on the miniature (the four older families in 179
  configurations, and seven new mechanisms); none gained. The lead adopted the consultant's scoring rule for all such
  work. At 15:25 the lead asked research for one table of every remaining source of nats toward 200,000; the answers
  that came back were small: selection-aware covers at most +0.07 nats (the rows of every cover carry the same
  Hardy–Littlewood under-dispersion), and folding a 90th prime into the modulus +0.12 nats a prime, which research
  expected to be negative on the fleet as built because the window shrinks below what the sieve can amortise.
- **The fleet.** A carry-over change to the Fermat rounds failed its production A/B (−1.1% expected hits a second, where
  +2 to +5% had been predicted) and was withdrawn. From the evening of the 25th both large cards logged near-records
  above 140,000 as a calibration: 5 found (141,241; 146,701; 147,331; 151,057; 159,631) against about 6.3 expected, which is
  consistent with the model at 200 digits. The record stayed at 160,357.
- **The user's toy-model programme.** After the user's 22:20 suggestion the research session ran nine lines of attack
  on toy versions of the problem (class fields; algebraic groups and primality; the function-field dictionary; sieve
  theory and parity; Bohr sets and lattices; probability and complexity; harmonic analysis; a wild card; coding theory).
  By 03:33 six had reported, one had been stopped, and none had found a substitute for cover and luck. Corrections made
  on the way, all by the research session: Result 1's advantage over congruences in the function-field model was
  overstated (aligned congruences match it at a third of the degree); a free parity oracle for every surviving row
  would be worth only about 1.4 nats at the sieve depths in use, because among rough numbers an odd number of prime
  factors is almost a coin flip; the exact sieve count of all 21.4 million members of one window puts the single best
  member at +3.81 nats over the average if the sieve were free (not +4.10), and the window behaves like a random-energy
  model with no exploitable correlations; a low-degree lower bound was proved for a planted Gaussian model of the
  problem; and the predicted curve for list-merging methods peaks at two lists, about +0.13 nats for one number, far
  short at scale.
- **The side lines.** The 10% line reached 110 digits (g = 59,377, 10.54%), the 25% line 48 digits (g = 23,227,
  27.2%), the 50% line 27 digits (g = 11,467, 52.75%; the 25-, 26- and 27-digit numbers are kernel-certified). I
  rechecked all three from N alone with `demo/verify_g.py`: every N − q below g fails a base-2 Fermat test, and N − g is
  a strong probable prime to 16 bases. The first half of the 120-digit rung found nothing in 1.12 expected; the second
  half was lost when its container was recycled. In the fixed-gap game a 319-digit number with g = 207,307 was found and certified, and for a gap of
  1,000,000 the size came down from 2,196 to 1,997 and then to 1,797 digits (g ≥ 1,021,897, the negative side
  kernel-certified; N − g a strong probable prime).
- **The stop.** At 08:34 on 26 Nov the user stopped all sessions and asked for the work to be submitted on PR #34.
