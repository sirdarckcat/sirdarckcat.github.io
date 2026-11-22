"""End-to-end check of search_gpu2.py where successes are frequent (Q = 3001, 54 residual primes):
the successes on k in [0, 4 * 32768) by brute force with gmpy2 (every residual complement tested),
by search.run_block on the CPU and by search_gpu2.py on the GPU must be the same set, and the GPU's
tests and prps must equal the CPU's. Also prints the model's expected count, kdone * exp(-E^).

    python3 check_small_gpu.py selftest_q3001.json GOLDBACH_DIR
"""
import json, math, re, subprocess, sys
import gmpy2
from gmpy2 import mpz

spec_path, GDIR = sys.argv[1], sys.argv[2]
sys.path.insert(0, GDIR)
import search  # noqa: E402

spec = json.load(open(spec_path))
for f in ("residual", "cover"):
    if isinstance(spec.get(f), str):
        spec[f] = json.loads(spec[f])
NB, L = 4, 32768
KMAX = NB * L
N0, M, U = mpz(spec["N0"]), mpz(spec["M"]), spec["residual"]
brute = [k for k in range(KMAX) if not any(gmpy2.is_prime(N0 + k * M - q) for q in U)]
brute_v = [k for k in brute if search.verify_success(spec, k)]
print(f"brute force: {len(brute)} members with every residual complement composite, {len(brute_v)} pass verify_success", flush=True)
search.init_spec(spec, 1000000, L)
search.G.update(sort_tests=False, skip_frac=0.0)
cpu_s, ct, cpp = [], 0, 0
for k0 in range(0, KMAX, L):
    s, t, p, a, _, _ = search.run_block(k0)
    cpu_s += s; ct += t; cpp += p
cpu_v = sorted(k for k in cpu_s if search.verify_success(spec, k))
print(f"CPU search.run_block: {len(cpu_s)} raw successes, {len(cpu_v)} verified, tests={ct} prps={cpp}", flush=True)
sl = dict(spec, name="q3001@check", kstart=0, kmax=KMAX, stop_on_success=False)
json.dump([sl], open("small_slice.json", "w"))
open("small_found.jsonl", "w").close()
r = subprocess.run([sys.executable, "search_gpu2.py", "small_slice.json", "--goldbach", GDIR, "--out", "small_found.jsonl"],
                   capture_output=True, text=True)
line = [l for l in r.stdout.splitlines() if l.startswith("[q3001@check]")]
print("GPU search_gpu2:", line[-1] if line else (r.stdout + r.stderr)[-500:], flush=True)
gpu_v = sorted(json.loads(l)["k"] for l in open("small_found.jsonl") if l.strip())
m = re.search(r"tests=(\d+) prp=(\d+) .*E\^=([\d.]+)", line[-1]) if line else None
gt, gp, eh = (int(m.group(1)), int(m.group(2)), float(m.group(3))) if m else (-1, -1, float("nan"))
print(f"model: expected kdone*exp(-E^) = {KMAX * math.exp(-eh):.1f}; found brute {len(brute_v)}, CPU {len(cpu_v)}, GPU {len(gpu_v)}")
ok = (gpu_v == cpu_v == brute_v) and gt == ct and gp == cpp
print("END-TO-END MATCH (success sets, tests, prps)" if ok else
      f"MISMATCH: sets equal gpu/cpu {gpu_v == cpu_v}, cpu/brute {cpu_v == brute_v}; tests {gt}/{ct}; prps {gp}/{cpp}")
