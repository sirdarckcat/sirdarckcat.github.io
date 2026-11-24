# Campaign records, 23 Nov 2026 (Q = 170,000)

Colab runtimes end 24 h after creation. gold-gpu (L4, created 2026-11-22T19:12:40Z) ended at 19:13:03Z on the 23rd, taking its logs with it. The others end at:
gold-g4 ~20:11Z, gold-g4b ~20:27Z, gold-g4c ~20:59Z (created 20:11 / 20:27 / 20:59 on the 22nd), gold-l4b ~00:38Z, gold-l4c ~00:41Z, gold-xt4 ~01:44Z on the 24th.
Before that, each card's state was snapshotted (`snap.py`: trees, envs, campaign logs, generator ledgers, CPU shares; not the regenerable vector chunks) and these
compact records were extracted (`extract.sh`), one directory a card:

- `<dir>_done.txt.xz`: every slice the campaign finished, `name@k0` one a line (c170v: the 89-moduli vectors, one 2^24 window each; c170 / c170f: campaign-mode slices of 2^25).
- `c170f_search.log.xz`: the L4/T4 slice lines in full (the lead's item 8 ledger: which levels of k of each m88f vector were done; `l4op/levels_done.py`).
- `<dir>_found.jsonl`: found lines (only gold-g4c's c170v: the g = 158,209 near-miss, certified in `../../records/budget_1e200_200digit_g158209/`).
- `ledger_p<P>.txt.xz`: each RTX card's 89-moduli generator ledger (covers already handed out, partition P of 3), so a replacement never repeats a vector.
- `summary.txt`: slices, batches, found lines, and the sums of the logged per-batch expected design hits and near-misses.

Final records of gold-g4 / gold-g4b / gold-g4c from their last snapshots (20:04 / 20:20 / 20:52Z); the L4s and the T4 still from 19:28-19:29Z. The day so far (first snapshots): expected design hits ~0.124 in all (RTX vector mode 0.075, RTX campaign mode before 10:57Z 0.037, L4/T4 0.012, gold-gpu's not
recovered), none found; expected near-misses >= 157,837 / 158,209 (logged in vector mode) ~0.49, one found (158,209). Final snapshots replace these before each runtime ends.
