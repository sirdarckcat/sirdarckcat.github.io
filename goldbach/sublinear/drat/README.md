# DRAT proofs that D(n) is not larger, n = 9..12 (uarch session, 24 Nov 2026)

For n = 9, 10, 11, 12 (D = 181, 223, 271, 331), `n<n>.cnf` is the formula "some residue vector on the first n odd primes
(exactly one class per modulus, class 0 allowed) strikes every odd prime below p'", with p' the next prime after D(n)
(191, 227, 277, 337), written by `../desert_sat.py` (variables x[m][c] for modulus m in class c; one "at least one" clause and a
sequential-counter "at most one" encoding per modulus; one clause per odd prime q < p': OR over m of x[m][q mod r_m]).
CaDiCaL 1.9.5 (pysat 1.9.dev25, solver name cadical195) reports UNSAT, and `n<n>.drat` is its DRAT proof (text).
Together with the vector of the desert tables (which strikes every odd prime below D), UNSAT gives D(n) = D exactly.

**These proofs have not been checked by a DRAT checker here** (running a downloaded checker was not permitted in this session).
They are meant for a checker of the Lean session's choice: `drat-trim n<n>.cnf n<n>.drat` or a verified one.

| n | D | p' | cnf bytes | drat bytes | drat.xz bytes | in this directory |
|---|---|---|---|---|---|---|
| 9 | 181 | 191 | 5,297 | 784,465 | 145,728 | cnf, drat.xz |
| 10 | 223 | 227 | 6,788 | 5,083,914 | 993,544 | cnf, drat.xz |
| 11 | 271 | 277 | 8,699 | 28,436,186 | 5,272,088 | cnf (regenerate the proof) |
| 12 | 331 | 337 | 10,802 | 148,358,148 | 25,151,784 | cnf (regenerate the proof) |

The solver is deterministic here (n = 9 and 10 regenerated bit-identically), so the two large proofs are not committed:

    pip install python-sat==1.9.dev25       # CaDiCaL 1.9.5 inside
    python3 ../desert_sat.py 11 271 cadical195 --drat n11.drat --cnf n11.cnf
    python3 ../desert_sat.py 12 331 cadical195 --drat n12.drat --cnf n12.cnf

SHA-256 of the uncompressed files:

    03e20d7c2abf62a4d6451d7628ec019f3c3b0b2db2905eb017e0ceae661054d7  n9.cnf
    efe0f9bc7c1a46efb6384fccd80098ea3075eb852355ff072b6ad29cdd1f34d6  n10.cnf
    980e077b347630ed0a25ec8f6256768cfd03731b691947da8cb1f34a0a2adccf  n11.cnf
    04774df712477f2f112090057c432c6825ce783b7502b77e5f35987472186c03  n12.cnf
    4460c5a999312bfef1be0083a45b709dd7f9c76b65527218bfbfbb60b6bbe1dd  n9.drat
    c887333da323141ec12c2724248bfa67fd1548c65764775b0c32d255fe10532a  n10.drat
    8c684c39ee7194bf6031304fe953ef80d1750a50aa65f31a4f61f7a074e6ea27  n11.drat
    efcedf5b690d422ff5278d9eb82197d26df9d85bf36ae30013ada9f604768665  n12.drat
