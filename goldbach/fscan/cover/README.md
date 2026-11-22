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
| `pt_*.txt` | the runs behind the tables below |

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

| Q | rows | best k found | k where S = 0 | E = p1·k |
|---|---|---|---|---|
| 122,000 | 11,474 | **856** | 860 | 20.56 |
| 130,000 | 12,159 | 925 | 935 | 22.22 |
| 140,000 | 13,010 | 1,014 | 1,021 | 24.36 |
| 150,000 | 13,848 | 1,103 | 1,109 | 26.49 |
| 160,000 | 14,683 | 1,190 | 1,195 | 28.58 |

(Q = 122,000: 30,000 sweeps, 3.6 minutes on 4 cores, from random starts;
the others 20,000 sweeps. The coldest replicas are not fully equilibrated,
which is why covers a few rows below the point S = 0 exist.)

Three conclusions.

1. **The plateau is the optimum.** The entropy vanishes within a few rows
   of the best cover found, at 0.62 of the random mean. No cover much
   below 856 exists on these moduli; what is left for cover optimization
   is about 0.3 nats, not the several nats that a "perfect rounding" of the
   fractional cover would give. This is a heuristic certificate (it rests
   on the sampler being in equilibrium down to β ≈ 4, which the 13-modulus
   check supports), not a proof.
2. **Covers are not scarce.** For Q = 122,000 the entropy is 27 nats at
   ⟨k⟩ = 866 and 45 nats at 871: there are about e^27 residue vectors
   within 10 rows (0.24 nats) of the best. A search is therefore limited by
   compute, not by the range of one progression, and `PT_DUMP` delivers as
   many independent vectors as wanted.
3. **Raising the target costs 8.8 rows, 0.21 nats, per 1,000 in g** with
   optimal covers, steady from 122,000 to 160,000.

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
