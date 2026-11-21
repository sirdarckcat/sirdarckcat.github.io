# bls/ — Game-1 Goldbach deserts certified by construction

A full congruence cover of the odd primes below Q, plus a 2-adic
condition, makes the complement P = N − g Brillhart–Lehmer–Selfridge
provable. The whole certificate for g(N) = g is then the cover plus one
modexp. Rationale and costs: `../phd/wp11_bls_game1.md`.

```
python3 goldbach/bls/full_cover.py 1200000                    # cover size
python3 goldbach/bls/bls_search.py 1200000 --out rec.json \
        --offsets 300000 --sieve 200000000 --log run.log      # find N
python3 goldbach/bls/verify_bls_record.py rec.json            # stdlib-only
python3 goldbach/bls/ladder.py                                # cost ladder
```

- `full_cover.py`: increasing-order greedy; it reproduces the paper's
  Table tab:results rows for Q = 10^5, 10^6 and 10^7.
- `bls_search.py`: needs gmpy2 and numpy; parallel over all cores.
- `verify_bls_record.py`: independent of the search code. It uses
  product-tree CRT, class-progression marking and a Python-int modexp,
  with no gmpy2 or numpy.
- `ladder.py`: measured-cost table for higher rungs.
