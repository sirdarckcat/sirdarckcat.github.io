# The capped game (largest g(N) for N < 10^200): cover statistics and an optimiser

Scripts and data behind the numbers quoted for the 200-digit game on 2026-11-22. The exact
statements they rely on are proved in `goldbach/lean/GoldbachGaps/Cap/`.

All scripts take a cover spec in the schema of `goldbach/phd/campaign3/base_spec.json`.

| file | what it does |
|---|---|
| `tempering.py SPEC SWEEPS SEED [Q] [extra moduli] [drop]` | Gibbs sampling with replica exchange over all nonzero residue vectors on the moduli of SPEC, weight `exp(-lam * rows left)`. Writes the best vector found and the mean rows left at each `lam` (`tempering_Q*_m*_seed*.json`). It is both an optimiser for covers and a measurement of how many vectors exist at each number of rows left. |
| `dos.py BOOST MDIGITS file.json ...` | Thermodynamic integration of those means: `S = ln(number of vectors)` as a function of rows left. |
| `mkspec.py tempering.json NAME OUT [digits]` | Re-counts the rows a vector leaves with independent code, builds `N0` by CRT and writes a spec in the campaign schema. Fed the campaign cover it reproduces `base_spec.json` field for field. |
| `capstudy.py SPEC` | First-moment law, Monte Carlo over random vectors, value of each modulus of the cover and of further moduli. |
| `pairs.py SPEC` | Second-order (pair) term of the Hardy–Littlewood model for the rows left. |

## Results for `Q = 122000` on the 88 moduli of campaign 3

- `spec_q122000_k850.json`: a cover leaving **850** rows (campaign 3: 867), same modulus.
  `E` at 199 digits is 20.42 instead of 20.83.
- Random nonzero vectors leave 1376.9 rows on average (exact; standard deviation 20.2), which
  is 33.08 nats. The campaign cover is 25 standard deviations below that average.
- Number of vectors by rows left (`dos_Q122000_m88_seed*.json`): `e^436` in all; about `e^131`
  with at most 912 rows, `e^72` with at most 879, `e^43` with at most 867, `e^24` with at most
  860, and the count reaches 1 near 850. The cold end of the sampler is not fully mixed, so
  the last figures are uncertain by several rows; no vector below 850 was seen in two runs.
- Value of moduli: the 20 largest of the cover are worth 3.1 nats of `E` for 120.6 nats of
  modulus; the next prime outside the cover is worth 0.12 nats for 6.1.
- Pair term for the 867 rows of the campaign cover: -0.013 nats.
