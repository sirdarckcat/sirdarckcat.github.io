# map_structure — structural analysis of the consultant's map (gb_data.json @ origin/ccr-cdb2641a-5zg8un)

Scripts: consultcheck/run/map_structure/an.py, an2.py. Raw outputs appended below (out.txt, out2.txt).
Edge convention (meta.mapLabel): "Arrows point from a result to what it relies on." A>B = A relies on B.

## Headline numbers
- 187 boxes, 417 links, 10 groups; DAG (no cycles, no dangling ids, no isolated box, one undirected component).
- Status: lean 95, leanhyp 1, comp 60, heur 15, paper 10, open 6  -> 96 kernel-checked, 91 not.
- Edge kinds: doc 320, direct 61, indirect 36. All 299 edges touching a research box are "doc" (a sentence in a document), none is checked.
- Group sizes: res 54, dep 31, eng 20, rec 18, lim 16, bnd 14, gpu 11, cov 8, ff 8, law 7.
- New since 23 Nov: 51 boxes, of which 31 are the cover-depth group (dep) — 61% of all new work.
- Source consistency: cur_res_edges 167/167 in data; cur_edges_lean 63/66 (3 in E_DROP, intended); cur_edges_lean5 42/42; spec_lean 95 nodes = the 95 lean boxes except s_parity (status lean, group res, no spec entry: a research summary carrying the kernel colour).

## Target set T (17 boxes: the 200-digit record search and its forecasts)
RECORD: r_160357 r_158209 r_earlier e_fleet200 e_rec160357 e_fleetnow e_records
FORECAST: m_ceiling m_price m_portfolio m_designmenu m_rowsabove m_staircase m_floor m_floorpred m_rounding m_doors
- premises of T (transitive): 85 boxes (lean 54, comp 21, paper 5, heur 3, open 1, leanhyp 1)
- NOT premises of T: 85 boxes. Of these 15 only consume T; 70 are neither premise nor consumer of any T box:
  res 22, dep 15, lim 11, ff 8 (all of ff), bnd 7, rec 4, cov 1, law 1, eng 1; by status lean 36, comp 22, heur 6, paper 5, open 1; 20 of them are new since 23 Nov.
- Of the 51 new boxes, 26 feed T, 20 are disconnected in both directions, 5 only consume.

## The "10% verdict" (m_portfolio, m_designmenu, m_floor): 58 premises
heur 5: m_h1, m_ceiling, d_law, d_recursion, m_floorpred; comp 16; lean 37; paper 0; open 0.
Choke point: every one of m_ceiling, m_price, m_portfolio, m_designmenu, m_rowsabove, m_rounding goes through m_density -> m_h1.
m_ceiling's entire ancestry is 4 boxes: m_density, m_h1, c_kills, c_thinning.
The validation boxes (t_calib, t_joint, t_tail, t_data, m_lgs) are NOT ancestors: they point at the model ("tests H1"), so the dependency graph shows the verdict resting on a heuristic with no evidence under it; the evidence hangs off as sinks.
The current facts are NOT ancestors either: r_160357 (users: only e_rec160357), e_rec160357 (sink), e_fleetnow (sink). The forecast boxes do not depend on the fleet's actual state; e_fleetnow>m_price is labelled "3.7x faster than priced" and e_fleetnow>m_portfolio "budget now smaller" — contradiction edges drawn as dependence.

## Soft spots (non-kernel boxes ranked by transitive dependents) — top
72 m_h1 (heur)  | 55 m_density (comp) | 43 e_cover_opt (comp) | 34 e_gpu | 34 m_selection | 32 e_selective | 28 e_cap200 | 27 e_fleet200 | 27 m_classical (paper) | 26 d_search | 24 d_table | 22 d_law (heur) | 20 m_ceiling (heur) | 20 m_bls (paper) | 18 m_price | 17 m_portfolio | 15 d_recursion (heur) | 13 m_h2 (open) | 12 s_prize | 12 e_c15907
- 72 of 187 boxes (62 of the 91 non-kernel boxes) have H1 as a premise.
- 47 of 60 "computed or measured" boxes and 5 of 10 "paper" boxes rest on at least one heur/open box; the evidence lens colours a box by its own kind, not its weakest premise.
- 10 Lean boxes "rely on" research boxes (8 L->R doc edges: provenance, e.g. r_160357>e_fleet200 "data from the fleet"; c_hits>m_h1 "assumes independence").

## Sinks: 30 boxes nobody relies on (res 10, dep 7, eng 5, bnd 3, rec 3, ff 2)
See list in raw output. Notable: m_designmenu, e_fleetnow, e_rec160357, m_doors, s_verdict (13 inputs, 0 users), m_lgs, d_capacity, d_prefixcheck, d_coversbig, d_reach, d_end89, d_g0exact, e_t5, e_dualcpu, e_fermatw, t_tail, t_budget, t_props, m_errata.

## Work not feeding T, by theme (70 disconnected + 15 consumer-only)
- Cover-depth asymptotics (dep): 15 of 31 — d_limit, d_nibble, d_pairproof, d_block, d_prefix, d_prefixcheck, d_capacity, d_limitcheck, d_greedy, d_reach, d_end89, d_g0exact, d_bounds, d_841, d_coversbig. Includes ALL of the consultant's own 25-Nov mathematics.
- Search-limit / barrier theorems: lim 11 of 16 + res barriers s_crt s_lattice s_mitm s_score s_lists m_wp3 m_toycrt m_mapshare m_budgets = 20 (they feed s_verdict, which is itself a sink).
- Function-field toy: ff 8 of 8 + s_parity s_ffsearch s_nonanalogy = 11.
- Asymptotic bounds: bnd 7 of 14 + m_thm1 m_thm2 m_lower = 10.
- Exhaustive statistics (student): t_data t_calib t_joint t_archip t_ml (+ t_props t_tail t_budget consumer-only) = 8 of 8.
- Other games: e_dual e_dualcpu e_t5 e_fermatw (consumer-only/disconnected); A025018 generator r_gen r_walk r_ranksieve r_rank x_bitsieve.
- Meta: m_errata, m_wp10, m_proofcarrying, v_brainstorm, m_lgs.

## Cross-group coupling
dep group: 70 internal edges; to it from res/eng only 7 edges (m_floor>d_law, m_floor>d_ub89, m_floorpred>d_recursion, m_rowsabove>d_families, + e_*); the depth theory touches the forecast through 3 boxes (d_law, d_recursion, d_families), all heur/comp.
res->lim 24 edges, all via s_* barrier boxes; ff has 4 inbound edges from res, 0 from eng/rec.

## Absences (no box at all)
Keyword scan over all box text (title+gist+detail+note) and GAPS_MAP.md:
- "goal": 0 boxes, 0 lines. "decision": 0/0. "recommend": 0/0. "priority": 0/0. "risk": 0/0. "deadline", "dollar", "cost of", "opportunity": 0.
- "user": 1 box (r_rank, unrelated). No box for what the user wants, who chose 200 digits or 10%, or why.
- Budget in units: only inside e_fleetnow detail ("7,967.7 compute units at 37.12 an hour (the 1,800-unit mark in 6.9 days)") and e_491; no box, and no forecast box depends on it.
- Alternatives in digit size: "250 digit", "1000 digit", "10^300", "why 200": 0. Only e_dual (heur, new, 2 dependants both sinks) prices other sizes; it is a consumer of m_ceiling, not an input to any plan box.
- No box for: the stopping rule; what counts as success (10% is called a "stretch target" inside r_160357); variance/luck of the forecast as an object ("variance" 1 box, unrelated); the near-miss mechanism as a strategy (the last two records were near-misses, mentioned in 9 boxes, owned by none); the sessions themselves (lead, fleet, spy, student) and who decides; negative results of the fleet (0 design hits against 0.41 expected) as evidence about the model; what is NOT mapped ("unmapped"/"unknown" 0).
- Edge types absent: "contradicts", "tests", "supersedes", "decides". All are drawn as "relies on".

---- RAW out.txt ----
nodes 187 edges 417 dangling [] selfloops []
nodes on cycles 0 []
mutual pairs []

## group x status
group lean leanhyp paper comp heur open total
rec 18 0 0 0 0 0 18
cov 8 0 0 0 0 0 8
dep 13 0 2 10 6 0 31
bnd 13 1 0 0 0 0 14
law 7 0 0 0 0 0 7
lim 16 0 0 0 0 0 16
ff 8 0 0 0 0 0 8
gpu 11 0 0 0 0 0 11
res 1 0 8 31 8 6 54
eng 0 0 0 19 1 0 20

## group x impact
group record engine bound steer aside
rec 6 8 0 1 3
cov 0 7 0 0 1
dep 0 1 23 6 1
bnd 0 0 6 0 8
law 0 3 4 0 0
lim 0 0 13 3 0
ff 0 5 0 3 0
gpu 0 9 0 0 2
res 0 3 17 29 5
eng 6 10 0 4 0

## status x impact
lean 6 32 32 10 15
leanhyp 0 0 1 0 0
paper 0 2 8 0 0
comp 6 11 16 23 4
heur 0 0 6 9 0
open 0 1 0 4 1

## edges between groups (from relies on to)
from\to rec cov dep bnd law lim ff gpu res eng
rec 21 11 0 0 0 0 0 0 0 7
cov 0 4 0 0 1 0 0 0 0 0
dep 5 3 70 4 2 1 0 0 7 3
bnd 0 7 2 7 0 0 0 0 0 0
law 0 0 0 0 2 0 0 0 0 0
lim 0 0 1 0 1 3 0 0 1 0
ff 0 0 0 0 0 0 7 0 0 0
gpu 3 0 0 0 0 0 0 8 0 0
res 5 7 5 4 5 24 4 0 106 16
eng 1 0 2 0 3 0 0 8 17 29
lean/research edge mix Counter({'R->R': 211, 'L->L': 110, 'R->L': 88, 'L->R': 8})
edge kind by mix Counter({('doc', 'R->R'): 211, ('doc', 'R->L'): 88, ('direct', 'L->L'): 61, ('indirect', 'L->L'): 36, ('doc', 'L->L'): 13, ('doc', 'L->R'): 8})

## top degree
19 2 m_density [res/comp/steer] Cost model: E = |U| · boost / ln N
13 2 e_cover_opt [eng/comp/engine] Cover design: greedy, annealing, parallel tempering
14 0 l_isleast [cov/lean/engine] Definition: least Goldbach summand g(N)
0 13 s_verdict [res/open/steer] Sublinear verdict so far: none known, none ruled out
7 5 e_fleet200 [eng/comp/record] The 200-digit fleet campaign (budget game)
10 1 d_def [dep/lean/steer] Cover depth D(n): how far a set of moduli can strike the primes
6 5 m_thm1 [res/paper/bound] Theorem: covers reach 1.349 · x · ln x
7 3 d_depthform [dep/lean/bound] The covering bound in depth form: covers exist up to 1.349 · y ln y
6 4 d_law [dep/heur/steer] The number of complete covers: ln g0 = θ(x) − c·Q/ln² x, with c near 1
6 3 e_gpu [eng/comp/engine] GPU Fermat engines
8 1 m_h1 [res/heur/steer] H1: the leftover rows are independent
3 6 m_classical [res/paper/engine] Thesis chapter 2: the classical constructions
5 4 s_prize [res/comp/steer] What a perfect search would be worth
4 5 s_score [res/comp/bound] Barrier: linear-time scoring is optimal
1 8 s_ladder [res/open/steer] The sublinear programme's ladder
5 4 d_recursion [dep/heur/steer] The law derived: a price per alive row, with the spread from Hardy–Littlewood pa
3 5 d_bounds [dep/lean/bound] What the depth says about g(N): an upper bound, Goldbach by covering, a lower bo
6 2 e_selective [eng/comp/steer] Selective testing: test only the emptiest members (the 3% rule)
3 5 s_lattice [res/comp/bound] Barrier: lattices and CRT with errors or lists
2 6 d_limit [dep/heur/bound] The limit of the cover depth: no limit is known. 1.1275 · r ln² r was withdrawn 

## SOFT SPOTS: non-lean boxes ranked by transitive dependents
72 8 m_h1 [res/heur/steer] H1: the leftover rows are independent {'comp': 42, 'lean': 10, 'heur': 11, 'open': 5, 'paper': 4}
55 19 m_density [res/comp/steer] Cost model: E = |U| · boost / ln N {'comp': 35, 'lean': 9, 'heur': 6, 'open': 5}
43 13 e_cover_opt [eng/comp/engine] Cover design: greedy, annealing, parallel tempering {'comp': 26, 'lean': 9, 'heur': 4, 'open': 4}
34 6 e_gpu [eng/comp/engine] GPU Fermat engines {'lean': 5, 'comp': 20, 'heur': 4, 'open': 5}
34 3 m_selection [res/comp/steer] Selection identity: where the successes sit {'comp': 21, 'lean': 5, 'heur': 4, 'open': 4}
32 6 e_selective [eng/comp/steer] Selective testing: test only the emptiest members (the 3% rule) {'comp': 19, 'lean': 5, 'heur': 4, 'open': 4}
28 2 e_cap200 [eng/comp/engine] The Lean session's cover experiments: 850 rows at Q = 122,000 {'lean': 5, 'comp': 15, 'heur': 4, 'open': 4}
27 7 e_fleet200 [eng/comp/record] The 200-digit fleet campaign (budget game) {'lean': 5, 'comp': 14, 'heur': 4, 'open': 4}
27 3 m_classical [res/paper/engine] Thesis chapter 2: the classical constructions {'comp': 10, 'lean': 2, 'open': 5, 'paper': 6, 'heur': 4}
26 2 d_search [dep/comp/engine] The exact search for D(n): one lemma, several cuts {'comp': 15, 'heur': 9, 'open': 1, 'paper': 1}
24 3 d_table [dep/comp/bound] Exact cover depth D(n) for up to 35 moduli {'comp': 13, 'heur': 9, 'open': 1, 'paper': 1}
22 6 d_law [dep/heur/steer] The number of complete covers: ln g0 = θ(x) − c·Q/ln² x, with c near 1 {'comp': 12, 'heur': 8, 'open': 1, 'paper': 1}
20 4 m_ceiling [res/heur/steer] Heuristic ceiling: about 2.13 million at 200 digits {'comp': 12, 'heur': 5, 'open': 3}
20 4 m_bls [res/paper/engine] N − 1 (BLS) certificate by CRT: no ECPP {'lean': 2, 'comp': 8, 'open': 5, 'paper': 2, 'heur': 3}
18 5 m_price [res/comp/steer] Price list: what raising the target costs {'heur': 4, 'comp': 11, 'open': 3}
17 4 m_portfolio [res/comp/steer] What the remaining budget buys {'heur': 4, 'comp': 10, 'open': 3}
15 5 d_recursion [dep/heur/steer] The law derived: a price per alive row, with the spread from Hardy–Littlewood pa {'heur': 7, 'comp': 6, 'open': 1, 'paper': 1}
13 4 m_h2 [res/open/steer] H2: no compositeness test cheaper than one exponentiation {'heur': 4, 'open': 4, 'comp': 2, 'paper': 3}
12 5 e_c15907 [eng/comp/engine] Complete covers: 15,907 on 89 primes, 16,747 on 92 {'lean': 4, 'open': 1, 'comp': 5, 'heur': 2}
12 5 s_prize [res/comp/steer] What a perfect search would be worth {'open': 2, 'comp': 6, 'heur': 4}
12 2 e_fscan [eng/comp/engine] fscan and tscan: CPU scanners for the low end {'comp': 7, 'open': 2, 'lean': 3}
11 1 m_lower [res/paper/bound] Unconditional growth: g ≫ ln N · ln₂N · ln₄N / ln₃N {'heur': 3, 'comp': 3, 'paper': 4, 'open': 1}
10 6 m_thm1 [res/paper/bound] Theorem: covers reach 1.349 · x · ln x {'heur': 3, 'comp': 3, 'paper': 3, 'open': 1}
9 3 m_wp10 [res/comp/aside] A proof of RH/GRH would move no lever {'heur': 2, 'open': 4, 'comp': 1, 'paper': 2}
9 2 e_verify [eng/comp/engine] Verification: three independent legs {'lean': 2, 'comp': 5, 'open': 1, 'heur': 1}
8 3 e_height [eng/comp/record] Height game: 1.2 million to 10 million, no ECPP {'lean': 2, 'comp': 4, 'open': 1, 'heur': 1}
8 2 d_families [dep/comp/steer] Complete covers sit in a few families fixed by the smallest moduli {'heur': 3, 'comp': 4, 'paper': 1}
8 2 m_floorpred [res/heur/steer] The same calculation above the end predicts how few rows a cover can leave {'open': 1, 'comp': 4, 'heur': 3}
7 7 t_data [res/comp/aside] Exhaustive g(N) near 10^12, 10^15 and 10^18 {'comp': 7}
7 4 m_wp7 [res/comp/bound] Five probes of non-covering mechanisms all end {'comp': 1, 'open': 1, 'paper': 3, 'heur': 2}
6 3 m_wp3 [res/heur/bound] Decoding barrier: sub-100 digits is brute force or nothing {'comp': 3, 'open': 3}
6 3 d_greedy [dep/comp/bound] Plain greedy reaches 0.72 · x ln² x, four to seven times the proved constant {'heur': 2, 'comp': 2, 'paper': 2}
6 2 d_ub89 [dep/comp/bound] At the campaign's size: 15,907 ≤ D(89) < 35,000, and a floor of 777 rows {'open': 1, 'comp': 3, 'heur': 2}
5 4 s_score [res/comp/bound] Barrier: linear-time scoring is optimal {'comp': 3, 'open': 2}
5 2 e_threshold [eng/comp/record] Threshold game: from 186 down to 150 digits, and the low end {'lean': 3, 'comp': 2}
5 2 m_thm2 [res/paper/bound] Theorem: no cover beyond x^(4+ε) {'heur': 2, 'comp': 1, 'open': 1, 'paper': 1}
5 2 d_limitcheck [dep/comp/bound] A referee's check of the research limit 1.1275 {'heur': 3, 'comp': 1, 'paper': 1}
4 4 d_prefix [dep/heur/bound] The recursion with the entropy of the small moduli put in: the ends move by 1 to {'heur': 2, 'paper': 1, 'comp': 1}
4 3 m_floor [res/comp/steer] A measured floor under every cover: 1,214 rows at 170,000 against the best known {'heur': 2, 'comp': 1, 'open': 1}
4 2 m_budgets [res/comp/steer] Two budgets: nats of modulus and nats of work {'comp': 1, 'open': 3}
4 2 d_nibble [dep/heur/bound] Why 1.349 is not the truth: pairs, deletion and the nibble {'paper': 2, 'heur': 1, 'comp': 1}
4 1 e_megagap [eng/comp/record] The 2,692-digit megagap: g = 1,134,871 {'lean': 2, 'comp': 2}
4 1 m_lemma2 [res/paper/bound] Lemma: a shared divisor divides q₁ − q₂ {'heur': 2, 'paper': 1, 'open': 1}
4 1 m_entropy [res/paper/bound] Planted certificates cost at least covering's marginal price {'heur': 2, 'paper': 1, 'open': 1}
4 1 m_falsify [res/comp/bound] Falsification engine: 13,661 instances, zero passes {'heur': 2, 'paper': 1, 'open': 1}
4 1 m_toycrt [res/comp/bound] Toy CRT decoder: LLL stops at the Johnson radius {'comp': 2, 'open': 2}
3 3 s_lattice [res/comp/bound] Barrier: lattices and CRT with errors or lists {'comp': 1, 'open': 2}
3 3 s_mitm [res/comp/bound] Barrier: meet in the middle, birthday trees, hashing {'comp': 1, 'open': 2}
3 2 m_closure [res/paper/bound] Divisor-Paradigm Closure Theorem {'heur': 2, 'open': 1}
3 2 d_limit [dep/heur/bound] The limit of the cover depth: no limit is known. 1.1275 · r ln² r was withdrawn  {'heur': 1, 'paper': 1, 'comp': 1}
3 2 e_491 [eng/comp/engine] A better 89th prime: 491 in place of 463, and the covers behind the record {'comp': 3}
3 1 e_records [eng/comp/record] Record board: three games {'lean': 2, 'comp': 1}
3 1 v_brainstorm [res/comp/steer] The 200-idea brainstorm: nothing worth a nat {'open': 3}
3 1 d_pairproof [dep/paper/bound] A draft proof of a constant above 1.349: one prime striking two rows {'heur': 1, 'paper': 1, 'comp': 1}
2 2 m_rounding [res/comp/steer] Door 1: the rounding gap {'heur': 2}
2 2 s_question [res/open/steer] The sublinear search question (P′) {'open': 2}
2 2 s_crt [res/comp/bound] Barrier: free coordinates stop at the cap {'comp': 1, 'open': 1}
2 2 s_ffsearch [res/comp/steer] Toy search over F₃[x]: the parity filter is worth 4–5× {'open': 2}
2 2 m_rowsabove [res/comp/steer] Rows above the design level decide the final record: families A and B {'comp': 2}
2 2 e_dual [eng/heur/steer] The other direction: a fixed gap and the fewest digits {'comp': 2}
2 2 d_block [dep/paper/bound] A structured prefix beats random classes: D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)² {'heur': 1, 'comp': 1}
2 1 t_calib [res/comp/steer] Tested: the chance that every row is composite {'comp': 2}
2 1 t_joint [res/comp/steer] Tested: pairs of neighbours at 366 lags {'comp': 2}
1 1 m_staircase [res/heur/steer] Operation Staircase: a compute ladder to 200,000 {'heur': 1}
1 1 s_lists [res/comp/bound] Barrier: list gain above Q is tiny {'open': 1}
1 1 s_nonanalogy [res/heur/bound] Why the integers are harder: a known non-analogy {'open': 1}
1 1 s_ladder [res/open/steer] The sublinear programme's ladder {'open': 1}
1 1 t_archip [res/comp/aside] Archipelagos: big gaps come in clusters {'comp': 1}
1 1 t_ml [res/comp/steer] Tested: no score beats the survivor count {'comp': 1}
1 1 m_mapshare [res/comp/bound] Neighbouring N share the prime map, but that excludes a cover {'open': 1}
1 1 e_sievechain [eng/comp/engine] The GPU sieve chain: a window's sieve phase from 83.7 to 44 ms {'comp': 1}
0 0 m_doors [res/heur/steer] Three doors: mathematics, compute, paradigm {}
0 0 m_proofcarrying [res/open/engine] Proof-carrying records: proposed, then delivered {}
0 0 m_errata [res/open/aside] Retractions and errata {}
0 0 s_miniature [res/comp/steer] Exact miniature: N below 10^9, Q = 1,000 {}
0 0 s_verdict [res/open/steer] Sublinear verdict so far: none known, none ruled out {}
0 0 t_props [res/comp/aside] Who the big numbers are {}
0 0 t_tail [res/comp/steer] Tested: the records of each window {}
0 0 t_budget [res/comp/steer] Tested: what a sieve can know {}
0 0 d_reach [dep/comp/bound] Best complete covers known: 0.78 to 0.88 · x ln² x on 30 to 302 moduli {}
0 0 d_end89 [dep/comp/bound] Pure covers on the 89 moduli end near 16,000 {}
0 0 d_g0exact [dep/comp/steer] Exact counts of covers for up to ten moduli {}
0 0 m_lgs [res/heur/steer] A model with no primes in it reproduces the campaign's ceiling {}
0 0 m_designmenu [res/comp/steer] What each design level buys, and the expected final record {}
0 0 e_rec160357 [eng/comp/record] How 160,357 was found and certified {}
0 0 e_fleetnow [eng/comp/steer] The fleet now: its pace, Colab's limits and what is left {}
0 0 e_fermatw [eng/comp/engine] IFMA Fermat tests for 300 to 400 digits (8 to 12 times gmpy2) {}
0 0 e_dualcpu [eng/comp/engine] The fixed-gap game on a processor: hours per hit {}
0 0 e_t5 [eng/comp/steer] A cover for g ≥ 10^6 on 629 moduli: 3,028 rows left {}
0 0 d_prefixcheck [dep/comp/bound] A referee's second read of the entropy of the small moduli {}
0 0 d_capacity [dep/heur/bound] A capacity bound for the top primes: each strikes about ln x/ln ln x rows (for c {}

## same but only heur/open/paper (unverified by computation)
72 8 m_h1 [res/heur/steer] H1: the leftover rows are independent
27 3 m_classical [res/paper/engine] Thesis chapter 2: the classical constructions
22 6 d_law [dep/heur/steer] The number of complete covers: ln g0 = θ(x) − c·Q/ln² x, with c near 1
20 4 m_ceiling [res/heur/steer] Heuristic ceiling: about 2.13 million at 200 digits
20 4 m_bls [res/paper/engine] N − 1 (BLS) certificate by CRT: no ECPP
15 5 d_recursion [dep/heur/steer] The law derived: a price per alive row, with the spread from Hardy–Littlewood pa
13 4 m_h2 [res/open/steer] H2: no compositeness test cheaper than one exponentiation
11 1 m_lower [res/paper/bound] Unconditional growth: g ≫ ln N · ln₂N · ln₄N / ln₃N
10 6 m_thm1 [res/paper/bound] Theorem: covers reach 1.349 · x · ln x
8 2 m_floorpred [res/heur/steer] The same calculation above the end predicts how few rows a cover can leave
6 3 m_wp3 [res/heur/bound] Decoding barrier: sub-100 digits is brute force or nothing
5 2 m_thm2 [res/paper/bound] Theorem: no cover beyond x^(4+ε)
4 4 d_prefix [dep/heur/bound] The recursion with the entropy of the small moduli put in: the ends move by 1 to
4 2 d_nibble [dep/heur/bound] Why 1.349 is not the truth: pairs, deletion and the nibble
4 1 m_lemma2 [res/paper/bound] Lemma: a shared divisor divides q₁ − q₂
4 1 m_entropy [res/paper/bound] Planted certificates cost at least covering's marginal price
3 2 m_closure [res/paper/bound] Divisor-Paradigm Closure Theorem
3 2 d_limit [dep/heur/bound] The limit of the cover depth: no limit is known. 1.1275 · r ln² r was withdrawn 
3 1 d_pairproof [dep/paper/bound] A draft proof of a constant above 1.349: one prime striking two rows
2 2 s_question [res/open/steer] The sublinear search question (P′)
2 2 e_dual [eng/heur/steer] The other direction: a fixed gap and the fewest digits
2 2 d_block [dep/paper/bound] A structured prefix beats random classes: D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)²
1 1 m_staircase [res/heur/steer] Operation Staircase: a compute ladder to 200,000
1 1 s_nonanalogy [res/heur/bound] Why the integers are harder: a known non-analogy
1 1 s_ladder [res/open/steer] The sublinear programme's ladder
0 0 m_doors [res/heur/steer] Three doors: mathematics, compute, paradigm
0 0 m_proofcarrying [res/open/engine] Proof-carrying records: proposed, then delivered
0 0 m_errata [res/open/aside] Retractions and errata
0 0 s_verdict [res/open/steer] Sublinear verdict so far: none known, none ruled out
0 0 m_lgs [res/heur/steer] A model with no primes in it reproduces the campaign's ceiling
0 0 d_capacity [dep/heur/bound] A capacity bound for the top primes: each strikes about ln x/ln ln x rows (for c

## lean boxes resting (transitively) on non-lean boxes
c_hits [lim/lean/steer] Expected successes = Σ (1 − p)^(rows left) <- ['m_h1']
r_158209 [rec/lean/record] Record: g(N) = 158,209 for a 200-digit N <- ['m_h1', 'e_cover_opt', 'm_density', 'e_selective', 'e_cap200', 'm_selection', 'e_gpu', 'e_fleet200']
r_earlier [rec/lean/record] Earlier records: 104,527 up to 157,837 <- ['m_h1', 'e_cover_opt', 'm_density', 'e_selective', 'e_fscan', 'e_threshold', 'e_cap200', 'm_selection', 'e_gpu', 'e_fleet200']
r_cover15907 [rec/lean/record] Pure cover: no prime below 15,907 is a summand <- ['m_h1', 'e_cover_opt', 'e_c15907', 'm_density']
r_family [rec/lean/record] A family of 21,378,978 covered numbers <- ['m_h1', 'e_cover_opt', 'e_c15907', 'm_density']
r_rank [rec/lean/aside] Record holders up to 10^12, and the shift law <- ['m_h1', 'e_megagap', 'e_cover_opt', 'e_verify', 'm_density', 'e_selective', 'e_fscan', 'e_threshold', 'e_cap200', 'm_classical', 'm_selection', 'e_gpu', 'e_height', 'm_bls', 'e_records', 'e_fleet200']
r_cover_more [rec/lean/record] Longer pure covers on 91 to 93 primes <- ['m_h1', 'e_cover_opt', 'e_c15907', 'm_density']
r_160357 [rec/lean/record] Record: g(N) = 160,357 for a 200-digit N <- ['m_h1', 'e_cover_opt', 'm_density', 'e_selective', 'e_cap200', 'm_selection', 'e_gpu', 'e_fleet200']
r_ranksieve [rec/lean/aside] Goldbach below 2^25, and its 26 record holders, proved in the kernel <- ['m_h1', 'e_megagap', 'e_cover_opt', 'e_verify', 'm_density', 'e_selective', 'e_fscan', 'e_threshold', 'e_cap200', 'm_classical', 'm_selection', 'e_gpu', 'e_height', 'm_bls', 'e_records', 'e_fleet200']
d_records [dep/lean/bound] The 200-digit pure covers are depth lower bounds: 89 to 93 moduli reach 16,981 <- ['m_h1', 'e_cover_opt', 'e_c15907', 'm_density']

## sinks (nobody relies on it): in=0
30 Counter({'res': 10, 'dep': 7, 'eng': 5, 'bnd': 3, 'rec': 3, 'ff': 2}) Counter({'comp': 14, 'lean': 10, 'heur': 3, 'open': 3})
   2 l_unbounded [bnd/lean/aside] g(N) is unbounded
   3 l_cb073 [bnd/lean/bound] Covering bound, unconditional: c = 0.73
   2 l_cb12 [bnd/lean/bound] Covering bound with explicit constant c = 1.2
   6 r_earlier [rec/lean/record] Earlier records: 104,527 up to 157,837
   2 r_family [rec/lean/record] A family of 21,378,978 covered numbers
   1 f_resultant [ff/lean/engine] Discriminant of N − Q as a resultant
   1 f_degree [ff/lean/steer] The desert, for J ≥ 1, in clean form
   2 r_ranksieve [rec/lean/aside] Goldbach below 2^25, and its 26 record holders, proved in the kernel
   3 d_841 [dep/lean/aside] Goldbach below 961 by covering alone
   2 d_coversbig [dep/lean/bound] Pure covers on 429 and 1,228 primes: 135,511 and 614,101
   4 m_doors [res/heur/steer] Three doors: mathematics, compute, paradigm
   3 m_proofcarrying [res/open/engine] Proof-carrying records: proposed, then delivered
   5 m_errata [res/open/aside] Retractions and errata
   4 s_miniature [res/comp/steer] Exact miniature: N below 10^9, Q = 1,000
   13 s_verdict [res/open/steer] Sublinear verdict so far: none known, none ruled out
   4 t_props [res/comp/aside] Who the big numbers are
   3 t_tail [res/comp/steer] Tested: the records of each window
   3 t_budget [res/comp/steer] Tested: what a sieve can know
   3 d_reach [dep/comp/bound] Best complete covers known: 0.78 to 0.88 · x ln² x on 30 to 302 moduli
   4 d_end89 [dep/comp/bound] Pure covers on the 89 moduli end near 16,000
   3 d_g0exact [dep/comp/steer] Exact counts of covers for up to ten moduli
   6 m_lgs [res/heur/steer] A model with no primes in it reproduces the campaign's ceiling
   3 m_designmenu [res/comp/steer] What each design level buys, and the expected final record
   6 e_rec160357 [eng/comp/record] How 160,357 was found and certified
   3 e_fleetnow [eng/comp/steer] The fleet now: its pace, Colab's limits and what is left
   1 e_fermatw [eng/comp/engine] IFMA Fermat tests for 300 to 400 digits (8 to 12 times gmpy2)
   2 e_dualcpu [eng/comp/engine] The fixed-gap game on a processor: hours per hit
   4 e_t5 [eng/comp/steer] A cover for g ≥ 10^6 on 629 moduli: 3,028 rows left
   2 d_prefixcheck [dep/comp/bound] A referee's second read of the entropy of the small moduli
   7 d_capacity [dep/heur/bound] A capacity bound for the top primes: each strikes about ln x/ln ln x rows (for c

## sources/axioms (relies on nothing): out=0
38 Counter({'lim': 10, 'cov': 5, 'bnd': 5, 'law': 5, 'rec': 4, 'gpu': 4, 'res': 3, 'ff': 2}) Counter({'lean': 35, 'open': 1, 'heur': 1, 'comp': 1})
   4 m_h2 [res/open/steer] H2: no compositeness test cheaper than one exponentiation
   3 m_wp3 [res/heur/bound] Decoding barrier: sub-100 digits is brute force or nothing
   7 t_data [res/comp/aside] Exhaustive g(N) near 10^12, 10^15 and 10^18
isolated []

## TARGET 17
premises of T (T relies on, transitively): 85 Counter({'lean': 54, 'comp': 21, 'paper': 5, 'heur': 3, 'open': 1, 'leanhyp': 1}) Counter({'dep': 16, 'res': 12, 'eng': 12, 'gpu': 11, 'rec': 9, 'bnd': 7, 'cov': 7, 'law': 6, 'lim': 5})
consumers of T only: 15
both 1
NOT premises of T: 85 Counter({'res': 32, 'dep': 15, 'lim': 11, 'ff': 8, 'bnd': 7, 'rec': 6, 'eng': 4, 'cov': 1, 'law': 1}) Counter({'lean': 38, 'comp': 29, 'heur': 8, 'paper': 5, 'open': 5})
NEITHER premise nor consumer: 70 Counter({'res': 22, 'dep': 15, 'lim': 11, 'ff': 8, 'bnd': 7, 'rec': 4, 'cov': 1, 'law': 1, 'eng': 1}) Counter({'lean': 36, 'comp': 22, 'heur': 6, 'paper': 5, 'open': 1}) Counter({'old': 43, 'new': 20, 'upd': 7})
 -- rec 4 of 18
      r_family [rec/lean/record] A family of 21,378,978 covered numbers
      r_walk [rec/lean/steer] A record is a cover: the exact test for "N beats G"
      r_gen [rec/lean/aside] A generator for A025018, proved correct, that runs forever exactly if Goldbach h
      x_bitsieve [rec/lean/engine] A prime sieve on bitmasks that the kernel can run
 -- cov 1 of 8
      c_cover_cap [cov/lean/engine] From a cover to a number below a cap
 -- dep 15 of 31
      d_bounds [dep/lean/bound] What the depth says about g(N): an upper bound, Goldbach by covering, a lower bo
      d_841 [dep/lean/aside] Goldbach below 961 by covering alone
      d_coversbig [dep/lean/bound] Pure covers on 429 and 1,228 primes: 135,511 and 614,101
      d_greedy [dep/comp/bound] Plain greedy reaches 0.72 · x ln² x, four to seven times the proved constant
      d_reach [dep/comp/bound] Best complete covers known: 0.78 to 0.88 · x ln² x on 30 to 302 moduli
      d_end89 [dep/comp/bound] Pure covers on the 89 moduli end near 16,000
      d_limit [dep/heur/bound] The limit of the cover depth: no limit is known. 1.1275 · r ln² r was withdrawn 
      d_nibble [dep/heur/bound] Why 1.349 is not the truth: pairs, deletion and the nibble
      d_g0exact [dep/comp/steer] Exact counts of covers for up to ten moduli
      d_limitcheck [dep/comp/bound] A referee's check of the research limit 1.1275
      d_pairproof [dep/paper/bound] A draft proof of a constant above 1.349: one prime striking two rows
      d_block [dep/paper/bound] A structured prefix beats random classes: D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)²
      d_prefixcheck [dep/comp/bound] A referee's second read of the entropy of the small moduli
      d_prefix [dep/heur/bound] The recursion with the entropy of the small moduli put in: the ends move by 1 to
      d_capacity [dep/heur/bound] A capacity bound for the top primes: each strikes about ln x/ln ln x rows (for c
 -- bnd 7 of 14
      l_unbounded [bnd/lean/aside] g(N) is unbounded
      l_counting [bnd/lean/bound] Counting bound: some N has no small summand
      l_consts [bnd/lean/aside] Explicit constants: C₂ and e^−γ
      l_mertensUpper [bnd/lean/aside] Elementary Mertens-type upper bound (κ = 1.367)
      l_cb073 [bnd/lean/bound] Covering bound, unconditional: c = 0.73
      l_cb12 [bnd/lean/bound] Covering bound with explicit constant c = 1.2
      l_cb_sharp [bnd/lean/bound] Covering bound, sharp: c < e^γ/(2C₂) = 1.349…
 -- law 1 of 7
      c_smooth [law/lean/engine] What survives a fixed layer is smooth or nearly
 -- lim 11 of 16
      c_lattice [lim/lean/bound] Lattice decoding radius
      c_deficit [lim/lean/bound] Partial information costs more than it earns
      c_johnson [lim/lean/bound] Inside the Johnson radius only the cover is left
      c_blackbox [lim/lean/bound] Black-box bound: no free search
      c_population [lim/lean/bound] No selection beats the population
      c_fewrows [lim/lean/bound] Few rows left is rare
      c_mitm [lim/lean/bound] Meet-in-the-middle price
      c_listgain [lim/lean/bound] One prime buys few rows
      c_listgain_q [lim/lean/bound] Above Q no list pays
      c_brainstorm [lim/lean/bound] Brainstorm: what a kernel could decide among 100 ideas
      c_needles [lim/lean/bound] Needles closer than Q are not independent
 -- ff 8 of 8
      f_sw [ff/lean/engine] Stickelberger–Swan theorem over any finite field
      f_discr_sub [ff/lean/engine] Discriminant of N − Q when N has zero derivative
      f_parity [ff/lean/engine] Parity theorem for N − Q
      f_notirr [ff/lean/engine] Corollary: N − Q is reducible
      f_desert [ff/lean/steer] The function-field desert
      f_general [ff/lean/steer] The desert for every row of degree J + 1
      f_resultant [ff/lean/engine] Discriminant of N − Q as a resultant
      f_degree [ff/lean/steer] The desert, for J ≥ 1, in clean form
 -- gpu 0 of 11
 -- res 22 of 54
      m_budgets [res/comp/steer] Two budgets: nats of modulus and nats of work
      m_wp3 [res/heur/bound] Decoding barrier: sub-100 digits is brute force or nothing
      m_toycrt [res/comp/bound] Toy CRT decoder: LLL stops at the Johnson radius
      m_wp10 [res/comp/aside] A proof of RH/GRH would move no lever
      m_thm1 [res/paper/bound] Theorem: covers reach 1.349 · x · ln x
      m_thm2 [res/paper/bound] Theorem: no cover beyond x^(4+ε)
      m_lower [res/paper/bound] Unconditional growth: g ≫ ln N · ln₂N · ln₄N / ln₃N
      m_errata [res/open/aside] Retractions and errata
      s_crt [res/comp/bound] Barrier: free coordinates stop at the cap
      s_lattice [res/comp/bound] Barrier: lattices and CRT with errors or lists
      s_mitm [res/comp/bound] Barrier: meet in the middle, birthday trees, hashing
      s_score [res/comp/bound] Barrier: linear-time scoring is optimal
      s_lists [res/comp/bound] Barrier: list gain above Q is tiny
      s_parity [res/lean/steer] Function-field toy: a parity desert, formally proved
      s_ffsearch [res/comp/steer] Toy search over F₃[x]: the parity filter is worth 4–5×
      s_nonanalogy [res/heur/bound] Why the integers are harder: a known non-analogy
      t_data [res/comp/aside] Exhaustive g(N) near 10^12, 10^15 and 10^18
      t_calib [res/comp/steer] Tested: the chance that every row is composite
      t_joint [res/comp/steer] Tested: pairs of neighbours at 366 lags
      t_archip [res/comp/aside] Archipelagos: big gaps come in clusters
      t_ml [res/comp/steer] Tested: no score beats the survivor count
      m_mapshare [res/comp/bound] Neighbouring N share the prime map, but that excludes a cover
 -- eng 1 of 20
      e_fermatw [eng/comp/engine] IFMA Fermat tests for 300 to 400 digits (8 to 12 times gmpy2)
consumers-only (use T but T does not use them):
    e_t5 [eng/comp/steer] A cover for g ≥ 10^6 on 629 moduli: 3,028 rows left
    e_dualcpu [eng/comp/engine] The fixed-gap game on a processor: hours per hit
    e_dual [eng/heur/steer] The other direction: a fixed gap and the fewest digits
    r_rank [rec/lean/aside] Record holders up to 10^12, and the shift law
    r_ranksieve [rec/lean/aside] Goldbach below 2^25, and its 26 record holders, proved in the kernel
    s_question [res/open/steer] The sublinear search question (P′)
    m_proofcarrying [res/open/engine] Proof-carrying records: proposed, then delivered
    s_verdict [res/open/steer] Sublinear verdict so far: none known, none ruled out
    t_props [res/comp/aside] Who the big numbers are
    t_budget [res/comp/steer] Tested: what a sieve can know
    s_miniature [res/comp/steer] Exact miniature: N below 10^9, Q = 1,000
    m_lgs [res/heur/steer] A model with no primes in it reproduces the campaign's ceiling
    v_brainstorm [res/comp/steer] The 200-idea brainstorm: nothing worth a nat
    s_ladder [res/open/steer] The sublinear programme's ladder
    t_tail [res/comp/steer] Tested: the records of each window
undirected component of T 187 outside []

## premises of RECORD boxes : 71 {'lean': 46, 'comp': 19, 'paper': 2, 'heur': 3, 'leanhyp': 1} {'dep': 11, 'lim': 5, 'gpu': 11, 'eng': 11, 'res': 9, 'bnd': 7, 'rec': 7, 'law': 4, 'cov': 6}
   heur 3
       d_law [dep/heur/steer] The number of complete covers: ln g0 = θ(x) − c·Q/ln² x, with c near 1
       m_h1 [res/heur/steer] H1: the leftover rows are independent
       m_ceiling [res/heur/steer] Heuristic ceiling: about 2.13 million at 200 digits
   open 0
   paper 2
       m_classical [res/paper/engine] Thesis chapter 2: the classical constructions
       m_bls [res/paper/engine] N − 1 (BLS) certificate by CRT: no ECPP
   comp 19
       e_verify [eng/comp/engine] Verification: three independent legs
       m_density [res/comp/steer] Cost model: E = |U| · boost / ln N
       e_fscan [eng/comp/engine] fscan and tscan: CPU scanners for the low end
       e_cap200 [eng/comp/engine] The Lean session's cover experiments: 850 rows at Q = 122,000
       m_selection [res/comp/steer] Selection identity: where the successes sit
       e_gpu [eng/comp/engine] GPU Fermat engines
       m_portfolio [res/comp/steer] What the remaining budget buys
       e_height [eng/comp/record] Height game: 1.2 million to 10 million, no ECPP
       m_price [res/comp/steer] Price list: what raising the target costs
       d_table [dep/comp/bound] Exact cover depth D(n) for up to 35 moduli
       e_491 [eng/comp/engine] A better 89th prime: 491 in place of 463, and the covers behind the record
       d_families [dep/comp/steer] Complete covers sit in a few families fixed by the smallest moduli
       e_megagap [eng/comp/record] The 2,692-digit megagap: g = 1,134,871
       e_cover_opt [eng/comp/engine] Cover design: greedy, annealing, parallel tempering
       e_selective [eng/comp/steer] Selective testing: test only the emptiest members (the 3% rule)
       e_threshold [eng/comp/record] Threshold game: from 186 down to 150 digits, and the low end
       e_sievechain [eng/comp/engine] The GPU sieve chain: a window's sieve phase from 83.7 to 44 ms
       m_rowsabove [res/comp/steer] Rows above the design level decide the final record: families A and B
       d_search [dep/comp/engine] The exact search for D(n): one lemma, several cuts
   leanhyp 1
       l_linnik [bnd/leanhyp/bound] Effective size of N, assuming Linnik
   lean premises: ['c_budget', 'c_hardness', 'c_hits', 'c_kills', 'c_layers', 'c_nofree', 'c_pigeon', 'c_selection', 'c_thinning', 'c_tilt', 'c_transfer', 'd_count', 'd_count_lower', 'd_covers', 'd_def', 'd_depthform', 'd_exact', 'd_more', 'g_class', 'g_conv', 'g_f26', 'g_f30', 'g_f52', 'g_fermat2', 'g_fermat28', 'g_fermat28r', 'g_montsqr', 'g_sched', 'g_step28', 'l_cover', 'l_cover_exists', 'l_exists', 'l_gammaid', 'l_isleast', 'l_mertens1', 'l_mertens3', 'l_mertensconst', 'l_pnt', 'l_primorial', 'x_block', 'x_coveredin', 'x_ecmul', 'x_ecpp_group', 'x_ecpp_step', 'x_fermat', 'x_least']

## premises of FORECAST boxes : 63 {'lean': 40, 'open': 1, 'comp': 16, 'paper': 3, 'heur': 3} {'dep': 16, 'lim': 5, 'res': 10, 'gpu': 7, 'law': 6, 'bnd': 5, 'eng': 7, 'rec': 4, 'cov': 3}
   heur 3
       d_law [dep/heur/steer] The number of complete covers: ln g0 = θ(x) − c·Q/ln² x, with c near 1
       d_recursion [dep/heur/steer] The law derived: a price per alive row, with the spread from Hardy–Littlewood pa
       m_h1 [res/heur/steer] H1: the leftover rows are independent
   open 1
       m_h2 [res/open/steer] H2: no compositeness test cheaper than one exponentiation
   paper 3
       m_closure [res/paper/bound] Divisor-Paradigm Closure Theorem
       m_lemma2 [res/paper/bound] Lemma: a shared divisor divides q₁ − q₂
       m_entropy [res/paper/bound] Planted certificates cost at least covering's marginal price
   comp 16
       m_density [res/comp/steer] Cost model: E = |U| · boost / ln N
       e_cap200 [eng/comp/engine] The Lean session's cover experiments: 850 rows at Q = 122,000
       m_selection [res/comp/steer] Selection identity: where the successes sit
       e_gpu [eng/comp/engine] GPU Fermat engines
       e_c15907 [eng/comp/engine] Complete covers: 15,907 on 89 primes, 16,747 on 92
       d_ub89 [dep/comp/bound] At the campaign's size: 15,907 ≤ D(89) < 35,000, and a floor of 777 rows
       d_table [dep/comp/bound] Exact cover depth D(n) for up to 35 moduli
       e_491 [eng/comp/engine] A better 89th prime: 491 in place of 463, and the covers behind the record
       e_fleet200 [eng/comp/record] The 200-digit fleet campaign (budget game)
       d_families [dep/comp/steer] Complete covers sit in a few families fixed by the smallest moduli
       e_cover_opt [eng/comp/engine] Cover design: greedy, annealing, parallel tempering
       e_selective [eng/comp/steer] Selective testing: test only the emptiest members (the 3% rule)
       m_wp7 [res/comp/bound] Five probes of non-covering mechanisms all end
       s_prize [res/comp/steer] What a perfect search would be worth
       m_falsify [res/comp/bound] Falsification engine: 13,661 instances, zero passes
       d_search [dep/comp/engine] The exact search for D(n): one lemma, several cuts
   leanhyp 0
   lean premises: ['c_budget', 'c_hardness', 'c_hits', 'c_kills', 'c_layers', 'c_nofree', 'c_pigeon', 'c_poly', 'c_prime_moduli', 'c_selection', 'c_thinning', 'c_tilt', 'c_two_rows', 'd_count', 'd_count_lower', 'd_covers', 'd_def', 'd_depthform', 'd_exact', 'd_more', 'd_pairs', 'd_pairsums', 'd_records', 'g_conv', 'g_fermat2', 'g_fermat28', 'g_fermat28r', 'g_montsqr', 'g_sched', 'g_step28', 'l_cover', 'l_gammaid', 'l_mertens1', 'l_mertens3', 'l_mertensconst', 'l_pnt', 'r_cover15907', 'r_cover_more', 'x_coveredin', 'x_fermat']

## premises of 10% verdict (m_portfolio,m_designmenu,m_floor) : 58 {'lean': 37, 'heur': 5, 'comp': 16} {'dep': 16, 'lim': 5, 'res': 8, 'rec': 4, 'eng': 7, 'bnd': 5, 'gpu': 7, 'law': 4, 'cov': 2}
   heur 5
       m_h1 [res/heur/steer] H1: the leftover rows are independent
       d_law [dep/heur/steer] The number of complete covers: ln g0 = θ(x) − c·Q/ln² x, with c near 1
       d_recursion [dep/heur/steer] The law derived: a price per alive row, with the spread from Hardy–Littlewood pa
       m_ceiling [res/heur/steer] Heuristic ceiling: about 2.13 million at 200 digits
       m_floorpred [res/heur/steer] The same calculation above the end predicts how few rows a cover can leave
   open 0
   paper 0
   comp 16
       e_cover_opt [eng/comp/engine] Cover design: greedy, annealing, parallel tempering
       m_density [res/comp/steer] Cost model: E = |U| · boost / ln N
       e_selective [eng/comp/steer] Selective testing: test only the emptiest members (the 3% rule)
       e_cap200 [eng/comp/engine] The Lean session's cover experiments: 850 rows at Q = 122,000
       s_prize [res/comp/steer] What a perfect search would be worth
       m_selection [res/comp/steer] Selection identity: where the successes sit
       e_gpu [eng/comp/engine] GPU Fermat engines
       d_ub89 [dep/comp/bound] At the campaign's size: 15,907 ≤ D(89) < 35,000, and a floor of 777 rows
       e_c15907 [eng/comp/engine] Complete covers: 15,907 on 89 primes, 16,747 on 92
       m_price [res/comp/steer] Price list: what raising the target costs
       m_rowsabove [res/comp/steer] Rows above the design level decide the final record: families A and B
       d_table [dep/comp/bound] Exact cover depth D(n) for up to 35 moduli
       d_search [dep/comp/engine] The exact search for D(n): one lemma, several cuts
       e_491 [eng/comp/engine] A better 89th prime: 491 in place of 463, and the covers behind the record
       e_fleet200 [eng/comp/record] The 200-digit fleet campaign (budget game)
       d_families [dep/comp/steer] Complete covers sit in a few families fixed by the smallest moduli
   leanhyp 0
   lean premises: ['c_budget', 'c_hardness', 'c_hits', 'c_kills', 'c_layers', 'c_nofree', 'c_pigeon', 'c_selection', 'c_thinning', 'c_tilt', 'd_count', 'd_count_lower', 'd_covers', 'd_def', 'd_depthform', 'd_exact', 'd_more', 'd_pairs', 'd_pairsums', 'd_records', 'g_conv', 'g_fermat2', 'g_fermat28', 'g_fermat28r', 'g_montsqr', 'g_sched', 'g_step28', 'l_cover', 'l_gammaid', 'l_mertens1', 'l_mertens3', 'l_mertensconst', 'l_pnt', 'r_cover15907', 'r_cover_more', 'x_coveredin', 'x_fermat']

## premises of r_160357 only : 31 {'lean': 23, 'heur': 1, 'comp': 7} {'lim': 4, 'res': 3, 'gpu': 7, 'eng': 5, 'law': 3, 'cov': 3, 'rec': 6}
   heur 1
       m_h1 [res/heur/steer] H1: the leftover rows are independent
   open 0
   paper 0
   comp 7
       e_cover_opt [eng/comp/engine] Cover design: greedy, annealing, parallel tempering
       e_gpu [eng/comp/engine] GPU Fermat engines
       m_density [res/comp/steer] Cost model: E = |U| · boost / ln N
       e_selective [eng/comp/steer] Selective testing: test only the emptiest members (the 3% rule)
       e_fleet200 [eng/comp/record] The 200-digit fleet campaign (budget game)
       e_cap200 [eng/comp/engine] The Lean session's cover experiments: 850 rows at Q = 122,000
       m_selection [res/comp/steer] Selection identity: where the successes sit
   leanhyp 0
   lean premises: ['c_budget', 'c_hits', 'c_kills', 'c_nofree', 'c_pigeon', 'c_selection', 'c_thinning', 'c_tilt', 'g_conv', 'g_fermat2', 'g_fermat28', 'g_fermat28r', 'g_montsqr', 'g_sched', 'g_step28', 'l_cover', 'l_isleast', 'x_block', 'x_ecmul', 'x_ecpp_group', 'x_ecpp_step', 'x_fermat', 'x_least']

## premises of m_ceiling : 4 {'lean': 2, 'heur': 1, 'comp': 1} {'lim': 1, 'res': 2, 'cov': 1}
   heur 1
       m_h1 [res/heur/steer] H1: the leftover rows are independent
   open 0
   paper 0
   comp 1
       m_density [res/comp/steer] Cost model: E = |U| · boost / ln N
   leanhyp 0
   lean premises: ['c_kills', 'c_thinning']

## premises of s_verdict : 110 {'comp': 29, 'lean': 65, 'open': 3, 'heur': 7, 'paper': 5, 'leanhyp': 1} {'res': 33, 'dep': 14, 'lim': 15, 'gpu': 11, 'ff': 6, 'law': 6, 'bnd': 7, 'eng': 7, 'rec': 4, 'cov': 7}
   heur 7
       s_nonanalogy [res/heur/bound] Why the integers are harder: a known non-analogy
       d_law [dep/heur/steer] The number of complete covers: ln g0 = θ(x) − c·Q/ln² x, with c near 1
       d_recursion [dep/heur/steer] The law derived: a price per alive row, with the spread from Hardy–Littlewood pa
       m_h1 [res/heur/steer] H1: the leftover rows are independent
       m_ceiling [res/heur/steer] Heuristic ceiling: about 2.13 million at 200 digits
       m_wp3 [res/heur/bound] Decoding barrier: sub-100 digits is brute force or nothing
       m_floorpred [res/heur/steer] The same calculation above the end predicts how few rows a cover can leave
   open 3
       m_h2 [res/open/steer] H2: no compositeness test cheaper than one exponentiation
       s_ladder [res/open/steer] The sublinear programme's ladder
       s_question [res/open/steer] The sublinear search question (P′)
   paper 5
       m_classical [res/paper/engine] Thesis chapter 2: the classical constructions
       m_closure [res/paper/bound] Divisor-Paradigm Closure Theorem
       m_bls [res/paper/engine] N − 1 (BLS) certificate by CRT: no ECPP
       m_lemma2 [res/paper/bound] Lemma: a shared divisor divides q₁ − q₂
       m_entropy [res/paper/bound] Planted certificates cost at least covering's marginal price
   comp 29
       s_lists [res/comp/bound] Barrier: list gain above Q is tiny
       m_budgets [res/comp/steer] Two budgets: nats of modulus and nats of work
       m_density [res/comp/steer] Cost model: E = |U| · boost / ln N
       s_ffsearch [res/comp/steer] Toy search over F₃[x]: the parity filter is worth 4–5×
       e_fscan [eng/comp/engine] fscan and tscan: CPU scanners for the low end
       e_cap200 [eng/comp/engine] The Lean session's cover experiments: 850 rows at Q = 122,000
       m_selection [res/comp/steer] Selection identity: where the successes sit
       e_gpu [eng/comp/engine] GPU Fermat engines
       e_c15907 [eng/comp/engine] Complete covers: 15,907 on 89 primes, 16,747 on 92
       d_ub89 [dep/comp/bound] At the campaign's size: 15,907 ≤ D(89) < 35,000, and a floor of 777 rows
       m_portfolio [res/comp/steer] What the remaining budget buys
       v_brainstorm [res/comp/steer] The 200-idea brainstorm: nothing worth a nat
       m_price [res/comp/steer] Price list: what raising the target costs
       d_table [dep/comp/bound] Exact cover depth D(n) for up to 35 moduli
       s_lattice [res/comp/bound] Barrier: lattices and CRT with errors or lists
       e_fleet200 [eng/comp/record] The 200-digit fleet campaign (budget game)
       m_wp10 [res/comp/aside] A proof of RH/GRH would move no lever
       s_mitm [res/comp/bound] Barrier: meet in the middle, birthday trees, hashing
       m_toycrt [res/comp/bound] Toy CRT decoder: LLL stops at the Johnson radius
       e_cover_opt [eng/comp/engine] Cover design: greedy, annealing, parallel tempering
       e_selective [eng/comp/steer] Selective testing: test only the emptiest members (the 3% rule)
       m_wp7 [res/comp/bound] Five probes of non-covering mechanisms all end
       s_prize [res/comp/steer] What a perfect search would be worth
       s_score [res/comp/bound] Barrier: linear-time scoring is optimal
       m_floor [res/comp/steer] A measured floor under every cover: 1,214 rows at 170,000 against the best known
       m_falsify [res/comp/bound] Falsification engine: 13,661 instances, zero passes
       d_search [dep/comp/engine] The exact search for D(n): one lemma, several cuts
       m_mapshare [res/comp/bound] Neighbouring N share the prime map, but that excludes a cover
       s_crt [res/comp/bound] Barrier: free coordinates stop at the cap
   leanhyp 1
       l_linnik [bnd/leanhyp/bound] Effective size of N, assuming Linnik
   lean premises: ['c_blackbox', 'c_brainstorm', 'c_budget', 'c_deficit', 'c_fewrows', 'c_hardness', 'c_hits', 'c_johnson', 'c_kills', 'c_lattice', 'c_layers', 'c_listgain', 'c_listgain_q', 'c_mitm', 'c_nofree', 'c_pigeon', 'c_poly', 'c_population', 'c_prime_moduli', 'c_selection', 'c_thinning', 'c_tilt', 'c_transfer', 'c_two_rows', 'd_count', 'd_count_lower', 'd_def', 'd_depthform', 'd_exact', 'd_more', 'd_pairs', 'd_pairsums', 'd_records', 'f_desert', 'f_discr_sub', 'f_general', 'f_notirr', 'f_parity', 'f_sw', 'g_class', 'g_conv', 'g_f26', 'g_f30', 'g_f52', 'g_fermat2', 'g_fermat28', 'g_fermat28r', 'g_montsqr', 'g_sched', 'g_step28', 'l_cover', 'l_cover_exists', 'l_exists', 'l_gammaid', 'l_isleast', 'l_mertens1', 'l_mertens3', 'l_mertensconst', 'l_pnt', 'l_primorial', 'r_cover15907', 'r_cover_more', 's_parity', 'x_coveredin', 'x_fermat']
r_160357 lean direct deps: ['e_fleet200', 'l_isleast', 'x_block', 'x_ecpp_step', 'x_least'] | users: ['e_rec160357']
r_158209 lean direct deps: ['e_fleet200', 'l_isleast', 'x_block', 'x_ecpp_step', 'x_least'] | users: ['m_proofcarrying']
r_earlier lean direct deps: ['e_fleet200', 'e_threshold', 'l_isleast', 'x_block', 'x_ecpp_step', 'x_least'] | users: []
e_fleet200 comp direct deps: ['e_cap200', 'e_cover_opt', 'e_gpu', 'e_selective', 'm_density'] | users: ['e_fleetnow', 'e_rec160357', 'e_records', 'm_portfolio', 'r_158209', 'r_160357', 'r_earlier']
e_rec160357 comp direct deps: ['e_491', 'e_fleet200', 'e_sievechain', 'm_density', 'm_rowsabove', 'r_160357'] | users: []
e_fleetnow comp direct deps: ['e_fleet200', 'm_portfolio', 'm_price'] | users: []
e_records comp direct deps: ['e_fleet200', 'e_height', 'e_megagap', 'e_threshold', 'e_verify'] | users: ['r_rank']
m_ceiling heur direct deps: ['m_density'] | users: ['e_dual', 'm_lgs', 'm_portfolio', 't_tail']
m_price comp direct deps: ['e_cover_opt', 'm_density'] | users: ['e_fleetnow', 'm_designmenu', 'm_portfolio', 'm_staircase', 'v_brainstorm']
m_portfolio comp direct deps: ['e_fleet200', 'm_ceiling', 'm_price'] | users: ['e_fleetnow', 'm_designmenu', 's_prize', 'v_brainstorm']
m_designmenu comp direct deps: ['m_portfolio', 'm_price', 'm_rowsabove'] | users: []
m_rowsabove comp direct deps: ['d_families', 'e_491', 'm_density'] | users: ['e_rec160357', 'm_designmenu']
m_staircase heur direct deps: ['e_gpu', 'e_selective', 'm_price', 'm_rounding'] | users: ['m_doors']
m_floor comp direct deps: ['d_law', 'd_ub89', 'e_cover_opt', 'm_floorpred'] | users: ['m_doors', 'm_rounding', 's_verdict']
m_floorpred heur direct deps: ['d_recursion', 's_prize'] | users: ['e_dual', 'm_floor']
m_rounding comp direct deps: ['e_cap200', 'e_cover_opt', 'm_density', 'm_floor'] | users: ['m_doors', 'm_staircase']
m_doors heur direct deps: ['m_closure', 'm_floor', 'm_rounding', 'm_staircase'] | users: []
s_verdict open direct deps: ['c_hardness', 'm_floor', 'm_mapshare', 's_crt', 's_ffsearch', 's_ladder', 's_lattice', 's_lists', 's_mitm', 's_nonanalogy', 's_prize', 's_question', 's_score'] | users: []

## new boxes by group Counter({'dep': 31, 'eng': 8, 'res': 6, 'rec': 5, 'lim': 1})
new boxes that are premises of T: 26 of 51
new boxes neither: 20
dep-group boxes premises of T: ['d_count', 'd_count_lower', 'd_exact', 'd_pairsums', 'd_more', 'd_ub89', 'd_law', 'd_recursion', 'd_table', 'd_families', 'd_def', 'd_covers', 'd_search', 'd_pairs', 'd_records', 'd_depthform']
---- RAW out2.txt ----
cur_res_edges keys 167 in gb_data 167 missing from data []
cur_edges_lean.py.txt 66 in data 63 not in data ['l_cb073>l_pnt', 'l_cb_sharp>l_mertens3', 'l_cb_sharp>l_pnt']
cur_edges_lean5.py.txt 42 in data 42 not in data []
spec_lean nodes 95 keys ['nodes'] spec ids not in data [] lean nodes not in spec ['s_parity']

boxes with status lean/paper/comp that transitively rely on >=1 heur/open box: 62 Counter({'comp': 47, 'lean': 10, 'paper': 5})
 of all comp boxes 60 ; comp with heur/open ancestor 47
 comp boxes with NO heur/open premise: ['d_greedy', 'd_search', 'd_table', 'e_fermatw', 'e_fscan', 'e_gpu', 'e_height', 'e_verify', 'm_falsify', 'm_wp7', 's_crt', 's_mitm', 't_data']
 boxes having m_h1 as premise: 72 of 187; non-lean boxes: 91 non-lean with m_h1 premise 62

doc-edge semantic classes (keyword heuristic, first match): {'other (uses/assumes/states)': 204, 'tests/validates': 85, 'corrects/replaces/withdraws': 20, 'provenance (data from / found by)': 11}
  tests/validates 85
      x_block>l_cover [is the cover, as a check]
      c_needles>c_brainstorm [residues within a budget]
      g_f52>x_fermat [computes the same test]
      g_fermat2>x_fermat [computes the same test]
      g_fermat28>x_fermat [computes the same test]
      e_fleet200>e_selective [uses the 3% rule]
      e_megagap>m_density [calibrates the model]
      e_megagap>m_classical [gap versus desert]
      e_verify>m_bls [checks the N − 1 proof]
      m_budgets>e_cover_opt [oracle against covers]
      m_closure>m_h2 [assumes H2]
      m_falsify>m_wp7 [calibrated on the probes]
      m_staircase>e_selective [engine gains]
      m_toycrt>m_wp3 [checks the barrier]
      m_wp10>m_h2 [untouched by GRH]
      m_wp10>m_bls [BLS beats Miller]
      m_thm1>l_cb_sharp [kernel-checked version]
      m_thm1>c_layers [the layered skeleton]
      m_thm1>l_counting [measured against]
      m_proofcarrying>x_least [the certificate theorem]
      v_brainstorm>m_price [price of each nat]
      e_cap200>e_cover_opt [cross-checked]
      r_rank>e_records [same sequence as the exhaustive board]
      s_lattice>c_lattice [Lean: the radius]
      s_lattice>m_toycrt [empirical check]
      s_score>c_population [Lean: population bound]
      s_score>e_selective [the 3% rule is the optimum]
      s_miniature>s_prize [validates the tilt]
      r_cover15907>e_c15907 [cover from the sublinear programme]
      e_gpu>g_fermat28 [proved to be a Fermat test]
      e_gpu>g_fermat28r [proved to be a Fermat test]
      e_gpu>g_fermat2 [proved to be a Fermat test]
      e_fscan>g_f52 [proved to be a Fermat test]
      e_fscan>g_f26 [proved to be a Fermat test]
      e_fscan>g_f30 [proved to be a Fermat test]
      t_calib>t_data [measured on]
      t_calib>m_h1 [tests H1]
      t_calib>c_hits [tests the formula]
      t_joint>t_data [measured on]
      t_joint>m_h1 [tests H1 on pairs]
      t_joint>c_needles [needles at scale]
      t_archip>c_brainstorm [cannot join a cover]
      t_archip>t_data [measured on]
      t_props>t_data [measured on]
      t_tail>m_ceiling [tests the tail]
      t_tail>t_data [measured on]
      t_ml>t_calib [baseline]
      t_ml>m_selection [the count is all]
      t_ml>t_data [measured on]
      t_budget>s_prize [small-scale analogue]
      t_budget>t_ml [count is sufficient]
      t_budget>t_data [measured on]
      m_lgs>m_density [same figures by another route]
      m_lgs>r_gen [tested on A025018]
      m_lgs>r_walk [the walker's question]
      m_lgs>d_bounds [rule A is the depth]
      d_g0exact>d_exact [reproduces the exact depths]
      d_g0exact>d_law [checks the sampler]
      d_limitcheck>d_pairsums [uses the product form]
      d_limitcheck>d_recursion [checks its four steps]
      d_table>d_more [a vector for every n]
      d_search>c_hardness [SAT as a cross-check]
      d_ub89>d_records [lower end is Lean-checked]
      d_greedy>m_thm1 [the paper theorem]
      d_reach>d_covers [Lean-certified points]
      d_end89>d_records [the certificates]
      d_end89>d_ub89 [proved upper bound]
      d_end89>d_law [read off the law]
      d_law>d_count_lower [proved lower bound]
      d_law>d_table [compared with exact depths]
      d_law>c_pigeon [beats the first moment]
      d_limit>d_limitcheck [referee's verdict]
      m_floor>d_ub89 [the rigorous floor]
      m_floor>e_cover_opt [the best cover known]
      m_floor>m_floorpred [close to the measured floor]
      m_rounding>m_floor [door 1 measured]
      m_doors>m_floor [door 1 measured]
      e_rec160357>r_160357 [certified in the kernel]
      e_rec160357>e_sievechain [top-of-range windows]
      e_dualcpu>e_selective [emptiest members only]
      d_pairproof>d_nibble [makes the sketch rigorous]
      d_capacity>d_greedy [tested on greedy covers]
      d_prefix>d_families [gives the families a cause]
      d_capacity>d_prefix [checks its asymptotic part, for typical covers]
      d_prefixcheck>d_prefix [referee's second read]
  corrects/replaces/withdraws 20
      r_walk>l_cover [the same condition as a cover]
      m_thm1>m_lower [beats the thesis bound]
      m_errata>m_wp3 [retracted open window]
      m_errata>m_wp10 [erratum]
      m_lgs>c_thinning [the dependence correction]
      d_table>d_search [found by]
      d_search>d_def [searches the definition]
      d_limit>d_recursion [limit of the recursion as first written]
      d_limit>m_thm1 [beyond 1.349]
      m_rowsabove>m_density [corrects its blind spot]
      m_designmenu>m_portfolio [updates the budget view]
      e_fleetnow>m_price [3.7× faster than priced]
      e_fleetnow>m_portfolio [budget now smaller]
      d_capacity>d_limit [a bound for typical covers only]
      d_prefix>d_law [where c = 1.00 comes from]
      d_limit>d_prefix [the replacement for the limit]
      d_block>d_depthform [beats the Lean theorem in order]
      d_block>m_thm1 [supersedes in order]
      d_block>d_limit [why the replacement is not derived]
      d_block>d_pairproof [supersedes in order]
  provenance (data from / found by) 11
      e_records>e_fleet200 [budget game]
      e_fleet200>e_gpu [runs on GPUs]
      e_fleet200>e_cover_opt [covers from tempering]
      m_portfolio>e_fleet200 [starting point]
      r_cover_more>e_c15907 [covers from the research session]
      s_lattice>c_johnson [Lean: only the cover is left]
      r_158209>e_fleet200 [data from the fleet]
      r_earlier>e_fleet200 [data from the fleet]
      d_end89>e_c15907 [the covers found]
      r_160357>e_fleet200 [data from the fleet]
      e_rec160357>e_fleet200 [found by the campaign]

longest chain depth per node top: [(12, 'm_doors'), (12, 'd_prefixcheck'), (12, 'd_capacity'), (11, 'm_staircase'), (11, 'd_block'), (10, 's_verdict'), (10, 'm_rounding'), (10, 'e_t5')]
chain m_designmenu: ['m_designmenu', 'm_rowsabove', 'd_families', 'd_law', 'd_count_lower', 'd_depthform', 'l_mertens3', 'l_gammaid', 'l_mertensconst', 'l_mertens1']
chain s_verdict: ['s_verdict', 'm_floor', 'd_ub89', 'd_records', 'r_cover_more', 'r_cover15907', 'e_c15907', 'e_cover_opt', 'm_density', 'm_h1', 'c_thinning']
r_160357 lean users(trans): ['e_rec160357']
e_rec160357 comp users(trans): []
e_fleetnow comp users(trans): []
t_data comp users(trans): ['t_archip', 't_budget', 't_calib', 't_joint', 't_ml', 't_props', 't_tail']
t_calib comp users(trans): ['t_budget', 't_ml']
t_tail comp users(trans): []
t_joint comp users(trans): ['t_archip', 't_tail']
t_ml comp users(trans): ['t_budget']
t_budget comp users(trans): []
e_dual heur users(trans): ['e_dualcpu', 'e_t5']
e_t5 comp users(trans): []
e_dualcpu comp users(trans): []
e_threshold comp users(trans): ['e_records', 'r_earlier', 'r_rank', 'r_ranksieve', 't_props']
e_height comp users(trans): ['e_dual', 'e_dualcpu', 'e_records', 'e_t5', 'm_errata', 'r_rank', 'r_ranksieve', 't_props']
e_megagap comp users(trans): ['e_records', 'r_rank', 'r_ranksieve', 't_props']
d_limit heur users(trans): ['d_block', 'd_capacity', 'd_prefixcheck']
d_block paper users(trans): ['d_capacity', 'd_prefixcheck']
d_capacity heur users(trans): []
m_lgs heur users(trans): []
m_errata open users(trans): []
m_h2 open users(trans): ['d_block', 'd_capacity', 'd_limit', 'd_prefixcheck', 'm_closure', 'm_doors', 'm_errata', 'm_thm2', 'm_wp10', 's_ladder', 's_nonanalogy', 's_question', 's_verdict']
s_prize comp users(trans): ['e_dual', 'e_dualcpu', 'e_t5', 'm_doors', 'm_floor', 'm_floorpred', 'm_rounding', 'm_staircase', 's_ladder', 's_miniature', 's_verdict', 't_budget']

keyword: #boxes mentioning | #lines GAPS_MAP.md
user               1   1  ['r_rank']
goal               0   0  []
decision           0   0  []
decide            11   1  ['c_brainstorm', 'x_block', 'f_sw', 'g_class', 'd_def', 'c_hardness', 'm_h2', 't_budget']
units              6   2  ['e_fleet200', 'm_errata', 'd_reach', 'd_g0exact', 'e_fleetnow', 'e_dual']
unit               7   2  ['e_fleet200', 'm_density', 'm_errata', 'd_reach', 'd_g0exact', 'e_fleetnow', 'e_dual']
Colab              4   3  ['e_height', 'e_gpu', 'e_rec160357', 'e_fleetnow']
dollar             0   0  []
\$                 0   0  []
deadline           0   0  []
stop              11   0  ['c_brainstorm', 'r_cover15907', 'r_gen', 'e_verify', 'm_toycrt', 'm_bls', 's_crt', 's_verdict']
give up            0   0  []
100 digits         2   0  ['m_ceiling', 'm_wp3']
150 digit          3   0  ['r_earlier', 'e_threshold', 'm_budgets']
300 digit          2   0  ['e_dual', 'e_dualcpu']
400 digit          4   0  ['e_gpu', 'e_fermatw', 'e_dual', 'e_dualcpu']
250 digit          0   0  []
1000 digit         0   0  []
10\^300            0   0  []
10\^1000           0   0  []
other digit        0   0  []
why 200            0   0  []
200 digits        14   3  ['r_earlier', 'e_cover_opt', 'm_ceiling', 'm_price', 'v_brainstorm', 't_calib', 't_budget', 'd_ub89']
A025018            5   2  ['r_rank', 'r_walk', 'r_gen', 'd_bounds', 'd_g0exact']
OEIS               4   0  ['r_rank', 'r_walk', 'r_gen', 'd_table']
publish            0   1  []
paper             11   3  ['l_primorial', 'l_exists', 'l_cover', 'l_cover_exists', 'l_cb_sharp', 'd_depthform', 'm_lemma2', 'm_thm1']
variance           1   0  ['d_recursion']
luck              18   2  ['l_cover', 'x_fermat', 'r_cover15907', 'r_family', 'r_cover_more', 'r_walk', 'd_def', 'd_bounds']
lucky              2   0  ['r_cover15907', 'm_errata']
risk               0   0  []
probability of     1   0  ['t_joint']
chance             9   1  ['m_portfolio', 'm_h1', 'm_doors', 't_calib', 't_archip', 'd_greedy', 'm_lgs', 'm_floor']
alternative        1   0  ['e_selective']
option             1   0  ['e_sievechain']
trade-off          1   0  ['c_budget']
opportunity        0   0  []
cost of            0   0  []
human              0   0  []
Lean session      19   8  ['c_brainstorm', 'c_thinning', 'r_rank', 'd_more', 'e_cover_opt', 'e_cap200', 'm_proofcarrying', 'v_brainstorm']
consultant         5   0  ['d_limit', 'd_pairproof', 'd_block', 'd_prefix', 'd_capacity']
spy                0   0  []
student            0   0  []
lead              11   1  ['f_parity', 'f_notirr', 'd_count_lower', 'd_pairs', 'd_limitcheck', 'm_rowsabove', 'm_designmenu', 'e_rec160357']
thesis            11   4  ['l_linnik', 'l_pnt', 'l_cb_sharp', 'f_resultant', 'd_depthform', 'm_density', 'm_h1', 'm_closure']
CPU                7   3  ['g_f26', 'g_fermat28', 'e_fleet200', 'e_gpu', 'e_fscan', 'e_fermatw', 'e_dualcpu']
cloud              0   0  []
rent              16   2  ['c_two_rows', 'c_nofree', 'c_transfer', 'g_f30', 'r_160357', 'c_hardness', 'e_records', 'e_height']
buy                7   0  ['c_listgain', 'r_cover_more', 'e_cover_opt', 'm_portfolio', 'm_doors', 'm_designmenu', 'e_dual']
card-day           1   0  ['m_price']
fleet-day          4   1  ['e_fleet200', 'm_price', 'm_portfolio', 'e_fleetnow']
1,800              2   0  ['e_491', 'e_fleetnow']
priority           0   0  []
next step          1   0  ['d_pairs']
recommend          0   0  []
should             2   0  ['m_proofcarrying', 'd_pairproof']
unknown            0   0  []
not known          1   0  ['d_table']
unmapped           0   0  []
not mapped         0   1  []
10%               12   4  ['c_listgain_q', 'r_160357', 'e_cover_opt', 'm_ceiling', 'm_portfolio', 'm_selection', 's_question', 's_prize']
ten per cent       0   0  []
ceiling           14   7  ['c_brainstorm', 'r_160357', 'e_c15907', 'm_ceiling', 'm_price', 'm_portfolio', 'm_wp7', 'm_bls']
k-tuple            1   0  ['m_h1']
prime gap          5   1  ['c_transfer', 'e_height', 'e_megagap', 'm_classical', 't_archip']
A-B family|famil  20   6  ['c_poly', 'r_family', 'e_fleet200', 'm_price', 'm_portfolio', 'm_closure', 'm_entropy', 'm_wp7']
near-miss          9   1  ['r_160357', 'e_records', 'e_fleet200', 'm_portfolio', 'm_designmenu', 'e_rec160357', 'e_491', 'e_fleetnow']
ECPP               8   0  ['x_ecpp_step', 'x_ecpp_group', 'x_ecmul', 'e_height', 'e_megagap', 'm_bls', 'm_errata', 'e_rec160357']
certificate       24   5  ['l_cover', 'x_least', 'x_ecpp_step', 'x_ecmul', 'r_158209', 'r_earlier', 'r_cover_more', 'r_walk']
