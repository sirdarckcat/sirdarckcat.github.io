# Handover: the 200-digit search on Colab's graphics cards

Written at the stop, 26 November 2026, 08:45 UTC. All work stopped on the user's decision at 08:39:40 UTC, and every Colab
runtime was released by 08:41 UTC.

## What the search was looking for

Goldbach's conjecture says that every even number larger than 2 is the sum of two primes. For an even number N, write
g(N) for the smallest prime p such that N − p is also prime. For almost every number g(N) is small: a typical 200-digit
number has g(N) of about 1,600. The question here was how large g(N) can be for an even N below 10^200 (a 1 followed by
200 zeros). Before this project the best value in this repository was 119,419. The search raised it to 160,357, for a 200-digit
N found on 24 November.

## How it worked, and why it was organised that way

Random numbers are hopeless for this: the chance that a random 200-digit N has g(N) above 150,000 is far too small to
ever see. So N was built in a special way. The search first fixes N's remainder on division by each of 89 small primes:
the odd primes up to 461, plus 491. The remainders are chosen so that for most primes q below a target of 170,000, the
number N − q is divisible by one of the small primes, so it is not prime. Such a set of remainders is called a cover.
About 1,250 primes below 170,000 are left uncovered by each cover.

Every N with a cover's remainders lies on a sequence N0, N0 + M, N0 + 2M, and so on, where M is twice the product of the
89 primes (a 193-digit number). For every member of the sequence, N − q is automatically composite for all the covered
primes q. What remains is luck: N has a large g(N) only if N − q also happens to be composite for the uncovered primes,
one after another, up to where the first prime appears. The search looked only at the top of each sequence, just below
10^200, so every N it found has 200 digits.

The graphics cards (GPUs) checked these candidates in two steps. First, a sieve divided N − q, for every candidate and
every uncovered prime q, by all primes up to 100 million; any N − q with such a factor is certainly not prime. After the
sieve, candidates differ a great deal in how many of their numbers N − q are still possibly prime, and those with the
fewest have by far the best chance. So only the most promising 1.5% of candidates went on to the second step, and from
25 November only 0.75%. That second step is a Fermat test, a fast check that a number is almost certainly prime. It was
applied to each remaining N − q in increasing order of q, and stopped at the first likely prime, whose q is g(N).

Any candidate whose g(N) beat the standing record was re-checked on an ordinary processor. It was then certified with a
complete proof: a certificate that N − g is prime, and for every smaller prime p, a reason why N − p is not prime.

The design target was g(N) of at least 170,000; call such a find a design result. Falling short of 170,000 still breaks the record if the result beats the
standing record, and that is how the last three records came.

## What it found

The search found seven records in about two days, each certified and kept in `goldbach/records/`:
- 125,269, then 132,103 and 133,981, all for 199-digit numbers, on 22 November;
- 146,191 for a 200-digit number, late on 22 November;
- 157,837 and 158,209 on 23 November;
- 160,357 on 24 November.

The last one is 7.5% of the largest g(N) one would expect among all numbers of that size, and about 99 times a typical
value.

The final campaign aimed at 170,000. It ran from 23 November 03:55 UTC to the stop and examined 67.5 million million
candidates. The model behind the search measures how often the tested numbers turned out prime and from that computes
how many successes to expect. It expected 0.69 design results. None came, which happens about half the time
at that expectation.

The same model predicted records below the target well: 2.5 expected above the record thresholds of the time, and 2
found (158,209 and 160,357).

For the last twelve hours the two remaining cards also reported every candidate above 140,000, to test the model on a
larger sample. It expected 7.15 such events, and 5 came: 159,631, 151,057, 147,331, 146,701 and 141,241. Each was
re-checked, and none is a record. Five or fewer would happen 28% of the time, so the model holds.

## What it cost

Colab charges in compute units. From the evening of 22 November to the stop, the search used about 2,750 units, about
2,460 of them on the final campaign. At their prices the cards cost:
- an RTX PRO 6000 card: 10 to 11.2 units an hour;
- an L4: about 2 units an hour;
- a T4: about 1 unit an hour.

At its largest, the fleet was three RTX PRO 6000 cards, three L4s and a T4, at 37 units an hour. From 25 November 19:38
UTC only the RTX PRO 6000 cards ran. An RTX card gave about 0.0036 expected design results an hour for 11.2 units, and an
L4 about 0.0004 for 1.9 units, so the RTX card returned about one and a half times as much per unit.

## What was tried and dropped

Most changes were tried on one card against an unchanged card running at the same time, and kept only if they measurably
helped. Dropped:
- **Carry-over.** Passing half-tested candidates on to the next batch keeps the GPU's test programs full. It gave the same
  results but 1.1% fewer expected design results per second in production, where a 2-5% gain had been predicted.
- **Clusters.** Letting groups of GPU threads share fast memory for the sieve would take at best 298 milliseconds per
  block of 16.8 million candidates, against 34 milliseconds for the existing method.
- **Overlap.** Running the next block's sieve while the current tests run gave no gain: 2.50 seconds for each round of work
  either way.
- **Kernel variants.** Two alternative arrangements of the big-number multiplication in the Fermat test were 3.5% and
  7.9% slower.
- **Other tweaks.** Some smaller settings of the sieve programs changed the time of a round of work by less than 1%,
  and were not adopted.

Kept:
- **Lower keep.** Keeping 0.75% of the candidates instead of 1.5% gave 5.6% more expected design results per
  second.
- **Better covers.** Covers using 491 in place of 463 gave 6% more.

## State at the stop

- **Units left:** 6,394.81 compute units, with nothing running.
- **Unfinished:**
  - The 170,000 target was not reached. On two RTX cards, an even chance of a result of 170,000 or more would need
    about four more days, about 2,100 units.
  - One third of the covers waited from 24 November 19:59 UTC for a third RTX card. Colab refused every request for one
    over the 37 hours to the stop.
  - The stopped L4 and T4 work waits too.
- **The files:**
  - This folder holds the search code, `README.md` (the engineering log), `TALLY.md` (expected against found for every
    campaign, final) and `runlogs/` (each card's final records).
  - `runlogs/2026-11-26/` holds the stop, including `snapshots.txt`, the list of the cards' final snapshot archives with
    their sizes and checksums.
  - `runlogs/2026-11-25/calib_hourly.jsonl` is the hour-by-hour log of the 140,000 check.
- **The snapshots:** the archives themselves (5 to 65 MB each) exist only in the temporary storage of the session that ran the
  fleet,
  and will be lost with it. A restart from this repository would regenerate the covers and skip the candidates listed as
  done in `runlogs/`.
