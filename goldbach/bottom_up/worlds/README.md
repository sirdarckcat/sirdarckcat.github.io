# Toy worlds (research's programme of 26 Nov, on the user's direction)

The user's direction: start with proofs on smaller toy examples (groups or similar) that are known not to transfer to the integers,
collect the tools and ideas, then transfer what can be transferred and replace the rest with other fields. In every world the object
is a separable score S(N) = Σ_r f_r(N mod r) under a constraint that couples the coordinates, and the question is whether the members
with extreme S can be produced at a cost proportional to the output. This session has Worlds 2 and 4.

- `world2.md`: linear coupling, that is, list recovery of polynomial CRT codes. It covers Johnson-type decoding at every window size,
  the exact condition for a set to be certified (without the Gaussian tail), folding and multiplicities with product lists, what
  folding uses, and prime powers.
- `world4.md`: the random box. It covers a lower bound for all algorithms on a random window, the dynamic-programming width of the
  integer window, the bound on merges that split the places, what an exact selection must read when the sieve reaches past the
  window, the NP-completeness of the problem for arbitrary tables, the converse table, and the additive labelling measured.
- Scripts and outputs:
  - `johnson_cost.py` → `johnson_cost.out`
  - `johnson_named.py` → `johnson_named.out`
  - `johnson_capacity.py` → `johnson_capacity.out`
  - `table_reads.py` → `table_reads.out`
  - `reduction_check.py` → `reduction_check.out`
  - `width_toy.py` → `width_toy.out`
  - `additive_chars.py` → `additive_chars.out`
  - `additive_peaks.py` → `additive_peaks.out`
