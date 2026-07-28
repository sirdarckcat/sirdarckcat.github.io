# WP7 — Bounded probes into mechanisms beyond static covering

Status: executed 2026-07-28. Five probes, each with a predeclared gate
(compression metric: offsets certified per nat of design entropy, benchmarked
against covering: ~4,400 offsets/nat at r=3 falling to ~0.4/nat at r≈1,200).
All five TERMINATED at their gates. Numeric checks reproducible; summary of
what a genuine WP7 breakthrough must now look like at the end.

## P1 — Prime-power moduli. TERMINATED (strictly dominated).
Upgrading a cover modulus p to p² costs ln p additional nats and yields ZERO
new kills: the q ≡ a (mod p²) class is a subset of the q ≡ a (mod p) class
already killed ([V] p=7: 227 ⊂ 1,613). Using p² instead of p kills p× fewer
offsets at 2× the cost. Composite-modulus gadgets reduce to their prime
factors with only losses.

## P2 — Polynomial value-set identities. TERMINATED (dominated; closest call).
Mechanism: N = m^k − c makes N − q = m^k − d^k algebraically composite for
every offset q = d^k − c. [V] Best case k=2: c=398 kills 113 offsets below
10^5. Cost: N is confined to a k-th-power family, surrendering (1−1/k)·lnB =
115 nats of search freedom (at B=10^100).
- vs average covering efficiency: 26× worse (113 offsets cost 4.4 nats via a
  fresh modulus r≈85).
- vs MARGINAL covering (endgame, ~2.5 nats/offset): only ~2–3× worse — but
  the family's offsets are generic, so after a real cover only ~8% of them
  (~20, optimising c) land in the residual set: ~5.8 nats per residual kill,
  plus QR-compatibility halves residue choices across the cover.
- Structural ceiling (mini-proposition): any polynomial identity mechanism is
  degree-1 (≡ ordinary covering) or degree ≥2, whose value set below Q has
  ≤ O(Q^{1/2}) members — at most ~316 killable offsets at k=2, fewer for
  higher k or for Aurifeuillian-type identities — while costing Θ(lnB) nats.
  The mechanism cannot scale past a few hundred offsets AT ANY price.

## P3 — Sierpiński–Riesel exponent families. TERMINATED (reduces to covering).
For N_n = k·2^n + c, the residue mod p cycles with period ord_p(2)
([V] example table for 5·2^n+1 mod 11). For any FIXED candidate the induced
constraint is one congruence class — ordinary covering, no entropy gain.
The exponent structure correlates residues ACROSS the candidate family,
which is a legitimate *search-throughput* trick (shared sieve state along n,
plausibly a small constant factor) — noted for the engine backlog, not an
entropy mechanism.

## P4 — Norm forms / splitting conditions. TERMINATED (reduces to covering).
"N − q is a norm in K" does not certify compositeness (rational primes with
the right splitting are norms), and any usable splitting condition on q is a
congruence condition mod disc(K)-related moduli — i.e., covering in
Galois-theoretic clothing, subject to the same ln r accounting.

## P5 — Residual-bias loophole. TERMINATED (empirically bounded).
Could N be chosen so residual complements are composite MORE often than the
coprimality boost predicts? The banked campaigns answer: across three covers
and ~1.2×10^9 scanned candidates, |Ê − E| ≤ 0.1 — any unexploited
compositeness structure is worth at most ~0.1 nats per candidate (factor
≤1.11). Pair-correlations between complements are already captured by the
cover's CRT information; nothing measurable remains.

## What a genuine WP7 breakthrough must now look like

The five terminations sharpen the requirement. A mechanism that breaks the
sub-100 barrier must simultaneously:
1. certify compositeness of N − q for a set of offsets of size ≫ Q^{1/2}
   (else P2's value-set ceiling applies), and
2. cost o(ln r) design entropy per offset at the margin (else it is
   covering), and
3. survive the P5 empirical bound (its effect would have to be invisible in
   Ê at current scales, i.e., activated only by special N — consistent, since
   constructed N are e^-2600-rare).
No known algebraic structure does all three. Combined with the WP3 memo's
barrier (CRT list-recovery beyond the Johnson radius; density-1.026 modular
subset-sum), the honest position is: sub-100 T(100,000) currently has no
viable route except Regime-I brute force (~5×10^4 GPU-years), and the two
named open problems + requirement (1)-(3) above are the precise mathematical
targets that would change that. This is the RQ7 deliverable.
