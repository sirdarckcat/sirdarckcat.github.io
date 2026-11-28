# T2: complete covers by parallel tempering, x = 127 to 1,999

This is a task from the research session (branch `ccr-d4a17dd0-7uu03r`, `goldbach/sublinear`). The moduli are the odd primes
up to x, and each gets one nonzero class. A vector *reaches* Q when every odd prime below Q lies in one of its classes. For
each x we look for the largest Q at which parallel tempering finds such a vector. The search program is `ptcover_fast2` (56
replicas, `betas56.txt`). It is `ptcover_fast` from the uarch session with two changes: it reports the first sweep at which
each best k was reached, and it allows up to 512 moduli (the old 256 crashed at x = 1,999). Its runs are otherwise identical.

The search (`t2.py`) works as follows.
- It first scans coarsely with short runs around 0.87·x·ln²x.
- It then confirms a missed Q with long runs and bisects to 0.5%.
- Every point uses 4 seeds, one core each, at a fixed budget: 80,000 sweeps for x ≤ 400, 120,000 for x ≤ 800 and 160,000
  above. At x = 997 it starts from the 40,111 cover.
- A point counts as reached when some seed ends at k = 0 (no row left).
- Every run is in `t2_runs.jsonl` and can be resumed. The container restarted several times on 24–25 November; the search
  resumed from the log each time, and the point in progress was run again.

## Table

| x | moduli | sweeps per run | bracket at that budget: largest Q reached / smallest Q missed by all seeds | seeds at k = 0 at the top (sweep of the first k = 0) | best k of each seed at the miss (sweep it was first reached) | 4× longer runs at the miss: best k (sweep) | best vector of any run: first odd prime in no class | / (x ln x) | / (x ln² x) | runs |
|---|---|---|---|---|---|---|---|---|---|---|
| 127 | 30 | 80,000 | 2,300 / 2,333 | 1 (714), 2 (1,083), 3 (763), 4 (1,618) | 1 (1,285), 1 (1,389), 1 (962), 1 (1,606) | 1 (1,285), 1 (1,389), 1 (962), 1 (1,606) | 2,311 (Q = 2,300, 80,000 sweeps) | 3.76 | 0.775 | 24 |
| 149 | 34 | 80,000 | 2,921 / 2,957 | 1 (62,117), 2 (14,468), 3 (43,139), 4 (70,949) | 1 (490), 1 (1,245), 1 (1,329), 1 (1,810) | 1 (490), 1 (1,245), 1 (1,329), 1 (1,810) | 2,953 (Q = 2,921, 80,000 sweeps) | 3.96 | 0.792 | 28 |
| 251 | 53 | 80,000 | 6,440 / 6,480 | 1 (25,585) | 1 (15,228), 1 (13,401), 1 (15,773), 1 (17,605) | 1 (15,228), 1 (13,401), 1 (15,773), 1 (17,605) | 6,451 (Q = 6,440, 80,000 sweeps) | 4.65 | 0.842 | 28 |
| 349 | 69 | 80,000 | 10,085 / 10,116 | 1 (49,821), 2 (21,895) | 1 (57,384), 1 (46,820), 1 (53,220), 1 (16,891) | 0 (96,193), 0 (302,094), 1 (53,220), 1 (16,891) | 10,159 (Q = 10,116, 320,000 sweeps) | 4.97 | 0.849 | 32 |
| 397 | 77 | 80,000 | 12,094 / 12,131 | 2 (76,308) | 1 (67,186), 1 (42,145), 1 (68,898), 1 (22,433) | 0 (265,529), 0 (133,820), 0 (133,976), 0 (316,759) | 12,163 (Q = 12,131, 320,000 sweeps) | 5.12 | 0.856 | 32 |
| 599 | 108 | 120,000 | 21,036 / 21,100 | 1 (60,573), 2 (106,750), 3 (110,280) | 1 (67,580), 1 (102,427), 2 (64,752), 1 (109,818) | – | 21,067 (Q = 21,036, 120,000 sweeps) | 5.50 | 0.860 | 28 |
| 797 | 138 | 120,000 | 30,916 / 31,009 | 4 (79,647) | 2 (75,433), 2 (67,629), 3 (97,419), 1 (82,476) | – | 30,931 (Q = 30,916, 120,000 sweeps) | 5.81 | 0.870 | 28 |
| 997 | 167 | 160,000 | 41,640 / 41,768 | 4 (154,850) | 2 (149,364), 1 (85,982), 2 (150,391), 2 (116,313) | – | 41,659 (Q = 41,640, 160,000 sweeps) | 6.05 | 0.876 | 24 |
| 1,499 | 238 | 160,000 | 70,059 / 70,275 | 4 (91,540) | 2 (138,914), 2 (135,283), 1 (143,628), 1 (158,423) | – | 70,111 (Q = 70,059, 160,000 sweeps) | 6.40 | 0.875 | 40 |
| 1,999 | 302 | 160,000 | 98,495 / 98,791 | 4 (153,925) | 2 (143,748), 3 (157,519), 4 (105,548), 2 (143,205) | – | 98,731 (Q = 98,495, 160,000 sweeps) | 6.50 | 0.855 | 36 |

Columns 5 to 7 give, for the top and the bottom of each bracket, the sweep at which each seed first reached its best k. That
shows whether a miss is a wall or a matter of run length. The best vector of each x is in `t2_vectors.txt`. The ones for
x ≥ 997 are also in `complete_cover_<reach>_<moduli>primes.txt`. All were rechecked by `reach.py` and by direct division.

## Findings

1. **The reach as a multiple of x·ln²x is 0.775, 0.792, 0.842, 0.849, 0.856, 0.860, 0.870, 0.876, 0.875 and 0.855** for
   x = 127 to 1,999. It is flat from 797 to 1,499 and lower at 1,999, where the one successful seed at the top needed 96%
   of the budget. This series does not come from one protocol throughout:
   - at 349 and 397 the best vectors come from the 4× longer runs;
   - x = 997 started from the 40,111 cover;
   - 599 and above were not probed with longer runs.
   The bracket columns of the table are the planned budget alone.
2. **The misses are a wall up to x = 251 and a matter of run length from about 350 on.** At x = 127, 149 and 251 every seed
   reached k = 1 at the smallest missed Q early (by sweep 490 to 17,605). It stayed there in runs four times longer (320,000
   sweeps, `t2_probe.py`). The wall at 127 is the exact optimum: the uarch session has since proved D(30) = 2,311. At
   x = 349 and 397 the longer runs cross the miss: 2 of 4 seeds at 10,116 and 4 of 4 at 12,131. From 397 on, the successful
   seeds at the top need 50–97% of the budget. So the entries from 349 on are lower bounds set by the budget.
3. **The tempered reach is close to where complete covers end, as counted.** The count is the research session's
   `cover_floor`, run at 60, 75, 85 and 93% of the tempered reach for x = 127 to 1,999. The 93% target was also run once
   from the best tempered cover (and the 85% one at 397 to 1,999). The results are in `floor/`, all nine sizes in
   `floor/floor_report.md`.
   - ln(number of complete covers) falls from θ(x) at Q = 0 with slope about 1.0·Q/ln²x (0.98 to 1.05 for x ≥ 251) up
     to about 75–85% of the reach.
   - Over the last interval (85 → 93%), random starts give slopes of 1.13 to 1.64. The cover start agrees with them at 93%
     up to x = 349 (within 0.3 nats), so there the steepening is real: 1.24, 1.62, 1.25 and 1.52 at x = 127, 149, 251, 349.
   - From 397 on the random starts undercount at 93%: by 1.5, 5.8, 6.6, 20.8 and 14.2 nats at x = 397, 599, 797, 1,499,
     1,999. With the cover-start values the slope is 1.21, 1.22, 1.09, 0.98 and 1.03. So the bend is clear up to 599,
     weaker at 797, and gone at 1,499 and 1,999. At those two sizes even the cover-start values are still rising (drift
     +3 to +10 nats), so they are lower bounds.
   - With the cover-start values, the straight line through the last interval ends at 0.96 to 1.03 × the tempered reach
     up to 599, and at 1.06, 1.11 and 1.12 × reach at 797, 1,499 and 1,999. There the reach is limited by the budget.
     A line of slope 1 through θ(x) ends 9–14% beyond the reach.
4. **At x = 997 near the end** (`floor/run_997.py`, `floor/x997_report.md`):
   - The counts at Q = 39,000 and 40,111 are ln g0 = 130.2 and 98.6 started from the 40,111 cover, 119–121 and 74–80 from
     random starts, and 94.6 at 40,111 started from the random family's best vector.
   - So the random starts mostly had not arrived. The two families of small-prime classes differ by about 4 nats.
   - The complete covers sampled at 40,111 reached 40,459, the first cover past 40,111 on these moduli.
   - Tempering from the 40,111 start then reached 41,047 and 41,659. Both are in a small-prime frame close to the second
     family's, not the start cover's.
   - The Lean session has certified all three in the kernel: Cover40459.lean, Cover41047.lean and Cover41659.lean, on its
     branch `ccr-36ca7b46-8twf14` (commit 673c39d for the last).
   - The count-based end of complete covers at 997 is at or below about 43,600, so 41,659 is at least 0.955 of it.

## Files

| file | what it is |
|---|---|
| `t2.py` | the search: `python3 t2.py x [x ...]` or `x:lo:hi[:startfile]`; resumable from `t2_runs.jsonl` |
| `ptcover_fast2.c` | the tempering program (see above); `ptcover_fast.c` and `ptcover.c` are its predecessors |
| `t2_firsthit.py`, `t2_firsthit.jsonl` | reruns of the bracket ends made before `ptcover_fast2` existed, for their first-hit sweeps (27 of 27 identical to the logged runs) |
| `t2_probe.py`, `t2_probe.log` | 4× longer runs at the smallest missed Q (x = 127 to 397) |
| `t2_table.py`, `t2_table.md`, `t2_vectors.txt` | the table above and the best vector per x |
| `reach.py` | the first odd prime in no class of a vector |
| `mod_<x>.txt`, `mod_997_start40111.txt`, `betas56.txt` | moduli, the 997 start cover, the temperatures |
| `complete_cover_*.txt` | the best covers at x = 997 (40,111 from earlier work; 41,047; 41,659), 1,499 and 1,999 |
| `floor/` | the cover counts: `run_floor.py` (x = 127 to 599), `run_997.py`, `cover_floor.c` and `cover_floor.py` from the research session, `cover_floor2.c` (also keeps the vector of the largest reach sampled), reports and raw outputs in `runs/` |
