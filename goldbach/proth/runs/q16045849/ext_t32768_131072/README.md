# Fallback range for the 16M rung: t ∈ [32768, 131072)

The spec allows t < 2^20 (F³ > P still holds). After 5,517 misses, the
chance that the main range t < 32768 holds no prime was ~13%. So this range
was sieved on the session's own container by the same chain as the main
pool:
- `ext_chain.sh` and `ext_sieve.py` drive it;
- `deepsieve` was built from `../../../deepsieve.c` with
  `gcc -O3 -march=native`.

| stage | survivors | kills | log |
|---|---|---|---|
| primes < 10⁹ (`desert.py`) | 56,187 | | `sieve_1e9.log` |
| [10⁹, 10¹¹) | 45,994 | 10,193 | `ds_1e9_1e11.log` |
| [10¹¹, 3·10¹¹) | 44,130 | 1,864 | `ds_1e11_3e11.log` |

Checks:
- The same sieve over t < 32768 reproduced
  `../survivors_T32768_B1000000000.json` exactly.
- The local `deepsieve` build reproduced the Colab kills on [10⁹, 2·10⁹)
  exactly (607 of 607).
- `deep_sieve.py` re-checked every kill in gmpy2 (P_t mod p = 0), with no bad
  pairs.

The `T131072` lists hold only t ≥ 32768. About 9.8 primes are expected among
the 44,130 survivors.

Each Colab CPU runtime moves here when its slice of the main range is done,
taking slice j/6 top-down (`pfgw_search.py`).
