# h2_sharing: cost floor per test and sharing of work (reviewer notes)

Verdict: barrier holds from this lens. The whole sieve+test layer is worth at most ~2-2.5 nats even if one half is made FREE; shortfall is 7.7.
Model: run/h2_sharing/model.py (R=1609 rows, Q=213,070; Monte-Carlo alive counts; hit=(1-p_B)^c; cost = sieve(B)+f*T*tests).

## Q1 sharing across moduli
- Every sharing scheme factors through Z/(prod n_i) (only ring mapping onto all Z/n_i). Arithmetic there is never cheaper per bit than 24-limb schoolbook:
  Karatsuba range 14 moduli -> 14^1.58=65 M(n) vs 14 (4.6x worse); FFT range ~7,500 butterflies x(1-3) per 664 bits per multiply vs 876 IMAD (4-8x worse).
- Exponent CAN be shared across the rows of a member (2^(n-1)=1 mod n  <=>  2^N = 2^(q+1) mod N-q) but the squaring chain is modulus-specific: saves 0.
- 2^(2^j) tables: modulus-specific. Windowing: base 2, multiplications already shifts. Montgomery batch trick: inversions only.
- n = kM + (N0-q): c = N0-q is full size, no sparse form; only ~32 free bits in N -> <=5% of the reduction. RNS on cover primes: 9-bit moduli, worse.
- Euler instead of Fermat: 1 squaring of 660 (0.15%). First 6-10 squarings already free.
## Q2 cheaper filters (break-even: cost x tests < r(1-p), r = recall on composites)
- p-1, B1=100: 144 squarings (x=0.22), r ~ 0.11*rho(4.2) ~ 5e-4. ECM tiny B1: same order, x larger. Loses 400x.
- batch gcd / remainder tree with primes to 1e10: ~50 M(S) per block = 0.6-2 Fermat tests per candidate for r=0.20. Loses 3-10x. r=0.5 needs 1e16.
- Jacobi/characters: zero information on rough n. Truncated Fermat: no information before the last squaring. Lucas: 1.5-2x a Fermat.
## Q3 operating point (hit mass per ns, relative to deployed B=1e8 keep 1.5%)
- team window model (24.2 ms fixed + generate by visits/marks + apply by marks per 2^24; T=36.5 ns effective): optimum B=1e8, keep 1.25%: x1.010 (0.010 nat). B=3e8 x0.96, 1e9 x0.75, 1e7 x0.93.
- FREE sieve to any depth (T kept): x7.7 = 2.04 nats at B=1e12 keep 0.2% (at B=1e9: x3.3 with keep 0.2%).
- FREE Fermat (sieve kept): x11.7 = 2.46 nats (B=1e6, test everything).
- marks-only model as given in the brief (0.03 ns/mark, 90 ns/test): says B=1e12, x1.7 -- artefact: omits pair visits (pi(B) x rows per 2^24 window: 3.6e6 visits/member at 1e12)
  and 0.03 ns/mark x 1,768 marks = 53 ns/member contradicts the measured 3.6-11 ns. Team figures: 3-9 ps a mark, 43 ns a test.
## Q4 prime-gap hunters -> see final answer table. Nothing they have is missing; nobody shares work between PRP tests.
