"""Do two searches at the same threshold overlap?  (phd/crossreview_8ffe9d7a.md, section 3)

    python3 overlap_check.py ../records/height_11263digit_g1200109/record.json \
            ../records/bls_game1_11263digit_g1200109/record.json  [their sieve bound, default 2e8]

Rebuilds desert.py's progression P_t = 1 + 2^n (m0 + t*Mc) for the
record's threshold (paper's greedy cover), locates the other record in it,
re-derives the other search's test count from its sieve depth, and gives
the joint likelihood of the two waiting times under the density model.
"""
import json
import math
import os
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desert  # noqa: E402
from gmpy2 import mpz  # noqa: E402


def main(mine_path, theirs_path, their_sieve=200_000_000):
    mine, theirs = json.load(open(mine_path)), json.load(open(theirs_path))
    spec = desert.build_spec(mine["Q"], order="increasing")
    m0, Mc, n, g = mpz(spec["m0"]), mpz(spec["Mc"]), spec["n"], spec["g"]
    assert mine["n"] == n and mine["g"] == g
    same = (theirs["g"] == g and theirs["n"] == n and
            [list(x) for x in theirs["cover"]] == [x for x in spec["cover"] if x[0] != 2])
    print("same g, n and cover:", same)
    q, r = divmod(((mpz(theirs["N"]) - g - 1) >> n) - m0, Mc)
    assert r == 0, "their complement is not in this progression"
    t_theirs, t_mine = int(q), mine["t"]
    par = t_theirs % 2
    print(f"their hit is t = {t_theirs} (offset i = {theirs['i']}); desert.py's is t = {t_mine}")
    surv = desert.sieve_candidates(spec, 1 << 14, int(their_sieve), os.cpu_count())
    theirs_tested = [int(t) for t in surv if t % 2 == par and t <= t_theirs]
    print(f"t of their parity up to their hit surviving a sieve to {int(their_sieve):.0e}: "
          f"{len(theirs_tested)}   (their log: {theirs['search']['tests']} tests)")
    log = os.path.join(os.path.dirname(os.path.abspath(mine_path)), "search_tests.jsonl")
    mine_tested = {json.loads(line)["t"] for line in open(log)}
    both = mine_tested & set(theirs_tested)
    print(f"tests here {len(mine_tested)}, there {len(theirs_tested)}, same integer tested by both "
          f"{len(both)}, distinct integers {len(mine_tested | set(theirs_tested))}")
    boost = 2.0
    for rr, _ in spec["cover"]:
        if rr != 2:
            boost *= rr / (rr - 1)
    per_t = boost / ((n + int(Mc).bit_length()) * math.log(2))
    lam_m = (t_mine + 1) * per_t
    lam_t = (t_theirs + 1) / 2 * per_t
    lam_u = ((t_mine + 1) + (t_theirs - t_mine) / 2) * per_t
    p_le2 = sum(math.exp(-lam_u) * lam_u ** j / math.factorial(j) for j in range(3))
    print(f"expected primes: here {lam_m:.2f}, there {lam_t:.2f}, union {lam_u:.2f}; found in the union: 2")
    print(f"P(wait >= here) = {math.exp(-lam_m):.3f}, P(wait >= there) = {math.exp(-lam_t):.3f}, "
          f"product if independent = {math.exp(-lam_m - lam_t):.5f}, "
          f"actual joint P(<= 2 primes) = {p_le2:.3f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(float(a) for a in sys.argv[3:]))
