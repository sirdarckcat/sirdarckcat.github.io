#!/usr/bin/env python3
"""Toy-scale lattice list-decoder for Chinese Remainder (CRT) codes.

Code.  Positions are the odd primes 3 <= p_1 < ... < p_n < 300 (n = 61).
The codeword of an integer m is (m mod p_1, ..., m mod p_n).  Given a
received word r = (r_1, ..., r_n) and a bound B, list decoding asks for
all |m| <= B whose agreement mass  A(m) = sum_{i : m = r_i mod p_i} ln p_i
is large.  The Johnson-type radius (Goldreich-Ron-Sudan / GSS FOCS 2000,
Howgrave-Graham form) is A_J = sqrt(ln B * ln M) with M = prod p_i: above
A_J a poly-time lattice algorithm provably finds all solutions; below A_J
exponentially many high-agreement m exist but no efficient algorithm is
known.  This module measures empirically where *practical* LLL succeeds
relative to A_J on solution-abundant planted instances.

Decoder (Howgrave-Graham: "m = R mod D for some divisor D >= M^beta of M,
|m| <= B").  Let R be the CRT lift of r mod M.  Pick degree ell and
multiplicity z <= ell and build the (ell+1)-dimensional lattice whose rows
are the coefficient vectors of g(B*y) (i.e. the x^k coefficient is scaled
by B^k) for
    g_a(x) = M^(z-a) * (x - R)^a          a = 0 .. z
    h_j(x) = x^j * (x - R)^z              j = 1 .. ell - z
For any m with m = R (mod D), D | M, every lattice polynomial c satisfies
D^z | c(m); if additionally ||c(B y)||_2 < D^z / sqrt(ell+1) and |m| <= B
then |c(m)| < D^z, hence c(m) = 0 over Z (Howgrave-Graham's lemma).  So we
LLL-reduce, read the short rows back as integer polynomials c(x) (the x^k
coefficient is entry_k / B^k, exactly divisible), and report their integer
roots with |m| <= B.  Balancing determinant against z*ln(D) reproduces the
Johnson radius as ell -> infinity: success iff A > sqrt(ln B * ln M).

LLL backend: python-flint (FLINT fmpz_mat.lll, delta=0.99) when available,
otherwise a pure-Python exact-integer LLL (Cohen Alg. 2.6.7) fallback.
Integer roots: FLINT fmpz_poly.factor when available, else sympy.

Usage:
    python3 decoder.py --selftest             # LLL + conventions checks
    python3 decoder.py --sanity               # rho=1.4 recovery + brute force
    python3 decoder.py --sweep --trials 20 --jobs 4 --out results.json
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from multiprocessing import Pool

try:
    import flint  # python-flint

    HAVE_FLINT = True
    LLL_BACKEND = f"python-flint {flint.__version__} (FLINT fmpz_mat.lll, delta=0.99, eta=0.51)"
except ImportError:  # pragma: no cover - fallback path
    flint = None
    HAVE_FLINT = False
    LLL_BACKEND = "pure-Python exact-integer LLL (Cohen Alg. 2.6.7, delta=0.99)"

import sympy

# ----------------------------------------------------------------------
# Code parameters (predeclared)
# ----------------------------------------------------------------------
PRIMES = tuple(sympy.primerange(3, 300))  # 3, 5, ..., 293  (n = 61)
N = len(PRIMES)
LNP = tuple(math.log(p) for p in PRIMES)
M = math.prod(PRIMES)
LN_M = sum(LNP)
B = 10**12
LN_B = math.log(B)
A_J = math.sqrt(LN_B * LN_M)  # Johnson-type radius (in ln-mass units)

ELL_GRID = (12, 20, 30)  # lattice degrees tried per instance
RHO_GRID = (0.70, 0.80, 0.90, 1.00, 1.10, 1.25)

# CRT lift precomputation: R = sum r_i * CRT_COEF_i mod M
_CRT_COEF = tuple((M // p) * pow(M // p, -1, p) for p in PRIMES)
_BPOW = [B**k for k in range(max(ELL_GRID) + 2)]


def _bpow(k):
    while k >= len(_BPOW):
        _BPOW.append(_BPOW[-1] * B)
    return _BPOW[k]


# ----------------------------------------------------------------------
# CRT code basics
# ----------------------------------------------------------------------
def crt_lift(residues):
    """Unique R in [0, M) with R = r_i (mod p_i) for all i."""
    return sum(r * c for r, c in zip(residues, _CRT_COEF)) % M


def agreement_mass(m, residues):
    """A(m) = sum of ln p_i over positions where m = r_i (mod p_i)."""
    return sum(lnp for p, lnp, r in zip(PRIMES, LNP, residues) if m % p == r)


def gen_instance(rho, rng):
    """Planted instance at target agreement ratio rho = A / A_J.

    m* uniform in [B/2, B); a uniformly random subset S of positions grown
    greedily until sum_{S} ln p >= rho * A_J; r_i = m* mod p_i on S, and
    uniform in [0, p_i) \\ {m* mod p_i} off S.
    """
    m_star = rng.randrange(B // 2, B)
    order = list(range(N))
    rng.shuffle(order)
    target = rho * A_J
    agree = set()
    mass = 0.0
    for i in order:
        if mass >= target:
            break
        agree.add(i)
        mass += LNP[i]
    residues = []
    for i, p in enumerate(PRIMES):
        c = m_star % p
        if i in agree:
            residues.append(c)
        else:
            t = rng.randrange(p - 1)  # uniform on [0, p) excluding c
            residues.append(t + 1 if t >= c else t)
    return {"m_star": m_star, "agree": agree, "planted_mass": mass, "residues": residues}


# ----------------------------------------------------------------------
# Lattice construction
# ----------------------------------------------------------------------
def build_basis(R, ell, z):
    """Rows = coefficient vectors of g_a(B y), h_j(B y); dimension ell+1.

    Triangular by degree: diagonal M^(z-a) B^a (a <= z), then B^(z+j).
    """
    assert 1 <= z <= ell
    # (x - R)^a coefficients, a = 0..z (constant first)
    pw = [[1]]
    for _ in range(z):
        prev = pw[-1]
        cur = [0] * (len(prev) + 1)
        for k, c in enumerate(prev):
            cur[k] += c * (-R)
            cur[k + 1] += c
        pw.append(cur)
    rows = []
    for a in range(z + 1):
        mz = M ** (z - a)
        row = [0] * (ell + 1)
        for k, c in enumerate(pw[a]):
            row[k] = c * mz * _bpow(k)
        rows.append(row)
    for j in range(1, ell - z + 1):
        row = [0] * (ell + 1)
        for k, c in enumerate(pw[z]):
            row[j + k] = c * _bpow(j + k)
        rows.append(row)
    return rows


# ----------------------------------------------------------------------
# LLL reduction
# ----------------------------------------------------------------------
def lll_reduce(rows):
    if HAVE_FLINT:
        red = flint.fmpz_mat(rows).lll(delta=0.99, eta=0.51)
        return [[int(red[i, j]) for j in range(red.ncols())] for i in range(red.nrows())]
    return lll_integer(rows)


def lll_integer(basis, delta_num=99, delta_den=100):
    """Exact-integer LLL (Cohen, Alg. 2.6.7), for independent integer rows.

    Pure-Python fallback; returns new LLL-reduced rows spanning the same
    lattice.  D[i] = Gram determinant of rows 0..i-1 (D[0] = 1),
    lam[i][j] = mu_{i,j} * D[j+1] are the exact integer GS data.
    """
    b = [list(row) for row in basis]
    n = len(b)
    if n <= 1:
        return b
    D = [0] * (n + 1)
    D[0] = 1
    lam = [[0] * n for _ in range(n)]

    def dot(u, v):
        return sum(x * y for x, y in zip(u, v))

    def gso_row(i):
        for j in range(i + 1):
            u = dot(b[i], b[j])
            for k in range(j):
                u = (D[k + 1] * u - lam[i][k] * lam[j][k]) // D[k]
            if j < i:
                lam[i][j] = u
            else:
                assert u > 0, "rows must be linearly independent"
                D[i + 1] = u

    def red(k, l):  # size-reduce b_k against b_l
        if 2 * abs(lam[k][l]) > D[l + 1]:
            q = (2 * lam[k][l] + D[l + 1]) // (2 * D[l + 1])  # round(mu)
            b[k] = [x - q * y for x, y in zip(b[k], b[l])]
            lam[k][l] -= q * D[l + 1]
            for i in range(l):
                lam[k][i] -= q * lam[l][i]

    gso_row(0)
    kmax = 0
    k = 1
    while k < n:
        if k > kmax:
            kmax = k
            gso_row(k)
        red(k, k - 1)
        lmb = lam[k][k - 1]
        if delta_den * (D[k + 1] * D[k - 1] + lmb * lmb) < delta_num * D[k] * D[k]:
            # swap rows k-1, k and fix up exact GS data (Cohen 2.6.7 SWAP)
            b[k - 1], b[k] = b[k], b[k - 1]
            for j in range(k - 1):
                lam[k - 1][j], lam[k][j] = lam[k][j], lam[k - 1][j]
            Bnew = (D[k - 1] * D[k + 1] + lmb * lmb) // D[k]
            for i in range(k + 1, kmax + 1):
                t = lam[i][k]
                lam[i][k] = (D[k + 1] * lam[i][k - 1] - lmb * t) // D[k]
                lam[i][k - 1] = (Bnew * t + lmb * lam[i][k]) // D[k + 1]
            D[k] = Bnew
            k = max(1, k - 1)
        else:
            for l in range(k - 2, -1, -1):
                red(k, l)
            k += 1
    return b


# ----------------------------------------------------------------------
# From short vectors to integer roots
# ----------------------------------------------------------------------
def vec_to_poly(vec):
    """Vector of c(B y) coefficients -> integer coefficients of c(x)."""
    coeffs = []
    for k, v in enumerate(vec):
        q, rem = divmod(v, _bpow(k))
        assert rem == 0, "lattice vector not divisible by B^k -- bug"
        coeffs.append(q)
    while coeffs and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs  # constant first


def integer_roots(coeffs, bound=B):
    """Integer roots m (|m| <= bound) of c(x) given constant-first coeffs."""
    if len(coeffs) <= 1:
        return set()
    roots = set()
    if HAVE_FLINT:
        _content, factors = flint.fmpz_poly(coeffs).factor()
        lin = [(int(f[0]), int(f[1])) for f, _ in factors if f.degree() == 1]
    else:
        x = sympy.Symbol("x")
        _c, factors = sympy.Poly(list(reversed(coeffs)), x).factor_list()
        lin = []
        for f, _ in factors:
            if f.degree() == 1:
                a1, a0 = f.all_coeffs()
                lin.append((int(a0), int(a1)))
    for a0, a1 in lin:  # factor a1*x + a0
        q, rem = divmod(-a0, a1)
        if rem == 0 and abs(q) <= bound:
            roots.add(q)
    return roots


def decode(residues, ell, z, factor_rows=None):
    """Run the lattice decoder; return (roots dict m -> best row rank, diag)."""
    R = crt_lift(residues)
    rows = build_basis(R, ell, z)
    t0 = time.time()
    red = lll_reduce(rows)
    t_lll = time.time() - t0
    ranked = sorted(red, key=lambda v: sum(x * x for x in v))
    if factor_rows is not None:
        ranked = ranked[:factor_rows]
    t0 = time.time()
    roots = {}
    for rank, v in enumerate(ranked):
        for m in integer_roots(vec_to_poly(v)):
            roots.setdefault(m, rank)
    t_roots = time.time() - t0
    diag = {
        "ln_shortest": 0.5 * math.log(sum(x * x for x in ranked[0])),
        "t_lll": round(t_lll, 3),
        "t_roots": round(t_roots, 3),
    }
    return roots, diag


# ----------------------------------------------------------------------
# Experiment
# ----------------------------------------------------------------------
def choose_z(ell, beta):
    return max(1, min(ell, round(ell * beta)))


def run_trial(rho, trial, seed_tag="v1"):
    """One planted instance at ratio rho, decoded with the full ell grid."""
    rng = random.Random(f"toycrt:{seed_tag}:{rho:.4f}:{trial}")
    inst = gen_instance(rho, rng)
    beta = inst["planted_mass"] / LN_M
    per_ell = []
    union = {}  # m -> mass
    for ell in ELL_GRID:
        z = choose_z(ell, beta)
        roots, diag = decode(inst["residues"], ell, z)
        infos = []
        for m, rank in sorted(roots.items()):
            mass = agreement_mass(m, inst["residues"])
            infos.append({"m": m, "mass": round(mass, 3), "row_rank": rank})
            if m not in union or union[m] < mass:
                union[m] = mass
        per_ell.append(
            {
                "ell": ell,
                "z": z,
                "recovered": inst["m_star"] in roots,
                "n_roots": len(roots),
                "roots": infos,
                # Howgrave-Graham sufficient condition margin (log scale):
                # need ln||v|| < z*A - 0.5*ln(ell+1) for the guarantee.
                "hg_bound": round(z * inst["planted_mass"] - 0.5 * math.log(ell + 1), 3),
                **diag,
            }
        )
    recovered = any(e["recovered"] for e in per_ell)
    others = {m: a for m, a in union.items() if m != inst["m_star"]}
    any_solution = any(a >= 0.9 * rho * A_J for a in others.values())
    best_mass = max(union.values(), default=0.0)
    return {
        "rho": rho,
        "trial": trial,
        "m_star": inst["m_star"],
        "planted_mass": round(inst["planted_mass"], 3),
        "n_agree": len(inst["agree"]),
        "recovered": recovered,
        "any_solution": any_solution,
        "best_mass": round(best_mass, 3),
        "best_over_AJ": round(best_mass / A_J, 4),
        "per_ell": per_ell,
    }


def _worker(job):
    rho, trial, seed_tag = job
    return run_trial(rho, trial, seed_tag)


def summarize(records):
    by_rho = {}
    for rec in records:
        by_rho.setdefault(rec["rho"], []).append(rec)
    rows = []
    for rho in sorted(by_rho):
        recs = by_rho[rho]
        n = len(recs)
        rows.append(
            {
                "rho": rho,
                "trials": n,
                "recovery_pct": 100.0 * sum(r["recovered"] for r in recs) / n,
                "any_solution_pct": 100.0 * sum(r["any_solution"] for r in recs) / n,
                "mean_best_over_AJ": sum(r["best_over_AJ"] for r in recs) / n,
                "mean_planted_over_AJ": sum(r["planted_mass"] for r in recs) / n / A_J,
                "recovery_by_ell": {
                    str(ell): sum(
                        any(e["recovered"] for e in r["per_ell"] if e["ell"] == ell)
                        for r in recs
                    )
                    for ell in ELL_GRID
                },
            }
        )
    # empirical 50% recovery threshold by linear interpolation
    rho_star = None
    for lo, hi in zip(rows, rows[1:]):
        f1, f2 = lo["recovery_pct"], hi["recovery_pct"]
        if f1 < 50.0 <= f2:
            rho_star = lo["rho"] + (50.0 - f1) * (hi["rho"] - lo["rho"]) / (f2 - f1)
            break
    if rho_star is None:
        if rows and rows[0]["recovery_pct"] >= 50.0:
            rho_star = rows[0]["rho"]  # threshold at or below grid minimum
        elif rows and rows[-1]["recovery_pct"] < 50.0:
            rho_star = float("inf")  # never reached on the grid
    return rows, rho_star


def run_sweep(rhos, trials, jobs, out_json, seed_tag="v1"):
    jobs_list = [(rho, t, seed_tag) for rho in rhos for t in range(trials)]
    t0 = time.time()
    records = []
    if jobs > 1:
        with Pool(jobs) as pool:
            for i, rec in enumerate(pool.imap(_worker, jobs_list)):
                records.append(rec)
                print(
                    f"[{i + 1}/{len(jobs_list)}] rho={rec['rho']:.2f} trial={rec['trial']} "
                    f"recovered={rec['recovered']} best/A_J={rec['best_over_AJ']:.3f}",
                    flush=True,
                )
    else:
        for i, job in enumerate(jobs_list):
            rec = _worker(job)
            records.append(rec)
            print(
                f"[{i + 1}/{len(jobs_list)}] rho={rec['rho']:.2f} trial={rec['trial']} "
                f"recovered={rec['recovered']} best/A_J={rec['best_over_AJ']:.3f}",
                flush=True,
            )
    table, rho_star = summarize(records)
    out = {
        "params": {
            "primes": f"odd primes in (2, 300), n={N}",
            "ln_M": LN_M,
            "B": B,
            "ln_B": LN_B,
            "A_J": A_J,
            "ell_grid": list(ELL_GRID),
            "trials_per_rho": trials,
            "seed_tag": seed_tag,
            "lll_backend": LLL_BACKEND,
            "wall_time_s": round(time.time() - t0, 1),
        },
        "summary": table,
        "rho_star_50pct_recovery": rho_star,
        "trials": records,
    }
    with open(out_json, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(table, indent=1))
    print("rho* (50% recovery) =", rho_star)
    print("wrote", out_json)
    return out


# ----------------------------------------------------------------------
# Self-tests and sanity checks
# ----------------------------------------------------------------------
def selftest():
    """Cheap invariant checks of every building block."""
    # CRT lift round-trips
    rng = random.Random(1234)
    for _ in range(5):
        m = rng.randrange(M)
        assert crt_lift([m % p for p in PRIMES]) == m
    # polynomial conventions (flint constant-first indexing)
    if HAVE_FLINT:
        f = flint.fmpz_poly([6, 5, 1])  # x^2 + 5x + 6
        assert int(f[0]) == 6 and int(f[1]) == 5 and f.degree() == 2
    assert integer_roots([6, 5, 1]) == {-2, -3}  # (x+2)(x+3)
    assert integer_roots([-10**12, 0, 0, 1], bound=10**4) == {10**4}  # x^3 - 10^12
    # LLL finds a planted short vector hidden by huge unimodular mixing
    dim, planted = 8, [3, -1, 4, 1, -5, 9, -2, 6]
    basis = [planted] + [
        [rng.randrange(-(10**25), 10**25) for _ in range(dim)] for _ in range(dim - 1)
    ]
    for name, fn in [("backend", lll_reduce), ("pure-python", lll_integer)]:
        red = sorted(fn(basis), key=lambda v: sum(x * x for x in v))
        assert red[0] in ([planted, [-x for x in planted]]), f"LLL ({name}) missed planted vector"
    # pure-python LLL agrees with flint on random bases (same lattice via HNF,
    # same successive minima profile up to sign choices is not required)
    if HAVE_FLINT:
        for t in range(3):
            mat = [[rng.randrange(-(10**8), 10**8) for _ in range(6)] for _ in range(6)]
            a = flint.fmpz_mat(mat)
            red_py = lll_integer(mat)
            assert flint.fmpz_mat(red_py).hnf() == a.hnf(), "fallback LLL changed the lattice"
            n_py = min(sum(x * x for x in v) for v in red_py)
            n_fl = min(
                sum(int(a2[i, j]) ** 2 for j in range(6)) for a2 in [a.lll()] for i in range(6)
            )
            assert n_py <= 4 * n_fl and n_fl <= 4 * n_py, "fallback LLL quality mismatch"
    # decoder basis is triangular with the right determinant profile
    Rtest = crt_lift([rng.randrange(p) for p in PRIMES])
    rows = build_basis(Rtest, 8, 3)
    for i, row in enumerate(rows):
        assert all(c == 0 for c in row[i + 1 :])
        expected = (M ** (3 - i) if i <= 3 else 1) * _bpow(i)
        assert abs(row[i]) == expected
    print("selftest: all checks passed")


def sanity_high_rho(trials=5, rho=1.4, seed_tag="sanity"):
    """At rho = 1.4 (well above A_J) recovery must be ~100%."""
    ok = 0
    for t in range(trials):
        rec = run_trial(rho, t, seed_tag)
        ok += rec["recovered"]
        print(
            f"  rho={rho} trial={t}: recovered={rec['recovered']} "
            f"planted_mass={rec['planted_mass']:.1f} (A_J={A_J:.1f})",
            flush=True,
        )
    print(f"sanity_high_rho: {ok}/{trials} recovered")
    assert ok == trials, "high-rho recovery failed -- decoder is buggy"
    return ok, trials


def sanity_bruteforce(rho=1.0, trial=0, seed_tag="sanity-bf", window=2000):
    """Verify instance generation + agreement computation by direct scan."""
    rng = random.Random(f"toycrt:{seed_tag}:{rho:.4f}:{trial}")
    inst = gen_instance(rho, rng)
    m_star, residues = inst["m_star"], inst["residues"]
    # (1) planted positions agree, non-planted positions disagree
    for i, p in enumerate(PRIMES):
        if i in inst["agree"]:
            assert residues[i] == m_star % p
        else:
            assert residues[i] != m_star % p
    # (2) agreement_mass(m*) equals the planted mass exactly
    assert abs(agreement_mass(m_star, residues) - inst["planted_mass"]) < 1e-9
    # (3) CRT lift consistency: p | (m* - R) exactly on the planted set
    R = crt_lift(residues)
    for i, p in enumerate(PRIMES):
        assert ((m_star - R) % p == 0) == (i in inst["agree"])
    # (4) brute-force scan near m*: no neighbour approaches the planted mass
    best_other = max(
        agreement_mass(m, residues)
        for m in range(m_star - window, m_star + window + 1)
        if m != m_star
    )
    print(
        f"sanity_bruteforce: planted_mass={inst['planted_mass']:.2f}, "
        f"best mass among {2 * window} neighbours = {best_other:.2f}"
    )
    assert best_other < inst["planted_mass"]
    print("sanity_bruteforce: all checks passed")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sanity", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--pilot", action="store_true", help="time one trial per rho extreme")
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--out", default="results.json")
    args = ap.parse_args()
    print(
        f"n={N} primes in (2,300); ln M={LN_M:.3f}; B=1e12 (ln B={LN_B:.3f}); "
        f"A_J={A_J:.3f}; backend: {LLL_BACKEND}"
    )
    if args.selftest:
        selftest()
    if args.sanity:
        sanity_bruteforce()
        sanity_high_rho()
    if args.pilot:
        for rho in (0.70, 1.00, 1.25):
            t0 = time.time()
            rec = run_trial(rho, 0, "pilot")
            times = [(e["ell"], e["z"], e["t_lll"], e["t_roots"]) for e in rec["per_ell"]]
            print(
                f"pilot rho={rho}: recovered={rec['recovered']} "
                f"best/A_J={rec['best_over_AJ']:.3f} total={time.time() - t0:.1f}s "
                f"(ell,z,t_lll,t_roots)={times}"
            )
    if args.sweep:
        run_sweep(RHO_GRID, args.trials, args.jobs, args.out)


if __name__ == "__main__":
    main()
