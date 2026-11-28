# World 3: the Goldbach problem in F_q[t], enumerated exhaustively

Asked by the research session on 26 November 2026, as part of the programme of toy worlds (a score that is a sum over
"primes" of functions of the residues, and a constraint that couples the coordinates: can the points with extreme score
be produced at a cost proportional to the output?). This directory is the exact data for the function-field world.

**Setting.** q odd (3, 5, 7, 9). Members: the polynomials N of degree n with a fixed leading coefficient (1, and as a
second family a non-square). Rows: the monic irreducibles Q, in order of degree and then of index (the index of a monic
polynomial of degree d is the number with base-q digits its coefficients c_0, …, c_{d−1}; in F_9 = F_3[i] the label of
a + bi is a + 3b). A row succeeds when N − Q is irreducible. L(N) is the number of rows before the first success and
D(N) the degree of that row, so every row of degree below D fails. Depth: a row is *left* at depth z when N − Q has no
factor among the first z irreducibles. A *cell* at a line of z moduli is a choice of one class for each; by
`card_monic_cell` every cell of moduli of total degree at most n has exactly q^(n − total degree) members.

**What is in the kernel** (`GoldbachGaps/FunctionField/Families.lean`, standard axioms; signatures in
`GoldbachGaps/FunctionField/STATEMENTS.md`): `card_monic_cell` (cells are exactly equidistributed),
`irreducible_sub_comp_X_add_C_iff` (if N(t + c) = N(t), the rows Q(t) and Q(t + c) succeed together),
`not_irreducible_sub_of_derivative_eq` (a row with Q′ = N′ never succeeds), `discr_of_derivative_eq_C` and
`not_irreducible_sub_of_derivative_sub_eq_C` (when N′ − Q′ is a non-zero constant the discriminant is
±lc^(n−2)·γ^n, and for even n with χ(−1)^(n(n−1)/2) = 1 the row fails), `not_irreducible_sub_of_aligned` (aligned
classes, section 3). Everything else on this page is measured.

All tables are in `tables.md` (written by `tables.py`); the numbers quoted below are copied from it.

## 1. The three questions

### (a) Is the best that exists against the best that cover-and-scan finds of the same shape as for the integers?

*The record is where the count over class vectors puts it.* Take the cells at a line and let the rows left be
independent with their exact average chance. The number of members this model expects at the record target is
between 0.2 and 10 in 38 of the 47 instances; the others are six of the eight structured cases of (b) and three
generic ones at 0.09, 0.18 and 0.19. At lower targets it is biased high: over the 28 instances with at least 10^6 members, predicted over
true has median 1.21 at 3,000 successes or more (range 1.06 to 1.46), 1.31 at 300 to 3,000, 1.46 at 30 to 300 and
1.54 at 10 to 30 (range 0.26 to 2.4). At q = 3, n = 18: 12,700 predicted for 10,026; 1,510 for 1,025; 161 for 101;
19.9 for 10; 0.56 for 1; and the level at which it expects one member is 738 rows, the record 754. Without cells
(every row with chance 1/n) the predicted record is half the true one at q = 3 (346 against 754).

*The optimum is not in a best cell*, as for the integers, and by more. q = 3, n = 18 (3.9·10^8 members), the record
target (754 rows), line = the first 8 irreducibles (cells of 27 members): at the line the best cells have 40 rows
left; after the cubics the optimum over all members has 24 and the best member of the best cells 26; then 15 against
18 after degree 4, 10 against 13, 6 against 10, 3 against 5, 1 against 4, and at full depth 0 against 4 (the integers'
miniature: 6 against 10 at depth 199). The cell of the optimum has 54 rows left at the line, 14 more than the best
cell (integers: 0 to 6 more), and 3.1% of all members are in cells at least as good. Over all instances the record's
cell has a median 8 rows more than the best cell, a median 4% of the members are in cells at least as good, and
cover first reaches the record after a median 3% of the members (in the integers' miniature the optimum was within
the best 0.2% of the cells). The larger distance is the smaller price of a row: a row left at the line costs
−ln(1 − p) = 0.34 nats here (p = 0.29 at q = 3, n = 18) against 1.6 in the integers' miniature, so luck outweighs the
cover sooner. With a share of the work, cover first finds at q = 3, n = 18 (record 754): 479 rows within 0.01% of the
members, 607 within 0.1% and within 1%, the record within 10% (`tables.md`, second table).

### (b) Where do the true optima sit?

Never at N′ = 0. In the enumerable range the record member is generic in 39 of the 47 instances (no symmetry,
derivative of high degree) and uses parity by luck: the record at q = 3, n = 12 has 24 rows left at the line, where the
best cell has 17, and only 2 of them are squarefree with an odd number of factors, where 12 are expected. The eight
structured records are all at n divisible by p (the monic record at 9^9 is shared by three translation-invariant
members, among them t⁹ − t + 1, invariant under every translation of F_9):

| instance | record member | L | best generic | members the cell model expects at L |
|---|---|---|---|---|
| q = 3, n = 9, monic | g(t³ − t), translation-invariant | 200 | 168 | 0.13 |
| q = 5, n = 10, monic | u² + 2u + 4, u = t⁵ − t | 206 | 185 | 0.09 |
| q = 5, n = 10, non-square | translation-invariant | 207 | | 0.09 |
| q = 7, n = 7, non-square | c(t⁷ − t + 4) | 149 | 77 | 0.0001 |
| q = 9, n = 6, non-square | translation-invariant (the whole top 12) | 97 | | 0.009 |
| q = 9, n = 6, monic | G(t³) + t² + ct + d (the whole top 12) | 120 | | 0.0001 |
| q = 9, n = 9, monic | t⁹ − t + 1 and two members invariant under a line of F_9 | 151 | 148 | 7.4 |
| q = 9, n = 9, non-square | translation-invariant | 161 | | 2.5 |

Two mechanisms explain them, and both are theorems.

*Symmetry.* If N(t + 1) = N(t) then N − Q(t + 1) = (N − Q)(t + 1), so a row and its translates succeed together
(`irreducible_sub_comp_X_add_C_iff`). The rows of a degree are a union of orbits of p, so "every row of degree d
fails" is a p-th of the independent trials for such a member. The invariant members are the polynomials g(t^p − t):
q^(n/p) of the q^n. Section 2 measures what this gives; the saving is for complete degrees only.

*Parity through the derivative.* disc(N − Q) is a resultant with N′ − Q′, so the parity of the number of factors of
N − Q depends on N only through N′ − Q′ and N modulo N′ − Q′. Rows with Q′ = N′ never succeed. When N′ − Q′ is a
non-zero constant γ the discriminant is ±lc^(n−2)·γ^n, which for even n does not depend on the row. For
N = G(t^p) + t² + ct + d that covers every monic quadratic at once (36 rows at q = 9): the record at q = 9, n = 6.
The desert theorems of `ParityDesert.lean` are the case N′ = 0.

### (c) What does selecting members by their count of odd-parity rows buy?

Order the members by the number of rows left at the line that are squarefree with an odd number of factors (the only
rows that can succeed), and compare with cover first at the same line. Members examined before half of the successes:

| q = 3, n = 18, cells of 27 | successes | cover first | parity order | ratio |
|---|---|---|---|---|
| | 10,026 | 10,034,889 | 608,013 | 16.5 |
| | 1,025 | 11,205,857 | 314,278 | 36 |
| | 101 | 9,643,250 | 165,925 | 58 |
| | 10 | 9,619,686 | 42,273 | 228 |
| the record | 1 | first reached after 10,536,683 | after 35,822 | |

At q = 5, n = 10 the ratios are 12, 17, 28, 37, 57, 179, 1,295 from 10,408 down to 10 successes; at q = 9, n = 8 they
are 21, 34, 41, 73, 163, 538, 3,574. Over all instances the parity order reaches the record after a median 0.006% of
the members, cover first after 3%. So the gain is 10 to 20 at ten thousand successes and 10² to 10⁴ near the record,
not a small factor. The reason is the size of the instances: an odd squarefree polynomial with no factor of degree at
most z is irreducible or has at least three factors of degree above z, so parity and a shallow sieve nearly decide
irreducibility (q = 3, n = 15: an odd row left at the line is irreducible with chance 0.67, after the cubics 0.85,
after the quartics 0.98; q = 3, n = 18: 0.54 after the quadratics). Where the chance is small the gain is the usual
0.5/Φ(−λσ) (parity alone, no sieve, q = 3,
n = 12, 1,018 successes: predicted 6.9, measured 6.8). The parity count needs one discriminant for every row left of
every member: it saves irreducibility tests, not members touched. The research session's reading through the sieve:
with u = n over the depth of the sieve, a rough polynomial with an odd number of factors is irreducible with chance
2/(u·ω(u) + ρ(u − 1)) (ω Buchstab's function, ρ Dickman's; exact for u ≤ 3); these instances sit at u = 3 to 6 and
the 200-digit search at u about 25, where a free parity would be worth a factor 2 (1.4 nats in all) and no more.
The ratios above grow toward the record because the share of members kept shrinks there, not because parity knows
more.

## 2. The translation-invariant family beyond the enumerable range (`symfam.py`)

For prime q the family g(t^q − t) is enumerated for n up to 33 with one FLINT factorisation per orbit of rows. The
counts for *all* q^n members come from the cell model, which the exhaustive runs calibrate (level at which one member
is expected against the true record: 3^18: 738 and 754; 3^15: 481 and 481; 3^12: 297 and 313; 5^10: 180 and 185 for
the best generic member; 7^7: 89 and 78; members with every row of degree at most 7 failing at 3^18: 206 expected,
121 true).

**The law.** Let F_d be the number of members of the family with every row of degree at most d failing, and G_d the
number of all members with the same. Then

    F_d ≈ (members of the family) × (G_d / all members)^(orbits / rows),

orbits and rows being those of degree at most d. Most orbits have p rows, and then this is G_d^(1/p); the rows that
the translation fixes (those in F_p[t^p − t]: 2 of the 8 cubics and 2 of the 116 sextics at q = 3) are orbits of one
(the refinement is the research session's verifiers'). Over the 59 entries of the table with F_d ≥ 20 the median
error is 5.6% with the orbit count and 9.7% with the plain p-th root; the largest is 46% (21 against 11 at
5^15, d = 4). For instance at q = 3, n = 30 (59,049 members of 2·10^14): d = 6, 7, 8 give F = 14,681, 2,841, 51
against cube roots 15,100, 3,140, 73; at q = 5, n = 25 (3,125 of 3·10^17): d = 2, 3, 4, 5 give 2,831, 2,067, 809, 9
against fifth roots 2,760, 2,020, 728, 15; at q = 7, n = 21 (343 of 6·10^17): d = 1, 2, 3, 4 give 343, 284, 133, 4
against seventh roots 326, 281, 134, 3.8. Part of it is an ordinary cover: for q = p every member of the family is
constant on F_p, so N − (t − a) has the root a + N(0) and every linear row fails by divisibility.

**What it gives.** In terms of D (every row of degree below D fails), the family of q^(n/p) members attains the D of
the best of all q^n members in every case computed (16: q = 3: n = 9 to 33; q = 5: n = 10 to 25; q = 7: n = 7 to 21), and
a larger one in three (3^9: 7 against 6; 5^10: 5 against 4; 3^21: 9, where the model expects 0.005 members of all
with D = 9). A member with "every row of degree at most d
fails" costs the p-th root of the generic work.

**What it does not give.** Inside a degree the first j rows lie in about j different orbits, so a family member
faces as many independent trials as a generic one. Above the last degree it passes, its L runs on like a generic
member's: the family's best L sits just above a degree boundary (1,572 = 1,318 + 254 at 3^21; 2,056 = 1,318 + 738 at
3^24; 582 = 508 + 74 at 3^18) and is above or below the best L of all members according to where the generic level
falls between two boundaries (above at 3^21 and 3^24, below at 3^18 and 3^27, equal at 3^30: 2,190 against 2,214). The same holds for the family
invariant under every translation of F_q, the q(q − 1) polynomials λ(t^q − t + c) (`as_family.py`): its largest D
is the generic one or more (D ≥ 4 at q = 5 and 7, where the generic level has D = 3; D = 3 at q = 11 and 13), its
largest L is not (96 at q = 11, 145 at q = 13, where the naive level is 277 and 417).

The member with L = 1,572 was checked not to be a further mechanism: over the 2,187 members of that family the number
of successful orbits among the 270 orbits of degree-8 rows is distributed as independent trials with the generic
chance (0.3 for an orbit left after degree 3), the best members have 10 orbits left, and 5 members have no success at
degree 8, as that predicts (`famdist.py`).

The tool, stated for any world: a group of ring automorphisms that fixes N and permutes the rows replaces the rows
of every orbit-closed set by their orbits. F_q[t] has t ↦ at + b and the Frobenius on the coefficients, and its
orbit-closed sets are the degrees; Z has only ±1. The Frobenius is a second instance: over F_9 it fixes the members
with coefficients in F_3, rows off F_3[t] pair up, and for even n the rows in F_3[t] fail outright (a polynomial of
even degree over F_3 is never irreducible over F_9). Measured with `w3` (family `frobenius`): every row of degree at
most 2 fails 28, 27, 21 and 10 times more often among those members than among all, at n = 6, 7, 8, 9
(`frobenius.txt`; the research session's verifiers found the same range), and the record of 9^9 is one of them.

## 3. Aligned classes (`aligned.py`)

A third design, the research session's: one polynomial R of degree J + 1 gives the class at every modulus of degree
at most J (N ≡ R modulo their product V_J). Then a row Q is struck exactly when R − Q has a factor of degree at most
J (`dvd_sub_iff_of_aligned`): every monic Q of degree J + 1 except the R − c (`not_irreducible_sub_of_aligned`), and
the rows of lower degree except those with R − Q irreducible. Its figures are reproduced: F_3, J = 3:
R = x⁴ + 2x² + 2 leaves none of the 32 rows of degree at most 4; F_5, J = 2: 3 of 55; F_7, J = 1: 5 of 28. It is an
explicit design with room deg V_J, a p-th of the parity desert's. It is not the best choice of classes: where every
choice can be enumerated the best cells leave fewer rows of the same target.

| q | J | moduli (total degree) | rows of degree ≤ J + 1 | fewest rows left, all cells | cells attaining it | fewest, aligned cells | aligned cells attaining it |
|---|---|---|---|---|---|---|---|
| 3 | 1 | 3 (3) | 6 | 0 | 2 of 27 | 1 | 3 of 9 |
| 3 | 2 | 6 (9) | 14 | 0 | 680 of 19,683 | 1 | 8 of 27 |
| 5 | 1 | 5 (5) | 15 | 0 | 2 of 3,125 | 3 | 10 of 25 |
| 7 | 1 | 7 (7) | 28 | 2 | 21 of 823,543 | 5 | 21 of 49 |
| 3 | 3 | 14 (33) | 32 | not enumerable | | 0 | 3 of 81 |
| 5 | 2 | 15 (25) | 55 | not enumerable | | 3 | 5 of 125 |
| 11 | 1 | 11 (11) | 66 | not enumerable | | 9 | 55 of 121 |

In the exhaustive runs "the best cells" are always the best over every choice of classes, so the aligned cells are
among the cells compared there; their targets (rows of degree at most J + 1, with V_J of degree at most n) are far
below the records of section 1.

## 4. Checks

`check_w3.py` recomputes, with FLINT factorisations of every member and none of the sieve code, the histogram of L,
the rows left after the linear factors and the count of odd-squarefree rows with the successes at every level, on
q = 3 (n = 8; n = 7 with leading coefficient −1), q = 5 (n = 5) and q = 7 (n = 4, non-square): identical. Every run
also checks the number of irreducibles of degree n, the number of squarefree polynomials (q^n − q^(n−1)) and that the
Möbius function sums to 0. `symfam.py` reproduces the family's records of the exhaustive runs (297 at 3^15, 206 at
5^10).

## 5. Files

`w3.c` (the enumeration: `w3 q n mu b OUT [extra cutoff ranks] [-l line ranks] [-t targets]`; mu is the inverse of the
leading coefficient, b the number of low coefficients in a block, rows of degree below b are used), `run_all.sh` (the
runs of this page), `analyse.py` (every table of one run), `summary.py`, `tables.py` (the tables of this page →
`tables.md`), `check_w3.py`, `symfam.py q n dmax [quadratics in the line]`, `as_family.py q`, `as_rate.py`, `famdist.py`, `outlier.py`,
`aligned.py q J`. `runs/` holds
the outputs without the four bulky kinds of line (the histograms by depth and the joint tables, 60 MB in all; rerun
to get them), `tables/` the output of `analyse.py` for each run, `sym/` the outputs of `symfam.py`. The largest runs
(3^18, 9^9: 3.9·10^8 members) take about an hour and 1 GB each; needs gcc, python-flint for the checks and the family.
