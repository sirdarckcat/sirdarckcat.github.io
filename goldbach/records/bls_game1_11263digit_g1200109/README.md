# Game 1 record: g(N) = 1,200,109, certified without ECPP

N has 11,263 digits; the decimal is in `N.txt`, and `record.json` holds N,
the cover and the certificate. g(N) = 1,200,109 is proved by:

- **2,004 congruences** N ≡ a_r (mod r), one per odd prime r ≤ 17,431
  (the paper's increasing-order greedy full cover of the odd primes below
  1.2·10^6), and N even. Every prime q < g lies in some class, so r | N − q
  and N − q is composite.
- **One modexp.** P = N − 1,200,109 = 1 + 2^12475·R with R odd, and
  2^(3·12475) > P. 7^((P−1)/2) ≡ −1 (mod P), and c1² − 4c2 is not a
  square, so P is prime by Brillhart–Lehmer–Selfridge.

Logs:

- `verify.log`: the independent stdlib-only verifier, PASS in 87 s.
- `crosscheck.log`: GMP BPSW on P, and the congruences rechecked under
  GMP.
- `search.log`: the discovery run. It took 3,472 tests on 4 cores in
  76 min. The model predicted 762 tests; that is a ~1% tail draw, and the
  model is validated in `phd/wp11_bls_game1.md` §3.

Reproduce: `python3 goldbach/bls/verify_bls_record.py
goldbach/records/bls_game1_11263digit_g1200109/record.json`
