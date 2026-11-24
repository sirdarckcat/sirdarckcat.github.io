#!/usr/bin/env python3
"""An independent check of D(n) by a SAT solver (no code shared with desert_fast*.c).

    python3 desert_sat.py n D [solver]          (solver: a pysat name, default cadical195)

Variables x[m][c]: modulus m (the m-th odd prime r) takes class c, 0 <= c < r.  Exactly one class per modulus (one clause "at least one" and a
cardinality encoding "at most one").  For an odd prime q, the clause OR_m x[m][q mod r_m] says some modulus strikes q.

  * "every odd prime below p' is struck", p' the next prime after D, must be UNSAT: no residue vector reaches p', so D(n) < p';
  * "every odd prime below D is struck" must be SAT, and the model is a vector whose least unstruck odd prime is checked here to be >= D.
Together: D(n) = D.  With --drat FILE the UNSAT run also writes a DRAT proof (solvers that support it), and with --cnf FILE the UNSAT formula in
DIMACS: a DRAT checker (e.g. drat-trim FILE.cnf FILE.drat, or a verified one) can check the pair.
"""
import sys, time
from pysat.formula import CNF
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def primes_upto(lim):
    s = bytearray([1]) * (lim + 1); s[0] = s[1] = 0
    for i in range(2, int(lim ** 0.5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(3, lim + 1) if s[i]]


def build(n, X):
    """the CNF of: a residue vector on the first n odd primes striking every odd prime below X; returns (cnf, var map, moduli)"""
    P = primes_upto(max(X, 4000))
    mods = P[:n]
    var, nv = {}, 0
    for m, r in enumerate(mods):
        for c in range(r):
            nv += 1; var[(m, c)] = nv
    cnf = CNF()
    for m, r in enumerate(mods):
        lits = [var[(m, c)] for c in range(r)]
        cnf.append(lits)                                                     # at least one class
        amo = CardEnc.atmost(lits=lits, bound=1, top_id=nv, encoding=EncType.seqcounter)
        nv = max(nv, amo.nv)
        cnf.extend(amo.clauses)                                              # at most one class
    for q in P:
        if q >= X: break
        cnf.append([var[(m, q % r)] for m, r in enumerate(mods)])            # q is struck by some modulus
    return cnf, var, mods


def solve(n, X, solver="cadical195", drat=None, cnf_path=None):
    cnf, var, mods = build(n, X)
    if cnf_path:
        cnf.to_file(cnf_path)                                                # DIMACS: the formula a DRAT checker reads beside the proof
    t0 = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses, with_proof=bool(drat)) as s:
        sat = s.solve()
        model = s.get_model() if sat else None
        proof = s.get_proof() if (drat and not sat) else None
    dt = time.time() - t0
    vec = None
    if sat:
        pos = set(l for l in model if l > 0)
        vec = [next(c for c in range(r) if var[(m, c)] in pos) for m, r in enumerate(mods)]
    if proof is not None:
        with open(drat, "w") as f:
            f.write("\n".join(proof) + "\n")
    return sat, vec, mods, dt, len(cnf.clauses)


def least_unstruck(vec, mods):
    for q in primes_upto(20000):
        if all(q % r != c for r, c in zip(mods, vec)):
            return q


def main():
    n, D = int(sys.argv[1]), int(sys.argv[2])
    solver = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "cadical195"
    drat = sys.argv[sys.argv.index("--drat") + 1] if "--drat" in sys.argv else None
    P = primes_upto(20000)
    nxt = next(p for p in P if p > D)
    sat1, vec1, mods, dt1, ncl1 = solve(n, D, solver)
    q1 = least_unstruck(vec1, mods) if sat1 else None
    ok1 = sat1 and q1 >= D
    print(f"n={n}: strike every odd prime below {D}: {'SAT' if sat1 else 'UNSAT'} in {dt1:.1f} s ({ncl1} clauses)"
          + (f", the model's least unstruck prime {q1}" if sat1 else "") + (" ok" if ok1 else " WRONG"), flush=True)
    cnfp = sys.argv[sys.argv.index("--cnf") + 1] if "--cnf" in sys.argv else None
    sat2, vec2, mods, dt2, ncl2 = solve(n, nxt, solver, drat, cnfp)
    ok2 = not sat2
    print(f"n={n}: strike every odd prime below {nxt}: {'SAT' if sat2 else 'UNSAT'} in {dt2:.1f} s ({ncl2} clauses)" + (" ok" if ok2 else " WRONG: D is not the maximum"), flush=True)
    print(f"SAT-CHECK n={n} D={D}: {'CONFIRMED' if ok1 and ok2 else 'FAILED'} ({solver})")
    sys.exit(0 if ok1 and ok2 else 1)


if __name__ == "__main__":
    main()
