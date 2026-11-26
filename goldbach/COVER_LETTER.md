# The least Goldbach summand below 10^200: what we tried and what we found

*A cover letter for pull request #34, written on 26 November 2026, the day the work stopped.*

This pull request collects five days of work, from 21 to 26 November 2026, on one question about prime numbers. The work
was done by nine AI sessions running Claude Code, each on its own branch of this repository, and coordinated by the
session that opened this pull request. The owner of the repository set the goal and steered the work through their
messages. No human mathematician has refereed any of it. Everything is in the `goldbach/` folder, and
`goldbach/README.md` is the place to start reading the files.

I have tried to write this letter so that it can be read without a mathematics degree. It explains the question, how
the search works, what we found, the long search for a better method (which did not succeed), the mistakes we made and
corrected along the way, and what is left to do. Technical words are explained the first time they appear, and there is
a short glossary at the end. "We" means the group of sessions; "I" means the coordinating session that wrote this
letter.

## The short version

For an even number N, let g(N) be the smallest prime p for which N − p is also prime. For example, 100 − 3 = 97 is
prime, so g(100) = 3. For almost every even number g(N) is small. The owner asked how large g(N) can be made when N
has at most 200 digits. They said they expected about 200,000, hoped for a million, and dreamed of two million.

The best number we found has 200 digits and g(N) = 160,357. Before this work, the best example in this repository was
119,419, and the best we know of in print was 105,667. We did not reach 200,000, and we can say fairly precisely why: a
search aimed at 200,000 needed about 250 times more computing than we had. The last two days went into looking for a
mathematical idea that would make up that factor of 250. We did not find one. We did learn where the difficulty lies,
and we ruled out most of the natural ways around it.

The same methods set records in related problems:

- The largest g(N) we know of for any N is now 16,046,137, for a number with 91,752 digits. The previous record was
  1,157,341.
- The smallest number we know whose g(N) is larger than anything in the range that computers have checked exhaustively
  has 23 digits. Before, the smallest such example in this repository had 150 digits.
- The fewest digits we know for a number with g(N) of at least 200,000 is 319. For g(N) of at least a million it is
  1,797, down from 2,480.

We also wrote a search program for graphics cards, worked out from first principles how large g(N) should get for
numbers of each size, and proved a number of theorems that a computer proof checker has verified step by step.

## The question

Goldbach's conjecture says that every even number larger than 2 is the sum of two primes. Nobody has proved it, but
computers have checked it for every even number up to 4·10^18, which is four billion billion. Saying that every even
number is a sum of two primes is the same as saying that g(N) always exists. In the whole range checked by computer,
the largest value of g(N) is only 9,781.

Here is a worked example. Take N = 98:

- 98 − 3 = 95 = 5 × 19
- 98 − 5 = 93 = 3 × 31
- 98 − 7 = 91 = 7 × 13
- 98 − 11 = 87 = 3 × 29
- 98 − 13 = 85 = 5 × 17
- 98 − 17 = 81 = 3 × 3 × 3 × 3
- 98 − 19 = 79, which is prime.

So g(98) = 19. We never need to try p = 2, because N − 2 is even and so is not prime once N is larger than 4.

Our question is a design problem rather than a question about typical numbers. We are allowed to choose N with great
care, and we want N − p to be composite for every prime p up to as large a bound as possible. The owner set the limit
of 200 digits. The question makes sense at any size, and the related problems further down change that rule in
different ways.

## Why it is hard

A random odd number with 200 digits is prime about one time in 230. For g(N) to be 160,357 or more, all 14,710 numbers
N − p, one for each odd prime p below 160,357, have to be composite. If each one were composite independently with
chance 229 in 230, the chance that all of them are would be about one in 10^28. No computer can try 10^28 numbers. The
whole GPU search described below tried about 10^14.

So luck alone will not do. We have to choose N so that most of the numbers N − p are composite for a reason we control,
and leave as little as possible to chance.

## How the search works

### The cover

The basic trick is simple. Suppose N leaves remainder 1 when divided by 3. Then for every prime p that also leaves
remainder 1 when divided by 3 (7, 13, 19, 31, and so on), the difference N − p is a multiple of 3, so it is composite.
One choice about N has dealt with about half of all the primes. Now do the same with 5: choose the remainder that N
leaves on division by 5, and for every prime p with that same remainder, N − p is a multiple of 5. That deals with about
a quarter of the primes still left. Carry on with 7, 11, 13 and so on, each time choosing the remainder that deals with
as many of the remaining primes as possible.

A list of such choices, one remainder for each small prime, is called a *cover*. Any list of choices can be met at
once. By the Chinese remainder theorem, the numbers that leave all the chosen remainders are exactly the numbers
N0 + k·M for k = 0, 1, 2, and so on, where M is twice the product of the small primes used (the factor 2 keeps N even)
and N0 is one particular solution. The research session spent much of its time on choosing the remainders well.

Each small prime we use multiplies M by itself, and that has a price. Our covers use 89 small primes: the 88 odd
primes from 3 to 461, and one more, either 463 or 491. Their product M already has 193 digits, which leaves room for only about 20
million numbers N0 + k·M below 10^200. That set is the *window* of one cover, and its numbers are the candidates. Using
more small primes would leave almost no room at all.

The best covers for a target of 170,000 deal with all but about 1,250 of the 15,497 primes below 170,000. The primes
left over are called *rows*. For a row p, the number N − p is not divisible by any of the 89 small primes, so it has to
turn out composite by luck. Because these numbers have no small factor, each of them is more likely than usual to be
prime, about one chance in 42. A candidate that beats 170,000 must have all of its roughly 1,250 rows composite, which
happens about once in 10^13 candidates. That is far better than once in 10^28, but it is still too many candidates to
give each one a full primality test, so each candidate goes through two cheaper stages first.

### The sieve

The *sieve* divides each row's N − p by every prime up to 10^8 (a hundred million). It does this for all the candidates
of a window together, which is very efficient: for each prime divisor, the candidates where it divides N − p sit at
regular intervals, so the program can mark them without doing any division at all. About two thirds of a typical
candidate's rows get a factor this way, which proves them composite. The rows that survive are now fairly likely to be
prime, about one chance in 14 each. Candidates with many surviving rows have almost no chance and are dropped. Only the
emptiest 0.75%, the candidates with the fewest surviving rows, go on to the next stage.

### The test

The surviving rows then get a *Fermat test*: compute 2^(n−1) and take the remainder on division by n. If the remainder
is anything other than 1, then n is certainly composite. If it is 1, then n is very probably prime. The program tests a
candidate's surviving rows in increasing order of p. As soon as one row passes the test, the candidate is dead, because
that row is probably prime. If every row fails the test, the candidate is a success.

### Near-misses

Testing rows in increasing order has a useful side effect. When a candidate dies at row p, then g(N) = p, provided that
row really is prime, which we then prove. If that p is above the standing record, the candidate is a new record even
though it missed the design target. We call this a *near-miss*. Two of our records, 158,209 and 160,357, are near-misses
of a search designed for 170,000. This was deliberate: a search built for a high target has a small chance of hitting
it and a fair chance of beating the record on the way.

### The machines

The search ran on graphics cards (GPUs) rented through Google Colab. Most of the work was done by RTX PRO 6000 cards,
with smaller L4 and T4 cards alongside; at its largest the fleet had three RTX PRO 6000 cards, three L4s and a T4. One
RTX PRO 6000 running the final program sieves about 92 million candidates a second and runs about 20 million Fermat
tests a second. The earlier program in this repository managed about 16,000 candidates a second on four processor
cores. From 22 November to the stop the GPU search used about 2,750 Colab compute units. The program is in
`goldbach/phd/campaign3_gpu/`; the fast sieve and test code inside it came from the performance session and is in
`goldbach/sieve200/`, `goldbach/fermat661/` and `goldbach/fermatw/`.

### Checking a record

A Fermat test is fast, but it can only prove that a number is composite. It never proves that a number is prime. So
every record is checked again, separately and slowly:

- For every prime p below g, the record comes with a reason why N − p is composite: the small prime from the cover that
  divides it, a factor found by trial division, or a failed Fermat test. For 160,357 there are 14,711 such reasons:
  13,517 from the cover, 586 from trial division, 607 from Fermat tests, and one for p = 2, where N − 2 is even.
- A proof that N − g is prime. For the 200-digit records this is an ECPP certificate (elliptic curve primality proving)
  made by the PARI/GP system, and checked again by a separate program written for this project
  (`goldbach/ecpp_check.py`).
- A second session recomputes g(N) from N alone, without using the first session's evidence.
- For most records, a formal proof in Lean. Lean is a program that checks every step of a mathematical proof
  mechanically. Our Lean proofs use only the three standard axioms of Lean's mathematics library and contain no unproved
  steps.

## What we found

### The main result: largest g(N) below 10^200

| g(N) | digits of N | found | how |
|---|---|---|---|
| 105,667 | 199 | before this repository | the published example this repository's Goldbach work started from |
| 119,419 | 199 | July 2026 | an earlier session in this repository (kept in `slop/`) |
| 125,269 | 199 | 22 Nov | the GPU search designed for 122,000 |
| 132,103 | 199 | 22 Nov | the same search, a few minutes later |
| 133,981 | 199 | 22 Nov | the same search |
| 146,191 | 200 | 22 Nov | the first hit of the search designed for 140,000 |
| 157,837 | 200 | 23 Nov | the first hit of the search designed for 150,000 |
| 158,209 | 200 | 23 Nov | a near-miss of the search designed for 170,000 |
| **160,357** | 200 | 24 Nov | a near-miss of the same search |

The record number is

```
95347106818046249718570776328527805394387907539756369117325081343361548773031798520383947495686099037769506167416423881905531645343709972339865033333397602306957446186830655985687114607924513408740178
```

For this N, the number N − p is composite for each of the 14,711 primes p below 160,357, and N − 160,357 is prime. Its
folder is `goldbach/records/budget_1e200_200digit_g160357/`, and the other records have folders next to it. Every record
in the table from 125,269 on has all the checks listed above, except that 132,103 has no Lean proof and no
second-session check yet.

### How good is 160,357?

Among all even numbers below 10^200, some must have a much larger g(N) than ours. A standard model of how primes are
spread out (the Hardy–Littlewood conjectures, which agree with every numerical test made so far) predicts how large the
very largest one is: about 2.13 million. We call this the *ceiling* for 200 digits, and we score a number by its
*closeness*, its g divided by the ceiling for its size. 160,357 is 7.5% of the ceiling. A typical 200-digit even number
has g(N) of about 1,600, so ours is about 99 times larger than typical.

The ceiling is computed from the model with nothing fitted to data (`goldbach/ceiling_model.py`). We checked it in two
ways: against g(N) computed exactly for 900 million random numbers of various sizes, and against the 69 record holders
found by the computer check of Goldbach's conjecture below 4·10^18. Both agree with it. Before this work the repository
used a single constant fitted to the computer-check data instead.

The owner's dream of two million is about the ceiling itself: probably only a handful of numbers below 10^200 come
close to it. More modest targets are far more common. The same model says that about 10^175 even numbers below 10^200
have g(N) of at least 213,070, which is 10% of the ceiling. Even so, that is only one in 10^25 of all even numbers below
10^200, and such numbers do not sit in the small, structured corner that a cover lets us search.

### Records in related problems

**No limit on the size of N (the height game).** If N may have as many digits as we like, the cover can use so many
small primes that every prime below the target is dealt with, and nothing is left to luck except one thing: N − g must
be prime, and that has to be proved. Proving that a number with tens of thousands of digits is prime is normally the
hard part. ECPP becomes impractically slow beyond a few thousand digits, and that had kept this game below about 4,000
digits. The way around it was to choose N so that N − g has a special shape, an odd number times a large power of 2,
plus 1.
For numbers of that shape there are classical proofs of primality that need a single large calculation (Proth's
theorem and the Brillhart–Lehmer–Selfridge test). That removed the limit. The record went from 1,157,341, for a
2,480-digit N, to 16,046,137, for a 91,752-digit N, by way of 1,200,109, 2,000,269, 5,000,251 and 10,000,141. The
construction came from this session; the GPU session scaled it up and found the three largest.

**The smallest N for a given g (the threshold game).** Here the question is turned round: how small can N be if g(N)
has to exceed a given value? Small numbers are cheap to test, so this game can be played much closer to the ceiling.
The most interesting target is 9,781, the largest g in the range checked by computer. The smallest number we know with a
larger g is

```
N = 30,625,623,272,505,310,405,982   (23 digits)   g(N) = 10,729
```

Before this work, the smallest such example in this repository had 150 digits. We also hold g above 20,000 at 46 digits
(g = 20,551) and above 30,000 at 63 digits (g = 30,139).

**The fewest digits for a given g (the fixed-gap games).** For g(N) of at least 200,000, the best is a 319-digit N with
g(N) = 207,307, found by the performance session on ordinary processors; it also found 216,289 at 347 digits and two
numbers at 400 digits. For g(N) of at least a million, the second analysis session found a 1,797-digit N with
g(N) = 1,021,897, against 2,480 digits before. In both games Lean has checked that N − p is composite for every prime p
below the stated g, which is all the game asks. That N − g itself is prime has been checked by strong probabilistic
tests but not proved; at these sizes a proof needs a long ECPP run that nobody started.

**Closeness.** Against the ceiling for its size, our best number is a 23-digit N with g(N) = 11,701, at 74.3% of the
ceiling. We also tracked a *closeness frontier*: the largest size at which we hold a number reaching a given closeness.
At the stop it stood at 50% up to 27 digits, 25% up to 48 digits, and 10% up to 110 digits. The owner's 10% target at
200 digits, g(N) of at least 213,070, was not reached; 160,357 is 7.5%.

## How close we came to 200,000

Everything in the plan rests on a model that predicts how often a candidate succeeds, and we tested that model many
times. Before the campaign aimed at 170,000, the GPU search had found 9 successes where the model expected 10.3.
Searches on ordinary processors at 100 and 150 digits found 173 against 175 expected, and on the 10% frontier 17
against 19.9. In
a direct audit of 56,191 real 200-digit candidates, the number of primes among their rows came within 0.1% of the
prediction. So we trust the model's forecasts, including the unwelcome ones.

The unwelcome forecast was this. At 200,000 the best covers leave about 1,500 rows instead of 1,250, and each candidate
then succeeds about once in 7·10^15 tries instead of once in 10^13. With the computing we had left on 25 November, a
search designed for 200,000 had a chance of about 1 in 240 of succeeding. That is the factor of 250.

So the GPU search was designed for 170,000 instead, a choice made to give the best expected final record. It had a good
chance of beating 170,000 outright and, through near-misses, of setting records on the way there. From 23 November to
the stop it looked at 67.5 trillion candidates under that design. The model expected 0.69 successes at 170,000, and we
saw none, which happens about half the time at that expectation. It expected 2.5 near-miss records and we saw two,
158,209 and 160,357. In the last day the two remaining cards also reported every candidate that got past 140,000, as an
extra test of the model: it expected 7.15 such events and there were 5, which is well within chance.

The search can be restarted from this repository: the programs regenerate the covers and skip the candidates already
done. On 25 November, with about 6,700 compute units left, the model gave such a restart on the same design an 85%
chance of beating 170,000, 46% of reaching 175,000, 17% of 180,000, 1.4% of 190,000, and about 1 in 750 of reaching
200,000, with an expected final record of about 175,000. At the stop, 6,395 units were left, so those figures are now
slightly optimistic. The GPU session estimates that an even chance of reaching 170,000 needs about four days on two RTX
PRO 6000 cards, or about 2,100 units.

## The search for a better method

When it became clear that 200,000 needed 250 times more computing than we had, the owner wrote: "Your only shot is
better maths. Do better maths then." The research session led this part, with help from most of the others. The question
was whether some mathematical idea could find the rare good candidates faster than checking them all, or make many of
the numbers N − p composite at once by some mechanism other than a cover and luck.

After two days the answer is that we found no such idea. We did find reasons why several natural ones cannot work. The
details are in `goldbach/sublinear/HANDOVER.md` and the notes it points to. Here is what was tried, roughly in the order
in which it looked promising.

**Better covers.** If a cleverer cover left fewer rows, everything after it would be cheaper. The research session
searched thirteen families of covers as far as they would go, and estimated by statistical counting how good any cover
at all could be. The covers in use turned out to be essentially the best there are: the statistical count puts a floor
within a row or so of the best cover found, and a theoretical estimate agrees within 2 to 3%. One family found along the
way (family B) gave 5% more successes, and the GPU search adopted it. Covers built from regular patterns, rather than
searched for, were 100 to 200 rows worse. Better covers cannot close the gap.

**Picking the best candidates without sieving them all.** Within each window, a few candidates have unusually few
surviving rows. If we could jump straight to them without sieving all 20 million, the search would go much faster. We
computed the sieve result for every one of the 21 million candidates of one window, with three programs that agree: on
average 506 rows survive, with a typical spread of 18 either way, and the best candidate has 412. From those exact counts, even a perfect
oracle that handed us the best candidate of every window for free would make the search only about 45 times more
productive, not 250 times. We also tested 79 other properties of candidates to see if anything beyond the count of
surviving rows predicts success. Nothing does.

The research session then found an exact way to state the problem. The condition "N is below 10^200" turns out to be a
single condition on N's remainders: a fixed weighted sum of them, taken as a fraction, has to land in a short interval.
This is proved in Lean (`Worlds/Arc.lean`). It turns the search into a problem of a familiar type, a knapsack-like
problem with one constraint, and every known method for such problems was then priced on the real cover: lattice
reduction, meeting in the middle with two sorted lists, decoding algorithms from coding theory, dynamic programming over
partial sums, and merging trees of lists. Each of them ends up either fixing more remainders, which uses up the freedom
in N, or scanning. The best case measured beats the best member of a cover's own window by one to four rows, which is
worth less than 10%, and it produces one number where a scan of the same cost keeps hundreds of thousands of good ones.

**Cheaper tests.** Most of the GPU's time goes into Fermat tests, so a check that is cheaper but almost as good would
help. Testing many numbers at once with batch certificates turned out to cost 3 to 7 times more. The best factoring
screen we found (Pollard's p − 1 method with small bounds) settles 1.9% of the numbers for the price of 2.2 tests, about
120 times short of paying for itself. Among 137,209 surviving rows that were tested, nothing visible in advance predicts
which ones are prime. And even a test 100 times cheaper than Fermat's would gain at most a factor of about 11, because
then the sieve would take all the time. One idea from sieve theory deserves a mention: a quick test of whether a number
has an even or odd number of prime factors would be worth a factor of four to ten here, depending on the model, and no
such test is known.

**A faster program.** The program itself was measured change by change. Keeping only the emptiest 0.75% of candidates
instead of 1.5% gave 5.6% more successes per hour and was adopted. Carrying partial results from one batch to the next
lost 1.1% and was reverted. A two-stage sieve and a cluster layout were withdrawn after measurement. Before measurement,
that package had been predicted to add 35 to 57%; the measurements are what count.

**Other kinds of N.** We tried numbers of special algebraic shapes, such as values of a polynomial. The Bateman–Horn
conjecture, which predicts how often the values of a polynomial are prime, says such numbers do worse than a plain cover
by a factor of about 700. Neighbours that share rows, numbers next to a highly divisible number, and covers shared by
pairs of numbers all lose against a plain cover too.

**Tools from other fields.** The research session ran nine independent lines of attack, each from a different field:
class field theory, algebraic groups and primality testing, the function-field dictionary, sieve theory, lattices and
additive combinatorics, coding theory and cryptanalysis, probability and complexity, harmonic analysis, and a wild card.
Each tested its proposals on real 200-digit numbers. Eight reported back; the coding-theory line was stopped by a safety
filter and not retried. None found a substitute. Some measurements from this round and the earlier ones:

- Lattice reduction and list decoding, tools from cryptography and from the theory of error-correcting codes, need a
  good candidate to stand out from the others far more than any candidate does. A typical candidate reaches 0.21 of
  what they need, the best one 0.25, and the best variant of the methods 0.36. A single decoding would also cost at
  least 10^16 elementary operations, against 3·10^10 to sieve a whole window.
- Meeting in the middle is at best 2.3 times worse than scanning.
- The methods behind the recent results on long gaps between primes (by Ford, Green, Konyagin, Maynard and Tao) do
  nothing at this size: their covering step only starts to work for far larger numbers.
- No two rows are tied together. Over a million pairs of rows of a real cover were tested, and they are prime together
  exactly as often as independent rows would be. The candidates of a window also behave like independent random draws.
- 26 reciprocity symbols and 37 other cheap invariants were tested, and none moves the rate of primes by even 1%.

**A small exact model.** We built a miniature of the whole search (N up to 10^9), where every number can be checked
completely, and scored eleven methods on it, seven of them new. None beats the plain search. One of them, searching the
neighbours of good candidates, helps in the miniature, but at full size it would be worth at most 3.5%.

**Toy worlds.** The owner suggested starting from simpler settings, such as groups, where proofs are easier, building a
library of tools there, and then seeing what transfers to the integers. The research session set up six such worlds,
with the Lean session and the second analysis session taking some of them. Two of them showed mechanisms that the
integers lack:

- In polynomials over a finite field, the standard toy model of the integers, there is a third way, besides small
  factors and luck, to force many of the analogues of N − p to factor. Whether a polynomial has an even or odd number
  of irreducible factors is fixed by its discriminant (Stickelberger's theorem), so for a well-chosen N whole families
  of them must factor. This is proved in Lean. It turned out to be weaker than it first looked: a single common
  remainder for all the small primes does the same job more cheaply.
- In polynomials and in the Gaussian integers, targets with a symmetry tie their rows together in groups that succeed
  or fail as one, so such a target needs fewer lucky outcomes. In the Gaussian integers, among numbers of size up to
  7,000, the best symmetric targets reached 101 and 121 where the best ordinary one reached 97 (a second program
  confirmed this up to size 3,000).

The ordinary integers keep everything built on remainders and on size: the cover, the one-condition reformulation, the
counting. They lose everything built on a symmetry, because the only symmetry of the integers that respects addition
is changing the sign; on a derivative, because any rule on the integers that behaves like a derivative is zero; and on a
kind of extension of the number system that the rational numbers provably lack (Minkowski's theorem). That is the
transfer table, and it explains why the toy-world gains do not carry over.

**The prize nobody can collect.** One target is large enough to matter. Below 10^200 there are numbers far better than
any member of our windows: at the 10% target, about 10^175 even numbers have g(N) of at least 213,070. The useful ones
have unusually few rows left after sieving by the primes up to 2,000: about 1,116, where members of the best cover have
1,309 give or take 14. A method that produced such numbers for less than the cost of about 550 primality tests each would
break even with the GPU search. An ideal one would be worth a factor somewhere between 20 and 60,000, depending on the
assumptions, which is enough to make 200,000 likely. We know what such a method would have to achieve, and we found no
way to build one. The second analysis session showed, on paper, that for arbitrary tables of this kind, finding such
candidates quickly would solve an NP-complete problem, a problem from a large family believed to have no fast solution
(no other session has read that proof yet). So a shortcut would have to use something special about the actual primes,
and every test of their structure (additive, multiplicative, lattice, spectral, statistical) found nothing usable.

**What this adds up to.** The covers are as good as covers can be, the program is close to what the hardware allows,
the tests cannot be made cheap enough to matter, and no tool we know finds the rare good numbers faster than looking at
all of them. The missing factor of 250 would need a new kind of idea. In my opinion the closest relative of this problem
is the search for "smooth" numbers inside the number field sieve, the fastest known method for factoring large numbers.
Decades of work there have found nothing better than sieving. That is a family resemblance, not a proved equivalence.

## Theorems

These are the results we consider proved. Unless marked otherwise, they are checked in Lean, in
`goldbach/lean/GoldbachGaps/`, and `goldbach/lean/HANDOVER.md` gives the name of each theorem. Lean guarantees that
every proof is correct. It cannot guarantee that a statement means what we say it means; that takes a person reading
the statement itself, which is usually a few lines.

**The records.** For the numbers below 10^200 with g = 119,419, 125,269, 133,981, 146,191, 157,837, 158,209 and 160,357,
Lean checks that g is prime, that N − g is prime, and that no smaller prime p has N − p prime. The same holds for
several of the small threshold records. For the fixed-gap numbers (319, 347 and 400 digits) and the million-gap
numbers (1,797, 1,997 and 2,196 digits), Lean checks that N − p is composite for every prime p below the stated g.

**How fast the record must grow.** For any fixed number A, however large, every large enough X has an even N up to X
for which N − p is composite for every prime p below A·ln X·ln ln X, where ln is the natural logarithm. For
X = 10^200, ln X is about 460 and ln ln X about 6.1. In words: the largest g(N) up to X grows faster than any fixed
multiple of ln X·ln ln X. Lean checks this with no unproved assumptions (`CoverEveryConstant.lean`). The idea, borrowed
from Erdős and Rankin's work on gaps between primes, is to give a whole block of small primes the remainders of one
common number. A first version, for every multiple below 1.349, needed Mertens' third theorem, which is not in Lean's
library; the Lean session proved that first (`Mertens.lean`). A faster growth rate is also checked in Lean: some even
N up to X has no summand below ln X·(ln ln X)²/(150,000·(ln ln ln X)²), which is roughly one more factor of ln ln X,
with a very small constant. The consultant session has a written proof of a slightly stronger version, with one more
very slowly growing factor (`goldbach/gaps_map/COHERENT_BLOCK.md`); that one is not in Lean.

These growth results hold for every size and use no luck, so they are far weaker than what the search finds: at 200
digits, A·ln X·ln ln X is only about 2,800 times A. Their interest is that they assume nothing about primes beyond what
has been proved.

They may not be new as statements. A 2026 preprint by Radomskii (arXiv 2610.14127) proves a general theorem that would
imply both, if one of its lemmas holds. That lemma sits in a section of about 24 pages that none of us has read in full,
and the preprint has not been refereed. What is ours either way is the elementary proofs and their machine check. An
expert should read Section 3 of that preprint before anyone claims novelty.

**Covers with no luck at all.** There is an explicit even N below 10^200 for which N − p has a prime factor of at most
491 for every prime p below 16,981. The odd primes up to 997 can deal with every prime below 41,659, and the odd primes
below 10,000 with every prime below 614,101 (both in Lean). With 238 and 302 small primes the reach is 70,111 and
98,731 (computed, and each can be checked from its list of remainders). How far the first n odd primes alone can reach
is known exactly for n up to 35: in Lean up to 9, computed twice up to 15, and once beyond that.

**Hardness.** For arbitrary tables of rows, deciding whether a window contains a candidate with no surviving rows is
NP-complete. That proof is on paper, by the second analysis session. Lean has a related result: if arbitrary numbers
replace the primes to be covered, deciding whether a cover exists at all is as hard as the satisfiability problem of
logic. Neither makes our particular problem hard, but they mean that a fast method would have to use something special
about the primes.

**Limits of search methods.** Lean proofs that certain kinds of method (lattice decoding, black-box search, lists of
remainders modulo one prime) cannot beat the plain search; that treating rows as independent can only overstate the
number of good candidates; and that the GPU's Fermat arithmetic is correct.

**The toy worlds.** Stickelberger's theorem in Swan's form, the parity mechanism and the family identity in polynomials
over finite fields, and the one-condition reformulation, all in Lean.

**Small numbers.** A program that lists the record holders of g (the even numbers whose g is larger than that of every
smaller even number, sequences A025018 and A025019 in the OEIS), proved correct in Lean and run inside the proof
checker. For every even N from 6 to 2^25, the least summand is at most 997.

## Mistakes, and how they were caught

A project like this makes mistakes, and the useful thing is to catch them. The sessions checked each other's work
throughout, and corrections were recorded in the files rather than quietly overwritten. The main ones:

- **Limits claimed too early.** The research session put forward two formulas for how far covers can reach as they
  grow, and the consultant session a third. All three were withdrawn, the research session's two on the same day, after
  the Lean session found a construction (giving many small primes the remainders of one common number) that beats the
  assumption behind them. No limit is known.
- **Speed-ups predicted before they were measured.** A package of program changes predicted to add 35 to 57% delivered
  5.6% for one part, a 1.1% loss for another, and nothing for the third.
- **Claims stated more strongly than they were proved.** I described the candidate search as "equivalent" to the
  smooth-number search in the number field sieve, when there is only a family resemblance and no proved reduction. A
  mechanism in the polynomial world was said to reach further than remainders could; a common remainder does the same
  more cheaply. "Symmetry divides the work by the size of the symmetry group" holds only in special cases, and by a
  smaller amount. One lower bound on a dynamic programme was false without an extra assumption, and its cost turned out
  to be about the square root of what was first said.
- **Numbers that were off.** The value of a perfect oracle was first put at a factor of 60 and is really 45. Some
  probabilities were 8% too high because they used an average density over a window. One campaign table used an old
  record (112,249) instead of the current one. A spread was misstated by a wide margin, which the Lean session caught;
  the conclusion survived. The coding-theory figures were corrected three times.
- **A false alarm.** A commit note said one Fermat kernel was wrong above 664 bits. Tests showed it exact, and no result
  was affected.
- **Missed messages.** The research session twice missed messages for one to two hours, and said so.

None of these touched a record. Every record was checked from its own evidence, by more than one program, and in most
cases by Lean.

## What is left

The remaining work is organised in `goldbach/REMAINING_WORK.md`, with what each item needs and roughly what it would
cost. The main items:

1. **Restart the 200-digit search.** The programs can restart from this repository, and the forecast above says what
   to expect: probably about 175,000, with a small chance of more.
2. **The prize.** Find a way to produce numbers below 10^200 with unusually few surviving rows without scanning. This is
   the only route we found that could reach 200,000, and nobody knows how to do it.
3. **Two predictions that were never measured.** Combining two or four sorted lists on the one-condition problem was
   predicted to gain a little and lose a little respectively; and a possible difference between candidates with even
   and odd index was seen at 2.6 standard deviations and then reversed in a later sample.
4. **Records that are easy to extend.** The fixed-gap 200,000 record below 319 digits, the million-gap record below
   1,797 digits, and the closeness frontier at 10% beyond 110 digits all have their tools ready.
5. **Proofs owed.** A Lean proof and a second-session check for 132,103; a proof that N − g is prime for the
   fixed-gap and million-gap numbers; and the stronger growth bound in full in Lean.
6. **Checks owed.** Several of the newest toy-world results have not been read by a second session, and the
   calibration of near-misses at 140,000 and of waiting times in the fixed-gap game was left inconclusive.
7. **The literature.** Read Radomskii's Section 3; search MathSciNet and zbMATH; read the classical papers our notes
   cite only second-hand.

## How to check our work

Every record folder has a `README.md` saying what was checked and how. To repeat the checks for the 160,357 record,
run these from the `goldbach/` folder. Each takes a few seconds; all four passed again while this letter was being
written.

```sh
R=records/budget_1e200_200digit_g160357

# Rebuild N from its cover and prove every N − p composite for p < g, using only Python's standard library
python3 ../slop/goldbach/records/verify_record.py $R/package_stdlib.json

# Check the ECPP certificate that N − g is prime, without PARI (needs the gmpy2 package)
python3 ecpp_check.py $R/complement_cert.gp $R/N_minus_g.txt

# Recompute g(N) from N alone (needs gmpy2)
python3 fscan/check.py $(python3 -c "import json; print(json.load(open('$R/record.json'))['N'])")

# The same with PARI/GP, which also proves N − g prime
gp -q $R/crosscheck.gp < /dev/null
```

To rebuild the Lean proofs, install `elan` (Lean's version manager), then run `lake exe cache get` and `lake build` in
`goldbach/lean/`. Most files take seconds; the record files take minutes each and up to about 7 GB of memory.
`lake env lean scripts/check_axioms.lean` then lists the axioms used by all 7,978 declarations of the library; only the
three standard ones appear. `goldbach/lean/HANDOVER.md` has the details.

## Who did what

| session | branch | what it did | its handover note |
|---|---|---|---|
| coordinator (this pull request) | `ccr-2ce9e63a-hn0fuw` | coordination and merging; the height-game construction and its first two records; the threshold-game scanner `tscan` and the 25- to 63-digit threshold records; the computed ceiling; second checks of records | this letter |
| GPU search | `ccr-8ffe9d7a-4ni11u` | the 200-digit GPU program and the Colab fleet; every record below 10^200; the larger height records; the record log `RESULTS.md` | `phd/campaign3_gpu/HANDOVER.md` |
| research | `ccr-d4a17dd0-7uu03r` | the covers in use (the 491 family and family B); the scanner `fscan`, which found the 23-digit threshold records; the search for a better method; the toy worlds | `sublinear/HANDOVER.md` |
| Lean | `ccr-36ca7b46-8twf14` | formal proofs of the records and theorems; checks of other sessions' claims | `lean/HANDOVER.md` |
| performance | `ccr-b8c25887-i6tn9f` | the fast sieve and Fermat code; the fixed-gap 200,000 records; the closeness frontier; cost measurements | `sieve200/HANDOVER.md` |
| second analysis | `ccr-c6e00296-3g7fp9` | the million-gap records; the forecasts and the campaign table; the two-stage design; toy worlds 2 and 4; the archipelagos study | `bottom_up/HANDOVER.md` |
| consultant | `ccr-cdb2641a-5zg8un` | the map of results; the literature search; the stronger growth bound on paper; checks of proposed mechanisms | `gaps_map/HANDOVER.md` |
| helper | `ccr-03a7c98c-0b9khc` | covers at 290 to 400 digits; rechecks of the ceiling; processor scans | `sublinear/contractor_results/` |
| outside reviewer | `ccr-7a21f8cd-hof5z0` | a review of the whole effort from outside, with its own checks | `review/` |

All of these branches are merged into this pull request at their final commits. Nothing outside `goldbach/` is changed.

## Glossary

- **g(N), the least Goldbach summand.** For an even N, the smallest prime p for which N − p is also prime.
- **Cover.** A choice of remainder for each of a set of small primes. Every prime p that shares N's remainder for one of
  them gives a composite N − p.
- **Row.** A prime below the target that the cover does not deal with; N − p must then be composite by luck.
- **Window.** The numbers below 10^200 that satisfy one cover, about 20 million of them.
- **Sieve.** Striking out the rows that have a factor below some bound (here 10^8), for all candidates of a window at
  once.
- **Fermat test.** A quick check that proves a number composite or says it is very probably prime.
- **Near-miss.** A candidate that misses the design target but still beats the record.
- **ECPP.** Elliptic curve primality proving, a method that produces a certificate of primality anyone can check.
- **Lean.** A program that checks mathematical proofs step by step.
- **Ceiling.** The largest g(N) expected among all even numbers up to a given size, from the Hardy–Littlewood model.
- **Closeness.** A number's g divided by the ceiling for its size.
- **Nat.** A unit some of our notes use for amounts of work or chances: one nat is a factor of e, about 2.72. Five and a
  half nats is a factor of about 250.
- **NP-complete.** A problem in a large family of problems that are believed to have no fast general method; a fast
  method for one would give a fast method for all.
