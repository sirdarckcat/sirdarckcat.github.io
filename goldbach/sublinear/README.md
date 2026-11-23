# Finding deserts without trying the numbers one by one

A research programme started on 23 November 2026, at the user's request, by
this session (experiments, number theory) and the Lean session (proofs).
It is expected to take a long time and may not succeed; this file is the
running record of what has been tried, what is proved, what is only measured,
and what is open.

## The question

The search for an even N < 10^200 with a large g(N) (the least prime p with
N − p prime) works in two stages. A *cover* fixes N modulo 88 small primes so
that most of the numbers N − q, q prime below the target, have a small factor.
The rows q it leaves (about 1,100 to 1,600) must then all give a composite
N − q by luck, and members N = N0 + tM are tried one after another: sieve,
keep the ones with the fewest rows left, test. One member in e^26 to e^39
succeeds, depending on the target.

The members with unusually few rows left after the sieve are far more likely
to succeed, and better numbers exist than the search can afford to find: the
best N below 10^200 for primes up to 10^7 is about e^10 times better than a
typical member (`../fscan/cover/brainstorm/`). The question is whether such
members can be *located* without enumerating all t:

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
  irreducible factor of Q′ divides N. So N = λ·V_J^p makes N − Q reducible for
  every monic irreducible Q of *any* degree below deg N whose derivative is
  J-smooth: all rows of degree ≤ J + 1, all but about 1/(J+1) of degree J + 2,
  and a Dickman proportion ρ((d−1)/J) beyond. In the F_9 example below
  (J = 3, deg N = 2,403) that is every quartic, about three quarters of the
  11,808 quintics and 38% of the 683,280 rows of degree 7, with no congruence
  and no luck.

**Corollary (deserts).** Let q be a square (q = p^(2e)), V_J the product of
all monic irreducibles of degree ≤ J, λ a non-square, and N = λ·V_J^p. Then
N − Q is reducible for every monic irreducible Q of degree ≤ J + 1 (p ∤ J+1):
those of degree ≤ J divide N, and for degree J + 1 the formula gives r even.
deg N ≈ p·q^J. Forcing the same by congruences needs a degree of order
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
of them. The last line shows where
the count goes with the whole sieve: it is the statement, already in the
brainstorm notes, that the best N for the primes up to 10^7 or 10^8 is
enormously better than anything the search can afford to find.

The fourth column is measured on 20,000 random members of a cover with 1,609
rows (mean ± standard deviation; `member_depth.py`). The ideal N are *not* members of the best
covers: 1,319 rows at depth 1,000 is 10.6 standard deviations below the mean
of such members, 685 at depth 20,000 is 17.5 below, and the e^39 members of
all the covers within a few rows of 1,609 reach about 9 standard deviations.
The ideal N give up a few rows on the small primes and are aligned, mildly,
with all the primes above: at the temperature that matters, a class change is
accepted with
probability below 0.01 for moduli under 128, about 0.1 for 128 to 512, 0.4 for
512 to 2,048, 0.7 for 2,048 to 8,192 and 0.9 above. No prime beyond 512 is
pinned to its best class; each is in a better-than-average one.

Caveats. (i) Tempering at low temperature is not fully in equilibrium (the
bottom of the z = 463 table is 20 nats low against direct counts); the error
moves the cost by about p_z·ΔS/β, 0.2 to 0.5 nats, in the direction of
understating the prize. (ii) The budget is counted in full-weight members,
that is, with the fleet's deep sieve and 3% rule behind each tested N in every
line. That selection is worth 2.0 nats today and about 1.8 after an ideal
search to 20,000, which has already used part of the same information.

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
   beyond the line the landscape is that of a random-energy model.
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
   block. The sets are sum-sets of random-looking class lists, so any
   locality-sensitive scheme collides on a good pair at most about twice as
   often as on a random one for a bucket of the same size; the exponent is
   0.88, i.e. K^0.94 work for a population K. Populations here are e^80 and
   more against e^33 operations available.
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
Garey–Johnson AN1), so nothing that treats the lists as arbitrary can be both
exact and fast. And for our lists the problem is the search for intervals
(N − Q, N] poor in rough numbers at fixed offsets, the same problem as record
prime gaps, where the state of the art is also covering congruences followed
by a sieve over the members.

In the language of the literature: collecting the prize means solving *noisy
Chinese remaindering with dense lists* on average — rate 460/1,940 and lists of
about a third of the classes for depth 2,000 — or equivalently maximum-
likelihood decoding of a Chinese-remainder code far below the Johnson radius.
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

## A provable lower bound (work in progress with the Lean session)

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
ln ln X / ln ln ln X. Neither is attempted here. For 200 digits the provable
bound is in the low thousands, against 157,837 found by search: as with prime
gaps, constructions are far behind luck at any size one can compute.

Status: proposed to the Lean session on 23 November as the theorem to
formalise next (needs Mertens' product in one direction and Chebyshev bounds).

## Ladder

| rung | what | who | state |
|---|---|---|---|
| 1 | Toy theorem (parity) and corollary, formal proof, Stickelberger–Swan included | Lean | done: proved without hypotheses (`FunctionField/ParityDesert.lean`, `Stickelberger.lean`, commit c0e3fb4 on the Lean branch), with two extensions (any degree; smooth derivative) |
| 2 | Toy search with the parity filter: measure the factor against the model | research | done: 4 to 5 times (Result 2) |
| 3 | Toy instance small enough to enumerate every member: does anything besides parity and the symmetries of F_q[x] predict the best members? | research | to do |
| 4 | Barrier statements for the integer search, formal | Lean | done (Lean branch, `Cap/BlackBox.lean`, `Cap/Radius.lean`, `Cap/Population.lean`): black-box bound (m questions reach the fraction m·g/K); inside the decoding radius only one-class lists pay for themselves, which is the cover (`list_deficit`, `johnson_leaves_the_cover`), and the radius is at least 3.88 times the typical agreement for K = 2^32; the population bound in Chernoff form (`hitMass_selected_le`: m tests on a population of e^F expect at most m·y^k + e^F·u^(−k)·∏(1 − s_j + s_j·y·u) successes however the members were found); the meet-in-the-middle condition ln P ≤ 2F − C (`mitm_condition_log`) |
| 5 | Integer candidates for information that is not a residue (anything cheaper than a Fermat test that correlates with primality of a rough number, in a special family of N) | both | open; no candidate yet |
| 6 | Constants: wheel and list merges inside the production sieve | research | costed at 0.1 to 0.4 nats, not started |
| 7 | The prize: number of N by rows left at depth z, and the cost of an ideal search | research | done for z up to 50,000 at the 10% target (Result 3): 3.5, 5.9, 8.8, 12.6, 14.8 nats |
| 8 | Problem (P′): any method that reaches beyond the Chinese-remainder line at less than the cost of scoring every member | both | open; lattices, meet in the middle, birthday trees and hashing ruled out with numbers (above) |

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
