# limit_check: scripts and outputs behind LIMIT_CHECK.md

All scripts need numpy; `topode*.py`, `calib.py`, `extrap.py` also need scipy. Each builds its own prime table to 2·10^7, so Q = 0.7·x·ln²x must stay below that (x up to about 1.2·10^5).

| script | what it does | output |
|---|---|---|
| greedy_real.py inc\|dec x… | greedy cover depth on real primes, moduli in increasing or decreasing order | out_greedy_real_*.txt |
| bulkgain.py | alive rows after greedy bulk (moduli ≤ x/ln x) against a random bulk | out_bulkgain.txt |
| allones.py | alive rows after the structured bulk with all classes 1 | out_allones.txt |
| topcheck.py 20000 0.70 | top phase on real primes against the Poisson-max model | out_topcheck_x20000.txt |
| topode.py, topode3.py x… | deterministic dynamic greedy in the Poisson model over the top moduli; capacity C(x) | out_top_capacity.txt |
| calib.py | real critical alive count against the model's, x = 2,000 to 10^5 | out_calib.txt |
| extrap.py | capacity converted to D/(x ln² x), calibrated and bare | out_extrap.txt |
| model_greedy.py | Poisson model at all moduli (shows what the bulk gets wrong) | out_model_greedy.txt |

Written 25 Nov 2026 by the consultant session for LIMIT_CHECK.md. Heuristic tools, not proofs.
