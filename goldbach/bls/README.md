# bls/ — the second, independent verification stack

Written by a separate session (branch `ccr-8ffe9d7a-4ni11u`, memo
`../phd/wp11_bls_game1.md`) without sight of `../proth/`. Since the merge
of 2026-11-21 it is kept as the independent leg of the repo's dual-stack
rule (SoK §4): the same records, checked by code that shares nothing with
the pipeline that found them.

```
python3 goldbach/bls/verify_bls_record.py goldbach/records/bls_game1_11263digit_g1200109/record.json
python3 goldbach/bls/xverify.py           goldbach/records/height_15595digit_g2000269/record.json
python3 goldbach/bls/verify_bls_record.py goldbach/bls/testvec_q1e5.json
```

- `verify_bls_record.py`: stdlib only. Rebuilds N from the published
  congruences, the 2-adic condition and the offset by product-tree CRT and
  compares it with the stored decimal; marks every class progression below
  g; one Python-int modexp and the BLS digit test. It reads this
  directory's record format; `../proth/interop.py to-bls` exports a
  `height_*` record into it.
- `xverify.py`: format-agnostic. Reads only N, g, the cover and the witness
  base, so it checks all three records directly.
- `testvec_q1e5.json`: verifier test vector (g = 100,069, 1,536 digits).

The third leg is PARI/GP: `crosscheck.gp` in each record directory builds
PARI's own N−1 certificate for N − g and scans every prime below g without
using the cover classes.

## Retired at the merge

`bls_search.py`, `full_cover.py`, `density_probe.py` and `ladder.py` — this
session's own cover builder, search, density probe and cost ladder — were
removed in favour of `../proth/desert.py`, `probe.py` and `ladder.py`,
as both sessions agreed. They are in the history at commit `6c66bcd`
(`git show 6c66bcd:goldbach/bls/bls_search.py`).

Numbers produced by that code, so that a re-run on the successor is not
mistaken for a failed reproduction (the successor uses a ~9% shorter lazy
cover and sieves to 10⁹ instead of 2·10⁸, so it is cheaper by design):

- `../records/bls_game1_11263digit_g1200109/search.log` and the record
  itself: `bls_search.py` at `647efbf` (3,472 tests, 762 expected);
- `testvec_q1e5.json`: `bls_search.py` at `4adaa4d` (122 tests, 123 expected);
- the density z-scores (+0.76 at Q = 10⁵, −0.43 at 3·10⁵) and the cost
  ladder in `../phd/wp11_bls_game1.md` §3–§4: `density_probe.py` and
  `ladder.py` at `6c66bcd`, on the paper's fixed-order covers.
