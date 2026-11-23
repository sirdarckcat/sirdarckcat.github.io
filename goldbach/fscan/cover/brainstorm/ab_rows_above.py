# Two covers with the same rows below Q and different rows above: where do their successes land?
#
#   python3 brainstorm/ab_rows_above.py dir tagA tagB        (dir holds spec_<tag>.json and found_<tag>.jsonl of search.py)
#
# For each cover: the uncovered primes just above Q, the number of successes, the mean of g - Q and the fraction of
# successes with g >= Q + d, against the model in which a success survives each uncovered prime above Q with
# probability 1 - p, p = boost / ln N (so the fraction is (1 - p)^(uncovered primes in [Q, Q + d))).
import json, math, sys, bisect
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
PR = primes_upto(200000)
out = {}
D = sys.argv[1]
for t in sys.argv[2:]:
    spec = json.load(open(f"{D}/spec_{t}.json"))[0]; found = [json.loads(l) for l in open(f"{D}/found_{t}.jsonl")]
    Q = spec["Q"]; cover = [tuple(c) for c in spec["cover"]]
    unc = [q for q in PR if q >= Q and all(q % r != a for r, a in cover)]
    p = spec["boost"] / math.log(int(found[0]["N"])); n = len(found)
    g = [f["g"] for f in found]; kmaxdone = max(f["k"] for f in found)
    model_mean = sum((unc[j] - Q) * (1 - p) ** j * p for j in range(len(unc)))
    line = f"{t}: rows below Q {len(spec['residual'])}; uncovered primes in Q..Q+2000 / +4000 / +8000: " + " / ".join(str(bisect.bisect_left(unc, Q + d)) for d in (2000, 4000, 8000))
    line += f"; successes {n} (up to k = {kmaxdone}); mean g - Q {sum(g)/n - Q:.0f} +- {(sum((x - sum(g)/n) ** 2 for x in g) / n) ** .5 / n ** .5:.0f} (model {model_mean:.0f}); median g {sorted(g)[n // 2]}"
    print(line)
    for d in (1000, 2000, 4000, 6000, 8000, 12000):
        j = bisect.bisect_left(unc, Q + d)
        print(f"     g >= Q + {d:5d}: {sum(x >= Q + d for x in g) / n:.4f}   model (1-p)^{j} = {(1 - p) ** j:.4f}")
    out[t] = (n, sum(g) / n - Q)
if len(out) == 2:
    a, b = [out[t] for t in sys.argv[2:4]]
    print(f"successes {a[0]} against {b[0]}; mean g - Q {a[1]:.0f} against {b[1]:.0f} (x{a[1] / b[1]:.2f})")
