#!/usr/bin/env python3
"""search_gpu5.py --vector-dir on stubs (no GPU): cq_limbs against the row-by-row to_limbs, and campaign() in vector mode with a fake run_batch, with and
without the Pipeline (overlap.py of the sieve tree): every vector exactly once, one slice [k_lo, k_lo + K) each with N >= 10^199 at k_lo and N < 10^200 at
k_lo + K - 1, chunk files read in order (including one written while the campaign runs), vectors whose window does not fit skipped, the done-set of a
restarted campaign honoured, and the exhaustion code.

    python3 test_vector_mode_fake.py /path/to/search_gpu5.py /path/to/sieve200/cuda
"""
import ast, json, os, random, sys, tempfile, threading, time, types
import numpy as np
drv, cuda = sys.argv[1], sys.argv[2]
sys.path.insert(0, cuda)
import overlap
from gmpy2 import mpz
src = open(drv).read()
tree = ast.parse(src)
seg = {n.name: ast.get_source_segment(src, n) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
ok = True

# 1. cq_limbs
def to_limbs(x, limbs):
    return np.frombuffer(int(x).to_bytes(4 * limbs, "little"), dtype=np.uint32)
ns = dict(np=np, to_limbs=to_limbs)
exec(seg["cq_limbs"], ns)
rng = random.Random(5)
for trial in range(300):
    if trial % 3 == 0:
        N0 = rng.getrandbits(576) << 64          # low limbs zero: borrows run two limbs and more
    elif trial % 3 == 1:
        N0 = (rng.getrandbits(560) << 96) | 5    # borrow chains through zero limbs
    else:
        N0 = rng.getrandbits(640) | 1
    rows = sorted(rng.sample(range(3, 1 << 18), 300)) + [N0 % (1 << 32) if N0 % (1 << 32) > 2 else 3, 1 << 31]
    rows = sorted(set(q for q in rows if q < N0))
    a = ns["cq_limbs"](N0, rows, 21)
    b = np.stack([to_limbs(N0 - q, 21) for q in rows])
    if not (a.dtype == np.uint32 and np.array_equal(a, b)):
        print("cq_limbs MISMATCH", trial); ok = False; break
else:
    print("  cq_limbs: 300 vectors (zero low limbs, borrow chains, random) identical to the row-by-row to_limbs: ok")

# 2. campaign in vector mode
class Dev:
    id = 0
    def __init__(self, i=0): pass
    def use(self): pass
class Stream:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False

def make_vectors(n, tag, M, rng):
    out = []
    for i in range(n):
        N0 = rng.randrange(0, M) & ~1
        kmax = (10 ** 200 - 1 - N0) // M + 1
        out.append(dict(name=f"q170000_m89_{tag}_v{i}", N0=str(N0), M=str(M), Q=170000, residual=[3, 5, 7], cover=[[3, 1]], kmax=kmax, ceiling_digits=200))
    return out

def run(pipeline, D, V, K, extra_file=None, wait=2):
    overlap._STREAM.clear()
    cp = types.ModuleType("cupy")
    cp.cuda = types.SimpleNamespace(Device=Dev, Stream=Stream, ExternalStream=lambda p: Stream(), runtime=types.SimpleNamespace())
    args = types.SimpleNamespace(kmax=0, klo=0, slice=K, desc=True, batch=4, no_stop=True, pipeline=pipeline, pipeline_depth=4, klog=K.bit_length() - 1,
                                 vector_dir=V, vector_digits=200, vector_wait=wait, trace_pipeline=0)
    import collections, glob, re
    nsc = dict(os=os, re=re, json=json, args=args, cp=cp, mpz=mpz, Pipeline=overlap.Pipeline, time=time, collections=collections, glob=glob)
    def load_specs(path):
        return json.load(open(path))
    nsc["load_specs"] = load_specs
    exec(seg["batch_plan"], nsc)
    exec(seg["VectorSource"], nsc)
    nsc["feeder_for"] = lambda spec: types.SimpleNamespace(window=lambda w0: ("W", spec["name"], w0))
    exec(seg["sieve_windows"], nsc)
    got = []
    def run_batch(batch, out, pipe=None):
        plan = nsc["batch_plan"](batch, K)
        nwin = sum(len(range(a, b, K)) for _, _, a, b in plan)
        ws = list(pipe.windows(nwin) if pipe else nsc["sieve_windows"](batch))
        assert [w[1][1] for w in ws] == [b["name"] for b in batch]
        for b in batch:
            got.append((b["name"], b["kstart"], b["kmax"], b["N0"], b["M"]))
        if extra_file and len(got) == 8:
            json.dump(extra_file[1], open(extra_file[0], "w"))         # a chunk that appears while the campaign runs
        lines = [f"[{b['name']}] k=[{b['kstart']},{b['kmax']}) 1s (1 k/s) tests=0 prp=0" for b in batch]
        return lines, [], "stats"
    nsc["run_batch"] = run_batch
    exec(seg["campaign"], nsc)
    rc = nsc["campaign"](D)
    return rc, got

rng = random.Random(7)
M = mpz(2)
for r in [3, 5, 7, 11, 13]: M *= r
M = int(json.load(open(os.environ["M89_SPECS"]))[0]["M"])                 # the real 89-moduli modulus (193 digits)
K = 1 << 24
for pipeline in (0, 1):
    D, V = tempfile.mkdtemp(), tempfile.mkdtemp()
    a = make_vectors(10, "a", M, rng); b = make_vectors(7, "b", M, rng)
    bad = dict(make_vectors(1, "z", M, rng)[0], kmax=1000)                  # its window cannot fit: skipped
    json.dump(a + [bad], open(os.path.join(V, "vec_000000.json"), "w"))
    json.dump(b, open(os.path.join(V, "vec_000001.json"), "w"))
    c = make_vectors(5, "c", M, rng)
    rc, got = run(pipeline, D, V, K, extra_file=(os.path.join(V, "vec_000002.json"), c))
    names = [g[0] for g in got]
    good = rc == 2 and len(names) == len(set(names)) == 22 and [n.split("@")[0] for n in names] == [s["name"] for s in a + b + c]
    for n, k0, k1, N0, Ms in got:
        N0, Ms = int(N0), int(Ms)
        good &= k1 - k0 == K and N0 + k0 * Ms >= 10 ** 199 and N0 + (k0 - 1) * Ms < 10 ** 199 and N0 + (k1 - 1) * Ms < 10 ** 200 and n.endswith(f"@{k0}")
    print(f"  pipeline={pipeline}: {len(names)} slices from 3 chunk files (one written mid-run), the window-too-long vector skipped, k_lo exact, rc {rc}: {'ok' if good else 'FAILED'}")
    ok &= good
    # restart: the log of the first 9 slices is there -> those are not repeated
    D2 = tempfile.mkdtemp()
    with open(os.path.join(D2, "search.log"), "w") as f:
        for n, k0, k1, _, _ in got[:9]:
            f.write(f"[{n}] k=[{k0},{k1}) 1s (1 k/s) tests=0 prp=0\n")
    rc2, got2 = run(pipeline, D2, V, K)
    good2 = rc2 == 2 and [g[0] for g in got2] == names[9:]
    print(f"  pipeline={pipeline}: restarted with 9 slices in search.log: the other {len(got2)} slices, in order, rc {rc2}: {'ok' if good2 else 'FAILED'}")
    ok &= good2
print("OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
