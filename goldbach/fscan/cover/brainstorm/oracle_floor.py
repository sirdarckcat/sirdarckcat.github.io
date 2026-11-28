# What would a perfect "small representative" solver buy?  For the first m odd primes as moduli (modulus e^theta,
# possibly far above 1e200) the number of covers with about k uncovered rows is e^S(k) (ptcover, thermodynamic
# integration).  A cover has its representative below X = 1e200 with probability e^-(theta - ln X), so the best cover
# that still has a representative below X sits where S(k) = theta - ln X.  E = k * boost / ln X.
# (A success needs e^E such representatives, not one: with S(k) = theta - ln X + E the floor is about 20 rows,
# 0.5 nats, higher than the column printed here.  ptcover holds at most 256 moduli.)
import math, subprocess, sys, os
W = os.path.dirname(os.path.abspath(__file__)) + "/"    # run from cover/: python3 brainstorm/oracle_floor.py Q m1,m2,... sweeps
Q = int(sys.argv[1]); LNX = 200 * math.log(10)
def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
P = primes_upto(5000)[1:]
print(f"Q = {Q}; columns: moduli, largest, theta, oversize (nats), random mean k, k at the entropy needed, E there, best k found (E if no size limit)")
for m in [int(a) for a in sys.argv[2].split(",")]:
    mods = P[:m]; theta = math.log(2) + sum(math.log(r) for r in mods); boost = 2.0
    for r in mods: boost *= r / (r - 1)
    fn = W + f"first{m}.mod"; open(fn, "w").write("".join(f"{r}\n" for r in mods))
    sweeps = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
    out = subprocess.run(["./ptcover", str(Q), fn, str(sweeps), "9", "betas56.txt"], capture_output=True, text=True).stdout
    rows = [l.split() for l in out.splitlines() if l and l[0] == " "]
    tab = [(float(r[0]), float(r[1]), float(r[4])) for r in rows]          # beta, <k>, S
    best = int([l for l in out.splitlines() if "best k" in l][0].split(":")[1])
    need = theta - LNX
    if need <= 0: kstar = best
    else:
        kstar = None
        for (b0, k0, s0), (b1, k1, s1) in zip(tab, tab[1:]):
            if s0 >= need >= s1 and s0 != s1:
                kstar = k0 + (k1 - k0) * (s0 - need) / (s0 - s1); break
        if kstar is None: kstar = float("nan")
    print(f"{m:4d} {mods[-1]:5d} {theta:8.1f} {need:8.1f} {tab[0][1]:9.0f} {kstar:9.0f} {kstar*boost/LNX:7.2f} {best:7d} ({best*boost/LNX:.2f})", flush=True)
