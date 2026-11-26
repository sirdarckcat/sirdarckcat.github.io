# Goldbach gaps: start here

This folder holds a search for even numbers N whose *least Goldbach summand* is unusually large. For an even N, the
least Goldbach summand g(N) is the smallest prime p for which N − p is also prime. For example g(98) = 19, because
98 − 3, 98 − 5, 98 − 7, 98 − 11, 98 − 13 and 98 − 17 are all composite and 98 − 19 = 79 is prime. For almost every
number g(N) is small; the game is to build numbers where it is large, and to prove it.

The main question was how large g(N) can be for an even N below 10^200. The best number found has g(N) = 160,357.

## What to read first

1. **`COVER_LETTER.md`**: what was tried, what was found and what went wrong, written for a reader without a
   mathematics degree. It ends with a glossary.
2. **`REMAINING_WORK.md`**: everything left unfinished, with where to pick it up and what it would cost.
3. **`RESULTS.md`**: the record log, newest first, with the details of how each record was found and checked.
4. **`records/`**: one folder per record, each with the number, its proof files and a `README.md`.

Each of the sessions that worked here wrote a handover note in plain English:

| note | what it covers |
|---|---|
| `phd/campaign3_gpu/HANDOVER.md` | the 200-digit search on Colab's graphics cards |
| `sublinear/HANDOVER.md` | the search for a better method, and the toy worlds |
| `lean/HANDOVER.md` | the formal proofs in Lean |
| `sieve200/HANDOVER.md` | the fast sieve and Fermat code, the fixed-gap 200,000 records, the closeness frontier |
| `bottom_up/HANDOVER.md` | the million-gap records, the forecasts, the two-stage design, toy worlds 2 and 4 |
| `gaps_map/HANDOVER.md` | the map of results, the literature, the stronger growth bound on paper |
| `review/OUTSIDE_REVIEW_2026-11-25.md` | an outside review of the whole effort; its Part 1 is for lay readers |

## How the folder is organised

**The records**

| path | what is there |
|---|---|
| `records/` | every certified record. Folder names say the game, the size of N and g: `budget_1e200_200digit_g160357` is the record below 10^200, `height_...` the height game (no limit on N), `threshold_...` the smallest N for a given g, `g200k_...` the fewest digits for g ≥ 200,000 |
| `g_million/` | the fewest digits for g ≥ 1,000,000 (1,797, 1,997 and 2,196 digits) |
| `closeness25/` | two numbers at a quarter of the largest g expected for their size (47 and 48 digits) |

**Searching at 200 digits**

| path | what is there |
|---|---|
| `phd/campaign3_gpu/` | the GPU search program, its run logs and its tally of expected against found |
| `phd/campaign3/`, `phd/cap200/` | the covers and processor drivers of the same campaign; covers for targets from 122,000 to 213,070 |
| `fscan/cover/`, `ptcover/` | the programs that search for good covers |
| `two_stage/` | how many candidates to test, and why the emptiest ones first |
| `search.py`, `cover.py`, `anneal.py`, `gen_variants.py` | the original processor search from July 2026 |

**Fast arithmetic**

| path | what is there |
|---|---|
| `sieve200/` | the sieve in C and on the GPU |
| `fermat661/`, `fermatw/` | Fermat tests for 200-digit numbers and for numbers of any size, on processors and on the GPU |
| `UARCH.md`, `HEADROOM.md` | measurements of every speed-up tried, and how much was left |

**The other games**

| path | what is there |
|---|---|
| `proth/`, `bls/` | the height game: numbers whose N − g has a shape that makes its primality quick to prove |
| `tscan/`, `fscan/` | scanners for small N (the threshold game and the closeness frontier) |
| `g200k/` | the fixed-gap 200,000 searches and the 10% closeness frontier |
| `tempering_covers/` | covers that deal with every prime below the target, with no luck at all |

**Theory and analysis**

| path | what is there |
|---|---|
| `ceiling_model.py`, `closeness.py`, `ceiling_table.json` | the largest g expected at each size, and the score of a number against it |
| `gsample.c`, `samples/`, `record_holders.txt` | the checks of that model: random numbers, and the 69 record holders below 4·10^18 |
| `sublinear/` | the research session's notes on the search for a better method (start with its `HANDOVER.md`; its `README.md` is the full record) |
| `bottom_up/`, `H2_one_page.md`, `balls_in_boxes/` | forecasts, bounds on search methods, and what a cheaper test would be worth |
| `archipelagos/` | g(N) computed exactly for 20 million consecutive even numbers near 10^12, 10^15 and 10^18 |
| `gaps_map/` | a map of how the results depend on each other; open `viz/goldbach_map.html` in a browser |
| `archive_map/` | a map of the Lean archive that came with the note `remark.pdf`, which started this round of work |
| `lean/` | the Lean proofs; build with `lake build` in that folder |
| `review/` | the outside review and its rechecks |
| `SOK_GOLDBACH_GAPS.md` | the state of knowledge from the earlier work, updated with errata |

**Earlier work (July 2026)**

`FRONTIER.md`, `IDEAS.md`, `IDEAS100.md`, `PROPOSAL_NEXT_CAMPAIGNS.md`, `constructions/`, `gpu/` and the scripts
`exp1m.py`, `exp_order.py`, `entropy_frontier.py`, `joint.py`, `realizable_frontier.py`, `frontier_table.py`,
`mega_verify.py`, `verify_megagap.py` and `verify_barrier.py` come from the sessions of July 2026, before this work.
A parallel collection from that time is in `../slop/goldbach/`.

## Checking a record

Each record folder's `README.md` lists its proof files and the commands that check them. `COVER_LETTER.md` has a worked
example for the 160,357 record: four commands, each taking a few seconds, that rebuild N, check the primality
certificate of N − g, and recompute g(N) from N alone in Python and in PARI/GP.

## How much to trust each result

The notes mark results in five grades: **proved** (on paper, sometimes within a stated model), **machine-checked**
(also proved in Lean), **computed twice** (by two independent programs or sessions), **computed once**, and **opinion**.
No human mathematician has refereed any of it. Some notes measure work in *nats*: one nat is a factor of e, about 2.72,
so 5.5 nats is a factor of about 250.
