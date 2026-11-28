"""Sustained, interleaved A/B of the Fermat kernels on production-range candidates (k in [2^30, 2^32)): after a 15 s warm-up,
R rounds; in each round every kernel runs B back-to-back launches of T tests. Reports each kernel's mean tests/s over its
rounds and the mean SM clock and board power sampled (nvidia-smi, 100 ms) while it ran, so a power- or heat-limited GPU
is measured as it runs in production rather than at the boost clock of a single launch.

    python3 ab_sustained.py SPECS.json R B      (FERMAT28_DIR: the uarch goldbach/fermat661/cuda checkout)"""
import json, os, subprocess, sys, time
import numpy as np, cupy as cp
sys.path.insert(0, os.environ.get("FERMAT28_DIR", "/content/f28w")); sys.path.insert(0, "/content/c3g")
import gpu_fermat28 as g28, gpu_fermat3 as g3, gpu_fermat as g2
spec = json.load(open(sys.argv[1]))[0]; R = int(sys.argv[2]); B = int(sys.argv[3]); T = 1 << 20
U = spec["residual"] if isinstance(spec["residual"], list) else json.loads(spec["residual"])
N0, M = int(spec["N0"]), int(spec["M"])
cq = cp.asarray(np.stack([g2.to_limbs(N0 - int(q), 21) for q in U])); Mv = cp.asarray(g2.to_limbs(M, 21))
rng = np.random.default_rng(7)
bi = cp.asarray(rng.integers(0, len(U), T).astype(np.int32)); bk = cp.asarray(rng.integers(1 << 30, 1 << 32, T, dtype=np.uint64).astype(np.uint32))
out = cp.empty(T, dtype=cp.uint8)
K = [("fermat3", g3.kernel(21))] + [(nm, g28.kernel(21, step_file=sf, asm_mad=am)) for nm, sf, am in
     [("s1rw plain", "fermat28_step_s1rw.cuh", False), ("s1w plain", "fermat28_step_s1w.cuh", False),
      ("s1 plain", "fermat28_step_s1.cuh", False), ("s1r asm", "fermat28_step_s1r.cuh", True)]]
go = lambda k: k(((T + 127) // 128,), (128,), (cq, Mv, bi, bk, out, np.int32(T)))
for _, k in K: go(k)
cp.cuda.Device().synchronize()
smi = subprocess.Popen(["nvidia-smi", "--query-gpu=clocks.sm,power.draw,temperature.gpu", "--format=csv,noheader,nounits", "-lms", "100"],
                       stdout=subprocess.PIPE, text=True, bufsize=1)
samples = []
import threading
def rd():
    for l in smi.stdout:
        try: samples.append((time.time(), *[float(x) for x in l.split(",")]))
        except ValueError: pass
threading.Thread(target=rd, daemon=True).start()
t0 = time.time()
while time.time() - t0 < 15:
    go(K[0][1]); cp.cuda.Device().synchronize()
res = {nm: [] for nm, _ in K}; win = {nm: [] for nm, _ in K}
for r in range(R):
    for nm, k in (K if r % 2 == 0 else K[::-1]):
        cp.cuda.Device().synchronize(); a = time.time()
        for _ in range(B): go(k)
        cp.cuda.Device().synchronize(); b = time.time()
        res[nm].append(B * T / (b - a)); win[nm].append((a, b))
time.sleep(0.3); smi.terminate()
for nm, _ in K:
    s = [x for x in samples if any(a <= x[0] <= b for a, b in win[nm])]
    clk = np.mean([x[1] for x in s]) if s else float("nan"); pw = np.mean([x[2] for x in s]) if s else float("nan"); tp = max([x[3] for x in s]) if s else float("nan")
    v = np.array(res[nm])
    print(f"[ab] {nm:11s} {v.mean():,.0f} tests/s (min {v.min():,.0f}, max {v.max():,.0f}) | SM {clk:.0f} MHz, {pw:.1f} W, max {tp:.0f} C | "
          f"{v.mean() / max(pw, 1):,.0f} tests/J", flush=True)
print("[ab] done")
