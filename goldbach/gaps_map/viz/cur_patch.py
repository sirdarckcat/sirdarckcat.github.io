# Changes to boxes that were already on the 23 Nov map.  Each patched box is marked "changed" (since = "upd").
# repl: {field: [(old text, new text)]} with the old text required to be present; *_add: text appended; any other key: replaced.
PATCH = {
# ---------------- Lean side
"r_158209": dict(
  repl={"gist": [("The standing record.", "The record from 23 to 24 Nov; 160,357 now stands above it.")],
        "detail": [("a 27-step elliptic-curve primality certificate", "a 26-step elliptic-curve primality certificate")],
        "note": [("This is the number the project is trying to beat. The stretch target of 213,070 is 10% of the research team's modelled ceiling of about 2.13 million.",
                  "Superseded on 24 Nov by 160,357. It was the first record built on 89 covering moduli, and the next one kept that pattern.")]}),
"r_earlier": dict(
  repl={"gist": [("The ladder before today's record,", "The ladder before the standing record,")],
        "detail": [("a primality chain of 18 to 32 steps", "a primality chain of 17 to 31 steps")],
        "note": [("seven records between 2026-11-22 and 2026-11-23", "six record-setting finds between 2026-11-22 and 2026-11-24, counting the two that have their own boxes")]}),
"r_rank": dict(
  repl={"title": [("up to 10^11", "up to 10^12")],
        "gist": [("The 39 even numbers up to 10^11", "The 42 even numbers up to 10^12"),
                 ("They agree with OEIS A025018 and A025019.", "They agree with terms 2 to 43 of OEIS A025018 and A025019.")],
        "detail": [("That no smaller number does better is a scan, not a theorem.",
                    "That no smaller number does better is a theorem below 2^25 (see the sieve box); beyond it, up to 10^12, it is a scan, not a theorem.")],
        "note": [("below 10^11", "below 10^12")]}),
"c_layers": dict(
  detail_add="Since 24 Nov the classes are stated on their own (exists_classes_of_layers), before the numbers N are built from them, so the covering bound can be read as a statement about the cover depth."),
"l_cb_sharp": dict(
  repl={"note": [("The record 158,209 is about 40 times larger", "The record 160,357 is about 42 times larger")]},
  detail_add="Since 24 Nov the file also states the cover itself, in depth form, as its own theorem; this one is built from it.",
  note_add=" Superseded on 25 Nov: formally in the kernel for every constant and in the order ln X·(ln ln X)²/(150000 (ln ln ln X)²) (boxes ‘The covering bound for every constant, in the kernel’ and ‘The order of the covering bound in the kernel’)."),
"l_cb073": dict(
  detail_add="Since 24 Nov it is built from the cover stated in depth form."),
# ---------------- length of the primality chains: counted as applications of the step check (the Lean files and the record READMEs count them so)
"x_ecpp_step": dict(repl={"gist": [("A chain of 27 steps proves", "A chain of 26 steps proves")]}),
# ---------------- research side (from the three delta ledgers of 25 Nov)
"e_records": dict(
  repl={"detail": [("The GPU fleet raised the budget record to 158,209 by 2026-11-23.", "The GPU fleet raised the budget record to 158,209 on 2026-11-23 and to 160,357 on 2026-11-24.")]},
  detail_add="The fleet's hits file was last updated on 23 Nov 02:10 UTC; near-miss records are in each record's own folder."),
"e_fleet200": dict(
  repl={"gist": [("The budget record rose 119,419 → 125,269 → 133,981 → 146,191 → 157,837 → 158,209 between 2026-11-22 and 2026-11-23.", "The budget record rose 125,269 → 133,981 → 146,191 → 157,837 → 158,209 → 160,357 between 2026-11-22 and 2026-11-24 (the 119,419 before them was a July CPU record).")],
        "detail": [("at 29 million effective full-weight members per second.", "at 29 million effective full-weight members per second; the planning model now uses 8.9 days from 24 Nov 04:05 UTC at 52 million (model units), and the fleet shrank on 24 Nov (see ‘The fleet now’)."),
                   ("so a design aimed at 170,000 produced the 158,209 record.", "so designs aimed at 170,000 produced the 158,209 and 160,357 records.")]},
  detail_add="The covers now include the 491 set (first 88 odd primes and 491) and the first-88 set on the smaller cards.",
  chips_add=["491 family"]),
"m_portfolio": dict(
  repl={"gist": [("From a record of 157,837 with about 10 fleet-days left, the expected final record is about 169,000–172,500 (7.9–8.1% of the ceiling).", "The planning model now expects a final record of about 175,000–176,000 (8.2% of the ceiling), with a chance of the 10% target below 0.01%; the earlier figure was 169,000–172,500 from a record of 157,837 with about 10 fleet-days left.")],
        "note": [("The standing record 158,209 sits below the expected final value", "The standing record 160,357 sits below the expected final value")]},
  detail_add="The newer figure comes from a faster measured rate (52 million effective members per second from 24 Nov 04:05 UTC) and the family-B designs (+1,000); it does not include the fleet's shrinking on 24 Nov. See ‘What each design level buys’ and ‘The fleet now’."),
"m_price": dict(
  detail_add="The ‘about 4,100’ depends on the cover's uncovered primes above the design level: at Q = 60,000 the mean landing was 3,766 above for family B against 3,071 for A (41 against 55 uncovered primes in the next 4,000). The fleet-days column assumes 1,262 rows on 88 moduli and an older engine; the fleet's own logs give 0.29 design hits a day at 7 GPUs, 3.7 times faster than priced."),
"m_density": dict(
  detail_add="The model counts rows below the design level Q only. The final record also depends on the uncovered primes above Q: a success must survive each with probability 1 − p, confirmed at Q = 60,000 (1,184 against 1,186 successes, landing shifted ×1.23); see ‘Rows above the design level’."),
"e_selective": dict(
  detail_add="Since 23 Nov the 3% rule holds only on the L4s and the T4: the RTX cards keep the emptiest 1.5% (keep fraction 0.985, design hits a second ×1.10 over 0.97), and the L4 test at 0.985 failed (×0.9865). The sieve depth was re-optimised jointly with the keep fraction for today's engine: 10^8 stays (the best alternative is +1.2% at keep fraction 0.99; deeper sieves lose)."),
"e_gpu": dict(
  detail_add="Since 23 Nov: 24.6M tests a second with the 29-bit kernel (+5.7% on the 23 Nov baseline) and 23.4M for the best 28-bit step; a window's sieve phase fell from 83.7 to 44.4 ms and an RTX batch from 0.945 to about 0.73 s (see ‘The GPU sieve chain’); a new IFMA CPU test for 300 to 400 digits is 8 to 12 times gmpy2."),
"e_cover_opt": dict(
  repl={"detail": [("There is no closed formula for the optimum and no proof of a floor: every claim of optimality is empirical.", "Until 24 Nov there was no closed formula for the optimum and no proof of a floor; now there is a derived predictor (1,221 rows at 170,000, 1,584 at 213,070, within 2% of the best found), measured floors (1,214; 1,554 to 1,596), a certified floor of 777 rows (exhaustive) and a linear-programme floor of 1,170 for fixed small classes. The 89-prime optimum 1,248 is confirmed three ways (186 covers at 1,248); with 491 as the 89th prime the best is 1,245."),
                   ("Greedy gives 867 rows at Q = 122,000", "Greedy plus annealing gives 867 rows at Q = 122,000 (plain greedy 912)")]},
  detail_add="A greedy-plus-descent code (archipelago session) leaves 1,309 rows at the campaign's point against 1,248 tempered; tempering at 30 to 302 moduli reaches 0.78 to 0.88 · x ln² x."),
"m_rounding": dict(
  detail_add="Since 24 Nov door 1 is measured: at Q = 170,000 the best cover (1,248 rows) is 34 rows (0.83 nat, a factor of at most 2.3) above the measured floor 1,214, and at 213,070 the best (1,609) is within 1.3 nats of the floors 1,554 to 1,596. The ‘annealed first-moment threshold’ is explained: the first-moment count is off by 1.35·ln Q/ln x in the loss (it predicts about 790 rows at 170,000; 1,248 were found). The only theorem is the exhaustive floor of 777 rows."),
"m_doors": dict(
  repl={"gist": [("Door 1 looks near-exhausted", "Door 1 is measured to be nearly exhausted (a floor under every cover, within 0.8 nat of the best)")]},
  detail_add="The measurement is empirical; the only theorem, the exhaustive floor of 777 rows against the best cover's 1,248, is far from closing the door."),
"m_staircase": dict(
  repl={"note": [("seven records in two days.", "six record-setting finds in three days (22 to 24 Nov).")],
        "gist": [("or about 4 nats of rounding mathematics plus a 10× fleet.", "or a 10× fleet plus rounding mathematics, now measured at no more than 0.8 to 1.3 nats.")],
        "detail": [("(146,191, 157,837, 158,209)", "(146,191, 157,837, 158,209, 160,357)")]}),
"e_c15907": dict(
  repl={"detail": [("so where complete covers stop is unknown.", "so complete covers on the 89 primes end near 16,000 (by a measured count of covers), and 15,907 ≤ D(89) < 35,000 is proved by exhaustive search.")],
        "note": [("against 7.4% found by search", "against 7.5% found by search")]},
  detail_add="A 94th prime (499) does not pay; a local search around the cover finds nothing; complete covers continue on larger sets to 41,659 (167 moduli, Lean-checked), 70,111 (238) and 98,731 (302)."),
"m_thm1": dict(
  detail_add="Since 24 Nov: a sketch for beating the constant exists (pairs of survivors struck by one large prime and a deletion argument, giving (1 + δ)·1.349 with δ about 0.1 measured; a Rödl nibble for any constant), certified covers reach 3.5 to 5 times the proved constant (up to 614,101 on 1,228 moduli), and the research session conjectures D(n) ≈ 1.1275 · r ln² r.",
  note_add=" Superseded in order on 25 Nov: a structured prefix gives r·ln² r·ln₃ r/(ln₂ r)² at paper level and r·ln² r/(9000 (ln₂ r)²) in the kernel (boxes ‘A structured prefix beats random classes’, ‘The order of the covering bound in the kernel’)."),
"m_thm2": dict(
  detail_add="A computed non-asymptotic bound at record size now exists too: D(89) < 35,000 by exhaustive search (4.6·10^8 nodes), and D(n) is known exactly to n = 35. Lean shows that depth below the next prime squared minus two for every n would imply Goldbach."),
"m_lower": dict(
  detail_add="The research session conjectured on 24 Nov that divisibility by primes up to ln N forces a least summand of (1.1275 + o(1))·ln N·(ln ln N)²; it withdrew that on 25 Nov and now has the order ln N·(ln ln N)²/ln ln ln N (heuristic), which is not derived either. The least summand can be as large as c·ln N·(ln₂N)²·ln₄N/(ln₃N)² for infinitely many N at paper level, and ln N·(ln₂N)²/(150000 (ln₃N)²) in the kernel (boxes ‘A structured prefix beats random classes’, ‘The order of the covering bound in the kernel’), above the earlier proved order and below ln²N·ln ln N."),
"m_ceiling": dict(
  repl={"note": [("The standing record 158,209 is 7.43% of it.", "The standing record 160,357 is 7.53% of it.")]},
  detail_add="Lean's independent closed formula (one constant fitted on the scan of every even N up to 10^12) puts the expected maximum below 10^200 at 2,133,689, 0.14% above; the ceiling is known to about 0.4%."),
"m_h1": dict(
  detail_add="A direct test at Q = 60,000 (1,184 against 1,186 successes) agrees with (1 − p)^rows, and a closed formula with one fitted constant for the dependence between the rows of one N reproduces the prize counts to within 0.1 nats."),
"s_prize": dict(
  detail_add="The 1/ln² z regularity of the table is explained: if the primes between two depths kill rows independently the deep table is the shallow one at another temperature (Lean's thinning law proves independence a safe direction above Q, and the table's depths lie below Q), and rows fall like (ln z)^−a with a = 2.0 to 2.1 (measured β 1.22 to 1.32); the whole table follows from one shallow table within 0.4 nats from depth 5,000. The prize is the same function as the floor under covers."),
"s_score": dict(
  detail_add="Row sharing by convolution is now priced: with the primes of a stretch known a number needs about 68 marks, four times cheaper per number but a million times worse per operation, and it excludes covers (see ‘Neighbouring N share the prime map’)."),
"s_ladder": dict(
  repl={"gist": [("Eight rungs:", "Nine rungs:"), ("(3) a fully enumerable toy, to do;", "(3) a fully enumerable toy, done over the integers (not in F_q[x]);"), ("(8) problem (P′), open.", "(8) problem (P′), open; (9) a provable lower bound for pure covers, done (16,981).")],
        "detail": [("as of 2026-11-23.", "as of 2026-11-25.")]}),
"s_verdict": dict(
  repl={"note": [("As of 23 November:", "As of 25 November:")]},
  detail_add="Update of 25 Nov: still none known, none ruled out. By measurement the covers in use are the best there are (better covers are not a way to 10%); the numbers wanted exist (about 10^175 even N below 10^200 have g ≥ 213,070) but 10^200 only pins residues up to 463; a perfect search at the fleet's sieve depth stops near 16% of the ceiling. New: the SAT reduction for arbitrary rows, row sharing priced and found incompatible with covers, and no lower bound against algorithms on prime rows from any known technique."),
"v_brainstorm": dict(
  detail_add="One later conclusion of the brainstorm README has since been retracted: ‘sharp designs within 100–200 of the weighted objective, vectors stay’ was wrong; the same weights showed near-optimal covers differing by 9 to 11 weighted rows (family B, about +1,000 expected record, about 0.2 nat), still consistent with ‘nothing worth a nat’."),
"m_errata": dict(
  detail_add="Added since: the soft-threshold conclusion of the brainstorm README (retracted); the D(n) counts for n = 25 to 27 (withdrawn after an array overflow, rerun with the same answers); the law's limit constant (1.349, then open, then 1.1275 within two hours, and since qualified by the referee check); marks per N at 170,000 (83, then 68); 4,500 corrected to 4,700 digits for a forced gap of 10^6; the planning horizon (8.5 and 8.2 days corrected to 8.9; 29M to 52M members a second); the entropy-zero plateau estimate (about 10 rows early at 170,000). On this map: the primality chains are 26 steps for 158,209 and 21 for 160,357 (the first version of the map said 27), and the earlier ladder's range is 17 to 31 steps."),
"e_threshold": dict(
  detail_add="The threshold game at g ≥ 10^6 has started as a cover only (629 moduli, 3,028 rows left): nothing found or certified."),
# ---------------- records quoted in other boxes
"r_cover15907": dict(
  repl={"detail": [("The record 158,209 reaches about ten times further", "The record 160,357 reaches about ten times further")]}),
"r_cover_more": dict(
  repl={"note": [("The record 158,209 is still about ten times higher because it adds luck.", "The record 160,357 is still about nine times higher than the best of these (16,981) because it adds luck.")]}),
}
