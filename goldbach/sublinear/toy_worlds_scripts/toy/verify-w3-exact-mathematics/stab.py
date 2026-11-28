# affine stabiliser of the best N of each instance: {(a,b): N(ax+b) = a^n N(x)}
import re, glob
from fam import world, poly
W = {q: world(q) for q in (3, 5, 7, 9)}
lines = []
for fn in ("enum_small.txt", "enum_mid.txt", "enum_big.txt"):
    try: lines += open(fn).read().split("\n")
    except FileNotFoundError: pass
i = 0
while i < len(lines):
    m = re.match(r"q (\d+) n (\d+) rows \d+ Gmax (\d+) cnt (\d+)", lines[i])
    if m:
        q, n, Gmax, cnt = map(int, m.groups())
        top = re.findall(r"\(G=(\d+) v=(\d+)\)", lines[i + 3])
        p, F, R, x, el = W[q]
        out = []
        for g, v in top:
            g = int(g); v = int(v)
            if g < Gmax: continue
            N = poly(R, F, el, q, v, n)
            st = [(str(a), str(b)) for a in el[1:] for b in el if N.compose(a * x + b) == a ** n * N]
            inF2 = (n % p == 0) and all(c == 0 for k, c in enumerate(N.coeffs()) if k % p and k > 2) and (N.coeffs()[2] == 1 if n > 2 else False)
            out.append(f"|Stab|={len(st)} {[s for s in st if s != ('1','0')]} N'=0:{N.derivative().is_zero()} F2:{inF2} N={N}")
        print(f"({q},{n}) Gmax={Gmax} x{cnt}: " + " || ".join(out))
    i += 1
