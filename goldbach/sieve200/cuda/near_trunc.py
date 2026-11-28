"""Near-miss truncation of the row lists (search_gpu5 --near-truncate 1; the idea, the numbers and the trade-off are in NEARTRUNC.md).

A near-miss is a member whose FIRST probable-prime row q (rows ascending) is >= --near-miss (G): every row below G is composite.  Rows at or above G cannot change that event, but they are in the
bit matrix, in the alive count the selection ranks the members by, and in every member's row list.  With the row list cut at G (`truncate_spec`):
  * the sieve, the count, the selection and the Fermat rounds see only the rows below G; the kept members are the ones with the fewest alive rows BELOW G (the statistic the near-miss probability
    (1 - p)^c_G depends on), not the fewest over all rows (measured on the production vector at B = 1e8: x1.065 expected near-misses per kept member; design hits, which need every row composite, x0.937);
  * a member for which the GPU finds no probable prime among the rows below G is a "success" of the truncated list: `first_prp_row` finds, on the CPU, the first probable prime among the rows at or
    above G (the g(N) of the near-miss), or none (a success of the full list, which search.verify_success confirms on the FULL spec: `full_spec`).
"""
import gmpy2


def truncate_spec(spec, thr):
    """Cut spec["residual"] to the rows q < thr, in place, keeping the whole list as spec["residual_full"].  Idempotent.  Returns spec."""
    if "residual_full" not in spec:
        spec["residual_full"] = list(spec["residual"])
        spec["residual"] = [q for q in spec["residual_full"] if int(q) < int(thr)]
    return spec


def full_spec(spec):
    """The spec with its whole row list back (what search.verify_success must see); the same object when it was never truncated."""
    if "residual_full" not in spec:
        return spec
    return dict(spec, residual=spec["residual_full"])


def first_prp_row(spec, k, thr, reps=25):
    """The first row q >= thr of the FULL list (ascending) with N0 + k M - q a probable prime (gmpy2 BPSW + reps Miller-Rabin rounds), or None.  The rows below thr are not looked at: the GPU's
    base-2 Fermat tests found them composite (a composite verdict of a Fermat test is certain), and a covered offset is composite by its congruence."""
    N = gmpy2.mpz(int(spec["N0"])) + int(k) * gmpy2.mpz(int(spec["M"]))
    for q in spec.get("residual_full", spec["residual"]):
        q = int(q)
        if q >= thr and gmpy2.is_prime(N - q, reps):
            return q
    return None


def settle_successes(spec, ks, thr, verify_success, near):
    """The members the GPU reports as successes (no probable prime among the rows it was given), for a spec cut at thr: returns the verified design successes (records of verify_success on the full
    spec) and appends (k, q) to `near` for every one that turns out to be a near-miss (first probable prime q >= thr among the rows the GPU never saw).  The driver then verifies each near-miss as it
    always does (every prime below q composite, N - q prime)."""
    found = []
    for k in sorted(ks):
        res = verify_success(full_spec(spec), int(k))
        if res:
            found.append((int(k), res))
        elif "residual_full" in spec:
            q = first_prp_row(spec, int(k), thr)
            if q is not None:
                near.append((int(k), q))
    return found
