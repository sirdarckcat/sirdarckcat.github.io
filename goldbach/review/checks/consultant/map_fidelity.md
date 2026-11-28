# map_fidelity: audit of the consultant map (origin/ccr-cdb2641a-5zg8un @ 85f67f4, 25 Nov 11:50 UTC)
Audited the RENDERED boxes (viz/gb_data.json = cur_res_* + cur_patch applied), 27 boxes + narrative GAPS_MAP.md.
Sources at head: research 921555c (11:46), fleet c518c38 (10:44; TALLY a8fc962 10:28), Lean 8042472 (11:52), uarch 05a396b (11:40), student aea95bb (11:35).

## Campaign-limit boxes: numbers RIGHT against primary source
- m_floor 1,214 / 1,248 / 1,554-1,596 / 1,609 / 1,470 / 1,264-1,277 / 1,308.67 / e^4.0: README l.1316-1364. Label "measured" correct (title fixed).
- d_ub89 777 (j=10, 7.3e8 nodes, 3.5 h), 401, 644, 62%, 15,907 <= D(89) < 35,000: README l.1240-1263. Label exhaustive/not in Lean correct.
- m_ceiling 2,130,704 = ceiling_table.json "200.0".median (p05 2,123,360, p95 2,143,754); 2,133,689 lgs model.txt l.66. heuristic label ok.
- s_prize 3.5/5.9/8.8/12.6/14.8 nats, e^39.3/35.8/30.5/26.7: README l.415-423, 513.
- m_designmenu table (0.89/0.52/0.19/0.017; 175,900...; 176,800...) = cover README l.493-508. P(10%) 0.00007.
- m_price = price_list.txt. m_portfolio 50,749 = reach_target.txt (9 days, 29M, old).
- m_floorpred 1,221 / 1,584, 1,505/1,262/888/550: README l.2207, 2277.
- e_fleetnow day-one numbers = day_one_report.txt l.15, l.33.
- d_prefixcheck = Lean cover_prefix_check README (0.058.., 3,349/3,452/1,606, 2%/9%/10^25).

## STALE / WRONG
1. e_dual, e_dualcpu, meta.news, GAPS_MAP l.213-214: fixed-gap game "untested", "costed, not run". Source since 09:37-11:46: 3 records (200,293 & 206,593 at 400 digits, Lean-certified 6a2b774; 216,289 at 347 digits), table "too hopeful by a factor of two to four in members", rows 4-7% above floor, survivors binomial not Poisson (gain 2-4 not 1.8-15), CPU-hours 1.1/15/420/12,000 (map: 1.3 vs 0.18, 49,000 vs 3,200), forced from 1,340 / 4,900 digits (map 1,300 / 4,700). Map boxes frozen at 48c73de (08:46).
2. e_fleetnow: "0 design hits against about 0.41 expected (P(0) = 66%)"; TALLY 10:25: 0.528 expected, P(none) 0.59; near-misses 2.21 expected / 2 found.
3. m_thm1 detail: "the research session conjectures D(n) ≈ 1.1275 · r ln² r" (withdrawn 10:20).
4. m_lower detail and edge d_limit>m_thm1: "now has the order ... /ln ln ln N" (withdrawn 11:45).
5. m_errata: "1.1275 ... since qualified by the referee check" (withdrawn).
6. e_t5: "3,028 rows ... no tempering run"; student 526aa3a/5634ebf: 2,829 at 629 moduli, 2,563 at 683, heat-bath PT, scan at 2,196 digits.
7. d_block chip 'unformalised', note "Not formalised, and far from it"; m_thm1 "any f(x)->inf times x ln x is the named open next theorem": Lean 1f1b090 (11:52, 2 min after map) proves every-constant.
8. GAPS_MAP header and meta.care: "snapshot ~09:00, research at 48c73de, fleet ebb6e1e, Lean a1c77dc" while commit msgs claim 921555c.
9. m_floorpred: no mention of "4 to 14% low nearer the end" (README l.40-43, 34551f6).
10. GAPS_MAP l.213 "200,000 at about 225 digits costs what 170,000 costs at 200" (QA defect e_dual fixed in box, not in narrative; source: 230).
## Status label overstated
- d_limit detail "The proved window is r ln² r ln₃ r/(ln₂ r)² ≪ D(n) ≪ r^(4+ε)", gist "rigorous D(n) ≥": paper proof by consultant, same hour, unrefereed (Lean README: "in outline ... should check it before it is cited"; research: "a theorem on paper"). Upper window has no source outside COHERENT_BLOCK.md.
- m_portfolio/m_designmenu/GAPS_MAP: 175,000-176,000 is for 7 GPUs at 0.29/day; fleet at 0.19/day. Flagged in box but headline unchanged.
## QA report applied? 14 sampled, 13 applied, 1 partial (d_reach "passes through different families"), plus narrative l.213 miss; e_dualcpu edge fixed to "1.8 to 15" but source now says 2 to 4.
