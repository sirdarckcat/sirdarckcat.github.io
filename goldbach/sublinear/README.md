# Finding deserts without trying the numbers one by one

A research programme started on 23 November 2026, at the user's request, by
this session (experiments, number theory) and the Lean session (proofs). This
file is the running record of what has been tried, what is proved, what is
only measured, and what is open.

**Where it stands (24 November, evening).** No method was found, and the
reason is now understood and quantified. Two results of the 24th sharpen
it, both in "A floor under every cover" and the section after it:

- The covers in use are the best there are. A measurement that needs no
  search to succeed (the partition function over all class vectors, run from
  a random start and from the best cover and compared) puts a floor of 1,214
  rows under every cover on the 89 moduli at Q = 170,000 where the two starts
  agree, and 1,247 or 1,248 at the bottom; the best cover found has 1,248.
  At the 10% target no cover comes within 80 rows of what a 1% chance would
  need. So better covers are not a way to 10%.
- A law. The number of class vectors on the odd primes up to x that strike
  every odd prime below Q is exp(θ(x) − c·Q/ln² x) with c = 1.00 ± 0.03,
  measured from 45 to 1,228 moduli and derived, constant included and
  nothing fitted, from the Hardy–Littlewood count of prime pairs (within 1 to
  5% at nine points, where the first-moment count is off by a factor 1.5 to
  1.9); the same calculation predicts within 6% how few rows the best cover
  leaves at the campaign's targets. It gives D(n) = r·ln² r/c: the luck-free depth is known
  to a few percent at every size, and at 200 digits it ends near 16,000 on 89
  moduli, where 15,907 has been found; rigorously, 15,907 ≤ D(89) < 37,000,
  the upper end by an exhaustive search of the uarch session.

- The numbers wanted exist in abundance: about 10^175 even N below 10^200
  have g(N) ≥ 213,070 (10% of the ceiling), and a search that could order N
  by the rows left at sieve depth 5,000 would reach one within the Colab units
  that remain (Result 3; the counting method is checked against an exact
  enumeration of every even number below 10^9, and re-enumerated
  independently by the Lean session).
- They cannot be located by anything known. 10^200 is exactly large enough to
  choose the residues of N modulo the primes up to 463; that choice is the
  cover, and it is collected in full. Beyond that line every method examined
  costs more than scoring candidates one by one, each ruled out with numbers
  and the counting parts proved in Lean ("Why nothing known collects the
  prize"). Problem (P′) states what would have to be solved.
- Even a perfect search over everything the fleet's sieve sees would stop
  near 16% of the ceiling with the remaining units.
- In the polynomial toy setting a mechanism that is neither a small factor
  nor luck does exist (Result 1), now proved in Lean without hypotheses,
  including a formal proof of Stickelberger–Swan; over the integers it has no
  counterpart.
- Two by-products about the integers, both proved in Lean: for all large X
  some even N ≤ X has no Goldbach summand below c·ln X·ln ln X, for every
  c < 1.349 (the one earlier bound we found has 1/2); and an explicit even
  N < 10^200 with every N − q, q prime below 16,981, divisible by a prime
  ≤ 491, certified by divisibility alone.
- A third by-product is exact and small: D(n), how far the first n odd primes
  can strike every prime with no luck, is 5, 7, 19, 31, 43, 67, 103, 163,
  181, 223, 271, 331, 419, 499, 613, 709, 739, 859, 907, 1,051, 1,213, 1,279,
  1,381, 1,471, 1,567, 1,669, 1,801, 1,933 for n = 1 to 28 (`desert.c`; two programs to n = 15, the uarch
  session's faster search beyond, and the Lean kernel to n = 9). It grows faster than the r·ln r of the theorem:
  like r·ln² r, by the law above.
  The Lean session proved that it also bounds the least summand from above
  (g(N) ≤ D(number of odd primes up to √N)) and that "D(n) < (next prime)² − 2
  for every n" implies Goldbach's conjecture.
- For the campaign itself the gains are in `../fscan/cover/`: the
  89-prime covers on which the fleet found 158,209 on the 23rd and 160,357
  on the 24th (7.53% of the ceiling; the second on a family-B cover of the
  491 set, rechecked here from its N), the first-88 covers
  (1,255 rows at 170,000) its smaller cards now run, and, late on the 23rd,
  the finding that the final record is decided by the rows a cover leaves
  *above* its design level: the near-optimal covers come in two families that
  the row count cannot tell apart and that differ by about +1,000 in expected
  final record. With the fleet's own measured rates the expected final record
  is about 175,000 to 176,000 (8.2% of the ceiling), and the chance of 10% in
  the remaining units is below 0.01%.

## The question

The search for an even N < 10^200 with a large g(N) (the least prime p with
N − p prime) works in two stages. A *cover* fixes N modulo 88 or 89 small primes so
that most of the numbers N − q, q prime below the target, have a small factor.
The rows q it leaves (about 1,100 to 1,600) must then all give a composite
N − q by luck, and members N = N0 + tM are tried one after another: sieve,
keep the ones with the fewest rows left, test. One member in e^26 to e^39
succeeds, depending on the target.

The members with unusually few rows left after the sieve are far more likely
to succeed, and far better numbers exist than the search can afford to find:
an explicit family for the primes up to 10^7 is about e^10 times better than
a typical member (`../fscan/cover/brainstorm/`), and the count in Result 3
below puts the best ones, by rows left at depth 10^8, some e^27 above the
members of the best covers. The question is whether such members can be
*located* without enumerating all t:

> Given the rows R, the progression N0 + tM (0 ≤ t < K) and the sieve primes
> s ≤ z, find t for which the number of rows q with N0 + tM − q free of prime
> factors ≤ z is far below its mean, in time sublinear in K.

More generally: any way of producing N for which many N − q are composite
that is neither a covering congruence (which costs ln r of the 460.5 nats of
10^200 per prime r) nor trial.

## What the note `remark.pdf` contributed

The user pointed to https://alpo.ge/remark.pdf for inspiration. It is a
four-page personal account of a claimed proof of the Riemann Hypothesis found
by working with Claude and formalised in Lean; it contains a timeline and
acknowledgements but no statement that can be checked from the note itself,
and nothing in this programme relies on its claim. What was taken from it is
the method it describes: find a *toy setting* (function fields) where the
analogous problem can be solved by combining ideas, then look for the
"native" counterpart over the integers, and formalise as you go.

## Result 1: in the toy setting a third mechanism exists

Toy setting: polynomials over a finite field F_q (q odd, characteristic p)
in place of integers, monic irreducible polynomials Q of small degree in
place of the primes q. The analogue of the desert is: N − Q reducible for
every monic irreducible Q of degree below a bound.

**Theorem (parity).** Let N ∈ F_q[x] have degree n, leading coefficient λ
and derivative N′ = 0 (N is a polynomial in x^p). Let Q be monic irreducible
of degree d < n with p ∤ d, and suppose N vanishes at every root of Q′. Then
N − Q is squarefree, and the number r of its irreducible factors satisfies

    (−1)^(n−r) = χ(−1)^A · χ(λ)^(n−d−1) · χ(−d)^n · χ(d)^d · (−1)^(d−1),
    A = n(n−1)/2 + n(d−1) + (d−1) + d(d−1)/2,

χ the quadratic character of F_q. So the parity of r is the same for all
such Q of a given degree; when it is even, every N − Q is reducible, although
no factor is exhibited.

*Proof.* Put f = N − Q, so f′ = −Q′ (degree d−1, leading coefficient −d).
A common root of f and f′ would be a common root of Q and Q′, so f is
squarefree. With disc f = (−1)^(n(n−1)/2) λ^(n−2) ∏_{f(α)=0} f′(α) and the
symmetry of the resultant, ∏ f′(α) = (−1)^(n(d−1)) (−d)^n λ^(−(d−1))
∏_{Q′(β)=0} f(β). As N(β) = 0, f(β) = −Q(β), and ∏ (−Q(β)) =
(−1)^(d−1) d^(−d) Res(Q, Q′) = (−1)^(d−1) d^(−d) (−1)^(d(d−1)/2) disc Q.
Stickelberger's theorem (Swan 1962; Pellet's formula) says
χ(disc g) = (−1)^(deg g − number of irreducible factors of g) for squarefree
g; apply it to f and to the irreducible Q. ∎

The Lean session derived the same statement independently from resultants
alone, as one identity over any field: for Q monic of degree d, N′ = 0, d ≠ 0
in the field, d < n, and every irreducible factor of Q′ dividing N,

    discr(N − Q) = (−1)^(n(n−1)/2 + nd + (d−1) + d(d−1)/2) · λ^(n−d−1) · d^(n−d) · discr(Q),

from which the parity formula follows by Stickelberger's theorem on both
sides.

**Formal status (23 November).** Everything in this section is proved in Lean
on the Lean session's branch `ccr-36ca7b46-8twf14`, standard axioms only:
`goldbach/lean/GoldbachGaps/FunctionField/ParityDesert.lean` (the identity,
squarefreeness, the parity formula, the deserts) and `Stickelberger.lean`
(commit c0e3fb4): for a finite field of odd characteristic and every
squarefree g, χ(discr g) = (−1)^(deg g + number of irreducible factors). The
latter was not in Mathlib; as far as either session knows it is the first
formal proof of Stickelberger–Swan. So the theorem and the corollary below
carry no hypothesis.

**Two extensions found by the Lean session** (proved there, commits 4d62189
and d3d39ea; checked here by factorisation, `parity_rule.py`):

- *Any degree, including p | d.* With e = deg Q′ and l its leading
  coefficient, discr(N − Q) = ± λ^(n−2−e) · l^(n−d) · discr(Q) with an explicit
  sign, and for q a square and λ a non-square the number of irreducible
  factors of N − Q is even exactly when (−1)^(d+1+e) · χ(l)^(n−d) = 1. For
  p ∤ d (e = d − 1, l = d) this always holds. Checked on all 240 irreducible
  cubics over F_9, for n − d even and odd, without exception
  (`parity_rule.txt`).
- *The hypothesis is about Q′ only.* What the proof uses is that every
  irreducible factor of Q′ divides N. So, with q an odd square and λ a
  non-square as in the corollary below, N = λ·V_J^p makes N − Q reducible for
  every monic irreducible Q of *any* degree d below deg N with p ∤ d whose
  derivative is J-smooth (for p | d, exactly for the rows that meet the sign
  rule above). Exact counts by the Lean session over F_9 with J = 3
  (deg N = 2,403): every quartic, 8,928 of the 11,808 quintics (75.6%) and
  282,672 of the 683,280 rows of degree 7 (41.4%), with no congruence and no
  luck. The derivative of a row is smooth a little more often than a random
  polynomial of its degree (38.7% at degree 6), because some of its
  coefficients vanish; for larger degrees the proportion falls roughly like
  Dickman's function of (d − 1)/J, which is an estimate and not a count.

**Corollary (deserts).** Let q be an odd square (q = p^(2e)), J ≥ 1, V_J the
product of all monic irreducibles of degree ≤ J, λ a non-square, and
N = λ·V_J^p. Then N − Q is reducible for every monic irreducible Q of degree
≤ J + 1 (p ∤ J+1): those of degree ≤ J divide N, and for degree J + 1 the
formula gives r even. deg N = p·deg V_J, a little above p·q^J (2,403 against
2,187 for F_9 and J = 3). Forcing the same by congruences needs a degree of order
q^(J+1)/J (primes of degree ≤ J always leave a fraction of order 1/J of the
rows of degree J + 1, and each of those then needs a prime of its own), and
a cover of degree p·q^J followed by luck succeeds with probability about
exp(−0.7 q / (p (J+1))). Over a prime field the same N with a suitable
(n mod 4, λ) handles the single top degree, at no saving.

**Checked** (`parity_desert.py`, python-flint; `parity_desert.txt`): the
parity is constant over all rows of each degree, and equal to the formula, in
every case tried: F_3, F_5, F_7, F_9, F_25, F_49, rows of degree 2, 3 and 4,
both kinds of λ, n ≡ 0 and p (mod 2p); for instance all 300 irreducible
quadratics over F_25 and 150 quartics over F_5 give a reducible N − Q, and so
do samples of the 1,620 quartics over F_9 (deg N = 2,403) and of the 5,200
cubics over F_25 (deg N = 3,125) in `parity_desert_big.txt`. For rows with
p | d the parity is mixed, and follows the sign rule above row by row.

**What this is and is not.** It is a compositeness mechanism that is not a
small factor and not luck: the parity of the number of prime factors, which
over F_q[x] is the quadratic character of a discriminant and, for N a p-th
power, depends only on N modulo the *derivative of the row*. The mechanism is
known: Swan (1962) already has families with an even number of factors
throughout (x^(8k) + x^m + 1 over F_2); Conrad, Conrad and Gross (2008) give
the general theory of the Möbius function of f(g) for f a polynomial in T^p,
including irreducible polynomials with no local obstruction and no
irreducible value at all; Sawin and Shusterman (2022) use it to break the
parity barrier for twin primes over F_q[T]. The Goldbach-shaped corollary
above (N fixed and inseparable, the row varying) is an instance; we have not
found it stated. K. Conrad's survey of the phenomenon is titled "Irreducible
values of polynomials: a non-analogy": it is the standard example of
something true over F_q[T] with no counterpart over the integers. It
is not a search algorithm. In the toy setting it buys (i) one more degree at
the deterministic frontier, a factor q/p in the number of rows; (ii) in the
regime where luck dominates, a cheap exact filter: half of the rows of any
member are certified reducible for the cost of a Jacobi symbol, which by the
selection identity is worth a factor of about 4 (1.4 nats; an estimate, to
be measured in rung 2), and more if the cover is chosen with parity in mind.
It does not find members with few rows left without enumeration even there.

**Desert or cover? (the design question, settled by counting.)** A zero
class at π makes π's factor in the parity symbol +1 for every row; a nonzero
class makes it a coin flip for the rows with π | Q′ and in exchange kills, by
divisibility, the rows in that class. A coin flip is worth nothing to a
search: it leaves the expected number of irreducible N − Q unchanged and only
says where they are, which is the filter of Result 2 and is free for every N.
So zero classes buy certainty on the rows with a smooth derivative and cost
the factor p in degree and the divisibility kills. At equal degree over F_9
(n = 2,403): the desert kills every quartic, 75.6% of the quintics and 41.4%
at degree 7; an ordinary cover (nonzero classes on the 285 primes of degree
≤ 3, plus 400 quartic moduli) leaves 13.8% of the rows of every degree before
any optimisation, mops up the 223 quartics left with the quartic moduli, and
so equals the desert at degree J + 1 and beats it above. The desert wins only
on the deterministic objective at degree exactly J + 1, and only when q/p is
large (the ratio (1 + 0.56(q − 1)/J)/p of the corollary: 1.5 for F_25 and
J = 2, 2.1 for F_49). Turning single zero classes of a desert into nonzero
ones is a loss on the rows the desert is for (those of which more than half
have a smooth derivative) and a gain only at higher degrees, where the
ordinary cover is better still. For search, the right design in the toy is an
ordinary cover, a generic N, and the parity filter on what is left. The rule
used here, that for N′ = 0 the parity depends on N only through its degree,
its leading coefficient and N modulo Q′, is `parity_card_factors_resultant`
and `parity_card_factors_congr` in the Lean library (commit 8683c0b).

## Result 2: what the parity filter is worth in a toy search

`toy_search.py` is the whole search in miniature over F_3[x]: a greedy cover
on the 14 irreducibles of degree ≤ 3, the 1,318 monic irreducible rows of
degree ≤ 8 (42 left by the cover), members N0 + T·M of degree 93, a sieve to
degree 6, selection, tests. 30,000 members, 1,426 successes (the model's
(1 − p)^k predicts 1,431). Parity is read off the discriminant of N − Q:

- half of the rows have odd parity (0.4984 of all, 0.5000 of those that
  survive the sieve); no irreducible N − Q has even parity; among odd
  survivors the irreducible ones are 0.2505 against 0.1252 among all
  survivors: exactly twice;
- successes per 1,000 tests, keeping the best 3% of members: 14.6 when
  members are ranked by rows left and every row is tested (the production
  scheme), 65.2 when they are ranked by *odd* rows left and only odd rows are
  tested: 4.5 times (5.1 at 1% kept, 3.8 at 10%, 2.0 with no selection).

So in the toy setting the filter is worth a factor 4 to 5 (1.4 to 1.6 nats),
as the selection identity predicts. It remains a constant factor: every
member is still looked at (`toy_search_m3_g8.txt`).

## Why the integers are harder (the gap to close)

The integer counterpart of Result 1 would be a way to compute, or to force,
the parity of the number of prime factors of N − q, the Liouville function
λ(N − q), for N in some special family. Nothing of the kind is known:

- λ(n) has no known formula short of factoring n; the role played by the
  discriminant and the derivative has no counterpart ("differentiating whole
  numbers").
- Any information that depends only on n modulo small numbers (Jacobi
  symbols, genus characters, norm-form conditions) is uncorrelated with λ(n)
  by the prime number theorem in progressions; this is the parity problem of
  sieve theory.
- Every algebraic certificate tried so far (differences of powers, two
  representations by quadratic forms, cyclotomic values) exhibits a
  factorisation N − q = A·B and so costs a congruence modulo A per row
  unless rows share it, which they do only through small primes (the cover)
  or for at most √Q rows.

- The integer shadow of "parity = character of a discriminant" does exist:
  by genus theory the number of prime factors of n is the 2-rank of the class
  group of Q(√−n) plus one (for n ≡ 3 mod 4 squarefree, n is prime exactly
  when the class number h(−n) is odd). But reading it off means finding the
  ambiguous forms of discriminant −4n, which is how the class-group factoring
  methods of Shanks and Schnorr–Lenstra work: it is as hard as factoring n.
  In F_q[x] the same invariant is one resultant.

So the transfer needs new mathematics, and the programme does not assume it
will be found.

## The search problem itself: where it sits

Dictionary: members t < K ↔ messages; (t mod s) for the sieve primes s ↔ a
codeword of a Chinese-remainder code (over F_q[x]: a Reed–Solomon code); the
rows give, for each s, the classes that kill something; the wanted t maximises
a sum of weights. This is soft-decision maximum-likelihood decoding with very
large lists, and:

- algebraic list decoding (Guruswami–Sudan, Koetter–Vardy; over the integers
  Goldreich–Ron–Sudan, Boneh, Guruswami–Sahai–Sudan, and Coppersmith's method)
  needs an agreement about four times the typical one for our parameters,
  while the best member among K exceeds the typical one by a few percent;
- two distinct members agree modulo sieve primes of total size below K
  (proved in Lean: `move_budget`), so there are no local moves;
- lists and birthday merges give ln(list size) nats for nothing and no more;
  for large alphabets the refined information-set decoders reduce to plain
  enumeration;
- maximum-likelihood decoding of Reed–Solomon codes is NP-hard in general
  (Guruswami–Vardy) and at least as hard as discrete logarithms in a suitable
  range (Cheng–Wan); "noisy Chinese remaindering" with small lists falls to
  lattices (Bleichenbacher–Nguyen), with lists as large as ours it does not.

The instance is special (all lists are images of one set of rows), and that
is the only place left to look.

## Result 3: what a perfect search would be worth

The numbers wanted exist in abundance; this section counts them. It answers
"how much would an algorithm be worth that finds members with few rows left
without trying them", as a function of how far up the primes it can reach.

**Setting.** Fix the target Q = 213,070 (10% of the ceiling). For a depth z,
call k_z(N) the number of rows q < Q for which N − q has no prime factor ≤ z.
An N with k_z rows left succeeds with probability (1 − p_z)^k_z, with
p_z = 2·∏_{3≤s≤z} s/(s−1) / ln N, if nothing is known about N beyond its
residues modulo the primes up to z. An *ideal search to depth z* tests the even
N < 10^200 in increasing order of k_z; its cost is the number of N tested
when the expected number of successes reaches one.

**Method.** The residue vector of N modulo all odd primes up to z is a state;
its energy is k_z. `ideal_tilt.c` samples the states at 108 temperatures by
parallel tempering (it is the cover problem with every prime up to z as a
modulus, at all temperatures instead of only at the bottom), and
`ideal_tilt.py` turns the histograms into the number of states g(k) at each
energy by multi-histogram reweighting, normalised by the total ∏ s. The number
of even N < 10^200 with k rows left is g(k)·(10^200/2)/∏ s, on the assumption
that the N below 10^200 are a fair sample of the residue vectors, which is the
assumption every part of the campaign already rests on.

**Check.** For z = 463 (the 89 primes of the best covers) the ideal search *is*
the present design: best covers first, every member tested. The program gives
one success per e^39.31 members, and e^−8.49 expected successes for the
remaining budget of e^30.75 members; the direct calculation from the covers
(`../fscan/cover/brainstorm/`) gives e^39.2 and 0.02%. The sampler reached the
known minimum of 1,609 rows.

**Result** (`ideal_tilt_213070.txt`):

| primes used ideally | N tested for one success at 213,070 | rows left at that depth, ideal N | same, typical member of the best cover | expected successes in the remaining budget (e^30.75) |
|---|---|---|---|---|
| ≤ 463 (today) | e^39.3 | 1,620 | 1,609 to 1,620 | 0.0002 |
| ≤ 1,000 | e^35.8 | 1,319 | 1,439 ± 11 | 0.007 |
| ≤ 2,000 | e^33.4 | 1,116 | 1,309 ± 14 | 0.08 |
| ≤ 5,000 | e^30.5 | 910 | 1,170 ± 17 | 1.3 |
| ≤ 20,000 | e^26.7 | 685 | 1,007 ± 18 | 50 |
| ≤ 50,000 | e^24.5 | 574 | 922 ± 19 | 400 |
| ≤ 10^8, rows beyond 50,000 treated as independent | about e^11.8 | 160 | 542 | — |

So the prize is 3.5 nats for the primes up to 1,000, 5.9 to 2,000, 8.8 to
5,000, 12.6 to 20,000 and 14.8 to 50,000, from 4.5 nats per factor e in depth
at the start to 2.4 at the end. An ideal search to depth 5,000 would bring the
10% record within the Colab units that remain; to 20,000 it would bring fifty
of them. The last line shows where the count goes with the whole sieve: it is
the statement, already in the brainstorm notes, that the best N for the primes
up to 10^7 or 10^8 is enormously better than anything the search can afford to
find.

A regularity, and its explanation. Over this range the cost times ln z is
nearly constant (241, 248, 254, 260, 265, 265 for the six depths) and so are
the rows left for the ideal N times ln² z (61,000 to 67,200): a typical
number loses rows like 1/ln z as the sieve deepens (Mertens), the ideal ones
like 1/ln² z. The Lean session traced this to a thinning law
(`Cap/Thinning.lean` and `scripts/thinning_check/` on its branch). If the
primes in (z, z′] kill the rows left at depth z independently, the table at
depth z′ is the table at depth z read at another temperature,
1 − e^(−β) = θ(1 − e^(−β′)) with θ = ∏(1 − 1/s), so the bottom of a deep table
is the middle of a shallow one, and along the cutoff of the ideal search the
rows fall like (ln z)^(−a) with a = (e^β − 1 − p)/(β − p), β the slope of
ln g at the cutoff. Measured here that slope is 1.32, 1.23, 1.22, 1.25, 1.29
at depths 1,000 to 50,000 (2.9 at 463, where the landscape is frozen), which
gives a = 2.1, 2.0, 2.0, 2.0, 2.1. So the exponent 2 is not "every prime
strikes twice": in the ideal population a new prime strikes about e^β = 3.5
times its usual share, and (e^β − 1)/β happens to be 2 at β = 1.26. Three
consequences. The ideal N of depth 50,000 have about 1,950 rows left at
depth 463 (β = 0.53 there): ordinary good residue vectors, not the best
covers, aligned with every later prime by a factor that grows from 1.7 to
3.5. The whole table follows from one shallow table to within 0.4 nats from
depth 5,000 and 1.4 from 463, always on the optimistic side, which is an
independent check of the five deeper runs. And for primes above Q the
independence used in the last line of the table is a proved inequality
(`thinCount_le_of_lt`: a prime above Q divides at most one row, so
independent thinning can only overstate the number of N with few rows); the
slack is estimated at 0.3 nats.

The fourth column is measured on 20,000 random members of a cover with 1,609
rows (mean ± standard deviation; `member_depth.py`). The ideal N are *not*
members of the best covers: 1,319 rows at depth 1,000 is 10.6 standard
deviations below the mean of such members, 685 at depth 20,000 is 17.5 below,
and the e^39 members of all the covers within a few rows of 1,609 reach about
9 standard deviations. The ideal N give up a few rows on the small primes and
are aligned, mildly, with all the primes above: at the temperature that
matters, a class change is accepted with probability below 0.01 for moduli
under 128, about 0.1 for 128 to 512, 0.4 for 512 to 2,048, 0.7 for 2,048 to
8,192 and 0.9 above. No prime beyond 512 is pinned to its best class; each is
in a better-than-average one.

Caveats. (i) Accuracy. For z ≥ 1,000 the answer sits at a temperature where
the sampler mixes freely: forward and backward free-energy estimates agree
within 0.1 nats in total down to that temperature, a second seed on a
shorter temperature ladder gives e^33.31 and e^30.46 for depths 2,000 and
5,000 (first run: e^33.37 and e^30.50), and the same method reproduces the
exact counts of the miniature below. Only for z = 463, where
the answer sits near the bottom of the landscape, is the sampler out of
equilibrium (20 nats low at the very bottom against direct counts), and that
line is checked against the covers themselves. (ii) The budget is counted in full-weight members,
that is, with the fleet's deep sieve and 3% rule behind each tested N in every
line. That selection is worth 2.0 nats today and about 1.8 after an ideal
search to 20,000, which has already used part of the same information.

**How many solutions there are.** Summing (1 − p_z)^k over *all* N gives the
expected number of even N < 10^200 with no prime row below the target, and it
must not depend on the depth z at which it is computed. It does not: for
213,070 the six runs give e^403.30, 403.28, 403.27, 403.26, 403.24, 403.24
(z = 463 to 50,000), about 10^175 numbers. At 245,000 it is e^395.7, at
300,000 e^383.1, at 350,000 e^371.5, at 500,000 e^338.0: about 0.23 nats less
per 1,000 in the target, which reaches zero near 2.1 million, the ceiling the
campaign measures against. So at the 10% level one N in 10^25 is a solution
and one in e^39 among the members of the best covers; the difficulty is
entirely one of location. The Lean session reaches the same counts by a
route that shares no code and no method with this one: a closed formula in
the singular series of N with one constant fitted on its scan of every even
N ≤ 10^12 (the rows of one N are slightly less dispersed than independent
ones) gives e^403.2, 395.7, 383.0, 371.5 and 337.9 at the five targets, within
0.1 nats of the sampler, and one expected N at 2,133,689
(`goldbach/lean/scripts/lgs_heuristic/` on branch `ccr-36ca7b46-8twf14`).

**How far an ideal search would go** (`ideal_tilt_targets.txt`). The same
count at higher targets, as the natural logarithm of the number of N tested
per success:

| target (share of the ceiling) | today (≤ 463) | ideal to 5,000 | to 20,000 | to 50,000 | to 10^8, rows independent beyond 20,000 |
|---|---|---|---|---|---|
| 213,070 (10%) | 39.3 | 30.5 | 26.7 | 24.5 | 11.7 |
| 245,000 (11.5%) | | | 32.5 | | 16.1 |
| 265,000 (12.4%) | | | | 33.7 | 19.0 |
| 300,000 (14.1%) | | | 42.7 | | 24.1 |
| 350,000 (16.4%) | | | 52.3 | | 31.9 |
| 500,000 (23.5%) | | | 81.4 | | 56.8 |
| reached with the remaining budget of e^30.75 | 172,000 (8.1%) | 214,000 (10.0%) | 235,000 (11.0%) | 249,000 (11.7%) | 343,000 (16.1%) |

Two readings. First, even a perfect search over everything the fleet's sieve
sees (depth 10^8) would end near 16% with the Colab units that remain, and
20% (426,140) would still cost it about e^44 tests, e^13 times the budget;
with today's method 20% costs about e^87 (extrapolated). Deeper residues
would give more (at 213,070 the expected successes of an ideal search within
the budget go from e^18 at depth 10^8 to e^27 at depth 10^12,
`ideal_tilt_depths.txt`), but nobody can sieve them. Second, each line of the
table is steep: between neighbouring targets the cost grows like the target
to a power from 1.2 to 2.3 (same file), so a factor e in tests moves any of
these methods by 0.2 to 0.3 percentage points.

**The same thing in miniature, exactly** (`toy_exact.c`, `toy_compare.py`,
`toy_exact_1e9_1000.txt`). Take X = 10^9 instead of 10^200, target Q = 1,000
(167 rows), and enumerate every even N below X with no prime factor from 3 to
29: 157,947,020 numbers, of which exactly 256 have g(N) ≥ 1,000. Here the
Chinese-remainder line is at 23 (2·3·5···23 ≤ 10^9), so "cover first" means
ordering N by the rows left at depth 23, and the deeper sieve is taken to 200.
No model is involved, only counting:

| successes wanted | N examined, cover first | N examined, ideal to depth 200 | ratio |
|---|---|---|---|
| 1 | 2,982 | 13 | 229 (5.4 nats) |
| 3 | 63,350 | 401 | 158 |
| 10 | 253,380 | 10,811 | 23 |
| 30 | 1,205,425 | 73,849 | 16 |
| all 256 | 151 million | 154 million | 1 |

The 62 numbers with at most 8 rows left at depth 200 have 24 to 34 rows left
at depth 23, where the best covers have 22; one of the 62 lies in the 888
members of the best covers. The 256 true successes have 25 to 41 rows at depth
23 (the average N has 36.8). So in the miniature, as in the count above, the
best numbers are luckily aligned members of mediocre covers, and an order that
could see the deeper residues would reach the first success two hundred times
sooner. The miniature is also where any proposed method for (P′) below can be
tested against the truth in seconds. The Lean session re-enumerated it with a
different program and obtained the same joint histogram byte for byte, and
recomputed the success law and the pair correlation quoted below
(`goldbach/lean/scripts/mini_check/` on its branch).

The miniature also checks the method of this section. The count of N by rows
left at depth 200 predicted from residue vectors alone (tempering,
reweighting, and the assumption that the N below X are a fair sample, here at
e^−168 numbers per residue vector; `toy_tilt_1000_200.txt`) against the exact
count:

| rows left at depth 200 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 14 | 16 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|
| exact | 1 | 12 | 49 | 339 | 1,564 | 6,774 | 24,859 | 229,438 | 1,310,838 | 11,436,352 |
| predicted | 0.9 | 7.9 | 53.8 | 311 | 1,541 | 6,582 | 24,522 | 226,760 | 1,306,248 | 11,450,782 |

Agreement is within 3% wherever the count is large and within sampling noise
at the bottom, including the single best number of the 158 million. The
other half of the model holds as well: the 256 true successes are distributed
over the levels as count × (1 − p)^k with p = 0.485 (12, 18, 15, 29, 28, 36,
34, 30, 18 found at k = 12 to 20 against 8.7, 14.4, 21.2, 27.6, 32.1, 33.3,
31.1, 26.0, 19.7), and the density of primes among the 200-rough numbers
below 10^9 is 0.489.

Looking at the best numbers of the miniature directly, for any structure the
argument might have missed (the 62 with at most 8 rows left, the 1,965 with at
most 10, the 256 successes): they are spread evenly over [0, 10^9) (the
successes lean to large N, where primes are rarer); modulo each small prime
they sit in several good classes, not one (class 2 mod 5 for 73% of them,
class 3 for 19%; the most popular class holds 30% modulo 7 and less beyond);
they have 1.3
standard deviations more incidences with the primes from 31 to 199 than a
random number, the successes 0.35; and two of the 62 best agree modulo 0.49 of
those primes on average, against 0.45 by chance. So nothing ties one of them
to another beyond three things the model already contains, as the Lean
session showed on the true successes when it tested this claim
(`goldbach/lean/scripts/mini_check/needles*` on its branch): the tilt of the
residues; the size (successes lean to large N); and rows shared by numbers
closer than Q. The last is a real exception to independence: N + h − q′ =
N − (q′ − h), so a neighbour N + h of a success inherits every row q′ with
q′ − h prime, and the 303 true successes of the miniature (counting those
divisible by a prime from 7 to 29) contain 4 pairs closer than 1,000 where
independence predicts 0.09 and the inheritance predicts 2.7. It does not help
the search. A neighbour keeps only the classes of the primes dividing h, so it
loses the cover: at 200 digits a neighbour at distance 30,030 of a number
with g near 158,000 inherits about 6,000 of the 19,050 rows below 213,070 and is
left with about 1,600 rows at risk, the same as a fresh member of the best
cover (my count and the Lean session's agree), and it cannot be sieved in
bulk.

What each prime beyond the line is worth, and costs, in the miniature (N
ordered by rows left at depth z; gain in nats over cover first for 10, 30 and
100 successes; "overhead" is the number of residue vectors modulo the primes
up to z per number below X, i.e. the work of pinning those primes by plain
enumeration):

| z | 29 | 31 | 37 | 43 | 61 | 97 | 200 |
|---|---|---|---|---|---|---|---|
| gain, 10 successes | 0.44 | 0.15 | 0.77 | 0.66 | 1.71 | 2.40 | 3.15 |
| gain, 30 successes | 0.21 | 0.02 | 0.18 | 0.34 | 0.62 | 1.50 | 2.79 |
| gain, 100 successes | 0.10 | 0.30 | 0.55 | 0.59 | 0.78 | 1.16 | 1.94 |
| overhead | 6.5 | 201 | 7.4·10^3 | 1.3·10^7 | 1.2·10^14 | 2.3·10^27 | 7.8·10^72 |

A prime just beyond the line buys a fraction of a nat and costs its own size:
this is point 3 of the next section, measured.

## Why nothing known collects the prize

The 460.5 nats of 10^200 are exactly enough to *choose* the residues of N
modulo the primes up to 463 (their product is 10^192.7). That choice is the
cover, and enumerating covers best-first is an ideal search to depth 463: this
part of the problem is solved. Everything in the table above lies beyond that
line, and the line is sharp for a structural reason.

1. *Free coordinates stop at ∏ s ≤ X.* By the Chinese remainder theorem the
   residues modulo any primes with product at most X = 10^200 can be
   prescribed, and N is then determined. The residue modulo any further prime
   is a sum of one term per free coordinate, reduced modulo that prime
   (N = Σ a_r e_r − jM), so changing a single coordinate changes every
   further residue. Two different N < X agree modulo primes of total size
   below ln X only (`move_budget`, proved in Lean). There are no local moves:
   beyond the line the landscape is that of a random-energy model. Measured
   in the miniature (`toy_rem_check.c`): over 118 million pairs of members of
   the same cover, N and N + 2·3·5···23, the rows left at depth 200 correlate
   at −0.029 within each cover quality, the small negative value expected
   from landing in a different class modulo every further prime.
2. *Lattices.* Chinese remaindering with errors or with lists (Goldreich–Ron–
   Sudan, Boneh, Guruswami–Sahai–Sudan, Bleichenbacher–Nguyen) finds N from
   residues when the lists are short and the agreement high: the weighted
   agreement must exceed about sqrt(ln X · Σ w²/ln s). Here the constraint
   available per prime beyond the line is about one nat (if the primes up to
   about 400 are pinned, some 80 nats are left for the 79 primes from 467 to
   997, and less per prime further up), which means lists holding a third of
   all classes. For the 580 primes from 467 to 5,000 with one-class lists, in
   a population of e^83, the best agreement that *exists* is about 22 against
   a decoding radius of 78; with lists of a third the radius exceeds the
   number of primes.
3. *Meet in the middle and generalised birthday.* The linear form of the
   residues does allow these. With population e^F, constraint cost
   C = Σ ln(s/l_s) and list entropy H = Σ ln l_s, the solutions number
   e^(F−C) and a meet in the middle produces them at constant cost each only
   when H ≤ 2(F − C), with lists of e^(H/2) in memory. For the whole problem
   (F = 460, C ≈ 425) and a memory of e^21 entries that extends the reach by
   one prime; Wagner's tree needs more slack, not less. The equivalent
   statement in the design: covers on 90 or more primes (fewer than one member
   each) are usable in principle and worth about 0.2 nats per extra prime,
   and that is all.
4. *Hashing for near neighbours.* Writing N = u + v, the agreement of a pair
   is an inner product of a one-hot vector with a set indicator, block by
   block. The sets are translates of random-looking class lists, so a
   locality-sensitive scheme collides on a good pair at most about twice as
   often as on a random one for a bucket of the same size. The exponents we
   computed are 0.88 (this session) and 0.99 (the Lean session, for its
   variant), i.e. at best K^0.94 work for a population K. Populations here
   are e^80 and more against e^33 operations available.
5. *Linear-time scoring.* What remains is to score every member, which is
   what the fleet's sieve does at 23 ns a member. Under that cost the present
   design is at its optimum: the gain of selection depends only on the kept
   fraction, the kept fraction is fixed by sieve cost against test cost, and
   the sieve cannot skip members (marks are generated along progressions).
   The Lean session's bound (a perfect solver on the present progressions is
   worth at most 4.3 to 5.3 nats over the 3% rule) is this statement for a
   population of e^22.

The Lean session tried independently to break this (lattices of moves,
additive and multiplicative splittings of t, tree search with bounds,
polynomial parametrisations, sharing rows between consecutive N by a
convolution) and could not; the formal parts of its answer are the Lean files
named in rung 4 of the ladder. Two of its remarks belong here. For
arbitrary lists the question "does any N below a bound meet every list" is
NP-complete already with two classes per modulus (Manders–Adleman 1978;
Garey–Johnson AN1), and for arbitrary *rows* the cover question itself
contains SAT, which the Lean session proved in the cover's own terms
(`Cap/Hardness.lean`, commit 84040ae: from a formula with n variables and m
clauses it builds n prime moduli and m(n+1) rows of polynomial size such that
the formula is satisfiable exactly when some N is congruent to every row
modulo one of the moduli). So nothing that treats the rows or the lists as
arbitrary data can be both exact and fast, and with the black-box bound
(`Cap/BlackBox.lean`) nothing that only asks members how good they are can
beat enumeration. Neither says anything about the one structured family that
matters, rows = the primes below Q: a lower bound against every algorithm on
that family is out of reach of any known proof technique. What can be done is
to price each property the prime rows have that arbitrary rows lack, and that
is what this section does. And for our lists the problem is the search for intervals
(N − Q, N] poor in rough numbers at fixed offsets, the same problem as record
prime gaps, where the state of the art is also covering congruences followed
by a sieve over the members.

The Lean session proved the general form of this (`Cap/ListGain.lean`,
`list_gain_le`): for one prime s, if w(a) is the number of rows killed when N
is in class a, μ its average over the classes and W its maximum, then any
list L of classes gains at most (W − μ)/ln(W/μ) · ln(s/|L|) rows over the
average, i.e. a nat of constraint on s buys at most (W − μ)/ln(W/μ) rows,
whatever the shape of the list. For every prime above Q (W = 1, at most 1,609
rows) that is 0.207 rows, 0.005 nats of success, per nat
(`list_gain_above_Q`), six times less than an extra covering prime; so
nothing that enumerates a product of lists (lattices, meet in the middle,
birthday trees) collects the part of the prize that lies above Q.

One structure does exist and does not pay. For a prime s above Q the list is
the set R of rows itself, a set of numbers below Q, so "N mod s is in the
list" implies "N mod s is small", an interval condition, and numbers that are
small modulo many primes at once *can* be found by lattice reduction
(simultaneous approximation). But R fills under 1% of the interval [0, Q), so
forcing N mod s below Q costs ln(s/Q) nats and raises the chance of a kill by
that prime only from k/s to k/Q = 0.8%: a hundred to a thousand times less
per nat than the last prime of the cover.

A second structure exists as well, and it is the only place where prime rows
are cheaper than arbitrary ones: the rows are the same for every N, so
neighbours share their arithmetic. If the primes of a stretch of length L near
10^200 are known (0.03·L probable-prime tests after a sieve to 10^8), then
every even N of the stretch is decided by table look-ups alone: N fails
exactly when N − π is a prime below the target for some prime π of the
stretch, about 68 marks per N at a target of 170,000. That is some 6,000
elementary operations per N, most of them the probable-prime tests, against
something like 20,000 for a member of a cover in the fleet's pipeline. But the N of a stretch
are consecutive, their residues modulo the cover primes are whatever they are,
and a number without a cover succeeds at 170,000 with probability about
e^(−46.6) against 0.17·e^(−30.0) of captured chance for a sieved member of a
cover: cheaper by a factor 4 per number and worse by a factor of about a
million per operation. A cover on the primes up to 13 would let seven members
share a window and gains a nat or two of the sixteen. The two structures
exclude each other: a cover spaces its members 10^193 apart, and sharing needs
them within 2·10^5.

In the language of the literature: collecting the prize means solving *noisy
Chinese remaindering with dense lists* on average — rate 460/1,940 and lists of
about a third of the classes for depth 2,000 — or equivalently maximum-
likelihood decoding of a Chinese-remainder code with far less agreement than
the Johnson bound requires.
The polynomial version was proposed as a hardness assumption (Naor–Pinkas) and
lattice attacks are known only for short lists (Bleichenbacher–Nguyen). Nothing
here proves that no algorithm exists. The claim is narrower: the prize is
real and of known size, the cover collects all of it that lies below the
Chinese-remainder line, and beyond the line every method we know of costs more
than scoring the members one by one.

**Open problem (P′).** Find even N < 10^200 for which at most 1,320 of the
primes q < 213,070 have N − q free of prime factors up to 1,000, at a cost of
fewer than e^30 operations in all for e^30 such N. About e^36 such N exist; the
best covers give 1,439 ± 11 and nothing below about 1,340 within any budget
considered here. A solution is worth 3.5 nats (a factor of 30) at the 10%
target, and the same question at depth 5,000 (910 rows) is worth 8.8.

## A provable lower bound (proved in Lean on 23 November)

The game is an instance of a question with almost no literature: how large
can g(N) be made, provably? The conjectured maximal order is ln² N · ln ln N
(Granville, van de Lune and te Riele 1989), the same order as the model
ceiling the campaign measures against. The only lower bound we have found is
in a 2026 preprint (W. Shi,
arXiv:2605.21529, Theorem 6.22 by its numbering; unrefereed; the author writes
that he has not found such bounds in the literature): the maximum of g(N)
over even N ≤ X is at least (1/2 + o(1)) ln X · ln ln X, by counting (each
prime p accounts for at most π(X) values of N, so π(z) ≥ ln X / 2 primes are
needed to account for all of them).

A cover gives more, and constructively. Let P1 be the odd primes up to αy and
P2 the primes in (αy, y]. With classes for P1 chosen at random among the
nonzero ones, an odd prime q < Q stays uncovered with probability
∏_{r ∈ P1}(1 − 1/(r − 1)) ≈ 2·C₂·e^(−γ)/ln(αy) (C₂ the twin-prime constant),
so some choice leaves at most that fraction of the π(Q) rows; if they are no
more than |P2|, each gets a prime of P2 of its own. The even N in [M, 2M),
M = 2·∏_{3≤r≤y} r, lying in all these classes then has every N − q divisible
by some r ≤ y, so g(N) ≥ Q. With α → 0 slowly this gives

    max over even N ≤ X of g(N) ≥ (e^γ/(2·C₂) − o(1)) · ln X · ln ln X,   e^γ/(2·C₂) = 1.349.

Letting each large prime cover two rows (pairs q, q′ with r | q − q′, the
Maier–Pomerance device) would double the constant but needs prime pairs with a
prescribed difference on average; several rows per prime, as in the large-gap
theorems of Ford, Green, Konyagin, Maynard and Tao, would give an extra factor
ln ln X / ln ln ln X. Neither is attempted here.

**At 200 digits, without luck.** Joint optimisation does much better than
the asymptotic count suggests. Tempering on the 89 smallest odd primes
(3 to 463) finds covers that leave *no row at all* up to Q = 15,907:
`complete_cover_15907.txt` gives a class for each of the 89 primes such that
every one of the 1,852 odd primes q ≤ 15,901 lies in the class of some r,
and `complete_cover.py` checks it and prints N0 (193 digits). For every even
N = N0 + tM, of which 21,378,978 are below 10^200, each N − q with q an odd
prime below 15,907 is divisible by a prime ≤ 463: no prime below 15,907 is a
Goldbach summand of N, with no primality or compositeness test involved. That
is 0.7% of the ceiling, against 7.5% for the record found by search (160,357
since 24 November 17:11 UTC, on the 89-prime covers of `../fscan/cover/`): as with
prime gaps, what can be constructed is far behind what can be found. At
15,950 and at 16,000 the best covers found on these 89 primes leave one row;
where exactly complete covers stop is not known. Two more primes still fit
below 10^200: with 467 and 479 added (91 primes, 95 members below 10^200)
a complete cover reaches 16,381 (`complete_cover_16381_91primes.txt`, 1,898
rows, every N − q divisible by a prime ≤ 479; N0 has 198 digits). And one
prime beyond the Chinese-remainder line can be had by enumeration, exactly as
point 3 of "Why nothing known collects the prize" says: on 92 primes (to 487)
the modulus exceeds 10^200 fivefold, tempering found 17,131 complete covers
at 16,500 and 16,600, and 3,505 of them (20.5%, against 19.5% expected) have
their number below 10^200; the best certifies 16,747
(`complete_cover_16747_92primes.txt`: one 200-digit N with every N − q, q an
odd prime below 16,747, divisible by a prime ≤ 487). Two primes beyond the
line (93 primes, to 491; the modulus exceeds 10^200 by a factor 2,500):
60,437 complete covers at 16,850 and 16,950, of which 18 have their number
below 10^200 (24 expected), the best certifying 16,981
(`complete_cover_16981_93primes.txt`). Each further prime costs its own size
in covers to enumerate and has bought about 235 in the target so far. A 94th
prime (499; one complete cover in 1.25 million would fall below 10^200) was
tried and did not pay: complete covers exist up to at least 17,250, but only
a few hundred thousand could be enumerated at 17,000. So 16,981 is the best
found. All four certificates (15,907; 16,381; 16,747; 16,981) are checked by
the Lean kernel (`Records.lean` on the Lean branch, commit 9acf05d).

**The same question exactly, for few primes** (`desert.c`, `desert_fast.c`). Let D(n) be the
largest value, over all residue vectors on the first n odd primes r, of the
least odd prime q that lies in none of the chosen classes. For an N in those
classes every odd prime below D(n) is struck (N − q is divisible by some r),
and D(n) is the first prime that no choice of N strikes; the complete covers
above are lower bounds, D(89) ≥ 15,907 and D(93) ≥ 16,981 (they also had to
fit below 10^200, which D does not ask). A depth-first search on "which
modulus strikes the smallest unstruck prime" gives the exact values:

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r_n | 3 | 5 | 7 | 11 | 13 | 17 | 19 | 23 | 29 | 31 | 37 | 41 |
| D(n) | 5 | 7 | 19 | 31 | 43 | 67 | 103 | 163 | 181 | 223 | 271 | 331 |
| D(n) / (r_n ln r_n) | 1.52 | 0.87 | 1.39 | 1.18 | 1.29 | 1.39 | 1.84 | 2.26 | 1.85 | 2.09 | 2.03 | 2.17 |
| optimal vectors | | 2 | 1 | 2 | 2 | 6 | 6 | 1 | 2 | 1 | 17 | 9 |

| n | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r_n | 43 | 47 | 53 | 59 | 61 | 67 | 71 | 73 | 79 | 83 | 89 | 97 | 101 | 103 | 107 | 109 |
| D(n) | 419 | 499 | 613 | 709 | 739 | 859 | 907 | 1,051 | 1,213 | 1,279 | 1,381 | 1,471 | 1,567 | 1,669 | 1,801 | 1,933 |
| D(n) / (r_n ln r_n) | 2.59 | 2.76 | 2.91 | 2.95 | 2.95 | 3.05 | 3.00 | 3.36 | 3.51 | 3.49 | 3.46 | 3.31 | 3.36 | 3.50 | 3.60 | 3.78 |
| optimal vectors | 2 | 1 | 3 | 2 | 2 | 4 | 2 | 1 | 2 | 2 | 1 | 1 | | | | |

("Optimal vectors": how many of the ∏ r class vectors reach D(n). A search of
the OEIS for the first twelve values on 24 November 2026 returned no
sequence.)

The values to n = 7 are also the result of a brute force over all vectors;
the first fifteen come out the same from the Lean session's separate program
(D(15) = 613 took 1.6·10^10 nodes here, `desert_fast.c`, the same search on
bit sets and in parallel, and 1.8·10^10 there). D(16) to D(28) are from the
uarch session's versions of the search (`desert_fast3.c`, `desert_fast4.c`,
`desert_fast5.c` and their result files on branch `ccr-b8c25887-i6tn9f`,
commits a81cc6f to 3539913). The first of them keeps the search and the cut
and changes the order: the moduli that can strike the branching prime are
tried most-struck-primes-first, and the branching prime is the unstruck prime
with the fewest moduli still able to strike it. That takes D(15) from
1.6·10^10 nodes to 1.1·10^7 and D(18) to 2.9·10^8 nodes in half a minute;
it reproduces D(1) to D(15), gives the same D(16) to D(20) for two orders of
the children (D(20) in 4.9·10^9 nodes), and its vectors were rechecked here
(every odd prime below each of the values from 709 to 1,933 struck, the
value itself not). The latest version adds one lemma to the cut: if the
capacity of the free moduli exceeds the primes still unstruck by a margin,
then in any vector below the node that still succeeds every free modulus
sits in a class within that margin of its fullest one; classes that do not
qualify are never tried, a prime that no qualifying class strikes ends the
node, and a modulus with one qualifying class is forced. That cuts the tree
by another factor of 100 to 200 (the proof that nothing reaches beyond
1,279 at n = 22 takes 2.1·10^7 nodes instead of 5.0·10^9), gives D(23) in 82
seconds and D(24) in five minutes, and makes the count of optimal vectors
cheap; a further cut (two free moduli whose fullest classes share a prime
strike one prime fewer together) brought D(25) to D(27) within minutes. (An
array overflow in the version used for n = 25 to 27 was found and fixed by
that session on 24 November, commit 6caad7d; the three values were confirmed
by the fixed program, with identical node counts for the proof runs at 25
and 26, and the counts of optimal vectors for n ≥ 25 are being recomputed.) The search comes with checks that share little or no code with it:
this session's `desert_fast.c` with nothing but the order of the children
changed gives the same D(16) to D(20); a brute force over all vectors agrees
for n ≤ 9, including the number of optimal vectors; a SAT solver (CaDiCaL)
finds "strike every odd prime below the next prime after D(n)" unsatisfiable
and "below D(n)" satisfiable for n = 8, 10, 12 and 13, and its count of
optimal vectors agrees for n ≤ 12; each new cut can be switched off and the
answers stay the same; and D(24) = 1,471 is the value tempering had found
before any exhaustive search reached it. All of it
agrees, and the values to n = 9 are theorems checked by the Lean kernel, which runs a search
proved correct (`CoverDepth.lean`, `CoverDepthRun.lean`, commits 9dce329 and
747767d on `ccr-36ca7b46-8twf14`; beyond 9 the lower bounds are theorems to
n = 18, one vector each, as are the large covers). Formalising it, the Lean
session proved three things that make D more than a lower bound:

- g(N) ≤ D(n) for every even N, with n the number of odd primes up to √N: the
  residues of N itself strike every odd prime below its least summand. So D
  bounds the least Goldbach summand from above as well.
- If D(n) ≤ N − 3 for that n, then N is a sum of two primes, one of them at
  most D(n). So "D(n) < (next prime)² − 2 for every n" implies Goldbach's
  conjecture, and there is room where D is known: 163 against 841 at n = 8,
  499 against 2,809 at n = 14, 1,933 against 12,767 at n = 28. (With D(9) = 181 in the kernel, every even N from 6 to 960 is a sum of two primes, one of them at most 181, with no primality test of any N − q.)
- D is strictly increasing, and the first record holders of the least
  summand, N = 6, 12, 30 and 98, attain D(0) to D(3) = 3, 5, 7, 19 exactly;
  from 220 on the records fall short, because there are more residue vectors
  than even numbers below the next prime square.

At n = 89 and 93 the ratio D/(r ln r) is at least 5.6. So what can be had
without luck grows faster than the r·ln r of the theorem. How fast is not
known. A first-moment count (∏(r − 1) vectors with nonzero classes, each
prime struck with probability 1 − ∏(1 − 1/(r − 1)), primes treated as
independent) puts the end of complete covers at 359 for n = 8 (D = 163), 857
for n = 12 (D = 331), 32,300 for n = 89 (found: 15,907) and 34,600 for n = 93
(found: 16,981), of order r·ln² r asymptotically. The truth sits at 40 to
50% of that count wherever it is known, with no sign of approaching it, and
for a known reason: under a random vector the number of unstruck primes is
much less dispersed than independent strikes allow (a small modulus strikes
about the same number of primes whatever its class), so the count overstates
what exists. The same count at 170,000 predicts covers with about 790 rows
left where tempering finds 1,248. So the estimate is an upper guide, not a
target, and for N ≤ X (r about ln X) the luck-free desert lies somewhere
between the proven ln X·ln ln X and order ln X·(ln ln X)², far below the
ln² X·ln ln X expected with luck. No proof of anything beyond the constant
1.349 at order r·ln r is in sight: it would need the primes below y in
classes modulo primes almost as large as y. (The nearest object in the
literature we found is the paired Jacobsthal function of Ziller and Morack,
arXiv:1706.00317, where a bound on a covering of all integers of an interval
with two classes per prime implies Goldbach's conjecture; here the targets
are the primes only and there is one class per prime.)

**Formal status.** Proved by the Lean session, standard axioms only
(`goldbach/lean/GoldbachGaps/CoverBound.lean`, commit 4a747b6 on
`ccr-36ca7b46-8twf14`; statements verbatim in `COVERBOUND_STATEMENTS.md`
there). With "p is a summand of N" meaning p and N − p both prime:

- `eventually_exists_even_le_no_summand` (no hypothesis): for all large X
  there is an even N ≤ X, N > 0.73·ln X·ln ln X, with no summand below
  0.73·ln X·ln ln X. The constant comes from an elementary bound for the
  product, ∏_{3≤r≤w}(r−2)/(r−1) ≤ (1575/1152)/ln(w+1).
- `eventually_exists_even_le_of_mul_lt_one` (commit a4c5d0f): the same with
  every constant below e^γ/(2·C₂) = 1.349, with no hypothesis; and
  `eventually_exists_even_le_no_summand_six_fifths` with the explicit constant
  1.2. This rests on Mertens' third theorem, ln w · ∏_{p≤w}(1 − 1/p) → e^(−γ),
  which was not in Mathlib and which the Lean session proved from Mathlib alone
  (`Mertens.lean`, `mertens_third`, by the route of Hardy and Wright §22.7–8;
  an independent formal proof exists in the PNT+ project).
- The order ln X · ln ln X by counting was already there (`Counting.lean`,
  constant 1/48).

So the state of the question, as far as we can tell: order ln X · ln ln X with
constant 1/2 by counting (one unrefereed preprint); every constant below
1.349 by covering (here, formal and unconditional). At y = 463 the
theorem's count gives 3,830, a plain greedy choice of classes strikes every
prime below 10,428 (below), and tempering reaches 15,907: the factor 3 to 4
is rows sharing a mop-up prime, the improvement the theorem leaves as a
remark. The finite
instances are checked by the Lean kernel from the classes alone, by
divisibilities only (`Records.lean` on the Lean branch):
`exists_lt_ten_pow_200_complete_cover_15907`, `…_16381`, `…_16747`,
`…_16981`, and the progression forms for 89 primes (all 21,378,978 members
below 10^200) and 91 primes (95 members).

**Why 1.349 is not the truth, and what a proof of more would need** (a
sketch and measurements; nothing in this part is proved). In the theorem
each of the largest primes, about x/ln x of them, strikes one surviving
prime. It could strike more. Take y = C·x·ln x. A class of a prime r′ near x
holds about C of the primes below y, and each of them survives the small
primes with probability of order 1/ln x, so among the survivors, about
C·x/(1.349·ln x) of them, of the order of x/ln² x pairs share a class of r′.
If a proportion φ of the large primes could each be given two survivors,
disjointly, the constant would be 1.349·(1 + φ). A class of r′ holds only
about C primes in all, so at a fixed C the largest primes can never strike
more than a handful each. The covers actually found reach much further, to y
of the order of x·ln² x, and there a class of a prime near x holds of the
order of ln x primes (six at x = 10^5): the reach comes from the primes
above about x^0.6 each taking a class far fuller than the average one, as
measured below.

The simplest algorithm already does it, and its reach can be measured far
beyond the sizes where the exact value or tempering are available
(`greedy_cover.py`, `greedy_cover.txt`): take the odd primes r ≤ x in
increasing order and give each the nonzero class that holds the most primes
below y not yet struck; G(x) is a y for which nothing is left.

| x | 23 | 53 | 100 | 200 | 463 | 1,000 | 3,000 | 10^4 | 3·10^4 | 10^5 | 3·10^5 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G(x) | 126 | 372 | 1,021 | 3,315 | 10,428 | 30,184 | 132,567 | 601,525 | 2,298,470 | 9,650,028 | 34,610,715 |
| G(x) / (x ln x) | 1.75 | 1.77 | 2.22 | 3.13 | 3.67 | 4.37 | 5.52 | 6.53 | 7.43 | 8.38 | 9.15 |
| G(x) / (x ln² x) | 0.56 | 0.45 | 0.48 | 0.59 | 0.60 | 0.63 | 0.69 | 0.71 | 0.72 | 0.73 | 0.73 |

So with the primes up to 300,000 the greedy vector strikes every odd prime
below 34.6 million, 6.8 times what the theorem's count allows, and from
x = 10^4 on its reach is 0.71 to 0.73 times x·ln² x: the order of the
first-moment count, not of x·ln x. (For x = 23 and 53 the exact values are
D(8) = 163 and D(15) = 613; at x = 463 tempering has 15,907. The greedy
vectors for x = 463 and 1,000 were rechecked independently.) Every one of
these is an unconditional statement about the even numbers in one residue
class modulo the product of the primes up to x; what is missing is a proof
that the greedy choice keeps working for all x. The Lean session reproduced
the table with its own code (within a few percent: being struck is not
monotone in y and ties between classes matter, so each figure is one
threshold among several and a lower bound for what the rule can do; with
ties broken at random its 167 moduli up to 997 reach 32,971), and it
certified that point: `coversBelow_32971` (`Cover32971.lean`, commit 68d90e6
on `ccr-36ca7b46-8twf14`) is a kernel-checked proof, by divisibility alone,
that the odd primes up to 997 strike every odd prime below 32,971, where the
theorem's count at x = 997 gives 9,290. Tempering does better than greedy
on those 167 moduli, as it does at 463: it finds classes that strike every
odd prime below 40,111 (`complete_cover_40111_167primes.txt`, checked
independently; 0.84·x·ln² x and 4.3 times the theorem's count), and nothing
complete at 41,000 in runs of the same length. The best reach known for
each set of moduli, exact for the first three (1,471 was found by tempering and is D(24)) and by tempering for the others
(`complete_covers_97_199_293.txt`, `complete_cover_15907.txt`,
`complete_cover_40111_167primes.txt`):

| primes up to x | 23 | 53 | 97 | 199 | 293 | 463 | 997 |
|---|---|---|---|---|---|---|---|
| moduli | 8 | 15 | 24 | 45 | 61 | 89 | 167 |
| every odd prime struck below | 163 | 613 | 1,471 | 4,909 | 8,311 | 15,907 | 40,111 |
| / (x ln x) | 2.26 | 2.91 | 3.31 | 4.66 | 4.99 | 5.60 | 5.83 |
| / (x ln² x) | 0.72 | 0.73 | 0.73 | 0.88 | 0.88 | 0.91 | 0.84 |

(The last entry comes from shorter runs relative to its size and is probably
not the end. As a calibration of the method: tempering runs of 200,000 sweeps
reach the exact D(17), D(18), D(19) and D(20) in every one of three seeds,
where runs of 40,000 sweeps had stopped one prime short at n = 17 and 18.) Against x·ln x the reach keeps growing; against x·ln² x it is
between 0.7 and 0.9 throughout. Four of these sizes are theorems checked by
the Lean kernel from the classes alone (`scripts/cover_depth/README.md` on
the Lean branch, commits 68d90e6 to 8940e8c): 15,907 to 16,981 on 89 to 93
moduli, 32,971 (greedy) and 40,111 (the vector above) on the 167 moduli up to
997, 135,511 on the 429 moduli up to 2,999 (a greedy vector with ties broken
at random; the theorem's count there is 32,390) and 614,101 on the 1,228
moduli up to 9,973 (greedy; the count gives 123,900; the certificate is a
4,298-digit N checked by divisibility in 17 minutes); the tempered vectors at
24, 45 and 61 moduli are certified as well. A mean-field model of the
same procedure, in which the remaining primes fall into the classes of each
r like independent balls and the prime takes the fullest class
(`greedy_meanfield.py`), reaches 0.90·x·ln² x at x = 463 and 10^4, 0.86 at
10^5 and 0.84 at 3·10^5: the same order, a quarter above the real greedy
choice at small x (real primes are spread more evenly over the classes of a
small r than independent balls would be, and a class of a prime near x holds
only about C primes, which independent balls ignore), and slowly falling. So
the measured reach and the model agree on x·ln² x up to a factor that moves,
if at all, like ln ln x.

Pigeonhole cannot give this, because the survivors are fewer than the
classes, and the greedy choice of classes for the small primes leaves a set
one cannot control. With classes drawn at random for the small primes the
averages are computable: the expected number of survivors is the one the
greedy choice guarantees, and the expected number of surviving pairs in a
common class of r′ is a finite sum over the pairs of primes below y in a
common class, each weighted by its chance of surviving, ∏(1 − ν_r/(r − 1))
with ν_r the number of distinct residues of the pair modulo r. (For r = 3
this is zero unless the two primes are congruent modulo 3, since a class
modulo 3 strikes half of all primes; so only pairs congruent modulo 3 count,
with a factor 1/2, and the product runs from r = 5.) A deletion argument
(mark each such pair with a small probability; keep the large primes with
exactly one marked pair that meets no other marked pair) then gives a
positive proportion of large primes striking two survivors, provided two
counts are bounded above up to constants: the second moment of the pair
counts and the number of conflicts between pairs of different primes. Both
reduce to upper-bound sieves for primes r′ with v + j·r′ prime (Brun,
Selberg), which lose only constant factors. That would prove (1 + δ)·1.349
for some δ > 0. It is not written out and not formalised.

The Opus session measured every quantity of this outline (`goldbach/
balls_in_boxes/` on branch `ccr-c6e00296-3g7fp9`, commit 621315a; x from
3,000 to 100,000, C from 1 to 8, classes drawn at random for the primes up to
w = x/2 or x^0.9, twenty draws each). The survivors number what the product
formula says, within 1%. The pairs of survivors in a common class match the
exact expectation within 4%, and are 1.00 to 1.15 times the bound with
r = 3 treated as above. They are *not* what independent balls would give:
0.4 to 0.9 of it, and classes holding three or more survivors are far rarer
than Poisson, because of the cap of about C primes per class. The second
moment of the pair counts is at most 1.26 times the squared mean and tends
to 1; the conflict count is 4 in the normalisation where independent degrees
give 4. So the two bounds the outline needs hold with small constants. The
deletion step itself keeps 9 to 11% of the large primes at C = 1.35 (12 to
14% at C = 2), with no trend in x: carried through, the outline would give a
constant near 1.5, not 2. Letting the large primes simply take their fullest
class of survivors, in increasing order, does more and grows with x: with
random classes up to w = x^0.9, everything is struck up to C = 1.39, 1.93,
2.47 and 3.14 at x = 3,000, 10^4, 3·10^4 and 10^5 (1.12, 1.40, 1.56, 1.78
with w = x/2), the large primes striking two to four survivors each; the
all-greedy rule reaches 5.5 to 8.4 at the same x, so choosing the small
primes' classes well is worth another factor of 3 to 4.

Where the all-greedy reach comes from was measured the same way (`T3.md`
there, commit 323c674; x = 10^4, 10^5 and 10^6, targets the odd primes below
0.72·x·ln² x). For each prime r take the excess m − λ of the class it takes
(m targets) over the average class of what is left (λ). Classes taken without
looking would strike Σλ along the same path and leave about 0.74/ln x of the
targets, so the excess has to add up to that: of the order of x in all when y
is of the order of x·ln² x, which is of the order of ln x per prime.

- The measured excess is 0.454, 0.458 and 0.458 times ln x per prime at the
  three x.
- The small primes make the strikes and the large ones make the difference.
  At x = 10^5 the primes up to 113 make 85% of the strikes with classes 0 to
  5% fuller than average, as random classes would be, and 3.5% of the excess.
  The primes above x^0.8 make 5 to 6% of the strikes and 55, 63 and 71% of
  the excess at the three x; those above x^0.9 make 31, 37 and 44%, each
  taking 2.3, 3.0 and 3.9 targets more than an average class.
- At this y the limit of about C primes per class does not bind: a class of
  a prime near x holds 0.72·ln² x/ln y primes, six at x = 10^5 and eight at
  10^6, and the class taken is 0.92 to 0.97 of the fullest of independent
  Poisson cells. In the middle range (average class from 1,000 down to 1) the
  excess is 0.58 to 0.89 of what independent cells would give, because the
  primes left are spread over the classes more evenly than independent balls
  (close to what the Montgomery–Hooley variance for primes in progressions
  gives).
- Random classes for the primes up to x^θ and the fullest class above cost
  what that range contributes to the excess: the reach is 0.99, 0.98, 0.88,
  0.58 and 0.29 of the all-greedy one for θ = 0.2, 0.4, 0.6, 0.8 and 0.9 at
  x = 10^4, and 1.00, 0.99, 0.92, 0.67 and 0.38 at 10^5, within 0.05 of one
  minus the share of the excess made by the primes up to x^θ; that share
  falls with x at every θ. (The rule was then tested as a prediction at
  x = 10^6: it gives 0.92, 0.71 and 0.44 for θ = 0.6, 0.8 and 0.9, and the
  runs gave 0.95, 0.74 and 0.45; commit 8c2a7a8.) So a proof may leave the classes of the primes up
  to x^0.6 to chance, where the averages are computable, at the cost of a
  tenth of the reach, and has to control the fullest classes of the primes
  between x^0.6 and x.
- Greedy is not the limit either. On the 167 moduli up to 997 the tempered
  vector (40,111) behaves like greedy up to r = 233, takes the fullest class
  at 80% of the moduli and gives up 1% of the strikes on the way; in exchange
  its 56 largest moduli strike 2.41 targets each, 1.38 times the fullest of
  independent cells, where greedy's strike 2.02 (0.96 times) and 33 targets
  are left. A joint choice arranges what is left so that the last moduli
  collect more than chance allows.

For "every constant" the primes of a growing middle range must each strike
several survivors, nearly all of them, which is a near-perfect matching in a
hypergraph (Pippenger–Spencer, the Rödl nibble) and needs the degrees
asymptotically, not up to constants. That
is the machinery of Ford, Green, Konyagin, Maynard and Tao for long gaps
between primes, in an easier regime: there a class of a large prime holds far
fewer than one prime on average and rich classes have to be found with the
Maynard sieve; here it holds C, and a class of a prime in the middle range
holds many. So we state as a conjecture, supported by
D(n), by the covers and by the greedy table: for every A there are infinitely
many even N with no Goldbach summand below A·ln N·ln ln N; and, more
precisely, D(n) is of order r_n·ln² r_n up to a factor that varies at most
like ln ln r_n, so that the summands forced away by divisibility alone reach
about ln N·(ln ln N)².

For the frame, what is known from above (standard sieve theory, not written
out here): for every even N and every large y there is a prime q ≤ y with
N − q free of prime factors up to y^(1/4 − ε), by the linear sieve with the
Bombieri–Vinogradov theorem, uniformly in N; that is D(n) ≤ r_n^(4 + ε) for
large n. With level of distribution 1 (Elliott–Halberstam) the same argument
gives r_n^(2 + ε), and r_n² itself is the Goldbach barrier: the Lean session's
implication above says that D(n) < (next prime)² − 2 for all n is enough for
Goldbach's conjecture. So the proven window is r·ln r ≪ D(n) ≪ r^(4 + ε),
and the computed values (0.7 to 0.9 times r·ln² r for every n from 8 to 167
moduli) sit near its lower end.

At the campaign's own size there is now a certified bound from above as
well. The uarch session's `cover_ub.c` (branch `ccr-b8c25887-i6tn9f`, commit
3539913; written for this question and sharing no code with the searches
for D) exhausts the tree of class vectors on the 89 moduli 3 to 463 with the
capacity cut: fix the classes of the smallest moduli in turn, and stop
wherever the primes still unstruck outnumber the sum of the fullest classes
of all the free moduli. It proves that no vector strikes every odd prime
below Y for Y = 170,000 (6,240 nodes), 80,000, 60,000, 50,000, 45,000,
40,000 and 37,000 (6.9·10^8 nodes, twenty minutes). So

    15,907 ≤ D(89) < 37,000,

both ends certified: for every even N whatever, some odd prime q below
37,000 has N − q free of prime factors up to 463. The program is validated
on the first n odd primes for n = 2 to 27 (it finds a cover at D(n) and
proves there is none at the next prime) and against brute force on 6 and 7
moduli. The true end is near 16,000 (below); the bound is where the capacity
cut, which ignores that the classes of large moduli overlap, runs out of
strength.

**A floor under every cover** (`cover_floor.c`, `cover_floor.py`,
`cover_floor_q170000.txt`; measurements, not proofs). The searches say what
can be found; this says what exists. Fix the moduli and a target Q, let k(a)
be the number of odd primes below Q that the class vector a leaves, and
Z(β) = Σ e^(−β·k(a)) over all ∏ r vectors. The best vector alone contributes
e^(−β·k_min), so for every β > 0

    k_min ≥ −ln Z(β)/β.

Z(0) = ∏ r exactly, and ln Z(β) is measured by parallel tempering at all
temperatures: the change between neighbouring temperatures comes from their
two histograms (Bennett's acceptance ratio), so the floor at β uses nothing
colder than β, and no search has to succeed for it. It is as good as the
equilibrium at β, and the test of that is to make the same run from random
vectors and from the best vector known and to see where the two agree.

Checks against exact answers:

- Seven moduli, all 4.8 million vectors enumerated: the mean of k, the
  entropy and the floor agree with the exact values to 0.01 at every
  temperature, for plain rows and for weighted rows.
- D(n). A complete cover forces Z(β) ≥ 1. With the target scanned upward,
  complete covers are sampled up to the proven D(20) = 1,051 and
  D(21) = 1,213 and not beyond. The same scan gave 1,279 and 1,381 for
  n = 22 and 23 before this session had read the exhaustive results, which
  are 1,279 and 1,381; at n = 24 it gives 1,471.
- Counting complete covers. A vector with k = 0 has weight 1 at every
  temperature, so the complete covers sampled at any temperature are uniform
  over all complete covers at that target, and the share of them whose least
  unstruck prime is at least y is g0(y)/g0(Q), g0 being the number of
  complete covers. A chain of five runs at n = 20 follows ln g0 from 23.5 at
  700 through 11.6 (860), 6.5 (960) and 5.0 (1,020) to 0 ± 0.5 at 1,051,
  where the exhaustive count is one vector.
- A limit. Where complete covers are very few, runs of this length do not
  sample them in proportion: at n = 24, just below D(24), Z comes out thirty
  times too small although complete covers were sampled. The cold end of a
  run from random vectors is a search like any other.

At the campaign's size, the 89 smallest odd primes and Q = 170,000 (15,496
rows; random nonzero classes leave 1,853, the best cover known 1,248), two
runs of a million sweeps, one from random covers and one from that cover:

| β | 0.59 | 0.83 | 0.95 | 1.07 | 1.19 | 1.31 | 1.45 | 1.65 | 2.05 | 2.45 | 3.5 | 5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mean rows, random start | 1,557.6 | 1,461.2 | 1,420.3 | 1,386.0 | 1,357.5 | 1,334.0 | 1,312.6 | 1,291.9 | 1,270.3 | 1,261.9 | 1,254.8 | 1,250.4 |
| mean rows, start at the best cover | 1,557.8 | 1,461.2 | 1,420.2 | 1,385.3 | 1,355.5 | 1,330.4 | 1,307.3 | 1,285.9 | 1,266.2 | 1,256.8 | 1,249.7 | 1,248.3 |
| ln(number of covers that matter) | 358 | 290 | 253 | 218 | 184 | 153 | 121 | 88 | 52 | 31 | 12 | 6 |
| floor, start at the best cover | 951 | 1,112 | 1,154 | 1,182 | 1,201 | 1,214 | 1,224 | 1,232 | 1,241 | 1,244 | 1,246 | 1,247 |
| floor, random start | 951 | 1,112 | 1,154 | 1,182 | 1,201 | 1,214 | 1,225 | 1,234 | 1,243 | 1,247 | 1,250 | 1,251 |

- Up to β = 1.07 the two runs agree within a row in the mean and within 0.1
  in the floor, and up to β = 1.31 within 0.4 in the floor (in runs ten
  times shorter they still differed there by 14 rows in the mean and by 3 in
  the floor). So no cover on these moduli leaves fewer than about 1,214
  rows, 34 fewer than the best known, unless the equilibrium at that
  temperature is dominated by covers that neither start reaches in a million
  sweeps. In the rate of the search that is a factor 2.3 at the very most.
- Colder than that the run from random covers is out of equilibrium (its
  floor passes 1,248, which exists), and the other run is the one to read:
  1,241 at β = 2.05, 1,244 at 2.45, 1,247 at the cold end. There it is not a
  bound in the strict sense, because a run started at the best cover known
  cannot report a better one that it does not find, and after a million
  sweeps it has drifted a little above equilibrium itself (see the next
  point). What it shows is that the covers found sit where the number of
  covers runs out.
- The bottom, from the run started at the best cover: e^4.0 covers with
  1,248 rows (e^5.6 in the run ten times shorter, which had drifted less;
  186 different ones have been found, e^5.2), fifty times as many with
  1,249, then a factor 22 falling to 11 over the next nine rows. One row lower
  the count is of order one, so the best cover on these moduli has 1,247 or
  1,248 rows.

At the 10% target, Q = 213,070 (19,050 rows; the best cover known leaves
1,609), the same pair of runs with 300,000 sweeps
(`cover_floor_q213070.txt`): the two floors agree within 0.5 up to
β = 1.07, where the floor is 1,554, and within 1 up to β = 1.65, where it is
1,596; the run from the best cover ends at 1,608, with e^2.8 covers at 1,609.
For the fleet as it is, a cover would need about 1,470 rows at this target
for a 1% chance of the 10% record in the days that remain, 1,375 for a 10%
chance and 1,295 for an even chance (the planning model of
`../fscan/cover/brainstorm/`: 0.0243 nats per row). No cover on these moduli
comes within 80 rows of the first of these figures. Better covers are not a
way to 10%: on this side the search has what there is.

**How many complete covers there are: a law, and where they end** (the same
tools; runs here and on the Lean session's machine, whose raw output is in
`goldbach/lean/scripts/cover_floor_runs/` on its branch at 86f11bd and
5075080). Let g0(Q) be the number of class vectors on the odd primes up to x
that strike every odd prime below Q, so that D is the largest Q with
g0(Q) > 0 and g0(0) = ∏ r = e^θ(x). Measured as above (ln Z at the cold end
and the share of the samples there that leave no row), at eight sizes:

| x | moduli | θ(x) | targets Q | (θ − ln g0)·ln² x / Q | end of the fitted line | best cover known |
|---|---|---|---|---|---|---|
| 73 | 20 | 65.2 | 700 to 1,020 | 1.09 to 1.15 | 1,082 | 1,051 (exact) |
| 127 | 30 | 111.2 | 500 to 2,000 | 1.09 to 1.22 | 2,297 | 2,311 (tempering; a wall) |
| 199 | 45 | 187.9 | 1,000 to 4,000 | 1.02 to 1.09 | 5,099 | 4,909 |
| 293 | 61 | 276.3 | 1,500 to 7,000 | 1.02 to 1.13 | 8,687 | 8,311 |
| 463 | 89 | 442.9 | 4,000 to 14,000 | 1.006 to 1.05 | 16,300 (measured end: about 16,000) | 15,907 |
| 997 | 167 | 955.6 | 15,000 to 38,000 | 0.992 to 1.010 | 45,400 | 40,111 |
| 2,999 | 429 | 2,931.7 | 20,000 to 100,000 | 0.989 to 1.035 | 185,000 | 135,511 (greedy) |
| 9,973 | 1,228 | 9,895.3 | 100,000 and 300,000 | 1.006 and 1.012 | 827,000 | 614,101 (greedy) |

So the logarithm of the number of complete covers is a straight line in the
target, from the full count at Q = 0 down to the end:

    ln g0(Q) = θ(x) − c·Q/ln² x,    c = 1.00 within a few percent.

In other words a class vector drawn at random strikes every odd prime below Q
with probability e^(−Q/ln² x). At x = 463 ten targets from 500 to 14,000 lie
within 5 nats of one line (two seeds agreeing to 0.1 from 6,000 on; slope
1.013/ln² x, value at Q = 0 within 3.5 of θ); at x = 997 seven targets
from 15,000 to 38,000 lie within 7.5 of the line with c = 1 exactly; at the
smaller sizes the points step around it, as D(n) itself does, and the
fitted c is 1.02 to 1.13 (`cover_floor_law.txt` has every point; raw runs
made here are in `cover_floor_runs/count/`). Three things follow.

- D(n) = θ(r_n)·ln² r_n/c, that is r·ln² r with a constant near 1 at these
  sizes: 1,082 against the exact 1,051 at n = 20,
  and 16,300, 45,400 and 185,000 for 89, 167 and 429 moduli (the true end
  lies a few percent before the end of the line, see below).
- Tempering's 15,907 on the campaign's 89 moduli is at the end or within 1%
  of it (below), and the uarch session's exhaustive neighbourhood search
  from that cover (free up to 32 moduli, keep the rest, search exactly)
  finds nothing beyond it. At 167 moduli tempering is about 10% short, at
  429 and 1,228 moduli the greedy choice reaches 0.73 of the end of the
  line.
- The first-moment count of the earlier section is wrong by a known factor:
  it expects π(Q)·∏(1 − 1/(r − 1)) = 0.741·Q/(ln Q·ln x) for the loss, the
  law says Q/ln² x, larger by 1.349·ln Q/ln x (the constant e^γ/(2·C₂) of
  the theorem again). That is why the count put the end at 32,300 for 89
  moduli.

The last eighth of the range. Above about 85% of the way runs from random
vectors no longer sample the complete covers in proportion (they find a
handful and stay with them), so at 89 moduli the Lean session's machine also
ran a million sweeps from the known complete cover, which is complete at
every target up to 15,907 (commit de9d330 there):

| Q | 14,000 | 14,500 | 15,000 | 15,300 | 15,600 | 15,907 |
|---|---|---|---|---|---|---|
| ln g0, runs from random vectors | 61.7 | 38.7 | 19.8 | 0.9 | 1.6 | none sampled |
| ln g0, run from the complete cover | 62.9 | 42.2 | 29.2 | 20.5 | 16.6 | 3.5 |
| the line with c = 1 | 71.3 | 58.0 | 44.8 | 36.8 | 28.8 | 20.7 |

The two agree at 14,000 and the run from the cover is the one to read
beyond. The curve steepens over the last eighth (an average slope of
1.17/ln² x from 14,000 on) and reaches about thirty complete covers at
15,907. So complete covers on the campaign's 89 moduli end near 16,000, 4%
before the end of the line, and the cover found by tempering on 23 November
is the end or within 1% of it; the best covers found at 15,950 and 16,000
leave one row. At 167 moduli the line holds to 38,000 (1.010 and 1.006 at
36,000 and 38,000, two seeds within 2.2); at 39,000 and at 40,111, the
tempered record, runs from random vectors still count e^120 and e^77
covers, which are underestimates, so the end there is several thousand
beyond the record.

*Why a straight line with slope 1/ln² x* (a heuristic that reproduces the
form and, within about 15%, the constant; not a proof). Count the complete
covers modulus by modulus, smallest first. Let V(s, A) be the logarithm of
the number of ways the moduli from s on can finish when A rows are still
alive. The classes of s hold K alive rows each, with mean μ = A/(s − 1), and
V(s, A) = ln Σ over the classes of exp(V(s⁺, A − K)). With V = const − p·A,
a price p per alive row, this gives p before s equal to p after s minus
κ(p)/(s − 1), where μ·κ is the cumulant generating function of K. If the
alive rows fell into the classes like Poisson counts, κ = e^p − 1, the price
would be p = −ln(1 − ln s/ln x), infinite at the last modulus and equal to
∏(1 − 1/(r − 1)) at the first, and the loss would be the first-moment count.
They do not: measured on random vectors, the variance of the number of alive
rows in a class of s is b·(ln s/ln Q) times its mean, with b between 1.2 and
1.4 for every s above 30 at both sizes tried (x = 463 with Q = 10,000 and
x = 997 with Q = 25,000; below 30 it is smaller still). This is the law of
Montgomery and Hooley for primes in progressions, up to the constant: the
further Q is above the modulus, the more evenly the primes fill its classes.
With variance v times the mean, κ = (e^(vp) − 1)/v, and for v = b·ln s/ln Q
the price equation becomes, for y = v·p as a function of ln s,
dy/d(ln ln s) = y + e^y − 1. Its solution through y = ∞ at the last modulus
is y = K·(ln s/ln x)² for the small moduli, K = 1.516 (the exponential of
twice the limit of ∫ from y to ∞ of dt/(t + e^t − 1) plus ½·ln y). So the
price at the first modulus is (K/b)·(ln Q/ln x)·∏(1 − 1/(r − 1)), and the
loss is

    π(Q)·(K/b)·(ln Q/ln x)·2·C₂·e^(−γ)/ln x = (1.124/b)·Q/ln² x.

The factor ln Q that turns the number of rows into Q comes from the
dispersion law, so the line is straight whatever Q is, and its slope is a
constant over ln² x. With b = 1.12 the constant is 1; the measured b is 1.3
for most moduli and less for the smallest.

Two checks of the calculation, and what they say about c. First, what it
produces is π(Q)·ln Q rather than Q, and in the range measured that is 9 to
13% more than Q. Written with π(Q)·ln Q the measured constant is 0.89 to
0.93 at every size from 463 to 9,973, and the calculation gives 1.124/b,
which is 0.90 for b = 1.25. Second, the same price equation with a finite
price β at the end gives the whole partition function of the previous
section (the formula is given below, under "The same calculation above the
end"), and fitted to the run at
Q = 170,000 over the temperatures that are in equilibrium (β ≤ 0.6, where
θ − ln Z goes from 110 to 1,000) it reproduces θ − ln Z to one part in a
thousand with c = 1.027 and b = 1.196, where that b predicts c = 1.028; the
spread of the alive rows over the classes measured directly at that target
has b between 1.1 and 1.4 for the moduli above 30, as at 10,000 and 25,000.
So with the measured dispersion the constant comes out right.

*The dispersion derived, and the law with nothing fitted*
(`cover_dispersion.py`, `cover_price.py` and their `.txt` files). The spread
of the alive rows over the classes of s is a statement about pairs: two
primes q, q′ below Q in one class of s are both alive with probability
∏(1 − ν_t/(t − 1)) over the smaller moduli t, ν_t = 1 if t divides q′ − q
and 2 if not. Summed over the pairs with the Hardy–Littlewood count of
prime pairs at each difference, the weight of the sieve and the singular
series of the pair multiply to a function of the difference whose mean is
exactly the Poisson value: at leading order the classes are Poisson. The
departure is the second-order term of the average of singular series, the
−(H/2)·ln H in Σ over h ≤ H of (H − h)·𝔖(h) (Montgomery and Soundararajan),
the term that also makes the variance of primes in progressions x·ln q
instead of x·ln x. Taken over the differences 6·s·j it gives

    variance/mean = 1 − 6·φ(s)·(s/(s − 1))·(π(Q)/Q)·ln(Q/(6·s)),    φ(s) = ∏ over odd primes t < s of (1 − 1/(t − 1)),

with no constant to choose. Measured on random vectors against the formula:

| modulus s (Q = 10,000) | 43 | 71 | 101 | 131 | 163 | 193 | 263 | 337 | 463 |
|---|---|---|---|---|---|---|---|---|---|
| variance/mean measured | 0.47 | 0.59 | 0.67 | 0.72 | 0.75 | 0.75 | 0.82 | 0.80 | 0.85 |
| formula | 0.47 | 0.60 | 0.67 | 0.72 | 0.75 | 0.78 | 0.82 | 0.85 | 0.89 |

(the same within 0.04 at Q = 25,000 and 170,000 for every modulus above 50;
below about 30 the formula fails, the mean per class being no longer small
against Q/(6·s), and it is cut off at 0.02 in what follows, where those
moduli do not matter because their prices are small). With this dispersion
in the price recursion, the price before the first modulus being the largest
that the recursion can carry to the last one (any price there above ln x − 1
gives the same answer within 1%):

| x | 463 | 463 | 997 | 997 | 997 | 2,999 | 2,999 | 9,973 | 9,973 |
|---|---|---|---|---|---|---|---|---|---|
| Q | 10,000 | 14,000 | 15,000 | 25,000 | 38,000 | 50,000 | 100,000 | 100,000 | 300,000 |
| θ − ln g0 measured | 271 | 381 | 316 | 520 | 802 | 772 | 1,589 | 1,186 | 3,582 |
| by the recursion | 279 | 388 | 328 | 540 | 812 | 791 | 1,545 | 1,191 | 3,414 |
| by the first moment | 158 | 212 | 200 | 314 | 456 | 499 | 932 | 806 | 2,181 |

Within 1 to 5% at every point, where the first-moment count is off by a
factor 1.5 to 1.9. The end of complete covers by the same recursion:

| x | 73 | 107 | 109 | 127 | 149 | 199 | 251 | 293 | 349 | 397 | 463 | 599 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| moduli | 20 | 27 | 28 | 30 | 34 | 45 | 53 | 61 | 69 | 77 | 89 | 108 |
| end by the recursion | 1,123 | 1,997 | 2,113 | 2,389 | 3,001 | 4,969 | 6,607 | 8,467 | 10,391 | 12,577 | 15,973 | 22,109 |
| best cover known | 1,051 | 1,801 | 1,933 | 2,311 | 2,953 | 4,909 | 6,451 | 8,311 | 10,159 | 12,163 | 15,907 | 21,067 |
| recursion / known | 1.07 | 1.11 | 1.09 | 1.03 | 1.02 | 1.01 | 1.02 | 1.02 | 1.02 | 1.03 | 1.00 | 1.05 |

(The first three are exact values of D; 2,311, 2,953 and 6,451 are walls,
where the Opus session's tempering stopped one row short at the next target
in runs four times longer; from 349 on the best cover is limited by run
length.) And beyond what any search has reached:

| x | 997 | 2,999 | 9,973 | 30,000 | 100,000 |
|---|---|---|---|---|---|
| moduli | 167 | 429 | 1,228 | 3,244 | 9,591 |
| end by the recursion | 44,917 | 194,203 | 905,951 | 3.51·10^6 | 1.51·10^7 |
| / (x·ln² x) | 0.95 | 1.01 | 1.07 | 1.10 | 1.14 |
| best cover known (tempering at 997, greedy beyond) | 40,111 | 135,511 | 614,101 | | 9.65·10^6 |

So the recursion gives the luck-free depth within 5% wherever it can be
checked from 30 to 108 moduli (and 7 to 11% too high below that, where D(n)
moves in steps of 5 to 10% from one n to the next), and at the campaign's 89 moduli it
gives 15,973 where the measurement says about 16,000 and tempering found
15,907. The constant of the law is therefore not a number but a slowly
moving quantity: by the recursion the loss falls slowly against
π(Q)·ln Q/ln² x as x grows (0.93 at 89 moduli, 0.86 to 0.88 at 1,228), and
D(n)/(r·ln² r) rises from 0.84 at 20 moduli to about 1.1 at 10,000. Where
that ends is not settled here. In the closed formula the correction to
Poisson classes is of order 1/ln x, which would take the law to the
first-moment count and D(n)/(r·ln² r) to e^γ/(2·C₂) = 1.349, the constant of
the theorem; but the closed formula stands for the full Hardy–Littlewood sum
only as far as it has been compared with it (Q up to 300,000, where the two
give 0.86 and 0.88), and for the moduli in the middle the full sum may keep
a correction of order one. So the limit of D(n)/(r·ln² r), if there is one,
lies between the 1.1 seen at the largest sizes and 1.349.

A caution on the two largest sizes in the tables. The runs at 2,999 and
9,973 moduli are short (20,000 and 12,000 sweeps), and the one at
Q = 300,000 was not in equilibrium: its mean row counts at the middle
temperatures were still falling by 1 to 2% between the first and the last
quarter, which makes the measured loss too large. The recursion says by how
much: a long run should give 3,330 to 3,414 there, not 3,582 (and about
1,545 instead of 1,589 at 2,999 moduli and Q = 100,000). That is a
prediction, made before the long runs (which the Lean session's machine is
making) are in.

*The same calculation above the end: how few rows a cover can leave.* With
a finite price β for a row left at the end, instead of an infinite one, the
price equation gives the whole partition function of the previous section,

    ln Z(β) = θ(x) − c·(Q/ln² x)·E(b·β·ln x/ln Q),    E(y) = exp(−2·∫ from y to ∞ of dt/(t + e^t − 1)),

with E(y) = y/K for small y (so that ln Z = θ − β·(rows left by random
classes) at high temperature, as it must be) and E → 1 as β → ∞ (the
counting law). For Q beyond the end D the entropy of this ensemble reaches
zero at a finite temperature, where no covers are left to count; that is at
y* with E(y*) − y*·E′(y*) = D/Q, and the rows left there are K·E′(y*) times
those left by random classes:

| D/Q | 0.5 | 0.3 | 0.2 | 0.134 | 0.096 | 0.077 | 0.05 | 0.02 | 0.01 |
|---|---|---|---|---|---|---|---|---|---|
| fewest rows left / rows left by random classes | 0.22 | 0.37 | 0.48 | 0.57 | 0.63 | 0.67 | 0.73 | 0.83 | 0.88 |

For large Q the ratio is 1 − √(K·D/Q), K = 1.516: what the best cover saves
over a random one is a share of the rows that falls like the inverse square
root of the target. Nothing in the table is fitted, and it depends on the
moduli only through D. On the campaign's 89 moduli (with D = 16,300; random
nonzero classes leave 1,853 rows at 170,000 and 2,278 at 213,070) it gives
1,172 and 1,527 rows; the floors measured above are 1,214 to 1,248 and 1,554
to 1,609, and the best covers found have 1,248 and 1,609 (ratios 0.673 and
0.706 against the predicted 0.633 and 0.670). So this smooth version is 5 to
6% on the optimistic side. Run instead with the derived dispersion and the
actual moduli (`cover_price.py floor 463 170000`: the recursion with a
finite price at the end, and the temperature at which its entropy reaches
zero), it gives 1,221 rows at 170,000 and 1,584 at 213,070: within 2% of the
1,248 and 1,609 of the best covers found, from the Hardy–Littlewood count of
prime pairs and nothing else. The covers of the campaign are not good by
accident of search; they are where the count of covers runs out.

The same formula covers the table of Result 3, which was made the day
before with a different sampler and for a different purpose. A number below
10^200 has 460 nats to spend on its residues, whatever the depth z, so the
count of such numbers with few rows left at depth z runs out where the
entropy above equals θ(z) − 460 instead of zero: put D = 460·ln² z/c in the
table. At the 10% target (19,050 rows):

| depth z | 463 | 1,000 | 2,000 | 5,000 | 20,000 | 50,000 |
|---|---|---|---|---|---|---|
| rows left by random classes | 2,278 | 2,037 | 1,853 | 1,655 | 1,425 | 1,305 |
| predicted fewest rows of any N < 10^200 | 1,505 | 1,262 | 1,081 | 888 | 665 | 550 |
| cutoff of the ideal search, measured (Result 3) | 1,620 | 1,319 | 1,116 | 910 | 685 | 574 |

(The cutoff of the ideal search lies a few rows above the fewest that exist:
11 at depth 463, where the fewest is 1,609.) So the prize of Result 3, the
3.5 to 14.8 nats that an ideal search to depth 1,000 to 50,000 would be
worth, is the same quantity as the floor under the covers, seen at other
depths: one function of 460·ln² z/Q.

*What of this is proved.* The object is: the Lean session defined the count
and proved the identity behind it in the kernel (`CoverCount.lean`, commit
c9354bc on `ccr-36ca7b46-8twf14`, standard axioms): g0(x, Q)/∏ r is the sum
over all sets T of rows of (−1)^|T|·∏(1 − ν_r(T)/r), ν_r(T) the number of
residues of T modulo r; g0 decreases as rows are added; it is positive
exactly when a cover exists, so D is where it reaches zero (instance:
g0(29, 181) > 0 and g0(29, 182) = 0). It also proved the one rigorous bound
on the loss there is: a cover on fewer moduli stays a cover whatever the
other classes are, so ln g0(x, Q) ≥ θ(x) − θ(x′) whenever the odd primes up
to x′ cover the odd primes below Q, stated for the ten certified covers
(for x ≥ 997 the loss at Q = 15,907 is at most θ(463) = 442.9, where the law
says 334). And the constant K is 1.5164516079595025850511213122…, enclosed
to 28 digits by exact rational arithmetic (`scripts/cover_count/` there).
The law itself and its derivation are a measurement and a heuristic; an
upper bound for g0 of this shape would bound D(n) by a multiple of r·ln² r
and prove Goldbach's conjecture for large N, by the implication above.

**Conjecture (counting law).** For Q between x and a fixed fraction of
θ(x)·ln² x, the number of class vectors modulo the odd primes up to x that
strike every odd prime below Q is exp(θ(x) − c·π(Q)·ln Q/ln² x), where c is
given by the price recursion above: 0.91 ± 0.02 for x from 463 to 9,973 (the
same as 1.00·Q/ln² x there), and between that and 2·C₂·e^(−γ) = 0.741 for
larger x. Consequently D(n) = κ_n·r_n·ln² r_n with κ_n between 0.84 and 1.14
for 20 to 10,000 moduli and at most e^γ/(2·C₂) = 1.349 in the limit, and the
least Goldbach summand that divisibility by the primes up to ln N alone can
force is of the exact order ln N·(ln ln N)².

## Ladder

| rung | what | who | state |
|---|---|---|---|
| 1 | Toy theorem (parity) and corollary, formal proof, Stickelberger–Swan included | Lean | done: proved without hypotheses (`FunctionField/ParityDesert.lean`, `Stickelberger.lean`, commit c0e3fb4 on the Lean branch), with two extensions (any degree; smooth derivative) |
| 2 | Toy search with the parity filter: measure the factor against the model | research | done: 4 to 5 times (Result 2) |
| 3 | An instance small enough to enumerate every member: does anything predict the best members beyond what the model contains? | both | done over the integers (every even N below 10^9, "The same thing in miniature"): nothing beyond the tilt of the residues, the size, and rows shared by numbers closer than Q; not done in F_q[x] |
| 4 | Barrier statements for the integer search, formal | Lean | done (Lean branch, `Cap/BlackBox.lean`, `Cap/Radius.lean`, `Cap/Population.lean`, `Cap/ListGain.lean`, `Cap/Thinning.lean`): black-box bound (m questions reach the fraction m·g/K); inside the decoding radius only one-class lists pay for themselves, which is the cover (`list_deficit`, `johnson_leaves_the_cover`), and the radius is at least 3.88 times the typical agreement for K = 2^32; the population bound in Chernoff form (`hitMass_selected_le`: m tests on a population of e^F expect at most m·y^k + e^F·u^(−k)·∏(1 − s_j + s_j·y·u) successes however the members were found); the meet-in-the-middle condition ln P ≤ 2F − C (`mitm_condition_log`) |
| 5 | Integer candidates for information that is not a residue (anything cheaper than a Fermat test that correlates with primality of a rough number, in a special family of N) | both | open; no candidate yet |
| 6 | Constants: wheel and list merges inside the production sieve | research | costed at 0.1 to 0.4 nats, not started |
| 7 | The prize: number of N by rows left at depth z, and the cost of an ideal search | research | done for z up to 50,000 at the 10% target (Result 3): 3.5, 5.9, 8.8, 12.6, 14.8 nats |
| 8 | Problem (P′): any method that reaches beyond the Chinese-remainder line at less than the cost of scoring every member | both | open; lattices, meet in the middle, birthday trees and hashing ruled out with numbers (above) |
| 9 | A provable lower bound for the largest g(N), and the largest g certified by factors alone at 200 digits | both | done: every constant below 1.349 times ln X · ln ln X, unconditional (`CoverBound.lean`, `Mertens.lean`); 16,981 (`Records.lean`) |

## References

- W. Sawin, M. Shusterman, On the Chowla and twin primes conjectures over
  F_q[T], Annals of Math. 196 (2022).
- R. G. Swan, Factorization of polynomials over finite fields, Pacific J.
  Math. 12 (1962) (Stickelberger's theorem; Pellet's formula).
- B. Conrad, K. Conrad, R. Gross, Prime specialization in genus 0, Trans.
  Amer. Math. Soc. 360 (2008); K. Conrad, Irreducible values of polynomials:
  a non-analogy.
- V. Guruswami, A. Vardy, Maximum-likelihood decoding of Reed–Solomon codes
  is NP-hard (2005). Q. Cheng, D. Wan, on the decodability of Reed–Solomon
  codes and discrete logarithms.
- A. Granville, J. van de Lune, H. J. J. te Riele, Checking the Goldbach
  conjecture on a vector computer, in Number Theory and Applications (1989).
  W. Shi, A matrix-theoretic exact formula for counting primes in intervals
  between consecutive odd squares, arXiv:2605.21529 (2026), for the counting
  lower bound on the least Goldbach prime.
- K. Manders, L. Adleman, NP-complete decision problems for binary quadratics,
  J. Comput. System Sci. 16 (1978) (Garey–Johnson problem AN1).
- M. Naor, B. Pinkas, Oblivious transfer and polynomial evaluation, STOC 1999
  (noisy polynomial interpolation as a hardness assumption). D. Wagner, A
  generalized birthday problem, CRYPTO 2002.
- D. Bleichenbacher, P. Nguyen, Noisy polynomial interpolation and noisy
  Chinese remaindering, EUROCRYPT 2000. O. Goldreich, D. Ron, M. Sudan,
  Chinese remaindering with errors (1999). D. Boneh, Finding smooth integers
  in short intervals using CRT decoding (2000). V. Guruswami, A. Sahai,
  M. Sudan, Soft-decision decoding of Chinese remainder codes (2000).
