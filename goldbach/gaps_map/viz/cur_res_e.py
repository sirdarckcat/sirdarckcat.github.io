# Added 2026-11-25, after the first build of the update: the consultant session's own draft (requested by the research session).
def D(short, why, src): return (short, why, "doc", src)
RE = {
"d_pairproof": dict(group="dep", status="paper", impact="bound", since="new",
  title="A draft proof of a constant above 1.349: one prime striking two rows",
  gist="The sketch of the previous box made rigorous at paper level, at the research session's request: after random classes on the primes up to y/ln y, match survivors in pairs, each pair struck by one prime of (αy, y] that divides the difference of the two primes (a rainbow matching), and bound the matching by a deletion argument. With Lavrik-type Hardy–Littlewood for shifts of size about x and Selberg's upper bound for triples it gives classes striking every odd prime below c·y·ln y for every c below 1.3523, against the proved 1.3490.",
  detail="The survival weights of stage 1 cancel the Hardy–Littlewood singular series exactly (the identity C₂·∏(1 + 2/(p(p − 3)))·∏(1 − 1/(p − 2)²)·4/3 = 1 holds prime by prime), so the number of edges is what independent rows would give. The gain is small because Selberg's constant 48 for the triple count bounds the conflicts: the matching covers about 0.25% of the survivors. If every second moment had its predicted value the same argument would give 1.479, which agrees with the measured deletion fractions of the archipelago session (1.48 to 1.51). Named gaps: the precise form of the long-range almost-all theorem (Mikawa's range as quoted in the literature does not contain shifts that large; Lavrik's and Wolke's should), an averaging lemma for the weights over prime labels (outline only), and ineffective constants. Not formalisable in Lean.",
  note="Gives the sketch a number to compare with the measurements. It does not touch the record at 200 digits. The text was not checked by anyone else.",
  chips=["consultant's draft", "unchecked", "PAIR_COVER.md"],
  where=[["Write-up", "goldbach/gaps_map/PAIR_COVER.md (branch ccr-cdb2641a-5zg8un, commit 09ff251)"]],
  search="pair cover rainbow matching deletion Lavrik Selberg 1.3523 constant 1.349 proof draft"),
"d_capacity": dict(group="dep", status="heur", impact="bound", since="new",
  title="Why the ratio D/(x ln² x) should eventually fall: a top prime strikes only about ln x/ln ln x rows",
  gist="The research session doubted its own limit 1.1275 and the consultant checked the argument. Split the moduli into small ones (up to x/ω) and top ones. The small ones leave about 2C₂e^(−γ)·π(Q)/ln x rows alive; a complete cover needs the largest classes of the top primes to add up to that. With less than one alive row per class for primes near x the largest class holds only ln x/(ln ln x − 1) rows, so D(x) is at most about 1.349·x ln² x/(ln ln x − 1) and the ratio D/(x ln² x) tends to 0, not to 1.1275.",
  detail="Tested on real primes. Greedy covers reach D/(x ln² x) = 0.55 (x = 151), 0.66 (2,000), 0.72 (2·10⁴ to 10⁵). Greedy classes on the small moduli leave 0.72 to 0.74 of the alive rows a random choice leaves, flat from x = 300 to 10⁵, so the small moduli are not negligible at any size that can be computed (the cap on their gain falls only like 2/√ln x). At x = 2·10⁴ the largest top classes found add up to 7,361 against 8,041 for Poisson class sizes. Fitted to these two factors the model puts the maximum of D/(x ln² x) at x = 10⁵ to 10⁶ (0.73) and gives 0.69 at 10⁹, 0.62 at 10¹⁵, 0.52 at 10³⁰, 0.37 at 10¹²⁰ (shape, not value). Not proved: Poisson class sizes of the alive primes in progressions out to class size ln x/ln ln x (Hardy–Littlewood for k-tuples), and the lower tail of the alive count over the e^(x/ln x) choices of the small classes.",
  note="Turns 1.1275 into a plateau and says nothing changes at the sizes of the campaign (89 to 1,228 moduli). The argument was the research session's; the check and its numbers are the consultant's, and nobody else has read them.",
  chips=["consultant's check", "research session's argument", "unchecked"],
  where=[["Note", "goldbach/gaps_map/LIMIT_CHECK.md (branch ccr-cdb2641a-5zg8un, commit b90e85c)"], ["Scripts", "goldbach/gaps_map/data/limit_check/"]],
  search="capacity bound limit ln ln x plateau greedy 0.72 bulk top Poisson largest class 1.1275 falls ratio"),

}
RE_EDGES = {
"d_pairproof>d_nibble": D("makes the sketch rigorous", "The deletion argument and the rainbow matching of the sketch are written as lemmas, with the inputs and constants named.", "PAIR_COVER.md sections 2 to 6"),
"d_pairproof>d_depthform": D("improves the Lean constant", "The Lean theorem is the one-row-per-prime version with c below 1.349; the draft raises it to about 1.352.", "PAIR_COVER.md section 1"),
"d_pairproof>l_mertens3": D("first moment of the survivors", "The expected number of survivors after stage 1 is the number of rows times the Mertens product 2C₂e^(−γ)/ln y.", "PAIR_COVER.md section 3"),
"d_pairproof>d_pairs": D("same local identity", "The cancellation of survival weights against the singular series, prime by prime, is the identity Lean proves for pairs (sum_rho_mul_sigma), here also for triples.", "PAIR_COVER.md section 3; CoverPairs.lean"),
"d_pairproof>m_thm1": D("beyond the paper theorem", "The draft proves a constant above the 1.349 of the paper theorem, using a pair of rows per prime.", "PAIR_COVER.md section 0"),
"d_capacity>d_limit": D("challenges the limit", "The capacity bound makes the limit of the ratio 0 and the 0.72 to 0.9 seen a plateau; 1.1275 is not a limit of D(x)/(x ln² x).", "LIMIT_CHECK.md sections 0 and 2"),
"d_capacity>d_recursion": D("where the recursion may differ", "The price equation takes the spread of the alive rows to second order; the top primes need the tail of the class sizes at ln x/ln ln x. Not rederived.", "LIMIT_CHECK.md section 5"),
"d_capacity>d_greedy": D("tested on greedy covers", "Greedy covers on real primes give the plateau at 0.72 that the fitted model reproduces.", "LIMIT_CHECK.md section 3"),
"d_capacity>d_nibble": D("why a nibble stops", "Typical classes at the top hold less than one alive row, so the leftover of any procedure that uses typical classes is close to the first-moment leftover.", "LIMIT_CHECK.md section 4 (D)"),
"d_capacity>l_mertens3": D("first moment of the survivors", "The rows left alive by the small primes are the Mertens count 2C₂e^(−γ)·π(Q)/ln y.", "LIMIT_CHECK.md section 0"),
}
