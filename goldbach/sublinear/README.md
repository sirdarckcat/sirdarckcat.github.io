# Finding deserts without trying the numbers one by one

A research programme started on 23 November 2026, at the user's request, by
this session (experiments, number theory) and the Lean session (proofs). This
file is the running record of what has been tried, what is proved, what is
only measured, and what is open.

**Where it stands (25 November, midday).** No method was found, and the
reason is now understood and quantified. The results of 24 November sharpen
it; they are in "A floor under every cover" and the sections after it:

- The covers in use are the best there are. A measurement that needs no
  search to succeed (the partition function over all class vectors, run from
  a random start and from the best cover and compared) puts a floor of 1,214
  rows under every cover on the 89 moduli at Q = 170,000 where the two starts
  agree, and 1,247 or 1,248 at the bottom; the best cover found has 1,248.
  That floor is measured; the certified one (exhaustive, uarch session)
  stands at 777. Covers
  come in families fixed by the classes of the smallest moduli; thirteen
  families were searched to the bottom one by one and the fleet's is the
  best (`../fscan/cover/README.md`). At the 10% target no cover comes within
  80 rows of what a 1% chance would need. So better covers are not a way to
  10%.
- A law, and its correction. The number of class vectors on the odd primes
  up to x that strike every odd prime below Q is exp(θ(x) − c·Q/ln² x) with
  c = 1.00 ± 0.03, measured from 45 to 1,228 moduli. A recursion derives it,
  constant included and nothing fitted, from the Hardy–Littlewood count of
  prime pairs: within 6% of the measured loss at all 24 counts from 89 to
  1,228 moduli (1 to 5.6% high in the lower half of the range, within 1.6%
  near the end), where the first-moment count is off by a factor 1.5 to
  1.9. Figures were written down before they were measured: the loss at 429
  moduli (1,545 predicted; 1,541 and 1,542 found), the count at the end of
  the 167 moduli (within 1.5%), D(35) (near 3,110, between 3,040 and 3,190:
  it is 3,079), and twelve counts of the Opus session on 138, 238 and 302
  moduli (all within 3.5%). The mechanism has been checked on complete
  covers themselves: the class a cover chooses strikes e^(v·p) times an
  average class, as the price of the derivation says, within about 20%
  while that factor runs from 1 to 185. The same calculation gives how few
  rows the best cover can leave: within 2% at the campaign's targets, 4 to
  14% low for targets nearer the end of complete covers, for a reason that
  is understood (a frozen level takes the largest of its counts, which the
  rate function puts a row too high).
- No limit is known, and two that were claimed here are withdrawn. On the
  24th: D(n) ~ 1.1275·r·ln² r, the limit of the recursion as first written
  (the Lean session refereed its arithmetic and found it right, with the
  caveat that it was the recursion's limit only). On the 25th I found what
  the caveat hides: the recursion lets the small moduli choose classes
  they do not have the entropy to choose (in its own solution the entropy
  of a prefix of the moduli goes negative, by 8 nats on the campaign's 89
  moduli at the end of complete covers and by 219 at 1,228 moduli). That
  part stands and was confirmed directly: among 1.1 million sampled
  complete covers on 167 moduli near the end, the 41 smallest moduli occur
  in six settings, against 40,000 settings far from the end, and the frozen
  part ends where the constrained recursion puts it. With the constraint in
  (the same recursion with weights, a convex minimisation) complete covers
  of the kind that searches find end at 0.91 to 1.01 times r·ln² r from 89
  to 25,996 moduli, turning down after about a thousand. But I then
  concluded that D(n) is of order r·ln² r/ln ln r in the limit, and that
  was wrong: the Lean session's second read the same day showed that
  frozen moduli need not behave like random classes. Classes taken from one
  common integer on the middle moduli (the block of Erdős and Rankin) leave
  fewer rows than any random-like choice, by a factor that grows without
  bound. It makes no difference while the largest modulus is below about
  10^25, but it gives
  a theorem on paper, D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)², which beats every
  bound of the order r·ln r (the consultant session wrote the proof out;
  the Lean session is formalising a corollary), and it leaves the order of
  D(n) open. At 200 digits nothing moves: complete covers on the 89 moduli
  end at 15,907 to 15,919 by the recursion in both forms, where 15,907 has
  been found; rigorously 15,907 ≤ D(89) < 35,000, the upper end by an
  exhaustive search of the uarch session. Exact values of D(n) are known to
  n = 35, and covers complete to 41,659, 70,111 and 98,731 on 167, 238 and
  302 moduli (Opus session), the first of them certified in the Lean
  kernel.
- The other direction, proposed by the user on the 25th: fix the gap and
  ask how few digits N needs. The same calculation prices it (a closed form
  for the split between cover and luck), and it gives records that need no
  GPU. First results the same day: two 400-digit numbers with no Goldbach
  summand below 200,293 and 206,593, found by the uarch session in under
  two CPU-hours and certified in the Lean kernel, then a 347-digit number
  with g = 216,289; about 319 and 300 digits are running, and 2,196 digits
  for a gap of 1,000,000 (2,480 held). Section "The other direction".

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
  ≤ 491, certified by divisibility alone. Since 25 November the first has a
  successor on paper of a higher order, c·ln X·(ln ln X)²·ln₄ X/(ln₃ X)²
  (the block of Erdős and Rankin; "A provable lower bound").
- A third by-product is exact and small: D(n), how far the first n odd primes
  can strike every prime with no luck, is 5, 7, 19, 31, 43, 67, 103, 163,
  181, 223, 271, 331, 419, 499, 613, 709, 739, 859, 907, 1,051, 1,213, 1,279,
  1,381, 1,471, 1,567, 1,669, 1,801, 1,933, 2,137, 2,311, 2,521, 2,647, 2,749, 2,953, 3,079 for n = 1 to 35 (`desert.c`; two programs to n = 15, the uarch
  session's faster search beyond, and the Lean kernel to n = 9). It grows faster than the r·ln r of the theorem:
  like r·ln² r at every size computed, by the law above (its order in the
  limit is open; it is at least r·ln² r·ln₃ r/(ln₂ r)², on paper).
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
ln ln X / ln ln ln X. Neither was attempted when this was written. Since
then (25 November) the consultant session has written out the first
(`goldbach/gaps_map/PAIR_COVER.md` on `ccr-cdb2641a-5zg8un`, commit 09ff251):
a matching of large primes to pairs of remaining rows, chosen by a deletion
argument in expectation over random classes on the small primes, gives an
explicit constant 1.3523 in place of 1.349 from Lavrik's long-range
almost-all theorem for prime pairs and Selberg's upper bounds (1.479 if the
second moments had their predicted values); its two open points are named
there (the exact form of the long-range theorem with a congruence
condition, and an averaging lemma for the survival weights), so it is a
proof on paper pending those, not a theorem here. Counting alone cannot
beat 1.349 in any order of the moduli.

Both are overtaken, as to order, by a third device that was proposed here
on 22 November, lost from this file, and brought back by the Lean session's
referee read of 25 November: the block of Erdős and Rankin. Give all the
primes t in (z, y/4] the class of one common integer N₁ in (Q, 2Q]; they
then strike every prime q for which N₁ − q has a prime factor in that
range, and what is left is a share of order ln ln y/ln y of the rows, on
average over N₁ (which needs only Chebyshev, Brun–Titchmarsh and a count of
smooth numbers, no sieve for prime pairs). The primes up to z take their
fullest classes and the primes above y/4 one row each. With
ln z = ln y·ln₃ y/(3·ln₂ y) this covers every odd prime below
c·y·ln² y·ln₃ y/(ln₂ y)², so that

    max over even N ≤ X of g(N) ≥ c·ln X·(ln₂ X)²·ln₄ X/(ln₃ X)²     for all large X

(ln₂ = ln ln, and so on): more than A·ln X·ln ln X for every A. The proof
is written out in `goldbach/gaps_map/COHERENT_BLOCK.md` (consultant
session, commit 0761b84 on `ccr-cdb2641a-5zg8un`), read by its author and
by me; the finite skeleton (a fixed layer, a pigeonhole layer and a mop-up
layer) is `Cap/Layers.lean` in the Lean library, kernel-checked since 22
November, and the Lean session began on 25 November to formalise the
corollary for every A. At the sizes of this project the block is worse than
what tempering finds (it overtakes random classes only near y = 10^25), so
this is a theorem about large X and changes nothing at 200 digits.

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
| optimal vectors | 2 | 1 | 3 | 2 | 2 | 4 | 2 | 1 | 2 | 2 | 1 | 1 | 2 | 12 | 10 | 1 |

| n | 29 | 30 | 31 | 32 | 33 | 34 | 35 |
|---|---|---|---|---|---|---|---|
| r_n | 113 | 127 | 131 | 137 | 139 | 149 | 151 |
| D(n) | 2,137 | 2,311 | 2,521 | 2,647 | 2,749 | 2,953 | 3,079 |
| D(n) / (r_n ln r_n) | 4.00 | 3.76 | 3.95 | 3.93 | 4.01 | 3.96 | 4.06 |
| D(n) / (r_n ln² r_n) | 0.85 | 0.78 | 0.81 | 0.80 | 0.81 | 0.79 | 0.81 |

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
and 26.) D(29) to D(35) are from a different program of the same session,
`cover_ub.c` driven by `findD.py` (commits 8ce578b and later): it climbs
from the previous value through better and better covers and ends with the
proof that no vector strikes every odd prime below the next prime (5.2·10^7
nodes at n = 29, 9.0·10^9 at n = 35, an hour); the seven vectors
were rechecked here. Its count mode gives the same number of optimal vectors
as the first program at every n from 2 to 28. Three of these values were known in advance by
other means: D(29) = 2,137 was predicted here before the search ran, as
D(22) to D(24) had been, from a scan of targets with the sampler of the
next sections (complete covers sampled at every target up to the prime
before 2,137; at 2,137 the best vector leaves one row and the measured
floor is positive), and D(30) = 2,311 and D(34) = 2,953 are the walls at
which the Opus session's tempering had stopped. The search comes with checks that share little or no code with it:
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
n = 35, one vector each (`CoverDepthMore.lean`, commit 673c39d), as are the
large covers; the upper bounds beyond 9 rest on the exhaustive searches). Formalising it, the Lean
session proved three things that make D more than a lower bound:

- g(N) ≤ D(n) for every even N, with n the number of odd primes up to √N: the
  residues of N itself strike every odd prime below its least summand. So D
  bounds the least Goldbach summand from above as well.
- If D(n) ≤ N − 3 for that n, then N is a sum of two primes, one of them at
  most D(n). So "D(n) < (next prime)² − 2 for every n" implies Goldbach's
  conjecture, and there is room where D is known: 163 against 841 at n = 8,
  499 against 2,809 at n = 14, 3,079 against 24,647 at n = 35. (With D(9) = 181 in the kernel, every even N from 6 to 960 is a sum of two primes, one of them at most 181, with no primality test of any N − q.)
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
complete at 41,000 in runs of the same length; sampling the complete covers
at 40,111 from that vector has since reached 40,459
(`complete_cover_40459_167primes.txt`, found by the Opus session on 24
November with the sampler of the later sections, checked here: all 4,239 odd
primes below 40,459 struck, every class nonzero, 49 of the 167 classes shared
with the earlier vector; certified in the Lean kernel, `Cover40459.lean`,
commit 3ccf2f0 there), and the same session's tempering at 41,000, started
from the 40,111 cover with four times the earlier budget, reached 41,047
(`complete_cover_41047_167primes.txt`, checked here: all 4,294 odd primes
below it struck, every class nonzero, and only 7 classes shared with the
40,111 cover: it is in another family; certified in the kernel as well,
`Cover41047.lean`, commit 9470f08), and then 41,659 at the end of that
search (`complete_cover_41659_167primes.txt`, checked here: all 4,357 odd
primes below it struck, every class nonzero; the next target, 41,768, was
missed by one or two rows in four seeds; certified in the kernel,
`Cover41659.lean`, commit 673c39d). The best reach known for
each set of moduli, exact for the first three (1,471 was found by tempering and is D(24)) and by tempering for the others
(`complete_covers_97_199_293.txt`, `complete_cover_15907.txt`,
`complete_cover_41659_167primes.txt`):

| primes up to x | 23 | 53 | 97 | 199 | 293 | 463 | 997 |
|---|---|---|---|---|---|---|---|
| moduli | 8 | 15 | 24 | 45 | 61 | 89 | 167 |
| every odd prime struck below | 163 | 613 | 1,471 | 4,909 | 8,311 | 15,907 | 41,659 |
| / (x ln x) | 2.26 | 2.91 | 3.31 | 4.66 | 4.99 | 5.60 | 6.05 |
| / (x ln² x) | 0.72 | 0.73 | 0.73 | 0.88 | 0.88 | 0.91 | 0.88 |

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

The same averages go further than pairs. At y = C·x·ln x there are about C
primes below y in an average class of r′, whatever the primes do (there are
that many more primes than classes), and a set of j of them survives the
random small classes with probability of order 1/ln^j x when its residues
leave a class free modulo each small r; so the expected number of classes of
r′ holding j survivors is of order x·C^j/ln^j x, unbounded for every fixed j
and C. That is the count behind "every constant": D(n)/(r_n·ln r_n) → ∞,
which the law above makes precise as ln r_n. What is missing for a proof is
not this count but the step that is hard in the work of Ford, Green,
Konyagin, Maynard and Tao on long gaps between primes: each modulus strikes
one class only, and the classes chosen must between them reach almost every
survivor.

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
40,000, 37,000 and 35,000 (2.6·10^7, 1.1·10^8 and 4.6·10^8 nodes for the
last three with the final build, an hour for the last). So

    15,907 ≤ D(89) < 35,000,

both ends certified: for every even N whatever, some odd prime q below
35,000 has N − q free of prime factors up to 463. (The count of nodes grows
fourfold for every 2,000 taken off Y there, and the walk was stopped.) The program is validated
on the first n odd primes for n = 2 to 27 (it finds a cover at D(n) and
proves there is none at the next prime) and against brute force on 6 and 7
moduli. The true end is near 16,000 (below); the bound is where the capacity
cut, which ignores that the classes of large moduli overlap, runs out of
strength.

The same program gives certified floors at the campaign's target (commit
b081d24 there): fix the classes of the first j moduli in every way and bound
the rest by their fullest classes. Every class vector on the 89 moduli
leaves at least 401 of the 15,496 odd primes below 170,000 unstruck (j = 6,
3 seconds), at least 644 (j = 8, 4.5 million nodes, three minutes) and at
least 777 (j = 10, 7.3·10^8 nodes, three and a half hours on one thread);
two moduli more cost 42 times the nodes from j = 6 to 8 and 163 times from
8 to 10, and it stops there. These
are theorems about every cover, where the 1,247 or 1,248 of the next section
is a measurement: the certified floor is 62% of the best cover known, and
the gap between them is again
the overlap of the classes of the large moduli, which the capacity cut does
not see. That session measured how fast the cut weakens with size: on 30
moduli, where D = 2,311, the proof that nothing reaches Y takes 115 nodes at
Y = 3·D, 4.2·10^5 at 1.2·D, 5.6·10^6 at 1.1·D and 5.6·10^7 at the next prime
after D; on 89 moduli 10^8 nodes buy Y = 2.3·D (the 37,000 above). At a fixed
ratio Y/D the cut loses four to five orders of magnitude between the two
sizes.

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

The same on the measure the fleet ranks covers by, rows weighted by what
they cost the expected record, on its 89 moduli (3 to 461 and 491), a million
sweeps from each start (`cover_floor_w491.txt`): the two floors agree up to
β = 1.19 (1,264.1 and 1,264.4 weighted rows) and within 0.6 at β = 1.31
(1,276.6 and 1,277.2); the run from the best cover of the fleet's family
ends at 1,308.6, the cover itself having 1,308.67, with e^3.6 times as many
covers for each weighted row above it; the run from random vectors comes
down to 1,309.36 on its own.

What the one-sided part of these floors covers has to be said with care,
after the families of the next section. A run started from a cover stays,
at the cold temperatures, in that cover's family (the classes of the dozen
smallest moduli: here 11.8 to 12 of 12 kept from β = 2 on), so the count at
the bottom and "1,247 or 1,248" are statements about the family of the best
cover and about every family the warm temperatures feed into it. The run
from random vectors ends in another family, 0.7 weighted rows above. Other
families are searched one by one in `../fscan/cover/README.md` ("Families at
the campaign's target").

**How many complete covers there are: a law, and where they end** (the same
tools; runs here, on the Lean session's machine, whose raw output is in
`goldbach/lean/scripts/cover_floor_runs/` on its branch at 86f11bd, 5075080
and 972bb6e, and by the Opus session, `goldbach/tempering_covers/floor/` on
`ccr-c6e00296-3g7fp9` at 1028072). Let g0(Q) be the number of class vectors on the odd primes up to x
that strike every odd prime below Q, so that D is the largest Q with
g0(Q) > 0 and g0(0) = ∏ r = e^θ(x). Measured as above (ln Z at the cold end
and the share of the samples there that leave no row), at thirteen sizes,
with the exact count at nine moduli (every vector enumerated by the Lean
session, `scripts/cover_count/g0_exact.c` at 4edfa27) for comparison:

| x | moduli | θ(x) | targets Q | (θ − ln g0)·ln² x / Q | end of the fitted line | best cover known |
|---|---|---|---|---|---|---|
| 29 | 9 | 21.9 | every Q from 59 to 181 (exact) | 1.17 to 1.45 | | 181 (exact) |
| 73 | 20 | 65.2 | 700 to 1,020 | 1.09 to 1.15 | 1,082 | 1,051 (exact) |
| 127 | 30 | 111.2 | 500 to 2,149 | 1.09 to 1.22 | 2,297 | 2,311 (tempering; a wall) |
| 149 | 34 | 131.0 | 1,772 to 2,746 | 1.09 to 1.13 | 2,947 | 2,953 (a wall) |
| 199 | 45 | 187.9 | 1,000 to 4,000 | 1.02 to 1.09 | 5,099 | 4,909 |
| 251 | 53 | 231.4 | 3,871 to 5,999 | 1.04 to 1.07 | 6,656 | 6,451 (a wall) |
| 293 | 61 | 276.3 | 1,500 to 7,000 | 1.02 to 1.13 | 8,687 | 8,311 |
| 349 | 69 | 322.6 | 6,095 to 9,448 | 1.03 to 1.07 | 10,406 | 10,159 |
| 397 | 77 | 370.0 | 7,298 to 11,312 | 1.02 to 1.06 | 12,460 | 12,163 |
| 463 | 89 | 442.9 | 4,000 to 14,000 | 1.006 to 1.05 | 16,300 (measured end: about 16,000) | 15,907 |
| 599 | 108 | 562.3 | 12,640 to 19,592 | 1.01 to 1.06 | 21,852 | 21,067 |
| 997 | 167 | 955.6 | 15,000 to 38,000 | 0.992 to 1.010 | 45,400 | 41,659 |
| 2,999 | 429 | 2,931.7 | 20,000 to 100,000 | 0.988 to 1.035 | 191,000 | 135,511 (greedy) |
| 9,973 | 1,228 | 9,895.3 | 100,000 and 300,000 | 1.006 and 1.012 | 827,000 | 614,101 (greedy) |

(The rows at 149, 251, 349, 397 and 599 and the targets above 2,000 at 127
are the Opus session's: four targets each, at 60, 75, 85 and 93% of the reach
of its tempering, 400,000 sweeps, two seeds; four of its runs re-read here
with `cover_floor.py` give its numbers. At 2,999 the target 100,000 is the
mean of two runs of 150,000 sweeps on the Lean session's machine, 1,390.4 and
1,389.7. The sampler itself is checked against the exact count: on the nine
moduli it gives ln g0 within 0.03 of the enumeration at Q = 59, 113, 149, 167
and 181, and within 0.09 along the reach of its complete covers, 42 values
compared.)

So the logarithm of the number of complete covers is a straight line in the
target, from the full count at Q = 0 down to the end:

    ln g0(Q) = θ(x) − c·Q/ln² x,    c = 1.00 within a few percent.

In other words a class vector drawn at random strikes every odd prime below Q
with probability e^(−Q/ln² x). At x = 463 ten targets from 500 to 14,000 lie
within 5 nats of one line (two seeds agreeing to 0.1 from 6,000 on; slope
1.013/ln² x, value at Q = 0 within 3.5 of θ); at x = 997 seven targets
from 15,000 to 38,000 lie within 7.5 of the line with c = 1 exactly; at the
smaller sizes the points step around it, as D(n) itself does, and the
fitted c is 1.02 to 1.13, rising to 1.17 to 1.45 in the exact count at nine
moduli (`cover_floor_law.txt` has every point; raw runs
made here are in `cover_floor_runs/count/`). Three things follow.

- D(n) = θ(r_n)·ln² r_n/c, that is r·ln² r with a constant near 1 at these
  sizes: 1,082 against the exact 1,051 at n = 20,
  and 16,300, 45,400 and 191,000 for 89, 167 and 429 moduli (the true end
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
36,000 and 38,000, two seeds within 2.2). Beyond that the Opus session ran
both kinds of start (`x997_report.md` on its branch; 400,000 sweeps, two
seeds each):

| Q | 39,000 | 40,111 |
|---|---|---|
| ln g0, runs from the 40,111 cover | 130.5, 129.8 | 98.57, 98.60 |
| ln g0, runs from random vectors | 119.1, 121.3 | 79.9, 74.3 |
| by the recursion, closed formula (on record before the runs) | 124.1 | 101.0 |
| by the recursion, whole pair sum | 132.4 | 110.2 |

The runs from the cover are steady over the four quarters and agree between
seeds to 0.7 and 0.03; the measured loss is within 1.5% of both versions of
the recursion at both targets. The runs from random vectors count 10 and 20
nats fewer, and that session found what is behind it. They settle in a
different family of classes for the moduli up to 41 (7:5, 13:7, 19:18, 23:8,
31:10, 41:7 against the cover's 7:3, 13:11, 19:3, 23:21, 31:7, 41:38), while
the runs from the cover keep the cover's classes on the first twelve moduli
and move freely on the rest; and a run started from the best vector of the
other family counts e^95.0 and e^94.2 there, steady and staying in that
family. So at 40,111 the two families hold e^98.6 and e^94.6 complete
covers, 4 nats apart, and the runs from random vectors had simply not
arrived: near the end the complete covers are split into families by the
classes of the smallest moduli, a run counts the family it is in, and it
moves between families only at temperatures where it is far from complete.
The reach of the samples at 40,111 in the first family gives the count
beyond: e^95.9 at 40,177, e^95 at 40,189, e^91 to e^95 at 40,237 and e^88 at
40,387 (the last from 51 samples), about 10 nats in the first 276, 1.8 times
the slope of the line; one of the samples is complete to 40,459. The family
with more covers at 40,111 is not the one that reaches furthest: the covers
complete to 41,047 and to 41,659 are in a third one, close to the second on
the moduli up to 41. Extrapolating the last interval, complete covers on the
167 moduli end at or below about 43,600, so that 41,659 is 96% of the way or
more (and 91 to 93% of the recursion's end, 44,900 to 45,600).

The Opus session measured the same stretch at six more sizes, 30 to 108
moduli (`floor_report.md` on its branch). The curve bends down before the
end at every one of them: in units of 1/ln² x the slope is 1.02 to 1.12 from
Q = 0 to the target at 60% of the reach, and 1.22 to 1.64 over the last
interval, from 85 to 93%. Runs started from the best tempered cover agree
with the runs from random vectors at the 85% targets where it was tried (397
moduli: 69.4 against 69.4 and 69.2; 599 moduli: 111.5 against 111.8 and
111.6) and at the 93% targets up to 349 moduli; at the 93% targets of 397 and
599 moduli the run from the cover counts more (36.3 against 34.4 and 35.2;
61.4 against 55.3 and 55.9), as it does at 89 moduli. The straight line
through the three targets below the bend ends between 0.5% short of the
tempered reach and 6% beyond it, the line through the last interval within
4% of it. So from 30 to 108 moduli, as at 89, tempering reaches the end of
the complete covers or comes within a few percent of it.

*Families.* The two families at 167 moduli are the rule and not an accident
of that size. Call a frame one nonzero class for each of the six smallest
moduli (92,160 frames) and a family the class vectors that share it; the
sampler can hold a frame fixed (`COVER_FLOOR_FRAME`, checked against a brute
force on seven moduli) and count the complete covers of one family. On the
45 moduli up to 199, for 24 frames drawn at random at each target:

| Q (share of the way to 4,909) | 2,000 (41%) | 3,000 (61%) | 4,000 (81%) |
|---|---|---|---|
| ln g0, all families together | 110.7 | 79.2 | 38.4 |
| the same per frame, if all families held equal shares | 99.3 | 67.8 | 27.0 |
| ln g0 of a family: mean over the 24 | 89.5 | 46.3 | 15 of 24 have no complete cover |
| standard deviation, lowest and highest | 3.7; 83.0 to 99.4 | 9.2; 30.2 to 63.9 | highest 25.4 |
| rows the frame leaves alive, range over the 24 | 68 to 79 | 94 to 113 | 123 to 137 |
| correlation of ln g0 with that number, and slope | −0.91; −1.38 per row | −0.96; −1.86 per row | −0.85; −2.9 per row (9 families) |

So a typical family holds e^(−10) of an equal share at 41% of the way and
e^(−21) at 61%, and at 81% most families hold nothing: the complete covers
sit in a small minority of the families, and more so the nearer the end.
Which families is decided almost entirely by one number, the rows that the
frame's six classes leave alive: each row more costs the family 1.4 nats at
41% of the way, 1.9 at 61% and 2.9 at 81%. That slope is the price of an
alive row of the recursion above, here measured directly, and it rises
toward the end as the recursion says it should. (At 4,000 the families with
at most 128 rows alive have complete covers and those with 134 or more have
none.) This is also the natural reading of the bend before the end: the
recursion adds up the classes of each modulus as if there were many of them,
and for the smallest moduli, where the price is high near the end and the
classes are few, the sum is carried by the best class alone.

Far above the end, at the campaign's target, the count of rows left alive
orders the families only roughly (see `../fscan/cover/README.md`, "Families
at the campaign's target"): the family all the fleet's covers belong to is
121st of the 92,160 by that count, and the dozen that leave the fewest rows
alive are 9 to 16 rows worse than it at equal effort.

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
| θ − ln g0 measured | 271 | 381 | 316 | 520 | 802 | 772 | 1,542 | 1,186 | 3,582 |
| by the recursion | 279 | 388 | 328 | 540 | 812 | 791 | 1,545 | 1,191 | 3,414 |
| by the first moment | 158 | 212 | 200 | 314 | 456 | 499 | 932 | 806 | 2,181 |

Within 5% at every point, where the first-moment count is off by a factor
1.5 to 1.9 (the entry at 2,999 moduli and Q = 100,000 is from the long runs
described below; the last column is a short run that was not in
equilibrium). The Opus session's 24 points, measured after this was written
down and with no part in it (`cover_price.py loss`, listed in
`cover_price.txt`):

| x | 127 | 149 | 251 | 349 | 397 | 599 |
|---|---|---|---|---|---|---|
| moduli | 30 | 34 | 53 | 69 | 77 | 108 |
| measured loss / recursion at 60, 75, 85, 93% of the reach | 1.05, 1.04, 1.05, 1.04 | 1.04, 1.01, 1.00, 1.04 | 0.98, 0.98, 0.98, 1.00 | 0.96, 0.97, 0.97, 1.01 | 0.96, 0.99, 0.98, 1.01 | 0.97, 0.97, 0.99, 1.02 |
| measured loss / first moment | 1.76 to 1.93 | 1.77 to 1.93 | 1.71 to 1.86 | 1.69 to 1.86 | 1.68 to 1.85 | 1.69 to 1.85 |

Within 4% from 53 moduli on and within 5.4% at 30 and 34, at every target.
The recursion is a smooth calculation and does not know about the bend
before the end, which shows as the last ratio of each column being the
largest, by 2 to 3%, from 53 moduli on. The end of complete covers by the
same recursion:

| x | 73 | 107 | 109 | 127 | 149 | 199 | 251 | 293 | 349 | 397 | 463 | 599 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| moduli | 20 | 27 | 28 | 30 | 34 | 45 | 53 | 61 | 69 | 77 | 89 | 108 |
| end by the recursion, closed formula | 1,123 | 1,997 | 2,113 | 2,389 | 3,001 | 4,969 | 6,607 | 8,467 | 10,391 | 12,577 | 15,973 | 22,109 |
| end by the recursion, whole pair sum (below) | 1,014 | 1,837 | 1,993 | 2,251 | 2,851 | 4,832 | 6,481 | 8,318 | 10,327 | 12,553 | 16,069 | 22,308 |
| best cover known | 1,051 | 1,801 | 1,933 | 2,311 | 2,953 | 4,909 | 6,451 | 8,311 | 10,159 | 12,163 | 15,907 | 21,067 |
| closed formula / known | 1.07 | 1.11 | 1.09 | 1.03 | 1.02 | 1.01 | 1.02 | 1.02 | 1.02 | 1.03 | 1.00 | 1.05 |
| pair sum / known | 0.96 | 1.02 | 1.03 | 0.97 | 0.97 | 0.98 | 1.00 | 1.00 | 1.02 | 1.03 | 1.01 | 1.06 |

(The first three are exact values of D; 2,311, 2,953 and 6,451 are walls,
where the Opus session's tempering stopped one row short at the next target
in runs four times longer; from 349 on the best cover is limited by run
length.) And beyond what any search has reached:

| x | 997 | 1,499 | 1,999 | 2,999 | 9,973 | 30,000 | 100,000 | 300,000 | 1,000,000 |
|---|---|---|---|---|---|---|---|---|---|
| moduli | 167 | 238 | 302 | 429 | 1,228 | 3,244 | 9,591 | 25,996 | 78,497 |
| end by the recursion, whole pair sum | 45,607 | 79,974 | 115,729 | 197,124 | 912,464 | 3.51·10^6 | 1.50·10^7 | 5.46·10^7 | 2.21·10^8 |
| / (x·ln² x) | 0.96 | 1.00 | 1.00 | 1.03 | 1.08 | 1.10 | 1.13 | 1.14 | 1.16 |
| / (x·ln² x) with the closed formula | 0.95 | 0.98 | 0.99 | 1.01 | 1.07 | 1.10 | 1.14 | 1.16 | 1.19 |
| best cover known (tempering to 1,999, greedy beyond) | 41,659 | 70,111 | 98,731 | 135,511 | 614,101 | | 9.65·10^6 | | |

(The covers at 1,499 and 1,999 are the Opus session's, 160,000 sweeps from
random starts, checked here: `complete_cover_70111_238primes.txt` and
`complete_cover_98731_302primes.txt`, 0.875 and 0.855 of x·ln² x and 88 and
85% of the recursion's end. Its whole series of tempered reach over x·ln² x
(not at one budget: the runs from covers and from random vectors had different
lengths, see Finding 1 of its README), for x = 127, 149, 251, 349, 397, 599, 797, 997, 1,499, 1,999,
is 0.775, 0.792, 0.842, 0.849, 0.856, 0.860, 0.870, 0.876, 0.875, 0.855: the
first two are exact values of D, and from about 600 on it is the budget and
not the end that stops the search, most at the largest size.)

So the recursion gives the luck-free depth within 4% wherever it can be
checked from 20 to 89 moduli, the three exact values of D included, and at
the campaign's 89 moduli it gives 15,973 or 16,069 where the measurement
says about 16,000 and tempering found 15,907. The uarch session's exact
values for 29 to 33 moduli arrived after these tables were made:

| moduli | 29 | 30 | 31 | 32 | 33 | 34 | 35 |
|---|---|---|---|---|---|---|---|
| D(n), exact | 2,137 | 2,311 | 2,521 | 2,647 | 2,749 | 2,953 | 3,079 |
| end by the recursion, whole pair sum | 2,125 | 2,251 | 2,383 | 2,557 | 2,707 | 2,851 | 3,024 |
| end by the recursion, closed formula | 2,270 | 2,390 | 2,552 | 2,700 | 2,834 | 3,002 | 3,192 |

The pair sum is 0.5 to 5.5% below the exact value at the seven sizes, the
closed formula 1 to 6% above. The last column was a forecast: with 3,024 and
3,192 in hand and the first six columns, "near 3,110, and a surprise outside
3,040 to 3,190" was sent to the uarch session before its search for D(35)
ran; the search gave 3,079.

*The whole pair sum instead of the closed formula* (`cover_price_hl.py`,
`cover_price_hl.txt`). The closed formula for the dispersion stands for a sum
over prime pairs, and that sum can be done whole. The weight of the pair
(q, q + 6·s·j) is, exactly,

    W(j) = a·c·∏ over the primes t dividing j of (1 + u_t),    u_t = 2/(t − 3) for the moduli t < s,  1/(t − 2) for the primes t > s,

where a = 6·s/(s − 1) is its mean (the Lean session's `sum_pair_weight`) and
c = ∏(1 + u_t/t)^(−1). Put R(m) = a·m − Σ over j ≤ m of W(j); it is positive
and grows slowly (like ln² m for m below s and like ln m/(2·φ(s)) beyond).
Then

    variance/mean = 1 − (φ(s)/li(Q))·[2·Σ over m of R(m)·(L2(6sm) − L2(6s(m + 1))) + a·L2(0)],

L2(d) being the Hardy–Littlewood integral for the difference d. Every term
has one sign, so nothing cancels and the sum can be taken at any size.
Against the Monte Carlo of the table above it is within 0.03 for every
modulus from 41 up at the three sizes tried, and closer than the closed
formula at both ends of the range (s = 337 at Q = 10,000: measured 0.80, pair
sum 0.80, closed formula 0.85; s = 43 at Q = 170,000: 0.34, 0.35, 0.30). In
the recursion it gives the ends of the two tables above: the smallest sizes
come out right, where the closed formula was 7 to 11% high. For the losses
below the end it is the other way round: measured over pair sum is 0.93 to
1.02 at the Opus session's 24 points (0.96 to 1.05 with the closed formula)
and 0.95 to 1.01 at the eight points in equilibrium of the first table (0.96
to 1.00). From 167 moduli on the two versions agree within 1.5%. So the
recursion is good to about 5% whichever way the dispersion is taken, and the
better dispersion does not make it better: what is left is in the recursion
itself (one price per row, and class counts of scaled-Poisson shape).

*The mechanism checked on covers themselves* (`cover_tilt.py`,
`cover_tilt.txt`). The recursion says more than a count: after the modulus s
the remaining problem prices an alive row at p_s, so the class chosen for s
should strike e^(v_s·p_s) times the rows of an average class. That can be
looked at directly. On 1,500 complete covers at Q = 12,000 on the 89 moduli
(sampled by one tempering run), modulus by modulus, smallest first:

| modulus s | 11 | 19 | 43 | 71 | 101 | 163 | 193 | 229 | 263 | 337 | 373 | 409 | 443 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rows alive before s, along the covers | 442 | 330 | 238 | 188 | 154 | 108 | 90 | 73 | 59 | 36 | 25.5 | 16 | 7.1 |
| the same for random vectors | 450 | 348 | 277 | 247 | 229 | 208 | 201 | 195 | 190 | 183 | 180 | 177 | 174 |
| rows struck by the chosen class / mean of a class | 1.11 | 1.31 | 1.84 | 2.38 | 2.81 | 4.70 | 5.97 | 7.27 | 8.18 | 17.8 | 22.9 | 40 | 94 |
| the recursion's e^(v·p) | 1.08 | 1.30 | 1.90 | 2.48 | 3.13 | 4.96 | 6.02 | 7.35 | 9.17 | 15.7 | 22.3 | 33 | 60 |
| fullest class / mean, along the covers | 1.13 | 1.32 | 1.89 | 2.49 | 3.17 | 5.15 | 6.52 | 8.46 | 9.80 | 20.2 | 26.7 | 45 | 103 |

The factor by which a complete cover beats an average class grows from 1.1
at the small moduli to 20 and more near the end, and the recursion has it
within 16% at every modulus up to s = 263, with nothing fitted (the file has
all of them); from 293 on the covers strike more than it says (by 31% at
293, 14% at 337, 3% at 373, 23% at 409, 56% at 443), as a cover comes to take
very nearly the fullest class. The same on 1,000 complete covers at
Q = 30,000 on the 167 moduli up to 997: the factor runs from 1.0 at the
smallest moduli to 185 at s = 971, and measured over predicted stays between
0.79 and 1.18 at every modulus listed, the covers striking 5 to 17% less
than the recursion says for the moduli from 40 to 260 and 10 to 18% more
over the last hundred. So the prices are not a device for getting the
count right: they are what the covers do. One thing the recursion does not
do, and it was tried: along the covers the alive rows are a thinned set and
their dispersion over the classes is higher than for random vectors (0.65
against 0.49 at s = 43, 0.81 against 0.65 at 101, 0.95 against 0.79 at 263,
close to what independent thinning of the random-vector figure gives), but
putting that dispersion into the recursion makes it worse, not better (the
loss comes out 8 to 22% too small at the 36 points measured, where the
dispersion of random vectors gives it within 7%). The recursion as it
stands is the consistent approximation at the level of pairs of rows, and
the correction for thinning belongs to an order it does not have.

*Where the constant ends up* (`cover_limit.py`, `cover_limit.txt`; a
heuristic like the rest, nothing fitted; this is the limit of the recursion
as it was on 24 November, and "The entropy of the small moduli" below
withdraws it as a statement about D(n)). The pair sum has a limit shape. To
leading order R(m) = (a·c/2)·M(m), where M(m) = Σ over squarefree d ≤ m of
u(d), u(d) the product of the u_t over the primes of d: a sum of dimension 2
over the primes below s and of dimension 1 above. Write
M(s^ρ) = g₂·ln² s·m(ρ). Then

    m(ρ) = ρ² for ρ ≤ 1,    ρ·m′(ρ) = 2·m(ρ) − m(ρ − 1) for ρ > 1,    m(ρ) = 2·e^γ·(ρ − 1) for large ρ

(the last both from solving the equation, to six digits, and from Mertens'
theorem applied to M directly, which is a check on the equation). The
constants combine exactly, c·g₂ = 1/(24·C₂), and with α = ln s/ln Q the
dispersion tends to

    v(α) = 1 − (e^(−γ)/2)·α·m((1 − α)/α):

1 at the last moduli, 1 − e^(−γ)/4 = 0.86 at α = 1/2, and 2α for α below 0.2.
So the moduli in the middle keep a correction of order one for ever: the
classes never become Poisson, and the first-moment count is off by a
constant factor in the limit as well. (This v/α is the b of the first
heuristic above: 1.2 to 1.4 at the sizes measured, 2 in the limit for the
small moduli.) At finite size the dispersion lies
below this limit by c(α)/ln Q, where c(α) falls from about 4 at α = 0.1
through 1.8 at α = 1/2 to 0.3 at α = 0.85, the same within 0.1 at
Q = 10^6, 10^7 and 10^8.

The price recursion becomes dp/d(ln α) = (e^(v(α)·p) − 1)/v(α), with p
infinite at the last modulus, where α = λ = ln x/ln Q, and p = Λ(λ)·α for
small α. The law then reads

    ln g0(x, Q) = θ(x) − 2·C₂·e^(−γ)·Λ(ln x/ln Q)·Q/ln² Q.

Independent rows would give Λ = 1/λ, the first-moment count. With the limit
profile Λ(1) = 1.19639 (the same program returns 1.0001 for independent rows
and K = 1.516452 for v = α, as it must). Since ln x/ln D tends to 1, the
limit of the law is

    ln g0 = θ(x) − 0.887·Q/ln² x,    D(n)/(r_n·ln² r_n) → e^γ/(2·C₂·Λ(1)) = 1.1275,

against 1.349 for independent rows. The approach is slow and not monotonic,
because two corrections of opposite sign die out at different rates: the
dispersion is below its limit by c(α)/ln Q, which lowers D, and ln x/ln D is
below 1 by about 2·ln ln x/ln x, which raises it. With both in the continuum
equation D/(x·ln² x) is 1.09 at x = 10^4, 1.14 at 10^5 and 1.16 at 10^6 (the
recursion over the actual primes gives 1.08, 1.13 and 1.16),
reaches a maximum of 1.20 between 10^12 and 10^15, and comes down through
1.19 at 10^20 and 1.17 at 10^50 to 1.14 at 10^200. So the c = 1.00 of the
law at the sizes measured is where the two corrections happen to leave it
between 100 and 1,000 moduli; by the recursion the constant at the end is
0.92 at 1,228 moduli, 0.88 at 10^5, 0.83 at the maximum of D/(x·ln² x), and
0.887 in the limit.

A referee's read (the Lean session, 25 November; `scripts/cover_limit_check/`
on its branch, commit a1c77dc, with exact sums of u(d) up to 10^11). None of
the four steps is wrong, and three of them now have their first correction
in closed form:

- R against M. On the mean over m, R(m) = (a·c/2)·M(2π·m) − a/2 (from
  Σ f(j)·j^(−w) = ζ(w)·Σ u(d)·d^(−w)); the −a/2 cancels the term a·L2(0) of
  the dispersion exactly. Checked to 0.05 on values of 40 to 140.
- The equation for m. It follows from an exact identity for M(x)·ln x, and
  the next term is a shift of the argument: M(s^ρ) =
  g₂·ln² s·[m(ρ) + (2γ + ln 12)·m′(ρ)/ln s + …]. Below s, M(x) =
  g₂·(ln² x + 7.27868·ln x + 5.5170) to 10^(−5), g₂ = 0.0874661499. The
  leading term alone is far off at any size one can sum (a factor 2.16 at
  ρ = 1 for s = 1,009, 1.56 for s = 1,000,003); with the first correction it
  is within 0.7%.
- The constants. 24·C₂·c·g₂ = 1 to ten digits, and the correction measured
  above comes out of the same expansions:
  c(α) = (e^(−γ)/2)·[(2γ + ln 4π − 1)·m′(ρ₀) + α·m(ρ₀)], ρ₀ = (1 − α)/α. That
  is 2.35, 1.65, 1.08 at α = 0.4, 0.5, 0.6, against 2.38, 1.59, 1.08
  extrapolated from the pair sums here; below α = 0.3 it is 10 to 20% under
  them (the moduli there are below 100).
- The price equation. With the same dispersion on both sides, the recursion
  over the actual primes gives 0.957, 0.983, 0.991, 0.995, 0.996, 0.997 of
  the continuum Λ at x = 10^3 to 10^8, and the largest price that can be
  carried is flat in the end price, so it is the solution that blows up at
  the last modulus.

One thing is not justified, and it comes before the first step: all of this
is the limit of the recursion. The recursion takes the dispersion of the
alive rows from random class vectors, while the sum over classes that it
models is taken along covers, where the dispersion differs (0.65 against
0.49 at s = 43 in `cover_tilt.txt`); the tilt e^(v·p) of a modulus is of
order one in the limit, so nothing makes that difference vanish as x grows.
Where it has been measured the recursion is within about 5% of the loss, of
either sign. So 1.1275 is the constant of the recursion's limit; whether
D(n)/(r·ln² r) has the same limit depends on that closure, which is open.

*The entropy of the small moduli: the limit does not hold* (`cover_price_prefix.py`,
`cover_price_prefix.txt`; found here on 25 November, after the referee's
read; what I first concluded from it about the limit was wrong, and the end
of this section says how). The
caveat has a definite content. At a modulus s the recursion's solution has
the chosen class hold e^(v·t) times the mean number of rows still alive, t
the price after s. There are only s − 1 classes, so a class that full is
there only if the smaller moduli have arranged it, and that takes entropy:
with μ rows alive per class,

    entropy of the level = ln(s − 1) − μ·(t·e^(v·t) − (e^(v·t) − 1)/v).

The levels sum to ln g0. But the sum over the moduli up to s is the
logarithm of the number of ways those moduli can be set as the count
assumes, and it cannot be negative. In the recursion it is:

| moduli | 89 | 138 | 167 | 238 | 302 | 429 | 1,228 |
|---|---|---|---|---|---|---|---|
| target | 15,907 (the end) | 28,766 | 40,111 | 65,203 | 91,820 | 100,000 | 300,000 |
| lowest entropy of a prefix, nats | −8 | −22 | −43 | −77 | −119 | −73 | −219 |
| at the modulus | 113 | 113 | 157 | 199 | 271 | 181 | 337 |

A modulus far below x has classes of many rows each and next to no entropy
of its own, so the choice the recursion gives it does not exist. The
deficit grows with the size, and at 1,228 moduli it is there at a third of
the reach. With the constraints "every prefix has entropy ≥ 0" the count is
a constrained maximum, and its dual is the same recursion with weights:

    ln g0 = min over w_s ≥ 1, non-increasing in s, of  Σ w_s·ln(s − 1) − π(Q)·p_start(w),
    p_s = p_{s⁺} − (w_s/(s − 1))·κ_s(p_{s⁺}/w_s)

(w = 1 is the recursion as it was; a constant w is the freezing of a
random-energy model; the derivative of the bound in the multiplier of a
prefix is that prefix's entropy, so a convex minimisation finds it). The
moduli with w > 1 are frozen: their classes are the same in nearly all
complete covers. These are the families of the runs. At 167 moduli and
40,111, where the runs keep the classes of the first twelve moduli and two
families hold e^98.6 and e^94.6 complete covers, the entropy of the first
twelve moduli is 0.2 nats with the constraint and −16 without. And the
runs at 1,228 moduli that would not come to equilibrium at 300,000 are
runs in which the moduli up to 383 have to find one setting.

A direct test of the freezing (`cover_floor.c` with COVER_FLOOR_PREFIXES
and COVER_FLOOR_CLASSES, which count, among the sampled covers that leave
no row, the settings of the first m moduli taken together and the classes
of each modulus; `cover_floor_runs/classes/`). The quantity the constraint
is about can be measured: the entropy of the first m moduli among complete
covers. On the 167 moduli, runs of 300,000 sweeps from the 41,659 cover at
three targets (1.1 to 1.9 million samples each, uniform over the complete
covers the run reaches):

| first m moduli (up to) | 6 (17) | 12 (41) | 24 (97) | 41 (181) | 61 (293) | 90 (467) | 120 (661) |
|---|---|---|---|---|---|---|---|
| classes to choose from, nats | 11 | 31 | 82 | 165 | 275 | 447 | 638 |
| **Q = 40,111**: settings seen | 2 | 3 | 3 | 6 | 16 | 2,674 | 16,780 |
| their entropy, nats | 0.07 | 0.45 | 0.45 | 1.07 | 2.1 | 3.6 | 5.3 |
| recursion with the constraint | 3.1 | 0.2 | 0.0 | 0.0 | 7.9 | 42 | 90 |
| recursion as it was | −1.1 | −16.5 | −36.4 | −42.1 | −27.4 | 16 | 73 |
| **Q = 38,000**: settings seen | 5 | 8 | 11 | 21 | 3,065 | 82,522 | 418,474 |
| their entropy, nats | 1.2 | 1.4 | 1.9 | 2.6 | 4.2 | 7.3 or more | 10.2 or more |
| recursion with the constraint | 3.3 | 0.2 | 0.0 | 0.7 | 14 | 58 | 115 |
| recursion as it was | −0.3 | −14.3 | −30.9 | −31.9 | −13.1 | 37 | 102 |
| **Q = 25,000**: settings seen | 4 | 75 | 473 | 40,481 | 456,858 | 1.7 million | 1.9 million |
| their entropy, nats | 0.6 | 3.7 | 4.9 | 8.3 or more | 11.5 or more | (as many as samples) | |
| recursion with the constraint | 3.4 | 0.4 | 4.8 | 30 | 78 | 168 | 274 |
| recursion as it was | 3.3 | 0.1 | 4.4 | 30 | 78 | 168 | 274 |

Near the end the 41 smallest moduli, which have 165 nats of classes to
choose from, occur in six settings among 1.1 million complete covers at
40,111 and in 21 among 1.4 million at 38,000: one or two nats of entropy
where the unconstrained recursion needs −42 and −32 and the constrained one
has 0.0 and 0.7. At 25,000, where neither version has a constraint binding
beyond the first dozen moduli, the same 41 moduli occur in 40,000 settings.
So the freezing is there, it sets in where the constraint starts to bind,
and it reaches as far up the moduli as the constrained recursion says (the
thaw: 16 settings of the first 61 moduli at 40,111, thousands of the first
90). In the detail the two differ: beyond the frozen part the measured
entropy grows more slowly than the recursion's (2.1 nats against 7.9 for
the first 61 moduli at 40,111; a run of this length does not visit every
setting that exists, so the measured figures are lower bounds, and the
plug-in estimate saturates at the logarithm of the number of samples), and
among the very first moduli the recursion spreads the entropy wrongly (it
leaves the moduli 3 to 13 free, having no dispersion for them, where the
samples have them fixed, and it freezes 17 to 41 at 25,000 where the
samples show 3.7 nats). The class of each single modulus tells the same
story: at 40,111 the commonest class has 94 to 99% of the samples at every
modulus up to 181 and 85% on average from 191 to 293; at 38,000 it has 71
to 74% at every modulus from 7 to 113, the mark of three or four families
rather than of free moduli. This is one start in one family.

What it changes at the sizes counted:

- Near the end the loss rises and the excess of the measured loss shrinks:
  measured over predicted goes from 1.007 to 1.002 at 167 moduli and 40,111,
  from 1.016 to 1.008 at 238 moduli and 65,203, from at most 1.028 to at
  most 1.016 at 302 moduli and 91,820. In the middle of the range nothing
  changes (0.97 to 0.99, as before).
- The test that stayed open. At 1,228 moduli and 300,000 the constrained
  loss is 3,452 (3,409 without the constraint; the 3,394 on record is the
  unconstrained figure with the dispersion at the moduli 3 to 17 cut at
  0.02 instead of 10^(−4); see the note on that cut below).
  The runs read 3,465 at 150,000 sweeps and 3,438 at 500,000, still falling
  slowly, so the constrained figure lies inside the range of the runs and
  the unconstrained one below all of them. That does not decide between
  the two: runs of finite length read high, and in the middle of the range
  the recursion itself reads 1 to 3% high at the larger sizes. What it does
  is remove the puzzle of a series that approached 3,394 and stopped 44
  short: the figure it was held against was 15 to 58 too low.
- Where complete covers end, D/(x·ln² x):

| x | 463 | 797 | 997 | 1,499 | 1,999 | 2,999 | 9,973 | 30,000 | 100,000 | 300,000 | 1,000,000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| moduli | 89 | 138 | 167 | 238 | 302 | 429 | 1,228 | 3,244 | 9,591 | 25,996 | 78,497 |
| the recursion as it was | 0.913 | 0.933 | 0.952 | 0.991 | 0.995 | 1.019 | 1.074 | 1.097 | 1.125 | 1.140 | 1.154 |
| with the constraint | 0.912 | 0.929 | 0.944 | 0.975 | 0.975 | 0.988 | 1.008 | 0.995 | 0.982 | 0.960 | 0.936 |
| evidence | 0.912 found, one row left 0.3% beyond | 0.923 to 0.926, counts extended | 0.876 found | 0.970 to 0.973, counts extended | 0.956 or more, counts extended | | | | | | |

  (Counts extended: the Opus session's straight line through its last two
  counts, the run from the cover at the last; found: the best complete
  cover, which at 167 moduli and beyond stops well before the count does.)
  (The last three columns were computed by the contractor session with the
  same script.) With the constraint the ratio stops rising near 1.0 at about
  a thousand moduli and turns down, to 0.94 at 78,497 moduli, where the
  unconstrained one has 1.15. So the c = 1.00 of the law is not two corrections
  crossing; it is where the constrained count stays, within 1%, from 400 to
  3,000 moduli.

How exact this is. The figures above move by about 1% with one choice: the
lower cut of the dispersion at the moduli 3 to 17, where the pair sum
returns nothing usable (values at or below zero) while the class counts do
differ a little (variance over mean 0.05 to 0.3 on random vectors). For a
cut of 10^(−4), 0.02 and 0.06 the constrained end is 15,907, 16,063 and
16,218 on the 89 moduli (known: 15,907 found, one row left at 15,950 and
16,000) and 78,186, 78,541 and 78,997 on 238 moduli (counts extended:
77,741 to 77,952); the loss at 1,228 moduli and 300,000 is 3,452, 3,445 and
3,434 (and 3,409, 3,394, 3,362 without the constraint). The tables use
10^(−4), which reproduces the one end that is known. The reason for the
sensitivity is the one found for the floors: a frozen level takes the
largest of a few counts, and the weighted recursion, like any
large-deviation estimate, puts that too high (by 18% of a standard
deviation for two classes, 60% for four, 20% for a hundred); a small cut
at the first moduli makes up for it there. The Lean session's second read
settles what the right input is and what it does: computed exactly from the
primes (and checked against the enumeration of every class vector), the
dispersion is 0.058, 0.057, 0.054 at the moduli 3, 5, 7 for Q = 300,000 and
0.11 to 0.34 from 11 to 43, where the pair sum is low by 0.05 on average
(above 43 the two agree, rms 0.003). With those dispersions its own
implementation, which reproduces all 24 rows of `cover_price_prefix.txt` to
the digit when given mine, has the constrained ends at 0.959, 0.957, 0.971,
0.993, 0.987, 0.997, 1.013 times x·ln² x for x = 463 to 9,973, the loss at
1,228 moduli and 300,000 at 3,426 (3,349 without the constraint), and
measured over predicted at 0.984 to 1.003 in the middle of the range and
1.02 to 1.04 near the end. So with exact inputs the middle of the range
comes right and the constrained recursion puts the end of complete covers
5% too far on the 89 moduli; the agreement within 1% in the table above
owes something to the low dispersions at 3, 5 and 7. What is missing acts
toward fewer covers near the end, and the exact treatment of the frozen
levels is the candidate. That session also found that the recursion is not
invariant under the order in which the moduli are taken (at 1,228 moduli
and 300,000 the unconstrained loss is 3,349 in increasing order, 3,452 with
3 to 17 first and the rest decreasing, 1,606 in decreasing order), so the
prefixes in increasing order are the constraints one can state inside it,
necessary there, and other families of subsets cannot be tested by
reordering; and that the dual is correct (its tilts feasible and
complementary, primal equal to dual within 3·10^(−4)).

And in the limit: nothing, yet. What follows is the record of an error
made and caught on the same day. From the entropy count I concluded that
all but the top moduli are frozen in the limit, that frozen moduli can do
no better than random classes, that they therefore leave 0.7413·π(Q)/ln x
rows for the top moduli to strike from classes holding O(1) of them, and
hence that D(n) ≤ (1.349 + o(1))·r·ln² r/ln ln r, with D(n)/(r·ln² r)
tending to 0. The consultant session checked it and first agreed
(`goldbach/gaps_map/LIMIT_CHECK.md` on `ccr-cdb2641a-5zg8un`, with a better
form of the count for the top moduli, as a capacity: the largest classes of
the top moduli must add up to the rows left). The Lean session's second
referee read (`scripts/cover_prefix_check/README.md` on its branch, commit
9eb7e2a) then showed the step "frozen moduli can do no better than random
classes" to be true of the model and false of the primes:

- Give every modulus t of a block (z, x/4] the class of one common integer,
  a_t = N₁ mod t with N₁ in (Q, 2Q]. The block then strikes q exactly when
  N₁ − q has a prime factor in (z, x/4], and leaves only the rows with
  N₁ − q smooth or of the form m·p with p > x/4 prime and m ≤ 8Q/x: a share
  of order ln ln x/ln x of the rows, where random classes on the same
  moduli leave ln z/ln x. It is the device of Erdős and Rankin for gaps
  between primes, and it has next to no entropy (one integer). Counted on
  real primes: the block (406, 937,500] at Q = 6·10^7 leaves 32.3% of the
  rows against 44.0% for random classes (Lean session, exact), and the
  ratio of the two is 0.93, 0.86, 0.72 at x = 10^4, 10^5, 10^6 (consultant
  session).
- So neither 1.1275 nor 1.349/ln ln r is a limit of D(n)/(r·ln² r). The
  capacity bound holds for covers whose small moduli act like random
  classes, which are the covers the entropy count sees and the only ones
  any search here has found; D(n) itself is a different matter. With the
  block in front, the same count for the top moduli allows
  Q/(x·ln² x) = 0.57, 0.51, 0.55, 0.65, 1.10 at ln x = 9.2, 20.7, 50, 100,
  350 (Lean session; no claim that such covers exist), growing without
  bound.
- And it gives a theorem of a new order. With ln z = ln x·ln₃ x/(3·ln₂ x)
  (ln₂ = ln ln, and so on), the block averaged over N₁, the fullest classes
  on the primes up to z and one row for each prime in (x/4, x],

      D(n) ≥ c·r_n·ln² r_n·ln₃ r_n/(ln₂ r_n)²    for some c > 0 and all large n,

  that is, infinitely many even N with no Goldbach summand below
  c·ln N·(ln₂ N)²·ln₄ N/(ln₃ N)². The consultant session has written the
  proof out line by line (`goldbach/gaps_map/COHERENT_BLOCK.md`, commit
  0761b84: Chebyshev, Brun–Titchmarsh, Mertens, and Rankin's trick for
  smooth numbers; the average over N₁ replaces any sieve for prime pairs);
  it is a proof on paper that only its author and I have read, and I have
  checked its orders of magnitude and its four steps, not every constant.
  It supersedes, as to order, every bound of the form A·r·ln r, including
  the 1.349 of the theorem in the Lean library and the 1.3523 of the
  pair-cover note. The Lean session points out that the skeleton has been
  in its library since 22 November (`Cap/Layers.lean`, written for the
  Erdős–Rankin adaptation proposed here that day and then dropped from
  this file), and it has begun to formalise the corollary "for every A and
  all large y, classes modulo the odd primes up to y cover every odd prime
  below A·y·ln y".

Where that leaves the question: D(n) is at least c·r·ln² r·ln₃ r/(ln₂ r)²
(on paper), the covers that searches find and counts count end at 0.91 to
1.01 times r·ln² r for 89 to 25,996 moduli by the constrained recursion
(0.936 at 78,497 moduli, where the unconstrained one has 1.154), and
whether structured covers reach further than those in the limit, and how
far, is open. At the sizes that can be computed nothing changes: the block
leaves 2% fewer rows than random classes at x = 10^4 and half as many only
near x = 10^25, and a cover built from it at x = 10^4 reaches 0.39 to 0.48
of x·ln² x where plain greedy reaches 0.71 and the constrained recursion
1.0.

A prediction, and its test. The runs first made at 2,999 and 9,973 moduli
were short (20,000 and 12,000 sweeps), and the one at Q = 300,000 was not in
equilibrium: its mean row counts at the middle temperatures were still
falling by 1 to 2% between the first and the last quarter, which makes the
measured loss too large. The recursion said by how much, and the figures
were written here before any long run existed: a long run should give 3,330
to 3,414 at 9,973 moduli and Q = 300,000, not 3,582, and about 1,545 instead
of 1,589 at 2,999 moduli and Q = 100,000. The Lean session's machine then ran
the second of these twice, 150,000 sweeps each from random vectors (commit
972bb6e there): 1,541.3 and 1,542.0. The long runs landed 3 to 4 nats from
the predicted figure and 47 from the short run. The two long runs at 9,973
moduli started on 24 November at 18:25 UTC and are not in; with the whole
pair sum the figure for them is 3,394 (computed and written here at 19:07
UTC the same day), with the closed formula 3,414. (Only the range 3,330 to
3,414, written at 18:02, is earlier than any long run: that session had
pushed the first run's output at 18:56, eleven minutes before the 3,394 was
written, and what can be said for the 3,394 is that it was computed without
reading it. And the test is one-sided, since every run of finite length
reads too high.) The first of the two (150,000 sweeps, commit 99815c7
there) gives 3,465.9: it moved 116 nats from the short run toward the
predicted figure and stopped 52 to 72 short of it, and it is not in
equilibrium either, its mean row counts at the middle temperatures still
falling by about 1% from the first quarter of the run to the last. So this
point is open. The second seed gives 3,464.6, so 150,000 sweeps give 3,465
reproducibly and it is the length of the run that holds it there: a run of
500,000 sweeps gives 3,437.7 (commit d6195b5 there), still drifting, more
slowly. By length of run from random vectors the loss reads 3,582, 3,465,
3,438 at 12,000, 150,000 and 500,000 sweeps, 24 to 44 above the figure on
record at the last. A run from a complete cover (the certified 614,101
vector) was meant to come at it from the other side and did not: it gives
3,466.9, the same as the runs from random vectors of its length, with
quarters that fall like theirs and 3 of the start's 12 smallest classes
kept at every temperature (chance would be 1.1). The middle temperatures
forget the start within the burn-in; the slow mode is something else, most
likely the families of the earlier paragraph taking their shares. So at
1,228 moduli the test stands as: approached from above to within 1.3%, not
yet reached, and no way found here to bound it from below. (A power law in
the length of the run through the three values, loss = L + A·t^(−a), has
L = 3,388 to 3,393 with a = 0.36 to 0.38, whether t is the whole run or the
middle of its sampled part. Three points and three parameters: that is an
estimate of where the series is heading, next to the 3,394 on record, and
not a test.)

Twelve more counts, predicted first (25 November). The Opus session counted
complete covers on 138, 238 and 302 moduli (x = 797, 1,499, 1,999) at 60,
75, 85 and 93% of the reach of its tempered covers (30,931; 70,111; 98,731),
two runs of 400,000 sweeps from random vectors at every target and one from
its best cover at the two highest (`floor/floor_report.md` on its branch).
The losses by the recursion were written into `cover_price_hl.txt` at 07:31
UTC, before any of those runs had finished:

| moduli | target | loss on record, pair sum | closed formula | measured | measured / pair sum |
|---|---|---|---|---|---|
| 138 | 18,559 | 434.0 | 433.3 | 423.0 | 0.975 |
| 138 | 23,198 | 535.5 | 537.8 | 524.1 | 0.979 |
| 138 | 26,291 | 601.6 | 606.2 | 599.3 | 0.996 |
| 138 | 28,766 | 656.3 | 662.9 | 658.5 | 1.003 |
| 238 | 42,067 | 791.9 | 796.1 | 773.8 | 0.977 |
| 238 | 52,583 | 978.2 | 987.7 | 966.9 | 0.988 |
| 238 | 59,594 | 1,104.9 | 1,118.7 | 1,123.5 | 1.017 |
| 238 | 65,203 | 1,200.9 | 1,216.5 | 1,227.9 | 1.023 |
| 302 | 59,239 | 1,024.8 | 1,032.7 | 1,013.9 | 0.989 |
| 302 | 74,048 | 1,263.8 | 1,277.3 | 1,268.0 | 1.003 |
| 302 | 83,921 | 1,425.3 | 1,443.1 | at most 1,464.3 | at most 1.027 |
| 302 | 91,820 | 1,553.3 | 1,573.2 | at most 1,605.9 | at most 1.034 |

(Measured: the mean of the two runs from random vectors at the two lower
targets, where they agree within 1.4 and are steady; the run from the cover
at the two higher ones, where the runs from random vectors read between 1.5
nats less and 22 more and are still falling. At 302 moduli the runs from
the cover are still falling too, by 7 to 10 nats over their second half, so
those two are upper bounds.) All twelve are within 3.5% of the figure on
record, and the ten that are in equilibrium within 2.6%. The error is not
noise: the recursion's loss is 1 to 2.5%
too large in the middle of the range and too small by up to 2 to 3% near
the end, and at a fixed share of the reach the ratio rises slowly with the
number of moduli (0.975, 0.977, 0.989 at 60%; 0.979, 0.988, 1.003 at 75%),
as it does at 429 moduli (0.998 at half the reach) and 1,228 (between 0.999
and 1.013 at a third). The closed formula is the closer of the two near the
end and the further in the middle. So the recursion is a 2 to 3% theory of
the count at every size tried, with an error that has a shape and moves
slowly with size; nothing here says where that error goes in the limit,
which is the referee's caveat above.

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

How far that floor can be trusted nearer the end (25 November; the fixed-gap
game below works at Q = 3·D to 7·D, the campaign at 10·D to 13·D). On the
same 89 moduli at four smaller targets, tempering for 30,000 sweeps (one
core, four minutes each) against the recursion:

| Q | 24,000 | 32,000 | 48,000 | 80,000 | 170,000 | 213,070 |
|---|---|---|---|---|---|---|
| D/Q | 0.66 | 0.50 | 0.33 | 0.20 | 0.094 | 0.075 |
| floor by the recursion (rows) | 44 | 97 | 217 | 474 | 1,221 | 1,584 |
| temperature β where its entropy reaches zero | 3.85 | 3.15 | 2.50 | 1.95 | 1.40 | 1.25 |
| best cover found | 50 | 109 | 229 | 494 | 1,248 | 1,609 |
| floor measured in the same run, the largest −ln Z/β | 50.2 | 108.8 | 230.2 | 495.6 | | |
| found above the recursion's floor | 14% | 12% | 5.5% | 4.2% | 2.2% | 1.6% |

The runs have converged (the best cover sits on the measured floor, and the
entropy left at the coldest temperature is 4 to 12 nats), so the difference
is the recursion's. Its ln Z is right within 4% at every temperature
before the freezing: the measured loss θ − ln Z is 0.96 to 1.00 of the
recursion's for β up to 2 at all four targets (`cover_floor_runs/small_targets/`). But the floor is a small
difference of large numbers, and the recursion divides ln Z wrongly between
energy and entropy at low temperature: at Q = 48,000 and β = 2.45 it has
220 rows left and 7 nats of entropy where the run has 266 rows and 127
nats, with nearly the same ln Z. The real ensemble freezes later and higher.
So the recursion's floor is a lower estimate that is good to 2% where the
freezing comes early (β near 1.3, the campaign) and 5 to 14% low where it
comes late (β from 2.5 up, targets within three times the end of complete
covers). Multiplying the recursion's loss by 1.03 before taking the floor
reproduces the four small cases within 4% (48.7, 104, 229, 495), but it
overshoots at the campaign's targets (1,267 and 1,642), so there is no single
factor; where rows are quoted below for the fixed-gap game, the covers
actually found are given beside the recursion's figure.

Where the rows go, on one case. Walk the best cover at Q = 48,000 (229 rows
left) through its moduli in increasing order beside the recursion's frozen
solution (215 rows left, the same with or without the prefix constraint of
the earlier section). Up to the modulus 101 the two agree: the cover has
648 rows alive there against 643, and at nearly every modulus its class is
the fullest there is (161 rows at 11 where the theory has 162, 31 at 43
against 29, 12 at 101 against 13). From 131 to 263 the theory asks for
classes fuller than any that exists: 10.4 rows at 131, where the fullest of
the 130 classes has 9 and the cover takes one with 6; 8.7, 7.6, 6.6, 6.0 at
163, 193, 229, 263, where the fullest have 8, 7, 6, 5. All of the
difference builds up there (412 rows alive at 263 against 383), and the
largest moduli then do as well as the theory or better. The cause is in the
rate function: where a level is frozen its class is the largest of s − 1
counts, and the largest of s − 1 Poisson-like counts lies about one row
below the value at which the large-deviation rate equals ln(s − 1) (the
Stirling factor of the point probability: [½·ln(2π·k) − ln(r/(r − 1))]/ln r
rows for a count k that is r times its mean, 1.4 rows at 131). While the
classes of a level are still many, the sum over them supplies that factor
and the recursion is right; that is the difference between complete covers
below the end (within 1.6% near the end) and the frozen floors above it (4
to 14% low). A floor with the exact law of the largest count in the frozen
levels has not been built.

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

Several more pieces are formal since (commits e992eb3 to 3ccf2f0 there, standard axioms).
The covering theorem is stated in depth form
(`eventually_exists_classes_of_mul_lt_one` in `CoverBound.lean`): for every
c < e^γ/(2·C₂) = 1.349 and all large y, some classes modulo the odd primes up
to y strike every odd prime below c·y·ln y. So the count is positive there
(`eventually_g0_pos`), and with the monotone bound it is bounded from below
on every larger set of moduli (`eventually_prod_le_g0`, and with c = 1.2
explicit): for all large y and every x ≥ y,

    ln g0(x, c·y·ln y) ≥ θ(x) − θ(y),

that is, in the range Q ≤ 1.349·y·ln y the loss is at most θ(y), about
Q/(c·ln Q). The law says Q/ln² x, which is smaller; the theorem is the only
bound on the loss that holds for all large sizes. And the first step of the
derivation is exact (`CoverPairs.lean`): for two rows q, q + d in one class
of a modulus s, the weight of the pair against independence over the smaller
moduli, times the Hardy–Littlewood density of the pair, summed over a full
period of the differences d = 6·s·j, has mean exactly 6·s/(s − 1), for every
truncation of the two products (`sum_pair_weight`, from the two local
identities `local_cancellation_below` and `local_cancellation_above`; the
proof does not use that the moduli lie below s). So at leading order the
alive rows fall into the classes of s as independent rows would, with
nothing assumed. What the derivation uses beyond that, the second-order term
of the average of singular series, rests on the Hardy–Littlewood conjecture
and is not formal. The product form of the pair weight used for the whole
pair sum is formal too (`CoverPairSums.lean`, f77b4bb), for every truncation
of the products: W(j) = a·c·∏ over the t dividing j of (1 + u_t) with
c = ∏(1 + u_t/t)^(−1) (`pairWeight_eq_prod`, `prod_w0_mul_sum`); the sum of
W over j ≤ m as a·c·Σ u(d)·⌊m/d⌋ (`sum_Ioc_pairWeight`); the defect
a·m − Σ W(j) = a·c·Σ u(d)·(m/d − ⌊m/d⌋), hence R(m) ≥ 0 for every m
(`pairWeight_defect`, `sum_Ioc_pairWeight_le`); the two local ratios behind
the limit profile, and ∏ over the primes t ≥ 5 of (t − 1)²/(t·(t − 2)) =
3/(4·C₂) (`tendsto_prod_sq_div`). The constant of the limit was recomputed
by that session with other numerics (Chebyshev points and Gauss–Legendre for
m, whose closed form on [1, 2] is ρ²·(5/2 − ln ρ) − 2ρ + 1/2; the price
equation in the variable ln p, regular at both ends): Λ(1) = 1.19639276351,
so that the limits are 0.8868957952·Q/ln² x and 1.1275281780·r·ln² r; these
are floating-point values agreeing to 2·10^(−12) across step sizes, a check
of the arithmetic and not of the equations. Last, the count itself is known exactly at nine moduli:
every one of the 3,234,846,615 class vectors enumerated
(`scripts/cover_count/g0_exact.c`, commit 4edfa27), which reproduces D(2) to
D(9) and the numbers of vectors at the depth, with g0(7, 19) = 1 and
g0(7, 20) = 0 in the kernel.

The law itself and its derivation are a measurement and a heuristic; an
upper bound for g0 of this shape would bound D(n) by a multiple of r·ln² r
and prove Goldbach's conjecture for large N, by the implication above.

*The other direction: a fixed gap and the fewest digits* (`cover_dual.py`,
`cover_dual.txt`; proposed by the user on 25 November). Instead of the
largest g below 10^200, fix the gap Q and ask how small N can be with
g(N) ≥ Q. The same calculation answers it. A number of size e^L can carry
the odd primes up to about x = L as moduli (θ(x) = L); on those the
complete covers end at D(L) = κ·L·ln² L; beyond the end the best cover
leaves the fraction ρ(D/Q) of the rows that random classes leave (the table
of "The same calculation above the end": ρ = 1 − √(K·D/Q) for small D/Q,
0 from D = Q on); and the rows left by random classes carry
2·C₂·π(Q)/L expected primes whatever the moduli are. So one member in e^E
succeeds, with

    E(L, Q) = 2·C₂·(π(Q)/L)·ρ(κ·L·ln² L / Q),

zero from the size on where D(L) = Q (the gap is then forced by divisibility
alone), and the ceiling of the game, the size at which a number with
g ≥ Q first exists at all, is about L = √(2·C₂·π(Q)): the frontier a search
can reach is at L = 2·C₂·π(Q)·ρ/(the logarithm of the trials it can afford),
so it falls behind the ceiling like √π(Q) as the gap grows. With the
recursion over the actual primes (its rows are 2% below the best covers at
the campaign's points and 4 to 7% below at the sizes of this game; see
below):

| gap Q = 200,000, digits | 100 | 150 | 200 | 220 | 230 | 240 | 260 | 300 | 350 | 400 | 500 | 600 | 800 | 1,000 | 1,300 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| moduli that fit | 49 | 69 | 89 | 96 | 100 | 103 | 110 | 125 | 142 | 159 | 192 | 224 | 286 | 347 | 434 |
| fewest rows left | 1,994 | 1,697 | 1,474 | 1,407 | 1,371 | 1,344 | 1,285 | 1,168 | 1,050 | 943 | 762 | 611 | 370 | 185 | 0 |
| chance per row, p | 0.0426 | 0.0305 | 0.0240 | 0.0221 | 0.0213 | 0.0205 | 0.0192 | 0.0170 | 0.0149 | 0.0133 | 0.0110 | 0.0094 | 0.0073 | 0.0060 | |
| members per success, powers of ten | 36.9 | 22.4 | 15.4 | 13.5 | 12.7 | 12.0 | 10.7 | 8.6 | 6.8 | 5.5 | 3.6 | 2.5 | 1.2 | 0.5 | 0 |

| gap Q = 1,000,000, digits | 400 | 600 | 800 | 1,000 | 1,200 | 1,500 | 2,000 | 2,480 | 3,000 | 4,000 |
|---|---|---|---|---|---|---|---|---|---|---|
| moduli that fit | 159 | 224 | 286 | 347 | 405 | 491 | 629 | 759 | 895 | 1,151 |
| fewest rows left | 6,476 | 5,514 | 4,802 | 4,222 | 3,744 | 3,130 | 2,315 | 1,683 | 1,130 | 324 |
| members per success, powers of ten | 37.4 | 22.5 | 15.2 | 11.0 | 8.3 | 5.7 | 3.3 | 2.0 | 1.1 | 0.2 |

For comparison the campaign's present design, 170,000 at 200 digits, needs
10^13.2 members a success, and the fleet scans about 4.5·10^12 a day; a
Fermat test costs roughly the cube of the number of digits and a member
needs tests in proportion to the digits. On those terms a gap of 200,000
costs at about 230 digits what 170,000 costs at 200; the units that remain
would buy one expected success at about 225 digits, and one day of the
fleet as it was on 24 November one at about 240, if its kernels ran at those
sizes (they are built for 200 digits; that is the lead's and the GPU
session's matter). The ceiling for this gap is 68.5 digits by the project's
ceiling model, and divisibility alone forces it from about 1,340 digits
(1,300 by the recursion without the entropy constraint). For
a gap of 1,000,000: ceiling 142 digits, the same budget about 1,040 to 1,120
digits, held today 2,480 digits, forced by divisibility from about 4,900
(4,700 without the constraint).
On closeness to the ceiling of its own size none of this beats the present
campaign at equal cost (200,000 at 225 digits is 7.3% of that size's
ceiling, where the present design is 8.0% of its own); closeness is bought
more cheaply at smaller sizes, as the project's earlier thresholds show,
because at a fixed share of the ceiling E grows in proportion to the digits.
What the dual game does offer at once is records of its own that need no
GPU, and a test of the recursion far from where it was built. Both are
under way since 25 November (uarch: 400, 350, 320 digits; this session: 300
digits; Opus: the gap of 1,000,000), and the first thing they showed is that
the table above is too hopeful by a factor of two to four in members:

- Rows. The recursion's floor is low by 4 to 7% at these ratios of Q to D
  (the test at small targets above). Converged tempering finds 1,218 rows at
  300 digits where the table has 1,168 (the run's own entropy reaches zero
  at 1,218 to 1,222, so that is the bottom, not the search), and the uarch
  session's runs have 1,113 at 350 digits (100,000 sweeps) and 1,010 at 400
  (200,000 sweeps) against 1,050 and 943. At 2,000 and 2,190 digits for the
  gap of 1,000,000 the Opus session is at 2,829 and 2,595 rows against 2,315
  and 2,039, not converged: at 629 moduli a sampler that proposes classes at
  random hardly moves the large moduli, and that session wrote a move that
  draws the class of a modulus from all its classes at once.
- Tests. On a processor the cost is the Fermat tests, not the members
  (`cover_dual_cpu.py`, `cover_dual_cpu.txt`). With gmpy2 on one core here a
  base-2 test takes 0.11 ms at 200 digits, 0.30 at 300, 0.66 at 400, 30 at
  1,500 and 51 at 2,000. The uarch session generalised its vector kernel to
  any length the same morning (`fermatw` on its branch: 32 microseconds at
  300 digits here, a factor 10.6).
- The cut. After a sieve to B a member keeps S of its rows; S is binomial
  with chance w = ln x/ln B per row (sd 0.69·√mean at B = 10^7, measured by
  the Opus session; I first took it Poisson, which overstates the gain), a
  survivor is prime with chance p′ = p/w, and a member that is not a hit
  costs about 1/p′ tests. Sieving is cheap next to testing, so one sieves
  many more members than one tests and tests only the emptiest; the best cut
  lies 2 to 3.5 standard deviations below the mean and gains a factor 2 to
  4 over testing every member.

CPU-hours per hit with the best cut (sieve to 10^7 for the first gap, 10^9
for the second; sieve speed as measured here with the uarch session's
sieve200):

| gap 200,000, digits | 400 | 350 | 300 | 260 |
|---|---|---|---|---|
| rows: the recursion's floor, found | 943, 1,010 | 1,050, 1,113 | 1,168, 1,218 | 1,285, |
| members per hit with the cover found, powers of ten | 5.9 | 7.3 | 9.1 | (10.8 at the floor) |
| CPU-hours, gmpy2 | 1.1 | 15 | 420 | (12,000 at the floor) |
| CPU-hours, the vector kernel | 0.24 | 2.7 | 78 | |

| gap 1,000,000, digits | 2,480 | 2,190 | 2,000 | 1,500 |
|---|---|---|---|---|
| rows: the recursion's floor, found so far | 1,683, 2,524 | 2,039, 2,595 | 2,315, 2,829 | 3,130, |
| CPU-hours with the cover found, gmpy2 | 2.2 | 3.3 | 9.5 | (180 at the floor) |

At 300 digits the calibration of the scan agrees with the calculation in
every figure it prints (4.2 million members of one cover: 498.6 survivors a
member against 495, a prime among the tested survivors once in 23.9 tests
against 1/0.0418, e^(−20.86) per member against e^(−20.90), 10.4% of the hit
mass at a cut that tests 2.4% of the members against 10.7%); the same
calculation holds end to end in the uarch session's checks at 400 digits
with smaller targets on the same cover (329 hits against 355 expected at
Q = 30,000, 6 against 6.0 at 100,000, 10 against 9.0 at 130,000). So four
cores reach 300 digits in about a day for the gap of 200,000 (16 hours
expected here, started 09:36 UTC on 302 covers of 1,218 and 1,219 rows), and
50 digits less cost a factor of 11 from 400 to 350 digits and of 29 from 350
to 300.

Results (every N recomputed here from N alone before it is listed):

| gap | digits | g(N) | found by | cover | members sieved, tests, CPU-hours | record files |
|---|---|---|---|---|---|---|
| 200,000 | 400 | 200,293 | uarch, 25 Nov 09:31 UTC | 159 moduli (3 to 941), 1,010 rows | 72.4 million, 58.0 million, 1.78 (both hits) | `records/g200k_400digit_g200293` on `ccr-b8c25887-i6tn9f` |
| 200,000 | 400 | 206,593 | the same run | the same | | `records/g200k_400digit_g206593` there |
| 200,000 | 347 | 216,289 | uarch, 25 Nov 11:41 UTC | 141 moduli (3 to 821), 1,115 rows | 806 million, 318 million, 8.5 for the whole 350-digit phase (the hit itself after 319 million members and 1.04 CPU-hours on its second progression; the first, 142 moduli, gave none in 488 million where 1.75 were expected) | `records/g200k_347digit_g216289` there |

Both are certified in the Lean kernel (`Gap200k_400digit_g200293.lean`,
`Gap200k_400digit_g206593.lean` and `FixedGap.lean` on the Lean branch,
commit 6a2b774, standard axioms): for every prime q below 200,293
(respectively 206,593), N − q is not prime, 16,996 (17,438) of them because
one of the 159 moduli divides it and 1,011 (1,079) because it fails the
base-2 Fermat test; and 10^399 ≤ N < 10^400. So "there is an even number
below 10^400 with no Goldbach summand below 200,000" is a theorem. That
N − g is prime, which makes g the exact value, rests on gmpy2's test here
and is not certified.

(At 400 digits the cut kept 7.1% of the hit mass, one hit expected per 10.7
million members sieved: 6.8 expected in the 72.4 million, 2 found, and none
in the first 69 million. A count that low or lower has probability 3.5%;
the uarch session checked the sieve against brute force, the kernel against
gmpy2, and the whole chain at three smaller targets on the same cover
before going on, all in agreement, so it stands as luck until the next
sizes say otherwise.)


**Conjecture (counting law), as it stands on 25 November at noon.** For Q
up to the end it predicts, the number of class vectors modulo the odd primes
up to x that strike every odd prime below Q is exp(θ(x) − L(x, Q)), L the
loss of the price recursion with the dispersions of the rows (the
Hardy–Littlewood pair sum, or computed from the primes at the smallest
moduli) and with the entropy of every prefix of the moduli kept
non-negative (`cover_price_prefix.py`). At the sizes counted (89 to 1,228
moduli, 24 counts) L is within 6% of the measured loss with the pair-sum
dispersions and within 4% with the exact ones (Lean session), and
L = 1.00·Q/ln² x within 5%. This is a statement about the covers that such
counts and searches see, those whose frozen moduli act like random classes.
For those, complete covers end at κ·r·ln² r with κ between 0.91 and 1.01
from 89 to 25,996 moduli, largest near a thousand moduli (the known values
of D(n) for 20 to 89 moduli have 0.77 to 0.91).

About D(n) itself, which is a maximum over all class vectors, what is
known on 25 November at noon is less than was claimed here on the 24th and
earlier that morning: D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)² for large n (the block
on a common integer; on paper), D(n) equals the end above within 1% at 89
moduli and is not known beyond, and no limit of D(n)/(r·ln² r) is derived:
not 1.1275 (the unconstrained recursion's, withdrawn at 10:20 UTC), not
1.349/ln ln r (mine of 10:20, withdrawn at 11:45). Whether
structured covers reach beyond the counted ones, and how far, is open.

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
