# Measured: the sub-100-digit wall, and why weak conditioning cannot break it

Target of the study: can an even **N < 10^100** with least Goldbach
summand **g(N) > 100 000** be constructed by anyone, with any amount of
compute reachable today?

The classic construction pins `N mod r` to ONE residue per prime modulus
r, spending `ln r` nats of the size budget `ln B = D·ln 10` (the CRT
modulus must stay under the bound or no representative exists below it).
The proposed generalisation is **set-valued conditioning**: constrain
`N mod r` to a SET `A_r` of k residues, spending only `ln(r/k)` nats.
`k = 1` is the classic cover, `k = r` is free and buys nothing.

The motivating estimate is a Gaussian extreme-value argument. Coverage
counts per residue class are ~Poisson(P_r); spending h_r nats on modulus
r yields ~σ_r·√(2 h_r) extra covered targets, so the Lagrangian optimum
allocates h_r ∝ P_r and predicts a total gain

    sqrt( 2 · H · sum_r P_r )

for a budget of H nats spread thinly over many moduli — orders of
magnitude, if attainable.

## The model (exact, not mean-field)

Because `N mod r` are independent by CRT, survival is a plain product:

    s_q = prod_r P(r does not divide N - q)
    P   = 1 - [q mod r in A_r] / k_r    (conditioned r)
        = 1 - 1/r                       (unconditioned r)
    E   = e^gamma · ln(RC) / ln(N) · sum_q s_q

Conditioning modulus r to its top-k classes changes `sum(s)` by
`(r·C_k/k − sum(s))/(r−1)` where `C_k` is the sum of the top-k class
weights — the discrete form of the extreme-value gain. With every
`k = 1` this reproduces the repo's validated `E = |U|·boost/ln N`
**to 0.3%**, and the classic prediction at 150 digits (E = 25.55)
matches the cover that actually produced the 150-digit record
(E = 24.91, predicted and measured) to 0.6 nats.

Search feasibility needs `H + E <= ln B`: H nats of conditioning leave
`exp(ln B − H)` admissible N below the bound, each winning the desert
lottery with probability `e^-E`.

`entropy_frontier.py` traces the frontier by a Lagrangian sweep;
`frontier_table.py` bisects the feasibility boundary.

## Result 1 — set-valued conditioning buys 1–2.8 nats, not orders of magnitude

| D | classic E | set-valued E | gain | candidates |
|---|---|---|---|---|
| 100 | 43.84 | 41.83 | 2.0 nats | 10^18.2 |
| 120 | 34.25 | 32.67 | 1.6 | 10^14.2 |
| 130 | 31.62 | 29.23 | 2.4 | 10^12.7 |
| 140 | 29.36 | 26.53 | 2.8 | 10^11.5 |
| 150 | 25.55 | 24.47 | 1.1 | 10^10.6 |

The optimizer never selects a modulus above 1123 even when offered every
prime below 15 000 — the frontier is converged, not pool-limited.

## Result 2 — the sqrt law is an unattainable upper bound

Predicted gain at 100 digits is ~3 400 covered primes. Measured, the
reduction saturates: the achieved exponent is **~H^0.35, not H^0.5**.
Two causes:

- **Overlap.** `sum P_r ≈ 25 000` against only `pi(Q) = 9 591` targets,
  so most nominal gain re-covers already-covered primes. The extreme-value
  argument adds independent contributions; the product structure eats them.
- **Poisson discreteness.** At large r the classes hold 0 or 1 targets,
  so there is no "excess over the mean" left to collect.

## Result 3 — and those nats are not real, because of enumerability

The set-valued optima condition ~200 moduli whose product is ~10^450.
Representatives below 10^100 exist, but *finding which residue
combination lands there* is a constrained-CRT problem (lattice / Wagner
k-list), not a scan — and both blow up at these dimensions. Free
enumeration requires the conditioned modulus `M1 <= B`, so that every
residue combination yields `~B/M1` representatives by simple progression
scanning. The candidate pool is then

    pool = (B / M1) · prod_r k_r = exp(rho + Lambda)
    rho    = ln B − ln M1     (k-room, the classic lever)
    Lambda = sum_r ln k_r     (residue multiplicity, the F4 zero-penalty freedom)

and a search succeeds when `rho + Lambda >= E`. `realizable_frontier.py`
optimizes under that constraint:

| D | realizable E | candidates | structure |
|---|---|---|---|
| 100 | 43.66 | 10^19.0 | M = 78d, pure k-room; multiplicity buys nothing |
| 140 | 27.50 | 10^11.9 | M = 131d, k-room e^20 + multiplicity e^12.4 |

Multiplicity is nearly free (12.4 nats of candidates for 0.15 nats of E
at 140 digits) but **redundant**: k-room already costs only ~0.05 nats of
E per nat of candidates, so the net gain is ~0.2 nats.

The structural conclusion: **the classic cover is optimal not by luck but
by construction** — it is the unique design whose admissible set is an
arithmetic progression, i.e. free to enumerate. Every relaxation that
buys coverage destroys enumerability, and every relaxation that preserves
enumerability buys almost nothing.

## Verdict

**Sub-100 digits at g > 100 000 costs 9.1·10^18 candidates** — about
193 000 GPU-years at an optimistic 1.5M candidates/s, or 19 years on a
10 000-GPU cluster. It is out of reach for any group, by roughly seven
orders of magnitude beyond plausible compute. Nothing in the
conditioning design space changes that; the exponent is a counting fact
about covers and prime density, not an artifact of one algorithm.

The same measurement gives the **reachable band** for a two-session
Colab GPU fleet (measured 7.9·10^5 candidates/s end to end):

| D | candidates | fleet wall-clock |
|---|---|---|
| 150 | 10^11.1 | ~2 days (matches the banked record campaign) |
| 140 | 10^11.9 | ~13 days |
| 135 | 10^12.5 | ~47 days |
| 130 | 10^13.0 | ~5 months |

So ~137–140 digits is the deepest rung reachable on a week-to-fortnight
campaign with the existing GPU engine.

## Reproduction

```
python3 entropy_frontier.py 100                 # set-valued sweep
python3 entropy_frontier.py 100 --classic       # k=1 baseline
python3 frontier_table.py --digits 100,120,150  # boundary bisection
python3 realizable_frontier.py --digits 100,140 # enumerability-constrained
```

## Independent verification of the WP3 decoding barrier (2026-07-28)

The parallel PhD track (`phd/wp3_small_representative_memo.md`) reaches
the same verdict from the coding-theory side: oversized covers (mass
A > ln B) would make sub-100 easy, but placing their CRT representative
below the bound is a modular subset-sum with per-position choices at
density ~1.026 — the regime where neither lattice reduction nor Wagner
k-trees work. Its v1 claimed a polynomial-time CRT-decoding escape and
retracted it, having compared the decoding radius and the existence
bound at *different* agreement sizes.

`verify_barrier.py` re-derives both at the SAME cover mass A, using a
Legendre transform for the design entropy rather than binomial counting:

| pool R | L | pool mass | A_max (exists) | A_J (decodes) | ratio |
|---|---|---|---|---|---|
| 1 000 | 1 | 956 | 339 | 469 | 0.723 |
| 60 000 | 1 | 59 816 | 570 | 3 711 | 0.154 |
| 60 000 | 16 | 59 816 | 1 305 | 14 845 | 0.088 |
| 10^6 | 16 | 998 483 | 1 697 | 60 651 | 0.028 |

The window is closed at every pool size; the best case is 28% short and
the gap widens with pool size and with L, since A_J grows like
sqrt(L·P) while the existence bound grows only logarithmically. The
computed radius at R = 60 000, L = 16 (14 845 nats) reproduces WP3's
figure exactly, so both analyses are evaluating the same quantity.

Two independent routes — enumerability of the admissible set (this file)
and decodability of an oversized cover (WP3) — therefore close on the
same conclusion, from opposite directions.
