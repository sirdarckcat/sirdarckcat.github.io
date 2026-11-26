# Scripts and outputs behind the toy-world and replacement-round pages

Copied on 26 November 2026 from this session's scratch space, where the agents of two workflows wrote them, so
that the numbers quoted in `../README.md` (sections "Toy worlds first" and "The replacement round") can be traced
to the code that produced them. Only source files and text outputs under 300 KB were kept; data files, installed
libraries and anything over that size were left out. The scripts refer to absolute scratch paths and to the
repository read-only; they are a record, not a package, and some need their own large intermediate files to
rerun. Two pages were stopped by a safety filter and nothing of theirs is here.

| directory | page |
|---|---|
| `toy/w3-exact/` | the Goldbach problem in F_q[x], exact enumeration of 41 instances |
| `toy/verify-w3-exact-mathematics/`, `toy/verify-w3-exact-numbers/` | its two verifiers (two further independent enumerators) |
| `toy/w3-mechanisms/` | the catalogue of forcing mechanisms in F_q[x] |
| `toy/verify-w3-mechanisms-*/` | its two verifiers |
| `toy/w5-groups/` | groups: the size constraint as one character in an arc, programmes, lower bounds, the real cover to seven later primes |
| `toy/verify-w5-groups-*/` | its two verifiers |
| `toy/w2-parameters/` | list recovery (second opinion) |
| `toy/verify-w2-parameters-*/` | its two verifiers |
| `toy/w4-converse/` | the random box and its converse (second opinion) |
| `toy/verify-w4-converse-*/` | its verifiers (the numbers verifier was stopped by a usage limit before reporting) |
| `toy/mine/` | this session's own checks (power-map sign, characteristic-2 parity and Artin-Schreier, aligned classes, the arc programme) |
| `repl/<lens>/` | the replacement round, one directory a lens: class fields, algebraic groups and primality theory, the function-field dictionary, sieve theory and parity, Bohr sets and lattices, probability and complexity, harmonic analysis, wild card; their verifiers were stopped by a usage limit before reporting, except one fragment |
