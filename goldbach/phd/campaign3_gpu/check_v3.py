"""Checks of search_gpu3.py, on a GPU runtime.

1. Its sieve gives the same alive matrix as search.run_block's CPU sieve (two campaign3 blocks).
2. Its slice lines equal search_gpu2.py's on the same slices (tests, prp, p^, alive/k, E^, hit%, found), at
   --skip-frac 0 and 0.95, also with a small pool and --dmax 3, so that pools are flushed several times.
3. End to end at Q = 3001, k < 131,072:
   - at skip-frac 0, brute force (gmpy2, every residual complement), search.run_block and search_gpu3.py find
     the same successes, and search_gpu3.py's tests and prps equal search.run_block's;
   - at skip-frac 0.5, search.run_block and search_gpu3.py agree on successes, tests, prps and hit mass.

    python3 check_v3.py specs_variants.json selftest_q3001.json GOLDBACH_DIR
"""
import json, math, os, re, subprocess, sys
import numpy as np

specs_path, small_path, GDIR = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["search_gpu3.py", "--goldbach", GDIR]
sys.path.insert(0, GDIR)
import search                      # noqa: E402
import gmpy2                       # noqa: E402
from gmpy2 import mpz              # noqa: E402
import cupy as cp                  # noqa: E402
import search_gpu3 as v3           # noqa: E402

ok_all = True
L = 32768
specs = v3.load_specs(specs_path)

# 1. sieve
spec = specs[3]
U, n0m = v3.variant_state(spec)
search.init_spec(spec, 1000000, L)
G = search.G
for k0 in (123 * L, 300_000_000 // L * L):
    alive = np.ones((len(G["U"]), L), dtype=bool)               # search.run_block's sieve, verbatim
    for i, q in enumerate(G["U"]):
        row = alive[i]
        kres = ((q - G["n0m"]) * G["inv"] - k0) % G["S"]
        for j, s in zip(kres[G["small"]].tolist(), G["S_small_list"]):
            row[j::s] = False
        jl = kres[~G["small"]]
        row[jl[jl < L]] = False
    g = cp.asnumpy(v3.sieve_block(U, n0m, k0, L)).astype(bool)
    same = bool((alive == g).all())
    ok_all &= same
    print(f"1. sieve k0={k0}: CPU alive {int(alive.sum())}, GPU alive {int(g.sum())}, identical: {same}", flush=True)

# 2. slice lines against search_gpu2.py
K0 = 123 * L
sl = [dict(s, name=s["name"] + f"@chk{K0}", kstart=K0, kmax=K0 + 4 * L, stop_on_success=False) for s in (specs[3], specs[5])]
json.dump(sl, open("v3_slices.json", "w"))
pat = re.compile(r"^\[(\S+)\] k=\[(\d+),(\d+)\) \S+ \(\S+ k/s\) (tests=\d+ prp=\d+ p\^=\S+ alive/k=\S+ E\^=\S+ hit%=\S+ found=\d+)")


def lines(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
    got = {m.group(1): m.group(2, 3, 4) for m in map(pat.match, r.stdout.splitlines()) if m}
    if not got:
        print((r.stdout + r.stderr)[-800:])
    return got


for f in ("0", "0.95"):
    a = lines([sys.executable, "search_gpu2.py", "v3_slices.json", "--goldbach", GDIR, "--out", "v3_f2.jsonl", "--skip-frac", f])
    for extra in ([], ["--pool", "20000", "--dmax", "3"]):
        b = lines([sys.executable, "search_gpu3.py", "v3_slices.json", "--goldbach", GDIR, "--out", "v3_f3.jsonl", "--skip-frac", f] + extra)
        same = bool(a) and a == b
        ok_all &= same
        print(f"2. skip-frac {f} {' '.join(extra) or '(defaults)'}: search_gpu2 {sorted(a.values())}", flush=True)
        print(f"   search_gpu3 {sorted(b.values())}  -> {'EQUAL' if same else 'DIFFERENT'}", flush=True)

# 3. Q = 3001 end to end
sp = json.load(open(small_path))
sp = sp[0] if isinstance(sp, list) else sp
for fld in ("residual", "cover"):
    if isinstance(sp.get(fld), str):
        sp[fld] = json.loads(sp[fld])
sp["Q"] = int(sp["Q"])
NB = 4
KMAX = NB * L
N0, M, Us = mpz(sp["N0"]), mpz(sp["M"]), sp["residual"]
brute = sorted(k for k in range(KMAX) if not any(gmpy2.is_prime(N0 + k * M - q) for q in Us))
brute_v = sorted(k for k in brute if search.verify_success(sp, k))
print(f"3. brute force: {len(brute)} members with every residual complement composite, {len(brute_v)} pass verify_success", flush=True)
for f in (0.0, 0.5):
    search.init_spec(sp, 1000000, L)
    search.G.update(sort_tests=False, skip_frac=f, p_est=0.055)
    cs, ct, cpp, hk, ha = [], 0, 0, 0.0, 0.0
    for k0 in range(0, KMAX, L):
        s, t, p, a, bhk, bha = search.run_block(k0)
        cs += s; ct += t; cpp += p; hk += bhk; ha += bha
    cpu_v = sorted(k for k in cs if search.verify_success(sp, k))
    json.dump([dict(sp, name=f"q3001@f{f}", kstart=0, kmax=KMAX)], open("v3_small.json", "w"))
    open("v3_small_found.jsonl", "w").close()
    got = lines([sys.executable, "search_gpu3.py", "v3_small.json", "--goldbach", GDIR, "--out", "v3_small_found.jsonl",
                 "--skip-frac", str(f), "--pool", "50000"])
    gpu_v = sorted(json.loads(l)["k"] for l in open("v3_small_found.jsonl") if l.strip())
    m = re.search(r"tests=(\d+) prp=(\d+) .* hit%=([\d.]+)", got.get(f"q3001@f{f}", ("", "", ""))[2])
    gt, gp, gh = (int(m.group(1)), int(m.group(2)), float(m.group(3))) if m else (-1, -1, -1.0)
    ch = 100 * hk / ha if f > 0 else 100.0
    same = gpu_v == cpu_v and gt == ct and gp == cpp and abs(gh - ch) < 0.05 and (f > 0 or cpu_v == brute_v) \
        and set(cpu_v) <= set(brute_v)
    ok_all &= same
    print(f"   skip-frac {f}: CPU {len(cpu_v)} successes tests={ct} prps={cpp} hit%={ch:.1f}; GPU v3 {len(gpu_v)} tests={gt} prps={gp} "
          f"hit%={gh:.1f} -> {'MATCH' if same else 'MISMATCH'}", flush=True)
print("ALL V3 CHECKS PASSED" if ok_all else "V3 CHECK FAILED")
