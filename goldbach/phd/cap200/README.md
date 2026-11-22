# The capped game (largest g(N) for N < 10^200): cover statistics and an optimiser

Scripts and data behind the numbers quoted for the 200-digit game on 2026-11-22. The exact
statements they rely on are proved in `goldbach/lean/GoldbachGaps/Cap/`.

All scripts take a cover spec in the schema of `goldbach/phd/campaign3/base_spec.json`.

| file | what it does |
|---|---|
| `tempering.py SPEC SWEEPS SEED [Q] [extra moduli] [drop]` | Gibbs sampling with replica exchange over all nonzero residue vectors on the moduli of SPEC, weight `exp(-lam * rows left)`. Writes the best vector found and the mean rows left at each `lam` (`tempering_Q*_m*_seed*.json`). It is both an optimiser for covers and a measurement of how many vectors exist at each number of rows left. |
| `dos.py BOOST MDIGITS file.json ...` | Thermodynamic integration of those means: `S = ln(number of vectors)` as a function of rows left. |
| `mkspec.py tempering.json NAME OUT [digits]` | Re-counts the rows a vector leaves with independent code, builds `N0` by CRT and writes a spec in the campaign schema. Fed the campaign cover it reproduces `base_spec.json` field for field. |
| `neighbours.py tempering.json WIN OUT` | All vectors differing from a cover in one class (and pairs of those) that leave at most `best + WIN` rows, in the pool format. |
| `mkspecs.py OUT PREFIX COUNT CEILING pool.json ...` | The `COUNT` lowest distinct vectors of one or more pools as a list of specs in the schema of `campaign3/specs_variants.json`, each re-counted with independent code. `kmax` is capped below `2^32` because the GPU kernel holds `k` in 32 bits. |
| `capstudy.py SPEC` | First-moment law, Monte Carlo over random vectors, value of each modulus of the cover and of further moduli. |
| `pairs.py SPEC` | Second-order (pair) term of the Hardy–Littlewood model for the rows left. |

## Results for `Q = 122000` on the 88 moduli of campaign 3

- `spec_q122000_k850.json`: a cover leaving **850** rows (campaign 3: 867), same modulus.
  `E` at 199 digits is 20.42 instead of 20.83.
- `specs_q122000_top64.json`: 64 distinct vectors on the same modulus, 2 leaving 850 rows and
  62 leaving 851 (`E` at 199 digits 20.42 to 20.45). Around the 850 cover there are 109
  vectors with 851 rows, 1,687 with 852 and 13,721 with 853 within two class changes.
- Random nonzero vectors leave 1376.9 rows on average (exact; standard deviation 20.2), which
  is 33.08 nats. The campaign cover is 25 standard deviations below that average.
- Number of vectors by rows left (`dos_Q122000_m88_seed*.json`): `e^436` in all; about `e^131`
  with at most 912 rows, `e^72` with at most 879, `e^43` with at most 867, `e^24` with at most
  860, and the count reaches 1 near 850. The cold end of the sampler is not fully mixed, so
  the last figures are uncertain by several rows; no vector below 850 was seen in two runs.
- Value of moduli: the 20 largest of the cover are worth 3.1 nats of `E` for 120.6 nats of
  modulus; the next prime outside the cover is worth 0.12 nats for 6.1.
- Pair term for the 867 rows of the campaign cover: -0.013 nats.

## Other targets, same 88 moduli (runs of 4,000 sweeps)

`E` is `-k ln(1 - p)` with `p = 0.02390` (cap `10^200`); `ln(members per vector)` is 22.42
below `10^200`, 22.18 with `k < 2^32`.

| Q | best rows left | `E` | file with 128 vectors |
|---|---|---|---|
| 122,000 | 850 | 20.57 | `specs_q122000_top64.json` (64 vectors: 850, 851) |
| 130,000 | 923 | 22.33 | `specs_q130000_top128.json` (923, 924) |
| 135,000 | 967 | 23.40 | `specs_q135000_top128.json` (967, 968) |
| 140,000 | 1,007 | 24.36 | `specs_q140000_top128.json` (1007, 1008; second run, the first gave 1011) |
| 145,000 | 1,051 | 25.43 | `specs_q145000_top128.json` (1051, 1052) |
| 150,000 | 1,098 | 26.57 | `specs_q150000_top128.json` (1098, 1099) |

So `E` grows by about 0.21 nats per 1,000 in `Q` with re-optimised covers. The research
session's sampler (`goldbach/fscan/cover/` on `ccr-d4a17dd0-7uu03r`) reports 851, 921, 1,011,
1,050 and 1,093 for 122,000, 130,000, 140,000, 145,000 and 150,000: the two agree to a few rows. Beyond the `Q` a cover
was built for, a further prime is left with probability 0.12 (the random-class rate) and
costs `p` each, which is 0.245 nats per 1,000: surviving past the design value by luck is
nearly as cheap as designing for it.

With the three primes 443, 449, 457 added to the moduli the best at `Q = 122,000` is 831 rows
(`E` = 20.24), but a vector then has only about 60 members: no gain in practice.
