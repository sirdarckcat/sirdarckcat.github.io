# Archipelagos: clusters of large Goldbach gaps, and a test of the model

g(N) is the least prime p with N − p prime. This study computes g(N) exactly for 20 million consecutive even N
near 10^12, 10^15 and 10^18 and compares the truth with the model behind every cost forecast of the 200-digit
search: a row N − q with a prime factor up to the sieve depth z is composite, and every other row is prime with
one fixed probability c_z, independently (hypothesis H1).

Charts: the Goldbach Archipelagos page, goldbach-archipelagos.html. On the Goldbach Gaps Map
(`../gaps_map/`, ../gaps_map/viz/goldbach_map.html) the results are the eight boxes tagged
'exhaustive test'.

A number is **big** when g(N) is in the top 1% of its window (g ≥ 368, 480, 614 at the three scales) and **huge** in
the top 0.01% (g ≥ 882, 1,202, 1,490). Each big number is an island; a cluster of linked islands is an archipelago.

## Results

| Question | Answer (near 10^18 unless stated) | Output |
|---|---|---|
| Do big gaps cluster? | Yes: 91% of big numbers sit in an archipelago of two or more (86% near 10^12, 89% near 10^15). The largest has 176 members and sits on the window's largest prime gap (558). Archipelagos of 20 or more: 1,710, against 66 in a control shuffled within classes mod 30030. | `archipelagos_e*.txt` |
| Why? | N + d reuses the composite N − q whenever q and q + d are both prime (Lean: `Needles.lean`). The lag 30 shares 67 of 111 rows and makes N + 30 about 18 times likelier to be big. | `theory_e*.txt` |
| Does the model explain the clustering? | At all 366 even lags up to 732, within about 1% at the strong lags and within block-bootstrap error bars everywhere. | `theory_e*.txt`, `lagse.txt` |
| Does the model get P(every row composite) right? | Within about 1% over five orders of magnitude once the sieve passes the threshold (totals 0.993 to 1.005 of the prediction). Shallow sieves (z = 13, 97) overstate it by 2–9%. | `theory_e*.txt` |
| The extreme tail? | Each window's record is where the model puts it: g ≥ 3,137 expected 1.2 times near 10^18, seen once. | `tail_e*.json` |
| Can machine learning beat the survivor count? | No. LightGBM with 133 features of the same residues loses to (1 − c)^rows with nothing fitted: −0.00012 ± 0.00003 nats per number near 10^18, and the same in two more runs. | `ml_e*.txt` |
| What is left to learn? | A sieve to 65,521 removes 27% of the uncertainty; the rest is whether the survivors are prime. | `budget_e*.json` |
| Who are the big numbers? | Almost never divisible by 3 (0.9%), and biased toward quadratic non-residue classes (57.4% ≡ 2 against 41.7% ≡ 1 mod 3), because of Chebyshev's bias among the primes below the threshold. | `archipelagos_e*.txt` |

## Files

| File | What it does |
|---|---|
| `gdata.py` | builds a window: g(N), primality and smallest prime factor (≤ 65,521) of every number; writes `data/<name>_*.npy` |
| `lib.py` | loading and row-counting helpers |
| `theory.py` | calibration of P(big \| survivors) and the lag enrichment R(d) against the model |
| `archipelagos.py` | clusters, the class-shuffled control, extremal index, primes below N, residue profile |
| `ml.py` | LightGBM against the count (`python3 ml.py e18 997`) |
| `budget.py`, `tail.py`, `lagse.py` | information budget, extreme tail, bootstrap error bars by lag class |
| `viz_data.py`, `amap.py`, `build_page.py`, `page_template.html` | chart data and the page `goldbach-archipelagos.html` |
| `explore/` | the first quick checks near 10^10 and 10^15 (`cluster_check.py`, `gradient_check.py`, `group_search.py`) |

The `.npy` arrays (about 600 MB) are not committed; `data/*.json` records how each window was built.

## Rebuild

```
pip install numpy scipy scikit-learn lightgbm
for s in 1e12 1e15 1e18; do python3 gdata.py $s 2e7 e${s#1e}; done    # 5 to 20 s each
for n in e12 e15 e18; do python3 theory.py $n > theory_$n.txt; python3 archipelagos.py $n > archipelagos_$n.txt; python3 tail.py $n; done
python3 ml.py e18 997; python3 ml.py e18 97; python3 ml.py e15 997      # one at a time: each needs several GB
python3 budget.py e18; python3 budget.py e15; python3 lagse.py e18; python3 lagse.py e15
python3 viz_data.py; python3 amap.py; python3 build_page.py
```

The windows were checked against deterministic Miller–Rabin on 1,200 values of g(N) and 12,000 numbers, with no mismatch.
