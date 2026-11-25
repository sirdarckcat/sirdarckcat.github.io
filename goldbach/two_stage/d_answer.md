# (d): soft-decision CRT list decoding as a fourth route, and why it cannot reach the ideal members

**The question.** Is there an enumerator of the N < 10^200 with about 1,116 rows left at depth 2,000 (a window gives 1,309 ± 14)
that costs under 550 Fermat tests per N it outputs? The research session has already shown three routes fail: windows, list
enumeration, and lattices on ∏(N − q). This note checks a fourth, the strongest known polynomial-time tool for "integers in a range
whose residues lie in given weighted lists": soft-decision Chinese-remainder list decoding (Guruswami, Sahai and Sudan, FOCS 2000).
Boneh's CRT decoding and the Coppersmith / Howgrave-Graham bound are special cases of it. `d_decoding.py` does the computations.

**Marks.** **[P]** proved, given the decoder's bound and the Poisson model of class counts. **[L]** literature. **[M]** computed.
**[O]** opinion.

1. **The decoder [L].** Given weights w_{r,a} ≥ 0 on the residues a mod each prime r, it lists, in polynomial time, every k < K with
   Σ_r w_{r, k mod r}·ln r ≥ √(ln K · Σ_{r,a} w_{r,a}²·ln r).
   - The CRT survey (Sudan, AAECC 2001) confirms the unweighted radius n − √(n(k + ε)).
   - The weighted form here is recalled from the paper, not quoted.
2. **The best weights, and what the decoder reaches [P].**
   - Take the members N = N0 + kM of the 89-moduli cover, so k < K0 = 10^200/M and ln K0 = 16.6, with 1,502 rows left.
   - For a target whose residues mod the primes in (463, z] kill β times the typical number of rows, Cauchy–Schwarz gives the best
     weights (the likelihood ratio). With them the condition becomes D(β) ≥ ln K0, where
     D(β) = Σ_r (ln r/r)·e^(m_r(β − 1)²) and m_r = 1,502/r.
   - The ideal members at 1,116 rows have β ≈ 2.
3. **Neutrality [P].**
   - One could hand the decoder some of the cover's primes too: it then pins their residues, and the progression grows to
     ln K = ln K0 + θ_d.
   - Optimizing the weight put on those primes, the condition on the primes above 463 becomes L²/E ≥ ln K0 + (θ_d − A²/B).
   - Here θ_d − A²/B ≥ 0 by Cauchy–Schwarz, with equality only when each pinned prime carries a single class.
   - So no choice of cover, and no mixture of covers, lowers the bar below what a single progression of length X/M allows. That
     is 16.6 nats.
4. **The numbers [M]:**

   | depth z | D(2) | ln K0 | decodable from β | rarity of members at that β | rarity of ideal members (β = 2) |
   |---|---|---|---|---|---|
   | 2,000 | 9.8 | 16.6 | 2.11 | e^−144 | e^−120 |
   | 5,000 | 11.3 | 16.6 | 2.09 | e^−216 | e^−185 |
   | 20,000 | 12.9 | 16.6 | 2.07 | e^−306 | e^−272 |

   The ideal members are below the decodable radius. The members above it occur at rates of e^−144 to e^−306, against e^16.6 members
   in a progression and e^36 in the whole campaign. So the decoder outputs nothing beyond what the window sieve already finds,
   at 3 ns a member.
5. **Why the small primes cannot help [P].**
   - The decoder's agreement is a sum over primes, so it sees each prime's class counts separately.
   - For a prime below the number of remaining rows, every nonzero class holds nearly the same number of rows, because the rows
     are equidistributed. The gain a cover makes there lies entirely in the overlaps (the union), which a separable agreement
     cannot see.
   - Hence the decoder must work inside a cover's progression, and by point 3 that costs it nothing and gains it nothing.

**Verdict.**
- Soft-decision CRT list decoding (GSS), and the lattice methods it contains, cannot reach the ideal-order prize: its radius at
  depth z is fixed by ln(X/M) = 16.6 nats whatever the cover. **[P given its bound]**
- Beyond the Johnson-type radius, no polynomial-time list decoder for CRT codes is known. **[L]**
- So any fourth route has to leave this class: either a non-separable use of the overlaps, or a parametrization of N that is not
  an arithmetic progression. I see no candidate for either. **[O]**
- The class-count model is Poisson, and the targets are taken as uniformly tilted. Exact counts from the real cover would move
  the β* column by a few hundredths, not past 2. **[O]**
