"""Check search_gpu2.py's GPU sieve against search.run_block's CPU sieve (identical alive matrices),
then its tests and prps on the 4 blocks that check_block.py measured on the CPU.

    python3 check_sieve.py specs_variants.json GOLDBACH_DIR
"""
import json, re, subprocess, sys
import numpy as np

specs_path, GDIR = sys.argv[1], sys.argv[2]
spec = json.load(open(specs_path))[3]
K0 = 123 * 32768
sl = dict(spec, name=spec["name"] + f"@check{K0}", kstart=K0, kmax=K0 + 4 * 32768, stop_on_success=False)
json.dump([sl], open("check_slice.json", "w"))
sys.argv = ["search_gpu2.py", "check_slice.json", "--goldbach", GDIR]
sys.path.insert(0, GDIR)
import search                      # noqa: E402
import cupy as cp                  # noqa: E402
import search_gpu2                 # noqa: E402  (parses the sys.argv above)

gs = search_gpu2.GpuSieve(spec, cp)
G = search.G
U, L = G["U"], G["block"]
for k0 in (K0, 300_000_000 // 32768 * 32768):
    alive = np.ones((len(U), L), dtype=bool)                  # search.run_block's sieve, verbatim
    for i, q in enumerate(U):
        row = alive[i]
        kres = ((q - G["n0m"]) * G["inv"] - k0) % G["S"]
        for j, s in zip(kres[G["small"]].tolist(), G["S_small_list"]):
            row[j::s] = False
        jl = kres[~G["small"]]
        row[jl[jl < L]] = False
    galive = cp.asnumpy(gs.block(k0, L)).astype(bool)
    print(f"k0={k0}: CPU alive {int(alive.sum())}, GPU alive {int(galive.sum())}, identical: {bool((alive == galive).all())}", flush=True)
r = subprocess.run([sys.executable, "search_gpu2.py", "check_slice.json", "--goldbach", GDIR, "--out", "check_found.jsonl"],
                   capture_output=True, text=True)
print("search_gpu2:", (r.stdout + r.stderr).strip()[-400:])
m = re.search(r"tests=(\d+) prp=(\d+)", r.stdout)
ok = m and int(m.group(1)) == 2412669 and int(m.group(2)) == 131072
print("MATCHES search.run_block (tests 2412669, prps 131072)" if ok else "MISMATCH")
