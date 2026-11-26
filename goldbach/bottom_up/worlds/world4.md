# World 4: the random box

This page answers the research session's request of 26 Nov, 00:15 UTC. Marks: **[P]** proved, **[M]** measured, **[O]** opinion.

**Notation.**
- G = ∏ Z/s_i over the later primes, and P = |G|.
- The window W ⊂ G has K members. On the integers it is the image of {N0 + kM : k < K} under the CRT.
- The score is separable: S(x) = Σ_i f_i(x_i). The target T = {S ≥ t} has density e^−κ.

## W4.1: a random window defeats every algorithm, whatever the tables [P]

**The model.**
- W is a uniformly random K-subset of G. This is Theorem A's random box, with the members' residue vectors independent and uniform.
- The tables f_i are known and arbitrary.
- The algorithm is adaptive and randomized, with unbounded computation.
- It pays 1 to draw an element of W, and 1 to test whether some x lies in W.

**The theorem.**

    P(success within Q operations) ≤ Q · max(e^−κ · P/(P − Q), K/(P − Q)) + K/(P − Q),

so the expected cost is at least ½ · min(e^κ, P/K) · (1 − o(1)). The bound is tight: scanning W achieves e^κ, and testing elements of T
achieves P/K.

**Proof.**
- Given the history, the unseen part of W is a uniformly random subset of the unseen part of G.
- So a new draw lands in T with probability at most |T|/(P − Q), and a test of a new x succeeds with probability at most K/(P − Q).
- Outputting an untested x succeeds with probability at most K/(P − Q).
- A union bound over the Q operations finishes it. ∎

**What follows.** The bound holds for every table. So no structure of the lists helps unless the window itself is structured: not
the fixed row set, not cosets, not intervals, not low degree. A successful integer method must therefore use the window. That window
is the CRT image of an interval: the rank-1 Bohr set where the reconstruction character x ↦ Σ c_i x_i/s_i (mod 1) lies in an arc of
length K/P (World 5). The tables' structure can enter only through it.

## W4.2: three classes of algorithm, on the integers themselves [P]

- **(B) Sub-progressions.** This is Theorem B: pinning gains about 3 nats at most.
- **(D) Dynamic programming over places.** Theorem W4.3 below: the window has width K.
- **(M) Merges that split the places.** This covers meet in the middle, the k-tree, and pin+list, with any filters below the root.
  - **The root's merge.** The root merges partial vectors on complementary place sets A | B. Its cost is at least |L_A| + |L_B| ≥ 2√(|L_A||L_B|).
  - **The matches.** By the CRT the matches number K|L_A||L_B|/P (in expectation, for random lists), at least the number of
    outputs O.
  - **So:** cost ≥ 2√(P·O/K). Per output at depth κ, that is at least 2√(P/K²)·e^(κ/2).
  - **When it beats scanning:** only if ln P < κ + 2 ln K − ln 4, which is at most 48.4 nats at K = e^16.6, or seven primes ≥ 467.
  - The toy in `../statement_c/` measured it: never below pinning plus scanning.

## W4.3: the integer window has dynamic-programming width K [P; M]

**The statement.**
- Take any order of the places and any cut A | B.
- The number of distinct residual sets {x_B : (x_A, x_B) ∈ W} lies between min(P_A, P_B, K) and twice that.
- **The proof.** Write N = a + P_A·t with a < P_A. The residual set of a prefix a is the progression {a + P_A t mod P_B : t < T_a},
  where T_a = ⌈(K − a)/P_A⌉. This set determines (a mod P_B, T_a).
- **Measured.** It is exactly min(P_A, P_B, K) at every cut of four toys (`width_toy.py`, `width_toy.out`).

**What follows.**
- By Myhill–Nerode, every exact read-once DP over the places, in any order, has width at least min(K, √P/s_max).
- Every tree decomposition has width at least min(K, P^(1/3)), by a balanced separator.
- At our parameters both are K, so a DP costs at least the scan.

**The converse [P].** Suppose a window has a read-once DP of width σ. Then the members with S ≥ t, for any separable score, can be
listed at cost O(σ Σ s_i + O·Σ s_i).

- First compute, by DP, the best completion of each state.
- Then run a depth-first search that drops every branch whose best completion falls below t.
- Every node the search keeps leads to at least one output.

**In F_q[t].** The room has width q^min(n, D_A, D_B), the trellis complexity of Reed–Solomon codes. That is the same obstruction.

**World 5.** World 5's precision DP is an approximate DP of width about m e^D. For the places 467–1,999, ln P = 1,496.2 and
D = ln(P/K) = 1,479.6 nats.

## The converse: what single structure, added to the random box, makes output-priced enumeration possible

| added structure | algorithm | cost | on the integers |
|---|---|---|---|
| none (random window, any tables) | — | ≥ ½ min(e^κ, P/K) (W4.1) | — |
| a window that is a product set on the scoring places (P_I ≤ K) | CRT pins | output | only P_I ≤ K: two primes ≥ 467 (Theorem B) |
| a window of DP width σ | DP, then a pruned depth-first search | σΣs + O·Σs | σ = K (W4.3): absent |
| a window that is an arc of precision e^−D (World 5) | DP over partial sums | about e^D Σs | D = 1,479.6 for the places 467–1,999: absent |
| an interval window, with lists that are intervals or progressions of classes | lattice enumeration | exponential in the number of constrained places | absent in substance (measured below) |
| a subspace window (F_{p^a}[t]), with lists that are F_p-subspaces | linear algebra | output | absent: Z/p has no subfields |
| a window holding a polynomial family, with lists that are multiplicative cosets | power and norm families | output, at a share K^(1/d − 1) of the window | absent: no heavy coset (research: 0.84 of noise, largest 1.35 ln r) |
| a code, with agreement beyond the Johnson radius | GS / KV / GSS | poly(input) | the guarantee needs places above K, where the input names every member: at least one weighted class per member, about 850 under the Gaussian model's condition (W2.1) |
| a split of the places, merged (M) | lists and range queries | ≥ 2√(P/K²)·e^(κ/2) per output | beats the scan only if ln P < 48.4 |

**Reading the table.**
- With arbitrary tables, only structure in the window works: a product set, small width, or low precision.
- Structure in the tables needs matching structure in the window.
- At our parameters the integer window has none of these.

## Measured: the additive labelling (`additive_chars.py`, `additive_peaks.py`)

The setting is the rows U of the 300 covers at 200,000, modulo the 213 primes 467–1,999, at h = 1..(s − 1)/2.

- **The bulk.**
  - **Mean power:** 0.8435 (sd 0.0007), against 0.952 for random subsets of the odd primes and 1.000 for pure noise.
  - **The same as your multiplicative 0.84, by Parseval [P].** Over all nontrivial characters, additive or multiplicative, the mean
    power is the variance of the class counts divided by their mean.
  - **So it measures regularity:** U is spread more evenly than a Poisson set, as sifted sets are in progressions. It is not a heavy
    direction.
- **The peaks.**
  - **Size:** the largest character over the 213 primes is 4.0 ± 0.3 ln s (at most 4.72), against 1.64 ± 0.2 for random prime subsets.
  - **Location:** the same (s, h) in every cover: (1889, 9), (1931, 377), (1861, 257), (1709, 236), (1609, 544).
  - **The explanation:** each h/s lies within 0.5/G of c/210 (1/210, 41/210, 29/210, 71/210).
    - U sits in 15 of the 210 classes mod 2·3·5·7: it is odd, and the cover fixes its classes at 3, 5 and 7.
    - U's own transform at these c/210 has power about 64.
    - These primes alias it, since G/(210 s) ≈ 0.5 turn.
- **The weight.**
  - **Share of the variance:** each prime's top frequency carries 1.68% of the score's variance (258 rows²), against 1.50% for random
    prime subsets.
  - **The excess:** 0.47 rows² (sd 0.7 rows), against the score's sd of 16 rows.
  - **The heavy-class lists' own spectra:** mean 1.000; largest 2.3–3.2 ln s, from the same aliasing.
- **Conclusion.** "Lists that are intervals or progressions of classes" is absent in substance. What exists is an alias of the
  cover's own structure mod 210, worth under one row.

## What a successful integer method must use

- **[P]** It must use the window's structure (W4.1).
- **[P]** It cannot do so through any of these:
  - sub-progressions beyond P_I ≤ K (B);
  - DP states over places (W4.3);
  - merges that split the places over more than 48 nats of them (M).
- **[M]** Any structure of the tables it relies on has to exist. Neither multiplicative cosets (research's measurement) nor additive
  progressions (here) do.
- **[O]** What is left is an operation whose intermediate objects are none of these: not members, not sub-progressions, not DP
  states, not lists of partial residue vectors on a split of the places. It would have to control the residues at more than 48 nats
  of places at once.
