# The lead's gate (1) for research's top32 shift, my own asserts, independent of check_specs.py: each shifted top4s spec against the unshifted top4 spec of the same cover.
import json, sys
U = json.load(open(sys.argv[1])); S = json.load(open(sys.argv[2]))
KLO, TOP, LO, HI = (1 << 32) - 16 * (1 << 25), 1 << 32, 10 ** 199, 10 ** 200
cv = lambda v: tuple(tuple(map(int, c)) for c in (v["cover"] if isinstance(v["cover"], list) else json.loads(v["cover"])))
res = lambda v: [int(q) for q in (v["residual"] if isinstance(v["residual"], list) else json.loads(v["residual"]))]
byc = {cv(v): v for v in U}
bad = 0; n = 0; names = set()
for s in S:
    u = byc[cv(s)]; n += 1
    N0s, N0u, M, ks = int(s["N0"]), int(u["N0"]), int(s["M"]), int(s["k_shift"])
    ok = (int(u["M"]) == M and 0 <= N0u < M and N0s == N0u + ks * M and int(s["kmax"]) == TOP
          and N0s + (TOP - 1) * M < HI and N0s + TOP * M >= HI and N0s + KLO * M >= LO
          and all(N0s % p == a and N0u % p == a for p, a in cv(s)) and len(cv(s)) == 88
          and res(s) == res(u) and s["name"].startswith("q170000_m88f_top4s_") and s["name"] not in names)
    names.add(s["name"])
    if not ok:
        bad += 1
        if bad <= 3: print("BAD", s["name"])
lo_n = min(int(s["N0"]) + KLO * int(s["M"]) for s in S); hi_n = max(int(s["N0"]) + (TOP - 1) * int(s["M"]) for s in S)
print(f"[s32] {n} shifted specs matched to their unshifted covers | bad {bad} | N at KLO >= {lo_n / 10 ** 200:.4f}e200 | largest N {hi_n / 10 ** 200:.10f}e200 | k_shift range {min(int(s['k_shift']) for s in S)}..{max(int(s['k_shift']) for s in S)}")
print("[s32] ASSERTS", "PASSED" if bad == 0 and n == len(U) else "FAILED")
