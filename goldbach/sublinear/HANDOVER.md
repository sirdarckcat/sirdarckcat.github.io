# Handover: looking for a shortcut to numbers with no small Goldbach partner

Research session, 23 to 26 November 2026. Written for a curious reader without a mathematics degree. The full record,
with every number and where it came from, is `README.md` in this folder; this note is the map.

## The question, and why it matters for the record

Take an even number N. Goldbach's conjecture says it is a sum of two primes, so there is a smallest prime p for which
N − p is also prime. Call it the least Goldbach partner of N, g(N). For most numbers it is tiny. The project's game
is to find an even number with fewer than 200 digits whose least partner is as large as possible. When the work
stopped the record was g = 160,357, found by the GPU fleet on 24 November. A model of how primes behave (a
prediction, nothing proved) says the largest value to expect among numbers of that size is about 2,130,704, so the
record is 7.5% of that "ceiling". The user asked for 10% (213,070), said they expected about 200,000, and hoped for
more.

The search has two steps. First it fixes the remainder of N on division by every prime from 3 to 463, chosen so that
for as many primes q as possible N − q is divisible by one of those small primes and so cannot be prime. This choice
is called a cover. It uses up almost all the freedom a 200-digit number has: fixing the remainder for a prime r
divides the remaining choice by r, and the primes up to 463 multiply to about 10^193. The primes q below the target
that the cover does not take care of, about 1,500 of them for a target of 200,000, are called rows: for each row,
N − q must turn out to be composite by luck. Second, the search runs through the roughly 21 million numbers below
10^200 that share the cover (the members of its window), keeps the 1.5% in which the fewest rows survive division by
the primes up to 10^8 (the sieve), and tests those. Each row is prime with a chance of about one in forty,
independently of the others, so a member gets through all its rows with a chance of about e^−36.5, and the work still
available was about 250 times too little to expect one success at 200,000.

I measure such gaps in nats: the natural logarithm of a ratio of chances or of amounts of work. One nat is a factor
of e, about 2.72, and a factor of 250 is 5.5 nats. My job was to look for better mathematics: a way to find the rare
members with unusually few surviving rows without trying them one by one, or any mechanism other than a cover and
luck that makes many of the numbers N − q composite at once.

How results are marked below. Proved in Lean: a proof checked by the Lean proof assistant, in the Lean session's
library (folder `goldbach/lean/GoldbachGaps/` on its branch `ccr-36ca7b46-8twf14`). Proved on paper: a written proof,
with who has read it. Computed twice: two independently written programs agree. Computed once: one program, with
its own checks. Opinion: my reading.

## What was tried, by idea

*Better covers.* The covers the fleet uses turn out to be the best there are: thirteen families of covers were
searched to the bottom and the fleet's is the best, and a statistical count over all possible covers, run from two
different starting points, puts a floor under every cover within a row of the best one found (measured, not
certified: the floor that an exhaustive search certifies is far lower). A law for how many choices of remainders
strike every prime below a bound was found, and then derived from the Hardy–Littlewood count of prime pairs with
nothing fitted, within 6% of the measured values from 89 to 1,228 primes (computed by several programs). So better
covers cannot close the gap.

*Do the wanted numbers exist?* In abundance: about 10^175 even numbers below 10^200 have g of 213,070 or more (an
estimate from the standard model of the primes; the counting method was checked against an exact count of every even
number below 10^9, which two sessions did independently). They are simply not where any feasible search looks.

*Finding the good members without trying them all.* Each member has a score, the number of rows that survive the
sieve, and that score is a sum of separate contributions from the sieving primes. What ties the contributions
together is the size limit. We showed that "N is below 10^200" is exactly one condition: a fixed weighted sum of N's
remainders, taken as a fraction, must land in a short interval (proved in Lean, `Worlds/Arc.lean`). That turns the
search into a knapsack-like problem with a single constraint, and every known way to exploit such a problem was
priced on the real cover: lattice reduction, meeting in the middle with two sorted lists, decoding algorithms from
coding theory, dynamic programmes over partial sums, merging and trees of lists. Each amounts either to fixing more
remainders, which costs freedom, or to scanning. The best measured case: handling the condition exactly for seven
primes beyond the cover, the best number below 10^200 beats the best member of the cover's own window by one to four
rows (computed twice), less than a tenth of a nat, and it comes as a single number, where a scan of the same cost
keeps hundreds of thousands of good members. Even an oracle that handed over, free, the single best member of each
window would gain 3.81 nats, still short of 5.5 (the exact sieve counts of all 21 million members were computed by
three programs that agree; the 3.81 was computed once). The Opus session showed that for arbitrary score tables
(encoded by their two allowed residues at each distinct prime modulus) an algorithm whose cost is proportional to its
output would solve an NP-complete problem via an expected-polynomial-time randomized reduction, implying NP ⊆ ZPP / RP
— and deterministically NP-complete if prime-power/composite moduli are allowed or the primes are supplied (proof on
paper by that session, checked by its own computation, and qualified after PR #34 review) — so any shortcut has to use
something special
about these particular tables. Every test of their structure (additive, multiplicative, lattice, spectral,
statistical) found nothing usable; the one real regularity, that every row is one more than a multiple of 6, is worth
almost nothing (computed, mostly twice).

*Toy worlds.* At the user's suggestion we studied simpler worlds where such tools exist and asked what carries over.
In polynomials over a finite field, a mechanism that is neither a small factor nor luck exists: the parity of the
number of irreducible factors is fixed by a discriminant, so for well-chosen N whole families of the analogue of
N − q are forced to factor (proved in Lean, `FunctionField/ParityDesert.lean` and `Stickelberger.lean`). Targets
unchanged by a shift of the variable tie their rows together in groups that succeed or fail as one, so such a target
needs far fewer lucky outcomes, though only for complete degrees of rows (the identity proved in Lean,
`FunctionField/Families.lean`; the record values computed four times independently, the law for the saving twice).
In the Gaussian integers the same tie appears for targets on the axes and diagonals (computed twice). In coding
theory, decoding beyond the classical limit needs lists that link several positions, which a sum of independent
scores never gives (proved on paper by the Opus session and by one of my agents, refereed by a verifier). What the
ordinary integers keep is everything built on remainders and order: the cover, the one-condition programme,
counting. What they lose is everything built on a symmetry (the integers have no symmetry that respects addition
except changing the sign), on a derivative (any rule on the integers that behaves like a derivative is zero), or on a
kind of extension of the number system that the rationals provably lack (Minkowski's theorem).

*Replacements from other fields.* Nine independent lines of attack, one field of mathematics each (class field
theory, algebraic groups and primality testing, the function-field dictionary, sieve theory, lattices and additive
combinatorics, coding theory and cryptanalysis, probability and complexity, harmonic analysis, and a wild card),
each testing its proposals on real 200-digit numbers. Eight reported; the coding-theory one was stopped by a safety
filter and not retried. None found a substitute, and the verifiers meant to check them were stopped by a usage limit,
so these are computed once. Three findings stand out. A free test of the parity of the number of prime factors would
be worth at most 1.38 nats at the search's sieve depth (other models give 1.6 to 2.3), because among numbers with no
small factor it is then a fair coin (a law from sieve theory, checked on small numbers). No two rows are tied: over a
million pairs of rows of the real cover were tested, with joint primes at the rate of independence. And the window
behaves like independent random draws: the correlation of scores between any two members is at most 0.003 (computed
twice).

*By-products about the integers.* For every constant c and all large X, some even number up to X has no Goldbach
partner below c·ln X·ln ln X, where ln is the natural logarithm, and a stronger bound of the same kind holds too
(proved in Lean, `CoverBound.lean`, `Mertens.lean` and the files beside them; as statements probably not new, the
elementary proof and its machine check are). The exact reach of the first n odd primes with no luck at all (how far
they alone can strike every prime) is known for n up to 35 (computed twice to n = 15, once beyond, in Lean to n = 9).
In the reverse game, the fewest digits for a given gap, numbers with g = 216,289 at 347 digits and g = 1,021,897 at
1,797 digits were found (certified in Lean).

*The side scan.* Idle cores of six sessions scanned about 6,500 covers the fleet never used, at the record target.
Nothing was found, as expected: about 0.004 finds were due (`cpu_scan/LEDGER.md`).

## Corrections and withdrawals

1. Two limits were claimed for how far the first n primes can reach and were withdrawn the same day, 25 November.
   With r the largest of those primes, they were 1.1275·r·(ln r)² (the limit of a recursion, which lets small primes
   make choices they cannot afford) and 1.349·r·(ln r)²/ln ln r (mine; the Lean session showed that classes taken
   from one common integer, an old device of Erdős and Rankin, beat the random-like covers my argument assumed). The
   constant 1.349 also appears in a proved lower bound; that bound stands and has since been superseded by stronger
   proved ones.
2. In the coding-theory world I first wrote that decoding to the classical limit returns nothing that fixing a few
   more remainders would not; the Opus session found the counting error. I then gave its cost as at least 25,000
   scans of a window; a verifier showed that a decoder that weights only the remainders actually present needs far
   less, about one weighted entry per member. The conclusion, never cheaper than scanning, stands; the margin I gave
   does not.
3. The polynomial parity mechanism was said to reach rows that remainders could only reach at much greater cost. That
   was wrong: one common remainder for all small primes does the same at a fraction of the cost (checked by complete
   enumeration and in Lean). The mechanism is real; its advantage was overstated.
4. "Symmetry divides the search exponent by the group size" was too strong: it holds only for whole degrees, and by
   the number of orbits rather than the group size.
5. For the one-condition programme, one lower bound was false without an extra hypothesis, and the reading I passed
   on, that its cost grows like the full precision, was wrong: about the square root is reachable, and was run.
6. The free-oracle ceiling was 4.10 nats by extrapolation; the exact counts give 3.81. Fixing remainders for two more
   primes was first valued at 0.49 to 0.53 nats; correctly counted it is 0.32.
7. In the polynomial world, the advantage of parity as a way of ranking candidates was described as growing with
   depth; at a fixed share of candidates kept, it falls.
8. The side scan was first started on 24 covers the fleet had already scanned; those are recorded as rescans.

## Open questions worth someone's time

1. A shortcut beyond the cover. At the 10% target, the numbers that would supply the missing factor have about 1,116
   rows left after sieving by the primes up to 2,000, where members of the best cover have 1,309 ± 14. A method that
   outputs such numbers for under 10^9 operations each (about 550 primality tests) would break even with the fleet;
   nothing known comes close.
2. Lists and trees on the one-condition problem. This was being measured when the work stopped, and no numbers came
   back. My prediction, not tested: two sorted lists reach nine more primes within one window-scan of work for a gain
   of five or six rows, and four lists reach twelve primes but need about seven rows of slack, so they lose. A
   four-list run at twelve primes that beats the window's best member by more than seven rows would prove the
   prediction wrong and make the route worth pursuing.
3. A fast parity of the number of prime factors. Whether it can be computed faster than factoring is open; it would
   matter here only if it cost under 2% of one primality test per row, and even then it is worth a factor of about
   four to ten, not 250.
4. Even and odd members. Rows of members with even index looked 0.35% likelier to be prime than those with odd index
   (2.6 standard deviations), with the opposite sign in a later sample. About ten million tests of each kind from the
   fleet's logs would settle it to 0.1%; no mechanism is known, and I expect noise.
5. The reach of small primes. It is proved in Lean to grow at least like r·(ln r)² divided by 9,000·(ln ln r)², and
   no upper bound of that kind is known; one complete cover of the first n primes that reaches beyond the recursion's
   prediction for its n would show that structured covers matter at practical sizes.
6. A five-minute check: the free-oracle ceiling of 3.81 nats was measured on one cover; the same count on a second
   cover should give 3.8 ± 0.2 if it is a property of the design.

Everything above is in `README.md` with its sources; the scripts behind the toy-world and replacement pages are in
`toy_worlds_scripts/`, and the side scan's record is in `cpu_scan/`.
