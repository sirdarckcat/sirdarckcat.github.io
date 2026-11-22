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
| 150,000 | 13,847 | 1,093 | 26.13 | `specs_q150000_128.json` |
| 155,000 | 14,271 | 1,138 | 27.20 | `specs_q155000_128.json` |
| 160,000 | 14,682 | 1,185 | 28.33 | `specs_q160000_128.json` |

(60,000 sweeps on one core, about 15 minutes each, from random starts;
`deliver/run_*.txt`. A first run of 30,000 sweeps on 4 cores gave 856 at
Q = 122,000 in 3.6 minutes, with the entropy reaching zero at ⟨k⟩ = 860:
the coldest replicas are not fully equilibrated, which is why covers a few
rows below that point exist. An independent sampler of another session
reached 850.)

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
