# The bottom-up round (helper session)

Companion to `../../BOTTOM_UP.md`. Python 3 with numpy and scipy; `gmp_cal.py` needs `libgmp.so.10` (called through ctypes, no headers). Everything runs in minutes on four cores except `a3_pairs.py` (about 3 minutes and 1 GB) and `rec_mc.py` (about 5 minutes).

| what | script | log |
|---|---|---|
| calibration of a Fermat test and of big multiplications with GMP (units for Bernstein's batch smooth part) | `gmp_cal.py` | `logs/gmp_cal.log` |
| cost per member of the alternatives to the window sieve (per-N root lookups, batch smooth part, z mod F(N)); lone-N loss against the sieve cost. Part (b) of this script passed the Opus rho as a cost in tests (wrong by the factor 13.9); parts (a) and (c) are in tests and stand | `q1_cost.py` | `logs/q1_cost.log` |
| the stake of a cheaper sieve with the Opus units (reproduces `two_stage/b_answer.md` table to 0.01 nat) | `q1_stake.py` | `logs/q1_stake.log` |
| supply of covers: single-move cost spectra from the best cover, additive generating function; check of additivity on random sets of moves | `dos_gf.py`, `dos_check.py` (read `../lattice/cls_sa_11.npy`) | `logs/dos_gf.log`, `logs/dos_check.log` |
| rate of the cover: mean and sd of the alive rows over random covers, Gaussian random-energy optimum (Q = 200,000 and 170,000) | `cover_rem.py`, `cover_rem170.py` | `logs/cover_rem.log`, `logs/cover_rem170.log` |
| dual and geometry numbers: rough positions of the window, expected overlap, exchange rate of a pin at a prime above 463 | `a12_numbers.py` | `logs/a12_numbers.log` |
| additive structure of the good members of a simulated window of 2*10^7 (`python3 a3_pairs.py seed fraction cover.npy`) | `a3_pairs.py` | `logs/a3_pairs_1pct.log`, `logs/a3_pairs_01pct.log` |
| the published records of the least Goldbach summand (OEIS A025018/A025019 b-files, Oliveira e Silva): `n N p` for 1 to 67, N only for 68 and 69 | `records.txt` | |
| calibration of the success model on the records: weighted CDF of each holder's alive-row count and Lambda(N, F(N)+) on a grid | `rec_mc.py` | `logs/rec_mc.log` |
| time-rescaling test (W ~ Exp(1), U ~ uniform), with the truncation prime R as chosen, larger (`1e3`) and smaller (`1e-3`) | `rec_rescale.py`, `rec_rescale_R.py seeds k_min R_multiplier` | `logs/rec_rescale.log`, `logs/rec_rescale_Rup.log`, `logs/rec_rescale_Rdown.log` |

Caveats. The cover is mine (1,524 rows), not the campaign's 1,502; the independent-move count of covers is an upper bound (other basins add covers) and Research's thermodynamic integration is the reference for the cover floor. The record calibration uses the sieve model with independent alive rows and a prime chance pi = 2 prod r/(r - 1)/ln N; it is a Monte Carlo over uniform classes, not a proof; the last two records (68, 69) have no listed least prime and are not used. An earlier Gaussian version of the record test was removed (its cumulants are invalid at these N). `a3_pairs.py` writes the window to `/tmp/F_window.npy` (80 MB, not kept).
