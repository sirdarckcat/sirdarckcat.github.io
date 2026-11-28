"""The re-check discrepancy path of a patched search_gpu5 engine, on the CPU: its verify_near_miss, true_g, kernel_discrepancy and
record_discrepancy, taken from the engine file itself (ast), run on the 160,357 record's vector with wrong claims.
    python3 -I test_recheck.py ENGINE.py RECORD.json OUTDIR"""
import ast, json, os, sys, time, types
from gmpy2 import mpz
import gmpy2
eng, recf, outd = sys.argv[1:4]
tree = ast.parse(open(eng).read())
want = {"verify_near_miss", "true_g", "kernel_discrepancy", "record_discrepancy"}
fns = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in want]
assert {f.name for f in fns} == want, [f.name for f in fns]
ns = {"mpz": mpz, "json": json, "os": os, "time": time, "args": types.SimpleNamespace(near_miss=160357)}
exec(compile(ast.Module(body=fns, type_ignores=[]), eng, "exec"), ns)
r = json.load(open(recf))
spec = {"name": r["name"], "N0": r["N0"], "M": r["M"], "Q": int(r["Q"]), "residual": r["residual"]}
K = int(r["k"])
os.makedirs(outd, exist_ok=True)
for f in ("found.jsonl", "kernel_discrepancy.jsonl"):
    p = os.path.join(outd, f)
    if os.path.exists(p): os.remove(p)
out = open(os.path.join(outd, "found.jsonl"), "a")
ok = True
def case(label, k, claimed, expect_g, expect_found, expect_nf):
    global ok
    lines, found = [], []
    t = time.time()
    vn = ns["verify_near_miss"](spec, k, claimed) if claimed is not None else None
    assert vn is None, f"{label}: the claim should fail its re-check"
    nf = ns["record_discrepancy"](spec, k, claimed, out, lines, found)
    dt = time.time() - t
    g = int(json.loads(open(os.path.join(outd, "kernel_discrepancy.jsonl")).read().splitlines()[-1])["g"])
    good = g == expect_g and (len(found) == 1) == expect_found and nf == expect_nf and any("C3GPU-KERNEL-DISCREPANCY" in l for l in lines)
    ok &= good
    print(f"{label}: true g {g} (expect {expect_g}), recorded {len(found)}, nf {nf}, {dt:.2f} s -> {'OK' if good else 'WRONG'}")
    for l in lines: print("   ", l[:220])
# the true g of a neighbour member, from N alone, by a plain loop (independent of true_g)
N1 = mpz(spec["N0"]) + (K + 1) * mpz(spec["M"])
p = 3
while not gmpy2.is_prime(N1 - p, 25):
    p = int(gmpy2.next_prime(p))
g1 = p
case("1. record member, wrong claim q = 160,343 (a prime row below the true first PRP)", K, 160343, 160357, True, 0)
case("2. record member, claimed design hit (no PRP below Q)", K, None, 160357, True, 0)
case(f"3. member k+1 (true g {g1} < 160,357), wrong claim q = 165,001", K + 1, 165001, g1, False, 0)
out.close()
fl = [json.loads(l) for l in open(os.path.join(outd, "found.jsonl"))]
dl = [json.loads(l) for l in open(os.path.join(outd, "kernel_discrepancy.jsonl"))]
print(f"found.jsonl: {len(fl)} lines {[(x['g'], x['near_miss'], x['claimed_q'], x['kernel_discrepancy']) for x in fl]}; kernel_discrepancy.jsonl: {len(dl)} lines")
ok &= len(fl) == 2 and len(dl) == 3 and all(x["N"] == r["N"] for x in fl)
print("RECHECK-TEST", "PASSED" if ok else "FAILED")
