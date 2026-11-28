#!/usr/bin/env python3
"""search_gpu5_xbatch.patch's campaign() / batch_plan() / Pipeline glue on stubs: the driver file (the GPU session's, with the patch applied; path in argv[1], default a scratch copy) is parsed, campaign / select_batch /
batch_plan are executed with a fake run_batch and a fake sieve.  Checks: the same batches in the same order with and without --pipeline, every slice exactly once, the exhaustion code, the sieve thread running ahead
into the next batch while the consumer is still busy with the current one, and nothing planned twice.

    python3 test_xbatch_campaign_fake.py /path/to/patched/search_gpu5.py
"""
import ast, contextlib, io, json, os, re, sys, tempfile, threading, time, types
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import overlap

src = open(sys.argv[1]).read()
tree = ast.parse(src)
funcs = {n.name: ast.get_source_segment(src, n) for n in tree.body if isinstance(n, ast.FunctionDef)}
assert {"campaign", "batch_plan"} <= set(funcs), sorted(funcs)


class Dev:
    id = 0
    def __init__(self, i=0): pass
    def use(self): pass
class Stream:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False


def run(pipeline, depth=1, trace=0, flush_style=False):
    overlap._STREAM.clear()
    cp = types.ModuleType("cupy")
    cp.cuda = types.SimpleNamespace(Device=Dev, Stream=Stream, ExternalStream=lambda p: Stream(), runtime=types.SimpleNamespace())
    D = tempfile.mkdtemp()
    specs = [dict(name=f"v{i}", Q=170000) for i in range(3)]
    log = []
    ev = []                                                       # (time, what)
    K = 1 << 4
    args = types.SimpleNamespace(kmax=16 * 4 * 2, klo=0, slice=16 * 2, desc=True, batch=2, no_stop=True, pipeline=pipeline, pipeline_depth=depth, trace_pipeline=trace, klog=4)
    ns = dict(os=os, re=re, json=json, args=args, cp=cp, mpz=int, Pipeline=overlap.Pipeline, time=time)
    ns["load_specs"] = lambda path: specs
    ns["feeder_for"] = lambda spec: types.SimpleNamespace(window=lambda w0: ev.append((time.perf_counter(), "sieve", w0)) or time.sleep(0.01) or ("W", spec["name"], w0))
    exec(funcs["batch_plan"], ns)
    exec("def sieve_windows(batch):\n    K = 1 << args.klog\n    for si, spec, kstart, kmax in batch_plan(batch, K):\n        fd = feeder_for(spec)\n        for w0 in range(kstart, kmax, K):\n            yield si, fd.window(w0)\n", ns)
    batches = []

    def run_batch(batch, out, pipe=None):
        K = 1 << args.klog
        plan = ns["batch_plan"](batch, K)
        nwin = sum(len(range(a, b, K)) for _, _, a, b in plan)
        src_ = pipe.windows(nwin) if pipe else ns["sieve_windows"](batch)
        got = []
        for si, w in src_:
            got.append(w)
            if not flush_style:
                time.sleep(0.04)                                  # the consumer is slower than the sieve
        if flush_style:
            time.sleep(0.04 * nwin)                               # production's pool: all the windows of the batch are taken at once, then ONE flush
        ev.append((time.perf_counter(), "batch-end", batch[0]["name"]))
        batches.append((tuple(b["name"] for b in batch), tuple(got)))
        return ["line"], [], "stats"
    ns["run_batch"] = run_batch
    open(os.path.join(D, "my_specs.json"), "w").write("[]")
    exec(funcs["campaign"], ns)
    rc = ns["campaign"](D)
    return rc, batches, ev


rc0, b0, e0 = run(False)
rc1, b1, e1 = run(True)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc2, b2, e2 = run(True, depth=2, trace=1, flush_style=True)
names0 = [x[0] for x in b0]
names1 = [x[0] for x in b1]
ok = rc0 == rc1 == 2
flat = [n for b in names1 for n in b]
ok &= names0 == names1 and len(flat) == len(set(flat)) == 3 * (16 * 4 * 2 // (16 * 2))      # every slice once
ok &= [x[1] for x in b0] == [x[1] for x in b1]                                              # the same windows in the same order
print(f"  batches without / with the pipeline: {len(b0)} / {len(b1)}, return codes {rc0} / {rc1} (2 = exhausted), identical batches and windows: {ok}")
# the sieve ran ahead: some window of batch n+1 was sieved before batch n finished
sieved_after = [t for t, w, *_ in e1 if w == "sieve"]
first_end = [t for t, w, *_ in e1 if w == "batch-end"][0]
ahead = sum(1 for t in sieved_after if t > first_end - 0.0) > 0 and any(t < first_end for t in sieved_after)
n_before_end = sum(1 for t in sieved_after if t < first_end)
n_windows_batch0 = sum(len(range(a, b, 16)) for a, b in [(0, 32)]) * 2
print(f"  windows sieved before the first batch ended: {n_before_end} (the batch has {n_windows_batch0}: more than that means the thread ran into the next batch)")
ok &= n_before_end > n_windows_batch0
# depth 2, one flush a batch (production's pool), --trace-pipeline: the same batches and windows; the thread sieves two windows of the next batch under the flush; one [pipeline] line a batch
sieved2 = [t for t, w, *_ in e2 if w == "sieve"]
first_end2 = [t for t, w, *_ in e2 if w == "batch-end"][0]
n_before_end2 = sum(1 for t in sieved2 if t < first_end2)
lines2 = [l for l in buf.getvalue().splitlines() if l.startswith("[pipeline]")]
ok2 = rc2 == 2 and [x[0] for x in b2] == names0 and [x[1] for x in b2] == [x[1] for x in b0] and n_before_end2 == n_windows_batch0 + 2 and len(lines2) == len(b2)
print(f"  depth 2 with one flush a batch: identical batches and windows {[x[1] for x in b2] == [x[1] for x in b0]}, {n_before_end2} windows sieved before the first batch ended (the batch's {n_windows_batch0} + the "
      f"2 that depth 2 allows under its flush), {len(lines2)} [pipeline] trace lines for {len(b2)} batches: {'ok' if ok2 else 'FAILED'}")
if lines2:
    print("   " + lines2[0][:230])
ok &= ok2
print("OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
