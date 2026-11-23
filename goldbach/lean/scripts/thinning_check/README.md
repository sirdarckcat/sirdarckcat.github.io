# Thinning between sieve depths: a check of the "prize table"

The research session's Result 3 (`goldbach/sublinear/README.md` on branch
`ccr-d4a17dd0-7uu03r`) counts, for a depth `z`, the even `N < 10^200` by the number `k_z(N)`
of rows `q < Q = 213,070` with `N - q` free of prime factors `≤ z`, and notes an empirical
regularity: the rows left for the ideal `N` fall like `1/ln² z`, "as if every prime struck
twice". These scripts test one explanation on that session's own tables
(`goldbach/sublinear/ideal_tilt_213070.txt`, commit `b3d6688`; pass its path as the argument).

## The law tested

If the primes in `(z, z']` killed the rows left at depth `z` independently, each row with
probability `1 - θ`, `θ = ∏_{z < s ≤ z'} (1 - 1/s) ≈ ln z / ln z'`, then

    E[y^k_z'] = E[(1 - θ (1 - y))^k_z]                         for every y,

that is `Z_z'(β') = Z_z(β)` with `1 - e^{-β} = θ (1 - e^{-β'})`. In the variables
`S(τ, k) = ln #{N : k rows left at depth z}`, `τ = ln ln z`, this is the Hamilton–Jacobi
equation `∂S/∂τ = k (e^{∂S/∂k} - 1)`, with `(1 - e^{-β}) / ln z`, `k e^β ln z` and `S - β k`
constant along characteristics (`β = ∂S/∂k`). Along the cutoff `S = p_z k` of the ideal search
it gives

    -d ln k_cut / d ln ln z = (e^β - 1 - p) / (β - p).

For the moduli above `Q` the law is an upper bound, proved in
`GoldbachGaps/Cap/Thinning.lean` (`thinSum_le_of_lt`, `thinCount_le_of_lt`,
`thinCount_le_chernoff`). Below `Q` it is not a theorem.

## What the tables say

* `thin.py` → `thin_213070.txt`: `ln Z` and `<k>` of every deeper table against the prediction
  from every shallower one. The means at `β = 0` thin exactly. At lower temperature the deeper
  table always has more rows than predicted (independent thinning overstates the kills): by
  0.6% at `β' = 0.95` and 3.9% at `β' = 4.7` from 20,000 to 50,000; by 1.5% and 12% from 5,000
  to 20,000; by 5% and a factor 9 from 463 to 1,000.
* `envelope.py` → `envelope_213070.txt`:
  1. The cutoff of the ideal search sits at `β_c = 1.32, 1.24, 1.22, 1.25, 1.29` for depths
     1,000 to 50,000 (`e^β_c` = 3.4 to 3.7; at 463 it is 2.76, near the bottom of the
     landscape). The exponent predicted there is 2.10, 2.00, 1.98, 2.02, 2.08; measured between
     consecutive depths: 1.75, 1.79, 1.88, 2.00. So the `1/ln² z` is the value of
     `(e^β - 1 - p)/(β - p)` at `β ≈ 1.25`; in the ideal population a new prime strikes about
     `e^β ≈ 3.5` times its usual share, not twice, and the envelope falls more slowly than
     that because the population is drawn again at every depth.
  2. Cutoffs predicted from a shallower table (canonical estimate, same estimate on the deeper
     table in brackets): 20,000 → 50,000: 567.3 (570.7); 5,000 → 50,000: 561.0 (570.7);
     463 → 50,000: 538.5 (570.7). In cost: 0.14, 0.41 and 1.35 nats too low. The ideal `N` of
     depth 50,000 are, at depth 463, at `β ≈ 0.53` (about 1,950 rows): ordinary good residue
     vectors, not the best covers.
  3. `mean - variance` of the row count at `β = 0` should be multiplied by `θ²`; it is larger
     by 2% to 7% at each step (the count is slightly less dispersed than binomial thinning
     makes it).
* `greedy_dispersion.py` → `greedy_dispersion.txt`: on the 89 covering primes the rows left
  spread over the classes of the next prime more evenly than at random (variance/mean 0.04 at
  3, 0.52 at 101, 0.79 at 463), and a greedy cover leaves 1,680 rows on the real rows against
  1,450 with Poisson class counts. That is why the law fails from shallow tables, and why a
  model with random class counts overstates what covers can do.

The research session's own continuation to `B = 10^8` ("rows beyond z independent") moves the
same way as the base depth grows: `e^11.22, 11.38, 11.50, 11.62, 11.72, 11.76` tested `N` for
`z = 463, …, 50,000`.

    python3 -I thin.py     path/to/ideal_tilt_213070.txt > thin_213070.txt
    python3 -I envelope.py path/to/ideal_tilt_213070.txt > envelope_213070.txt
    python3 -I greedy_dispersion.py > greedy_dispersion.txt
