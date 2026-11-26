# r6_workqueue: "Persistent work-queue Fermat kernel that removes the per-wave tail"

Verdict: MEASURED AND REJECTED on the RTX PRO 6000 (G4) cards; built but never run on L4 / T4.

## How production schedules Fermat work (primary sources)

- Driver: fleet branch `origin/ccr-8ffe9d7a-4ni11u:goldbach/phd/campaign3_gpu/search_gpu5.py`
  - `run_pool` (line 311). Round rule, line 335: `D = max(1, min(dmax, rem.max(), target // active))`,
    every active member is tested on D rows a round; line 371 `act = act[(~hit) & (~done)]` compacts every round.
  - With `--fused-rounds 1` (line 320) the same schedule runs on the device: uarch branch
    `goldbach/fermat661/cuda/fround_kernels.cuh` (`fr_plan` D = clamp(target / nact, 1, dmax); `fr_compact` order-preserving),
    ~10 launches and one host read a round (FROUND.md).
  - `run_pool_split` (line 395): two half-pools in two threads on two streams, each with `target // 2` (line 415).
  - One flush a batch (`--pool 2097152`, v89/run_v5_vec.sh line 8; line 513).
- Deployed flags (runlogs/2026-11-24):
  - G4 `gold-g4f/deep_env_v89`: `--pool-threads 2 --pipeline 1 --pipeline-depth 4 --fused-rounds 1 --target 524288` (dmax default 8), f = 0.985.
  - L4 / T4 `gold-l4f/deep_env`, `gold-xt4b/deep_env`: `--fused-rounds 1` only (target 2^20, one pool thread, no pipeline), f = 0.97.
  - No `--persist`, no `--tail-target` anywhere in the deployed driver (0 matches).
- So production is NOT "one row per alive member per wave" (that is the legacy goldbach/gpu/engine150.py, lines 269-280).
  Launches are kept at ~target tests by raising D up to 8; only when active < target/8 do they shrink.

## The recommendation was built and measured (23 Nov)

- Kernel: uarch `goldbach/fermat661/cuda/fermat28_persist_kernel.cuh` (every thread takes a member with one atomicAdd, tests its rows
  in order to the first PRP, takes the next); driver patch `search_gpu5_persist.patch` (`--persist 1`, `--persist-cta-sm`, `--persist-maxreg`,
  plus a `--tail-target/--dtail` tail rule for the rounds); CPU tests `test_fermat28_persist.py`, `bench_persist.py`.
- GPU logs on the fleet branch, `uarch_measure/`:
  - `plt8_persist_rtxpro6000.txt`: v1 2.68-2.84 s a batch against base 1.84 / a2 1.53 (a warp-divergence bug). Tail rule alone (a2t) 1.504 vs 1.524/1.529 = -1.5%, under the 2% bar, not deployed.
  - `plt9_persist_v2_rtxpro6000.txt`: kernel 23.43M tests/s = 0.98 x production (23.79M); alone (no sieve beside it) 1.782 s vs base 1.844 s = -3.4%;
    beside the sieve (ps1) 1.667 s vs a2 1.537 s = +8.5% WORSE. 111.8k members still in flight when the queue empties, finished by 16 round-based launches in 98-121 ms (2.08M tests).
  - `plt10_persist_room_rtxpro6000.txt`: 2 / 3 / 4 / 5 CTAs an SM, carve-outs, sieve flat out: 1.627-1.824 s against a2 1.522-1.547 s: +5% to +19% in every configuration.
- Write-ups: uarch `fermat661/cuda/FERMAT28.md` lines 191-245; `HEADROOM.md` lines 100-108 ("closed for the RTX cards"; "For the L4 / T4 the plain -3.4% is available, ~+0.6% of the fleet", "untested there").
- Reason it loses on the G4: 940 persistent CTAs hold 61,440 of an SM's 65,536 registers and never retire, so the overlapped sieve gets no slot.

## Is there an under-filled tail, and how big?

Measured:
- `uarch_measure/profile_pool_rtxpro6000.txt` (alone, one pool of 2,015,232): 44-45 rounds, waste 3.1%, kernels 22.7-22.9M tests/s against 23.3M peak, gap 6.0-7.1% of run_pool.
- `fround/frab_rtxpro6000.txt` (f = 0.985, beside the sieve): half-pool of 503,808, 36-41 rounds, kernels 0.34-0.41 s, run_pool wall 0.640-0.691 s, gap 0.235-0.350 s.
- `fround/tune2_rtxpro6000.txt`: waste 5.7% (target 2^20), 3.1% (target 524288), 3.8% (dmax 4), 5.0% (dmax 6); only tgt512k moved the batch (x0.986).
- `fround/ctlab_rtxpro6000.txt`: gap a half-pool 0.295 -> 0.198 s but batch x0.998: the gaps are already filled by the other half and the sieve.

My simulation of the schedule (sim_rounds.py, sim2.py in this folder; p = 0.0713) reproduces all five measured waste figures within 0.1 pt
(3.1 / 5.7 / 3.0 / 3.8 / 5.0%). For today's G4 half-pool (503,808 members, half-target 2^18): ~43 rounds, 16 of them below half the target,
holding 2.7% of the tests; if nothing else used the GPU they would cost <= ~20 ms a batch. On the G4 the sieve stream uses that time.
L4 (one pool of 2.0M, target 2^20, one wave = 37,120 tests): 19 rounds below one wave holding 0.24% of tests, ~36 ms of an ~8 s batch (0.5%).

## Batch split

- G4 (HEADROOM.md status at 14:30Z, 0.755 s a batch): Fermat kernels ~0.62 s alone, sieve ~0.25 s alone; serial-sum fit batch = fixed (sieve) + Fermat;
  fixed part ~0.243 s (32%). README line 566: the sieve thread is busy ~100% of a batch.
- L4 (HEADROOM.md, two batch times): S = 3.27 s, F = 6.06 s of 9.33 s on 23 Nov 17:30Z; after l4op the sieve is ~0.8 s a 2^25 window, batch ~8.05 s:
  Fermat ~6.2 s (77%), sieve ~1.6 s (20%), other ~0.3 s (3%).

## Residual

- G4: none (measured worse). Ceiling of any waste/tail fix that keeps the overlap: the 3.1% waste x ~65% Fermat share = ~2% of a batch.
- L4 / T4 (20% of the fleet: 0.51 of 2.51 RTX-equivalents): +0 to +3.4% a card = +0 to +0.7% of the fleet = <= 0.007 nats.
  My estimate: waste 3.1% x 0.77 = 2.4% + tail 0.5% - 0.98x kernel x 0.77 = 1.5% -> ~+1.3% a card, ~+0.3% of the fleet.
- A flag gets most of it without the kernel: `--target` was only ever tested on the RTX cards. Simulated waste for the L4 pool:
  3.06% (2^20, now) -> 1.55% (2^19) -> 0.78% (2^18) -> 0.38% (2^17), for 7-26 more rounds. Not measured.
