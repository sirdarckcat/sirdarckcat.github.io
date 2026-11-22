# cover: how good can a residue cover be?

For the game "largest g(N) with N below 10^200" the search exponent is
E = p1·k, where k is the number of primes q < Q that the modulus leaves
uncovered (q ≢ a_r mod r for every modulus r) and p1 = boost/ln N is the
chance that such a row N − q is prime. With the moduli fixed, p1 is fixed,
so everything is in k. `ptcover.c` attacks k from two sides: it looks for
the best cover, and it estimates how many covers of each quality exist,
which says where the search has to stop.

| file | what it is |
|---|---|
| `ptcover.c` | parallel tempering over the residues; prints the best cover, ⟨k⟩ per temperature and the entropy |
| `make_specs.py` | turns covers into search specs (the JSON format of `phd/campaign3`), rechecking each from scratch |
| `c3_moduli.txt` | the 88 moduli and residues of campaign 3 (k = 867), `c3_moduli_only.txt` the moduli alone |
| `cover_q122k_k856.json` | the best cover found here for Q = 122,000 on those moduli |
| `check_specs.py` | independent recheck of a spec file from N0 and M alone |
| `selection_check.py` | rows left per member by sieve depth and the hit mass of the emptiest members, on real members |
| `deliver/` | spec files for eight targets, and the runs that produced them |
| `meanfield.py`, `greedy_vs_model.py` | a closed-form prediction of the optimum and why it misses the level |
| `closeness_cost.py` | the search exponent of a target closeness at each size of N |
| `pt_*.txt` | the other runs behind the tables below |

## Method

A replica holds one nonzero class per modulus and makes single-modulus
moves with the Metropolis rule at inverse temperature β, energy k.
Neighbouring replicas are exchanged. A move costs two class lists (about
300 rows on average), so 56 replicas do about 10^7 moves a second on 4
cores.

The replicas sample e^{−βk}, so the run also gives the entropy
S(k) = ln #{covers with about k uncovered rows}: S(β = 0) = Σ ln(r − 1) is
the number of all covers, and dS = β·d⟨k⟩ along the temperature ladder.
Where S reaches zero there are no covers left: that is an estimate of the
smallest k that exists, obtained without finding it.

## Check on a case with a known answer

13 moduli (3 to 43), Q = 10,007: the exhaustive enumeration of `enumv.c`
says the minimum is 186 and exactly 6 covers reach it. `ptcover` finds 186,
and its entropy there is 2.15 against the true ln 6 = 1.79; at ⟨k⟩ = 186.6
it gives 3.66 against ln 34 = 3.53 for the covers up to 187.

## Result for the 200-digit game (the 88 moduli of campaign 3)

Random classes leave 1,377 ± 20 rows (measured at β = 0). The cover of
campaign 3, found by greedy choice plus annealing, has k = 867.

| Q | rows | best k found | E = p1·k (200 digits) | spec file in `deliver/` |
|---|---|---|---|---|
| 122,000 | 11,474 | **851** | 20.34 | `specs_q122000_64.json` |
| 130,000 | 12,158 | 921 | 22.02 | `specs_q130000_128.json` |
| 135,000 | 12,575 | 968 | 23.14 | `specs_q135000_128.json` |
| 140,000 | 13,009 | 1,011 | 24.17 | `specs_q140000_128.json` |
| 145,000 | 13,421 | 1,050 | 25.10 | `specs_q145000_128.json` |
| 150,000 | 13,847 | 1,092 | 26.10 | `specs_q150000_128_k1092.json` (and `specs_q150000_128.json` at 1,093) |
| 155,000 | 14,271 | 1,138 | 27.20 | `specs_q155000_128.json` |
| 160,000 | 14,682 | 1,185 | 28.33 | `specs_q160000_128.json` |

(60,000 sweeps on one core, about 15 minutes each, from random starts;
`deliver/run_*.txt`. A first run of 30,000 sweeps on 4 cores gave 856 at
Q = 122,000 in 3.6 minutes, with the entropy reaching zero at ⟨k⟩ = 860:
the coldest replicas are not fully equilibrated, which is why covers a few
rows below that point exist. An independent sampler of another session
reached 850 at Q = 122,000 and 1,007 at 140,000. Four more seeds of 150,000
sweeps at Q = 150,000 ended at 1,092, 1,092, 1,093 and 1,097
(`deliver/more150/`): the bottom is rugged at the level of a few rows, and a
single run is within about five rows of it.)

The spec files hold 64 or 128 residue vectors each, all within one or two
rows of the best found, in the JSON format of `phd/campaign3`, with
kmax = 5.4·10^9 so that N stays below 10^200. `check_specs.py` rechecks
them from N0 and M alone: a row q counts as covered exactly when
gcd(N0 − q, M) > 1.

Other modulus sets at Q = 122,000 (20,000 sweeps): the first 86 odd primes
give 870, the first 88 give 856, the first 90 give 842
(`pt_first*.txt`). Two more moduli buy 14 rows, about 0.25 nats of E after
the larger boost, for 5.3 digits of modulus: 0.02 nats of E per nat of
modulus. The campaign's set (84 primes to 439 plus 467, 487, 491, 683) is
equivalent to the first 88.

Three conclusions.

1. **The plateau is the optimum.** The entropy vanishes within a few rows
   of the best cover found, at 0.62 of the random mean. No cover much
   below 850 exists on these moduli; against the 867 of campaign 3 that is
   0.4 nats, not the several nats that a "perfect rounding" of the
   fractional cover would give. This is a heuristic certificate (it rests
   on the sampler being in equilibrium down to β ≈ 4, which the 13-modulus
   check supports), not a proof.
2. **Covers are not scarce.** For Q = 122,000 the entropy is 27 nats at
   ⟨k⟩ = 866 and 45 nats at 871: there are about e^27 residue vectors
   within 10 rows (0.24 nats) of the best. A search is therefore limited by
   compute, not by the range of one progression, and `PT_DUMP` delivers as
   many independent vectors as wanted.
3. **Raising the target costs 8.7 rows, 0.21 nats, per 1,000 in g** with
   optimal covers, steady from 122,000 to 160,000.

## Vectors in bulk (`covergen.c`, `gen_vectors.sh`)

With the CPU sieve in front of the GPUs a vector's whole progression is used
up in about two minutes, so the search needs thousands of vectors a day.
They exist: near the best cover, the covers with at most a given number of
uncovered rows form large sets connected by single-class changes, and
`covergen` walks in such a set (a move is accepted exactly when it stays at
or below the cap) and prints every cover it visits once.

| target Q | cap on uncovered rows | distinct covers reached | time (4 cores) |
|---|---|---|---|
| 150,000 | 1,092 (the best known) | about 1,000 | used up |
| 150,000 | 1,093 | more than 120,000 | 20,000 in 5 s; 120,000 in 6 min |
| 150,000 | 1,094 | not exhausted | 20,000 in 3 s |
| 140,000 | 1,007 (the best known) | 50 | used up |
| 140,000 | 1,008 | about 4,800 | 45 s |

One row more multiplies the supply by 30 to 100 and costs 2.4% of the
success probability per member, so a search that needs 1,700 vectors a day
can stay within one or two rows of the best cover for months.

```
./gen_vectors.sh 150000 1093 5000 b1 101     # -> specs_q150000_b1.json, 5,000 new vectors, best first
./gen_vectors.sh 140000 1008 2000 b1 201     # at 140,000 use cap 1009 once 1008 runs dry
```

The script builds `covergen`, walks from the covers in `starts/q<Q>.txt`,
turns the best `count` new covers into specs with `make_specs.py` and
rechecks the file with `check_specs.py` (5,000 vectors: 4 minutes, nearly all
of it the recheck). `starts/ledger_q<Q>.txt` remembers every vector handed
out (a hash of N0) so that batches never repeat one; the two ledgers start
with the files delivered so far for these targets, including the other
sampler's. Use a new seed for every batch. If the walk stops early ("no new
cover for 30 s") the cap is used up: raise it by one. For another target,
`python3 specs_to_covers.py specs.json > starts/q<Q>.txt` makes starting
points from any spec file, and `python3 make_specs.py --ledger
starts/ledger_q<Q>.txt specs.json` enters its vectors in the ledger. The
starting points at 140,000 are the 1,007- and 1,008-row covers of the other
session's sampler (`phd/cap200`), which are better than this sampler's
1,011.

## Which members to test

A member N0 + tM succeeds with probability (1 − p)^a, where a is the number
of its residual rows that the sieve leaves and p the chance that such a row
is prime, so the emptiest members carry far more than their share of the
hits. `selection_check.py` measures this on real members (131,072 members
of the first Q = 130,000 vector, every row sieved by all non-modulus primes
up to the depth; `selection_check_q130k.txt`):

| sieve depth | rows left, mean ± sd | p | hit mass in the emptiest 0.1% / 1% / 8% | binomial model |
|---|---|---|---|---|
| 2^17 | 483.0 ± 14.7 | 0.0456 | 0.8% / 5.0% / 23.7% | 0.9 / 5.3 / 24.3 |
| 2^20 | 410.6 ± 14.7 | 0.0537 | 1.1% / 6.4% / 27.5% | 1.2 / 6.8 / 28.3 |
| 2^23 | 357.1 ± 14.5 | 0.0617 | 1.4% / 8.0% / 31.4% | 1.6 / 8.3 / 32.2 |
| 2^26 | 315.9 ± 14.2 | 0.0698 | 1.9% / 9.4% / 34.8% | 2.0 / 10.0 / 35.8 |
| 2^28 | 293.3 ± 14.0 | 0.0752 | 2.2% / 10.5% / 37.1% | 2.4 / 11.1 / 38.2 |

The rows left are slightly less spread than a binomial (the model is 5 to
10% optimistic in the tail), the mean is exact, and the mean success
probability is the same at every depth (2.0·10^-10), as it must be. The
model column is Φ(Φ⁻¹(f) + δ·sd) with δ = −ln(1 − p); it is what the
campaign table (tested fraction against test rate) is computed from.

## What a given closeness costs at each size of N

Closeness is g divided by the largest g expected below N (`closeness.py`).
`closeness_cost.py` takes a size and a target fraction of that ceiling, finds
the best cover with `ptcover`, and prints the search exponent
(`closeness_cost.txt`):

| digits | target | Q | rows | moduli | random | best cover | E (nats) | candidates per success |
|---|---|---|---|---|---|---|---|---|
| 23 | 50% | 8,094 | 1,017 | 13 (to 43) | 191 | 148 | 19.7 | 1.4e+09 |
| 23 | 75% | 12,141 | 1,451 | 13 (to 43) | 273 | 222 | 29.6 | 5.0e+13 |
| 23 | 90% | 14,569 | 1,707 | 13 (to 43) | 321 | 268 | 35.7 | 3.5e+16 |
| 30 | 50% | 15,147 | 1,768 | 17 (to 61) | 309 | 238 | 26.2 | 9.9e+11 |
| 30 | 75% | 22,720 | 2,537 | 17 (to 61) | 442 | 363 | 39.9 | 2.0e+18 |
| 40 | 50% | 29,498 | 3,202 | 22 (to 83) | 521 | 413 | 36.5 | 3.5e+16 |
| 50 | 50% | 49,125 | 5,049 | 26 (to 103) | 788 | 630 | 46.4 | 7.7e+20 |
| 60 | 50% | 74,273 | 7,325 | 31 (to 131) | 1,095 | 891 | 57.1 | 3.8e+25 |
| 100 | 50% | 232,674 | 20,649 | 48 (to 227) | 2,796 | 2,354 | 99.8 | 1.7e+44 |
| 200 | 10% | 213,070 | 19,050 | 88 (to 461) | 2,283 | 1,626 | 38.9 | 1.3e+17 |
| 200 | 50% | 1,065,352 | 83,213 | 88 (to 461) | 9,972 | 8,740 | 209.2 | 8.4e+91 |

Reading. The exponent for a fixed fraction grows in proportion to the number
of digits: 50% needs about 0.4·ln N nats, that is about N^0.4 candidates
(1.4·10^9 at 23 digits, 3.5·10^16 at 40, 10^44 at 100, 10^92 at 200). The
cover also gets relatively worse as the target grows on the same moduli
(best/random is 0.62 at Q = 122,000, 0.71 at 213,000 and 0.88 at 1,065,000
on the 88 moduli): with many more rows than classes the classes are too
even to choose between. So a fleet that affords about 28 nats reaches 7 to
7.5% of the ceiling at 200 digits, about 45% at 40 digits and about 85% at
21 to 23 digits; the share is set by the size of N, not by the method. At
200 digits, 10% is already 10^17 candidates and 50% is out of the question.

## What does not give the optimum: a formula, or a proof

*A formula.* `meanfield.py` treats the alive rows before each modulus r as an
independent thinning of the classes mod r and lets the cover take the
fullest class that exists (N·D(x‖α) = d·ln(r − 1), with the sub-Poisson
factor d = min(1, ln m/ln Q) for small moduli). It gets the trends right:
14 rows for two more moduli (measured 14), and a slope in Q within 15% of
the measured one. It gets the level wrong: 682 predicted at Q = 122,000
against 851, and the ratio predicted/optimum is 0.79 to 0.84 in every case
tried. `greedy_vs_model.py` shows why: prime by prime, the class the greedy
choice actually finds is one or two rows smaller than the largest class of
a Poisson sample of the same mean (6 against 7 at r = 439, 26 against 28 at
r = 97, 1,436 against 1,455 at r = 5), and plain greedy ends at 912. So the
sampler, not a formula, is the tool for k_opt.

*A proof.* A rigorous floor needs an upper bound on the number of covers
with few uncovered rows. The routes tried all end vacuous for 88 moduli:
exact enumeration of the classes of the primes up to 13 followed by "every
later prime covers at most its fullest class" leaves a capacity of about
3,500 rows for 2,957 alive ones; tree-structured inclusion–exclusion
(Hunter–Worsley) over the moduli over-counts every row covered by primes
that are not adjacent in the tree; bounded-difference and Bernstein
inequalities for the lower tail of k are dominated by the small primes. The
entropy estimate above therefore stays a measurement.

## The brainstorm of 22 November 2026 (`brainstorm/`)

Two hundred ideas for a large step at 200 digits, 100 from this session and
100 from the Lean session, each tested by the other. None is worth one nat as
a change of method; `brainstorm/README.md` has the reason, the price list from
150,000 to 213,070 (10% of the ceiling: 1,100 card-years at the present
engine), the checks of the model on 356 successes at low thresholds, and the
engineering that is still open (0.6 to 1.3 nats).

## Use

```
gcc -O3 -march=native -fopenmp -o ptcover ptcover.c -lm
./ptcover 122000 c3_moduli_only.txt 30000 7 betas56.txt > run.txt       # best cover + entropy table
PT_DUMP=covers.txt PT_KDUMP=862 ./ptcover 122000 c3_moduli_only.txt 30000 8 betas56.txt > run2.txt
python3 make_specs.py 122000 pt_q122k 540000000 covers.txt specs.json 200   # 200 best, campaign3 format
./ptcover 10007 m13.txt 40000 3 betas13.txt                              # the check above
```

`make_specs.py` recomputes the residual of every cover and builds the even
N0 below M = 2·∏r by the Chinese remainder theorem; for the base spec of
campaign 3 it reproduces N0, M, boost and E.
