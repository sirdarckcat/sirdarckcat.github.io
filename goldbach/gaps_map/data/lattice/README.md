# Lattice-decoding check (helper session)

Companion to `../../LATTICE_CHECK.md`. Python 3, numpy, scipy.

| step | script | log |
|---|---|---|
| Research's table recomputed from the real alive rows (exact residue counts); variants: true list sizes (GSS), soft decision with row-count weights and optimised per-prime scales, subsets of rows, products of shifted copies, pin-first, cost | `lat_check.py [ln K]` | `logs/lat_check.log` |
| simulation of a whole window (2e7 members, 460 primes): mean, sd and maximum of the hard and soft agreement against the predictions | `lat_sim.py seed K z` | `logs/lat_sim1.log` |
| per-prime exponents of the modulus optimised by marginal efficiency | `lat_exp.py` | `logs/lat_exp.log` |
| the isolated-N loss and the break-even budget, from a binomial survivors model | `iso_check.py` | `logs/iso_check.log` |

`cls_sa_11.npy` holds the 89 classes of the annealed cover (1,524 rows alive; made by `../rows/sa.py`); `lat_check.py` and `lat_sim.py` rebuild the alive rows from it. Caveats: the cover is mine, not the campaign's (1,502 rows); the lattice cost is dimension^4 times entry size, a lower bound; the soft-decision threshold is the Cauchy-Schwarz optimum of the Johnson-type inequality, not a re-derivation of the Guruswami-Sahai-Sudan theorem.
