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
}
RE_EDGES = {
"d_pairproof>d_nibble": D("makes the sketch rigorous", "The deletion argument and the rainbow matching of the sketch are written as lemmas, with the inputs and constants named.", "PAIR_COVER.md sections 2 to 6"),
"d_pairproof>d_depthform": D("improves the Lean constant", "The Lean theorem is the one-row-per-prime version with c below 1.349; the draft raises it to about 1.352.", "PAIR_COVER.md section 1"),
"d_pairproof>l_mertens3": D("first moment of the survivors", "The expected number of survivors after stage 1 is the number of rows times the Mertens product 2C₂e^(−γ)/ln y.", "PAIR_COVER.md section 3"),
"d_pairproof>d_pairs": D("same local identity", "The cancellation of survival weights against the singular series, prime by prime, is the identity Lean proves for pairs (sum_rho_mul_sigma), here also for triples.", "PAIR_COVER.md section 3; CoverPairs.lean"),
"d_pairproof>m_thm1": D("beyond the paper theorem", "The draft proves a constant above the 1.349 of the paper theorem, using a pair of rows per prime.", "PAIR_COVER.md section 0"),
}
