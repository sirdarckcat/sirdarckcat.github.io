# Independent check of a cover and export in the schema of goldbach/phd/campaign3/base_spec.json.
#   python3 mkspec.py tempering_Q122000_seed1.json name out.json [digits]
import json, math, sys
src, name, out = sys.argv[1], sys.argv[2], sys.argv[3]
D = int(sys.argv[4]) if len(sys.argv) > 4 else 199
t = json.load(open(src)); Q = t["Q"]; cover = [(int(r), int(a)) for r, a in t["cover"]]
def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True
assert all(is_prime(r) and r > 2 and 0 < a < r for r, a in cover) and len({r for r, _ in cover}) == len(cover)
rows = [q for q in range(3, Q) if is_prime(q)]
residual = [q for q in rows if all(q % r != a for r, a in cover)]
boost = 2.0; M = 2
for r, _ in cover: boost *= r / (r - 1); M *= r
# CRT: N0 even, N0 = a (mod r)
N0 = 0; mod = 2
for r, a in cover:
    inv = pow(mod, -1, r)
    N0 = N0 + mod * (((a - N0) * inv) % r); mod *= r
assert mod == M and N0 % 2 == 0 and all(N0 % r == a for r, a in cover) and 0 <= N0 < M
LN = D * math.log(10); E = len(residual) * boost / LN
spec = {"Q": Q, "cover": [[r, a] for r, a in cover], "residual": residual, "boost": boost,
        "m_digits": math.log10(M), "E": E, "n_digits_est": float(D), "N0": str(N0), "M": str(M), "name": name}
json.dump(spec, open(out, "w"))
print("Q %d  moduli %d  rows %d  left %d  boost %.4f  M digits %.2f  E(%d digits) %.3f  exact -k ln(1-p) %.3f  members below 1e200: %.3g" % (
    Q, len(cover), len(rows), len(residual), boost, math.log10(M), D, E, -len(residual) * math.log(1 - boost / LN), 10 ** 200 / M))
