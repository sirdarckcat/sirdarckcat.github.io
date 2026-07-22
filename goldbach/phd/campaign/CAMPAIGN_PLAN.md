# Campaign plan — Q = 107 720 desert record (WP2 + WP6)

Goal: an even N < 10^199 with g(N) > 107 719 (every prime ≤ 107 719 excluded
as a summand, i.e. cover target Q = 107 720, π(Q) = 10 251 primes incl. 2).
Any hit beats the budget-game incumbent R(10^199) = 107 719; a hit with
N < N₁₉₇ = 6.939105·10^196 also beats the threshold game T(100 000).
Prepared 2026-07-22 on the 4-core campaign box.

## 1. Cover frontier (cover.py, Q = 107 720, rmax = 6000)

| spec | e_target | congr | digits(M) | \|U\| | boost | E (self-cons.) | est digits(N) | k-cap N<10^199 | k-cap N<N₁₉₇ |
|---|---|---|---|---|---|---|---|---|---|
| cover_e170.json | 17.0 | 92 | 202.6 | 746 | 11.02 | 17.00 | 210.0 | — (M > 10^199) | — |
| cover_e175.json | 17.5 | 91 | 198.4 | 750 | 11.07 | 17.50 | 206.0 | 3 | 0 |
| cover_e180.json | 18.0 | 89 | 194.3 | 764 | 10.96 | 18.00 | 202.1 | 5.5·10^4 | 3.8·10^2 |
| cover_e185.json | 18.5 | 88 | 190.6 | 770 | 10.99 | 18.50 | 198.6 | 2.44·10^8 | 1.69·10^6 |

Anneal polish (anneal.py, e_cap 18.5, seeds 1 and 2, 60k–80k iterations,
~13 min each): **no improvement** — both runs return exactly the greedy +
coordinate-descent cover (88 congr, M = 190.6d, |U| = 770, E = 18.50).
The greedy cover is a robust local optimum of F = log M + E; the annealed
copy is committed as `cover_e185_anneal.json` (identical cover, adds N0/M).
An e_cap = 18.0 anneal was not pursued: no rearrangement at E ≤ 18 can fit,
since even the frontier-optimal M at E = 18 (194.3d) leaves only ~5·10^4
usable k below the ceiling, ~0.1 % of the required e^18 ≈ 6.6·10^7 elements.

## 2. Chosen base spec — `base_spec.json`, name `phd_q107720_e185`

88 congruences (moduli 3..643), M = 190.61 digits (191-digit integer),
|U| = 770 residual primes, boost = 10.99, self-consistent E = 18.50.

Rationale: the 199-digit ceiling makes the choice unambiguous. Expected
elements to first hit is e^E, and total wall-clock e^E/throughput falls as
e_target rises, so one wants the largest E whose M leaves enough k-headroom
under the ceiling. e170 does not even fit (M alone has 203 digits); e175
admits 3 values of k; e180 admits 5.5·10^4 k per progression — with 200
variants that is 1.1·10^7 elements against a required e^18 ≈ 6.6·10^7,
i.e. ≲ 15 % hit probability at total exhaustion. e185 is the first frontier
point with real headroom: k up to 2.44·10^8 stays below 10^199, and k up to
1.69·10^6 even stays below N₁₉₇ — so with kmax = 1.5·10^6 **every** hit
beats both games, and the expected hit (k* ≈ 6.7·10^5 per variant across
200 variants) lands at ≈ 196.4 digits ≈ 2.8·10^196 < N₁₉₇. Expected cost
e^18.7/2118 k s⁻¹ ≈ 17 h is the minimum on the frontier subject to the
ceiling, so e185 minimizes expected wall-clock among admissible specs.

## 3. Variants — `specs_variants.json`

`gen_variants.py base_spec.json specs_variants.json 200 1500000 199`:
200 independent CRT progressions (base + 199 residue-swap variants),
kmax = 1 500 000 and ceiling_digits = 199 on every spec.
E range 18.500–18.546; |U| range 770–772 (770: 22 specs, 771: 67, 772: 111).
Total budget 3·10^8 progression elements, all with N < N₁₉₇.

## 4. Calibration (E8) — measured on this box, 2026-07-22

Runs (search.py, sieve_b = 3·10^6, block = 32768, --procs 4; first-2-variant
copies with reduced kmax kept in the session scratchpad, committed variant
file untouched):

| run | k scanned | wall | k/s | tests | prp | p̂ | alive/k | Ê |
|---|---|---|---|---|---|---|---|---|
| variant 0, kmax 30000* | 32 768 | 60 s | 504* | 557 629 | 32 768 | 0.0588 | 318.6 | 18.73 |
| variant 1, kmax 30000* | 32 768 | 59 s | 507* | 553 666 | 32 768 | 0.0592 | 318.6 | 18.86 |
| variant 0, kmax 131072 | 131 072 | 62 s | **2118** | 2 222 787 | 131 072 | 0.0590 | 318.5 | **18.78** |

\* kmax = 30000 is smaller than one 32768 block, so search.py dispatched a
single block to one worker (no parallelism) and normalized alive/k and Ê by
kdone = 30000 instead of the 32768 k actually scanned; the table shows
corrected values (raw printout said 348 alive/k, Ê = 20.45/20.60). Operational
note: give search.py kmax in multiples of `--block` (1.5·10^6 ≈ 45.8 blocks is
fine; the last partial block slightly overstates alive/k and Ê in the log).

Density calibration: measured Ê = 18.73–18.86 (combined 18.79 ± 0.05)
against slice-model E = 18.82–18.88 at the calibration digits (~195), i.e.
**model/measurement ratio 0.995 — the density model E = |U|·boost/ln N is
confirmed to ~0.1 in E**, matching the prior campaign's ±0.2 calibration.
Fermat filter behaviour: ~17.0 tests/k, every scanned k killed by a base-2
PRP complement (0 successes expected and observed at this depth: λ ≈ 0.002).

Throughput: 2118 k/s end-to-end on 4 procs (2213 k/s excluding the 2.8 s
per-spec init; ~570 k/s single-core, 3.8× scaling). The concurrent WP1
verification jobs were visible on the box (load ≈ 1–3 before/during runs),
so these figures are, if anything, slightly pessimistic.

## 5. Expected time-to-hit (Poisson, rate = throughput · e^−E_eff)

Breadth-first over 200 variants; at the expected hit depth the self-consistent
per-element density is E_eff = 18.71 (digits(N) ≈ 196.4), so expected elements
to first hit ≈ e^18.71 = 1.33·10^8.

- Expected wall-clock to first hit: 1.33·10^8 / 2118 k/s ≈ **17.5 h**
- P(hit ≤ 12 h) ≈ **0.50**; P(hit ≤ 24 h) ≈ **0.75**
- Full committed budget (3·10^8 elements, ≈ 39 h): λ ≈ 2.25 → **P(hit) ≈ 0.90**
- Expected hit: k ≈ 6.7·10^5, N ≈ 10^196.4 ≈ 2.8·10^196 < N₁₉₇ → beats both games.

Contingency: if the 3·10^8 budget exhausts without a hit (~10 %), extend with
kstart = 1.5·10^6 and larger kmax — the 10^199 ceiling allows k up to
2.44·10^8, at the cost that hits beyond k ≈ 1.69·10^6 only beat the budget
game. Launch command (lead):

```
cd goldbach && python3 search.py phd/campaign/specs_variants.json \
    --procs 4 --out phd/campaign/found.jsonl
```

(search.py processes specs sequentially, each spec using all 4 procs; every
spec carries kmax = 1.5·10^6 and ceiling_digits = 199. Successes are
BPSW-verified exhaustively over all primes < Q and logged with g(N).)

Note on search order: as-is, search.py exhausts each spec's full k-range
before the next (depth-first). To realize the breadth-first small-N bias from
the research log, run in k-slices instead — e.g. pass 1 with `--kmax 262144`
over all 200 specs after stripping the per-spec kmax, then pass 2 with
kstart = 262144, etc. Time-to-hit statistics are unaffected (density varies
only ~±0.15 in E across the k-range); only the found-N distribution shifts.
