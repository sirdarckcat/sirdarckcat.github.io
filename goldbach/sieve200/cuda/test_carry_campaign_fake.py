#!/usr/bin/env python3
"""search_gpu5_carry.patch (--carry-over) end to end on the CPU: the patched driver's campaign / run_batch / run_batch_carry / run_pool_split / MultiTester / CarryTester, exec'd from
the file, on fake sieve windows and a fake Fermat kernel whose verdict depends only on (N0, q, k) of a test, with the round kernels of fround compiled by g++ (test_fround_cpu.py's stand-ins).

Runs, every one a whole campaign in its own directory:
  A   --carry-over 0 with the deployed fround.py (the reference: production's code paths)
  A2  --carry-over 0 with the carry fround.py                        -> search.log and gpu3_stats.log identical to A (but times)
  B   --carry-over 1, --pool-threads 2, default stop (D = 1)
  C   --carry-over 1, --pool-threads 1, --carry-stop below target / 2 (rounds with D > 1 before the stop)
  D   --carry-over 1, --pool-threads 2, --pipeline 1 --pipeline-depth 2, slices of two windows and a pool flushed mid-batch
  E   --carry-over 1, --pool-threads 2, killed after the found records of its 4th batch are written and before its log lines, then restarted in the same directory
For B..E: every slice line exactly once and identical to A's (with the SUCCESS / NEARMISS / discrepancy lines before it, in A's order), but its seconds and k/s; found.jsonl the same
records as A's, each N once (E included); the batch lines' counted tests summed equal to A's; fewer tests computed and fewer launches than A.

    python3 test_carry_campaign_fake.py PATCHED_DRIVER FROUND_CARRY FROUND_DEPLOYED
"""
import ast, importlib.util, json, os, re, shutil, sys, tempfile, threading, time, types, zlib, bisect
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
F661 = os.path.join(HERE, "..", "..", "fermat661", "cuda")
sys.path.insert(0, HERE)
sys.path.insert(0, F661)
import test_fround_cpu as TF                                    # noqa: E402

DRIVER, FR_CARRY, FR_DEPLOYED = sys.argv[1:4]
lib = TF.build()
cp, cupyx = TF.install_fake_cupy(lib)
TF.FakeStream.synchronize = lambda self: None
_KLOCK = threading.Lock()                                       # fround_cpu.cpp keeps blockIdx / threadIdx in globals: one CPU kernel at a time (run_pool_split's two threads)
_kcall = TF.FakeKernel.__call__


def _locked(self, *a, **k):
    with _KLOCK:
        return _kcall(self, *a, **k)


TF.FakeKernel.__call__ = _locked


class Stream:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def synchronize(self): pass


class Dev:
    id = 0
    attributes = {"MultiProcessorCount": 4}
    def __init__(self, *a): pass
    def use(self): pass
    def synchronize(self): pass


cp.cuda.Stream = Stream
cp.cuda.Device = Dev
cp.cuda.runtime = types.SimpleNamespace()                       # no stream priorities: overlap.new_stream falls back to a plain stream
import overlap                                                  # noqa: E402

FR_DIR = tempfile.mkdtemp()
for f in ("fround_kernels.cuh",):
    shutil.copy(os.path.join(F661, f), FR_DIR)


def load_fround(path, tag):
    dst = os.path.join(FR_DIR, f"fround_{tag}.py")
    shutil.copy(path, dst)
    spec = importlib.util.spec_from_file_location("fround", dst)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FROUND = {"deployed": load_fround(FR_DEPLOYED, "deployed"), "carry": load_fround(FR_CARRY, "carry")}
src = open(DRIVER).read()
tree = ast.parse(src)
NEEDED = ["_SPLIT_STREAMS", "_CT", "_CT_KM", "MultiTester", "record_discrepancy", "run_pool", "_fermat_stream", "run_pool_split", "CarryTester", "SliceState", "DedupOut", "Carry",
          "_expand", "run_batch_carry", "batch_plan", "sieve_windows", "run_batch", "campaign", "load_specs"]
segs = {}
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        segs[node.name] = ast.get_source_segment(src, node)
    elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        segs[node.targets[0].id] = ast.get_source_segment(src, node)
missing = [n for n in NEEDED if n not in segs]
assert not missing, missing

# ---- the fake world: specs, windows, the Fermat verdict, the CPU checks ----
P_PRP = 0.0714
M = (1 << 40) + 15
NEAR = None                                                     # --near-miss, set below from the specs


def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.nonzero(s)[0]


PR = primes_upto(30000)


def make_specs():
    specs = []
    for i in range(3):
        rng = np.random.default_rng(100 + i)
        res = np.sort(rng.choice(PR[PR > 50], 260 + 20 * i, replace=False))
        specs.append(dict(name=f"v{i}", N0=str((1 << 650) + 2 * 12345 * i + 1), M=str(M), Q=int(res[-1]) + 1, residual=[int(q) for q in res]))
    return specs


def verdict(n0lo, q, k):
    h = ((n0lo.astype(np.uint64) * np.uint64(0x9E3779B1) + q.astype(np.uint64) * np.uint64(0x85EBCA6B) + k.astype(np.uint64) * np.uint64(0xC2B2AE35) + np.uint64(777))
         * np.uint64(0x27D4EB2F)) >> np.uint64(13)
    return ((h % np.uint64(1000003)).astype(np.float64) / 1000003.0 < P_PRP).astype(np.uint8)


class FakeFermat:
    """the Fermat kernel: cq rows are (N0 mod 2^32, q) here, so a test's verdict is a function of (N0, q, k) alone, whatever the global row"""
    def __call__(self, grid, block, a):
        cq, Mv, idx, kv, out, T = a
        T = int(T)
        if T:
            r = cq[np.asarray(idx[:T], dtype=np.int64)]
            out[:T] = verdict(r[:, 0], r[:, 1], np.asarray(kv[:T]))


g28 = types.SimpleNamespace(step_nmax=lambda step: 700, kernel=lambda limbs, step_file=None, asm_mad=False: FakeFermat())


def fake_cq_rows(N0, residual, limbs):
    q = np.asarray([int(x) for x in residual], dtype=np.uint32)
    return np.stack([np.full(q.size, int(N0) & 0xFFFFFFFF, np.uint32), q], axis=1)


class FakeWindow:
    pass


def make_feeder(K):
    def feeder_for(spec):
        base = spec["name"].split("@")[0]
        R = len(spec["residual"])

        def window(w0):
            rng = np.random.default_rng(zlib.crc32(f"{base}:{w0}".encode()))
            n = 1400 + int(rng.integers(0, 100))                # (three slices a batch: above run_pool_split's 4,096, so the reference is split as in production)
            ks = np.sort(rng.choice(K, n, replace=False)).astype(np.uint32) + np.uint32(w0)
            cnt = np.where(rng.random(n) < 0.04, rng.integers(0, 4, n), rng.integers(30, R + 1, n)).astype(np.int32)
            rows = np.concatenate([np.sort(rng.choice(R, int(c), replace=False)) for c in cnt] + [np.zeros(0, np.int64)]).astype(np.uint16)
            w = FakeWindow()
            w.k, w.cnt, w.rows = ks, cnt, rows
            w.alive_total = rng.integers(0, 5000, 64)
            w.hm_kept = rng.random(64) * 0.01
            w.hm_all = w.hm_kept + rng.random(64)
            return w
        return types.SimpleNamespace(window=window)
    return feeder_for


def N_of(spec, k):
    return int(spec["N0"]) + int(k) * int(spec["M"])


def verify_success(spec, k):
    if k % 7 == 3:
        return None                                             # -> the discrepancy path
    N = N_of(spec, k)
    return {"k": int(k), "N": str(N), "digits": len(str(N)), "g": int(spec["Q"])}


def verify_near_miss(spec, k, q):
    if k % 5 == 2:
        return None
    N = N_of(spec, k)
    return {"k": int(k), "N": str(N), "digits": len(str(N)), "g": int(q), "near_miss": True, "Q": int(spec["Q"])}


def kernel_discrepancy(spec, k, claimed_q, out, lines):
    N = N_of(spec, k)
    lines.append(f"  C3GPU-KERNEL-DISCREPANCY {spec['name']} k={k}: claimed {claimed_q} (re-check Error)")
    if k % 2:
        return None
    g = int(spec["Q"]) + 5 if claimed_q is None else int(claimed_q)
    return {"k": int(k), "N": str(N), "digits": len(str(N)), "g": g, "near_miss": g < int(spec["Q"]), "Q": int(spec["Q"]), "name": spec["name"], "kernel_discrepancy": True}


def count_below(cols, offs, sid, thr_row):
    cols, offs, sid, thr = (np.asarray(x) for x in (cols, offs, sid, thr_row))
    out = np.zeros(sid.size, np.int32)
    for m in range(sid.size):
        out[m] = int(np.searchsorted(cols[offs[m]:offs[m + 1]], thr[sid[m]]))
    return out


def namespace(args, fround_mod):
    sys.modules["fround"] = fround_mod
    ns = dict(os=os, re=re, json=json, time=time, threading=threading, bisect=bisect, np=np, cp=cp, cupyx=cupyx, args=args, mpz=int,
              search=types.SimpleNamespace(verify_success=verify_success), verify_near_miss=verify_near_miss, kernel_discrepancy=kernel_discrepancy, count_below=count_below,
              gpu_fermat28=g28, _cq_rows=fake_cq_rows, to_limbs=lambda x, limbs: [int(x) & 0xFFFFFFFF] * limbs, kernel2=None, kernel3=None, _NSM=4,
              Pipeline=overlap.Pipeline, overlapped=overlap.overlapped, feeder_for=make_feeder(1 << args.klog))
    for name in NEEDED:
        exec(segs[name], ns)
    return ns


def make_args(**kw):
    a = dict(batch=3, kmax=16 * (1 << 13), klo=0, desc=False, no_stop=True, slice=1 << 13, block=32768, skip_frac=0.985, p_est=0.0715, near_miss=0, target=2048, dmax=8,
             fused_rounds=1, pool=1 << 21, klog=13, pool_threads=2, carry_over=0, carry_stop=0, profile_pool=0, overlap=0, pipeline=0, pipeline_depth=1, trace_pipeline=0,
             kernel=28, k28_step="fermat29_step_s1.cuh", k28_asm=1, log_near_exp=1, vector_dir=None, flush_each_window=0, fermat_cta_sm=0, deep=0)
    a.update(kw)
    return types.SimpleNamespace(**a)


SPECS = make_specs()
NEAR = int(SPECS[0]["residual"][150])


def run_campaign(name, crash_at=None, fround="carry", **kw):
    D = tempfile.mkdtemp(prefix=f"carry_{name}_")
    json.dump(SPECS, open(os.path.join(D, "my_specs.json"), "w"))
    args = make_args(near_miss=NEAR, **kw)
    t0 = time.perf_counter()
    rc = None
    for attempt in range(2):
        ns = namespace(args, FROUND[fround])
        if crash_at is not None and attempt == 0:
            real = ns["run_batch_carry"]
            calls = [0]

            def crashing(batch, out, pipe, carry, final=False):
                res = real(batch, out, pipe, carry, final)
                calls[0] += 1
                if calls[0] == crash_at:
                    raise KeyboardInterrupt("simulated kill after the found records, before the log lines")
                return res
            ns["run_batch_carry"] = crashing
        try:
            rc = ns["campaign"](D)
            break
        except KeyboardInterrupt:
            continue
    return D, rc, time.perf_counter() - t0


MASK = re.compile(r"(\] k=\[\d+,\d+\)) \d+s \(\d+ k/s\)")


def parse_log(D):
    """name -> (the lines before its slice line since the previous slice line, the masked slice line); and the count of every slice line"""
    blocks, seen, cur = {}, {}, []
    for l in open(os.path.join(D, "search.log")).read().splitlines():
        if not l.strip():
            continue
        m = re.match(r"\[(\S+)\] k=\[", l)
        if m:
            nm = m.group(1)
            seen[nm] = seen.get(nm, 0) + 1
            blocks[nm] = (tuple(cur), MASK.sub(r"\1 Xs (X k/s)", l))
            cur = []
        else:
            cur.append(l)
    return blocks, seen, cur


def parse_stats(D):
    tests = comp = launches = 0
    eh = 0.0
    lines = open(os.path.join(D, "gpu3_stats.log")).read().splitlines()
    for l in lines:
        tests += int(re.search(r"tests (\d+) counted", l).group(1))
        comp += int(re.search(r", (\d+) computed", l).group(1))
        launches += int(re.search(r"\), (\d+) launches", l).group(1))
        eh += float(re.search(r"expected hits ([\d.e+-]+)", l).group(1))
    return dict(tests=tests, computed=comp, launches=launches, ehits=eh, batches=len(lines), last=lines[-1] if lines else "")


def found(D):
    recs = [json.loads(l) for l in open(os.path.join(D, "found.jsonl"))]
    return recs


def main():
    ok = True
    runs = {}
    runs["A"] = run_campaign("A", fround="deployed")
    runs["A2"] = run_campaign("A2", fround="carry")
    runs["B"] = run_campaign("B", carry_over=1)
    runs["C"] = run_campaign("C", carry_over=1, pool_threads=1, carry_stop=512)
    runs["D"] = run_campaign("D", carry_over=1, pipeline=1, pipeline_depth=2, slice=2 << 13, kmax=16 * (2 << 13), pool=6000)
    runs["E"] = run_campaign("E", carry_over=1, crash_at=6)
    runs["L"] = run_campaign("L", carry_over=1, kmax=48 * (1 << 13))
    runs["Lref"] = run_campaign("Lref", fround="deployed", kmax=48 * (1 << 13))
    for k, (D, rc, dt) in runs.items():
        good = rc == 2
        print(f"  run {k}: return code {rc} (2 = exhausted), {dt:.1f} s", flush=True)
        ok &= good
    # A2 against A: the carry fround with --carry-over 0 changes nothing
    a_log = open(os.path.join(runs["A"][0], "search.log")).read()
    a2_log = open(os.path.join(runs["A2"][0], "search.log")).read()
    tmask = lambda s: re.sub(r"^\S+Z ", "", MASK.sub(r"\1 Xs (X k/s)", s), flags=re.M)
    a_st = re.sub(r"\) [\d.]+s:", ") Xs:", tmask(open(os.path.join(runs["A"][0], "gpu3_stats.log")).read()))
    a2_st = re.sub(r"\) [\d.]+s:", ") Xs:", tmask(open(os.path.join(runs["A2"][0], "gpu3_stats.log")).read()))
    same = tmask(a_log) == tmask(a2_log) and a_st == a2_st and found(runs["A"][0]) == found(runs["A2"][0])
    print(f"  A2 (carry fround.py, --carry-over 0) against A (deployed fround.py): search.log, gpu3_stats.log and found.jsonl identical but times: {'ok' if same else 'FAILED'}", flush=True)
    ok &= same
    ref_blocks, ref_seen, _ = parse_log(runs["A"][0])
    ref_found = {json.dumps(r, sort_keys=True) for r in found(runs["A"][0])}
    ref_stats = parse_stats(runs["A"][0])
    nsucc = sum(1 for b in ref_blocks.values() for l in b[0] if "SUCCESS " in l)
    nnear = sum(1 for b in ref_blocks.values() for l in b[0] if "SUCCESS-NEARMISS" in l or "NEARMISS-REJECTED" in l)
    ndisc = sum(1 for b in ref_blocks.values() for l in b[0] if "DISCREPANCY" in l)
    print(f"  A: {len(ref_blocks)} slices, {len(ref_found)} found records ({nsucc} SUCCESS lines, {nnear} near-miss lines, {ndisc} discrepancy lines), {ref_stats['batches']} batch lines, "
          f"{ref_stats['tests']} tests counted / {ref_stats['computed']} computed (waste {100 * (1 - ref_stats['tests'] / ref_stats['computed']):.2f}%), {ref_stats['launches']} launches", flush=True)
    ok &= nsucc > 0 and nnear > 0 and ndisc > 0 and all(v == 1 for v in ref_seen.values())
    for k in ("B", "C", "D", "E", "L"):
        D = runs[k][0]
        if k in ("D", "L"):                                     # their own references: slices of two windows / a longer campaign
            Dref = run_campaign("Dref", slice=2 << 13, kmax=16 * (2 << 13), pool=6000, fround="deployed")[0] if k == "D" else runs["Lref"][0]
            rb, rs, _ = parse_log(Dref)
            rf = {json.dumps(r, sort_keys=True) for r in found(Dref)}
            rst = parse_stats(Dref)
        else:
            rb, rf, rst = ref_blocks, ref_found, ref_stats
        blocks, seen, tail = parse_log(D)
        recs = found(D)
        Ns = [r["N"] for r in recs]
        st = parse_stats(D)
        once = all(v == 1 for v in seen.values()) and set(seen) == set(rb)
        same_blocks = blocks == rb and not tail
        same_found = {json.dumps(r, sort_keys=True) for r in recs} == rf and len(Ns) == len(set(Ns))
        counted = st["tests"] == rst["tests"]
        cheaper = (st["computed"] < rst["computed"] and (st["launches"] < rst["launches"] or k == "C")) or k == "E"     # (C: one part against A's two; E redoes the slices left open by the kill)
        good = once and same_blocks and same_found and counted and cheaper
        print(f"  run {k}: {len(seen)} slices, each line once: {once}; slice blocks identical to the reference: {same_blocks}; found.jsonl the same {len(recs)} records, each N once: {same_found}; "
              f"tests counted {st['tests']} (reference {rst['tests']}): {counted}; computed {st['computed']} / {rst['computed']} (waste {100 * (1 - st['tests'] / st['computed']):.2f}% / "
              f"{100 * (1 - rst['tests'] / rst['computed']):.2f}%), launches {st['launches']} / {rst['launches']}; expected hits summed {st['ehits']:.4e} / {rst['ehits']:.4e}: "
              f"{'ok' if good else 'FAILED'}", flush=True)
        if not same_blocks:
            for nm in sorted(set(rb) | set(blocks)):
                if blocks.get(nm) != rb.get(nm):
                    print("     first difference:", nm, "\n       ref ", rb.get(nm), "\n       got ", blocks.get(nm))
                    break
        ok &= good
    for k in ("B", "L"):
        sl = open(os.path.join(runs[k][0], "gpu3_stats.log")).read().splitlines()
        print(f"   run {k}: a batch line in the middle: {sl[len(sl) // 2][:420]}")
        print(f"   run {k}: the drain's line:            {sl[-1][:420]}")
    print("OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
