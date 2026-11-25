# Bottom-up round (25 November): families of N that are not progressions, and non-separable use of the overlaps

This round was the research session's request after the user's message ("Discover new math if necessary. No 'last open claim'. If
you run out of ideas, build new paths from the bottom up."). Each construction carries its number at 200 digits against the fleet's
baseline: 89 moduli, 1,502 rows, E = 36.46 nats. Marks: **[P]** proved, **[M]** computed, **[O]** opinion.

Context **[M]**: the model ceiling at 10^200 (`closeness.py`) is 2,130,704, so 200,000 is closeness 9.4% and 170,000 is 8.0%.

## 1. Families that share rows (the archipelago mechanism) — `shared_rows.py` **[M]**

- **The mechanism:** N + d reuses the composite N − q whenever q and q + d are both prime. Members N0 + jD with D < Q share their
  tested integers.
- **The cost:** only the moduli that divide D are a common cover. The best classes on them, by brute force:

  | shared moduli | D | rows | E | sharing (ln μ) | net |
  |---|---|---|---|---|---|
  | 3 | 6 | 8,989 | 58.7 | +9.0 | −13.3 |
  | 3, 5 | 30 | 6,720 | 54.9 | +7.6 | −10.9 |
  | 3, 5, 7 | 210 | 5,570 | 53.2 | +5.8 | −10.9 |
  | 3–11 | 2,310 | 5,006 | 52.6 | +3.5 | −12.6 |
  | 3–13 | 30,030 | 4,571 | 52.0 | +1.1 | −14.5 |

- Sharing needs members within Q of each other, while a full cover keeps them M ≈ 10^193 apart.

## 2. The shift-robust pair — `pair_cover.py` **[M]**

- One cover is made good for both N and N + d, with the union of their rows as targets. It is compared with a single cover found
  the same way (greedy plus descent: 1,581 rows).
- d = 6: N has 1,730 rows, 22% shared, **−3.6 nats**. d = 30: 1,778 rows, 33% shared, **−4.6**. d = 210: 1,804 rows, 40% shared,
  **−4.8**.

## 3. Divisor families, N + h = L highly composite **[P]**

- Here (q + h) | L kills row q. But then N ≡ −h (mod p) for every p | L. That is the common-integer cover, Erdős and Rankin's
  block, which leaves about the random-class count: 2,146 rows against 1,502, **−16 nats**.
- Prime powers in L add nothing. A large prime P in L kills at most one row, at a cost of ln P.

## 4. The overlaps

- **[P]** Two primes p1 ≠ p2 beyond the cover strike a common row |U|/(p1·p2) times on average for a member uniform in its window,
  whatever the cover. The sieve's statistic is the exact union, so it already uses all they carry.
- **[M]** Strikes per row are Poisson, with mean Σ1/p = 1.10 to 10^8. Without double strikes, sd(S) would be 40.6 instead of 18.0,
  and δ 3.0 instead of 1.33 (80% of the hit mass captured at 1.5% instead of 20%). So the clumping of strikes is what limits the
  window sieve. The share of struck rows struck twice or more is 10.4% at depth 2,000 and 45% at 10^8.
- **[M]** Making later-prime strikes repel would cost a KL of about |U|(Σ1/p)²/2: 34 nats at depth 2,000 (906 at 10^8). It would
  return about 31 kills, or 0.9 nats, at 2,000. That is a return of 1/37.

## 5. The exchange rates of soft constraints, at the real class counts (Poisson, m = 1,502/s) **[M]**

| at s = 467 | KL (nats) | extra kills | rows per nat of KL | rows per nat if built by CRT (charged ln s) |
|---|---|---|---|---|
| the heaviest class (a pin) | 6.15 | +5.8 | 0.94 | 0.94 |
| the heaviest quarter | 1.38 | +2.4 | 1.73 | 0.39 |
| the heaviest half | 0.69 | +1.3 | 1.91 | 0.21 |
| the heaviest three quarters | 0.29 | +0.7 | 2.32 | 0.11 |

- The research session's "soft is worth 2–3 rows per nat, a pin about 1" is right per nat of KL. The decline with s is the same at
  701, 997 and 1,999.
- **[P]** A CRT construction (a union of classes in a window) is output-sensitive only when the window covers every combination of
  the constrained primes. So it charges ln s per prime however soft the constraint, and soft constraints come out 4–9 times worse
  than pins.
- Three currencies exist:
  - window, which charges ln s per prime (CRT);
  - scanning, which charges e^KL members scanned per member kept (the sieve, at 3 ns a member);
  - algebraic rate, which charges 1/d of the range for polynomial families, whose built-in value structure is not aligned with the
    heavy classes.
- A currency that charges about KL and does no scanning would be new. It amounts to an output-sensitive enumerator for random CRT
  boxes: {k < K : k mod s_i ∈ A_i for all i}, with ∏ s_i ≫ K.
- **[M]** Searching over polynomial families for alignment does not supply it.
  - For quadratic families pinned to 229, the alignment noise summed over the primes (229, 2,000] has sd of about 3.6 rows.
  - The best of e^20 candidate polynomials gains about 23 kills, or 0.46 nats, against the family's base loss of 5.5.

## 6. A frame for the enumerator **[O]**

- Enumerating the deep tail means finding k such that F(k) = ∏_{q∈U}(N0 + kM − q) has many linear factors divisible by primes in
  (463, z]. That is the number field sieve's relation collection: smooth values of a polynomial in a short range.
- There, decades of work have found nothing output-sensitive beyond sieving and special-q, and special-q is folding a prime into
  the modulus.
- Our F is fully split, so its "smoothness" is many independent per-factor events.
