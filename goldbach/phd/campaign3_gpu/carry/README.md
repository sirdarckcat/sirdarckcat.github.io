# Carry-over of unfinished members into the next Fermat pool (the lead's item 1, 25 Nov 17:57Z)

The code is uarch's (ccr-b8c25887-i6tn9f at fe27cbe):
- `fround_carry.patch` applied to the deployed fround.py (a4d0c7933ffd) gives `fround_carry.py` (88f67789996f).
- `search_gpu5_carry.patch` applied to 9385f3b's search_gpu5.py (4f27d916ea93) gives bf10e5fb8bf0.
- This session added `--record` on top (the lead's 140,000 calibration, 18:52Z): a verified near-miss with g <= RECORD goes to near_events.jsonl beside found.jsonl, with
  "sub_record": true and each N once. found.jsonl keeps the records and every design hit. The result is `search_gpu5_carry.py` (2377c5775be7).

## Checks

1. Launch timing: `time_launch.py` on gold-g4j with production paused 14 s (`time_launch_gold-g4j.txt`).
   - The production 29-bit step: t_min = 1.499 ms and R = 24.87M tests/s.
   - uarch's 23 Nov fit had implied about 4 ms.
2. CPU: uarch's `test_carry_campaign_fake.py` on these exact files PASSED. With --record unset it gives `proof_carry_split_cpu.txt`.
   `test_split.py`: the record split with the carry path's dedup, across a restart: PASSED.
3. The identity gate on gold-g4j, 19:49:21-19:51:12Z with production paused (`cgate.sh`, `cmp_cgate.py`, `cgate_gold-g4j.txt`, `cgate_stats_gold-g4j.txt`).
   - Setup: 28 vectors the card had done, the production options and --near-miss 50000.
   - The production engine and the carry engine (--carry-over 1 --record 160357) gave the same 28 slice lines (timings aside).
   - They gave the same 820 events as a set (all sub-record: in near_events.jsonl), and the same 98,824,669 counted tests.
   - The production known case on the carry engine: 23 = 23.
   - Rounds a half-pool 43.0 → 22.4, against uarch's 44.8 → 22.0.
   - Tests computed −2.63% and waste 3.06% → 0.45%, both including the run's final drain.
4. Deployed on gold-g4j at 19:53:41-19:54:42Z (`deploy_carry.py`).
   - The engine and fround were swapped (the old ones kept as *_pre_carry.py).
   - deep_env_v89 gained --carry-over 1 --record 160357, and NEAR_MISS went 160357 → 140000.
   - The campaign restarted in place at a batch end; the generator and the row guard were untouched.
   - The production A/B against gold-g4k (baseline) runs from 20:00Z.
