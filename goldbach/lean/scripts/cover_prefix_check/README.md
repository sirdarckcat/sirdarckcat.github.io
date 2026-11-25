# A referee's second read: the entropy of the small moduli

The research session's write-up (`goldbach/sublinear/README.md` on branch `ccr-d4a17dd0-7uu03r`, section
"The entropy of the small moduli: the limit does not hold", read at commit `fbf0b09`; its code
`cover_price_prefix.py`, its table `cover_price_prefix.txt`) withdraws the limit `1.1275` of the first read
(`../cover_limit_check/`). In its place it puts the same price recursion with a constraint: the entropy
of every prefix of the moduli, taken in increasing order, must not be negative. It asked (25 November
2026, 10:24 UTC) for a referee's read of four things:

* (a) the identity "the entropies of the levels sum to `ln g0`" and the sign of the partial sums;
* (b) whether "every prefix in increasing order" is the right family of constraints or only a necessary one;
* (c) the dual form of the constrained count;
* (d) the argument for the limit, `D(n) ≤ (e^γ/(2 C₂) + o(1)) · r ln² r / ln ln r`.

This directory is that read. Nothing here is a proof.

## The verdict

* **(a) holds, with one input that is not what the write-up takes it to be.** My implementation, written
  from the description and not from the code, reproduces all 24 rows of the write-up's table to the last
  printed digit when it is given the write-up's dispersions, and the identity holds to rounding
  (`10^-11`). But the dispersion at the smallest moduli is not "nearly 0". Computed from the primes
  themselves (exactly, and checked against the enumeration of every class vector) it is 0.058, 0.057,
  0.054 at the moduli 3, 5, 7 for `Q = 300,000`, where the Hardy–Littlewood sum gives −0.18, −0.07, −0.003,
  cut to `10^-4`. With the dispersions from the primes the deficits are larger and begin at the first
  moduli, and every figure moves by 1 to 6%: as much as the constraint moves it.
* **(b) is necessary inside the model and cannot be settled inside it.** The recursion is not invariant
  under the order of the moduli: at 1,228 moduli and 300,000 it gives a loss of 3,349 in increasing
  order, 3,452 with the six smallest moduli first and the rest in decreasing order, and 1,606 in
  decreasing order (measured: at most 3,438). So the increasing order is singled out by where the model's
  closure is accurate, not by the problem, and other families of constraints cannot be tested by
  reordering. What the numbers say: with either set of dispersions, measured over constrained rises by
  about 5% from the middle of the range to the end of complete covers. The constraint as it stands does not
  remove that trend; what is missing acts in the direction of fewer covers near the end.
* **(c) is correct.** Weak duality is immediate; strong duality holds because the maximiser inside is
  unique. Numerically: at every point the tilts of the dual's minimum satisfy the constraints with
  equality where the multiplier is positive, and their primal value equals the dual value; and a direct
  maximisation of the primal at 89 moduli (SLSQP, which knows nothing of the dual) lands on the same
  value to `10^-9`.
* **(d) does not hold.** The step "the frozen moduli can do no better than random classes" is true of the
  model and false of the primes. Give every modulus in a block `(z, x/4]` the class of one common
  integer. Then the block leaves a row `q` only if `N₁ − q` has no prime factor in the block, and by the
  upper-bound sieve for prime pairs that is `O(ln ln x / ln x)` of the rows, against `ln z/ln x` for
  random classes: a classical device (Erdős, Rankin). With that prefix the write-up's own count for the
  top moduli forbids nothing below about `x ln³x · ln₃x / (3 (ln₂x)³)` and allows more than with random
  classes at every size, so the bound with `1/ln ln r` is not derived; and in outline the same device gives a rigorous `D(n) ≥ c · r ln² r · ln₃ r / (ln₂ r)²`,
  which is more than every constant times `r ln r`. None of this shows at the sizes that can be computed:
  the block leaves 2% fewer rows than random classes at `x = 10^4`, 9% fewer at `10^6`, and half as many
  only near `x = 10^25`.

## The model, as implemented here

Rows: the odd primes below `Q`. Moduli: the odd primes up to `x`, in some order. Before a modulus `s`
there are `A` rows alive, `μ = A/(s − 1)` per nonzero class. With tilt `t` the chosen class holds
`μ e^{v t}` rows and the level has entropy `ln(s − 1) − μ (t e^{v t} − k(t))`, `k(t) = (e^{v t} − 1)/v`,
where `v` is the variance over the mean of the alive rows in a class of `s` when the moduli before `s` have
uniform random nonzero classes. The count is the maximum over the tilts of the sum of the entropies, with
a price `β = 40` on every row left at the end; "with the constraint" adds that every partial sum is `≥ 0`.

`prefix_check.py` differs from the write-up's code in two ways, both on purpose.

* The dispersion is exact for the primes below `Q`. Two rows at difference `d` are both alive with
  probability `φ² G(d)`, `G(d)` a product over the earlier moduli, and the number of pairs of rows at
  every difference comes from one autocorrelation of the indicator of the primes. Rows that are moduli
  themselves are treated as they are (a row `q` is never struck by the modulus `q`; the row `s` lies in no
  nonzero class of `s`). The result agrees with the enumeration of every class vector to `4·10^-14` in
  seven small configurations, including orders in which 3 is not first.
* The moduli can be taken in any order.

## (a) The identity, the sign, and the input at the smallest moduli

**With the write-up's dispersions** (`with_writeup_dispersions.txt`): loss as it was, lowest prefix
entropy and where, loss with the constraint, the largest frozen modulus and the weight at 3 agree with
`cover_price_prefix.txt` in every digit printed, at all 24 points. The sum of the level entropies minus
`Σ ln(s − 1) − p_start · rows` is below `10^-11` everywhere. So the computation is right.

**The dispersion at the smallest moduli** (`dispersions.txt`). At `Q = 300,000`:

| modulus | 3 | 5 | 7 | 11 | 13 | 17 | 19 | 23 | 29 | 31 | 37 | 41 | 43 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| from the primes | 0.058 | 0.057 | 0.054 | 0.112 | 0.136 | 0.169 | 0.220 | 0.231 | 0.277 | 0.297 | 0.302 | 0.326 | 0.337 |
| Hardy–Littlewood pair sum | −0.184 | −0.075 | −0.003 | 0.074 | 0.112 | 0.158 | 0.185 | 0.219 | 0.254 | 0.270 | 0.298 | 0.316 | 0.328 |

Above 43 the two agree: mean difference 0.0003, root mean square 0.003 (0.009 at `Q = 15,907`). Below, the
pair sum is low by 0.05 on average, and negative at 3, 5, 7, which a variance cannot be. The value at 3
can be read off directly: the two classes of 3 hold 12,970 and 13,025 of the 25,996 rows, and
`27.5²/12,997.5 = 0.058`. It is the imbalance of the primes between classes, of relative size `1/ln Q`,
which a smooth density does not have; and it is usable: the fuller class of 3 strikes 27 more rows than
the mean. (The write-up notes that `cover_price_hl.py`'s lower cut of 0.02 at the moduli 3 to 17 added
gain "where the true value is nearly 0". The true value there is 0.05 to 0.17.)

**With the dispersions from the primes** (`table.txt`; "write-up" is `cover_price_prefix.txt`):

| moduli | Q | loss as it was: write-up, primes | lowest prefix entropy (at modulus): write-up, primes | loss with the constraint: write-up, primes | measured | measured / constrained: write-up, primes |
|---|---|---|---|---|---|---|
| 89 | 10,000 | 284.0, 275.5 | 0.7 (3), 0.1 (3) | 284.0, 275.5 | 271.2 | 0.955, 0.984 |
| 89 | 14,000 | 391.3, 367.9 | -0.7 (53), -16.8 (43) | 391.3, 373.4 | 380.0 | 0.971, 1.018 |
| 89 | 15,300 | 425.6, 395.1 | -5.5 (83), -25.2 (53) | 425.7, 405.3 | 422.4 | 0.992, 1.042 |
| 89 | 15,907 | 442.9, 416.4 | -7.9 (113), -23.6 (61) | 443.7, 424.7 | 439.4 | 0.990, 1.035 |
| 138 | 18,559 | 437.1, 426.2 | 0.7 (3), -4.2 (31) | 437.1, 426.4 | 423.0 | 0.968, 0.992 |
| 138 | 23,198 | 539.4, 515.1 | -4.6 (61), -22.4 (47) | 539.5, 522.5 | 524.1 | 0.971, 1.003 |
| 138 | 26,291 | 606.0, 587.9 | -12.8 (89), -24.7 (73) | 606.6, 591.8 | 599.3 | 0.988, 1.013 |
| 138 | 28,766 | 661.2, 630.3 | -21.7 (113), -41.1 (89) | 662.5, 642.7 | 658.5 | 0.994, 1.025 |
| 167 | 15,000 | 334.0, 315.0 | 0.7 (3), -9.1 (5) | 334.0, 319.4 | 315.5 | 0.945, 0.988 |
| 167 | 25,000 | 542.4, 524.6 | -0.4 (47), -14.3 (47) | 542.4, 528.0 | 520.0 | 0.959, 0.985 |
| 167 | 38,000 | 808.6, 779.8 | -34.6 (139), -52.0 (113) | 811.4, 790.7 | 802.0 | 0.988, 1.014 |
| 167 | 40,111 | 851.4, 820.1 | -42.7 (157), -60.1 (131) | 855.3, 833.7 | 857.0 | 1.002, 1.028 |
| 238 | 42,067 | 796.9, 774.1 | -13.8 (83), -30.6 (83) | 797.6, 780.1 | 773.8 | 0.970, 0.992 |
| 238 | 52,583 | 984.5, 955.1 | -37.4 (131), -56.9 (113) | 987.8, 967.7 | 966.9 | 0.979, 0.999 |
| 238 | 59,594 | 1,112.1, 1,082.0 | -58.7 (173), -76.8 (151) | 1,118.6, 1,099.1 | 1,123.4 | 1.004, 1.022 |
| 238 | 65,203 | 1,208.7, 1,168.7 | -77.1 (199), -100.0 (181) | 1,218.3, 1,194.7 | 1,227.9 | 1.008, 1.028 |
| 302 | 59,239 | 1,031.0, 1,005.6 | -29.7 (113), -47.7 (109) | 1,033.4, 1,015.8 | 1,013.9 | 0.981, 0.998 |
| 302 | 74,048 | 1,271.6, 1,231.9 | -63.0 (173), -89.1 (151) | 1,278.9, 1,256.7 | 1,268.0 | 0.991, 1.009 |
| 302 | 83,921 | 1,434.1, 1,397.7 | -92.3 (211), -114.7 (199) | 1,446.7, 1,424.8 | 1,464.3 (upper bound) | 1.012, 1.028 |
| 302 | 91,820 | 1,562.9, 1,517.9 | -119.2 (271), -144.1 (229) | 1,580.9, 1,556.8 | 1,605.9 (upper bound) | 1.016, 1.032 |
| 429 | 50,000 | 794.6, 775.7 | -0.8 (47), -16.0 (47) | 794.6, 779.0 | 771.6 | 0.971, 0.991 |
| 429 | 100,000 | 1,538.8, 1,512.3 | -72.5 (181), -90.8 (167) | 1,548.1, 1,530.1 | 1,541.7 | 0.996, 1.008 |
| 1,228 | 100,000 | 1,199.0, 1,182.2 | -4.5 (53), -17.8 (53) | 1,199.1, 1,185.0 | 1,186.2 | 0.989, 1.001 |
| 1,228 | 300,000 | 3,409.1, 3,348.8 | -218.8 (337), -260.8 (317) | 3,452.5, 3,425.6 | 3,437.7 (upper bound) | 0.996, 1.004 |

* The sign is confirmed, and more so: the lowest prefix entropy is −261 instead of −219 at 1,228 moduli,
  and negative prefixes appear earlier (−9 at the modulus 5 for 167 moduli and 15,000, where the
  write-up's table has none). In the recursion as it was, the level of the modulus 3 alone has entropy −25
  at 1,228 moduli and 300,000: it is asked for a class 1.5% above the mean, 200 rows, where the fuller of the
  two classes is 27 above it.
* The recursion as it was is sensitive to these few inputs: 3,349 instead of 3,409. The three moduli 3, 5,
  7 carry 45 of the 60 (`sensitivity.txt`). The constrained count is less sensitive: 3,426 instead of
  3,452.5, of which 3, 5, 7 carry 17 and the moduli up to 43 all but 3.
* With the dispersions from the primes the agreement in the middle of the range improves (measured over
  constrained 0.984 to 1.003, against 0.945 to 0.99), and near the end it is worse (1.02 to 1.04,
  against 0.99 to 1.016). The trend is the same in both columns: the ratio rises by 5 to 6% from the
  middle of the range to the end. So the agreement "within 1% near the end" owes something to the low
  dispersions at the smallest moduli.
* At 1,228 moduli and 300,000 the 500,000-sweep run, an upper bound for the loss, is 15 below the
  write-up's constrained figure and 12 above the one from the primes. Only the second is compatible with
  the count being a maximum. The difference between the two is a third of the effect of the constraint
  there (77), so this point does not test the constraint to better than that.

**Where complete covers end** (`ends.txt`), `D/(x ln² x)`:

| x | 463 | 797 | 997 | 1,499 | 1,999 | 2,999 | 9,973 |
|---|---|---|---|---|---|---|---|
| as it was: write-up, primes | 0.913, 0.978 | 0.933, 0.971 | 0.952, 1.000 | 0.991, 1.025 | 0.995, 1.023 | 1.019, 1.034 | 1.074, 1.089 |
| with the constraint: write-up, primes | 0.912, 0.959 | 0.929, 0.957 | 0.944, 0.971 | 0.975, 0.993 | 0.975, 0.987 | 0.988, 0.997 | 1.008, 1.013 |
| the write-up's evidence | 0.912 found | 0.923 to 0.926 | 0.876 found | 0.970 to 0.973 | 0.956 or more | | |

With the dispersions from the primes the constrained count ends 5% beyond the end that was found at 89
moduli (16,730 against 15,907), 3% beyond the extended counts at 138 and 2% at 238. The difference between
the two inputs shrinks with the size (5%, 3%, 3%, 2%, 1%, 1%, 0.5%). My reading, not tested: the entropy
bound credits a modulus that has `n` classes with a best class `√(2 ln n)` standard deviations above the
mean, and the mean best of `n` is 1.0, 1.03, 1.27, 1.54 for `n` = 2, 4, 6, 10; setting the dispersion to
zero at 3, 5, 7 removes a gain of about that size.

## (b) The family of constraints

The decomposition by prefixes is exact in any order of the moduli. The model is not the same in any
order (`orders_*.txt`; dispersions recomputed exactly for each order):

| order of the moduli, 1,228 moduli and 300,000 | loss as it was | lowest prefix entropy | loss with the constraint | moduli with weight above 1 |
|---|---|---|---|---|
| increasing | 3,348.8 | -260.8 at 317 | 3,425.6 | 75 |
| decreasing | 1,605.8 | 9.2 at 9973 | 1,605.8 | 0 |
| 3..17 first, then decreasing | 3,451.8 | -69.3 at 17 | 3,488.0 | 6 |
| upper half increasing, then lower half increasing | 3,398.3 | 8.4 at 4547 | 3,398.3 | 0 |
| lower half decreasing, then upper half increasing | 1,933.8 | 8.4 at 4523 | 1,933.8 | 0 |
| random 1 | 2,914.6 | 8.1 at 3343 | 2,914.6 | 0 |
| random 2 | 3,298.2 | 8.5 at 4789 | 3,298.2 | 0 |

(measured: at most 3,437.7.) At 429 moduli and 100,000 the same seven orders give 1,512, 753, 1,555,
1,541, 954, 1,343, 1,544 as it was, against 1,541.7 measured.

* The count of the recursion depends on the order by up to a factor two in the exponent. The orders
  that fail are those that leave moduli with few classes for the end, where they must take nearly
  everything in one class: the closure `k(t) = (e^{v t} − 1)/v` has the tail of a Poisson variable, and a
  modulus with 2 to 16 classes does not. In increasing order the large tilts fall on the large moduli,
  whose classes hold a few rows each, and there the tail is right. So the increasing order is the one in
  which the model can be trusted, and that is a property of the closure.
* Among orders that keep the smallest moduli first the loss as it was still moves by 3% (3,349 to
  3,452), which is more than the constraint moves it in increasing order (77, or 2.3%). The model does
  not resolve effects of the size under discussion.
* Hence: the prefixes in increasing order are a necessary family for the model in the only order in which
  it is accurate. Whether they are sufficient cannot be decided by this model, since any other chain of
  subsets needs the model in another order. For comparison: in Derrida's generalised random energy model,
  where the increments at the nodes of the tree are independent, the prefix sums in the order of the tree
  are exactly the constraints. Here the class counts at different nodes of a level are not independent
  (the same class of the same modulus, on overlapping sets of alive rows), which is the situation of the
  non-hierarchical version of Bolthausen and Kistler (2006), where the free energy is that of a suitably
  chosen hierarchy (the least over the chains, as I recall it): every chain gives a bound.
* The data, as far as they go, point one way. With both sets of dispersions measured over constrained
  rises from the middle of the range to the end, and with the dispersions from the primes the constrained
  count is 2 to 4% under the measured loss near the end at 89, 138, 167, 238 and 302 moduli, and ends 2 to
  5% beyond the evidence. If constraints are missing, they are of the kind the write-up expects: more of
  them, moving the truth further from 1.1275.

## (c) The dual

With multipliers `λ_j ≥ 0` on the prefix sums the Lagrangian weights the level `s` by
`w_s = 1 + Σ_{j ≥ s} λ_j`, which is at least 1 and does not increase with `s`. The value function stays
linear in the alive rows, `V = C − p A`, and one step gives `p_s = p_{s⁺} − max_t (1/(s−1)) [p_{s⁺} e^{v t} −
w_s (t e^{v t} − k(t))]`, whose maximum is at `t = p_{s⁺}/w_s` (the derivative is
`v e^{v t} (p_{s⁺} − w_s t)`) and equals `(w_s/(s−1)) k(p_{s⁺}/w_s)`: the write-up's formula. The dual
value `Σ w_s ln(s−1) − p_start · rows` is an upper bound for the constrained maximum for every `λ`, it is
convex in `λ`, and its derivative in `λ_j` is the prefix entropy at the maximising tilts because that
maximiser is unique. At a minimum over `λ ≥ 0` the prefix entropies are therefore `≥ 0` and vanish where
`λ_j > 0`, the tilts are feasible for the primal, and their primal value equals the dual value: no gap.

Checked: the last column of `table.txt` gives, at every point, the lowest prefix entropy at the dual's
tilts (never below `−3·10^-4`), the largest prefix entropy in absolute value where the multiplier is
positive (at most `3·10^-4`) and primal minus dual (at most `2·10^-4`, on values of hundreds to
thousands). `primal_463.txt`: SLSQP on the tilts with the 89 prefix constraints, from two starting points,
gives 18.2844 at 15,907 and 37.6897 at 15,300, the dual minima to `10^-9`.

## (d) The limit

**What holds.** For a fixed `a < 1` the tilts that the recursion as it was gives to the moduli up to `Q^a`
cost a multiple of `Q/ln² Q` nats, and those moduli have `Q^a`. Inside the model the moduli up to `x/B`
then gain little over random classes; by my estimate (levels spending their own entropy, Gaussian range)
the rows they leave fall by a relative `2 √(2 ln ln x/(B ln x))`, which is 0.3 at `ln x = 100` for `B = 4`
and 0.1 at `ln x = 1000`. So inside the model the statement is right in the limit and the limit is far
away. The count for the top moduli (a class with `K` rows costs `K ln(K/μ)`) is the usual first-moment
bound.

**What does not hold.** "Frozen" means that the entropy of a prefix is used up, so that one setting of
those moduli is taken: the best one. Which setting is best is an extremal question about the primes, and
the model answers it with the tail of its own distribution around random classes. There are settings
outside that distribution. Take a block of moduli, the odd primes `t` in `(z, w]`, and one integer
`N₁ ≥ Q`, and give every modulus of the block the class `a_t = N₁ mod t`. Then the block strikes `q`
exactly when `N₁ − q` has a prime factor in `(z, w]`. For `w² > N₁` the rows left are those with `N₁ − q`
free of prime factors above `z` (few: the smooth numbers, `ρ(u) N₁` with `u = ln N₁/ln z`) and those with
`N₁ − q = m p`, `p > w` prime, `m ≤ N₁/w`. Classes of different moduli above `√N₁` are then disjoint on the
rows, where random classes overlap. Counted exactly (`block_60000000.txt`, 3,562,114 rows, `N₁ = 2^26`):

| block `(z, w]` | moduli | rows left, common integer | rows left, random classes (expected) | ratio | leading order `ρ(u) + ln(ln N₁/ln w)` |
|---|---|---|---|---|---|
| (406, 937,500] | 73,927 | 32.3% | 44.0% | 0.735 | 31.9% |
| (90, 937,500] | 73,982 | 27.9% | 33.5% | 0.832 | 27.5% |
| (1,351, 234,375] | 20,563 | 51.0% | 58.5% | 0.872 | 50.7% |
| (8,192, 58,593] | 4,901 | 80.3% | 82.1% | 0.978 | 80.3% |

At the sizes of the cover problem the block must end below `x` while `Q/x` is of order `ln² x`, and the
rows with `N₁ − q = m p`, `p > w`, are then many: a fraction `ln(ln Q/ln w)`, about `2 ln ln x/ln x`. At
`x = 9,973` and `Q = 852,000` (`block_852000.txt`) the block `(256, 2,493]` leaves 0.991 of what random
classes leave and the block `(256, 9,973]` 0.905. In the limit the fraction goes to zero while random
classes leave `ln z/ln w` (`block_limit.txt`; `w = x/4`, `Q = x ln² x`, the best `z`):

| `ln x` | 9.21 | 13.8 | 20.7 | 34.5 | 50 | 69 | 100 | 230 | 1000 |
|---|---|---|---|---|---|---|---|---|---|
| rows left by the block, common integer over random | 0.98 | 0.91 | 0.81 | 0.66 | 0.55 | 0.46 | 0.37 | 0.22 | 0.07 |

So the moduli below the top are not held to what random classes do, and the factor is unbounded:
`O(ln ln x/ln x)` of the rows against `ln z/ln x · const`, by the upper-bound sieve for the pairs
`p`, `N₁ − m p` (Brun, Selberg; uniform in `m`), with `N₁` a power of two so that the singular series
average to a constant.

**Consequences.**

* The bound `D(n) ≤ (e^γ/(2 C₂) + o(1)) r ln² r/ln ln r` is not derived. Put the block `(z, x/4]` and
  the small moduli (random or greedy, a factor `0.7413/ln z`) before the top moduli, and count the top
  moduli as the write-up does (those in `(x/4, x]`, each striking `ln x/ln ln x` rows: `0.75 x/ln ln x`
  rows in all). The largest `Q` for which the rows left by the moduli below the top fit that count, at
  leading order (`block_capacity.txt`):

  | `ln x` | 9.21 | 13.8 | 20.7 | 34.5 | 50 | 100 | 230 | 350 | 1000 | 10000 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | random classes below the top, `Q/(x ln² x)` | 0.55 | 0.46 | 0.39 | 0.32 | 0.28 | 0.23 | 0.19 | 0.18 | 0.15 | 0.11 |
  | the block on a common integer, `Q/(x ln² x)` | 0.57 | 0.53 | 0.51 | 0.52 | 0.55 | 0.65 | 0.90 | 1.10 | 1.96 | 8.86 |

  The first row is the write-up's bound with the top taken as `(x/4, x]` (it falls like `1/ln ln x`). The second never falls below a half
  and grows like `ln x · ln₃ x/(3 (ln₂ x)³)` (`ln_k` the `k`-fold logarithm): the count forbids nothing
  below about `x ln³ x · ln₃ x/(3 (ln₂ x)³)`. This is not a claim that complete covers exist there, which
  would need the second moment; it is the write-up's own count applied to a prefix it had excluded. If
  the count for the top moduli is believed, `D(n)/(r ln² r)` does not tend to zero, and has no finite
  limit.
* A rigorous lower bound, in outline. Block `(z, x/4]` with `a_t = N₁ mod t`, `N₁` the power of two in
  `[Q, 2Q)`, `ln z = ln x · ln₃ x/(3 ln₂ x)`. Rows left: at most `Ψ(N₁, z) ≤ Q/ln^{3−o(1)} x` with
  `N₁ − q` smooth, and at most `Σ_{m ≤ 8Q/x} C g(m) (N₁/m)/ln²(x/4) = O(Q ln₂ x/ln² x)` of the form
  `N₁ − q = m p`. The moduli up to `z`, each taking its fullest class of what is left, leave a factor
  `∏ (1 − 1/(t − 1)) = O(1/ln z)`, that is `O(Q (ln₂ x)²/(ln³ x · ln₃ x))` rows. The moduli in `(x/4, x]`
  take one row each; there are `(3/4 + o(1)) x/ln x` of them. So

      D(n) ≥ c · r ln² r · ln₃ r/(ln₂ r)²      for large n and some c > 0,

  which is Rankin's bound for gaps with one more logarithm, because only primes have to be struck. It
  exceeds `A r ln r` for every `A` (the theorem in `GoldbachGaps/CoverBound.lean` has `A < 1.349`), and
  through the classes `N ≡ a_t` it says that infinitely many even `N` have no Goldbach summand below
  `c · ln N (ln₂ N)² ln₄ N/(ln₃ N)²`. I have not written it out line by line; the consultant session, which
  holds the asymptotic part, should check it before it is cited. It is far from formalisable here (it
  needs the upper-bound sieve for a pair of linear forms and the count of smooth numbers).
* At the sizes that can be computed nothing changes. The block beats random classes by 2% at `x = 10^4`
  and by a factor two only near `x = 10^25`, and the tilted classes of the constrained count do better
  than either there (they reach `1.0 x ln² x` at `x = 9,973`, where random classes below the top and the
  fullest classes at the top would reach about `0.6`). The law with `c ≈ 1` describes the range that can be computed.
  What changes is every statement about the limit: `1.1275` was withdrawn for one reason; the
  replacement `1.349/ln ln r` falls for another.

## Files

* `prefix_check.py`: the dispersions (exact, any order), the two passes, the dual by L-BFGS-B with the
  certificate, the primal by SLSQP, the ends. Needs numpy and scipy.
  `table.txt`, `orders_*.txt`, `levels_*.txt`, `primal_463.txt`, `ends.txt`: its output.
* `against_writeup.py`: the same code fed with the write-up's dispersions, the two sets of dispersions
  side by side, and which moduli carry the difference. It imports the research session's
  `cover_price.py` and `cover_price_hl.py` from a directory given on the command line; they are not
  copied here. `with_writeup_dispersions.txt`, `dispersions.txt`, `sensitivity.txt`: its output.
* `block_check.py`: rows left by a block with a common integer against random classes, exact at one `Q`,
  the leading-order ratio by size, and what the count for the top moduli allows after each kind of
  prefix. `block_60000000.txt`, `block_852000.txt`, `block_limit.txt`, `block_capacity.txt`.

      python3 prefix_check.py table > table.txt
      python3 prefix_check.py orders 9973 300000 > orders_9973_300000.txt
      python3 prefix_check.py levels 9973 300000 > levels_9973_300000.txt
      python3 prefix_check.py primal 463 15907 > primal_463.txt
      python3 prefix_check.py ends 463 797 997 1499 1999 2999 9973 > ends.txt
      python3 against_writeup.py DIR table > with_writeup_dispersions.txt       (DIR: the research session's files)
      python3 against_writeup.py DIR dispersions > dispersions.txt
      python3 against_writeup.py DIR sensitivity > sensitivity.txt
      python3 block_check.py 60000000 > block_60000000.txt
      python3 block_check.py 852000 2493 9973 > block_852000.txt
      python3 block_check.py limit > block_limit.txt
      python3 block_check.py capacity > block_capacity.txt
