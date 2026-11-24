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
| 155,000 | 14,271 | 1,137 | 27.18 | `specs_q155000_128.json` (1,138 to 1,140); `starts/q155000.txt` |
| 160,000 | 14,682 | 1,181 | 28.23 | `specs_q160000_128.json` (1,185); `starts/q160000.txt` |
| 165,000 | 15,092 | 1,221 | 29.19 | `starts/q165000.txt` (two runs of 150,000 sweeps: 1,221 and 1,222) |
| 167,500 | 15,301 | 1,243 | 29.71 | `starts/q167500.txt` (one run of 120,000 sweeps) |
| 170,000 | 15,496 | 1,262 | 30.17 | `starts/q170000.txt` (seven runs: 1,262 four times, 1,263 three times) |
| 172,500 | 15,708 | 1,284 | 30.69 | `starts/q172500.txt` (one run) |
| 175,000 | 15,915 | 1,302 | 31.12 | `starts/q175000.txt` (one run) |
| 177,500 | 16,123 | 1,323 | 31.63 | `starts/q177500.txt` (one run) |
| 213,070 | 19,050 | 1,623 | 38.80 | `starts/q213070.txt` (four runs of 150,000 sweeps, all 1,623; the 10% threshold) |

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
| 150,000 | 1,092 (the best known) | 2,282 | used up |
| 150,000 | 1,093 | more than 120,000 | 20,000 in 5 s; 120,000 in 6 min |
| 150,000 | 1,094 | not exhausted | 20,000 in 3 s |
| 140,000 | 1,007 (the best known) | 65 | used up |
| 140,000 | 1,008 | about 4,800 | 45 s |
| 155,000 | 1,137 (the best known) | 7 | used up |
| 155,000 | 1,138 | about 900 | 30 s |
| 160,000 | 1,181 (the best known) | 1,072 | used up |
| 160,000 | 1,182 | more than 6,000 | 10 s |
| 165,000 | 1,221 (the best known) | 22 | used up |
| 165,000 | 1,222 | about 1,150 | 30 s |
| 170,000 | 1,262 (the best known) | 36 | used up |
| 170,000 | 1,263 | about 9,800 | 60 s |
| 170,000 | 1,264 | more than 50,000 | 60 s |

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
1,011; at 160,000 they are that sampler's 294 covers with 1,181 rows together
with 778 found here. `specs_to_covers.py` and the `--ledger` form also read
that session's pool files.

**One more modulus.** With vectors free, the progression of one vector does
not have to be long, and the modulus set can grow until a vector holds just
over half a sieve window. On the first 89 odd primes (3 to 463; M has 192.7
digits, 2.14·10^7 members a vector) the optimiser reaches 1,248 rows at
Q = 170,000 and 1,609 at 213,070, against 1,262 and 1,623 on the campaign's
88 moduli; after the larger boost that is E = 30.30 against 30.53 and 39.06
against 39.27, i.e. 1.27 and 1.23 times the success rate. `./gen_vectors.sh
Q cap count name seed m89` uses `starts/q<Q>_m89.txt` and sets kmax per
vector. Starting files exist for 170,000 (1,248 rows: four of six tempering
runs end there, a capped walk finds nothing lower, and three independent
routes, the runs, the walk and the best first-88 covers extended by a class
of 463, all land on the same 186 covers), 175,000 (1,291; campaign set 1,302), 180,000 (1,334; campaign
set 1,352) and 213,070 (1,609). The fleet's record of 23 November, 158,209,
came from this set at 170,000. With 8.5 fleet-days left and that record in
hand, `brainstorm/portfolio_budget.py 8.5 29e6 158209 0 m89` gives an expected
final record of 172,700 at design 170,000, 173,000 at 175,000 and 171,200 at
180,000: 170,000 to 175,000 are equivalent, and the design need not move
before the record does. (The 29 million members a second in that command was
the planning figure of the morning. The fleet's measured expected design hits
of the evening, checked against its tally of expected and found successes at
earlier design levels (about 9 expected, 9 found), correspond to 52 million in
the model's units; with that rate the expected final record is about 175,000
to 176,000, and what matters most is the family of the cover: see "Rows above
the design level" below.)

**Which 89th prime.** The 89th modulus need not be 463. Extending each
first-88 cover (below) by the best class of a candidate prime r screens all
r from 463 to 700 in seconds: 491 gives 1,245 rows, 557 gives 1,246, and 479,
503, 523 and 613 give 1,247, against 1,248 for 463. For the first 88 primes
with 491 a capped walk finds nothing below 1,245, and the levels fill two rows
lower than with 463: 1,800 distinct covers at ≤ 1,247 rows, 26,000 at ≤ 1,248
and 82,000 at ≤ 1,249 in 40 seconds, where the 463 family has 5,700 at
≤ 1,249, 69,000 at ≤ 1,250 and 144,000 at ≤ 1,251 in a minute. With the boost
11.043 that is E = 29.86 at the best cover against 29.93, and about 5 to 7%
more successes per member at the level a large supply is drawn from; a vector
has 2.016·10^7 members instead of 2.138·10^7. `./gen_vectors.sh 170000 1248
count name seed m89r491` uses `starts/q170000_m89r491.txt` (2 covers at
1,245, 93 at 1,246, 1,828 at 1,247, 2,001 at 1,248; see the two families
below).

**The first 88 odd primes** (3 to 461, in place of the campaign's 3 to 439
with 467, 487, 491 and 683). M has 190.00 digits, so a vector has 9.9·10^9
members below 10^200, more than the campaign's 5.4·10^9, and the engine needs
no change. At Q = 170,000 six tempering runs of 150,000 sweeps ended at
1,261, 1,259, 1,259, 1,259 and 1,257 rows and one of 500,000 at 1,255; three
of four further runs reached 1,255 within 400,000 sweeps, always the same two
covers, a capped walk from them finds nothing lower, and 1,255 is what the
89-prime optimum gives when 463 is removed (1,248 + 7). So 1,255 is taken as
the optimum; this set needs longer runs than the other two. With the slightly larger boost (11.021 against
11.008) that is E = 30.03 against 30.17 for the campaign's 1,262, about 14%
more successes per member at the best cover and about 10% at the supply
level; at 213,070 the same set gives 1,619 against 1,623. Supply: 2,150
distinct covers at ≤ 1,257 rows and 36,800 at ≤ 1,258 in 40 seconds.
`./gen_vectors.sh 170000 1258 count name seed m88f` uses
`starts/q170000_m88f.txt` (2 covers at 1,255, 99 at 1,256, 2 at 1,257, 188
at 1,258 since the selection below; about 2,200 exist at ≤ 1,257) and sets kmax per vector (9,898,466,666 for these; cap it at 2^32
if the kernel needs 32-bit k). The fleet's four smaller cards have run this
set since 23 November. With 32-bit k the range [0, 2^32) of such a vector
ends at N ≈ 0.43·10^200, while the vector goes on to 10^200:
`GEN_KMAX=top32 ./gen_vectors.sh ...` (`make_specs.py ... top32 ...`) moves N0
up by a multiple of M so that k = 2^32 − 1 is the last member below 10^200.
ln N is then 0.83 larger on the top levels, the chance that a row holds a
prime falls by 0.18%, and with 30 expected primes a member that is 5.6% more
successes per member for no other change (the spec records the move as
`k_shift`, `check_specs.py` allows for it, and the cover can be handed out
again for its top range even if its low range was used).

**Rows above the design level: two families.** The optimiser counts the
uncovered rows below Q and nothing else. A member that passes all of them
still stops at the first uncovered prime q ≥ Q with N − q prime, so the final
record also depends on how many primes the cover leaves uncovered just above
Q. The planning model (`brainstorm/rank_covers.py`, `soft_weights.py`) prices
a row by what one more uncovered row at q costs in expected final record,
relative to a row below the record in hand. With the fleet's own expected
rates of 23 November (9.3·10^-7 design hits a second on each of the three
large cards, 3.2·10^-6 for the fleet, 2.1 to 2.3 in the 8.2 days left; the
model reproduces this at 52 million effective members a second) and the
record at 158,209:

| row at | ≤ 164,000 | 168,000 | 170,000 | 172,000 | 175,000 | 178,000 | 180,000 | 185,000 |
|---|---|---|---|---|---|---|---|---|
| weight | 1.00 | 0.93 | 0.83 | 0.67 | 0.39 | 0.19 | 0.12 | 0.03 |

A row just above the record weighs the same as a row below it: near-misses
there are expected a dozen times over anyway, and what limits the final
record is the range 168,000 to 180,000. Measured this way, the near-optimal
covers of each set fall into two families that the row count below Q cannot
tell apart:

| set | family | covers | rows < 170,000 | below 158,209 | 170–175k | 175–180k | 180–190k | weighted rows | expected final record |
|---|---|---|---|---|---|---|---|---|---|
| first 89 | A | 396 | 1,248.6 | 1,168.2 | 57.2 | 60.6 | 110.9 | 1,300.4 | 174,850 |
| first 89 | B | 224 | 1,249.0 | 1,174.0 | 46.6 | 49.1 | 105.2 | 1,291.7 | 175,830 |
| first 88 + 491 | A | 76 | 1,248.0 | 1,167.5 | 58.4 | 61.1 | 112.8 | 1,300.9 | 174,810 |
| first 88 + 491 | B | 3,924 | 1,247.5 | 1,173.1 | 46.1 | 50.3 | 104.8 | 1,290.1 | 176,020 |
| first 88 | A | 653 | 1,257.9 | 1,177.6 | 58.4 | 61.0 | 112.9 | 1,310.8 | 174,150 |
| first 88 | B | 291 | 1,257.3 | 1,181.3 | 46.0 | 49.7 | 102.8 | 1,299.3 | 175,280 |

(Family B is what `starts/q170000_<set>.txt` now holds, family A the rest
of `starts/all/`.) Family B has about six more rows below the record and
about thirty fewer between 170,000 and 190,000: 13% fewer near-misses just
above the record, the same number of design hits within 1%, 28% more members
expected to pass 175,000 and 69% more to pass 180,000. In weighted rows it is 9 to 11 better, about a quarter
more of the rate that decides the final record, and worth about +1,000 in
expected final record. A capped walk keeps the family of its starting cover:
an emulation of the fleet's producer (walks of 11,000 covers at cap 1,251, a
third of them, the 1,000 with the fewest rows) gives 1,302.2 weighted rows
and 174,680 from family A starts, 1,293.0 and 175,690 from family B starts,
at the same 1,250.4 rows below Q. The advantage needs time to pay: with less
than about two days of the present fleet left, family A is ahead by 100 to
200, since then the record is decided below Q. As a rule that does not depend
on the fleet's size: family B while the expected number of design hits in the
time that remains is above about 0.5 (B − A is +970 at 2.25 expected hits,
+450 at 1.1, +50 at 0.55, −170 at 0.27), family A below that. Those figures
are for the first 89 primes. On the 491 set, whose family B has half a row
less below 170,000 than its family A, B stays ahead until about 0.35 expected
design hits remain (+270 with two days of the fleet left, +46 with 1.25, −24
with one day), and family A's gain below that is under 25: there the cards
keep family B to the end.

The mechanism was then tested directly where successes are cheap
(`brainstorm/ab_rows_above.py`, `ab_rows_above.txt`): at Q = 60,000, two
covers of one capped walk with 347 rows below Q each and 41 against 55
uncovered primes in the next 4,000, run on the same 62.9 million members with
the fleet's selection rule. They give 1,184 and 1,186 successes, the same
number, as the rows below Q say. Their successes land at a mean g − Q of
3,766 ± 108 against 3,071 ± 103 (the model: 3,912 and 3,057), with 35.4%
against 25.8% of them above Q + 4,000 (model 37.1% and 26.4%) and 12.2%
against 9.8% above Q + 8,000 (13.4% and 8.9%). So at equal rows below Q the
cover with fewer rows above it places its successes 23% further beyond Q,
4.7 standard errors, and the size is what the law "a success survives each
uncovered prime above Q with probability 1 − p" predicts from the two row
lists alone. The fleet's own check on the vectors it had consumed gave 57.2
and 60.5 uncovered primes in 170–175k and 175–180k for family A and 46.1 and
50.4 for family B on the 491 set, as predicted here.

`starts/q170000_m89.txt`, `q170000_m89r491.txt` and `q170000_m88f.txt` now
hold family B only, best expected record first (224, 3,924 and 291 covers);
the complete files are in `starts/all/`. `python3 brainstorm/rank_covers.py
days rate record Q out.txt file ... [--within X]` scores and sorts any cover
files, and `python3 brainstorm/soft_weights.py days rate record Q covers.txt`
writes the row weights. `covergen` takes them: with
`COVERGEN_WEIGHTS=weights.txt` the walk is capped on the weighted rows
(which reach above Q) instead of the rows below Q, so a supply drawn that way
stays good above Q however far it walks; without the variable its output is
unchanged, byte for byte with one walker. `ptcover_w.c` is the tempering on
weighted rows and `ptcover_wfast.c` the same with the fast move evaluation of
`ptcover_fast.c` (the deficit of the few rows that weigh less than a full one
is subtracted from 64 times the plain count): identical tables, BEST and dump
for a given seed, 3 to 4 times faster.

Supply of family B (capture-recapture between two independent walks, an
order of magnitude). On the first 89 primes: about 10,000 covers at ≤ 1,250
rows, 170,000 at ≤ 1,251, 2.7 million at ≤ 1,252, so some 40 million at
≤ 1,253. On the first 88 with 491: 24,000 at ≤ 1,248, 290,000 at ≤ 1,249,
3.7 million at ≤ 1,250, so some 50 million at ≤ 1,251, the same volumes two
rows lower; emulated producer there: 1,290.6 weighted rows and 175,965 at cap
1,248, 1,291.0 and 175,915 at cap 1,249. For the ten million vectors the
large cards use in the rest of the campaign that is about 1,293 weighted rows
on the 491 set, 1,295 on the first 89 and 1,303 on family A. On the weighted
measure 491 is also the best 89th prime of all candidates up to 900 (best
cover 1,287.2 weighted rows; 557: 1,288.2; 523: 1,288.8; 463: 1,289.8). A cap
on weighted rows does not improve the supply within a family: at 3.6 million
covers the weighted cap 1,292.5 and the plain cap 1,250 give the same mean
weighted rows on the 491 set, because within a family the rows above Q
hardly vary. The gain is in the choice of family, and the producers can keep
their plain caps. Nothing better than family B was found on the weighted
measure itself. Local weighted descents from family B and from the covers
designed for 175,000 find nothing. Four weighted tempering runs of 400,000
sweeps from random starts (`ptcover_wfast`, three on the first 89 primes and
one on the 491 set) end at 1,290.64, 1,290.64, 1,291.23 and 1,290.78 weighted
rows, in basins unrelated to family B (74 to 78 of the 89 classes differ, 1,252
to 1,258 rows below 170,000), and that basin carried over to the 491 set
gives 1,290.78 again; family B has 1,289.81 on the first 89 and 1,287.19 on
the 491 set. A cover cannot beat the best sharp design at every threshold at
once, and family B is within 0, 4.6 and 7 rows of the best covers known for
170,000, 175,000 and 180,000, which bounds any gain over it at about 3.6
weighted rows. So family B was a lucky find of the plain search that the
weighted search does not reproduce, and it stands. It also stays within 100 in
expected final record of the best cover known for a record of 172,000,
175,000 or 178,000 (it has 1,341 rows below 180,000 against 1,334 for the
cover designed for 180,000), so a design hit does not call for new covers.
What it calls for is an engine design level above the new record:
`starts/q180000_m89r491.txt` holds the same 491 family-B covers counted to
180,000 (1,340 to 1,344 rows; 2,770 covers), for `./gen_vectors.sh 180000 1344
count name seed m89r491`. A descent at 180,000 from them reaches 1,337 rows,
but with a record of 172,000 or 175,000 in hand those covers score no better
than the ones in the file (175,665 against 175,820; 177,164 against 177,171),
because they pay for the rows above 175,000 with rows below.

**What each design level buys** (`brainstorm/design_menu.py`,
`design_menu.txt`). The same model gives, for the best cover known at each
design level on the first 89 primes, the chances of the final record passing
far thresholds (8.0 days left, the fleet's measured rate, record 158,209; a
design with more rows below its own level is slowed in proportion to half of
the extra rows, the sieve's share of the work):

| designed for | P(≥ 170k) | ≥ 175k | ≥ 180k | ≥ 185k | ≥ 190k | ≥ 200k | ≥ 213,070 | expected final record |
|---|---|---|---|---|---|---|---|---|
| 170,000, family B | 0.89 | 0.52 | 0.19 | 0.068 | 0.017 | 0.0017 | 0.00007 | 175,900 |
| 170,000, family A | 0.89 | 0.43 | 0.12 | 0.037 | 0.010 | 0.0007 | 0.00004 | 174,900 |
| 175,000 | 0.83 | 0.54 | 0.20 | 0.072 | 0.023 | 0.0023 | 0.00009 | 175,600 |
| 180,000 | 0.75 | 0.47 | 0.22 | 0.068 | 0.017 | 0.0016 | 0.00008 | 174,900 |
| 190,000 | 0.63 | 0.36 | 0.15 | 0.077 | 0.032 | 0.0027 | 0.00010 | 173,000 |
| 200,000 | 0.46 | 0.26 | 0.11 | 0.052 | 0.021 | 0.0041 | 0.00016 | 170,400 |
| 213,070 | 0.40 | 0.25 | 0.10 | 0.043 | 0.015 | 0.0029 | 0.00029 | 170,000 |

Family B at 170,000 has the highest expected record and is within a few
points of the best design for every threshold up to 185,000. A design aimed
at a far threshold raises the chance of that threshold by a factor of two to
four and no more (190,000: 3.2% against 1.7%; 200,000: 0.41% against 0.17%;
10%: 0.03% against 0.007%), and pays 3,000 to 6,000 in expected record for
it. Starting files for 190,000 and 200,000 exist (`starts/q190000_m89.txt`,
1,420 rows; `starts/q200000_m89.txt`, 1,502 rows; one tempering run each).

`descend.sh Q start.txt out.txt` looks for a better cover by repeated capped
walks: walk with the cap one or two rows above the best, keep what is at or
below the best, lower the cap when something better turns up. From the long
runs' 1,182 at Q = 160,000 it reached 1,181 in a minute, the value the other
sampler found independently; at 140,000, 150,000 and 155,000 it found nothing
below 1,007, 1,092 and 1,137, and more covers at those levels. Two samplers
and this walk agreeing within a row or two is the evidence that these are the
optima on the 88 moduli.

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
