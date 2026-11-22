import GoldbachGaps.Basic
import GoldbachGaps.Covering
import GoldbachGaps.Counting
import GoldbachGaps.ECPP
import GoldbachGaps.Desert
import GoldbachGaps.Record150
import GoldbachGaps.Record199
import GoldbachGaps.Records
import GoldbachGaps.Fscan.Fermat52
import GoldbachGaps.Fscan.Fermat26
import GoldbachGaps.Fscan.Schedule
import GoldbachGaps.Fscan.Kernel52
import GoldbachGaps.Fscan.Kernel26
import GoldbachGaps.Fscan.ClassStage

/-!
# Least Goldbach summands in Lean

For an even `N`, the least Goldbach summand is `g(N) = min {p prime : N - p prime}`.
This library formalises the theorem-shaped parts of `goldbach/` and `slop/goldbach/`:

* `Basic`    – definitions; every odd prime is `g(N)` for arbitrarily large even `N`
               (paper Theorem `thm:dirichlet`), hence `g` is unbounded.
* `Covering` – the covering certificate and its unconditional realisation
               (paper Proposition `prop:cover`, Theorem `thm:coverdirichlet`).
* `Counting` – the counting bound: for large `X` some even `n` in `(X, 2X]` has no
               Goldbach summand below `log X · log log X / 48`.
* `ECPP`     – a kernel-checkable elliptic-curve primality criterion (one Atkin–Morain
               step), proved sound against Mathlib's group law.
* `Desert`   – a kernel-checkable test that no prime in a block is a Goldbach summand.
* `Record150`, `Record199` – generated certificates (see `scripts/gen_record.py`) for the
               150-digit record `g = 104527` and the 199-digit record `g = 119419`.
* `Records`  – the two bounded record games as closed theorems.
* `Fscan.*`  – correctness of the arithmetic kernels of the `goldbach/fscan` scanner (code
               at commit `a3ab69c` on branch `ccr-d4a17dd0-7uu03r`), one lane at a time:
               `Fermat52` / `Fermat26` are the Montgomery squaring steps `F52_STEP` and
               `FM_STEP` (relation, bounds, no 64-bit overflow); `Schedule` is the exponent
               schedule; `Kernel52` / `Kernel26` combine them into "the lane reports 1 iff
               `2^(n-1) ≡ 1 (mod n)`"; `ClassStage` is the division-free residue of
               `exact_stage`.

## Building

`lake exe cache get && lake build`. The two record files dominate: the kernel replays the
full certificates, which took about 8 minutes on 4 cores with a peak of about 9 GB of
memory. No `sorry`, no `native_decide`, no extra axioms: `#print axioms` on any theorem
here lists only `propext`, `Classical.choice` and `Quot.sound`.

## Regenerating the record files

    python3 scripts/gen_record.py ../records/threshold_150digit_g104527 Record150 \
        GoldbachGaps/Record150.lean
    python3 scripts/gen_record.py ../../slop/goldbach/records/r200/record_r200_r1.json \
        Record199 GoldbachGaps/Record199.lean

## Not covered

The 2,480-digit height record (`slop/goldbach/records/g1`, `g = 1157341`). `ECPP` uses
affine coordinates with one modular inversion per group operation, recomputed inside the
kernel; that is fine at 200 digits and far too slow at 2,480. A projective-coordinate
checker would be needed for it.
-/
