# Cross-review: branch `ccr-8ffe9d7a-4ni11u` vs `ccr-2ce9e63a-hn0fuw`

> **Status after the merge (2026-11-21).** Written before the two branches
> were merged; "this branch" is `ccr-8ffe9d7a-4ni11u` and paths are those
> of its head `6c66bcd`. At the merge its author asked for two corrections,
> applied below and marked ⟲: an erratum to §4.4 and the hash note in §1.
> The reverse review is `crossreview_8ffe9d7a.md`; what was agreed is in
> `merge_2026-11-21.md`.

Status: 2026-11-21, at user request ("review your results with
`ccr-2ce9e63a-hn0fuw`"). Both branches start from `a3885fb`. Prompted by
the same PDF, they independently found the same construction: a full
cover, a 2-adic CRT condition, and a complement proved prime by BLS from
one modexp. All checks below were re-run in this container.

## 1. Verdict

- **Same method, found twice.**
  - Both branches re-derive the same Pocklington + BLS N^(1/3) argument
    inline.
  - Both build the same paper-greedy cover at Q = 1.2·10^6: 2,005 classes,
    r ≤ 17,431.
  - Both get the same g = 1,200,109 with different N. The sha256 of the
    decimals differ: `4eb6cbc5…` (theirs) and `8b97681b…` (here).
    ⟲ These two are hashes of the `N.txt` *files* (decimal plus newline);
    the hashes of the decimal strings, the convention used elsewhere, are
    `cf388b5b…` and `7bdbe05a…`.
- **The other branch has priority and the incumbent.**
  - Its g = 1,200,109 record was committed at 08:03 UTC, against 08:44
    here.
  - It has since certified **g = 2,000,269** at 15,595 digits, using a
    lazy cover ~10% shorter. That is the Game-1 incumbent. This branch's
    record is an independent second certificate for g = 1,200,109.
- **No error was found in any record.** All records pass every verifier
  (§2).
- **Their theory checks out** (§4.1), and their one post-cutoff
  literature citation was verified verbatim against the source PDF.
- **This branch overclaimed** "new record" and "first record without
  ECPP" relative to the combined state. That is corrected in this commit
  (§4.3).

## 2. Verification matrix

| record | their `proth/verify.py` | `bls/xverify.py` (this branch, stdlib) | PARI `crosscheck.gp` (re-run here) |
|---|---|---|---|
| theirs, g = 1,200,109, 11,263 d | PASS (their log) | **PASS**, 87 s | **PASS**, 1 m 56 s |
| theirs, g = 2,000,269, 15,595 d | PASS (their log) | **PASS**, 232 s | **PASS**, 7 m 12 s |
| this branch, g = 1,200,109, 11,263 d | **PASS**, 5.5 s (gmpy2) | **PASS**, 88 s | **PASS**, 1 m 53 s |

- **The PARI path does not use the cover classes.** It builds PARI's own
  N−1 certificate for P = N − g and runs `isprime`. It also checks, for
  every prime q < g, that gcd(N − q, r_max#) > 1.
- **The files extracted from their records match their SHA256SUMS.**
- **PARI/GP 2.15.4 was installed here (apt) for this review.**

## 3. Method comparison

| | this branch, `goldbach/bls/` | other branch, `goldbach/proth/` |
|---|---|---|
| 2-adic condition | N ≡ g+1+2^n (mod 2^(n+1)), so v₂(P−1) = n exactly | P = m·2^n + 1 with m ≡ m₀ (mod M_c); v₂(P−1) ≥ n, F = full 2-power |
| witness base | least prime a with (a/P) = −1. In effect a fixed cover prime, since P mod r is constant on the progression | fixed in advance: a cover prime b with ((a_b−g)/b) = −1 |
| cover | paper's increasing greedy | **lazy weighted greedy over a 3× prime pool: −10% digits, about −30% search**; increasing greedy also available |
| sieve bound | 2·10^8 | 10^9 |
| verifier | stdlib; product-tree CRT re-derives N from (cover, n, i); tamper suite 6/6 | stdlib; reads N and re-derives every claim from N, g, cover; **plus the PARI path** |
| model checks | `density_probe.py`: z = +0.76 (Q = 10^5), −0.43 (Q = 3·10^5) | calibration run: 46 primes against 48.6 predicted |
| extras | `--skip` resume; `ladder.py`; `xverify.py` | `search_tests.jsonl` checkpoint; `package.py`; `pigeonhole_table.py`; Lean plan |

## 4. Findings

### 4.1 Other branch — re-derived and correct

- **Theorem 1:** C(x) ≥ (e^γ/(2C₂) − o(1))·x·ln x, with
  e^γ/(2C₂) = 1.349. The steps check:
  - the pigeonhole recursion t ← t(r−2)/(r−1) + 1/(r−1);
  - the identity (r−2)/(r−1) = (1 − 1/(r−1)²)(1 − 1/r) and Mertens;
  - the endgame, with one survivor per prime in (x/ln x, x].

  It beats the paper's Theorem 14 (the FGKMT transfer) by a factor
  ln₃N/ln₄N. It also beats Shi's counting constant ½, under Shi's
  convention p(n) = ∞ when n has no partition.
- **Theorem 2:** C(x) ≤ x^(4+ε), and x^(2+ε) on Elliott–Halberstam. It
  uses the linear sieve at level Q^(1/2−ε) by Bombieri–Vinogradov. The
  maximum over classes is included, so adversarial residues are allowed.
  The argument is correct. It is the asymptotic form of this branch's
  per-instance computation (WP10 §B): the record covers have
  z = 613–683 ≫ Q^(1/4) ≈ 18, so the sieve floor is vacuous there. Both
  analyses agree that GRH adds nothing, because Bombieri–Vinogradov
  already gives GRH's level for sieve sums.
- **GRH ledger (their WP10 §3).** It agrees item by item with this
  branch's WP10. Their row 2 is a point this branch missed. It is a
  guaranteed, not just expected, BLS-certifiable prime in the
  progression: N < M^(12+o(1)) unconditionally (Chang's smooth-modulus
  Linnik exponent 12/5; marked [L], not re-checked here), and
  M^(6+o(1)) on GRH. In practice the exponent is 1.5.
- **Citation check:** W. Shi, arXiv:2605.21529v6, Theorem 6.22(iii) and
  Remark 6.24. Verified verbatim from the v6 PDF:
  - the theorem states max_{n≤X even} p(n) ≥ (½ + o(1))·log X·log log X;
  - the remark calls this "the limit of pure counting … an improvement
    would need a covering construction in the spirit of
    Ford–Green–Konyagin–Maynard–Tao, here covering only the primes p ≤ z".

  Their quotation is accurate. *Nit:* the bibitem uses the v6 document's
  own title ("Matrix B: …"), while the arXiv listing and the PDF metadata
  still show the older title, "A Matrix-Theoretic Exact Formula for
  Counting Primes in Intervals Between Consecutive Odd Squares". Citing
  with the version suffix avoids confusion.

### 4.2 Other branch — small items

- **One claim is too optimistic.** "Hours on a gwnum-class engine" for
  the 16,045,848 rung (~5,700 tests at 91,753 digits) holds for the GPU
  fleet or a few dozen cores, not one gwnum core. Suggest "hours on the
  GPU fleet".
- **One citation was not re-checked.** Chang (2014, L = 12/5) is marked
  [L] there and was not re-checked here.

### 4.3 This branch — corrections made in this commit

- **Records ledger.** RESULTS.md, the SoK and the research log called
  g = 1,200,109 a "new record" and "the first record … with no ECPP". On
  the combined history that is wrong on priority and superseded on value.
  They now say "independent second certificate" and name the incumbent
  2,000,269 on the other branch.
- **Ladder.** WP11's cost ladder uses the increasing greedy. The other
  branch's lazy cover is ~10% shorter, so WP11's costs are ~30%
  pessimistic; its `proth/README.md` ladder is the better reference.
- **SoK §7.3 note.** This branch's note ("a theorem here needs
  Hardy–Littlewood-strength input") is right about the record-scale walls
  of partial covers plus luck. It must now be read alongside their
  Theorem 2, which is the first unconditional impossibility statement for
  covering certificates, although only an asymptotic one.

### 4.4 One joint observation worth a cheap experiment

> ⟲ Erratum (2026-11-21, from the other session's review, reproduced here
> with overlap_check.py): the two Q = 1.2·10^6 searches were one
> progression. This branch's offsets i are that branch's odd t = 2i+1;
> 1,341 integers were tested by both, 4,778 distinct. In the union 6.42
> primes were expected and 2 found, so P(≤ 2) = 0.046, not ≈1%. The probe
> proposed below is superseded by the out-of-sample run reported in WP12.

Both Q = 1.2·10^6 searches ran about 4× long:

| search | tests | expected |
|---|---|---|
| theirs | 2,647 | ~703 |
| this branch | 3,472 | 762 |

Together that is 2 primes in 6,119 tests against ~8.3 expected, which
has Poisson P(≤ 2) ≈ 1%. The two runs share the cover and g, so P lies in
the same residue class modulo the cover modulus in both. Everything
else is on-model: their 2·10^6 run (648 tests against 973), and three
calibration probes (46/48.6, 54/48.7, 8/9.3).

The Hardy–Littlewood density of a single linear form does not depend on
the class, so this is most likely chance. The day-scale ladder costs rest
on the same model, however. A ~1.5 h exhaustive probe of the
Q = 1.2·10^6 class (3,000 tests, about 4 primes expected) is cheap
insurance before committing ~3.5 days to the 10^7 rung:
`bls/density_probe.py 1200000 --tests 3000 --sieve 200000000`.

## 5. Merge plan (proposed, not executed)

> ⟲ Superseded by what the two sessions agreed (`merge_2026-11-21.md`):
> as below, except that this branch's WP10 and WP11 keep their numbers
> and the other branch's memo became WP12.

A trial merge of the other branch into this one conflicts in
`SOK_GOLDBACH_GAPS.md` and `phd/RESEARCH_LOG.md`. `RESULTS.md` merges
textually, but would then hold two "new record" sections for the same g.

1. **Base Game 1 on the other branch:** `goldbach/proth/`, both of its
   records, its WP10 memo, its SoK rev-4 addendum and its record board.
2. **Renumber this branch's WP10 and fold in WP11.** Rename
   `phd/wp10_grh_remark.md` to `phd/wp10b_grh_reach.md`. It is
   complementary: it has the 10^65.6/10^72.4 shortfalls, the Door-1 lift
   sizes and the per-instance sieve floors. Link it from their WP10 §3,
   and reduce `phd/wp11_bls_game1.md` to an "independent reproduction"
   note.
3. **Keep the verification tooling.** Keep `bls/xverify.py` and
   `bls/verify_bls_record.py` as the second, independent verification
   stack (the repo's dual-stack rule, SoK §4), plus `density_probe.py`
   and the tamper suite. Drop `bls/full_cover.py`, `bls_search.py` and
   `ladder.py` as duplicates of `proth/desert.py` and the proth ladder.
4. **Keep this branch's record as a reproducibility artifact** (~60 KB),
   labelled "independent second certificate for g = 1,200,109: different
   N, independent code".
