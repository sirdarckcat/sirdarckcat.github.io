# r4_ceiling_statement: working notes (25 Nov 2026)

Sources read (all read-only, `git show origin/<branch>:<path>`):
- research `ccr-d4a17dd0-7uu03r` @ 921555c: `goldbach/sublinear/README.md` (R), `ideal_tilt_213070.txt`,
  `ideal_tilt_targets.txt`, `ideal_tilt_depths.txt`, `ideal_tilt.py`, `cover_floor_q213070.txt`;
  `goldbach/fscan/cover/README.md` (C), `closeness_cost.txt`, `brainstorm/README.md` (B),
  `brainstorm/design_menu.txt`, `brainstorm/reach_target.{py,txt}`, `brainstorm/portfolio_budget.py`
- lead `ccr-2ce9e63a-hn0fuw` @ cd82336: `goldbach/RESULTS.md`, `goldbach/phd/RESEARCH_LOG.md`,
  `goldbach/phd/cap200/brainstorm/README.md`, `goldbach/lean/scripts/lgs_heuristic/{README.md,model.py}`
- PR #34 body (REST), no comments on it
- fleet `ccr-8ffe9d7a-4ni11u` @ c518c38: `campaign3_gpu/TALLY.md`, `README.md`
- consultant `ccr-cdb2641a-5zg8un`: `goldbach/gaps_map/GAPS_MAP.md`

## (a) the spy's numbers
- nats/row: 2*prod_{3<=s<=463} s/(s-1) / ln(10^200) = 2*5.5224/460.517 = 0.02398; -ln(1-p) = 0.02428.
  `ideal_tilt_213070.txt`: "boost_z=11.0448 p_z=0.02398". R l.1354: "0.0243 nats per row". OK.
- budget e^30.75 = ln(9 d * 86400 * 29e6) = 30.747: the planning figure of 23 Nov 02:40Z
  (`ideal_tilt.py` default budget_nats=30.75; `reach_target.py` days=9 rate=29e6). Later measured rate 52M/s
  (C l.192-198), units last 8.9 d from 24 Nov 04:05Z (C l.258) -> ~e^31.1..31.3. "~31 nats" OK.
- rows: best cover at Q=213,070 on the first 89 odd primes = 1,609 (R l.409, l.1346; C l.182). Cost by the
  sources e^39.31 (sampler, cutoff k=1,620), e^39.2 direct. Spy's 38.7 = 1,609*0.024, 0.5 nat low.
- "even odds need <= ~1,288 rows": R l.1351-1354 says 1,470 (1% chance), 1,375 (10%), 1,295 (even). OK.
- shortfall: spy e^7.7 (x2,200) = gap to even odds on the updated budget ((1,609-1,295)*0.0243 = 7.6).
  Sources for ONE EXPECTED success: e^8.49 (x4,900; R l.406-408), "about 5,600 times the remaining budget
  (140 years of the present fleet, about 600 card-years)" (B l.194-197; 1,623-row 88-moduli cover; 41,000
  fleet-days with the 1,609-row cover). So the spy's is the mildest reading; conclusion unchanged.
- floor (the spy omitted it): tempering from two starts at Q=213,070 agree to 0.5 up to beta=1.07 where the
  floor is 1,554, 1,596 at beta=1.65 (R l.1346-1350). "No cover on these moduli comes within 80 rows" of 1,470.
- what the budget reaches (R l.513): today 172,000 (8.1%); ideal to 5,000: 214,000 (10.0%); 20,000: 235,000
  (11.0%); 50,000: 249,000 (11.7%); 10^8: 343,000 (16.1%). Planning model at the measured rate: 175,000 to
  176,000 (8.2%), P(10%) < 0.01% (R l.120-127). `design_menu.txt` (8.0 d, 52M/s, record 158,209):
  P(>=213,070) = 7.0e-5 (170k family B, in production), 3.8e-5 (family A), 2.9e-4 (design 213,070, which
  costs ~6,000 of expected record: 169,988 vs 175,934).

## (b) does the statement exist? Yes, >= 6 places
1. R top "Where it stands" l.16-23 (better covers are not a way to 10%), l.84-97 (10^175 numbers; ideal-5,000
   would reach one; "even a perfect search ... would stop near 16%"), l.120-127 (8.2%, chance of 10% < 0.01%).
2. R "A floor under every cover" l.1346-1356 (the spy's exact figures).
3. R Result 3 tables l.413-421 and l.505-518.
4. C l.484-509 design menu; l.545-575 "What a given closeness costs" ("a fleet that affords about 28 nats
   reaches 7 to 7.5% ... the share is set by the size of N, not by the method ... 50% is out of the question").
5. B l.46-66 price list (213,070: E 39.1, 400,000 card-days = 1,100 card-years; "20% needs E near 80"),
   l.174-199 "What 10% takes".
6. consultant GAPS_MAP.md l.118 ("aiming at 213,070 needs about 5,600 times more"), l.211 ("chance of 10%
   below 0.01%").
7. on the lead's own branch: `phd/cap200/brainstorm/README.md` l.114 "An expected record of 213,070 needs
   about 1,000 years of this fleet"; l.140 "The goal 213,070 with the fleet time there is asks for 8.4 nats".
NOT in: lead RESULTS.md (no hit for 213,070 / 0.01% / 8.2% / expected record), RESEARCH_LOG.md (last entry
23 Nov early), PR #34 body ("Open at the time of writing: the 200-digit search keeps running on a design for
g >= 170,000"). The lead's tree has 0 files under goldbach/sublinear and goldbach/fscan/cover
(merged research only up to 731826c of 22 Nov), so R, C, B are not in the PR at all.

## (c) cost at 25% and 50%
ln(N tested per success), R l.505-513 (`ideal_tilt_targets.txt`):
| target | today (<=463) | ideal 5,000 | 20,000 | 50,000 | 10^8 |
| 213,070 (10%) | 39.3 | 30.5 | 26.7 | 24.5 | 11.7 |
| 245,000 | | | 32.5 | | 16.1 |
| 265,000 | | | | 33.7 | 19.0 |
| 300,000 | | | 42.7 | | 24.1 |
| 350,000 | | | 52.3 | | 31.9 |
| 500,000 (23.5%) | | | 81.4 | | 56.8 |
20% (426,140): ideal-10^8 ~e^44; today's method ~e^87 extrapolated (R l.516-518); B l.66 "E near 80".
50% (1,065,352): 83,213 rows, random 9,972, best cover 8,740 on 88 moduli, E = 209.2 nats, 8.4e91 candidates
(`closeness_cost.txt`).
25% (532,676): NOT in the sources. My interpolation: today's method ~100-106 nats (rows = random*(1-sqrt(K*D/Q)),
R l.2196-2203, +5.5%); ideal-20,000 ~88; ideal-10^8 ~63 (exponents 1.24 and 1.62 of `ideal_tilt_depths.txt`).
Against a budget of e^31: 25% is short by e^32 even with a perfect search over the whole sieve, e^70+ today.

## number of even N < 10^200 with g(N) >= target (R l.484-499; Lean `lgs_heuristic/README.md`)
213,070: e^403.3 ~ 10^175.2 | 245,000: e^395.7 ~ 10^171.9 | 300,000: e^383.1 ~ 10^166.4 |
350,000: e^371.5 ~ 10^161.3 | 500,000: e^338.0 ~ 10^146.8 | one expected N at 2,133,689 (ceiling 2,130,704).
Not in the sources, from my re-implementation of the Lean formula lnT (c = 0.92; it reproduces the five
figures above to 0.1 nat; r4work/count_by_target.py): 426,140 (20%): e^354.4 ~ 10^153.9;
532,676 (25%): e^330.7 ~ 10^143.6; 1,065,352 (50%): e^217.1 ~ 10^94.3.

## (d) decision put to the user?
No repo document asks it. Only trace of the target: B l.176 "The user's standing goal since 23 November is
g >= 213,070". PR #34 calls "largest g below 10^200" "the current primary goal" and never says the 10% target
is priced out. But the user already re-scoped once: "The other direction, proposed by the user on the 25th"
(R l.75-82, l.2348-2487): fixed gap, fewest digits; g = 216,289 at 347 digits (PR #34 lists it).

## fleet state the spy did not use
TALLY.md (25 Nov 10:25Z): five cards, 0.19 design hits/day against ~0.29 with seven; 0.528 expected design
hits logged at Q = 170,000 since 23 Nov 03:55Z, 0 found; near-misses 2.205 expected, 2 found.
CU per hour (fleet README l.153-159): RTX PRO 6000 10.05, L4 1.94, T4 1.15 -> 25.1 CU/h now, 37.1 with seven.
Members per CU are about equal across cards, so the member budget (~e^31) is fixed by the units, not the days.

## verdict
partly_done: the analysis exists and is more precise than the spy's; missing is only (i) a short paragraph in
the lead's user-facing documents (PR #34 / RESULTS.md) and (ii) an explicit spend/target question to the user.
Gain in nats for the search: 0.
