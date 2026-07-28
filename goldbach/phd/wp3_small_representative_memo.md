# WP3 memo — The sub-100 problem as CRT-code list recovery

Status: working memo, 2026-07-28. Claims marked [V] are verified computations
in this repo; claims marked [R] are recalled literature bounds requiring
verification before anything is built on them.

## 1. Problem

Find even N < B = 10^100 with g(N) > 100,000: every prime q < 10^5 must have
N − q composite. In the covering paradigm, congruences N ≡ a_r (mod r) force
r | N − q for all q ≡ a_r (mod r); residual (uncovered) primes must lose an
independent primality lottery with failure exponent E = |U|·boost/ln N.

[V] Brute frontier (validated density model, this repo): E ≈ 52 at 100
digits → e^52 ≈ 5×10^22 candidates ≈ 3×10^8 A100-years. Compute is dead;
the paradigm's constraint digits(N) ≥ digits(M) is what must break.

## 2. Two no-go results for natural reductions

**2a. Fixed-subset modular knapsack is entropy-starved.** [V]
Fix moduli S (|S| = n), allowed near-optimal residue sets A_r; residue swaps
shift the CRT representative by known vectors δ_r — a modular subset-sum
with window target [0, B). Effective density
d_eff = Σ lb|A_r| / lb(M/B) ≈ 0.22–0.33 for coverage-viable |A_r| ≤ 8.
No lattice attack can find what doesn't exist: the fixed-subset instance has
no solutions. The essential entropy (~500 bits) is in the *choice of S*,
making the real problem bilinear (subset × residues), outside standard
knapsack/CVP formulations.

**2b. Incremental CRT growth (beam) collapses to entropy conservation.** [V]
Toy at Q=10^4, T=10^25 (this memo's experiment): growing an oversized cover
while keeping the representative < T yields rep 414 digits below the modulus
mass — but E *worsens* (34.3 vs 20.5 conventional), because:
- forced (t=0) congruences are exactly E-neutral: coverage rate 1/r cancels
  boost growth r/(r−1) (Mertens neutrality);
- once mass exceeds T, t_max = ⌊(T−N0)/M⌋ hits 0 within ~1 modulus, so
  sequential growth accesses only O(1) positions of genuine choice beyond the
  conventional budget. Good final systems have prefix-valid representatives,
  but reaching them sequentially requires the beam to have already guessed a
  lucky N0 during the free phase — which is the original exhaustive search.
Conclusion: solutions exist (first-moment surplus ~2^145 at the right design
point) but both naive access paths reduce to exhaustive search. This is the
RQ4 "entropy conservation" phenomenon, now with a concrete mechanism.

## 3. The right formalization: list recovery of Chinese Remainder codes

Positions = primes r in a pool P; the "received data" at position r is the
set A_r of top-ℓ coverage residue classes (computable from the target prime
set alone); a "codeword" is any integer N < B via its residues. We seek N < B
whose residues agree with A_r on a position subset of large total mass
Σ ln r ≈ the cover mass. This is exactly **list recovery of CRT codes**
(Goldreich–Ron–Sudan; Boneh, "Finding smooth integers using CRT decoding";
Guruswami–Sahai–Sudan soft-decision CRT decoding) [R].

- [R] GSS-type lattice decoders run in polynomial time when weighted
  agreement mass A exceeds a Johnson-type radius ≈ sqrt(ℓ · ln B · P),
  P = total pool mass in nats.
- [V] Naive parameters (pool < 5,000, agreement ~150 positions) sit in the
  gap: solutions exist below the decodable radius. This *is* the classical
  existence-vs-decoding gap of list decoding, instantiated for Goldbach
  deserts. "Close the CRT list-recovery gap" = "construct sub-100 deserts".

**The scaling discovery** [V, contingent on the [R] bound]: existence grows
linearly in pool mass P (freedom ≈ 1.5 bits/position) while the decoding
radius grows as sqrt(P). The two curves cross:

| pool R | positions | radius (nats) | existence cap (nats) | window |
|---|---|---|---|---|
| 5,000 | 668 | 1,504 | 925 | closed |
| 30,000 | 3,244 | 3,701 | 3,603 | closed (near) |
| 60,000 | 6,056 | 5,248 | 6,527 | **OPEN** |
| 100,000 | 9,591 | 6,775 | 10,202 | **OPEN** |

At R ≈ 60k–100k with ℓ = 2, a design point exists where (a) solutions exist
by counting and (b) the recalled decoder radius reaches them. The implied
agreement mass (~2,300–2,900 digits of cover) leaves |U| ~ 100–200 residuals
→ E ≈ 6–12 at 10^100: a trivially searchable tail. The whole e^52 wall would
collapse into one (enormous but polynomial) lattice computation.

## 4. Honest caveats

1. The sqrt(ℓ·lnB·P) radius is recalled, not verified; the exact GSS/Boneh
   amplitude form and its list-recovery (ℓ>1) generalization must be pulled
   from the papers. A factor of 2 in the bound moves the window by 4× in P.
2. Existence is a first-moment estimate; second-moment/concentration needed.
3. Decoder practicality: dimension ~#positions (thousands) with multi-
   thousand-bit entries. Polynomial ≠ practical; but toy scale (Q=10^4,
   pool ~10^3, dim ~10^2) is fully runnable with fplll/flatter.
4. Even on success the decoded N must clear the E ≈ 6–12 residual lottery →
   need poly-many decoder outputs (weight re-randomization).

## 5. Programme

1. Pull GRS/Boneh/GSS and verify the exact soft-decision radius; redo §3
   arithmetic with the true constants. (Desk work, days.)
2. Toy decoder at Q=10^4: pool primes < 1,500, B = 10^25, ℓ = 2; implement
   the Coppersmith/GSS lattice; measure how close practical BKZ gets to the
   theoretical radius. Predeclared success gate: decode agreement mass ≥ 1.2×
   the conventional-cover mass at equal B.
3. If the constants hold: scale ladder, and the sub-100 attempt becomes a
   lattice-reduction campaign (new WP: LLL/BKZ engineering, not sieving).
4. If the window closes under true constants: the memo's §2 no-gos plus the
   quantified gap constitute the RQ7 barrier result — "sub-100 constructions
   require decoding CRT codes beyond radius X" — publishable either way.
