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
p | d (not covered by the theorem) the parity is mixed, as it should be.

**What this is and is not.** It is a compositeness mechanism that is not a
small factor and not luck: the parity of the number of prime factors, which
over F_q[x] is the quadratic character of a discriminant and, for N a p-th
power, depends only on N modulo the *derivative of the row* (the idea behind
Sawin and Shusterman's proof of the twin prime conjecture over F_q[x]). It
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

## Ladder

| rung | what | who | state |
|---|---|---|---|
| 1 | Toy theorem (parity) and corollary, formal proof; Stickelberger–Swan as a hypothesis or proved | Lean | statement sent 23 Nov; numerics done here |
| 2 | Toy search with the parity filter: measure the factor against the model | research | done: 4 to 5 times (Result 2) |
| 3 | Toy instance small enough to enumerate every member: does anything besides parity and the symmetries of F_q[x] predict the best members? | research | to do |
| 4 | Barrier statements for the integer search, formal: black-box lower bound; decoding-radius inequality for our parameters; what residue information can never give | Lean | to do |
| 5 | Integer candidates for information that is not a residue (anything cheaper than a Fermat test that correlates with primality of a rough number, in a special family of N) | both | open; no candidate yet |
| 6 | Constants: wheel and list merges inside the production sieve | research | costed at 0.1 to 0.4 nats, not started |

## References

- W. Sawin, M. Shusterman, On the Chowla and twin primes conjectures over
  F_q[T], Annals of Math. 196 (2022).
- R. G. Swan, Factorization of polynomials over finite fields, Pacific J.
  Math. 12 (1962) (Stickelberger's theorem; Pellet's formula).
- V. Guruswami, A. Vardy, Maximum-likelihood decoding of Reed–Solomon codes
  is NP-hard (2005). Q. Cheng, D. Wan, on the decodability of Reed–Solomon
  codes and discrete logarithms.
- D. Bleichenbacher, P. Nguyen, Noisy polynomial interpolation and noisy
  Chinese remaindering, EUROCRYPT 2000. O. Goldreich, D. Ron, M. Sudan,
  Chinese remaindering with errors (1999). D. Boneh, Finding smooth integers
  in short intervals using CRT decoding (2000). V. Guruswami, A. Sahai,
  M. Sudan, Soft-decision decoding of Chinese remainder codes (2000).
