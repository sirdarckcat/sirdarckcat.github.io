# Rows, covers and gaps at 200 digits (helper session)

Companion to `../../ROWS_AND_GAPS.md`. Python 3 with numpy; everything runs in minutes on a laptop.

| step | script | log |
|---|---|---|
| a cover with the campaign's parameters (89 odd moduli 3..463, odd primes below Q = 200,000): greedy, then coordinate descent; writes `rows_alive.npy`, `cls.npy` | `cover.py` | `logs/cover.log` |
| annealing of the 89 classes (`python3 sa.py seed T0 steps T1 start.npy`) | `sa.py` | `logs/sa1.log` `sa2.log` `sa3.log` (6M steps), `sa11.log` `sa12.log` (70M steps, from the best of the first runs) |
| second-order Hardy-Littlewood correction on the alive rows; size of N; exponent by decade | `e23.py` | `logs/e23.log` |
| algebraic family N = a^2 + c: F(c), forced rows alive, price of the unpinned moduli and of the square classes | `e1.py` | `logs/e1.log` |
| selection inside a class vector: cost per success against the sieve cost, and the infinite-budget ceiling | `sel.py` | `logs/sel.log` |
| greedy covering of 1..y by one class per prime up to 463; the FGKMT smallness condition and the tilted-sieve constant at x = 463 | `yx.py` | `logs/yx.log` |

`cover.py` must run first (the others read `rows_alive.npy`; `sa.py` reads `cls.npy`, then `cls_sa_*.npy` it writes itself). Caveats: the cover is mine (1,576 rows after coordinate descent, 1,524 after annealing), not the campaign's 1,502; the survivor model in `sel.py` is binomial with the Mertens probability for each row (about 1 % off the exact product at 463, which moves no gain by more than 0.02 nats); the third-order Hardy-Littlewood term is an estimate, not computed.
