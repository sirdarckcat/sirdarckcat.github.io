# Edge texts for the Lean boxes added in the 2026-11-25 update.  key "A>B": A relies on B.
# 2-tuples (short, why) are links the reference tool finds; 4-tuples (short, why, kind, source) are added by hand
# (kind "direct": read in the proof text by hand, "doc": a document or docstring states it).
E_LEAN5 = {
# ---------------- the record 160,357
"r_160357>l_isleast": ("states", "The record is a statement about IsLeastSummand N 160357, the definition of the least Goldbach summand."),
"r_160357>x_least": ("closes with", "Same proof shape as every record: block checks for every prime below 160,357 plus primality of 160,357 and of N − 160,357 give the complete certificate."),
"r_160357>x_block": ("20 block checks", "The negative half, that no smaller prime is a summand, is twenty block checks, each re-run by the kernel."),
"r_160357>x_ecpp_step": ("21-step primality proof", "That N − 160,357 is prime is proved by a chain of 21 elliptic-curve steps, each checked by the one-step soundness theorem."),
# ---------------- the generator for A025018 and the kernel's sieve
"r_gen>l_isleast": ("records are least summands", "IsRecord N g says that g is the least Goldbach summand of N and larger than that of every smaller even number."),
"r_gen>l_primorial": ("the front always exists", "exists_isFront builds an even number that no prime below g has struck from multiples of a primorial, the same primorial-core lemma as the qualitative theorem."),
"r_walk>l_isleast": ("states", "mem_walk and beats_iff_wheels are statements about the least summand: N is announced exactly when its least summand exceeds the running maximum."),
"r_walk>l_cover": ("the same condition as a cover", "beats_iff_wheels is the exact two-way form of the covering certificate: N has no summand up to G exactly when its residues modulo the primes up to √N cover every prime q ≤ G. The 200-digit certificates establish it with about 90 small moduli.", "doc", "RecordWalk.lean header: \"This is the condition the 200-digit certificates establish\""),
"x_bitsieve>l_isleast": ("builds on", "The record-holder and ‘among the ten largest’ definitions of the sieve file are statements about the least Goldbach summand."),
"r_ranksieve>r_rank": ("fills the table", "The kernel-proved record holders below 2^25 are the first 26 entries of the record table: the sieve proves completeness where the table had a scan."),
"r_ranksieve>x_bitsieve": ("run by the kernel's sieve", "isRecordHolder_iff applies the sieve's chain theorems (mem_of_isRecordHolder, isRecordHolder_of_mem); every interval is a kernel evaluation.", "direct", "RankSieve.lean: the chain theorems are used after `open BitSieve`, a relative open that the reference tool does not resolve"),
# ---------------- the cover depth
"d_def>l_cover": ("strikes = covers", "A vector strikes a prime q when q lies in the class of some modulus r, so that r divides N − q for every N in those classes. That is the covering certificate's mechanism, turned into a function of the number of moduli.", "doc", "CoverDepth.lean header"),
"d_exact>d_def": ("states", "isDepth_n is the statement IsDepth for the first n odd primes."),
"d_exact>d_more": ("lower-bound certificate", "From nine moduli on, the lower half of each exact value is a CoversBelow certificate of the kind collected in the longer table."),
"d_more>d_def": ("lower bounds for the depth", "Each entry states CoversBelow for the odd primes up to the n-th, a lower bound for their depth."),
"d_841>d_def": ("uses the depth", "Each range states IsDepth for its list of moduli and reads off the summand bound."),
"d_841>d_exact": ("the nine exact depths", "The values 3, 5, 7, 19, 31, 43, 67, 103, 163 and 181 are the theorems isDepth_0 to isDepth_9, so the proof is a table lookup."),
"d_841>d_bounds": ("applies the depth bound", "Each range uses exists_isSummand_of_lt_sq: if the depth of the primes up to the square root is at most N − 3, N has a summand up to the depth."),
"d_bounds>d_def": ("states depth", "Both bounds are statements about IsDepth for the odd primes up to the square root."),
"d_bounds>d_exact": ("small cases", "The record holders 6, 12, 30 and 98 are compared with the exact depths 3, 5, 7 and 19, and 220 with 43."),
"d_bounds>l_cover_exists": ("Dirichlet construction", "The lower bound takes a strike vector, realises it by a number from Dirichlet's theorem in the progression, and concludes with the covering existence theorem that its least summand is at least the depth."),
"d_bounds>l_isleast": ("states", "Its conclusions are statements about IsSummand and IsLeastSummand."),
"d_bounds>r_gen": ("terms of A025018", "isRecord_and_isDepth compares the first terms of the sequence with the depth; IsRecord is defined in the generator's file."),
"d_covers>d_def": ("lower bounds for the depth", "Each certified cover states CoversBelow for its list of odd primes, a lower bound for their depth."),
"d_covers>x_coveredin": ("divisibility certificate", "Each vector is certified as a covered range of an explicit even N: the kernel re-evaluates every block test and the covered-range theorem turns divisibility into ‘no summand’."),
"d_coversbig>d_def": ("lower bounds for the depth", "Each certified cover states CoversBelow for its list of odd primes, a lower bound for their depth."),
"d_coversbig>x_coveredin": ("divisibility certificate", "Each vector is certified as a covered range of an explicit even N, with 17 and 75 block checks."),
"d_records>d_def": ("lower bounds for the depth", "The certified 200-digit covers are restated as CoversBelow for the odd primes up to 463, 479, 487 and 491."),
"d_records>r_cover15907": ("the same cover", "The bound for 89 moduli is the 15,907 complete cover of the 200-digit search, read through coversBelow_of_complete_cover."),
"d_records>r_cover_more": ("the longer covers", "The bounds for 91, 92 and 93 moduli are the three longer complete covers certified for the 200-digit search."),
"d_depthform>c_layers": ("layered covers", "The classes come from the layered-cover lemma: fix a first layer, choose the middle layer by pigeonhole, and give each remaining row its own prime of the last layer."),
"d_depthform>l_mertens3": ("needs Mertens", "The count in the layered cover is a product over odd primes of (r − 2)/(r − 1), which Mertens' third theorem evaluates as 2·C₂·e^(−γ)/ln w; this fixes the constant 1/(2C₂e^−γ) = 1.349."),
"d_depthform>l_pnt": ("counts primes", "The layers are counted with the prime number theorem in its two-sided form."),
"l_cb073>d_depthform": ("built from the depth form", "The unconditional theorem constructs its number N from the classes that the depth form provides, once the elementary Mertens-type bound fixes the constant 0.73."),
"l_cb_sharp>d_depthform": ("built from the depth form", "The sharp theorem constructs its number N from the classes that the depth form provides, with Mertens' third theorem supplying the constant 1.349."),
# ---------------- the count of covers
"d_count>d_def": ("positive exactly up to the depth", "isDepth_iff_coverCount: the count is positive for the primes below the depth and zero beyond, so the depth is the count's last positive point."),
"d_count_lower>d_count": ("bounds the count", "g0 and the monotone bound coverCount_mul_prod_le are the objects the lower bounds are about."),
"d_count_lower>d_depthform": ("positivity from the covering bound", "In the range Q = c·y ln y the depth form says some vector covers, so g0 is positive there; the monotone bound carries it to every larger set of moduli."),
"d_count_lower>d_exact": ("exact small case", "g0(29, 181) > 0 and g0(29, 182) = 0 is the exact depth of nine moduli, written as a count."),
"d_pairs>d_count": ("same count, two rows", "card_pair_uncovered counts the class vectors that leave both rows uncovered, using the class-vector type and Covers of the count: the second-order term of the inclusion–exclusion count of covers.", "direct", "CoverPairs.lean (`open CoverCount in`, a relative open that the reference tool does not resolve); scripts/cover_count/README.md section 4"),
"d_pairsums>d_pairs": ("extends", "The product form and the partial sums are statements about the same pair weight (rho and sigma of the previous file), for every truncation of the products."),
# ---------------- the limit on search methods
"c_hardness>d_def": ("builds on the depth search", "The reduction uses the depth-first search of the cover depth: run on the constructed rows it decides the formula, and a covering vector is exactly what that search looks for."),
}
# links that the earlier map carried and that the new references subsume (the tool now reaches them through the depth form)
E_DROP = ["l_cb073>l_pnt", "l_cb_sharp>l_mertens3", "l_cb_sharp>l_pnt"]
