# fm13 at 665 bits (the lead's question of 25 Nov 10:04Z on uarch 018b7ed)

uarch's 018b7ed says `fm13` (13 limbs of 52 bits, documented "up to 664 bits") is wrong above 664 bits and makes
`search_c.py` use `fmw` there. Every 200-digit number below 10^200 has at most 665 bits (10^200 = 2^664.39), and the CPU
shares (Q = 150,000 g8ffe1 vectors at k >= 2^32, M of 191 digits) searched only 665-bit members: N0 + kM passes 2^664 at
k ~ 4,162,978,815 < 2^32.

`test665b.py` runs the `fm13` build that `search_c.py` loads on this IFMA CPU against Python `pow` / gmpy2
(`test665b_out.txt`):

- 665 bits, n in [2^664, 10^200): 0 wrong residues and 0 wrong verdicts in 30,133 numbers. They include random odd numbers,
  the top 1%, 10^200 - j, 2^664 + j, 1,800 primes, 30 base-2 pseudoprimes, and the rows of the record's N.
- `fm13.Members.first_pass`, the call `search_c.py` makes, on a CPU-share spec at k = 4.16e9-5.39e9 against a plain gmpy2
  loop: 2,800 members, 705 with a pass, 0 wrong.
- The real limit: no errors through 672 bits. The first wrong verdicts come at 673 bits (4 of 460), and from 674 bits most
  numbers fail. Every failure is a false composite, never a false pass, so an overflow could not have lost a hit (a hit
  needs every row composite). It could only make a false candidate, which gmpy2 verification rejects.

The GPU path does not use `fm13`. Kernel 28 with the 29-bit step (23 x 29 bits, R = 2^669, n < 2^665) range-checks every
spec at setup and every round (flag 2). The top-of-range known cases (25 = 25, 46 = 46, 40 = 40) compare against
`cpu_brute_k0.py`, which uses gmpy2's BPSW.
