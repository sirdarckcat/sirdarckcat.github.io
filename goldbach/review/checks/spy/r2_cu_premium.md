# r2_cu_premium - working notes (reviewer, 25 Nov ~12:30Z)

Recommendation: "Find and remove the unexplained +3.17 CU/h premium on the newer G4s" (spy rank 2).

## Sources read
- fleet branch origin/ccr-8ffe9d7a-4ni11u (HEAD c518c38, 25 Nov 10:44Z):
  - goldbach/phd/campaign3_gpu/README.md:153 (T4 1.15), :158-160 (G4 10.05, A100 6.73, L4 1.94, CPU 0.26, "from the Colab usage rate as runtimes were added (22 Nov)"),
    :695-706 and :760-778 (caps, 22:46Z run-to-end rule, 5 active assignments at 22:47Z)
  - runlogs/2026-11-24/day_one_report.txt:33 "CU: 7,967.7 at 37.12/h" (the ONLY balance figure in any branch)
  - runlogs/2026-11-24/rates_0400.txt, TALLY.md:69-75 (per-card expected design hits)
  - bringup/handover.sh:16, handover_pro.sh:36, handover_end.sh:23, g4_poll.sh:10, l4_poll.sh:10, stopgap_l4.sh:8, test_cap.sh:20/48/50; goldbach/gpu/fleet.py:186
    -> every runtime is created with `colab new -s NAME --gpu TYPE`, no other flag, in round 1 and round 2 alike
  - uarch_measure/plt4_rtxpro6000.txt:84-88: G4 host = 48 vCPU EPYC 9B45, 176 GB (23 Nov, at 10.05 CU/h)
  - no script calls `colab usage`; no units ledger is committed; no note on high-RAM / shapes anywhere (grep on all branches)
- consultant map: goldbach/gaps_map/data/ledgers/ledger_fleet_delta.md:266 "No CU figure after 04:05Z is in the repo."
- lead transcript dump (scratchpad/lead_pages/p004_full.txt:127-128, 202-218; p008:112; p011:51,119; p012:154; p013:58) - GPU session's own reports:
  - 23 Nov 16:47Z 8,383.78 @37.12 | 18:40Z 8,309.56 | 19:12Z 8,291.01 | 24 Nov 04:05Z 7,967.7 @37.12 | 24 Nov 22:47Z 7,275 @28.30 (5 assignments) | 25 Nov 07:33Z 7,027.8 @28.30
  - 25 Nov 07:37Z report: "the same mix costs 28.30 today, +3.17 CU/h, so at least one of the newer sessions is priced higher. If it is the two new G4s ... ~11.7 CU/h each. I cannot attribute it per session from here."

## Premise checks
1. Discrepancy exists: YES. Displayed rate 28.30 vs 25.13 nominal; balance confirms: 7,275 -> 7,027.8 in 8.767 h = 28.20 CU/h (nominal would be 220.3 CU, measured 247.2).
2. It is the spy's finding: NO. It is the GPU session's own caveat, already relayed to the lead (who repeated it to the user) at 07:37Z; nobody followed up.
3. It sits on the two newer G4s: NOT SHOWN, and the balance leans against "only from their creation":
   - 24 Nov 04:05 -> 22:47Z burned 692.7 CU; nominal with no handover gaps is at most 665.7 (15.9 h x 37.12 + 2.67 h x 27.07 + 0.13 h x 25.13): excess 27.0.
   - a premium of 1.585 on g4g (19:16Z) and g4h (19:33Z) gives only 10.7 CU by 22:47Z.
   - earlier windows ran at or BELOW nominal (16:47Z 23 Nov -> 04:05Z 24 Nov: 416.1 measured vs 419.5 no-gap nominal).
   - so either the higher price began around 14-16Z on 24 Nov (on sessions already running), or ~16 CU went elsewhere that day.
4. Cause is a runtime shape option: NO SUPPORT. Same creation command throughout; round-1 replacements (g4d/e/f, l4d/e/f, xt4b) priced exactly nominal (37.12 = 3x10.05 + 3x1.94 + 1.15 at 04:05Z 24 Nov).
   No cheaper shape for the same card in any note. The G4 host was already 48 vCPU / 176 GB at 10.05.
5. Removable: NOT UNDER THE RULES. Lead's 22:46Z rule: no proactive stops, because a stopped card may not be regranted (G4 refused since 19:59Z 24 Nov, L4 since 22:39Z). Re-rolling a G4 risks 43% of the fleet's hit rate.

## Numbers (GPU session 07:37Z, last-hour rates; agree with TALLY.md:72-74)
- design hits/s: G4 9.58e-7, L4 1.19e-7 (1.185e-7 mean), T4 5.45e-8
- per CU at nominal: G4 3.43e-4, L4 2.20e-4 (0.64), T4 1.71e-4 (0.50)
- fleet 7.95e-3 /h = 0.19 /day; per CU 2.81e-4 at 28.30, 3.16e-4 at 25.13: x1.126 = 0.119 nats (spy's arithmetic is right as an upper bound)
- on 7,027.8 CU: 1.97 expected design hits at 28.30, 2.22 at 25.13 (+0.25); 10.3 vs 11.7 days
- gain from stopping the small cards (the lead's pending decision) depends on where the premium sits:
  A on the two G4s (11.635 each): G4 2.96e-4 -> +5.6% | C uniform x1.126: +8.5% | D on the T4 alone: drop T4 +15% | B on the 2 L4 + T4: +22%

## Cheapest decisive test (0 CU)
- now: GPU session prints its raw usage-log lines (time, rate, balance) for 24 Nov 04:05-22:47Z; a reading between 19:59Z and 21:16Z of 27.07 clears g4g/g4h and l4g, 30.24 pins them.
- tonight: `colab usage` every <= 20 s over 19:10-19:40Z (l4g 19:15, g4g 19:16, g4h 19:33), then 21:21Z (xt4c) and 22:42Z (l4i); also the + step of every replacement.
  l4g and g4g end one minute apart, so sparse polling confounds them.

## Verdict
valid_untested as a 0-CU attribution check; the "remove it by choosing a cheaper shape" part has no support. Value 0 to 0.12 nats; not a way out of the local minimum (7.7 nats needed for 213,070).
