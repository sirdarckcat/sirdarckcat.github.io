#!/usr/bin/env python3
"""D(n) with cover_ub: climb from a value known to be attained.  At Y, proof mode either finds a cover (then its least unstruck odd prime q >= Y
is attained, and Y becomes the next prime after q) or proves no cover strikes every odd prime below Y (then D(n) = the last q).
    python3 findD.py n start [binary]"""
import sys, subprocess, re, time
n, Y = int(sys.argv[1]), int(sys.argv[2]); B = sys.argv[3] if len(sys.argv) > 3 else "./cover_ub"
def isp(x): return x > 1 and all(x % k for k in range(2, int(x ** .5) + 1))
def nextp(x):
    x += 1
    while not isp(x): x += 1
    return x
oddP = [q for q in range(3, 40000) if isp(q)]
q_att, vec_att, t_all = None, None, time.time()
while True:
    t0 = time.time(); out = subprocess.run([B, str(n), str(Y), "proof"], capture_output=True, text=True).stdout
    nodes = re.search(r"nodes=(\d+)", out).group(1)
    if "COVER FOUND" in out:
        cov = [tuple(map(int, t.split(":"))) for t in re.search(r"vector:(.*)", out).group(1).split()]
        q = next(p for p in oddP if not any(p % r == c for r, c in cov))
        assert q >= Y, (q, Y)
        print(f"n={n}: a cover of every odd prime below {Y} ({nodes} nodes, {time.time()-t0:.1f} s); its least unstruck prime {q}", flush=True)
        q_att, vec_att = q, cov; Y = nextp(q)
    elif "NO COVER" in out:
        print(f"n={n}: NO COVER below {Y} ({nodes} nodes, {time.time()-t0:.1f} s)", flush=True)
        break
    else:
        print("unexpected output:", out); sys.exit(1)
print(f"FINDD n={n} D={q_att} (attained by the vector; no vector strikes every odd prime below {Y}) seconds={time.time()-t_all:.1f} vector: " + " ".join(f"{r}:{c}" for r, c in vec_att))
