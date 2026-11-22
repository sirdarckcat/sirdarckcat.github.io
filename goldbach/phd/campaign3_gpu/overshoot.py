"""How far past its threshold each campaign3 hit went, against the model.

For a hit at threshold Q with least summand g, the rows it survived beyond Q are the primes q in [Q, g) that its cover leaves
uncovered (q mod r != a_r for every class): each such N - q was a composite the cover did not force. The model makes each of
them prime with probability p = boost / ln N, independently, so the count is geometric: expected (1 - p) / p, tail
P(>= u) = (1 - p)^u, and the sum over n hits is negative binomial.

    python3 overshoot.py hits.jsonl SPECS.json [SPECS2.json ...] > overshoot.json
"""
import json, math, sys
import numpy as np
from sympy import primerange


def nb_sf(s, n, p):
    """P(S >= s) for S = sum of n iid geometric failure counts with success probability p."""
    acc = sum(math.exp(math.lgamma(j + n) - math.lgamma(j + 1) - math.lgamma(n) + n * math.log(p) + j * math.log1p(-p)) for j in range(s))
    return max(0.0, 1.0 - acc)


def main():
    L = lambda x: json.loads(x) if isinstance(x, str) else x
    specs = {}
    for f in sys.argv[2:]:
        for v in json.load(open(f)):
            specs[v["name"]] = v
    hits = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    P = np.array(list(primerange(2, 600000)), dtype=np.int64)
    rows = []
    for h in hits:
        v = specs[h["name"].split("@")[0]]
        Q, g, N = int(v["Q"]), int(h["g"]), int(h["N"])
        seg = P[(P >= Q) & (P < g)]
        cv = np.zeros(len(seg), dtype=bool)
        for r, a in L(v["cover"]):
            cv |= (seg % int(r)) == int(a)
        u = int((~cv).sum())
        p = float(v["boost"]) / math.log(N)
        rows.append(dict(name=h["name"], gpu=h.get("gpu"), Q=Q, g=g, digits=h["digits"], rows_survived=u,
                         expected=round((1 - p) / p, 2), p_row=round(p, 5), tail=round((1 - p) ** u, 4)))
    out = dict(rows=rows, by_Q={})
    for Q in sorted(set(r["Q"] for r in rows)):
        rs = [r for r in rows if r["Q"] == Q]
        n, s = len(rs), sum(r["rows_survived"] for r in rs)
        p = sum(r["p_row"] for r in rs) / n
        out["by_Q"][str(Q)] = dict(hits=n, rows_survived=s, expected=round(sum(r["expected"] for r in rs), 1), tail=round(nb_sf(s, n, p), 4))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
