# Inputs of TALLY.md as of 2026-11-25 10:25 UTC

- `snap_all.txt`: `../../t3.py` on the c170* dirs of each replaced card's final snapshot (round 1: gold-g4, g4b, g4c, l4b,
  l4c, xt4; round 2: gold-g4d, g4e, g4f, l4d, l4e, l4f, xt4b). Round-2 snapshots also hold copies of their predecessors'
  older dirs, which `mkmd.py` does not count again.
- `lives_all.txt`: `t3.py` on the five running cards at 10:22-10:25Z (c170r / c170g). A resumed dir holds its
  predecessor's records too, so these rows are whole shares.
- `snap_since.txt`: the round-2 snapshots, with the sums from 24 Nov 19:59:08Z on (the smaller fleet).
- `snap150.txt`: the Q = 150,000 dirs (c150) of the round-1 snapshots (final, 23 Nov ~03:55-04:03Z).
- `mkmd.py`: writes the Q = 170,000 table rows, the near-miss sums by threshold, and each running card's own part.
