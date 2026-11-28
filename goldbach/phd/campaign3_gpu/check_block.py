"""Check search_gpu.py against search.run_block on whole blocks (skip-frac 0): same alive total,
tests, prps and successes. Runs the CPU blocks in a process pool, the GPU slice once.

    python3 check_block.py specs_variants.json GOLDBACH_DIR [nblocks] [variant]
"""
import json, os, subprocess, sys
from multiprocessing import Pool

specs_path, GDIR = sys.argv[1], sys.argv[2]
NB = int(sys.argv[3]) if len(sys.argv) > 3 else 4
VI = int(sys.argv[4]) if len(sys.argv) > 4 else 3
sys.path.insert(0, GDIR)
import search  # noqa: E402

spec = json.load(open(specs_path))[VI]
spec["residual"] = spec["residual"] if isinstance(spec["residual"], list) else json.loads(spec["residual"])
K0 = 123 * 32768                    # an arbitrary block range
blocks = [K0 + b * 32768 for b in range(NB)]


def cpu_init():
    search.init_spec(spec, 1000000, 32768)
    search.G.update(sort_tests=False, skip_frac=0.0)


def cpu_block(k0):
    s, t, p, a, _, _ = search.run_block(k0)
    return k0, sorted(s), t, p, a


if __name__ == "__main__":
    with Pool(min(NB, os.cpu_count() or 1), initializer=cpu_init) as pool:
        cpu = sorted(pool.map(cpu_block, blocks))
    ct = sum(r[2] for r in cpu); cp_ = sum(r[3] for r in cpu); ca = sum(r[4] for r in cpu)
    cs = sorted(k for r in cpu for k in r[1])
    print(f"CPU search.run_block: {NB} blocks from k={K0}: alive={ca} tests={ct} prps={cp_} successes={cs}", flush=True)
    sl = dict(spec, name=spec["name"] + f"@check{K0}", kstart=K0, kmax=K0 + NB * 32768, stop_on_success=False)
    json.dump([sl], open("check_slice.json", "w"))
    r = subprocess.run([sys.executable, "search_gpu.py", "check_slice.json", "--goldbach", GDIR, "--out", "check_found.jsonl"],
                       capture_output=True, text=True)
    print("GPU search_gpu.py:", (r.stdout + r.stderr).strip()[-600:], flush=True)
    import re
    m = re.search(r"tests=(\d+) prp=(\d+) .*alive/k=([\d.]+)", r.stdout)
    gt, gp = int(m.group(1)), int(m.group(2))
    ok = gt == ct and gp == cp_
    print("BLOCKS MATCH (tests, prps)" if ok else f"MISMATCH: gpu tests={gt} prps={gp} vs cpu {ct} {cp_}")
