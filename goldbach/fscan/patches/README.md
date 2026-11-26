# fscan_wide.patch: fscan past Q = 12,288 and past 256 rows (the 50% line at 29 to 31 digits)

Against the fscan.c of the research branch (ccr-d4a17dd0, 25 Nov), `cd` to the repository root and `patch -p1 < goldbach/fscan/patches/fscan_wide.patch`.

- `NW` 24 -> 32 (`-DNW=` overrides): the alive bitset over the odd primes below Q holds 2,048 of them, Q up to 17,863
  (29 digits: 12,930; 32 digits: 16,456).  The refusal `Q > 64 NW 8` is gone; the existing check on the number of odd
  primes below Q (`too many rows`) is the limit.  Only the vector enumeration touches NW.
- `-DMAXROWS=512` (AVX-512 only): row masks of 8 words instead of 4, for the classes that leave more than 256 rows
  (at 30 digits, Q = 14,138, the fewest is 258).  The exact stage ORs 64-byte rows; member masks, the drain, `mtot`, the
  row-mask table and the `ha` histogram follow `MW = MAXROWS / 64`.  The default stays 256: the same code as before.

Checks (25 Nov, Sapphire Rapids, all four cores busy with other work):

- The default build (NW 32, 256 rows) and `-DMAXROWS=512` against the unpatched fscan at 28 digits (Q = 12,141, L = 383,
  the two vectors of 222 rows, 10^27 < N <= 1.02 10^27, theta 125, Ta 135, hist=1): 3.06 10^9 members, the output
  identical apart from the timing fields (STATS, HS and HA histograms).
- `check_wide.py ./fscan512` (30 digits, Q = 14,138, the 258-row vector N0 = 6579123466680728): fscan's histogram of the
  rows left by the exact stage over 23,887 sampled members, and its selected / kept / tests / prps over 1,528,729 members
  (171 / 171 / 1,068 / 171), agree with a replay in Python that shares nothing with fscan (score, exact rows, Fermat).
- Speed at 28 digits (15.3 10^9 members, min of 3 interleaved runs): unpatched 10.30 s, NW 32 10.85 s (within the
  +-10% noise of the busy machine; the enumeration alone, about 1.2 s, takes 0.2 s more), `MAXROWS=512` 11.79 s
  (about 14% slower: use it only for classes above 256 rows).  The Fermat arithmetic still holds below 2^100, i.e. to
  31 digits at c <= 1.2.
