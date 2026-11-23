# Result ledger: Goldbach-gap thesis + SOK + IDEAS notes

Sources read in full: thesis `main.tex`, `ch1_introduction.tex` ... `ch7_outlook.tex`, plus `appendix_data.tex` (it is `\input` by main.tex, so it was read although not on the list); research notes `SOK_GOLDBACH_GAPS.md` (rev 3 plus the rev-4 addendum of 2026-11-21 and the 2026-11-22 ceiling-model update), `IDEAS100.md`, `IDEAS.md`.
Path prefix for the thesis files: `<scratchpad>/wt/thesis/goldbach/thesis/`; for the notes: `<scratchpad>/wt/research/goldbach/`. In `where:` fields "SOK" = SOK_GOLDBACH_GAPS.md.
Conventions: N even; g(N) = least prime p with N-p prime; nats = natural-log units; E = failure exponent (section "failure_exponent"); Q = target (all primes < Q to be excluded); U = residual (uncovered) prime offsets; M = cover modulus; N = N0 + kM.
Status vocabulary: proved-in-text | Lean-checked | computed | conjectural | retracted, with parenthetical qualifiers. NO entry is Lean-checked: no file names a Lean theorem; SOK section 7 item 8 says the Lean toolchain could not be installed and formal verification is "Not yet done".
60 entries, ordered roughly foundations -> constructions -> cost model -> records -> frontier -> barriers -> closure -> outlook/limits. Where I re-computed a quoted number myself this is said explicitly; everything else is as stated in the source.

---

## def_games | Three games: height, threshold, budget
- kind: proposition (definitions)
- says: For even N>=4, g(N)=min{p prime : N-p prime}. Height game = maximise g(N) with N unbounded; threshold game T(Q)=min{N even, Goldbach-representable : g(N)>Q}; budget game R(X)=max{g(N) : N<X}, where "fewer than 200 digits" means N<10^199. R is nondecreasing in X, and the thesis stresses that R(10^199) and R(10^200) are different games so every record must state its bound.
- status: proved-in-text (definitions)
- uses: none
- where: ch1_introduction.tex, Definition def:games and the remark "A naming caution"
- matters: fixes the scoring rules (strict N<10^199 vs up-to-200-digit N) that every record and target in this ledger refers to.

## hl_heuristic | Hardy-Littlewood count of Goldbach partitions
- kind: open-problem
- says: r(N) ~ 2*Pi_2*N/(log N)^2 * prod_{p|N, p>2}(p-1)/(p-2), with Pi_2=prod_{p>2}(1-1/(p-1)^2)~0.6601 and r(N)=#{p<=N : p and N-p prime}; a typical large even N should therefore have many partitions, and the interesting question is how lopsided the most lopsided one must be.
- status: conjectural
- uses: ext:HL
- where: ch1_introduction.tex, eq:HL
- matters: template for the independence heuristic (H1) and the Mertens-adjusted prime probability behind the failure exponent.

## exhaustive_glvdtr | Exhaustive data and the GLvdtR ceiling law
- kind: empirical
- says: Exhaustive search: g=1093 at N=60,119,912; g(N)<=5569 for all even N<=4*10^14 (Richstein); g=9781 first attained at N=3,325,581,707,333,960,528 and g(N)<=9781 for all even N<=4*10^18 (Oliveira e Silva-Herzog-Pardi). Granville-van de Lune-te Riele conjecture g(N)=O((log N)^2 log log N); SOK fits g_max(X)~C*ln^2X*lnlnX with C~1.4 at 19 digits, but ceiling_model.py (HL heuristic only) gives 1.40 at 19 digits, 1.47 at 25 and 1.58 at 63 digits, so C=1.4 understates g at larger sizes.
- status: computed (data); conjectural (ceiling law)
- uses: hl_heuristic, ext:OeS, ext:Richstein, ext:GLvdtR
- where: ch1_introduction.tex, eq:GLR and paragraph after Definition def:games; SOK section 6 (update 2026-11-22)
- matters: the conjectural ceiling from which every "wall" estimate (T(10^5)~10^53, R(10^200)~1.8M) is extrapolated.

## cert_semantics | What a certified record certifies, and how
- kind: algorithm
- says: Three separate claims: (a) no prime below the stated value is a summand (settled unconditionally by a congruence divisor or a failed base-2 strong-PRP witness), (b) N is Goldbach-representable (needs an exhibited prime complement), (c) least summand = stated value (both, plus a primality certificate for the complement, ECPP via PARI/GP). Pipeline: reconstruct N from (N0,M,k); per-prime witness (proper divisor or strong base-2 witness); ECPP of N-g; independent re-verification (own projective elliptic-curve arithmetic, no library); SHA-256 manifest. SOK section 4: four process incidents caught (vacuous GP scan, junk 2-byte ECPP "certificate", process-kill/cwd losses, audit found zero false-accept paths but three false-reject bugs); "no record that passed all legs has ever been overturned". Machine-checking of the verifier (or of IsLeast {p | p.Prime and (N-p).Prime} g for N-1-certified records) is "not yet done".
- status: computed
- uses: ext:ECPP, ext:BPSW, bls_complement
- where: ch1_introduction.tex "Notation and conventions"; ch3_engineering.tex section sec:certification; SOK sections 4 and 7.8
- matters: defines what "certified" means for each record and confirms nothing here is proof-assistant checked.

## factorial_deserts | Factorial composites, Wilson, and 27!+28
- kind: lemma
- says: n!+k is composite for 2<=k<=n, and n!-k is composite for n>=4, 2<=k<=n. Wilson obstructions: if n+1 is prime then (n+1)|n!+1; if n+2 is prime then (n+2)|n!-1; so factorial primes n!+1 (n>=3) occur only when n+1 is composite. Worked example N=27!+28 (29 digits): every prime q<=67 has N-q composite by an explicit factor (q=29 via Wilson, q=59 via 41|27!-31) and N-71 is prime, so g(N)=71; heuristically factorial deserts reach only ~log N/log log N.
- status: proved-in-text (finite explicit witnesses; I re-checked g(27!+28)=71, 41|27!-31, 29|27!-1 numerically)
- uses: ext:Wilson
- where: ch2_foundations.tex, Lemma lem:fact, Lemma lem:wilson, Corollary cor:facprime, Proposition prop:71, Table tab:witness
- matters: pedagogical baseline showing a factorial wastes each small prime on a single residue class.

## primorial_unbounded | Primorial deserts; g is unbounded unconditionally
- kind: theorem
- says: If m_P=prod_{p<=P}p divides even N>2P then N-q is composite for every prime q<=P (Lemma lem:primcore). With s=nextprime(P) and any prime t=-s (mod m_P) (infinitely many by Dirichlet) N=s+t has g(N)=s>P, so sup g=infinity unconditionally, and Linnik gives log N<<P hence g(N)>>log N. Instances: 30030=17+30013 (g=17); m_43=13082761331670030=89+13082761331669941 (g=89), both re-checked. Heuristic roughness bonus: N=m_P makes N-q P-rough, multiplying its prime probability by ~e^gamma*log P (Mertens), expected least surviving summand ~P(1+e^-gamma)~1.56P, at a modulus cost ~e^P.
- status: proved-in-text (the 1.56P roughness remark is heuristic)
- uses: ext:Dirichlet, ext:Linnik, ext:Mertens
- where: ch2_foundations.tex, Lemma lem:primcore, Theorem thm:dirichlet, Remarks rem:concrete and rem:rough
- matters: first unconditional unboundedness result and origin of the Mertens "boost" factor that reappears in the failure exponent.

## cover_certificate | Covering certificate and greedy cover
- kind: proposition
- says: If odd primes r with residues a_r are such that every odd prime q<Q has q=a_r (mod r) for some r, N is even, N=a_r (mod r) for all r and N>Q+max r, then N-q is composite for every prime q<Q (M=2*prod r by CRT; the size hypothesis only needs the divisors to be proper). Greedy algorithm: for r=3,5,7,... pick the residue class holding most still-uncovered odd primes below Q. At Q=10^5 a complete greedy cover uses 356 congruences and a 1,020-digit modulus versus a primorial of ~43,000 digits (both re-checked: 355 odd moduli give 1,019.6 digits); SOK: a complete cover for Q=10^8 needs 327,455 digits (no partition exhibited).
- status: proved-in-text (proposition); computed (greedy sizes)
- uses: ext:CRT, ext:Erdos1950
- where: ch2_foundations.tex, section sec:covering, Proposition prop:cover, algorithm box; SOK section 1
- matters: the exclusion side of every record; its cheapness is the whole subject.

## partial_cover_search | Partial cover plus progression search
- kind: construction
- says: Stop the greedy cover early; U = odd prime offsets <Q left uncovered. CRT gives N0 mod M=2*prod_{r in R} r, every candidate is N=N0+kM, and for each q in U test N-q by a probable-prime test. A failed PRP test is a rigorous compositeness proof (pseudoprimes only cause false positives), so if N-q is composite for all q in U then no prime q<Q is a summand (Proposition prop:partial). It turns a proof obligation into a search of cost e^E candidates.
- status: proved-in-text
- uses: cover_certificate, failure_exponent
- where: ch2_foundations.tex, section sec:partial, eq:progression, Proposition prop:partial
- matters: the construction behind every record in the thesis and the paradigm whose limits the rest studies.

## cover_realisation | Every cover is realised by Goldbach numbers
- kind: theorem
- says: For any cover {(r,a_r)} of the odd primes below Q by odd prime moduli there are infinitely many even N>Q+max r with an explicit partition N=s+t, N=a_r (mod r) for all r, and g(N)>=Q (take a prime s in a reduced class avoiding every a_r, then a prime t=a_r-s, by Dirichlet twice). For initial-segment covers (one modulus per prime p<=x) Linnik gives s,t<<M^L, hence log N<<theta(x)<<x; asserted only for initial-segment covers.
- status: proved-in-text
- uses: cover_certificate, ext:Dirichlet, ext:Linnik
- where: ch2_foundations.tex, Theorem thm:coverdirichlet, Remark rem:size
- matters: upgrades claim (a) to an actual Goldbach number so unboundedness results transfer from covers.

## gap_transfer | Prime gaps transfer to deserts, one way only
- kind: proposition
- says: If [N-Q,N-2] contains no prime then no prime q<=Q is a summand, so a Goldbach-representable N has g(N)>Q; the converse fails because a desert only needs the sparse set {N-q : q prime} composite. Measured: the 2,692-digit desert has g=1,134,871, above the largest certified prime gap 1,113,106, with an integer ~6.9x shorter than the one realising that gap; for the 237-digit height construction of an earlier draft [N-1926,N-2] is prime-free and N-1927 passes BPSW (gap information gives g>1926) while the certified g is 109,621. SOK: a 1.16M desert needs ~2,480 digits vs ~18,000-digit gap endpoints; "Goldbach gaps are strictly cheaper than prime gaps".
- status: proved-in-text (proposition); computed (comparisons; I re-checked that nextprime(1,113,106)=1,113,137, consistent with the Q=1,113,138 cover)
- uses: rec_height, ext:BPSW
- where: ch2_foundations.tex, section sec:gaps, Proposition prop:transfer; ch1_introduction.tex "Certified incumbents"; SOK section 1
- matters: deserts are a strict relaxation of gaps, so gap records are the wrong benchmark to chase.

## lower_bound_thm | Unconditional growth rate of g
- kind: theorem
- says: There are infinitely many even N, each with an explicit Goldbach representation, with g(N) >> (log N)(log_2 N)(log_4 N)/log_3 N. Proof: the Erdos-Rankin covering of [1,y], y=floor(c*x*log x*log_3 x/log_2 x), by one class mod each prime p<=x (FGKMT), normalised so the mod-2 class covers only evens, then fed through the realisation theorem and the Linnik size bound; this equals the best known prime-gap order.
- status: proved-in-text (relies on ext:FGKMT)
- uses: cover_realisation, ext:FGKMT, ext:Rankin, ext:Linnik
- where: ch2_foundations.tex, Theorem thm:lower
- matters: the rigorous lower end of the maximal order of g, which the constructive programme cannot currently beat asymptotically.

## wp12_covering_thms | Primes-only covering bound and impossibility (SOK)
- kind: theorem
- says: SOK rev 4 states (WP12 Theorem 1) that residues modulo the primes <=x can cover all primes below (1.349-o(1))*x*ln x, beating the FGKMT-transfer bound and the counting constant 1/2 of arXiv:2605.21529, and (Theorem 2) that they can never cover all primes below x^(4+eps) (x^(2+eps) under Elliott-Halberstam), because for any even N some prime q<x^(4+eps) has N-q free of prime factors <=x; vacuous at record parameters. Greedy complete covers reach Q~0.72*x*ln^2 x (SOK section 5.5).
- status: proved-in-text (asserted in SOK; proof is in phd/wp12_prime_covering_grh_ledger.md, which I did not read)
- uses: lower_bound_thm, cover_certificate, ext:ElliottHalberstam
- where: SOK Rev 4 addendum item 2; section 5 item 5 arrow; section 7 item 3(ii)
- matters: first lower bound beating the FGKMT transfer and first impossibility theorem for divisor certificates (asymptotic only).

## sandwich_open | The asymptotic sandwich for max g
- kind: open-problem
- says: Between the rigorous (log N)(log_2 N)(log_4 N)/log_3 N and the conjectural (log N)^2 log log N there is a factor of about log N; the question is whether covering only the prime offsets (not a whole interval) asymptotically beats the prime-gap scale. SOK: no theorem "every even N<B has g(N)<=f(B)" exists beyond trivialities, even conditionally.
- status: conjectural (open)
- uses: lower_bound_thm, exhaustive_glvdtr, wp12_covering_thms
- where: ch2_foundations.tex (display after Theorem thm:lower); ch7_outlook.tex open problem 7; SOK section 7 item 3
- matters: states exactly which asymptotic statement would be new mathematics.

## failure_exponent | Failure exponent E and the e^E search cost
- kind: proposition (heuristic)
- says: For a partial cover with residual set U, a candidate N=N0+kM has all |U| residual complements composite with probability ~(1-boost/log N)^|U| ~ e^-E, where E=|U|*boost/log N and boost=2*prod_{r in R} r/(r-1) (Mertens roughness); so e^E candidates are needed per expected hit. Levers: more moduli shrink |U| but raise boost and log M; larger N lowers E; higher Q raises |U| roughly in proportion to pi(Q). SOK form: p1~e^gamma*ln(max contiguous prime)/ln N and cost e^(p1*k) with k=|U|.
- status: conjectural (rests on independence heuristic H1; checked in "calibration")
- uses: partial_cover_search, hl_heuristic, ext:PNT, ext:Mertens
- where: ch1_introduction.tex eq:E; ch3_engineering.tex section "The failure exponent", eq:boost; SOK section 2
- matters: the single currency (nats) in which every construction, engine improvement and record is priced.

## calibration | Model checked against 1.2e9 candidates
- kind: empirical
- says: Across three independent covers and ~1.2*10^9 scanned candidates the measured exponent Ehat (mean survivors per candidate x measured PRP pass rate) agrees with E to within 0.1 nats (a factor 1.11), per-slice values stable to a couple of percent; 1.2*10^9 equals the total of the three non-record campaigns (2.4+5.6+4.0 x 10^8). IDEAS/SOK add: 195-digit cover measured Ehat=17.4 vs predicted 17.28 (naive) / 17.51 (exact density e^(-a*ln(1-p)) averaged over a; naive undercounts by ~0.2 nats); 2 hits in ~1,780 progressions vs cumulative expectation ~2.1; the n=7 fully logged hits fell at 0.25x-3.0x of E (median 0.5x, "plan for 3x"); lognormal bonus sigma_a~13-14 worth ~0.3 nats.
- status: computed
- uses: failure_exponent, failed_campaigns
- where: ch3_engineering.tex section sec:calibration; IDEAS.md F1, F2; IDEAS100.md B8; SOK section 2
- matters: licenses doing feasibility questions by arithmetic (but see Doubts on what it does and does not bound).

## engine_search | Sieve, variants, survivor ordering, selective testing
- kind: algorithm
- says: Per-offset sieving with cached modular inverses (best sieve bound B=10^6: thesis says 901 vs 816 "thousand candidates per second" at B=3*10^6, IDEAS F5 reports the same 901 vs 816 as "k/s" on a 30k-k sweep); residue-swap variants share M and |U| (+47% throughput from cached inverses; zero-penalty catalogs: 26 single swaps -> 325 pairs -> ~2,600 triples = ~3,000 progressions at base |U|); survivor-ordered testing (success (1-p)^a concentrates hits in the low-survivor tail: factor 1.83 in conditional time-to-first-hit, only ~8% for full-sweep expectation, 12x on a toy); selective testing (skip the fullest 92% of each block at 199 digits: raw rate 1,772 -> ~16,300, keeping 27.6% of hit mass, net "about 3x"; works because tests per candidate ~1/phat~17 are flat in a while success decays geometrically in a).
- status: computed
- uses: failure_exponent, calibration
- where: ch3_engineering.tex section sec:engine; IDEAS.md F2, F4, F5
- matters: each item buys a fixed number of nats of E (e.g. x1.83 ~ 0.6 nats); the only engineering levers besides raw compute.

## gpu_throughput | GPU throughput converts into nats
- kind: empirical
- says: CUDA Montgomery-CIOS Fermat engine with bit-matrix sieve, validated bit-for-bit, sustains ~2.5*10^6 tests/s (T4) and ~8.5*10^6 (A100) vs ~6*10^3 on four CPU cores; T4/CPU ratio ~430 = 6.1 nats, matching the E-gap (~6) between the CPU-reachable 179-digit and GPU-reachable 150-digit rungs. Frontier is logarithmic in compute (10x = 2.3 nats); two-session fleet = 7.9*10^5 candidates/s (IDEAS100 E5 gives the split 185k + 604k k/s for the 150-digit run).
- status: computed
- uses: engine_search, failure_exponent
- where: ch3_engineering.tex paragraph "Hardware"; IDEAS100.md E5; SOK section 2
- matters: the last 29 digits (179 -> 150) were bought purely with throughput, so compute rather than cleverness sets the frontier.

## ratchet | Ratchet beats a single grand slam
- kind: verdict
- says: Breadth-first scans of many variants keep N near N0 but hit a hard pool-exhaustion ceiling; depth-first scans of one progression have an unbounded runway (N grows only logarithmically in k). The "ratchet" (design a cover, run to a hit, bank a certified record, re-tune, repeat) produced the ladder 195 -> 179 -> 150 digits at Q~10^5 (SOK: 193 -> 186 -> 179, each ~7-digit rung ~2.5x the previous search). The 150-digit record came at k=6.21*10^10 of a full [0,7.5*10^10) scan, 63.8% depth, cumulative expectation 0.40.
- status: computed
- uses: engine_search, rec_threshold
- where: ch3_engineering.tex section sec:ratchet; ch1_introduction.tex "Certified incumbents"; SOK section 3
- matters: the strategy that actually produces records under a fixed compute budget.

## failed_campaigns | Three campaigns without a record
- kind: negative-result
- says: E10 (budget game, Q=107,720, target g>107,719): 2.4*10^8 candidates, survival e^-lambda=0.17; Campaign 2 (Q=99,991, 168-digit cover, T(10^5) ladder): 5.6*10^8, survival 0.22; Campaign 3 (Q=122,000, target g>119,419): 4.0*10^8, survival 0.93, hand-stopped after 2.3% of its budget when a parallel effort was found on the same target (checkpoint committed, resumable). Per-slice statistics tracked the model throughout.
- status: computed
- uses: calibration, failure_exponent
- where: ch3_engineering.tex section sec:campaigns, Table tab:campaigns; appendix_data.tex (phd/campaign{,2,3}/)
- matters: reported with survival probabilities they are measurements of E and supply the 1.2*10^9-candidate sample.

## rec_threshold | Threshold-game records for T(100,000)
- kind: empirical
- says: 150-digit N~8.27*10^149 with g=104,527 (cover at Q=100,003, hit at k=6.21*10^10, GPU fleet, true E 24.91); 195-digit N~7.12*10^194 with g=100,297 (round 2 spec v990, k=70,186; a second hit at v1088, k=76,862 gave N~7.80*10^194, g=101,611, so the record stands); 197-digit g=107,719 from a dual-game cover at Q=105,668; pure-threshold cover needs only Q=100,003 (~8% fewer targets, |U|~700-704, E~17.2-17.5 at 195 digits). History: 1,020-digit complete cover g=100,747 (overpays ~7x). Descending ladder 195 -> 179 -> 150 digits.
- status: computed (certified by witnesses + ECPP; appendix marks the 150-digit record "re-verified")
- uses: partial_cover_search, ratchet, calibration, cert_semantics
- where: ch1_introduction.tex Table tab:records; appendix_data.tex section "Certified records"; IDEAS.md F1; IDEAS100.md E5; SOK section 3
- matters: the T(10^5) incumbent is 150 digits against a truth estimated near 10^53.

## rec_budget | Budget-game records R(10^199) and R(10^200)
- kind: empirical
- says: R(10^199): 199-digit N with g=119,419 (cover at Q~1.19*10^5, t=1.46*10^8; CPU; appendix: "re-verified"). R(10^200) row: 200-digit N with g=112,249 (cover at Q=107,720, k=56,770; GPU), which exceeds 10^199 by 3.4%. SOK adds an earlier 199-digit g=110,917 (N<N*, hit at 99.9% of its range, 3.0x the expectation) and classifies the 200-digit 112,249 as a negative result (GPU throughput without re-tuning the cover for the range-bound regime did not beat the tuned CPU cover; 119,419 stood). Since the 119,419 integer is also <10^200, the 112,249 record is dominated.
- status: computed
- uses: partial_cover_search, def_games, failed_campaigns
- where: ch1_introduction.tex Table tab:records and "A naming caution"; appendix_data.tex; SOK sections 3 and 6
- matters: the numbers the team's below-10^200 target must beat as documented here (the task brief's 158,209 is not in these files).

## rec_height | Height-game records at thesis scale
- kind: empirical
- says: 2,480-digit N with g=1,157,341 (cover at Q=1.16*10^6, t=14,544; SOK: hit #443, p1*k~7.7, "search-trivial, certification-bound") and 2,692-digit N with g=1,134,871 (cover at Q=1,113,138, k=14), which beats the largest certified prime gap 1,113,106 with an integer ~6.9x shorter. ECPP certification ~2 h (+2 h python re-verify, +2 h APR-CL) at 2,480 digits, scaling ~quartically, capping ECPP-based ladders near ~4,000 digits (g~2.5M). Superseded by the N-1-form records in "bls_complement".
- status: computed
- uses: partial_cover_search, cert_semantics, gap_transfer
- where: ch1_introduction.tex Table tab:records; SOK sections 2, 3 and 6 (Game 1)
- matters: the thesis-era height frontier and why it was certification-bound.

## bls_complement | N-1-form complement removes the certification wall
- kind: construction
- says: SOK rev 4 (2026-11-21): write N-g = 1+2^n*R; cover moduli are odd so the cover congruences become congruences on R, CRT intersects the two systems, and 2^n>(N-g)^(1/3) makes the Brillhart-Lehmer-Selfridge N-1 test a one-modexp proof (N is 1.5x the cover modulus, vs Proth's 2x); complete covers become optimal, no residual witnesses, no ECPP. Records: g=10,000,141 at 61,329 digits (3,072 GPU screens, ~2 h A100, re-proved on CPU); g=5,000,251 at 33,938 digits (3,140 PRP tests, 44 min on one A100); g=2,000,269 at 15,595 digits (648 tests, 37 min on 4 cores); g=1,200,109 at 11,263 digits certified twice by independent code. Found independently by two sessions that cross-verified. Wall is now PRP throughput (GMP, 4 cores: g>5*10^6 ~11 h, 10^7 ~3.4 days, 16,045,848 = largest known prime gap ~13 days) and the length of complete covers; prime density in the CRT-constrained progression is the ordinary e^gamma*ln B/ln P per sieve survivor (probes 54 vs 48.7, 8 vs 9.3, 46 vs 48.6, 6 vs 4.62).
- status: computed
- uses: cover_certificate, cert_semantics, ext:BLS, ext:Proth
- where: SOK Rev 4 addendum item 1; section 1 last table row; section 6 Game 1 arrow; section 7 item 2 arrow (proth/README.md, phd/wp11_bls_game1.md not read)
- matters: raises the height record ~9x (1.16M -> 10.0M) but is useless for the bounded games because it spends digits.

## frontier_table | Cover frontier and price list at Q~10^5
- kind: empirical
- says: Greedy digit-capped covers (digits: moduli, |U|, E): 195: 89, 692, 16.8; 170: 79, 754, 20.6; 150: 72, 802, 24.4; 140: 68, 830, 26.8; 130: 64, 862, 29.5; 120: 60, 899, 32.8; 100: 52, 973, 41.3 (IDEAS100 adds 160: 76, 773, 22.3). Slope grows from ~0.15 nats/digit (195->170) to ~0.43 (120->100); SOK: ~2.5x search per 7 digits near 195->179, ~1 digit per percent of cover quality. Price list (threshold game, A100 at 8.5*10^6 tests/s; this E column differs from the one above): 140 digits E=28.1, 0.10 A100-yr, ~$1,000; 135: 29.7, 0.49, $5,000; 130: 31.2, 2.3, $24,000; 125: 32.9, 12, $125,000; 120: 34.7, 73, $770,000; 100: 44.1, 8.9*10^5, $9.4 billion; fundable to ~130 digits, institutional to ~120.
- status: computed
- uses: failure_exponent, partial_cover_search, gpu_throughput
- where: ch4_frontier.tex Tables tab:frontier and tab:menu; IDEAS100.md header table; SOK sections 6 and 8
- matters: quantitative reason the threshold frontier is ~130-140 digits and sub-100 is out of reach by compute.

## rung_ladder | Rung ladder at 199 digits
- kind: empirical
- says: 88 moduli, boost~11, 199 digits (Q: |U|, E, e^E, fleet time at 7.9*10^5 candidates/s): 122,000: 867, 20.83, 1.1*10^9, 23 min; 135,000: 1,004, 24.12, 3.0*10^10, 11 h; 150,000: 1,138, 27.34, 7.5*10^11, 11 d; 175,000: 1,335, 32.07, 8.5*10^13, 3.4 y; 200,000: 1,569, 37.69, 2.4*10^16, 950 y (I re-checked E=|U|*11/ln(10^199) and the times). Rungs are geometrically spaced (each 25-280x the last), so climbing every rung costs only ~4% more than jumping to the top and banks a certified record at each.
- status: computed
- uses: failure_exponent, frontier_table, gpu_throughput
- where: ch4_frontier.tex Table tab:ladder
- matters: the budget-game price list and basis of the Operation Staircase.

## equilibrium | Cover size is an equilibrium, not a budget
- kind: proposition (observation)
- says: Adding modulus r=461 to the 88-modulus cover kills ~3.5 residual offsets (-3.5*boost/log N=-0.084 nats) but multiplies boost by 461/460 (+0.082 nats): net +0.00, a stationary point; at B=10^200 the cover spends log M~437 of ~461 available nats, so the digit budget is not tight and extra moduli are neutral to harmful. SOK: under a size cap the optimum shrinks M below the naive value (each nat removed from M buys a full nat of t-range but costs only ~0.2 nats of exponent).
- status: computed (see Doubts: the two quoted nat figures belong to different Q)
- uses: failure_exponent
- where: ch4_frontier.tex section sec:equilibrium, Observation obs:equilibrium; SOK section 2 "Range-bound vs compute-bound"
- matters: leftover digits buy nothing, so only better rounding mathematics or more compute can move E.

## lp_vacuous | LP relaxation is vacuous; exponent = rounding gap
- kind: proposition
- says: For the 88 moduli (3..~457) and the odd primes below Q, the set-cover LP (each modulus spreads a unit of weight over its classes) covers 100.00% of the primes at both Q=122,000 and Q=200,000 (HiGHS, ~2 s), because sum_r 1/(r-1)~1.86 gives 186% of the required mass. So LP duals certify nothing about integral covers, and the exponent is an integrality gap: at Q=122,000 the uncovered fraction goes 15.6% (=e^-1.86, "naive independent rounding") -> 7.56% (adaptive greedy, |U|=867 of 11,474) -> 0% (LP); each absolute percentage point removed is worth ~2.7 nats (a factor 15 in compute).
- status: computed (the 15.6% baseline is a first-order figure; see Doubts)
- uses: failure_exponent, partial_cover_search, ext:HiGHS
- where: ch4_frontier.tex section sec:lp, Proposition prop:lp, Corollary cor:rounding; appendix_data.tex (wp8/lp_bound.py)
- matters: reframes all difficulty as rounding and kills the "publish LP duals as optimality certificates" programme.

## door1_prize | Size of the rounding prize
- kind: empirical
- says: Uniform random class assignments of the 88 moduli at Q=122,000 give |U| mean 1,377 (12.0% of 11,474), sd 21.0 (below the independence prediction 34.8, i.e. negatively correlated); design entropy ln prod(r-1)=435.7 nats; annealed first-moment estimate of the best ensemble member u*=mu-sqrt(2 ln Omega)*sigma~758 vs greedy 867 (z=24.3 of 29.5 sd); one prime saved = 0.0240 nats, so the honest prize is ~2.6 nats (x14), and only if the annealed threshold is attainable (6.6% uncovered). SOK: random residues leave k0~0.74*pi(Q)/ln y, greedy+GRASP/SA reach ~0.60*k0 (here 867/1,377=0.63) then plateau; SOK 5.1 targets k~0.5*k0 (~689 here), below the annealed 758 (=0.55*k0).
- status: computed
- uses: lp_vacuous, failure_exponent
- where: ch4_frontier.tex section "How much is there to win?"; SOK sections 2 and 5.1
- matters: bounds the remaining value of better covers at this scale to 0-2.6 nats.

## door1_attacks | Exact and global attacks on the greedy cover
- kind: negative-result
- says: CP-SAT large-neighbourhood search freezing all but 7-15 moduli: 41 windows (<=300 s each) always matched, never beat |U|=867; per-window LP certificates (floor(LP)=incumbent coverage) proved 21 of 22 windows optimal (exception: a window of the smallest moduli, where the LP is loose); exact solves of the 30 largest and then the 44 largest moduli (half the cover) leave |U|=867. Belief propagation with decimation (validated against exhaustive enumeration: tracks exact E|U| to 0.7%, finds the exact optimum on a small instance) returns 874 at beta=1.5, worse at higher beta, i.e. 7 primes short of greedy. Naive BP at beta=4 predicts E|U|->35 (the LP fantasy): replica-symmetric BP inherits the LP's blindness to integrality; one-step RSB treatment is the flagged missing theory.
- status: computed
- uses: lp_vacuous, door1_prize, ext:CPSAT, ext:MezardMontanari
- where: ch4_frontier.tex section sec:door1 ("Exact local optimisation", "Global methods"); appendix_data.tex (d11_lns.py, d12_bp.py)
- matters: shows |U|=867 survives every exact or global method tried.

## landscape_verdict | Basin landscape; greedy near quenched optimum
- kind: verdict
- says: Random-start coordinate ascent lands at |U|~968 and 20 exact windows recover none of its 101-prime gap to greedy; independent ascent solutions agree on only 2.4% of class choices (chance level), so there is no backbone; the space is a field of mutually distant, locally-exact-stable basins spanning at least |U| in [867,980], and greedy's sequential adaptivity lands ~100 primes deeper than a typical basin. Verdict: at Q=122,000 with these moduli |U|=867 is at or very near the quenched optimum, 758 is an ensemble-existence heuristic, realistic prize 0 to 2.6 nats, probably nearer 0. IDEAS F3 corroborates on the Q=100,003 cover: three anneal seeds give identical |U|, steepest descent from 5 starts finds zero improving single swaps; an apparent E 17.07<17.28 was a convention mismatch.
- status: computed (evidence); judgement (verdict)
- uses: door1_attacks, door1_prize
- where: ch4_frontier.tex Observations obs:landscape and obs:door1; IDEAS.md F3
- matters: tells the team not to expect cheap gains from re-optimising covers at this benchmark.

## existence_sub100 | Sub-100-digit deserts exist in abundance
- kind: proposition (heuristic count)
- says: With no cover at all, E_random~110 at B=10^100, so density e^-110 and ~10^100*e^-110~10^52 qualifying integers below 10^100 (IDEAS100: e^-108, ~10^53, "true T(100,000) near 65-70 digits"); SOK: truth T(10^5)~10^53 (53 digits, +-5) from the GLvdtR law, with an absolute cover-and-scan floor of 38-49 digits. Nothing here is an existence obstruction; the difficulty is purely constructive.
- status: conjectural
- uses: failure_exponent, exhaustive_glvdtr
- where: ch5_barriers.tex introduction; IDEAS100.md header; SOK sections 5.4 and 6
- matters: establishes that sub-100 is a construction/search problem, not an impossibility.

## regime_I | Regime I: the cover fits inside the budget
- kind: proposition
- says: If A=log M<=log B the CRT progression supplies e^(log B - A) candidates and the search costs e^E. Optimum at Q=10^5, B=10^100: 44 moduli, M~10^79, |U|=1,060, boost=9.6, E=44.1, e^E~1.4*10^19 candidates ~9*10^5 GPU-years at ~5*10^5 candidates/s; an independent study (FRONTIER.md) gets E=43.66 (within 0.4 nats), and the SOK memo 44.1.
- status: computed
- uses: failure_exponent, frontier_table, gpu_throughput
- where: ch5_barriers.tex section "Two regimes", Regime I; SOK section 6
- matters: the only currently viable sub-100 route costs ~9*10^5 GPU-years, seven orders beyond plausible compute.

## regime_II | Regime II: oversized covers need small representatives
- kind: proposition
- says: If A>log B coverage becomes excellent: all 9,592 primes below 10^5 are covered by 355 moduli of total mass 1,019 digits, and with L=16 classes per modulus 420 moduli leave |U|=165, E=10.2, e^E~27,000 candidates (re-checked). Solutions exist (design entropy ~2,698 nats vs squeeze log(M/B)=2,630 nats, stated surplus +57 nats => ~e^57 valid (design, N) pairs below 10^100) but the density of designs with representative below B is e^-2630, so enumeration is out by ~1,100 orders of magnitude. Sub-100 becomes easy iff small CRT representatives can be found directly.
- status: computed (heuristic accounting; see Doubts on 2,698-2,630=68 vs +57)
- uses: failure_exponent, regime_I
- where: ch5_barriers.tex section "Two regimes", Regime II
- matters: pins the whole sub-100 problem down to "find a small representative of an oversized cover".

## subset_sum_density | Small representatives = density-1 modular subset-sum
- kind: proposition (reduction)
- says: CRT reconstruction is additive (idempotent basis), so finding a design whose representative lies in [0,B) is an inhomogeneous modular subset-sum problem with per-position choices (|C_r|=L), density d=2,698/2,630~1.026; low density (d<0.94) falls to lattice reduction (Lagarias-Odlyzko, Coster et al.), very high density to birthday/k-tree methods (Wagner), so density ~1 is the hard regime. Solution set ~2^82 inside ~2^3893 designs; meet-in-the-middle ~2^1897; Wagner k-tree with these list sizes ~2^938.
- status: conjectural (hardness is presumed; accounting is computed)
- uses: regime_II, ext:LagariasOdlyzko, ext:Coster, ext:Wagner
- where: ch5_barriers.tex section "The small-representative problem is modular subset-sum"; SOK section 5 item 3
- matters: names the first of the two hard problems sitting under the sub-100 record.

## thm_barrier | CRT-decoding barrier (heuristic theorem)
- kind: theorem
- says: GSS (Theorem 3) list-decodes CRT codes only with agreement mass A>sqrt(L*log B*P), P=sum over the pool of log p_i (checked numerically against the exact finite-ell optimum: ratio 1.001-1.004, pools 5*10^3..10^5, L in {1,2}); at pool bound 60,000, L=16: pool mass 59,816 nats, radius 14,845 nats vs cover mass 2,860 nats, i.e. 5.2x short. Barrier: for CRT-cover constructions of even N<B with g(N)>Q no parameter choice satisfies both (a) A<log B+log C(n,s)+s*log L (representatives exist) and (b) A>sqrt(L*log B*P). Table (pool bound, L: exists/decodes): 1,000, 1: 339/469=0.72; 60,000, 1: 570/3,711=0.15; 60,000, 16: 1,305/14,845=0.09; 10^6, 16: 1,697/60,651=0.03. Hence sub-100 via oversized covers needs list-recovery of CRT codes beyond the Johnson-type radius or a density-1 subset-sum algorithm.
- status: conjectural (labelled "Theorem; heuristic, first-moment"; radii re-computed here: 14,845 / 469 / 60,651)
- uses: subset_sum_density, regime_II, ext:GSS, ext:GoldreichRonSudan
- where: ch5_barriers.tex eq:gss, Theorem thm:barrier, Table tab:barrier; SOK section 5 item 3
- matters: shows the decoding shortcut to small representatives fails at every pool size.

## lll_threshold | LLL does not beat the Johnson-type radius
- kind: empirical
- says: CRT-decoding testbed (plant a small solution at controlled agreement mass, run LLL on a Howgrave-Graham-style lattice): at ell=30 recovery succeeds above 1.028*A_J and fails below; at ell=45 the threshold is ~1.02*A_J (converging to the theoretical radius from above); below threshold failure is total: 390 decodes returned zero non-planted roots even with 10^7 alternative solutions in the instance.
- status: computed
- uses: thm_barrier, ext:LLL
- where: ch5_barriers.tex section "Does lattice reduction beat the radius in practice?"; appendix_data.tex (phd/toy_crt/)
- matters: makes the Johnson-type radius a practical algorithmic boundary, not just a proof artefact.

## retractions | Two retracted claims in barrier analysis
- kind: negative-result
- says: (i) An earlier "open window" (pool sizes where representatives exist and the decoder works) is withdrawn: the radius was evaluated at one agreement size s and the existence bound at a different s (near 2n/3); requiring both at the same s closes the window at every pool size; an independent Legendre-transform re-derivation (verify_barrier.py, PR #31) reproduces the 14,845-nat radius and finds the best case still 28% short. (ii) Units error: sub-100 cost was reported as 5*10^4 GPU-years, corrected to ~9*10^5 (factor 18) because the candidate count was divided by the test rate (8.5*10^6/s) instead of the candidate rate (~17 tests per candidate); caught by an independent E=43.66.
- status: retracted
- uses: thm_barrier, regime_I
- where: ch5_barriers.tex section sec:retraction and Remark rem:units; SOK sections 5.3 and 6
- matters: marks numbers that must not be reused (SOK section 7 item 10 still quotes the old 5*10^4).

## sub100_verdict | Where sub-100 stands
- kind: verdict
- says: Regime I is the only viable route and costs E=44.1 (~9*10^5 GPU-years); the fundable frontier is 130-140 digits; two well-posed open problems sit under the record: CRT list-recovery beyond the Johnson-type radius for structured, solution-abundant instances, and modular subset-sum with per-position choices at density ~1 (2^82 solutions among 2^3893 designs); the barrier does not apply to a construction certifying compositeness by something other than a congruence divisor. SOK adds the wall formulas digits(N) >~ 0.57*phi*pi(Q)/ln(compute) (~132 digits at ln C=25, ~95 at 35 with phi=0.60; superseded at 100 digits by the cap-aware E~44) and the absolute floor digits >~ sqrt(c*pi(Q))/2.3, c in [0.8,1.3] = 38-49 digits; prediction: the record stalls in the 120-135-digit band.
- status: conjectural
- uses: regime_I, thm_barrier, lll_threshold, thm_closure
- where: ch5_barriers.tex section "Where this leaves sub-100"; SOK section 6 (Game T) and summary table
- matters: states exactly what would have to be broken for T(10^5)<10^100.

## probes_p1_p5 | Five bounded probes of non-covering mechanisms
- kind: negative-result
- says: Metric: offsets certified per nat of design entropy (covering ~4,400 per nat at r=3 falling to ~0.4 per nat at r~1,200). P1 prime-power moduli: p -> p^2 costs an extra log p nats and kills nothing new (class mod p^2 inside class mod p; at p=7: 227 inside 1,613), dominated. P2 polynomial value-set identities N=m^k-c: best k=2, c=398 kills 113 offsets below 10^5, costs (1-1/k)log B (115 nats at B=10^100), value set <=O(Q^(1/2)). P3 Sierpinski-Riesel N=k*2^n+c: one congruence class per fixed candidate, i.e. ordinary covering (cross-family correlation only a search-throughput trick). P4 norm forms/splitting: norms do not certify compositeness, usable splitting conditions are congruences mod discriminant-related moduli. P5 residual bias: |Ehat-E|<=0.1 over 3 covers and 1.2*10^9 candidates caps unexploited compositeness structure at 0.1 nats.
- status: computed
- uses: calibration, failure_exponent, cover_certificate
- where: ch6_closure.tex section sec:wp7; SOK section 5 item 6; appendix_data.tex (wp7_probes.md)
- matters: five predeclared-gate failures that motivated the closure theorem and leave a 3-condition test (>>sqrt(Q) offsets, o(ln r) nats/offset, invisible at current Ehat scales) for any future mechanism.

## schema_language | Construction schemes and the schema language L
- kind: proposition (definitions)
- says: A construction scheme is (F,C): a candidate family F (parameters in Z^m, poly-time map to even N<B, design cost log B - log|N(Theta)|) and a certificate map C giving a divisor witness 1<D<N-q; planted = algebraic identity, extracted = per-instance divisor discovery; E_eff = log of expected candidates. L ::= Congruence(d,a) | PolyImage(f in Z[m], deg<=4) | ExpFamily(N=j*a^n+c) | MultiPoly(A,B in Z[u_1..u_v], deg<=2, v<=3) | NormForm(K, disc<=10^4) | Cyclotomic(Phi_n, n<=200) | Compose(L,L) depth<=2; primality-defined and extraction mechanisms excluded. "Beats covering" = certify more than CEIL=3*sqrt(Q)~1,048 distinct prime offsets at marginal cost below covering's average 437 nats/10,607 offsets=0.041 nats per offset (not its endgame ~1.01); with design budget log B~461 a bulk mechanism needs <0.44 nats/offset.
- status: proved-in-text (definitions)
- uses: failure_exponent, cover_certificate
- where: ch6_closure.tex Definition def:scheme, section sec:grammar
- matters: turns "no construction beats covering" into a checkable statement.

## correlation_covering | Correlations are covering in disguise
- kind: lemma
- says: Proposition prop:shared: if d>1 divides both N-q1 and N-q2 (distinct odd primes <Q) then d | q1-q2, so every prime factor of d is <Q. Lemma lem:correlation: every two-complement divisor event is measurable w.r.t. the events {s | N-q}, s,q<Q; conditional on these and the sieve data, (H1) makes residual primality indicators independent, so success probability factorises as prod(1-p_q) and E_eff = design cost + sum p_q, the covering objective; the thesis adds that |Ehat-E|<=0.1 over 1.2*10^9 candidates bounds any violation.
- status: proved-in-text (proposition); conditional on H1 (lemma)
- uses: calibration, hl_heuristic
- where: ch6_closure.tex section "Lemma 2 first", Proposition prop:shared, Lemma lem:correlation; ch7_outlook.tex "The closure argument"
- matters: excludes "luck-shaping" mechanisms that would make leftovers jointly composite, except through small-prime divisors the sieve already harvests.

## lem_entropy | Entropy accounting for planted certificates
- kind: lemma
- says: For a planted (F,C) define the certified sub-image density delta_eff (density, in a generic width-Q window at height B, of integers for which the scheme can exhibit its planted witness with poly-range parameters); the amortised design cost per certified offset is at least log(1/delta_eff)-O(log log B), and for every family in L at least the covering cost. Proof is by cases (the family sections below); the o(1) terms and value-equidistribution inputs are listed as unfinished.
- status: conjectural (proof by cases partly done; o(1) terms open)
- uses: polyimage_ceiling, expfamily_budget, multipoly_cluster, multipoly_isolation, compose_empty, thm_closure
- where: ch6_closure.tex Lemma lem:entropy; "What remains genuinely conjectural" item 3; ch7_outlook.tex Door 3
- matters: the part of the closure theorem whose rigour is still to be completed.

## conj_h2 | Sub-modexp compositeness detection (H2)
- kind: open-problem
- says: Let n be uniform in [X,2X] with no prime factor below B_0=(log X)^O(1). Is there a randomised test of compositeness with soundness >=2/3 in time o(M(log X)*log X), cheaper than one modular exponentiation? Known: trial division/batch gcd (Bernstein) certify only the small-divisor mass (soundness o(1) on rough inputs); Jacobi symbols equidistribute on rough composites; Fermat, Euler, Miller-Rabin and Frobenius all cost Theta(M log X); no lower bound is known. A detector with cost c and recall rho speeds every search by 1/(c+(1-rho)) (c=0.1, rho=0.9 gives 5x).
- status: conjectural
- uses: failure_exponent, ext:Bernstein
- where: ch6_closure.tex section "Lemma 3: the detector floor", Conjecture conj:h2; ch7_outlook.tex open problem 1; appendix_data.tex (h2_open_problem.md)
- matters: the one genuinely open hypothesis of the closure theorem; a positive answer would speed every prime-hunting project.

## polyimage_ceiling | Univariate identity families are capped at sqrt(Q)
- kind: proposition
- says: A degree-d form takes at most Q^(1/d) values below Q, so it certifies at most 349 (d=2), 50 (d=3), 19 (d=4) or 7 (d=6) prime offsets at any budget, all below CEIL=1,048; hence every PolyImage with d>=2 is closed at any price, d=1 is ordinary covering, and Cyclotomic schemas fall under the same bound since phi(n)>=2 for n>=3.
- status: proved-in-text
- uses: schema_language, probes_p1_p5
- where: ch6_closure.tex section "Univariate identity families: a ceiling, not a price"; Table tab:closure
- matters: retires two families outright by pure counting.

## expfamily_budget | ExpFamily is 2.5x over the entropy budget
- kind: proposition
- says: For N=j*a^n+c a prime s certifies q when (q-c)*j^-1 lies in <a> mod s, confining n to one class mod ord_s(a): cost log ord_s(a) nats per offset. Floor: s | a^d-1 forces cost log d > log log_a s; over all s<10^5 the cheapest is log 5=1.609 (a=7, s=2801; re-checked 2801 | 7^5-1). Cheap certificates are scarce (a modulus s serves a fraction d/s of offsets; s=2801, d=5 gives ~20), so buying offsets cheapest-first for a in {2,3,5,7}: reaching 1,048 offsets costs 1,151 nats vs total design budget log B~461 (2.5x over), and at most 419 offsets are affordable.
- status: proved-in-text (exhaustive computation)
- uses: schema_language, referee_bug
- where: ch6_closure.tex section "ExpFamily: supply, not price", Observation obs:expfamily
- matters: closes the strongest non-covering family quantitatively rather than empirically.

## multipoly_cluster | MultiPoly with v<d: the cluster bound
- kind: proposition (first moment)
- says: For G=A*B homogeneous of total degree d in v variables, value-set exponent alpha=min(1,v/d), the expected number of k-element clusters of G-values in a width-Q window below X is ~X^alpha*(X^(alpha-1)*Q)^(k-1), so clusters exist only up to k_max(alpha)=1+floor(alpha*log X/((1-alpha)*log X-log Q)), finite iff alpha<1-log Q/log X. At X=10^200, Q=2*10^5 the threshold is alpha*=0.9735 and every v<d combination has alpha<=(d-1)/d<=0.9, k_max<=13 (table: (2,2,2): 2; (2,2,3): 4; (2,3,3): 2; (2,3,4): 5; (2,4,4),(3,3,4): 3; (2,4,5),(3,3,5): 6; (3,4,5): 3; all re-computed) versus ~18,000 offsets needed. Empirical check on (x^2+y^2+z^2)(x^2+2y^2+3z^2): alpha-hat=0.761 vs 0.750.
- status: conjectural (first-moment count; equidistribution assumed)
- uses: schema_language, lem_entropy
- where: ch6_closure.tex section "MultiPoly: clusters, isolation, and orbits" (cluster bound), Table tab:kmax
- matters: closes shared-variable identity families with v<d, which deliver only O(1) offsets per candidate.

## multipoly_isolation | MultiPoly with v>=d: isolation and symmetry
- kind: proposition (draft rigour)
- says: For v>=d value sets are window-dense (products of two binary quadratic forms represent ~9,300 of the 17,983 prime offsets below 2*10^5), so closure must come from access: around a solution u_0 the lattice points delta keeping G(u_0+delta) in a width-2Q window form a slab with extents Q*X^(-(d-1)/d) (gradient) and Q^(1/2)*X^(-(d-2)/(2d)) (Hessian directions), 10^-145 and 10^-47 at X=10^200, Q=2*10^5, d=4, so only delta=0: window solutions are pairwise isolated. Symmetry cannot help: preserving G conserves value (one offset per orbit); preserving one factor conserves its divisor (sieve-equivalent if small, isolated sliver if ~X^(1/2)); mixing both factors gives a coarse lattice of ~(log X)^2~2*10^5 points against a window of relative width 10^-195; solving G(u)=m for prescribed m is a nontrivial factorisation of m (the extraction horn).
- status: conjectural (the thesis marks this "draft rigour")
- uses: schema_language, multipoly_cluster
- where: ch6_closure.tex section "MultiPoly" (paragraphs "Above the threshold: isolation" and "Symmetry cannot help"); Table tab:closure
- matters: dense existence of multivariate certificates is non-constructive for geometric, not complexity-theoretic, reasons.

## compose_empty | Composition of two families is empty at scale
- kind: proposition
- says: Requiring N=m^2-c1 and N=m'^2-c2 forces (m-m')(m+m')=c1-c2, so m<=|c1-c2| whereas N~10^200 needs m~10^100; for c=398 and 4686 there are exactly five solutions, the largest with m=1073 (re-computed: (m,m')=(51,83),(126,142),(264,272),(534,538),(1071,1073)). So the only viable composition is family-plus-congruence: covering plus one family capped at 349 offsets. The scorer sums composition parts generously and Compose still peaked well below threshold.
- status: proved-in-text
- uses: polyimage_ceiling, schema_language
- where: ch6_closure.tex section "Compose: empty, not expensive"
- matters: closes depth-2 composition without any cost accounting.

## thm_closure | Divisor-Paradigm Closure theorem (target statement)
- kind: theorem
- says: For a construction scheme with planted certificate map expressible in L, assuming (H1) Hardy-Littlewood-type independence of complement primality given all divisibility data and (H2) no constant-soundness compositeness test on random rough inputs in o(one modular exponentiation), E_eff(F,C) >= E*(Q,B)-o(1) with E* the covering frontier; moreover extracted certificates on any window-dense family are factoring-equivalent, and certificate-free detection is already done at its known-optimal cost. Closure table: Congruence = covering baseline, composite d dominated (proved); PolyImage k>=2 <=349 offsets (proved, price-free); Cyclotomic (proved, price-free); ExpFamily 1,151 vs 461 nats, cap 419 (proved, quantitative); MultiPoly v<d k_max<=13 (first moment); MultiPoly v>=d isolation + orbit conservation, else extraction (draft rigour); NormForm reduces to MultiPoly (proved); Compose depth 2 empty at 10^200 (proved). Still conjectural: H1; H2; the o(1) terms in Lemma lem:entropy and the equidistribution inputs; mechanisms outside L.
- status: conjectural (stated target with proof skeleton, conditional on H1 and H2; the abstract says "at the level of rigour of a well-supported research programme")
- uses: correlation_covering, lem_entropy, conj_h2, polyimage_ceiling, expfamily_budget, multipoly_cluster, multipoly_isolation, compose_empty, falsification_engine
- where: ch6_closure.tex Theorem thm:closure, Table tab:closure, section "Verdict"; main.tex abstract
- matters: the thesis's main claim: within L nothing beats covering, so records are governed by the rounding gap and throughput.

## falsification_engine | Falsification engine: zero passes
- kind: negative-result
- says: Tier 0 reproduces hand-derived numbers from primitives (best m^2-c below 10^5: c=398, 113 offsets) and corrects covering's endgame to ~1.0 nats/offset at Q=122,000 (not 2.5). Tier 1 sweeps 13,661 schema instances over all seven families: zero passes (the first run's 16 "passes" were a filter-semantics leak: congruence-containing schemas scored against the escape criterion); near-miss board topped by ExpFamily at 3.1-4.2 nats per residual kill (~3x covering's endgame). Tier 2: an LLM-driven evolutionary search (AlphaEvolve-style) whose candidates emit only schema JSON (locked subprocess, no network, fresh-interpreter trusted grader, hand-audited passes; a program printing fitness=1.0 scores 0) gave 41 candidates, zero passes, only four families explored, stalling ~53x short of the bar at the ExpFamily optimum.
- status: computed
- uses: schema_language, expfamily_budget, probes_p1_p5, ext:AlphaEvolve
- where: ch6_closure.tex section sec:engine-falsify, Table tab:closure caption; appendix_data.tex (phd/wp9/engine/)
- matters: the empirical support for the closure claim.

## referee_bug | The referee broke before the theorem (50x overdraft)
- kind: verdict
- says: Within ~10 candidates the search lifted reported fitness 0.27 -> 0.46 inside ExpFamily by cutting mean per-offset cost 3.71 -> 2.20 nats, exploiting a scorer hole: ExpFamily was credited ~10,416 certifiable offsets but charged log ord per offset only against the 867 residual primes, so bulk coverage cost ~10,416*2.20~22,900 nats against a budget of 461 (~50x). The repair (charge every claimed offset; cap coverage at the affordable log B/cost) produced the design-entropy budget constraint, the average-cost benchmark (0.041 vs 1.01 nats/offset) and the ExpFamily purchase argument. Methodological finding: adversarial search is most valuable as referee hardening (candidates emit data not scores, separate trusted grader, quantities re-derived from primitives, passes hand-audited).
- status: computed (incident report)
- uses: falsification_engine, expfamily_budget, schema_language
- where: ch6_closure.tex section sec:referee, Remark rem:referee; ch1_introduction.tex "What is new here" item 5; ch7_outlook.tex closing note
- matters: shows the closure benchmarks were hardened by an adversary and why average-vs-marginal benchmarking matters.

## idea_dead_ends | Ideas tested and killed, with numbers
- kind: negative-result
- says: Planting composites via k-congruences (forcing s | N-q) costs density 1/s (ln s>=6.1 nats for s coprime to M) to save p~0.06 nats, which the sieve harvests for free (IDEAS F7; thesis: "divisor information is fully harvested", no free information on the k side). Composite/prime-power moduli: their classes are subsets of their prime factors' classes. Primorial shift N=q0+k*P# at a 161-digit modulus leaves |U|=1,468 (best q0=11) vs ~770 for greedy, ~+8 nats (B1). Maier-matrix positioning (B4) and Selberg-weighted residual selection (B7) subsumed by the cover; Chebyshev-bias exploitation ~10^-70 (B5); incremental modexp sharing across k impossible (C7); additive meet-in-the-middle on N dead (C9). Admissible-tuple designs called "covering again" (B6; contrast SOK section 7.1).
- status: computed (small-scale tests); proved-in-text (k-congruence cost)
- uses: correlation_covering, probes_p1_p5, cover_certificate
- where: IDEAS.md F7; IDEAS100.md B1, B4-B7, C7, C9; ch7_outlook.tex "The closure argument"
- matters: spares the team from re-deriving ten dead ends.

## three_doors | Only three doors remain
- kind: verdict
- says: After the closure theorem every improvement to a desert record passes through one of three doors: Door 1 mathematics (rounding gap, prize 0-2.6 nats i.e. up to x14, resistant), Door 2 compute (records are logarithmic in compute), Door 3 the paradigm (closed within L; the deliverable flips to finishing the theorem and keeping the falsification engine running). Auxiliary facts: divisor information is fully harvested (k-side congruences only relabel sub-progressions the sieve already scores) and correlation is covering (Proposition prop:shared), with P5 capping remaining structure at 0.1 nats.
- status: conjectural (conditional on thm_closure)
- uses: thm_closure, landscape_verdict, correlation_covering, door2_throughput
- where: ch7_outlook.tex section "The closure argument" and the Door 1/2/3 sections
- matters: the programme-level planning conclusion.

## door1_ideas | Untried Door-1 ensembles
- kind: open-problem
- says: Four untried routes to the rounding gap: (1) banded construction with an exact endgame (small moduli exact, middle band with second-moment control of pairwise overlaps, large moduli finished as an exact weighted matching against the uncovered set); (2) import Erdos-Rankin/FGKMT rounding constructively (open: what residual fraction is achievable at pi(Q)~10^4 with budget theta(457)?); (3) one-step replica-symmetry-breaking for an honest quenched threshold; (4) post the 867-prime benchmark (11,474 primes, 88 moduli) as a public optimisation challenge. Open problem 2: where is the quenched truth between greedy 7.56%, annealed ~6.6% and LP 0%?
- status: conjectural
- uses: landscape_verdict, door1_attacks, lower_bound_thm
- where: ch7_outlook.tex Door 1 list and open problem 2; SOK section 5 item 1
- matters: the only places where mathematics could still buy nats.

## door2_throughput | The compute door, priced
- kind: verdict
- says: Records are logarithmic in compute: each 10x buys 2.3 nats, "about four digits" on the threshold game (thesis and SOK). Engineering in hand: selective testing ported to GPU (2-3x), batch remainder-tree sieving to depth 10^9-10^10 (~1.5x per thesis; IDEAS100 A7/C3 say 2-3x), exact marginal stopping rule (5-15%). Volunteer computing: a peak-era Folding@home-scale network ~2*10^5 x the two-GPU fleet would put Q=200,000 about two days away (1% of it: months); silicon: a 660-bit Montgomery-modexp ASIC buys 10-100x an A100 per die, a rack ~e^5.5-e^8 over today's fleet at single-digit millions.
- status: conjectural (planning estimates)
- uses: gpu_throughput, engine_search, rung_ladder, ext:Bernstein, ext:PrimeGrid
- where: ch7_outlook.tex section "Door 2: throughput (compute)"; IDEAS100.md A7, C3; SOK section 5 item 2
- matters: unglamorous but completely reliable route to higher Q.

## quantum_grover | Grover crossover: no
- kind: negative-result
- says: Grover halves the exponent (e^E -> e^(E/2) oracle calls) but one oracle call evaluates ~|U| modular exponentiations of 660-bit numbers reversibly with no early exit, ~10^5-10^6 s at fault-tolerant estimates (Gidney-Ekera), versus 1.25*10^-6 s per classical candidate on the fleet. Quantum wins only when E>E*=2*log[(C_q/W_q)(W_c/C_c)]: E*~55 (one machine, C_q=10^6 s), ~41 (1,000 machines), ~27 (1,000 machines and a 1000x cheaper oracle) versus E=37.7 (Q=200,000) and 44.1 (sub-100); the three E* values re-computed. Conclusion: not needed and not helpful with non-miraculous constants; parked until C_q approaches seconds.
- status: computed (accounting)
- uses: failure_exponent, rung_ladder, regime_I, ext:Grover, ext:GidneyEkera
- where: ch7_outlook.tex section "Do we need a quantum computer?", Table tab:quantum; SOK section 7 item 10; IDEAS100.md C4
- matters: removes quantum search from the near-term plan with numbers attached.

## staircase | Operation Staircase to g>200,000
- kind: verdict (plan)
- says: Costed budget-game path: now Q=140,009 (E~25, days); +1 week Q=150,000 (E=27.3, ~4 fleet-days after a 2-3x engine gain); +1 month Q~165,000 (E~30, "two to three fleet-weeks"); +1 quarter Q=175,000 (E=32.1, "1.4 fleet-years raw", 2-4 months with engine work and fleet growth; gate: stay in-house only if Door 1 delivered >=2 nats); the wall Q=190,000-200,000 (E=35.4-37.7) needs ~e^5.5 beyond step 4 via a few hundred swarm/volunteer GPUs for a quarter, an ASIC/FPGA rack, or 4 nats of Door-1 mathematics plus a 10x fleet. Parallel workers claim disjoint variant sets in a committed ledger.
- status: conjectural (plan; two of its time estimates disagree with Table tab:ladder, see Doubts)
- uses: rung_ladder, door1_ideas, door2_throughput, failed_campaigns
- where: ch7_outlook.tex section "Operation Staircase"
- matters: the thesis's recommended schedule for pushing budget-game records from 119,419 toward 200,000.

## wall_models | Predicted limits per game (SOK section 6)
- kind: verdict
- says: With g_max(X)~C*ln^2X*lnlnX, C~1.4: truth T(10^5)~10^53 (~53 digits, +-5; "our 150 digits is ~2.9x the logarithm of the truth") and R(10^200)~C*(460.5)^2*ln 460.5~1.8M (re-computed 1.82M); Game 1 unbounded. Cost identity p1*k~1.32*phi*pi(Q)/ln N (phi~0.60). T(10^5): ~140 digits (days) / ~130 (months) today, ~120-125 heroic, stall at 120-135, floor 38-49. R(10^200), range-bound: today's ceiling Q~170,000 (ln C=25), heroic ~250,000 (ln C=35), future ~450,000 (phi->0.45, ln C=45), i.e. ~25% of truth; the 119,419 record is ~70% of the 170k ceiling. Game 1: 10^7 in ~2 GPU-hours measured (replacing the older ECPP-era ~2.5M estimate). The 2026-11-22 note says the constant is no longer fitted and the ratio to ln^2X*lnlnX grows with size, so the "truth" g figures are too small (digits too large).
- status: conjectural
- uses: exhaustive_glvdtr, failure_exponent, regime_I, sub100_verdict, bls_complement
- where: SOK section 6 "THE WALL" and its summary table
- matters: the team's reference for how much headroom is left in each game.

## grh_dead | GRH route to g(N) theorems is dead
- kind: negative-result
- says: SOK section 7 item 3(i): even granting a proof of GRH, its sqrt(x) error term exceeds the main term on the record progressions by 10^65.6 (150 digits) and 10^95.9 (200 digits); at GRH's sieve level (which Bombieri-Vinogradov already gives) every linear-sieve floor is vacuous; only level-Q input beyond Elliott-Halberstam would certify even ~140-280 residuals against the ~830-870 achieved; a theorem about g(N) itself needs Hardy-Littlewood-strength input, i.e. H1. "GRH would move constants, not walls."
- status: computed (quantified in phd/wp10_grh_remark.md, which I did not read)
- uses: wp12_covering_thms, hl_heuristic, ext:GRH, ext:BombieriVinogradov, ext:ElliottHalberstam
- where: SOK Rev 4 addendum item 3; section 7 item 3(i)
- matters: no conditional theorem of the form "g(N)<=f(N)" is within reach at record scale; limits stay forecasts.

## sok_unexplored | Unplayed games and untested ideas
- kind: open-problem
- says: Untouched or partly open: singular-series (correlation-aware) cover design (rescore covers by prod_s(1-omega(s)/s)/(1-1/s)^k and re-anneal; "modest constant" expected) and IDEAS100 B8/C8 variance-maximising covers; aggregate/sublinear compositeness certificates (batch-gcd/product-tree style); neighbouring record categories: S(q)=least N with g(N)=q exactly (thesis: T(Q)=min_{q>Q}S(q), 130 orders of magnitude between 4*10^18 and 10^150 unexplored), double deserts (g1,g2 both large), Lemoine deserts (odd N=p+2q), odd-Goldbach three-prime deserts; science from ~10^8 PRP-tested complements (HL k-tuple corrections); complexity placement ("exists even N<B with g(N)>Q" NP-hard?); machine-checked proof of the verifier or of IsLeast {p | p.Prime and (N-p).Prime} g; IDEAS100 C1 (BKZ/CVP residue assignment), C5 (learned k-prioritisation), C6 (FFT-shared catalog sieve), C10 (TPU bigints) untested; E9: if C1+C8+C5 together exceed ~5 nats, 105-110 digits enters fleet range.
- status: conjectural
- uses: cert_semantics, correlation_covering, thm_closure
- where: SOK section 7 items 1, 5, 6, 7, 8, 9; ch7_outlook.tex open problem 6; IDEAS100.md C1, C5, C6, C8, C10, E9
- matters: the list of directions nobody has tried, including free first-ever record categories.

---

## Dependency notes

1. Unconditional theory: Dirichlet's theorem (ext) plus congruence certificates (cover_certificate) give true Goldbach numbers with g>=Q (cover_realisation); feeding in the FGKMT interval covering (ext) and Linnik (ext) gives g >> log N log_2 N log_4 N/log_3 N (lower_bound_thm); wp12_covering_thms refines this for primes-only covers; sandwich_open is what remains between that and the GLvdtR conjecture.
2. Certification: cover congruences settle claim (a) (cover_certificate, partial_cover_search); an exhibited prime complement plus ECPP settles (b),(c) (cert_semantics); bls_complement replaces ECPP by a one-modexp N-1 proof, which is why the height record jumped to 10,000,141.
3. Price of a record: partial_cover_search plus the Mertens/HL heuristic (hl_heuristic) give failure_exponent; calibration (1.2e9 candidates, supplied by failed_campaigns) validates it; engine_search plus gpu_throughput convert compute into nats; ratchet turns that into rec_threshold and rec_budget.
4. Frontier arithmetic: failure_exponent plus greedy covers give frontier_table and rung_ladder; equilibrium explains why spare digits do not help; the price list inside frontier_table and the ladder feed staircase.
5. Rounding gap: lp_vacuous (sum 1/(r-1)=1.86 -> LP covers 100%) makes the exponent an integrality gap; door1_prize bounds the prize at 0-2.6 nats; door1_attacks and landscape_verdict show greedy is at or near the quenched optimum; door1_ideas lists what is untried.
6. Sub-100 wall: regime_I (E=44.1, ~9e5 GPU-years) forces oversized covers (regime_II, E=10.2), which need small CRT representatives (subset_sum_density, density 1.026) or CRT decoding (thm_barrier, 5.2x short, lll_threshold); retractions record what was wrong; sub100_verdict summarises; existence_sub100 shows the problem is constructive only.
7. Closure: correlation_covering (given H1) plus lem_entropy by cases (polyimage_ceiling, expfamily_budget, multipoly_cluster, multipoly_isolation, compose_empty) plus conj_h2 give thm_closure, which yields three_doors.
8. Adversarial audit: schema_language -> falsification_engine -> referee_bug -> corrected benchmark (average 0.041 nats/offset) and budget constraint -> expfamily_budget; probes_p1_p5 and calibration supply the 0.1-nat residual-bias cap used in correlation_covering.
9. Height game: complete covers plus the N-1-form complement (bls_complement) remove the certification wall of rec_height; remaining cost is PRP throughput and complete-cover length (greedy ~0.72*x*ln^2 x, theorem ~1.349*x*ln x in wp12_covering_thms).
10. Limits are forecasts: exhaustive_glvdtr (C~1.4, ceiling model) feeds wall_models (T(10^5)~10^53, R(10^200)~1.8M); grh_dead says no theorem about g(N) without H1-strength input; so every limit rests on hl_heuristic and the GLvdtR conjecture, not on a proved bound.

---

## Doubts

**A. Status and rigour**
1. No Lean-checked statement exists in these files (SOK 7.8: "Not yet done"). Many items called theorems are heuristic: thm_barrier ("heuristic, first-moment"), thm_closure (target statement, conditional on H1 and H2), multipoly_cluster and multipoly_isolation (first moment / "draft rigour"), lem_entropy (o(1) terms open).
2. thm_closure scope: (i) NormForm is "proved" only by reduction to MultiPoly, whose v>=d half is draft rigour; (ii) E* is the covering frontier, but the best covering is unknown by 0-2.6 nats (Door 1), so "nothing beats covering" is relative to an unknown optimum; (iii) "beats covering" is defined through covering's average cost 0.041 nats/offset and CEIL=3*sqrt(Q); a hybrid (covering + one capped family) is only mentioned, not priced. P2 at B=10^100 costs 115 nats for 113 kills ~1.02 nats/kill vs covering's endgame ~1.0 (different Q): a near-tie on the marginal benchmark; (iv) mechanisms outside L are untreated (the thesis says so).
3. Calibration logic: Ehat is defined as (mean survivors per candidate) x (measured pass rate), a first-moment quantity (expected number of prime complements). The closure text uses |Ehat-E|<=0.1 to bound hidden correlation/structure in the JOINT all-composite probability, which a first-moment match does not obviously constrain. The joint test is the hit tally (IDEAS F1: 2 hits vs ~2.1 expected; SOK: 7 hits at 0.25x-3.0x of E), statistically weak (+-0.5 nats per hit). Also the known second-order correction (exact density, +0.2 nats at 195 digits) exceeds the quoted 0.1-nat tolerance. SOK 7.1 itself says the 0.1 bound covers only "accidental" correlation in non-designed covers.
4. wp12_covering_thms and grh_dead are asserted in SOK only; their proofs/numbers live in phd/wp12_*.md and phd/wp10_*.md, which were not read.
5. Door-1 verdict ("greedy at or near the quenched optimum") rests on one benchmark (Q=122,000, 88 moduli) plus IDEAS F3's single-swap stability at Q=100,003; the annealed 758 uses a Gaussian tail out to 29.5 sigma on a bounded count.
6. Statuses of H1 and H2: conj_h2 is phrased as a question ("does there exist a test...?") while hypothesis (H2) in thm_closure asserts the negative answer; the thesis also says a positive answer "breaks the cost floor, not the covering monopoly", so why H2 is a hypothesis of the main inequality (rather than only of the "certificate-free" clause) is not spelled out.

**B. Contradictions between files / outdated material**
7. Budget-game bookkeeping: Table tab:records lists R(10^200)=112,249 as an incumbent, but the 199-digit g=119,419 integer is <10^199<10^200, so R(10^200)>=119,419 by the thesis's own definition; the naming-caution remark calls 119,419 "the smaller value" (it is larger); SOK calls the 112,249 run a negative result. The task brief's "largest known ~158,209" for N<10^200 appears in none of the assigned files (a grep of the two worktrees found 158209 only inside data files, e.g. a prime list in constructions/wall_1M_199d.json, not in any .md/.tex text). By my own interpolation of Table tab:ladder (E=27.34 at 150,000 and 32.07 at 175,000), Q~158,209 would be E~28.9, e^E~3.5e12, ~50 fleet-days at 7.9e5 candidates/s (not stated in the text).
8. Height game: the thesis (July 2026) gives 1,157,341 at 2,480 digits as the height incumbent and calls the regime certification-bound; SOK rev 4 (2026-11-21) supersedes this (g=10,000,141 at 61,329 digits, certification free). SOK sections 5.5, 6, 7.2, 7.8 carry arrows marking what changed.
9. SOK section 7.10 (quantum) still quotes the retracted "~5*10^4 GPU-years" and calls Grover "trivial if fault-tolerant hardware exists"; the thesis quantifies the crossover (E*~41-55 vs E=44.1) and concludes no. IDEAS100 C4 ("~10^3 logical qubits, 2040s") is likewise superseded.
10. Correlation shaping: the thesis (ch6, ch7) says correlation is covering and "luck-shaping has no purchase", IDEAS100 B6 says inadmissible-tuple design is "equivalent, not new", but SOK 7.1 says designing the residual set for inadmissibility modulo primes OUTSIDE the cover provably raises the all-composite probability and "nobody has ever optimized for it" (modest constant expected); IDEAS100 B8/C8 measure a free ~0.3-nat lognormal bonus and ask whether cover design can fatten it.
11. SOK section 6 vs thesis ladder: SOK's "today's ceiling Q~170,000" (ln C=25, phi=0.60) vs Table tab:ladder, where E=25 corresponds to Q~140,000 (Operation Staircase step 1 agrees with the ladder). SOK's three estimates of the true T(10^5) also differ: ~10^53 (GLvdtR law), IDEAS100 "65-70 digits" (consistent with E_random~108-110), while the thesis's own no-cover formula 2*pi(Q)/ln N would put the first qualifying N near 10^60.
12. Ladder naming: thesis ratchet 195 -> 179 -> 150 digits vs SOK 193 -> 186 -> 179 (probably different sub-ladders, not stated).

**C. Internal numeric inconsistencies (my re-computation)**
13. Corollary cor:rounding calls 15.6% (=e^-1.86) "naive independent rounding", but the thesis's own uniform-random sample gives mean |U|=1,377 = 12.0% of 11,474 (sd 34.8 under independence corresponds to p=0.12, and prod(1-1/(r-1)) over the moduli = 0.120). So the true "doing nothing clever" baseline is 12.0%, greedy's 7.56% is a factor 1.6 (not a halving) below it, and the "greedy sits halfway, in halvings" remark depends on the first-order figure.
14. obs:equilibrium: -0.084 nats (3.5 kills, boost~11, log N~458-461) and +0.082 nats do not belong to the same Q: the boost side equals E*ln(461/460), which is +0.082 only for E~37.7 (Q=200,000) and +0.045 for E=20.83 (Q=122,000); at Q=122,000 the net would be about -0.04, not 0.
15. Moduli count: "88 moduli 3,5,...,457" but pi(457)=88 counts the prime 2, so 3..457 are 87 odd primes; the quoted log M~437 and ln prod(r-1)=435.7 fit 3..461 (436.8, 435.1) rather than 3..457 (430.7, 429.0), and 461 is the modulus the same section says is "added". The sum 1/(r-1)=1.86 fits either.
16. regime_II: design entropy 2,698 minus squeeze 2,630 is 68 nats, not the stated surplus +57 (=2^82, e^56.8); the density d=1.026 uses 2,698/2,630.
17. E_random: ch5 says ~110 (IDEAS100 108) at 10^100 for "no cover", but the thesis's own formula with empty cover (boost=2) gives 2*9,591/ln(10^100)=83.3; the derivation of 110 is not given (the conclusion "10^52 integers exist" is only strengthened if 83 is right).
18. E at 100 digits is 41.3 (Table tab:frontier, IDEAS100), 44.1 (Table tab:menu and ch5), 43.66 (independent study); the thesis does not say that the larger values include k-room (progression length) while the frontier table does not.
19. Staircase vs ladder: step 3 (Q~165,000, E~30) is "two to three fleet-weeks", but e^30/7.9e5 s ~157 days raw, ~7.5-11 weeks even with a 2-3x engine gain; step 4 calls 3.4 years (ladder) "1.4 fleet-years raw", which equals 3.4/2.4, i.e. already includes the engine gain. Also unclear whether the 7.9e5 candidates/s (=185k+604k, IDEAS100 E5 measured on the 150-digit run) was re-measured at 199 digits; modexp cost grows super-linearly in operand size, so ladder times could be optimistic and the 100-140-digit prices pessimistic.
20. "Each 10x buys 2.3 nats, about four digits" (ch7, SOK 5.2) vs the thesis's own tables: 0.15-0.43 nats/digit, i.e. 2.3 nats = 5-15 digits; IDEAS.md header and F1 say "one digit per ~2.3 nats", which is neither.
21. Engine numbers: selective testing "net about 3x" but 9.2x raw gain x 0.276 retained mass = 2.5x; survivor-ordering "factor 1.83 in expected time-to-first-hit" is, per IDEAS F2, a conditional-discovery gain (full-sweep expectation gain ~8%); batch remainder-tree "1.5x" (thesis) vs "2-3x" (IDEAS100 A7/C3); sieve-depth/scan rates are "thousand candidates per second" in ch3 (901 vs 816; 1,772 -> 16,300) but "k/s" in IDEAS F5 for a 30k-k CPU sweep, so a factor-1000 unit slip is possible.
22. ch6 section sec:wp7 still quotes covering's tail cost as ~0.4 offsets/nat (2.5 nats/offset) while its own Tier 0 later says the correct endgame figure is ~1.0 nats/offset at Q=122,000 ("not the 2.5 quoted earlier from a different target").
23. Campaign 3: 4.0e8 candidates with survival 0.93 (lambda~0.073) vs e^E=1.1e9 for Q=122,000 in the ladder (lambda would be ~0.36, survival ~0.70); presumably raw vs hit-mass-weighted candidates (selective testing), but the table does not say.
24. IDEAS100 E9: e^41.3 at 10^7 k/s is ~2,700 years, not "~900 A100-years" (900 would need ~3*10^7 k/s).
25. ch1 says every Table-1 entry was verified twice (pipeline + independent verifier), but the appendix marks only the 150-digit and 199-digit records "re-verified"; the others say "witnesses + ECPP".
26. The bibliography contains entries never cited in the chapters (Juhasz-Bartalos arXiv:2510.21870 on ranking minimal primes; Moser-Tardos; Cornacchia; Zsigmondy), suggesting dropped sections; the Juhasz-Bartalos prediction results are not engaged anywhere.

**D. Not read / checks performed**
27. Not read: RESULTS.md, FRONTIER.md, PROPOSAL_NEXT_CAMPAIGNS.md, phd/*.md (WP3, WP7, WP8-WP12, wp10 GRH remark, RESEARCH_LOG), proth/README.md, ceiling_model.py and the record directories; entries citing them rely on the three .md files and the thesis only.
28. Independent spot-checks I ran (scripts in `<scratchpad>/gbmap_thesis_checks/`): g(27!+28)=71 and its witnesses; g(30030)=17, g(m_43)=89; all quoted g values are prime; nextprime(1,113,106)=1,113,137 and nextprime(16,045,848)=16,045,849; pi(122,000)=11,475, pi(200,000)=17,984, pi(10^5)=9,592; sum 1/(r-1)=1.855 and boost=11.0 for 3..457; ladder E values vs |U|*11/ln(10^199); Regime-I/II E values (44.2, 10.2); GSS radii (14,845; 469; 60,651); k_max table and alpha*=0.9735; c=398/4686 five solutions; 2801 | 7^5-1; menu A100-year figures (~$10,000-10,600 per A100-year); Grover E* (54.8, 41.0, 27.2); T(10^5) from the C=1.4 law = 10^52.96 and R(10^200)=1.82M. All agreed except where listed in section C.
